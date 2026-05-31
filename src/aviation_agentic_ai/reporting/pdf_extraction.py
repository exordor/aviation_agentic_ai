from __future__ import annotations

from collections import Counter
from pathlib import Path
from time import perf_counter
from typing import Any

from aviation_agentic_ai.chunking.chunks import (
    SourceChunk,
    build_chunks,
    build_chunks_for_pdf_backend,
    write_chunks_jsonl,
)
from aviation_agentic_ai.evaluation.gold import GoldLabel, load_gold_labels
from aviation_agentic_ai.evaluation.metrics import aggregate_retrieval_metrics, retrieval_metrics
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import write_json_report
from aviation_agentic_ai.sources.docling_backend import (
    detect_docling_text_artifact_warnings,
    normalize_docling_document,
    timed_docling_conversion,
)
from aviation_agentic_ai.sources.pdf_backends import (
    DOCLING_STRUCTURE,
    HYBRID_DOCLING_PYMUPDF,
    PYMUPDF_BLOCKS,
    PYMUPDF_TEXT_LEGACY,
    PYMUPDF_TEXT_SORT,
    pdf_backend_roles,
)
from aviation_agentic_ai.sources.pdf_hybrid import (
    build_hybrid_repair_report,
    normalize_hybrid_items,
)
from aviation_agentic_ai.sources.pymupdf_backend import (
    PyMuPDFPageText,
    timed_pymupdf_extraction,
)
from aviation_agentic_ai.utils.io import write_json_document
from aviation_agentic_ai.utils.text import tokenize_terms


GOLD_HEADING_SAMPLE = (
    "Introduction",
    "Structure of the Atmosphere",
    "Air is a Fluid",
    "Viscosity",
    "Friction",
    "Pressure Altitude",
    "Density Altitude",
    "Effect of Pressure on Density",
    "Effect of Temperature on Density",
    "Effect of Humidity (Moisture) on Density",
    "Theories in the Production of Lift",
    "Newton's Basic Laws of Motion",
)


def _normalize(text: str) -> str:
    return " ".join(str(text).lower().split())


def _compact(text: str) -> str:
    return "".join(str(text).lower().split())


