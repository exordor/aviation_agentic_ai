from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable
from typing import Any

from aviation_agentic_ai.ontology.atmonto_experiment import (
    LLMInvoker,
    canonical_fact_key,
    parse_llm_prediction_payload,
    term_name,
    validate_prediction_record,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run_agents import (
    critic_reasons,
    routed_fact,
)
from aviation_agentic_ai.utils.json_extraction import JSONPayloadExtractionError, extract_json_object

PROMPT_VERSION = "atcscc_s5_s6_live_agentic_pilot_v2"
ISO_LOCAL_SECONDS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
TMI_LEVEL_PREDICATES = {
    "advisoryNumber",
    "effectiveEndTime",
    "effectiveStartTime",
    "extensionProbability",
    "impactingCondition",
    "impactingConditionMessage",
    "implementationStatus",
    "initiativeComments",
    "issuedTime",
    "reRouteReason",
    "reRouteType",
}

AgentInvoker = Callable[[list[dict[str, str]]], str]


def run_live_agentic_record(
    *,
    record: dict[str, Any],
    schema_slice: dict[str, Any],
    route_map: dict[str, dict[str, set[str]]],
    invoker: LLMInvoker,
    progress: bool,
    index: int,
    total: int,
) -> dict[str, Any]:
    if progress:
        print(f"[live-s5-s6] {index}/{total} {record['source_id']}", flush=True)
    extractor_messages = _extractor_messages(record, schema_slice)
    extractor_raw = invoker(extractor_messages)
    extractor_task = _task(record, "S5_live_llm_extractor_agent", extractor_messages)
    extractor_record = parse_llm_prediction_payload(
        raw_response=extractor_raw,
        task=extractor_task,
        schema_slice=schema_slice,
    )
    _profile_normalize_live_record(extractor_record, record)
    validator_results = validate_prediction_record(
        record=extractor_record,
        source_row={"source_id": record["source_id"], "text": record.get("source_text", "")},
        schema_slice=schema_slice,
    )
    s5_facts = [
        item["validated_fact"]
        for item in validator_results
        if item.get("accepted") and isinstance(item.get("validated_fact"), dict)
    ]
    critic_raw = ""
    critic_payload: dict[str, Any] = {}
    critic_parse_error = None
    if s5_facts:
        critic_raw = invoker(_critic_messages(record, s5_facts, validator_results, route_map))
        try:
            critic_payload = extract_json_object(critic_raw)
        except (JSONPayloadExtractionError, ValueError) as exc:
            critic_parse_error = str(exc)
    critic_drop_ids = _critic_drop_ids(critic_payload)
    allowed_facts, critic_items, quarantine = _critic_allowed_facts(
        record=record,
        s5_facts=s5_facts,
        route_map=route_map,
        critic_drop_ids=critic_drop_ids,
        critic_payload=critic_payload,
    )
    refiner_raw = ""
    refiner_record: dict[str, Any] = {}
    final_validation: list[dict[str, Any]] = []
    refiner_fallback = False
    if allowed_facts:
        refiner_messages = _refiner_messages(record, allowed_facts, critic_payload)
        refiner_raw = invoker(refiner_messages)
        refiner_task = _task(record, "S6_live_llm_refiner_agent", refiner_messages)
        refiner_record = parse_llm_prediction_payload(
            raw_response=refiner_raw,
            task=refiner_task,
            schema_slice=schema_slice,
        )
        _profile_normalize_live_record(refiner_record, record)
        final_validation = validate_prediction_record(
            record=refiner_record,
            source_row={"source_id": record["source_id"], "text": record.get("source_text", "")},
            schema_slice=schema_slice,
        )
    final_facts, safety_quarantine = _final_facts(
        allowed_facts=allowed_facts,
        final_validation=final_validation,
        route_map=route_map,
    )
    refiner_contract_failed = _refiner_contract_failed(
        allowed_facts=allowed_facts,
        final_facts=final_facts,
    )
    if allowed_facts and (
        not final_facts
        or refiner_record.get("json_adherence") is not True
        or refiner_contract_failed
    ):
        refiner_fallback = True
        final_facts = [_live_refined_fact(fact, routed_fact(fact, route_map)) for fact in allowed_facts]
    quarantine.extend(safety_quarantine)
    final_schema_valid = (
        bool(final_facts)
        if refiner_fallback
        else all(item.get("accepted") for item in final_validation)
        if final_validation
        else bool(final_facts)
    )
    return {
        "system_id": "S5_S6_live_agentic_pilot",
        "sample_id": record.get("sample_id"),
        "source_id": str(record["source_id"]),
        "source_family": record.get("source_family", "atcscc_advisories"),
        "json_adherence": bool(extractor_record.get("json_adherence")),
        "schema_valid": final_schema_valid,
        "candidate_fact_count": len(extractor_record.get("facts") or []),
        "validator_accepted_fact_count": len(s5_facts),
        "validator_rejected_fact_count": sum(1 for item in validator_results if not item.get("accepted")),
        "critic_quarantined_fact_count": len(quarantine),
        "accepted_fact_count": len(final_facts),
        "facts": final_facts,
        "s5_facts": s5_facts,
        "validator_results": validator_results,
        "critic_results": critic_items,
        "live_critic_payload": {
            "raw_response": critic_raw,
            "payload": critic_payload,
            "parse_error": critic_parse_error,
            "drop_fact_ids": sorted(critic_drop_ids),
        },
        "critic_quarantine": quarantine,
        "refiner_results": {
            "raw_response": refiner_raw,
            "json_adherence": refiner_record.get("json_adherence"),
            "parse_error": refiner_record.get("parse_error"),
            "contract_failed": refiner_contract_failed,
            "fallback_used": refiner_fallback,
        },
        "agent_call_counts": {
            "extractor": 1,
            "validator": 1,
            "critic": 1 if s5_facts else 0,
            "refiner": 1 if allowed_facts else 0,
        },
    }


def quality_counters(records: list[dict[str, Any]]) -> dict[str, Any]:
    failure_types = Counter(
        str(record.get("failure", {}).get("exception_type"))
        for record in records
        if record.get("run_status") == "failed"
    )
    return {
        "record_count": len(records),
        "failed_record_count": sum(1 for record in records if record.get("run_status") == "failed"),
        "failure_type_counts": dict(sorted(failure_types.items())),
        "extractor_json_adherence_count": sum(1 for record in records if record.get("json_adherence")),
        "final_schema_valid_record_count": sum(1 for record in records if record.get("schema_valid")),
        "refiner_fallback_count": sum(
            1 for record in records if record.get("refiner_results", {}).get("fallback_used")
        ),
        "agent_call_counts": {
            role: sum(record.get("agent_call_counts", {}).get(role, 0) for record in records)
            for role in ("extractor", "validator", "critic", "refiner")
        },
    }


def agent_roles() -> list[dict[str, str]]:
    return [
        {
            "agent": "extractor",
            "input": "ATCSCC source text plus ATMONTO ATCSCC profile menu",
            "operation": "live LLM schema-constrained fact proposal",
            "output": "candidate flat KG facts with copied evidence spans",
        },
        {
            "agent": "validator",
            "input": "extractor facts, source text, and schema slice",
            "operation": "deterministic schema, datatype/range, and evidence validation",
            "output": "S5 validator-accepted facts and validator rejections",
        },
        {
            "agent": "critic",
            "input": "S5 facts, CQ routes, validator rejections, and source text",
            "operation": "live LLM critique with deterministic duplicate/text-artifact safeguards",
            "output": "drop decisions and quarantine reasons",
        },
        {
            "agent": "refiner",
            "input": "critic-filtered S5 facts",
            "operation": "live LLM final payload rewrite under no-new-facts safety gate",
            "output": "S6 facts retained after final deterministic validation",
        },
    ]


def _extractor_messages(record: dict[str, Any], schema_slice: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are the Extractor agent for an ATCSCC advisory KG experiment. "
                "Return strict JSON only with source_id, source_family, and facts. "
                "Every fact must use the allowed ATMONTO profile classes/properties, "
                "must quote evidence_text from the advisory, and must be one flat "
                "predicate-value assertion."
            ),
        },
        {
            "role": "user",
            "content": "\n\n".join(
                [
                    f"sample_id: {record.get('sample_id')}",
                    f"source_id: {record.get('source_id')}",
                    f"candidate_subject_class: {record.get('candidate_subject_class')}",
                    "Use candidate_subject_class exactly for TMI-level facts when provided.",
                    "Render datetime values as UTC ISO strings ending in Z.",
                    _schema_menu(schema_slice),
                    "Return JSON shape: "
                    '{"source_id": "...", "source_family": "atcscc_advisories", "facts": [...]}',
                    "Advisory text:\n" + str(record.get("source_text") or ""),
                ]
            ),
        },
    ]


