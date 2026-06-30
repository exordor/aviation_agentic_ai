"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from collections import Counter
from pathlib import Path
import json
from hashlib import sha1

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path

from ._io import (
    ceil_div,
    compact_text,
    read_json,
    read_jsonl,
    read_jsonl_lenient,
    term_name,
    write_json,
    write_jsonl,
)
from ._system_defs import (
    ALLOWED_REJECTION_ADJUDICATIONS,
    GOLD_CANDIDATE_REVIEW_JSONL,
    GOLD_CANDIDATE_REVIEW_MD,
    GOLD_MANIFEST_PATH,
    GOLD_REVIEW_BATCH_DIR,
    GOLD_REVIEW_BATCH_INDEX_MD,
    GOLD_REVIEW_DECISION_DIR,
    GOLD_REVIEW_DECISION_DRAFT_PATH,
    GOLD_REVIEW_DECISION_INDEX_MD,
    GOLD_REVIEW_DECISION_PROGRESS_JSON,
    GOLD_REVIEW_DECISION_PROGRESS_MD,
    GOLD_REVIEW_PRIORITY_PACKET_DIR,
    GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
    GOLD_REVIEW_PRIORITY_PACKET_JSON,
    GOLD_REVIEW_PROGRESS_JSON,
    GOLD_REVIEW_PROGRESS_MD,
    GOLD_REVIEW_SESSION_PLAN_JSON,
    GOLD_REVIEW_SESSION_PLAN_MD,
    GOLD_REVIEW_WORKLIST_JSON,
    GOLD_REVIEW_WORKLIST_MD,
    GOLD_REVIEW_WORKLOAD_PLAN_JSON,
    GOLD_REVIEW_WORKLOAD_PLAN_MD,
    GOLD_SEMANTIC_GROUPS_JSON,
    GOLD_SEMANTIC_GROUPS_MD,
    GOLD_TEMPLATE_PATH,
    PENDING_GOLD_STATUS,
    REJECTION_ANALYSIS_JSON,
    REVIEWED_GOLD_STATUS,
    REVIEW_CHECKLIST_FIELDS,
    SYSTEMS,
    SystemDefinition,
)
from ._gold_validation import (
    incomplete_review_checklist_fields,
    review_checklist_template,
    validate_gold_annotation_records,
)
from ._prediction_validation import (
    valid_prediction_records,
)

def rejection_group_lookup(rejection_analysis: dict[str, Any]) -> dict[tuple[str, tuple[str, ...]], dict[str, Any]]:
    lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
    for group in rejection_analysis.get("groups", []):
        if not isinstance(group, dict):
            continue
        predicate = str(group.get("predicate", ""))
        errors = tuple(str(error) for error in group.get("errors", []))
        lookup[(predicate, errors)] = group
    return lookup

def summarize_rejected_fact(
    *,
    record: dict[str, Any],
    validator_result: dict[str, Any],
    candidate_by_id: dict[str, dict[str, Any]],
    group_lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]],
) -> dict[str, Any]:
    fact_id = str(validator_result.get("fact_id", ""))
    candidate = candidate_by_id.get(fact_id, {})
    errors = tuple(str(error) for error in validator_result.get("errors", []))
    predicate = str(candidate.get("predicate", ""))
    group = group_lookup.get((predicate, errors), {})
    return {
        "fact_id": fact_id,
        "predicate": predicate,
        "errors": list(errors),
        "subject_class": candidate.get("subject_class"),
        "object_class": candidate.get("object_class"),
        "object": candidate.get("object"),
        "value": candidate.get("value"),
        "evidence_text": candidate.get("evidence_text"),
        "suggested_decision": group.get("decision"),
        "suggested_rationale": group.get("rationale"),
        "suggested_action": group.get("recommended_action"),
    }

def build_gold_review_worklist(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    rejection_analysis = read_json(repo_root / REJECTION_ANALYSIS_JSON)
    group_lookup = rejection_group_lookup(rejection_analysis)

    work_records: list[dict[str, Any]] = []
    total_rejected_facts = 0
    records_with_rejections = 0
    class_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    suggested_decision_counts: Counter[str] = Counter()

    for record in gold_records:
        annotation = record.get("gold_annotation", {})
        status = str(annotation.get("annotation_status", "missing_status"))
        status_counts[status] += 1
        class_name = str(record.get("candidate_subject_class", ""))
        class_counts[class_name] += 1
        candidate_by_id = {
            str(candidate.get("fact_id")): candidate
            for candidate in record.get("candidate_facts", [])
            if isinstance(candidate, dict) and candidate.get("fact_id")
        }
        rejected = [
            summarize_rejected_fact(
                record=record,
                validator_result=result,
                candidate_by_id=candidate_by_id,
                group_lookup=group_lookup,
            )
            for result in record.get("validator_results", [])
            if isinstance(result, dict) and result.get("accepted") is False
        ]
        if rejected:
            records_with_rejections += 1
        total_rejected_facts += len(rejected)
        for item in rejected:
            if item.get("suggested_decision"):
                suggested_decision_counts[str(item["suggested_decision"])] += 1
        work_records.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "source_url": record.get("source_url"),
                "advisory_date": record.get("advisory_date"),
                "advisory_number": record.get("advisory_number"),
                "candidate_subject_class": record.get("candidate_subject_class"),
                "annotation_status": status,
                "candidate_fact_count": record.get("candidate_fact_count", 0),
                "accepted_fact_count": record.get("accepted_fact_count", 0),
                "rejected_fact_count": len(rejected),
                "source_text_excerpt": record.get("source_text_excerpt", ""),
                "required_tasks": [
                    "mark valid candidate facts",
                    "mark invalid candidate fact IDs",
                    "add missing gold facts with evidence_text",
                    "adjudicate validator-rejected facts",
                ],
                "rejected_facts_to_adjudicate": rejected,
            }
        )

    return {
        "source_family": "nasa_atmonto_gold_review_worklist",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "annotation_guide": "docs/nasa_atmonto_gold_annotation_guide.md",
        "selected_source_id_count": len(manifest["selected_source_ids"]),
        "record_count": len(work_records),
        "records_with_rejections": records_with_rejections,
        "total_rejected_facts_to_adjudicate": total_rejected_facts,
        "status_counts": dict(sorted(status_counts.items())),
        "candidate_subject_class_counts": dict(sorted(class_counts.items())),
        "suggested_decision_counts": dict(sorted(suggested_decision_counts.items())),
        "records": work_records,
        "completion_gate": (
            "Use this worklist to complete reviewed gold annotations; scoring still requires "
            "the JSONL template to pass gold annotation validation."
        ),
    }

def gold_review_worklist_markdown(worklist: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Annotation Review Worklist",
        "",
        f"- Gold template: `{worklist['gold_template']}`",
        f"- Annotation guide: `{worklist['annotation_guide']}`",
        f"- Records: {worklist['record_count']}",
        f"- Records with validator rejections: {worklist['records_with_rejections']}",
        f"- Rejected facts to adjudicate: {worklist['total_rejected_facts_to_adjudicate']}",
        f"- Status counts: `{json.dumps(worklist['status_counts'], sort_keys=True)}`",
        f"- Suggested decisions: `{json.dumps(worklist['suggested_decision_counts'], sort_keys=True)}`",
        "",
        "## Review Queue",
        "",
        "| Sample | Source | Class | Candidates | Accepted | Rejected | Status |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for record in worklist["records"]:
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"`{record['candidate_subject_class']}` | "
            f"{record['candidate_fact_count']} | "
            f"{record['accepted_fact_count']} | "
            f"{record['rejected_fact_count']} | "
            f"`{record['annotation_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Rejected Facts Needing Adjudication",
            "",
            "| Sample | Fact | Predicate | Errors | Suggested decision | Evidence |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in worklist["records"]:
        for fact in record["rejected_facts_to_adjudicate"]:
            evidence = compact_text(fact.get("evidence_text"))[:140]
            lines.append(
                "| "
                f"`{record['sample_id']}` | "
                f"`{fact['fact_id']}` | "
                f"`{fact['predicate']}` | "
                f"`{', '.join(fact['errors'])}` | "
                f"`{fact.get('suggested_decision')}` | "
                f"{evidence} |"
            )
    lines.extend(["", "## Completion Gate", "", f"- {worklist['completion_gate']}"])
    return "\n".join(lines).rstrip() + "\n"

def run_gold_review_worklist(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    worklist = build_gold_review_worklist(repo_root)
    write_json(repo_root / GOLD_REVIEW_WORKLIST_JSON, worklist)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).write_text(
        gold_review_worklist_markdown(worklist),
        encoding="utf-8",
    )
    return {
        "worklist_json": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_JSON, repo_root),
        "worklist_markdown": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_MD, repo_root),
        "record_count": worklist["record_count"],
        "records_with_rejections": worklist["records_with_rejections"],
        "total_rejected_facts_to_adjudicate": worklist["total_rejected_facts_to_adjudicate"],
    }

def candidate_review_value(fact: dict[str, Any]) -> object:
    if fact.get("object") not in (None, ""):
        return fact.get("object")
    if fact.get("value") not in (None, ""):
        return fact.get("value")
    properties = fact.get("properties")
    if isinstance(properties, dict) and properties:
        return json.dumps(properties, sort_keys=True, ensure_ascii=False)
    for key, value in sorted(fact.items()):
        if key.startswith("atm:") and value not in (None, ""):
            if isinstance(value, dict):
                return value.get("label") or json.dumps(value, sort_keys=True, ensure_ascii=False)
            return value
    return ""

def candidate_review_predicate(fact: dict[str, Any]) -> str:
    if fact.get("predicate"):
        return term_name(fact.get("predicate"))
    properties = fact.get("properties")
    if isinstance(properties, dict) and len(properties) == 1:
        return term_name(next(iter(properties)))
    if isinstance(properties, dict) and len(properties) > 1:
        return "property_bundle"
    for key in sorted(fact):
        if key.startswith("atm:"):
            return term_name(key)
    return "unmapped_payload"

def candidate_review_object_class(fact: dict[str, Any]) -> str:
    if fact.get("object_class"):
        return term_name(fact.get("object_class"))
    for key, value in sorted(fact.items()):
        if key.startswith("atm:") and isinstance(value, dict) and value.get("type"):
            return term_name(value["type"])
    return ""

def candidate_review_subject_class(fact: dict[str, Any]) -> str:
    return term_name(fact.get("subject_class") or fact.get("type") or "")

def candidate_review_kind(fact: dict[str, Any]) -> str:
    if fact.get("fact_type") in {"object_property", "datatype_property"}:
        return "canonical_fact"
    if isinstance(fact.get("properties"), dict):
        return "property_bundle"
    if any(str(key).startswith("atm:") for key in fact):
        return "schema_shaped_object"
    return "freeform_or_unmapped_fact"

def candidate_review_signature(fact: dict[str, Any]) -> tuple[str, str, str, str, str, str, str]:
    return (
        candidate_review_kind(fact),
        candidate_review_subject_class(fact),
        candidate_review_predicate(fact),
        compact_text(candidate_review_value(fact)).lower(),
        candidate_review_object_class(fact),
        term_name(fact.get("datatype")),
        compact_text(fact.get("evidence_text")).lower(),
    )

def candidate_review_fields(fact: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_kind": candidate_review_kind(fact),
        "subject_class": candidate_review_subject_class(fact),
        "predicate": candidate_review_predicate(fact),
        "value_or_object": candidate_review_value(fact),
        "object_class": candidate_review_object_class(fact),
        "datatype": term_name(fact.get("datatype")),
        "evidence_text": compact_text(fact.get("evidence_text")),
    }

