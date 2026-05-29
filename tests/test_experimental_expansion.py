import json
from pathlib import Path

from aviation_agentic_ai.evaluation.gold import GoldLabel, load_gold_labels
from aviation_agentic_ai.evaluation.metrics import retrieval_metrics
from aviation_agentic_ai.ontology.cq import normalize_cq_artifact
from aviation_agentic_ai.reporting.answer_eval import write_answer_evaluation
from aviation_agentic_ai.reporting.kg_extraction_comparison import write_kg_extraction_comparison
from aviation_agentic_ai.reporting.retrieval_ablation import write_retrieval_ablation
from aviation_agentic_ai.reporting.robustness import write_robustness_evaluation


def _write_boundary_cqs(path: Path) -> None:
    cqs = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "What affects lift?",
                        "key_entities": ["angle of attack", "lift"],
                        "odp_hint": "Causal relation",
                        "expected_answer": "Angle of attack affects lift.",
                    }
                ],
                "1": [
                    {
                        "competency_question": "Can this chapter determine V-speeds?",
                        "key_entities": ["V-speeds"],
                        "odp_hint": "Unsupported",
                        "expected_answer": "The chapter does not provide aircraft-specific V-speeds.",
                    }
                ],
            }
        }
    )
    path.write_text(json.dumps(cqs) + "\n", encoding="utf-8")


