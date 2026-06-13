from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import (
    normalize_report_text,
    read_json_object_or_empty,
    write_json_report,
)


DEFAULT_GOLD_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl")
DEFAULT_SCORING_PATH = Path("reports/stages/nasa_atmonto_formal_experiment_scoring.json")
DEFAULT_SEMANTIC_GROUPS_PATH = Path("reports/stages/nasa_atmonto_gold_semantic_groups.json")
DEFAULT_REJECTION_ADJUDICATION_PATH = Path(
    "reports/stages/nasa_atmonto_rejection_adjudication.json"
)

CQ_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "CQ-D01",
        "role": "Domain typing",
        "evaluation_status": "partially_measurable_now",
        "coverage_scope": "records",
        "predicates": (),
        "gold_fields": ("candidate_subject_class", "subject_class", "advisoryNumber"),
        "metric": "primary type coverage plus advisory-number property metrics",
        "gap": "Per-system primary-class accuracy is not yet scored as a first-class metric.",
        "layer": "S0, S1b, S2, S3, S4, validator",
    },
    {
        "id": "CQ-D02",
        "role": "Entity role",
        "evaluation_status": "directly_measurable_now",
        "predicates": ("controlledNASelement",),
        "gold_fields": ("predicate", "object", "object_class", "evidence_text", "source_id"),
        "metric": "role-aware controlled-element precision/recall/F1 and profile-gap rate",
        "gap": "ARTCC controlled-element facts remain profile gaps until a reviewed bridge exists.",
        "layer": "S0 parser, entity canonicalizer, S2/S4 enrichment, validator",
    },
    {
        "id": "CQ-D03",
        "role": "Temporal semantics",
        "evaluation_status": "directly_measurable_now",
        "predicates": ("issuedTime", "effectiveStartTime", "effectiveEndTime"),
        "gold_fields": ("normalized_value", "raw_time_string", "evidence_text", "source_id"),
        "metric": "normalized-time precision/recall/F1 and fabricated-time false positives",
        "gap": "The report can score exact values but does not yet isolate rollover-specific errors.",
        "layer": "S0 time normalizer, S1b canonicalizer, S2/S3/S4",
    },
    {
        "id": "CQ-E01",
        "role": "Status/action",
        "evaluation_status": "directly_measurable_now",
        "predicates": ("implementationStatus", "initiativeComments"),
        "gold_fields": ("status_value", "action_cue", "initiativeComments", "evidence_text"),
        "metric": "status/action predicate F1 and active-overclaim false positives",
        "gap": "Status labels are sparse, so comments evidence remains important context.",
        "layer": "S0, S2, S3, S4",
    },
    {
        "id": "CQ-E02",
        "role": "Cause/condition",
        "evaluation_status": "directly_measurable_now",
        "predicates": (
            "impactingCondition",
            "impactingConditionMessage",
            "initiativeComments",
            "reRouteReason",
        ),
        "gold_fields": ("condition_label", "raw_cause_text", "evidence_text", "comments"),
        "metric": "cause/condition macro-F1 and unsupported-cause rate",
        "gap": "Some source-supported causes remain outside the current controlled vocabulary.",
        "layer": "S2/S3/S4 enrichment, enum canonicalizer, gold review",
    },
    {
        "id": "CQ-E03",
        "role": "Route/airspace semantics",
        "evaluation_status": "directly_measurable_now",
        "predicates": ("reRouteType", "reRouteReason", "controlledNASelement", "initiativeComments"),
        "gold_fields": ("primary_type", "route_element", "reRouteType", "reRouteReason", "evidence_text"),
        "metric": "reroute predicate-family F1 and constrained-element F1",
        "gap": "AFP/CTOP semantics remain deferred unless the profile and sample support them.",
        "layer": "S2/S3/S4, validator/repair",
    },
    {
        "id": "CQ-O01",
        "role": "Core conformance",
        "evaluation_status": "directly_measurable_now",
        "predicates": ("advisoryNumber", "issuedTime", "effectiveStartTime", "effectiveEndTime"),
        "gold_fields": ("fact_id", "predicate", "datatype", "evidence_text", "validator_status"),
        "metric": "schema violation rate, repair success, and required-core-field coverage",
        "gap": "Schema conformance is separate from semantic support and must not be treated as truth.",
        "layer": "validator/repair, S3, S4",
    },
    {
        "id": "CQ-O02",
        "role": "Type-specific conformance",
        "evaluation_status": "directly_measurable_now",
        "predicates": (
            "extensionProbability",
            "reRouteType",
            "reRouteReason",
            "impactingConditionMessage",
        ),
        "gold_fields": ("primary_type", "typed_predicates", "raw_value", "validator_errors"),
        "metric": "type-specific violation rate and profile-gap count",
        "gap": "Accepted profile extensions require reviewed ontology/profile changes.",
        "layer": "schema-slice LLM, validator/repair, S4",
    },
    {
        "id": "CQ-P01",
        "role": "Evidence coverage",
        "evaluation_status": "directly_measurable_now",
        "coverage_scope": "all_gold_facts",
        "predicates": (),
        "gold_fields": ("source_id", "evidence_text", "source_system_id", "fact_id"),
        "metric": "evidence containment coverage for accepted and reviewed missing facts",
        "gap": "The current contract stores evidence text, not stable character offsets.",
        "layer": "S0/S2/S3/S4, evidence checker",
    },
    {
        "id": "CQ-P02",
        "role": "Evidence support",
        "evaluation_status": "directly_measurable_now",
        "coverage_scope": "all_gold_facts",
        "predicates": (),
        "gold_fields": ("target_value", "evidence_text", "invalid_candidate_fact_ids"),
        "metric": "semantic precision, unsupported-triple rate, and rejected-fact adjudication counts",
        "gap": "Value-support judgement remains a reviewed semantic metric, not pure SHACL validation.",
        "layer": "gold review, adversarial validator review, S4 diagnostics",
    },
    {
        "id": "CQ-Q01",
        "role": "Source-bounded queryability",
        "evaluation_status": "partially_measurable_now",
        "predicates": (
            "controlledNASelement",
            "impactingCondition",
            "effectiveStartTime",
            "effectiveEndTime",
            "implementationStatus",
        ),
        "gold_fields": ("query_target_fields", "returned_advisory_ids", "citations", "evidence_text"),
        "metric": "query-field coverage now; answer-set precision/recall after query materialization",
        "gap": "Template graph queries over the frozen KG are not yet materialized as a scored artifact.",
        "layer": "graph materialization, graph query, later GraphRAG layer",
    },
    {
        "id": "CQ-A01",
        "role": "Abstention",
        "evaluation_status": "partially_measurable_now",
        "predicates": (
            "effectiveEndTime",
            "extensionProbability",
            "impactingCondition",
            "reRouteReason",
            "controlledNASelement",
        ),
        "gold_fields": ("field_present", "explicitness_label", "evidence_text", "missing_fact_notes"),
        "metric": "absent-field false positives and abstention correctness",
        "gap": "The gold set exposes false positives, but explicit absent-field labels need a follow-up pass.",
        "layer": "S1b/S2/S3/S4, sufficiency/abstention layer",
    },
)


