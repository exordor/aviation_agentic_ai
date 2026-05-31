from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from aviation_agentic_ai.paths import project_relative_path


@dataclass(frozen=True)
class DoclingItem:
    item_id: str
    page: int | None
    label: str
    text: str
    level: int | None
    parent_id: str | None
    bbox: dict[str, float] | None
    order: int
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def docling_available() -> bool:
    try:
        from docling.document_converter import DocumentConverter  # noqa: F401
    except Exception:
        return False
    return True


def convert_pdf_with_docling(pdf_path: str | Path) -> Any:
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    return converter.convert(Path(pdf_path))


def timed_docling_conversion(pdf_path: str | Path) -> tuple[Any | None, float, str]:
    start = perf_counter()
    try:
        result = convert_pdf_with_docling(pdf_path)
    except Exception as exc:
        return None, round(perf_counter() - start, 4), f"{type(exc).__name__}: {exc}"
    return result, round(perf_counter() - start, 4), ""


def _label_name(item: Any) -> str:
    label = getattr(item, "label", None)
    if label is None:
        return type(item).__name__.upper()
    return str(getattr(label, "name", getattr(label, "value", label))).upper()


def _item_text(item: Any, document: Any) -> str:
    text = getattr(item, "text", None)
    if text:
        return str(text)
    if hasattr(item, "export_to_markdown"):
        try:
            return str(item.export_to_markdown(doc=document))
        except TypeError:
            return str(item.export_to_markdown())
        except Exception:
            return ""
    return ""


def _bbox_to_dict(bbox: Any) -> dict[str, float] | None:
    if bbox is None:
        return None
    values: dict[str, float] = {}
    for source, target in (("l", "l"), ("t", "t"), ("r", "r"), ("b", "b")):
        value = getattr(bbox, source, None)
        if value is not None:
            values[target] = float(value)
    if not values:
        for source, target in (("x0", "x0"), ("y0", "y0"), ("x1", "x1"), ("y1", "y1")):
            value = getattr(bbox, source, None)
            if value is not None:
                values[target] = float(value)
    return values or None


def _item_page_and_bbox(item: Any) -> tuple[int | None, dict[str, float] | None]:
    prov = getattr(item, "prov", None)
    if not prov:
        return None, None
    first = prov[0]
    page_no = getattr(first, "page_no", None)
    page = int(page_no) - 1 if page_no is not None and int(page_no) > 0 else None
    return page, _bbox_to_dict(getattr(first, "bbox", None))


def _raw_item(item: Any) -> dict[str, Any]:
    return {
        "type": type(item).__name__,
        "label": _label_name(item),
        "has_text": bool(getattr(item, "text", "")),
        "has_provenance": bool(getattr(item, "prov", None)),
    }


def _parent_for_level(last_headers: dict[int, str], level: int | None) -> str | None:
    if level is None:
        return None
    for candidate in range(level - 1, 0, -1):
        if candidate in last_headers:
            return last_headers[candidate]
    return None


def extract_docling_items(result: Any) -> list[DoclingItem]:
    document = result.document
    items: list[DoclingItem] = []
    last_headers: dict[int, str] = {}
    for order, (item, level) in enumerate(document.iterate_items()):
        label = _label_name(item)
        text = _item_text(item, document).strip()
        if not text and label not in {"TABLE", "PICTURE"}:
            continue
        item_id = f"docling_item_{order:05d}"
        level_value = int(level) if level is not None else None
        parent_id = _parent_for_level(last_headers, level_value)
        page, bbox = _item_page_and_bbox(item)
        normalized = DoclingItem(
            item_id=item_id,
            page=page,
            label=label,
            text=text,
            level=level_value,
            parent_id=parent_id,
            bbox=bbox,
            order=order,
            raw=_raw_item(item),
        )
        items.append(normalized)
        if label == "SECTION_HEADER" and level_value is not None:
            last_headers[level_value] = item_id
            for stale in [key for key in last_headers if key > level_value]:
                del last_headers[stale]
    return items


def extract_docling_hierarchy(result: Any) -> list[dict[str, Any]]:
    return [
        {
            "item_id": item.item_id,
            "page": item.page,
            "text": item.text,
            "level": item.level,
            "parent_id": item.parent_id,
            "order": item.order,
        }
        for item in extract_docling_items(result)
        if item.label == "SECTION_HEADER"
    ]


def extract_docling_tables(result: Any) -> list[dict[str, Any]]:
    return [
        {
            "item_id": item.item_id,
            "page": item.page,
            "text": item.text,
            "level": item.level,
            "order": item.order,
        }
        for item in extract_docling_items(result)
        if item.label == "TABLE"
    ]


def extract_docling_lists(result: Any) -> list[dict[str, Any]]:
    return [
        {
            "item_id": item.item_id,
            "page": item.page,
            "text": item.text,
            "level": item.level,
            "parent_id": item.parent_id,
            "order": item.order,
        }
        for item in extract_docling_items(result)
        if item.label in {"LIST_ITEM", "ENUMERATION"}
    ]


def extract_docling_markdown(result: Any) -> str:
    return str(result.document.export_to_markdown())


MERGED_AVIATION_RE = re.compile(
    r"\b(?:Angleofattack|Lowangleofattack|angleofattack|Angleof|angleof)\b"
)
ALL_CAPS_PARTIAL_RE = re.compile(r"\b[A-Z]{3,}\b")


def detect_docling_text_artifact_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    if MERGED_AVIATION_RE.search(text):
        warnings.append("merged_aviation_term")
    long_tokens = [token for token in re.findall(r"\b\w+\b", text) if len(token) >= 28]
    if long_tokens:
        warnings.append("very_long_token")
    for token in ALL_CAPS_PARTIAL_RE.findall(text):
        if token in {"ORESSURE", "IRE"}:
            warnings.append(f"ocr_like_partial_word:{token}")
    return sorted(set(warnings))


def normalize_docling_document(
    result: Any,
    *,
    document_id: str,
    source_path: str | Path,
    runtime_s: float | None = None,
) -> dict[str, Any]:
    items = extract_docling_items(result)
    markdown = extract_docling_markdown(result)
    status = str(getattr(result, "status", "unknown"))
    normalized_items = []
    for item in items:
        row = item.to_dict()
        row["artifact_warnings"] = detect_docling_text_artifact_warnings(item.text)
        normalized_items.append(row)
    return {
        "metadata": {
            "document_id": document_id,
            "source_path": project_relative_path(source_path),
            "pdf_backend": "docling_structure",
            "structure_backend": "docling_layout_labels",
            "text_backend": "docling_text",
            "structure_authority": True,
            "text_fidelity_authority": False,
            "docling_available": True,
            "docling_status": status,
            "docling_runtime_s": runtime_s,
            "items_total": len(normalized_items),
            "section_headers_total": sum(
                1 for item in normalized_items if item["label"] == "SECTION_HEADER"
            ),
            "tables_total": sum(1 for item in normalized_items if item["label"] == "TABLE"),
            "lists_total": sum(
                1 for item in normalized_items if item["label"] in {"LIST_ITEM", "ENUMERATION"}
            ),
            "text_artifact_warnings": sum(
                len(item.get("artifact_warnings", [])) for item in normalized_items
            ),
        },
        "items": normalized_items,
        "hierarchy": [
            item
            for item in normalized_items
            if item.get("label") == "SECTION_HEADER"
        ],
        "tables": [item for item in normalized_items if item.get("label") == "TABLE"],
        "lists": [
            item
            for item in normalized_items
            if item.get("label") in {"LIST_ITEM", "ENUMERATION"}
        ],
        "markdown": markdown,
    }
