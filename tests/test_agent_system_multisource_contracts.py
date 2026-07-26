"""Focused multi-source source-snapshot and evidence-gate contracts."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system import contracts
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    EvidenceCard,
    EvidenceClaim,
    GraphPatchBlock,
    GraphPatchLine,
    GraphValidationResult,
    PersistedProfileGap,
    SourceFamily,
    SourceRecord,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.formal_graph import (
    build_evidence_index,
    write_fact_trace,
)
from aviation_agentic_ai.agent_system.materialize import materialize_validated_facts
from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system import sources
from aviation_agentic_ai.agent_system.sources import build_source_snapshot


def _record(source_id: str, family: SourceFamily, content: str) -> SourceRecord:
    return SourceRecord(source_id=source_id, family=family, content=content)


def test_source_snapshot_registry_round_trips_canonical_jsonl(tmp_path):
    """A new run persists each source snapshot in the canonical JSONL artifact."""

    registry = contracts.SourceSnapshotRegistry(
        snapshots=[
            build_source_snapshot(
                _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
            ),
            build_source_snapshot(
                _record("metar:KJFK:1", SourceFamily.METAR, "KJFK 192151Z TSRA")
            ),
        ]
    )

    path = registry.write_jsonl(tmp_path)

    assert path.name == "source_snapshots.jsonl"
    assert [json.loads(line)["source_id"] for line in path.read_text().splitlines()] == [
        "advisory:1",
        "metar:KJFK:1",
    ]
    assert contracts.SourceSnapshotRegistry.read_jsonl(path) == registry


def test_source_snapshot_is_immutable_after_checksum_binding():
    """Bound source content cannot be replaced after its checksum is recorded."""

    snapshot = build_source_snapshot(
        _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
    )

    with pytest.raises(ValidationError, match="frozen"):
        snapshot.content = "altered"


def test_source_snapshot_registry_rejects_duplicate_source_ids():
    """Two snapshots may not claim the same source ID in one run."""

    snapshot = build_source_snapshot(
        _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
    )

    with pytest.raises(ValueError, match="duplicate source snapshot ID"):
        contracts.SourceSnapshotRegistry(snapshots=[snapshot, snapshot])


def test_source_snapshot_registry_rejects_malformed_jsonl_rows(tmp_path):
    """Malformed canonical artifact rows fail before any evidence can bind to them."""

    path = tmp_path / "source_snapshots.jsonl"
    path.write_text('{"source_id": "metar:1"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="invalid source snapshot JSON at line 1"):
        contracts.SourceSnapshotRegistry.read_jsonl(path)


def test_source_snapshot_registry_rejects_checksum_with_conflicting_content():
    """A repeated checksum cannot bind different source content."""

    advisory = build_source_snapshot(
        _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
    )
    forged_metar = build_source_snapshot(
        _record("metar:1", SourceFamily.METAR, "KJFK 192151Z TSRA")
    ).model_copy(update={"content_sha256": advisory.content_sha256})

    with pytest.raises(ValueError, match="checksum does not match content"):
        contracts.SourceSnapshotRegistry(snapshots=[advisory, forged_metar])


def test_source_snapshot_registry_rejects_source_family_mismatch():
    """A source ID cannot be registered under a family different from its record."""

    metar_snapshot = build_source_snapshot(
        _record("source:1", SourceFamily.METAR, "KJFK 192151Z TSRA")
    )

    with pytest.raises(ValueError, match="source snapshot family mismatch"):
        contracts.SourceSnapshotRegistry(
            snapshots=[metar_snapshot],
            expected_families={"source:1": SourceFamily.ATCSCC_ADVISORY},
        )


def test_evidence_index_binds_a_claim_to_its_matching_source_snapshot():
    """Evidence survives only when it is contained in the snapshot named by source ID."""

    registry = contracts.SourceSnapshotRegistry(
        snapshots=[
            build_source_snapshot(
                _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
            ),
            build_source_snapshot(
                _record("metar:1", SourceFamily.METAR, "KJFK 192151Z TSRA")
            ),
        ]
    )
    card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="weather",
                value="thunderstorm",
                evidence_text="KJFK 192151Z TSRA",
                source_id="metar:1",
            )
        ],
    )

    index = build_evidence_index([card], registry)

    assert index == {"metar:1": card.claims}


def test_evidence_index_rejects_text_from_the_wrong_source_snapshot():
    """A claim cannot cite advisory source ID for text found only in a METAR."""

    registry = contracts.SourceSnapshotRegistry(
        snapshots=[
            build_source_snapshot(
                _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
            ),
            build_source_snapshot(
                _record("metar:1", SourceFamily.METAR, "KJFK 192151Z TSRA")
            ),
        ]
    )
    card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="weather",
                value="thunderstorm",
                evidence_text="KJFK 192151Z TSRA",
                source_id="advisory:1",
            )
        ],
    )

    assert build_evidence_index([card], registry) == {}


def test_evidence_index_rejects_a_snapshot_with_a_bad_checksum():
    """Legacy single-snapshot input also fails closed when its checksum is forged."""

    snapshot = build_source_snapshot(
        _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
    ).model_copy(update={"content_sha256": "0" * 64})
    card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="measure",
                value="ground_stop",
                evidence_text="GROUND STOP",
                source_id="advisory:1",
            )
        ],
    )

    assert build_evidence_index([card], snapshot) == {}


def test_query_store_reads_canonical_multisource_snapshot_artifact(tmp_path):
    """A new-run profile gap validates against its named JSONL source snapshot."""

    snapshot = build_source_snapshot(
        _record("metar:1", SourceFamily.METAR, "KJFK 192151Z TSRA")
    )
    contracts.SourceSnapshotRegistry(snapshots=[snapshot]).write_jsonl(tmp_path)
    event_id = "urn:aviation-agentic-ai:event:1"
    (tmp_path / "kg.jsonl").write_text(
        json.dumps(
            {
                "triple_id": "fact:type",
                "subject": event_id,
                "predicate": "rdf:type",
                "object": "atm:GroundDelayProgramTMI",
                "source_document": "metar:1",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "profile_gaps.jsonl").write_text(
        PersistedProfileGap(
            profile_gap_id="gap:1",
            event_id=event_id,
            field="weather_observation",
            value="thunderstorm",
            evidence_text="KJFK 192151Z TSRA",
            reason="not in the active profile",
            source_id="metar:1",
            source_snapshot_sha256=snapshot.content_sha256,
        ).model_dump_json()
        + "\n",
        encoding="utf-8",
    )

    store = QueryGraphStore(tmp_path)

    assert [gap.profile_gap_id for gap in store.profile_gaps] == ["gap:1"]


def test_source_snapshot_registry_builds_from_records_and_writes_new_run_artifact(tmp_path):
    """The source layer emits the canonical snapshot artifact for an ingest run."""

    registry = sources.build_source_snapshot_registry(
        [
            _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP"),
            _record("taf:1", SourceFamily.TAF, "TAF KJFK 1920Z"),
        ]
    )

    path = sources.write_source_snapshot_registry(registry, tmp_path)

    assert path.name == "source_snapshots.jsonl"
    assert contracts.SourceSnapshotRegistry.read_jsonl(path).snapshots == registry.snapshots


def test_fact_trace_uses_the_checksum_of_the_matched_multisource_claim(tmp_path):
    """Trace persistence uses the matched claim's snapshot, not registry order."""

    advisory = build_source_snapshot(
        _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
    )
    metar = build_source_snapshot(
        _record("metar:1", SourceFamily.METAR, "KJFK 192151Z TSRA")
    )
    registry = contracts.SourceSnapshotRegistry(snapshots=[advisory, metar])
    line = GraphPatchLine(
        subject="urn:event:1",
        predicate="atm:impactingCondition",
        object="thunderstorm",
        source_ids=[metar.source_id],
    )
    fact = ValidatedFact(
        fact_id="fact:weather",
        subject_iri=line.subject,
        subject_class_iri="https://example.test/GroundDelayProgram",
        predicate_iri="https://example.test/impactingCondition",
        object_kind="literal",
        object_value=line.object,
        source_ids=[metar.source_id],
        evidence_texts=[metar.content],
    )
    card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="weather",
                value="thunderstorm",
                evidence_text=metar.content,
                source_id=metar.source_id,
            )
        ],
    )

    path = write_fact_trace(
        result=GraphValidationResult(accepted=[fact], publishable=True),
        block=GraphPatchBlock(patch_lines=[line]),
        evidence_cards=[card],
        source_snapshot=registry,
        output_dir=tmp_path,
    )

    row = json.loads(path.read_text(encoding="utf-8"))
    assert row["source_id"] == metar.source_id
    assert row["source_snapshot_sha256"] == metar.content_sha256


def test_materialization_rejects_a_fact_without_a_registered_snapshot(tmp_path):
    """Materialization cannot persist provenance absent from the run registry."""

    advisory = build_source_snapshot(
        _record("advisory:1", SourceFamily.ATCSCC_ADVISORY, "GROUND STOP")
    )
    registry = contracts.SourceSnapshotRegistry(snapshots=[advisory])
    fact = ValidatedFact(
        fact_id="fact:unsnapshotted",
        subject_iri="urn:event:1",
        subject_class_iri="https://example.test/GroundDelayProgram",
        predicate_iri="https://example.test/advisoryNumber",
        object_kind="literal",
        object_value="1",
        source_ids=["caller:extra"],
    )

    with pytest.raises(ValueError, match="checksum-valid source snapshots"):
        materialize_validated_facts(
            facts=[fact],
            guide=load_schema_guide(),
            source_snapshot=registry,
            output_dir=tmp_path,
        )
