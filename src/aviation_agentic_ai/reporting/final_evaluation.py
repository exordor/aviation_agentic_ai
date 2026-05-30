from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.paths import project_relative_path


def _read_json(path: str | Path) -> dict[str, Any] | None:
    source = Path(path)
    if not source.exists():
        return None
    data = json.loads(source.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"value": data}


def _get(data: dict[str, Any] | None, *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _gold_label_review(gold_labels: dict[str, Any] | None) -> dict[str, Any]:
    if not gold_labels:
        return {"present": False}
    labels = [
        label
        for label in gold_labels.get("labels", [])
        if isinstance(label, dict) and label.get("cq_id")
    ]
    levels = Counter(str(label.get("gold_level", "page")) for label in labels)
    pages = sorted(
        {
            int(label["source_page"])
            for label in labels
            if isinstance(label.get("source_page"), int)
        }
    )
    return {
        "present": True,
        "labels_total": len(labels),
        "gold_levels": dict(sorted(levels.items())),
        "source_pages": pages,
        "review_required": bool(_get(gold_labels, "metadata", "review_required")),
        "review_status": _get(
            gold_labels,
            "metadata",
            "review_status",
            default="not_marked_reviewed",
        ),
        "human_review": bool(_get(gold_labels, "metadata", "human_review", default=False)),
        "external_expert_certified": bool(
            _get(gold_labels, "metadata", "external_expert_certified", default=False)
        ),
        "aviation_expert_certified": bool(
            _get(gold_labels, "metadata", "aviation_expert_certified", default=False)
        ),
        "metadata_notes": _get(gold_labels, "metadata", "notes", default=""),
        "label_checks": [
            {
                "cq_id": label.get("cq_id"),
                "gold_level": label.get("gold_level", "page"),
                "source_page": label.get("source_page"),
                "expected_chunk_count": len(label.get("expected_chunk_ids", [])),
                "evidence_span_count": len(label.get("evidence_spans", [])),
                "key_entity_count": len(label.get("key_entities", [])),
            }
            for label in labels
        ],
    }


def _chunking_strategy_result(
    chunking: dict[str, Any] | None,
    strategy: str,
) -> dict[str, Any]:
    if not chunking:
        return {}
    strategy_data = _get(chunking, "strategies", strategy, default={})
    if not isinstance(strategy_data, dict):
        return {}
    return {
        "metrics": strategy_data.get("aggregate", {}),
        "chunk_stats": strategy_data.get("chunk_stats", {}),
        "explanation": strategy_data.get("explanation", ""),
        "collection_name": strategy_data.get("collection_name"),
        "chunks_path": strategy_data.get("chunks_path"),
    }


def _chunking_ranking(chunking: dict[str, Any] | None) -> list[dict[str, Any]]:
    ranking = _get(chunking, "ranking", default=[])
    return [item for item in ranking if isinstance(item, dict)]


def _experiment_aggregate(
    evidence_eval: dict[str, Any] | None,
    experiment: str,
    mode: str,
) -> dict[str, Any]:
    return _get(
        evidence_eval,
        "experiments",
        experiment,
        "aggregate",
        mode,
        default={},
    ) or {}


def _retrieval_failures(report: dict[str, Any] | None, mode: str = "hybrid") -> list[dict[str, Any]]:
    if not report:
        return []
    failures: list[dict[str, Any]] = []
    for record in report.get("records", []):
        if not isinstance(record, dict):
            continue
        result = _get(record, "results", mode, default={})
        retrieval = _get(result, "metrics", "retrieval", default={})
        if retrieval.get("recall_at_5") is True:
            continue
        failures.append(
            {
                "cq_id": record.get("cq_id"),
                "question": record.get("question"),
                "source_page": record.get("source_page"),
                "mode": mode,
                "first_relevant_rank": retrieval.get("first_relevant_rank"),
                "retrieved_source_pages": retrieval.get("retrieved_source_pages", []),
                "retrieved_chunk_ids": retrieval.get("retrieved_chunk_ids", []),
            }
        )
    return failures


def _evidence_failures(
    evidence_eval: dict[str, Any] | None,
    experiment: str,
    mode: str = "hybrid",
) -> list[dict[str, Any]]:
    if not evidence_eval:
        return []
    failures: list[dict[str, Any]] = []
    records = _get(evidence_eval, "experiments", experiment, "records", default=[])
    for record in records:
        if not isinstance(record, dict):
            continue
        mode_metrics = _get(record, "modes", mode, default={})
        answer_support = mode_metrics.get("answer_support")
        kg_metrics = mode_metrics.get("kg_evidence", {})
        span_metrics = mode_metrics.get("span", {})
        chunk_metrics = mode_metrics.get("chunk", {})
        citation_metrics = mode_metrics.get("citation", {})
        if answer_support == "supported":
            continue
        failures.append(
            {
                "cq_id": record.get("cq_id"),
                "question": record.get("question"),
                "gold_level": record.get("gold_level"),
                "source_page": record.get("source_page"),
                "mode": mode,
                "answer_support": answer_support,
                "chunk_recall_at_5": chunk_metrics.get("chunk_recall_at_5"),
                "span_hit": span_metrics.get("span_hit"),
                "key_entity_coverage": kg_metrics.get("key_entity_coverage"),
                "kg_evidence_coverage": kg_metrics.get("evidence_coverage"),
                "citation_completeness": citation_metrics.get("citation_completeness"),
            }
        )
    return failures


def _citation_summary(
    evidence_eval: dict[str, Any] | None,
    experiment: str,
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for mode in ("vector", "graph", "hybrid"):
        aggregate = _experiment_aggregate(evidence_eval, experiment, mode)
        summary[mode] = {
            "citation_validity": aggregate.get("citation_validity"),
            "answer_support_distribution": aggregate.get(
                "answer_support_distribution",
                {},
            ),
        }
    return summary


def _strategy_decision(
    chunking: dict[str, Any] | None,
    evidence_eval: dict[str, Any] | None,
) -> dict[str, Any]:
    ranking = _chunking_ranking(chunking)
    best = ranking[0].get("strategy") if ranking else "structure_aware"
    fixed_hybrid = _experiment_aggregate(evidence_eval, "fixed_window", "hybrid")
    structure_hybrid = _experiment_aggregate(evidence_eval, "structure_aware", "hybrid")
    return {
        "recommended_default": "structure_aware",
        "chunking_best_by_retrieval": best,
        "baseline": "fixed_window",
        "decision_status": "selected_for_demo_and_next_phase",
        "rationale": [
            "Structure-aware chunks ranked first in chunking comparison by Recall@5/MRR@5/Context Precision@5.",
            "Structure-aware Hybrid RAG keeps vector-level page recall while exposing KG evidence.",
            "Fixed-window remains the baseline because the first KG and reports are reproducible artifacts.",
            "GraphRAG should be presented as structured evidence support, not as a single blended score.",
        ],
        "evidence_level_delta": {
            "chunk_recall_at_5": round(
                _as_float(structure_hybrid.get("chunk_recall_at_5"))
                - _as_float(fixed_hybrid.get("chunk_recall_at_5")),
                4,
            ),
            "span_hit_rate": round(
                _as_float(structure_hybrid.get("span_hit_rate"))
                - _as_float(fixed_hybrid.get("span_hit_rate")),
                4,
            ),
            "supported_answer_count": (
                structure_hybrid.get("answer_support_distribution", {}).get("supported", 0)
                - fixed_hybrid.get("answer_support_distribution", {}).get("supported", 0)
            ),
        },
    }


def build_final_evaluation_review(
    *,
    gold_labels_path: str | Path,
    chunking_comparison_path: str | Path,
    fixed_hybrid_path: str | Path,
    structure_aware_hybrid_path: str | Path,
    evidence_eval_path: str | Path,
    graphrag_review_path: str | Path,
) -> dict[str, Any]:
    gold_labels = _read_json(gold_labels_path)
    chunking = _read_json(chunking_comparison_path)
    fixed_hybrid = _read_json(fixed_hybrid_path)
    structure_hybrid = _read_json(structure_aware_hybrid_path)
    evidence_eval = _read_json(evidence_eval_path)
    graphrag_review = _read_json(graphrag_review_path)
    return {
        "metadata": {
            "created_at": datetime.now(UTC).isoformat(),
            "scoring_policy": "layered_metrics_no_mixed_overall_score",
            "source_paths": {
                "gold_labels": project_relative_path(gold_labels_path),
                "chunking_comparison": project_relative_path(chunking_comparison_path),
                "fixed_hybrid": project_relative_path(fixed_hybrid_path),
                "structure_aware_hybrid": project_relative_path(structure_aware_hybrid_path),
                "evidence_eval": project_relative_path(evidence_eval_path),
                "graphrag_review": project_relative_path(graphrag_review_path),
            },
        },
        "gold_label_review": _gold_label_review(gold_labels),
        "default_strategy_decision": _strategy_decision(chunking, evidence_eval),
        "chunking_failure_analysis": {
            "ranking": _chunking_ranking(chunking),
            "fixed_window": _chunking_strategy_result(chunking, "fixed_window"),
            "structure_aware": _chunking_strategy_result(chunking, "structure_aware"),
            "semantic_meta_like": _chunking_strategy_result(chunking, "semantic_meta_like"),
            "interpretation": [
                "Fixed-window is stable and reproducible but may split evidence at artificial boundaries.",
                "Structure-aware chunking preserves handbook sections, improving context precision and explanation quality.",
                "Semantic/meta-like chunking is closer to semantic boundary detection but is costlier and less reproducible in this v1 implementation.",
            ],
        },
        "hybrid_failure_analysis": {
            "fixed_window_hybrid_retrieval_failures": _retrieval_failures(fixed_hybrid),
            "structure_aware_hybrid_retrieval_failures": _retrieval_failures(
                structure_hybrid
            ),
            "fixed_window_evidence_failures": _evidence_failures(
                evidence_eval,
                "fixed_window",
            ),
            "structure_aware_evidence_failures": _evidence_failures(
                evidence_eval,
                "structure_aware",
            ),
        },
        "citation_completeness": {
            "fixed_window": _citation_summary(evidence_eval, "fixed_window"),
            "structure_aware": _citation_summary(evidence_eval, "structure_aware"),
        },
        "graphrag_review_summary": {
            "present": graphrag_review is not None,
            "recommendations": _get(graphrag_review, "recommendations", default=[]),
            "interpretation_count": len(_get(graphrag_review, "interpretations", default=[])),
        },
        "submission_claims": [
            "The project implements a reproducible PDF-to-chunks-to-KG-to-vector-index-to-Hybrid-RAG pipeline for PHAK Chapter 4.",
            "Evaluation is intentionally layered into retrieval, KG evidence, and LLM answer/citation metrics.",
            "Structure-aware chunking is the recommended demo/default strategy; fixed-window remains the baseline.",
            "The advisory assistant boundary is explicit: this is flight learning and decision support, not a substitute for POH, checklist, ATC, instructor, or pilot judgment.",
        ],
        "remaining_limitations": [
            "Gold labels are reviewed for evidence alignment but are not certified by an aviation domain examiner.",
            "The KG is scoped to PHAK Chapter 4 and does not yet cover emergency/procedure manuals.",
            "Page-level Recall@5 is a coarse benchmark and under-represents structured evidence value.",
            "The local web demo is offline-first and does not prove production-scale deployment readiness.",
        ],
        "advisory_boundary": ADVISORY_BOUNDARY,
    }


def write_final_evaluation_review_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_final_evaluation_review_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    decision = result["default_strategy_decision"]
    gold = result["gold_label_review"]
    failure = result["hybrid_failure_analysis"]
    citation = result["citation_completeness"]
    lines = [
        "# Final Evaluation Review",
        "",
        "## Summary",
        "",
        "- Scoring policy: layered metrics only; no mixed overall score.",
        f"- Recommended default strategy: `{decision['recommended_default']}`",
        f"- Baseline strategy: `{decision['baseline']}`",
        f"- Chunking best by retrieval: `{decision['chunking_best_by_retrieval']}`",
        "",
        "## Gold Label Review",
        "",
        f"- Labels: {gold.get('labels_total', 0)}",
        f"- Gold levels: `{gold.get('gold_levels', {})}`",
        f"- Review required: {gold.get('review_required')}",
        f"- Review status: `{gold.get('review_status')}`",
        f"- Human review: {gold.get('human_review')}",
        f"- External aviation expert certified: {gold.get('external_expert_certified')}",
        "",
        "## Strategy Decision",
        "",
    ]
    lines.extend(f"- {item}" for item in decision["rationale"])
    lines.extend(
        [
            "",
            "Evidence-level delta, structure-aware hybrid minus fixed-window hybrid:",
            "",
            "| Metric | Delta |",
            "| --- | ---: |",
        ]
    )
    for key, value in decision["evidence_level_delta"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Chunking Failure Analysis",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in result["chunking_failure_analysis"]["interpretation"])
    lines.extend(
        [
            "",
            "## Hybrid Failure Analysis",
            "",
            "| Group | Count |",
            "| --- | ---: |",
            "| fixed_window retrieval failures | "
            f"{len(failure['fixed_window_hybrid_retrieval_failures'])} |",
            "| structure_aware retrieval failures | "
            f"{len(failure['structure_aware_hybrid_retrieval_failures'])} |",
            f"| fixed_window evidence failures | {len(failure['fixed_window_evidence_failures'])} |",
            "| structure_aware evidence failures | "
            f"{len(failure['structure_aware_evidence_failures'])} |",
            "",
            "## Citation Completeness",
            "",
            "| Experiment | Mode | Citation validity | Supported answers |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for experiment, modes in citation.items():
        for mode, metrics in modes.items():
            support = metrics.get("answer_support_distribution", {})
            lines.append(
                f"| {experiment} | {mode} | {metrics.get('citation_validity')} | "
                f"{support.get('supported', 0)} |"
            )
    lines.extend(
        [
            "",
            "## Submission Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in result["submission_claims"])
    lines.extend(["", "## Remaining Limitations", ""])
    lines.extend(f"- {item}" for item in result["remaining_limitations"])
    lines.extend(["", "## Advisory Boundary", "", result["advisory_boundary"]])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_final_evaluation_review(
    output_dir: str | Path,
    *,
    gold_labels_path: str | Path,
    chunking_comparison_path: str | Path,
    fixed_hybrid_path: str | Path,
    structure_aware_hybrid_path: str | Path,
    evidence_eval_path: str | Path,
    graphrag_review_path: str | Path,
    report_name: str = "final_evaluation_review",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_final_evaluation_review(
        gold_labels_path=gold_labels_path,
        chunking_comparison_path=chunking_comparison_path,
        fixed_hybrid_path=fixed_hybrid_path,
        structure_aware_hybrid_path=structure_aware_hybrid_path,
        evidence_eval_path=evidence_eval_path,
        graphrag_review_path=graphrag_review_path,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "final_evaluation_review"
    json_path = write_final_evaluation_review_json(result, output / f"{stem}.json")
    md_path = write_final_evaluation_review_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
