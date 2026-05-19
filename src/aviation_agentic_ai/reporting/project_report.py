from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.config import load_yaml
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.hygiene import build_hygiene_plan


PROJECT_REPORT_SECTIONS = (
    "Project motivation and course objective alignment",
    "Architecture overview",
    "Ontology/TBox generation and evaluation",
    "KG/ABox extraction and validation",
    "Chunking comparison design",
    "Hybrid RAG protocol and layered metrics",
    "Current results and limitations",
    "Advisory assistant boundary",
    "Next work plan",
    "Reproducibility appendix",
)

LLMRunner = Callable[[str, float, int], str]


def _read_text_source(
    path: Path,
    *,
    base: str | Path = PROJECT_ROOT,
    max_chars: int = 4000,
) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "excerpt": "",
        }
    text = path.read_text(encoding="utf-8")
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "excerpt": text[:max_chars],
        "truncated": len(text) > max_chars,
    }


def _read_binary_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "binary": True,
            "size_bytes": 0,
        }
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "binary": True,
        "format": path.suffix.removeprefix(".") or "binary",
        "size_bytes": path.stat().st_size,
        "excerpt": "",
    }


def _read_yaml_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "data": {},
        }
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "data": load_yaml(path),
    }


def _compact_chunking_report(data: dict[str, Any]) -> dict[str, Any]:
    strategies: dict[str, Any] = {}
    for name, strategy in data.get("strategies", {}).items():
        if not isinstance(strategy, dict):
            continue
        records = strategy.get("records", [])
        strategies[name] = {
            "aggregate": strategy.get("aggregate", {}),
            "chunks_path": strategy.get("chunks_path"),
            "collection_name": strategy.get("collection_name"),
            "explanation": strategy.get("explanation"),
            "recommendation": strategy.get("recommendation"),
            "records_total": len(records) if isinstance(records, list) else "unknown",
            "tradeoff": strategy.get("tradeoff"),
        }
    return {
        "metadata": data.get("metadata", {}),
        "ranking": data.get("ranking", []),
        "strategies": strategies,
        "source_compaction": "strategy records and retrieved chunk texts omitted",
    }


def _compact_hybrid_record(record: dict[str, Any]) -> dict[str, Any]:
    compact_results: dict[str, Any] = {}
    for mode, result in record.get("results", {}).items():
        if not isinstance(result, dict):
            continue
        metrics = result.get("metrics", {})
        retrieval = metrics.get("retrieval", {}) if isinstance(metrics, dict) else {}
        compact_results[mode] = {
            "metrics": metrics,
            "matched_chunk_ids": retrieval.get("matched_chunk_ids", []),
            "matched_source_pages": retrieval.get("matched_source_pages", []),
            "retrieved_chunk_ids": retrieval.get("retrieved_chunk_ids", []),
            "retrieved_source_pages": retrieval.get("retrieved_source_pages", []),
        }
    gold = record.get("gold", {})
    return {
        "cq_id": record.get("cq_id"),
        "gold_level": gold.get("gold_level") if isinstance(gold, dict) else None,
        "key_entities": record.get("key_entities", []),
        "question": record.get("question"),
        "results": compact_results,
        "source_page": record.get("source_page"),
    }


def _compact_hybrid_report(data: dict[str, Any]) -> dict[str, Any]:
    records = data.get("records", [])
    return {
        "aggregate": data.get("aggregate", {}),
        "metadata": data.get("metadata", {}),
        "records": [
            _compact_hybrid_record(record)
            for record in records
            if isinstance(record, dict)
        ],
        "records_total": len(records) if isinstance(records, list) else "unknown",
        "source_compaction": "prompts, answers, triples, and full retrieved chunk texts omitted",
    }


def _compact_json_data(path: Path, data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if path.name == "chunking_comparison.json":
        return _compact_chunking_report(data), True
    if path.name.startswith("hybrid_rag") and path.suffix == ".json":
        return _compact_hybrid_report(data), True
    return data, False


def _read_json_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "data": {},
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    data = data if isinstance(data, dict) else {"value": data}
    compacted_data, compacted = _compact_json_data(path, data)
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "data": compacted_data,
        "compacted": compacted,
    }


