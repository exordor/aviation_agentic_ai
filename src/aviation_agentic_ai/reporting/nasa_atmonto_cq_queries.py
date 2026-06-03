from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import normalize_report_text, write_json_report
from aviation_agentic_ai.reporting.nasa_atmonto_cq import normalize_atmonto_predicate


DEFAULT_GOLD_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl")
DEFAULT_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_cq_query_templates.json")
DEFAULT_SYSTEM_PREDICTION_PATHS: dict[str, Path] = {
    "S0_rule_only": Path("data/experiments/nasa_atmonto/formal/s0_rule_only_predictions.jsonl"),
    "S2_llm_schema_slice": Path(
        "data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_predictions.jsonl"
    ),
    "S3_llm_schema_slice_validator_repair": Path(
        "data/experiments/nasa_atmonto/formal/s3_llm_schema_slice_validator_repair_predictions.jsonl"
    ),
    "S4_hybrid_backbone_enrichment": Path(
        "data/experiments/nasa_atmonto/formal/s4_hybrid_backbone_enrichment_predictions.jsonl"
    ),
}

GRAPH_USE_GATE_TEMPLATE_SYSTEMS: dict[str, str] = {
    "QT-Q01-AFFECTED-NAS-ELEMENTS": "S4_hybrid_backbone_enrichment",
    "QT-Q01-TIME-WINDOW": "S0_rule_only",
    "QT-Q01-CAUSE-CONDITION": "S4_hybrid_backbone_enrichment",
    "QT-Q01-STATUS-ACTION": "S4_hybrid_backbone_enrichment",
    "QT-Q01-ROUTE-SEMANTICS": "S4_hybrid_backbone_enrichment",
    "QT-A01-ABSTENTION-FIELDS": "S4_hybrid_backbone_enrichment",
}

QUERY_TEMPLATES: tuple[dict[str, Any], ...] = (
    {
        "id": "QT-Q01-AFFECTED-NAS-ELEMENTS",
        "cq_ids": ["CQ-Q01", "CQ-D02", "CQ-E03"],
        "question": "Which airports, ARTCCs, routes, or other NAS elements are affected by the advisory?",
        "predicates": ("controlledNASelement",),
        "answer_type": "entity_set",
        "route": "graph_template",
        "metric": "answer-set precision/recall/F1 plus evidence containment",
    },
    {
        "id": "QT-Q01-TIME-WINDOW",
        "cq_ids": ["CQ-Q01", "CQ-D03", "CQ-O01"],
        "question": "What are the effective start and end times for the advisory?",
        "predicates": ("effectiveStartTime", "effectiveEndTime"),
        "answer_type": "temporal_interval",
        "route": "graph_template",
        "metric": "time-field answer-set precision/recall/F1",
    },
    {
        "id": "QT-Q01-CAUSE-CONDITION",
        "cq_ids": ["CQ-Q01", "CQ-E02"],
        "question": "What weather, volume, runway, equipment, or other condition explains the restriction?",
        "predicates": ("impactingCondition", "impactingConditionMessage", "reRouteReason"),
        "answer_type": "condition_set",
        "route": "graph_template",
        "metric": "condition/reason answer-set precision/recall/F1",
    },
    {
        "id": "QT-Q01-STATUS-ACTION",
        "cq_ids": ["CQ-Q01", "CQ-E01"],
        "question": "What status or action is stated for the advisory?",
        "predicates": ("implementationStatus", "initiativeComments"),
        "answer_type": "status_or_comment",
        "route": "hybrid_graph_plus_source_span",
        "metric": "status/comment answer-set precision/recall/F1",
    },
    {
        "id": "QT-Q01-ROUTE-SEMANTICS",
        "cq_ids": ["CQ-Q01", "CQ-E03", "CQ-O02"],
        "question": "What reroute type, reroute reason, and constrained element are represented?",
        "predicates": ("reRouteType", "reRouteReason", "controlledNASelement"),
        "answer_type": "route_constraint_tuple",
        "route": "hybrid_graph_plus_source_span",
        "metric": "route predicate-family answer-set precision/recall/F1",
    },
    {
        "id": "QT-A01-ABSTENTION-FIELDS",
        "cq_ids": ["CQ-A01"],
        "question": "Which expected fields are absent or unsupported and should trigger abstention?",
        "predicates": (
            "effectiveEndTime",
            "extensionProbability",
            "impactingCondition",
            "reRouteReason",
            "controlledNASelement",
        ),
        "answer_type": "field_presence_and_abstention",
        "route": "critic_gate",
        "metric": "false-positive count and abstention-readiness signal",
    },
)


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


