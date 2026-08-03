"""Offline registration of FAA order document evidence.

This is the ingestion half of the RAG pipeline.  It registers the immutable
PDF-derived source version, paragraph anchors, and retrieval chunks.  The
embedding/reindex command consumes those chunks; no LLM is called here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.faa_order_document import (
    DEFAULT_CHUNK_OVERLAP_TOKENS,
    DEFAULT_MAX_CHUNK_TOKENS,
    DEFAULT_SECTION_PREFIXES,
    FAA_ORDER_SOURCE_URL,
    FAAOrderSourcePackage,
    load_faa_order_source_package,
)
from aviation_agentic_ai.agent_system.source_path_resolver import (
    resolve_source_path,
)
from aviation_agentic_ai.agent_system.source_retrieval import (
    build_source_record_chunks,
)
from aviation_agentic_ai.paths import PROJECT_ROOT


@dataclass(frozen=True)
class FAAOrderIngestionResult:
    status: str
    source_version_id: str
    card_count: int
    chunk_count: int
    chunk_ids: tuple[str, ...]
    reason: str = ""


@dataclass(frozen=True)
class FAAOrderIngestionSummary:
    """Bounded outcome for the document ingestion domain."""

    status: str
    discovered_count: int
    selected_count: int
    attempted_count: int
    skipped_count: int
    ok_count: int
    insufficient_count: int
    blocked_count: int
    source_version_id: str | None = None
    chunk_count: int = 0
    reason: str = ""


def configured_faa_order_document_options(
    config: dict[str, Any],
) -> dict[str, object]:
    """Read the bounded document scope from source metadata."""

    metadata = config.get("source_metadata")
    source_metadata = metadata if isinstance(metadata, dict) else {}
    row = source_metadata.get("faa_order_7210_3ee")
    document_config = row if isinstance(row, dict) else {}
    raw_prefixes = document_config.get("section_prefixes", DEFAULT_SECTION_PREFIXES)
    if not isinstance(raw_prefixes, (list, tuple)) or not all(
        isinstance(value, str) and value for value in raw_prefixes
    ):
        raise ValueError("FAA order section_prefixes must be a non-empty string list")
    max_tokens = document_config.get("max_chunk_tokens", DEFAULT_MAX_CHUNK_TOKENS)
    overlap = document_config.get(
        "chunk_overlap_tokens", DEFAULT_CHUNK_OVERLAP_TOKENS
    )
    if not isinstance(max_tokens, int) or max_tokens < 1:
        raise ValueError("FAA order max_chunk_tokens must be a positive integer")
    if not isinstance(overlap, int) or overlap < 0 or overlap >= max_tokens:
        raise ValueError("FAA order chunk overlap must be below max_chunk_tokens")
    return {
        "effective_start": str(
            document_config.get("effective_start", "2025-02-20")
        ),
        "section_prefixes": tuple(raw_prefixes),
        "max_chunk_tokens": max_tokens,
        "chunk_overlap_tokens": overlap,
    }


def register_faa_order_source(
    store: AviationEvidenceStore,
    package: FAAOrderSourcePackage,
) -> FAAOrderIngestionResult:
    """Persist one immutable FAA order package and its paragraph chunks."""

    store.register_source_asset(package.asset)
    store.register_source_version(package.source_version)
    for card in package.cards:
        if card.source_anchor_id is None:
            raise ValueError("FAA order card has no source anchor")
        store.register_source_anchor(
            package.source_version_id,
            char_start=card.char_start,
            char_end=card.char_end,
        )
    for chunk in package.extraction_chunks:
        if chunk.source_anchor_id is None:
            raise ValueError("FAA order extraction chunk has no source anchor")
        store.register_source_anchor(
            package.source_version_id,
            char_start=chunk.char_start,
            char_end=chunk.char_end,
        )
    chunks = build_source_record_chunks((package.source_version,))
    store.upsert_source_chunks(chunks)
    return FAAOrderIngestionResult(
        status="ok",
        source_version_id=package.source_version_id,
        card_count=len(package.cards),
        chunk_count=len(chunks),
        chunk_ids=tuple(chunk.chunk_id for chunk in chunks),
    )


def run_faa_order_ingestion(
    config: dict[str, Any],
    store: AviationEvidenceStore,
    *,
    source_root: str | Path | None = None,
    project_root: str | Path = PROJECT_ROOT,
) -> FAAOrderIngestionSummary:
    """Execute the PDF's offline RAG ingestion stages for one configured source.

    The function deliberately stops at immutable source records and chunks.
    Embedding is performed by the normal ``reindex`` command, and online
    retrieval/generation remains the existing Query Agent path.
    """

    configured = config.get("sources")
    sources = configured if isinstance(configured, dict) else {}
    configured_path = sources.get("faa_order_7210_3ee")
    if not isinstance(configured_path, str) or not configured_path:
        return FAAOrderIngestionSummary(
            status="blocked",
            discovered_count=0,
            selected_count=0,
            attempted_count=0,
            skipped_count=0,
            ok_count=0,
            insufficient_count=0,
            blocked_count=1,
            reason="config.sources.faa_order_7210_3ee is not configured",
        )

    urls = config.get("source_urls")
    source_urls = urls if isinstance(urls, dict) else {}
    source_url = source_urls.get("faa_order_7210_3ee")
    if not isinstance(source_url, str) or not source_url:
        source_url = FAA_ORDER_SOURCE_URL

    try:
        document_options = configured_faa_order_document_options(config)
        resolved = resolve_source_path(
            configured_path,
            source_root=source_root,
            project_root=project_root,
        )
        package = load_faa_order_source_package(
            resolved.resolved_path,
            source_url=source_url,
            **document_options,
        )
        checksums = config.get("source_checksums")
        source_checksums = checksums if isinstance(checksums, dict) else {}
        expected = source_checksums.get("faa_order_7210_3ee")
        if expected is not None and expected != package.asset_sha256:
            raise ValueError(
                "source checksum mismatch for faa_order_7210_3ee: "
                f"expected {expected}, observed {package.asset_sha256}"
            )
        if not package.cards:
            return FAAOrderIngestionSummary(
                status="insufficient",
                discovered_count=1,
                selected_count=1,
                attempted_count=1,
                skipped_count=0,
                ok_count=0,
                insufficient_count=1,
                blocked_count=0,
                source_version_id=package.source_version_id,
                reason="configured sections yielded no evidence cards",
            )
        prior = store.get_source_version(package.source_version_id)
        result = register_faa_order_source(store, package)
        if prior is not None:
            return FAAOrderIngestionSummary(
                status="ok",
                discovered_count=1,
                selected_count=1,
                attempted_count=0,
                skipped_count=1,
                ok_count=1,
                insufficient_count=0,
                blocked_count=0,
                source_version_id=package.source_version_id,
                chunk_count=result.chunk_count,
                reason="source version already registered",
            )
        return FAAOrderIngestionSummary(
            status="ok",
            discovered_count=1,
            selected_count=1,
            attempted_count=1,
            skipped_count=0,
            ok_count=1,
            insufficient_count=0,
            blocked_count=0,
            source_version_id=package.source_version_id,
            chunk_count=result.chunk_count,
        )
    except Exception as exc:
        return FAAOrderIngestionSummary(
            status="blocked",
            discovered_count=1,
            selected_count=1,
            attempted_count=1,
            skipped_count=0,
            ok_count=0,
            insufficient_count=0,
            blocked_count=1,
            reason=f"{type(exc).__name__}: {exc}",
        )


__all__ = [
    "FAAOrderIngestionResult",
    "FAAOrderIngestionSummary",
    "configured_faa_order_document_options",
    "register_faa_order_source",
    "run_faa_order_ingestion",
]