def _is_legacy_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 90:
        return False
    if stripped.endswith((".", ",", ";", ":")):
        return False
    words = stripped.split()
    title_words = sum(1 for word in words if word[:1].isupper())
    return title_words >= max(1, len(words) // 2) or stripped[:1].isdigit()


def _legacy_heading_candidates(pages: list[PyMuPDFPageText], *, sorted_text: bool) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for page in pages:
        text = page.sorted_text if sorted_text and page.sorted_text else page.text
        for line_index, line in enumerate(text.splitlines()):
            stripped = " ".join(line.split())
            if _is_legacy_heading(stripped):
                candidates.append(
                    {
                        "text": stripped,
                        "page": page.page_number,
                        "line_index": line_index,
                        "label": "HEURISTIC_HEADING",
                    }
                )
    return candidates


def _block_heading_candidates(blocks: list[Any]) -> list[dict[str, Any]]:
    candidates = []
    for block in blocks:
        text = " ".join(str(block.text).split())
        if _is_legacy_heading(text):
            candidates.append(
                {
                    "text": text,
                    "page": block.page_number,
                    "block_no": block.block_no,
                    "label": "PYMUPDF_BLOCK_HEADING_CANDIDATE",
                }
            )
    return candidates


def _items_within_page_limit(
    items: list[dict[str, Any]],
    *,
    max_pages: int,
) -> list[dict[str, Any]]:
    return [
        item
        for item in items
        if item.get("page") is None or int(item.get("page", 0)) < max_pages
    ]


def _docling_header_candidates(
    items: list[dict[str, Any]],
    *,
    max_pages: int | None = None,
) -> list[dict[str, Any]]:
    scoped_items = _items_within_page_limit(items, max_pages=max_pages) if max_pages else items
    return [
        {
            "text": str(item.get("text", "")),
            "page": item.get("page"),
            "item_id": item.get("item_id"),
            "label": "SECTION_HEADER",
            "level": item.get("level"),
        }
        for item in scoped_items
        if item.get("label") == "SECTION_HEADER"
    ]


def _matched_gold_headings(candidates: list[dict[str, Any]]) -> set[str]:
    candidate_texts = {_normalize(candidate.get("text", "")) for candidate in candidates}
    return {heading for heading in GOLD_HEADING_SAMPLE if _normalize(heading) in candidate_texts}


def _line_wrapped_fragment_count(candidates: list[dict[str, Any]]) -> int:
    gold = [_normalize(item) for item in GOLD_HEADING_SAMPLE]
    count = 0
    for candidate in candidates:
        text = _normalize(candidate.get("text", ""))
        if text in gold:
            continue
        if any(text and (heading.startswith(text) or heading.endswith(text)) for heading in gold):
            count += 1
    return count


def _table_false_heading_count(candidates: list[dict[str, Any]], matched: set[str]) -> int:
    count = 0
    for candidate in candidates:
        text = str(candidate.get("text", ""))
        if any(_normalize(text) == _normalize(heading) for heading in matched):
            continue
        page = candidate.get("page")
        table_like = (
            str(page) in {"1", "2"}
            or text.isdigit()
            or any(token in text.lower() for token in ("millibars", "pressure", "mercury"))
        )
        count += int(table_like)
    return count


def _page_number_false_heading_count(candidates: list[dict[str, Any]], matched: set[str]) -> int:
    return sum(
        1
        for candidate in candidates
        if str(candidate.get("text", "")).strip().isdigit()
        and not any(
            _normalize(candidate.get("text", "")) == _normalize(heading) for heading in matched
        )
    )


def _section_hierarchy_validity(candidates: list[dict[str, Any]]) -> float:
    order = [_normalize(candidate.get("text", "")) for candidate in candidates]
    positions = [order.index(_normalize(heading)) for heading in GOLD_HEADING_SAMPLE if _normalize(heading) in order]
    if not positions:
        return 0.0
    return round(sum(1 for left, right in zip(positions, positions[1:]) if left < right) / max(len(positions) - 1, 1), 4)


def _heading_metrics(
    *,
    backend: str,
    candidates: list[dict[str, Any]],
    text_corpus: str,
    runtime_s: float,
    table_detection_count: int = 0,
    text_artifact_count: int = 0,
    repaired_artifact_count: int = 0,
) -> dict[str, Any]:
    matched = _matched_gold_headings(candidates)
    false_count = max(0, len(candidates) - len(matched))
    precision = round(len(matched) / len(candidates), 4) if candidates else 0.0
    recall = round(len(matched) / len(GOLD_HEADING_SAMPLE), 4)
    f1 = round((2 * precision * recall) / (precision + recall), 4) if precision + recall else 0.0
    text_compact = _compact(text_corpus)
    found_as_text = [
        heading for heading in GOLD_HEADING_SAMPLE if _compact(heading) in text_compact
    ]
    return {
        "backend": backend,
        "heading_candidates": len(candidates),
        "heading_precision": precision,
        "heading_recall": recall,
        "heading_f1": f1,
        "false_heading_count": false_count,
        "table_false_heading_count": _table_false_heading_count(candidates, matched),
        "page_number_false_heading_count": _page_number_false_heading_count(candidates, matched),
        "line_wrapped_heading_fragment_count": _line_wrapped_fragment_count(candidates),
        "gt_headings_found_as_text": len(found_as_text),
        "gt_headings_labeled_as_section_header": len(matched)
        if backend in {DOCLING_STRUCTURE, HYBRID_DOCLING_PYMUPDF}
        else 0,
        "matched_gold_headings": sorted(matched),
        "missing_gold_headings": [
            heading for heading in GOLD_HEADING_SAMPLE if heading not in matched
        ],
        "section_hierarchy_validity": _section_hierarchy_validity(candidates),
        "table_detection_count": table_detection_count,
        "runtime_s": runtime_s,
        "text_artifact_count": text_artifact_count,
        "repaired_artifact_count": repaired_artifact_count,
        "sample_false_headings": [
            candidate
            for candidate in candidates
            if candidate.get("text") not in matched
        ][:12],
    }


def build_pdf_extraction_strategy_update(comparison: dict[str, Any]) -> dict[str, Any]:
    legacy = comparison["backends"].get(PYMUPDF_TEXT_LEGACY, {})
    docling = comparison["backends"].get(DOCLING_STRUCTURE, {})
    hybrid = comparison["backends"].get(HYBRID_DOCLING_PYMUPDF, {})
    return {
        "metadata": {
            "report_name": "pdf_extraction_strategy_update",
            "old_backend": "PyMuPDF text + heuristic heading detection",
            "new_recommended_backend": "Docling structure + PyMuPDF text fidelity",
            "recommended_backend_id": HYBRID_DOCLING_PYMUPDF,
            "status": "candidate_default_not_final",
            "human_review": False,
            "external_expert_certified": False,
        },
        "evidence_summary": {
            "pymupdf_legacy_false_heading_count": legacy.get("false_heading_count"),
            "pymupdf_legacy_heading_precision": legacy.get("heading_precision"),
            "docling_heading_recall": docling.get("heading_recall"),
            "docling_section_headers": docling.get("heading_candidates"),
            "hybrid_repaired_artifacts": hybrid.get("repaired_artifact_count"),
        },
        "decision": {
            "pymupdf_heuristic_status": "demoted_to_legacy_baseline_only",
            "docling_status": "primary_structure_extractor",
            "pymupdf_text_status": "text_fidelity_reference_and_fast_fallback",
            "hybrid_status": "candidate_default_for_structure_aware_pdf_chunking_after_downstream_validation",
        },
        "remaining_risks": [
            "Docling word merging",
            "Docling runtime and model availability",
            "table label ambiguity",
            "chunk ID compatibility",
            "downstream retrieval must be regenerated before scientific claims change",
        ],
        "backend_roles": {name: role.to_dict() for name, role in pdf_backend_roles().items()},
    }


def _strategy_update_markdown(result: dict[str, Any]) -> str:
    evidence = result["evidence_summary"]
    decision = result["decision"]
    lines = [
        "# PDF Extraction Strategy Update",
        "",
        "## Decision",
        "",
        f"- PyMuPDF heuristic status: `{decision['pymupdf_heuristic_status']}`",
        f"- Docling status: `{decision['docling_status']}`",
        f"- PyMuPDF text status: `{decision['pymupdf_text_status']}`",
        f"- Hybrid status: `{decision['hybrid_status']}`",
        "",
        "## Evidence",
        "",
        f"- Legacy PyMuPDF false heading count: {evidence['pymupdf_legacy_false_heading_count']}",
        f"- Legacy PyMuPDF heading precision: {evidence['pymupdf_legacy_heading_precision']}",
        f"- Docling heading recall on gold sample: {evidence['docling_heading_recall']}",
        f"- Hybrid repaired artifacts: {evidence['hybrid_repaired_artifacts']}",
        "",
        "## Remaining Risks",
        "",
    ]
    lines.extend(f"- {risk}" for risk in result["remaining_risks"])
    lines.extend(
        [
            "",
            "This is internal engineering evidence. It is not human review, external "
            "aviation expert certification, or operational readiness evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def write_pdf_extraction_strategy_update(
    comparison: dict[str, Any],
    reviews_dir: str | Path,
) -> tuple[Path, Path, dict[str, Any]]:
    output_dir = Path(reviews_dir)
    result = build_pdf_extraction_strategy_update(comparison)
    json_path = write_json_report(result, output_dir / "pdf_extraction_strategy_update.json")
    md_path = output_dir / "pdf_extraction_strategy_update.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_strategy_update_markdown(result), encoding="utf-8")
    return json_path, md_path, result


def write_pdf_extraction_comparison(
    pdf_path: str | Path,
    output_dir: str | Path,
    *,
    normalized_output_path: str | Path | None = None,
    reviews_dir: str | Path | None = None,
    command: str = "aviation-ai report pdf-extraction-comparison",
) -> tuple[Path, Path, dict[str, Any]]:
    pdf = Path(pdf_path)
    output = Path(output_dir)
    pymupdf_pages_full, _words, blocks_full, pymupdf_runtime = timed_pymupdf_extraction(pdf)
    pymupdf_pages = [page for page in pymupdf_pages_full if page.page_number < 5]
    blocks = [block for block in blocks_full if block.page_number < 5]
    docling_result, docling_runtime, docling_error = timed_docling_conversion(pdf)
    pymupdf_text = "\n".join(page.text for page in pymupdf_pages)
    sorted_text = "\n".join(page.sorted_text for page in pymupdf_pages)

    backends = {
        PYMUPDF_TEXT_LEGACY: _heading_metrics(
            backend=PYMUPDF_TEXT_LEGACY,
            candidates=_legacy_heading_candidates(pymupdf_pages, sorted_text=False),
            text_corpus=pymupdf_text,
            runtime_s=pymupdf_runtime,
        ),
        PYMUPDF_TEXT_SORT: _heading_metrics(
            backend=PYMUPDF_TEXT_SORT,
            candidates=_legacy_heading_candidates(pymupdf_pages, sorted_text=True),
            text_corpus=sorted_text,
            runtime_s=pymupdf_runtime,
        ),
        PYMUPDF_BLOCKS: _heading_metrics(
            backend=PYMUPDF_BLOCKS,
            candidates=_block_heading_candidates(blocks),
            text_corpus=pymupdf_text,
            runtime_s=pymupdf_runtime,
        ),
    }

    normalized_docling: dict[str, Any] = {
        "metadata": {
            "docling_available": docling_result is not None,
            "docling_error": docling_error,
            "docling_runtime_s": docling_runtime,
        },
        "items": [],
    }
    hybrid_document: dict[str, Any] = {
        "metadata": {
            "pdf_backend": HYBRID_DOCLING_PYMUPDF,
            "docling_available": docling_result is not None,
            "docling_error": docling_error,
            "docling_runtime_s": docling_runtime,
            "pymupdf_runtime_s": pymupdf_runtime,
            "status": "docling_not_run",
        },
        "items": [],
    }
    if docling_result is not None:
        normalized_docling = normalize_docling_document(
            docling_result,
            document_id=pdf.stem,
            source_path=pdf,
            runtime_s=docling_runtime,
        )
        hybrid_items = normalize_hybrid_items(normalized_docling["items"], pymupdf_pages_full)
        repair_count = sum(len(item.get("repairs", [])) for item in hybrid_items)
        warning_count = sum(len(item.get("artifact_warnings", [])) for item in hybrid_items)
        hybrid_document = {
            "metadata": {
                **normalized_docling["metadata"],
                "pdf_backend": HYBRID_DOCLING_PYMUPDF,
                "structure_backend": "docling_layout_labels",
                "text_backend": "pymupdf_text_reference",
                "text_fidelity_authority": True,
                "pymupdf_runtime_s": pymupdf_runtime,
                "hybrid_repair_applied": repair_count > 0,
                "repair_count": repair_count,
                "text_artifact_warnings": warning_count,
                "status": "hybrid_docling_pymupdf_ready",
            },
            "items": hybrid_items,
            "hierarchy": [item for item in hybrid_items if item.get("label") == "SECTION_HEADER"],
            "tables": [item for item in hybrid_items if item.get("label") == "TABLE"],
            "lists": [
                item
                for item in hybrid_items
                if item.get("label") in {"LIST_ITEM", "ENUMERATION"}
            ],
        }
        docling_scoped_items = _items_within_page_limit(normalized_docling["items"], max_pages=5)
        hybrid_scoped_items = _items_within_page_limit(hybrid_items, max_pages=5)
        docling_text = "\n".join(str(item.get("text", "")) for item in docling_scoped_items)
        hybrid_text = "\n".join(str(item.get("text", "")) for item in hybrid_scoped_items)
        docling_candidates = _docling_header_candidates(normalized_docling["items"], max_pages=5)
        hybrid_candidates = _docling_header_candidates(hybrid_items, max_pages=5)
        backends[DOCLING_STRUCTURE] = _heading_metrics(
            backend=DOCLING_STRUCTURE,
            candidates=docling_candidates,
            text_corpus=docling_text,
            runtime_s=docling_runtime,
            table_detection_count=sum(
                1 for item in docling_scoped_items if item.get("label") == "TABLE"
            ),
            text_artifact_count=sum(
                len(detect_docling_text_artifact_warnings(str(item.get("text", ""))))
                for item in docling_scoped_items
            ),
        )
        backends[HYBRID_DOCLING_PYMUPDF] = _heading_metrics(
            backend=HYBRID_DOCLING_PYMUPDF,
            candidates=hybrid_candidates,
            text_corpus=hybrid_text,
            runtime_s=round(docling_runtime + pymupdf_runtime, 4),
            table_detection_count=sum(
                1 for item in hybrid_scoped_items if item.get("label") == "TABLE"
            ),
            text_artifact_count=sum(
                len(item.get("artifact_warnings", [])) for item in hybrid_scoped_items
            ),
            repaired_artifact_count=repair_count,
        )
    else:
        for backend in (DOCLING_STRUCTURE, HYBRID_DOCLING_PYMUPDF):
            backends[backend] = {
                "backend": backend,
                "status": "not_run",
                "docling_error": docling_error,
                "heading_precision": 0.0,
                "heading_recall": 0.0,
                "heading_f1": 0.0,
                "false_heading_count": 0,
                "runtime_s": docling_runtime,
            }

    normalized_path = Path(
        normalized_output_path
        or PROJECT_ROOT / "data" / "normalized" / f"{pdf.stem}.hybrid_docling_pymupdf.json"
    )
    write_json_document(hybrid_document, normalized_path)
    repair_report = build_hybrid_repair_report(hybrid_document)
    repair_json_path = write_json_report(
        repair_report,
        output / "pdf_hybrid_repair_report.json",
    )
    repair_md_path = output / "pdf_hybrid_repair_report.md"
    repair_md_path.parent.mkdir(parents=True, exist_ok=True)
    repair_md_path.write_text(_repair_report_markdown(repair_report), encoding="utf-8")

    result = {
        "metadata": {
            "report_name": "pdf_extraction_comparison",
            "command": command,
            "pdf_path": project_relative_path(pdf),
            "gold_heading_sample_total": len(GOLD_HEADING_SAMPLE),
            "normalized_hybrid_document": project_relative_path(normalized_path),
            "hybrid_repair_report_json": project_relative_path(repair_json_path),
            "hybrid_repair_report_md": project_relative_path(repair_md_path),
            "claim_policy": (
                "Docling is treated as structure authority for this document; PyMuPDF "
                "heuristic headings are legacy baseline only. No human/expert review is claimed."
            ),
        },
        "gold_heading_sample": list(GOLD_HEADING_SAMPLE),
        "backends": backends,
        "backend_roles": {name: role.to_dict() for name, role in pdf_backend_roles().items()},
    }
    json_path = write_json_report(result, output / "pdf_extraction_comparison.json")
    md_path = output / "pdf_extraction_comparison.md"
    md_path.write_text(_comparison_markdown(result), encoding="utf-8")
    write_pdf_extraction_strategy_update(
        result,
        reviews_dir or PROJECT_ROOT / "reports" / "reviews",
    )
    return json_path, md_path, result


def _repair_report_markdown(result: dict[str, Any]) -> str:
    metadata = result.get("metadata", {})
    lines = [
        "# PDF Hybrid Repair Report",
        "",
        f"- Total Docling items: {metadata.get('total_docling_items')}",
        f"- Repaired items: {metadata.get('repaired_items')}",
        f"- Unrepaired suspicious items: {metadata.get('unrepaired_suspicious_items')}",
        f"- Merged-word artifacts detected: {metadata.get('merged_word_artifacts_detected')}",
        f"- Table label ambiguities: {metadata.get('table_label_ambiguities')}",
        "",
        "Repairs are conservative and only use PyMuPDF text as the reference.",
        "",
        "## Repair Examples",
        "",
    ]
    examples = result.get("repair_examples", [])
    if not examples:
        lines.append("- No repairs were applied.")
    for example in examples:
        lines.append(
            f"- `{example.get('item_id')}` page={example.get('page')}: "
            f"{example.get('original_text')} -> {example.get('repaired_text')}"
        )
    lines.append("")
    return "\n".join(lines)


def _comparison_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# PDF Extraction Comparison",
        "",
        result["metadata"]["claim_policy"],
        "",
        "| Backend | Precision | Recall | F1 | False headings | Runtime s | Artifacts | Repairs |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for backend, data in result["backends"].items():
        lines.append(
            f"| `{backend}` | {data.get('heading_precision')} | "
            f"{data.get('heading_recall')} | {data.get('heading_f1')} | "
            f"{data.get('false_heading_count')} | {data.get('runtime_s')} | "
            f"{data.get('text_artifact_count', 0)} | {data.get('repaired_artifact_count', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- PyMuPDF plain-text heading heuristics are retained only as a legacy baseline.",
            "- Docling labels provide the structural authority for section/table/list boundaries.",
            "- The hybrid backend uses PyMuPDF to detect and conservatively repair Docling text artifacts.",
            "- Downstream retrieval claims require the separate PDF backend chunking comparison.",
            "",
        ]
    )
    return "\n".join(lines)


def _chunk_file_name(pdf_path: str | Path, backend: str, strategy: str) -> str:
    return f"{Path(pdf_path).stem}.{backend}.{strategy}.jsonl"


def _lexical_hits(question: str, chunks: list[SourceChunk], *, top_k: int = 10) -> list[dict[str, Any]]:
    query_terms = tokenize_terms(question, stopwords=None)
    scored: list[tuple[float, SourceChunk]] = []
    for chunk in chunks:
        terms = tokenize_terms(chunk.text, stopwords=None)
        if not terms:
            score = 0.0
        else:
            overlap = len(query_terms & terms)
            score = overlap / max(len(query_terms), 1)
        scored.append((score, chunk))
    ordered = sorted(scored, key=lambda item: (-item[0], item[1].chunk_id))
    return [
        {
            "chunk_id": chunk.chunk_id,
            "page": chunk.page,
            "text": chunk.text,
            "score": round(score, 6),
            "section": chunk.section,
        }
        for score, chunk in ordered[:top_k]
    ]


def _evidence_match_rates(labels: list[GoldLabel], chunks: list[SourceChunk]) -> dict[str, Any]:
    supported = [label for label in labels if not label.expected_abstention]
    exact_hits = 0
    normalized_hits = 0
    corpus = "\n".join(chunk.text for chunk in chunks)
    normalized_corpus = _normalize(corpus)
    for label in supported:
        spans = [span.text for span in label.evidence_spans if span.text]
        exact_hits += int(any(span in corpus for span in spans))
        normalized_hits += int(any(_normalize(span) in normalized_corpus for span in spans))
    denominator = len(supported) or 1
    return {
        "evidence_span_exact_match_rate": round(exact_hits / denominator, 4),
        "evidence_normalized_match_rate": round(normalized_hits / denominator, 4),
    }


def _strategy_chunk_summary(
    *,
    name: str,
    backend: str,
    chunks: list[SourceChunk],
    labels: list[GoldLabel],
    runtime_s: float,
    chunks_path: Path,
) -> dict[str, Any]:
    supported = [label for label in labels if not label.expected_abstention]
    metric_items = []
    records = []
    for label in supported:
        hits = _lexical_hits(label.question or label.answer_key, chunks, top_k=10)
        metrics = retrieval_metrics(hits, label, top_k=10)
        metric_items.append(metrics)
        records.append(
            {
                "cq_id": label.cq_id,
                "question_type": label.question_type,
                "metrics": metrics,
                "top_hits": hits[:5],
            }
        )
    labels_by_type = Counter(label.question_type or "<missing>" for label in labels)
    aggregate = aggregate_retrieval_metrics(metric_items)
    backend_values = {
        key: sorted(
            {
                str(chunk.metadata.get(key))
                for chunk in chunks
                if chunk.metadata.get(key) not in (None, "")
            }
        )
        for key in ("source_backend", "structure_backend", "text_backend", "backend_status")
    }
    return {
        "strategy": name,
        "backend": backend,
        "chunks_path": project_relative_path(chunks_path),
        "chunks_total": len(chunks),
        "chunking": _chunk_stats(chunks),
        "table_chunk_count": sum(1 for chunk in chunks if chunk.metadata.get("table_item_ids")),
        "section_chunk_count": sum(1 for chunk in chunks if chunk.section),
        "repair_count": sum(int(chunk.metadata.get("repair_count", 0)) for chunk in chunks),
        "runtime_s": runtime_s,
        "labels_total": len(labels),
        "supported_total": len(supported),
        "label_distribution": dict(sorted(labels_by_type.items())),
        "retrieval": aggregate,
        **_evidence_match_rates(labels, chunks),
        "kg_evidence_in_source_rate": "not_run",
        "backend_metadata": backend_values,
        "records": records[:20],
    }


def _percentile(values: list[int], percentile: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile)))
    return ordered[index]