def _read_artifact_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if path.suffix == ".json":
        return _read_json_source(path, base=base)
    if path.suffix in {".yaml", ".yml"}:
        return _read_yaml_source(path, base=base)
    if path.suffix.lower() in {".pptx", ".pdf", ".png", ".jpg", ".jpeg", ".webp"}:
        return _read_binary_source(path, base=base)
    return _read_text_source(path, base=base, max_chars=8000)


def _read_current_artifacts(
    root: Path,
    current_artifacts: dict[str, Any],
) -> dict[str, Any]:
    sources: dict[str, Any] = {}
    for key, rel_path in current_artifacts.items():
        if not isinstance(rel_path, str):
            continue
        path = root / rel_path
        sources[key] = _read_artifact_source(path, base=root)
        if path.suffix == ".md":
            json_path = path.with_suffix(".json")
            if json_path.exists():
                sources[f"{key}_json"] = _read_json_source(json_path, base=root)
    return sources


def build_project_evidence_pack(
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
    stage_dir: str | Path | None = None,
    reviews_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(project_root)
    stages = Path(stage_dir) if stage_dir is not None else root / "reports" / "stages"
    reviews = Path(reviews_dir) if reviews_dir is not None else root / "reports" / "reviews"
    index_path = Path(stage_index_path) if stage_index_path is not None else stages / "index.json"
    if index_path.exists():
        stage_index = _read_json_source(index_path, base=root)
    else:
        stage_index = {
            "path": project_relative_path(index_path, base=root),
            "present": False,
            "data": build_hygiene_plan(
                stages,
                root / "reports" / "archive",
                reviews,
                base=root,
            ),
        }
    current_artifacts = stage_index.get("data", {}).get("current_active_artifacts", {})
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "report_sections": list(PROJECT_REPORT_SECTIONS),
        "advisory_boundary": ADVISORY_BOUNDARY,
        "stage_index": stage_index,
        "current_artifacts": _read_current_artifacts(root, current_artifacts)
        if isinstance(current_artifacts, dict)
        else {},
        "readme": _read_text_source(root / "README.md", base=root),
        "goals": _read_text_source(root / "GOALS.md", base=root),
        "tasks": _read_text_source(root / "TASKS.md", base=root),
        "course_goal": _read_text_source(root / "tmp" / "goal.md", base=root),
        "configs": {
            "default": _read_yaml_source(root / "configs" / "default.yaml", base=root),
            "ontology_generation": _read_yaml_source(
                root / "configs" / "ontology_generation.yaml",
                base=root,
            ),
            "extraction_profile": _read_yaml_source(
                root / "configs" / "extraction_profile.yaml",
                base=root,
            ),
        },
        "source_policy": {
            "env_files_read": False,
            "secrets_allowed": False,
            "missing_results_policy": "Use TBD / Not yet run; do not invent results.",
        },
    }


def _present_marker(source: dict[str, Any]) -> str:
    return "present" if source.get("present") else "missing"


