from pathlib import Path

from aviation_agentic_ai.chunking.chunks import (
    BENCHMARK_V2_CHUNKING_STRATEGIES,
    CHUNKING_STRATEGIES,
    SourceChunk,
    _cosine_similarity,
    _proposition_segments,
    _window_text,
    build_chunks,
    chunking_profile,
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
            similarity_fn=lambda _left, _right: 0.5,
        )
        assert chunks
        assert all(chunk.text for chunk in chunks)
        assert chunks[0].chunk_id.startswith(f"source-{strategy}-p00-c")
        assert all(chunk.strategy == strategy for chunk in chunks)
        assert all(chunk.token_count > 0 for chunk in chunks)


def test_benchmark_v2_chunking_strategies_are_registered() -> None:
    assert set(BENCHMARK_V2_CHUNKING_STRATEGIES).issubset(set(CHUNKING_STRATEGIES))
    assert "structure_aware_medium" in CHUNKING_STRATEGIES
    assert "structure_aware_large" in CHUNKING_STRATEGIES
    assert "late_chunking_stub" not in CHUNKING_STRATEGIES


def test_chunking_profile_marks_partial_and_fallback_methods() -> None:
    embedding = chunking_profile("embedding_semantic")
    hierarchy = chunking_profile("hierarchical_parent_child")
    proposition = chunking_profile("proposition_like")

    assert embedding.semantic_backend == "sentence_transformers_or_fallback_lexical"
    assert embedding.lexical_fallback is True
    assert hierarchy.implementation_status == "partial"
    assert hierarchy.parent_child_retrieval == "partial_child_index_parent_metadata"
    assert proposition.returned_context_unit == "proposition_only"


def test_window_text_prefers_word_boundary_before_hard_cut() -> None:
    windows = _window_text("alpha beta gamma delta", max_chars=12, overlap_chars=0)

    assert windows[0][2] == "alpha beta"
    assert not windows[0][2].endswith("g")


def test_cosine_similarity_rejects_mismatched_dimensions() -> None:
    try:
        _cosine_similarity([1.0, 0.0], [1.0])
    except ValueError as exc:
        assert "same length" in str(exc)
    else:  # pragma: no cover - assertion guard.
        raise AssertionError("Expected ValueError")


def test_proposition_like_merges_leading_short_fragment() -> None:
    segments = _proposition_segments(
        (
            "Intro. Lift is the upward force created by pressure differences across the wing. "
            "Pilots monitor aircraft performance carefully."
        ),
        max_chars=900,
        overlap_chars=80,
        min_chars=40,
    )

    assert segments
    assert segments[0][2].startswith("Intro. Lift is")
    assert len(segments[0][2]) >= 40
    assert all(len(segment[2]) >= 40 for segment in segments[:-1])


def test_fixed_and_recursive_size_tiers_apply_relative_sizes(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    text = " ".join([f"Sentence {index} affects lift." for index in range(80)])
    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [PdfPage(page_number=0, text=text)],
    )

    fixed_small = build_chunks("data/raw/source.pdf", strategy="fixed_small")
    fixed_large = build_chunks("data/raw/source.pdf", strategy="fixed_large")
    recursive_small = build_chunks("data/raw/source.pdf", strategy="recursive_small")
    recursive_large = build_chunks("data/raw/source.pdf", strategy="recursive_large")

    assert len(fixed_small) > len(fixed_large)
    assert len(recursive_small) > len(recursive_large)
    assert fixed_small[0].metadata["configured_max_chars"] == 400
    assert fixed_large[0].metadata["configured_max_chars"] == 1600


def test_structure_aware_size_variants_apply_relative_sizes(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    text = "\n".join(
        [f"Section {index}\n" + " ".join(["Lift affects climb."] * 10) for index in range(30)]
    )
    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [PdfPage(page_number=0, text=text)],
    )

    small = build_chunks("data/raw/source.pdf", strategy="structure_aware")
    medium = build_chunks("data/raw/source.pdf", strategy="structure_aware_medium")
    large = build_chunks("data/raw/source.pdf", strategy="structure_aware_large")

    assert len(small) >= len(medium) >= len(large)
    assert medium[0].metadata["configured_max_chars"] == 900
    assert large[0].metadata["configured_max_chars"] == 1600


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


def test_embedding_semantic_falls_back_to_lexical_when_backend_fails(monkeypatch) -> None:
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
    monkeypatch.setattr(
        chunk_module,
        "_embedding_similarity_fn",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("backend missing")),
    )

    chunks = build_chunks("data/raw/source.pdf", strategy="embedding_semantic")

    assert chunks
    assert chunks[0].metadata["semantic_backend"] == "fallback_lexical"
    assert "backend missing" in chunks[0].metadata["semantic_backend_error"]


def test_embedding_semantic_uses_mock_embedding_backend(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(
                page_number=0,
                text=(
                    ("Air affects lift. Lift affects climb. " * 20)
                    + "Weather changes visibility."
                ),
            )
        ],
    )
    monkeypatch.setattr(
        chunk_module,
        "_embedding_similarity_fn",
        lambda *_args, **_kwargs: (lambda left, right: 0.0 if "Weather" in right else 0.9),
    )

    chunks = build_chunks("data/raw/source.pdf", strategy="embedding_semantic")

    assert len(chunks) == 2
    assert chunks[0].metadata["semantic_backend"] == "sentence_transformers"


def test_proposition_like_marks_heuristic_proposition_chunks(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(
                page_number=0,
                text=(
                    "Lift is the upward force. Angle of attack affects lift. "
                    "This handbook includes examples for pilots."
                ),
            )
        ],
    )

    chunks = build_chunks("data/raw/source.pdf", strategy="proposition_like")

    assert chunks
    assert chunks[0].metadata["proposition_extraction"] == "heuristic_sentence_cue"
    assert chunks[0].metadata["llm_proposition_extraction"] is False
    assert any("affects lift" in chunk.text for chunk in chunks)


def test_hierarchical_parent_child_emits_parent_metadata(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(
                page_number=0,
                text=(
                    "Lift Section\n"
                    "Air flows over a wing. Lift changes with angle of attack. "
                    "Pressure affects performance."
                ),
            )
        ],
    )

    chunks = build_chunks("data/raw/source.pdf", strategy="hierarchical_parent_child")

    assert chunks
    assert chunks[0].parent_chunk_id.startswith("source-hierarchical_parent_child-p00-parent")
    assert chunks[0].parent_text
    assert chunks[0].metadata["retrieval_integration"] == "partial_child_index_parent_metadata"


def test_contextual_prefix_adds_deterministic_source_prefix(monkeypatch) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(page_number=3, text="Lift Section\nAir flows over a wing.")
        ],
    )

    chunks = build_chunks("data/raw/source.pdf", strategy="contextual_prefix")

    assert chunks
    assert chunks[0].text.startswith("Source: PHAK Chapter 4")
    assert "page=3" in chunks[0].context_prefix
    assert chunks[0].metadata["llm_contextualization"] is False
