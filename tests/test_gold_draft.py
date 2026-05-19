import json
from pathlib import Path

from aviation_agentic_ai.chunking.chunks import SourceChunk, write_chunks_jsonl
from aviation_agentic_ai.evaluation.gold import load_gold_labels
from aviation_agentic_ai.evaluation.gold_draft import build_gold_draft
from aviation_agentic_ai.ontology.cq import normalize_cq_artifact


def test_build_gold_draft_creates_chunk_and_span_labels(tmp_path: Path) -> None:
    cq_path = tmp_path / "boundary.json"
    cqs = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "How does angle of attack affect lift?",
                        "key_entities": ["angle of attack", "lift"],
                        "odp_hint": "Causal relation",
                        "expected_answer": "Angle of attack affects lift.",
                    }
                ]
            }
        }
    )
    cq_path.write_text(json.dumps(cqs) + "\n", encoding="utf-8")
    chunks_path = tmp_path / "chunks.jsonl"
    write_chunks_jsonl(
        [
            SourceChunk(
                chunk_id="doc-fixed-p00-c00",
                source_document="doc",
                source_path="doc.pdf",
                page=0,
                chunk_index=0,
                char_start=0,
                char_end=48,
                text="Angle of attack affects lift. Other sentence.",
                strategy="fixed_window",
            )
        ],
        chunks_path,
    )

    payload = build_gold_draft(cq_path, [chunks_path], output_path=tmp_path / "gold.json")
    labels = load_gold_labels(tmp_path / "gold.json")

    label = labels[payload["labels"][0]["cq_id"]]
    assert label.gold_level == "span"
    assert label.expected_chunk_ids == ("doc-fixed-p00-c00",)
    assert label.evidence_spans[0].text == "Angle of attack affects lift."
    assert payload["metadata"]["review_required"] is True
