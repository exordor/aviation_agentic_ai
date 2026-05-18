from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass(frozen=True)
class PdfPage:
    page_number: int
    text: str


def extract_pages(pdf_path: str | Path, max_pages: int | None = None) -> Iterator[PdfPage]:
    """Yield non-empty text pages from a PDF with stable zero-based page numbers."""
    with fitz.open(str(pdf_path)) as doc:
        for page_number, page in enumerate(doc):
            if max_pages is not None and page_number >= max_pages:
                break
            text = page.get_text("text")
            if text.strip():
                yield PdfPage(page_number=page_number, text=text)
