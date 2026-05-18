from pathlib import Path

from aviation_agentic_ai.chunking.chunks import (
    CHUNKING_STRATEGIES,
    SourceChunk,
    build_chunks,
    read_chunks_jsonl,
    write_chunks_jsonl,
)
from aviation_agentic_ai.utils.pdf import PdfPage


def test_build_chunks_has_stable_ids_and_page_metadata(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(page_number=0, text="Air flows over a wing. Lift changes with angle of attack."),
            PdfPage(page_number=1, text="Pressure and density affect aircraft performance."),
        ],
    )

    chunks = build_chunks("data/raw/source.pdf", max_chars=80, overlap_chars=10)

    assert [chunk.chunk_id for chunk in chunks] == [
        "source-fixed_window-p00-c00",
        "source-fixed_window-p01-c00",
    ]
    assert chunks[0].page == 0
    assert chunks[0].text
    assert chunks[0].strategy == "fixed_window"


def test_chunk_jsonl_round_trip(tmp_path: Path) -> None:
    chunk = SourceChunk(
        chunk_id="doc-p00-c00",
        source_document="doc",
        source_path="data/raw/doc.pdf",
        page=0,
        chunk_index=0,
        char_start=0,
        char_end=12,
        text="Air and lift.",
    )
    path = write_chunks_jsonl([chunk], tmp_path / "chunks.jsonl")

    assert read_chunks_jsonl(path) == [chunk]


def test_all_chunking_strategies_generate_non_empty_stable_chunks(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(
                page_number=0,
                text=(
                    "Airfoil Structure\n"
                    "Air flows over a wing. Lift changes with angle of attack. "
                    "Pressure and density affect performance."
                ),
            )
        ],
    )

    for strategy in CHUNKING_STRATEGIES:
        chunks = build_chunks(
            "data/raw/source.pdf",
            strategy=strategy,
            max_chars=70,
            overlap_chars=10,
        )
        assert chunks
        assert all(chunk.text for chunk in chunks)
        assert chunks[0].chunk_id.startswith(f"source-{strategy}-p00-c")
        assert all(chunk.strategy == strategy for chunk in chunks)


def test_sentence_recursive_preserves_sentence_endings(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(
                page_number=0,
                text="First sentence is complete. Second sentence is complete. Third sentence ends.",
            )
        ],
    )

    chunks = build_chunks(
        "data/raw/source.pdf",
        strategy="sentence_recursive",
        max_chars=35,
        overlap_chars=0,
    )

    assert all(chunk.text.endswith((".", ";", "?", "!", ":")) for chunk in chunks)


def test_structure_aware_preserves_section_metadata(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(page_number=0, text="Lift Mechanisms\nAir flows over a wing.")
        ],
    )

    chunks = build_chunks(
        "data/raw/source.pdf",
        strategy="structure_aware",
        max_chars=120,
        overlap_chars=0,
    )

    assert chunks[0].section == "Lift Mechanisms"


def test_semantic_meta_like_splits_on_mock_similarity_drop(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(
                page_number=0,
                text="Air affects lift. Lift affects climb. Weather changes visibility.",
            )
        ],
    )

    def fake_similarity(left: str, right: str) -> float:
        return 0.0 if "Weather" in right else 0.9

    chunks = build_chunks(
        "data/raw/source.pdf",
        strategy="semantic_meta_like",
        max_chars=60,
        overlap_chars=0,
        similarity_fn=fake_similarity,
    )

    assert len(chunks) == 2
    assert "Weather" in chunks[1].text
