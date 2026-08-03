from __future__ import annotations

from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.faa_order_document import (
    DEFAULT_SECTION_PREFIXES,
    FAA_ORDER_SOURCE_ID,
    build_faa_order_source_package,
    build_faa_order_extraction_chunks,
    extract_faa_order_cards,
    load_faa_order_source_package,
)
from aviation_agentic_ai.agent_system.source_retrieval import build_source_record_chunks
from aviation_agentic_ai.utils.pdf import PdfPage


def test_extracts_targeted_order_paragraphs_with_page_anchors() -> None:
    pages = (
        PdfPage(
            page_number=411,
            text=(
                "Section 10. Ground Delay Programs\n"
                "18−10−6. ATCSCC PROCEDURES\n"
                "Upon receipt of information, the ATCSCC must conference affected facilities.\n"
                "18−10−7. FACILITY PROCEDURES\n"
                "Facilities must coordinate implementation.\n"
            ),
        ),
        PdfPage(
            page_number=452,
            text=(
                "Section 22. National Playbook\n"
                "18−22−1. PURPOSE\n"
                "The National Playbook contains pre-validated routes.\n"
            ),
        ),
        PdfPage(
            page_number=24,
            text=(
                "Paragraph Page\n"
                "18−10−6. ATCSCC PROCEDURES " + ". . . " * 12 + "18−10−1\n"
            ),
        ),
    )

    cards = extract_faa_order_cards(pages, sections=("18-10", "18-22"))

    assert [card.paragraph_id for card in cards] == ["18-10-6", "18-10-7", "18-22-1"]
    assert cards[0].section_id == "18-10"
    assert cards[0].page_number == 412
    assert "conference affected facilities" in cards[0].evidence_text
    assert cards[0].evidence_ref


def test_source_package_binds_cards_to_one_immutable_text_version() -> None:
    pages = (
        PdfPage(
            page_number=410,
            text="18−10−1. POLICY\nGDP policy text.\n",
        ),
    )

    package = build_faa_order_source_package(
        pages,
        pdf_sha256="a" * 64,
        pdf_byte_count=123,
        source_url="https://example.test/order.pdf",
    )

    assert package.source_version.source_id == FAA_ORDER_SOURCE_ID
    assert package.source_version.family.value == "web_document"
    assert package.source_version.content
    assert package.source_version_id == package.source_version.source_version_id
    assert package.cards[0].source_version_id == package.source_version_id
    assert package.cards[0].evidence_text in package.source_version.content
    assert package.asset_sha256 == "a" * 64
    assert package.pdf_byte_count == 123
    chunks = build_source_record_chunks((package.source_version,))
    assert len(chunks) == 1
    assert chunks[0].metadata["paragraph_id"] == "18-10-1"


def test_default_scope_selects_the_complete_chapter_18_prefix() -> None:
    pages = tuple(
        PdfPage(
            page_number=400 + section,
            text=f"18−{section}−1. SECTION {section}\nPolicy text for section {section}.\n",
        )
        for section in range(1, 27)
    )

    cards = extract_faa_order_cards(
        pages,
        section_prefixes=DEFAULT_SECTION_PREFIXES,
    )

    assert len(cards) == 26
    assert {card.section_id for card in cards} == {
        f"18-{section}" for section in range(1, 27)
    }


def test_recursive_extraction_chunks_preserve_parent_and_exact_source_spans() -> None:
    body = " ".join(f"token{index}." for index in range(900))
    package = build_faa_order_source_package(
        (
            PdfPage(
                page_number=410,
                text=f"18−10−1. POLICY\n{body}\n",
            ),
        ),
        pdf_sha256="d" * 64,
        pdf_byte_count=4321,
        max_chunk_tokens=500,
        chunk_overlap_tokens=50,
    )

    chunks = package.extraction_chunks
    assert len(chunks) >= 2
    assert all(chunk.token_count <= 500 for chunk in chunks)
    assert all(chunk.paragraph_id == "18-10-1" for chunk in chunks)
    assert chunks[0].char_end > chunks[1].char_start
    assert all(
        package.source_version.content[chunk.char_start : chunk.char_end]
        == chunk.evidence_text
        for chunk in chunks
    )
    assert all(chunk.parent_evidence_ref == package.cards[0].evidence_ref for chunk in chunks)
    assert build_faa_order_extraction_chunks(
        package.cards,
        max_tokens=500,
        overlap_tokens=50,
    )


def test_local_chapter_18_pdf_has_26_sections_and_159_numbered_paragraphs() -> None:
    pdf_path = Path("data/raw/faa_orders/JO_7210.3EE_2025-02-20.pdf")
    if not pdf_path.exists():
        pytest.skip("pinned FAA source is not installed in this checkout")

    package = load_faa_order_source_package(pdf_path)

    assert len({card.section_id for card in package.cards}) == 26
    assert len(package.cards) == 159
    assert package.extraction_chunks
