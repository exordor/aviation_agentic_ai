from pathlib import Path

import pytest

from aviation_agentic_ai.chunking import chunks as chunk_module
from aviation_agentic_ai.chunking.chunks import build_chunks, build_chunks_from_normalized_pdf_document
from aviation_agentic_ai.reporting import pdf_extraction
from aviation_agentic_ai.sources import docling_backend, pdf_hybrid
from aviation_agentic_ai.sources.pdf_hybrid import repair_docling_text_with_pymupdf
from aviation_agentic_ai.sources.pymupdf_backend import PyMuPDFBlock, PyMuPDFPageText
from aviation_agentic_ai.utils.pdf import PdfPage


def test_hybrid_repair_uses_pymupdf_spaced_reference() -> None:
    assert pdf_hybrid.EXPLICIT_DOCLING_REPAIR_REPLACEMENTS["ORESSURE"] == "PRESSURE"
    repaired, repairs, warnings = repair_docling_text_with_pymupdf(
        "Angleofattack and ORESSURE",
        "Angle of attack and PRESSURE are visible in the source.",
    )

    assert "Angle of attack" in repaired
    assert "PRESSURE" in repaired
    assert repairs
    assert "merged_aviation_term" in warnings


def test_hybrid_repair_leaves_uncertain_text_unchanged() -> None:
    repaired, repairs, warnings = repair_docling_text_with_pymupdf(
        "Unclearmergedtoken",
        "A page with unrelated text.",
    )

    assert repaired == "Unclearmergedtoken"
    assert repairs == []
    assert "docling_text_not_aligned_to_pymupdf_page" in warnings


class _FallbackMarkdownItem:
    text = ""

    def export_to_markdown(self, doc=None) -> str:
        if doc is not None:
            raise TypeError("doc argument unsupported")
        return "Fallback markdown"


class _BrokenMarkdownItem:
    text = ""

    def export_to_markdown(self, doc=None) -> str:
        _ = doc
        raise RuntimeError("broken export")


def test_docling_item_text_records_expected_markdown_fallback_diagnostic() -> None:
    text, diagnostic = docling_backend._item_text_and_diagnostic(
        _FallbackMarkdownItem(),
        object(),
    )

    assert text == "Fallback markdown"
    assert diagnostic == "export_to_markdown_doc_argument_unsupported"


def test_docling_item_text_does_not_swallow_unexpected_export_errors() -> None:
    with pytest.raises(RuntimeError, match="broken export"):
        docling_backend._item_text_and_diagnostic(_BrokenMarkdownItem(), object())


def test_docling_section_headers_create_chunk_boundaries_without_heuristic(monkeypatch) -> None:
    monkeypatch.setattr(
        chunk_module,
        "_is_heading",
        lambda _line: (_ for _ in ()).throw(AssertionError("_is_heading should not run")),
    )
    document = {
        "metadata": {
            "document_id": "doc",
            "source_path": "data/raw/doc.pdf",
            "pdf_backend": "hybrid_docling_pymupdf",
            "structure_backend": "docling_layout_labels",
            "text_backend": "pymupdf_text_reference",
            "text_fidelity_authority": True,
        },
        "items": [
            {
                "item_id": "i0",
                "page": 0,
                "label": "SECTION_HEADER",
                "text": "Lift",
                "level": 1,
            },
            {
                "item_id": "i1",
                "page": 0,
                "label": "TEXT",
                "text": "Air flows over a wing.",
                "level": 1,
                "source_text_trace": {
                    "docling_item_id": "i1",
                    "pymupdf_page": 0,
                    "pymupdf_reference_available": True,
                },
            },
            {
                "item_id": "i2",
                "page": 0,
                "label": "TABLE",
                "text": "| Angle | Lift |",
                "level": 1,
            },
        ],
    }

    chunks = build_chunks_from_normalized_pdf_document(document, strategy="structure_aware_large")

    assert chunks
    assert chunks[0].section == "Lift"
    assert chunks[0].metadata["source_backend"] == "hybrid_docling_pymupdf"
    assert chunks[0].metadata["structure_backend"] == "docling_layout_labels"
    assert chunks[0].metadata["text_backend"] == "pymupdf_text_reference"
    assert chunks[-1].metadata["table_item_ids"] == ["i2"]


