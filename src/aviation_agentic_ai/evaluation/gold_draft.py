from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.chunking.chunks import SourceChunk, read_chunks_jsonl
from aviation_agentic_ai.evaluation.gold import load_boundary_questions
from aviation_agentic_ai.paths import project_relative_path


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9']+", text.lower()) if len(token) > 2}


def _entity_score(chunk: SourceChunk, key_entities: list[str]) -> int:
    normalized = _normalize(chunk.text)
    score = sum(1 for entity in key_entities if _normalize(entity) in normalized)
    if score:
        return score
    entity_tokens = set().union(*(_tokens(entity) for entity in key_entities)) if key_entities else set()
    return len(_tokens(chunk.text) & entity_tokens)


def _candidate_chunks(
    chunks_by_path: dict[str, list[SourceChunk]],
    *,
    source_page: int,
    key_entities: list[str],
    limit_per_strategy: int,
) -> list[SourceChunk]:
    candidates: list[SourceChunk] = []
    for chunks in chunks_by_path.values():
        page_chunks = [chunk for chunk in chunks if chunk.page == source_page]
        ranked = sorted(
            page_chunks,
            key=lambda chunk: (_entity_score(chunk, key_entities), -len(chunk.text)),
            reverse=True,
        )
        selected = [chunk for chunk in ranked if _entity_score(chunk, key_entities) > 0]
        candidates.extend((selected or ranked)[:limit_per_strategy])
    return candidates


def _sentence_candidates(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    for match in re.finditer(r"[^.!?;\n]+(?:[.!?;]+|(?=\n)|$)", text):
        sentence = " ".join(match.group(0).split())
        if sentence:
            spans.append((match.start(), match.end(), sentence))
    if not spans and text.strip():
        excerpt = " ".join(text.split())[:240]
        spans.append((0, min(len(text), 240), excerpt))
    return spans


def _evidence_spans(
    chunks: list[SourceChunk],
    key_entities: list[str],
    *,
    max_spans: int,
) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for chunk in chunks:
        ranked_sentences = sorted(
            _sentence_candidates(chunk.text),
            key=lambda item: sum(
                1 for entity in key_entities if _normalize(entity) in _normalize(item[2])
            ),
            reverse=True,
        )
        for start, end, sentence in ranked_sentences:
            score = sum(1 for entity in key_entities if _normalize(entity) in _normalize(sentence))
            if key_entities and score == 0:
                continue
            key = (chunk.page, _normalize(sentence))
            if key in seen:
                continue
            seen.add(key)
            spans.append(
                {
                    "page": chunk.page,
                    "text": sentence,
                    "char_start": chunk.char_start + start,
                    "char_end": chunk.char_start + end,
                }
            )
            if len(spans) >= max_spans:
                return spans
    if not spans and chunks:
        chunk = chunks[0]
        excerpt = " ".join(chunk.text.split())[:240]
        spans.append(
            {
                "page": chunk.page,
                "text": excerpt,
                "char_start": chunk.char_start,
                "char_end": chunk.char_start + min(len(chunk.text), len(excerpt)),
            }
        )
    return spans[:max_spans]


def build_gold_draft(
    boundary_cq_path: str | Path,
    chunks_paths: list[str | Path],
    *,
    output_path: str | Path | None = None,
    max_chunks_per_strategy: int = 3,
    max_spans: int = 2,
) -> dict[str, Any]:
    chunks_by_path = {
        project_relative_path(path): read_chunks_jsonl(path)
        for path in chunks_paths
        if Path(path).exists()
    }
    if not chunks_by_path:
        raise FileNotFoundError("No chunk files found for gold draft generation.")

    labels: list[dict[str, Any]] = []
    for cq in load_boundary_questions(boundary_cq_path):
        key_entities = [str(item) for item in cq.get("key_entities", [])]
        chunks = _candidate_chunks(
            chunks_by_path,
            source_page=int(cq["source_page"]),
            key_entities=key_entities,
            limit_per_strategy=max_chunks_per_strategy,
        )
        spans = _evidence_spans(chunks, key_entities, max_spans=max_spans)
        expected_chunk_ids = sorted({chunk.chunk_id for chunk in chunks})
        labels.append(
            {
                "cq_id": str(cq["id"]),
                "source_document": str(cq.get("source_document", "")),
                "source_page": int(cq["source_page"]),
                "expected_chunk_ids": expected_chunk_ids,
                "evidence_spans": spans,
                "key_entities": key_entities,
                "answer_key": str(cq.get("expected_answer", "")),
                "gold_level": "span" if spans else "chunk" if expected_chunk_ids else "page",
            }
        )

    payload = {
        "metadata": {
            "generated_at": datetime.now(UTC).isoformat(),
            "generator": "aviation-ai cqs gold-draft",
            "boundary_cq_path": project_relative_path(boundary_cq_path),
            "chunks_paths": list(chunks_by_path.keys()),
            "review_required": True,
            "notes": "Auto-drafted from source chunks; review spans before final claims.",
        },
        "labels": labels,
    }
    if output_path is not None:
        write_gold_draft(payload, output_path)
    return payload


def write_gold_draft(payload: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
