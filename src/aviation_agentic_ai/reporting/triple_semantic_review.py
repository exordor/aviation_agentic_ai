from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.kg.extraction import read_kg_jsonl
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report


REVIEW_FIELDS = (
    "subject_correct",
    "object_correct",
    "predicate_correct",
    "direction_correct",
    "evidence_supports_triple",
    "too_generic",
    "duplicate_or_near_duplicate",
)
CORRECTNESS_FIELDS = (
    "subject_correct",
    "object_correct",
    "predicate_correct",
    "direction_correct",
)


def _load_existing_annotations(path: str | Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    payload = read_json_object_or_empty(path, wrap_non_object=False)
    annotations: dict[str, dict[str, Any]] = {}
    for record in payload.get("records", []):
        if not isinstance(record, dict):
            continue
        triple = record.get("triple", {})
        annotation = record.get("annotation", {})
        if not isinstance(triple, dict) or not isinstance(annotation, dict):
            continue
        triple_id = str(triple.get("triple_id", ""))
        if triple_id:
            annotations[triple_id] = dict(annotation)
    return annotations


def _merge_annotation(default: dict[str, Any], existing: dict[str, Any] | None) -> dict[str, Any]:
    if not existing:
        return default
    merged = dict(default)
    for key in list(REVIEW_FIELDS) + ["status", "reviewer_notes"]:
        if key in existing:
            merged[key] = existing[key]
    return merged


def _truthy(value: Any) -> bool:
    return value is True or str(value).strip().lower() == "true"


def _is_reviewed(annotation: dict[str, Any]) -> bool:
    if annotation.get("status") in {"reviewed", "accepted", "rejected", "llm_reviewed"}:
        return True
    return all(annotation.get(field) in {True, False} for field in REVIEW_FIELDS)


def _summarize_annotations(records: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed = [record for record in records if _is_reviewed(record["annotation"])]
    reviewed_total = len(reviewed)
    needs_review_total = len(records) - reviewed_total
    summary: dict[str, Any] = {
        "reviewed_total": reviewed_total,
        "needs_review_total": needs_review_total,
        "reviewed": reviewed_total,
        "needs_review": needs_review_total,
        "fields": list(REVIEW_FIELDS) + ["status", "reviewer_notes"],
    }
    if reviewed_total:
        summary["semantic_correctness_rate"] = round(
            sum(
                int(all(_truthy(record["annotation"].get(field)) for field in CORRECTNESS_FIELDS))
                for record in reviewed
            )
            / reviewed_total,
            4,
        )
        summary["evidence_support_rate"] = round(
            sum(
                int(_truthy(record["annotation"].get("evidence_supports_triple")))
                for record in reviewed
            )
            / reviewed_total,
            4,
        )
    return summary


def build_triple_semantic_review_sample(
    kg_path: str | Path,
    *,
    sample_size: int = 100,
    annotations_path: str | Path | None = None,
) -> dict[str, Any]:
    triples = sorted(read_kg_jsonl(kg_path), key=lambda item: item.triple_id)
    sample = triples[:sample_size]
    existing_annotations = _load_existing_annotations(annotations_path)
    records: list[dict[str, Any]] = []
    for triple in sample:
        annotation = {field: "needs_review" for field in REVIEW_FIELDS}
        annotation["status"] = "needs_llm_review"
        annotation["reviewer_notes"] = ""
        annotation["human_review"] = False
        annotation["external_expert_certified"] = False
        annotation["aviation_expert_certified"] = False
        annotation = _merge_annotation(annotation, existing_annotations.get(triple.triple_id))
        records.append(
            {
                "triple": triple.to_dict(),
                "annotation": annotation,
            }
        )
    return {
        "metadata": {
            "kg_path": project_relative_path(kg_path),
            "triples_total": len(triples),
            "sample_size_requested": sample_size,
            "sample_size": len(records),
            "semantic_correctness_claimed": False,
            "semantic_correctness_status": "llm_review_pending_not_human_certified",
            "human_review": False,
            "external_expert_certified": False,
            "aviation_expert_certified": False,
            "annotations_path": project_relative_path(annotations_path)
            if annotations_path is not None
            else None,
        },
        "summary": _summarize_annotations(records),
        "records": records,
    }


def write_triple_semantic_review_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path)


def write_triple_semantic_review_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Triple Semantic Review Sample",
        "",
        f"- KG: `{result['metadata']['kg_path']}`",
        f"- Triples total: {result['metadata']['triples_total']}",
        f"- Sample size: {result['metadata']['sample_size']}",
        "- Semantic correctness claimed: no",
        "- Default review status: `needs_llm_review`",
        "- Human review: false",
        "- External aviation expert certified: false",
        f"- Reviewed triples: {result['summary']['reviewed_total']}",
        f"- Needs review: {result['summary']['needs_review_total']}",
        "- Unreviewed annotation fields stay `needs_review`; rates are shown only after review.",
        "",
        "## Annotation Fields",
        "",
        *[f"- `{field}`" for field in result["summary"]["fields"]],
        "",
        "## Model-Based Review Instructions",
        "",
        "- Use `triple-semantic-llm-review` for model-based judging.",
        "- Leave uncertain fields as `needs_review` unless a schema-valid LLM review is supplied.",
        "- Do not treat this report as manual or expert semantic correctness evidence.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Reviewed total | {result['summary']['reviewed_total']} |",
        f"| Needs review total | {result['summary']['needs_review_total']} |",
    ]
    if "semantic_correctness_rate" in result["summary"]:
        lines.append(
            f"| Semantic correctness rate | {result['summary']['semantic_correctness_rate']} |"
        )
        lines.append(f"| Evidence support rate | {result['summary']['evidence_support_rate']} |")
    lines.extend(
        [
            "",
        "## Sample Preview",
        "",
        ]
    )
    for record in result["records"][:20]:
        triple = record["triple"]
        lines.append(
            f"- `{triple['triple_id']}`: {triple['subject']} -{triple['predicate']}-> "
            f"{triple['object']} (chunk `{triple['chunk_id']}`)"
        )
    if len(result["records"]) > 20:
        lines.append(f"- ... {len(result['records']) - 20} additional triples in JSON sample")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_triple_semantic_review(
    kg_path: str | Path,
    output_dir: str | Path,
    *,
    sample_size: int = 100,
    report_name: str = "triple_semantic_review",
    json_name: str = "triple_semantic_review_sample",
    annotations_path: str | Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_triple_semantic_review_sample(
        kg_path,
        sample_size=sample_size,
        annotations_path=annotations_path,
    )
    output = Path(output_dir)
    json_stem = Path(json_name).stem or "triple_semantic_review_sample"
    md_stem = Path(report_name).stem or "triple_semantic_review"
    json_path = write_triple_semantic_review_json(result, output / f"{json_stem}.json")
    md_path = write_triple_semantic_review_markdown(result, output / f"{md_stem}.md")
    return json_path, md_path, result
