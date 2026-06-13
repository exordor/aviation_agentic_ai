from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from aviation_agentic_ai.ontology.atmonto_experiment import (
    canonical_fact_key,
    semantic_metrics,
    term_name,
)
from aviation_agentic_ai.ontology.atmonto_minimal_loop import validate_candidate_payloads
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.io import normalize_report_text

CONTROLLED_ELEMENT_TEXT_ARTIFACTS = {
    "ADDS",
    "ADVZY",
    "ARE",
    "CAN",
    "DIEGO",
    "EXPECT",
    "HOLDING",
    "INTO",
    "MINUTES",
    "NECESSARY",
    "THAT",
    "UPDATES",
    "USERS",
    "WILL",
}


def build_prediction_record(
    *,
    s0_record: dict[str, Any],
    input_record: dict[str, Any],
    schema_slice: dict[str, Any],
    route_map: dict[str, dict[str, set[str]]],
) -> dict[str, Any]:
    source_id = str(s0_record["source_id"])
    validations = validate_candidate_payloads(
        [{"source_id": source_id, "facts": s0_record.get("candidate_facts", [])}],
        [{"source_id": source_id, "text": input_record.get("source_text", "")}],
        schema_slice,
    )
    s5_facts = [
        item["validated_fact"]
        for item in validations
        if item.get("accepted") and isinstance(item.get("validated_fact"), dict)
    ]
    s6_facts: list[dict[str, Any]] = []
    critic_results: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    seen_keys = set()
    for fact in s5_facts:
        routed = routed_fact(fact, route_map)
        reasons = critic_reasons(fact, input_record, seen_keys)
        critic_item = {**routed, "accepted": not reasons, "reasons": reasons}
        critic_results.append(critic_item)
        if reasons:
            quarantine.append(critic_item)
            continue
        seen_keys.add(canonical_fact_key(fact))
        s6_facts.append(refined_fact(fact, routed))
    return {
        "system_id": "S5_S6_independent_agentic_run",
        "sample_id": input_record.get("sample_id"),
        "source_id": source_id,
        "source_family": input_record.get("source_family", "atcscc_advisories"),
        "json_adherence": True,
        "schema_valid": not any(not item.get("accepted") for item in validations),
        "candidate_fact_count": len(s0_record.get("candidate_facts", [])),
        "validator_accepted_fact_count": len(s5_facts),
        "validator_rejected_fact_count": sum(1 for item in validations if not item.get("accepted")),
        "critic_quarantined_fact_count": len(quarantine),
        "accepted_fact_count": len(s6_facts),
        "facts": s6_facts,
        "s5_facts": s5_facts,
        "validator_results": validations,
        "critic_results": critic_results,
        "critic_quarantine": quarantine,
    }


def critic_reasons(
    fact: dict[str, Any],
    input_record: dict[str, Any],
    seen_keys: set[tuple[str, str, str, str, str, str, str]],
) -> list[str]:
    reasons: list[str] = []
    evidence = str(fact.get("evidence_text") or "")
    source_text = str(input_record.get("source_text") or "")
    if not evidence or normalize_report_text(evidence) not in normalize_report_text(source_text):
        reasons.append("evidence_not_contained_after_normalization")
    if canonical_fact_key(fact) in seen_keys:
        reasons.append("duplicate_canonical_fact")
    if is_text_artifact_controlled_element(fact):
        reasons.append("text_artifact_controlled_element")
    return reasons


def is_text_artifact_controlled_element(fact: dict[str, Any]) -> bool:
    if term_name(fact.get("predicate")) != "controlledNASelement":
        return False
    label = str(fact.get("object_label") or tail_token(fact.get("object"))).upper()
    return label in CONTROLLED_ELEMENT_TEXT_ARTIFACTS


def tail_token(value: object) -> str:
    text = str(value or "")
    if not text:
        return ""
    return text.rstrip("/#").replace("#", ":").rsplit(":", 1)[-1]


def refined_fact(fact: dict[str, Any], routed: dict[str, Any]) -> dict[str, Any]:
    return {
        **fact,
        "agentic_system_id": "S5_S6_independent_agentic_run",
        "agentic_route_module": routed["module"],
        "agentic_cq_ids": routed["cq_ids"],
        "agentic_refiner_status": "accepted_after_validator_and_critic",
    }


def agent_roles() -> list[dict[str, str]]:
    return [
        {
            "agent": "extractor",
            "input": "formal ATCSCC source records plus S0 source-derived candidates",
            "operation": "start from source-derived candidate facts without reading S4 output",
            "output": "candidate fact payloads",
        },
        {
            "agent": "validator",
            "input": "candidate fact payloads and NASA ATMONTO ATCSCC schema slice",
            "operation": "rerun schema, datatype, range, and evidence validation",
            "output": "S5 validator-accepted facts and validator rejections",
        },
        {
            "agent": "critic",
            "input": "S5 accepted facts, CQ manifest, source text, and profile heuristics",
            "operation": "flag duplicate facts, unsupported evidence, and text-artifact NAS elements",
            "output": "critic quarantine reasons",
        },
        {
            "agent": "refiner",
            "input": "critic decisions",
            "operation": "drop quarantined facts and annotate accepted facts with CQ/module routes",
            "output": "S6 refined facts for scoring",
        },
    ]