def _metric_value(data: dict[str, Any], *keys: str, default: str = "TBD") -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _chunking_summary_lines(
    artifact_sources: dict[str, Any],
    categories: dict[str, Any],
) -> list[str]:
    report = artifact_sources.get("chunking_comparison")
    data = artifact_sources.get("chunking_comparison_json", {}).get("data", {})
    if not isinstance(data, dict) or not data:
        return [
            f"RAG experiment artifacts listed: {len(categories.get('rag_experiments', []))}. "
            "Chunking comparison should discuss retrieval tradeoffs rather than collapse "
            "them into a single score.",
        ]

    ranking = data.get("ranking", [])
    strategies = data.get("strategies", {})
    metadata = data.get("metadata", {})
    best = ranking[0] if ranking and isinstance(ranking[0], dict) else {}
    best_name = best.get("strategy", "TBD")
    fixed = strategies.get("fixed_window", {}) if isinstance(strategies, dict) else {}
    fixed_retrieval = _metric_value(fixed, "aggregate", "retrieval", default={})
    fixed_chunking = _metric_value(fixed, "aggregate", "chunking", default={})
    best_strategy = strategies.get(best_name, {}) if isinstance(strategies, dict) else {}
    best_chunking = _metric_value(best_strategy, "aggregate", "chunking", default={})
    report_path = report.get("path", "reports/stages/chunking_comparison.md") if report else "TBD"
    return [
        f"Chunking comparison evidence: `{report_path}`. It evaluated "
        f"{metadata.get('questions_total', 'TBD')} boundary CQs across "
        f"{len(strategies) if isinstance(strategies, dict) else 'TBD'} strategies.",
        f"Best chunking strategy: {best_name} with Recall@5="
        f"{best.get('recall_at_5', 'TBD')}, MRR@5={best.get('mrr_at_5', 'TBD')}, "
        f"and Context Precision@5={best.get('context_precision_at_5', 'TBD')}.",
        "Fixed-window remains the KG-aligned strategy for the current Hybrid RAG run: "
        f"Recall@5={fixed_retrieval.get('recall_at_5', 'TBD')}, "
        f"MRR@5={fixed_retrieval.get('mrr_at_5', 'TBD')}, Context Precision@5="
        f"{fixed_retrieval.get('context_precision_at_5', 'TBD')}, chunks="
        f"{fixed_chunking.get('chunk_count', 'TBD')}.",
        f"Interpretation: {best_name} improves ranking quality and context precision by "
        "preserving handbook structure, but its finer granularity increases chunk count "
        f"to {best_chunking.get('chunk_count', 'TBD')}. It is a candidate for future "
        "KG re-extraction rather than being mixed with the current fixed-window KG.",
    ]


