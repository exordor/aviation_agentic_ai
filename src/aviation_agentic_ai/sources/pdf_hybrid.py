from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.sources.docling_backend import (
    detect_docling_text_artifact_warnings,
    docling_available,
    normalize_docling_document,
    timed_docling_conversion,
)
from aviation_agentic_ai.sources.pdf_backends import HYBRID_DOCLING_PYMUPDF
from aviation_agentic_ai.sources.pymupdf_backend import (
    PyMuPDFPageText,
    pymupdf_page_text_index,
    timed_pymupdf_extraction,
)


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def align_docling_item_to_pymupdf_page(
    item: dict[str, Any],
    pymupdf_pages: list[PyMuPDFPageText],
) -> int | None:
    page = item.get("page")
    if isinstance(page, int) and any(candidate.page_number == page for candidate in pymupdf_pages):
        return page
    item_compact = _compact(str(item.get("text", "")))
    if not item_compact:
        return None
    for candidate in pymupdf_pages:
        if item_compact in _compact(candidate.text):
            return candidate.page_number
    return None


def _word_sequence_replacements(page_text: str) -> dict[str, str]:
    words = re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)?", page_text)
    replacements: dict[str, str] = {}
    for start in range(len(words)):
        for width in range(2, 6):
            phrase_words = words[start : start + width]
            if len(phrase_words) < 2:
                continue
            phrase = " ".join(phrase_words)
            compact = _compact(phrase)
            if len(compact) >= 8:
                replacements.setdefault(compact, phrase)
    return replacements


def _reference_span(page_text: str, phrase: str) -> dict[str, int] | None:
    index = page_text.lower().find(phrase.lower())
    if index < 0:
        return None
    return {"char_start": index, "char_end": index + len(phrase)}


def detect_docling_text_artifacts(item_text: str, pymupdf_page_text: str) -> list[str]:
    warnings = detect_docling_text_artifact_warnings(item_text)
    if item_text and _compact(item_text) and _compact(item_text) not in _compact(pymupdf_page_text):
        warnings.append("docling_text_not_aligned_to_pymupdf_page")
    return sorted(set(warnings))


def repair_docling_text_with_pymupdf(
    item_text: str,
    pymupdf_page_text: str,
) -> tuple[str, list[dict[str, Any]], list[str]]:
    warnings = detect_docling_text_artifacts(item_text, pymupdf_page_text)
    if not item_text.strip() or not pymupdf_page_text.strip():
        return item_text, [], warnings

    repaired = item_text
    repairs: list[dict[str, Any]] = []
    replacements = _word_sequence_replacements(pymupdf_page_text)
    token_matches = list(re.finditer(r"\b[A-Za-z]{6,}\b", item_text))
    for match in token_matches:
        token = match.group(0)
        replacement = replacements.get(_compact(token))
        if not replacement or replacement == token:
            continue
        repaired = re.sub(rf"\b{re.escape(token)}\b", replacement, repaired, count=1)
        repairs.append(
            {
                "original_text": token,
                "repaired_text": replacement,
                "repair_reason": "pymupdf_spaced_word_sequence_match",
                "confidence": "high",
                "pymupdf_reference_span": _reference_span(pymupdf_page_text, replacement),
            }
        )

    explicit_replacements = {"ORESSURE": "PRESSURE"}
    for bad, good in explicit_replacements.items():
        if bad in repaired and re.search(rf"\b{re.escape(good)}\b", pymupdf_page_text):
            repaired = repaired.replace(bad, good)
            repairs.append(
                {
                    "original_text": bad,
                    "repaired_text": good,
                    "repair_reason": "pymupdf_exact_reference_word_present",
                    "confidence": "medium",
                    "pymupdf_reference_span": _reference_span(pymupdf_page_text, good),
                }
            )

    return repaired, repairs, warnings


def normalize_hybrid_items(
    docling_items: list[dict[str, Any]],
    pymupdf_pages: list[PyMuPDFPageText],
) -> list[dict[str, Any]]:
    page_index = pymupdf_page_text_index(pymupdf_pages)
    document_reference_text = "\n".join(page.text for page in pymupdf_pages)
    hybrid_items: list[dict[str, Any]] = []
    for item in docling_items:
        aligned_page = align_docling_item_to_pymupdf_page(item, pymupdf_pages)
        pymupdf_text = page_index.get(aligned_page, "") if aligned_page is not None else ""
        original_text = str(item.get("text", ""))
        repaired_text, repairs, warnings = repair_docling_text_with_pymupdf(
            original_text,
            pymupdf_text,
        )
        reference_scope = "page"
        if not repairs and warnings and document_reference_text and document_reference_text != pymupdf_text:
            document_repaired, document_repairs, document_warnings = repair_docling_text_with_pymupdf(
                original_text,
                document_reference_text,
            )
            if document_repairs:
                repaired_text = document_repaired
                repairs = [
                    {**repair, "pymupdf_reference_scope": "document"}
                    for repair in document_repairs
                ]
                warnings = sorted(set([*warnings, *document_warnings]))
                reference_scope = "document_fallback"
        hybrid = {
            **item,
            "original_text": original_text,
            "text": repaired_text,
            "repaired_text": repaired_text,
            "hybrid_repair_applied": bool(repairs),
            "repairs": repairs,
            "artifact_warnings": warnings,
            "source_text_trace": {
                "docling_item_id": item.get("item_id"),
                "pymupdf_page": aligned_page,
                "pymupdf_reference_available": bool(pymupdf_text),
                "pymupdf_reference_scope": reference_scope,
            },
        }
        hybrid_items.append(hybrid)
    return hybrid_items