def _chunk_stats(chunks: list[SourceChunk]) -> dict[str, Any]:
    lengths = [len(chunk.text) for chunk in chunks]
    tokens = [chunk.token_count or len(chunk.text.split()) for chunk in chunks]
    return {
        "chunk_count": len(chunks),
        "avg_chars": round(sum(lengths) / len(lengths), 2) if lengths else 0.0,
        "p95_chars": _percentile(lengths, 0.95),
        "avg_tokens": round(sum(tokens) / len(tokens), 2) if tokens else 0.0,
    }


def write_pdf_backend_chunking_comparison(
    pdf_path: str | Path,
    gold_labels_path: str | Path,
    chunks_dir: str | Path,
    output_dir: str | Path,
    *,
    max_labels: int | None = None,
    command: str = "aviation-ai report pdf-backend-chunking-comparison",
) -> tuple[Path, Path, dict[str, Any]]:
    pdf = Path(pdf_path)
    chunks_root = Path(chunks_dir)
    output = Path(output_dir)
    labels = list(load_gold_labels(gold_labels_path).values())
    if max_labels is not None:
        labels = labels[:max_labels]
    strategies = (
        ("legacy_pymupdf_structure_aware_large", PYMUPDF_TEXT_LEGACY, "structure_aware_large"),
        ("docling_structure_aware_large", DOCLING_STRUCTURE, "structure_aware_large"),
        ("hybrid_docling_pymupdf_structure_aware_large", HYBRID_DOCLING_PYMUPDF, "structure_aware_large"),
        ("recursive_medium_baseline", "pymupdf_recursive_medium", "recursive_medium"),
        ("fixed_large_baseline", "pymupdf_fixed_large", "fixed_large"),
    )
    summaries: dict[str, Any] = {}
    for name, backend, chunk_strategy in strategies:
        start = perf_counter()
        if backend in {PYMUPDF_TEXT_LEGACY, DOCLING_STRUCTURE, HYBRID_DOCLING_PYMUPDF}:
            chunks = build_chunks_for_pdf_backend(
                pdf,
                pdf_backend=backend,
                strategy=chunk_strategy,
            )
        else:
            chunks = build_chunks(pdf, strategy=chunk_strategy)
        runtime_s = round(perf_counter() - start, 4)
        chunks_path = chunks_root / _chunk_file_name(pdf, backend, chunk_strategy)
        write_chunks_jsonl(chunks, chunks_path)
        summaries[name] = _strategy_chunk_summary(
            name=name,
            backend=backend,
            chunks=chunks,
            labels=labels,
            runtime_s=runtime_s,
            chunks_path=chunks_path,
        )
    ranking = sorted(
        [
            {
                "strategy": name,
                "backend": summary["backend"],
                "recall_at_5": summary["retrieval"].get("recall_at_5", 0.0),
                "mrr_at_5": summary["retrieval"].get("mrr_at_5", 0.0),
                "context_recall": summary["retrieval"].get("context_recall", 0.0),
                "evidence_normalized_match_rate": summary.get(
                    "evidence_normalized_match_rate",
                    0.0,
                ),
            }
            for name, summary in summaries.items()
        ],
        key=lambda row: (
            -float(row["recall_at_5"]),
            -float(row["mrr_at_5"]),
            -float(row["context_recall"]),
            row["strategy"],
        ),
    )
    hybrid = summaries.get("hybrid_docling_pymupdf_structure_aware_large", {})
    hybrid_repair_count = hybrid.get("repair_count", 0)
    result = {
        "metadata": {
            "report_name": "pdf_backend_chunking_comparison",
            "command": command,
            "pdf_path": project_relative_path(pdf),
            "gold_labels_path": project_relative_path(gold_labels_path),
            "chunks_dir": project_relative_path(chunks_root),
            "labels_total": len(labels),
            "supported_total": sum(1 for label in labels if not label.expected_abstention),
            "recommended_default_backend": HYBRID_DOCLING_PYMUPDF,
            "recommended_default_status": "candidate_default_not_final",
            "interpretation_policy": (
                "Structure quality and retrieval quality are reported separately. "
                "No universal PDF backend superiority claim is made."
            ),
            "hybrid_repair_count": hybrid_repair_count,
        },
        "ranking": ranking,
        "strategies": summaries,
    }
    json_path = write_json_report(result, output / "pdf_backend_chunking_comparison.json")
    md_path = output / "pdf_backend_chunking_comparison.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_backend_chunking_markdown(result), encoding="utf-8")
    return json_path, md_path, result


def _backend_chunking_markdown(result: dict[str, Any]) -> str:
    metadata = result["metadata"]
    lines = [
        "# PDF Backend Chunking Comparison",
        "",
        metadata["interpretation_policy"],
        "",
        f"Recommended default backend: `{metadata['recommended_default_backend']}` "
        f"({metadata['recommended_default_status']}).",
        "",
        "| Strategy | Backend | Chunks | Recall@5 | MRR@5 | Context Recall | Repairs |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["ranking"]:
        summary = result["strategies"][row["strategy"]]
        lines.append(
            f"| `{row['strategy']}` | `{row['backend']}` | {summary['chunks_total']} | "
            f"{row['recall_at_5']} | {row['mrr_at_5']} | {row['context_recall']} | "
            f"{summary['repair_count']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Legacy PyMuPDF structure-aware chunks are a baseline for comparability.",
            "- Docling and hybrid chunks use Docling labels rather than PyMuPDF heading heuristics.",
            "- Hybrid repairs are counted separately from retrieval metrics.",
            "- Insufficient-evidence labels are excluded from supported-answer retrieval aggregates.",
            "",
        ]
    )
    return "\n".join(lines)
