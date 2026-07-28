"""Deterministic source-independent DecisionCase reconstruction core."""

from __future__ import annotations

import hashlib
import json

from aviation_agentic_ai.agent_system.contracts import (
    BTSOutcomeBundle,
    DecisionCaseGraphBundle,
    DecisionCaseMemberBinding,
    DecisionCaseReconstructionSeed,
    DecisionContextEvent,
    ReconstructionTrace,
    SourceBinding,
    SourceSnapshotRegistry,
    ValidatedFact,
    WeatherContextBundle,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    LoadedValidationProfile,
    ValidationProfileRegistry,
    validate_fact_for_publication,
)
from aviation_agentic_ai.cross_source.contracts import CanonicalEntity

RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
PROV_ENTITY_IRI = "http://www.w3.org/ns/prov#Entity"
PROV_COLLECTION_IRI = "http://www.w3.org/ns/prov#Collection"
PROV_SPECIALIZATION_OF_IRI = "http://www.w3.org/ns/prov#specializationOf"
PROV_HAD_MEMBER_IRI = "http://www.w3.org/ns/prov#hadMember"
CASE_DECISION_CASE_IRI = (
    "urn:aviation-agentic-ai:decision-case-schema:DecisionCase"
)
CASE_RECONSTRUCTION_IRI = (
    "urn:aviation-agentic-ai:decision-case-schema:DecisionCaseReconstruction"
)

FORBIDDEN_CAUSAL_PREDICATES = frozenset(
    {
        "urn:aviation-agentic-ai:causedBy",
        "urn:aviation-agentic-ai:motivatedBy",
        "urn:aviation-agentic-ai:affectedBy",
    }
)

BUILDER_ID = "urn:aviation-agentic-ai:builder:decision-case-core-v1"
BUILDER_CHECKSUM = hashlib.sha256(
    b"decision-case-core-v1:event-weather-public-observation-membership"
).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _stable_iri(namespace: str, payload: object) -> str:
    return namespace + _digest(payload)


def _core_profile(registry: ValidationProfileRegistry) -> LoadedValidationProfile:
    profiles = [
        profile
        for profile in registry.profiles
        if profile.ref.layer == "decision_case_core"
    ]
    if len(profiles) != 1:
        raise ValueError("exactly one DecisionCase core profile is required")
    return profiles[0]


def _source_bindings(
    source_ids: set[str],
    registry: SourceSnapshotRegistry,
) -> tuple[SourceBinding, ...]:
    bindings: list[SourceBinding] = []
    for source_id in sorted(source_ids):
        snapshot = registry.get(source_id)
        if snapshot is None:
            raise ValueError(
                f"DecisionCase source is absent from snapshot registry: {source_id}"
            )
        bindings.append(
            SourceBinding(
                source_id=source_id,
                source_family=snapshot.family,
                snapshot_sha256=snapshot.content_sha256,
            )
        )
    return tuple(bindings)