def truncated_candidate_payload(fact: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in sorted(fact.items()):
        if key == "evidence_text":
            payload[key] = compact_text(value)[:500]
        elif isinstance(value, str):
            payload[key] = compact_text(value)[:500]
        else:
            payload[key] = value
    return payload

def validator_results_by_fact_id(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for result in record.get("validator_results", []):
        if isinstance(result, dict) and result.get("fact_id") and str(result["fact_id"]) not in results:
            results[str(result["fact_id"])] = result
    return results

def system_candidate_facts(system: SystemDefinition, record: dict[str, Any]) -> list[dict[str, Any]]:
    field = "candidate_facts" if system.system_id == "S0_rule_only" else "facts"
    return [fact for fact in record.get(field, []) if isinstance(fact, dict)]

def build_system_candidate_review_package(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])

    prediction_records_by_system: dict[str, dict[str, dict[str, Any]]] = {}
    output_status_by_system: dict[str, bool] = {}
    raw_fact_counts_by_system: Counter[str] = Counter()
    for system in SYSTEMS:
        parse_result = read_jsonl_lenient(repo_root / system.expected_output)
        output_status_by_system[system.system_id] = bool(parse_result["exists"])
        records = valid_prediction_records(parse_result, selected_ids) if parse_result["exists"] else []
        prediction_records_by_system[system.system_id] = {
            str(record.get("source_id")): record
            for record in records
            if isinstance(record, dict)
        }
        for record in records:
            raw_fact_counts_by_system[system.system_id] += len(system_candidate_facts(system, record))

    review_records: list[dict[str, Any]] = []
    cluster_count_by_system: Counter[str] = Counter()
    accepted_cluster_count = 0
    rejected_cluster_count = 0
    candidate_kind_counts: Counter[str] = Counter()
    schema_error_counts: Counter[str] = Counter()

    for gold_record in gold_records:
        source_id = str(gold_record.get("source_id"))
        clusters: dict[tuple[str, str, str, str, str, str, str], dict[str, Any]] = {}
        for system in SYSTEMS:
            prediction_record = prediction_records_by_system[system.system_id].get(source_id)
            if not prediction_record:
                continue
            validations = validator_results_by_fact_id(prediction_record)
            for fact in system_candidate_facts(system, prediction_record):
                signature = candidate_review_signature(fact)
                candidate_id = "cand-" + sha1(
                    json.dumps(
                        [source_id, *signature],
                        sort_keys=True,
                        ensure_ascii=False,
                    ).encode("utf-8")
                ).hexdigest()[:16]
                cluster = clusters.setdefault(
                    signature,
                    {
                        "candidate_id": candidate_id,
                        "review_fields": candidate_review_fields(fact),
                        "source_systems": [],
                        "system_observations": [],
                        "schema_status_counts": {},
                        "schema_error_counts": {},
                    },
                )
                if system.system_id not in cluster["source_systems"]:
                    cluster["source_systems"].append(system.system_id)
                fact_id = str(fact.get("fact_id", ""))
                validation = validations.get(fact_id, {})
                accepted = validation.get("accepted")
                errors = [str(error) for error in validation.get("errors", [])]
                status = str(validation.get("status", "not_validated"))
                cluster["system_observations"].append(
                    {
                        "system_id": system.system_id,
                        "fact_id": fact_id,
                        "accepted_by_validator": accepted,
                        "validator_status": status,
                        "validator_errors": errors,
                        "repairs": validation.get("repairs", []),
                        "fact_payload": truncated_candidate_payload(fact),
                    }
                )

        candidate_clusters = []
        for cluster in clusters.values():
            status_counts = Counter(
                observation["validator_status"]
                for observation in cluster["system_observations"]
            )
            error_counts = Counter(
                error
                for observation in cluster["system_observations"]
                for error in observation["validator_errors"]
            )
            source_systems = sorted(cluster["source_systems"])
            for system_id in source_systems:
                cluster_count_by_system[system_id] += 1
            accepted_by_any = any(
                observation["accepted_by_validator"] is True
                for observation in cluster["system_observations"]
            )
            rejected_by_all = all(
                observation["accepted_by_validator"] is False
                for observation in cluster["system_observations"]
                if observation["accepted_by_validator"] is not None
            )
            if accepted_by_any:
                accepted_cluster_count += 1
            elif rejected_by_all:
                rejected_cluster_count += 1
            candidate_kind_counts[str(cluster["review_fields"]["candidate_kind"])] += 1
            schema_error_counts.update(error_counts)
            candidate_clusters.append(
                {
                    **cluster,
                    "source_systems": source_systems,
                    "schema_status_counts": dict(sorted(status_counts.items())),
                    "schema_error_counts": dict(sorted(error_counts.items())),
                    "accepted_by_any_system_validator": accepted_by_any,
                    "rejected_by_all_system_validators": rejected_by_all,
                    "review_action_options": [
                        "accept_as_gold_fact",
                        "reject_semantically",
                        "add_corrected_missing_fact",
                        "ignore_structurally_invalid_payload",
                    ],
                }
            )

        candidate_clusters.sort(key=lambda item: item["candidate_id"])
        review_records.append(
            {
                "sample_id": gold_record.get("sample_id"),
                "source_id": source_id,
                "source_url": gold_record.get("source_url"),
                "candidate_subject_class": gold_record.get("candidate_subject_class"),
                "annotation_status": gold_record.get("gold_annotation", {}).get(
                    "annotation_status"
                ),
                "source_text_excerpt": gold_record.get("source_text_excerpt", ""),
                "candidate_cluster_count": len(candidate_clusters),
                "candidate_clusters": candidate_clusters,
            }
        )

    summary = {
        "source_family": "nasa_atmonto_system_candidate_review",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "candidate_review_jsonl": project_relative_path(
            repo_root / GOLD_CANDIDATE_REVIEW_JSONL,
            repo_root,
        ),
        "candidate_review_markdown": project_relative_path(
            repo_root / GOLD_CANDIDATE_REVIEW_MD,
            repo_root,
        ),
        "selected_source_id_count": len(selected_ids),
        "record_count": len(review_records),
        "system_ids": [system.system_id for system in SYSTEMS],
        "prediction_outputs_exist_by_system": dict(sorted(output_status_by_system.items())),
        "raw_fact_counts_by_system": dict(sorted(raw_fact_counts_by_system.items())),
        "candidate_cluster_count": sum(record["candidate_cluster_count"] for record in review_records),
        "candidate_cluster_counts_by_system": dict(sorted(cluster_count_by_system.items())),
        "accepted_cluster_count": accepted_cluster_count,
        "rejected_cluster_count": rejected_cluster_count,
        "candidate_kind_counts": dict(sorted(candidate_kind_counts.items())),
        "schema_error_counts": dict(sorted(schema_error_counts.items())),
        "records": review_records,
        "completion_gate": (
            "Use this cross-system candidate package during manual gold review so S1-S3 "
            "facts are considered alongside the rule-only baseline. It is not itself "
            "reviewed gold and must not be scored as manual truth."
        ),
    }
    return summary

def system_candidate_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Cross-System Candidate Review",
        "",
        f"- Gold template: `{report['gold_template']}`",
        f"- Candidate review JSONL: `{report['candidate_review_jsonl']}`",
        f"- Records: {report['record_count']}",
        f"- Candidate clusters: {report['candidate_cluster_count']}",
        f"- Raw fact counts by system: `{json.dumps(report['raw_fact_counts_by_system'], sort_keys=True)}`",
        f"- Cluster counts by system: `{json.dumps(report['candidate_cluster_counts_by_system'], sort_keys=True)}`",
        f"- Candidate kinds: `{json.dumps(report['candidate_kind_counts'], sort_keys=True)}`",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Review Queue",
        "",
        "| Sample | Source | Class | Candidate clusters | Status |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for record in report["records"]:
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"`{record['candidate_subject_class']}` | "
            f"{record['candidate_cluster_count']} | "
            f"`{record['annotation_status']}` |"
        )
    lines.extend(
        [
            "",
            "## High-Load Samples",
            "",
            "| Sample | Source | Candidate clusters | Dominant systems |",
            "| --- | --- | ---: | --- |",
        ]
    )
    top_records = sorted(
        report["records"],
        key=lambda item: int(item["candidate_cluster_count"]),
        reverse=True,
    )[:20]
    for record in top_records:
        systems = Counter(
            system_id
            for cluster in record["candidate_clusters"]
            for system_id in cluster["source_systems"]
        )
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"{record['candidate_cluster_count']} | "
            f"`{json.dumps(dict(sorted(systems.items())), sort_keys=True)}` |"
        )
    return "\n".join(lines) + "\n"