def normalize_atmonto_predicate(predicate: object) -> str:
    value = str(predicate or "").strip()
    if value.startswith("atm:"):
        return value.split(":", 1)[1]
    return value


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


def _gold_facts(record: dict[str, Any]) -> list[dict[str, Any]]:
    annotation = record.get("gold_annotation") if isinstance(record.get("gold_annotation"), dict) else {}
    facts: list[dict[str, Any]] = []
    for field_name, status in (("valid_facts", "accepted"), ("missing_facts", "reviewed_missing")):
        for fact in annotation.get(field_name, []) if isinstance(annotation, dict) else []:
            if isinstance(fact, dict):
                facts.append({**fact, "gold_status": status})
    return facts


def _contains_evidence(source_text: object, evidence_text: object) -> bool:
    evidence = normalize_report_text(evidence_text)
    if not evidence:
        return False
    return evidence in normalize_report_text(source_text)


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def _round_metric(value: object) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def _build_gold_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    class_counts = Counter(str(record.get("candidate_subject_class", "")) for record in records)
    predicate_counts: Counter[str] = Counter()
    accepted_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    rejected_counts: Counter[str] = Counter()
    records_by_predicate: dict[str, set[str]] = {}
    evidence_checked = 0
    evidence_contained = 0
    evidence_missing = 0
    invalid_candidate_fact_count = 0
    rejected_adjudication_count = 0
    reviewed_records = 0

    for record in records:
        annotation = record.get("gold_annotation") if isinstance(record.get("gold_annotation"), dict) else {}
        if annotation.get("annotation_status") == "reviewed":
            reviewed_records += 1
        invalid_candidate_fact_count += len(annotation.get("invalid_candidate_fact_ids", []))
        source_text = record.get("source_text", "")
        record_predicates: set[str] = set()
        for fact in _gold_facts(record):
            predicate = normalize_atmonto_predicate(fact.get("predicate"))
            if not predicate:
                continue
            predicate_counts[predicate] += 1
            record_predicates.add(predicate)
            if fact["gold_status"] == "accepted":
                accepted_counts[predicate] += 1
            else:
                missing_counts[predicate] += 1
            evidence_text = fact.get("evidence_text")
            if evidence_text:
                evidence_checked += 1
                if _contains_evidence(source_text, evidence_text):
                    evidence_contained += 1
            else:
                evidence_missing += 1
        for predicate in record_predicates:
            records_by_predicate.setdefault(predicate, set()).add(str(record.get("sample_id", "")))
        for fact in annotation.get("rejected_fact_adjudications", []):
            if isinstance(fact, dict):
                predicate = normalize_atmonto_predicate(fact.get("predicate"))
                rejected_counts[predicate] += 1
                rejected_adjudication_count += 1

    return {
        "records_total": len(records),
        "reviewed_records": reviewed_records,
        "candidate_subject_class_counts": _counter_dict(class_counts),
        "gold_fact_count": sum(predicate_counts.values()),
        "accepted_gold_fact_count": sum(accepted_counts.values()),
        "reviewed_missing_fact_count": sum(missing_counts.values()),
        "predicate_counts": _counter_dict(predicate_counts),
        "accepted_predicate_counts": _counter_dict(accepted_counts),
        "reviewed_missing_predicate_counts": _counter_dict(missing_counts),
        "record_counts_by_predicate": dict(
            sorted((predicate, len(sample_ids)) for predicate, sample_ids in records_by_predicate.items())
        ),
        "invalid_candidate_fact_count": invalid_candidate_fact_count,
        "rejected_adjudication_count": rejected_adjudication_count,
        "rejected_predicate_counts": _counter_dict(rejected_counts),
        "evidence": {
            "checked_fact_count": evidence_checked,
            "contained_fact_count": evidence_contained,
            "not_contained_fact_count": evidence_checked - evidence_contained,
            "missing_evidence_fact_count": evidence_missing,
            "containment_rate": _rate(evidence_contained, evidence_checked),
        },
    }


