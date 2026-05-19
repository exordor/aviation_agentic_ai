import json
from pathlib import Path

from aviation_agentic_ai.ontology.cq import normalize_cq_artifact
from aviation_agentic_ai.reporting.hybrid_rag import write_hybrid_rag_experiment


def test_hybrid_rag_report_calculates_metrics(tmp_path: Path) -> None:
    cqs = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "What affects lift?",
                        "key_entities": ["lift"],
                        "odp_hint": "Causal relation",
                        "expected_answer": "Angle of attack affects lift.",
                    }
                ]
            }
        }
    )
    cq_path = tmp_path / "boundary.json"
    cq_path.write_text(json.dumps(cqs) + "\n", encoding="utf-8")

    def fake_query_runner(question, mode, *_args, **_kwargs):
        return {
            "question": question,
            "mode": mode,
            "fused_chunks": [
                {
                    "chunk_id": "doc-p00-c00",
                    "page": 0,
                    "source": mode,
                    "text": "Angle of attack affects lift.",
                }
            ],
            "graph_triples": [
                {
                    "triple_id": "t1",
                    "chunk_id": "doc-p00-c00",
                    "page": 0,
                    "subject": "angle of attack",
                    "predicate": "affects",
                    "object": "lift",
                    "subject_class": "Cl_AngleOfAttack",
                    "object_class": "Cl_Lift",
                    "evidence_text": "Angle of attack affects lift.",
                }
            ],
            "answer": "Angle of attack affects lift. Citations: doc-p00-c00, t1",
        }

    json_path, md_path, result = write_hybrid_rag_experiment(
        cq_path,
        tmp_path / "chunks.jsonl",
        tmp_path / "kg.jsonl",
        tmp_path / "chroma",
        tmp_path,
        query_runner=fake_query_runner,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["aggregate"]["hybrid"]["recall_at_5"] == 1.0
    assert result["aggregate"]["hybrid"]["citation_completeness"] == 1.0
    assert result["aggregate"]["hybrid"]["retrieval"]["recall_at_5"] == 1.0
    assert result["aggregate"]["hybrid"]["kg_evidence"]["evidence_coverage"] == 1.0
    assert result["aggregate"]["hybrid"]["llm_answer"]["citation_completeness"] == 1.0
    assert result["metadata"]["run_manifest"]["collection_name"] == "phak_ch4_chunks"
    assert result["metadata"]["run_manifest"]["rebuild_policy"] == {
        "chunks": False,
        "indexes": False,
        "kg": False,
    }
    assert "learning and decision-support" in result["metadata"]["advisory_boundary"]
    assert result["records"][0]["gold"]["gold_level"] == "page"


def test_hybrid_rag_report_supports_custom_report_name(tmp_path: Path) -> None:
    cqs = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "What affects lift?",
                        "key_entities": ["lift"],
                        "odp_hint": "Causal relation",
                        "expected_answer": "Angle of attack affects lift.",
                    }
                ]
            }
        }
    )
    cq_path = tmp_path / "boundary.json"
    cq_path.write_text(json.dumps(cqs) + "\n", encoding="utf-8")

    def fake_query_runner(question, mode, *_args, **_kwargs):
        return {
            "question": question,
            "mode": mode,
            "fused_chunks": [{"chunk_id": "doc-p00-c00", "page": 0, "source": mode}],
            "graph_triples": [],
            "answer": "Answer. Citations: doc-p00-c00",
        }

    json_path, md_path, _result = write_hybrid_rag_experiment(
        cq_path,
        tmp_path / "chunks.jsonl",
        tmp_path / "kg.jsonl",
        tmp_path / "chroma",
        tmp_path,
        report_name="hybrid_rag_structure_aware",
        query_runner=fake_query_runner,
    )

    assert json_path.name == "hybrid_rag_structure_aware.json"
    assert md_path.name == "hybrid_rag_structure_aware.md"
    assert not (tmp_path / "hybrid_rag_experiment.json").exists()


def test_hybrid_rag_report_can_use_questions_from_gold_labels(tmp_path: Path) -> None:
    cq_path = tmp_path / "boundary.json"
    cq_path.write_text(json.dumps({"doc": {}}) + "\n", encoding="utf-8")
    gold_path = tmp_path / "expanded.gold.json"
    gold_path.write_text(
        json.dumps(
            {
                "labels": [
                    {
                        "cq_id": "expanded-1",
                        "question": "What affects lift?",
                        "question_type": "supported",
                        "source_document": "doc",
                        "source_page": 0,
                        "expected_chunk_ids": ["doc-p00-c00"],
                        "key_entities": ["lift"],
                        "answer_key": "Angle of attack affects lift.",
                        "gold_level": "chunk",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_query_runner(question, mode, *_args, **_kwargs):
        return {
            "question": question,
            "mode": mode,
            "fused_chunks": [{"chunk_id": "doc-p00-c00", "page": 0, "source": mode}],
            "graph_triples": [],
            "answer": "Answer. Citations: doc-p00-c00",
        }

    _json_path, _md_path, result = write_hybrid_rag_experiment(
        cq_path,
        tmp_path / "chunks.jsonl",
        tmp_path / "kg.jsonl",
        tmp_path / "chroma",
        tmp_path,
        gold_labels_path=gold_path,
        query_runner=fake_query_runner,
    )

    assert result["metadata"]["questions_total"] == 1
    assert result["records"][0]["cq_id"] == "expanded-1"
    assert result["records"][0]["gold"]["gold_level"] == "chunk"
