from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.web.data import (
    ARTIFACTS,
    build_demo_explanation,
    build_experiment_summary,
)


def _read_json(path: str | Path) -> dict[str, Any] | None:
    source = Path(path)
    if not source.exists():
        return None
    data = json.loads(source.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"value": data}


def _metric_value(data: dict[str, Any] | None, *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _artifact_readiness(project_root: str | Path) -> dict[str, dict[str, Any]]:
    root = Path(project_root)
    return {
        key: {
            "path": rel_path,
            "present": (root / rel_path).exists(),
        }
        for key, rel_path in ARTIFACTS.items()
    }


def _kg_graph_sample(report: dict[str, Any] | None) -> dict[str, Any]:
    if not report:
        return {}
    for record in report.get("records", []):
        if not isinstance(record, dict):
            continue
        hybrid = _metric_value(record, "results", "hybrid", default={})
        triples = hybrid.get("graph_triples", []) if isinstance(hybrid, dict) else []
        if triples:
            return {
                "cq_id": record.get("cq_id"),
                "mode": "hybrid",
                "triple_count": len(triples),
            }
    return {}


def build_web_demo_readiness(
    project_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(project_root)
    artifacts = _artifact_readiness(root)
    evidence_eval = _read_json(root / ARTIFACTS["evidence_level_evaluation"])
    graphrag_review = _read_json(root / ARTIFACTS["graphrag_review"])
    structure_report = _read_json(root / ARTIFACTS["structure_aware_hybrid"])
    kg_graph_sample = _kg_graph_sample(structure_report)
    explanation = build_demo_explanation(root)
    explanation_ready = bool(
        explanation.get("pipeline_steps")
        and explanation.get("mode_explanations")
        and explanation.get("strategy_decision", {}).get("recommended")
    )
    structure_ready = (
        artifacts["structure_aware_hybrid"]["present"]
        and artifacts["structure_aware_kg"]["present"]
        and artifacts["structure_aware_chunks"]["present"]
    )
    fixed_ready = artifacts["fixed_hybrid"]["present"]
    evidence_ready = artifacts["evidence_level_evaluation"]["present"]
    selected_default = "structure_aware" if structure_ready and evidence_ready else "fixed_window"
    fixed_hybrid_eval = _metric_value(
        evidence_eval,
        "experiments",
        "fixed_window",
        "aggregate",
        "hybrid",
        default={},
    )
    structure_hybrid_eval = _metric_value(
        evidence_eval,
        "experiments",
        "structure_aware",
        "aggregate",
        "hybrid",
        default={},
    )
    consistency_checks = {
        "layered_scoring_policy": _metric_value(
            evidence_eval,
            "metadata",
            "scoring_policy",
        )
        == "layered_metrics_no_mixed_overall_score",
        "fixed_window_ready": fixed_ready,
        "structure_aware_ready": structure_ready,
        "evidence_level_ready": evidence_ready,
        "advisory_boundary_defined": bool(ADVISORY_BOUNDARY),
        "graphrag_review_ready": graphrag_review is not None,
        "question_scoped_kg_graph_ready": bool(kg_graph_sample),
        "demo_explanation_ready": explanation_ready,
    }
    return {
        "metadata": {
            "created_at": datetime.now(UTC).isoformat(),
            "project_root": project_relative_path(root),
            "purpose": "offline_first_fastapi_web_demo_readiness",
        },
        "ready": all(consistency_checks.values()),
        "selected_default_strategy": selected_default,
        "baseline_strategy": "fixed_window",
        "artifacts": artifacts,
        "consistency_checks": consistency_checks,
        "metrics": {
            "fixed_window_hybrid": fixed_hybrid_eval,
            "structure_aware_hybrid": structure_hybrid_eval,
            "summary": build_experiment_summary(root),
        },
        "kg_graph": {
            "ready": bool(kg_graph_sample),
            "scope": "question_scoped_retrieved_evidence",
            "default_experiment": "structure_aware",
            "default_mode": "hybrid",
            "sample": kg_graph_sample,
        },
        "explanation": {
            "ready": explanation_ready,
            "pipeline_steps": len(explanation.get("pipeline_steps", [])),
            "mode_explanations": len(explanation.get("mode_explanations", {})),
            "recommended_strategy": explanation.get("strategy_decision", {}).get(
                "recommended",
                "TBD",
            ),
            "default_path": explanation.get("narrative", {}).get("default_path", "TBD"),
        },
        "advisory_boundary": ADVISORY_BOUNDARY,
        "demo_script": [
            "Open the local FastAPI web demo.",
            "Start with the Demo Narrative and Pipeline Explanation panels.",
            "Confirm artifact readiness and advisory boundary in the sidebar.",
            "Select a boundary CQ and compare vector, graph, and hybrid evidence.",
            "Use Why This Result to explain the current evidence shape and metric signals.",
            "Use the KG relationship graph to explain retrieved structured evidence.",
            "Switch between structure-aware and fixed-window experiments.",
            "Explain GraphRAG as structured KG evidence support, not a single-score winner.",
        ],
        "ui_smoke_checklist": [
            "macOS-style sidebar question list is visible.",
            "Top toolbar exposes strategy and retrieval mode segmented controls.",
            "Demo Narrative, Pipeline Explanation, and Mode Comparison are visible.",
            "Why This Result updates for the selected question and retrieval mode.",
            "Question-scoped KG graph renders nodes and edges for structure_aware + hybrid.",
            "Vector mode shows a clear empty state for KG graph evidence.",
            "Answer, gold label, chunk evidence, and KG triple evidence remain readable.",
            "Default selection is structure_aware + hybrid.",
            "Narrow viewport does not overlap controls or evidence text.",
        ],
        "recommendations": [
            "Use structure_aware as the default demo strategy when all artifacts are present.",
            "Keep fixed_window visible as the baseline comparison.",
            "Keep live query auto-gated by artifact and LLM readiness for reproducible review demos.",
        ],
    }


def write_web_demo_readiness_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_web_demo_readiness_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fixed = result["metrics"]["fixed_window_hybrid"]
    structure = result["metrics"]["structure_aware_hybrid"]
    kg_graph = result["kg_graph"]
    explanation = result["explanation"]
    lines = [
        "# Web Demo Readiness",
        "",
        f"- Ready: {result['ready']}",
        f"- Default strategy: `{result['selected_default_strategy']}`",
        f"- Baseline strategy: `{result['baseline_strategy']}`",
        "- Live query: auto-gated by artifact and LLM readiness",
        "",
        "## Artifact Readiness",
        "",
        "| Artifact | Present | Path |",
        "| --- | ---: | --- |",
    ]
    for key, item in result["artifacts"].items():
        lines.append(f"| {key} | {item['present']} | `{item['path']}` |")
    lines.extend(
        [
            "",
            "## Evidence Summary",
            "",
            "| Strategy | Chunk Recall@5 | Span hit rate | KG triple relevance | Supported answers |",
            "| --- | ---: | ---: | ---: | ---: |",
            "| fixed_window | "
            f"{fixed.get('chunk_recall_at_5', 'TBD')} | "
            f"{fixed.get('span_hit_rate', 'TBD')} | "
            f"{fixed.get('kg_triple_relevance', 'TBD')} | "
            f"{fixed.get('answer_support_distribution', {}).get('supported', 'TBD')} |",
            "| structure_aware | "
            f"{structure.get('chunk_recall_at_5', 'TBD')} | "
            f"{structure.get('span_hit_rate', 'TBD')} | "
            f"{structure.get('kg_triple_relevance', 'TBD')} | "
            f"{structure.get('answer_support_distribution', {}).get('supported', 'TBD')} |",
            "",
            "## KG Graph Readiness",
            "",
            f"- Ready: {kg_graph['ready']}",
            f"- Scope: `{kg_graph['scope']}`",
            f"- Default: `{kg_graph['default_experiment']}` + `{kg_graph['default_mode']}`",
            "- Sample: "
            f"`{kg_graph.get('sample', {}).get('cq_id', 'TBD')}` with "
            f"{kg_graph.get('sample', {}).get('triple_count', 'TBD')} triples",
            "",
            "## Demo Explanation Readiness",
            "",
            f"- Ready: {explanation['ready']}",
            f"- Default path: `{explanation['default_path']}`",
            f"- Recommended strategy: `{explanation['recommended_strategy']}`",
            f"- Pipeline steps: {explanation['pipeline_steps']}",
            f"- Mode explanations: {explanation['mode_explanations']}",
            "",
            "## Demo Script",
            "",
        ]
    )
    lines.extend(f"- {step}" for step in result["demo_script"])
    lines.extend(
        [
            "",
            "## Apple-Style UI Smoke Checklist",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in result["ui_smoke_checklist"])
    lines.extend(
        [
            "",
            "## Advisory Boundary",
            "",
            result["advisory_boundary"],
            "",
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_web_demo_readiness(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    report_name: str = "web_demo_readiness",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_web_demo_readiness(project_root)
    output = Path(output_dir)
    stem = Path(report_name).stem or "web_demo_readiness"
    json_path = write_web_demo_readiness_json(result, output / f"{stem}.json")
    md_path = write_web_demo_readiness_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
