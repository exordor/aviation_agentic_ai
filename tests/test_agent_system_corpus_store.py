"""Focused contracts for the cross-run TMI-event corpus store."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path

from aviation_agentic_ai.agent_system.contracts import (
    PersistedProfileGap,
    SourceSnapshotRegistry,
    stable_id,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusObservation,
    CorpusQueryStore,
    build_corpus,
    load_event_catalog,
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
    event_type: str = "atm:GroundStopTMI",
    facility_id: str = _fixture_module.FACILITY_ID,
    formal_reason: str | None = None,
    evidence_text: str | None = None,
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
        if evidence_text is not None:
            updated["evidence_text"] = evidence_text
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


def _write_context_run(run_dir: Path) -> None:
    _fixture_module._write_context_layer(run_dir)


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


def _set_snapshot_content(run_dir: Path, content: str) -> str:
    content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    snapshot_path = run_dir / "source_snapshots.jsonl"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    snapshot["content"] = content
    snapshot["content_sha256"] = content_sha256
    snapshot_path.write_text(
        json.dumps(snapshot, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    graph_path = run_dir / "kg.jsonl"
    graph_rows = [
        json.loads(line)
        for line in graph_path.read_text(encoding="utf-8").splitlines()
    ]
    for row in graph_rows:
        if _fixture_module.SOURCE_ID in row["source_ids"]:
            row["source_snapshot_checksums"][_fixture_module.SOURCE_ID] = (
                content_sha256
            )
    graph_path.write_text(
        "".join(json.dumps(row) + "\n" for row in graph_rows),
        encoding="utf-8",
    )

    trace_path = run_dir / "fact_trace.jsonl"
    trace_rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
    ]
    for row in trace_rows:
        row["source_snapshot_sha256"] = content_sha256
    trace_path.write_text(
        "".join(json.dumps(row) + "\n" for row in trace_rows),
        encoding="utf-8",
    )
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"]["source_snapshots"]["sha256"] = (
        hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    )
    manifest["context_artifacts"]["fact_trace"]["sha256"] = hashlib.sha256(
        trace_path.read_bytes()
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return content_sha256


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


def test_build_corpus_retains_revised_versions_of_one_logical_source(
    tmp_path: Path,
) -> None:
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    event_id = "urn:event:revised-source"
    _write_run(run_a, event_id=event_id, suffix="stable")
    _write_run(run_b, event_id=event_id, suffix="stable")
    revised_content = (
        _fixture_module.ADVISORY_CONTENT + "REVISION: UPDATED SOURCE TEXT\n"
    )
    revised_sha256 = _set_snapshot_content(run_b, revised_content)

    corpus_dir = tmp_path / "corpus"
    manifest = build_corpus([run_a, run_b], corpus_dir)

    original_sha256 = hashlib.sha256(
        _fixture_module.ADVISORY_CONTENT.encode("utf-8")
    ).hexdigest()
    bindings = [
        json.loads(line)
        for line in (corpus_dir / "source_bindings.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    evidence_links = [
        json.loads(line)
        for line in (corpus_dir / "evidence_links.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert manifest.source_object_count == 2
    assert manifest.source_binding_count == 2
    assert len(bindings) == 2
    assert {
        (row["event_id"], row["source_id"], row["object_key"])
        for row in bindings
    } == {
        (event_id, _fixture_module.SOURCE_ID, original_sha256),
        (event_id, _fixture_module.SOURCE_ID, revised_sha256),
    }
    assert {
        row["artifact_id"]
        for row in evidence_links
        if row["owner_kind"] == "fact"
    } == {original_sha256, revised_sha256}


def test_build_corpus_merges_events_and_full_iri_facts(tmp_path: Path) -> None:
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    event_a = "urn:event:a"
    event_b = "urn:event:b"
    _write_run(run_a, event_id=event_a, suffix="a")
    _write_run(run_b, event_id=event_b, suffix="b")

    build_corpus([run_a, run_b], tmp_path / "corpus")

    events = load_event_catalog(tmp_path / "corpus")
    facts = load_corpus_facts(tmp_path / "corpus")
    event_a_facts = load_corpus_facts(
        tmp_path / "corpus",
        event_id=event_a,
    )
    assert [event.event_id for event in events] == [event_a, event_b]
    assert len(facts) == 8
    assert len(event_a_facts) == 4
    assert {fact.fact_id for fact in event_a_facts} == set(events[0].fact_ids)
    assert all(fact.predicate_iri.startswith("http") for fact in facts)


def test_build_corpus_v3_merges_semantic_facts_and_keeps_evidence_links(
    tmp_path: Path,
) -> None:
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    _write_run(
        run_a,
        event_id="urn:event:duplicate",
        suffix="a",
        evidence_text="SIGNATURE:",
    )
    _write_run(
        run_b,
        event_id="urn:event:duplicate",
        suffix="b",
        evidence_text="SIGNATURE:\n26/05/19 20:30",
    )

    corpus_dir = tmp_path / "corpus"
    manifest = build_corpus([run_b, run_a], corpus_dir)

    facts = [
        json.loads(line)
        for line in (corpus_dir / "facts.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    links = [
        json.loads(line)
        for line in (corpus_dir / "evidence_links.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert manifest.manifest_version == "tmi-event-corpus-v3"
    assert len(facts) == 4
    assert len(links) == 8
    assert {link["owner_kind"] for link in links} == {"fact"}
    assert len({link["owner_id"] for link in links}) == 4


def test_build_corpus_v3_preserves_context_and_observation_boundaries(
    tmp_path: Path,
) -> None:
    context_run = tmp_path / "context"
    _write_context_run(context_run)
    _write_reason_profile_gap(context_run, event_id=_fixture_module.EVENT_ID)
    observation_run = tmp_path / "observations"
    _fixture_module._write_formal_observation_layer(observation_run)

    corpus_dir = tmp_path / "corpus"
    manifest = build_corpus([context_run], corpus_dir)
    observation_corpus_dir = tmp_path / "observation-corpus"
    build_corpus([observation_run], observation_corpus_dir)

    associations = [
        json.loads(line)
        for line in (corpus_dir / "context_associations.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    gaps = [
        json.loads(line)
        for line in (corpus_dir / "profile_gaps.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    observations = [
        json.loads(line)
        for line in (observation_corpus_dir / "observations.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    formal_fact_ids = {
        row["fact_id"]
        for row in (
            json.loads(line)
            for line in (corpus_dir / "facts.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    assert manifest.artifacts["context_associations"].count == len(associations)
    assert associations and all(row["causal_claim"] is False for row in associations)
    assert not formal_fact_ids.intersection(
        row["association_id"] for row in associations
    )
    assert gaps[0]["evidence_text"] == "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
    assert any(row["value"] == 0 for row in observations)
    nullable = CorpusObservation.model_validate(
        {**observations[0], "value": None}
    )
    assert nullable.value is None


def test_build_corpus_v3_registers_the_complete_layout_stably(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    _write_run(run_dir, event_id="urn:event:stable", suffix="stable")
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_manifest = build_corpus([run_dir], first)
    second_manifest = build_corpus([run_dir], second)

    expected = {
        "build_results",
        "artifacts",
        "source_objects",
        "source_bindings",
        "events",
        "facts",
        "event_facts",
        "evidence_links",
        "profile_gaps",
        "context_associations",
        "observations",
        "alignment_audit",
        "tmi_coverage",
        "kg",
        "kg_ttl",
        "neo4j_nodes",
        "neo4j_relationships",
    }
    assert set(first_manifest.artifacts) == expected
    assert first_manifest == second_manifest
    alignment = json.loads(
        (first / "alignment_audit.json").read_text(encoding="utf-8")
    )
    coverage = json.loads(
        (first / "tmi_coverage.json").read_text(encoding="utf-8")
    )
    assert alignment["formal_fact_count"] == first_manifest.fact_count
    assert alignment["unknown_formal_term_count"] == 0
    assert coverage["selected_count"] == 1
    assert coverage["eligible_count"] == 1
    assert coverage["published_event_count"] == 1
    ground_stop = next(
        row for row in coverage["families"] if row["family"] == "GS"
    )
    assert ground_stop["detected_count"] == 1
    assert ground_stop["published_count"] == 1
    for metadata in first_manifest.artifacts.values():
        first_path = first / metadata.path
        second_path = second / metadata.path
        assert first_path.exists()
        if first_path.is_dir():
            assert sorted(path.name for path in first_path.iterdir()) == sorted(
                path.name for path in second_path.iterdir()
            )
        else:
            assert first_path.read_bytes() == second_path.read_bytes()


def test_build_corpus_uses_semantic_not_legacy_fact_identity(tmp_path: Path) -> None:
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

    manifest = build_corpus([run_a, run_b], tmp_path / "corpus")

    assert manifest.fact_count == 8


def test_build_corpus_collapses_repeated_runs_of_the_same_event(
    tmp_path: Path,
) -> None:
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    event_id = "urn:event:repeated"
    _write_run(run_a, event_id=event_id, suffix="stable")
    _write_run(run_b, event_id=event_id, suffix="stable")
    _set_snapshot_timestamp(run_b, "2026-05-20T20:30:00+00:00")

    manifest = build_corpus([run_a, run_b], tmp_path / "corpus")

    events = load_event_catalog(tmp_path / "corpus")
    bindings = (
        tmp_path / "corpus" / "source_bindings.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    memberships = (
        tmp_path / "corpus" / "event_facts.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    assert manifest.run_count == 2
    assert manifest.event_count == 1
    assert len(events) == 1
    assert events[0].run_ids == ["run-a", "run-b"]
    assert len(bindings) == 1
    binding = json.loads(bindings[0])
    assert binding["snapshot_timestamps"] == [
        "2026-05-19T20:30:00+00:00",
        "2026-05-20T20:30:00+00:00",
    ]
    assert len(memberships) == 4


def test_corpus_query_store_filters_and_pages_events(tmp_path: Path) -> None:
    from aviation_agentic_ai.agent_system.corpus_store import (
        CorpusEventQuery,
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
    first_page = store.find_events(
        CorpusEventQuery(facility_id=kjfk, limit=1)
    )
    second_page = store.find_events(
        CorpusEventQuery(facility_id=kjfk, offset=1, limit=1)
    )
    gdp_page = store.find_events(
        CorpusEventQuery(
            event_type_iri=(
                "https://data.nasa.gov/ontologies/atmonto/ATM#"
                "GroundDelayProgramTMI"
            )
        )
    )

    assert first_page.total_matches == 2
    assert [event.event_id for event in first_page.events] == ["urn:event:a"]
    assert [event.event_id for event in second_page.events] == ["urn:event:c"]
    assert [event.event_id for event in gdp_page.events] == ["urn:event:c"]
    assert {
        fact.subject_iri for fact in store.get_event_facts("urn:event:c")
    } == {"urn:event:c"}


def test_corpus_query_store_returns_context_observations_and_gap_evidence(
    tmp_path: Path,
) -> None:
    """Removing corpus-only context records would make this read insufficient."""

    run_dir = tmp_path / "run"
    _write_context_run(run_dir)
    _write_reason_profile_gap(run_dir, event_id=_fixture_module.EVENT_ID)
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_dir], corpus_dir)

    store = CorpusQueryStore(corpus_dir)

    context = store.get_weather_context(_fixture_module.EVENT_ID)
    gaps = store.get_event_evidence(_fixture_module.EVENT_ID)
    assert {item.relation_type for item in context} == {
        "latest_forecast_known_at_issue",
    }
    assert any(
        item.evidence_text == "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
        for item in gaps
    )


def test_corpus_query_store_builds_an_event_scoped_graph_view(tmp_path: Path) -> None:
    """Building adjacency from all corpus facts would leak another event."""

    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    _write_run(run_a, event_id="urn:event:a", suffix="a")
    _write_run(run_b, event_id="urn:event:b", suffix="b")
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_a, run_b], corpus_dir)
    store = CorpusQueryStore(corpus_dir)
    graph = store.graph_for_event("urn:event:a")
    event_edges = graph.neighbors(
        "urn:event:a",
        direction="out",
    )

    assert event_edges
    assert not graph.neighbors(
        "urn:event:b",
        direction="out",
    )


def test_event_graph_filters_globally_merged_sources_to_selected_event(
    tmp_path: Path,
) -> None:
    """A shared semantic fact must not expose another event's source binding."""

    run_dir = tmp_path / "run"
    _write_run(run_dir, event_id="urn:event:a", suffix="a")
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_dir], corpus_dir)

    facts_path = corpus_dir / "facts.jsonl"
    rows = [
        json.loads(line)
        for line in facts_path.read_text(encoding="utf-8").splitlines()
    ]
    event_type = next(
        row
        for row in rows
        if row["predicate_iri"]
        == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    )
    event_type["source_ids"] = sorted(
        {*event_type["source_ids"], "urn:source:other-event"}
    )
    facts_path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )
    manifest_path = corpus_dir / "corpus_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"]["facts"]["sha256"] = hashlib.sha256(
        facts_path.read_bytes()
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    store = CorpusQueryStore(corpus_dir)
    graph = store.graph_for_event("urn:event:a")
    type_edges = graph.neighbors(
        "urn:event:a",
        direction="out",
        predicate_iris=("http://www.w3.org/1999/02/22-rdf-syntax-ns#type",),
    )

    assert type_edges
    assert {edge.source_ids for edge in type_edges} == {
        (_fixture_module.SOURCE_ID,)
    }


def test_export_event_contains_only_selected_event_artifacts(tmp_path: Path) -> None:
    """Writing a replayable run artifact into an event export is a contract bug."""

    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    _write_run(run_a, event_id="urn:event:a", suffix="a")
    _write_run(run_b, event_id="urn:event:b", suffix="b")
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_a, run_b], corpus_dir)

    export_dir = tmp_path / "event-export"
    from aviation_agentic_ai.agent_system import corpus_store

    export_event = getattr(corpus_store, "export_event", None)
    assert callable(export_event)
    export_event(corpus_dir=corpus_dir, event_id="urn:event:a", output_dir=export_dir)

    assert {
        path.name for path in export_dir.iterdir()
    } == {
        "tmi_event_export_manifest.json",
        "event.json",
        "facts.jsonl",
        "event_facts.jsonl",
        "evidence_links.jsonl",
        "profile_gaps.jsonl",
        "context_associations.jsonl",
        "observations.jsonl",
        "source_bindings.jsonl",
        "source_objects",
        "kg.ttl",
    }
    assert "urn:event:a" in (export_dir / "event.json").read_text(encoding="utf-8")
    assert "urn:event:b" not in (export_dir / "facts.jsonl").read_text(encoding="utf-8")
    assert [
        json.loads(line)
        for line in (export_dir / "event_facts.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line
    ] == [
        {"event_id": "urn:event:a", "fact_id": fact.fact_id}
        for fact in CorpusQueryStore(corpus_dir).get_event_facts("urn:event:a")
    ]
