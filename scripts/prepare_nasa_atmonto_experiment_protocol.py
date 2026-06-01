from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path


ATCSCC_ALIGNED_JSONL = Path(
    "data/processed/nasa_atmonto/aligned/2026-05-14/atcscc_advisories.jsonl"
)
ATCSCC_CANDIDATES_JSONL = Path(
    "data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_candidates.jsonl"
)
ATCSCC_VALIDATED_JSONL = Path(
    "data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl"
)
GOLD_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json")
GOLD_TEMPLATE_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl")
REJECTION_ANALYSIS_JSON = Path("reports/stages/nasa_atmonto_rejection_error_analysis.json")
REJECTION_ANALYSIS_MD = Path("reports/stages/nasa_atmonto_rejection_error_analysis.md")

SAMPLE_SIZE = 100
SAMPLE_SEED = "nasa-atmonto-atcscc-gold-v1"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records)
        + ("\n" if records else ""),
        encoding="utf-8",
    )


def stable_rank(value: str) -> str:
    return sha256(f"{SAMPLE_SEED}|{value}".encode("utf-8")).hexdigest()


def compact_text(value: str, limit: int = 900) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def source_date(source_id: str) -> str:
    match = re.match(r"(\d{4}-\d{2}-\d{2}):", source_id)
    return match.group(1) if match else ""


def candidate_subject_class(payload: dict[str, Any]) -> str:
    if payload.get("subject_class"):
        return str(payload["subject_class"])
    facts = payload.get("facts", [])
    if facts and isinstance(facts[0], dict):
        return str(facts[0].get("subject_class", ""))
    return ""


