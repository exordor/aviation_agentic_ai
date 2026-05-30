from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.evaluation.gold import EvidenceSpan, GoldLabel, load_gold_labels
from aviation_agentic_ai.evaluation.metrics import answer_metrics, kg_evidence_metrics
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.io import (
    normalize_report_text,
    read_json_object_or_none,
    write_json_report,
)


def _load_json(path: str | Path) -> dict[str, Any] | None:
    return read_json_object_or_none(path, wrap_non_object=True)


def _normalize(text: str) -> str:
    return normalize_report_text(text)


def _span_hit(span: EvidenceSpan, chunks: list[dict[str, Any]]) -> bool:
    for chunk in chunks:
        if int(chunk.get("page", -1)) != span.page:
            continue
        if not span.text or _normalize(span.text) in _normalize(chunk.get("text", "")):
            return True
    return False


def _chunk_recall(chunks: list[dict[str, Any]], gold: GoldLabel) -> dict[str, Any]:
    top_chunks = chunks[:5]
    expected = set(gold.expected_chunk_ids)
    retrieved = [str(chunk.get("chunk_id", "")) for chunk in top_chunks]
    matched = [chunk_id for chunk_id in retrieved if chunk_id in expected]
    return {
        "chunk_recall_at_5": bool(matched) if expected else None,
        "expected_chunk_ids": sorted(expected),
        "retrieved_chunk_ids": retrieved,
        "matched_chunk_ids": matched,
    }


def _span_metrics(chunks: list[dict[str, Any]], gold: GoldLabel) -> dict[str, Any]:
    spans = list(gold.evidence_spans)
    matched = [span for span in spans if _span_hit(span, chunks[:5])]
    return {
        "span_hit": bool(matched) if spans else None,
        "span_hit_count": len(matched),
        "span_total": len(spans),
        "matched_spans": [
            {
                "page": span.page,
                "text": span.text,
                "char_start": span.char_start,
                "char_end": span.char_end,
            }
            for span in matched
        ],
    }


def _answer_support_status(
    *,
    chunk_hit: bool | None,
    span_hit: bool | None,
    kg_covered: bool,
    citation_valid: bool,
    abstained: bool,
) -> str:
    if abstained:
        return "insufficient_evidence"
    evidence_hit = bool(span_hit) or bool(chunk_hit)
    if evidence_hit and citation_valid and kg_covered:
        return "supported"
    if citation_valid and (evidence_hit or kg_covered):
        return "partially_supported"
    return "unsupported"


def _evaluate_mode(
    record: dict[str, Any],
    mode: str,
    gold: GoldLabel,
) -> dict[str, Any]:
    result = record.get("results", {}).get(mode, {})
    chunks = result.get("fused_chunks", [])
    triples = result.get("graph_triples", [])
    chunk_metrics = _chunk_recall(chunks, gold)
    span_metrics = _span_metrics(chunks, gold)
    kg_metrics = kg_evidence_metrics(triples, gold.key_entities)
    citation_metrics = answer_metrics(result)
    status = _answer_support_status(
        chunk_hit=chunk_metrics["chunk_recall_at_5"],
        span_hit=span_metrics["span_hit"],
        kg_covered=bool(kg_metrics["evidence_coverage"]),
        citation_valid=bool(citation_metrics["citation_completeness"]),
        abstained=bool(citation_metrics["insufficient_evidence_abstention"]),
    )
    return {
        "mode": mode,
        "chunk": chunk_metrics,
        "span": span_metrics,
        "kg_evidence": kg_metrics,
        "citation": citation_metrics,
        "answer_support": status,
    }


def _aggregate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(records) or 1
    chunk_items = [item["chunk"]["chunk_recall_at_5"] for item in records]
    chunk_denominator = len([item for item in chunk_items if item is not None]) or 1
    span_items = [item["span"]["span_hit"] for item in records]
    span_denominator = len([item for item in span_items if item is not None]) or 1
    support_counts: dict[str, int] = {}
    for item in records:
        support_counts[item["answer_support"]] = support_counts.get(item["answer_support"], 0) + 1
    return {
        "questions_total": len(records),
        "chunk_recall_at_5": round(
            sum(int(item) for item in chunk_items if item is not None) / chunk_denominator,
            4,
        ),
        "span_hit_rate": round(
            sum(int(item) for item in span_items if item is not None) / span_denominator,
            4,
        ),
        "key_entity_coverage": round(
            sum(int(item["kg_evidence"]["key_entity_coverage"]) for item in records)
            / denominator,
            4,
        ),
        "kg_triple_relevance": round(
            sum(int(item["kg_evidence"]["evidence_coverage"]) for item in records)
            / denominator,
            4,
        ),
        "citation_validity": round(
            sum(int(item["citation"]["citation_completeness"]) for item in records)
            / denominator,
            4,
        ),
        "answer_support_distribution": support_counts,
    }


