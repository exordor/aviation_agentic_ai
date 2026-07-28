"""Formal DecisionCase core ownership independent of optional source layers."""

from __future__ import annotations

from aviation_agentic_ai.agent_system.contracts import (
    DecisionCaseMemberBinding,
    DecisionCaseReconstructionSeed,
    SourceBinding,
    SourceFamily,
)
from aviation_agentic_ai.agent_system.decision_case_graph import (
    CASE_DECISION_CASE_IRI,
    CASE_RECONSTRUCTION_IRI,
    FORBIDDEN_CAUSAL_PREDICATES,
    PROV_HAD_MEMBER_IRI,
    RDF_TYPE_IRI,
    build_decision_case_graph,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)


def _seed(
    source_families: tuple[tuple[str, SourceFamily], ...] = (
        ("advisory:1", SourceFamily.ATCSCC_ADVISORY),
    ),
) -> DecisionCaseReconstructionSeed:
    return DecisionCaseReconstructionSeed(
        conceptual_case_iri="urn:aviation-agentic-ai:decision-case:event-1",
        reconstruction_iri=(
            "urn:aviation-agentic-ai:decision-case-reconstruction:" + "a" * 64
        ),
        reconstruction_trace_id="reconstruction-trace:" + "a" * 64,
        reconstruction_input_sha256="a" * 64,
        profile_refs=load_validation_profile_registry(
            decision_guide=load_schema_guide()
        ).refs,
        source_bindings=tuple(
            SourceBinding(
                source_id=source_id,
                source_family=source_family,
                snapshot_sha256="b" * 64,
            )
            for source_id, source_family in source_families
        ),
        builder_id="urn:aviation-agentic-ai:builder:decision-case-core-v1",
        builder_checksum="c" * 64,
    )


def test_publishable_event_has_case_core_without_bts() -> None:
    """Removing BTS must not remove the formal case and event membership."""

    registry = load_validation_profile_registry(decision_guide=load_schema_guide())
    event_iri = "urn:aviation-agentic-ai:event:1"

    bundle = build_decision_case_graph(
        seed=_seed(),
        members=(
            DecisionCaseMemberBinding(
                member_iri=event_iri,
                member_kind="event",
                source_ids=("advisory:1",),
            ),
        ),
        profile_registry=registry,
    )

    assert bundle.status == "ok", bundle.failure_reason
    assert {
        fact.object_value
        for fact in bundle.formal_facts
        if fact.predicate_iri == RDF_TYPE_IRI
    } >= {
        CASE_DECISION_CASE_IRI,
        CASE_RECONSTRUCTION_IRI,
    }
    assert any(
        fact.predicate_iri == PROV_HAD_MEMBER_IRI
        and fact.object_value == event_iri
        for fact in bundle.formal_facts
    )
    assert {
        fact.validation_profile.layer for fact in bundle.formal_facts
    } == {"decision_case_core"}


def test_optional_members_are_exactly_the_accepted_members() -> None:
    """A failed optional layer must be omittable without changing the core."""

    registry = load_validation_profile_registry(decision_guide=load_schema_guide())
    members = (
        DecisionCaseMemberBinding(
            member_iri="urn:aviation-agentic-ai:event:1",
            member_kind="event",
            source_ids=("advisory:1",),
        ),
        DecisionCaseMemberBinding(
            member_iri="urn:aviation-agentic-ai:weather-report:metar-1",
            member_kind="weather_report",
            source_ids=("metar:1",),
        ),
        DecisionCaseMemberBinding(
            member_iri="urn:aviation-agentic-ai:observation:active-1",
            member_kind="public_observation",
            source_ids=("bts:1",),
        ),
    )

    bundle = build_decision_case_graph(
        seed=_seed(
            (
                ("advisory:1", SourceFamily.ATCSCC_ADVISORY),
                ("metar:1", SourceFamily.METAR),
                ("bts:1", SourceFamily.BTS_ON_TIME),
            )
        ),
        members=members,
        profile_registry=registry,
    )

    assert bundle.status == "ok", bundle.failure_reason
    assert {
        fact.object_value
        for fact in bundle.formal_facts
        if fact.predicate_iri == PROV_HAD_MEMBER_IRI
    } == {member.member_iri for member in members}
    assert bundle.reconstruction_trace is not None
    assert bundle.reconstruction_trace.member_iris == tuple(
        sorted(member.member_iri for member in members)
    )


def test_case_core_never_emits_causal_predicates() -> None:
    """Case co-membership must never be promoted to a causal relationship."""

    registry = load_validation_profile_registry(decision_guide=load_schema_guide())
    bundle = build_decision_case_graph(
        seed=_seed(
            (
                ("advisory:1", SourceFamily.ATCSCC_ADVISORY),
                ("metar:1", SourceFamily.METAR),
            )
        ),
        members=(
            DecisionCaseMemberBinding(
                member_iri="urn:aviation-agentic-ai:event:1",
                member_kind="event",
                source_ids=("advisory:1",),
            ),
            DecisionCaseMemberBinding(
                member_iri="urn:aviation-agentic-ai:weather-report:metar-1",
                member_kind="weather_report",
                source_ids=("metar:1",),
            ),
        ),
        profile_registry=registry,
    )

    assert bundle.status == "ok", bundle.failure_reason
    assert not {
        fact.predicate_iri for fact in bundle.formal_facts
    } & FORBIDDEN_CAUSAL_PREDICATES