def _critic_messages(
    record: dict[str, Any],
    s5_facts: list[dict[str, Any]],
    validator_results: list[dict[str, Any]],
    route_map: dict[str, dict[str, set[str]]],
) -> list[dict[str, str]]:
    routed = [routed_fact(fact, route_map) for fact in s5_facts]
    rejected = [
        {"fact_id": item.get("fact_id"), "errors": item.get("errors", [])}
        for item in validator_results
        if not item.get("accepted")
    ]
    return [
        {
            "role": "system",
            "content": (
                "You are the Critic agent. Review validator-accepted ATCSCC KG facts. "
                "Return strict JSON only. Drop facts only when they are duplicate, "
                "not actually supported by copied evidence, or obvious page-boilerplate/text artifacts. "
                "Do not propose new facts."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "source_id": record.get("source_id"),
                    "source_text": record.get("source_text"),
                    "validator_accepted_facts": s5_facts,
                    "cq_routes": routed,
                    "validator_rejections": rejected,
                    "required_output": {
                        "drop_fact_ids": [],
                        "concerns": [{"fact_id": "example", "reason": "short reason"}],
                        "global_notes": [],
                    },
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        },
    ]


def _refiner_messages(
    record: dict[str, Any],
    allowed_facts: list[dict[str, Any]],
    critic_payload: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are the Refiner agent. Return strict JSON only. Your facts list may "
                "only contain facts copied from validator_accepted_facts. Do not add new "
                "predicates, values, classes, or evidence. Preserve fact_id when present."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "source_id": record.get("source_id"),
                    "source_family": record.get("source_family", "atcscc_advisories"),
                    "validator_accepted_facts": allowed_facts,
                    "critic_decision": critic_payload,
                    "required_output": {
                        "source_id": record.get("source_id"),
                        "source_family": record.get("source_family", "atcscc_advisories"),
                        "facts": allowed_facts,
                    },
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        },
    ]


