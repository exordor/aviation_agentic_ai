from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path


def artifact_size_bytes(path: str | Path | None) -> int | None:
    if path is None:
        return None
    source = Path(path)
    if not source.exists():
        return None
    if source.is_file():
        return source.stat().st_size
    return sum(item.stat().st_size for item in source.rglob("*") if item.is_file())


def cost_latency_block(
    *,
    elapsed_seconds: float,
    questions_total: int | None = None,
    cases_total: int | None = None,
    chunks_path: str | Path | None = None,
    kg_path: str | Path | None = None,
    index_dir: str | Path | None = None,
    token_usage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "elapsed_seconds": round(elapsed_seconds, 4),
        "questions_total": questions_total,
        "cases_total": cases_total,
        "chunks_path": project_relative_path(chunks_path) if chunks_path is not None else None,
        "chunks_size_bytes": artifact_size_bytes(chunks_path),
        "kg_path": project_relative_path(kg_path) if kg_path is not None else None,
        "kg_size_bytes": artifact_size_bytes(kg_path),
        "index_dir": project_relative_path(index_dir) if index_dir is not None else None,
        "index_size_bytes": artifact_size_bytes(index_dir),
        "llm_token_usage": token_usage,
    }