def prepare_decision_case_reconstruction(
    event: DecisionContextEvent,
    canonical_facility: CanonicalEntity,
    weather_bundle: WeatherContextBundle,
    outcome_bundle: BTSOutcomeBundle,
    snapshot_registry: SourceSnapshotRegistry,
    profile_registry: ValidationProfileRegistry,
) -> DecisionCaseReconstructionSeed:
    """Prepare one deterministic identity before optional facts are projected."""

    _core_profile(profile_registry)
    weather_ids = (
        tuple(sorted(weather_bundle.selected_report_ids))
        if weather_bundle.status == "ok"
        else ()
    )
    summary_ids = (
        tuple(sorted(summary.summary_id for summary in outcome_bundle.summaries))
        if outcome_bundle.status == "ok"
        else ()
    )
    source_ids = {event.advisory_source_id}
    if weather_bundle.status == "ok":
        source_ids.update(
            association.source_id for association in weather_bundle.associations
        )
    if outcome_bundle.status == "ok":
        source_ids.update(summary.source_id for summary in outcome_bundle.summaries)
    bindings = _source_bindings(source_ids, snapshot_registry)
    profile_refs = tuple(
        sorted(
            profile_registry.refs,
            key=lambda ref: (ref.layer, ref.profile_id, ref.profile_checksum),
        )
    )
    reconstruction_input = {
        "builder_id": BUILDER_ID,
        "event_id": event.event_id,
        "facility_id": canonical_facility.entity_id,
        "profile_refs": [ref.model_dump(mode="json") for ref in profile_refs],
        "selected_weather_report_ids": list(weather_ids),
        "selected_bts_summary_ids": list(summary_ids),
        "source_bindings": [
            binding.model_dump(mode="json") for binding in bindings
        ],
    }
    reconstruction_input_sha256 = _digest(reconstruction_input)
    public_profiles = [
        profile
        for profile in profile_registry.profiles
        if profile.ref.layer == "public_operational_observation"
    ]
    procedure = (
        public_profiles[0].aggregation_procedure
        if outcome_bundle.status == "ok" and len(public_profiles) == 1
        else None
    )
    if outcome_bundle.status == "ok" and procedure is None:
        raise ValueError("BTS observations require one aggregation procedure")
    return DecisionCaseReconstructionSeed(
        conceptual_case_iri=_stable_iri(
            "urn:aviation-agentic-ai:decision-case:",
            event.event_id,
        ),
        reconstruction_iri=(
            "urn:aviation-agentic-ai:decision-case-reconstruction:"
            + reconstruction_input_sha256
        ),
        reconstruction_trace_id=(
            "reconstruction-trace:" + reconstruction_input_sha256
        ),
        reconstruction_input_sha256=reconstruction_input_sha256,
        profile_refs=profile_refs,
        source_bindings=bindings,
        builder_id=BUILDER_ID,
        builder_checksum=BUILDER_CHECKSUM,
        aggregation_procedure_id=(
            procedure.procedure_id if procedure is not None else None
        ),
        aggregation_procedure_checksum=(
            procedure.checksum if procedure is not None else None
        ),
    )


def _fact(
    *,
    subject_iri: str,
    subject_class_iri: str,
    predicate_iri: str,
    object_value: str,
    object_class_iri: str,
    profile: LoadedValidationProfile,
    evidence_ref: str,
    source_ids: tuple[str, ...] = (),
) -> ValidatedFact:
    semantic_payload = {
        "object_class_iri": object_class_iri,
        "object_value": object_value,
        "predicate_iri": predicate_iri,
        "profile": profile.ref.model_dump(mode="json"),
        "subject_class_iri": subject_class_iri,
        "subject_iri": subject_iri,
    }
    fact = ValidatedFact(
        fact_id="decision-case-core-fact:" + _digest(semantic_payload),
        subject_iri=subject_iri,
        subject_class_iri=subject_class_iri,
        predicate_iri=predicate_iri,
        object_kind="iri",
        object_value=object_value,
        object_class_iri=object_class_iri,
        source_ids=list(sorted(set(source_ids))),
        evidence_texts=[],
        validation_profile=profile.ref,
        evidence_mode="system_membership",
        evidence_ref=evidence_ref,
    )
    validate_fact_for_publication(
        fact,
        ValidationProfileRegistry(profiles=(profile,)),
    )
    return fact


def _typed_fact(
    resource_iri: str,
    class_iri: str,
    *,
    profile: LoadedValidationProfile,
    evidence_ref: str,
    source_ids: tuple[str, ...] = (),
) -> ValidatedFact:
    return _fact(
        subject_iri=resource_iri,
        subject_class_iri=class_iri,
        predicate_iri=RDF_TYPE_IRI,
        object_value=class_iri,
        object_class_iri=class_iri,
        profile=profile,
        evidence_ref=evidence_ref,
        source_ids=source_ids,
    )


