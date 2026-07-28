"""Focused contracts for the cross-run decision-case corpus store."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.corpus_store import (
    build_corpus,
    load_case_catalog,
    load_corpus_facts,
)


_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "corpus_store_query_tools_fixture",
    Path(__file__).with_name("test_agent_system_query_tools.py"),
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_fixture_module = importlib.util.module_from_spec(_FIXTURE_SPEC)
_FIXTURE_SPEC.loader.exec_module(_fixture_module)
_base_rows = _fixture_module._rows
_write_graph = _fixture_module._write_graph


def _write_run(
    run_dir: Path,
    *,
    event_id: str,
    suffix: str,
    type_fact_id: str | None = None,
) -> None:
    rows = []
    for row in _base_rows():
        updated = dict(row)
        updated["subject"] = event_id
        updated["triple_id"] = (
            type_fact_id
            if row["predicate"] == "rdf:type" and type_fact_id is not None
            else f"{row['triple_id']}:{suffix}"
        )
        rows.append(updated)
    _write_graph(run_dir, rows)


def _set_snapshot_timestamp(run_dir: Path, timestamp: str) -> None:
    snapshot_path = run_dir / "source_snapshots.jsonl"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    snapshot["snapshot_timestamp"] = timestamp
    snapshot_path.write_text(
        json.dumps(snapshot, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"]["source_snapshots"]["sha256"] = (
        hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    )
    manifest_path.write_text(
        json.dumps(manifest, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def test_build_corpus_deduplicates_shared_source_objects(tmp_path: Path) -> None:
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    _write_run(run_a, event_id="urn:event:a", suffix="a")
    _write_run(run_b, event_id="urn:event:b", suffix="b")

    manifest = build_corpus([run_b, run_a], tmp_path / "corpus")

    objects = sorted((tmp_path / "corpus" / "source_objects").glob("*.txt"))
    assert manifest.run_count == 2
    assert manifest.source_object_count == 1
    assert len(objects) == 1
    assert objects[0].read_text(encoding="utf-8") == _fixture_module.ADVISORY_CONTENT


def test_build_corpus_merges_cases_and_full_iri_facts(tmp_path: Path) -> None:
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    event_a = "urn:event:a"
    event_b = "urn:event:b"
    _write_run(run_a, event_id=event_a, suffix="a")
    _write_run(run_b, event_id=event_b, suffix="b")

    build_corpus([run_a, run_b], tmp_path / "corpus")

    cases = load_case_catalog(tmp_path / "corpus")
    facts = load_corpus_facts(tmp_path / "corpus")
    event_a_facts = load_corpus_facts(
        tmp_path / "corpus",
        event_id=event_a,
    )
    assert [case.event_id for case in cases] == [event_a, event_b]
    assert len(facts) == 8
    assert len(event_a_facts) == 4
    assert {fact.fact_id for fact in event_a_facts} == set(cases[0].fact_ids)
    assert all(fact.predicate_iri.startswith("http") for fact in facts)


def test_build_corpus_rejects_conflicting_fact_content(tmp_path: Path) -> None:
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    _write_run(
        run_a,
        event_id="urn:event:a",
        suffix="a",
        type_fact_id="fact:conflict",
    )
    _write_run(
        run_b,
        event_id="urn:event:b",
        suffix="b",
        type_fact_id="fact:conflict",
    )

    with pytest.raises(ValueError, match="conflicting fact content"):
        build_corpus([run_a, run_b], tmp_path / "corpus")


def test_build_corpus_collapses_repeated_runs_of_the_same_case(
    tmp_path: Path,
) -> None:
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    event_id = "urn:event:repeated"
    _write_run(run_a, event_id=event_id, suffix="stable")
    _write_run(run_b, event_id=event_id, suffix="stable")
    _set_snapshot_timestamp(run_b, "2026-05-20T20:30:00+00:00")

    manifest = build_corpus([run_a, run_b], tmp_path / "corpus")

    cases = load_case_catalog(tmp_path / "corpus")
    bindings = (
        tmp_path / "corpus" / "source_bindings.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    memberships = (
        tmp_path / "corpus" / "case_facts.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    assert manifest.run_count == 2
    assert manifest.case_count == 1
    assert len(cases) == 1
    assert cases[0].run_ids == ["run-a", "run-b"]
    assert len(bindings) == 1
    binding = json.loads(bindings[0])
    assert binding["snapshot_timestamps"] == [
        "2026-05-19T20:30:00+00:00",
        "2026-05-20T20:30:00+00:00",
    ]
    assert len(memberships) == 4
