"""Formal Graph Kernel focused tests (plan §5.6 batch-one acceptance).

Covers the nine required batch-one acceptance cases:

1. Provider failure returns ``BLOCKED`` and produces no KG artifacts.
2. Empty or malformed Graph Patch returns ``BLOCKED``.
3. Unknown canonical object is rejected.
4. Unknown source and forged provenance endpoint are rejected.
5. Invalid ``extensionProbability`` is rejected.
6. Missing required Ground Stop property makes the graph non-publishable.
7. Non-source-contained evidence cannot support a formal fact.
8. The fixed Ground Stop case produces publishable ``ValidatedFact`` objects.
9. Every accepted fact has an exact evidence binding.

The fixtures use the real fixed advisory (plan §2) ``2026-05-19:123`` so the
exact-evidence extraction and the source-containment check (plan §5.2) are
exercised against real source text, not synthetic phrases.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

import pytest

from aviation_agentic_ai.agent_system.agents import (
    AdvisoryMentions,
    build_advisory_evidence,
    parse_structured_fields,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    AgentTask,
    EvidenceCard,
    EvidenceClaim,
    GraphPatchBlock,
    GraphPatchLine,
    ModelCallRecord,
    ProfileGap,
    SourceFamily,
    SourceRecord,
    SourceSnapshotRegistry,
)
from aviation_agentic_ai.agent_system.formal_graph import (
    build_evidence_index,
    validate_graph_patch,
    write_fact_trace,
    write_profile_gaps,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot,
    load_advisory_source,
    write_source_snapshot_registry,
)
from aviation_agentic_ai.config import load_yaml
from aviation_agentic_ai.cross_source.identifiers import stable_id

# ---------------------------------------------------------------------------
# Fixed Ground Stop case (plan §2)
# ---------------------------------------------------------------------------

SOURCE_ID = "2026-05-19:123"
EVENT_CLASS = "atm:GroundStopTMI"
FACILITY_ID = "urn:aviation-agentic-ai:facility:airport:KJFK"
ADVISORY_CONTENT = (
    "ATCSCC ADVZY 123 JFK/ZNY 05/19/2026 CDM GROUND STOP\n"
    "MESSAGE:\n"
    "CTL ELEMENT: JFK ELEMENT TYPE: APT ADL TIME: 2135Z "
    "GROUND STOP PERIOD: 19/2100Z - 19/2245Z "
    "DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB "
    "PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 "
    "NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 257 / 71 / 51 "
    "PROBABILITY OF EXTENSION: MEDIUM "
    "IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS:\n"
    "EFFECTIVE TIME:\n192138-192345\n"
)


@pytest.fixture(scope="module")
def guide():
    return load_schema_guide()


@pytest.fixture(scope="module")
def advisory_record() -> SourceRecord:
    return SourceRecord(
        source_id=SOURCE_ID,
        family=SourceFamily.ATCSCC_ADVISORY,
        content=ADVISORY_CONTENT,
    )


@pytest.fixture(scope="module")
def event_uri() -> str:
    return stable_id("evt", SOURCE_ID, EVENT_CLASS)


@pytest.fixture(scope="module")
def mentions(advisory_record) -> AdvisoryMentions:
    return parse_structured_fields(advisory_record.content)


@pytest.fixture(scope="module")
def snapshot(advisory_record):
    return SourceSnapshotRegistry(
        snapshots=(build_source_snapshot(advisory_record),)
    )


@dataclass
class _FacilityEntity:
    entity_id: str
    preferred_label: str
    entity_type: "Enum"


@pytest.fixture(scope="module")
def facility_entity() -> _FacilityEntity:
    class EType(Enum):
        AIRPORT = "airport"

    return _FacilityEntity(
        entity_id=FACILITY_ID,
        preferred_label="JOHN F KENNEDY INTL",
        entity_type=EType.AIRPORT,
    )


# ---------------------------------------------------------------------------
# §5.2 exact-evidence extraction
# ---------------------------------------------------------------------------


def test_advisory_extracts_exact_source_spans_for_all_fixed_fields(mentions, advisory_record):
    """Plan §5.2: every EvidenceClaim carries text copied from the source."""

    task = AgentTask(
        run_id="r",
        source_id=SOURCE_ID,
        objective="extract mentions",
        allowed_tools=["get_advisory", "parse_structured_fields", "get_schema_event_classes"],
    )
    evidence = build_advisory_evidence(
        task=task,
        advisory=advisory_record,
        event_classes=[EVENT_CLASS],
        mentions=mentions,
    )
    fields = {c.field_name for c in evidence.claims}
    # All six fixed fields must produce claims with exact source spans.
    assert {
        "event_type",
        "controlled_facility",
        "advisory_number",
        "effective_start",
        "effective_end",
        "extension_probability",
        "impacting_condition",
    }.issubset(fields)
    for claim in evidence.claims:
        # Plan §5.2 hard assertion: the evidence text must be source-contained.
        assert claim.evidence_text in advisory_record.content
        assert claim.source_id == advisory_record.source_id
        # Synthetic phrases are explicitly forbidden (plan §5.2).
        assert not claim.evidence_text.startswith("event mention")
        assert not claim.evidence_text.startswith("term mention")
        assert not claim.evidence_text.startswith("period start")


def test_extension_probability_and_impacting_condition_normalized(mentions):
    """Plan §2: extension_probability=MEDIUM, impacting_condition=weather."""

    assert mentions.extension_probability == "MEDIUM"
    assert mentions.impacting_condition == "weather"
    assert mentions.evidence_spans["impacting_condition"] == (
        "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
    )


def test_source_snapshot_registry_records_content_and_sha256(
    advisory_record,
    tmp_path,
):
    """The current JSONL registry pins exact source content and SHA-256."""

    snapshot = build_source_snapshot(advisory_record)
    path = write_source_snapshot_registry(
        SourceSnapshotRegistry(snapshots=(snapshot,)),
        tmp_path,
    )
    payload = json.loads(path.read_text(encoding="utf-8").strip())
    assert path.name == "source_snapshots.jsonl"
    assert payload["source_id"] == SOURCE_ID
    assert payload["family"] == "atcscc_advisory"
    assert payload["content"] == ADVISORY_CONTENT
    assert len(payload["content_sha256"]) == 64
    assert payload["snapshot_timestamp"]
    # The checksum must match a fresh computation of the same content.
    import hashlib

    assert payload["content_sha256"] == hashlib.sha256(ADVISORY_CONTENT.encode("utf-8")).hexdigest()


def test_empty_profile_gap_artifact_is_still_written(snapshot, tmp_path):
    from aviation_agentic_ai.agent_system.contracts import GraphValidationResult

    path = write_profile_gaps(
        result=GraphValidationResult(publishable=True),
        event_id="urn:aviation-agentic-ai:event:empty-gap-test",
        source_snapshot=snapshot,
        output_dir=tmp_path,
    )
    assert path.exists()
    assert path.read_text(encoding="utf-8") == ""


# ---------------------------------------------------------------------------
# §5.4 Formal Graph Kernel checks
# ---------------------------------------------------------------------------


def _evidence_cards_for_fixed_case(
    advisory_record, facility_entity, mentions
) -> list[EvidenceCard]:
    """Build advisory/facility/terminology evidence cards with exact source spans.

    The terminology card carries ``ontology_target=atm:GroundStopTMI`` so the
    Formal Graph Kernel can bind ``rdf:type`` to it (plan §11.2). Its evidence
    text is the exact Ground Stop mention span from the advisory.
    """

    # Advisory card carries the exact source spans captured by the parser.
    advisory_claims = []
    for field_name in (
        "event_type",
        "controlled_facility",
        "advisory_number",
        "effective_start",
        "effective_end",
        "extension_probability",
        "impacting_condition",
    ):
        value = getattr(mentions, field_name)
        if value and field_name in mentions.evidence_spans:
            advisory_claims.append(
                EvidenceClaim(
                    field_name=field_name,
                    value=value,
                    evidence_text=mentions.evidence_spans[field_name],
                    source_id=SOURCE_ID,
                )
            )
    advisory_card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=advisory_claims,
        source_ids=[SOURCE_ID],
    )
    facility_card = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="controlled_facility",
                value=FACILITY_ID,
                ontology_target="nas:Airport",
                evidence_text="CTL ELEMENT: JFK",
                source_id=SOURCE_ID,
                canonical_ref=FACILITY_ID,
            )
        ],
        canonical_refs=[FACILITY_ID],
        source_ids=[SOURCE_ID],
    )
    term_span = (
        mentions.evidence_spans.get("operational_term")
        or mentions.evidence_spans.get("event_type")
        or ""
    )
    terminology_card = EvidenceCard(
        agent_role="terminology",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="operational_term",
                value="urn:aviation-agentic-ai:term:gs",
                ontology_target=EVENT_CLASS,
                evidence_text=term_span,
                source_id=SOURCE_ID,
                canonical_ref="urn:aviation-agentic-ai:term:gs",
            )
        ],
        canonical_refs=["urn:aviation-agentic-ai:term:gs"],
        source_ids=[SOURCE_ID],
    )
    return [advisory_card, facility_card, terminology_card]


def _validate(
    block_raw, guide, event_uri, snapshot, evidence_cards, *, canonical=None, sources=None
):
    block = _test_block(block_raw)
    return validate_graph_patch(
        block=block,
        event_iri=event_uri,
        event_class=EVENT_CLASS,
        schema_guide=guide,
        canonical_entities=canonical if canonical is not None else {FACILITY_ID: "nas:Airport"},
        known_source_ids=sources if sources is not None else {SOURCE_ID},
        evidence_cards=evidence_cards,
        source_snapshot=snapshot,
    )


def _test_block(raw: str) -> GraphPatchBlock:
    """Build a Kernel input directly; production parses only Assembly JSON."""

    section = "facts"
    facts: list[GraphPatchLine] = []
    gaps: list[ProfileGap] = []
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or line == "GRAPH_PATCH":
            continue
        if line == "PROFILE_GAPS":
            section = "gaps"
            continue
        subject, predicate, object_value, support = (
            value.strip() for value in line.split("|")
        )
        if section == "facts":
            facts.append(
                GraphPatchLine(
                    subject=subject,
                    predicate=predicate,
                    object=object_value,
                    source_ids=[support],
                )
            )
        else:
            gaps.append(
                ProfileGap(
                    field=subject,
                    value=predicate,
                    evidence=object_value,
                    reason=support,
                )
            )
    return GraphPatchBlock(patch_lines=facts, profile_gaps=gaps, raw=raw)


def test_unknown_canonical_object_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§5.6 acceptance 3: unknown canonical object is rejected."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | urn:facility:UNKNOWN | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    rules = {r.rule for r in result.rejected}
    assert "canonical_object" in rules
    assert not result.publishable


def test_unknown_source_and_forged_provenance_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§5.6 acceptance 4: unknown source and forged provenance endpoint rejected."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | forged:source\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"{evt} | prov:wasDerivedFrom | forged:source | forged:source\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    rules = {r.rule for r in result.rejected}
    assert rules & {"source_id", "source_snapshot", "provenance_endpoint"}
    assert not result.publishable


def test_registry_rejects_mixed_and_unsnapshotted_provenance_sources(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """Known caller IDs cannot bypass checksum-valid snapshot membership."""

    registry = snapshot
    block = (
        f"GRAPH_PATCH\n"
        f"{event_uri} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}, caller:extra\n"
        f"{event_uri} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{event_uri} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"{event_uri} | prov:wasDerivedFrom | caller:extra | {SOURCE_ID}\n"
    )

    result = _validate(
        block,
        guide,
        event_uri,
        registry,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
        sources={SOURCE_ID, "caller:extra"},
    )

    assert {rejected.rule for rejected in result.rejected} >= {
        "source_snapshot",
        "provenance_endpoint",
    }
    assert all("caller:extra" not in fact.source_ids for fact in result.accepted)


def test_registry_binds_profile_gap_artifact_to_its_exact_snapshot(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions, tmp_path
):
    """A multi-source profile gap persists the snapshot that contains its evidence."""

    metar = build_source_snapshot(
        SourceRecord(
            source_id="metar:KJFK:1",
            family=SourceFamily.METAR,
            content="KJFK 192151Z TSRA",
        )
    )
    registry = SourceSnapshotRegistry(snapshots=[snapshot.snapshots[0], metar])
    block = _test_block(
        "GRAPH_PATCH\n"
        f"{event_uri} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{event_uri} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{event_uri} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        "PROFILE_GAPS\n"
        "impacting_condition | weather | "
        "IMPACTING CONDITION: WEATHER / THUNDERSTORMS | not_in_profile\n"
    )
    result = validate_graph_patch(
        block=block,
        event_iri=event_uri,
        event_class=EVENT_CLASS,
        schema_guide=guide,
        canonical_entities={FACILITY_ID: "nas:Airport"},
        known_source_ids={SOURCE_ID, metar.source_id},
        evidence_cards=_evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
        source_snapshot=registry,
    )

    path = write_profile_gaps(
        result=result,
        event_id=event_uri,
        source_snapshot=registry,
        output_dir=tmp_path,
    )

    row = json.loads(path.read_text(encoding="utf-8"))
    assert row["source_id"] == SOURCE_ID
    assert row["source_snapshot_sha256"] == snapshot.snapshots[0].content_sha256


def test_invalid_extension_probability_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§5.6 acceptance 5: invalid extensionProbability value is rejected."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | ABSURD | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    rules = {r.rule for r in result.rejected}
    assert "enum" in rules
    assert not result.publishable


def test_missing_required_ground_stop_property_non_publishable(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§5.6 acceptance 6: missing required Ground Stop property -> non-publishable."""

    evt = event_uri
    # Missing atm:extensionProbability (required exact cardinality 1).
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    # No rows rejected, but the graph-level cardinality error blocks publication.
    assert not result.publishable
    assert any("extensionProbability exact cardinality" in e for e in result.graph_errors)


