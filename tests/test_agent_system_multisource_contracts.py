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
from aviation_agentic_ai.agent_system.query_tools import (
    QueryGraphStore,
    QueryToolError,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.agent_system import sources
from aviation_agentic_ai.agent_system.sources import build_source_snapshot
from aviation_agentic_ai.agent_system.workflow import (
    AuthoritySourceRecordRegistry,
    AuthoritySourceRegistryStatus,
    merge_authority_source_records,
)


def _record(source_id: str, family: SourceFamily, content: str) -> SourceRecord:
    return SourceRecord(source_id=source_id, family=family, content=content)


DECISION_PROFILE_REF = next(
    ref
    for ref in load_validation_profile_registry(
        decision_guide=load_schema_guide()
    ).refs
    if ref.layer == "decision"
)
PROFILE_REGISTRY = load_validation_profile_registry(
    decision_guide=load_schema_guide()
)


def _decision_fact(**fields: object) -> ValidatedFact:
    """Build a source-text decision fact with explicit v1 ownership."""

    fact_id = fields["fact_id"]
    assert isinstance(fact_id, str)
    return ValidatedFact(
        **fields,
        validation_profile=DECISION_PROFILE_REF,
        evidence_mode="source_text",
        evidence_ref=fact_id,
    )


def _artifact_metadata(path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.name,
        "count": sum(1 for line in data.splitlines() if line.strip()),
        "sha256": __import__("hashlib").sha256(data).hexdigest(),
        "status": "ok",
    }


def _write_current_query_run(
    run_dir,
    *,
    write_registry: bool = True,
) -> contracts.SourceSnapshot:
    """Write one hand-authored current run without using production manifest code."""

    snapshot = build_source_snapshot(
        _record(
            "advisory:1",
            SourceFamily.ATCSCC_ADVISORY,
            "GROUND STOP",
        )
    )
    graph_path = run_dir / "kg.jsonl"
    graph_path.write_text(
        json.dumps(
            {
                "triple_id": "fact:type",
                "subject": "urn:aviation-agentic-ai:event:1",
                "predicate": "rdf:type",
                "object": "atm:GroundStopTMI",
                "subject_class": "atm:GroundStopTMI",
                "object_class": "atm:GroundStopTMI",
                "object_kind": "iri",
                "source_document": snapshot.source_id,
                "evidence_text": "GROUND STOP",
                "profile_id": DECISION_PROFILE_REF.profile_id,
                "profile_checksum": DECISION_PROFILE_REF.profile_checksum,
                "validation_layer": "decision",
                "evidence_mode": "source_text",
                "evidence_ref": "fact:type",
                "source_ids": [snapshot.source_id],
                "source_snapshot_checksums": {
                    snapshot.source_id: snapshot.content_sha256,
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    context_artifacts: dict[str, dict[str, object]] = {}
    if write_registry:
        registry_path = contracts.SourceSnapshotRegistry(
            snapshots=[snapshot]
        ).write_jsonl(run_dir)
        context_artifacts["source_snapshots"] = _artifact_metadata(registry_path)
    layers = {}
    for profile in PROFILE_REGISTRY.profiles:
        layers[profile.ref.layer] = {
            "status": (
                "ok" if profile.ref.layer == "decision" else "insufficient"
            ),
            "profile_id": profile.ref.profile_id,
            "profile_checksum": profile.ref.profile_checksum,
            "formal_fact_count": (
                1 if profile.ref.layer == "decision" else 0
            ),
        }
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "decision-case-run-v1",
                "run_id": run_dir.name,
                "materialization": {
                    "materialized": True,
                    "fact_count": 1,
                    "profile_refs": [
                        DECISION_PROFILE_REF.model_dump(mode="json")
                    ],
                    "layer_fact_counts": {"decision": 1},
                    "artifacts": {"kg_jsonl": str(graph_path)},
                },
                "formal_layers": layers,
                "context_artifacts": context_artifacts,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return snapshot


def test_query_store_rejects_a_run_without_current_manifest(tmp_path):
    """A graph file alone cannot be mistaken for a queryable current run."""

    _write_current_query_run(tmp_path)
    (tmp_path / "run_manifest.json").unlink()

    with pytest.raises(QueryToolError, match="current run manifest"):
        QueryGraphStore(tmp_path)


def test_query_store_rejects_a_run_with_the_wrong_manifest_version(tmp_path):
    """A versioned but unsupported run is not a current query source."""

    _write_current_query_run(tmp_path)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["manifest_version"] = "decision-case-run-v0"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(QueryToolError, match="current run manifest version"):
        QueryGraphStore(tmp_path)


def test_profile_gap_requires_registered_jsonl_snapshot(tmp_path):
    """A legacy single snapshot cannot authorize a current profile gap."""

    snapshot = _write_current_query_run(tmp_path, write_registry=False)
    (tmp_path / "source_snapshot.json").write_text(
        snapshot.model_dump_json(),
        encoding="utf-8",
    )
    (tmp_path / "profile_gaps.jsonl").write_text(
        PersistedProfileGap(
            profile_gap_id="gap:1",
            event_id="urn:aviation-agentic-ai:event:1",
            field="measure",
            value="ground_stop",
            evidence_text="GROUND STOP",
            reason="not admitted by the active profile",
            source_id=snapshot.source_id,
            source_snapshot_sha256=snapshot.content_sha256,
        ).model_dump_json()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(QueryToolError, match="source_snapshots.jsonl"):
        QueryGraphStore(tmp_path)


def test_current_profile_owned_run_remains_queryable(tmp_path):
    """Current manifest, registry, ownership, and checksums authorize graph reads."""

    _write_current_query_run(tmp_path)

    store = QueryGraphStore(tmp_path)

    assert store.event_ids == ["urn:aviation-agentic-ai:event:1"]


def test_parallel_authority_record_reducer_deduplicates_identical_rows():
    """Parallel branches may repeat an identical audit row without duplicating it."""

    record = _record(
        "authority:pcg:ground-stop",
        SourceFamily.FAA_TERM,
        '{"authority_text":"Ground Stop"}',
    )

    merged = merge_authority_source_records(
        AuthoritySourceRecordRegistry(records=(record,)),
        AuthoritySourceRecordRegistry(records=(record.model_copy(deep=True),)),
    )

    assert merged.status is AuthoritySourceRegistryStatus.OK
    assert [row.source_id for row in merged.records] == [record.source_id]


@pytest.mark.parametrize(
    ("right_record", "reason_code"),
    [
        (
            _record(
                "authority:pcg:ground-stop",
                SourceFamily.FAA_TERM,
                '{"authority_text":"different"}',
            ),
            "AUTHORITY_SOURCE_ID_CONFLICT",
        ),
        (
            _record(
                "authority:pcg:ground-stop",
                SourceFamily.METAR,
                '{"authority_text":"Ground Stop"}',
            ),
            "AUTHORITY_SOURCE_FAMILY_NOT_ALLOWED",
        ),
    ],
)
def test_parallel_authority_record_reducer_blocks_without_partial_rows(
    right_record,
    reason_code,
):
    """A conflicting or non-authority row blocks the audit channel atomically."""

    left = _record(
        "authority:pcg:ground-stop",
        SourceFamily.FAA_TERM,
        '{"authority_text":"Ground Stop"}',
    )

    merged = merge_authority_source_records(
        AuthoritySourceRecordRegistry(records=(left,)),
        AuthoritySourceRecordRegistry(records=(right_record,)),
    )

    assert merged.status is AuthoritySourceRegistryStatus.BLOCKED
    assert merged.reason_code == reason_code
    assert merged.error_id
    assert merged.records == ()


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


def test_bts_outcome_bundle_requires_derivation_seeds_for_an_ok_result():
    """BTS aggregation cannot publish a summary without its row-level derivation seed."""

    assert "derivation_seeds" in contracts.BTSOutcomeBundle.model_fields


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


def test_registered_authority_snapshot_alone_creates_no_event_evidence():
    """Audit source registration is broader than event-fact authorization."""

    authority = build_source_snapshot(
        _record(
            "authority:pcg:ground-stop",
            SourceFamily.FAA_TERM,
            "The GS is a process that requires aircraft to remain on the ground.",
        )
    )
    registry = contracts.SourceSnapshotRegistry(snapshots=[authority])

    assert build_evidence_index([], registry) == {}


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

    snapshot = _write_current_query_run(tmp_path)
    event_id = "urn:aviation-agentic-ai:event:1"
    (tmp_path / "profile_gaps.jsonl").write_text(
        PersistedProfileGap(
            profile_gap_id="gap:1",
            event_id=event_id,
            field="measure",
            value="ground_stop",
            evidence_text="GROUND STOP",
            reason="not in the active profile",
            source_id=snapshot.source_id,
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
    fact = _decision_fact(
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
    fact = _decision_fact(
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
            profile_registry=PROFILE_REGISTRY,
            source_snapshot=registry,
            output_dir=tmp_path,
        )