def run_system_candidate_review_package(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_system_candidate_review_package(repo_root)
    records = report["records"]
    write_jsonl(repo_root / GOLD_CANDIDATE_REVIEW_JSONL, records)
    (repo_root / GOLD_CANDIDATE_REVIEW_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_CANDIDATE_REVIEW_MD).write_text(
        system_candidate_review_markdown(report),
        encoding="utf-8",
    )
    batch_report = build_gold_review_batches(repo_root, candidate_review=report)
    (repo_root / GOLD_REVIEW_BATCH_DIR).mkdir(parents=True, exist_ok=True)
    for batch in batch_report["batches"]:
        (repo_root / batch["path"]).write_text(
            gold_review_batch_markdown(batch),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_BATCH_INDEX_MD).write_text(
        gold_review_batch_index_markdown(batch_report),
        encoding="utf-8",
    )
    return {
        "candidate_review_jsonl": report["candidate_review_jsonl"],
        "candidate_review_markdown": report["candidate_review_markdown"],
        "batch_index_markdown": batch_report["batch_index_markdown"],
        "batch_count": batch_report["batch_count"],
        "record_count": report["record_count"],
        "candidate_cluster_count": report["candidate_cluster_count"],
        "raw_fact_counts_by_system": report["raw_fact_counts_by_system"],
        "candidate_cluster_counts_by_system": report["candidate_cluster_counts_by_system"],
    }

def markdown_cell(value: object, *, max_chars: int = 180) -> str:
    text = compact_text(value)
    if len(text) > max_chars:
        text = text[: max_chars - 3].rstrip() + "..."
    return text.replace("|", "\\|")

def build_gold_review_batches(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
    candidate_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if candidate_review is None:
        candidate_review = build_system_candidate_review_package(repo_root)
    records = list(candidate_review["records"])
    batches: list[dict[str, Any]] = []
    for start in range(0, len(records), batch_size):
        batch_records = records[start : start + batch_size]
        batch_number = len(batches) + 1
        batch_id = f"batch_{batch_number:02d}"
        candidate_cluster_count = sum(
            int(record.get("candidate_cluster_count", 0)) for record in batch_records
        )
        batches.append(
            {
                "batch_id": batch_id,
                "batch_number": batch_number,
                "path": project_relative_path(
                    repo_root / GOLD_REVIEW_BATCH_DIR / f"{batch_id}.md",
                    repo_root,
                ),
                "record_count": len(batch_records),
                "first_sample_id": batch_records[0]["sample_id"] if batch_records else None,
                "last_sample_id": batch_records[-1]["sample_id"] if batch_records else None,
                "candidate_cluster_count": candidate_cluster_count,
                "records": batch_records,
            }
        )
    return {
        "source_family": "nasa_atmonto_gold_review_batches",
        "batch_size": batch_size,
        "batch_count": len(batches),
        "record_count": len(records),
        "candidate_cluster_count": sum(
            int(record.get("candidate_cluster_count", 0)) for record in records
        ),
        "candidate_review_jsonl": candidate_review["candidate_review_jsonl"],
        "gold_template": candidate_review["gold_template"],
        "batch_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_BATCH_INDEX_MD,
            repo_root,
        ),
        "batches": batches,
        "completion_gate": (
            "Review every batch, then transfer reviewed decisions into "
            "data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl and run "
            "gold validation before freezing the formal gold set."
        ),
    }

def gold_review_batch_markdown(batch: dict[str, Any]) -> str:
    lines = [
        f"# NASA ATMONTO Gold Review {batch['batch_id']}",
        "",
        f"- Samples: `{batch['first_sample_id']}` to `{batch['last_sample_id']}`",
        f"- Records: {batch['record_count']}",
        f"- Candidate clusters: {batch['candidate_cluster_count']}",
        "",
        "## Batch Checklist",
        "",
        "- [ ] Read every source text excerpt and URL when needed.",
        "- [ ] Mark semantically valid candidate facts.",
        "- [ ] Mark semantically invalid candidate fact IDs.",
        "- [ ] Add missing gold facts with evidence text.",
        "- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.",
        "",
    ]
    for record in batch["records"]:
        lines.extend(
            [
                f"## {record['sample_id']} / {record['source_id']}",
                "",
                f"- Source URL: {record.get('source_url')}",
                f"- Candidate class: `{record.get('candidate_subject_class')}`",
                f"- Current status: `{record.get('annotation_status')}`",
                f"- Candidate clusters: {record.get('candidate_cluster_count')}",
                "",
                "Source excerpt:",
                "",
                f"> {markdown_cell(record.get('source_text_excerpt'), max_chars=900)}",
                "",
                "Review actions:",
                "",
                "- [ ] valid facts selected",
                "- [ ] invalid candidate fact IDs selected",
                "- [ ] missing facts added",
                "- [ ] rejected facts adjudicated if applicable",
                "",
                "| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for cluster in record["candidate_clusters"]:
            fields = cluster["review_fields"]
            validator = json.dumps(cluster["schema_status_counts"], sort_keys=True)
            errors = json.dumps(cluster["schema_error_counts"], sort_keys=True)
            lines.append(
                "| "
                f"`{cluster['candidate_id']}` | "
                f"`{', '.join(cluster['source_systems'])}` | "
                f"`{markdown_cell(fields.get('candidate_kind'), max_chars=80)}` | "
                f"`{markdown_cell(fields.get('predicate'), max_chars=80)}` | "
                f"{markdown_cell(fields.get('value_or_object'), max_chars=160)} | "
                f"`{markdown_cell(validator, max_chars=120)}` | "
                f"`{markdown_cell(errors, max_chars=120)}` | "
                f"{markdown_cell(fields.get('evidence_text'), max_chars=220)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def gold_review_batch_index_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Batches",
        "",
        f"- Candidate review: `{report['candidate_review_jsonl']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Records: {report['record_count']}",
        f"- Batches: {report['batch_count']}",
        f"- Candidate clusters: {report['candidate_cluster_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Batches",
        "",
        "| Batch | Samples | Records | Candidate clusters | File |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for batch in report["batches"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['first_sample_id']}`-`{batch['last_sample_id']}` | "
            f"{batch['record_count']} | "
            f"{batch['candidate_cluster_count']} | "
            f"`{batch['path']}` |"
        )
    return "\n".join(lines) + "\n"

def run_gold_review_batches(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    candidate_review = build_system_candidate_review_package(repo_root)
    report = build_gold_review_batches(
        repo_root,
        batch_size=batch_size,
        candidate_review=candidate_review,
    )
    (repo_root / GOLD_REVIEW_BATCH_DIR).mkdir(parents=True, exist_ok=True)
    for batch in report["batches"]:
        (repo_root / batch["path"]).write_text(
            gold_review_batch_markdown(batch),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_BATCH_INDEX_MD).write_text(
        gold_review_batch_index_markdown(report),
        encoding="utf-8",
    )
    return {
        "batch_index_markdown": report["batch_index_markdown"],
        "batch_count": report["batch_count"],
        "record_count": report["record_count"],
        "candidate_cluster_count": report["candidate_cluster_count"],
        "batch_files": [batch["path"] for batch in report["batches"]],
    }

def record_cross_system_cluster_count(record: dict[str, Any]) -> int:
    return sum(
        1
        for cluster in record.get("candidate_clusters", [])
        if isinstance(cluster, dict)
        and any(system != "S0_rule_only" for system in cluster.get("source_systems", []))
    )

def record_workload_score(
    *,
    candidate_cluster_count: int,
    cross_system_cluster_count: int,
    rejected_fact_count: int,
    source_word_count: int,
) -> int:
    return (
        candidate_cluster_count
        + cross_system_cluster_count
        + (rejected_fact_count * 3)
        + (source_word_count // 80)
    )

def review_complexity_tier(workload_score: int) -> str:
    if workload_score <= 40:
        return "light"
    if workload_score <= 65:
        return "medium"
    return "heavy"

def review_priority_lane(record: dict[str, Any]) -> str:
    if int(record["rejected_fact_count"]) > 0:
        return "1_rejection_adjudication"
    if record["complexity_tier"] == "heavy":
        return "2_high_cross_system_coverage"
    return "3_standard_review"

SEMANTIC_GROUP_DEFINITIONS: dict[str, dict[str, str]] = {
    "ground_stop_lifecycle": {
        "label": "Ground stop lifecycle",
        "description": "CDM ground-stop creation, extension, and cancellation notices.",
    },
    "reroute_or_route_constraint": {
        "label": "Reroute or route constraint",
        "description": "Route-required, oceanic-route-closure, reroute-cancellation, CDR, or SWAP advisories.",
    },
    "volcanic_activity_bulletin": {
        "label": "Volcanic activity bulletin",
        "description": "Volcanic-ash advisories carried through ATCSCC as generic traffic-management notices.",
    },
    "ground_delay_program_lifecycle": {
        "label": "Ground delay program lifecycle",
        "description": "CDM ground-delay program, proposed GDP, and GDP cancellation notices.",
    },
    "airport_arrival_or_scheduling_delay": {
        "label": "Airport arrival or scheduling delay",
        "description": "Airport arrival-delay, airport-scheduling-delay, and compacted-demand notices.",
    },
    "hotline_or_webpage_status": {
        "label": "Hotline or webpage status",
        "description": "TCA/hotline page activation or termination status messages.",
    },
    "airport_diversion_recovery": {
        "label": "Airport diversion recovery",
        "description": "Airport diversion-recovery activation notices.",
    },
    "special_or_flow_constraint_fyi": {
        "label": "Special mission or flow-constraint FYI",
        "description": "Planning-only or FYI notices that are not clean active reroute/GDP/GS events.",
    },
    "flight_plan_drop_time_status": {
        "label": "Flight plan drop time status",
        "description": "Extended flight-plan drop-time implementation notices.",
    },
    "other_tmi_status": {
        "label": "Other TMI status",
        "description": "Residual ATCSCC status notices not captured by a higher-precedence group.",
    },
}

def atcscc_advisory_headline(source_text: object) -> str:
    for line in str(source_text or "").splitlines():
        headline = compact_text(line)
        if headline.startswith("ATCSCC ADVZY"):
            return headline
    return ""

def classify_atcscc_semantic_group(headline: str) -> tuple[str, str]:
    text = headline.upper()
    if "VOLCANIC ACTIVITY BULLETIN" in text:
        return "volcanic_activity_bulletin", "headline contains VOLCANIC ACTIVITY BULLETIN"
    if "GROUND DELAY PROGRAM" in text:
        return "ground_delay_program_lifecycle", "headline contains GROUND DELAY PROGRAM"
    if "GROUND STOP" in text or "CDM GS CNX" in text:
        return "ground_stop_lifecycle", "headline contains GROUND STOP or CDM GS CNX"
    if (
        "AIRPORT ARRIVAL DELAYS" in text
        or "AIRPORTS ARRIVAL DELAYS" in text
        or "AIRPORT SCHEDULING DELAYS" in text
    ):
        return (
            "airport_arrival_or_scheduling_delay",
            "headline contains airport arrival/scheduling delay language",
        )
    if (
        "ROUTE RQD" in text
        or "ROUTE CLOSURE" in text
        or "REROUTE" in text
        or "CDRS" in text
        or "SWAP" in text
    ):
        return "reroute_or_route_constraint", "headline contains route, CDR, reroute, or SWAP language"
    if "DIVERSION RECOVERY" in text:
        return "airport_diversion_recovery", "headline contains DIVERSION RECOVERY"
    if "HOTLINE" in text or "WEB PAGE" in text:
        return "hotline_or_webpage_status", "headline contains HOTLINE or WEB PAGE"
    if "FLIGHT PLAN DROP TIMES" in text:
        return "flight_plan_drop_time_status", "headline contains FLIGHT PLAN DROP TIMES"
    if "STARSHIP" in text or "CAPPING TUNNELING" in text:
        return "special_or_flow_constraint_fyi", "headline contains STARSHIP or CAPPING TUNNELING"
    return "other_tmi_status", "no higher-precedence semantic headline rule matched"

def build_gold_semantic_groups(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    workload_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    workload_plan = workload_plan or build_gold_review_workload_plan(repo_root)
    source_records = {record["sample_id"]: record for record in read_jsonl(repo_root / GOLD_TEMPLATE_PATH)}
    group_records: list[dict[str, Any]] = []
    group_counts: Counter[str] = Counter()
    group_class_counts: dict[str, Counter[str]] = {}
    group_date_counts: dict[str, Counter[str]] = {}
    group_priority_counts: dict[str, Counter[str]] = {}
    class_counts: Counter[str] = Counter()
    date_counts: Counter[str] = Counter()

    for review_record in workload_plan["records"]:
        sample_id = str(review_record["sample_id"])
        source_record = source_records.get(sample_id)
        if source_record is None:
            raise ValueError(
                f"sample_id {sample_id!r} found in workload plan but not in gold template"
            )
        headline = atcscc_advisory_headline(source_record.get("source_text"))
        group_id, rationale = classify_atcscc_semantic_group(headline)
        candidate_class = str(review_record.get("candidate_subject_class") or "")
        source_date = str(source_record.get("advisory_date") or str(review_record["source_id"]).split(":", 1)[0])
        priority_lane = str(review_record.get("priority_lane") or "")
        group_counts[group_id] += 1
        class_counts[candidate_class] += 1
        date_counts[source_date] += 1
        group_class_counts.setdefault(group_id, Counter())[candidate_class] += 1
        group_date_counts.setdefault(group_id, Counter())[source_date] += 1
        group_priority_counts.setdefault(group_id, Counter())[priority_lane] += 1
        group_records.append(
            {
                "sample_id": sample_id,
                "source_id": review_record["source_id"],
                "advisory_date": source_date,
                "batch_id": review_record["batch_id"],
                "priority_lane": priority_lane,
                "candidate_subject_class": candidate_class,
                "semantic_group_id": group_id,
                "semantic_group_label": SEMANTIC_GROUP_DEFINITIONS[group_id]["label"],
                "classification_basis": "ATCSCC advisory headline heuristic",
                "classification_rationale": rationale,
                "headline": headline,
            }
        )

    groups = []
    for group_id, count in group_counts.most_common():
        records = [record for record in group_records if record["semantic_group_id"] == group_id]
        groups.append(
            {
                "group_id": group_id,
                "label": SEMANTIC_GROUP_DEFINITIONS[group_id]["label"],
                "description": SEMANTIC_GROUP_DEFINITIONS[group_id]["description"],
                "record_count": count,
                "candidate_subject_class_counts": dict(sorted(group_class_counts[group_id].items())),
                "source_date_counts": dict(sorted(group_date_counts[group_id].items())),
                "priority_lane_counts": dict(sorted(group_priority_counts[group_id].items())),
                "sample_ids": [record["sample_id"] for record in records],
                "example_headlines": [
                    {
                        "sample_id": record["sample_id"],
                        "headline": record["headline"],
                    }
                    for record in records[:5]
                ],
            }
        )

    min_group_count = min(group_counts.values()) if group_counts else 0
    return {
        "source_family": "nasa_atmonto_gold_semantic_groups",
        "status": "ready_for_stratified_reporting",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "workload_plan": project_relative_path(repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD, repo_root),
        "semantic_groups_json": project_relative_path(repo_root / GOLD_SEMANTIC_GROUPS_JSON, repo_root),
        "semantic_groups_markdown": project_relative_path(repo_root / GOLD_SEMANTIC_GROUPS_MD, repo_root),
        "record_count": len(group_records),
        "semantic_group_count": len(groups),
        "semantic_group_counts": dict(group_counts.most_common()),
        "candidate_subject_class_counts": dict(sorted(class_counts.items())),
        "source_date_counts": dict(sorted(date_counts.items())),
        "minimum_semantic_group_count": min_group_count,
        "records": group_records,
        "groups": groups,
        "use_in_experiment": (
            "Use these groups for stratified error analysis and per-group reporting. "
            "They are not train/dev/test splits and do not create gold truth by themselves."
        ),
        "limitations": [
            "Grouping is based on deterministic headline heuristics, not domain-expert taxonomy.",
            "Small groups should be merged or reported descriptively if confidence intervals are unstable.",
            "Ontology candidate classes and operational semantic groups intentionally differ for status/cancellation/FYI notices.",
        ],
    }

def gold_semantic_groups_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Semantic Groups",
        "",
        "## Material Passport",
        "",
        "- Artifact: semantic grouping report for the 100-record ATCSCC gold-set candidate.",
        f"- Gold template: `{report['gold_template']}`",
        f"- Workload plan: `{report['workload_plan']}`",
        "- Classification method: deterministic ATCSCC advisory headline heuristics.",
        "- Boundary: grouping is for stratified analysis; it is not an annotation decision and not a train/dev/test split.",
        "",
        "## Summary",
        "",
        f"- Records: {report['record_count']}",
        f"- Semantic groups: {report['semantic_group_count']}",
        f"- Minimum group size: {report['minimum_semantic_group_count']}",
        f"- Candidate class counts: `{json.dumps(report['candidate_subject_class_counts'], sort_keys=True)}`",
        f"- Source-date counts: `{json.dumps(report['source_date_counts'], sort_keys=True)}`",
        "",
        "## Semantic Groups",
        "",
        "| Group | Label | Records | Candidate classes | Priority lanes | Example samples |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for group in report["groups"]:
        lines.append(
            "| "
            f"`{group['group_id']}` | "
            f"{group['label']} | "
            f"{group['record_count']} | "
            f"`{json.dumps(group['candidate_subject_class_counts'], sort_keys=True)}` | "
            f"`{json.dumps(group['priority_lane_counts'], sort_keys=True)}` | "
            f"`{', '.join(group['sample_ids'][:8])}` |"
        )

    lines.extend(
        [
            "",
            "## Records",
            "",
            "| Sample | Source | Date | Batch | Candidate class | Semantic group | Headline |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"`{record['advisory_date']}` | "
            f"`{record['batch_id']}` | "
            f"`{record['candidate_subject_class']}` | "
            f"`{record['semantic_group_id']}` | "
            f"{record['headline']} |"
        )
    lines.extend(["", "## Use In Experiment", "", f"- {report['use_in_experiment']}", ""])
    lines.append("## Limitations")
    lines.append("")
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    return "\n".join(lines).rstrip() + "\n"

def estimate_review_minutes(
    *,
    candidate_cluster_count: int,
    cross_system_cluster_count: int,
    rejected_fact_count: int,
    source_word_count: int,
) -> int:
    return (
        3
        + ceil_div(candidate_cluster_count, 4)
        + ceil_div(cross_system_cluster_count, 6)
        + (rejected_fact_count * 2)
        + ceil_div(source_word_count, 120)
    )

def build_gold_review_workload_plan(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    worklist = build_gold_review_worklist(repo_root)
    candidate_review = build_system_candidate_review_package(repo_root)
    batch_report = build_gold_review_batches(
        repo_root,
        batch_size=batch_size,
        candidate_review=candidate_review,
    )
    worklist_by_sample = {record["sample_id"]: record for record in worklist["records"]}
    batch_by_sample: dict[str, str] = {}
    for batch in batch_report["batches"]:
        for record in batch["records"]:
            batch_by_sample[str(record["sample_id"])] = str(batch["batch_id"])

    workload_records: list[dict[str, Any]] = []
    complexity_counts: Counter[str] = Counter()
    lane_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()

    for candidate_record in candidate_review["records"]:
        sample_id = str(candidate_record["sample_id"])
        work_record = worklist_by_sample[sample_id]
        candidate_cluster_count = int(candidate_record.get("candidate_cluster_count", 0))
        cross_system_count = record_cross_system_cluster_count(candidate_record)
        rejected_fact_count = int(work_record.get("rejected_fact_count", 0))
        source_word_count = len(compact_text(candidate_record.get("source_text_excerpt")).split())
        workload_score = record_workload_score(
            candidate_cluster_count=candidate_cluster_count,
            cross_system_cluster_count=cross_system_count,
            rejected_fact_count=rejected_fact_count,
            source_word_count=source_word_count,
        )
        estimated_minutes = estimate_review_minutes(
            candidate_cluster_count=candidate_cluster_count,
            cross_system_cluster_count=cross_system_count,
            rejected_fact_count=rejected_fact_count,
            source_word_count=source_word_count,
        )
        record = {
            "sample_id": sample_id,
            "source_id": candidate_record.get("source_id"),
            "batch_id": batch_by_sample[sample_id],
            "candidate_subject_class": candidate_record.get("candidate_subject_class"),
            "annotation_status": work_record.get("annotation_status"),
            "candidate_cluster_count": candidate_cluster_count,
            "cross_system_candidate_cluster_count": cross_system_count,
            "rejected_fact_count": rejected_fact_count,
            "source_word_count": source_word_count,
            "workload_score": workload_score,
            "complexity_tier": review_complexity_tier(workload_score),
            "estimated_review_minutes": estimated_minutes,
        }
        record["priority_lane"] = review_priority_lane(record)
        complexity_counts[str(record["complexity_tier"])] += 1
        lane_counts[str(record["priority_lane"])] += 1
        class_counts[str(record["candidate_subject_class"])] += 1
        workload_records.append(record)

    records_by_sample = {record["sample_id"]: record for record in workload_records}
    batch_summaries: list[dict[str, Any]] = []
    for batch in batch_report["batches"]:
        records = [records_by_sample[str(record["sample_id"])] for record in batch["records"]]
        batch_summaries.append(
            {
                "batch_id": batch["batch_id"],
                "path": batch["path"],
                "record_count": len(records),
                "first_sample_id": batch["first_sample_id"],
                "last_sample_id": batch["last_sample_id"],
                "candidate_cluster_count": sum(
                    int(record["candidate_cluster_count"]) for record in records
                ),
                "cross_system_candidate_cluster_count": sum(
                    int(record["cross_system_candidate_cluster_count"]) for record in records
                ),
                "rejected_fact_count": sum(int(record["rejected_fact_count"]) for record in records),
                "estimated_review_minutes": sum(
                    int(record["estimated_review_minutes"]) for record in records
                ),
                "complexity_counts": dict(
                    sorted(Counter(str(record["complexity_tier"]) for record in records).items())
                ),
                "priority_lane_counts": dict(
                    sorted(Counter(str(record["priority_lane"]) for record in records).items())
                ),
            }
        )

    review_order = sorted(
        workload_records,
        key=lambda record: (
            str(record["priority_lane"]),
            -int(record["rejected_fact_count"]),
            -int(record["workload_score"]),
            str(record["sample_id"]),
        ),
    )
    total_minutes = sum(int(record["estimated_review_minutes"]) for record in workload_records)
    return {
        "source_family": "nasa_atmonto_gold_review_workload_plan",
        "gold_template": worklist["gold_template"],
        "worklist_markdown": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_MD, repo_root),
        "candidate_review_jsonl": candidate_review["candidate_review_jsonl"],
        "batch_index_markdown": batch_report["batch_index_markdown"],
        "decision_templates": project_relative_path(repo_root / GOLD_REVIEW_DECISION_INDEX_MD, repo_root),
        "progress_markdown": project_relative_path(repo_root / GOLD_REVIEW_PROGRESS_MD, repo_root),
        "record_count": len(workload_records),
        "batch_count": batch_report["batch_count"],
        "records_with_rejections": worklist["records_with_rejections"],
        "total_rejected_facts_to_adjudicate": worklist[
            "total_rejected_facts_to_adjudicate"
        ],
        "estimated_total_review_minutes": total_minutes,
        "estimated_total_review_hours": round(total_minutes / 60, 2),
        "complexity_counts": dict(sorted(complexity_counts.items())),
        "priority_lane_counts": dict(sorted(lane_counts.items())),
        "candidate_subject_class_counts": dict(sorted(class_counts.items())),
        "records": workload_records,
        "recommended_review_order": review_order,
        "batches": batch_summaries,
        "completion_gate": (
            "All 100 records still need source-reviewed decisions before semantic scoring; "
            "this workload plan only prioritizes manual review and does not create gold truth."
        ),
    }

def gold_review_workload_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Workload Plan",
        "",
        f"- Gold template: `{plan['gold_template']}`",
        f"- Worklist: `{plan['worklist_markdown']}`",
        f"- Candidate review: `{plan['candidate_review_jsonl']}`",
        f"- Batch index: `{plan['batch_index_markdown']}`",
        f"- Decision templates: `{plan['decision_templates']}`",
        f"- Progress tracker: `{plan['progress_markdown']}`",
        f"- Records: {plan['record_count']}",
        f"- Batches: {plan['batch_count']}",
        f"- Records with validator rejections: {plan['records_with_rejections']}",
        f"- Rejected facts to adjudicate: {plan['total_rejected_facts_to_adjudicate']}",
        f"- Estimated total review time: {plan['estimated_total_review_minutes']} minutes "
        f"({plan['estimated_total_review_hours']} hours)",
        f"- Complexity counts: `{json.dumps(plan['complexity_counts'], sort_keys=True)}`",
        f"- Priority lanes: `{json.dumps(plan['priority_lane_counts'], sort_keys=True)}`",
        "",
        "## Priority Lanes",
        "",
        "| Lane | Meaning |",
        "| --- | --- |",
        "| `1_rejection_adjudication` | Review first: these records need both semantic gold decisions and rejected-fact adjudications. |",
        "| `2_high_cross_system_coverage` | Review next: no pilot rejection, but many cross-system candidate alternatives need source checks. |",
        "| `3_standard_review` | Complete after the higher-workload lanes; still required for final recall/F1. |",
        "",
        "## Batch Workload",
        "",
        "| Batch | Samples | Records | Clusters | Cross-system clusters | Rejected facts | Est. min | Complexity | Lanes | File |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for batch in plan["batches"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['first_sample_id']}`-`{batch['last_sample_id']}` | "
            f"{batch['record_count']} | "
            f"{batch['candidate_cluster_count']} | "
            f"{batch['cross_system_candidate_cluster_count']} | "
            f"{batch['rejected_fact_count']} | "
            f"{batch['estimated_review_minutes']} | "
            f"`{json.dumps(batch['complexity_counts'], sort_keys=True)}` | "
            f"`{json.dumps(batch['priority_lane_counts'], sort_keys=True)}` | "
            f"`{batch['path']}` |"
        )
    lines.extend(
        [
            "",
            "## Recommended Review Order",
            "",
            "| Order | Sample | Batch | Lane | Tier | Score | Est. min | Clusters | Cross-system | Rejected | Class |",
            "| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for index, record in enumerate(plan["recommended_review_order"], start=1):
        lines.append(
            "| "
            f"{index} | "
            f"`{record['sample_id']}` | "
            f"`{record['batch_id']}` | "
            f"`{record['priority_lane']}` | "
            f"`{record['complexity_tier']}` | "
            f"{record['workload_score']} | "
            f"{record['estimated_review_minutes']} | "
            f"{record['candidate_cluster_count']} | "
            f"{record['cross_system_candidate_cluster_count']} | "
            f"{record['rejected_fact_count']} | "
            f"`{record['candidate_subject_class']}` |"
        )
    lines.extend(["", "## Completion Gate", "", f"- {plan['completion_gate']}"])
    return "\n".join(lines).rstrip() + "\n"

def run_gold_review_workload_plan(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    plan = build_gold_review_workload_plan(repo_root)
    write_json(repo_root / GOLD_REVIEW_WORKLOAD_PLAN_JSON, plan)
    (repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD).write_text(
        gold_review_workload_plan_markdown(plan),
        encoding="utf-8",
    )
    return {
        "workload_plan_json": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_JSON,
            repo_root,
        ),
        "workload_plan_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD,
            repo_root,
        ),
        "record_count": plan["record_count"],
        "batch_count": plan["batch_count"],
        "estimated_total_review_minutes": plan["estimated_total_review_minutes"],
        "complexity_counts": plan["complexity_counts"],
        "priority_lane_counts": plan["priority_lane_counts"],
    }

def decision_progress_record_lookup(
    decision_progress: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for batch in decision_progress.get("batch_progress", []):
        if not isinstance(batch, dict):
            continue
        for record in batch.get("records", []):
            if isinstance(record, dict) and record.get("source_id"):
                records[str(record["source_id"])] = record
    return records

def review_session_id(index: int) -> str:
    return f"session_{index:02d}"

def gold_review_session_summary(
    *,
    session_id: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    status_counts = Counter(str(record["decision_status"]) for record in records)
    if status_counts.get("needs_revision"):
        status = "needs_revision"
    elif records and status_counts.get("ready_to_apply", 0) == len(records):
        status = "ready_to_apply"
    elif status_counts.get("ready_to_apply") or status_counts.get("in_progress"):
        status = "in_progress"
    else:
        status = "pending_manual_review"
    return {
        "session_id": session_id,
        "status": status,
        "record_count": len(records),
        "ready_to_apply_record_count": status_counts.get("ready_to_apply", 0),
        "remaining_record_count": len(records) - status_counts.get("ready_to_apply", 0),
        "estimated_review_minutes": sum(
            int(record["estimated_review_minutes"]) for record in records
        ),
        "rejected_fact_count": sum(int(record["rejected_fact_count"]) for record in records),
        "pending_rejected_fact_decision_count": sum(
            int(record["pending_rejected_fact_decision_count"]) for record in records
        ),
        "priority_lane_counts": dict(
            sorted(Counter(str(record["priority_lane"]) for record in records).items())
        ),
        "decision_status_counts": dict(sorted(status_counts.items())),
        "records": records,
    }

def build_gold_review_session_plan(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    target_session_minutes: int = 90,
    workload_plan: dict[str, Any] | None = None,
    decision_progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    workload_plan = workload_plan or build_gold_review_workload_plan(repo_root)
    decision_progress = decision_progress or build_gold_review_decision_progress(repo_root)
    progress_by_source_id = decision_progress_record_lookup(decision_progress)
    review_records: list[dict[str, Any]] = []
    for record in workload_plan["recommended_review_order"]:
        progress = progress_by_source_id.get(str(record.get("source_id")), {})
        progress_status = progress.get("status", "not_started")
        review_records.append(
            {
                **record,
                "decision_status": progress_status,
                "decision_issue_count": progress.get("issue_count", 0),
                "pending_rejected_fact_decision_count": progress.get(
                    "rejected_fact_decisions",
                    {},
                ).get("pending", 0),
                "decision_template": project_relative_path(
                    repo_root / GOLD_REVIEW_DECISION_DIR / f"{record['batch_id']}.jsonl",
                    repo_root,
                ),
                "priority_packet": project_relative_path(
                    repo_root
                    / GOLD_REVIEW_PRIORITY_PACKET_DIR
                    / f"{record['priority_lane']}.md",
                    repo_root,
                ),
            }
        )

    sessions: list[dict[str, Any]] = []
    current_records: list[dict[str, Any]] = []
    current_minutes = 0
    for record in review_records:
        minutes = int(record["estimated_review_minutes"])
        if current_records and current_minutes + minutes > target_session_minutes:
            sessions.append(
                gold_review_session_summary(
                    session_id=review_session_id(len(sessions) + 1),
                    records=current_records,
                )
            )
            current_records = []
            current_minutes = 0
        current_records.append(record)
        current_minutes += minutes
    if current_records:
        sessions.append(
            gold_review_session_summary(
                session_id=review_session_id(len(sessions) + 1),
                records=current_records,
            )
        )
    remaining_records = [
        record for record in review_records if record["decision_status"] != "ready_to_apply"
    ]
    next_session = next(
        (session for session in sessions if session["status"] != "ready_to_apply"),
        None,
    )

    return {
        "source_family": "nasa_atmonto_gold_review_session_plan",
        "status": "ready_for_manual_review" if remaining_records else "ready_to_apply",
        "workload_plan": project_relative_path(repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD, repo_root),
        "decision_progress": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD,
            repo_root,
        ),
        "session_plan_json": project_relative_path(
            repo_root / GOLD_REVIEW_SESSION_PLAN_JSON,
            repo_root,
        ),
        "session_plan_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_SESSION_PLAN_MD,
            repo_root,
        ),
        "target_session_minutes": target_session_minutes,
        "record_count": len(review_records),
        "ready_to_apply_record_count": len(review_records) - len(remaining_records),
        "remaining_record_count": len(remaining_records),
        "estimated_remaining_review_minutes": sum(
            int(record["estimated_review_minutes"]) for record in remaining_records
        ),
        "session_count": len(sessions),
        "completed_session_count": sum(
            1 for session in sessions if session["status"] == "ready_to_apply"
        ),
        "next_session": next_session,
        "sessions": sessions,
        "completion_gate": (
            "Session plans are manual-review queues only. A record becomes gold only after "
            "the reviewer confirms decisions in review_decisions JSONL, applies the draft, "
            "validates annotations, and freezes the reviewed gold set."
        ),
    }

def gold_review_session_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Session Plan",
        "",
        f"- Status: `{plan['status']}`",
        f"- Workload plan: `{plan['workload_plan']}`",
        f"- Decision progress: `{plan['decision_progress']}`",
        f"- Target session length: {plan['target_session_minutes']} minutes",
        f"- Ready-to-apply records: {plan['ready_to_apply_record_count']}",
        f"- Remaining records: {plan['remaining_record_count']}",
        f"- Estimated remaining review time: {plan['estimated_remaining_review_minutes']} minutes",
        f"- Completed sessions: {plan['completed_session_count']} / {plan['session_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {plan['completion_gate']}",
        "",
    ]
    if not plan["sessions"]:
        return "\n".join(lines + ["## Sessions", "", "- No remaining review records."]) + "\n"

    next_session = plan.get("next_session")
    if next_session:
        lines.extend(
            [
                "## Next Session",
                "",
                f"- Session: `{next_session['session_id']}`",
                f"- Status: `{next_session['status']}`",
                f"- Records: {next_session['record_count']}",
                f"- Ready / remaining records: {next_session['ready_to_apply_record_count']} / {next_session['remaining_record_count']}",
                f"- Estimated minutes: {next_session['estimated_review_minutes']}",
                f"- Pending rejected-fact decisions: {next_session['pending_rejected_fact_decision_count']}",
                "",
                "| Order | Sample | Source | Status | Batch | Lane | Est. min | Rejected pending | Decision file | Priority packet |",
                "| ---: | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
            ]
        )
        for index, record in enumerate(next_session["records"], start=1):
            lines.append(
                "| "
                f"{index} | "
                f"`{record['sample_id']}` | "
                f"`{record['source_id']}` | "
                f"`{record['decision_status']}` | "
                f"`{record['batch_id']}` | "
                f"`{record['priority_lane']}` | "
                f"{record['estimated_review_minutes']} | "
                f"{record['pending_rejected_fact_decision_count']} | "
                f"`{record['decision_template']}` | "
                f"`{record['priority_packet']}` |"
            )
    else:
        lines.extend(["## Next Session", "", "- No remaining review records."])

    lines.extend(
        [
            "",
            "## Sessions",
            "",
            "| Session | Status | Records | Ready | Remaining | Est. min | Rejected facts | Pending rejected decisions | Lanes |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for session in plan["sessions"]:
        lines.append(
            "| "
            f"`{session['session_id']}` | "
            f"`{session['status']}` | "
            f"{session['record_count']} | "
            f"{session['ready_to_apply_record_count']} | "
            f"{session['remaining_record_count']} | "
            f"{session['estimated_review_minutes']} | "
            f"{session['rejected_fact_count']} | "
            f"{session['pending_rejected_fact_decision_count']} | "
            f"`{json.dumps(session['priority_lane_counts'], sort_keys=True)}` |"
        )
    return "\n".join(lines).rstrip() + "\n"

def run_gold_review_session_plan(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    plan = build_gold_review_session_plan(repo_root)
    write_json(repo_root / GOLD_REVIEW_SESSION_PLAN_JSON, plan)
    (repo_root / GOLD_REVIEW_SESSION_PLAN_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_SESSION_PLAN_MD).write_text(
        gold_review_session_plan_markdown(plan),
        encoding="utf-8",
    )
    return {
        "session_plan_json": plan["session_plan_json"],
        "session_plan_markdown": plan["session_plan_markdown"],
        "status": plan["status"],
        "ready_to_apply_record_count": plan["ready_to_apply_record_count"],
        "remaining_record_count": plan["remaining_record_count"],
        "session_count": plan["session_count"],
        "completed_session_count": plan["completed_session_count"],
    }

def priority_lane_label(lane: str) -> str:
    labels = {
        "1_rejection_adjudication": "Rejected-fact adjudication first",
        "2_high_cross_system_coverage": "High cross-system candidate coverage",
        "3_standard_review": "Standard source review",
    }
    return labels.get(lane, lane)

def cluster_copy_ids(cluster: dict[str, Any]) -> dict[str, list[str]]:
    s0_ids: list[str] = []
    cross_system_ids: list[str] = []
    all_ids: list[str] = []
    for observation in cluster.get("system_observations", []):
        if not isinstance(observation, dict):
            continue
        fact_id = str(observation.get("fact_id", ""))
        if not fact_id:
            continue
        all_ids.append(fact_id)
        system_id = str(observation.get("system_id", ""))
        if system_id == "S0_rule_only":
            s0_ids.append(fact_id)
        elif observation.get("accepted_by_validator") is True:
            cross_system_ids.append(fact_id)
    return {
        "s0_fact_ids": sorted(set(s0_ids)),
        "schema_valid_cross_system_fact_ids": sorted(set(cross_system_ids)),
        "all_fact_ids": sorted(set(all_ids)),
    }

def review_packet_candidate_cluster(cluster: dict[str, Any]) -> dict[str, Any]:
    copy_ids = cluster_copy_ids(cluster)
    return {
        "candidate_id": cluster.get("candidate_id"),
        "source_systems": cluster.get("source_systems", []),
        "schema_status_counts": cluster.get("schema_status_counts", {}),
        "schema_error_counts": cluster.get("schema_error_counts", {}),
        "accepted_by_any_system_validator": cluster.get("accepted_by_any_system_validator"),
        "rejected_by_all_system_validators": cluster.get("rejected_by_all_system_validators"),
        "review_fields": cluster.get("review_fields", {}),
        **copy_ids,
    }

def build_gold_review_priority_packets(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    workload_plan = build_gold_review_workload_plan(repo_root, batch_size=batch_size)
    candidate_review = build_system_candidate_review_package(repo_root)
    worklist = build_gold_review_worklist(repo_root)
    candidate_by_sample = {
        str(record["sample_id"]): record for record in candidate_review["records"]
    }
    worklist_by_sample = {str(record["sample_id"]): record for record in worklist["records"]}

    lanes: dict[str, dict[str, Any]] = {}
    for workload_record in workload_plan["recommended_review_order"]:
        lane_id = str(workload_record["priority_lane"])
        sample_id = str(workload_record["sample_id"])
        candidate_record = candidate_by_sample[sample_id]
        work_record = worklist_by_sample[sample_id]
        lane = lanes.setdefault(
            lane_id,
            {
                "lane_id": lane_id,
                "label": priority_lane_label(lane_id),
                "path": project_relative_path(
                    repo_root / GOLD_REVIEW_PRIORITY_PACKET_DIR / f"{lane_id}.md",
                    repo_root,
                ),
                "records": [],
            },
        )
        decision_template = (
            GOLD_REVIEW_DECISION_DIR / f"{workload_record['batch_id']}.jsonl"
        )
        lane["records"].append(
            {
                **workload_record,
                "source_url": candidate_record.get("source_url"),
                "source_text_excerpt": candidate_record.get("source_text_excerpt", ""),
                "decision_template": project_relative_path(
                    repo_root / decision_template,
                    repo_root,
                ),
                "batch_markdown": project_relative_path(
                    repo_root / GOLD_REVIEW_BATCH_DIR / f"{workload_record['batch_id']}.md",
                    repo_root,
                ),
                "candidate_clusters": [
                    review_packet_candidate_cluster(cluster)
                    for cluster in candidate_record.get("candidate_clusters", [])
                    if isinstance(cluster, dict)
                ],
                "rejected_facts_to_adjudicate": work_record.get(
                    "rejected_facts_to_adjudicate",
                    [],
                ),
            }
        )

    lane_reports: list[dict[str, Any]] = []
    for lane_id in sorted(lanes):
        lane = lanes[lane_id]
        records = lane["records"]
        lane_reports.append(
            {
                **lane,
                "record_count": len(records),
                "estimated_review_minutes": sum(
                    int(record["estimated_review_minutes"]) for record in records
                ),
                "candidate_cluster_count": sum(
                    int(record["candidate_cluster_count"]) for record in records
                ),
                "cross_system_candidate_cluster_count": sum(
                    int(record["cross_system_candidate_cluster_count"])
                    for record in records
                ),
                "rejected_fact_count": sum(
                    int(record["rejected_fact_count"]) for record in records
                ),
            }
        )

    return {
        "source_family": "nasa_atmonto_gold_review_priority_packets",
        "workload_plan": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD,
            repo_root,
        ),
        "candidate_review_jsonl": candidate_review["candidate_review_jsonl"],
        "decision_templates": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_INDEX_MD,
            repo_root,
        ),
        "packet_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
            repo_root,
        ),
        "record_count": workload_plan["record_count"],
        "lane_count": len(lane_reports),
        "priority_lane_counts": workload_plan["priority_lane_counts"],
        "lanes": lane_reports,
        "completion_gate": (
            "Priority packets are reviewer work aids. They do not make a record reviewed; "
            "final decisions must still be entered in review_decisions JSONL and validated."
        ),
    }

def gold_review_priority_packet_index_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Priority Packets",
        "",
        f"- Workload plan: `{report['workload_plan']}`",
        f"- Candidate review: `{report['candidate_review_jsonl']}`",
        f"- Decision templates: `{report['decision_templates']}`",
        f"- Records: {report['record_count']}",
        f"- Priority lanes: `{json.dumps(report['priority_lane_counts'], sort_keys=True)}`",
        "",
        "## Packets",
        "",
        "| Lane | Records | Est. min | Candidate clusters | Cross-system clusters | Rejected facts | File |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for lane in report["lanes"]:
        lines.append(
            "| "
            f"`{lane['lane_id']}` | "
            f"{lane['record_count']} | "
            f"{lane['estimated_review_minutes']} | "
            f"{lane['candidate_cluster_count']} | "
            f"{lane['cross_system_candidate_cluster_count']} | "
            f"{lane['rejected_fact_count']} | "
            f"`{lane['path']}` |"
        )
    lines.extend(["", "## Completion Gate", "", f"- {report['completion_gate']}"])
    return "\n".join(lines).rstrip() + "\n"

def gold_review_priority_packet_summary(report: dict[str, Any]) -> dict[str, Any]:
    lanes: list[dict[str, Any]] = []
    for lane in report["lanes"]:
        lanes.append(
            {
                key: value
                for key, value in lane.items()
                if key != "records"
            }
            | {
                "records": [
                    {
                        key: record[key]
                        for key in (
                            "sample_id",
                            "source_id",
                            "batch_id",
                            "candidate_subject_class",
                            "priority_lane",
                            "complexity_tier",
                            "workload_score",
                            "estimated_review_minutes",
                            "candidate_cluster_count",
                            "cross_system_candidate_cluster_count",
                            "rejected_fact_count",
                            "decision_template",
                            "batch_markdown",
                        )
                    }
                    for record in lane["records"]
                ]
            }
        )
    return {
        key: value
        for key, value in report.items()
        if key not in {"lanes"}
    } | {"lanes": lanes}

def gold_review_priority_packet_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# NASA ATMONTO Gold Review Priority Packet: {packet['lane_id']}",
        "",
        f"- Label: {packet['label']}",
        f"- Records: {packet['record_count']}",
        f"- Estimated review time: {packet['estimated_review_minutes']} minutes",
        f"- Candidate clusters: {packet['candidate_cluster_count']}",
        f"- Cross-system clusters: {packet['cross_system_candidate_cluster_count']}",
        f"- Rejected facts: {packet['rejected_fact_count']}",
        "",
        "## Packet Checklist",
        "",
        "- [ ] Read the source excerpt and open the source URL when the excerpt is insufficient.",
        "- [ ] Copy source-supported S0 IDs into `valid_candidate_fact_ids`.",
        "- [ ] Copy source-supported schema-valid S1-S3 IDs into `valid_cross_system_fact_ids`.",
        "- [ ] Add corrected or missing facts manually when no candidate is source-correct.",
        "- [ ] Complete rejected-fact adjudications when present.",
        "",
    ]
    for record in packet["records"]:
        lines.extend(
            [
                f"## {record['sample_id']} / {record['source_id']}",
                "",
                f"- Batch: `{record['batch_id']}`",
                f"- Decision template: `{record['decision_template']}`",
                f"- Batch checklist: `{record['batch_markdown']}`",
                f"- Priority lane: `{record['priority_lane']}`",
                f"- Complexity: `{record['complexity_tier']}` (score={record['workload_score']}, est={record['estimated_review_minutes']} min)",
                f"- Candidate class: `{record['candidate_subject_class']}`",
                f"- Candidate clusters: {record['candidate_cluster_count']}",
                f"- Cross-system clusters: {record['cross_system_candidate_cluster_count']}",
                f"- Rejected facts: {record['rejected_fact_count']}",
                f"- Source URL: {record.get('source_url')}",
                "",
                "Source excerpt:",
                "",
                f"> {markdown_cell(record.get('source_text_excerpt'), max_chars=900)}",
                "",
            ]
        )
        if record["rejected_facts_to_adjudicate"]:
            lines.extend(
                [
                    "Rejected facts to adjudicate:",
                    "",
                    "| Fact ID | Predicate | Errors | Suggested decision | Evidence |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for fact in record["rejected_facts_to_adjudicate"]:
                lines.append(
                    "| "
                    f"`{fact.get('fact_id')}` | "
                    f"`{fact.get('predicate')}` | "
                    f"`{', '.join(fact.get('errors', []))}` | "
                    f"`{fact.get('suggested_decision')}` | "
                    f"{markdown_cell(fact.get('evidence_text'), max_chars=220)} |"
                )
            lines.append("")
        lines.extend(
            [
                "Candidate clusters:",
                "",
                "| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for cluster in record["candidate_clusters"]:
            fields = cluster["review_fields"]
            lines.append(
                "| "
                f"`{cluster['candidate_id']}` | "
                f"`{', '.join(cluster['source_systems'])}` | "
                f"`{markdown_cell(fields.get('predicate'), max_chars=80)}` | "
                f"{markdown_cell(fields.get('value_or_object'), max_chars=140)} | "
                f"`{', '.join(cluster['s0_fact_ids'])}` | "
                f"`{', '.join(cluster['schema_valid_cross_system_fact_ids'])}` | "
                f"`{markdown_cell(json.dumps(cluster['schema_status_counts'], sort_keys=True), max_chars=100)}` | "
                f"`{markdown_cell(json.dumps(cluster['schema_error_counts'], sort_keys=True), max_chars=100)}` | "
                f"{markdown_cell(fields.get('evidence_text'), max_chars=180)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def run_gold_review_priority_packets(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_gold_review_priority_packets(repo_root)
    write_json(repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON, gold_review_priority_packet_summary(report))
    (repo_root / GOLD_REVIEW_PRIORITY_PACKET_DIR).mkdir(parents=True, exist_ok=True)
    for lane in report["lanes"]:
        (repo_root / lane["path"]).write_text(
            gold_review_priority_packet_markdown(lane),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD).write_text(
        gold_review_priority_packet_index_markdown(report),
        encoding="utf-8",
    )
    return {
        "priority_packet_json": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON,
            repo_root,
        ),
        "priority_packet_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
            repo_root,
        ),
        "record_count": report["record_count"],
        "lane_count": report["lane_count"],
        "priority_lane_counts": report["priority_lane_counts"],
        "packet_files": [lane["path"] for lane in report["lanes"]],
    }

def gold_review_record_progress(record: dict[str, Any]) -> dict[str, Any]:
    annotation = record.get("gold_annotation", {})
    status = str(annotation.get("annotation_status", "missing_status"))
    return {
        "sample_id": record.get("sample_id"),
        "source_id": record.get("source_id"),
        "annotation_status": status,
        "review_complete": status == REVIEWED_GOLD_STATUS,
        "valid_fact_count": len(annotation.get("valid_facts", [])),
        "missing_fact_count": len(annotation.get("missing_facts", [])),
        "invalid_candidate_fact_count": len(annotation.get("invalid_candidate_fact_ids", [])),
        "rejected_fact_adjudication_count": len(
            annotation.get("rejected_fact_adjudications", [])
        ),
        "notes_present": bool(str(annotation.get("notes", "")).strip()),
    }

def build_gold_review_progress(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
    batch_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    if batch_report is None:
        batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)
    validation = validate_gold_annotation_records(
        gold_records=gold_records,
        selected_source_ids=selected_ids,
    )
    progress_by_source_id = {
        str(record.get("source_id")): gold_review_record_progress(record)
        for record in gold_records
    }
    batch_progress: list[dict[str, Any]] = []
    for batch in batch_report["batches"]:
        records = [
            progress_by_source_id.get(str(record.get("source_id")))
            for record in batch["records"]
        ]
        concrete_records = [record for record in records if isinstance(record, dict)]
        reviewed_count = sum(1 for record in concrete_records if record["review_complete"])
        pending_count = len(concrete_records) - reviewed_count
        if pending_count == 0 and concrete_records:
            status = "complete"
        elif reviewed_count == 0:
            status = "not_started"
        else:
            status = "in_progress"
        batch_progress.append(
            {
                "batch_id": batch["batch_id"],
                "path": batch["path"],
                "status": status,
                "record_count": len(concrete_records),
                "reviewed_record_count": reviewed_count,
                "pending_record_count": pending_count,
                "candidate_cluster_count": batch["candidate_cluster_count"],
                "first_sample_id": batch["first_sample_id"],
                "last_sample_id": batch["last_sample_id"],
                "records": concrete_records,
            }
        )

    reviewed_total = sum(batch["reviewed_record_count"] for batch in batch_progress)
    pending_total = sum(batch["pending_record_count"] for batch in batch_progress)
    return {
        "source_family": "nasa_atmonto_gold_review_progress",
        "status": (
            "ready_for_freeze"
            if validation["status"] == "ready_for_scoring"
            else "pending_manual_review"
        ),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "batch_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_BATCH_INDEX_MD,
            repo_root,
        ),
        "review_progress_json": project_relative_path(
            repo_root / GOLD_REVIEW_PROGRESS_JSON,
            repo_root,
        ),
        "review_progress_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PROGRESS_MD,
            repo_root,
        ),
        "record_count": len(gold_records),
        "reviewed_record_count": reviewed_total,
        "pending_record_count": pending_total,
        "batch_count": len(batch_progress),
        "complete_batch_count": sum(
            1 for batch in batch_progress if batch["status"] == "complete"
        ),
        "validation_status": validation["status"],
        "validation_error_count": validation["error_count"],
        "validation_warning_count": validation["warning_count"],
        "batch_progress": batch_progress,
        "completion_gate": (
            "All batches must be complete and gold annotation validation must be "
            "ready_for_scoring before freezing atcscc_gold_v1.reviewed.jsonl."
        ),
    }

def gold_review_progress_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Progress",
        "",
        f"- Status: `{report['status']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Batch index: `{report['batch_index_markdown']}`",
        f"- Records: {report['record_count']}",
        f"- Reviewed records: {report['reviewed_record_count']}",
        f"- Pending records: {report['pending_record_count']}",
        f"- Complete batches: {report['complete_batch_count']} / {report['batch_count']}",
        f"- Validation status: `{report['validation_status']}`",
        f"- Validation errors: {report['validation_error_count']}",
        f"- Validation warnings: {report['validation_warning_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Batch Progress",
        "",
        "| Batch | Status | Reviewed | Pending | Candidate clusters | File |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for batch in report["batch_progress"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['status']}` | "
            f"{batch['reviewed_record_count']} | "
            f"{batch['pending_record_count']} | "
            f"{batch['candidate_cluster_count']} | "
            f"`{batch['path']}` |"
        )
    return "\n".join(lines) + "\n"

def run_gold_review_progress(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_gold_review_progress(repo_root, batch_size=batch_size)
    write_json(repo_root / GOLD_REVIEW_PROGRESS_JSON, report)
    (repo_root / GOLD_REVIEW_PROGRESS_MD).write_text(
        gold_review_progress_markdown(report),
        encoding="utf-8",
    )
    return {
        "review_progress_json": report["review_progress_json"],
        "review_progress_markdown": report["review_progress_markdown"],
        "status": report["status"],
        "reviewed_record_count": report["reviewed_record_count"],
        "pending_record_count": report["pending_record_count"],
        "complete_batch_count": report["complete_batch_count"],
        "batch_count": report["batch_count"],
    }

def rejection_adjudication_decision_lookup(
    rejection_adjudication: dict[str, Any],
) -> dict[tuple[str, tuple[str, ...]], dict[str, Any]]:
    lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
    for group in rejection_adjudication.get("groups", []):
        predicate = str(group.get("predicate", ""))
        errors = tuple(str(error) for error in group.get("errors", []))
        lookup[(predicate, errors)] = group
    return lookup

def rejected_fact_decision_template(
    record: dict[str, Any],
    *,
    rejection_adjudication_lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]]
    | None = None,
) -> list[dict[str, Any]]:
    candidate_by_id = {
        str(candidate.get("fact_id")): candidate
        for candidate in record.get("candidate_facts", [])
        if isinstance(candidate, dict) and candidate.get("fact_id")
    }
    templates: list[dict[str, Any]] = []
    for result in record.get("validator_results", []):
        if not isinstance(result, dict) or result.get("accepted") is not False:
            continue
        fact_id = str(result.get("fact_id", ""))
        candidate = candidate_by_id.get(fact_id, {})
        predicate = term_name(candidate.get("predicate"))
        errors = tuple(str(error) for error in result.get("errors", []))
        suggestion = (
            (rejection_adjudication_lookup or {}).get((predicate, errors), {})
        )
        templates.append(
            {
                "fact_id": fact_id,
                "predicate": predicate,
                "errors": list(errors),
                "evidence_text": compact_text(candidate.get("evidence_text")),
                "decision": "",
                "rationale": "",
                "recommended_action": "",
                "suggested_decision": suggestion.get("final_decision", ""),
                "suggested_confidence": suggestion.get("confidence", ""),
                "suggested_rationale": suggestion.get("decision_basis", ""),
                "suggested_recommended_action": suggestion.get("required_follow_up", ""),
            }
        )
    return templates

def validator_accepted_candidate_fact_ids(record: dict[str, Any]) -> list[str]:
    candidate_fact_ids = [
        str(candidate.get("fact_id"))
        for candidate in record.get("candidate_facts", [])
        if isinstance(candidate, dict) and candidate.get("fact_id")
    ]
    accepted_fact_ids = {
        str(result.get("fact_id"))
        for result in record.get("validator_results", [])
        if isinstance(result, dict)
        and result.get("accepted") is True
        and result.get("fact_id")
    }
    return [fact_id for fact_id in candidate_fact_ids if fact_id in accepted_fact_ids]

def cross_system_candidate_options(record: dict[str, Any]) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for cluster in record.get("candidate_clusters", []):
        if not isinstance(cluster, dict):
            continue
        review_fields = cluster.get("review_fields", {})
        for observation in cluster.get("system_observations", []):
            if not isinstance(observation, dict):
                continue
            system_id = str(observation.get("system_id", ""))
            fact_id = str(observation.get("fact_id", ""))
            if system_id == "S0_rule_only" or not fact_id:
                continue
            if observation.get("accepted_by_validator") is not True:
                continue
            options.append(
                {
                    "fact_id": fact_id,
                    "candidate_id": cluster.get("candidate_id"),
                    "system_id": system_id,
                    "validator_status": observation.get("validator_status"),
                    "review_fields": review_fields,
                }
            )
    return options

def gold_review_decision_record(
    *,
    batch_id: str,
    record: dict[str, Any],
    gold_record: dict[str, Any],
    rejection_adjudication_lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]]
    | None = None,
) -> dict[str, Any]:
    cross_system_options = cross_system_candidate_options(record)
    accepted_candidate_fact_ids = validator_accepted_candidate_fact_ids(gold_record)
    return {
        "batch_id": batch_id,
        "sample_id": record.get("sample_id"),
        "source_id": record.get("source_id"),
        "source_url": record.get("source_url"),
        "annotation_status": PENDING_GOLD_STATUS,
        "annotator_id": "",
        "reviewed_at": "",
        "notes": "",
        "review_checklist": review_checklist_template(),
        "valid_candidate_fact_ids": [],
        "valid_cross_system_fact_ids": [],
        "invalid_candidate_fact_ids": [],
        "missing_facts": [],
        "suggested_valid_candidate_fact_ids": accepted_candidate_fact_ids,
        "rejected_fact_adjudications": rejected_fact_decision_template(
            gold_record,
            rejection_adjudication_lookup=rejection_adjudication_lookup,
        ),
        "review_context": {
            "candidate_cluster_count": record.get("candidate_cluster_count"),
            "candidate_cluster_ids": [
                cluster.get("candidate_id") for cluster in record.get("candidate_clusters", [])
            ],
            "candidate_fact_ids": [
                candidate.get("fact_id")
                for candidate in gold_record.get("candidate_facts", [])
                if isinstance(candidate, dict)
            ],
            "validator_accepted_candidate_fact_ids": accepted_candidate_fact_ids,
            "cross_system_fact_ids": [option["fact_id"] for option in cross_system_options],
            "cross_system_candidate_options": cross_system_options,
        },
        "instructions": (
            "Set annotation_status to reviewed only after source-text review. Put accepted "
            "rule-baseline fact IDs in valid_candidate_fact_ids, rejected rule-baseline IDs "
            "in invalid_candidate_fact_ids, put accepted S1-S3 schema-valid fact IDs in "
            "valid_cross_system_fact_ids, add corrected/manual facts to missing_facts, and "
            "complete every rejected_fact_adjudications decision. Set all review_checklist "
            "items to true only after completing the source-text, semantic-rubric, profile-gap, "
            "and missing-fact checks. The suggested_valid_candidate_fact_ids field lists "
            "validator-accepted S0 facts, and rejected-fact suggested_* fields are copied from "
            "property-level rejection adjudication. All suggestions must be confirmed, edited, "
            "or rejected by the reviewer before scoring."
        ),
    }

def build_gold_review_decision_templates(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
    batch_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from ._rejection_adjudication import build_rejection_adjudication_report
    repo_root = Path(repo_root).resolve()
    if batch_report is None:
        batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)
    gold_records_by_source_id = {
        str(record.get("source_id")): record for record in read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    }
    rejection_adjudication = build_rejection_adjudication_report(repo_root)
    adjudication_lookup = rejection_adjudication_decision_lookup(rejection_adjudication)
    batches: list[dict[str, Any]] = []
    for batch in batch_report["batches"]:
        decision_records = [
            gold_review_decision_record(
                batch_id=batch["batch_id"],
                record=record,
                gold_record=gold_records_by_source_id[str(record.get("source_id"))],
                rejection_adjudication_lookup=adjudication_lookup,
            )
            for record in batch["records"]
        ]
        batches.append(
            {
                "batch_id": batch["batch_id"],
                "path": project_relative_path(
                    repo_root / GOLD_REVIEW_DECISION_DIR / f"{batch['batch_id']}.jsonl",
                    repo_root,
                ),
                "record_count": len(decision_records),
                "first_sample_id": batch["first_sample_id"],
                "last_sample_id": batch["last_sample_id"],
                "rejected_fact_adjudication_count": sum(
                    len(record["rejected_fact_adjudications"]) for record in decision_records
                ),
                "suggested_valid_candidate_fact_count": sum(
                    len(record["suggested_valid_candidate_fact_ids"])
                    for record in decision_records
                ),
                "records": decision_records,
            }
        )
    return {
        "source_family": "nasa_atmonto_gold_review_decision_templates",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "decision_template_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_INDEX_MD,
            repo_root,
        ),
        "decision_dir": project_relative_path(repo_root / GOLD_REVIEW_DECISION_DIR, repo_root),
        "batch_count": len(batches),
        "record_count": sum(batch["record_count"] for batch in batches),
        "suggested_valid_candidate_fact_count": sum(
            batch["suggested_valid_candidate_fact_count"] for batch in batches
        ),
        "batches": batches,
        "completion_gate": (
            "Decision templates are editable review inputs. Applying them with all records "
            "still pending must not produce reviewed gold; set records to reviewed only after "
            "manual source-text review."
        ),
    }

def gold_review_decision_index_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Decision Templates",
        "",
        f"- Gold template: `{report['gold_template']}`",
        f"- Decision directory: `{report['decision_dir']}`",
        f"- Records: {report['record_count']}",
        f"- Batches: {report['batch_count']}",
        f"- Suggested valid S0 candidate facts: {report['suggested_valid_candidate_fact_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "- `review_checklist` items must all be true before a record can be "
        "applied as reviewed.",
        "- `suggested_valid_candidate_fact_ids` lists S0 facts accepted by the schema "
        "validator; copy only source-supported IDs into `valid_candidate_fact_ids`.",
        "- Rejected-fact `suggested_*` fields are copied from "
        "`reports/stages/nasa_atmonto_rejection_adjudication.md`; leave `decision`, "
        "`rationale`, and `recommended_action` empty until a reviewer confirms them.",
        "",
        "## Decision Files",
        "",
        "| Batch | Samples | Records | Suggested valid S0 facts | Rejected facts | File |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for batch in report["batches"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['first_sample_id']}`-`{batch['last_sample_id']}` | "
            f"{batch['record_count']} | "
            f"{batch['suggested_valid_candidate_fact_count']} | "
            f"{batch['rejected_fact_adjudication_count']} | "
            f"`{batch['path']}` |"
        )
    return "\n".join(lines) + "\n"

def run_gold_review_decision_templates(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)
    report = build_gold_review_decision_templates(repo_root, batch_report=batch_report)
    (repo_root / GOLD_REVIEW_DECISION_DIR).mkdir(parents=True, exist_ok=True)
    for batch in report["batches"]:
        write_jsonl(repo_root / batch["path"], batch["records"])
    (repo_root / GOLD_REVIEW_DECISION_INDEX_MD).write_text(
        gold_review_decision_index_markdown(report),
        encoding="utf-8",
    )
    return {
        "decision_template_index_markdown": report["decision_template_index_markdown"],
        "decision_dir": report["decision_dir"],
        "batch_count": report["batch_count"],
        "record_count": report["record_count"],
        "decision_files": [batch["path"] for batch in report["batches"]],
    }

def read_gold_review_decisions(decision_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(decision_dir.glob("batch_*.jsonl")):
        records.extend(read_jsonl(path))
    return records

def gold_review_decision_has_manual_edits(decision: dict[str, Any]) -> bool:
    if str(decision.get("annotation_status", PENDING_GOLD_STATUS)) != PENDING_GOLD_STATUS:
        return True
    if str(decision.get("annotator_id", "")).strip():
        return True
    if str(decision.get("reviewed_at", "")).strip():
        return True
    if str(decision.get("notes", "")).strip():
        return True
    checklist = decision.get("review_checklist")
    if isinstance(checklist, dict) and any(checklist.get(field) for field in REVIEW_CHECKLIST_FIELDS):
        return True
    for field in (
        "valid_candidate_fact_ids",
        "valid_cross_system_fact_ids",
        "invalid_candidate_fact_ids",
        "missing_facts",
    ):
        if decision.get(field):
            return True
    for adjudication in decision.get("rejected_fact_adjudications", []):
        if not isinstance(adjudication, dict):
            continue
        if any(
            str(adjudication.get(field, "")).strip()
            for field in ("decision", "rationale", "recommended_action")
        ):
            return True
    return False

def rejection_decision_completion_counts(decision: dict[str, Any]) -> dict[str, int]:
    adjudications = [
        item
        for item in decision.get("rejected_fact_adjudications", [])
        if isinstance(item, dict)
    ]
    completed = 0
    for adjudication in adjudications:
        if (
            str(adjudication.get("decision", "")) in ALLOWED_REJECTION_ADJUDICATIONS
            and str(adjudication.get("rationale", "")).strip()
            and str(adjudication.get("recommended_action", "")).strip()
        ):
            completed += 1
    total = len(adjudications)
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
    }

def build_cross_system_fact_lookup(
    *,
    repo_root: Path,
    selected_ids: set[str],
) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for system in SYSTEMS:
        if system.system_id == "S0_rule_only":
            continue
        parse_result = read_jsonl_lenient(repo_root / system.expected_output)
        if not parse_result["exists"]:
            continue
        for record in valid_prediction_records(parse_result, selected_ids):
            for fact in system_candidate_facts(system, record):
                fact_id = str(fact.get("fact_id", ""))
                if not fact_id:
                    continue
                enriched = dict(fact)
                enriched.setdefault("source_id", record.get("source_id"))
                enriched["source_system_id"] = system.system_id
                enriched["selected_as_gold_from_cross_system_candidate"] = True
                lookup[fact_id] = enriched
    return lookup

def unique_facts_by_id(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for index, fact in enumerate(facts):
        fact_id = str(fact.get("fact_id") or f"manual-missing-{index}")
        if fact_id in seen:
            continue
        seen.add(fact_id)
        unique.append(fact)
    return unique

def apply_gold_review_decision_to_record(
    *,
    gold_record: dict[str, Any],
    decision: dict[str, Any],
    cross_system_fact_lookup: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    source_id = str(gold_record.get("source_id"))
    cross_system_fact_lookup = cross_system_fact_lookup or {}
    candidate_by_id = {
        str(candidate.get("fact_id")): candidate
        for candidate in gold_record.get("candidate_facts", [])
        if isinstance(candidate, dict) and candidate.get("fact_id")
    }
    valid_ids = [str(value) for value in decision.get("valid_candidate_fact_ids", [])]
    cross_system_valid_ids = [
        str(value) for value in decision.get("valid_cross_system_fact_ids", [])
    ]
    invalid_ids = [str(value) for value in decision.get("invalid_candidate_fact_ids", [])]
    unknown_valid = sorted(set(valid_ids) - set(candidate_by_id))
    unknown_cross_system_valid = sorted(
        set(cross_system_valid_ids) - set(cross_system_fact_lookup)
    )
    unknown_invalid = sorted(set(invalid_ids) - set(candidate_by_id))
    if unknown_valid:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "unknown_valid_candidate_fact_ids",
                "fact_ids": unknown_valid,
            }
        )
    if unknown_cross_system_valid:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "unknown_valid_cross_system_fact_ids",
                "fact_ids": unknown_cross_system_valid,
            }
        )
    if unknown_invalid:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "unknown_invalid_candidate_fact_ids",
                "fact_ids": unknown_invalid,
            }
        )
    source_mismatch_ids = sorted(
        fact_id
        for fact_id in cross_system_valid_ids
        if str(cross_system_fact_lookup.get(fact_id, {}).get("source_id")) != source_id
    )
    if source_mismatch_ids:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "valid_cross_system_fact_source_mismatch",
                "fact_ids": source_mismatch_ids,
            }
        )
    if errors:
        return gold_record, errors

    status = str(decision.get("annotation_status", PENDING_GOLD_STATUS))
    if status not in {PENDING_GOLD_STATUS, REVIEWED_GOLD_STATUS}:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "invalid_annotation_status",
                "annotation_status": status,
            }
        )
        return gold_record, errors

    review_checklist = decision.get("review_checklist")
    incomplete_checklist = incomplete_review_checklist_fields(review_checklist)
    if status == REVIEWED_GOLD_STATUS and incomplete_checklist:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "incomplete_review_checklist",
                "fields": incomplete_checklist,
            }
        )
        return gold_record, errors

    updated = dict(gold_record)
    annotation = dict(updated.get("gold_annotation", {}))
    manual_missing_facts = [
        fact for fact in decision.get("missing_facts", []) if isinstance(fact, dict)
    ]
    cross_system_missing_facts = [
        cross_system_fact_lookup[fact_id] for fact_id in cross_system_valid_ids
    ]
    annotation.update(
        {
            "annotation_status": status,
            "annotator_id": str(decision.get("annotator_id", "")),
            "valid_facts": [candidate_by_id[fact_id] for fact_id in valid_ids],
            "invalid_candidate_fact_ids": invalid_ids,
            "missing_facts": unique_facts_by_id(
                [*manual_missing_facts, *cross_system_missing_facts]
            ),
            "review_checklist": (
                review_checklist_template(True)
                if status == REVIEWED_GOLD_STATUS
                else {
                    field: (
                        isinstance(review_checklist, dict)
                        and review_checklist.get(field) is True
                    )
                    for field in REVIEW_CHECKLIST_FIELDS
                }
            ),
            "rejected_fact_adjudications": [
                adjudication
                for adjudication in decision.get("rejected_fact_adjudications", [])
                if isinstance(adjudication, dict)
            ],
            "notes": str(decision.get("notes", "")),
        }
    )
    updated["gold_annotation"] = annotation
    return updated, []

