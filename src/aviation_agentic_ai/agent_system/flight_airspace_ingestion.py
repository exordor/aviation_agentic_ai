"""Deterministic Flight/Airspace source ingestion into the evidence store.

The service is deliberately source-adapter driven: it registers immutable
record versions, creates exact full-record anchors, and publishes typed
structured rows through the general knowledge-publication spine. Reviewed
NASA Flight/Airspace relations are additionally admitted by checksum-pinned
ATMONTO application profiles and the shared Formal Publication Kernel.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, TypeVar

from aviation_agentic_ai.agent_system.airspace_sources import (
    NASAActualRouteSourceRecord,
    NASAFlightSourceRecord,
    NASANavigationFixSourceRecord,
    NASARDFSourceTrace,
    NASASectorSourceRecord,
    NASATrackPointSourceRecord,
    NASRAirportARTCCAssignmentSourceRecord,
    NASRAirportSourceRecord,
    NASRARTCCSourceRecord,
    NASRSourceTrace,
    iter_nasa_atmonto_airspace_records,
    iter_nasr_airspace_records,
)
from aviation_agentic_ai.agent_system.atmonto_sample_sources import (
    ATMONTOAirportDataSourceRecord,
    ATMONTHistoricalWeatherSourceRecord,
    ATMONTHOSourceTrace,
    ATMONTOTAFSourceRecord,
    ATMONTOTMISourceRecord,
    iter_atmonto_public_sample_records,
)
from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.flight_airspace_contracts import (
    AirCarrierRecord,
    AirportOperationalObservationRecord,
    AircraftModelRecord,
    AircraftRecord,
    ARTCCRecord,
    AirportARTCCAssignmentRecord,
    AirportRecord,
    FlightAirspaceMaterialization,
    FlightPublicationRecord,
    FlightRecord,
    NavigationFixRecord,
    RouteRecord,
    SectorRecord,
    SectorPassageRecord,
    TrackPointRecord,
    TMIPublicationRecord,
    WeatherForecastRecord,
    WeatherObservationRecord,
)
from aviation_agentic_ai.agent_system.flight_sources import (
    BTSFlightSourceRecord,
    FAAAircraftTechnicalSourceRecord,
    FLIGHT_SOURCE_ADAPTER_VERSION,
    IEMWeatherSourceRecord,
    iter_bts_flight_sources,
    iter_faa_registry_technical_sources,
    iter_iem_weather_sources,
)
from aviation_agentic_ai.agent_system.flight_airspace_publication import (
    compile_nasa_flight_airspace_facts,
    run_nasa_flight_airspace_publication_kernel,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    KnowledgePublicationPackage,
    KnowledgePublicationRecord,
    KnowledgeRootRecord,
    PublicationEvidenceLink,
    PublicationFactMembership,
    PublicationSourceMembership,
    stable_knowledge_publication_id,
)
from aviation_agentic_ai.agent_system.materialize import FormalPublication
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.source_path_resolver import resolve_source_path
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot_registry,
    build_source_version,
    discover_source_assets,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    KnowledgeIngestionResult,
    SemanticFactRecord,
    SourceAnchorRecord,
    SourceAssetRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    ValidationProfileRegistry,
    load_validation_profile_registry,
)
from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.utils.identifiers import stable_id


_SOURCE_KEYS = (
    "bts_flight_operations",
    "faa_aircraft_registry",
    "historical_metar_speci",
    "nasa_atmonto_instances",
    "nasr_airspace_zip",
)


@dataclass(frozen=True, slots=True)
class FlightAirspaceRootResult:
    """One source-root outcome returned by the ingestion service."""

    source_version_id: str
    source_family: SourceFamily
    root_kind: str
    root_id: str | None
    publication_id: str | None
    status: str
    disposition: str
    reason: str


@dataclass(frozen=True, slots=True)
class FlightAirspaceIngestionSummary:
    """Compact aggregate plus inspectable per-root outcomes."""

    asset_count: int
    discovered_count: int
    selected_count: int
    attempted_count: int
    ok_count: int
    insufficient_count: int
    blocked_count: int
    skipped_count: int
    results: tuple[FlightAirspaceRootResult, ...]

    @property
    def root_count(self) -> int:
        return self.selected_count


class _SummaryAccumulator:
    def __init__(self, max_result_records: int) -> None:
        self.max_result_records = max_result_records
        self.discovered_count = 0
        self.selected_count = 0
        self.attempted_count = 0
        self.ok_count = 0
        self.insufficient_count = 0
        self.blocked_count = 0
        self.skipped_count = 0
        self.results: list[FlightAirspaceRootResult] = []

    def add(self, result: FlightAirspaceRootResult) -> None:
        self.discovered_count += 1
        self.selected_count += 1
        if result.disposition == "skipped":
            self.skipped_count += 1
        else:
            self.attempted_count += 1
        if result.status == "ok":
            self.ok_count += 1
        elif result.status == "insufficient":
            self.insufficient_count += 1
        else:
            self.blocked_count += 1
        if len(self.results) < self.max_result_records:
            self.results.append(result)

    def extend(self, results: Iterable[FlightAirspaceRootResult]) -> None:
        for result in results:
            self.add(result)

    def build(self, *, asset_count: int) -> FlightAirspaceIngestionSummary:
        return FlightAirspaceIngestionSummary(
            asset_count=asset_count,
            discovered_count=self.discovered_count,
            selected_count=self.selected_count,
            attempted_count=self.attempted_count,
            ok_count=self.ok_count,
            insufficient_count=self.insufficient_count,
            blocked_count=self.blocked_count,
            skipped_count=self.skipped_count,
            results=tuple(self.results),
        )


@dataclass(frozen=True, slots=True)
class _PendingPublication:
    source_version: SourceVersionRecord
    adapter_id: str
    root_kind: str
    materialization: FlightAirspaceMaterialization
    supporting_source_versions: tuple[SourceVersionRecord, ...] = ()

    @property
    def source_versions(self) -> tuple[SourceVersionRecord, ...]:
        return (self.source_version, *self.supporting_source_versions)


@dataclass(frozen=True, slots=True)
class _PendingInsufficient:
    source_version: SourceVersionRecord
    adapter_id: str
    root_kind: str
    reason: str


_AdaptedRecord = TypeVar("_AdaptedRecord")


def _canonical_digest(value: object) -> str:
    content = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _record_with_domain(record: SourceRecord, temporal_domain_id: str) -> SourceRecord:
    metadata = dict(record.metadata)
    metadata["temporal_domain_id"] = temporal_domain_id
    return record.model_copy(update={"metadata": metadata})


def _full_record_anchor(version: SourceVersionRecord) -> SourceAnchorRecord:
    return SourceAnchorRecord(
        source_anchor_id=stable_id(
            "source-anchor",
            version.source_version_id,
            0,
            len(version.content),
        ),
        source_version_id=version.source_version_id,
        char_start=0,
        char_end=len(version.content),
        anchor_kind="full_record",
    )


def _publication_package(
    *,
    root_id: str,
    root_kind: str,
    temporal_domain_id: str,
    source_version: SourceVersionRecord,
    structured_payload: object,
    supporting_source_versions: tuple[SourceVersionRecord, ...] = (),
    formal_publication: FormalPublication | None = None,
    fact_traces: tuple[FactTraceRow, ...] = (),
) -> KnowledgePublicationPackage:
    digest_payload: dict[str, object] = {
        "adapter_version": FLIGHT_SOURCE_ADAPTER_VERSION,
        "root_id": root_id,
        "root_kind": root_kind,
        "structured_payload": structured_payload,
    }
    if supporting_source_versions or formal_publication is not None:
        digest_payload["supporting_source_version_ids"] = sorted(
            version.source_version_id for version in supporting_source_versions
        )
        digest_payload["formal_facts"] = (
            [
                fact.model_dump(mode="json")
                for fact in formal_publication.accepted
            ]
            if formal_publication is not None
            else []
        )
    digest = _canonical_digest(digest_payload)
    publication_id = stable_knowledge_publication_id(
        root_id,
        source_version.source_version_id,
        digest,
    )
    source_versions = (source_version, *supporting_source_versions)
    versions_by_source_id = {version.source_id: version for version in source_versions}
    if len(versions_by_source_id) != len(source_versions):
        raise ValueError("publication source IDs must be unique")
    anchors_by_id = {
        anchor.source_anchor_id: anchor
        for anchor in (_full_record_anchor(version) for version in source_versions)
    }
    anchor = _full_record_anchor(source_version)
    evidence_ref = "full_record"
    facts = tuple(formal_publication.accepted) if formal_publication is not None else ()
    traces_by_fact_id = {trace.fact_id: trace for trace in fact_traces}
    if len(traces_by_fact_id) != len(fact_traces):
        raise ValueError("formal fact traces must be unique")
    if set(traces_by_fact_id) != {fact.fact_id for fact in facts}:
        raise ValueError("formal facts and traces do not match")

    fact_evidence_links: list[PublicationEvidenceLink] = []
    for fact in facts:
        trace = traces_by_fact_id[fact.fact_id]
        version = versions_by_source_id.get(trace.source_id)
        if version is None:
            raise ValueError("formal fact source is outside the publication")
        char_start = version.content.find(trace.evidence_text)
        if char_start < 0:
            raise ValueError("formal fact evidence is absent from source version")
        fact_anchor = SourceAnchorRecord(
            source_anchor_id=stable_id(
                "source-anchor",
                version.source_version_id,
                char_start,
                char_start + len(trace.evidence_text),
            ),
            source_version_id=version.source_version_id,
            char_start=char_start,
            char_end=char_start + len(trace.evidence_text),
            anchor_kind="text_span",
        )
        anchors_by_id.setdefault(fact_anchor.source_anchor_id, fact_anchor)
        fact_evidence_links.append(
            PublicationEvidenceLink(
                evidence_link_id=stable_id(
                    "publication-evidence",
                    publication_id,
                    "fact",
                    fact.fact_id,
                    version.source_version_id,
                    fact_anchor.source_anchor_id,
                    fact.evidence_ref,
                ),
                publication_id=publication_id,
                owner_kind="fact",
                owner_id=fact.fact_id,
                source_version_id=version.source_version_id,
                source_anchor_id=fact_anchor.source_anchor_id,
                evidence_text=trace.evidence_text,
                evidence_ref=fact.evidence_ref,
            )
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
            primary_source_version_id=source_version.source_version_id,
            formal_publication_digest=digest,
        ),
        publication_sources=tuple(
            PublicationSourceMembership(
                membership_id=stable_id(
                    "publication-source",
                    publication_id,
                    version.source_version_id,
                    "primary" if index == 0 else "supporting",
                ),
                publication_id=publication_id,
                source_version_id=version.source_version_id,
                source_role="primary" if index == 0 else "supporting",
            )
            for index, version in enumerate(source_versions)
        ),
        source_anchors=tuple(anchors_by_id[key] for key in sorted(anchors_by_id)),
        facts=tuple(
            SemanticFactRecord(
                fact_id=fact.fact_id,
                subject_iri=fact.subject_iri,
                subject_class_iri=fact.subject_class_iri,
                predicate_iri=fact.predicate_iri,
                object_kind=fact.object_kind,
                object_value=fact.object_value,
                object_class_iri=fact.object_class_iri,
                datatype_iri=fact.datatype_iri,
                validation_profile=fact.validation_profile,
                evidence_mode=fact.evidence_mode,
            )
            for fact in facts
        ),
        fact_memberships=tuple(
            PublicationFactMembership(
                membership_id=stable_id(
                    "publication-fact",
                    publication_id,
                    fact.fact_id,
                ),
                publication_id=publication_id,
                fact_id=fact.fact_id,
            )
            for fact in facts
        ),
        evidence_links=(
            PublicationEvidenceLink(
                evidence_link_id=stable_id(
                    "publication-evidence",
                    publication_id,
                    "structured_record",
                    root_id,
                    source_version.source_version_id,
                    anchor.source_anchor_id,
                    evidence_ref,
                ),
                publication_id=publication_id,
                owner_kind="structured_record",
                owner_id=root_id,
                source_version_id=source_version.source_version_id,
                source_anchor_id=anchor.source_anchor_id,
                evidence_text=source_version.content,
                evidence_ref=evidence_ref,
            ),
            *fact_evidence_links,
        ),
    )


def _bts_publication(
    record: BTSFlightSourceRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    required = {
        "reporting carrier": record.reporting_carrier,
        "flight number": record.flight_number,
        "origin": record.origin,
        "destination": record.destination,
        "scheduled departure key": record.scheduled_departure_key,
    }
    missing = [label for label, value in required.items() if not value]
    if missing:
        raise ValueError("missing " + ", ".join(missing))
    source = _record_with_domain(record.source, temporal_domain_id)
    version = build_source_version(source)
    flight_id = stable_id(
        "flight",
        SourceFamily.BTS_FLIGHT_OPERATION.value,
        record.flight_date.isoformat(),
        record.reporting_carrier,
        record.flight_number,
        record.origin,
        record.destination,
        record.scheduled_departure_key,
    )
    structured = {
        "flight_date": record.flight_date.isoformat(),
        "reporting_carrier": record.reporting_carrier,
        "flight_number": record.flight_number,
        "tail_number": record.tail_number,
        "origin": record.origin,
        "destination": record.destination,
        "scheduled_departure_key": record.scheduled_departure_key,
        "scheduled_departure": record.scheduled_departure,
        "actual_wheels_off": record.actual_wheels_off,
        "time_basis": record.time_basis,
        "cancelled": record.cancelled,
        "diverted": record.diverted,
    }
    package = _publication_package(
        root_id=flight_id,
        root_kind="flight",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload=structured,
    )
    publication_id = package.publication.publication_id
    flight = FlightRecord(
        flight_id=flight_id,
        temporal_domain_id=temporal_domain_id,
        source_family=SourceFamily.BTS_FLIGHT_OPERATION,
        service_date=record.flight_date,
        reporting_carrier=record.reporting_carrier,
        flight_number=record.flight_number,
        origin_airport_id=record.origin,
        destination_airport_id=record.destination,
        scheduled_departure_key=record.scheduled_departure_key,
        tail_number=record.tail_number,
        scheduled_departure=record.scheduled_departure,
        actual_wheels_off=record.actual_wheels_off,
        time_basis=record.time_basis,
        cancelled=record.cancelled,
        diverted=record.diverted,
    )
    carrier = AirCarrierRecord(
        carrier_id=stable_id(
            "air-carrier",
            SourceFamily.BTS_FLIGHT_OPERATION.value,
            record.reporting_carrier,
        ),
        temporal_domain_id=temporal_domain_id,
        source_family=SourceFamily.BTS_FLIGHT_OPERATION,
        carrier_code=record.reporting_carrier,
        display_name=None,
    )
    materialization = FlightAirspaceMaterialization(
        publication=package,
        flight=flight,
        flight_publication=FlightPublicationRecord(
            publication_id=publication_id,
            flight_id=flight_id,
            temporal_domain_id=temporal_domain_id,
            primary_source_version_id=version.source_version_id,
        ),
        air_carriers=(carrier,),
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:bts-flight",
        root_kind="flight",
        materialization=materialization,
    )


def _weather_publication(
    record: IEMWeatherSourceRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    source = _record_with_domain(record.source, temporal_domain_id)
    version = build_source_version(source)
    observation_id = stable_id(
        "weather-observation",
        SourceFamily.HISTORICAL_METAR_SPECI.value,
        record.station_id,
        record.observed_at.isoformat(),
        version.source_version_id,
    )
    structured = {
        "station_id": record.station_id,
        "observed_at": record.observed_at,
        "report_type": record.report_type,
        "raw_report": record.raw_report,
        "phenomenon_tokens": record.phenomenon_tokens,
    }
    package = _publication_package(
        root_id=observation_id,
        root_kind="weather_observation",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload=structured,
    )
    publication_id = package.publication.publication_id
    materialization = FlightAirspaceMaterialization(
        publication=package,
        weather_observations=(
            WeatherObservationRecord(
                observation_id=observation_id,
                publication_id=publication_id,
                temporal_domain_id=temporal_domain_id,
                source_family=SourceFamily.HISTORICAL_METAR_SPECI,
                station_id=record.station_id,
                observed_at=record.observed_at,
                report_type=record.report_type,
                raw_report=record.raw_report,
                phenomenon_tokens=record.phenomenon_tokens,
                source_version_id=version.source_version_id,
            ),
        ),
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:historical-weather",
        root_kind="weather_observation",
        materialization=materialization,
    )


def _registry_publications(
    record: FAAAircraftTechnicalSourceRecord,
    temporal_domain_id: str,
) -> tuple[_PendingPublication, _PendingPublication]:
    source = _record_with_domain(record.source, temporal_domain_id)
    version = build_source_version(source)
    aircraft_id = stable_id(
        "aircraft",
        SourceFamily.FAA_AIRCRAFT_REGISTRY.value,
        record.tail_number,
    )
    model_id = stable_id(
        "aircraft-model",
        SourceFamily.FAA_AIRCRAFT_REGISTRY.value,
        record.manufacturer,
        record.model_code,
    )
    structured = {
        "tail_number": record.tail_number,
        "model_code": record.model_code,
        "manufacturer": record.manufacturer,
        "model": record.model,
        "registry_snapshot_at": record.registry_snapshot_at,
    }
    aircraft_package = _publication_package(
        root_id=aircraft_id,
        root_kind="aircraft",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload=structured,
    )
    model_package = _publication_package(
        root_id=model_id,
        root_kind="aircraft_model",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload=structured,
    )
    aircraft = _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:faa-registry-aircraft",
        root_kind="aircraft",
        materialization=FlightAirspaceMaterialization(
            publication=aircraft_package,
            aircraft=(
                AircraftRecord(
                    aircraft_id=aircraft_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.FAA_AIRCRAFT_REGISTRY,
                    registration_number=record.tail_number,
                ),
            ),
        ),
    )
    model = _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:faa-registry-model",
        root_kind="aircraft_model",
        materialization=FlightAirspaceMaterialization(
            publication=model_package,
            aircraft_models=(
                AircraftModelRecord(
                    aircraft_model_id=model_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.FAA_AIRCRAFT_REGISTRY,
                    manufacturer_code=record.manufacturer,
                    model_code=record.model_code,
                    display_name=record.model,
                ),
            ),
        ),
    )
    return aircraft, model


def _nasr_source_record(
    trace: NASRSourceTrace,
    *,
    asset: SourceAssetRecord,
    logical_time: datetime | None,
) -> SourceRecord:
    return SourceRecord(
        source_id=trace.source_record_id,
        family=SourceFamily.NASR_AIRSPACE,
        content=trace.canonical_content,
        title=f"NASR {trace.record_locator}",
        effective_date=logical_time,
        source_url=asset.source_url,
        asset_id=asset.asset_id,
        logical_time=logical_time.isoformat() if logical_time is not None else None,
        metadata={
            "archive_sha256": trace.archive_checksum,
            "zip_member": trace.zip_member,
            "line_number": trace.line_number,
            "record_locator": trace.record_locator,
            "record_checksum": trace.record_checksum,
            "parser_version": FLIGHT_SOURCE_ADAPTER_VERSION,
        },
    )


def _nasa_source_record(
    trace: NASARDFSourceTrace,
    *,
    asset: SourceAssetRecord,
    time_basis: str | None = None,
) -> SourceRecord:
    """Preserve one canonical subject-level ATMONTO record as evidence."""

    metadata = {
        "archive_sha256": trace.archive_checksum,
        "zip_member": trace.zip_member,
        "record_locator": trace.record_locator,
        "subject_iri": trace.subject_iri,
        "related_subject_iris": list(trace.related_subject_iris),
        "record_checksum": trace.record_checksum,
        "parser_version": FLIGHT_SOURCE_ADAPTER_VERSION,
    }
    if time_basis is not None:
        metadata["time_basis"] = time_basis

    return SourceRecord(
        source_id=trace.source_record_id,
        family=SourceFamily.NASA_ATMONTO_INSTANCE,
        content="\n".join(trace.canonical_triples),
        title=f"NASA ATMONTO {trace.subject_iri}",
        source_url=asset.source_url,
        asset_id=asset.asset_id,
        metadata=metadata,
    )


def _atmonto_sample_source_record(
    trace: ATMONTHOSourceTrace,
    *,
    asset: SourceAssetRecord,
    logical_time: datetime,
) -> SourceRecord:
    triples = (*trace.canonical_subject_triples, *trace.association_triples)
    return SourceRecord(
        source_id=trace.source_record_id,
        family=SourceFamily.NASA_ATMONTO_INSTANCE,
        content="\n".join(triples),
        title=f"NASA ATMONTO {trace.subject_iri}",
        effective_date=logical_time,
        source_url=asset.source_url,
        asset_id=asset.asset_id,
        logical_time=logical_time.isoformat(),
        metadata={
            "archive_sha256": trace.archive_checksum,
            "zip_member": trace.zip_member,
            "record_locator": trace.record_locator,
            "subject_iri": trace.subject_iri,
            "record_checksum": trace.record_checksum,
            "parser_version": FLIGHT_SOURCE_ADAPTER_VERSION,
            "time_basis": "source_naive_interpreted_utc",
        },
    )


def _atmonto_weather_publication(
    record: ATMONTHistoricalWeatherSourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    if not record.report_text:
        raise ValueError("NASA METAR report has no source report text")
    source = _record_with_domain(
        _atmonto_sample_source_record(
            record.source,
            asset=asset,
            logical_time=record.observed_at,
        ),
        temporal_domain_id,
    )
    version = build_source_version(source)
    observation_id = record.subject_iri
    package = _publication_package(
        root_id=observation_id,
        root_kind="weather_observation",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload={
            "airport_iri": record.airport_iri,
            "observed_at": record.observed_at,
            "interval_end": record.interval_end,
            "report_text": record.report_text,
        },
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:nasa-metar",
        root_kind="weather_observation",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            weather_observations=(
                WeatherObservationRecord(
                    observation_id=observation_id,
                    publication_id=package.publication.publication_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    station_id=_airport_identifier(record.airport_iri),
                    observed_at=record.observed_at,
                    report_type="METAR",
                    raw_report=record.report_text,
                    source_version_id=version.source_version_id,
                ),
            ),
        ),
    )


def _atmonto_taf_publication(
    record: ATMONTOTAFSourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    source = _record_with_domain(
        _atmonto_sample_source_record(
            record.source,
            asset=asset,
            logical_time=record.issued_at,
        ),
        temporal_domain_id,
    )
    version = build_source_version(source)
    package = _publication_package(
        root_id=record.subject_iri,
        root_kind="weather_forecast",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload={
            "airport_iri": record.airport_iri,
            "issued_at": record.issued_at,
            "valid_from": record.valid_from,
            "valid_to": record.valid_to,
            "report_text": record.report_text,
        },
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:nasa-taf",
        root_kind="weather_forecast",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            weather_forecasts=(
                WeatherForecastRecord(
                    forecast_id=record.subject_iri,
                    publication_id=package.publication.publication_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    station_id=_airport_identifier(record.airport_iri),
                    issued_at=record.issued_at,
                    valid_from=record.valid_from,
                    valid_to=record.valid_to,
                    raw_report=record.report_text,
                    source_version_id=version.source_version_id,
                ),
            ),
        ),
    )


def _atmonto_airport_data_publication(
    record: ATMONTOAirportDataSourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    source = _record_with_domain(
        _atmonto_sample_source_record(
            record.source,
            asset=asset,
            logical_time=record.interval_start,
        ),
        temporal_domain_id,
    )
    version = build_source_version(source)
    package = _publication_package(
        root_id=record.subject_iri,
        root_kind="airport_operational_observation",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload={
            "airport_iri": record.airport_iri,
            "interval_start": record.interval_start,
            "interval_end": record.interval_end,
            "metrics": record.metrics,
        },
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:nasa-aspm",
        root_kind="airport_operational_observation",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            airport_operational_observations=(
                AirportOperationalObservationRecord(
                    observation_id=record.subject_iri,
                    publication_id=package.publication.publication_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    airport_id=_airport_identifier(record.airport_iri),
                    interval_start=record.interval_start,
                    interval_end=record.interval_end,
                    metrics=dict(record.metrics),
                    source_version_id=version.source_version_id,
                ),
            ),
        ),
    )


def _atmonto_tmi_publication(
    record: ATMONTOTMISourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    source = _record_with_domain(
        _atmonto_sample_source_record(
            record.source,
            asset=asset,
            logical_time=record.issued_at,
        ),
        temporal_domain_id,
    )
    version = build_source_version(source)
    package = _publication_package(
        root_id=record.subject_iri,
        root_kind="tmi",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload={
            "tmi_type": record.tmi_type,
            "controlled_element_iri": record.controlled_element_iri,
            "airport_iri": record.airport_iri,
            "reason": record.reason,
            "issued_at": record.issued_at,
            "effective_from": record.effective_from,
            "effective_to": record.effective_to,
        },
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:nasa-tmi",
        root_kind="tmi",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            tmi_publications=(
                TMIPublicationRecord(
                    tmi_id=record.subject_iri,
                    publication_id=package.publication.publication_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    tmi_type=record.tmi_type,
                    controlled_element_id=record.controlled_element_iri,
                    airport_id=(
                        _airport_identifier(record.airport_iri)
                        if record.airport_iri is not None
                        else None
                    ),
                    reason=record.reason,
                    issued_at=record.issued_at,
                    effective_from=record.effective_from,
                    effective_to=record.effective_to,
                    source_version_id=version.source_version_id,
                ),
            ),
        ),
    )


def _nasa_sector_publication(
    record: NASASectorSourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    source = _record_with_domain(
        _nasa_source_record(record.source, asset=asset),
        temporal_domain_id,
    )
    version = build_source_version(source)
    package = _publication_package(
        root_id=record.subject_iri,
        root_kind="sector",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload={
            "subject_iri": record.subject_iri,
            "sector_identifier": record.sector_identifier,
        },
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:nasa-sector",
        root_kind="sector",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            sectors=(
                SectorRecord(
                    sector_id=record.subject_iri,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    sector_identifier=record.sector_identifier,
                ),
            ),
        ),
    )


def _nasa_fix_publication(
    record: NASANavigationFixSourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    source = _record_with_domain(
        _nasa_source_record(record.source, asset=asset),
        temporal_domain_id,
    )
    version = build_source_version(source)
    package = _publication_package(
        root_id=record.subject_iri,
        root_kind="navigation_fix",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload={
            "subject_iri": record.subject_iri,
            "fix_identifier": record.fix_identifier,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "sector_iris": record.sector_iris,
        },
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:nasa-navigation-fix",
        root_kind="navigation_fix",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            navigation_fixes=(
                NavigationFixRecord(
                    fix_id=record.subject_iri,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    fix_identifier=record.fix_identifier,
                    latitude=record.latitude,
                    longitude=record.longitude,
                ),
            ),
        ),
    )


def _iri_fragment(value: str) -> str:
    return value.rsplit("#", 1)[-1].rstrip("/").rsplit("/", 1)[-1]


def _airport_identifier(value: str) -> str:
    fragment = _iri_fragment(value)
    return fragment.removesuffix("airport")


def _nasa_flight_publication(
    record: NASAFlightSourceRecord,
    *,
    routes_by_flight: dict[str, tuple[NASAActualRouteSourceRecord, ...]],
    points_by_route: dict[str, tuple[NASATrackPointSourceRecord, ...]],
    sector_ids_by_fix: dict[str, tuple[str, ...]],
    fix_records_by_id: dict[
        str,
        tuple[NASANavigationFixSourceRecord, ...],
    ],
    sectors_by_id: dict[str, NASASectorSourceRecord],
    profile_registry: ValidationProfileRegistry,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    if record.actual_departure_time is None:
        raise ValueError("NASA Flight has no actual departure time")
    if record.departure_airport_iri is None or record.arrival_airport_iri is None:
        raise ValueError("NASA Flight has no departure or arrival airport")

    primary_source = _record_with_domain(
        _nasa_source_record(
            record.source,
            asset=asset,
            time_basis=record.time_basis,
        ),
        temporal_domain_id,
    )
    primary_version = build_source_version(primary_source)
    flight_id = stable_id(
        "flight",
        SourceFamily.NASA_ATMONTO_INSTANCE.value,
        record.subject_iri,
    )
    structured = {
        "subject_iri": record.subject_iri,
        "call_sign": record.call_sign,
        "departure_airport_iri": record.departure_airport_iri,
        "arrival_airport_iri": record.arrival_airport_iri,
        "actual_departure_time": record.actual_departure_time,
        "actual_arrival_time": record.actual_arrival_time,
        "operated_by_iri": record.operated_by_iri,
        "aircraft_iri": record.aircraft_iri,
        "aircraft_type_iri": record.aircraft_type_iri,
        "actual_route_iris": record.actual_route_iris,
    }
    route_records = routes_by_flight.get(record.subject_iri, ())
    point_records = tuple(
        point
        for route in route_records
        for point in points_by_route.get(route.subject_iri, ())
    )
    referenced_fix_ids = {
        point.fix_iri for point in point_records if point.fix_iri is not None
    }
    fix_records = tuple(
        fix_record
        for fix_id in sorted(referenced_fix_ids)
        for fix_record in fix_records_by_id.get(fix_id, ())
    )
    referenced_sector_ids = {
        sector_id
        for point in point_records
        for sector_id in (
            *point.sector_iris,
            *sector_ids_by_fix.get(point.fix_iri or "", ()),
        )
    }
    sector_records = tuple(
        sectors_by_id[sector_id]
        for sector_id in sorted(referenced_sector_ids)
        if sector_id in sectors_by_id
    )

    supporting_records_by_id: dict[str, SourceRecord] = {}

    def register_supporting_record(
        trace: NASARDFSourceTrace,
        *,
        time_basis: str | None = None,
    ) -> None:
        source = _record_with_domain(
            _nasa_source_record(trace, asset=asset, time_basis=time_basis),
            temporal_domain_id,
        )
        previous = supporting_records_by_id.setdefault(source.source_id, source)
        if previous != source:
            raise ValueError("conflicting NASA source records share identity")

    for route in route_records:
        register_supporting_record(route.source)
    for point in point_records:
        register_supporting_record(point.source, time_basis=point.time_basis)
    for fix in fix_records:
        register_supporting_record(fix.source)
    for sector in sector_records:
        register_supporting_record(sector.source)
    supporting_records_by_id.pop(primary_source.source_id, None)
    supporting_records = tuple(
        supporting_records_by_id[source_id]
        for source_id in sorted(supporting_records_by_id)
    )
    supporting_versions = tuple(
        build_source_version(source) for source in supporting_records
    )

    compilation = compile_nasa_flight_airspace_facts(
        flights=(record,),
        routes=route_records,
        track_points=point_records,
        navigation_fixes=fix_records,
        sectors=sector_records,
        flight_root_ids={record.subject_iri: flight_id},
        profile_registry=profile_registry,
    )
    formal_publication = run_nasa_flight_airspace_publication_kernel(
        compilation=compilation,
        profile_registry=profile_registry,
        source_snapshot=build_source_snapshot_registry(
            [primary_source, *supporting_records]
        ),
    )
    package = _publication_package(
        root_id=flight_id,
        root_kind="flight",
        temporal_domain_id=temporal_domain_id,
        source_version=primary_version,
        supporting_source_versions=supporting_versions,
        structured_payload=structured,
        formal_publication=formal_publication,
        fact_traces=compilation.fact_traces,
    )
    publication_id = package.publication.publication_id

    route_rows: list[RouteRecord] = []
    point_rows: list[TrackPointRecord] = []
    passage_rows: list[SectorPassageRecord] = []
    mutable_supporting_versions = list(supporting_versions)
    memberships = list(package.publication_sources)
    anchors = list(package.source_anchors)
    evidence_links = list(package.evidence_links)

    def add_support(
        trace: NASARDFSourceTrace,
        *,
        owner_id: str,
        evidence_ref: str,
        time_basis: str | None = None,
    ) -> tuple[SourceVersionRecord, SourceAnchorRecord]:
        source = _record_with_domain(
            _nasa_source_record(trace, asset=asset, time_basis=time_basis),
            temporal_domain_id,
        )
        version = build_source_version(source)
        anchor = _full_record_anchor(version)
        if version.source_version_id not in {
            item.source_version_id for item in mutable_supporting_versions
        }:
            mutable_supporting_versions.append(version)
            memberships.append(
                PublicationSourceMembership(
                    membership_id=stable_id(
                        "publication-source",
                        publication_id,
                        version.source_version_id,
                        "supporting",
                    ),
                    publication_id=publication_id,
                    source_version_id=version.source_version_id,
                    source_role="supporting",
                )
            )
            anchors.append(anchor)
        evidence_links.append(
            PublicationEvidenceLink(
                evidence_link_id=stable_id(
                    "publication-evidence",
                    publication_id,
                    "structured_record",
                    owner_id,
                    version.source_version_id,
                    anchor.source_anchor_id,
                    evidence_ref,
                ),
                publication_id=publication_id,
                owner_kind="structured_record",
                owner_id=owner_id,
                source_version_id=version.source_version_id,
                source_anchor_id=anchor.source_anchor_id,
                evidence_text=version.content,
                evidence_ref=evidence_ref,
            )
        )
        return version, anchor

    for route_record in route_records:
        route_id = stable_id("route", publication_id, route_record.subject_iri)
        route_rows.append(
            RouteRecord(
                route_id=route_id,
                flight_publication_id=publication_id,
                temporal_domain_id=temporal_domain_id,
                source_route_key=route_record.subject_iri,
                route_kind="actual",
            )
        )
        add_support(
            route_record.source,
            owner_id=route_id,
            evidence_ref="route_subject",
        )
        for point_record in points_by_route.get(route_record.subject_iri, ()):
            if point_record.sequence_number is None or point_record.reporting_time is None:
                raise ValueError("NASA TrackPoint has no sequence number or reporting time")
            point_source = _record_with_domain(
                _nasa_source_record(
                    point_record.source,
                    asset=asset,
                    time_basis=point_record.time_basis,
                ),
                temporal_domain_id,
            )
            point_version = build_source_version(point_source)
            point_anchor = _full_record_anchor(point_version)
            point_id = stable_id(
                "track-point",
                route_id,
                point_record.sequence_number,
                point_version.source_version_id,
                point_anchor.source_anchor_id,
            )
            add_support(
                point_record.source,
                owner_id=point_id,
                evidence_ref="track_point_subject",
                time_basis=point_record.time_basis,
            )
            sector_ids = tuple(
                sorted(
                    {
                        *point_record.sector_iris,
                        *sector_ids_by_fix.get(point_record.fix_iri or "", ()),
                    }.intersection(sectors_by_id)
                )
            )
            point_rows.append(
                TrackPointRecord(
                    track_point_id=point_id,
                    route_id=route_id,
                    temporal_domain_id=temporal_domain_id,
                    sequence_number=point_record.sequence_number,
                    reporting_time=point_record.reporting_time,
                    latitude=point_record.latitude,
                    longitude=point_record.longitude,
                    ground_speed=point_record.ground_speed,
                    navigation_fix_id=(
                        point_record.fix_iri
                        if point_record.fix_iri in fix_records_by_id
                        else None
                    ),
                    sector_ids=sector_ids,
                    source_version_id=point_version.source_version_id,
                    source_anchor_id=point_anchor.source_anchor_id,
                )
            )
            for sector_id in sector_ids:
                derivation_id = stable_id(
                    "derivation",
                    "nasa-sector-passage-v1",
                    publication_id,
                    point_id,
                    sector_id,
                )
                passage_id = stable_id(
                    "sector-passage",
                    publication_id,
                    point_id,
                    sector_id,
                    derivation_id,
                )
                passage_rows.append(
                    SectorPassageRecord(
                        passage_id=passage_id,
                        flight_publication_id=publication_id,
                        route_id=route_id,
                        track_point_id=point_id,
                        sector_id=sector_id,
                        temporal_domain_id=temporal_domain_id,
                        reporting_time=point_record.reporting_time,
                        derivation_id=derivation_id,
                    )
                )
                add_support(
                    point_record.source,
                    owner_id=passage_id,
                    evidence_ref="sector_passage_from_track_point",
                )

    package = KnowledgePublicationPackage(
        root=package.root,
        publication=package.publication,
        publication_sources=tuple(memberships),
        source_anchors=tuple(anchors),
        facts=package.facts,
        fact_memberships=package.fact_memberships,
        evidence_links=tuple(evidence_links),
        derivations=package.derivations,
    )
    time_basis = (
        "source_naive_interpreted_utc"
        if record.time_basis == "source_naive_interpreted_utc"
        else "utc"
    )
    return _PendingPublication(
        source_version=primary_version,
        supporting_source_versions=tuple(mutable_supporting_versions),
        adapter_id="flight-airspace:nasa-flight",
        root_kind="flight",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            flight=FlightRecord(
                flight_id=flight_id,
                temporal_domain_id=temporal_domain_id,
                source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                source_flight_key=record.subject_iri,
                service_date=record.actual_departure_time.date(),
                call_sign=record.call_sign,
                operated_by_id=record.operated_by_iri,
                aircraft_id=record.aircraft_iri,
                aircraft_type_id=record.aircraft_type_iri,
                origin_airport_id=_airport_identifier(record.departure_airport_iri),
                destination_airport_id=_airport_identifier(record.arrival_airport_iri),
                actual_departure=record.actual_departure_time,
                actual_arrival=record.actual_arrival_time,
                time_basis=time_basis,
            ),
            flight_publication=FlightPublicationRecord(
                publication_id=publication_id,
                flight_id=flight_id,
                temporal_domain_id=temporal_domain_id,
                primary_source_version_id=primary_version.source_version_id,
            ),
            routes=tuple(route_rows),
            track_points=tuple(point_rows),
            sector_passages=tuple(passage_rows),
        ),
    )


def _nasr_airport_publication(
    record: NASRAirportSourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    source = _record_with_domain(
        _nasr_source_record(
            record.source,
            asset=asset,
            logical_time=record.effective_start,
        ),
        temporal_domain_id,
    )
    version = build_source_version(source)
    airport_id = stable_id(
        "airport",
        SourceFamily.NASR_AIRSPACE.value,
        record.airport_code,
    )
    package = _publication_package(
        root_id=airport_id,
        root_kind="airport",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload={
            "airport_code": record.airport_code,
            "faa_code": record.faa_code,
            "display_name": record.display_name,
            "city": record.city,
            "state": record.state,
            "effective_start": record.effective_start,
        },
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:nasr-airport",
        root_kind="airport",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            airports=(
                AirportRecord(
                    airport_id=airport_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.NASR_AIRSPACE,
                    airport_code=record.airport_code,
                    display_name=record.display_name,
                ),
            ),
        ),
    )


def _nasr_artcc_publication(
    record: NASRARTCCSourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
) -> _PendingPublication:
    source = _record_with_domain(
        _nasr_source_record(
            record.source,
            asset=asset,
            logical_time=record.effective_start,
        ),
        temporal_domain_id,
    )
    version = build_source_version(source)
    artcc_id = stable_id(
        "artcc",
        SourceFamily.NASR_AIRSPACE.value,
        record.artcc_code,
    )
    package = _publication_package(
        root_id=artcc_id,
        root_kind="artcc",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload={
            "artcc_code": record.artcc_code,
            "icao_code": record.icao_code,
            "display_name": record.display_name,
            "state": record.state,
            "effective_start": record.effective_start,
        },
    )
    return _PendingPublication(
        source_version=version,
        adapter_id="flight-airspace:nasr-artcc",
        root_kind="artcc",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            artccs=(
                ARTCCRecord(
                    artcc_id=artcc_id,
                    temporal_domain_id=temporal_domain_id,
                    source_family=SourceFamily.NASR_AIRSPACE,
                    artcc_code=record.artcc_code,
                    display_name=record.display_name,
                ),
            ),
        ),
    )


def _nasr_assignment_publication(
    record: NASRAirportARTCCAssignmentSourceRecord,
    *,
    asset: SourceAssetRecord,
    temporal_domain_id: str,
    airport_publication_id: str,
    artcc_publication_id: str,
) -> _PendingPublication:
    source = _record_with_domain(
        _nasr_source_record(
            record.source,
            asset=asset,
            logical_time=record.effective_start,
        ),
        temporal_domain_id,
    )
    version = build_source_version(source)
    procedure_id = "nasr-airport-artcc-role-v1"
    procedure_checksum = _canonical_digest({"procedure_id": procedure_id})
    assignment_id = stable_id(
        "airport-artcc-assignment",
        airport_publication_id,
        artcc_publication_id,
        record.assignment_role,
        record.effective_start.isoformat() if record.effective_start else "",
        "",
        procedure_checksum,
    )
    derivation_id = stable_id(
        "nasr-airport-artcc-derivation",
        assignment_id,
        version.source_version_id,
        procedure_checksum,
    )
    assignment = AirportARTCCAssignmentRecord(
        assignment_id=assignment_id,
        airport_publication_id=airport_publication_id,
        artcc_publication_id=artcc_publication_id,
        temporal_domain_id=temporal_domain_id,
        assignment_role=record.assignment_role,
        effective_start=record.effective_start,
        effective_end=None,
        procedure_id=procedure_id,
        procedure_checksum=procedure_checksum,
        derivation_id=derivation_id,
    )
    package = _publication_package(
        root_id=assignment_id,
        root_kind="airport_artcc_assignment",
        temporal_domain_id=temporal_domain_id,
        source_version=version,
        structured_payload=assignment.model_dump(mode="json"),
    )
    return _PendingPublication(
        source_version=version,
        adapter_id=(
            "flight-airspace:nasr-assignment:"
            f"{record.assignment_role}:{record.artcc_code}"
        ),
        root_kind="airport_artcc_assignment",
        materialization=FlightAirspaceMaterialization(
            publication=package,
            airport_artcc_assignments=(assignment,),
        ),
    )


def _metadata(config: dict[str, Any], key: str) -> dict[str, Any]:
    all_metadata = config.get("source_metadata")
    if not isinstance(all_metadata, dict):
        return {}
    value = all_metadata.get(key)
    return value if isinstance(value, dict) else {}


def _required_domain(config: dict[str, Any], key: str) -> str:
    value = _metadata(config, key).get("temporal_domain_id")
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"source_metadata.{key}.temporal_domain_id must be configured"
        )
    return value


def _required_datetime(config: dict[str, Any], key: str, field: str) -> datetime:
    value = _metadata(config, key).get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"source_metadata.{key}.{field} must be configured")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"source_metadata.{key}.{field} must include a timezone")
    return parsed.astimezone(UTC)


def _scope_date(value: object, *, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{field} must be an ISO date") from exc
    raise ValueError(f"{field} must be an ISO date")


def _bts_ingestion_scope(
    config: dict[str, Any],
) -> tuple[
    date | None,
    date | None,
    set[str] | None,
    set[tuple[str, str]] | None,
]:
    """Return the explicit BTS row scope; never imply a national month scan."""

    scope = _metadata(config, "bts_flight_operations").get("ingestion_scope")
    if not isinstance(scope, dict):
        raise ValueError(
            "source_metadata.bts_flight_operations.ingestion_scope must be "
            "configured; use mode=all only for an explicit full archive scan"
        )
    mode = scope.get("mode")
    if mode == "all":
        return None, None, None, None
    if mode != "bounded":
        raise ValueError(
            "source_metadata.bts_flight_operations.ingestion_scope.mode must "
            "be bounded or all"
        )

    raw_start = scope.get("service_date_from")
    raw_end = scope.get("service_date_to")
    start = (
        _scope_date(raw_start, field="ingestion_scope.service_date_from")
        if raw_start is not None
        else None
    )
    end = (
        _scope_date(raw_end, field="ingestion_scope.service_date_to")
        if raw_end is not None
        else None
    )
    if start is not None and end is not None and start > end:
        raise ValueError(
            "ingestion_scope.service_date_from must not be after "
            "service_date_to"
        )

    raw_airports = scope.get("origin_airports")
    if raw_airports is None:
        airports = None
    elif isinstance(raw_airports, list) and all(
        isinstance(value, str) and value.strip() for value in raw_airports
    ):
        airports = {value.strip().upper() for value in raw_airports}
    else:
        raise ValueError(
            "ingestion_scope.origin_airports must be a list of airport codes"
        )

    raw_routes = scope.get("routes")
    if raw_routes is None:
        routes = None
    elif isinstance(raw_routes, list):
        routes = set()
        for value in raw_routes:
            if not (
                isinstance(value, list)
                and len(value) == 2
                and all(isinstance(code, str) and code.strip() for code in value)
            ):
                raise ValueError(
                    "ingestion_scope.routes must contain [origin, destination] pairs"
                )
            routes.add((value[0].strip().upper(), value[1].strip().upper()))
    else:
        raise ValueError(
            "ingestion_scope.routes must contain [origin, destination] pairs"
        )
    if start is None and end is None and airports is None and routes is None:
        raise ValueError("bounded BTS ingestion_scope must define at least one filter")
    return start, end, airports, routes


def _configured_assets(
    config: dict[str, Any],
    *,
    source_root: str | Path | None,
    project_root: str | Path,
) -> tuple[SourceAssetRecord, ...]:
    configured_sources = config.get("sources")
    sources = configured_sources if isinstance(configured_sources, dict) else {}
    selected = {key: sources[key] for key in _SOURCE_KEYS if key in sources}
    if not selected:
        return ()
    scoped = dict(config)
    scoped["sources"] = selected
    return discover_source_assets(
        scoped,
        source_root=source_root,
        project_root=project_root,
    )


def _asset_path(
    asset: SourceAssetRecord,
    *,
    source_root: str | Path | None,
    project_root: str | Path,
) -> Path:
    return resolve_source_path(
        asset.local_path,
        source_root=source_root,
        project_root=project_root,
    ).resolved_path


def _terminal_result(
    store: AviationEvidenceStore,
    pending: _PendingPublication,
) -> KnowledgeIngestionResult | None:
    prior = store.get_knowledge_ingestion_result(
        source_version_id=pending.source_version.source_version_id,
        adapter_id=pending.adapter_id,
        adapter_version=FLIGHT_SOURCE_ADAPTER_VERSION,
    )
    if prior is not None and prior.status in {"ok", "insufficient"}:
        return prior
    return None


def _summary_result(
    pending: _PendingPublication,
    *,
    status: str,
    disposition: str,
    reason: str,
    root_id: str | None = None,
    publication_id: str | None = None,
) -> FlightAirspaceRootResult:
    package = pending.materialization.publication
    return FlightAirspaceRootResult(
        source_version_id=pending.source_version.source_version_id,
        source_family=pending.source_version.family,
        root_kind=pending.root_kind,
        root_id=root_id if root_id is not None else package.root.root_id,
        publication_id=(
            publication_id
            if publication_id is not None
            else package.publication.publication_id
        ),
        status=status,
        disposition=disposition,
        reason=reason,
    )


def _knowledge_outcome(
    pending: _PendingPublication,
    *,
    status: str,
    reason: str,
) -> KnowledgeIngestionResult:
    package = pending.materialization.publication
    accepted = status == "ok"
    return KnowledgeIngestionResult(
        source_version_id=pending.source_version.source_version_id,
        adapter_id=pending.adapter_id,
        adapter_version=FLIGHT_SOURCE_ADAPTER_VERSION,
        profile_checksum=None,
        status=status,
        root_id=package.root.root_id if accepted else None,
        publication_id=package.publication.publication_id if accepted else None,
        reason=reason,
        recorded_at=datetime.now(UTC),
    )


def _record_insufficient(
    store: AviationEvidenceStore,
    *,
    source: SourceRecord,
    temporal_domain_id: str,
    adapter_id: str,
    root_kind: str,
    reason: str,
) -> FlightAirspaceRootResult:
    version = build_source_version(_record_with_domain(source, temporal_domain_id))
    store.register_source_version(version)
    prior = store.get_knowledge_ingestion_result(
        source_version_id=version.source_version_id,
        adapter_id=adapter_id,
        adapter_version=FLIGHT_SOURCE_ADAPTER_VERSION,
    )
    if prior is not None and prior.status in {"ok", "insufficient"}:
        return FlightAirspaceRootResult(
            source_version_id=version.source_version_id,
            source_family=version.family,
            root_kind=root_kind,
            root_id=prior.root_id,
            publication_id=prior.publication_id,
            status=prior.status,
            disposition="skipped",
            reason=prior.reason,
        )
    store.record_knowledge_ingestion_result(
        KnowledgeIngestionResult(
            source_version_id=version.source_version_id,
            adapter_id=adapter_id,
            adapter_version=FLIGHT_SOURCE_ADAPTER_VERSION,
            profile_checksum=None,
            status="insufficient",
            root_id=None,
            publication_id=None,
            reason=reason,
            recorded_at=datetime.now(UTC),
        )
    )
    return FlightAirspaceRootResult(
        source_version_id=version.source_version_id,
        source_family=version.family,
        root_kind=root_kind,
        root_id=None,
        publication_id=None,
        status="insufficient",
        disposition="recorded",
        reason=reason,
    )


def _record_insufficient_chunks(
    store: AviationEvidenceStore,
    records: Iterable[_PendingInsufficient],
    *,
    chunk_size: int,
) -> Iterator[FlightAirspaceRootResult]:
    """Register unsupported normalized records without per-row transactions."""

    chunk: list[_PendingInsufficient] = []

    def flush() -> tuple[FlightAirspaceRootResult, ...]:
        if not chunk:
            return ()
        store.register_source_versions(
            tuple(pending.source_version for pending in chunk)
        )
        summaries: list[FlightAirspaceRootResult] = []
        new_results: list[KnowledgeIngestionResult] = []
        for pending in chunk:
            prior = store.get_knowledge_ingestion_result(
                source_version_id=pending.source_version.source_version_id,
                adapter_id=pending.adapter_id,
                adapter_version=FLIGHT_SOURCE_ADAPTER_VERSION,
            )
            if prior is not None and prior.status in {"ok", "insufficient"}:
                disposition = "skipped"
                status = prior.status
                reason = prior.reason
            else:
                disposition = "recorded"
                status = "insufficient"
                reason = pending.reason
                new_results.append(
                    KnowledgeIngestionResult(
                        source_version_id=pending.source_version.source_version_id,
                        adapter_id=pending.adapter_id,
                        adapter_version=FLIGHT_SOURCE_ADAPTER_VERSION,
                        status="insufficient",
                        reason=reason,
                        recorded_at=datetime.now(UTC),
                    )
                )
            summaries.append(
                FlightAirspaceRootResult(
                    source_version_id=pending.source_version.source_version_id,
                    source_family=pending.source_version.family,
                    root_kind=pending.root_kind,
                    root_id=None,
                    publication_id=None,
                    status=status,
                    disposition=disposition,
                    reason=reason,
                )
            )
        store.record_knowledge_ingestion_results(tuple(new_results))
        chunk.clear()
        return tuple(summaries)

    for record in records:
        chunk.append(record)
        if len(chunk) >= chunk_size:
            yield from flush()
    yield from flush()


def _publish_chunks(
    store: AviationEvidenceStore,
    pending_records: Iterable[_PendingPublication],
    *,
    chunk_size: int,
) -> Iterator[FlightAirspaceRootResult]:
    chunk: list[_PendingPublication] = []

    def flush() -> tuple[FlightAirspaceRootResult, ...]:
        if not chunk:
            return ()
        store.register_source_versions(
            tuple(
                version
                for pending in chunk
                for version in pending.source_versions
            )
        )
        publishable: list[_PendingPublication] = []
        completed: list[FlightAirspaceRootResult] = []
        for pending in chunk:
            prior = _terminal_result(store, pending)
            if prior is None:
                publishable.append(pending)
                continue
            completed.append(
                _summary_result(
                    pending,
                    status=prior.status,
                    disposition="skipped",
                    reason=prior.reason,
                    root_id=prior.root_id,
                    publication_id=prior.publication_id,
                )
            )
        outcomes = store.apply_flight_airspace_publication_batch(
            tuple(pending.materialization for pending in publishable)
        )
        ingestion_results: list[KnowledgeIngestionResult] = []
        for pending in publishable:
            publication_id = (
                pending.materialization.publication.publication.publication_id
            )
            outcome = outcomes[publication_id]
            if outcome == "blocked":
                status = "blocked"
                reason = "structured publication was rejected by the store"
            else:
                status = "ok"
                reason = "structured publication accepted"
            ingestion_results.append(
                _knowledge_outcome(pending, status=status, reason=reason)
            )
            completed.append(
                _summary_result(
                    pending,
                    status=status,
                    disposition=outcome,
                    reason=reason,
                    root_id=(
                        pending.materialization.publication.root.root_id
                        if status == "ok"
                        else None
                    ),
                    publication_id=publication_id if status == "ok" else None,
                )
            )
        store.record_knowledge_ingestion_results(tuple(ingestion_results))
        chunk.clear()
        return tuple(completed)

    for pending in pending_records:
        chunk.append(pending)
        if len(chunk) >= chunk_size:
            yield from flush()
    yield from flush()


def _ingest_adapted_records(
    store: AviationEvidenceStore,
    records: Iterable[_AdaptedRecord],
    *,
    converter: Callable[[_AdaptedRecord, str], _PendingPublication],
    source_getter: Callable[[_AdaptedRecord], SourceRecord],
    temporal_domain_id: str,
    adapter_id: str,
    root_kind: str,
    chunk_size: int,
) -> Iterator[FlightAirspaceRootResult]:
    pending: list[_PendingPublication] = []
    for record in records:
        try:
            publication = converter(record, temporal_domain_id)
        except ValueError as exc:
            if pending:
                yield from _publish_chunks(
                    store,
                    tuple(pending),
                    chunk_size=chunk_size,
                )
                pending.clear()
            yield _record_insufficient(
                store,
                source=source_getter(record),
                temporal_domain_id=temporal_domain_id,
                adapter_id=adapter_id,
                root_kind=root_kind,
                reason=str(exc),
            )
            continue
        pending.append(publication)
        if len(pending) >= chunk_size:
            yield from _publish_chunks(
                store,
                tuple(pending),
                chunk_size=chunk_size,
            )
            pending.clear()
    if pending:
        yield from _publish_chunks(
            store,
            tuple(pending),
            chunk_size=chunk_size,
        )


def run_flight_airspace_ingestion(
    config: dict[str, Any],
    store: AviationEvidenceStore,
    *,
    source_root: str | Path | None = None,
    project_root: str | Path = PROJECT_ROOT,
    chunk_size: int = 500,
    max_result_records: int = 100,
) -> FlightAirspaceIngestionSummary:
    """Ingest configured Flight/Airspace families into Store v2.

    Each adapter is consumed independently.  A terminal result is resumable,
    while a blocked root is attempted again on the next run.
    """

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    if max_result_records < 0:
        raise ValueError("max_result_records must not be negative")
    assets = _configured_assets(
        config,
        source_root=source_root,
        project_root=project_root,
    )
    for asset in assets:
        store.register_source_asset(asset)
    assets_by_key = {asset.asset_key: asset for asset in assets}
    summary = _SummaryAccumulator(max_result_records)

    bts_asset = assets_by_key.get("bts_flight_operations")
    if bts_asset is not None:
        metadata = _metadata(config, "bts_flight_operations")
        (
            service_date_from,
            service_date_to,
            origin_airports,
            routes,
        ) = _bts_ingestion_scope(config)
        configured_timezones = metadata.get("origin_timezones")
        origin_timezones = (
            configured_timezones if isinstance(configured_timezones, dict) else {}
        )
        records = iter_bts_flight_sources(
            _asset_path(
                bts_asset,
                source_root=source_root,
                project_root=project_root,
            ),
            origin_timezones={str(key): str(value) for key, value in origin_timezones.items()},
            service_date_from=service_date_from,
            service_date_to=service_date_to,
            origin_airports=origin_airports,
            routes=routes,
            asset_id=bts_asset.asset_id,
            asset_sha256=bts_asset.content_sha256,
            source_url=bts_asset.source_url,
        )
        domain = _required_domain(config, "bts_flight_operations")
        summary.extend(
            _ingest_adapted_records(
                store,
                records,
                converter=_bts_publication,
                source_getter=lambda record: record.source,
                temporal_domain_id=domain,
                adapter_id="flight-airspace:bts-flight",
                root_kind="flight",
                chunk_size=chunk_size,
            )
        )

    weather_asset = assets_by_key.get("historical_metar_speci")
    if weather_asset is not None:
        records = iter_iem_weather_sources(
            _asset_path(
                weather_asset,
                source_root=source_root,
                project_root=project_root,
            ),
            asset_id=weather_asset.asset_id,
            asset_sha256=weather_asset.content_sha256,
            source_url=weather_asset.source_url,
        )
        domain = _required_domain(config, "historical_metar_speci")
        summary.extend(
            _ingest_adapted_records(
                store,
                records,
                converter=_weather_publication,
                source_getter=lambda record: record.source,
                temporal_domain_id=domain,
                adapter_id="flight-airspace:historical-weather",
                root_kind="weather_observation",
                chunk_size=chunk_size,
            )
        )

    registry_asset = assets_by_key.get("faa_aircraft_registry")
    if registry_asset is not None:
        metadata = _metadata(config, "faa_aircraft_registry")
        configured_tails = metadata.get("tail_numbers")
        tail_numbers = (
            {str(value) for value in configured_tails}
            if isinstance(configured_tails, list)
            else None
        )
        records = iter_faa_registry_technical_sources(
            _asset_path(
                registry_asset,
                source_root=source_root,
                project_root=project_root,
            ),
            registry_snapshot_at=_required_datetime(
                config,
                "faa_aircraft_registry",
                "registry_snapshot_at",
            ),
            tail_numbers=tail_numbers,
            asset_id=registry_asset.asset_id,
            asset_sha256=registry_asset.content_sha256,
            source_url=registry_asset.source_url,
        )
        domain = _required_domain(config, "faa_aircraft_registry")
        summary.extend(
            _publish_chunks(
                store,
                (
                    pending
                    for record in records
                    for pending in _registry_publications(record, domain)
                ),
                chunk_size=chunk_size,
            )
        )

    nasa_asset = assets_by_key.get("nasa_atmonto_instances")
    if nasa_asset is not None:
        domain = _required_domain(config, "nasa_atmonto_instances")
        flight_airspace_profiles = load_validation_profile_registry(
            decision_guide=load_schema_guide(),
            include_flight_airspace=True,
        )
        nasa_records = tuple(
            iter_nasa_atmonto_airspace_records(
                _asset_path(
                    nasa_asset,
                    source_root=source_root,
                    project_root=project_root,
                ),
                include_global_fixes=False,
            )
        )
        flights = tuple(
            row for row in nasa_records if isinstance(row, NASAFlightSourceRecord)
        )
        routes = tuple(
            row
            for row in nasa_records
            if isinstance(row, NASAActualRouteSourceRecord)
        )
        points = tuple(
            row for row in nasa_records if isinstance(row, NASATrackPointSourceRecord)
        )
        sectors = tuple(
            row for row in nasa_records if isinstance(row, NASASectorSourceRecord)
        )
        referenced_fix_ids = {
            row.fix_iri for row in points if row.fix_iri is not None
        }
        fixes_by_id: dict[str, NASANavigationFixSourceRecord] = {}
        fix_records_by_id: dict[str, list[NASANavigationFixSourceRecord]] = {}
        sector_ids_by_fix: dict[str, set[str]] = {}
        referenced_sector_sources: dict[str, NASARDFSourceTrace] = {}
        for row in nasa_records:
            if not isinstance(row, NASANavigationFixSourceRecord):
                continue
            if row.subject_iri not in referenced_fix_ids:
                continue
            fix_records_by_id.setdefault(row.subject_iri, []).append(row)
            sector_ids_by_fix.setdefault(row.subject_iri, set()).update(
                row.sector_iris
            )
            for sector_id in row.sector_iris:
                referenced_sector_sources.setdefault(sector_id, row.source)
            prior = fixes_by_id.get(row.subject_iri)
            if prior is None or len(row.source.canonical_triples) > len(
                prior.source.canonical_triples
            ):
                fixes_by_id[row.subject_iri] = row

        sectors_by_id = {row.subject_iri: row for row in sectors}
        for row in points:
            for sector_id in row.sector_iris:
                referenced_sector_sources.setdefault(sector_id, row.source)
        for sector_id, trace in referenced_sector_sources.items():
            sectors_by_id.setdefault(
                sector_id,
                NASASectorSourceRecord(
                    source=trace,
                    subject_iri=sector_id,
                    sector_identifier=_iri_fragment(sector_id),
                ),
            )
        sectors = tuple(
            sectors_by_id[key] for key in sorted(sectors_by_id)
        )

        summary.extend(
            _publish_chunks(
                store,
                (
                    _nasa_sector_publication(
                        row,
                        asset=nasa_asset,
                        temporal_domain_id=domain,
                    )
                    for row in sectors
                ),
                chunk_size=chunk_size,
            )
        )
        summary.extend(
            _publish_chunks(
                store,
                (
                    _nasa_fix_publication(
                        row,
                        asset=nasa_asset,
                        temporal_domain_id=domain,
                    )
                    for row in fixes_by_id.values()
                ),
                chunk_size=chunk_size,
            )
        )

        routes_by_flight: dict[str, list[NASAActualRouteSourceRecord]] = {}
        for route in routes:
            for flight_iri in route.flight_iris:
                routes_by_flight.setdefault(flight_iri, []).append(route)
        points_by_route: dict[str, list[NASATrackPointSourceRecord]] = {}
        for point in points:
            for route_iri in point.route_iris:
                points_by_route.setdefault(route_iri, []).append(point)

        flight_publications: list[_PendingPublication] = []
        flight_insufficient: list[_PendingInsufficient] = []
        for flight in flights:
            try:
                flight_publications.append(
                    _nasa_flight_publication(
                        flight,
                        routes_by_flight={
                            key: tuple(value) for key, value in routes_by_flight.items()
                        },
                        points_by_route={
                            key: tuple(value) for key, value in points_by_route.items()
                        },
                        sector_ids_by_fix={
                            key: tuple(sorted(value))
                            for key, value in sector_ids_by_fix.items()
                        },
                        fix_records_by_id={
                            key: tuple(value)
                            for key, value in fix_records_by_id.items()
                        },
                        sectors_by_id=sectors_by_id,
                        profile_registry=flight_airspace_profiles,
                        asset=nasa_asset,
                        temporal_domain_id=domain,
                    )
                )
            except ValueError as exc:
                source = _record_with_domain(
                    _nasa_source_record(flight.source, asset=nasa_asset),
                    domain,
                )
                flight_insufficient.append(
                    _PendingInsufficient(
                        source_version=build_source_version(source),
                        adapter_id="flight-airspace:nasa-flight",
                        root_kind="flight",
                        reason=str(exc),
                    )
                )
        summary.extend(
            _record_insufficient_chunks(
                store,
                flight_insufficient,
                chunk_size=chunk_size,
            )
        )
        summary.extend(
            _publish_chunks(
                store,
                flight_publications,
                chunk_size=chunk_size,
            )
        )

        nasa_metadata = _metadata(config, "nasa_atmonto_instances")
        if nasa_metadata.get("include_public_sample_layers") is True:
            configured_date = nasa_metadata.get("sample_date", "2014-07-15")
            sample_date = _scope_date(
                configured_date,
                field="nasa_atmonto_instances.sample_date",
            )
            configured_airports = nasa_metadata.get(
                "weather_aspm_airport_codes",
                ["KJFK", "KEWR", "KLGA"],
            )
            if not (
                isinstance(configured_airports, list)
                and configured_airports
                and all(
                    isinstance(value, str) and value.strip()
                    for value in configured_airports
                )
            ):
                raise ValueError(
                    "nasa_atmonto_instances.weather_aspm_airport_codes "
                    "must be a non-empty list"
                )
            sample_records = iter_atmonto_public_sample_records(
                _asset_path(
                    nasa_asset,
                    source_root=source_root,
                    project_root=project_root,
                ),
                sample_date=sample_date,
                airport_codes={value.strip().upper() for value in configured_airports},
            )

            def public_sample_publications() -> Iterator[_PendingPublication]:
                for sample_record in sample_records:
                    if isinstance(sample_record, ATMONTHistoricalWeatherSourceRecord):
                        yield _atmonto_weather_publication(
                            sample_record,
                            asset=nasa_asset,
                            temporal_domain_id=domain,
                        )
                    elif isinstance(sample_record, ATMONTOTAFSourceRecord):
                        yield _atmonto_taf_publication(
                            sample_record,
                            asset=nasa_asset,
                            temporal_domain_id=domain,
                        )
                    elif isinstance(sample_record, ATMONTOAirportDataSourceRecord):
                        yield _atmonto_airport_data_publication(
                            sample_record,
                            asset=nasa_asset,
                            temporal_domain_id=domain,
                        )
                    else:
                        yield _atmonto_tmi_publication(
                            sample_record,
                            asset=nasa_asset,
                            temporal_domain_id=domain,
                        )

            summary.extend(
                _publish_chunks(
                    store,
                    public_sample_publications(),
                    chunk_size=chunk_size,
                )
            )

    nasr_asset = assets_by_key.get("nasr_airspace_zip")
    if nasr_asset is not None:
        domain = _required_domain(config, "nasr_airspace")
        nasr_rows = iter_nasr_airspace_records(
            _asset_path(
                nasr_asset,
                source_root=source_root,
                project_root=project_root,
            )
        )
        references: list[_PendingPublication] = []
        assignments: list[NASRAirportARTCCAssignmentSourceRecord] = []
        airport_publications: dict[str, str] = {}
        artcc_publications: dict[str, str] = {}
        for record in nasr_rows:
            if isinstance(record, NASRAirportSourceRecord):
                pending = _nasr_airport_publication(
                    record,
                    asset=nasr_asset,
                    temporal_domain_id=domain,
                )
                references.append(pending)
                airport_publications[record.airport_code] = (
                    pending.materialization.publication.publication.publication_id
                )
            elif isinstance(record, NASRARTCCSourceRecord):
                pending = _nasr_artcc_publication(
                    record,
                    asset=nasr_asset,
                    temporal_domain_id=domain,
                )
                references.append(pending)
                artcc_publications[record.artcc_code] = (
                    pending.materialization.publication.publication.publication_id
                )
            else:
                assignments.append(record)
        summary.extend(
            _publish_chunks(store, references, chunk_size=chunk_size)
        )
        assignment_publications: list[_PendingPublication] = []
        for record in assignments:
            airport_publication_id = airport_publications.get(record.airport_code)
            artcc_publication_id = artcc_publications.get(record.artcc_code)
            if airport_publication_id is None or artcc_publication_id is None:
                source = _nasr_source_record(
                    record.source,
                    asset=nasr_asset,
                    logical_time=record.effective_start,
                )
                summary.add(
                    _record_insufficient(
                        store,
                        source=source,
                        temporal_domain_id=domain,
                        adapter_id=(
                            "flight-airspace:nasr-assignment:"
                            f"{record.assignment_role}:{record.artcc_code}"
                        ),
                        root_kind="airport_artcc_assignment",
                        reason="referenced airport or ARTCC publication is unavailable",
                    )
                )
                continue
            assignment_publications.append(
                _nasr_assignment_publication(
                    record,
                    asset=nasr_asset,
                    temporal_domain_id=domain,
                    airport_publication_id=airport_publication_id,
                    artcc_publication_id=artcc_publication_id,
                )
            )
        summary.extend(
            _publish_chunks(
                store,
                assignment_publications,
                chunk_size=chunk_size,
            )
        )

    return summary.build(asset_count=len(assets))


ingest_flight_airspace_sources = run_flight_airspace_ingestion


__all__ = [
    "FlightAirspaceIngestionSummary",
    "FlightAirspaceRootResult",
    "ingest_flight_airspace_sources",
    "run_flight_airspace_ingestion",
]
