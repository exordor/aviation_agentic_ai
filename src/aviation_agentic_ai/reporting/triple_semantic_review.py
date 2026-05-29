from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aviation_agentic_ai.kg.extraction import read_kg_jsonl
from aviation_agentic_ai.paths import project_relative_path


REVIEW_FIELDS = (
    "subject_correct",
    "object_correct",
    "predicate_correct",
    "direction_correct",
    "evidence_supports_triple",
    "too_generic",
    "duplicate_or_near_duplicate",
)


def build_triple_semantic_review_sample(
    kg_path: str | Path,
    *,
    sample_size: int = 100,
) -> dict[str, Any]:
    triples = sorted(read_kg_jsonl(kg_path), key=lambda item: item.triple_id)
    sample = triples[:sample_size]
    records: list[dict[str, Any]] = []
    for triple in sample:
        annotation = {field: "needs_review" for field in REVIEW_FIELDS}
        annotation["status"] = "needs_manual_review"
        annotation["reviewer_notes"] = ""
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
        },
        "summary": {
            "needs_review": len(records),
            "reviewed": 0,
            "fields": list(REVIEW_FIELDS) + ["status", "reviewer_notes"],
        },
        "records": records,
    }


def write_triple_semantic_review_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


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
        "- Default review status: `needs_manual_review`",
        "- All annotation fields are initialized as `needs_review` for manual review.",
        "",
        "## Annotation Fields",
        "",
        *[f"- `{field}`" for field in result["summary"]["fields"]],
        "",
        "## Sample Preview",
        "",
    ]
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
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_triple_semantic_review_sample(kg_path, sample_size=sample_size)
    output = Path(output_dir)
    json_stem = Path(json_name).stem or "triple_semantic_review_sample"
    md_stem = Path(report_name).stem or "triple_semantic_review"
    json_path = write_triple_semantic_review_json(result, output / f"{json_stem}.json")
    md_path = write_triple_semantic_review_markdown(result, output / f"{md_stem}.md")
    return json_path, md_path, result