def _hybrid_summary_lines(
    artifact_sources: dict[str, Any],
    retrieval_config: dict[str, Any],
) -> list[str]:
    report = artifact_sources.get("hybrid_rag_experiment")
    data = artifact_sources.get("hybrid_rag_experiment_json", {}).get("data", {})
    if not isinstance(data, dict) or not data:
        return [
            "Hybrid RAG uses separate retrieval, KG evidence, and LLM answer metrics. "
            f"Configured retrieval defaults include vector_top_k="
            f"{retrieval_config.get('vector_top_k', 'TBD')}, graph_hops="
            f"{retrieval_config.get('graph_hops', 'TBD')}, and hybrid_top_k="
            f"{retrieval_config.get('hybrid_top_k', 'TBD')}.",
        ]

    metadata = data.get("metadata", {})
    aggregate = data.get("aggregate", {})
    vector = aggregate.get("vector", {})
    graph = aggregate.get("graph", {})
    hybrid = aggregate.get("hybrid", {})
    lift = aggregate.get("hybrid_lift", {})
    manifest = metadata.get("run_manifest", {})
    llm = manifest.get("llm", {}) if isinstance(manifest, dict) else {}
    report_path = report.get("path", "reports/stages/hybrid_rag_experiment.md") if report else "TBD"
    lines = [
        f"Hybrid RAG evidence: `{report_path}`. It evaluated "
        f"{metadata.get('questions_total', 'TBD')} boundary CQs using "
        f"`{metadata.get('chunking_strategy', 'TBD')}` chunks, collection "
        f"`{metadata.get('collection_name', 'TBD')}`, and LLM "
        f"{llm.get('provider', 'TBD')}/{llm.get('model', 'TBD')}.",
        "Retrieval metrics: vector Recall@5="
        f"{_metric_value(vector, 'retrieval', 'recall_at_5')}, graph Recall@5="
        f"{_metric_value(graph, 'retrieval', 'recall_at_5')}, hybrid Recall@5="
        f"{_metric_value(hybrid, 'retrieval', 'recall_at_5')}; vector MRR@5="
        f"{_metric_value(vector, 'retrieval', 'mrr_at_5')}, graph MRR@5="
        f"{_metric_value(graph, 'retrieval', 'mrr_at_5')}, hybrid MRR@5="
        f"{_metric_value(hybrid, 'retrieval', 'mrr_at_5')}.",
        "KG evidence metrics: graph coverage="
        f"{_metric_value(graph, 'kg_evidence', 'evidence_coverage')}, hybrid coverage="
        f"{_metric_value(hybrid, 'kg_evidence', 'evidence_coverage')}, hybrid provenance "
        f"complete={_metric_value(hybrid, 'kg_evidence', 'provenance_complete_rate')}, "
        f"hybrid invalid triples={_metric_value(hybrid, 'kg_evidence', 'avg_invalid_triple_count')}.",
        "LLM answer metrics: vector citation completeness="
        f"{_metric_value(vector, 'llm_answer', 'citation_completeness')}, graph="
        f"{_metric_value(graph, 'llm_answer', 'citation_completeness')}, hybrid="
        f"{_metric_value(hybrid, 'llm_answer', 'citation_completeness')}; hybrid "
        "insufficient-evidence abstention="
        f"{_metric_value(hybrid, 'llm_answer', 'insufficient_evidence_abstention')}.",
        "Hybrid lift is reported as layered evidence, not a mixed total score: "
        f"vs vector Recall@5={lift.get('vs_vector_recall_at_5', 'TBD')}, "
        f"vs graph Recall@5={lift.get('vs_graph_recall_at_5', 'TBD')}.",
    ]
    structure_report = artifact_sources.get("hybrid_rag_structure_aware")
    structure_data = artifact_sources.get("hybrid_rag_structure_aware_json", {}).get("data", {})
    if isinstance(structure_data, dict) and structure_data:
        structure_metadata = structure_data.get("metadata", {})
        structure_aggregate = structure_data.get("aggregate", {})
        structure_hybrid = structure_aggregate.get("hybrid", {})
        structure_lift = structure_aggregate.get("hybrid_lift", {})
        structure_path = structure_report.get("path", "reports/stages/hybrid_rag_structure_aware.md")
        lines.append(
            f"Structure-aware Hybrid RAG evidence: `{structure_path}`. It evaluated "
            f"{structure_metadata.get('questions_total', 'TBD')} boundary CQs with hybrid "
            f"Recall@5={_metric_value(structure_hybrid, 'retrieval', 'recall_at_5')}, "
            "KG evidence coverage="
            f"{_metric_value(structure_hybrid, 'kg_evidence', 'evidence_coverage')}, "
            "and lift vs vector Recall@5="
            f"{structure_lift.get('vs_vector_recall_at_5', 'TBD')}."
        )
    review = artifact_sources.get("graphrag_review")
    if review and review.get("present"):
        lines.append(
            f"GraphRAG interpretation evidence: `{review.get('path')}` explains "
            "retrieval, KG evidence, and LLM answer behavior separately."
        )
    evidence_report = artifact_sources.get("evidence_level_evaluation")
    evidence_data = artifact_sources.get("evidence_level_evaluation_json", {}).get("data", {})
    if isinstance(evidence_data, dict) and evidence_data:
        fixed_hybrid = _metric_value(
            evidence_data,
            "experiments",
            "fixed_window",
            "aggregate",
            "hybrid",
            default={},
        )
        structure_hybrid = _metric_value(
            evidence_data,
            "experiments",
            "structure_aware",
            "aggregate",
            "hybrid",
            default={},
        )
        structure_support = structure_hybrid.get("answer_support_distribution", {})
        fixed_support = fixed_hybrid.get("answer_support_distribution", {})
        lines.append(
            "Evidence-level evaluation: "
            f"`{evidence_report.get('path', 'reports/stages/evidence_level_evaluation.md')}` "
            f"shows structure-aware hybrid span hit rate="
            f"{structure_hybrid.get('span_hit_rate', 'TBD')} and supported answers="
            f"{structure_support.get('supported', 'TBD')}; fixed-window hybrid span hit rate="
            f"{fixed_hybrid.get('span_hit_rate', 'TBD')} and supported answers="
            f"{fixed_support.get('supported', 'TBD')}."
        )
    return lines


