"""Deterministic ingestion of FAA order document evidence.

The PDF is an offline source artifact.  This module only extracts stable
page/paragraph evidence and immutable source records; it does not call an LLM
or publish graph facts.  Candidate fact generation and publication remain the
shared ontology-constrained pipeline used by other source families.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re

from pydantic import Field
import tiktoken

from aviation_agentic_ai.agent_system.contracts import SourceFamily, StrictModel
from aviation_agentic_ai.agent_system.storage_contracts import (
    SourceAssetRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id
from aviation_agentic_ai.utils.pdf import PdfPage, extract_pages


FAA_ORDER_SOURCE_ID = "faa-order:jo-7210.3ee"
FAA_ORDER_ASSET_KEY = "faa_order_7210_3ee"
FAA_ORDER_SOURCE_URL = (
    "https://www.faa.gov/documentLibrary/media/Order/"
    "7210.3EE_Basic_dtd_2-20-25.pdf"
)

DEFAULT_SECTION_PREFIXES = ("18",)
DEFAULT_MAX_CHUNK_TOKENS = 500
DEFAULT_CHUNK_OVERLAP_TOKENS = 50

_PARAGRAPH_RE = re.compile(
    r"(?m)^\s*(?P<paragraph>18-\d+-\d+)\.\s*(?P<heading>[^\n]*)"
)
_TOPICS = {
    "18-1": "traffic_management_mission",
    "18-7": "traffic_management_initiatives",
    "18-10": "ground_delay_program",
    "18-20": "route_advisory",
    "18-22": "national_playbook",
    "18-26": "weather_management",
}

_TOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")


class FAAOrderEvidenceCard(StrictModel):
    """One page/paragraph-anchored evidence unit from JO 7210.3EE."""

    source_id: str = Field(min_length=1)
    source_version_id: str | None = None
    source_anchor_id: str | None = None
    evidence_ref: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    section_id: str = Field(pattern=r"^18-\d+$")
    paragraph_id: str = Field(pattern=r"^18-\d+-\d+$")
    heading: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)


class FAAOrderExtractionChunk(StrictModel):
    """One recursively bounded LLM/RAG unit backed by a parent paragraph."""

    chunk_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_version_id: str | None = None
    source_anchor_id: str | None = None
    evidence_ref: str = Field(min_length=1)
    parent_evidence_ref: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    section_id: str = Field(pattern=r"^18-\d+$")
    paragraph_id: str = Field(pattern=r"^18-\d+-\d+$")
    heading: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    evidence_text: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    parent_char_start: int = Field(ge=0)
    parent_char_end: int = Field(gt=0)
    token_count: int = Field(ge=1)


@dataclass(frozen=True)
class FAAOrderSourcePackage:
    """Immutable extracted source plus evidence cards for downstream stages."""

    asset: SourceAssetRecord
    source_version: SourceVersionRecord
    cards: tuple[FAAOrderEvidenceCard, ...]
    extraction_chunks: tuple[FAAOrderExtractionChunk, ...]
    asset_sha256: str
    pdf_byte_count: int

    @property
    def source_version_id(self) -> str:
        return self.source_version.source_version_id


def _normalise_page_text(text: str) -> str:
    """Normalize PDF typography without changing semantic content."""

    return (
        text.replace("\u2212", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u00a0", " ")
    )


def _is_table_of_contents_page(text: str) -> bool:
    """Reject TOC pages whose dotted leaders are not document evidence."""

    return text.count(". . .") >= 10 and "Paragraph" in text and "Page" in text


def _token_count(text: str) -> int:
    return len(_TOKEN_ENCODING.encode(text))


def _selected_section(
    section_id: str,
    *,
    sections: Sequence[str] | None,
    section_prefixes: Sequence[str],
) -> bool:
    if sections is not None:
        return section_id in set(sections)
    return any(
        section_id == prefix or section_id.startswith(f"{prefix}-")
        for prefix in section_prefixes
    )


def _source_content(pages: Sequence[PdfPage]) -> tuple[str, tuple[tuple[PdfPage, str, int], ...]]:
    ordered = tuple(sorted(pages, key=lambda page: page.page_number))
    fragments: list[str] = []
    locations: list[tuple[PdfPage, str, int]] = []
    offset = 0
    for index, page in enumerate(ordered):
        if index:
            separator = "\n\f\n"
            fragments.append(separator)
            offset += len(separator)
        text = _normalise_page_text(page.text).strip()
        fragments.append(text)
        locations.append((page, text, offset))
        offset += len(text)
    return "".join(fragments), tuple(locations)


def extract_faa_order_cards(
    pages: Sequence[PdfPage],
    *,
    sections: Sequence[str] | None = None,
    section_prefixes: Sequence[str] = DEFAULT_SECTION_PREFIXES,
) -> tuple[FAAOrderEvidenceCard, ...]:
    """Extract configured numbered paragraphs with deterministic anchors."""

    _, locations = _source_content(pages)
    cards: list[FAAOrderEvidenceCard] = []
    for page, text, page_offset in locations:
        if _is_table_of_contents_page(text):
            continue
        matches = tuple(_PARAGRAPH_RE.finditer(text))
        for index, match in enumerate(matches):
            paragraph_id = match.group("paragraph")
            section_id = "-".join(paragraph_id.split("-")[:2])
            if not _selected_section(
                section_id,
                sections=sections,
                section_prefixes=section_prefixes,
            ):
                continue
            raw_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            raw_start = match.start()
            while raw_start < raw_end and text[raw_start].isspace():
                raw_start += 1
            while raw_end > raw_start and text[raw_end - 1].isspace():
                raw_end -= 1
            evidence_text = text[raw_start:raw_end]
            page_number = page.page_number + 1
            cards.append(
                FAAOrderEvidenceCard(
                    source_id=FAA_ORDER_SOURCE_ID,
                    evidence_ref=stable_id(
                        "faa-order-evidence",
                        FAA_ORDER_SOURCE_ID,
                        page_number,
                        paragraph_id,
                    ),
                    page_number=page_number,
                    section_id=section_id,
                    paragraph_id=paragraph_id,
                    heading=match.group("heading").strip() or paragraph_id,
                    topic=_TOPICS.get(section_id, "faa_order"),
                    evidence_text=evidence_text,
                    char_start=page_offset + raw_start,
                    char_end=page_offset + raw_end,
                )
            )
    return tuple(cards)


def _bounded_end(text: str, start: int, max_tokens: int) -> int:
    """Find the largest natural boundary that fits the token budget."""

    if _token_count(text[start:]) <= max_tokens:
        return len(text)
    low = start + 1
    high = len(text)
    while low < high:
        middle = (low + high + 1) // 2
        if _token_count(text[start:middle]) <= max_tokens:
            low = middle
        else:
            high = middle - 1
    hard_end = low
    minimum = start + max(1, (hard_end - start) // 2)
    candidates: list[int] = []
    for match in re.finditer(r"\n\n+|\n|(?<=[.!?;:])\s+|\s+", text[start:hard_end]):
        boundary = start + match.start()
        if boundary >= minimum:
            candidates.append(boundary)
    end = candidates[-1] if candidates else hard_end
    while end > start and text[end - 1].isspace():
        end -= 1
    return max(end, start + 1)


def _overlap_start(text: str, start: int, end: int, overlap_tokens: int) -> int:
    if overlap_tokens <= 0:
        return end
    low = start
    high = end
    while low < high:
        middle = (low + high) // 2
        if _token_count(text[middle:end]) <= overlap_tokens:
            high = middle
        else:
            low = middle + 1
    candidate = low
    while candidate < end and not text[candidate].isspace():
        candidate += 1
    while candidate < end and text[candidate].isspace():
        candidate += 1
    return candidate if candidate < end else end


def build_faa_order_extraction_chunks(
    cards: Sequence[FAAOrderEvidenceCard],
    *,
    max_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    overlap_tokens: int = DEFAULT_CHUNK_OVERLAP_TOKENS,
) -> tuple[FAAOrderExtractionChunk, ...]:
    """Recursively split paragraph evidence while preserving exact offsets."""

    if max_tokens < 1:
        raise ValueError("max_tokens must be positive")
    if overlap_tokens < 0 or overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be non-negative and below max_tokens")
    result: list[FAAOrderExtractionChunk] = []
    for card in cards:
        text = card.evidence_text
        local_start = 0
        chunk_index = 0
        while local_start < len(text):
            while local_start < len(text) and text[local_start].isspace():
                local_start += 1
            if local_start >= len(text):
                break
            local_end = _bounded_end(text, local_start, max_tokens)
            evidence_text = text[local_start:local_end]
            global_start = card.char_start + local_start
            global_end = card.char_start + local_end
            evidence_ref = stable_id(
                "faa-order-extraction-evidence",
                card.evidence_ref,
                chunk_index,
                global_start,
                global_end,
            )
            result.append(
                FAAOrderExtractionChunk(
                    chunk_id=stable_id(
                        "faa-order-extraction-chunk",
                        card.evidence_ref,
                        chunk_index,
                        global_start,
                        global_end,
                        max_tokens,
                        overlap_tokens,
                    ),
                    source_id=card.source_id,
                    source_version_id=card.source_version_id,
                    source_anchor_id=None,
                    evidence_ref=evidence_ref,
                    parent_evidence_ref=card.evidence_ref,
                    page_number=card.page_number,
                    section_id=card.section_id,
                    paragraph_id=card.paragraph_id,
                    heading=card.heading,
                    topic=card.topic,
                    chunk_index=chunk_index,
                    evidence_text=evidence_text,
                    char_start=global_start,
                    char_end=global_end,
                    parent_char_start=card.char_start,
                    parent_char_end=card.char_end,
                    token_count=_token_count(evidence_text),
                )
            )
            if local_end >= len(text):
                break
            next_start = _overlap_start(text, local_start, local_end, overlap_tokens)
            local_start = next_start if next_start > local_start else local_end
            chunk_index += 1
    return tuple(result)


def build_faa_order_source_package(
    pages: Sequence[PdfPage],
    *,
    pdf_sha256: str,
    pdf_byte_count: int,
    source_url: str = FAA_ORDER_SOURCE_URL,
    local_path: str = (
        "data/raw/faa_orders/JO_7210.3EE_2025-02-20.pdf"
    ),
    effective_start: str = "2025-02-20",
    sections: Sequence[str] | None = None,
    section_prefixes: Sequence[str] = DEFAULT_SECTION_PREFIXES,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    chunk_overlap_tokens: int = DEFAULT_CHUNK_OVERLAP_TOKENS,
) -> FAAOrderSourcePackage:
    """Build an immutable source version and bind extracted cards to it."""

    content, _ = _source_content(pages)
    content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    asset_id = stable_id("source-asset", FAA_ORDER_ASSET_KEY, pdf_sha256)
    source_version_id = stable_id(
        "source-version",
        FAA_ORDER_SOURCE_ID,
        content_sha256,
    )
    raw_cards = extract_faa_order_cards(
        pages,
        sections=sections,
        section_prefixes=section_prefixes,
    )
    raw_chunks = build_faa_order_extraction_chunks(
        raw_cards,
        max_tokens=max_chunk_tokens,
        overlap_tokens=chunk_overlap_tokens,
    )
    asset = SourceAssetRecord(
        asset_id=asset_id,
        asset_key=FAA_ORDER_ASSET_KEY,
        family=SourceFamily.WEB_DOCUMENT,
        local_path=local_path,
        source_url=source_url,
        media_type="application/pdf",
        content_sha256=pdf_sha256,
        byte_count=pdf_byte_count,
        effective_start=effective_start,
        effective_end=None,
    )
    source_version = SourceVersionRecord(
        source_version_id=source_version_id,
        source_id=FAA_ORDER_SOURCE_ID,
        family=SourceFamily.WEB_DOCUMENT,
        asset_id=asset_id,
        content=content,
        content_sha256=content_sha256,
        source_url=source_url,
        logical_time="2025-02-20",
        metadata={
            "document_title": "Facility Operation and Administration",
            "edition": "JO 7210.3EE Basic",
            "effective_date": "2025-02-20",
            "source_role": "normative_document_reference",
            "extraction": "pymupdf_text_pages",
            "chunking": "recursive_chapter_paragraph_v2",
            "max_chunk_tokens": max_chunk_tokens,
            "chunk_overlap_tokens": chunk_overlap_tokens,
            "chunk_spans": [
                {
                    "char_start": chunk.char_start,
                    "char_end": chunk.char_end,
                    "paragraph_id": chunk.paragraph_id,
                    "section_id": chunk.section_id,
                    "page_number": chunk.page_number,
                    "topic": chunk.topic,
                    "evidence_ref": chunk.evidence_ref,
                    "parent_evidence_ref": chunk.parent_evidence_ref,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                }
                for chunk in raw_chunks
            ],
        },
    )
    cards = []
    for card in raw_cards:
        anchor_id = stable_id(
            "source-anchor",
            source_version_id,
            card.char_start,
            card.char_end,
        )
        cards.append(
            card.model_copy(
                update={
                    "source_version_id": source_version_id,
                    "source_anchor_id": anchor_id,
                }
            )
        )
    extraction_chunks = tuple(
        chunk.model_copy(
            update={
                "source_version_id": source_version_id,
                "source_anchor_id": stable_id(
                    "source-anchor",
                    source_version_id,
                    chunk.char_start,
                    chunk.char_end,
                ),
            }
        )
        for chunk in raw_chunks
    )
    return FAAOrderSourcePackage(
        asset=asset,
        source_version=source_version,
        cards=tuple(cards),
        extraction_chunks=extraction_chunks,
        asset_sha256=pdf_sha256,
        pdf_byte_count=pdf_byte_count,
    )


def load_faa_order_source_package(
    pdf_path: str | Path,
    *,
    source_url: str = FAA_ORDER_SOURCE_URL,
    effective_start: str = "2025-02-20",
    sections: Sequence[str] | None = None,
    section_prefixes: Sequence[str] = DEFAULT_SECTION_PREFIXES,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    chunk_overlap_tokens: int = DEFAULT_CHUNK_OVERLAP_TOKENS,
) -> FAAOrderSourcePackage:
    """Read the pinned PDF and return source/version/chunk evidence objects."""

    path = Path(pdf_path)
    raw = path.read_bytes()
    return build_faa_order_source_package(
        tuple(extract_pages(path)),
        pdf_sha256=hashlib.sha256(raw).hexdigest(),
        pdf_byte_count=len(raw),
        source_url=source_url,
        local_path=path.as_posix(),
        effective_start=effective_start,
        sections=sections,
        section_prefixes=section_prefixes,
        max_chunk_tokens=max_chunk_tokens,
        chunk_overlap_tokens=chunk_overlap_tokens,
    )


__all__ = [
    "DEFAULT_SECTION_PREFIXES",
    "DEFAULT_MAX_CHUNK_TOKENS",
    "DEFAULT_CHUNK_OVERLAP_TOKENS",
    "FAA_ORDER_ASSET_KEY",
    "FAA_ORDER_SOURCE_ID",
    "FAA_ORDER_SOURCE_URL",
    "FAAOrderEvidenceCard",
    "FAAOrderExtractionChunk",
    "FAAOrderSourcePackage",
    "build_faa_order_source_package",
    "build_faa_order_extraction_chunks",
    "extract_faa_order_cards",
    "load_faa_order_source_package",
]
