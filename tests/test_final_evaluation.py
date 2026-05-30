from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.final_evaluation import build_final_evaluation_review


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def _hybrid_report(cq_id: str = "cq-1") -> dict:
    return {
        "aggregate": {
            "hybrid": {
                "retrieval": {"recall_at_5": 1.0},
                "kg_evidence": {"evidence_coverage": 1.0},
            }
        },
        "records": [
            {
                "cq_id": cq_id,
                "question": "What affects lift?",
                "source_page": 7,
                "results": {
                    "hybrid": {
                        "metrics": {
                            "retrieval": {
                                "recall_at_5": True,
                                "retrieved_source_pages": [7],
                                "retrieved_chunk_ids": ["chunk-1"],
                            }
                        }
                    }
                },
            }
        ],
    }


def _evidence_eval() -> dict:
    mode_aggregate = {
        "chunk_recall_at_5": 1.0,
        "span_hit_rate": 1.0,
        "citation_validity": 1.0,
        "answer_support_distribution": {"supported": 1},
    }
    mode_record = {
        "answer_support": "supported",
        "chunk": {"chunk_recall_at_5": True},
        "span": {"span_hit": True},
        "kg_evidence": {"key_entity_coverage": True, "evidence_coverage": True},
        "citation": {"citation_completeness": True},
    }
    return {
        "metadata": {"scoring_policy": "layered_metrics_no_mixed_overall_score"},
        "experiments": {
            experiment: {
                "aggregate": {
                    "vector": mode_aggregate,
                    "graph": mode_aggregate,
                    "hybrid": mode_aggregate,
                },
                "records": [
                    {
                        "cq_id": "cq-1",
                        "question": "What affects lift?",
                        "gold_level": "span",
                        "source_page": 7,
                        "modes": {
                            "vector": mode_record,
                            "graph": mode_record,
                            "hybrid": mode_record,
                        },
                    }
                ],
            }
            for experiment in ("fixed_window", "structure_aware")
        },
    }


def test_final_evaluation_review_keeps_layered_metrics(tmp_path: Path) -> None:
    gold = _write_json(
        tmp_path / "gold.json",
        {
            "metadata": {
                "review_required": False,
                "review_status": "internal_project_gold_not_human_certified",
                "human_review": False,
            },
            "labels": [
                {
                    "cq_id": "cq-1",
                    "source_page": 7,
                    "gold_level": "span",
                    "expected_chunk_ids": ["chunk-1"],
                    "evidence_spans": [{"page": 7, "text": "lift"}],
                    "key_entities": ["lift"],
                }
            ],
        },
    )
    chunking = _write_json(
        tmp_path / "chunking.json",
        {
            "ranking": [
                {
                    "strategy": "structure_aware",
                    "recall_at_5": 1.0,
                    "mrr_at_5": 1.0,
                    "context_precision_at_5": 1.0,
                }
            ],
            "strategies": {
                "structure_aware": {
                    "aggregate": {"recall_at_5": 1.0},
                    "chunk_stats": {"chunk_count": 10},
                    "explanation": "Preserves section boundaries.",
                },
                "fixed_window": {"aggregate": {"recall_at_5": 1.0}},
            },
        },
    )
    fixed = _write_json(tmp_path / "fixed.json", _hybrid_report())
    structure = _write_json(tmp_path / "structure.json", _hybrid_report())
    evidence = _write_json(tmp_path / "evidence.json", _evidence_eval())
    review = _write_json(tmp_path / "review.json", {"recommendations": ["Use structure-aware."]})

    result = build_final_evaluation_review(
        gold_labels_path=gold,
        chunking_comparison_path=chunking,
        fixed_hybrid_path=fixed,
        structure_aware_hybrid_path=structure,
        evidence_eval_path=evidence,
        graphrag_review_path=review,
    )

    assert result["metadata"]["scoring_policy"] == "layered_metrics_no_mixed_overall_score"
    assert result["gold_label_review"]["review_required"] is False
    assert result["gold_label_review"]["human_review"] is False
    assert result["default_strategy_decision"]["recommended_default"] == "structure_aware"
    assert "overall_score" not in result
    assert "overall_score" not in result["default_strategy_decision"]
    assert result["citation_completeness"]["structure_aware"]["hybrid"]["citation_validity"] == 1.0


def test_cli_report_final_evaluation_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_report_evaluation

    def fake_writer(output_dir, **kwargs):
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        json_path = output / f"{kwargs['report_name']}.json"
        md_path = output / f"{kwargs['report_name']}.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# Final Evaluation\n", encoding="utf-8")
        return json_path, md_path, {
            "default_strategy_decision": {"recommended_default": "structure_aware"}
        }

    monkeypatch.setattr(cli_report_evaluation, "write_final_evaluation_review", fake_writer)
    result = CliRunner().invoke(
        main,
        ["report", "final-evaluation", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert "Final evaluation review complete" in result.output
