"""Deterministic source representations prepared for retrieval indexing."""

from __future__ import annotations

import hashlib

import pytest

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.source_retrieval import (
    SOURCE_CHUNK_REPRESENTATION_VERSION,
    build_full_record_anchor,
    build_source_record_chunk,
    build_source_record_chunks,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    SourceVersionRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


def _source_version(
    source_id: str,
    family: SourceFamily,
    content: str,
    *,
    title: str | None = None,
) -> SourceVersionRecord:
    content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    metadata: dict[str, object] = {}
    if title is not None:
        metadata["title"] = title
    return SourceVersionRecord(
        source_version_id=stable_id(
            "source-version",
            source_id,
            content_sha256,
        ),
        source_id=source_id,
        family=family,
        asset_id="source-asset:test",
        content=content,
        content_sha256=content_sha256,
        source_url="https://example.test/source",
        logical_time="2026-05-19T20:51:00Z",
        metadata=metadata,
    )


def test_text_source_version_builds_one_exact_full_record_chunk() -> None:
    """Trimming or partial offsets would break exact source verification."""

    content = "  GROUND STOP\nDUE TO THUNDERSTORMS  "
    version = _source_version(
        "2026-05-19:123",
        SourceFamily.ATCSCC_ADVISORY,
        content,
        title="Advisory 123",
    )

    anchor = build_full_record_anchor(version)
    chunk = build_source_record_chunk(
        version,
        event_id="urn:aviation-agentic-ai:event:123",
    )

    assert chunk is not None
    assert anchor.char_start == 0
    assert anchor.char_end == len(content)
    assert anchor.anchor_kind == "full_record"
    assert chunk.text == content
    assert chunk.char_start == 0
    assert chunk.char_end == len(content)
    assert chunk.source_anchor_id == anchor.source_anchor_id
    assert chunk.chunk_kind == "source_record"
    assert (
        chunk.representation_version
        == SOURCE_CHUNK_REPRESENTATION_VERSION
        == "aviation-source-chunk-v1"
    )
    assert chunk.event_id == "urn:aviation-agentic-ai:event:123"
    assert chunk.metadata == {
        "content_sha256": version.content_sha256,
        "logical_time": "2026-05-19T20:51:00Z",
        "source_family": "atcscc_advisory",
        "source_id": "2026-05-19:123",
        "title": "Advisory 123",
    }


@pytest.mark.parametrize(
    "family",
    (
        SourceFamily.ATCSCC_ADVISORY,
        SourceFamily.NASR_FACILITY,
        SourceFamily.FAA_TERM,
        SourceFamily.METAR,
        SourceFamily.TAF,
    ),
)
def test_each_textual_source_family_builds_one_chunk(
    family: SourceFamily,
) -> None:
    """Omitting one admitted text family would make its evidence undiscoverable."""

    version = _source_version(
        f"source:{family.value}",
        family,
        f"exact content for {family.value}",
    )

    assert len(build_source_record_chunks((version,))) == 1


def test_bts_rows_remain_structured_and_are_not_chunked() -> None:
    """Embedding BTS rows would blur structured observations into prose."""

    version = _source_version(
        "bts:KJFK:2026-05-19T20",
        SourceFamily.BTS_ON_TIME,
        '{"scheduled_arrivals": 22, "cancelled": 0}',
    )

    assert build_source_record_chunk(version) is None
    assert build_source_record_chunks((version,)) == ()


def test_source_chunk_identity_is_repeatable_and_revision_specific() -> None:
    """Reusing a chunk ID after content revision would hide immutable history."""

    original = _source_version(
        "2026-05-19:123",
        SourceFamily.ATCSCC_ADVISORY,
        "GROUND STOP",
    )
    revision = _source_version(
        "2026-05-19:123",
        SourceFamily.ATCSCC_ADVISORY,
        "GROUND STOP EXTENDED",
    )

    first = build_source_record_chunk(original)
    repeated = build_source_record_chunk(original)
    revised = build_source_record_chunk(revision)

    assert first == repeated
    assert first is not None
    assert revised is not None
    assert first.chunk_id != revised.chunk_id
    assert first.source_version_id != revised.source_version_id


def test_document_chunk_spans_are_materialized_as_retrieval_chunks() -> None:
    content = "18-10-1. POLICY\nGDP policy.\n\f\n18-10-2. GENERAL\nGDP general."
    version = _source_version(
        "faa-order:jo-7210.3ee",
        SourceFamily.WEB_DOCUMENT,
        content,
    ).model_copy(
        update={
            "metadata": {
                "chunk_spans": [
                    {"char_start": 0, "char_end": 27, "paragraph_id": "18-10-1"},
                    {"char_start": 30, "char_end": len(content), "paragraph_id": "18-10-2"},
                ]
            }
        }
    )

    chunks = build_source_record_chunks((version,))

    assert len(chunks) == 2
    assert [chunk.text for chunk in chunks] == [
        content[0:27],
        content[30:],
    ]
    assert [chunk.metadata["paragraph_id"] for chunk in chunks] == [
        "18-10-1",
        "18-10-2",
    ]