def gold_review_decision_record_progress(
    *,
    gold_record: dict[str, Any],
    decision: dict[str, Any] | None,
    cross_system_fact_lookup: dict[str, dict[str, Any]],
    duplicate_source_ids: set[str],
) -> dict[str, Any]:
    sample_id = gold_record.get("sample_id")
    source_id = str(gold_record.get("source_id"))
    if decision is None:
        return {
            "sample_id": sample_id,
            "source_id": source_id,
            "annotation_status": "missing_decision_record",
            "status": "missing_decision",
            "manual_edits_present": False,
            "ready_to_apply": False,
            "issue_count": 1,
            "issues": [{"error": "missing_decision_record"}],
            "rejected_fact_decisions": {"total": 0, "completed": 0, "pending": 0},
        }

    errors: list[dict[str, Any]] = []
    if source_id in duplicate_source_ids:
        errors.append({"error": "duplicate_decision_source_id", "source_id": source_id})

    manual_edits_present = gold_review_decision_has_manual_edits(decision)
    rejection_counts = rejection_decision_completion_counts(decision)
    annotation_status = str(decision.get("annotation_status", PENDING_GOLD_STATUS))
    updated, apply_errors = apply_gold_review_decision_to_record(
        gold_record=gold_record,
        decision=decision,
        cross_system_fact_lookup=cross_system_fact_lookup,
    )
    errors.extend(apply_errors)

    if not apply_errors and annotation_status == REVIEWED_GOLD_STATUS:
        validation = validate_gold_annotation_records(
            gold_records=[updated],
            selected_source_ids={source_id},
        )
        errors.extend(validation["errors"])

    if errors:
        status = "needs_revision"
    elif annotation_status == REVIEWED_GOLD_STATUS:
        status = "ready_to_apply"
    elif manual_edits_present:
        status = "in_progress"
    else:
        status = "not_started"

    suggested_valid_candidate_fact_ids = decision.get("suggested_valid_candidate_fact_ids")
    if not isinstance(suggested_valid_candidate_fact_ids, list):
        suggested_valid_candidate_fact_ids = validator_accepted_candidate_fact_ids(gold_record)

    return {
        "sample_id": sample_id,
        "source_id": source_id,
        "annotation_status": annotation_status,
        "status": status,
        "manual_edits_present": manual_edits_present,
        "ready_to_apply": status == "ready_to_apply",
        "issue_count": len(errors),
        "issues": errors[:20],
        "suggested_valid_candidate_fact_count": len(suggested_valid_candidate_fact_ids),
        "rejected_fact_decisions": rejection_counts,
    }