def _write_gold(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "labels": [
                    {
                        "cq_id": "doc-p00-c29d89a530",
                        "question": "What affects lift?",
                        "question_type": "supported",
                        "source_document": "doc",
                        "source_page": 0,
                        "expected_chunk_ids": ["doc-p00-c00"],
                        "evidence_spans": [{"page": 0, "text": "Angle of attack affects lift."}],
                        "key_entities": ["angle of attack", "lift"],
                        "answer_key": "Angle of attack affects lift.",
                        "gold_level": "span",
                    },
                    {
                        "cq_id": "doc-p01-dbcda7dbf4",
                        "question": "Can this chapter determine V-speeds?",
                        "question_type": "insufficient_evidence",
                        "source_document": "doc",
                        "source_page": -1,
                        "expected_chunk_ids": [],
                        "evidence_spans": [],
                        "key_entities": ["V-speeds"],
                        "answer_key": "Current material is insufficient.",
                        "gold_level": "no_answer",
                        "expected_abstention": True,
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_gold_loader_supports_no_answer_labels(tmp_path: Path) -> None:
    gold_path = tmp_path / "gold.json"
    _write_gold(gold_path)

    labels = load_gold_labels(gold_path)

    assert labels["doc-p01-dbcda7dbf4"].gold_level == "no_answer"
    assert labels["doc-p01-dbcda7dbf4"].expected_abstention is True
    assert retrieval_metrics(
        [{"chunk_id": "doc-p01-c00", "page": 1, "text": "V-speeds"}],
        labels["doc-p01-dbcda7dbf4"],
    )["recall_at_5"] is False
    assert GoldLabel.from_dict(
        {
            "cq_id": "x",
            "source_page": -1,
            "expected_abstention": True,
        }
    ).gold_level == "no_answer"


def test_retrieval_ablation_uses_layered_metrics_and_manifest(tmp_path: Path) -> None:
    cq_path = tmp_path / "cqs.json"
    gold_path = tmp_path / "gold.json"
    _write_boundary_cqs(cq_path)
    _write_gold(gold_path)

    def fake_runner(question, mode, *_args, **kwargs):
        if "V-speeds" in question:
            return {"fused_chunks": [], "graph_triples": []}
        return {
            "fused_chunks": [
                {
                    "chunk_id": "doc-p00-c00",
                    "page": 0,
                    "text": "Angle of attack affects lift.",
                    "source": mode,
                }
            ],
            "graph_triples": [
                {
                    "triple_id": f"t-{mode}-{kwargs.get('graph_hops')}",
                    "chunk_id": "doc-p00-c00",
                    "page": 0,
                    "subject": "angle of attack",
                    "predicate": "affects",
                    "object": "lift",
                    "evidence_text": "Angle of attack affects lift.",
                }
            ],
        }

    json_path, md_path, result = write_retrieval_ablation(
        cq_path,
        tmp_path / "chunks.jsonl",
        tmp_path / "kg.jsonl",
        tmp_path / "chroma",
        tmp_path,
        gold_labels_path=gold_path,
        scenarios=(("vector", 2, 5, 8), ("hybrid", 1, 5, 8), ("hybrid", 3, 5, 8)),
        query_runner=fake_runner,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert "overall_score" not in result
    assert result["metadata"]["run_manifest"]["experiment_name"] == "retrieval_ablation"
    assert result["scenarios"]["hybrid_hops1_v5_h8"]["aggregate"]["retrieval"]["recall_at_5"] == 0.5
    assert result["scenarios"]["hybrid_hops3_v5_h8"]["aggregate"]["kg_evidence"]["evidence_coverage"] == 0.5
    assert result["metadata"]["cost_latency"]["questions_total"] == 2


def test_retrieval_ablation_loads_benchmark_v2_questions(tmp_path: Path) -> None:
    def fake_runner(question, *_args, **_kwargs):
        if "current" in question.lower() or "clearance" in question.lower():
            return {"fused_chunks": [], "graph_triples": []}
        return {
            "fused_chunks": [
                {
                    "chunk_id": "unmatched",
                    "page": -1,
                    "text": "unmatched",
                    "source": "vector",
                }
            ],
            "graph_triples": [],
        }

    _json_path, _md_path, result = write_retrieval_ablation(
        tmp_path / "unused_boundary.json",
        tmp_path / "chunks.jsonl",
        tmp_path / "kg.jsonl",
        tmp_path / "chroma",
        tmp_path,
        gold_labels_path=Path("data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"),
        scenarios=(("vector", 2, 5, 8),),
        query_runner=fake_runner,
    )

    assert result["metadata"]["questions_total"] == 120
    assert result["metadata"]["label_breakdown"]["supported_total"] == 100
    assert result["metadata"]["label_breakdown"]["no_answer_total"] == 20
    assert len(result["scenarios"]["vector_hops2_v5_h8"]["records"]) == 120


def test_kg_extraction_comparison_counts_quality_and_duplicates(tmp_path: Path) -> None:
    fixed = tmp_path / "fixed.kg.jsonl"
    structure = tmp_path / "structure.kg.jsonl"
    fixed.write_text(
        json.dumps(
            {
                "triple_id": "t1",
                "subject": "angle of attack",
                "predicate": "affects",
                "object": "lift",
                "subject_class": "Cl_AngleOfAttack",
                "object_class": "Cl_Lift",
                "chunk_id": "doc-p00-c00",
                "page": 0,
                "evidence_text": "Angle of attack affects lift.",
                "model": "mock",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    structure.write_text(fixed.read_text(encoding="utf-8") * 2, encoding="utf-8")
    gold_path = tmp_path / "gold.json"
    _write_gold(gold_path)

    json_path, md_path, result = write_kg_extraction_comparison(
        tmp_path,
        fixed_kg_path=fixed,
        structure_aware_kg_path=structure,
        gold_labels_path=gold_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["experiments"]["fixed_window"]["valid_triples"] == 1
    assert result["experiments"]["structure_aware"]["duplicate_triple_count"] == 1
    assert result["experiments"]["structure_aware"]["key_entity_coverage"] == 0.5


def test_answer_and_robustness_reports_handle_abstention(tmp_path: Path) -> None:
    gold_path = tmp_path / "gold.json"
    hybrid_path = tmp_path / "hybrid.json"
    robustness_path = tmp_path / "robustness.json"
    _write_gold(gold_path)
    hybrid_path.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "cq_id": "doc-p00-c29d89a530",
                        "question": "What affects lift?",
                        "results": {
                            "hybrid": {
                                "fused_chunks": [{"chunk_id": "doc-p00-c00", "page": 0}],
                                "graph_triples": [{"triple_id": "t1", "page": 0}],
                                "answer": "Angle of attack affects lift. Citations: doc-p00-c00, t1, page 0",
                            }
                        },
                    },
                    {
                        "cq_id": "doc-p01-dbcda7dbf4",
                        "question": "Can this chapter determine V-speeds?",
                        "results": {
                            "hybrid": {
                                "fused_chunks": [],
                                "graph_triples": [],
                                "answer": "The current PHAK Chapter 4 evidence is insufficient to determine this.",
                            }
                        },
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    robustness_path.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "case_id": "r1",
                        "base_cq_id": "doc-p00-c29d89a530",
                        "question": "Which factor changes lift?",
                        "case_type": "paraphrase",
                        "expected_chunk_ids": ["doc-p00-c00"],
                    },
                    {
                        "case_id": "r2",
                        "base_cq_id": "doc-p01-dbcda7dbf4",
                        "question": "What is the aircraft Vx?",
                        "case_type": "unsupported",
                        "expected_abstention": True,
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    answer_json, answer_md, answer_result = write_answer_evaluation(
        tmp_path,
        gold_labels_path=gold_path,
        hybrid_report_path=hybrid_path,
    )
    assert answer_json.exists()
    assert answer_md.exists()
    assert answer_result["aggregate"]["hybrid"]["abstention_correctness"] == 1.0
    assert answer_result["aggregate"]["hybrid"]["advisory_boundary_violation_count"] == 0

    def fake_runner(question, *_args, **_kwargs):
        if "Vx" in question:
            return {"fused_chunks": [], "graph_triples": [], "answer": "Insufficient evidence."}
        return {
            "fused_chunks": [{"chunk_id": "doc-p00-c00", "page": 0}],
            "graph_triples": [{"triple_id": "t1", "page": 0}],
            "answer": "Angle of attack affects lift. Citations: doc-p00-c00, t1",
        }

    robust_json, robust_md, robust_result = write_robustness_evaluation(
        robustness_path,
        tmp_path / "chunks.jsonl",
        tmp_path / "kg.jsonl",
        tmp_path / "chroma",
        tmp_path,
        query_runner=fake_runner,
    )
    assert robust_json.exists()
    assert robust_md.exists()
    assert robust_result["aggregate"]["retrieval_stability"] == 1.0
    assert robust_result["aggregate"]["abstention_correctness"] == 1.0