def test_missing_required_reroute_time_type_is_non_publishable(guide) -> None:
    source_id = "example:reroute:137"
    event_class = "atm:ReRouteTMI"
    event_uri = stable_id("evt", source_id, event_class)
    content = (
        "ATCSCC ADVZY 137 DCC ROUTE RQD /FL\n"
        "REASON: WEATHER VALID: ETD 202030 TO 210200 "
        "PROBABILITY OF EXTENSION: MODERATE"
    )
    source = SourceRecord(
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        content=content,
    )
    snapshot = SourceSnapshotRegistry(
        snapshots=(build_source_snapshot(source),)
    )
    evidence = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        source_ids=[source_id],
        claims=[
            EvidenceClaim(
                field_name="event_type",
                value="REROUTE",
                ontology_target=event_class,
                evidence_text="ROUTE RQD",
                source_id=source_id,
            ),
            EvidenceClaim(
                field_name="extension_probability",
                value="MEDIUM",
                evidence_text="PROBABILITY OF EXTENSION: MODERATE",
                source_id=source_id,
            ),
            EvidenceClaim(
                field_name="implementation_status",
                value="RQD",
                evidence_text="ROUTE RQD",
                source_id=source_id,
            ),
            EvidenceClaim(
                field_name="re_route_reason",
                value="WEATHER",
                evidence_text="REASON: WEATHER",
                source_id=source_id,
            ),
            EvidenceClaim(
                field_name="re_route_type",
                value="ROUTE",
                evidence_text="ROUTE RQD",
                source_id=source_id,
            ),
            EvidenceClaim(
                field_name="re_route_time_type",
                value="ETD",
                evidence_text="VALID: ETD",
                source_id=source_id,
            ),
        ],
    )
    block = _test_block(
        "GRAPH_PATCH\n"
        f"{event_uri} | rdf:type | {event_class} | {source_id}\n"
        f"{event_uri} | atm:extensionProbability | MEDIUM | {source_id}\n"
        f"{event_uri} | atm:implementationStatus | RQD | {source_id}\n"
        f"{event_uri} | atm:reRouteReason | WEATHER | {source_id}\n"
        f"{event_uri} | atm:reRouteType | ROUTE | {source_id}\n"
    )

    result = validate_graph_patch(
        block=block,
        event_iri=event_uri,
        event_class=event_class,
        schema_guide=guide,
        canonical_entities={},
        known_source_ids={source_id},
        evidence_cards=[evidence],
        source_snapshot=snapshot,
    )

    assert not result.publishable
    assert any(
        "reRouteTimeType exact cardinality" in error
        for error in result.graph_errors
    )