def build_source_stats(
    rows: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    validations: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    candidate_by_id = {str(payload["source_id"]): payload for payload in candidates}
    validations_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for validation in validations:
        validations_by_id[str(validation["source_id"])].append(validation)

    for row in rows:
        sid = str(row["source_id"])
        payload = candidate_by_id.get(sid, {"facts": []})
        row_validations = validations_by_id.get(sid, [])
        rejected = [item for item in row_validations if not item.get("accepted")]
        accepted = [item for item in row_validations if item.get("accepted")]
        predicate_counts = Counter(
            str(item.get("candidate", {}).get("predicate")) for item in row_validations
        )
        stats[sid] = {
            "source_id": sid,
            "source_date": source_date(sid),
            "candidate_subject_class": candidate_subject_class(payload),
            "candidate_fact_count": len(payload.get("facts", [])),
            "accepted_fact_count": len(accepted),
            "rejected_fact_count": len(rejected),
            "candidate_predicate_counts": dict(sorted(predicate_counts.items())),
            "has_rejection": bool(rejected),
            "rejection_predicates": sorted(
                {
                    str(item.get("candidate", {}).get("predicate"))
                    for item in rejected
                    if item.get("candidate")
                }
            ),
        }
    return stats


def stratified_gold_sample(stats: dict[str, dict[str, Any]], sample_size: int) -> list[str]:
    rejected_ids = [sid for sid, item in stats.items() if item["has_rejection"]]
    accepted_only_ids = [sid for sid, item in stats.items() if not item["has_rejection"]]

    selected: list[str] = []

    by_rejection_predicate: dict[str, list[str]] = defaultdict(list)
    for sid in rejected_ids:
        for predicate in stats[sid]["rejection_predicates"]:
            by_rejection_predicate[predicate].append(sid)
    for predicate in sorted(by_rejection_predicate):
        for sid in sorted(set(by_rejection_predicate[predicate]), key=stable_rank)[:8]:
            if sid not in selected:
                selected.append(sid)

    by_class: dict[str, list[str]] = defaultdict(list)
    for sid, item in stats.items():
        by_class[str(item["candidate_subject_class"])].append(sid)
    for class_name in sorted(by_class):
        for sid in sorted(by_class[class_name], key=stable_rank)[:8]:
            if sid not in selected:
                selected.append(sid)

    target_rejected = min(40, len(rejected_ids))
    for sid in sorted(rejected_ids, key=stable_rank):
        if sum(1 for item in selected if stats[item]["has_rejection"]) >= target_rejected:
            break
        if sid not in selected:
            selected.append(sid)

    for sid in sorted(accepted_only_ids, key=stable_rank):
        if len(selected) >= sample_size:
            break
        if sid not in selected:
            selected.append(sid)

    return selected[:sample_size]


def classify_rejection(predicate: str, errors: tuple[str, ...], sample: dict[str, Any]) -> dict[str, str]:
    value = str(sample.get("value") or "")
    object_class = str(sample.get("object_class") or "")
    subject_class = str(sample.get("subject_class") or "")
    if predicate == "controlledNASelement" and "range_violation" in errors:
        return {
            "decision": "nasa_atmonto_profile_gap_candidate",
            "rationale": (
                "ATCSCC constrained facilities include ARTCC center identifiers, but the current "
                "runtime slice validates controlledNASelement against TFMcontrolElement. The NASA "
                "TBox path does not make nas:ARTCC a TFMcontrolElement in this profile."
            ),
            "recommended_action": (
                "Review whether ATCSCC center facilities should be bridged into the runtime "
                "profile as controlled NAS elements, or whether they require a separate property."
            ),
        }
    if predicate == "impactingConditionMessage" and "domain_violation" in errors:
        return {
            "decision": "nasa_atmonto_profile_gap_candidate",
            "rationale": (
                "Ground stop advisories contain explicit impacting-condition details, but "
                "impactingConditionMessage is currently constrained to GroundDelayProgramTMI."
            ),
            "recommended_action": (
                "Review a profile extension for GroundStopTMI, or keep only impactingCondition "
                "and preserve the full source phrase as evidence until reviewed."
            ),
        }
    if predicate == "extensionProbability" and value.upper() == "MODERATE":
        return {
            "decision": "extractor_normalization_bug_candidate",
            "rationale": (
                "The source uses MODERATE while ATMONTO enumerates LOW, MEDIUM, HIGH, and NONE. "
                "This should be normalized to MEDIUM only if the mapping is approved."
            ),
            "recommended_action": (
                "Add a reviewed enum-normalization rule MODERATE -> MEDIUM and keep the raw "
                "surface value in provenance."
            ),
        }
    if predicate == "impactingCondition" and value.lower() == "staffing":
        return {
            "decision": "nasa_atmonto_profile_gap_candidate",
            "rationale": (
                "ATCSCC uses STAFFING as an impacting condition, but the ATMONTO enum contains "
                "equipment, other, runway, volume, and weather."
            ),
            "recommended_action": (
                "Decide whether STAFFING should become a profile extension value or map to "
                "other with the raw value retained in impactingConditionMessage."
            ),
        }
    return {
        "decision": "manual_review_required",
        "rationale": (
            f"No deterministic classification rule for predicate={predicate}, "
            f"errors={','.join(errors)}, subject_class={subject_class}, object_class={object_class}."
        ),
        "recommended_action": "Inspect source evidence and NASA ATMONTO profile before changing extraction.",
    }


def rejection_error_analysis(validations: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for item in validations:
        if item.get("accepted"):
            continue
        candidate = item.get("candidate", {})
        key = (
            str(candidate.get("predicate")),
            tuple(str(error) for error in item.get("errors", [])),
        )
        groups[key].append(item)

    group_rows: list[dict[str, Any]] = []
    for (predicate, errors), items in sorted(
        groups.items(),
        key=lambda pair: (-len(pair[1]), pair[0][0], pair[0][1]),
    ):
        subject_class_counts = Counter(
            str(item.get("candidate", {}).get("subject_class")) for item in items
        )
        object_class_counts = Counter(
            str(item.get("candidate", {}).get("object_class"))
            for item in items
            if item.get("candidate", {}).get("object_class")
        )
        value_counts = Counter(
            str(item.get("candidate", {}).get("value"))
            for item in items
            if item.get("candidate", {}).get("value") is not None
        )
        sample_candidate = items[0]["candidate"]
        classification = classify_rejection(predicate, errors, sample_candidate)
        group_rows.append(
            {
                "predicate": predicate,
                "errors": list(errors),
                "count": len(items),
                "decision": classification["decision"],
                "rationale": classification["rationale"],
                "recommended_action": classification["recommended_action"],
                "subject_class_counts": dict(sorted(subject_class_counts.items())),
                "object_class_counts": dict(sorted(object_class_counts.items())),
                "value_counts": dict(value_counts.most_common(10)),
                "sample_rejections": [
                    {
                        "source_id": str(item["source_id"]),
                        "subject_class": item["candidate"].get("subject_class"),
                        "predicate": item["candidate"].get("predicate"),
                        "object_class": item["candidate"].get("object_class"),
                        "value": item["candidate"].get("value"),
                        "evidence_text": item["candidate"].get("evidence_text"),
                    }
                    for item in items[:5]
                ],
            }
        )

    decision_counts = Counter(row["decision"] for row in group_rows for _ in range(row["count"]))
    return {
        "source_family": "nasa_atmonto_rejection_error_analysis",
        "input_validated_facts": ATCSCC_VALIDATED_JSONL.as_posix(),
        "rejected_fact_count": sum(row["count"] for row in group_rows),
        "group_count": len(group_rows),
        "decision_counts_by_fact": dict(sorted(decision_counts.items())),
        "groups": group_rows,
        "boundary": (
            "Decisions classify likely next action for research triage; they are not final "
            "ontology extension approvals without manual review."
        ),
    }


def markdown_rejection_report(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Rejection Error Analysis",
        "",
        f"- Input: `{report['input_validated_facts']}`",
        f"- Rejected facts: {report['rejected_fact_count']}",
        f"- Property/error groups: {report['group_count']}",
        "",
        "## Decision Counts By Fact",
        "",
    ]
    for decision, count in report["decision_counts_by_fact"].items():
        lines.append(f"- `{decision}`: {count}")
    lines.extend(["", "## Property-Level Groups", ""])
    for group in report["groups"]:
        lines.extend(
            [
                f"### {group['predicate']} / {', '.join(group['errors'])}",
                "",
                f"- Count: {group['count']}",
                f"- Decision: `{group['decision']}`",
                f"- Rationale: {group['rationale']}",
                f"- Recommended action: {group['recommended_action']}",
                f"- Subject classes: `{json.dumps(group['subject_class_counts'], sort_keys=True)}`",
                f"- Object classes: `{json.dumps(group['object_class_counts'], sort_keys=True)}`",
                f"- Values: `{json.dumps(group['value_counts'], sort_keys=True)}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            "- These decisions are research triage labels.",
            "- Profile-gap candidates require ontology/profile review before becoming accepted extensions.",
            "- Extractor-bug candidates require a regression test before changing extraction behavior.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_gold_template_records(
    selected_ids: list[str],
    rows: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    validations: list[dict[str, Any]],
    stats: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows_by_id = {str(row["source_id"]): row for row in rows}
    candidates_by_id = {str(payload["source_id"]): payload for payload in candidates}
    validations_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for validation in validations:
        validations_by_id[str(validation["source_id"])].append(validation)

    records: list[dict[str, Any]] = []
    for index, sid in enumerate(selected_ids, start=1):
        row = rows_by_id[sid]
        payload = candidates_by_id.get(sid, {"facts": []})
        row_validations = validations_by_id.get(sid, [])
        records.append(
            {
                "sample_id": f"ATCSCC-GOLD-{index:03d}",
                "source_id": sid,
                "source_family": "atcscc_advisories",
                "source_url": row.get("source_url"),
                "advisory_date": row.get("advisory_date"),
                "advisory_number": row.get("advisory_number"),
                "candidate_subject_class": stats[sid]["candidate_subject_class"],
                "sampling_tags": [
                    "has_rejection" if stats[sid]["has_rejection"] else "accepted_only",
                    f"class:{stats[sid]['candidate_subject_class']}",
                    f"source_date:{stats[sid]['source_date']}",
                ],
                "candidate_fact_count": stats[sid]["candidate_fact_count"],
                "accepted_fact_count": stats[sid]["accepted_fact_count"],
                "rejected_fact_count": stats[sid]["rejected_fact_count"],
                "source_text": row.get("text", ""),
                "source_text_excerpt": compact_text(str(row.get("text", ""))),
                "candidate_facts": payload.get("facts", []),
                "validator_results": [
                    {
                        "fact_id": item.get("fact_id"),
                        "status": item.get("status"),
                        "accepted": item.get("accepted"),
                        "errors": item.get("errors", []),
                        "repairs": item.get("repairs", []),
                    }
                    for item in row_validations
                ],
                "gold_annotation": {
                    "annotation_status": "pending_manual_gold_annotation",
                    "annotator_id": "",
                    "review_checklist": {
                        "source_text_checked": False,
                        "semantic_rubric_checked": False,
                        "profile_gap_boundary_checked": False,
                        "missing_facts_checked": False,
                    },
                    "valid_facts": [],
                    "invalid_candidate_fact_ids": [],
                    "rejected_fact_adjudications": [],
                    "missing_facts": [],
                    "notes": "",
                },
            }
        )
    return records


def build_gold_manifest(
    selected_ids: list[str],
    stats: dict[str, dict[str, Any]],
    *,
    repo_root: Path,
) -> dict[str, Any]:
    class_counts = Counter(str(stats[sid]["candidate_subject_class"]) for sid in selected_ids)
    source_date_counts = Counter(str(stats[sid]["source_date"]) for sid in selected_ids)
    rejected_count = sum(1 for sid in selected_ids if stats[sid]["has_rejection"])
    predicate_exposure = Counter(
        predicate
        for sid in selected_ids
        for predicate in stats[sid].get("rejection_predicates", [])
    )
    return {
        "source_family": "atcscc_advisory_gold_sample",
        "sample_status": "sample_template_created_gold_labels_pending",
        "sampling_seed": SAMPLE_SEED,
        "sample_size": len(selected_ids),
        "sample_size_target": SAMPLE_SIZE,
        "input_atcscc_aligned": project_relative_path(repo_root / ATCSCC_ALIGNED_JSONL, repo_root),
        "input_candidates": project_relative_path(repo_root / ATCSCC_CANDIDATES_JSONL, repo_root),
        "input_validated_facts": project_relative_path(repo_root / ATCSCC_VALIDATED_JSONL, repo_root),
        "annotation_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "selection_policy": {
            "target_n": "100 advisories, within the requested 80-120 range",
            "strata": [
                "records with rejected candidate facts",
                "candidate TMI class",
                "source advisory date within the aligned ATCSCC window",
            ],
            "purpose": (
                "Create an annotation-ready gold sample for triple precision, recall, "
                "manual semantic correctness, and rejection adjudication."
            ),
        },
        "sample_counts": {
            "has_rejection": rejected_count,
            "accepted_only": len(selected_ids) - rejected_count,
            "candidate_subject_class": dict(sorted(class_counts.items())),
            "source_date": dict(sorted(source_date_counts.items())),
            "rejection_predicate_exposure": dict(sorted(predicate_exposure.items())),
        },
        "selected_source_ids": selected_ids,
        "manual_annotation_required": [
            "mark each candidate fact valid or invalid",
            "add missing gold facts not produced by any system",
            "record invalid reason and evidence span",
            "adjudicate profile-gap candidates before using them as accepted schema extensions",
        ],
    }


def prepare_protocol_artifacts(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    rows = read_jsonl(repo_root / ATCSCC_ALIGNED_JSONL)
    candidates = read_jsonl(repo_root / ATCSCC_CANDIDATES_JSONL)
    validations = read_jsonl(repo_root / ATCSCC_VALIDATED_JSONL)
    stats = build_source_stats(rows, candidates, validations)
    selected_ids = stratified_gold_sample(stats, SAMPLE_SIZE)

    if len(selected_ids) != SAMPLE_SIZE:
        raise ValueError(f"Expected {SAMPLE_SIZE} sample records, got {len(selected_ids)}")

    gold_records = build_gold_template_records(selected_ids, rows, candidates, validations, stats)
    gold_manifest = build_gold_manifest(selected_ids, stats, repo_root=repo_root)
    rejection_report = rejection_error_analysis(validations)

    write_json(repo_root / GOLD_MANIFEST_PATH, gold_manifest)
    write_jsonl(repo_root / GOLD_TEMPLATE_PATH, gold_records)
    write_json(repo_root / REJECTION_ANALYSIS_JSON, rejection_report)
    (repo_root / REJECTION_ANALYSIS_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / REJECTION_ANALYSIS_MD).write_text(
        markdown_rejection_report(rejection_report),
        encoding="utf-8",
    )

    return {
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "rejection_analysis_json": project_relative_path(repo_root / REJECTION_ANALYSIS_JSON, repo_root),
        "rejection_analysis_md": project_relative_path(repo_root / REJECTION_ANALYSIS_MD, repo_root),
        "sample_size": len(selected_ids),
        "rejected_fact_count": rejection_report["rejected_fact_count"],
        "rejection_group_count": rejection_report["group_count"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare NASA ATMONTO formal experiment protocol artifacts."
    )
    parser.add_argument("--repo-root", default=PROJECT_ROOT, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = prepare_protocol_artifacts(args.repo_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"NASA ATMONTO experiment protocol preparation failed: {exc}", file=sys.stderr)
        raise
