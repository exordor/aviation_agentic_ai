from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PYMUPDF_TEXT_LEGACY = "pymupdf_text_legacy"
PYMUPDF_TEXT_SORT = "pymupdf_text_sort"
PYMUPDF_BLOCKS = "pymupdf_blocks"
DOCLING_STRUCTURE = "docling_structure"
HYBRID_DOCLING_PYMUPDF = "hybrid_docling_pymupdf"

PDF_BACKENDS = (
    PYMUPDF_TEXT_LEGACY,
    PYMUPDF_TEXT_SORT,
    PYMUPDF_BLOCKS,
    DOCLING_STRUCTURE,
    HYBRID_DOCLING_PYMUPDF,
)


@dataclass(frozen=True)
class PdfBackendRole:
    name: str
    structure_backend: str
    text_backend: str
    structure_authority: bool
    text_fidelity_authority: bool
    status: str
    role: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["limitations"] = list(self.limitations)
        return data


def pdf_backend_roles() -> dict[str, PdfBackendRole]:
    return {
        PYMUPDF_TEXT_LEGACY: PdfBackendRole(
            name=PYMUPDF_TEXT_LEGACY,
            structure_backend="pymupdf_plain_text_heading_heuristic",
            text_backend="pymupdf_text",
            structure_authority=False,
            text_fidelity_authority=True,
            status="legacy_structure_unreliable",
            role="fast baseline and historical comparability",
            limitations=(
                "Plain text line breaks create false heading candidates.",
                "Heuristic heading detection is not a structural authority.",
            ),
        ),
        PYMUPDF_TEXT_SORT: PdfBackendRole(
            name=PYMUPDF_TEXT_SORT,
            structure_backend="pymupdf_sorted_text",
            text_backend="pymupdf_sorted_text",
            structure_authority=False,
            text_fidelity_authority=True,
            status="fast_fallback_not_structural_authority",
            role="fast fallback and text comparison",
            limitations=("Sorted text can improve reading order but does not label sections.",),
        ),
        PYMUPDF_BLOCKS: PdfBackendRole(
            name=PYMUPDF_BLOCKS,
            structure_backend="pymupdf_blocks",
            text_backend="pymupdf_blocks",
            structure_authority=False,
            text_fidelity_authority=True,
            status="block_signal_not_heading_authority",
            role="block-level diagnostic baseline",
            limitations=("Block boundaries are layout hints, not semantic headings.",),
        ),
        DOCLING_STRUCTURE: PdfBackendRole(
            name=DOCLING_STRUCTURE,
            structure_backend="docling_layout_labels",
            text_backend="docling_text",
            structure_authority=True,
            text_fidelity_authority=False,
            status="primary_structure_extractor",
            role="section/table/list/hierarchy extraction",
            limitations=(
                "Docling may introduce merged words or OCR-like boundary artifacts.",
                "Runtime and model availability are heavier than PyMuPDF.",
            ),
        ),
        HYBRID_DOCLING_PYMUPDF: PdfBackendRole(
            name=HYBRID_DOCLING_PYMUPDF,
            structure_backend="docling_layout_labels",
            text_backend="pymupdf_text_reference",
            structure_authority=True,
            text_fidelity_authority=True,
            status="candidate_default_not_final",
            role="Docling structure with PyMuPDF text-fidelity validation and repair",
            limitations=(
                "Repairs are conservative and only applied when PyMuPDF supports them.",
                "Downstream retrieval impact must be reported separately from structure quality.",
            ),
        ),
    }


def pdf_backend_role(name: str) -> PdfBackendRole:
    roles = pdf_backend_roles()
    if name not in roles:
        raise ValueError(f"Unsupported PDF backend: {name}")
    return roles[name]