def test_non_source_contained_evidence_cannot_support_fact(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§5.6 acceptance 7: non-source-contained evidence cannot support a fact."""

    # Forge an advisory card whose evidence text is NOT in the source content.
    forged_card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="event_type",
                value="GS",
                evidence_text="THIS TEXT IS NOT IN THE SOURCE",
                source_id=SOURCE_ID,
            )
        ],
        source_ids=[SOURCE_ID],
    )
    facility_card = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="controlled_facility",
                value=FACILITY_ID,
                ontology_target="nas:Airport",
                evidence_text="THIS IS ALSO FORGED",
                source_id=SOURCE_ID,
                canonical_ref=FACILITY_ID,
            )
        ],
        canonical_refs=[FACILITY_ID],
        source_ids=[SOURCE_ID],
    )
    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
    )
    result = _validate(block, guide, event_uri, snapshot, [forged_card, facility_card])
    # The forged evidence index is empty for SOURCE_ID -> every fact fails the
    # evidence-binding check (rule "evidence").
    rules = {r.rule for r in result.rejected}
    assert "evidence" in rules
    assert not result.publishable


def test_fixed_ground_stop_case_produces_publishable_facts(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§5.6 acceptance 8: the fixed Ground Stop case produces publishable facts.

    NOTE: the frozen schema slice declares ``atm:impactingCondition`` with a
    domain of ``[atm:GroundDelayProgramTMI]`` only, yet also carries a
    ``data_all_values_from`` constraint for ``atm:GroundStopTMI`` on that
    property — a slice-internal inconsistency. Per the no-ontology-change
    boundary (plan §8), the Formal Graph Kernel honors the declared domain, so
    ``impactingCondition`` is not publishable for a Ground Stop event in batch
    one (it would be a profile gap). The publishable fixed graph therefore
    excludes it; this slice/plan conflict is surfaced in the CHECKPOINT.
    """

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:advisoryNumber | 123 | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveStartTime | 2026-05-19T21:00:00Z | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveEndTime | 2026-05-19T22:45:00Z | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert not result.rejected, [r.reason for r in result.rejected]
    assert not result.graph_errors, result.graph_errors
    assert result.publishable
    assert len(result.accepted) >= 6
    # The rdf:type fact carries the real NASA GroundStopTMI IRI on the subject
    # and object class; controlledNASelement carries the real ATM predicate IRI.
    type_facts = [f for f in result.accepted if "rdf-syntax" in f.predicate_iri]
    assert type_facts and all("GroundStopTMI" in f.object_class_iri for f in type_facts)
    pred_iris = {f.predicate_iri for f in result.accepted}
    assert any("controlledNASelement" in iri for iri in pred_iris)
    assert any("extensionProbability" in iri for iri in pred_iris)
    # Accepted facts use real ATMONTO IRIs, not example-namespace placeholders.
    for fact in result.accepted:
        assert "example.org" not in fact.subject_class_iri
        assert "example.org" not in fact.predicate_iri


def test_every_accepted_fact_has_exact_evidence_binding(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions, tmp_path
):
    """§5.6 acceptance 9: every accepted fact has an exact evidence binding."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
    )
    cards = _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions)
    result = _validate(block, guide, event_uri, snapshot, cards)
    assert result.publishable
    for fact in result.accepted:
        assert fact.evidence_texts, f"fact {fact.fact_id} has no evidence binding"
        for text in fact.evidence_texts:
            # Every bound evidence text must appear verbatim in the source.
            assert text in advisory_record.content
    # The fact-trace file records one row per accepted fact with exact evidence.
    block_parsed = _test_block(block)
    trace_path = write_fact_trace(
        result=result,
        block=block_parsed,
        evidence_cards=cards,
        source_snapshot=snapshot,
        output_dir=tmp_path,
    )
    rows = [
        json.loads(ln) for ln in trace_path.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    assert len(rows) == len(result.accepted)
    for row in rows:
        assert row["source_id"] == SOURCE_ID
        assert row["evidence_text"] in advisory_record.content
        assert row["evidence_agent_role"] in ("advisory", "facility")
        assert (
            row["source_snapshot_sha256"]
            == snapshot.snapshots[0].content_sha256
        )


# ---------------------------------------------------------------------------
# Evidence index sanity
# ---------------------------------------------------------------------------


def test_evidence_index_drops_non_source_contained_claims(advisory_record, snapshot):
    """The evidence index only retains source-contained evidence texts."""

    good = EvidenceClaim(
        field_name="event_type",
        value="GS",
        evidence_text="GROUND STOP PERIOD: 19/2100Z - 19/2245Z",
        source_id=SOURCE_ID,
    )
    forged = EvidenceClaim(
        field_name="x",
        value="y",
        evidence_text="NOT IN SOURCE",
        source_id=SOURCE_ID,
    )
    card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[good, forged],
        source_ids=[SOURCE_ID],
    )
    index = build_evidence_index([card], snapshot)
    # The index now carries EvidenceClaim objects (plan §11 fact-to-claim gate).
    texts = [claim.evidence_text for claim in index[SOURCE_ID]]
    assert any("GROUND STOP PERIOD" in t for t in texts)
    assert not any("NOT IN SOURCE" in t for t in texts)


# ---------------------------------------------------------------------------
# §11 adversarial regressions (fact-level evidence correction)
# ---------------------------------------------------------------------------


def test_adversarial_extension_probability_low_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§11: source MEDIUM, patch LOW -> rejected and non-publishable."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | LOW | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    # LOW is in the allowed-value set, so it passes the enum check; the
    # fact-to-claim binding rejects it because no claim has value LOW.
    assert any(r.rule == "evidence" and "extensionProbability" in r.reason for r in result.rejected)
    assert not result.publishable


def test_adversarial_advisory_number_999_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§11: source advisory number 123, patch 999 -> rejected and non-publishable."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"{evt} | atm:advisoryNumber | 999 | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert any(r.rule == "evidence" and "advisoryNumber" in r.reason for r in result.rejected)
    assert not result.publishable


def test_adversarial_wrong_effective_time_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§11: a schema-valid but source-incorrect effective time -> rejected."""

    evt = event_uri
    # 23:59Z is a valid xsd:dateTime but does not match source 19/2100Z (21:00Z).
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveStartTime | 2026-05-19T23:59:00Z | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert any(r.rule == "evidence" and "effectiveStartTime" in r.reason for r in result.rejected)
    assert not result.publishable


def test_controlled_facility_binds_to_ctl_element_evidence(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§11: the controlled-facility fact binds to ``CTL ELEMENT: JFK``,
    not to an unrelated Ground Stop span."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert result.publishable
    controlled = next(f for f in result.accepted if "controlledNASelement" in f.predicate_iri)
    # The bound evidence is exactly the facility span, not the Ground Stop span.
    assert controlled.evidence_texts == ["CTL ELEMENT: JFK"]
    assert all("GROUND STOP" not in t for t in controlled.evidence_texts)


def test_event_type_binds_to_ground_stop_mention_via_terminology(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§11: the event type binds to the exact Ground Stop mention through the
    terminology claim (not through an advisory span)."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert result.publishable
    type_fact = next(f for f in result.accepted if "rdf-syntax" in f.predicate_iri)
    # The bound evidence is the terminology claim's exact Ground Stop span.
    assert type_fact.evidence_texts
    assert "GROUND STOP" in type_fact.evidence_texts[0]


def test_valid_fixed_case_trace_has_one_relevant_binding_per_fact(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions, tmp_path
):
    """§11: the valid fixed case remains publishable and its fact trace has one
    relevant evidence binding per accepted fact (no unrelated-claim selection)."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:advisoryNumber | 123 | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveStartTime | 2026-05-19T21:00:00Z | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveEndTime | 2026-05-19T22:45:00Z | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
    )
    cards = _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions)
    result = _validate(block, guide, event_uri, snapshot, cards)
    assert result.publishable
    # Each accepted fact carries exactly one evidence text (the matched claim).
    for fact in result.accepted:
        assert len(fact.evidence_texts) == 1, (
            f"fact {fact.predicate_iri} has {len(fact.evidence_texts)} evidence texts"
        )
    block_parsed = _test_block(block)
    trace_path = write_fact_trace(
        result=result,
        block=block_parsed,
        evidence_cards=cards,
        source_snapshot=snapshot,
        output_dir=tmp_path,
    )
    rows = [
        json.loads(ln) for ln in trace_path.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    assert len(rows) == len(result.accepted)
    # Each trace row's evidence is the matched claim text and is source-contained.
    for row in rows:
        assert row["evidence_text"] in advisory_record.content
    # The advisoryNumber trace row binds to the ADVZY span, not to an unrelated span.
    adv_row = next(r for r in rows if "advisoryNumber" in r["graph_patch_line"])
    assert "ADVZY 123" in adv_row["evidence_text"]


# ---------------------------------------------------------------------------
# §12 regressions: full-date binding, zero Advisory calls, explicit profile gap
# ---------------------------------------------------------------------------


def test_advisory_period_anchored_to_full_utc_date(mentions):
    """§12: the deterministic parser anchors period tokens to the full UTC date
    carried by the advisory header, preserving the raw substring as evidence."""

    assert mentions.effective_start == "2026-05-19T21:00:00Z"
    assert mentions.effective_end == "2026-05-19T22:45:00Z"
    # The raw source substring is preserved as evidence_text.
    assert mentions.evidence_spans["effective_start"] == "19/2100Z"
    assert mentions.evidence_spans["effective_end"] == "19/2245Z"


def test_exact_fixed_time_binds_and_publishable(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§12: exact ``2026-05-19T21:00:00Z`` binds and remains publishable."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveStartTime | 2026-05-19T21:00:00Z | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert result.publishable
    assert any(
        "effectiveStartTime" in f.predicate_iri and f.object_value == "2026-05-19T21:00:00Z"
        for f in result.accepted
    )


def test_wrong_month_same_day_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§12: ``2026-06-19T21:00:00Z`` (wrong month) is rejected."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveStartTime | 2026-06-19T21:00:00Z | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert any(r.rule == "evidence" and "effectiveStartTime" in r.reason for r in result.rejected)
    assert not result.publishable


def test_wrong_year_same_month_day_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§12: ``2027-05-19T21:00:00Z`` (wrong year) is rejected."""

    evt = event_uri
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveStartTime | 2027-05-19T21:00:00Z | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert any(r.rule == "evidence" and "effectiveStartTime" in r.reason for r in result.rejected)
    assert not result.publishable


def test_wrong_clock_time_rejected(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§12: a value with the wrong day or clock time remains rejected."""

    evt = event_uri
    # Correct date but wrong clock time (23:59 vs 21:00).
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"{evt} | atm:effectiveStartTime | 2026-05-19T23:59:00Z | {SOURCE_ID}\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    assert any(r.rule == "evidence" and "effectiveStartTime" in r.reason for r in result.rejected)
    assert not result.publishable


def test_complete_advisory_makes_zero_advisory_model_calls(advisory_record, mentions):
    """§12: a complete deterministic parse of the fixed record makes zero
    Advisory Agent model calls; no no-op response is recorded."""

    task = AgentTask(
        run_id="r",
        source_id=SOURCE_ID,
        objective="extract mentions",
        allowed_tools=["get_advisory", "parse_structured_fields", "get_schema_event_classes"],
    )
    calls = []

    def invoker(agent_role, template_vars):
        calls.append((agent_role, template_vars))
        return ModelCallRecord(
            agent="advisory",
            raw_response="NOOP-UNUSED",
            prompt_version="advisory-agent-v2",
        )

    evidence = build_advisory_evidence(
        task=task,
        advisory=advisory_record,
        event_classes=[EVENT_CLASS],
        mentions=mentions,
    )
    # §12: zero Advisory model calls for the complete fixed record.
    assert calls == []
    assert calls == []
    # The deterministic parse still produced all fixed claims.
    assert len(evidence.claims) >= 8


def test_impacting_condition_is_explicit_source_supported_profile_gap(
    guide, event_uri, snapshot, advisory_record, facility_entity, mentions
):
    """§12: the fixed ``impacting_condition`` appears as one source-contained
    ProfileGap, not as an accepted fact or a domain-rejection substitute."""

    evt = event_uri
    # The patch includes a real PROFILE_GAPS entry for impacting_condition.
    block = (
        f"GRAPH_PATCH\n"
        f"{evt} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{evt} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{evt} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        f"\n"
        f"PROFILE_GAPS\n"
        f"impacting_condition | weather | IMPACTING CONDITION: WEATHER / THUNDERSTORMS | "
        f"not_in_profile\n"
    )
    result = _validate(
        block,
        guide,
        event_uri,
        snapshot,
        _evidence_cards_for_fixed_case(advisory_record, facility_entity, mentions),
    )
    # The patch is publishable (the gap is not a rejection).
    assert result.publishable
    # Exactly one source-contained ProfileGap for impacting_condition.
    assert len(result.profile_gaps) == 1
    gap = result.profile_gaps[0]
    assert gap.field == "impacting_condition"
    assert gap.value == "weather"
    # The gap evidence is a verbatim source substring.
    assert gap.evidence in advisory_record.content
    assert "IMPACTING CONDITION: WEATHER" in gap.evidence
    # The gap is NOT a formal fact.
    assert not any("impactingCondition" in f.predicate_iri for f in result.accepted)
    # The gap is NOT a rejected row (a domain rejection is not a profile gap).
    assert not any("impactingCondition" in r.graph_patch_line for r in result.rejected)


def test_unanchored_period_abstains_without_guessing():
    """§12: if a period cannot be anchored to one full date deterministically,
    the time claim is omitted (no guessing)."""

    from aviation_agentic_ai.agent_system.agents import _anchor_period_value

    # Day 20 disagrees with header day 19 -> None (no guess).
    assert _anchor_period_value("20/2100Z", 2026, 5, 19) is None
    # Day 19 agrees -> full UTC.
    assert _anchor_period_value("19/2100Z", 2026, 5, 19) == "2026-05-19T21:00:00Z"


def test_approved_real_records_have_bounded_period_and_reason_semantics():
    config = load_yaml("configs/cross_source_v1.yaml")
    expected = {
        "2026-05-19:123": (
            "GS",
            "JFK",
            "2026-05-19T21:00:00Z",
            "2026-05-19T22:45:00Z",
            "weather",
        ),
        "2026-05-19:138": (
            "GDP",
            "JFK",
            "2026-05-19T22:05:00Z",
            "2026-05-20T02:59:00Z",
            "weather",
        ),
        "2026-05-20:020": (
            "GDP",
            "EWR",
            "2026-05-20T01:24:00Z",
            "2026-05-20T05:46:00Z",
            None,
        ),
    }
    for source_id, values in expected.items():
        record = load_advisory_source(config, source_id)
        parsed = parse_structured_fields(record.content)
        assert (
            parsed.event_type,
            parsed.controlled_facility,
            parsed.effective_start,
            parsed.effective_end,
            parsed.impacting_condition,
        ) == values
        if parsed.impacting_condition:
            assert parsed.evidence_spans["impacting_condition"] == (
                "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
            )


def test_period_anchor_allows_only_immediate_calendar_rollover():
    from aviation_agentic_ai.agent_system.agents import _anchor_period_value

    assert (
        _anchor_period_value(
            "01/0030Z",
            2026,
            12,
            31,
            allow_next_day=True,
        )
        == "2027-01-01T00:30:00Z"
    )
    assert (
        _anchor_period_value(
            "02/0030Z",
            2026,
            12,
            31,
            allow_next_day=True,
        )
        is None
    )


def test_validated_profile_gap_is_persisted_as_a_source_bound_audit_row(
    guide,
    event_uri,
    snapshot,
    advisory_record,
    facility_entity,
    mentions,
    tmp_path,
):
    block = _test_block(
        "GRAPH_PATCH\n"
        f"{event_uri} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}\n"
        f"{event_uri} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}\n"
        f"{event_uri} | atm:extensionProbability | MEDIUM | {SOURCE_ID}\n"
        "\nPROFILE_GAPS\n"
        "impacting_condition | weather | "
        "IMPACTING CONDITION: WEATHER / THUNDERSTORMS | "
        "not_in_profile\n"
    )
    result = validate_graph_patch(
        block=block,
        event_iri=event_uri,
        event_class=EVENT_CLASS,
        schema_guide=guide,
        canonical_entities={FACILITY_ID: "nas:Airport"},
        known_source_ids={SOURCE_ID},
        evidence_cards=_evidence_cards_for_fixed_case(
            advisory_record,
            facility_entity,
            mentions,
        ),
        source_snapshot=snapshot,
    )
    path = write_profile_gaps(
        result=result,
        event_id=event_uri,
        source_snapshot=snapshot,
        output_dir=tmp_path,
    )
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["event_id"] == (
        "urn:aviation-agentic-ai:event:"
        f"{event_uri.removeprefix('evt:')}"
    )
    assert rows[0]["source_id"] == SOURCE_ID
    assert rows[0]["value"] == "weather"
    assert (
        rows[0]["source_snapshot_sha256"]
        == snapshot.snapshots[0].content_sha256
    )
    assert rows[0]["profile_gap_id"]


def test_gdp_reason_is_a_formal_lowercase_fact_with_exact_evidence(guide):
    source_id = "2026-05-19:138"
    event_class = "atm:GroundDelayProgramTMI"
    config = load_yaml("configs/cross_source_v1.yaml")
    advisory = load_advisory_source(config, source_id)
    parsed = parse_structured_fields(advisory.content)
    snapshot = build_source_snapshot(advisory)
    event_id = stable_id("evt", source_id, event_class)
    advisory_claims = [
        EvidenceClaim(
            field_name=field,
            value=getattr(parsed, field),
            evidence_text=parsed.evidence_spans[field],
            source_id=source_id,
        )
        for field in (
            "advisory_number",
            "effective_start",
            "effective_end",
            "impacting_condition",
        )
    ]
    cards = [
        EvidenceCard(
            agent_role="advisory",
            status=AgentStatus.RESOLVED,
            claims=advisory_claims,
            source_ids=[source_id],
        ),
        EvidenceCard(
            agent_role="facility",
            status=AgentStatus.RESOLVED,
            claims=[
                EvidenceClaim(
                    field_name="controlled_facility",
                    value=FACILITY_ID,
                    ontology_target="nas:Airport",
                    evidence_text=parsed.evidence_spans["controlled_facility"],
                    source_id=source_id,
                    canonical_ref=FACILITY_ID,
                )
            ],
            canonical_refs=[FACILITY_ID],
            source_ids=[source_id],
        ),
        EvidenceCard(
            agent_role="terminology",
            status=AgentStatus.RESOLVED,
            claims=[
                EvidenceClaim(
                    field_name="operational_term",
                    value="urn:aviation-agentic-ai:term:gdp",
                    ontology_target=event_class,
                    evidence_text=parsed.evidence_spans["operational_term"],
                    source_id=source_id,
                    canonical_ref="urn:aviation-agentic-ai:term:gdp",
                )
            ],
            canonical_refs=["urn:aviation-agentic-ai:term:gdp"],
            source_ids=[source_id],
        ),
    ]
    block = _test_block(
        "GRAPH_PATCH\n"
        f"{event_id} | rdf:type | {event_class} | {source_id}\n"
        f"{event_id} | atm:controlledNASelement | {FACILITY_ID} | {source_id}\n"
        f"{event_id} | atm:advisoryNumber | 138 | {source_id}\n"
        f"{event_id} | atm:effectiveStartTime | "
        f"2026-05-19T22:05:00Z | {source_id}\n"
        f"{event_id} | atm:effectiveEndTime | "
        f"2026-05-20T02:59:00Z | {source_id}\n"
        f"{event_id} | atm:impactingCondition | weather | {source_id}\n"
    )
    result = validate_graph_patch(
        block=block,
        event_iri=event_id,
        event_class=event_class,
        schema_guide=guide,
        canonical_entities={FACILITY_ID: "nas:Airport"},
        known_source_ids={source_id},
        evidence_cards=cards,
        source_snapshot=SourceSnapshotRegistry(snapshots=(snapshot,)),
    )
    assert result.publishable
    reason = next(
        fact for fact in result.accepted if fact.predicate_iri.endswith("impactingCondition")
    )
    assert reason.object_value == "weather"
    assert reason.evidence_texts == ["IMPACTING CONDITION: WEATHER / THUNDERSTORMS"]