def build_gold_review_decision_progress(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
    batch_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    if batch_report is None:
        batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)

    decision_root = repo_root / GOLD_REVIEW_DECISION_DIR
    decisions = read_gold_review_decisions(decision_root) if decision_root.exists() else []
    decision_source_ids = [str(decision.get("source_id")) for decision in decisions]
    duplicate_source_ids = {
        source_id for source_id, count in Counter(decision_source_ids).items() if count > 1
    }
    decisions_by_source_id = {
        str(decision.get("source_id")): decision
        for decision in decisions
        if decision.get("source_id")
    }
    gold_records_by_source_id = {
        str(record.get("source_id")): record for record in gold_records
    }
    cross_system_fact_lookup = build_cross_system_fact_lookup(
        repo_root=repo_root,
        selected_ids=selected_ids,
    )

    progress_by_source_id: dict[str, dict[str, Any]] = {}
    for source_id, gold_record in gold_records_by_source_id.items():
        progress_by_source_id[source_id] = gold_review_decision_record_progress(
            gold_record=gold_record,
            decision=decisions_by_source_id.get(source_id),
            cross_system_fact_lookup=cross_system_fact_lookup,
            duplicate_source_ids=duplicate_source_ids,
        )

    missing_decision_source_ids = sorted(set(gold_records_by_source_id) - set(decisions_by_source_id))
    unexpected_decision_source_ids = sorted(set(decisions_by_source_id) - set(gold_records_by_source_id))
    batch_progress: list[dict[str, Any]] = []
    for batch in batch_report["batches"]:
        records = [
            progress_by_source_id[str(record.get("source_id"))]
            for record in batch["records"]
            if str(record.get("source_id")) in progress_by_source_id
        ]
        status_counts = Counter(record["status"] for record in records)
        if status_counts.get("needs_revision", 0):
            status = "needs_revision"
        elif records and status_counts.get("ready_to_apply", 0) == len(records):
            status = "ready_to_apply"
        elif status_counts.get("in_progress", 0) or status_counts.get("ready_to_apply", 0):
            status = "in_progress"
        elif status_counts.get("missing_decision", 0):
            status = "missing_decisions"
        else:
            status = "not_started"
        rejected_counts = Counter()
        suggested_valid_candidate_count = 0
        for record in records:
            rejected_counts.update(record["rejected_fact_decisions"])
            suggested_valid_candidate_count += record["suggested_valid_candidate_fact_count"]
        batch_progress.append(
            {
                "batch_id": batch["batch_id"],
                "decision_path": project_relative_path(
                    repo_root / GOLD_REVIEW_DECISION_DIR / f"{batch['batch_id']}.jsonl",
                    repo_root,
                ),
                "status": status,
                "record_count": len(records),
                "ready_to_apply_record_count": status_counts.get("ready_to_apply", 0),
                "in_progress_record_count": status_counts.get("in_progress", 0),
                "not_started_record_count": status_counts.get("not_started", 0),
                "needs_revision_record_count": status_counts.get("needs_revision", 0),
                "missing_decision_record_count": status_counts.get("missing_decision", 0),
                "suggested_valid_candidate_fact_count": suggested_valid_candidate_count,
                "rejected_fact_decision_count": rejected_counts["total"],
                "completed_rejected_fact_decision_count": rejected_counts["completed"],
                "pending_rejected_fact_decision_count": rejected_counts["pending"],
                "records": records,
            }
        )

    total_status_counts = Counter(
        record["status"] for record in progress_by_source_id.values()
    )
    rejected_totals = Counter()
    suggested_valid_candidate_total = 0
    for record in progress_by_source_id.values():
        rejected_totals.update(record["rejected_fact_decisions"])
        suggested_valid_candidate_total += record["suggested_valid_candidate_fact_count"]
    status = (
        "ready_to_apply"
        if progress_by_source_id
        and total_status_counts.get("ready_to_apply", 0) == len(progress_by_source_id)
        and not unexpected_decision_source_ids
        and not duplicate_source_ids
        else "needs_revision"
        if total_status_counts.get("needs_revision", 0)
        or unexpected_decision_source_ids
        or duplicate_source_ids
        else "in_progress"
        if total_status_counts.get("in_progress", 0)
        or total_status_counts.get("ready_to_apply", 0)
        else "missing_decisions"
        if total_status_counts.get("missing_decision", 0)
        else "not_started"
    )
    return {
        "source_family": "nasa_atmonto_gold_review_decision_progress",
        "status": status,
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "decision_dir": project_relative_path(decision_root, repo_root),
        "decision_progress_json": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON,
            repo_root,
        ),
        "decision_progress_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD,
            repo_root,
        ),
        "record_count": len(gold_records_by_source_id),
        "decision_record_count": len(decisions),
        "ready_to_apply_record_count": total_status_counts.get("ready_to_apply", 0),
        "in_progress_record_count": total_status_counts.get("in_progress", 0),
        "not_started_record_count": total_status_counts.get("not_started", 0),
        "needs_revision_record_count": total_status_counts.get("needs_revision", 0),
        "missing_decision_record_count": total_status_counts.get("missing_decision", 0),
        "duplicate_decision_source_ids": sorted(duplicate_source_ids),
        "missing_decision_source_ids": missing_decision_source_ids,
        "unexpected_decision_source_ids": unexpected_decision_source_ids,
        "suggested_valid_candidate_fact_count": suggested_valid_candidate_total,
        "rejected_fact_decision_count": rejected_totals["total"],
        "completed_rejected_fact_decision_count": rejected_totals["completed"],
        "pending_rejected_fact_decision_count": rejected_totals["pending"],
        "batch_count": len(batch_progress),
        "ready_to_apply_batch_count": sum(
            1 for batch in batch_progress if batch["status"] == "ready_to_apply"
        ),
        "batch_progress": batch_progress,
        "completion_gate": (
            "All 100 decision records must be ready_to_apply before the reviewed draft can "
            "be treated as complete manual gold. Pending suggested_valid_candidate_fact_ids "
            "and rejected-fact suggested_* fields do not count until copied or edited into "
            "reviewer decision fields."
        ),
    }