def _task(record: dict[str, Any], system_id: str, messages: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "system_id": system_id,
        "sample_id": record.get("sample_id"),
        "source_id": str(record["source_id"]),
        "source_family": record.get("source_family", "atcscc_advisories"),
        "messages": messages,
    }


def _profile_normalize_live_record(
    prediction_record: dict[str, Any],
    input_record: dict[str, Any],
) -> None:
    facts = prediction_record.get("facts")
    if not isinstance(facts, list):
        return
    candidate_subject_class = input_record.get("candidate_subject_class")
    for fact in facts:
        if not isinstance(fact, dict):
            continue
        predicate = term_name(fact.get("predicate"))
        if candidate_subject_class and predicate in TMI_LEVEL_PREDICATES:
            fact["subject_class"] = str(candidate_subject_class)
        if predicate in {"effectiveEndTime", "effectiveStartTime", "issuedTime"}:
            value = fact.get("value")
            if isinstance(value, str):
                if ISO_LOCAL_SECONDS_RE.fullmatch(value):
                    fact["value"] = f"{value}Z"
                elif value.endswith("+00:00"):
                    fact["value"] = value.removesuffix("+00:00") + "Z"


def _schema_menu(schema_slice: dict[str, Any]) -> str:
    return json.dumps(
        {
            "allowed_classes": [
                row.get("prefixed_name") or row.get("local_name")
                for row in schema_slice.get("classes", [])
                if isinstance(row, dict)
            ],
            "allowed_object_properties": _property_menu(schema_slice, "object_properties"),
            "allowed_datatype_properties": _property_menu(schema_slice, "datatype_properties"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _property_menu(schema_slice: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return [
        {
            "predicate": row.get("prefixed_name") or row.get("local_name"),
            "domain": row.get("domain_set") or row.get("domain_iri_set") or [],
            "range_or_datatype": (
                row.get("range_set")
                or row.get("range_iri_set")
                or row.get("datatype_set")
                or row.get("datatype_iri_set")
                or []
            ),
        }
        for row in schema_slice.get(key, [])
        if isinstance(row, dict)
    ]


def _critic_drop_ids(payload: dict[str, Any]) -> set[str]:
    raw_ids = payload.get("drop_fact_ids", [])
    if not isinstance(raw_ids, list):
        return set()
    return {str(item) for item in raw_ids if item}


def _critic_allowed_facts(
    *,
    record: dict[str, Any],
    s5_facts: list[dict[str, Any]],
    route_map: dict[str, dict[str, set[str]]],
    critic_drop_ids: set[str],
    critic_payload: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    allowed: list[dict[str, Any]] = []
    critic_items: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str, str, str, str, str]] = set()
    concern_reasons = _concern_reasons(critic_payload)
    for fact in s5_facts:
        routed = routed_fact(fact, route_map)
        reasons = critic_reasons(fact, record, seen_keys)
        fact_id = str(fact.get("fact_id") or "")
        if fact_id in critic_drop_ids:
            reasons.append("live_critic_drop")
        reasons.extend(concern_reasons.get(fact_id, []))
        critic_item = {**routed, "accepted": not reasons, "reasons": sorted(set(reasons))}
        critic_items.append(critic_item)
        if reasons:
            quarantine.append(critic_item)
            continue
        seen_keys.add(canonical_fact_key(fact))
        allowed.append(fact)
    return allowed, critic_items, quarantine


def _concern_reasons(payload: dict[str, Any]) -> dict[str, list[str]]:
    reasons: dict[str, list[str]] = {}
    concerns = payload.get("concerns", [])
    if not isinstance(concerns, list):
        return reasons
    for item in concerns:
        if not isinstance(item, dict) or not item.get("fact_id"):
            continue
        reason = str(item.get("reason") or "live_critic_concern")
        reasons.setdefault(str(item["fact_id"]), []).append(f"live_critic:{reason}")
    return reasons


def _final_facts(
    *,
    allowed_facts: list[dict[str, Any]],
    final_validation: list[dict[str, Any]],
    route_map: dict[str, dict[str, set[str]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    allowed_by_key = {canonical_fact_key(fact): fact for fact in allowed_facts}
    final: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str, str, str, str, str]] = set()
    for item in final_validation:
        fact = item.get("validated_fact") if item.get("accepted") else None
        if not isinstance(fact, dict):
            continue
        key = canonical_fact_key(fact)
        routed = routed_fact(fact, route_map)
        if key not in allowed_by_key:
            quarantine.append(
                {**routed, "accepted": False, "reasons": ["refiner_added_fact_outside_s5_contract"]}
            )
            continue
        if key in seen_keys:
            quarantine.append({**routed, "accepted": False, "reasons": ["duplicate_refined_fact"]})
            continue
        seen_keys.add(key)
        final.append(_live_refined_fact(fact, routed))
    return final, quarantine


def _refiner_contract_failed(
    *,
    allowed_facts: list[dict[str, Any]],
    final_facts: list[dict[str, Any]],
) -> bool:
    allowed_keys = {canonical_fact_key(fact) for fact in allowed_facts}
    final_keys = {canonical_fact_key(fact) for fact in final_facts}
    return bool(allowed_keys) and final_keys != allowed_keys


def _live_refined_fact(fact: dict[str, Any], routed: dict[str, Any]) -> dict[str, Any]:
    return {
        **fact,
        "agentic_system_id": "S5_S6_live_agentic_pilot",
        "agentic_route_module": routed["module"],
        "agentic_cq_ids": routed["cq_ids"],
        "agentic_refiner_status": "accepted_after_live_agentic_loop",
    }