def build_project_report_draft(evidence: dict[str, Any]) -> str:
    stage_index = evidence.get("stage_index", {}).get("data", {})
    categories = stage_index.get("categories", {})
    current_artifacts = stage_index.get("current_active_artifacts", {})
    artifact_sources = evidence.get("current_artifacts", {})
    curated_eval = artifact_sources.get("curated_ontology_evaluation_json", {}).get("data", {})
    kg_validation = artifact_sources.get("kg_validation_json", {}).get("data", {})
    structure_kg_validation = artifact_sources.get(
        "structure_aware_kg_validation_json", {}
    ).get("data", {})
    structural = curated_eval.get("structural_metrics", {}) if isinstance(curated_eval, dict) else {}
    judgment = curated_eval.get("judgment", {}) if isinstance(curated_eval, dict) else {}
    config_default = evidence.get("configs", {}).get("default", {}).get("data", {})
    retrieval_config = config_default.get("retrieval", {}) if isinstance(config_default, dict) else {}
    ontology_path = current_artifacts.get("active_ontology", "TBD")
    ontology_design = current_artifacts.get("ontology_design", "TBD")
    kg_path = kg_validation.get("kg_path", current_artifacts.get("validated_kg", "TBD"))
    kg_triples = kg_validation.get("triples_total", "TBD")
    kg_errors = kg_validation.get("errors_total", "TBD")
    structure_kg_path = structure_kg_validation.get(
        "kg_path",
        current_artifacts.get("structure_aware_kg", "TBD"),
    )
    structure_kg_triples = structure_kg_validation.get("triples_total", "TBD")
    structure_kg_errors = structure_kg_validation.get("errors_total", "TBD")
    web_readiness = artifact_sources.get("web_demo_readiness_json", {}).get("data", {})
    web_explanation = (
        web_readiness.get("explanation", {}) if isinstance(web_readiness, dict) else {}
    )
    chunking_lines = _chunking_summary_lines(artifact_sources, categories)
    hybrid_lines = _hybrid_summary_lines(artifact_sources, retrieval_config)
    has_chunking = bool(
        artifact_sources.get("chunking_comparison_json", {}).get("data", {})
    )
    has_hybrid = bool(
        artifact_sources.get("hybrid_rag_experiment_json", {}).get("data", {})
    )
    has_structure_hybrid = bool(
        artifact_sources.get("hybrid_rag_structure_aware_json", {}).get("data", {})
    )
    has_evidence_eval = bool(
        artifact_sources.get("evidence_level_evaluation_json", {}).get("data", {})
    )
    has_web_readiness = isinstance(web_readiness, dict) and bool(web_readiness)
    if has_chunking and has_hybrid:
        if has_structure_hybrid:
            first_next_work = (
                "1. Review the auto-drafted chunk/span gold labels and fix weak spans."
                if has_evidence_eval
                else "1. Refine gold labels from source-page to chunk/span evidence."
            )
            if has_web_readiness:
                next_work_lines = [
                    first_next_work,
                    "2. Smoke-test the FastAPI web demo and capture final review notes.",
                    "3. Write project-defense conclusions from fixed-window and structure-aware runs.",
                    "4. Generate the AI-polished final report after review.",
                    "5. Prepare final submission checks.",
                ]
            else:
                next_work_lines = [
                    first_next_work,
                    "2. Write project-defense conclusions from fixed-window and structure-aware runs.",
                    "3. Decide whether `structure_aware` becomes the default GraphRAG strategy.",
                    "4. Generate the AI-polished final report after review.",
                    "5. Implement the minimal web interface demonstrator.",
                ]
        else:
            next_work_lines = [
                "1. Review the chunking and Hybrid RAG reports for project-defense claims.",
                "2. Decide whether to re-extract the KG with `structure_aware` chunks.",
                "3. Refine gold labels from source-page to chunk/span evidence.",
                "4. Generate the AI-polished final report after review.",
                "5. Implement the minimal web interface demonstrator.",
            ]
    else:
        next_work_lines = [
            "1. Run report hygiene to maintain a readable stage dashboard.",
            "2. Run chunking comparison and Hybrid RAG experiments with recorded run manifests.",
            "3. Refine gold labels from source-page to chunk/span evidence.",
            "4. Use the AI report command to polish this deterministic draft.",
        ]
    reproducibility_lines = [
        "- `uv run aviation-ai report chunking-comparison`",
        "- `uv run aviation-ai index build`",
        "- `uv run aviation-ai report hybrid-rag`",
    ]
    if has_structure_hybrid:
        reproducibility_lines.extend(
            [
                "- `uv run aviation-ai kg extract --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --ttl-output data/kg/06_phak_ch4_0.structure_aware.kg.ttl`",
                "- `uv run aviation-ai kg validate --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output-dir reports/stages --report-name structure_aware_kg_validation`",
                "- `uv run aviation-ai index build --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --collection-name phak_ch4_chunks_structure_aware`",
                "- `uv run aviation-ai report hybrid-rag --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --collection-name phak_ch4_chunks_structure_aware --chunking-strategy structure_aware --report-name hybrid_rag_structure_aware`",
                "- `uv run aviation-ai report graphrag-review`",
            ]
        )
    if has_evidence_eval:
        reproducibility_lines.extend(
            [
                "- `uv run aviation-ai cqs gold-draft`",
                "- `uv run aviation-ai report evidence-eval`",
            ]
        )
    if has_web_readiness:
        reproducibility_lines.extend(
            [
                "- `uv run aviation-ai report web-demo-readiness`",
                "- `uv run aviation-ai web serve`",
            ]
        )
    reproducibility_lines.extend(
        [
            "- `uv run aviation-ai report hygiene --apply`",
            "- `uv run aviation-ai report project --no-ai`",
            "- `uv run aviation-ai report project --ai`",
        ]
    )
    lines = [
        "# Aviation Agentic AI Project Report",
        "",
        "## Project motivation and course objective alignment",
        "",
        "This project investigates a reproducible aviation-domain RAG pipeline that turns "
        "FAA training text into ontology, KG, retrieval, and grounded-answer artifacts. "
        f"Course goal evidence: `{evidence['course_goal']['path']}` "
        f"({_present_marker(evidence['course_goal'])}).",
        "",
        "## Architecture overview",
        "",
        "The implementation is CLI-first and separates ontology, KG extraction, chunking, "
        "retrieval, evaluation, and reporting modules. Primary configuration evidence is "
        "`configs/default.yaml`, `configs/ontology_generation.yaml`, and "
        "`configs/extraction_profile.yaml`.",
        "",
        "## Ontology/TBox generation and evaluation",
        "",
        f"The active ontology is `{ontology_path}`, with design rationale in "
        f"`{ontology_design}`. It replaces the historical baseline as the explainable "
        "schema used for KG extraction.",
        f"Curated ontology metrics: triples={structural.get('triples', 'TBD')}, "
        f"classes={structural.get('classes', 'TBD')}, object_properties="
        f"{structural.get('object_properties', 'TBD')}, TBox-only="
        f"{structural.get('tbox_only', 'TBD')}, label coverage="
        f"{structural.get('class_label_coverage', 'TBD')}.",
        f"Ontology judgment: valid TBox prototype="
        f"{judgment.get('valid_tbox_prototype', 'TBD')}, publication-ready="
        f"{judgment.get('publication_ready_ontology', 'TBD')}.",
        f"Historical ontology evaluation artifacts indexed: "
        f"{len(categories.get('ontology_evaluation', []))}.",
        "",
        "## KG/ABox extraction and validation",
        "",
        "The KG stage is designed around focused triples with provenance and deterministic "
        "validation against the extraction profile.",
        f"Validated KG artifact: `{kg_path}`. Triples={kg_triples}; validation errors="
        f"{kg_errors}; ontology constraint=`{kg_validation.get('ontology_path', ontology_path)}`.",
        f"Structure-aware KG artifact: `{structure_kg_path}`. Triples="
        f"{structure_kg_triples}; validation errors={structure_kg_errors}. It is kept "
        "separate from the fixed-window KG to avoid mixing chunk-id schemas.",
        "",
        "## Chunking comparison design",
        "",
        *chunking_lines,
        "",
        "## Hybrid RAG protocol and layered metrics",
        "",
        *hybrid_lines,
        "",
        "## Current results and limitations",
        "",
        "Current evidence now covers the explainable curated ontology, fixed-window KG, "
        "structure-aware KG, chunking comparison, fixed-window Hybrid RAG, "
        "structure-aware Hybrid RAG, and GraphRAG review when their reports are present "
        "in the stage index.",
        "Web demo readiness: "
        f"ready={web_readiness.get('ready', 'TBD') if isinstance(web_readiness, dict) else 'TBD'}, "
        "default strategy="
        f"{web_readiness.get('selected_default_strategy', 'TBD') if isinstance(web_readiness, dict) else 'TBD'}.",
        "The web demo is an offline-first FastAPI interface with a macOS-style "
        "sidebar, toolbar controls, answer workspace, chunk evidence, KG triple "
        "evidence, KG relationship graph, pipeline explanation, mode comparison, "
        "Why This Result panel, and advisory boundary display.",
        "Web explanation readiness: "
        f"ready={web_explanation.get('ready', 'TBD') if isinstance(web_explanation, dict) else 'TBD'}, "
        "default path="
        f"{web_explanation.get('default_path', 'TBD') if isinstance(web_explanation, dict) else 'TBD'}, "
        "recommended strategy="
        f"{web_explanation.get('recommended_strategy', 'TBD') if isinstance(web_explanation, dict) else 'TBD'}.",
        "Limitations: chunk/span gold labels are auto-drafted and still require "
        "human review, structure-aware KG extraction is more expensive because it "
        "uses many smaller chunks, and GraphRAG should be defended as structured "
        "evidence support rather than a single-score Recall improvement.",
        "",
        "## Advisory assistant boundary",
        "",
        evidence["advisory_boundary"],
        "",
        "## Next work plan",
        "",
        *next_work_lines,
        "",
        "## Reproducibility appendix",
        "",
        *reproducibility_lines,
        "",
        "## Evidence Sources",
        "",
        f"- Stage index: `{evidence['stage_index']['path']}` "
        f"({_present_marker(evidence['stage_index'])})",
        f"- README: `{evidence['readme']['path']}` ({_present_marker(evidence['readme'])})",
        f"- Goal: `{evidence['course_goal']['path']}` "
        f"({_present_marker(evidence['course_goal'])})",
        "- Configs: `configs/default.yaml`, `configs/ontology_generation.yaml`, "
        "`configs/extraction_profile.yaml`",
        "",
    ]
    return "\n".join(lines)


