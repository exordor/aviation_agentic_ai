"""Cross-source association generation over accepted source publications.

These tests intentionally exercise the missing P1C.1 generation service.  The
fixtures publish only source-qualified participants; no association row is
inserted by test code.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.flight_airspace_contracts import (
    ARTCCRecord,
    AircraftModelRecord,
    AircraftRecord,
    AirportARTCCAssignmentRecord,
    AirportRecord,
    FlightAirspaceMaterialization,
    FlightPublicationRecord,
    FlightRecord,
    TMIPublicationRecord,
    WeatherObservationRecord,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    KnowledgePublicationPackage,
    KnowledgePublicationRecord,
    KnowledgeRootRecord,
    PublicationEvidenceLink,
    PublicationSourceMembership,
    stable_knowledge_publication_id,
)
from aviation_agentic_ai.agent_system.storage_contracts import SourceVersionRecord
from aviation_agentic_ai.utils.identifiers import stable_id


OPS_DOMAIN = "operations-2026-05-17"
REGISTRY_DOMAIN = "registry-2026-07-28"


def _source(
    store: AviationEvidenceStore,
    *,
    source_id: str,
    family: SourceFamily,
    content: str,
    temporal_domain_id: str,
    logical_time: datetime | None = None,
) -> tuple[SourceVersionRecord, Any]:
    checksum = hashlib.sha256(content.encode()).hexdigest()
    version = SourceVersionRecord(
        source_version_id=stable_id("source-version", source_id, checksum),
        source_id=source_id,
        family=family,
        asset_id=None,
        content=content,
        content_sha256=checksum,
        source_url=None,
        logical_time=logical_time.isoformat() if logical_time is not None else None,
        metadata={"temporal_domain_id": temporal_domain_id},
    )
    store.register_source_version(version)
    anchor = store.register_source_anchor(
        version.source_version_id,
        char_start=0,
        char_end=len(content),
    )
    return version, anchor


def _package(
    *,
    root_id: str,
    root_kind: str,
    temporal_domain_id: str,
    source: SourceVersionRecord,
    anchor: Any,
) -> KnowledgePublicationPackage:
    digest = hashlib.sha256(
        f"{root_id}|{source.source_version_id}".encode()
    ).hexdigest()
    publication_id = stable_knowledge_publication_id(
        root_id,
        source.source_version_id,
        digest,
    )
    return KnowledgePublicationPackage(
        root=KnowledgeRootRecord(
            root_id=root_id,
            root_kind=root_kind,
            temporal_domain_id=temporal_domain_id,
            active_publication_id=publication_id,
        ),
        publication=KnowledgePublicationRecord(
            publication_id=publication_id,
            root_id=root_id,
            temporal_domain_id=temporal_domain_id,
            primary_source_version_id=source.source_version_id,
            formal_publication_digest=digest,
        ),
        publication_sources=(
            PublicationSourceMembership(
                membership_id=stable_id(
                    "publication-source",
                    publication_id,
                    source.source_version_id,
                    "primary",
                ),
                publication_id=publication_id,
                source_version_id=source.source_version_id,
                source_role="primary",
            ),
        ),
        source_anchors=(anchor,),
        facts=(),
        fact_memberships=(),
        evidence_links=(
            PublicationEvidenceLink(
                evidence_link_id=stable_id(
                    "publication-evidence",
                    publication_id,
                    "structured_record",
                    root_id,
                    source.source_version_id,
                    anchor.source_anchor_id,
                    "source_record",
                ),
                publication_id=publication_id,
                owner_kind="structured_record",
                owner_id=root_id,
                source_version_id=source.source_version_id,
                source_anchor_id=anchor.source_anchor_id,
                evidence_text=source.content,
                evidence_ref="source_record",
            ),
        ),
    )


def _publish_flight(
    store: AviationEvidenceStore,
    *,
    label: str,
    destination: str = "KJFK",
    tail_number: str | None = None,
    wheels_off: datetime | None = datetime(2026, 5, 17, 12, tzinfo=UTC),
    arrival: datetime | None = datetime(2026, 5, 17, 13, tzinfo=UTC),
    time_basis: str = "utc",
    temporal_domain_id: str = OPS_DOMAIN,
) -> tuple[str, str]:
    scheduled_key = f"2026-05-17:{label}:KATL:{destination}"
    flight_id = stable_id(
        "flight",
        SourceFamily.BTS_FLIGHT_OPERATION.value,
        "2026-05-17",
        "DL",
        label,
        "KATL",
        destination,
        scheduled_key,
    )
    source, anchor = _source(
        store,
        source_id=f"bts-flight:{label}",
        family=SourceFamily.BTS_FLIGHT_OPERATION,
        content=(
            f"DL,{label},{tail_number or ''},KATL,{destination},"
            f"{wheels_off.isoformat() if wheels_off else ''},"
            f"{arrival.isoformat() if arrival else ''}"
        ),
        temporal_domain_id=temporal_domain_id,
    )
    package = _package(
        root_id=flight_id,
        root_kind="flight",
        temporal_domain_id=temporal_domain_id,
        source=source,
        anchor=anchor,
    )
    publication_id = package.publication.publication_id
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=package,
            flight=FlightRecord(
                flight_id=flight_id,
                temporal_domain_id=temporal_domain_id,
                source_family=SourceFamily.BTS_FLIGHT_OPERATION,
                service_date=date(2026, 5, 17),
                reporting_carrier="DL",
                flight_number=label,
                origin_airport_id="KATL",
                destination_airport_id=destination,
                scheduled_departure_key=scheduled_key,
                tail_number=tail_number,
                scheduled_departure=wheels_off,
                actual_wheels_off=wheels_off,
                actual_arrival=arrival,
                time_basis=time_basis,
                cancelled=False,
                diverted=False,
            ),
            flight_publication=FlightPublicationRecord(
                publication_id=publication_id,
                flight_id=flight_id,
                temporal_domain_id=temporal_domain_id,
                primary_source_version_id=source.source_version_id,
            ),
        )
    )
    return flight_id, publication_id


def _publish_weather(
    store: AviationEvidenceStore,
    *,
    label: str,
    station_id: str,
    observed_at: datetime,
    temporal_domain_id: str = OPS_DOMAIN,
) -> tuple[str, str]:
    content = f"{station_id} {observed_at.isoformat()} METAR {label}"
    source, anchor = _source(
        store,
        source_id=f"metar:{label}",
        family=SourceFamily.HISTORICAL_METAR_SPECI,
        content=content,
        temporal_domain_id=temporal_domain_id,
    )
    observation_id = stable_id(
        "weather-observation",
        SourceFamily.HISTORICAL_METAR_SPECI.value,
        station_id,
        observed_at.isoformat(),
        source.source_version_id,
    )
    package = _package(
        root_id=observation_id,
        root_kind="weather_observation",
        temporal_domain_id=temporal_domain_id,
        source=source,
        anchor=anchor,
    )
    publication_id = package.publication.publication_id
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=package,
            weather_observations=(
                WeatherObservationRecord(
                    observation_id=observation_id,
                    publication_id=publication_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.HISTORICAL_METAR_SPECI,
                    station_id=station_id,
                    observed_at=observed_at,
                    report_type="METAR",
                    raw_report=content,
                    phenomenon_tokens=("RA",),
                    source_version_id=source.source_version_id,
                    time_basis="utc",
                ),
            ),
        )
    )
    return observation_id, publication_id


def _publish_registry_entry(
    store: AviationEvidenceStore,
    *,
    label: str,
    registration_number: str,
    model_code: str,
) -> tuple[str, str, str, str]:
    content = f"{registration_number},{model_code},AIRBUS,A319"
    source, anchor = _source(
        store,
        source_id=f"faa-registry:{label}",
        family=SourceFamily.FAA_AIRCRAFT_REGISTRY,
        content=content,
        temporal_domain_id=REGISTRY_DOMAIN,
        logical_time=datetime(2026, 7, 28, tzinfo=UTC),
    )
    aircraft_id = stable_id(
        "aircraft",
        SourceFamily.FAA_AIRCRAFT_REGISTRY.value,
        registration_number,
    )
    aircraft_package = _package(
        root_id=aircraft_id,
        root_kind="aircraft",
        temporal_domain_id=REGISTRY_DOMAIN,
        source=source,
        anchor=anchor,
    )
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=aircraft_package,
            aircraft=(
                AircraftRecord(
                    aircraft_id=aircraft_id,
                    temporal_domain_id=REGISTRY_DOMAIN,
                    source_family=SourceFamily.FAA_AIRCRAFT_REGISTRY,
                    registration_number=registration_number,
                ),
            ),
        )
    )
    model_id = stable_id(
        "aircraft-model",
        SourceFamily.FAA_AIRCRAFT_REGISTRY.value,
        "AIRBUS",
        model_code,
    )
    model_package = _package(
        root_id=model_id,
        root_kind="aircraft_model",
        temporal_domain_id=REGISTRY_DOMAIN,
        source=source,
        anchor=anchor,
    )
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=model_package,
            aircraft_models=(
                AircraftModelRecord(
                    aircraft_model_id=model_id,
                    temporal_domain_id=REGISTRY_DOMAIN,
                    source_family=SourceFamily.FAA_AIRCRAFT_REGISTRY,
                    manufacturer_code="AIRBUS",
                    model_code=model_code,
                    display_name="A319",
                ),
            ),
        )
    )
    return (
        aircraft_id,
        aircraft_package.publication.publication_id,
        model_id,
        model_package.publication.publication_id,
    )


def _publish_tmi(
    store: AviationEvidenceStore,
    *,
    label: str,
    tmi_type: str,
    airport_id: str | None,
    effective_from: datetime | None,
    effective_to: datetime | None,
    departure_scope_airports: tuple[str, ...] = (),
    departure_scope_artccs: tuple[str, ...] = (),
) -> tuple[str, str]:
    content = (
        f"{tmi_type} {airport_id or 'NO-SCOPE'} "
        f"{effective_from.isoformat() if effective_from else 'NO-START'} "
        f"{effective_to.isoformat() if effective_to else 'NO-END'}"
    )
    source, anchor = _source(
        store,
        source_id=f"tmi:{label}",
        family=SourceFamily.NASA_ATMONTO_INSTANCE,
        content=content,
        temporal_domain_id=OPS_DOMAIN,
    )
    tmi_id = f"urn:tmi:{label}"
    package = _package(
        root_id=tmi_id,
        root_kind="tmi",
        temporal_domain_id=OPS_DOMAIN,
        source=source,
        anchor=anchor,
    )
    publication_id = package.publication.publication_id
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=package,
            tmi_publications=(
                TMIPublicationRecord(
                    tmi_id=tmi_id,
                    publication_id=publication_id,
                    temporal_domain_id=OPS_DOMAIN,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    tmi_type=tmi_type,
                    controlled_element_id=airport_id,
                    airport_id=airport_id,
                    departure_scope_declared=bool(
                        departure_scope_airports or departure_scope_artccs
                    ),
                    departure_scope_airport_ids=departure_scope_airports,
                    departure_scope_artcc_ids=departure_scope_artccs,
                    reason="weather",
                    issued_at=datetime(2026, 5, 17, 11, tzinfo=UTC),
                    effective_from=effective_from,
                    effective_to=effective_to,
                    source_version_id=source.source_version_id,
                ),
            ),
        )
    )
    return tmi_id, publication_id


def _publish_within_assignment(
    store: AviationEvidenceStore,
    *,
    airport_code: str,
    artcc_code: str,
) -> str:
    airport_source, airport_anchor = _source(
        store,
        source_id=f"nasa-airport:{airport_code}",
        family=SourceFamily.NASA_ATMONTO_INSTANCE,
        content=f"{airport_code} within {artcc_code}",
        temporal_domain_id=OPS_DOMAIN,
    )
    airport_id = stable_id(
        "airport",
        SourceFamily.NASA_ATMONTO_INSTANCE.value,
        airport_code,
    )
    airport_package = _package(
        root_id=airport_id,
        root_kind="airport",
        temporal_domain_id=OPS_DOMAIN,
        source=airport_source,
        anchor=airport_anchor,
    )
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=airport_package,
            airports=(
                AirportRecord(
                    airport_id=airport_id,
                    temporal_domain_id=OPS_DOMAIN,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    airport_code=airport_code,
                ),
            ),
        )
    )
    artcc_source, artcc_anchor = _source(
        store,
        source_id=f"nasa-artcc:{artcc_code}",
        family=SourceFamily.NASA_ATMONTO_INSTANCE,
        content=f"ARTCC {artcc_code}",
        temporal_domain_id=OPS_DOMAIN,
    )
    artcc_id = stable_id(
        "artcc",
        SourceFamily.NASA_ATMONTO_INSTANCE.value,
        artcc_code,
    )
    artcc_package = _package(
        root_id=artcc_id,
        root_kind="artcc",
        temporal_domain_id=OPS_DOMAIN,
        source=artcc_source,
        anchor=artcc_anchor,
    )
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=artcc_package,
            artccs=(
                ARTCCRecord(
                    artcc_id=artcc_id,
                    temporal_domain_id=OPS_DOMAIN,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    artcc_code=artcc_code,
                ),
            ),
        )
    )
    assignment_source, assignment_anchor = _source(
        store,
        source_id=f"nasa-airport-artcc:{airport_code}:{artcc_code}",
        family=SourceFamily.NASA_ATMONTO_INSTANCE,
        content=f"{airport_code} withinARTCC {artcc_code}",
        temporal_domain_id=OPS_DOMAIN,
    )
    checksum = "d" * 64
    assignment_id = stable_id(
        "airport-artcc-assignment",
        airport_package.publication.publication_id,
        artcc_package.publication.publication_id,
        "within",
        "",
        "",
        checksum,
    )
    assignment_package = _package(
        root_id=assignment_id,
        root_kind="airport_artcc_assignment",
        temporal_domain_id=OPS_DOMAIN,
        source=assignment_source,
        anchor=assignment_anchor,
    )
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=assignment_package,
            airport_artcc_assignments=(
                AirportARTCCAssignmentRecord(
                    assignment_id=assignment_id,
                    airport_publication_id=(
                        airport_package.publication.publication_id
                    ),
                    artcc_publication_id=artcc_package.publication.publication_id,
                    temporal_domain_id=OPS_DOMAIN,
                    assignment_role="within",
                    procedure_id="nasa-within-artcc-v1",
                    procedure_checksum=checksum,
                    derivation_id=f"derivation:{assignment_id}",
                ),
            ),
        )
    )
    return assignment_package.publication.publication_id


def _materialize(
    store: AviationEvidenceStore,
    *,
    temporal_domain_id: str | None = OPS_DOMAIN,
) -> Any:
    from aviation_agentic_ai.agent_system.cross_source_associations import (
        materialize_cross_source_associations,
    )

    return materialize_cross_source_associations(
        store=store,
        temporal_domain_id=temporal_domain_id,
    )


def _binding(batch: Any, association_id: str) -> Any:
    return next(
        binding
        for binding in batch.bindings
        if binding.association_id == association_id
    )


def _assert_exact_participant_evidence(
    batch: Any,
    *,
    association_id: str,
    publication_ids: set[str],
) -> None:
    binding = _binding(batch, association_id)
    assert set(binding.participating_publication_ids) == publication_ids
    assert {
        link.publication_id for link in binding.participant_evidence
    } == publication_ids
    assert all(link.source_version_id for link in binding.participant_evidence)
    assert all(link.source_anchor_id for link in binding.participant_evidence)
    assert set(binding.derivation.input_publication_ids) == publication_ids
    assert set(binding.derivation.input_source_version_ids) == {
        link.source_version_id for link in binding.participant_evidence
    }
    assert binding.derivation.derivation_id == binding.derivation_id


def test_weather_generation_keeps_all_strictly_under_thirty_minute_qualifiers(
    tmp_path: Path,
) -> None:
    """A <=30-minute or airport-only join would fail this boundary fixture."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="weather-association-test",
        create=True,
    )
    try:
        flight_id, flight_publication = _publish_flight(store, label="100")
        accepted_publications = {
            _publish_weather(
                store,
                label="before-29",
                station_id="KATL",
                observed_at=datetime(2026, 5, 17, 11, 31, tzinfo=UTC),
            )[1],
            _publish_weather(
                store,
                label="after-29",
                station_id="KATL",
                observed_at=datetime(2026, 5, 17, 12, 29, tzinfo=UTC),
            )[1],
        }
        _publish_weather(
            store,
            label="before-30",
            station_id="KATL",
            observed_at=datetime(2026, 5, 17, 11, 30, tzinfo=UTC),
        )
        _publish_weather(
            store,
            label="after-30",
            station_id="KATL",
            observed_at=datetime(2026, 5, 17, 12, 30, tzinfo=UTC),
        )
        _publish_weather(
            store,
            label="wrong-station",
            station_id="KCLT",
            observed_at=datetime(2026, 5, 17, 12, 5, tzinfo=UTC),
        )
        _publish_weather(
            store,
            label="wrong-domain",
            station_id="KATL",
            observed_at=datetime(2026, 5, 17, 12, 5, tzinfo=UTC),
            temporal_domain_id="other-operations-domain",
        )

        batch = _materialize(store)
        rows = store._connection.execute(
            """
            SELECT * FROM flight_weather_associations
            WHERE flight_publication_id = ?
            ORDER BY observation_time
            """,
            (flight_publication,),
        ).fetchall()

        assert len(rows) == 2
        assert {row["weather_publication_id"] for row in rows} == (
            accepted_publications
        )
        assert {row["delta_seconds"] for row in rows} == {1740}
        assert {row["flight_time_field"] for row in rows} == {
            "actual_wheels_off"
        }
        assert all(row["causal_claim"] == 0 for row in rows)
        for row in rows:
            _assert_exact_participant_evidence(
                batch,
                association_id=row["association_id"],
                publication_ids={
                    flight_publication,
                    row["weather_publication_id"],
                },
            )
        assert flight_id
    finally:
        store.close()


