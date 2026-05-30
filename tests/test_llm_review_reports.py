from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType

from aviation_agentic_ai.evaluation import llm_review
from aviation_agentic_ai.evaluation.llm_review import (
    LLMReviewMetadata,
    extract_json_object,
    input_hash,
    llm_runtime_available,
    not_run_result,
)
from aviation_agentic_ai.reporting.llm_review_reports import (
    write_answer_generation_benchmark_subset,
    write_answer_llm_judge,
    write_benchmark_llm_review,
    write_graph_path_llm_review,
    write_llm_review_consistency,
    write_triple_semantic_llm_review,
)


def _runner(_prompt: str, _temperature: float, _max_tokens: int) -> str:
    return json.dumps(
        {
            "decision": "keep",
            "confidence": 0.8,
            "scores": {
                "subject_correct": 1,
                "predicate_correct": 1,
                "object_correct": 1,
                "direction_correct": 1,
                "evidence_supports_triple": 1,
                "path_relevant_to_question": 1,
                "path_is_explanatory": 1,
                "path_is_misleading": 0,
                "answer_correctness": 2,
                "answer_relevance": 2,
                "faithfulness_to_retrieved_context": 2,
                "citation_support": 2,
            },
            "recommended_action": "keep",
            "cited_source_fields": ["evidence_spans"],
            "uncertainty_flags": [],
            "requires_human_review": False,
            "rationale": "Supported by supplied evidence.",
        }
    )


def _gold_payload() -> dict:
    return {
        "label_set": "test",
        "labels": [
            {
                "cq_id": "q1",
                "question": "What is lift?",
                "question_type": "concept_definition",
                "answer_key": "Lift is an upward force.",
                "source_document": "doc",
                "source_page": 1,
                "expected_abstention": False,
                "expected_chunk_ids": ["c1"],
                "evidence_spans": [{"page": 1, "text": "Lift is an upward force."}],
                "key_entities": ["lift"],
                "gold_level": "span",
            }
        ],
    }


def test_llm_review_schema_rejects_certification_flags() -> None:
    metadata = LLMReviewMetadata(
        reviewer_model="test-model",
        prompt_version="v1",
        input_hash=input_hash({"x": 1}),
        review_run_id="run",
        temperature=0.0,
        reviewer_role="strict_evidence_reviewer",
    )
    assert metadata.human_review is False
    assert extract_json_object("```json\n{\"decision\":\"keep\"}\n```")["decision"] == "keep"
    result = not_run_result(
        item_id="q1",
        item_type="benchmark_label",
        review_kind="test",
        prompt_version="v1",
        input_payload={"x": 1},
        reviewer_role="strict_evidence_reviewer",
        reason="disabled",
    )
    assert result.metadata.review_status == "llm_review_not_run"
    assert result.human_review is False


def test_llm_runtime_available_uses_central_environment_loader(monkeypatch) -> None:
    calls: list[str] = []

    def load_environment() -> bool:
        calls.append("loaded")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-from-loader")
        return True

    monkeypatch.setattr(llm_review, "load_environment", load_environment)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setitem(sys.modules, "langchain_openai", ModuleType("langchain_openai"))

    assert llm_runtime_available() is True
    assert calls == ["loaded"]


def test_benchmark_llm_review_marks_model_based_not_human(tmp_path: Path) -> None:
    gold = tmp_path / "gold.json"
    gold.write_text(json.dumps(_gold_payload()) + "\n", encoding="utf-8")

    json_path, md_path, result = write_benchmark_llm_review(
        gold,
        tmp_path,
        max_items=1,
        runner=_runner,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["summary"]["llm_reviewed_total"] == 2
    record = result["records"][0]
    assert record["human_review"] is False
    assert record["external_expert_certified"] is False
    assert record["aviation_expert_certified"] is False
    assert record["metadata"]["score_method"] == "llm_judge"


def test_triple_graph_answer_llm_reports_are_not_expert_certified(tmp_path: Path) -> None:
    triple_sample = tmp_path / "triple_semantic_review_sample.json"
    triple_sample.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "triple": {
                            "triple_id": "t1",
                            "subject": "lift",
                            "predicate": "affects",
                            "object": "drag",
                            "evidence_text": "Lift affects drag.",
                        }
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    graph_report = tmp_path / "graph.json"
    graph_report.write_text(
        json.dumps(
            {
                "scenarios": {
                    "s1": {
                        "records": [
                            {
                                "cq_id": "q1",
                                "question": "How does lift affect drag?",
                                "gold": {"question_type": "relation_causal"},
                                "graph_paths": [{"path_id": "p1"}],
                                "hits": [],
                                "metrics": {"graph_paths": {"path_recall_at_5": 1}},
                            }
                        ],
                        "failure_cases": [
                            {
                                "cq_id": "q1",
                                "failure_categories": ["graph_fusion_dilution"],
                            }
                        ],
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    answer_generation = tmp_path / "answers.json"
    answer_generation.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "cq_id": "q1",
                        "method": "hybrid",
                        "answer_status": "generated",
                        "answer": "Lift affects drag. Citations: c1",
                        "gold": _gold_payload()["labels"][0],
                        "retrieval": {"fused_chunks": [{"chunk_id": "c1"}]},
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    _triple_json, _triple_md, triple = write_triple_semantic_llm_review(
        triple_sample,
        tmp_path,
        max_items=1,
        runner=_runner,
    )
    _graph_json, _graph_md, graph = write_graph_path_llm_review(
        graph_report,
        tmp_path,
        max_items=1,
        runner=_runner,
    )
    _answer_json, _answer_md, answer = write_answer_llm_judge(
        answer_generation,
        tmp_path,
        max_items=1,
        runner=_runner,
    )

    for result in (triple, graph, answer):
        assert result["metadata"]["human_review"] is False
        assert result["metadata"]["external_expert_certified"] is False
        assert result["summary"]["score_method"] == "llm_judge"
    assert answer["summary"]["llm_answer_correctness_rate"] == 1.0


def test_answer_generation_not_run_when_llm_unavailable(tmp_path: Path) -> None:
    gold = tmp_path / "gold.json"
    gold.write_text(json.dumps(_gold_payload()) + "\n", encoding="utf-8")

    _json_path, _md_path, result = write_answer_generation_benchmark_subset(
        gold,
        tmp_path / "chunks.jsonl",
        tmp_path / "kg.jsonl",
        tmp_path / "index",
        tmp_path,
        max_questions=1,
        run_llm=False,
    )

    assert result["metadata"]["answers_total"] == 0
    assert result["records"][0]["answer_status"] == "not_run"
    assert result["metadata"]["human_review"] is False


def test_llm_review_consistency_reports_one_pass_as_not_measured(tmp_path: Path) -> None:
    empty = {"records": [{"item_id": "q1", "decision": {"recommended_action": "keep"}}]}
    paths = []
    for name in ("benchmark", "triple", "graph", "answer"):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(empty) + "\n", encoding="utf-8")
        paths.append(path)

    _json_path, _md_path, result = write_llm_review_consistency(
        tmp_path,
        benchmark_review_path=paths[0],
        triple_review_path=paths[1],
        graph_path_review_path=paths[2],
        answer_judge_path=paths[3],
    )

    assert result["summary"]["consistency_not_measured"] is True
    assert result["metadata"]["human_review"] is False