def test_hybrid_document_records_not_run_when_docling_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(pdf_hybrid, "docling_available", lambda: False)
    monkeypatch.setattr(
        pdf_hybrid,
        "timed_pymupdf_extraction",
        lambda *_args, **_kwargs: (
            [PyMuPDFPageText(page_number=0, text="Introduction", sorted_text="Introduction")],
            [],
            [],
            0.01,
        ),
    )

    document = pdf_hybrid.build_hybrid_pdf_document("data/raw/doc.pdf")

    assert document["metadata"]["docling_available"] is False
    assert document["metadata"]["status"] == "docling_unavailable_fallback_only"
    assert document["items"] == []


def test_legacy_pymupdf_structure_chunks_are_marked_as_legacy(monkeypatch) -> None:
    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(page_number=0, text="Lift Section\nAir flows over a wing.")
        ],
    )

    chunks = build_chunks("data/raw/source.pdf", strategy="structure_aware_large")

    assert chunks
    assert chunks[0].metadata["source_backend"] == "pymupdf_text_legacy"
    assert chunks[0].metadata["structure_backend"] == "pymupdf_heading_heuristic_legacy"
    assert chunks[0].metadata["backend_status"] == "legacy_structure_unreliable"


class _FakeLabel:
    def __init__(self, name: str) -> None:
        self.name = name


class _FakeProv:
    page_no = 1
    bbox = None


class _FakeItem:
    def __init__(self, label: str, text: str) -> None:
        self.label = _FakeLabel(label)
        self.text = text
        self.prov = [_FakeProv()]


class _FakeDocument:
    pages = {1: object()}

    def iterate_items(self):
        for item in [
            _FakeItem("SECTION_HEADER", "Introduction"),
            _FakeItem("SECTION_HEADER", "Structure of the Atmosphere"),
            _FakeItem("TEXT", "Angleofattack appears here."),
        ]:
            yield item, 1

    def export_to_markdown(self) -> str:
        return "# Introduction\n\nAngleofattack appears here."


class _FakeResult:
    document = _FakeDocument()
    status = "SUCCESS"


def test_pdf_extraction_comparison_writes_reports_with_mocked_backends(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        pdf_extraction,
        "timed_pymupdf_extraction",
        lambda *_args, **_kwargs: (
            [
                PyMuPDFPageText(
                    page_number=0,
                    text=(
                        "Introduction\nStructure of the Atmosphere\n"
                        "Angle of attack appears here."
                    ),
                    sorted_text=(
                        "Introduction\nStructure of the Atmosphere\n"
                        "Angle of attack appears here."
                    ),
                )
            ],
            [],
            [PyMuPDFBlock(page_number=0, text="Introduction", block_no=0, block_type=0, bbox={})],
            0.01,
        ),
    )
    monkeypatch.setattr(
        pdf_extraction,
        "timed_docling_conversion",
        lambda *_args, **_kwargs: (_FakeResult(), 0.02, ""),
    )

    json_path, md_path, result = pdf_extraction.write_pdf_extraction_comparison(
        tmp_path / "doc.pdf",
        tmp_path,
        normalized_output_path=tmp_path / "normalized.json",
        reviews_dir=tmp_path / "reviews",
    )

    assert json_path.exists()
    assert md_path.exists()
    assert (tmp_path / "pdf_hybrid_repair_report.json").exists()
    assert (tmp_path / "reviews" / "pdf_extraction_strategy_update.json").exists()
    assert result["backends"]["docling_structure"]["gt_headings_labeled_as_section_header"] == 2
    assert result["backends"]["hybrid_docling_pymupdf"]["repaired_artifact_count"] >= 1
