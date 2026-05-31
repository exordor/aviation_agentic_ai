from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import fitz


@dataclass(frozen=True)
class PyMuPDFPageText:
    page_number: int
    text: str
    sorted_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PyMuPDFWord:
    page_number: int
    text: str
    block_no: int
    line_no: int
    word_no: int
    bbox: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PyMuPDFBlock:
    page_number: int
    text: str
    block_no: int
    block_type: int | None
    bbox: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_pymupdf_text(text: str) -> str:
    return " ".join(str(text).split())


def extract_pymupdf_pages_text(
    pdf_path: str | Path,
    *,
    max_pages: int | None = None,
    sorted_text: bool = True,
) -> list[PyMuPDFPageText]:
    pages: list[PyMuPDFPageText] = []
    with fitz.open(str(pdf_path)) as doc:
        for page_number, page in enumerate(doc):
            if max_pages is not None and page_number >= max_pages:
                break
            text = page.get_text("text")
            sorted_page_text = page.get_text("text", sort=True) if sorted_text else ""
            if text.strip() or sorted_page_text.strip():
                pages.append(
                    PyMuPDFPageText(
                        page_number=page_number,
                        text=text,
                        sorted_text=sorted_page_text,
                    )
                )
    return pages


def extract_pymupdf_words(
    pdf_path: str | Path,
    *,
    max_pages: int | None = None,
) -> list[PyMuPDFWord]:
    words: list[PyMuPDFWord] = []
    with fitz.open(str(pdf_path)) as doc:
        for page_number, page in enumerate(doc):
            if max_pages is not None and page_number >= max_pages:
                break
            for raw in page.get_text("words"):
                if len(raw) < 8:
                    continue
                x0, y0, x1, y1, text, block_no, line_no, word_no = raw[:8]
                if str(text).strip():
                    words.append(
                        PyMuPDFWord(
                            page_number=page_number,
                            text=str(text),
                            block_no=int(block_no),
                            line_no=int(line_no),
                            word_no=int(word_no),
                            bbox={
                                "x0": float(x0),
                                "y0": float(y0),
                                "x1": float(x1),
                                "y1": float(y1),
                            },
                        )
                    )
    return words


def extract_pymupdf_blocks(
    pdf_path: str | Path,
    *,
    max_pages: int | None = None,
) -> list[PyMuPDFBlock]:
    blocks: list[PyMuPDFBlock] = []
    with fitz.open(str(pdf_path)) as doc:
        for page_number, page in enumerate(doc):
            if max_pages is not None and page_number >= max_pages:
                break
            for raw in page.get_text("blocks"):
                if len(raw) < 5:
                    continue
                x0, y0, x1, y1, text = raw[:5]
                block_no = int(raw[5]) if len(raw) > 5 else len(blocks)
                block_type = int(raw[6]) if len(raw) > 6 else None
                if str(text).strip():
                    blocks.append(
                        PyMuPDFBlock(
                            page_number=page_number,
                            text=normalize_pymupdf_text(str(text)),
                            block_no=block_no,
                            block_type=block_type,
                            bbox={
                                "x0": float(x0),
                                "y0": float(y0),
                                "x1": float(x1),
                                "y1": float(y1),
                            },
                        )
                    )
    return blocks


def pymupdf_page_text_index(pages: list[PyMuPDFPageText]) -> dict[int, str]:
    return {page.page_number: normalize_pymupdf_text(page.text) for page in pages}


def timed_pymupdf_extraction(
    pdf_path: str | Path,
    *,
    max_pages: int | None = None,
) -> tuple[list[PyMuPDFPageText], list[PyMuPDFWord], list[PyMuPDFBlock], float]:
    start = perf_counter()
    pages = extract_pymupdf_pages_text(pdf_path, max_pages=max_pages)
    words = extract_pymupdf_words(pdf_path, max_pages=max_pages)
    blocks = extract_pymupdf_blocks(pdf_path, max_pages=max_pages)
    return pages, words, blocks, round(perf_counter() - start, 4)
