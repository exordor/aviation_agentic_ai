from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.thesis_dashboard import (
    write_thesis_experiment_dashboard,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _write_dashboard_fixture(root: Path) -> None:
    stages = root / "reports" / "stages"
    (root / "docs").mkdir(parents=True)
    (root / "reports" / "final").mkdir(parents=True)
    (root / "docs" / "thesis_positioning.md").write_text("layered evaluation\n", encoding="utf-8")
    (root / "docs" / "experiment_workflow.md").write_text("workflow\n", encoding="utf-8")
    _write_json(
        stages / "thesis_claims_review.json",
        {
            "claim_safety_matrix": [
                {
                    "claim": "Ontology constrains KG extraction.",
                    "safe_wording": "The task ontology constrains extraction.",
                    "evidence_files": ["curated_ontology_evaluation.json"],
                    "current_evidence": "Validation passes.",
                    "supported_strength": "strong",
                    "unsafe_wording_to_avoid": "The ontology fully models aviation.",
                }
            ]
        },
    )
    _write_json(stages / "evaluation_protocol_review.json", {"metric_catalog": []})
    _write_json(
        stages / "benchmark_v2_summary.json",
        {"metadata": {"labels_total": 120, "supported_total": 100, "no_answer_total": 20}},
    )
    retrieval_metrics = {
        "recall_at_5": 0.5,
        "recall_at_10": 0.6,
        "mrr_at_5": 0.3,
        "ndcg_at_10": 0.4,
        "context_recall": 0.7,
    }
    _write_json(
        stages / "retrieval_ablation_benchmark_v2.json",
        {
            "metadata": {"gold_labels_path": "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"},
            "scenarios": {
                "vector_hops2_v5_h8": {"aggregate": {"retrieval": retrieval_metrics}},
                "hybrid_hops2_v5_h8": {
                    "aggregate": {
                        "retrieval": retrieval_metrics,
                        "kg_evidence": {"evidence_coverage": 0.8},
                    }
                },
            },
        },
    )
    _write_json(
        stages / "graph_traversal_ablation_benchmark_v2.json",
        {
            "scenarios": {
                "hybrid_vector_traversal_guarded": {
                    "aggregate": {
                        "retrieval": {"recall_at_5": 0.45},
                        "graph_paths": {
                            "path_recall_at_5": 0.65,
                            "path_precision_at_5": 0.6,
                            "requires_model_review": True,
                            "human_review": False,
                        },
                    },
                    "failure_cases": [
                        {"failure_categories": ["graph_fusion_dilution", "kg_sparse_for_question"]}
                    ],
                },
                "traversal_graph_2_hop": {
                    "aggregate": {
                        "retrieval": {"recall_at_5": 0.1},
                        "graph_paths": {"path_coverage": 0.75},
                    },
                    "failure_cases": [],
                },
            }
        },
    )
    _write_json(
        stages / "sufficiency_evaluation.json",
        {
            "metadata": {"gold_labels_path": "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"},
            "metrics": {
                "abstention_accuracy": 1.0,
                "false_answer_rate": 0.0,
                "false_abstention_rate": 0.25,
                "risk_category_accuracy": 1.0,
            },
            "records": [
                {
                    "cq_id": "q1",
                    "expected_decision": "answer",
                    "decision": {"decision": "abstain"},
                }
            ],
        },
    )
    _write_json(
        stages / "kg_extraction_comparison.json",
        {
            "experiments": {
                "structure_aware": {
                    "provenance_complete_rate": 1.0,
                    "evidence_in_chunk_rate": 1.0,
                    "valid_triples": 448,
                    "unsupported_triple_count": 0,
                }
            }
        },
    )
    _write_json(stages / "curated_ontology_evaluation.json", {"structural_metrics": {}})
    _write_json(
        stages / "triple_semantic_review_sample.json",
        {
            "metadata": {"sample_size": 100, "semantic_correctness_claimed": False},
            "summary": {"reviewed": 0, "needs_review": 100},
        },
    )
    _write_json(stages / "answer_evaluation.json", {"aggregate": {}})
    _write_json(stages / "robustness_evaluation.json", {"aggregate": {}})
    _write_json(
        stages / "benchmark_review_pack.json",
        {"finding_counts": {"unnatural_machine_generated_wording": 3}},
    )
    _write_json(
        stages / "benchmark_llm_review.json",
        {
            "summary": {
                "items_total": 2,
                "llm_reviewed_total": 2,
                "review_status": "llm_reviewed_not_human_certified",
            }
        },
    )
    _write_json(
        stages / "triple_semantic_llm_review.json",
        {
            "summary": {
                "items_total": 2,
                "llm_reviewed_total": 2,
                "llm_evidence_support_rate": 1.0,
            }
        },
    )
    _write_json(
        stages / "graph_path_llm_review.json",
        {
            "summary": {
                "items_total": 2,
                "llm_reviewed_total": 2,
                "llm_path_relevance_rate": 1.0,
            }
        },
    )
    _write_json(
        stages / "answer_generation_benchmark_subset.json",
        {"metadata": {"answers_total": 3, "evaluation_status": "complete"}},
    )
    _write_json(
        stages / "answer_llm_judge.json",
        {
            "summary": {
                "items_total": 2,
                "llm_reviewed_total": 2,
                "llm_answer_correctness_rate": 1.0,
            }
        },
    )
    _write_json(
        stages / "llm_review_consistency.json",
        {"summary": {"agreement_rate": 1.0, "consistency_not_measured": False}},
    )


def test_thesis_dashboard_report_generation_and_matrices(tmp_path: Path) -> None:
    _write_dashboard_fixture(tmp_path)

    json_path, md_path, result = write_thesis_experiment_dashboard(
        tmp_path / "reports" / "stages",
        project_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    rq_names = {row["rq"] for row in result["rq_to_evidence_matrix"]}
    assert {
        "RQ1 ontology constraint",
        "RQ2 evidence traceability",
        "RQ3 graph evidence vs vector sufficiency",
        "RQ4 safety-aware abstention",
    } <= rq_names
    benchmark = next(
        row for row in result["dataset_usage_matrix"] if row["dataset"] == "benchmark v2 120"
    )
    assert benchmark["evidence_role"] == "main_thesis_benchmark"
    pilots = [
        row
        for row in result["dataset_usage_matrix"]
        if row["dataset"] in {"10-CQ pilot", "35-question expanded"}
    ]
    assert all(row["evidence_role"] == "pilot" for row in pilots)
    assert result["consistency_checks"]["primary_thesis_metrics_have_report_evidence"]
    assert result["consistency_checks"]["primary_thesis_metric_gaps"] == []
    assert result["consistency_checks"]["human_review_absent"]
    assert result["consistency_checks"]["benchmark_llm_review_available"]
    assert result["primary_results"]["llm_review_status"]["human_review"] is False
    assert result["consistency_checks"]["no_unsafe_claim_patterns"]


def test_workflow_runner_references_existing_cli_commands() -> None:
    makefile = Path("Makefile").read_text(encoding="utf-8")
    for command in [
        "uv run ruff check .",
        "uv run pytest",
        "uv run aviation-ai report thesis-claims",
        "uv run aviation-ai report evaluation-protocol",
        "uv run aviation-ai report retrieval-ablation --gold-labels",
        "uv run aviation-ai report graph-traversal-ablation --gold-labels",
        "uv run aviation-ai report sufficiency-eval",
        "uv run aviation-ai report triple-semantic-review --sample-size 100",
        "uv run aviation-ai report benchmark-llm-review",
        "uv run aviation-ai report triple-semantic-llm-review",
        "uv run aviation-ai report answer-llm-judge",
        "uv run aviation-ai report thesis-experiment-dashboard",
    ]:
        assert command in makefile