def _local_name(value: object) -> str:
    text = str(value or "").strip()
    if "#" in text:
        text = text.rsplit("#", 1)[1]
    if ":" in text:
        text = text.rsplit(":", 1)[1]
    if "/" in text:
        text = text.rsplit("/", 1)[1]
    return text


def _answer_value(fact: dict[str, Any]) -> str:
    value = fact.get("object_label")
    if value in (None, ""):
        value = fact.get("value", fact.get("object"))
    return _local_name(value)


def _answer_key(source_id: object, predicate: object, value: object) -> tuple[str, str, str]:
    return (
        str(source_id or ""),
        _predicate_name(predicate),
        normalize_report_text(value),
    )


def _predicate_name(predicate: object) -> str:
    return _local_name(normalize_atmonto_predicate(predicate))


def _fact_status_accepted(fact: dict[str, Any]) -> bool:
    status = str(fact.get("validator_status") or fact.get("status") or "").lower()
    if not status:
        return True
    return "accepted" in status and "rejected" not in status


def _gold_facts(record: dict[str, Any]) -> list[dict[str, Any]]:
    annotation = record.get("gold_annotation") if isinstance(record.get("gold_annotation"), dict) else {}
    facts: list[dict[str, Any]] = []
    for field_name, status in (("valid_facts", "accepted"), ("missing_facts", "reviewed_missing")):
        for fact in annotation.get(field_name, []) if isinstance(annotation, dict) else []:
            if isinstance(fact, dict):
                facts.append({**fact, "gold_status": status})
    return facts


def _collect_gold_answers(
    records: list[dict[str, Any]],
    predicates: tuple[str, ...],
) -> dict[tuple[str, str, str], dict[str, Any]]:
    target = {_predicate_name(predicate) for predicate in predicates}
    answers: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in records:
        source_id = record.get("source_id") or record.get("advisory_source_id")
        if not source_id:
            source_id = (record.get("gold_annotation") or {}).get("source_id")
        source_text = record.get("source_text", "")
        for fact in _gold_facts(record):
            predicate = _predicate_name(fact.get("predicate"))
            if predicate not in target:
                continue
            value = _answer_value(fact)
            key = _answer_key(fact.get("source_id") or source_id, predicate, value)
            evidence = fact.get("evidence_text", "")
            answers[key] = {
                "source_id": key[0],
                "predicate": predicate,
                "value": value,
                "evidence_text": evidence,
                "evidence_contained": bool(evidence)
                and normalize_report_text(evidence) in normalize_report_text(source_text),
                "gold_status": fact.get("gold_status"),
            }
    return answers


def _collect_system_answers(
    records: list[dict[str, Any]],
    predicates: tuple[str, ...],
) -> dict[tuple[str, str, str], dict[str, Any]]:
    target = {_predicate_name(predicate) for predicate in predicates}
    answers: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in records:
        facts = record.get("facts")
        if not isinstance(facts, list):
            facts = record.get("candidate_facts", [])
        for fact in facts:
            if not isinstance(fact, dict) or not _fact_status_accepted(fact):
                continue
            predicate = _predicate_name(fact.get("predicate"))
            if predicate not in target:
                continue
            value = _answer_value(fact)
            key = _answer_key(fact.get("source_id") or record.get("source_id"), predicate, value)
            answers[key] = {
                "source_id": key[0],
                "predicate": predicate,
                "value": value,
                "evidence_text": fact.get("evidence_text", ""),
                "fact_id": fact.get("fact_id"),
            }
    return answers