def build_project_report_prompt(evidence: dict[str, Any], draft: str) -> str:
    evidence_json = json.dumps(evidence, indent=2, sort_keys=True)
    return (
        "Write a complete Markdown project report for the Aviation Agentic AI project.\n\n"
        "Rules:\n"
        "- Use only the evidence pack and deterministic draft below.\n"
        "- Cite source file paths inline when making factual claims.\n"
        "- Do not invent completed experiments, metrics, models, or results.\n"
        "- If evidence is missing, write TBD or Not yet run.\n"
        "- Do not include API keys, tokens, secrets, or environment variable values.\n"
        "- Preserve the advisory boundary and do not claim the assistant replaces POH, "
        "checklists, ATC, instructor guidance, or pilot judgment.\n"
        "- Keep all required sections from the deterministic draft.\n\n"
        f"Deterministic draft:\n---\n{draft}\n---\n\n"
        f"Evidence pack JSON:\n---\n{evidence_json[:20000]}\n---\n"
    )


def _invoke_llm_project_report(prompt: str, temperature: float, max_tokens: int) -> str:
    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "AI project report generation requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    from aviation_agentic_ai.llm.providers import get_llm

    response = get_llm(temperature=temperature, max_tokens=max_tokens).invoke(
        [HumanMessage(content=prompt)]
    )
    return str(getattr(response, "content", response)).strip()


def write_project_report_sources(evidence: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_project_report_markdown(markdown: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return path


def write_project_report(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
    use_ai: bool = False,
    llm_runner: LLMRunner | None = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
) -> tuple[Path, Path, dict[str, Any]]:
    evidence = build_project_evidence_pack(
        project_root=project_root,
        stage_index_path=stage_index_path,
    )
    draft = build_project_report_draft(evidence)
    prompt = build_project_report_prompt(evidence, draft)
    if use_ai:
        runner = llm_runner or _invoke_llm_project_report
        markdown = runner(prompt, temperature, max_tokens)
    else:
        markdown = draft
    output = Path(output_dir)
    md_path = write_project_report_markdown(markdown, output / "project_report.md")
    sources_path = write_project_report_sources(evidence, output / "project_report_sources.json")
    return md_path, sources_path, {
        "used_ai": use_ai,
        "prompt": prompt,
        "markdown": markdown,
        "sources": evidence,
        "output_paths": {
            "markdown": project_relative_path(md_path),
            "sources": project_relative_path(sources_path),
        },
    }