def gold_review_decision_progress_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Decision Progress",
        "",
        f"- Status: `{report['status']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Decision directory: `{report['decision_dir']}`",
        f"- Records: {report['record_count']}",
        f"- Decision records: {report['decision_record_count']}",
        f"- Ready to apply: {report['ready_to_apply_record_count']}",
        f"- In progress: {report['in_progress_record_count']}",
        f"- Not started: {report['not_started_record_count']}",
        f"- Needs revision: {report['needs_revision_record_count']}",
        f"- Missing decisions: {report['missing_decision_record_count']}",
        f"- Suggested valid S0 candidate facts: {report['suggested_valid_candidate_fact_count']}",
        "- Rejected-fact decisions confirmed: "
        f"{report['completed_rejected_fact_decision_count']} / "
        f"{report['rejected_fact_decision_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Batch Progress",
        "",
        "| Batch | Status | Ready | In progress | Not started | Needs revision | "
        "Missing | Suggested valid S0 | Rejected decisions | File |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for batch in report["batch_progress"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['status']}` | "
            f"{batch['ready_to_apply_record_count']} | "
            f"{batch['in_progress_record_count']} | "
            f"{batch['not_started_record_count']} | "
            f"{batch['needs_revision_record_count']} | "
            f"{batch['missing_decision_record_count']} | "
            f"{batch['suggested_valid_candidate_fact_count']} | "
            f"{batch['completed_rejected_fact_decision_count']} / "
            f"{batch['rejected_fact_decision_count']} | "
            f"`{batch['decision_path']}` |"
        )

    attention_records = [
        (batch["batch_id"], record)
        for batch in report["batch_progress"]
        for record in batch["records"]
        if record["status"] != "ready_to_apply"
    ][:25]
    lines.extend(["", "## Records Needing Attention", ""])
    if not attention_records:
        lines.append("- None.")
    else:
        lines.extend(
            [
                "| Batch | Sample | Status | Issues | Rejected pending |",
                "| --- | --- | --- | ---: | ---: |",
            ]
        )
        for batch_id, record in attention_records:
            lines.append(
                "| "
                f"`{batch_id}` | "
                f"`{record['sample_id']}` | "
                f"`{record['status']}` | "
                f"{record['issue_count']} | "
                f"{record['rejected_fact_decisions']['pending']} |"
            )
        remaining = sum(
            1
            for batch in report["batch_progress"]
            for record in batch["records"]
            if record["status"] != "ready_to_apply"
        ) - len(attention_records)
        if remaining > 0:
            lines.append(f"- ... {remaining} more records omitted")

    if report["duplicate_decision_source_ids"]:
        lines.extend(["", "## Duplicate Decision Source IDs", ""])
        lines.append(", ".join(f"`{value}`" for value in report["duplicate_decision_source_ids"]))
    if report["unexpected_decision_source_ids"]:
        lines.extend(["", "## Unexpected Decision Source IDs", ""])
        lines.append(", ".join(f"`{value}`" for value in report["unexpected_decision_source_ids"]))
    return "\n".join(lines) + "\n"

