from __future__ import annotations

import json
from typing import Any, Callable

from aviation_agentic_ai.agents.repair_planner import (
    build_repair_planner_messages,
    deterministic_repair_targets,
    parse_repair_plan,
)
from aviation_agentic_ai.agents.types import (
    ExtractionResult,
    ExtractionTrace,
    FactIdentityKey,
    evidence_span_hash,
    identity_key_label,
)
from aviation_agentic_ai.ontology.atmonto_experiment import (
    build_default_llm_invoker,
    canonical_fact_key,
    evidence_tolerant_fact_key,
    parse_llm_prediction_payload,
    term_name,
    validate_prediction_record,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run_agents import (
    routed_fact,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.live_pilot_agents import (
    _critic_allowed_facts,
    _critic_drop_ids,
    _critic_messages,
    _extractor_messages,
    _final_facts,
    _profile_normalize_live_record,
    _refiner_messages,
    _task,
)

AgentInvoker = Callable[[list[dict[str, str]]], str]


class ExtractionAgent:
    """Bounded L1 extractor-validator-critic-repair loop for ATCSCC facts."""

    def __init__(
        self,
        *,
        schema_slice: dict[str, Any],
        route_map: dict[str, dict[str, set[str]]] | None = None,
        max_iterations: int = 2,
        temperature: float = 0.0,
        max_tokens: int = 4000,
    ) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        self.schema_slice = schema_slice
        self.route_map = route_map or {}
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.max_tokens = max_tokens

    def run(
        self,
        record: dict[str, Any],
        *,
        invoker: AgentInvoker | None = None,
        invoker_label: str = "default",
        progress: bool = False,
    ) -> ExtractionResult:
        active_invoker = invoker or build_default_llm_invoker(
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        accepted_by_key: dict[FactIdentityKey, dict[str, Any]] = {}
        blocked_by_key: dict[FactIdentityKey, list[dict[str, Any]]] = {}
        trace = ExtractionTrace()
        repair_targets: list[dict[str, Any]] = []
        blocked_key_labels: list[str] = []
        agent_call_counts = {"extractor": 0, "validator": 0, "critic": 0, "repair_planner": 0, "refiner": 0}

        for iteration in range(self.max_iterations):
            trace.iterations_used = iteration + 1
            if progress:
                print(f"[agent] extraction iteration {iteration + 1}", flush=True)
            extraction_messages = self._iteration_extractor_messages(
                record=record,
                repair_targets=repair_targets,
                blocked_keys=blocked_key_labels,
            )
            agent_call_counts["extractor"] += 1
            task = _task(record, "L1_agentic_extraction", extraction_messages)
            raw_response = active_invoker(extraction_messages)
            prediction = parse_llm_prediction_payload(
                raw_response=raw_response,
                task=task,
                schema_slice=self.schema_slice,
            )
            _profile_normalize_live_record(prediction, record)
            validations = validate_prediction_record(
                record=prediction,
                source_row={"source_id": str(record["source_id"]), "text": record.get("source_text", "")},
                schema_slice=self.schema_slice,
            )
            agent_call_counts["validator"] += 1
            accepted_candidates = [
                item["validated_fact"]
                for item in validations
                if item.get("accepted") and isinstance(item.get("validated_fact"), dict)
            ]
            validator_rejections = self._record_validator_rejections(
                validations,
                blocked_by_key,
                trace,
            )

            critic_payload: dict[str, Any] = {"drop_fact_ids": [], "concerns": [], "global_notes": []}
            critic_items: list[dict[str, Any]] = []
            critic_quarantine: list[dict[str, Any]] = []
            allowed_facts: list[dict[str, Any]] = []
            if accepted_candidates:
                critic_messages = _critic_messages(
                    record,
                    accepted_candidates,
                    validations,
                    self.route_map,
                )
                agent_call_counts["critic"] += 1
                critic_payload = self._invoke_json(active_invoker, critic_messages)
                allowed_facts, critic_items, critic_quarantine = _critic_allowed_facts(
                    record=record,
                    s5_facts=accepted_candidates,
                    route_map=self.route_map,
                    critic_drop_ids=_critic_drop_ids(critic_payload),
                    critic_payload=critic_payload,
                )
                self._record_critic_quarantine(
                    facts=accepted_candidates,
                    critic_quarantine=critic_quarantine,
                    blocked_by_key=blocked_by_key,
                    trace=trace,
                )

            self._merge_allowed_facts(
                allowed_facts=allowed_facts,
                accepted_by_key=accepted_by_key,
                blocked_by_key=blocked_by_key,
                trace=trace,
            )

            missing_predicates = self._missing_predicates(list(accepted_by_key.values()))
            blocked_key_labels = sorted(identity_key_label(key) for key in blocked_by_key)
            planner_messages = build_repair_planner_messages(
                record=record,
                accepted_facts=list(accepted_by_key.values()),
                validator_rejections=validator_rejections,
                critic_quarantine=critic_quarantine,
                missing_predicates=missing_predicates,
                blocked_keys=blocked_key_labels,
            )
            agent_call_counts["repair_planner"] += 1
            planner_payload = parse_repair_plan(active_invoker(planner_messages))
            fallback_targets = deterministic_repair_targets(
                validator_rejections=validator_rejections,
                critic_quarantine=critic_quarantine,
                missing_predicates=missing_predicates,
            )
            repair_targets = (
                planner_payload["repair_targets"]
                if planner_payload["parse_ok"]
                else fallback_targets
            )
            if not repair_targets:
                break
            if iteration + 1 >= self.max_iterations:
                trace.budget_exhausted = True
                break

        final_facts = self._run_refiner(
            record=record,
            accepted_facts=list(accepted_by_key.values()),
            active_invoker=active_invoker,
            agent_call_counts=agent_call_counts,
            trace=trace,
        )
        trace.accepted_identity_keys = set(accepted_by_key)
        trace.blocked_identity_keys = set(blocked_by_key) - set(accepted_by_key)
        blocked = [
            item
            for key, items in blocked_by_key.items()
            if key not in accepted_by_key
            for item in items
        ]
        return ExtractionResult(
            facts=final_facts,
            blocked=blocked,
            trace=trace,
            metadata={
                "system_id": "L1_agentic_extraction",
                "source_id": str(record.get("source_id")),
                "source_family": record.get("source_family", "atcscc_advisories"),
                "max_iterations": self.max_iterations,
                "agent_call_counts": agent_call_counts,
                "live_llm_run": invoker is None,
                "invoker_label": invoker_label,
            },
        )

    def _iteration_extractor_messages(
        self,
        *,
        record: dict[str, Any],
        repair_targets: list[dict[str, Any]],
        blocked_keys: list[str],
    ) -> list[dict[str, str]]:
        messages = list(_extractor_messages(record, self.schema_slice))
        if repair_targets or blocked_keys:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Repair pass instructions. Extract only facts supported by copied evidence. "
                        "Do not repeat blocked identity/evidence pairs.\n"
                        f"repair_targets: {repair_targets}\n"
                        f"blocked_keys: {blocked_keys}"
                    ),
                }
            )
        return messages

    def _record_validator_rejections(
        self,
        validations: list[dict[str, Any]],
        blocked_by_key: dict[FactIdentityKey, list[dict[str, Any]]],
        trace: ExtractionTrace,
    ) -> list[dict[str, Any]]:
        rejections: list[dict[str, Any]] = []
        for item in validations:
            if item.get("accepted"):
                continue
            candidate = item.get("candidate")
            predicate = self._item_predicate(item)
            reasons = [str(error) for error in item.get("errors", [])]
            rejections.append(
                {
                    "fact_id": item.get("fact_id"),
                    "predicate": predicate,
                    "errors": reasons,
                    "candidate": candidate,
                }
            )
            event = {
                "event": "validator_rejected",
                "fact_id": item.get("fact_id"),
                "predicate": predicate,
                "reasons": reasons,
            }
            if isinstance(candidate, dict):
                key = evidence_tolerant_fact_key(candidate)
                event.update(
                    {
                        "identity_key": identity_key_label(key),
                        "evidence_hash": evidence_span_hash(candidate.get("evidence_text")),
                    }
                )
                trace.blocked_evidence_hashes[predicate] = event["evidence_hash"]
                blocked_by_key.setdefault(key, []).append({**event, "fact": candidate})
            trace.events.append(event)
        return rejections

    def _record_critic_quarantine(
        self,
        *,
        facts: list[dict[str, Any]],
        critic_quarantine: list[dict[str, Any]],
        blocked_by_key: dict[FactIdentityKey, list[dict[str, Any]]],
        trace: ExtractionTrace,
    ) -> None:
        facts_by_id = {str(fact.get("fact_id")): fact for fact in facts}
        for item in critic_quarantine:
            fact = facts_by_id.get(str(item.get("fact_id")))
            if not fact:
                continue
            key = evidence_tolerant_fact_key(fact)
            event_hash = evidence_span_hash(fact.get("evidence_text"))
            previous_hashes = {
                str(entry.get("evidence_hash"))
                for entry in blocked_by_key.get(key, [])
                if entry.get("evidence_hash")
            }
            if event_hash in previous_hashes:
                trace.blocked_repeat_count += 1
            event = {
                "event": "critic_quarantined",
                "fact_id": fact.get("fact_id"),
                "predicate": term_name(fact.get("predicate")),
                "identity_key": identity_key_label(key),
                "evidence_hash": event_hash,
                "reasons": item.get("reasons", []),
            }
            trace.events.append(event)
            trace.blocked_evidence_hashes[event["predicate"]] = event["evidence_hash"]
            blocked_by_key.setdefault(key, []).append({**item, "fact": fact, **event})

    def _merge_allowed_facts(
        self,
        *,
        allowed_facts: list[dict[str, Any]],
        accepted_by_key: dict[FactIdentityKey, dict[str, Any]],
        blocked_by_key: dict[FactIdentityKey, list[dict[str, Any]]],
        trace: ExtractionTrace,
    ) -> None:
        for fact in allowed_facts:
            key = evidence_tolerant_fact_key(fact)
            predicate = term_name(fact.get("predicate"))
            current_hash = evidence_span_hash(fact.get("evidence_text"))
            blocked_hashes = {
                str(item.get("evidence_hash"))
                for item in blocked_by_key.get(key, [])
                if item.get("evidence_hash")
            }
            if current_hash in blocked_hashes:
                trace.blocked_repeat_count += 1
                trace.events.append(
                    {
                        "event": "blocked_repeat_skipped",
                        "fact_id": fact.get("fact_id"),
                        "predicate": predicate,
                        "identity_key": identity_key_label(key),
                        "evidence_hash": current_hash,
                    }
                )
                continue
            if key in accepted_by_key:
                previous_hash = evidence_span_hash(accepted_by_key[key].get("evidence_text"))
                if current_hash != previous_hash:
                    accepted_by_key[key] = fact
                    blocked_by_key.pop(key, None)
                    trace.accepted_evidence_hashes[predicate] = current_hash
                    trace.events.append(
                        {
                            "event": "accepted_identity_replaced",
                            "fact_id": fact.get("fact_id"),
                            "predicate": predicate,
                            "identity_key": identity_key_label(key),
                            "evidence_hash": current_hash,
                            "previous_evidence_hash": previous_hash,
                        }
                    )
                    continue
                trace.events.append(
                    {
                        "event": "accepted_identity_preserved",
                        "fact_id": fact.get("fact_id"),
                        "predicate": predicate,
                        "identity_key": identity_key_label(key),
                    }
                )
                continue
            accepted_by_key[key] = fact
            blocked_by_key.pop(key, None)
            trace.accepted_evidence_hashes[predicate] = current_hash
            trace.events.append(
                {
                    "event": "accepted",
                    "fact_id": fact.get("fact_id"),
                    "predicate": predicate,
                    "identity_key": identity_key_label(key),
                    "evidence_hash": current_hash,
                }
            )

    def _missing_predicates(self, accepted_facts: list[dict[str, Any]]) -> list[str]:
        accepted_predicates = {term_name(fact.get("predicate")) for fact in accepted_facts}
        routed_predicates = sorted(self.route_map)
        return [predicate for predicate in routed_predicates if predicate not in accepted_predicates]

    def _run_refiner(
        self,
        *,
        record: dict[str, Any],
        accepted_facts: list[dict[str, Any]],
        active_invoker: AgentInvoker,
        agent_call_counts: dict[str, int],
        trace: ExtractionTrace,
    ) -> list[dict[str, Any]]:
        if not accepted_facts:
            return []
        refiner_messages = _refiner_messages(
            record,
            accepted_facts,
            {"drop_fact_ids": [], "concerns": [], "global_notes": []},
        )
        agent_call_counts["refiner"] += 1
        task = _task(record, "L1_agentic_extraction_refiner", refiner_messages)
        refined = parse_llm_prediction_payload(
            raw_response=active_invoker(refiner_messages),
            task=task,
            schema_slice=self.schema_slice,
        )
        _profile_normalize_live_record(refined, record)
        final_validation = validate_prediction_record(
            record=refined,
            source_row={"source_id": str(record["source_id"]), "text": record.get("source_text", "")},
            schema_slice=self.schema_slice,
        )
        final_facts, quarantine = _final_facts(
            allowed_facts=accepted_facts,
            final_validation=final_validation,
            route_map=self.route_map,
        )
        for item in quarantine:
            trace.events.append({**item, "event": "refiner_quarantined"})
        if self._refiner_omitted_or_changed_accepted_set(
            accepted_facts=accepted_facts,
            final_facts=final_facts,
        ):
            trace.events.append(
                {
                    "event": "refiner_contract_failed",
                    "reason": "refiner_output_did_not_match_accepted_fact_set",
                }
            )
            return self._annotate_l1_final_facts(accepted_facts)
        return self._annotate_l1_final_facts(final_facts or accepted_facts)

    def _invoke_json(self, invoker: AgentInvoker, messages: list[dict[str, str]]) -> dict[str, Any]:
        raw = invoker(messages)
        try:
            payload = json.loads(raw)
        except ValueError:
            return {"drop_fact_ids": [], "concerns": [], "global_notes": [], "raw_response": raw}
        return payload if isinstance(payload, dict) else {"drop_fact_ids": [], "concerns": [], "global_notes": []}

    def _refiner_omitted_or_changed_accepted_set(
        self,
        *,
        accepted_facts: list[dict[str, Any]],
        final_facts: list[dict[str, Any]],
    ) -> bool:
        accepted_keys = {canonical_fact_key(fact) for fact in accepted_facts}
        final_keys = {canonical_fact_key(fact) for fact in final_facts}
        return bool(accepted_keys) and accepted_keys != final_keys

    def _annotate_l1_final_facts(self, facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        annotated: list[dict[str, Any]] = []
        for fact in facts:
            routed = routed_fact(fact, self.route_map)
            annotated.append(
                {
                    **fact,
                    "agentic_system_id": "L1_agentic_extraction",
                    "agentic_route_module": routed["module"],
                    "agentic_cq_ids": routed["cq_ids"],
                    "agentic_refiner_status": "accepted_after_l1_agent_loop",
                }
            )
        return annotated

    def _item_predicate(self, item: dict[str, Any]) -> str:
        for key in ("candidate", "validated_fact"):
            payload = item.get(key)
            if isinstance(payload, dict) and payload.get("predicate"):
                return term_name(payload.get("predicate"))
        return term_name(item.get("predicate"))
