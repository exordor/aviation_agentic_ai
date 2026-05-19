from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path


def _load_json(path: str | Path) -> dict[str, Any] | None:
    source = Path(path)
    if not source.exists():
        return None
    data = json.loads(source.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"value": data}


def _metric(data: dict[str, Any], *keys: str, default: Any = "TBD") -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _mode_summary(experiment: dict[str, Any], mode: str) -> dict[str, Any]:
    return {
        "retrieval": _metric(experiment, "aggregate", mode, "retrieval", default={}),
        "kg_evidence": _metric(experiment, "aggregate", mode, "kg_evidence", default={}),
        "llm_answer": _metric(experiment, "aggregate", mode, "llm_answer", default={}),
    }


def _failure_cases(experiment: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for record in experiment.get("records", []):
        if not isinstance(record, dict):
            continue
        hybrid = record.get("results", {}).get("hybrid", {})
        metrics = hybrid.get("metrics", {})
        retrieval = metrics.get("retrieval", {})
        kg_metrics = metrics.get("kg_evidence", {})
        answer = metrics.get("llm_answer", {})
        retrieval_hit = bool(retrieval.get("recall_at_5"))
        kg_covered = bool(kg_metrics.get("evidence_coverage"))
        citation_complete = bool(answer.get("citation_completeness"))
        if not retrieval_hit and kg_covered:
            failure_type = "page_recall_miss_but_kg_evidence_found"
        elif retrieval_hit and not kg_covered:
            failure_type = "retrieval_hit_but_kg_evidence_missing"
        elif not citation_complete:
            failure_type = "citation_incomplete"
        else:
            continue
        failures.append(
            {
                "cq_id": record.get("cq_id"),
                "failure_type": failure_type,
                "question": record.get("question"),
                "source_page": record.get("source_page"),
                "hybrid_recall_at_5": retrieval.get("recall_at_5"),
                "kg_evidence_coverage": kg_metrics.get("evidence_coverage"),
                "citation_completeness": answer.get("citation_completeness"),
            }
        )
    return failures


def _experiment_summary(label: str, experiment: dict[str, Any] | None) -> dict[str, Any]:
    if not experiment:
        return {"label": label, "present": False}
    aggregate = experiment.get("aggregate", {})
    return {
        "label": label,
        "present": True,
        "metadata": experiment.get("metadata", {}),
        "vector": _mode_summary(experiment, "vector"),
        "graph": _mode_summary(experiment, "graph"),
        "hybrid": _mode_summary(experiment, "hybrid"),
        "hybrid_lift": aggregate.get("hybrid_lift", {}),
        "failure_cases": _failure_cases(experiment),
    }


def _chunking_summary(chunking: dict[str, Any] | None) -> dict[str, Any]:
    if not chunking:
        return {"present": False}
    ranking = chunking.get("ranking", [])
    best = ranking[0] if ranking and isinstance(ranking[0], dict) else {}
    strategies = chunking.get("strategies", {})
    return {
        "present": True,
        "best_strategy": best.get("strategy"),
        "ranking": ranking,
        "structure_aware": strategies.get("structure_aware", {}).get("aggregate", {}),
        "fixed_window": strategies.get("fixed_window", {}).get("aggregate", {}),
    }


def _interpretations(
    fixed: dict[str, Any],
    structure_aware: dict[str, Any],
    chunking: dict[str, Any],
) -> list[dict[str, str]]:
    fixed_vector_recall = _metric(fixed, "vector", "retrieval", "recall_at_5")
    fixed_hybrid_recall = _metric(fixed, "hybrid", "retrieval", "recall_at_5")
    fixed_graph_coverage = _metric(fixed, "graph", "kg_evidence", "evidence_coverage")
    fixed_hybrid_coverage = _metric(fixed, "hybrid", "kg_evidence", "evidence_coverage")
    best_strategy = chunking.get("best_strategy", "TBD")
    items = [
        {
            "claim": "GraphRAG value is evidence structure, not current page-level Recall lift.",
            "evidence": (
                f"Fixed-window vector Recall@5={fixed_vector_recall}; hybrid "
                f"Recall@5={fixed_hybrid_recall}; graph/hybrid KG evidence coverage="
                f"{fixed_graph_coverage}/{fixed_hybrid_coverage}."
            ),
            "implication": (
                "Do not claim Hybrid RAG beats vector-only retrieval on the current "
                "coarse page-level benchmark."
            ),
        },
        {
            "claim": "Vector-only can win page-level Recall@5 because the gold label is coarse.",
            "evidence": (
                "The current gold target is source_page, so any chunk from the right "
                "page counts even when it lacks structured relations."
            ),
            "implication": "Add chunk/span-level gold labels before drawing stronger GraphRAG conclusions.",
        },
        {
            "claim": "Hybrid fusion can lower page Recall when graph results add related but off-page evidence.",
            "evidence": "Fixed-window hybrid lift vs vector Recall@5="
            f"{_metric(fixed, 'hybrid_lift', 'vs_vector_recall_at_5')}.",
            "implication": "Review fusion failures before tuning graph weight or hop depth.",
        },
        {
            "claim": f"{best_strategy} is the best chunking candidate for the next KG.",
            "evidence": "Chunking comparison ranked it first by Recall@5/MRR@5/Context Precision@5.",
            "implication": "Re-extract KG on structure-aware chunks before using it as the Hybrid RAG default.",
        },
    ]
    if structure_aware.get("present"):
        items.append(
            {
                "claim": "Structure-aware Hybrid RAG is available as a second experiment.",
                "evidence": "Its metrics are recorded separately and should be compared with fixed-window.",
                "implication": "Use the paired reports to decide the default chunking strategy.",
            }
        )
    return items


def build_graphrag_review(
    chunking_comparison_path: str | Path,
    fixed_hybrid_path: str | Path,
    structure_aware_hybrid_path: str | Path | None = None,
) -> dict[str, Any]:
    chunking = _load_json(chunking_comparison_path)
    fixed_experiment = _load_json(fixed_hybrid_path)
    if fixed_experiment is None:
        raise FileNotFoundError(f"Missing fixed-window Hybrid RAG report: {fixed_hybrid_path}")
    structure_experiment = (
        _load_json(structure_aware_hybrid_path)
        if structure_aware_hybrid_path is not None
        else None
    )
    fixed_summary = _experiment_summary("fixed_window", fixed_experiment)
    structure_summary = _experiment_summary("structure_aware", structure_experiment)
    chunking_summary = _chunking_summary(chunking)
    return {
        "metadata": {
            "created_at": datetime.now(UTC).isoformat(),
            "chunking_comparison_path": project_relative_path(chunking_comparison_path),
            "fixed_hybrid_path": project_relative_path(fixed_hybrid_path),
            "structure_aware_hybrid_path": project_relative_path(structure_aware_hybrid_path)
            if structure_aware_hybrid_path is not None
            else None,
            "structure_aware_present": bool(structure_experiment),
        },
        "chunking_comparison": chunking_summary,
        "experiments": {
            "fixed_window": fixed_summary,
            "structure_aware": structure_summary,
        },
        "interpretations": _interpretations(
            fixed_summary,
            structure_summary,
            chunking_summary,
        ),
        "recommendations": [
            "Report GraphRAG as adding structured KG evidence, not as current page Recall@5 winner.",
            "Use structure-aware chunks for the next KG extraction candidate.",
            "Refine gold labels to chunk/span-level evidence before optimizing fusion.",
        ],
    }


def write_graphrag_review_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_graphrag_review_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fixed = result["experiments"]["fixed_window"]
    structure = result["experiments"]["structure_aware"]
    chunking = result["chunking_comparison"]
    lines = [
        "# GraphRAG Review",
        "",
        "## Summary",
        "",
        "GraphRAG's current value is KG evidence coverage and explainable structured "
        "evidence, not higher page-level Recall@5 than vector-only retrieval.",
        "",
        "## Fixed-Window Baseline",
        "",
        "| Mode | Recall@5 | MRR@5 | Context Precision@5 | KG evidence coverage | Citation completeness |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode in ("vector", "graph", "hybrid"):
        summary = fixed[mode]
        lines.append(
            f"| {mode} | {_metric(summary, 'retrieval', 'recall_at_5')} | "
            f"{_metric(summary, 'retrieval', 'mrr_at_5')} | "
            f"{_metric(summary, 'retrieval', 'context_precision_at_5')} | "
            f"{_metric(summary, 'kg_evidence', 'evidence_coverage')} | "
            f"{_metric(summary, 'llm_answer', 'citation_completeness')} |"
        )
    lines.extend(
        [
            "",
            "Hybrid lift:",
            f"- vs vector Recall@5: {_metric(fixed, 'hybrid_lift', 'vs_vector_recall_at_5')}",
            f"- vs graph Recall@5: {_metric(fixed, 'hybrid_lift', 'vs_graph_recall_at_5')}",
            "",
            "## Chunking Interpretation",
            "",
            f"- Best chunking strategy: `{chunking.get('best_strategy', 'TBD')}`.",
            "- `structure_aware` preserves handbook section/list boundaries, which explains "
            "its stronger MRR and Context Precision in the chunking comparison.",
            "",
            "## Failure Cases",
            "",
        ]
    )
    failures = fixed.get("failure_cases", [])
    if failures:
        for failure in failures:
            lines.append(
                f"- `{failure['cq_id']}`: {failure['failure_type']} "
                f"(source page {failure['source_page']})."
            )
    else:
        lines.append("- None identified in the fixed-window hybrid records.")
    lines.extend(["", "## Structure-Aware Experiment", ""])
    if structure.get("present"):
        lines.extend(
            [
                "| Mode | Recall@5 | MRR@5 | Context Precision@5 | KG evidence coverage | Citation completeness |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for mode in ("vector", "graph", "hybrid"):
            summary = structure[mode]
            lines.append(
                f"| {mode} | {_metric(summary, 'retrieval', 'recall_at_5')} | "
                f"{_metric(summary, 'retrieval', 'mrr_at_5')} | "
                f"{_metric(summary, 'retrieval', 'context_precision_at_5')} | "
                f"{_metric(summary, 'kg_evidence', 'evidence_coverage')} | "
                f"{_metric(summary, 'llm_answer', 'citation_completeness')} |"
            )
    else:
        lines.append("Not yet run. Use structure-aware KG extraction before comparing defaults.")
    lines.extend(["", "## Interpretations", ""])
    for item in result["interpretations"]:
        lines.extend(
            [
                f"- {item['claim']}",
                f"  Evidence: {item['evidence']}",
                f"  Implication: {item['implication']}",
            ]
        )
    lines.extend(["", "## Recommendations", ""])
    for recommendation in result["recommendations"]:
        lines.append(f"- {recommendation}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_graphrag_review(
    chunking_comparison_path: str | Path,
    fixed_hybrid_path: str | Path,
    output_dir: str | Path,
    *,
    structure_aware_hybrid_path: str | Path | None = None,
    report_name: str = "graphrag_review",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_graphrag_review(
        chunking_comparison_path,
        fixed_hybrid_path,
        structure_aware_hybrid_path=structure_aware_hybrid_path,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "graphrag_review"
    json_path = write_graphrag_review_json(result, output / f"{stem}.json")
    md_path = write_graphrag_review_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