def build_decision_case_graph(
    seed: DecisionCaseReconstructionSeed,
    members: tuple[DecisionCaseMemberBinding, ...],
    profile_registry: ValidationProfileRegistry,
) -> DecisionCaseGraphBundle:
    """Finalize one formal case core from explicitly accepted members."""

    try:
        profile = _core_profile(profile_registry)
        profile_registry.resolve(profile.ref)
        if profile.ref not in seed.profile_refs:
            raise ValueError("DecisionCase core profile is absent from reconstruction seed")
        bindings = {binding.source_id: binding for binding in seed.source_bindings}
        if len(bindings) != len(seed.source_bindings):
            raise ValueError("duplicate DecisionCase source binding")
        grouped: dict[str, DecisionCaseMemberBinding] = {}
        for member in members:
            missing_sources = set(member.source_ids) - set(bindings)
            if missing_sources:
                raise ValueError(
                    "DecisionCase member source is absent from reconstruction seed"
                )
            previous = grouped.get(member.member_iri)
            if previous is None:
                grouped[member.member_iri] = member.model_copy(
                    update={"source_ids": tuple(sorted(set(member.source_ids)))}
                )
            elif previous.member_kind != member.member_kind:
                raise ValueError("DecisionCase member has conflicting kinds")
            else:
                grouped[member.member_iri] = previous.model_copy(
                    update={
                        "source_ids": tuple(
                            sorted(
                                set(previous.source_ids) | set(member.source_ids)
                            )
                        )
                    }
                )
        event_members = [
            member for member in grouped.values() if member.member_kind == "event"
        ]
        if len(event_members) != 1:
            raise ValueError("DecisionCase requires exactly one event member")

        evidence_ref = seed.reconstruction_trace_id
        facts = [
            _typed_fact(
                seed.conceptual_case_iri,
                CASE_DECISION_CASE_IRI,
                profile=profile,
                evidence_ref=evidence_ref,
            ),
            _typed_fact(
                seed.conceptual_case_iri,
                PROV_ENTITY_IRI,
                profile=profile,
                evidence_ref=evidence_ref,
            ),
            _typed_fact(
                seed.reconstruction_iri,
                CASE_RECONSTRUCTION_IRI,
                profile=profile,
                evidence_ref=evidence_ref,
            ),
            _typed_fact(
                seed.reconstruction_iri,
                PROV_COLLECTION_IRI,
                profile=profile,
                evidence_ref=evidence_ref,
            ),
            _fact(
                subject_iri=seed.reconstruction_iri,
                subject_class_iri=CASE_RECONSTRUCTION_IRI,
                predicate_iri=PROV_SPECIALIZATION_OF_IRI,
                object_value=seed.conceptual_case_iri,
                object_class_iri=CASE_DECISION_CASE_IRI,
                profile=profile,
                evidence_ref=evidence_ref,
            ),
        ]
        for member in sorted(grouped.values(), key=lambda item: item.member_iri):
            facts.extend(
                [
                    _typed_fact(
                        member.member_iri,
                        PROV_ENTITY_IRI,
                        profile=profile,
                        evidence_ref=evidence_ref,
                        source_ids=member.source_ids,
                    ),
                    _fact(
                        subject_iri=seed.reconstruction_iri,
                        subject_class_iri=CASE_RECONSTRUCTION_IRI,
                        predicate_iri=PROV_HAD_MEMBER_IRI,
                        object_value=member.member_iri,
                        object_class_iri=PROV_ENTITY_IRI,
                        profile=profile,
                        evidence_ref=evidence_ref,
                        source_ids=member.source_ids,
                    ),
                ]
            )
        by_id = {fact.fact_id: fact for fact in facts}
        if len(by_id) != len(facts):
            raise ValueError("duplicate DecisionCase core fact")
        if set(fact.predicate_iri for fact in facts) & FORBIDDEN_CAUSAL_PREDICATES:
            raise ValueError("DecisionCase core contains a causal predicate")
        member_iris = tuple(sorted(grouped))
        trace = ReconstructionTrace(
            **seed.model_dump(),
            member_iris=member_iris,
        )
        return DecisionCaseGraphBundle(
            status="ok",
            case_iri=seed.conceptual_case_iri,
            reconstruction_iri=seed.reconstruction_iri,
            formal_facts=sorted(facts, key=lambda fact: fact.fact_id),
            reconstruction_trace=trace,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return DecisionCaseGraphBundle(status="blocked", failure_reason=str(exc))


__all__ = [
    "BUILDER_CHECKSUM",
    "BUILDER_ID",
    "CASE_DECISION_CASE_IRI",
    "CASE_RECONSTRUCTION_IRI",
    "FORBIDDEN_CAUSAL_PREDICATES",
    "PROV_HAD_MEMBER_IRI",
    "PROV_SPECIALIZATION_OF_IRI",
    "RDF_TYPE_IRI",
    "build_decision_case_graph",
    "prepare_decision_case_reconstruction",
]