def _score_answer_sets(
    gold_answers: dict[tuple[str, str, str], dict[str, Any]],
    predicted_answers: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, Any]:
    gold_keys = set(gold_answers)
    predicted_keys = set(predicted_answers)
    true_positive = len(gold_keys & predicted_keys)
    false_positive = len(predicted_keys - gold_keys)
    false_negative = len(gold_keys - predicted_keys)
    precision = true_positive / len(predicted_keys) if predicted_keys else None
    recall = true_positive / len(gold_keys) if gold_keys else None
    f1 = None
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    predicted_with_evidence = sum(
        1 for answer in predicted_answers.values() if normalize_report_text(answer.get("evidence_text"))
    )
    return {
        "gold_answer_count": len(gold_keys),
        "predicted_answer_count": len(predicted_keys),
        "true_positive_count": true_positive,
        "false_positive_count": false_positive,
        "false_negative_count": false_negative,
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "f1": round(f1, 4) if f1 is not None else None,
        "predicted_evidence_coverage": round(predicted_with_evidence / len(predicted_keys), 4)
        if predicted_keys
        else None,
    }


def build_cq_query_manifest() -> dict[str, Any]:
    return {
        "source_family": "nasa_atmonto_cq_query_manifest",
        "status": "query_templates_ready",
        "metadata": {
            "template_count": len(QUERY_TEMPLATES),
            "boundary": "Retrospective FAA ATCSCC advisory KG queries only; no live operational use.",
        },
        "templates": [
            {
                **template,
                "predicates": list(template["predicates"]),
                "pseudo_sparql": _pseudo_sparql(template),
                "graph_pattern": _graph_pattern(template),
            }
            for template in QUERY_TEMPLATES
        ],
    }


def _pseudo_sparql(template: dict[str, Any]) -> str:
    values = " ".join(f"atm:{predicate}" for predicate in template["predicates"])
    return (
        "SELECT ?advisory ?predicate ?answer ?evidence WHERE {\n"
        f"  VALUES ?predicate {{ {values} }}\n"
        "  ?advisory ?predicate ?answer .\n"
        "  OPTIONAL { ?statement prov:wasDerivedFrom ?evidence . }\n"
        "}"
    )


def _graph_pattern(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "subject": "ATCSCC advisory/TMI node",
        "predicates": [f"atm:{predicate}" for predicate in template["predicates"]],
        "object": template["answer_type"],
        "required_provenance": True,
        "route": template["route"],
    }