def _evaluate_experiment(
    label: str,
    experiment: dict[str, Any] | None,
    gold_labels: dict[str, GoldLabel],
) -> dict[str, Any]:
    if experiment is None:
        return {"present": False, "label": label}
    mode_records: dict[str, list[dict[str, Any]]] = {mode: [] for mode in ("vector", "graph", "hybrid")}
    question_records: list[dict[str, Any]] = []
    for record in experiment.get("records", []):
        cq_id = str(record.get("cq_id"))
        gold = gold_labels.get(cq_id)
        if gold is None:
            continue
        mode_results = {
            mode: _evaluate_mode(record, mode, gold)
            for mode in ("vector", "graph", "hybrid")
        }
        for mode, metrics in mode_results.items():
            mode_records[mode].append(metrics)
        question_records.append(
            {
                "cq_id": cq_id,
                "question": record.get("question", ""),
                "gold_level": gold.gold_level,
                "source_page": gold.source_page,
                "modes": mode_results,
            }
        )
    return {
        "present": True,
        "label": label,
        "metadata": experiment.get("metadata", {}),
        "aggregate": {
            mode: _aggregate_records(records)
            for mode, records in mode_records.items()
        },
        "records": question_records,
    }


def build_evidence_level_evaluation(
    gold_labels_path: str | Path,
    *,
    fixed_hybrid_path: str | Path,
    structure_aware_hybrid_path: str | Path,
) -> dict[str, Any]:
    gold_labels = load_gold_labels(gold_labels_path)
    fixed = _load_json(fixed_hybrid_path)
    structure = _load_json(structure_aware_hybrid_path)
    return {
        "metadata": {
            "gold_labels_path": project_relative_path(gold_labels_path),
            "fixed_hybrid_path": project_relative_path(fixed_hybrid_path),
            "structure_aware_hybrid_path": project_relative_path(structure_aware_hybrid_path),
            "labels_total": len(gold_labels),
            "scoring_policy": "layered_metrics_no_mixed_overall_score",
        },
        "experiments": {
            "fixed_window": _evaluate_experiment("fixed_window", fixed, gold_labels),
            "structure_aware": _evaluate_experiment("structure_aware", structure, gold_labels),
        },
    }


def write_evidence_level_evaluation_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path)


def write_evidence_level_evaluation_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Evidence-Level Evaluation",
        "",
        f"- Gold labels: `{result['metadata']['gold_labels_path']}`",
        f"- Labels: {result['metadata']['labels_total']}",
        "- Scoring: layered metrics only; no mixed overall score.",
        "",
    ]
    for experiment_name, experiment in result["experiments"].items():
        lines.extend([f"## {experiment_name}", ""])
        if not experiment.get("present"):
            lines.extend(["Not available.", ""])
            continue
        lines.extend(
            [
                "| Mode | Chunk Recall@5 | Span hit rate | Key entity coverage | "
                "KG triple relevance | Citation validity | Supported | Partial | "
                "Insufficient | Unsupported |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for mode in ("vector", "graph", "hybrid"):
            aggregate = experiment["aggregate"][mode]
            support = aggregate["answer_support_distribution"]
            lines.append(
                f"| {mode} | {aggregate['chunk_recall_at_5']} | "
                f"{aggregate['span_hit_rate']} | {aggregate['key_entity_coverage']} | "
                f"{aggregate['kg_triple_relevance']} | {aggregate['citation_validity']} | "
                f"{support.get('supported', 0)} | {support.get('partially_supported', 0)} | "
                f"{support.get('insufficient_evidence', 0)} | "
                f"{support.get('unsupported', 0)} |"
            )
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_evidence_level_evaluation(
    gold_labels_path: str | Path,
    output_dir: str | Path,
    *,
    fixed_hybrid_path: str | Path,
    structure_aware_hybrid_path: str | Path,
    report_name: str = "evidence_level_evaluation",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_evidence_level_evaluation(
        gold_labels_path,
        fixed_hybrid_path=fixed_hybrid_path,
        structure_aware_hybrid_path=structure_aware_hybrid_path,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "evidence_level_evaluation"
    json_path = write_evidence_level_evaluation_json(result, output / f"{stem}.json")
    md_path = write_evidence_level_evaluation_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