def read_jsonl_objects(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected object at {project_relative_path(path)}:{line_number}")
        records.append(payload)
    return records


def predicate_route_map(cq_manifest: dict[str, Any]) -> dict[str, dict[str, set[str]]]:
    route_map: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"cq_ids": set(), "route_labels": set(), "graph_use_decisions": set()}
    )
    for cq in cq_manifest.get("cqs", []):
        if not isinstance(cq, dict):
            continue
        for predicate in cq.get("required_predicates", []):
            key = term_name(predicate)
            route_map[key]["cq_ids"].add(str(cq.get("cq_id") or "unknown"))
            route_map[key]["route_labels"].add(str(cq.get("route_label") or "unspecified"))
            route_map[key]["graph_use_decisions"].add(
                str(cq.get("graph_use_decision") or "unspecified")
            )
    return route_map


def routed_fact(fact: dict[str, Any], route_map: dict[str, dict[str, set[str]]]) -> dict[str, Any]:
    predicate = term_name(fact.get("predicate"))
    route = route_map.get(predicate)
    return {
        "fact_id": fact.get("fact_id"),
        "source_id": fact.get("source_id"),
        "predicate": predicate,
        "cq_ids": sorted(route["cq_ids"]) if route else [],
        "route_labels": sorted(route["route_labels"]) if route else ["unmapped"],
        "graph_use_decisions": sorted(route["graph_use_decisions"]) if route else ["unmapped"],
        "module": module_label(route),
        "evidence_text": str(fact.get("evidence_text") or "")[:240],
    }


def module_label(route: dict[str, set[str]] | None) -> str:
    if route is None:
        return "unmapped_profile_fact"
    labels = route["route_labels"]
    if "deterministic" in labels:
        return "deterministic_core"
    if "validator" in labels:
        return "validator_evidence"
    if "graph" in labels:
        return "graph_query"
    if "hybrid" in labels:
        return "hybrid_semantic"
    if "abstain" in labels:
        return "abstention_control"
    return "cq_routed"


def facts_from_records(records: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    return [
        fact
        for record in records
        for fact in record.get(field, [])
        if isinstance(fact, dict)
    ]


def rounded_semantic_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "available",
        "predicted_fact_count",
        "gold_fact_count",
        "true_positive_count",
        "false_positive_count",
        "false_negative_count",
        "precision",
        "recall",
        "f1",
        "manual_semantic_correctness",
    )
    return {
        field: round(value, 4) if isinstance((value := metrics.get(field)), float) else value
        for field in fields
    }


def system_semantic_metrics(scoring: dict[str, Any], system_id: str) -> dict[str, Any]:
    for system in scoring.get("systems", []):
        if isinstance(system, dict) and system.get("system_id") == system_id:
            return rounded_semantic_metrics(system.get("semantic_metrics") or {})
    return {}


def scored_semantic_metrics(
    *,
    predictions: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
) -> dict[str, Any]:
    return rounded_semantic_metrics(
        semantic_metrics(predictions=predictions, gold_records=gold_records)
    )


def metric_delta(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    delta: dict[str, Any] = {}
    for field in ("predicted_fact_count", "true_positive_count", "precision", "recall", "f1"):
        if isinstance(after.get(field), (int, float)) and isinstance(before.get(field), (int, float)):
            value = after[field] - before[field]
            delta[field] = round(value, 4) if isinstance(value, float) else value
    return delta


def quarantine_summary(quarantine: list[dict[str, Any]]) -> dict[str, Any]:
    reason_counts: Counter[str] = Counter()
    for item in quarantine:
        for reason in item.get("reasons", []):
            reason_counts[str(reason)] += 1
    return {
        "quarantined_fact_count": len(quarantine),
        "reason_counts": dict(sorted(reason_counts.items())),
        "examples": quarantine[:10],
    }


def routing_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    module_counts: Counter[str] = Counter()
    cq_counts: Counter[str] = Counter()
    for record in records:
        for item in record.get("critic_results", []):
            if item.get("accepted"):
                module_counts[str(item["module"])] += 1
                for cq_id in item["cq_ids"]:
                    cq_counts[str(cq_id)] += 1
    return {
        "module_counts": dict(sorted(module_counts.items())),
        "cq_fact_counts": dict(sorted(cq_counts.items())),
        "unmapped_fact_count": module_counts.get("unmapped_profile_fact", 0),
    }
