from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from math import sqrt
from pathlib import Path
from typing import Any, Callable

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.utils.pdf import extract_pages


PILOT_CHUNKING_STRATEGIES = (
    "fixed_window",
    "sentence_recursive",
    "structure_aware",
    "semantic_meta_like",
)

BENCHMARK_V2_CHUNKING_STRATEGIES = (
    "fixed_small",
    "fixed_medium",
    "fixed_large",
    "recursive_small",
    "recursive_medium",
    "recursive_large",
    "structure_aware",
    "structure_aware_medium",
    "structure_aware_large",
    "semantic_meta_like",
    "embedding_semantic",
    "proposition_like",
    "hierarchical_parent_child",
    "contextual_prefix",
)

CHUNKING_STRATEGIES = tuple(
    dict.fromkeys((*PILOT_CHUNKING_STRATEGIES, *BENCHMARK_V2_CHUNKING_STRATEGIES))
)

CHUNK_SIZE_TIERS: dict[str, tuple[int, int]] = {
    "fixed_small": (400, 80),
    "fixed_medium": (900, 150),
    "fixed_large": (1600, 250),
    "recursive_small": (400, 80),
    "recursive_medium": (900, 150),
    "recursive_large": (1600, 250),
    "structure_aware_medium": (900, 150),
    "structure_aware_large": (1600, 250),
    "embedding_semantic": (900, 150),
    "proposition_like": (900, 80),
    "hierarchical_parent_child": (400, 80),
    "contextual_prefix": (900, 150),
}

SimilarityFn = Callable[[str, str], float]
Segment = tuple[int, int, str, str]
ChunkWindow = dict[str, Any]

DEFAULT_SEMANTIC_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PROPOSITION_CUE_RE = re.compile(
    r"\b("
    r"is|means|refers to|causes|affects|increases|decreases|produces|results|"
    r"consists|composed|part|component"
    r")\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class ChunkingProfile:
    name: str
    family: str
    max_chars: int
    overlap_chars: int
    max_tokens: int | None
    overlap_tokens: int | None
    retrieval_unit: str
    returned_context_unit: str
    semantic_backend: str
    lexical_fallback: bool
    real_embeddings: bool
    boundary_threshold: float | None
    parent_context_enabled: bool
    parent_child_retrieval: str
    context_prefix_enabled: bool
    implementation_status: str
    limitations: tuple[str, ...]
    name_accuracy: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["limitations"] = list(self.limitations)
        return data


@dataclass(frozen=True)
class SourceChunk:
    chunk_id: str
    source_document: str
    source_path: str
    page: int
    chunk_index: int
    char_start: int
    char_end: int
    text: str
    token_count: int = 0
    strategy: str = "fixed_window"
    section: str = ""
    parent_chunk_id: str = ""
    parent_section: str = ""
    parent_page: int | None = None
    parent_text: str = ""
    context_prefix: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_text(text: str) -> str:
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())


def approximate_token_count(text: str) -> int:
    """Approximate token count with deterministic whitespace tokenization."""
    return len(text.split())


def _approx_tokens_for_chars(chars: int | None) -> int | None:
    if chars is None:
        return None
    return max(1, round(chars / 4))


