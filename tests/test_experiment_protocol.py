import json
from datetime import UTC, datetime
from pathlib import Path

from aviation_agentic_ai.evaluation.document_metadata import (
    SectionRecord,
    document_metadata_from_pdf,
)
from aviation_agentic_ai.evaluation.gold import (
    GoldLabel,
    GoldLabelReadError,
    gold_labels_for_questions,
    load_questions_and_gold_labels,
    load_gold_labels,
)
from aviation_agentic_ai.evaluation.metrics import (
    answer_metrics,
    kg_evidence_metrics,
    retrieval_metrics,
)
from aviation_agentic_ai.evaluation.protocol import build_run_manifest, safe_llm_metadata


def test_run_manifest_records_protocol_without_secret_fields(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("MODEL_NAME", "gpt-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")

    manifest = build_run_manifest(
        "hybrid_rag",
        parameters={"vector_top_k": 5},
        artifacts={"chunks_path": tmp_path / "chunks.jsonl"},
        rebuild_policy={"chunks": False, "indexes": True, "kg": False},
        collection_name="test_collection",
        chunking_strategy="structure_aware",
        command="aviation-ai report hybrid-rag",
        created_at=datetime(2026, 5, 18, 12, 0, tzinfo=UTC),
    )

    assert manifest["run_id"] == "hybrid-rag-20260518T120000Z"
    assert manifest["rebuild_policy"] == {"chunks": False, "indexes": True, "kg": False}
    assert manifest["collection_name"] == "test_collection"
    assert manifest["chunking_strategy"] == "structure_aware"
    assert manifest["llm"] == {"provider": "openai", "model": "gpt-test"}
    assert "OPENAI_API_KEY" not in json.dumps(manifest)
    assert "sk-secret" not in json.dumps(manifest)


def test_safe_llm_metadata_uses_central_environment_loader(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        "aviation_agentic_ai.evaluation.protocol.load_environment",
        lambda: calls.append("loaded"),
    )
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("MODEL_NAME", "deepseek-test")

    assert safe_llm_metadata() == {"provider": "deepseek", "model": "deepseek-test"}
    assert calls == ["loaded"]


def test_load_questions_and_gold_labels_uses_full_gold_label_questions(
    tmp_path: Path,
) -> None:
    gold_path = tmp_path / "gold.json"
    gold_path.write_text(
        json.dumps(
            {
                "labels": [
                    {
                        "cq_id": "q1",
                        "question": "What is lift?",
                        "question_type": "concept_definition",
                        "answer_key": "Lift is an upward force.",
                        "source_document": "doc",
                        "source_page": 1,
                        "key_entities": ["lift"],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    questions, labels = load_questions_and_gold_labels(
        tmp_path / "missing_boundary_cqs.json",
        gold_path,
    )

    assert list(labels) == ["q1"]
    assert questions == [
        {
            "id": "q1",
            "competency_question": "What is lift?",
            "source_document": "doc",
            "source_page": 1,
            "key_entities": ["lift"],
            "expected_answer": "Lift is an upward force.",
            "cq_type": "concept_definition",
        }
    ]


def test_load_questions_and_gold_labels_reuses_preloaded_gold_for_cq_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[Path] = []
    overlay_label = GoldLabel(cq_id="q1", source_document="gold-doc", source_page=7)

    def load_gold_once(path: str | Path) -> dict[str, GoldLabel]:
        calls.append(Path(path))
        return {"q1": overlay_label}

    monkeypatch.setattr(
        "aviation_agentic_ai.evaluation.gold.load_gold_labels",
        load_gold_once,
    )
    monkeypatch.setattr(
        "aviation_agentic_ai.evaluation.gold.load_boundary_questions",
        lambda _path: [
            {
                "id": "q1",
                "competency_question": "What is lift?",
                "source_document": "cq-doc",
                "source_page": 1,
            }
        ],
    )

    questions, labels = load_questions_and_gold_labels(
        tmp_path / "boundary.json",
        tmp_path / "gold.json",
    )

    assert len(calls) == 1
    assert questions[0]["id"] == "q1"
    assert labels["q1"] == overlay_label


def test_document_and_section_metadata_schema() -> None:
    document = document_metadata_from_pdf(
        "data/raw/06_phak_ch4_0.pdf",
        title="PHAK Chapter 4",
        chapter="4",
        page_start=0,
        page_end=10,
    )
    section = SectionRecord(
        section_id="phak-ch4-aerodynamics",
        title="Aerodynamics",
        level=1,
        page_start=0,
        page_end=10,
    )

    assert document.to_dict()["source_path"] == "data/raw/06_phak_ch4_0.pdf"
    assert document.to_dict()["chapter"] == "4"
    assert section.to_dict()["parent_id"] is None


def test_gold_labels_support_page_chunk_and_span_levels(tmp_path: Path) -> None:
    labels_path = tmp_path / "gold.jsonl"
    labels_path.write_text(
        "\n".join(
            [
                json.dumps({"cq_id": "q1", "source_document": "doc", "source_page": 1}),
                json.dumps(
                    {
                        "cq_id": "q2",
                        "source_document": "doc",
                        "source_page": 2,
                        "expected_chunk_ids": ["doc-p02-c00"],
                    }
                ),
                json.dumps(
                    {
                        "cq_id": "q3",
                        "source_document": "doc",
                        "source_page": 3,
                        "tags": ["span", "internal_project_gold_not_human_certified"],
                        "review": {"status": "internal_project_gold_not_human_certified"},
                        "evidence_spans": [{"page": 3, "text": "stall warning"}],
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    labels = load_gold_labels(labels_path)

    assert labels["q1"].gold_level == "page"
    assert labels["q2"].gold_level == "chunk"
    assert labels["q3"].gold_level == "span"
    assert labels["q3"].evidence_spans[0].text == "stall warning"


def test_gold_jsonl_errors_include_line_number(tmp_path: Path) -> None:
    labels_path = tmp_path / "gold.jsonl"
    labels_path.write_text(
        json.dumps({"cq_id": "q1", "source_document": "doc", "source_page": 1})
        + "\nnot-json\n",
        encoding="utf-8",
    )

    try:
        load_gold_labels(labels_path)
    except GoldLabelReadError as exc:
        message = str(exc)
    else:  # pragma: no cover - assertion guard.
        raise AssertionError("Expected GoldLabelReadError")

    assert "gold.jsonl" in message
    assert "line 2" in message


def test_gold_record_errors_include_label_index(tmp_path: Path) -> None:
    labels_path = tmp_path / "gold.json"
    labels_path.write_text(
        json.dumps(
            {
                "labels": [
                    {
                        "cq_id": "q1",
                        "source_document": "doc",
                        "source_page": 1,
                        "evidence_spans": [{"text": "missing page"}],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        load_gold_labels(labels_path)
    except GoldLabelReadError as exc:
        message = str(exc)
    else:  # pragma: no cover - assertion guard.
        raise AssertionError("Expected GoldLabelReadError")

    assert "gold.json" in message
    assert "label 1" in message


def test_gold_labels_fall_back_to_source_page_from_cqs() -> None:
    questions = [
        {
            "id": "q1",
            "source_document": "doc",
            "source_page": 4,
            "key_entities": ["lift"],
            "expected_answer": "Lift answer.",
        }
    ]

    labels = gold_labels_for_questions(questions)

    assert labels["q1"] == GoldLabel(
        cq_id="q1",
        source_document="doc",
        source_page=4,
        key_entities=("lift",),
        answer_key="Lift answer.",
        gold_level="page",
    )


def test_layered_metrics_handle_retrieval_kg_and_answer_cases() -> None:
    retrieval = retrieval_metrics(
        [
            {"chunk_id": "wrong", "page": 1, "text": "other"},
            {"chunk_id": "doc-p02-c00", "page": 2, "text": "Angle of attack affects lift."},
        ],
        GoldLabel(
            cq_id="q1",
            source_document="doc",
            source_page=2,
            expected_chunk_ids=("doc-p02-c00",),
            gold_level="chunk",
        ),
    )
    kg = kg_evidence_metrics(
        [
            {
                "triple_id": "t1",
                "chunk_id": "doc-p02-c00",
                "page": 2,
                "subject": "angle of attack",
                "predicate": "affects",
                "object": "lift",
                "evidence_text": "Angle of attack affects lift.",
            }
        ],
        ["lift"],
    )
    answer = answer_metrics(
        {
            "answer": "Angle of attack affects lift. Citations: doc-p02-c00, t1",
            "fused_chunks": [{"chunk_id": "doc-p02-c00", "page": 2}],
            "graph_triples": [{"triple_id": "t1", "chunk_id": "doc-p02-c00", "page": 2}],
        }
    )

    assert retrieval["recall_at_5"]
    assert retrieval["first_relevant_rank"] == 2
    assert kg["evidence_coverage"]
    assert kg["provenance_complete_rate"] == 1.0
    assert answer["citation_completeness"]
    assert answer["valid_chunk_citation"]
    assert answer["valid_triple_citation"]
