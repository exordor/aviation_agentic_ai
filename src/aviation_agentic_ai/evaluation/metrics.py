from __future__ import annotations

import math
import re
from typing import Any

from aviation_agentic_ai.evaluation.gold import EvidenceSpan, GoldLabel


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _gold_from_input(gold: GoldLabel | dict[str, Any] | int) -> GoldLabel:
    if isinstance(gold, GoldLabel):
        return gold
    if isinstance(gold, dict):
        return GoldLabel.from_dict(gold)
    return GoldLabel(cq_id="", source_document="", source_page=int(gold))


def _span_matches_hit(span: EvidenceSpan, hit: dict[str, Any]) -> bool:
    if int(hit.get("page", -1)) != span.page:
        return False
    if not span.text:
        return True
    return _normalize(span.text) in _normalize(str(hit.get("text", "")))


def _hit_matches_gold(hit: dict[str, Any], gold: GoldLabel) -> bool:
    level = gold.gold_level
    if gold.expected_abstention or level in {"no_answer", "none", "unsupported", "insufficient_evidence"}:
        return False
    if level == "span" and gold.evidence_spans:
        return any(_span_matches_hit(span, hit) for span in gold.evidence_spans)
    if level == "chunk" and gold.expected_chunk_ids:
        return str(hit.get("chunk_id", "")) in set(gold.expected_chunk_ids)
    if gold.evidence_spans:
        return any(_span_matches_hit(span, hit) for span in gold.evidence_spans)
    if gold.expected_chunk_ids:
        return str(hit.get("chunk_id", "")) in set(gold.expected_chunk_ids)
    if gold.source_page < 0:
        return False
    return int(hit.get("page", -1)) == gold.source_page


def _gold_context_units(gold: GoldLabel) -> list[tuple[str, Any]]:
    if gold.expected_abstention or gold.gold_level in {
        "no_answer",
        "none",
        "unsupported",
        "insufficient_evidence",
    }:
        return []
    if gold.evidence_spans:
        return [("span", span) for span in gold.evidence_spans]
    if gold.expected_chunk_ids:
        return [("chunk", str(chunk_id)) for chunk_id in gold.expected_chunk_ids]
    if gold.source_page >= 0:
        return [("page", int(gold.source_page))]
    return []


def _hit_matches_context_unit(hit: dict[str, Any], unit: tuple[str, Any]) -> bool:
    unit_type, value = unit
    if unit_type == "span":
        return _span_matches_hit(value, hit)
    if unit_type == "chunk":
        return str(hit.get("chunk_id", "")) == str(value)
    if unit_type == "page":
        return int(hit.get("page", -1)) == int(value)
    return False


def _matched_context_units(
    hits: list[dict[str, Any]],
    gold: GoldLabel,
) -> set[int]:
    units = _gold_context_units(gold)
    matched: set[int] = set()
    for unit_index, unit in enumerate(units):
        if any(_hit_matches_context_unit(hit, unit) for hit in hits):
            matched.add(unit_index)
    return matched


def _relevance_by_rank(hits: list[dict[str, Any]], gold: GoldLabel, k: int) -> list[int]:
    return [int(_hit_matches_gold(hit, gold)) for hit in hits[:k]]


def _recall_at_k(hits: list[dict[str, Any]], gold: GoldLabel, k: int) -> bool:
    return any(_relevance_by_rank(hits, gold, k))


def _precision_at_k(hits: list[dict[str, Any]], gold: GoldLabel, k: int) -> float:
    return round(sum(_relevance_by_rank(hits, gold, k)) / max(k, 1), 4)


def _context_precision_at_k(hits: list[dict[str, Any]], gold: GoldLabel, k: int) -> float:
    top_hits = hits[:k]
    if not top_hits:
        return 0.0
    relevant = sum(_relevance_by_rank(hits, gold, k))
    return round(relevant / len(top_hits), 4)


def _mrr_at_k(hits: list[dict[str, Any]], gold: GoldLabel, k: int) -> float:
    for rank, relevant in enumerate(_relevance_by_rank(hits, gold, k), start=1):
        if relevant:
            return round(1.0 / rank, 4)
    return 0.0


def _ndcg_at_k(hits: list[dict[str, Any]], gold: GoldLabel, k: int) -> float:
    relevance = _relevance_by_rank(hits, gold, k)
    dcg = sum(rel / math.log2(rank + 1) for rank, rel in enumerate(relevance, start=1))
    relevant_total = len(_gold_context_units(gold)) or int(any(relevance))
    ideal_relevant = min(relevant_total, k)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_relevant + 1))
    return round(dcg / idcg, 4) if idcg else 0.0