def test_weather_generation_requires_utc_flight_time(tmp_path: Path) -> None:
    """A local or unknown Flight clock must never enter the UTC proximity join."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="weather-time-basis-test",
        create=True,
    )
    try:
        _publish_flight(
            store,
            label="local",
            wheels_off=datetime(2026, 5, 17, 12),
            time_basis="origin_local",
        )
        _publish_weather(
            store,
            label="utc",
            station_id="KATL",
            observed_at=datetime(2026, 5, 17, 12, 5, tzinfo=UTC),
        )

        _materialize(store)

        assert store._connection.execute(
            "SELECT COUNT(*) FROM flight_weather_associations"
        ).fetchone()[0] == 0
    finally:
        store.close()


def test_weather_generation_uses_arrival_time_at_destination(
    tmp_path: Path,
) -> None:
    """Destination weather is paired with arrival, not departure time."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="arrival-weather-association-test",
        create=True,
    )
    try:
        _flight_id, flight_publication = _publish_flight(
            store,
            label="arrival",
            destination="KJFK",
            wheels_off=datetime(2026, 5, 17, 12, tzinfo=UTC),
            arrival=datetime(2026, 5, 17, 13, tzinfo=UTC),
        )
        _weather_id, weather_publication = _publish_weather(
            store,
            label="arrival",
            station_id="KJFK",
            observed_at=datetime(2026, 5, 17, 12, 31, tzinfo=UTC),
        )

        _materialize(store)

        row = store._connection.execute(
            """
            SELECT * FROM flight_weather_associations
            WHERE flight_publication_id = ?
              AND weather_publication_id = ?
            """,
            (flight_publication, weather_publication),
        ).fetchone()
        assert row is not None
        assert row["flight_time_field"] == "actual_arrival"
        assert row["delta_seconds"] == 1740
        assert row["causal_claim"] == 0
    finally:
        store.close()


