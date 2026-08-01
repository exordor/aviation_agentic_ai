"""Deterministic, evidence-bounded associations over active publications.

The association tables are rebuildable read models.  They never merge source
identities and never promote temporal proximity, a later registry snapshot, or
TMI applicability into causal, historical, or actual-control claims.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.flight_airspace_contracts import (
    CrossSourceAssociationBinding,
    CrossSourceAssociationMaterialization,
    CrossSourceParticipantEvidence,
    FlightAircraftSnapshotMatchRecord,
    FlightTMIApplicabilityRecord,
    FlightWeatherAssociationRecord,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    DeterministicDerivationRecord,
    KnowledgePublicationPackage,
    KnowledgePublicationRecord,
    KnowledgeRootRecord,
    PublicationEvidenceLink,
    PublicationSourceMembership,
    stable_knowledge_publication_id,
)
from aviation_agentic_ai.agent_system.storage_contracts import SourceAnchorRecord
from aviation_agentic_ai.utils.identifiers import stable_id


WEATHER_PROCEDURE_ID = "flight-weather-proximity-v1"
SNAPSHOT_PROCEDURE_ID = "tail-registry-snapshot-match-v1"
TMI_RULE_ID = "tmi-applicability-v1"

_WEATHER_POLICY = {
    "causal_claim": False,
    "comparison": "strict_less_than",
    "endpoint_time_rules": {
        "destination": ["actual_arrival"],
        "origin": ["actual_wheels_off", "actual_departure"],
    },
    "max_delta_seconds": 1800,
    "station_match": "flight_endpoint_airport_exact",
    "temporal_domain": "same",
    "utc_time_basis": ["utc", "source_naive_interpreted_utc"],
    "version": WEATHER_PROCEDURE_ID,
}
_SNAPSHOT_POLICY = {
    "historical_model_claim": False,
    "match": "normalized_registration_exact",
    "registry_temporal_role": "later_technical_snapshot",
    "version": SNAPSHOT_PROCEDURE_ID,
}
_TMI_POLICY = {
    "actual_control_claim": False,
    "gdp_gs": "destination_then_scope_then_actual_departure_in_effective_interval",
    "reroute": "requires_explicit_route_or_origin_destination_scope",
    "temporal_domain": "same",
    "version": TMI_RULE_ID,
}


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _checksum(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


WEATHER_PROCEDURE_CHECKSUM = _checksum(_WEATHER_POLICY)
SNAPSHOT_PROCEDURE_CHECKSUM = _checksum(_SNAPSHOT_POLICY)
TMI_RULE_CHECKSUM = _checksum(_TMI_POLICY)


@dataclass(frozen=True, slots=True)
class _Participant:
    role: str
    publication_id: str
    root_id: str


@dataclass(frozen=True, slots=True)
class _EvidenceSeed:
    participant_role: str
    publication_id: str
    source_version_id: str
    source_anchor_id: str
    char_start: int
    char_end: int
    anchor_kind: str
    evidence_text: str
    evidence_ref: str


@dataclass(frozen=True, slots=True)
class _AirportARTCCEvidence:
    artcc_code: str
    assignment_id: str
    assignment_publication_id: str


def _parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _normalized_registration(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"[^A-Z0-9]", "", value.upper())
    return normalized or None


def _active_flights(
    store: AviationEvidenceStore,
    temporal_domain_id: str | None,
) -> tuple[Any, ...]:
    return tuple(
        store._connection.execute(
            """
            SELECT detail.*, root.temporal_domain_id, flight.source_family
            FROM knowledge_roots AS root
            JOIN flight_publications AS detail
              ON detail.publication_id = root.active_publication_id
            JOIN flights AS flight ON flight.flight_id = detail.flight_id
            WHERE root.root_kind = 'flight'
              AND (? IS NULL OR root.temporal_domain_id = ?)
            ORDER BY detail.publication_id
            """,
            (temporal_domain_id, temporal_domain_id),
        ).fetchall()
    )


def _active_airport_artcc_evidence(
    store: AviationEvidenceStore,
    temporal_domain_id: str | None,
) -> dict[tuple[str, str], tuple[_AirportARTCCEvidence, ...]]:
    rows = store._connection.execute(
        """
        SELECT assignment.temporal_domain_id, airport.identifier AS airport_code,
               artcc.identifier AS artcc_code, assignment.assignment_id,
               assignment_root.active_publication_id
                 AS assignment_publication_id
        FROM airport_artcc_assignments AS assignment
        JOIN knowledge_roots AS assignment_root
          ON assignment_root.root_id = assignment.assignment_id
         AND assignment_root.root_kind = 'airport_artcc_assignment'
        JOIN knowledge_roots AS airport_root
          ON airport_root.active_publication_id = assignment.airport_publication_id
         AND airport_root.root_kind = 'airport'
        JOIN airports AS airport ON airport.airport_id = airport_root.root_id
        JOIN knowledge_roots AS artcc_root
          ON artcc_root.active_publication_id = assignment.artcc_publication_id
         AND artcc_root.root_kind = 'artcc'
        JOIN artccs AS artcc ON artcc.artcc_id = artcc_root.root_id
        WHERE assignment.assignment_role = 'within'
          AND airport_root.temporal_domain_id = assignment.temporal_domain_id
          AND artcc_root.temporal_domain_id = assignment.temporal_domain_id
          AND (? IS NULL OR assignment.temporal_domain_id = ?)
        ORDER BY assignment.temporal_domain_id, airport.identifier,
                 artcc.identifier, assignment.assignment_id
        """,
        (temporal_domain_id, temporal_domain_id),
    ).fetchall()
    by_airport: dict[
        tuple[str, str], list[_AirportARTCCEvidence]
    ] = defaultdict(list)
    for row in rows:
        by_airport[(row["temporal_domain_id"], row["airport_code"])].append(
            _AirportARTCCEvidence(
                artcc_code=row["artcc_code"],
                assignment_id=row["assignment_id"],
                assignment_publication_id=row["assignment_publication_id"],
            )
        )
    return {key: tuple(value) for key, value in by_airport.items()}


def _root_evidence(
    store: AviationEvidenceStore,
    participant: _Participant,
    *,
    association_kind: str,
) -> tuple[_EvidenceSeed, ...]:
    rows = store._connection.execute(
        """
        SELECT link.source_version_id, link.source_anchor_id,
               link.evidence_text, link.evidence_ref,
               anchor.char_start, anchor.char_end, anchor.anchor_kind
        FROM publication_evidence_links AS link
        JOIN source_anchors AS anchor
          ON anchor.source_anchor_id = link.source_anchor_id
        WHERE link.publication_id = ?
          AND link.owner_kind = 'structured_record'
          AND link.owner_id = ?
          AND link.source_anchor_id IS NOT NULL
        ORDER BY link.source_version_id, link.source_anchor_id,
                 link.evidence_link_id
        """,
        (participant.publication_id, participant.root_id),
    ).fetchall()
    links: list[_EvidenceSeed] = []
    for row in rows:
        links.append(
            _EvidenceSeed(
                participant_role=participant.role,
                publication_id=participant.publication_id,
                source_version_id=row["source_version_id"],
                source_anchor_id=row["source_anchor_id"],
                char_start=row["char_start"],
                char_end=row["char_end"],
                anchor_kind=row["anchor_kind"],
                evidence_text=row["evidence_text"],
                evidence_ref=(
                    f"{association_kind}:{participant.role}:{row['evidence_ref']}"
                ),
            )
        )
    return tuple(links)


def _ordered_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _binding(
    store: AviationEvidenceStore,
    *,
    association_kind: str,
    association_id: str,
    temporal_domain_id: str,
    procedure_id: str,
    procedure_checksum: str,
    normalized_parameters: dict[str, Any],
    participants: tuple[_Participant, ...],
    input_entity_ids: tuple[str, ...],
    result_payload: dict[str, Any],
) -> CrossSourceAssociationBinding | None:
    evidence: list[_EvidenceSeed] = []
    for participant in participants:
        participant_links = _root_evidence(
            store,
            participant,
            association_kind=association_kind,
        )
        if not participant_links:
            return None
        evidence.extend(participant_links)
    publication_ids = _ordered_unique(
        participant.publication_id for participant in participants
    )
    source_version_ids = _ordered_unique(
        link.source_version_id for link in evidence
    )
    entity_ids = _ordered_unique(input_entity_ids)
    result_checksum = _checksum(result_payload)
    publication_digest = _checksum(
        {
            "association_id": association_id,
            "association_kind": association_kind,
            "input_publication_ids": publication_ids,
            "procedure_checksum": procedure_checksum,
            "result_checksum": result_checksum,
        }
    )
    association_publication_id = stable_knowledge_publication_id(
        association_id,
        source_version_ids[0],
        publication_digest,
    )
    derivation_id = stable_id(
        "derivation",
        association_publication_id,
        temporal_domain_id,
        procedure_id,
        procedure_checksum,
        _canonical(normalized_parameters),
        _canonical(list(publication_ids)),
        _canonical(list(source_version_ids)),
        _canonical(list(entity_ids)),
        result_checksum,
    )
    derivation = DeterministicDerivationRecord(
        derivation_id=derivation_id,
        publication_id=association_publication_id,
        temporal_domain_id=temporal_domain_id,
        procedure_id=procedure_id,
        procedure_checksum=procedure_checksum,
        normalized_parameters=normalized_parameters,
        input_publication_ids=publication_ids,
        input_source_version_ids=source_version_ids,
        input_entity_ids=entity_ids,
        result_checksum=result_checksum,
        result_summary=f"1 {association_kind} association",
    )
    anchors_by_id = {
        item.source_anchor_id: SourceAnchorRecord(
            source_anchor_id=item.source_anchor_id,
            source_version_id=item.source_version_id,
            char_start=item.char_start,
            char_end=item.char_end,
            anchor_kind=item.anchor_kind,
        )
        for item in evidence
    }
    association_evidence = tuple(
        PublicationEvidenceLink(
            evidence_link_id=stable_id(
                "publication-evidence",
                association_publication_id,
                "association",
                association_id,
                item.source_version_id,
                item.source_anchor_id,
                item.evidence_ref,
            ),
            publication_id=association_publication_id,
            owner_kind="association",
            owner_id=association_id,
            source_version_id=item.source_version_id,
            source_anchor_id=item.source_anchor_id,
            evidence_text=item.evidence_text,
            evidence_ref=item.evidence_ref,
        )
        for item in evidence
    )
    association_publication = KnowledgePublicationPackage(
        root=KnowledgeRootRecord(
            root_id=association_id,
            root_kind=association_kind,
            temporal_domain_id=temporal_domain_id,
            active_publication_id=association_publication_id,
        ),
        publication=KnowledgePublicationRecord(
            publication_id=association_publication_id,
            root_id=association_id,
            temporal_domain_id=temporal_domain_id,
            primary_source_version_id=source_version_ids[0],
            formal_publication_digest=publication_digest,
        ),
        publication_sources=tuple(
            PublicationSourceMembership(
                membership_id=stable_id(
                    "publication-source",
                    association_publication_id,
                    source_version_id,
                    "primary" if index == 0 else "supporting",
                ),
                publication_id=association_publication_id,
                source_version_id=source_version_id,
                source_role="primary" if index == 0 else "supporting",
            )
            for index, source_version_id in enumerate(source_version_ids)
        ),
        source_anchors=tuple(
            anchors_by_id[key] for key in sorted(anchors_by_id)
        ),
        facts=(),
        fact_memberships=(),
        evidence_links=association_evidence,
        derivations=(derivation,),
    )
    return CrossSourceAssociationBinding(
        association_kind=association_kind,
        association_id=association_id,
        participating_publication_ids=publication_ids,
        participant_evidence=tuple(
            CrossSourceParticipantEvidence(
                participant_role=item.participant_role,
                publication_id=item.publication_id,
                source_version_id=item.source_version_id,
                source_anchor_id=item.source_anchor_id,
                evidence_ref=item.evidence_ref,
            )
            for item in evidence
        ),
        derivation_id=derivation_id,
        derivation=derivation,
        association_publication=association_publication,
    )


def _weather_associations(
    store: AviationEvidenceStore,
    flights: tuple[Any, ...],
    temporal_domain_id: str | None,
) -> tuple[
    tuple[FlightWeatherAssociationRecord, ...],
    tuple[CrossSourceAssociationBinding, ...],
]:
    observations = store._connection.execute(
        """
        SELECT observation.*, root.root_id
        FROM knowledge_roots AS root
        JOIN weather_observations AS observation
          ON observation.publication_id = root.active_publication_id
        WHERE root.root_kind = 'weather_observation'
          AND (? IS NULL OR root.temporal_domain_id = ?)
        ORDER BY observation.publication_id
        """,
        (temporal_domain_id, temporal_domain_id),
    ).fetchall()
    by_station: dict[tuple[str, str], list[Any]] = defaultdict(list)
    for observation in observations:
        by_station[
            (observation["temporal_domain_id"], observation["station_id"])
        ].append(observation)

    records: list[FlightWeatherAssociationRecord] = []
    bindings: list[CrossSourceAssociationBinding] = []
    for flight in flights:
        if flight["time_basis"] not in {"utc", "source_naive_interpreted_utc"}:
            continue
        endpoint_times: list[tuple[str, str, datetime]] = []
        departure_time = _parse_time(flight["actual_wheels_off_time"])
        departure_field = "actual_wheels_off"
        if departure_time is None:
            departure_time = _parse_time(flight["actual_departure_time"])
            departure_field = "actual_departure"
        if departure_time is not None:
            endpoint_times.append(
                (flight["origin_airport_id"], departure_field, departure_time)
            )
        arrival_time = _parse_time(flight["actual_arrival_time"])
        if arrival_time is not None:
            endpoint_times.append(
                (
                    flight["destination_airport_id"],
                    "actual_arrival",
                    arrival_time,
                )
            )

        for station_id, flight_time_field, flight_time in endpoint_times:
            for observation in by_station.get(
                (flight["temporal_domain_id"], station_id),
                (),
            ):
                observation_time = _parse_time(observation["observed_at"])
                if observation_time is None:
                    continue
                delta_seconds = int(
                    abs((flight_time - observation_time).total_seconds())
                )
                if delta_seconds >= int(_WEATHER_POLICY["max_delta_seconds"]):
                    continue
                association_id = stable_id(
                    "flight-weather-association",
                    flight["publication_id"],
                    observation["publication_id"],
                    flight_time_field,
                    WEATHER_PROCEDURE_CHECKSUM,
                )
                result = {
                    "association_id": association_id,
                    "delta_seconds": delta_seconds,
                    "flight_time": flight_time.isoformat(),
                    "flight_time_field": flight_time_field,
                    "observation_time": observation_time.isoformat(),
                    "station_id": station_id,
                }
                binding = _binding(
                    store,
                    association_kind="flight_weather",
                    association_id=association_id,
                    temporal_domain_id=flight["temporal_domain_id"],
                    procedure_id=WEATHER_PROCEDURE_ID,
                    procedure_checksum=WEATHER_PROCEDURE_CHECKSUM,
                    normalized_parameters=dict(_WEATHER_POLICY),
                    participants=(
                        _Participant(
                            "flight",
                            flight["publication_id"],
                            flight["flight_id"],
                        ),
                        _Participant(
                            "weather",
                            observation["publication_id"],
                            observation["weather_observation_id"],
                        ),
                    ),
                    input_entity_ids=(
                        flight["flight_id"],
                        observation["weather_observation_id"],
                        observation["station_id"],
                    ),
                    result_payload=result,
                )
                if binding is None:
                    continue
                records.append(
                    FlightWeatherAssociationRecord(
                        association_id=association_id,
                        flight_publication_id=flight["publication_id"],
                        weather_publication_id=observation["publication_id"],
                        temporal_domain_id=flight["temporal_domain_id"],
                        flight_time_field=flight_time_field,
                        flight_time=flight_time,
                        observation_time=observation_time,
                        delta_seconds=delta_seconds,
                        procedure_id=WEATHER_PROCEDURE_ID,
                        procedure_checksum=WEATHER_PROCEDURE_CHECKSUM,
                        derivation_id=binding.derivation_id,
                        causal_claim=False,
                    )
                )
                bindings.append(binding)
    return tuple(records), tuple(bindings)


def _snapshot_associations(
    store: AviationEvidenceStore,
    flights: tuple[Any, ...],
) -> tuple[
    tuple[FlightAircraftSnapshotMatchRecord, ...],
    tuple[CrossSourceAssociationBinding, ...],
]:
    aircraft_rows = store._connection.execute(
        """
        SELECT aircraft.aircraft_id, aircraft.registration_mark,
               root.active_publication_id AS aircraft_publication_id,
               publication.primary_source_version_id, source.logical_time
        FROM aircraft
        JOIN knowledge_roots AS root ON root.root_id = aircraft.aircraft_id
        JOIN knowledge_publications AS publication
          ON publication.publication_id = root.active_publication_id
        JOIN source_versions AS source
          ON source.source_version_id = publication.primary_source_version_id
        WHERE root.root_kind = 'aircraft'
          AND aircraft.source_family = ?
        ORDER BY root.active_publication_id
        """,
        (SourceFamily.FAA_AIRCRAFT_REGISTRY.value,),
    ).fetchall()
    model_rows = store._connection.execute(
        """
        SELECT model.aircraft_model_id,
               root.active_publication_id AS model_publication_id,
               publication.primary_source_version_id
        FROM aircraft_models AS model
        JOIN knowledge_roots AS root ON root.root_id = model.aircraft_model_id
        JOIN knowledge_publications AS publication
          ON publication.publication_id = root.active_publication_id
        WHERE root.root_kind = 'aircraft_model'
          AND model.source_family = ?
        ORDER BY root.active_publication_id
        """,
        (SourceFamily.FAA_AIRCRAFT_REGISTRY.value,),
    ).fetchall()
    models_by_source: dict[str, list[Any]] = defaultdict(list)
    for model in model_rows:
        models_by_source[model["primary_source_version_id"]].append(model)
    aircraft_by_registration: dict[str, list[Any]] = defaultdict(list)
    for aircraft in aircraft_rows:
        normalized = _normalized_registration(aircraft["registration_mark"])
        if normalized is not None and _parse_time(aircraft["logical_time"]) is not None:
            aircraft_by_registration[normalized].append(aircraft)

    records: list[FlightAircraftSnapshotMatchRecord] = []
    bindings: list[CrossSourceAssociationBinding] = []
    for flight in flights:
        registration = _normalized_registration(flight["tail_number"])
        if registration is None:
            continue
        candidates = aircraft_by_registration.get(registration, ())
        if not candidates:
            continue
        combinations = [
            (aircraft, model)
            for aircraft in candidates
            for model in (
                models_by_source.get(aircraft["primary_source_version_id"], ())
                or (None,)
            )
        ]
        match_status = "exact" if len(combinations) == 1 else "ambiguous"
        for aircraft, model in combinations:
            snapshot_at = _parse_time(aircraft["logical_time"])
            if snapshot_at is None:
                continue
            model_publication_id = (
                model["model_publication_id"] if model is not None else None
            )
            match_id = stable_id(
                "flight-aircraft-snapshot-match",
                flight["publication_id"],
                aircraft["aircraft_publication_id"],
                model_publication_id or "",
                SNAPSHOT_PROCEDURE_CHECKSUM,
            )
            participants = [
                _Participant("flight", flight["publication_id"], flight["flight_id"]),
                _Participant(
                    "aircraft",
                    aircraft["aircraft_publication_id"],
                    aircraft["aircraft_id"],
                ),
            ]
            entity_ids = [flight["flight_id"], aircraft["aircraft_id"]]
            if model is not None:
                participants.append(
                    _Participant(
                        "aircraft_model",
                        model["model_publication_id"],
                        model["aircraft_model_id"],
                    )
                )
                entity_ids.append(model["aircraft_model_id"])
            result = {
                "match_id": match_id,
                "match_status": match_status,
                "normalized_registration": registration,
                "registry_snapshot_at": snapshot_at.isoformat(),
            }
            binding = _binding(
                store,
                association_kind="aircraft_snapshot",
                association_id=match_id,
                temporal_domain_id=flight["temporal_domain_id"],
                procedure_id=SNAPSHOT_PROCEDURE_ID,
                procedure_checksum=SNAPSHOT_PROCEDURE_CHECKSUM,
                normalized_parameters=dict(_SNAPSHOT_POLICY),
                participants=tuple(participants),
                input_entity_ids=tuple(entity_ids),
                result_payload=result,
            )
            if binding is None:
                continue
            records.append(
                FlightAircraftSnapshotMatchRecord(
                    match_id=match_id,
                    flight_publication_id=flight["publication_id"],
                    aircraft_publication_id=aircraft["aircraft_publication_id"],
                    aircraft_model_publication_id=model_publication_id,
                    temporal_domain_id=flight["temporal_domain_id"],
                    registry_snapshot_at=snapshot_at,
                    matched_registration_number=registration,
                    match_status=match_status,
                    procedure_id=SNAPSHOT_PROCEDURE_ID,
                    procedure_checksum=SNAPSHOT_PROCEDURE_CHECKSUM,
                    derivation_id=binding.derivation_id,
                    historical_model_claim=False,
                )
            )
            bindings.append(binding)
    return tuple(records), tuple(bindings)


def _tmi_associations(
    store: AviationEvidenceStore,
    flights: tuple[Any, ...],
    temporal_domain_id: str | None,
) -> tuple[
    tuple[FlightTMIApplicabilityRecord, ...],
    tuple[CrossSourceAssociationBinding, ...],
]:
    tmis = store._connection.execute(
        """
        SELECT tmi.*, root.root_id
        FROM source_tmi_publications AS tmi
        JOIN knowledge_roots AS root
          ON root.active_publication_id = tmi.publication_id
        WHERE root.root_kind = 'tmi'
          AND tmi.tmi_type IN ('GroundDelayProgramTMI', 'GroundStopTMI')
          AND tmi.airport_id IS NOT NULL
          AND (? IS NULL OR tmi.temporal_domain_id = ?)
        ORDER BY tmi.publication_id
        """,
        (temporal_domain_id, temporal_domain_id),
    ).fetchall()
    by_destination: dict[tuple[str, str], list[Any]] = defaultdict(list)
    for tmi in tmis:
        by_destination[(tmi["temporal_domain_id"], tmi["airport_id"])].append(tmi)
    airport_artcc_evidence = _active_airport_artcc_evidence(
        store,
        temporal_domain_id,
    )

    records: list[FlightTMIApplicabilityRecord] = []
    bindings: list[CrossSourceAssociationBinding] = []
    for flight in flights:
        for tmi in by_destination.get(
            (flight["temporal_domain_id"], flight["destination_airport_id"]),
            (),
        ):
            scope_airports = tuple(json.loads(tmi["departure_scope_airport_ids_json"]))
            scope_artccs = tuple(json.loads(tmi["departure_scope_artcc_ids_json"]))
            scope_declared = bool(tmi["departure_scope_declared"])
            origin_artcc_evidence = airport_artcc_evidence.get(
                (
                    flight["temporal_domain_id"],
                    flight["origin_airport_id"],
                ),
                (),
            )
            origin_artccs = tuple(
                item.artcc_code for item in origin_artcc_evidence
            )
            matching_artcc_evidence = tuple(
                item
                for item in origin_artcc_evidence
                if item.artcc_code in scope_artccs
            )
            if not scope_declared:
                scope_status = "not_declared"
            elif flight["origin_airport_id"] in scope_airports:
                scope_status = "exact_origin_airport_match"
            elif matching_artcc_evidence:
                scope_status = "exact_origin_artcc_match"
            elif scope_artccs and not origin_artcc_evidence:
                scope_status = "unknown_origin_artcc"
            elif scope_airports or scope_artccs:
                scope_status = "origin_airport_not_in_scope"
            else:
                scope_status = "declared_without_members"

            utc_qualified = flight["time_basis"] in {
                "utc",
                "source_naive_interpreted_utc",
            }
            flight_reference_time = None
            flight_time_field = "actual_wheels_off"
            if utc_qualified:
                flight_reference_time = _parse_time(
                    flight["actual_wheels_off_time"]
                )
                if flight_reference_time is None:
                    flight_time_field = "actual_departure"
                    flight_reference_time = _parse_time(
                        flight["actual_departure_time"]
                    )
            effective_from = _parse_time(tmi["effective_from"])
            effective_to = _parse_time(tmi["effective_to"])
            time_match = (
                flight_reference_time is not None
                and effective_from is not None
                and effective_to is not None
                and effective_from
                <= flight_reference_time
                < effective_to
            )
            if (
                flight_reference_time is None
                or effective_from is None
                or effective_to is None
            ):
                status = "unknown"
                limitation = (
                    "A UTC-qualified Flight departure time or complete TMI "
                    "interval is unavailable."
                )
            elif scope_status == "not_declared":
                status = "unknown"
                limitation = "The accepted TMI record has no explicit departure scope."
            elif scope_status in {"unknown_origin_artcc", "declared_without_members"}:
                status = "unknown"
                limitation = "Declared departure scope cannot be resolved from accepted references."
            elif scope_status == "origin_airport_not_in_scope":
                status = "not_applicable"
                limitation = "Flight origin is outside the explicit departure-airport scope."
            elif time_match:
                status = "applicability_candidate"
                limitation = (
                    "Candidate from destination, departure scope, and departure "
                    "time only; no EDCT or actual-control record is available."
                )
            else:
                status = "not_applicable"
                limitation = "Flight time does not overlap the TMI effective interval."

            normalized_inputs = {
                "departure_scope_declared": scope_declared,
                "departure_scope_status": scope_status,
                "destination": flight["destination_airport_id"],
                "destination_match": True,
                "effective_from": (
                    effective_from.isoformat() if effective_from is not None else None
                ),
                "effective_to": (
                    effective_to.isoformat() if effective_to is not None else None
                ),
                "flight_reference_time": (
                    flight_reference_time.isoformat()
                    if flight_reference_time is not None
                    else None
                ),
                "flight_time_field": flight_time_field,
                "origin": flight["origin_airport_id"],
                "origin_artccs": list(origin_artccs),
                "time_match": time_match,
            }
            applicability_id = stable_id(
                "flight-tmi-applicability",
                flight["publication_id"],
                tmi["publication_id"],
                TMI_RULE_CHECKSUM,
                _canonical(normalized_inputs),
            )
            result = {
                "applicability_id": applicability_id,
                "status": status,
                "limitation": limitation,
            }
            reference_participants = tuple(
                _Participant(
                    "airport_artcc_assignment",
                    item.assignment_publication_id,
                    item.assignment_id,
                )
                for item in (
                    matching_artcc_evidence
                    if matching_artcc_evidence
                    else origin_artcc_evidence
                )
            ) if scope_artccs else ()
            binding = _binding(
                store,
                association_kind="tmi_applicability",
                association_id=applicability_id,
                temporal_domain_id=flight["temporal_domain_id"],
                procedure_id=TMI_RULE_ID,
                procedure_checksum=TMI_RULE_CHECKSUM,
                normalized_parameters=dict(_TMI_POLICY),
                participants=(
                    _Participant("flight", flight["publication_id"], flight["flight_id"]),
                    _Participant("tmi", tmi["publication_id"], tmi["tmi_id"]),
                    *reference_participants,
                ),
                input_entity_ids=(
                    flight["flight_id"],
                    tmi["tmi_id"],
                    *(item.assignment_id for item in origin_artcc_evidence),
                ),
                result_payload=result,
            )
            if binding is None:
                continue
            records.append(
                FlightTMIApplicabilityRecord(
                    applicability_id=applicability_id,
                    flight_publication_id=flight["publication_id"],
                    tmi_publication_id=tmi["publication_id"],
                    temporal_domain_id=flight["temporal_domain_id"],
                    tmi_family=tmi["tmi_type"],
                    status=status,
                    rule_id=TMI_RULE_ID,
                    rule_checksum=TMI_RULE_CHECKSUM,
                    normalized_inputs=normalized_inputs,
                    limitation=limitation,
                    derivation_id=binding.derivation_id,
                    actual_control_claim=False,
                )
            )
            bindings.append(binding)
    return tuple(records), tuple(bindings)


def materialize_cross_source_associations(
    *,
    store: AviationEvidenceStore,
    temporal_domain_id: str | None = None,
) -> CrossSourceAssociationMaterialization:
    """Build and idempotently store all evidence-supported active joins."""

    flights = _active_flights(store, temporal_domain_id)
    weather, weather_bindings = _weather_associations(
        store,
        flights,
        temporal_domain_id,
    )
    snapshots, snapshot_bindings = _snapshot_associations(store, flights)
    applicability, applicability_bindings = _tmi_associations(
        store,
        flights,
        temporal_domain_id,
    )
    materialization = CrossSourceAssociationMaterialization(
        rebuilt_temporal_domain_ids=(
            (temporal_domain_id,)
            if temporal_domain_id is not None
            else tuple(
                sorted({row["temporal_domain_id"] for row in flights})
            )
        ),
        flight_weather_associations=weather,
        aircraft_snapshot_matches=snapshots,
        tmi_applicability=applicability,
        bindings=tuple(
            sorted(
                (*weather_bindings, *snapshot_bindings, *applicability_bindings),
                key=lambda binding: binding.association_id,
            )
        ),
    )
    store.apply_cross_source_association_materialization(materialization)
    return materialization


__all__ = [
    "SNAPSHOT_PROCEDURE_CHECKSUM",
    "SNAPSHOT_PROCEDURE_ID",
    "TMI_RULE_CHECKSUM",
    "TMI_RULE_ID",
    "WEATHER_PROCEDURE_CHECKSUM",
    "WEATHER_PROCEDURE_ID",
    "materialize_cross_source_associations",
]
