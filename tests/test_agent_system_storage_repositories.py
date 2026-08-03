"""Focused checks for the storage repository boundaries."""

from __future__ import annotations

import hashlib

from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.storage_contracts import (
    SourceFamily,
    SourceVersionRecord,
)
from aviation_agentic_ai.agent_system.storage_repositories import (
    RetrievalRepository,
    SemanticRepository,
    SourceRepository,
)
from aviation_agentic_ai.utils.identifiers import stable_id


def test_repository_facades_delegate_to_one_authoritative_store(tmp_path) -> None:
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:repository-boundary",
        create=True,
    )
    content = "ATCSCC source record"
    digest = hashlib.sha256(content.encode()).hexdigest()
    version = SourceVersionRecord(
        source_version_id=stable_id("source-version", "fixture:repo", digest),
        source_id="fixture:repo",
        family=SourceFamily.ATCSCC_ADVISORY,
        asset_id=None,
        content=content,
        content_sha256=digest,
        source_url=None,
        logical_time=None,
        metadata={},
    )

    assert isinstance(store.sources, SourceRepository)
    assert isinstance(store.semantic, SemanticRepository)
    assert isinstance(store.retrieval, RetrievalRepository)
    assert store.sources.register_source_version(version) == "inserted"
    assert store.sources.get_source_version(version.source_version_id) == version
    assert store.retrieval.get_event("event:missing") is None
    assert store.semantic.get_knowledge_revision() == 0
    store.close()