def test_registry_snapshot_generation_normalizes_tail_and_preserves_ambiguity(
    tmp_path: Path,
) -> None:
    """Exact and ambiguous normalized registrations must not be conflated."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="snapshot-association-test",
        create=True,
    )
    try:
        _exact_flight_id, exact_flight_publication = _publish_flight(
            store,
            label="exact",
            tail_number=" n-123aa ",
        )
        _ambiguous_flight_id, ambiguous_flight_publication = _publish_flight(
            store,
            label="ambiguous",
            tail_number="N999ZZ",
        )
        _, exact_aircraft_publication, _, exact_model_publication = (
            _publish_registry_entry(
                store,
                label="exact",
                registration_number="N123AA",
                model_code="A319-1",
            )
        )
        _publish_registry_entry(
            store,
            label="ambiguous-a",
            registration_number="N999ZZ",
            model_code="A319-2",
        )
        _publish_registry_entry(
            store,
            label="ambiguous-b",
            registration_number="N-999ZZ",
            model_code="A319-3",
        )

        batch = _materialize(store)
        exact_rows = store._connection.execute(
            """
            SELECT * FROM flight_aircraft_snapshot_matches
            WHERE flight_publication_id = ?
            """,
            (exact_flight_publication,),
        ).fetchall()
        ambiguous_rows = store._connection.execute(
            """
            SELECT * FROM flight_aircraft_snapshot_matches
            WHERE flight_publication_id = ? ORDER BY aircraft_publication_id
            """,
            (ambiguous_flight_publication,),
        ).fetchall()

        assert len(exact_rows) == 1
        assert exact_rows[0]["match_status"] == "exact"
        assert exact_rows[0]["matched_registration_number"] == "N123AA"
        assert exact_rows[0]["historical_model_claim"] == 0
        assert exact_rows[0]["temporal_domain_id"] == OPS_DOMAIN
        _assert_exact_participant_evidence(
            batch,
            association_id=exact_rows[0]["snapshot_match_id"],
            publication_ids={
                exact_flight_publication,
                exact_aircraft_publication,
                exact_model_publication,
            },
        )

        assert len(ambiguous_rows) == 2
        assert {row["match_status"] for row in ambiguous_rows} == {"ambiguous"}
        assert all(row["historical_model_claim"] == 0 for row in ambiguous_rows)
        assert all(row["temporal_domain_id"] == OPS_DOMAIN for row in ambiguous_rows)
        for row in ambiguous_rows:
            _assert_exact_participant_evidence(
                batch,
                association_id=row["snapshot_match_id"],
                publication_ids={
                    ambiguous_flight_publication,
                    row["aircraft_publication_id"],
                    row["model_publication_id"],
                },
            )
    finally:
        store.close()


def test_gdp_and_ground_stop_generation_is_candidate_scoped(
    tmp_path: Path,
) -> None:
    """Pre-filter by destination/scope before evaluating bounded candidates."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="tmi-applicability-test",
        create=True,
    )
    try:
        _flight_id, flight_publication = _publish_flight(store, label="tmi")
        tmis = dict(
            (
                label,
                _publish_tmi(
                    store,
                    label=label,
                    tmi_type=tmi_type,
                    airport_id=airport,
                    effective_from=start,
                    effective_to=end,
                    departure_scope_airports=scope_airports,
                ),
            )
            for label, tmi_type, airport, start, end, scope_airports in (
                (
                    "gdp-match",
                    "GroundDelayProgramTMI",
                    "KJFK",
                    datetime(2026, 5, 17, 11, 30, tzinfo=UTC),
                    datetime(2026, 5, 17, 12, 30, tzinfo=UTC),
                    ("KATL",),
                ),
                (
                    "gs-match",
                    "GroundStopTMI",
                    "KJFK",
                    datetime(2026, 5, 17, 11, 50, tzinfo=UTC),
                    datetime(2026, 5, 17, 12, 10, tzinfo=UTC),
                    ("KATL",),
                ),
                (
                    "wrong-destination",
                    "GroundDelayProgramTMI",
                    "KLGA",
                    datetime(2026, 5, 17, 11, 30, tzinfo=UTC),
                    datetime(2026, 5, 17, 12, 30, tzinfo=UTC),
                    ("KATL",),
                ),
                (
                    "missing-time",
                    "GroundDelayProgramTMI",
                    "KJFK",
                    None,
                    None,
                    ("KATL",),
                ),
                (
                    "missing-scope",
                    "GroundDelayProgramTMI",
                    "KJFK",
                    datetime(2026, 5, 17, 11, 30, tzinfo=UTC),
                    datetime(2026, 5, 17, 12, 30, tzinfo=UTC),
                    (),
                ),
                (
                    "reroute-no-scope",
                    "ReRouteTMI",
                    None,
                    datetime(2026, 5, 17, 11, 30, tzinfo=UTC),
                    datetime(2026, 5, 17, 12, 30, tzinfo=UTC),
                    (),
                ),
            )
        )

        batch = _materialize(store)
        rows = store._connection.execute(
            """
            SELECT candidate.*, publication.root_id AS tmi_id
            FROM flight_tmi_applicability AS candidate
            JOIN knowledge_publications AS publication
              ON publication.publication_id = candidate.tmi_publication_id
            WHERE candidate.flight_publication_id = ?
            ORDER BY publication.root_id
            """,
            (flight_publication,),
        ).fetchall()
        by_tmi = {row["tmi_id"]: row for row in rows}

        for label in ("gdp-match", "gs-match"):
            tmi_id, tmi_publication = tmis[label]
            row = by_tmi[tmi_id]
            assert row["status"] == "applicability_candidate"
            assert row["actual_control_claim"] == 0
            normalized_inputs = json.loads(row["normalized_inputs_json"])
            assert normalized_inputs["flight_reference_time"].endswith(
                "12:00:00+00:00"
            )
            assert normalized_inputs["flight_time_field"] == "actual_wheels_off"
            assert normalized_inputs["time_match"] is True
            _assert_exact_participant_evidence(
                batch,
                association_id=row["applicability_id"],
                publication_ids={flight_publication, tmi_publication},
            )

        missing = by_tmi[tmis["missing-time"][0]]
        missing_scope = by_tmi[tmis["missing-scope"][0]]
        assert missing["status"] == "unknown"
        assert missing_scope["status"] == "unknown"
        assert missing["actual_control_claim"] == 0
        assert missing_scope["actual_control_claim"] == 0
        assert tmis["wrong-destination"][0] not in by_tmi
        assert tmis["reroute-no-scope"][0] not in by_tmi
        for row in (missing, missing_scope):
            _assert_exact_participant_evidence(
                batch,
                association_id=row["applicability_id"],
                publication_ids={flight_publication, row["tmi_publication_id"]},
            )
    finally:
        store.close()


