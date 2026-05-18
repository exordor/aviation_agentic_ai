from __future__ import annotations

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
    if level == "span" and gold.evidence_spans:
        return any(_span_matches_hit(span, hit) for span in gold.evidence_spans)
    if level == "chunk" and gold.expected_chunk_ids:
        return str(hit.get("chunk_id", "")) in set(gold.expected_chunk_ids)
    if gold.evidence_spans:
        return any(_span_matches_hit(span, hit) for span in gold.evidence_spans)
    if gold.expected_chunk_ids:
        return str(hit.get("chunk_id", "")) in set(gold.expected_chunk_ids)
    return int(hit.get("page", -1)) == gold.source_page


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
        "recall_at_5": bool(ranks),
        "mrr_at_5": round(1.0 / ranks[0], 4) if ranks else 0.0,
        "context_precision_at_5": round(len(ranks) / max(len(top_hits), 1), 4),
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
        "mrr_at_5": round(
            sum(float(item.get("mrr_at_5", 0.0)) for item in metric_items) / denominator,
            4,
        ),
        "context_precision_at_5": round(
            sum(float(item.get("context_precision_at_5", 0.0)) for item in metric_items)
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
    abstention_markers = (
        "insufficient",
        "do not support",
        "cannot determine",
        "can't determine",
        "unable to determine",
        "not enough evidence",
    )
    citation_complete = bool(cited_chunks or cited_triples or cited_pages)
    return {
        "citation_completeness": citation_complete,
        "valid_chunk_citation": bool(cited_chunks),
        "valid_page_citation": bool(cited_pages),
        "valid_triple_citation": bool(cited_triples),
        "valid_citations": cited_chunks + cited_triples + [f"page {page}" for page in cited_pages],
        "insufficient_evidence_abstention": any(marker in answer_lower for marker in abstention_markers),
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

