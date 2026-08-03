"""Live HybridRAG runtime over the authoritative evidence store."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    SOURCE_CHUNK_COLLECTION,
    TMI_EVENT_COLLECTION,
    ChromaSourceRetrievalIndex,
    ChromaTMIEventRetrievalIndex,
    SentenceTransformerTMIEventEncoder,
)
from aviation_agentic_ai.agent_system.knowledge_entity_retrieval_index import (
    KNOWLEDGE_ENTITY_COLLECTION,
    ChromaKnowledgeEntityRetrievalIndex,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    VectorIndexStateRecord,
)
from aviation_agentic_ai.config import (
    configured_dataset_id,
    configured_store_root,
    resolve_project_path,
    validate_web_evidence_config,
)
from aviation_agentic_ai.agent_system.web_evidence_client import (
    HttpWigoloWebClient,
    WebEvidenceClient,
)
from aviation_agentic_ai.agent_system.web_evidence_contracts import (
    WebEvidenceConfig,
)


@dataclass(frozen=True)
class QueryRuntime:
    """Authoritative store plus independently optional vector readers."""

    store: AviationEvidenceStore
    source_index: ChromaSourceRetrievalIndex | None
    event_index: ChromaTMIEventRetrievalIndex | None
    knowledge_index: ChromaKnowledgeEntityRetrievalIndex | None = None
    # Query-time web access is an explicitly authorized, read-only sidecar.
    # It is intentionally not a store writer and is absent by default.
    web_client: WebEvidenceClient | None = None
    web_config: WebEvidenceConfig | None = None


def _storage_config(config: dict[str, Any]) -> dict[str, Any]:
    agent_system = config.get("agent_system")
    if not isinstance(agent_system, dict):
        raise ValueError("config.agent_system must be a mapping")
    storage = agent_system.get("storage")
    if not isinstance(storage, dict):
        raise ValueError("config.agent_system.storage must be a mapping")
    return storage


def _chroma_dir(
    storage: dict[str, Any],
    *,
    store_root: Path,
) -> Path:
    configured = storage.get("chroma", "chroma")
    if not isinstance(configured, str) or not configured:
        raise ValueError(
            "config.agent_system.storage.chroma must be a non-empty path"
        )
    candidate = Path(configured)
    return candidate if candidate.is_absolute() else store_root / candidate


def _embedding_model_name(storage: dict[str, Any]) -> str:
    configured = storage.get(
        "embedding_model",
        DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
    )
    if not isinstance(configured, str) or not configured:
        raise ValueError(
            "config.agent_system.storage.embedding_model must be a "
            "non-empty string"
        )
    return configured


def _require_current_index(
    store: AviationEvidenceStore,
    collection_name: str,
) -> VectorIndexStateRecord:
    state = store.get_vector_index_state(collection_name)
    if state is None:
        raise ValueError(f"vector index state is missing: {collection_name}")
    if (
        state.status != "current"
        or state.indexed_knowledge_revision != store.get_knowledge_revision()
    ):
        raise ValueError(f"vector index is stale: {collection_name}")
    return state


def _open_source_index(
    store: AviationEvidenceStore,
    chroma_dir: Path,
    *,
    model_name: str,
    allow_model_download: bool,
) -> ChromaSourceRetrievalIndex:
    state = _require_current_index(store, SOURCE_CHUNK_COLLECTION)
    if state.embedding_model_id != model_name:
        raise ValueError("source index embedding model differs from config")
    encoder = SentenceTransformerTMIEventEncoder(
        model_name,
        allow_download=allow_model_download,
    )
    return ChromaSourceRetrievalIndex(store, chroma_dir, encoder)


def _open_event_index(
    store: AviationEvidenceStore,
    chroma_dir: Path,
) -> ChromaTMIEventRetrievalIndex:
    _require_current_index(store, TMI_EVENT_COLLECTION)
    return ChromaTMIEventRetrievalIndex(store, chroma_dir)


def _open_knowledge_index(
    store: AviationEvidenceStore,
    chroma_dir: Path,
    *,
    model_name: str,
    allow_model_download: bool,
) -> ChromaKnowledgeEntityRetrievalIndex:
    state = _require_current_index(store, KNOWLEDGE_ENTITY_COLLECTION)
    if state.embedding_model_id != model_name:
        raise ValueError("knowledge index embedding model differs from config")
    encoder = SentenceTransformerTMIEventEncoder(
        model_name,
        allow_download=allow_model_download,
    )
    return ChromaKnowledgeEntityRetrievalIndex(store, chroma_dir, encoder)


def open_query_runtime(
    config: dict[str, object],
    *,
    store_dir: str | Path | None = None,
    allow_model_download: bool = False,
    allow_live_web: bool = False,
) -> QueryRuntime:
    """Open the live store and independently attach valid vector indexes."""

    typed_config = dict(config)
    storage = _storage_config(typed_config)
    root = (
        configured_store_root(typed_config)
        if store_dir is None
        else resolve_project_path(store_dir)
    )
    chroma_dir = _chroma_dir(storage, store_root=root)
    model_name = _embedding_model_name(storage)
    store = AviationEvidenceStore.open(
        root,
        dataset_id=configured_dataset_id(typed_config),
        create=False,
    )

    web_config = validate_web_evidence_config(typed_config)
    web_client: WebEvidenceClient | None = None
    if allow_live_web and web_config.enabled:
        token = os.environ.get(web_config.token_env) or None
        web_client = HttpWigoloWebClient(
            web_config.base_url,
            token,
            web_config.timeout_seconds,
        )

    try:
        source_index = _open_source_index(
            store,
            chroma_dir,
            model_name=model_name,
            allow_model_download=allow_model_download,
        )
    except Exception:
        source_index = None
    try:
        event_index = _open_event_index(store, chroma_dir)
    except Exception:
        event_index = None
    try:
        knowledge_index = _open_knowledge_index(
            store,
            chroma_dir,
            model_name=model_name,
            allow_model_download=allow_model_download,
        )
    except Exception:
        knowledge_index = None
    return QueryRuntime(
        store=store,
        source_index=source_index,
        event_index=event_index,
        knowledge_index=knowledge_index,
        web_client=web_client,
        web_config=web_config if web_client is not None else None,
    )


__all__ = ["QueryRuntime", "open_query_runtime"]