def run_gold_review_decision_progress(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)
    report = build_gold_review_decision_progress(
        repo_root,
        batch_report=batch_report,
    )
    write_json(repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON, report)
    (repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD).write_text(
        gold_review_decision_progress_markdown(report),
        encoding="utf-8",
    )
    return {
        "decision_progress_json": report["decision_progress_json"],
        "decision_progress_markdown": report["decision_progress_markdown"],
        "status": report["status"],
        "ready_to_apply_record_count": report["ready_to_apply_record_count"],
        "in_progress_record_count": report["in_progress_record_count"],
        "not_started_record_count": report["not_started_record_count"],
        "needs_revision_record_count": report["needs_revision_record_count"],
        "missing_decision_record_count": report["missing_decision_record_count"],
        "record_count": report["record_count"],
    }

def apply_gold_review_decisions(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    decision_dir: str | Path = GOLD_REVIEW_DECISION_DIR,
    output_path: str | Path = GOLD_REVIEW_DECISION_DRAFT_PATH,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    decision_root = Path(decision_dir)
    if not decision_root.is_absolute():
        decision_root = repo_root / decision_root
    output = Path(output_path)
    if not output.is_absolute():
        output = repo_root / output

    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    decisions = read_gold_review_decisions(decision_root)
    cross_system_fact_lookup = build_cross_system_fact_lookup(
        repo_root=repo_root,
        selected_ids=selected_ids,
    )
    decisions_by_source_id = {str(decision.get("source_id")): decision for decision in decisions}
    errors: list[dict[str, Any]] = []
    duplicate_source_ids = [
        source_id
        for source_id, count in Counter(str(decision.get("source_id")) for decision in decisions).items()
        if count > 1
    ]
    if duplicate_source_ids:
        errors.append({"error": "duplicate_decision_source_ids", "source_ids": duplicate_source_ids})

    updated_records: list[dict[str, Any]] = []
    for record in gold_records:
        source_id = str(record.get("source_id"))
        decision = decisions_by_source_id.get(source_id)
        if decision is None:
            updated_records.append(record)
            continue
        updated, record_errors = apply_gold_review_decision_to_record(
            gold_record=record,
            decision=decision,
            cross_system_fact_lookup=cross_system_fact_lookup,
        )
        errors.extend(record_errors)
        updated_records.append(updated)

    if not errors:
        write_jsonl(output, updated_records)

    validation = validate_gold_annotation_records(
        gold_records=updated_records,
        selected_source_ids=selected_ids,
    )
    return {
        "source_family": "nasa_atmonto_gold_review_decision_apply",
        "decision_dir": project_relative_path(decision_root, repo_root),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "output_path": project_relative_path(output, repo_root),
        "output_written": not errors,
        "decision_record_count": len(decisions),
        "updated_record_count": len(updated_records),
        "error_count": len(errors),
        "errors": errors[:100],
        "validation_status": validation["status"],
        "validation_error_count": validation["error_count"],
        "validation_warning_count": validation["warning_count"],
        "reviewed_record_count": validation["reviewed_record_count"],
        "pending_record_count": validation["pending_record_count"],
    }

def final_rejection_group_decision(group: dict[str, Any]) -> dict[str, Any]:
    predicate = str(group.get("predicate", ""))
    errors = {str(error) for error in group.get("errors", [])}
    value_counts = group.get("value_counts", {})
    object_counts = group.get("object_class_counts", {})
    subject_counts = group.get("subject_class_counts", {})

    if (
        predicate == "controlledNASelement"
        and "range_violation" in errors
        and object_counts == {"ARTCC": group.get("count")}
    ):
        return {
            "final_decision": "profile_gap",
            "confidence": "high",
            "decision_basis": (
                "ATCSCC source evidence identifies constrained ARTCC centers, while the "
                "runtime NASA ATMONTO profile requires controlledNASelement objects to be "
                "atm:TFMcontrolElement. The mismatch is a profile coverage gap, not a "
                "surface extraction error."
            ),
            "required_follow_up": (
                "Add a reviewed profile bridge or alternate property for ARTCC-controlled "
                "NAS elements; keep current facts rejected until that profile change is approved."
            ),
        }
    if (
        predicate == "impactingConditionMessage"
        and "domain_violation" in errors
        and subject_counts == {"GroundStopTMI": group.get("count")}
    ):
        return {
            "final_decision": "profile_gap",
            "confidence": "high",
            "decision_basis": (
                "Ground Stop advisories carry explicit impacting-condition message text, "
                "but the runtime profile only permits impactingConditionMessage on "
                "GroundDelayProgramTMI. The extracted text is source-supported; the domain "
                "constraint is too narrow for this ATCSCC subset."
            ),
            "required_follow_up": (
                "Review a GroundStopTMI domain extension for impactingConditionMessage, or "
                "store the message as provenance-only evidence until the profile is extended."
            ),
        }
    if (
        predicate == "extensionProbability"
        and "allowed_value_violation" in errors
        and set(value_counts) == {"MODERATE"}
    ):
        return {
            "final_decision": "extractor_bug",
            "confidence": "medium",
            "decision_basis": (
                "The source surface value is MODERATE, while the runtime profile accepts "
                "LOW, MEDIUM, HIGH, or NONE. This is a normalization gap in the extractor "
                "or mapping layer, not a need to broaden the ontology before scoring."
            ),
            "required_follow_up": (
                "Add a regression-tested normalization rule MODERATE -> MEDIUM and retain "
                "the raw surface value in provenance."
            ),
        }
    if (
        predicate == "impactingCondition"
        and "allowed_value_violation" in errors
        and set(value_counts) == {"staffing"}
    ):
        return {
            "final_decision": "profile_gap",
            "confidence": "medium",
            "decision_basis": (
                "The ATCSCC source explicitly uses STAFFING as an impacting condition, but "
                "the runtime NASA ATMONTO enum does not include a staffing category. Mapping "
                "it to other would lose a recurring operational distinction."
            ),
            "required_follow_up": (
                "Review STAFFING as a profile extension value, or map to other only with "
                "the raw staffing value preserved in impactingConditionMessage."
            ),
        }
    return {
        "final_decision": "manual_review_only",
        "confidence": "low",
        "decision_basis": (
            "This property/error pattern is not covered by deterministic adjudication rules."
        ),
        "required_follow_up": "Inspect source evidence and NASA ATMONTO terms manually.",
    }