def _context_recall(hits: list[dict[str, Any]], gold: GoldLabel, k: int = 10) -> float:
    units = _gold_context_units(gold)
    if not units:
        return 1.0 if gold.expected_abstention else 0.0
    matched = _matched_context_units(hits[:k], gold)
    return round(len(matched) / len(units), 4)


def retrieval_metrics(
    hits: list[dict[str, Any]],
    gold: GoldLabel | dict[str, Any] | int,
    top_k: int = 5,
) -> dict[str, Any]:
    label = _gold_from_input(gold)
    top_hits = hits[:top_k]
    ranks = [
        index
        for index, hit in enumerate(top_hits, start=1)
        if _hit_matches_gold(hit, label)
    ]
    matched_hits = [top_hits[index - 1] for index in ranks]
    return {
        "gold_level": label.gold_level,
        "expected_abstention": label.expected_abstention,
        "recall_at_5": _recall_at_k(hits, label, 5),
        "recall_at_10": _recall_at_k(hits, label, 10),
        "precision_at_5": _precision_at_k(hits, label, 5),
        "precision_at_10": _precision_at_k(hits, label, 10),
        "mrr_at_5": _mrr_at_k(hits, label, 5),
        "mrr_at_10": _mrr_at_k(hits, label, 10),
        "ndcg_at_10": _ndcg_at_k(hits, label, 10),
        "context_precision_at_5": _context_precision_at_k(hits, label, 5),
        "context_recall": _context_recall(hits, label, 10),
        "first_relevant_rank": ranks[0] if ranks else None,
        "retrieved_chunk_ids": [str(hit.get("chunk_id", "")) for hit in top_hits],
        "retrieved_source_pages": [int(hit.get("page", -1)) for hit in top_hits],
        "matched_chunk_ids": [str(hit.get("chunk_id", "")) for hit in matched_hits],
        "matched_source_pages": [int(hit.get("page", -1)) for hit in matched_hits],
    }