def _predicate_metrics_by_system(scoring: dict[str, Any], predicates: tuple[str, ...]) -> list[dict[str, Any]]:
    if not predicates:
        return []
    target = {normalize_atmonto_predicate(predicate) for predicate in predicates}
    systems: list[dict[str, Any]] = []
    for system in scoring.get("systems", []):
        if not isinstance(system, dict):
            continue
        predicate_metrics = {
            normalize_atmonto_predicate(item.get("predicate")): item
            for item in system.get("property_level_semantic_metrics", [])
            if isinstance(item, dict)
        }
        selected = [predicate_metrics[predicate] for predicate in sorted(target) if predicate in predicate_metrics]
        if not selected:
            continue
        predicted = sum(int(item.get("predicted_fact_count") or 0) for item in selected)
        gold = sum(int(item.get("gold_fact_count") or 0) for item in selected)
        true_positive = sum(int(item.get("true_positive_count") or 0) for item in selected)
        false_positive = sum(int(item.get("false_positive_count") or 0) for item in selected)
        false_negative = sum(int(item.get("false_negative_count") or 0) for item in selected)
        precision = _rate(true_positive, predicted)
        recall = _rate(true_positive, gold)
        f1 = None
        if precision is not None and recall is not None and precision + recall > 0:
            f1 = round(2 * precision * recall / (precision + recall), 4)
        systems.append(
            {
                "system_id": system.get("system_id", ""),
                "label": system.get("label", ""),
                "available": bool(system.get("available")),
                "predicates_evaluated": [item.get("predicate", "") for item in selected],
                "predicted_fact_count": predicted,
                "gold_fact_count": gold,
                "true_positive_count": true_positive,
                "false_positive_count": false_positive,
                "false_negative_count": false_negative,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )
    return systems


def _best_system(metrics: list[dict[str, Any]]) -> dict[str, Any] | None:
    scored = [metric for metric in metrics if metric.get("f1") is not None]
    if not scored:
        return None
    best = max(scored, key=lambda metric: (float(metric.get("f1") or 0.0), metric.get("system_id", "")))
    return {
        "system_id": best["system_id"],
        "label": best["label"],
        "precision": best["precision"],
        "recall": best["recall"],
        "f1": best["f1"],
    }


def _predicate_gold_coverage(
    gold_summary: dict[str, Any],
    predicates: tuple[str, ...],
    *,
    coverage_scope: str = "predicates",
) -> dict[str, Any]:
    if coverage_scope == "all_gold_facts":
        return {
            "coverage_scope": coverage_scope,
            "predicates": [],
            "gold_fact_count": int(gold_summary["gold_fact_count"]),
            "record_count": int(gold_summary["records_total"]),
            "predicate_counts": {"all_gold_facts": int(gold_summary["gold_fact_count"])},
        }
    if coverage_scope == "records":
        return {
            "coverage_scope": coverage_scope,
            "predicates": [],
            "gold_fact_count": int(gold_summary["records_total"]),
            "record_count": int(gold_summary["records_total"]),
            "predicate_counts": {"records": int(gold_summary["records_total"])},
        }
    normalized = [normalize_atmonto_predicate(predicate) for predicate in predicates]
    predicate_counts = gold_summary["predicate_counts"]
    record_counts = gold_summary["record_counts_by_predicate"]
    return {
        "coverage_scope": coverage_scope,
        "predicates": normalized,
        "gold_fact_count": sum(int(predicate_counts.get(predicate, 0)) for predicate in normalized),
        "record_count": None,
        "predicate_record_count_sum": sum(
            int(record_counts.get(predicate, 0)) for predicate in normalized
        ),
        "predicate_counts": {
            predicate: int(predicate_counts.get(predicate, 0)) for predicate in normalized
        },
    }


def build_nasa_atmonto_cq_evaluation(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    scoring_path: str | Path = DEFAULT_SCORING_PATH,
    semantic_groups_path: str | Path = DEFAULT_SEMANTIC_GROUPS_PATH,
    rejection_adjudication_path: str | Path = DEFAULT_REJECTION_ADJUDICATION_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    gold_file = root / gold_path
    scoring_file = root / scoring_path
    semantic_groups_file = root / semantic_groups_path
    rejection_file = root / rejection_adjudication_path

    records = _read_jsonl_objects(gold_file)
    scoring = read_json_object_or_empty(scoring_file)
    semantic_groups = read_json_object_or_empty(semantic_groups_file)
    rejection = read_json_object_or_empty(rejection_file)
    gold_summary = _build_gold_summary(records)

    cq_evaluations = []
    for definition in CQ_DEFINITIONS:
        predicates = tuple(str(predicate) for predicate in definition["predicates"])
        system_metrics = _predicate_metrics_by_system(scoring, predicates)
        cq_evaluations.append(
            {
                **definition,
                "predicates": list(predicates),
                "gold_coverage": _predicate_gold_coverage(
                    gold_summary,
                    predicates,
                    coverage_scope=str(definition.get("coverage_scope", "predicates")),
                ),
                "system_metrics": system_metrics,
                "best_system": _best_system(system_metrics),
            }
        )

    status_counts = Counter(item["evaluation_status"] for item in cq_evaluations)
    return {
        "source_family": "nasa_atmonto_cq_evaluation",
        "status": "cq_evaluation_mapping_ready",
        "metadata": {
            "cq_count": len(cq_evaluations),
            "gold_path": project_relative_path(gold_file, root),
            "scoring_path": project_relative_path(scoring_file, root),
            "semantic_groups_path": project_relative_path(semantic_groups_file, root),
            "rejection_adjudication_path": project_relative_path(rejection_file, root),
            "boundary": "Retrospective FAA ATCSCC advisory extraction only; no live operational use.",
        },
        "evaluation_status_counts": _counter_dict(status_counts),
        "gold_summary": gold_summary,
        "scoring_summary": {
            "status": scoring.get("status"),
            "system_count": len(scoring.get("systems", [])),
            "overall_system_metrics": [
                {
                    "system_id": system.get("system_id", ""),
                    "label": system.get("label", ""),
                    "available": bool(system.get("available")),
                    "precision": _round_metric((system.get("semantic_metrics") or {}).get("precision")),
                    "recall": _round_metric((system.get("semantic_metrics") or {}).get("recall")),
                    "f1": _round_metric((system.get("semantic_metrics") or {}).get("f1")),
                    "scoring_validity": (system.get("semantic_metrics") or {}).get("scoring_validity"),
                }
                for system in scoring.get("systems", [])
                if isinstance(system, dict)
            ],
        },
        "semantic_group_summary": {
            "status": semantic_groups.get("status"),
            "semantic_group_count": semantic_groups.get("semantic_group_count"),
            "record_count": semantic_groups.get("record_count"),
            "groups": [
                {
                    "group_id": group.get("group_id", ""),
                    "label": group.get("label", ""),
                    "record_count": group.get("record_count", 0),
                }
                for group in semantic_groups.get("groups", [])
                if isinstance(group, dict)
            ],
        },
        "rejection_summary": {
            "property_level_complete": bool(rejection.get("property_level_complete")),
            "rejected_fact_count": rejection.get("rejected_fact_count"),
            "pending_fact_count": rejection.get("pending_fact_count"),
            "decision_counts_by_fact": rejection.get("decision_counts_by_fact", {}),
        },
        "cq_evaluations": cq_evaluations,
        "next_steps": [
            "Add primary-class accuracy scoring for CQ-D01 instead of relying on class coverage.",
            "Materialize frozen-snapshot template queries for CQ-Q01 and score answer-set precision/recall.",
            "Add explicit absent-field labels or derived negative examples for CQ-A01 abstention correctness.",
            "Keep ARTCC controlled-element profile gaps separate from accepted facts until a reviewed bridge exists.",
        ],
    }


def write_nasa_atmonto_cq_evaluation_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_cq_evaluation_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = result["metadata"]
    gold = result["gold_summary"]
    evidence = gold["evidence"]
    lines = [
        "# NASA ATMONTO CQ Evaluation Mapping",
        "",
        "## Scope",
        "",
        f"- Gold set: `{metadata['gold_path']}`",
        f"- Scoring report: `{metadata['scoring_path']}`",
        f"- Semantic groups: `{metadata['semantic_groups_path']}`",
        f"- Rejection adjudication: `{metadata['rejection_adjudication_path']}`",
        f"- Boundary: {metadata['boundary']}",
        "",
        "## Gold Coverage Snapshot",
        "",
        f"- Reviewed records: {gold['reviewed_records']}/{gold['records_total']}",
        f"- Gold facts: {gold['gold_fact_count']} "
        f"({gold['accepted_gold_fact_count']} accepted, "
        f"{gold['reviewed_missing_fact_count']} reviewed missing)",
        f"- Invalid candidate facts: {gold['invalid_candidate_fact_count']}",
        f"- Rejected-fact adjudications: {gold['rejected_adjudication_count']}",
        f"- Evidence containment: {evidence['contained_fact_count']}/"
        f"{evidence['checked_fact_count']} checked "
        f"({evidence['containment_rate']})",
        "",
        "### Candidate Subject Classes",
        "",
        "| Class | Records |",
        "| --- | ---: |",
    ]
    for class_name, count in gold["candidate_subject_class_counts"].items():
        lines.append(f"| `{class_name}` | {count} |")

    lines.extend(
        [
            "",
            "### Top Gold Predicates",
            "",
            "| Predicate | Gold facts | Accepted | Reviewed missing | Records |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    accepted = gold["accepted_predicate_counts"]
    missing = gold["reviewed_missing_predicate_counts"]
    record_counts = gold["record_counts_by_predicate"]
    for predicate, count in list(gold["predicate_counts"].items())[:20]:
        lines.append(
            f"| `{predicate}` | {count} | {accepted.get(predicate, 0)} | "
            f"{missing.get(predicate, 0)} | {record_counts.get(predicate, 0)} |"
        )

    lines.extend(
        [
            "",
            "## CQ Evaluation Matrix",
            "",
            "| CQ | Role | Status | Gold coverage | Best current system | F1 | Main gap |",
            "| --- | --- | --- | ---: | --- | ---: | --- |",
        ]
    )
    for cq in result["cq_evaluations"]:
        best = cq.get("best_system") or {}
        best_label = best.get("system_id", "n/a")
        best_f1 = best.get("f1")
        f1_text = "n/a" if best_f1 is None else str(best_f1)
        lines.append(
            f"| `{cq['id']}` | {cq['role']} | `{cq['evaluation_status']}` | "
            f"{cq['gold_coverage']['gold_fact_count']} | `{best_label}` | {f1_text} | "
            f"{cq['gap']} |"
        )

    lines.extend(["", "## System-Level Metrics", ""])
    for system in result["scoring_summary"]["overall_system_metrics"]:
        lines.append(
            f"- `{system['system_id']}`: precision={system['precision']}, "
            f"recall={system['recall']}, f1={system['f1']}, "
            f"validity=`{system['scoring_validity']}`"
        )

    lines.extend(
        [
            "",
            "## Rejection Boundary",
            "",
            f"- Property-level complete: {result['rejection_summary']['property_level_complete']}",
            f"- Rejected facts: {result['rejection_summary']['rejected_fact_count']}",
            f"- Pending facts: {result['rejection_summary']['pending_fact_count']}",
            f"- Decisions: `{json.dumps(result['rejection_summary']['decision_counts_by_fact'], sort_keys=True)}`",
            "",
            "## Next Experiment Steps",
            "",
        ]
    )
    lines.extend(f"- {step}" for step in result["next_steps"])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_cq_evaluation(
    *,
    output_dir: str | Path,
    report_name: str = "nasa_atmonto_cq_evaluation",
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    scoring_path: str | Path = DEFAULT_SCORING_PATH,
    semantic_groups_path: str | Path = DEFAULT_SEMANTIC_GROUPS_PATH,
    rejection_adjudication_path: str | Path = DEFAULT_REJECTION_ADJUDICATION_PATH,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_cq_evaluation(
        repo_root=repo_root,
        gold_path=gold_path,
        scoring_path=scoring_path,
        semantic_groups_path=semantic_groups_path,
        rejection_adjudication_path=rejection_adjudication_path,
    )
    output = Path(output_dir)
    json_path = write_nasa_atmonto_cq_evaluation_json(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_cq_evaluation_markdown(result, output / f"{report_name}.md")
    return json_path, md_path, result
