import json
from pathlib import Path

from aviation_agentic_ai.reporting.graphrag_review import write_graphrag_review


def _hybrid_report() -> dict:
    return {
        "metadata": {"questions_total": 2, "chunking_strategy": "fixed_window"},
        "aggregate": {
            "vector": {
                "retrieval": {
                    "recall_at_5": 1.0,
                    "mrr_at_5": 0.75,
                    "context_precision_at_5": 0.4,
                },
                "kg_evidence": {"evidence_coverage": 0.0},
                "llm_answer": {"citation_completeness": 1.0},
            },
            "graph": {
                "retrieval": {
                    "recall_at_5": 0.8,
                    "mrr_at_5": 0.65,
                    "context_precision_at_5": 0.49,
                },
                "kg_evidence": {"evidence_coverage": 0.9},
                "llm_answer": {"citation_completeness": 1.0},
            },
            "hybrid": {
                "retrieval": {
                    "recall_at_5": 0.9,
                    "mrr_at_5": 0.73,
                    "context_precision_at_5": 0.4,
                },
                "kg_evidence": {"evidence_coverage": 0.9},
                "llm_answer": {"citation_completeness": 1.0},
            },
            "hybrid_lift": {
                "vs_vector_recall_at_5": -0.1,
                "vs_graph_recall_at_5": 0.1,
            },
        },
        "records": [
            {
                "cq_id": "newton",
                "question": "How should Newton laws be represented?",
                "source_page": 5,
                "results": {
                    "hybrid": {
                        "metrics": {
                            "retrieval": {"recall_at_5": False},
                            "kg_evidence": {"evidence_coverage": True},
                            "llm_answer": {"citation_completeness": True},
                        }
                    }
                },
            },
            {
                "cq_id": "wingtip",
                "question": "How should wingtip vortex be modeled?",
                "source_page": 8,
                "results": {
                    "hybrid": {
                        "metrics": {
                            "retrieval": {"recall_at_5": True},
                            "kg_evidence": {"evidence_coverage": False},
                            "llm_answer": {"citation_completeness": True},
                        }
                    }
                },
            },
        ],
    }


def test_graphrag_review_separates_metrics_and_explains_failures(tmp_path: Path) -> None:
    chunking_path = tmp_path / "chunking_comparison.json"
    fixed_path = tmp_path / "hybrid_rag_experiment.json"
    chunking_path.write_text(
        json.dumps(
            {
                "ranking": [{"strategy": "structure_aware"}],
                "strategies": {
                    "fixed_window": {"aggregate": {}},
                    "structure_aware": {"aggregate": {}},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    fixed_path.write_text(json.dumps(_hybrid_report()) + "\n", encoding="utf-8")

    json_path, md_path, result = write_graphrag_review(
        chunking_path,
        fixed_path,
        tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert "overall" not in result
    assert result["experiments"]["fixed_window"]["vector"]["retrieval"]["recall_at_5"] == 1.0
    assert result["experiments"]["fixed_window"]["graph"]["kg_evidence"]["evidence_coverage"] == 0.9
    assert result["experiments"]["fixed_window"]["hybrid_lift"] == {
        "vs_vector_recall_at_5": -0.1,
        "vs_graph_recall_at_5": 0.1,
    }
    assert [item["failure_type"] for item in result["experiments"]["fixed_window"]["failure_cases"]] == [
        "page_recall_miss_but_kg_evidence_found",
        "retrieval_hit_but_kg_evidence_missing",
    ]
    markdown = md_path.read_text(encoding="utf-8")
    assert "GraphRAG's current value is KG evidence coverage" in markdown
    assert "source_page" in markdown
