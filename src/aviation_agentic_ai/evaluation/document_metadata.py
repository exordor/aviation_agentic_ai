from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path


@dataclass(frozen=True)
class DocumentMetadata:
    document_id: str
    title: str
    source_type: str
    source_path: str
    chapter: str
    revision_date: str | None = None
    page_start: int | None = None
    page_end: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SectionRecord:
    section_id: str
    title: str
    level: int
    page_start: int
    page_end: int
    parent_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def document_metadata_from_pdf(
    pdf_path: str | Path,
    *,
    document_id: str | None = None,
    title: str | None = None,
    source_type: str = "faa_handbook_chapter",
    chapter: str = "4",
    revision_date: str | None = None,
    page_start: int | None = None,
    page_end: int | None = None,
) -> DocumentMetadata:
    path = Path(pdf_path)
    return DocumentMetadata(
        document_id=document_id or path.stem,
        title=title or path.stem.replace("_", " "),
        source_type=source_type,
        source_path=project_relative_path(path),
        chapter=chapter,
        revision_date=revision_date,
        page_start=page_start,
        page_end=page_end,
    )