def build_hybrid_pdf_document(
    pdf_path: str | Path,
    document_id: str | None = None,
) -> dict[str, Any]:
    pdf = Path(pdf_path)
    doc_id = document_id or pdf.stem
    pymupdf_pages, pymupdf_words, pymupdf_blocks, pymupdf_runtime = timed_pymupdf_extraction(pdf)
    if not docling_available():
        return {
            "metadata": {
                "document_id": doc_id,
                "source_path": project_relative_path(pdf),
                "pdf_backend": HYBRID_DOCLING_PYMUPDF,
                "structure_backend": "docling_layout_labels",
                "text_backend": "pymupdf_text_reference",
                "structure_authority": False,
                "text_fidelity_authority": True,
                "docling_available": False,
                "docling_runtime_s": 0.0,
                "pymupdf_runtime_s": pymupdf_runtime,
                "status": "docling_unavailable_fallback_only",
                "error": "Docling import failed.",
            },
            "items": [],
            "pymupdf_pages": [page.to_dict() for page in pymupdf_pages],
        }

    result, docling_runtime, error = timed_docling_conversion(pdf)
    if result is None:
        return {
            "metadata": {
                "document_id": doc_id,
                "source_path": project_relative_path(pdf),
                "pdf_backend": HYBRID_DOCLING_PYMUPDF,
                "structure_backend": "docling_layout_labels",
                "text_backend": "pymupdf_text_reference",
                "structure_authority": False,
                "text_fidelity_authority": True,
                "docling_available": True,
                "docling_runtime_s": docling_runtime,
                "pymupdf_runtime_s": pymupdf_runtime,
                "status": "docling_conversion_failed_fallback_only",
                "error": error,
            },
            "items": [],
            "pymupdf_pages": [page.to_dict() for page in pymupdf_pages],
        }

    docling_document = normalize_docling_document(
        result,
        document_id=doc_id,
        source_path=pdf,
        runtime_s=docling_runtime,
    )
    items = normalize_hybrid_items(docling_document["items"], pymupdf_pages)
    repair_count = sum(len(item.get("repairs", [])) for item in items)
    warning_count = sum(len(item.get("artifact_warnings", [])) for item in items)
    return {
        "metadata": {
            **docling_document["metadata"],
            "pdf_backend": HYBRID_DOCLING_PYMUPDF,
            "structure_backend": "docling_layout_labels",
            "text_backend": "pymupdf_text_reference",
            "structure_authority": True,
            "text_fidelity_authority": True,
            "pymupdf_runtime_s": pymupdf_runtime,
            "pymupdf_pages_total": len(pymupdf_pages),
            "pymupdf_words_total": len(pymupdf_words),
            "pymupdf_blocks_total": len(pymupdf_blocks),
            "hybrid_repair_applied": repair_count > 0,
            "repair_count": repair_count,
            "text_artifact_warnings": warning_count,
            "status": "hybrid_docling_pymupdf_ready",
        },
        "items": items,
        "hierarchy": [item for item in items if item.get("label") == "SECTION_HEADER"],
        "tables": [item for item in items if item.get("label") == "TABLE"],
        "lists": [
            item
            for item in items
            if item.get("label") in {"LIST_ITEM", "ENUMERATION"}
        ],
        "pymupdf_pages": [page.to_dict() for page in pymupdf_pages],
        "pymupdf_blocks": [block.to_dict() for block in pymupdf_blocks],
    }


def build_hybrid_repair_report(document: dict[str, Any]) -> dict[str, Any]:
    items = document.get("items", [])
    repaired = [item for item in items if item.get("hybrid_repair_applied")]
    suspicious = [item for item in items if item.get("artifact_warnings")]
    page_counts: dict[str, dict[str, int]] = {}
    for item in items:
        page = str(item.get("page"))
        row = page_counts.setdefault(page, {"items": 0, "repairs": 0, "warnings": 0})
        row["items"] += 1
        row["repairs"] += len(item.get("repairs", []))
        row["warnings"] += len(item.get("artifact_warnings", []))
    return {
        "metadata": {
            **document.get("metadata", {}),
            "report_name": "pdf_hybrid_repair_report",
            "total_docling_items": len(items),
            "repaired_items": len(repaired),
            "unrepaired_suspicious_items": sum(
                1 for item in suspicious if not item.get("hybrid_repair_applied")
            ),
            "merged_word_artifacts_detected": sum(
                1
                for item in suspicious
                for warning in item.get("artifact_warnings", [])
                if warning == "merged_aviation_term"
            ),
            "table_label_ambiguities": sum(
                1
                for item in items
                if item.get("label") == "SECTION_HEADER"
                and re.search(r"\b(table|figure|pressure|millibars)\b", str(item.get("text", "")), re.I)
            ),
        },
        "page_level_repair_counts": page_counts,
        "repair_examples": [
            {
                "item_id": item.get("item_id"),
                "page": item.get("page"),
                "label": item.get("label"),
                "original_text": item.get("original_text"),
                "repaired_text": item.get("repaired_text"),
                "repairs": item.get("repairs", []),
            }
            for item in repaired[:10]
        ],
        "unrepaired_suspicious_examples": [
            {
                "item_id": item.get("item_id"),
                "page": item.get("page"),
                "label": item.get("label"),
                "text": item.get("text"),
                "artifact_warnings": item.get("artifact_warnings", []),
            }
            for item in suspicious
            if not item.get("hybrid_repair_applied")
        ][:10],
    }
