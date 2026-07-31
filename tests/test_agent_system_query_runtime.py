"""Runtime assembly over the live evidence store and optional indexes."""

from __future__ import annotations

from pathlib import Path

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.query_runtime import open_query_runtime
from aviation_agentic_ai.agent_system.source_retrieval import (
    build_source_record_chunks,
)
from aviation_agentic_ai.agent_system.sources import build_source_version


def _config(store_root: Path) -> dict[str, object]:
    return {
        "agent_system": {
            "dataset_id": "dataset:query-runtime",
            "storage": {
                "root": str(store_root),
                "chroma": "chroma",
                "embedding_model": "model:query-runtime",
            },
        }
    }


def test_runtime_opens_store_without_manifest_or_vector_indexes(
    tmp_path: Path,
) -> None:
    store_root = tmp_path / "store"
    store = AviationEvidenceStore.open(
        store_root,
        dataset_id="dataset:query-runtime",
        create=True,
    )
    store.close()

    runtime = open_query_runtime(_config(store_root))
    try:
        assert runtime.store.dataset_id == "dataset:query-runtime"
        assert runtime.source_index is None
        assert runtime.event_index is None
    finally:
        runtime.store.close()


def test_runtime_degrades_source_and_event_indexes_independently(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import aviation_agentic_ai.agent_system.query_runtime as runtime_module

    store_root = tmp_path / "store"
    store = AviationEvidenceStore.open(
        store_root,
        dataset_id="dataset:query-runtime",
        create=True,
    )
    store.close()
    event_index = object()

    monkeypatch.setattr(
        runtime_module,
        "_open_source_index",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ValueError("source index stale")
        ),
    )
    monkeypatch.setattr(
        runtime_module,
        "_open_event_index",
        lambda *args, **kwargs: event_index,
    )

    runtime = open_query_runtime(_config(store_root))
    try:
        assert runtime.source_index is None
        assert runtime.event_index is event_index
    finally:
        runtime.store.close()


def test_lexical_search_honors_exact_source_version_whitelist(
    tmp_path: Path,
) -> None:
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:query-runtime",
        create=True,
    )
    first = build_source_version(
        SourceRecord(
            source_id="source:first",
            family=SourceFamily.ATCSCC_ADVISORY,
            content="GROUND STOP WEATHER",
        )
    )
    second = build_source_version(
        SourceRecord(
            source_id="source:second",
            family=SourceFamily.ATCSCC_ADVISORY,
            content="GROUND STOP VOLUME",
        )
    )
    try:
        store.register_source_version(first)
        store.register_source_version(second)
        store.upsert_source_chunks(
            (
                *build_source_record_chunks((first,)),
                *build_source_record_chunks((second,)),
            )
        )

        unrestricted = store.search_source_text(
            "GROUND",
            source_version_ids=None,
            current_only=False,
        )
        empty = store.search_source_text(
            "GROUND",
            source_version_ids=(),
            current_only=False,
        )
        selected = store.search_source_text(
            "GROUND",
            source_version_ids=(second.source_version_id,),
            current_only=False,
        )

        assert {row.source_version_id for row in unrestricted} == {
            first.source_version_id,
            second.source_version_id,
        }
        assert empty == ()
        assert [row.source_version_id for row in selected] == [
            second.source_version_id
        ]
    finally:
        store.close()
