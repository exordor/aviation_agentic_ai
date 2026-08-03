"""Deterministic source representations for rebuildable retrieval indexes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.storage_contracts import (
    SourceAnchorRecord,
    SourceChunkRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


SOURCE_CHUNK_REPRESENTATION_VERSION = "aviation-source-chunk-v1"

_TEXTUAL_SOURCE_FAMILIES = frozenset(
    {
        SourceFamily.ATCSCC_ADVISORY,
        SourceFamily.NASR_FACILITY,
        SourceFamily.FAA_TERM,
        SourceFamily.METAR,
        SourceFamily.TAF,
        SourceFamily.WEB_DOCUMENT,
    }
)


def build_full_record_anchor(
    source_version: SourceVersionRecord,
) -> SourceAnchorRecord:
    """Return the exact full-text anchor for one immutable source version."""

    return SourceAnchorRecord(
        source_anchor_id=stable_id(
            "source-anchor",
            source_version.source_version_id,
            0,
            len(source_version.content),
        ),
        source_version_id=source_version.source_version_id,
        char_start=0,
        char_end=len(source_version.content),
        anchor_kind="full_record",
    )


def build_source_record_chunk(
    source_version: SourceVersionRecord,
    *,
    event_id: str | None = None,
) -> SourceChunkRecord | None:
    """Build one exact full-record chunk for an admitted textual source."""

    if source_version.family not in _TEXTUAL_SOURCE_FAMILIES:
        return None
    anchor = build_full_record_anchor(source_version)
    metadata = {
        **source_version.metadata,
        "content_sha256": source_version.content_sha256,
        "logical_time": source_version.logical_time,
        "source_family": source_version.family.value,
        "source_id": source_version.source_id,
    }
    return SourceChunkRecord(
        chunk_id=stable_id(
            "source-chunk",
            source_version.source_version_id,
            "source_record",
            anchor.char_start,
            anchor.char_end,
            SOURCE_CHUNK_REPRESENTATION_VERSION,
        ),
        source_version_id=source_version.source_version_id,
        event_id=event_id,
        chunk_kind="source_record",
        text=source_version.content,
        char_start=anchor.char_start,
        char_end=anchor.char_end,
        source_anchor_id=anchor.source_anchor_id,
        representation_version=SOURCE_CHUNK_REPRESENTATION_VERSION,
        metadata=metadata,
    )


def _build_declared_span_chunks(
    source_version: SourceVersionRecord,
) -> tuple[SourceChunkRecord, ...] | None:
    """Materialize source-owned chunk spans when an adapter supplied them.

    PDF and other structured documents can provide paragraph/section spans
    during deterministic ingestion.  The spans remain ordinary source chunks
    so the existing FTS/Chroma indexing path can embed them without creating a
    second retrieval implementation.
    """

    raw_spans = source_version.metadata.get("chunk_spans")
    if not isinstance(raw_spans, list):
        return None
    base_metadata = {
        key: value
        for key, value in source_version.metadata.items()
        if key != "chunk_spans"
    }
    chunks: list[SourceChunkRecord] = []
    for span in raw_spans:
        if not isinstance(span, dict):
            raise ValueError("source chunk span must be an object")
        char_start = span.get("char_start")
        char_end = span.get("char_end")
        if not isinstance(char_start, int) or not isinstance(char_end, int):
            raise ValueError("source chunk span offsets must be integers")
        if char_start < 0 or char_end <= char_start or char_end > len(source_version.content):
            raise ValueError("source chunk span is outside source content")
        anchor = SourceAnchorRecord(
            source_anchor_id=stable_id(
                "source-anchor",
                source_version.source_version_id,
                char_start,
                char_end,
            ),
            source_version_id=source_version.source_version_id,
            char_start=char_start,
            char_end=char_end,
            anchor_kind="text_span",
        )
        metadata = {
            **base_metadata,
            "chunking": "declared_span",
            **{
                key: value
                for key, value in span.items()
                if key not in {"char_start", "char_end"}
            },
        }
        chunks.append(
            SourceChunkRecord(
                chunk_id=stable_id(
                    "source-chunk",
                    source_version.source_version_id,
                    "source_record",
                    char_start,
                    char_end,
                    SOURCE_CHUNK_REPRESENTATION_VERSION,
                ),
                source_version_id=source_version.source_version_id,
                event_id=None,
                chunk_kind="source_record",
                text=source_version.content[char_start:char_end],
                char_start=char_start,
                char_end=char_end,
                source_anchor_id=anchor.source_anchor_id,
                representation_version=SOURCE_CHUNK_REPRESENTATION_VERSION,
                metadata=metadata,
            )
        )
    return tuple(sorted(chunks, key=lambda chunk: chunk.chunk_id))


def build_source_record_chunks(
    source_versions: Iterable[SourceVersionRecord],
    *,
    event_ids_by_source_version: Mapping[str, str] | None = None,
) -> tuple[SourceChunkRecord, ...]:
    """Build deterministically ordered chunks without writing an index."""

    event_ids = event_ids_by_source_version or {}
    chunks: list[SourceChunkRecord] = []
    for source_version in source_versions:
        declared = _build_declared_span_chunks(source_version)
        if declared is not None:
            chunks.extend(declared)
            continue
        chunk = build_source_record_chunk(
            source_version,
            event_id=event_ids.get(source_version.source_version_id),
        )
        if chunk is not None:
            chunks.append(chunk)
    return tuple(
        sorted(
            chunks,
            key=lambda chunk: (
                chunk.source_version_id,
                chunk.char_start,
                chunk.char_end,
                chunk.chunk_id,
            ),
        )
    )
