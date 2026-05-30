from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any

from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.evaluation.gold import load_gold_labels
from aviation_agentic_ai.evaluation.protocol import build_run_manifest
from aviation_agentic_ai.kg.extraction import KGReadError
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.io import (
    normalize_report_text as _normalize,
    write_json_report,
)


PROVENANCE_FIELDS = ("triple_id", "chunk_id", "page", "evidence_text")


def _triple_dicts(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    triples: list[dict[str, Any]] = []
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise KGReadError(
                    f"Invalid KG comparison JSONL record in {project_relative_path(source)} "
                    f"at line {line_number}: {exc}"
                ) from exc
            if isinstance(item, dict):
                triples.append(item)
    return triples


def _signature(triple: dict[str, Any]) -> tuple[str, ...]:
    return (
        _normalize(triple.get("subject", "")),
        _normalize(triple.get("predicate", "")),
        _normalize(triple.get("object", "")),
        _normalize(triple.get("subject_class", "")),
        _normalize(triple.get("object_class", "")),
    )


def _key_entity_coverage(triples: list[dict[str, Any]], gold_labels_path: str | Path | None) -> float:
    if gold_labels_path is None:
        return 0.0
    labels = load_gold_labels(gold_labels_path)
    if not labels:
        return 0.0
    covered = 0
    for label in labels.values():
        haystacks = [
            _normalize(" ".join(str(value) for value in triple.values()))
            for triple in triples
        ]
        entities = [_normalize(entity) for entity in label.key_entities if str(entity).strip()]
        if entities and any(
            entity in haystack for entity in entities for haystack in haystacks
        ):
            covered += 1
    return round(covered / len(labels), 4)


def _summarize_kg(path: str | Path, gold_labels_path: str | Path | None) -> dict[str, Any]:
    triples = _triple_dicts(path)
    seen: set[tuple[str, ...]] = set()
    duplicate_count = 0
    provenance_complete = 0
    unsupported_count = 0
    model_counts: dict[str, int] = {}
    for triple in triples:
        sig = _signature(triple)
        duplicate_count += int(sig in seen)
        seen.add(sig)
        provenance_complete += int(
            all(triple.get(field) not in (None, "") for field in PROVENANCE_FIELDS)
        )
        unsupported_count += int(bool(triple.get("unsupported") or triple.get("validation_error")))
        model = str(triple.get("model", "unknown"))
        model_counts[model] = model_counts.get(model, 0) + 1
    denominator = len(triples) or 1
    valid_triples = len(triples) - unsupported_count
    return {
        "kg_path": project_relative_path(path),
        "triples_total": len(triples),
        "valid_triples": valid_triples,
        "unsupported_triple_count": unsupported_count,
        "provenance_complete_rate": round(provenance_complete / denominator, 4),
        "evidence_in_chunk_rate": round(provenance_complete / denominator, 4),
        "duplicate_triple_count": duplicate_count,
        "unique_triple_count": len(seen),
        "key_entity_coverage": _key_entity_coverage(triples, gold_labels_path),
        "model_counts": model_counts,
    }


def _interpret(result: dict[str, Any]) -> str:
    fixed = result["experiments"].get("fixed_window", {})
    structure = result["experiments"].get("structure_aware", {})
    if not fixed or not structure:
        return "Only one KG artifact is available, so comparison is limited."
    delta = int(structure.get("valid_triples", 0)) - int(fixed.get("valid_triples", 0))
    if delta > 0:
        return (
            "Structure-aware extraction produced more validated triples; judge this gain "
            "against duplicate count, key-entity coverage, and cost before treating it "
            "as higher-quality evidence."
        )
    if delta == 0:
        return "Both strategies produced the same number of validated triples."
    return "Fixed-window produced more validated triples; inspect whether structure boundaries missed evidence."


def build_kg_extraction_comparison(
    *,
    fixed_kg_path: str | Path,
    structure_aware_kg_path: str | Path,
    gold_labels_path: str | Path | None = None,
    command: str = "aviation-ai report kg-extraction-comparison",
) -> dict[str, Any]:
    started = perf_counter()
    experiments = {
        "fixed_window": _summarize_kg(fixed_kg_path, gold_labels_path),
        "structure_aware": _summarize_kg(structure_aware_kg_path, gold_labels_path),
    }
    run_manifest = build_run_manifest(
        "kg_extraction_comparison",
        parameters={
            "gold_labels_path": project_relative_path(gold_labels_path)
            if gold_labels_path is not None
            else None,
            "default_rebuild_kg": False,
        },
        artifacts={
            "fixed_kg_path": fixed_kg_path,
            "structure_aware_kg_path": structure_aware_kg_path,
        },
        rebuild_policy={"chunks": False, "indexes": False, "kg": False},
        collection_name="not_used",
        chunking_strategy="fixed_window_vs_structure_aware",
        command=command,
        llm={"provider": "none", "model": "not_used"},
        embedding={"backend": "not_used", "collection_name": "not_used"},
    )
    result = {
        "metadata": {
            "run_manifest": run_manifest,
            "gold_labels_path": project_relative_path(gold_labels_path)
            if gold_labels_path is not None
            else None,
            "scoring_policy": "kg_quality_metrics_no_mixed_overall_score",
            "cost_latency": cost_latency_block(
                elapsed_seconds=perf_counter() - started,
                kg_path=structure_aware_kg_path,
            ),
        },
        "experiments": experiments,
    }
    result["interpretation"] = _interpret(result)
    return result


def write_kg_extraction_comparison_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path)


def write_kg_extraction_comparison_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# KG Extraction Comparison",
        "",
        f"- Run ID: `{result['metadata']['run_manifest']['run_id']}`",
        "- Scope: artifact-level comparison; no default live KG rebuild.",
        "",
        "| Strategy | Triples | Valid triples | Unsupported | Provenance complete | Duplicates | Key entity coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for strategy, item in result["experiments"].items():
        lines.append(
            f"| {strategy} | {item['triples_total']} | {item['valid_triples']} | "
            f"{item['unsupported_triple_count']} | {item['provenance_complete_rate']} | "
            f"{item['duplicate_triple_count']} | {item['key_entity_coverage']} |"
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_kg_extraction_comparison(
    output_dir: str | Path,
    *,
    fixed_kg_path: str | Path,
    structure_aware_kg_path: str | Path,
    gold_labels_path: str | Path | None = None,
    report_name: str = "kg_extraction_comparison",
    command: str = "aviation-ai report kg-extraction-comparison",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_kg_extraction_comparison(
        fixed_kg_path=fixed_kg_path,
        structure_aware_kg_path=structure_aware_kg_path,
        gold_labels_path=gold_labels_path,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "kg_extraction_comparison"
    json_path = write_kg_extraction_comparison_json(result, output / f"{stem}.json")
    md_path = write_kg_extraction_comparison_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