def test_tmi_artcc_scope_requires_same_domain_reference_evidence(
    tmp_path: Path,
) -> None:
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="tmi-artcc-scope-test",
        create=True,
    )
    try:
        _flight_id, flight_publication = _publish_flight(
            store,
            label="artcc-scope",
        )
        assignment_publication = _publish_within_assignment(
            store,
            airport_code="KATL",
            artcc_code="ZTL",
        )
        _tmi_id, tmi_publication = _publish_tmi(
            store,
            label="artcc-scope",
            tmi_type="GroundDelayProgramTMI",
            airport_id="KJFK",
            effective_from=datetime(2026, 5, 17, 11, 30, tzinfo=UTC),
            effective_to=datetime(2026, 5, 17, 12, 30, tzinfo=UTC),
            departure_scope_artccs=("ZTL",),
        )

        batch = _materialize(store)
        row = store._connection.execute(
            "SELECT * FROM flight_tmi_applicability"
        ).fetchone()

        assert row["status"] == "applicability_candidate"
        inputs = json.loads(row["normalized_inputs_json"])
        assert inputs["departure_scope_status"] == "exact_origin_artcc_match"
        assert inputs["origin_artccs"] == ["ZTL"]
        _assert_exact_participant_evidence(
            batch,
            association_id=row["applicability_id"],
            publication_ids={
                flight_publication,
                tmi_publication,
                assignment_publication,
            },
        )
    finally:
        store.close()