def chunking_profile(
    strategy: str,
    *,
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> ChunkingProfile:
    if strategy not in CHUNKING_STRATEGIES:
        raise ValueError(f"Unsupported chunking strategy: {strategy}")
    effective_max_chars, effective_overlap_chars = _strategy_size_settings(
        strategy,
        max_chars,
        overlap_chars,
    )
    base = {
        "name": strategy,
        "max_chars": effective_max_chars,
        "overlap_chars": effective_overlap_chars,
        "max_tokens": _approx_tokens_for_chars(effective_max_chars),
        "overlap_tokens": _approx_tokens_for_chars(effective_overlap_chars),
        "retrieval_unit": "chunk_text",
        "returned_context_unit": "chunk_text",
        "semantic_backend": "none",
        "lexical_fallback": False,
        "real_embeddings": False,
        "boundary_threshold": None,
        "parent_context_enabled": False,
        "parent_child_retrieval": "not_applicable",
        "context_prefix_enabled": False,
        "implementation_status": "implemented",
        "limitations": (),
        "name_accuracy": "accurate",
    }
    def make_profile(**overrides: Any) -> ChunkingProfile:
        values = {**base, **overrides}
        return ChunkingProfile(**values)

    if strategy in {"fixed_window", "fixed_small", "fixed_medium", "fixed_large"}:
        return make_profile(
            family="fixed_window",
            limitations=("May cut semantic or structural boundaries.",),
        )
    if strategy in {
        "sentence_recursive",
        "recursive_small",
        "recursive_medium",
        "recursive_large",
    }:
        return make_profile(
            family="sentence_recursive",
            retrieval_unit="sentence_merged_chunk",
            returned_context_unit="sentence_merged_chunk",
            limitations=("Sentence-aware merging is deterministic, not learned.",),
        )
    if strategy in {"structure_aware", "structure_aware_medium", "structure_aware_large"}:
        return make_profile(
            family="structure_aware",
            retrieval_unit="section_line_merged_chunk",
            returned_context_unit="section_line_merged_chunk",
            limitations=("Heading/list detection is heuristic and page-local.",),
        )
    if strategy == "semantic_meta_like":
        return make_profile(
            family="semantic_boundary_lexical",
            retrieval_unit="lexical_semantic_chunk",
            returned_context_unit="lexical_semantic_chunk",
            semantic_backend="lexical_similarity",
            lexical_fallback=True,
            boundary_threshold=0.08,
            limitations=("Semantic boundary decisions use lexical similarity, not embeddings.",),
        )
    if strategy == "embedding_semantic":
        return make_profile(
            family="semantic_boundary_embedding",
            retrieval_unit="embedding_semantic_chunk",
            returned_context_unit="embedding_semantic_chunk",
            semantic_backend="sentence_transformers_or_fallback_lexical",
            lexical_fallback=True,
            real_embeddings=True,
            boundary_threshold=0.08,
            implementation_status="implemented_with_deterministic_fallback",
            limitations=("Only true semantic when the sentence-transformers backend loads.",),
            name_accuracy="conditional_on_backend",
        )
    if strategy == "proposition_like":
        return make_profile(
            family="proposition_like_heuristic",
            retrieval_unit="cue_sentence_or_merged_chunk",
            returned_context_unit="proposition_only",
            implementation_status="heuristic_partial",
            limitations=(
                "Cue-word segmentation is deterministic and not LLM proposition extraction.",
                "Current retrieval returns proposition-like units, not parent paragraph context.",
            ),
            name_accuracy="partial_should_not_be_called_llm_proposition_extraction",
        )
    if strategy == "hierarchical_parent_child":
        return make_profile(
            family="hierarchical_parent_child",
            retrieval_unit="child_chunk",
            returned_context_unit="child_chunk_text",
            parent_context_enabled=False,
            parent_child_retrieval="partial_child_index_parent_metadata",
            implementation_status="partial",
            limitations=(
                "Parent text is stored in chunk metadata but the retriever returns child text.",
                "Do not claim full parent-return retrieval for this strategy.",
            ),
            name_accuracy="partial_parent_metadata_only",
        )
    if strategy == "contextual_prefix":
        return make_profile(
            family="contextual_prefix",
            retrieval_unit="prefix_plus_chunk_text",
            returned_context_unit="prefix_plus_chunk_text",
            context_prefix_enabled=True,
            implementation_status="implemented_no_llm_contextualization",
            limitations=("Prefix is deterministic source metadata, not LLM contextual retrieval.",),
        )
    raise ValueError(f"Unsupported chunking strategy: {strategy}")


def chunking_profiles(
    strategies: tuple[str, ...] = CHUNKING_STRATEGIES,
    *,
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> dict[str, ChunkingProfile]:
    return {
        strategy: chunking_profile(
            strategy,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
        )
        for strategy in strategies
    }


def chunk_output_path_for_strategy(base_output_path: str | Path, strategy: str) -> Path:
    path = Path(base_output_path)
    if strategy == "fixed_window":
        return path
    if path.suffix == ".jsonl":
        return path.with_name(f"{path.stem}.{strategy}{path.suffix}")
    return path.with_name(f"{path.name}.{strategy}.jsonl")


def collection_name_for_strategy(base_collection_name: str, strategy: str) -> str:
    return base_collection_name if strategy == "fixed_window" else f"{base_collection_name}_{strategy}"


def _window_text(text: str, max_chars: int, overlap_chars: int) -> list[tuple[int, int, str]]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap_chars < 0:
        raise ValueError("overlap_chars must be non-negative")
    if overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be smaller than max_chars")

    windows: list[tuple[int, int, str]] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        hard_end = min(start + max_chars, text_length)
        end = hard_end
        if hard_end < text_length:
            paragraph_break = text.rfind("\n", start, hard_end)
            sentence_break = max(text.rfind(". ", start, hard_end), text.rfind("; ", start, hard_end))
            soft_end = max(paragraph_break, sentence_break)
            if soft_end > start + max_chars // 2:
                end = soft_end + 1
        chunk_text = text[start:end].strip()
        if chunk_text:
            windows.append((start, end, chunk_text))
        if end >= text_length:
            break
        start = max(end - overlap_chars, start + 1)
    return windows


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9']+", text.lower()) if len(token) > 2}


def _lexical_similarity(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def _embedding_similarity_fn(
    model_name: str,
    *,
    allow_download: bool,
) -> SimilarityFn:
    from sentence_transformers import SentenceTransformer

    try:
        model = SentenceTransformer(model_name, local_files_only=not allow_download)
    except TypeError:
        if not allow_download:
            raise
        model = SentenceTransformer(model_name)
    cache: dict[str, list[float]] = {}

    def encode(text: str) -> list[float]:
        if text not in cache:
            vector = model.encode(text)
            cache[text] = [float(value) for value in vector]
        return cache[text]

    def similarity(left: str, right: str) -> float:
        return _cosine_similarity(encode(left), encode(right))

    return similarity


def _is_sentence_boundary(text: str) -> bool:
    return bool(text.rstrip().endswith((".", "!", "?", ";", ":")))


def _is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 90:
        return False
    if stripped.endswith((".", ",", ";", ":")):
        return False
    title_words = sum(1 for word in stripped.split() if word[:1].isupper())
    return title_words >= max(1, len(stripped.split()) // 2) or bool(
        re.match(r"^(chapter|section|\d+(?:\.\d+)*)\b", stripped, flags=re.IGNORECASE)
    )


def _sentence_segments(text: str, section: str = "") -> list[Segment]:
    segments: list[Segment] = []
    pattern = re.compile(r"[^.!?;\n]+(?:[.!?;]+|(?=\n)|$)")
    for match in pattern.finditer(text):
        segment_text = match.group(0).strip()
        if segment_text:
            segments.append((match.start(), match.end(), segment_text, section))
    return segments


def _structure_segments(text: str) -> list[Segment]:
    segments: list[Segment] = []
    current_section = ""
    cursor = 0
    for line in text.splitlines():
        start = text.find(line, cursor)
        end = start + len(line)
        cursor = end
        stripped = line.strip()
        if not stripped:
            continue
        if _is_heading(stripped):
            current_section = stripped
        segments.append((start, end, stripped, current_section))
    return segments


def _overlap_tail(segments: list[Segment], overlap_chars: int) -> list[Segment]:
    if overlap_chars <= 0:
        return []
    tail: list[Segment] = []
    chars = 0
    for segment in reversed(segments):
        chars += len(segment[2])
        if chars > overlap_chars and tail:
            break
        tail.append(segment)
    return list(reversed(tail))


def _merge_segments(
    segments: list[Segment],
    max_chars: int,
    overlap_chars: int,
    force_section_boundaries: bool = False,
) -> list[Segment]:
    chunks: list[Segment] = []
    current: list[Segment] = []
    current_len = 0
    current_section = ""

    def flush() -> None:
        nonlocal current, current_len, current_section
        if not current:
            return
        text = " ".join(segment[2] for segment in current).strip()
        chunks.append((current[0][0], current[-1][1], text, current_section))
        current = _overlap_tail(current, overlap_chars)
        current_len = sum(len(segment[2]) + 1 for segment in current)
        current_section = current[-1][3] if current else ""

    for segment in segments:
        segment_len = len(segment[2]) + 1
        section_changed = (
            force_section_boundaries
            and current
            and bool(segment[3])
            and bool(current_section)
            and segment[3] != current_section
        )
        if current and (current_len + segment_len > max_chars or section_changed):
            flush()
        if not current:
            current_section = segment[3]
        current.append(segment)
        current_len += segment_len
        if len(segment[2]) > max_chars:
            flush()
    if current:
        text = " ".join(segment[2] for segment in current).strip()
        chunks.append((current[0][0], current[-1][1], text, current_section))
    return chunks


def _semantic_segments(
    text: str,
    max_chars: int,
    overlap_chars: int,
    similarity_fn: SimilarityFn = _lexical_similarity,
    boundary_threshold: float = 0.08,
) -> list[Segment]:
    sentences = _sentence_segments(text)
    if not sentences:
        return []
    chunks: list[list[Segment]] = [[sentences[0]]]
    min_boundary_chars = max_chars // 2
    for previous, current in zip(sentences, sentences[1:]):
        active = chunks[-1]
        active_text = " ".join(segment[2] for segment in active)
        similarity = similarity_fn(previous[2], current[2])
        would_exceed = len(active_text) + len(current[2]) + 1 > max_chars
        semantic_boundary = similarity < boundary_threshold and len(active_text) >= min_boundary_chars
        if semantic_boundary or would_exceed:
            chunks.append([current])
        else:
            active.append(current)

    merged: list[Segment] = []
    for chunk_segments in chunks:
        if not chunk_segments:
            continue
        text_chunk = " ".join(segment[2] for segment in chunk_segments).strip()
        if len(text_chunk) <= max_chars:
            merged.append((chunk_segments[0][0], chunk_segments[-1][1], text_chunk, "semantic"))
        else:
            merged.extend(_merge_segments(chunk_segments, max_chars, overlap_chars))
    return merged


def _strategy_size_settings(
    strategy: str,
    max_chars: int,
    overlap_chars: int,
) -> tuple[int, int]:
    return CHUNK_SIZE_TIERS.get(strategy, (max_chars, overlap_chars))


def _proposition_segments(
    text: str,
    max_chars: int,
    overlap_chars: int,
    min_chars: int = 80,
) -> list[Segment]:
    sentences = _sentence_segments(text)
    if not sentences:
        return []

    raw: list[Segment] = []
    buffer: list[Segment] = []

    def flush_buffer() -> None:
        nonlocal buffer
        if not buffer:
            return
        raw.extend(_merge_segments(buffer, max_chars=max_chars, overlap_chars=overlap_chars))
        buffer = []

    for sentence in sentences:
        cue_rich = bool(PROPOSITION_CUE_RE.search(sentence[2]))
        if cue_rich:
            flush_buffer()
            raw.append((sentence[0], sentence[1], sentence[2], "proposition_like"))
            continue
        buffer.append(sentence)
        if sum(len(item[2]) + 1 for item in buffer) >= max_chars:
            flush_buffer()
    flush_buffer()

    merged: list[Segment] = []
    for segment in raw:
        if len(segment[2]) < min_chars and merged:
            previous = merged.pop()
            merged.append(
                (
                    previous[0],
                    segment[1],
                    f"{previous[2]} {segment[2]}".strip(),
                    previous[3] or segment[3],
                )
            )
        else:
            merged.append(segment)
    return merged


def _contextual_prefix_windows(
    text: str,
    max_chars: int,
    overlap_chars: int,
    *,
    source_document: str,
    page_number: int,
) -> list[ChunkWindow]:
    segments = _merge_segments(
        _structure_segments(text),
        max_chars=max_chars,
        overlap_chars=overlap_chars,
        force_section_boundaries=True,
    )
    windows: list[ChunkWindow] = []
    for start, end, chunk_text, section in segments:
        prefix_parts = [
            "Source: PHAK Chapter 4",
            f"document={source_document}",
            f"page={page_number}",
        ]
        if section:
            prefix_parts.append(f"section={section}")
        prefix = "; ".join(prefix_parts)
        windows.append(
            {
                "start": start,
                "end": end,
                "text": f"{prefix}\n{chunk_text}",
                "section": section,
                "context_prefix": prefix,
                "metadata": {
                    "contextualization": "deterministic_prefix",
                    "llm_contextualization": False,
                },
            }
        )
    return windows


def _hierarchical_parent_child_windows(
    text: str,
    child_max_chars: int,
    child_overlap_chars: int,
) -> list[ChunkWindow]:
    parent_segments = _merge_segments(
        _structure_segments(text),
        max_chars=1600,
        overlap_chars=0,
        force_section_boundaries=True,
    )
    if not parent_segments:
        parent_segments = [(0, len(text), text.strip(), "page")]
    child_segments = _merge_segments(
        _sentence_segments(text),
        max_chars=child_max_chars,
        overlap_chars=child_overlap_chars,
    )
    windows: list[ChunkWindow] = []
    for start, end, child_text, section in child_segments:
        parent_index = 0
        parent = parent_segments[0]
        for candidate_index, candidate in enumerate(parent_segments):
            overlaps = start < candidate[1] and end > candidate[0]
            if overlaps:
                parent_index = candidate_index
                parent = candidate
                break
        windows.append(
            {
                "start": start,
                "end": end,
                "text": child_text,
                "section": section or parent[3],
                "parent_index": parent_index,
                "parent_section": parent[3],
                "parent_text": parent[2],
                "metadata": {
                    "retrieval_integration": "partial_child_index_parent_metadata",
                    "parent_context_available": True,
                },
            }
        )
    return windows


def _chunk_windows_for_strategy(
    text: str,
    strategy: str,
    max_chars: int,
    overlap_chars: int,
    similarity_fn: SimilarityFn | None,
) -> list[Segment]:
    if strategy not in CHUNKING_STRATEGIES:
        raise ValueError(f"Unsupported chunking strategy: {strategy}")
    effective_max_chars, effective_overlap_chars = _strategy_size_settings(
        strategy,
        max_chars,
        overlap_chars,
    )
    if strategy == "fixed_window":
        return [
            (start, end, chunk_text, "")
            for start, end, chunk_text in _window_text(text, max_chars, overlap_chars)
        ]
    if strategy.startswith("fixed_"):
        return [
            (start, end, chunk_text, "")
            for start, end, chunk_text in _window_text(
                text,
                effective_max_chars,
                effective_overlap_chars,
            )
        ]
    if strategy in {
        "sentence_recursive",
        "recursive_small",
        "recursive_medium",
        "recursive_large",
    }:
        return _merge_segments(
            _sentence_segments(text),
            effective_max_chars,
            effective_overlap_chars,
        )
    if strategy in {"structure_aware", "structure_aware_medium", "structure_aware_large"}:
        return _merge_segments(
            _structure_segments(text),
            effective_max_chars,
            effective_overlap_chars,
            force_section_boundaries=strategy == "structure_aware",
        )
    if strategy == "proposition_like":
        return _proposition_segments(text, effective_max_chars, effective_overlap_chars)
    return _semantic_segments(
        text,
        effective_max_chars,
        effective_overlap_chars,
        similarity_fn=similarity_fn or _lexical_similarity,
    )


def _window_from_segment(segment: Segment) -> ChunkWindow:
    return {
        "start": segment[0],
        "end": segment[1],
        "text": segment[2],
        "section": segment[3],
        "metadata": {},
    }


def _chunk_windows_with_metadata_for_strategy(
    text: str,
    strategy: str,
    max_chars: int,
    overlap_chars: int,
    similarity_fn: SimilarityFn | None,
    *,
    source_document: str,
    page_number: int,
    embedding_model: str,
    semantic_download: bool,
    semantic_metadata_override: dict[str, Any] | None = None,
) -> tuple[list[ChunkWindow], dict[str, Any]]:
    effective_max_chars, effective_overlap_chars = _strategy_size_settings(
        strategy,
        max_chars,
        overlap_chars,
    )
    strategy_metadata: dict[str, Any] = {
        "configured_max_chars": effective_max_chars,
        "configured_overlap_chars": effective_overlap_chars,
        "profile_family": chunking_profile(
            strategy,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
        ).family,
    }
    if strategy == "embedding_semantic":
        if semantic_metadata_override is not None:
            similarity = similarity_fn or _lexical_similarity
            strategy_metadata.update(semantic_metadata_override)
        else:
            backend = "sentence_transformers"
            backend_error = ""
            similarity = similarity_fn
            if similarity is None:
                try:
                    similarity = _embedding_similarity_fn(
                        embedding_model,
                        allow_download=semantic_download,
                    )
                except Exception as exc:
                    backend = "fallback_lexical"
                    backend_error = f"{type(exc).__name__}: {exc}"
                    similarity = _lexical_similarity
            else:
                backend = "provided_similarity_fn"
            strategy_metadata.update(
                {
                    "semantic_backend": backend,
                    "semantic_embedding_model": embedding_model
                    if backend == "sentence_transformers"
                    else "",
                    "semantic_backend_error": backend_error,
                }
            )
        segments = _semantic_segments(
            text,
            effective_max_chars,
            effective_overlap_chars,
            similarity_fn=similarity,
        )
        return [_window_from_segment(segment) for segment in segments], strategy_metadata
    if strategy == "hierarchical_parent_child":
        strategy_metadata["retrieval_integration"] = "partial_child_index_parent_metadata"
        return (
            _hierarchical_parent_child_windows(
                text,
                effective_max_chars,
                effective_overlap_chars,
            ),
            strategy_metadata,
        )
    if strategy == "contextual_prefix":
        strategy_metadata.update(
            {
                "contextualization": "deterministic_prefix",
                "llm_contextualization": False,
            }
        )
        return (
            _contextual_prefix_windows(
                text,
                effective_max_chars,
                effective_overlap_chars,
                source_document=source_document,
                page_number=page_number,
            ),
            strategy_metadata,
        )
    if strategy == "proposition_like":
        strategy_metadata.update(
            {
                "proposition_extraction": "heuristic_sentence_cue",
                "llm_proposition_extraction": False,
            }
        )
    if strategy == "semantic_meta_like":
        strategy_metadata["semantic_backend"] = "lexical_similarity"
    segments = _chunk_windows_for_strategy(
        text,
        strategy=strategy,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
        similarity_fn=similarity_fn,
    )
    return [_window_from_segment(segment) for segment in segments], strategy_metadata


def _resolve_semantic_similarity(
    strategy: str,
    similarity_fn: SimilarityFn | None,
    *,
    embedding_model: str,
    semantic_download: bool,
) -> tuple[SimilarityFn | None, dict[str, Any] | None]:
    if strategy != "embedding_semantic":
        return similarity_fn, None
    if similarity_fn is not None:
        return similarity_fn, {
            "semantic_backend": "provided_similarity_fn",
            "semantic_embedding_model": "",
            "semantic_backend_error": "",
        }
    try:
        return _embedding_similarity_fn(embedding_model, allow_download=semantic_download), {
            "semantic_backend": "sentence_transformers",
            "semantic_embedding_model": embedding_model,
            "semantic_backend_error": "",
        }
    except Exception as exc:
        return _lexical_similarity, {
            "semantic_backend": "fallback_lexical",
            "semantic_embedding_model": "",
            "semantic_backend_error": f"{type(exc).__name__}: {exc}",
        }


def build_chunks(
    pdf_path: str | Path,
    max_chars: int = 1200,
    overlap_chars: int = 150,
    max_pages: int | None = None,
    strategy: str = "fixed_window",
    similarity_fn: SimilarityFn | None = None,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
) -> list[SourceChunk]:
    """Build stable page-aware chunks from a PDF."""
    pdf = Path(pdf_path)
    source_document = pdf.stem
    chunks: list[SourceChunk] = []
    resolved_similarity_fn, semantic_metadata = _resolve_semantic_similarity(
        strategy,
        similarity_fn,
        embedding_model=embedding_model,
        semantic_download=semantic_download,
    )
    for page in extract_pages(pdf, max_pages=max_pages):
        text = _normalize_text(page.text)
        windows, strategy_metadata = _chunk_windows_with_metadata_for_strategy(
            text,
            strategy=strategy,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
            similarity_fn=resolved_similarity_fn,
            source_document=source_document,
            page_number=page.page_number,
            embedding_model=embedding_model,
            semantic_download=semantic_download,
            semantic_metadata_override=semantic_metadata,
        )
        for chunk_index, window in enumerate(windows):
            chunk_id = f"{source_document}-{strategy}-p{page.page_number:02d}-c{chunk_index:02d}"
            parent_index = window.get("parent_index")
            parent_chunk_id = (
                f"{source_document}-{strategy}-p{page.page_number:02d}-parent{int(parent_index):02d}"
                if parent_index is not None
                else ""
            )
            metadata = {
                **strategy_metadata,
                **dict(window.get("metadata", {})),
            }
            token_count = approximate_token_count(str(window["text"]))
            metadata["token_count"] = token_count
            chunks.append(
                SourceChunk(
                    chunk_id=chunk_id,
                    source_document=source_document,
                    source_path=project_relative_path(pdf),
                    page=page.page_number,
                    chunk_index=chunk_index,
                    char_start=int(window["start"]),
                    char_end=int(window["end"]),
                    text=str(window["text"]),
                    token_count=token_count,
                    strategy=strategy,
                    section=str(window.get("section", "")),
                    parent_chunk_id=parent_chunk_id,
                    parent_section=str(window.get("parent_section", "")),
                    parent_page=page.page_number if parent_chunk_id else None,
                    parent_text=str(window.get("parent_text", "")),
                    context_prefix=str(window.get("context_prefix", "")),
                    metadata=metadata,
                )
            )
    return chunks


def write_chunks_jsonl(chunks: list[SourceChunk], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(chunk.to_dict(), sort_keys=True) for chunk in chunks]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return path


def read_chunks_jsonl(path: str | Path) -> list[SourceChunk]:
    chunks: list[SourceChunk] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        chunks.append(SourceChunk(**data))
    return chunks


def build_chunk_file(
    pdf_path: str | Path,
    output_path: str | Path,
    max_chars: int = 1200,
    overlap_chars: int = 150,
    max_pages: int | None = None,
    strategy: str = "fixed_window",
    similarity_fn: SimilarityFn | None = None,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
) -> tuple[Path, list[SourceChunk]]:
    chunks = build_chunks(
        pdf_path,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
        max_pages=max_pages,
        strategy=strategy,
        similarity_fn=similarity_fn,
        embedding_model=embedding_model,
        semantic_download=semantic_download,
    )
    path = write_chunks_jsonl(chunks, output_path)
    return path, chunks