def aggregate_retrieval_metrics(metric_items: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(metric_items) or 1
    return {
        "recall_at_5": round(
            sum(int(item.get("recall_at_5", False)) for item in metric_items) / denominator,
            4,
        ),
        "recall_at_10": round(
            sum(int(item.get("recall_at_10", False)) for item in metric_items)
            / denominator,
            4,
        ),
        "precision_at_5": round(
            sum(float(item.get("precision_at_5", 0.0)) for item in metric_items)
            / denominator,
            4,
        ),
        "precision_at_10": round(
            sum(float(item.get("precision_at_10", 0.0)) for item in metric_items)
            / denominator,
            4,
        ),
        "mrr_at_5": round(
            sum(float(item.get("mrr_at_5", 0.0)) for item in metric_items) / denominator,
            4,
        ),
        "mrr_at_10": round(
            sum(float(item.get("mrr_at_10", 0.0)) for item in metric_items) / denominator,
            4,
        ),
        "ndcg_at_10": round(
            sum(float(item.get("ndcg_at_10", 0.0)) for item in metric_items) / denominator,
            4,
        ),
        "context_precision_at_5": round(
            sum(float(item.get("context_precision_at_5", 0.0)) for item in metric_items)
            / denominator,
            4,
        ),
        "context_recall": round(
            sum(float(item.get("context_recall", 0.0)) for item in metric_items)
            / denominator,
            4,
        ),
    }


def kg_evidence_metrics(
    triples: list[dict[str, Any]],
    key_entities: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    normalized_entities = [_normalize(entity) for entity in key_entities if str(entity).strip()]
    covered_entities: list[str] = []
    for entity in normalized_entities:
        for triple in triples:
            haystack = _normalize(" ".join(str(value) for value in triple.values()))
            if entity and entity in haystack:
                covered_entities.append(entity)
                break

    provenance_fields = ("triple_id", "chunk_id", "page", "evidence_text")
    complete_count = 0
    invalid_count = 0
    unsupported_count = 0
    for triple in triples:
        has_all_provenance = all(triple.get(field) not in (None, "") for field in provenance_fields)
        complete_count += int(has_all_provenance)
        invalid_count += int(not has_all_provenance)
        unsupported_count += int(bool(triple.get("unsupported") or triple.get("validation_error")))

    denominator = len(triples) or 1
    coverage = bool(covered_entities) if normalized_entities else bool(triples)
    return {
        "evidence_coverage": coverage,
        "key_entity_coverage": coverage,
        "key_entities_covered": sorted(set(covered_entities)),
        "related_triple_count": len(triples),
        "supporting_triple_count": len(triples),
        "provenance_complete_rate": round(complete_count / denominator, 4),
        "invalid_triple_count": invalid_count,
        "unsupported_triple_count": unsupported_count,
    }


def answer_metrics(result: dict[str, Any]) -> dict[str, Any]:
    answer = str(result.get("answer", ""))
    answer_lower = answer.lower()
    chunks = result.get("fused_chunks", [])
    triples = result.get("graph_triples", [])
    chunk_ids = [str(item.get("chunk_id", "")) for item in chunks if item.get("chunk_id")]
    triple_ids = [str(item.get("triple_id", "")) for item in triples if item.get("triple_id")]
    pages = {str(item.get("page")) for item in chunks + triples if item.get("page") is not None}

    cited_chunks = [chunk_id for chunk_id in chunk_ids if chunk_id.lower() in answer_lower]
    cited_triples = [triple_id for triple_id in triple_ids if triple_id.lower() in answer_lower]
    cited_pages = [
        page
        for page in sorted(pages)
        if re.search(rf"\bpage\s*[=:]?\s*{re.escape(page)}\b", answer_lower)
    ]
    cited_chunk_like = set(re.findall(r"\b[a-z0-9_.-]+-p\d{1,3}-c\d{1,3}[a-z0-9_.-]*\b", answer_lower))
    cited_triple_like = set(re.findall(r"\bt\d+\b", answer_lower))
    cited_page_like = {
        f"page {match}"
        for match in re.findall(r"\bpage\s*[=:]?\s*(\d+)\b", answer_lower)
    }
    abstention_markers = (
        "insufficient",
        "do not support",
        "cannot determine",
        "can't determine",
        "unable to determine",
        "not enough evidence",
    )
    is_abstention = any(marker in answer_lower for marker in abstention_markers)
    citation_complete = bool(cited_chunks or cited_triples or cited_pages)
    valid_citations = cited_chunks + cited_triples + [f"page {page}" for page in cited_pages]
    all_detected_citations = (
        set(valid_citations)
        | cited_chunk_like
        | cited_triple_like
        | cited_page_like
    )
    available_citation_units = set(chunk_ids) | set(triple_ids) | {
        f"page {page}" for page in pages
    }
    citation_precision = (
        round(len(set(valid_citations) & all_detected_citations) / len(all_detected_citations), 4)
        if all_detected_citations
        else (1.0 if is_abstention else 0.0)
    )
    citation_recall = (
        round(len(set(valid_citations)) / len(available_citation_units), 4)
        if available_citation_units
        else (1.0 if is_abstention else 0.0)
    )
    return {
        "citation_completeness": citation_complete,
        "citation_precision": citation_precision,
        "citation_recall": citation_recall,
        "valid_chunk_citation": bool(cited_chunks),
        "valid_page_citation": bool(cited_pages),
        "valid_triple_citation": bool(cited_triples),
        "valid_citations": valid_citations,
        "detected_citations": sorted(all_detected_citations),
        "available_citation_units": sorted(available_citation_units),
        "citation_scoring_method": "deterministic_heuristic",
        "insufficient_evidence_abstention": is_abstention,
        "answer_present": bool(answer.strip()),
    }


def aggregate_kg_evidence_metrics(metric_items: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(metric_items) or 1
    return {
        "evidence_coverage": round(
            sum(int(item.get("evidence_coverage", False)) for item in metric_items) / denominator,
            4,
        ),
        "avg_related_triple_count": round(
            sum(int(item.get("related_triple_count", 0)) for item in metric_items) / denominator,
            4,
        ),
        "avg_supporting_triple_count": round(
            sum(int(item.get("supporting_triple_count", 0)) for item in metric_items) / denominator,
            4,
        ),
        "provenance_complete_rate": round(
            sum(float(item.get("provenance_complete_rate", 0.0)) for item in metric_items)
            / denominator,
            4,
        ),
        "avg_invalid_triple_count": round(
            sum(int(item.get("invalid_triple_count", 0)) for item in metric_items) / denominator,
            4,
        ),
    }


def aggregate_answer_metrics(metric_items: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(metric_items) or 1
    return {
        "citation_completeness": round(
            sum(int(item.get("citation_completeness", False)) for item in metric_items)
            / denominator,
            4,
        ),
        "citation_precision": round(
            sum(float(item.get("citation_precision", 0.0)) for item in metric_items)
            / denominator,
            4,
        ),
        "citation_recall": round(
            sum(float(item.get("citation_recall", 0.0)) for item in metric_items)
            / denominator,
            4,
        ),
        "insufficient_evidence_abstention": round(
            sum(int(item.get("insufficient_evidence_abstention", False)) for item in metric_items)
            / denominator,
            4,
        ),
        "answer_present": round(
            sum(int(item.get("answer_present", False)) for item in metric_items) / denominator,
            4,
        ),
    }
