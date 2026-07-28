"""Persistent case-vector index bound to one normalized corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.case_retrieval_index import (
    ChromaCaseRetrievalIndex,
    build_case_retrieval_index,
)
from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusArtifactMetadata,
    CorpusBuildManifest,
    CorpusCase,
    CorpusQueryStore,
)


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
KJFK = "urn:aviation-agentic-ai:facility:airport:KJFK"
KEWR = "urn:aviation-agentic-ai:facility:airport:KEWR"


class FakeEncoder:
    model_id = "test/four-dimensional"

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [
            [float(index + 1), 1.0, 0.0, 0.0]
            for index, _ in enumerate(texts)
        ]


class InconsistentEncoder:
    model_id = "test/inconsistent"

    def encode(self, texts: list[str]) -> list[list[float]]:
        assert len(texts) == 2
        return [[1.0, 0.0], [1.0, 0.0, 0.0]]


def _write_jsonl(
    path: Path,
    rows: list[StrictModel],
) -> CorpusArtifactMetadata:
    data = "".join(row.model_dump_json() + "\n" for row in rows).encode()
    path.write_bytes(data)
    return CorpusArtifactMetadata(
        path=path.name,
        count=len(rows),
        sha256=hashlib.sha256(data).hexdigest(),
    )


@pytest.fixture
def corpus_dir(tmp_path: Path) -> Path:
    cases = [
        CorpusCase(
            case_id="case:a",
            case_iri="urn:decision-case:a",
            reconstruction_iri="urn:decision-case-reconstruction:a",
            event_id="urn:event:a",
            run_ids=["run:a"],
            advisory_source_id="2026-05-19:123",
            event_type_iris=[f"{ATM}GroundStopTMI"],
            facility_ids=[KJFK],
            operational_start="2026-05-19T21:00:00+00:00",
            operational_end="2026-05-19T21:30:00+00:00",
            reason_status="profile_gap",
            reason_value="weather",
        ),
        CorpusCase(
            case_id="case:b",
            case_iri="urn:decision-case:b",
            reconstruction_iri="urn:decision-case-reconstruction:b",
            event_id="urn:event:b",
            run_ids=["run:b"],
            advisory_source_id="2026-05-19:138",
            event_type_iris=[f"{ATM}GroundDelayProgramTMI"],
            facility_ids=[KEWR],
            operational_start="2026-05-19T22:05:00+00:00",
            operational_end="2026-05-20T02:59:00+00:00",
            reason_status="formal",
            reason_value="weather",
        ),
    ]
    artifacts = {
        "cases": _write_jsonl(tmp_path / "cases.jsonl", cases),
        "facts": _write_jsonl(tmp_path / "facts.jsonl", []),
        "case_facts": _write_jsonl(tmp_path / "case_facts.jsonl", []),
        "source_bindings": _write_jsonl(
            tmp_path / "source_bindings.jsonl",
            [],
        ),
    }
    manifest = CorpusBuildManifest(
        corpus_id="corpus:test",
        run_count=2,
        case_count=2,
        fact_count=0,
        source_binding_count=0,
        source_object_count=0,
        artifacts=artifacts,
    )
    (tmp_path / "corpus_manifest.json").write_text(
        manifest.model_dump_json() + "\n",
        encoding="utf-8",
    )
    return tmp_path


def test_index_persists_one_normalized_vector_per_case(
    corpus_dir: Path,
) -> None:
    store = CorpusQueryStore(corpus_dir)
    manifest = build_case_retrieval_index(
        corpus_dir,
        encoder=FakeEncoder(),
    )
    index = ChromaCaseRetrievalIndex(
        store,
        corpus_dir / "case_index",
    )

    assert manifest.corpus_id == store.manifest.corpus_id
    assert manifest.document_count == len(store.cases)
    assert manifest.vector_count == len(store.cases)
    assert manifest.embedding_dimension == 4
    assert index.collection.count() == len(store.cases)
    vector = index.get_case_vector(store.cases[0].case_id)
    assert sum(value * value for value in vector) == pytest.approx(1.0)
    documents = (corpus_dir / "case_index" / "case_documents.jsonl").read_text(
        encoding="utf-8"
    )
    assert '"embedding"' not in documents
    assert '"vector"' not in documents


def test_repeated_build_recreates_stable_ids_without_duplicates(
    corpus_dir: Path,
) -> None:
    first = build_case_retrieval_index(corpus_dir, encoder=FakeEncoder())
    first_documents = (
        corpus_dir / "case_index" / "case_documents.jsonl"
    ).read_bytes()

    second = build_case_retrieval_index(corpus_dir, encoder=FakeEncoder())
    reopened = ChromaCaseRetrievalIndex(
        CorpusQueryStore(corpus_dir),
        corpus_dir / "case_index",
    )

    assert second == first
    assert (
        corpus_dir / "case_index" / "case_documents.jsonl"
    ).read_bytes() == first_documents
    assert reopened.collection.count() == 2


def test_inconsistent_dimensions_do_not_publish_manifest(
    corpus_dir: Path,
) -> None:
    manifest_path = (
        corpus_dir / "case_index" / "case_index_manifest.json"
    )

    with pytest.raises(ValueError, match="dimension"):
        build_case_retrieval_index(
            corpus_dir,
            encoder=InconsistentEncoder(),
        )

    assert not manifest_path.exists()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("corpus_id", "corpus:other", "another corpus"),
        ("embedding_dimension", 3, "dimension"),
        ("vector_count", 99, "count"),
    ],
)
def test_reader_rejects_stale_or_corrupt_index_contract(
    corpus_dir: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    build_case_retrieval_index(corpus_dir, encoder=FakeEncoder())
    manifest_path = (
        corpus_dir / "case_index" / "case_index_manifest.json"
    )
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload[field] = value
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        ChromaCaseRetrievalIndex(
            CorpusQueryStore(corpus_dir),
            corpus_dir / "case_index",
        )


def test_reader_rejects_modified_case_documents(
    corpus_dir: Path,
) -> None:
    build_case_retrieval_index(corpus_dir, encoder=FakeEncoder())
    documents_path = (
        corpus_dir / "case_index" / "case_documents.jsonl"
    )
    documents_path.write_text(
        documents_path.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="checksum"):
        ChromaCaseRetrievalIndex(
            CorpusQueryStore(corpus_dir),
            corpus_dir / "case_index",
        )
