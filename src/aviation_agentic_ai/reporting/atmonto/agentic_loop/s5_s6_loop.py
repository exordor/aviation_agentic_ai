from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from aviation_agentic_ai.ontology.atmonto_experiment import semantic_metrics, term_name
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import (
    normalize_report_text,
    read_json_object_or_empty,
    write_json_report,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.contract import (
    DEFAULT_CQ_MANIFEST_PATH,
)
from aviation_agentic_ai.reporting.nasa_atmonto_cq import DEFAULT_GOLD_PATH
from aviation_agentic_ai.reporting.atmonto.agentic_loop.s5_s6_loop_render import (
    write_nasa_atmonto_s5_s6_agentic_loop_markdown,
)

DEFAULT_SCORING_PATH = Path("reports/stages/nasa_atmonto_formal_experiment_scoring.json")
DEFAULT_S4_PREDICTIONS_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s4_hybrid_backbone_enrichment_predictions.jsonl"
)
DEFAULT_AGENTIC_LOOP_PATH = Path("reports/stages/nasa_atmonto_agentic_loop.json")


def build_nasa_atmonto_s5_s6_agentic_loop(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    s4_predictions_path: str | Path = DEFAULT_S4_PREDICTIONS_PATH,
    scoring_path: str | Path = DEFAULT_SCORING_PATH,
    agentic_loop_path: str | Path = DEFAULT_AGENTIC_LOOP_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    gold_records = _read_jsonl_objects(_resolve(root, gold_path))
    cq_manifest = read_json_object_or_empty(_resolve(root, cq_manifest_path))
    s4_records = _read_jsonl_objects(_resolve(root, s4_predictions_path))
    scoring = read_json_object_or_empty(_resolve(root, scoring_path))
    agentic_loop = read_json_object_or_empty(_resolve(root, agentic_loop_path))
    source_text_by_id = _source_text_by_id(gold_records)
    route_map = _predicate_route_map(cq_manifest)
    s5_facts = _prediction_facts(s4_records)
    routed_facts = [_routed_fact(fact, route_map, source_text_by_id) for fact in s5_facts]
    s6_facts = [fact for fact, routed in zip(s5_facts, routed_facts) if routed["evidence_supported"]]
    quarantined = [routed for routed in routed_facts if not routed["evidence_supported"]]
    s5_metrics = _rounded_semantic_metrics(semantic_metrics(predictions=s5_facts, gold_records=gold_records))
    s6_metrics = _rounded_semantic_metrics(semantic_metrics(predictions=s6_facts, gold_records=gold_records))
    s4_metrics = _system_semantic_metrics(scoring, "S4_hybrid_backbone_enrichment")
    return {
        "source_family": "nasa_atmonto_s5_s6_agentic_loop",
        "status": "s5_s6_agentic_evidence_gate_scored",
        "metadata": {
            "gold_path": project_relative_path(_resolve(root, gold_path), root),
            "cq_manifest_path": project_relative_path(_resolve(root, cq_manifest_path), root),
            "s4_predictions_path": project_relative_path(_resolve(root, s4_predictions_path), root),
            "scoring_path": project_relative_path(_resolve(root, scoring_path), root),
            "agentic_loop_path": project_relative_path(_resolve(root, agentic_loop_path), root),
            "input_system_id": "S4_hybrid_backbone_enrichment",
            "agentic_loop_status": agentic_loop.get("status"),
            "record_count": len(s4_records),
            "s5_fact_count": len(s5_facts),
            "s6_fact_count": len(s6_facts),
            "s5_unique_scored_fact_count": s5_metrics.get("predicted_fact_count"),
            "s6_unique_scored_fact_count": s6_metrics.get("predicted_fact_count"),
            "quarantined_fact_count": len(quarantined),
            "strict_main_metrics_changed": False,
            "independent_live_llm_run": False,
            "boundary": (
                "S5/S6 are executable artifact-driven wrappers over the current S4 output. "
                "They are not an independent live multi-agent LLM extraction run."
            ),
        },
        "stage_definitions": [
            {
                "system_id": "S5_agentic_cq_module_routed_extraction",
                "input": "S4_hybrid_backbone_enrichment accepted facts",
                "operation": "Annotate facts with CQ/module route labels from the CQ manifest.",
                "claim_boundary": "Reusable routing layer; not new semantic extraction quality by itself.",
            },
            {
                "system_id": "S6_agentic_evidence_verifier_repair",
                "input": "S5 routed facts and original ATCSCC source text",
                "operation": "Verify evidence containment and quarantine unsupported facts.",
                "claim_boundary": "Evidence gate; no unsupported value repair or profile extension is applied.",
            },
        ],
        "metrics": {
            "s4_reported_semantic_metrics": s4_metrics,
            "s5_routed_semantic_metrics": s5_metrics,
            "s6_evidence_gated_semantic_metrics": s6_metrics,
            "delta_s6_minus_s5": _metric_delta(s6_metrics, s5_metrics),
        },
        "routing_summary": _routing_summary(routed_facts),
        "evidence_gate": {
            "supported_fact_count": len(s6_facts),
            "quarantined_fact_count": len(quarantined),
            "support_rate": _safe_ratio(len(s6_facts), len(s5_facts)),
            "quarantine_examples": quarantined[:10],
        },
        "sota_interpretation": {
            "what_is_satisfied": (
                "The artifact chain now drives a concrete S5/S6 routing and evidence-verifier "
                "pass over scored ATCSCC predictions."
            ),
            "remaining_gap": (
                "A future S5/S6 run should call separate extractor, validator, critic, and refiner "
                "agents before S4-style scoring, rather than wrapping S4 outputs."
            ),
            "claim_use": (
                "Use this artifact as executable loop evidence and a bridge to S5/S6 implementation; "
                "do not cite it as an autonomous multi-agent extraction result."
            ),
        },
    }


def write_nasa_atmonto_s5_s6_agentic_loop_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_s5_s6_agentic_loop(
    *,
    output_dir: str | Path,
    report_name: str = "nasa_atmonto_s5_s6_agentic_loop",
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    s4_predictions_path: str | Path = DEFAULT_S4_PREDICTIONS_PATH,
    scoring_path: str | Path = DEFAULT_SCORING_PATH,
    agentic_loop_path: str | Path = DEFAULT_AGENTIC_LOOP_PATH,
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    result = build_nasa_atmonto_s5_s6_agentic_loop(
        repo_root=repo_root,
        gold_path=gold_path,
        cq_manifest_path=cq_manifest_path,
        s4_predictions_path=s4_predictions_path,
        scoring_path=scoring_path,
        agentic_loop_path=agentic_loop_path,
    )
    json_path = write_nasa_atmonto_s5_s6_agentic_loop_json(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_s5_s6_agentic_loop_markdown(result, output / f"{report_name}.md")
    return json_path, md_path, result


def _resolve(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _read_jsonl_objects(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected object at {project_relative_path(path)}:{line_number}")
        records.append(payload)
    return records


def _source_text_by_id(gold_records: list[dict[str, Any]]) -> dict[str, str]:
    return {
        str(record.get("source_id")): str(record.get("source_text") or "")
        for record in gold_records
        if record.get("source_id")
    }


def _prediction_facts(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for record in records:
        source_id = record.get("source_id")
        for fact in record.get("facts", []):
            if isinstance(fact, dict):
                facts.append(fact if fact.get("source_id") else {**fact, "source_id": source_id})
    return facts


def _predicate_route_map(cq_manifest: dict[str, Any]) -> dict[str, dict[str, set[str]]]:
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


def _routed_fact(
    fact: dict[str, Any],
    route_map: dict[str, dict[str, set[str]]],
    source_text_by_id: dict[str, str],
) -> dict[str, Any]:
    predicate = term_name(fact.get("predicate"))
    route = route_map.get(predicate)
    evidence = str(fact.get("evidence_text") or "")
    source_text = source_text_by_id.get(str(fact.get("source_id")), "")
    supported = bool(evidence) and normalize_report_text(evidence) in normalize_report_text(source_text)
    return {
        "fact_id": fact.get("fact_id"),
        "source_id": fact.get("source_id"),
        "predicate": predicate,
        "cq_ids": sorted(route["cq_ids"]) if route else [],
        "route_labels": sorted(route["route_labels"]) if route else ["unmapped"],
        "graph_use_decisions": sorted(route["graph_use_decisions"]) if route else ["unmapped"],
        "module": _module_label(route),
        "evidence_supported": supported,
        "evidence_text": evidence[:240],
    }


def _module_label(route: dict[str, set[str]] | None) -> str:
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


def _rounded_semantic_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
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
    rounded: dict[str, Any] = {}
    for field in fields:
        value = metrics.get(field)
        rounded[field] = round(value, 4) if isinstance(value, float) else value
    return rounded


def _system_semantic_metrics(scoring: dict[str, Any], system_id: str) -> dict[str, Any]:
    for system in scoring.get("systems", []):
        if isinstance(system, dict) and system.get("system_id") == system_id:
            return _rounded_semantic_metrics(system.get("semantic_metrics") or {})
    return {}


def _metric_delta(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    delta: dict[str, Any] = {}
    for field in ("predicted_fact_count", "true_positive_count", "precision", "recall", "f1"):
        if isinstance(after.get(field), (int, float)) and isinstance(before.get(field), (int, float)):
            value = after[field] - before[field]
            delta[field] = round(value, 4) if isinstance(value, float) else value
    return delta


def _routing_summary(routed_facts: list[dict[str, Any]]) -> dict[str, Any]:
    module_counts = Counter(str(item["module"]) for item in routed_facts)
    predicate_counts = Counter(str(item["predicate"]) for item in routed_facts)
    cq_counts: Counter[str] = Counter()
    for item in routed_facts:
        for cq_id in item["cq_ids"]:
            cq_counts[cq_id] += 1
    return {
        "module_counts": dict(sorted(module_counts.items())),
        "predicate_counts": dict(sorted(predicate_counts.items())),
        "cq_fact_counts": dict(sorted(cq_counts.items())),
        "unmapped_fact_count": module_counts.get("unmapped_profile_fact", 0),
    }


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None