def build_nasa_atmonto_cq_query_evaluation(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    system_prediction_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    gold_file = _resolve(root, gold_path)
    system_paths = system_prediction_paths or DEFAULT_SYSTEM_PREDICTION_PATHS
    gold_records = _read_jsonl_objects(gold_file)
    systems = {
        system_id: _read_jsonl_objects(_resolve(root, path))
        for system_id, path in system_paths.items()
        if _resolve(root, path).exists()
    }
    manifest = build_cq_query_manifest()

    template_results: list[dict[str, Any]] = []
    aggregate_by_system: dict[str, list[dict[str, Any]]] = {system_id: [] for system_id in systems}
    for template in manifest["templates"]:
        predicates = tuple(str(predicate) for predicate in template["predicates"])
        gold_answers = _collect_gold_answers(gold_records, predicates)
        system_results = []
        for system_id, records in systems.items():
            predicted_answers = _collect_system_answers(records, predicates)
            metrics = _score_answer_sets(gold_answers, predicted_answers)
            aggregate_by_system[system_id].append(metrics)
            system_results.append(
                {
                    "system_id": system_id,
                    "metrics": metrics,
                    "answer_quality_status": _answer_quality_status(metrics),
                }
            )
        template_results.append(
            {
                "template_id": template["id"],
                "cq_ids": template["cq_ids"],
                "question": template["question"],
                "predicates": list(predicates),
                "gold_answer_count": len(gold_answers),
                "system_results": system_results,
            }
        )

    return {
        "source_family": "nasa_atmonto_cq_query_evaluation",
        "status": "cq_query_answer_quality_ready",
        "metadata": {
            "gold_path": project_relative_path(gold_file, root),
            "system_prediction_paths": {
                system_id: project_relative_path(_resolve(root, path), root)
                for system_id, path in system_paths.items()
                if _resolve(root, path).exists()
            },
            "system_count": len(systems),
            "template_count": len(template_results),
            "aggregation_policy": "template_weighted_predicate_answers",
            "boundary": "Deterministic answer-set evaluation only; LLM answer generation is not run.",
        },
        "query_manifest": manifest,
        "template_results": template_results,
        "aggregate_by_system": {
            system_id: _aggregate_metrics(metrics) for system_id, metrics in aggregate_by_system.items()
        },
        "graph_use_gate_proxy": _graph_use_gate_proxy(template_results),
        "graphrag_answer_quality": {
            "evaluation_layer": "pre_generation_answer_set_quality",
            "llm_generation_status": "not_run",
            "claim_boundary": (
                "This artifact measures whether graph/query outputs can recover source-bounded "
                "CQ answers with evidence. It does not claim generated-answer superiority."
            ),
        },
    }


def _graph_use_gate_proxy(template_results: list[dict[str, Any]]) -> dict[str, Any]:
    selected_metrics: list[dict[str, Any]] = []
    selected_templates: list[dict[str, Any]] = []
    for template in template_results:
        template_id = str(template["template_id"])
        selected_system = GRAPH_USE_GATE_TEMPLATE_SYSTEMS.get(
            template_id, "S4_hybrid_backbone_enrichment"
        )
        system_result = next(
            (
                item
                for item in template["system_results"]
                if item["system_id"] == selected_system
            ),
            None,
        )
        if system_result is None:
            continue
        metrics = system_result["metrics"]
        selected_metrics.append(metrics)
        selected_templates.append(
            {
                "template_id": template_id,
                "selected_system": selected_system,
                "cq_ids": template["cq_ids"],
                "question": template["question"],
                "metrics": metrics,
                "reason": _graph_use_gate_reason(template_id, selected_system),
            }
        )
    return {
        "status": "deterministic_queryability_proxy",
        "policy": (
            "select deterministic S0 for direct temporal fields and S4 hybrid "
            "backbone-enrichment for entity, cause, status, route, and abstention templates"
        ),
        "selected_templates": selected_templates,
        "aggregate": _aggregate_metrics(selected_metrics),
        "boundary": (
            "This is an answer-set/queryability proxy over existing system outputs, not a live "
            "vector or graph retriever run."
        ),
    }


def _graph_use_gate_reason(template_id: str, selected_system: str) -> str:
    if selected_system == "S0_rule_only":
        return "direct deterministic field; graph expansion is unnecessary"
    if template_id == "QT-A01-ABSTENTION-FIELDS":
        return "use S4 critic-gated hybrid facts to expose missing or unsupported fields"
    return "relation-heavy or semantic field; use S4 hybrid backbone enrichment"


def _answer_quality_status(metrics: dict[str, Any]) -> str:
    if not metrics["gold_answer_count"]:
        return "no_gold_answers"
    f1 = metrics.get("f1")
    if f1 is None:
        return "no_predicted_answers"
    if float(f1) >= 0.7 and metrics.get("predicted_evidence_coverage") == 1.0:
        return "ready_for_answer_generation"
    if float(f1) >= 0.4:
        return "usable_with_review"
    return "needs_retrieval_or_extraction_review"


def _aggregate_metrics(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(metrics) or 1
    totals = Counter()
    f1_values = []
    for metric in metrics:
        for key in (
            "gold_answer_count",
            "predicted_answer_count",
            "true_positive_count",
            "false_positive_count",
            "false_negative_count",
        ):
            totals[key] += int(metric.get(key) or 0)
        if metric.get("f1") is not None:
            f1_values.append(float(metric["f1"]))
    precision = totals["true_positive_count"] / totals["predicted_answer_count"] if totals["predicted_answer_count"] else None
    recall = totals["true_positive_count"] / totals["gold_answer_count"] if totals["gold_answer_count"] else None
    f1 = None
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    return {
        **dict(totals),
        "micro_precision": round(precision, 4) if precision is not None else None,
        "micro_recall": round(recall, 4) if recall is not None else None,
        "micro_f1": round(f1, 4) if f1 is not None else None,
        "macro_f1": round(sum(f1_values) / denominator, 4) if f1_values else None,
    }


def write_cq_query_manifest_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ATCSCC CQ Query Manifest",
        "",
        f"- Status: `{result['status']}`",
        f"- Templates: {result['metadata']['template_count']}",
        f"- Boundary: {result['metadata']['boundary']}",
        "",
        "| Template | CQs | Route | Predicates | Metric |",
        "| --- | --- | --- | --- | --- |",
    ]
    for template in result["templates"]:
        lines.append(
            f"| `{template['id']}` | {', '.join(template['cq_ids'])} | "
            f"`{template['route']}` | {', '.join(f'`{p}`' for p in template['predicates'])} | "
            f"{template['metric']} |"
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_cq_query_evaluation_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO CQ Query and Answer-Quality Evaluation",
        "",
        "## Scope",
        "",
        f"- Gold set: `{result['metadata']['gold_path']}`",
        f"- Boundary: {result['metadata']['boundary']}",
        f"- GraphRAG layer: {result['graphrag_answer_quality']['evaluation_layer']}",
        f"- LLM generation: `{result['graphrag_answer_quality']['llm_generation_status']}`",
        "",
        "## Aggregate by System",
        "",
        "| System | Gold answers | Predicted | TP | FP | FN | Micro P | Micro R | Micro F1 | Macro F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for system_id, metrics in result["aggregate_by_system"].items():
        lines.append(
            f"| `{system_id}` | {metrics['gold_answer_count']} | {metrics['predicted_answer_count']} | "
            f"{metrics['true_positive_count']} | {metrics['false_positive_count']} | "
            f"{metrics['false_negative_count']} | {metrics['micro_precision']} | "
            f"{metrics['micro_recall']} | {metrics['micro_f1']} | {metrics['macro_f1']} |"
        )
    lines.extend(["", "## Template Results", ""])
    for template in result["template_results"]:
        lines.extend(
            [
                f"### {template['template_id']}",
                "",
                f"- Question: {template['question']}",
                f"- CQs: {', '.join(template['cq_ids'])}",
                f"- Predicates: {', '.join(f'`{p}`' for p in template['predicates'])}",
                f"- Gold answers: {template['gold_answer_count']}",
                "",
                "| System | P | R | F1 | Evidence coverage | Status |",
                "| --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for system in template["system_results"]:
            metrics = system["metrics"]
            lines.append(
                f"| `{system['system_id']}` | {metrics['precision']} | {metrics['recall']} | "
                f"{metrics['f1']} | {metrics['predicted_evidence_coverage']} | "
                f"`{system['answer_quality_status']}` |"
            )
        lines.append("")
    lines.extend(
        [
            "## S7 Graph-Use Gate Proxy",
            "",
            f"- Status: `{result['graph_use_gate_proxy']['status']}`",
            f"- Policy: {result['graph_use_gate_proxy']['policy']}",
            f"- Boundary: {result['graph_use_gate_proxy']['boundary']}",
            "",
            "| Template | Selected system | P | R | F1 | Reason |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for template in result["graph_use_gate_proxy"]["selected_templates"]:
        metrics = template["metrics"]
        lines.append(
            f"| `{template['template_id']}` | `{template['selected_system']}` | "
            f"{metrics['precision']} | {metrics['recall']} | {metrics['f1']} | "
            f"{template['reason']} |"
        )
    aggregate = result["graph_use_gate_proxy"]["aggregate"]
    lines.extend(
        [
            "",
            (
                f"Aggregate routed proxy micro-F1: {aggregate['micro_f1']} "
                f"(P={aggregate['micro_precision']}, R={aggregate['micro_recall']})."
            ),
            "",
            "## Claim Boundary",
            "",
            result["graphrag_answer_quality"]["claim_boundary"],
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_nasa_atmonto_cq_query_evaluation(
    *,
    output_dir: str | Path,
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    report_name: str = "nasa_atmonto_cq_query_evaluation",
    system_prediction_paths: dict[str, str | Path] | None = None,
) -> tuple[Path, Path, Path, Path, dict[str, Any]]:
    root = Path(repo_root)
    output = Path(output_dir)
    result = build_nasa_atmonto_cq_query_evaluation(
        repo_root=root,
        gold_path=gold_path,
        system_prediction_paths=system_prediction_paths,
    )
    manifest_file = _resolve(root, manifest_path)
    manifest_md = manifest_file.with_suffix(".md")
    write_json_report(result["query_manifest"], manifest_file, sort_keys=False)
    write_cq_query_manifest_markdown(result["query_manifest"], manifest_md)
    stem = Path(report_name).stem or "nasa_atmonto_cq_query_evaluation"
    json_path = write_json_report(result, output / f"{stem}.json", sort_keys=False)
    md_path = write_cq_query_evaluation_markdown(result, output / f"{stem}.md")
    return json_path, md_path, manifest_file, manifest_md, result
