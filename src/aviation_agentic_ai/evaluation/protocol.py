from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.config import load_environment
from aviation_agentic_ai.paths import project_relative_path


def _safe_path_value(value: Any) -> Any:
    if isinstance(value, Path):
        return project_relative_path(value)
    if isinstance(value, dict):
        return {str(key): _safe_path_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_path_value(item) for item in value]
    return value


def safe_llm_metadata() -> dict[str, str]:
    load_environment()
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    default_model = {
        "openai": "gpt-4o-mini",
        "deepseek": "deepseek-chat",
        "vllm": "Qwen/Qwen3-30B-A3B-Instruct-2507-FP8",
    }.get(provider, "unknown")
    return {
        "provider": provider,
        "model": os.getenv("MODEL_NAME", default_model),
    }


def embedding_metadata(
    index_dir: str | Path,
    collection_name: str,
    *,
    collections: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    return {
        "backend": "chromadb_default_embedding_function",
        "index_dir": project_relative_path(index_dir),
        "collection_name": collection_name,
        "collections": list(collections or [collection_name]),
    }


def build_run_manifest(
    experiment_name: str,
    *,
    parameters: dict[str, Any],
    artifacts: dict[str, Any],
    rebuild_policy: dict[str, bool],
    collection_name: str,
    chunking_strategy: str,
    command: str,
    document: dict[str, Any] | None = None,
    llm: dict[str, str] | None = None,
    embedding: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> dict[str, Any]:
    timestamp = created_at or datetime.now(UTC)
    run_slug = experiment_name.replace("_", "-")
    return {
        "run_id": f"{run_slug}-{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
        "experiment_name": experiment_name,
        "created_at": timestamp.isoformat(),
        "command": command,
        "parameters": _safe_path_value(parameters),
        "artifacts": _safe_path_value(artifacts),
        "rebuild_policy": {
            "chunks": bool(rebuild_policy.get("chunks", False)),
            "indexes": bool(rebuild_policy.get("indexes", False)),
            "kg": bool(rebuild_policy.get("kg", False)),
        },
        "collection_name": collection_name,
        "chunking_strategy": chunking_strategy,
        "llm": llm or safe_llm_metadata(),
        "embedding": embedding or embedding_metadata("", collection_name),
        "document": document or {},
    }
