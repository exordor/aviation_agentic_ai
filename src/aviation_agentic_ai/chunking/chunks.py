from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.utils.pdf import extract_pages


CHUNKING_STRATEGIES = (
    "fixed_window",
    "sentence_recursive",
    "structure_aware",
    "semantic_meta_like",
)

SimilarityFn = Callable[[str, str], float]
Segment = tuple[int, int, str, str]


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
    strategy: str = "fixed_window"
    section: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_text(text: str) -> str:
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())


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


def _chunk_windows_for_strategy(
    text: str,
    strategy: str,
    max_chars: int,
    overlap_chars: int,
    similarity_fn: SimilarityFn | None,
) -> list[Segment]:
    if strategy not in CHUNKING_STRATEGIES:
        raise ValueError(f"Unsupported chunking strategy: {strategy}")
    if strategy == "fixed_window":
        return [(start, end, chunk_text, "") for start, end, chunk_text in _window_text(text, max_chars, overlap_chars)]
    if strategy == "sentence_recursive":
        return _merge_segments(_sentence_segments(text), max_chars, overlap_chars)
    if strategy == "structure_aware":
        return _merge_segments(
            _structure_segments(text),
            max_chars,
            overlap_chars,
            force_section_boundaries=True,
        )
    return _semantic_segments(
        text,
        max_chars,
        overlap_chars,
        similarity_fn=similarity_fn or _lexical_similarity,
    )


def build_chunks(
    pdf_path: str | Path,
    max_chars: int = 1200,
    overlap_chars: int = 150,
    max_pages: int | None = None,
    strategy: str = "fixed_window",
    similarity_fn: SimilarityFn | None = None,
) -> list[SourceChunk]:
    """Build stable page-aware chunks from a PDF."""
    pdf = Path(pdf_path)
    source_document = pdf.stem
    chunks: list[SourceChunk] = []
    for page in extract_pages(pdf, max_pages=max_pages):
        text = _normalize_text(page.text)
        for chunk_index, (start, end, chunk_text, section) in enumerate(
            _chunk_windows_for_strategy(
                text,
                strategy=strategy,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
                similarity_fn=similarity_fn,
            )
        ):
            chunks.append(
                SourceChunk(
                    chunk_id=(
                        f"{source_document}-{strategy}-p{page.page_number:02d}-c{chunk_index:02d}"
                    ),
                    source_document=source_document,
                    source_path=project_relative_path(pdf),
                    page=page.page_number,
                    chunk_index=chunk_index,
                    char_start=start,
                    char_end=end,
                    text=chunk_text,
                    strategy=strategy,
                    section=section,
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
) -> tuple[Path, list[SourceChunk]]:
    chunks = build_chunks(
        pdf_path,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
        max_pages=max_pages,
        strategy=strategy,
        similarity_fn=similarity_fn,
    )
    path = write_chunks_jsonl(chunks, output_path)
    return path, chunks