def test_cross_source_materialization_is_idempotent_and_keeps_stable_bindings(
    tmp_path: Path,
) -> None:
    """A repeat rebuild must not duplicate rows, evidence, or derivations."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="association-idempotency-test",
        create=True,
    )
    try:
        _publish_flight(store, label="repeat", tail_number="N123AA")
        _publish_weather(
            store,
            label="repeat",
            station_id="KATL",
            observed_at=datetime(2026, 5, 17, 12, 10, tzinfo=UTC),
        )
        _publish_registry_entry(
            store,
            label="repeat",
            registration_number="N123AA",
            model_code="A319-1",
        )
        _publish_tmi(
            store,
            label="repeat",
            tmi_type="GroundDelayProgramTMI",
            airport_id="KJFK",
            effective_from=datetime(2026, 5, 17, 11, 30, tzinfo=UTC),
            effective_to=datetime(2026, 5, 17, 12, 30, tzinfo=UTC),
        )

        first = _materialize(store)
        first_counts = tuple(
            store._connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "flight_weather_associations",
                "flight_aircraft_snapshot_matches",
                "flight_tmi_applicability",
                "deterministic_derivations",
            )
        )
        first_revision = store.get_knowledge_revision()
        second = _materialize(store)
        second_counts = tuple(
            store._connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "flight_weather_associations",
                "flight_aircraft_snapshot_matches",
                "flight_tmi_applicability",
                "deterministic_derivations",
            )
        )

        assert first_counts == (1, 1, 1, 3)
        assert second_counts == first_counts
        assert store.get_knowledge_revision() == first_revision
        assert {
            (binding.association_id, binding.derivation_id)
            for binding in second.bindings
        } == {
            (binding.association_id, binding.derivation_id)
            for binding in first.bindings
        }
    finally:
        store.close()


def test_tmi_current_view_replaces_unknown_after_artcc_evidence_arrives(
    tmp_path: Path,
) -> None:
    """A rebuild exposes one current applicability result, not stale history."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="association-current-view-test",
        create=True,
    )
    try:
        _publish_flight(store, label="late-artcc", destination="KJFK")
        _publish_tmi(
            store,
            label="late-artcc",
            tmi_type="GroundDelayProgramTMI",
            airport_id="KJFK",
            effective_from=datetime(2026, 5, 17, 11, 30, tzinfo=UTC),
            effective_to=datetime(2026, 5, 17, 12, 30, tzinfo=UTC),
            departure_scope_artccs=("ZTL",),
        )

        first = _materialize(store)
        assert [row.status for row in first.tmi_applicability] == ["unknown"]
        stale_id = first.tmi_applicability[0].applicability_id

        _publish_within_assignment(
            store,
            airport_code="KATL",
            artcc_code="ZTL",
        )
        second = _materialize(store)

        assert [row.status for row in second.tmi_applicability] == [
            "applicability_candidate"
        ]
        rows = store._connection.execute(
            "SELECT applicability_id, status FROM flight_tmi_applicability"
        ).fetchall()
        assert [(row["applicability_id"], row["status"]) for row in rows] == [
            (second.tmi_applicability[0].applicability_id, "applicability_candidate")
        ]
        assert store._connection.execute(
            "SELECT active_publication_id FROM knowledge_roots WHERE root_id = ?",
            (stale_id,),
        ).fetchone()[0] is None
    finally:
        store.close()
