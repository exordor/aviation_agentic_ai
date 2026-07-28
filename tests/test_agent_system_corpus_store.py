"""Focused contracts for the cross-run decision-case corpus store."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from aviation_agentic_ai.agent_system.contracts import (
    PersistedProfileGap,
    SourceSnapshotRegistry,
    stable_id,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    build_corpus,
    load_case_catalog,
    load_corpus_facts,
)
from aviation_agentic_ai.cli_agent_system import agent_system


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
    event_type: str = "atm:GroundStopTMI",
    facility_id: str = _fixture_module.FACILITY_ID,
    formal_reason: str | None = None,
) -> None:
    rows = []
    for row in _base_rows():
        updated = dict(row)
        updated["subject"] = event_id
        updated["subject_class"] = event_type
        if row["predicate"] == "rdf:type":
            updated["object"] = event_type
            updated["object_class"] = event_type
        elif row["predicate"] == "atm:controlledNASelement":
            updated["object"] = facility_id
        updated["triple_id"] = (
            type_fact_id
            if row["predicate"] == "rdf:type" and type_fact_id is not None
            else f"{row['triple_id']}:{suffix}"
        )
        rows.append(updated)
    if formal_reason is not None:
        rows.append(
            {
                "triple_id": f"fact:reason:{suffix}",
                "subject": event_id,
                "predicate": "atm:impactingCondition",
                "object": formal_reason,
                "subject_class": event_type,
                "object_class": "",
                "object_kind": "literal",
                "source_document": _fixture_module.SOURCE_ID,
                "evidence_text": (
                    "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
                ),
            }
        )
    _write_graph(run_dir, rows)


def _write_reason_profile_gap(run_dir: Path, *, event_id: str) -> None:
    source_id = _fixture_module.SOURCE_ID
    evidence = "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
    registry = SourceSnapshotRegistry.read_jsonl(
        run_dir / "source_snapshots.jsonl"
    )
    snapshot = registry.get(source_id)
    assert snapshot is not None
    profile = _fixture_module.PROFILE_BY_LAYER["decision"]
    evidence_ref = stable_id(
        "profile-gap-evidence",
        source_id,
        snapshot.content_sha256,
        "impacting_condition",
        "weather",
        evidence,
    )
    profile_gap_id = stable_id(
        "profile-gap",
        event_id,
        "impacting_condition",
        "weather",
        "not_in_profile",
        evidence_ref,
        profile.profile_id,
        profile.profile_checksum,
        profile.layer,
    )
    gap = PersistedProfileGap(
        profile_gap_id=profile_gap_id,
        event_id=event_id,
        field="impacting_condition",
        value="weather",
        evidence_text=evidence,
        reason="not_in_profile",
        source_id=source_id,
        source_snapshot_sha256=snapshot.content_sha256,
        evidence_ref=evidence_ref,
        validation_profile=profile,
    )
    gap_path = run_dir / "profile_gaps.jsonl"
    gap_path.write_text(gap.model_dump_json() + "\n", encoding="utf-8")
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["profile_gaps"] = {
        "path": "profile_gaps.jsonl",
        "count": 1,
        "sha256": hashlib.sha256(gap_path.read_bytes()).hexdigest(),
        "status": "ok",
    }
    manifest_path.write_text(
        json.dumps(manifest, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


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


def test_corpus_query_store_filters_and_pages_cases(tmp_path: Path) -> None:
    from aviation_agentic_ai.agent_system.corpus_store import (
        CorpusCaseQuery,
        CorpusQueryStore,
    )

    kjfk = _fixture_module.FACILITY_ID
    kewr = "urn:aviation-agentic-ai:facility:airport:KEWR"
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    run_c = tmp_path / "run-c"
    _write_run(run_a, event_id="urn:event:a", suffix="a", facility_id=kjfk)
    _write_run(run_b, event_id="urn:event:b", suffix="b", facility_id=kewr)
    _write_run(
        run_c,
        event_id="urn:event:c",
        suffix="c",
        facility_id=kjfk,
        event_type="atm:GroundDelayProgramTMI",
    )
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_a, run_b, run_c], corpus_dir)

    store = CorpusQueryStore(corpus_dir)
    first_page = store.find_cases(
        CorpusCaseQuery(facility_id=kjfk, limit=1)
    )
    second_page = store.find_cases(
        CorpusCaseQuery(facility_id=kjfk, offset=1, limit=1)
    )
    gdp_page = store.find_cases(
        CorpusCaseQuery(
            event_type_iri=(
                "https://data.nasa.gov/ontologies/atmonto/ATM#"
                "GroundDelayProgramTMI"
            )
        )
    )

    assert first_page.total_matches == 2
    assert [case.case_id for case in first_page.cases] == ["urn:event:a"]
    assert [case.case_id for case in second_page.cases] == ["urn:event:c"]
    assert [case.case_id for case in gdp_page.cases] == ["urn:event:c"]
    assert {
        fact.subject_iri for fact in store.get_case_facts("urn:event:c")
    } == {"urn:event:c"}


def test_corpus_query_preserves_formal_gap_and_missing_reason_states(
    tmp_path: Path,
) -> None:
    from aviation_agentic_ai.agent_system.corpus_query import (
        answer_corpus_question,
    )
    from aviation_agentic_ai.agent_system.query_tool_graph import (
        DECLARED_REASON_QUESTION,
    )

    ground_stop = tmp_path / "ground-stop"
    gdp = tmp_path / "gdp"
    cancellation = tmp_path / "cancellation"
    _write_run(
        ground_stop,
        event_id="urn:event:ground-stop",
        suffix="ground-stop",
    )
    _write_reason_profile_gap(
        ground_stop,
        event_id="urn:event:ground-stop",
    )
    _write_run(
        gdp,
        event_id="urn:event:gdp",
        suffix="gdp",
        event_type="atm:GroundDelayProgramTMI",
        formal_reason="weather",
    )
    _write_run(
        cancellation,
        event_id="urn:event:cancellation",
        suffix="cancellation",
        event_type="atm:GroundDelayProgramTMI",
    )
    corpus_dir = tmp_path / "corpus"
    build_corpus([ground_stop, gdp, cancellation], corpus_dir)

    gap = answer_corpus_question(
        corpus_dir=corpus_dir,
        question=DECLARED_REASON_QUESTION,
        event_id="urn:event:ground-stop",
    )
    formal = answer_corpus_question(
        corpus_dir=corpus_dir,
        question=DECLARED_REASON_QUESTION,
        event_id="urn:event:gdp",
    )
    missing = answer_corpus_question(
        corpus_dir=corpus_dir,
        question=DECLARED_REASON_QUESTION,
        event_id="urn:event:cancellation",
    )

    assert gap.status == "insufficient"
    assert gap.retrieved_case_ids == ["urn:event:ground-stop"]
    assert gap.retrieved_fact_ids == []
    assert "profile-gap metadata" in gap.answer
    assert formal.status == "ok"
    assert formal.retrieved_case_ids == ["urn:event:gdp"]
    assert formal.retrieved_fact_ids == ["fact:reason:gdp"]
    assert "weather" in formal.answer
    assert "IMPACTING CONDITION: WEATHER / THUNDERSTORMS" in formal.answer
    assert missing.status == "insufficient"
    assert missing.retrieved_case_ids == ["urn:event:cancellation"]
    assert missing.retrieved_fact_ids == []
    assert "No declared reason" in missing.answer
    assert gap.model_calls == formal.model_calls == missing.model_calls == []


def test_ask_corpus_lists_bounded_cases_without_a_model(tmp_path: Path) -> None:
    from aviation_agentic_ai.agent_system.corpus_query import (
        CORPUS_CATALOG_QUESTION,
    )

    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    _write_run(run_a, event_id="urn:event:a", suffix="a")
    _write_run(run_b, event_id="urn:event:b", suffix="b")
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_a, run_b], corpus_dir)

    result = CliRunner().invoke(
        agent_system,
        [
            "ask-corpus",
            "--corpus-dir",
            str(corpus_dir),
            "--question",
            CORPUS_CATALOG_QUESTION,
            "--limit",
            "1",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "status: ok" in result.output
    assert "matching_cases: 2" in result.output
    assert "cases_returned: urn:event:a" in result.output
    assert "model_calls: 0" in result.output
