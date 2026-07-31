"""Validated artifacts for deterministic weather and public observation context."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from aviation_agentic_ai.agent_system.bts_observations import (
    build_bts_public_observation_summaries,
)
from aviation_agentic_ai.agent_system.contracts import (
    BTSObservationBundle,
    BTSPublicObservationBundle,
    BTSPublicObservationSummary,
    TMIEventContext,
    FactTraceRow,
    ObservationDerivation,
    ObservationFactTrace,
    SourceFamily,
    SourceRecord,
    SourceSnapshotRegistry,
    WeatherContextAssociation,
    WeatherContextBundle,
    WeatherFactTrace,
)
from aviation_agentic_ai.agent_system.construction_contracts import EventEvidenceIntegrationStatus
from aviation_agentic_ai.agent_system.ingestion_package import (
    build_event_ingestion_package,
)
from aviation_agentic_ai.agent_system.materialize import (
    _absolute_event_iri,
    run_formal_publication_kernel,
)
from aviation_agentic_ai.agent_system.public_observations import (
    build_bts_observation_facts,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    build_source_version,
    build_source_snapshot_registry,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    EventWeatherAssociation,
    PublicObservationRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.agent_system.weather_context import (
    build_weather_context,
)
from aviation_agentic_ai.agent_system.weather_context_validation import (
    validate_weather_context_bundle,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.cross_source.contracts import CanonicalEntity
from aviation_agentic_ai.cross_source.identifiers import stable_id


_SIGNATURE_RE = re.compile(r"(?m)^SIGNATURE:\s*\n(?P<stamp>\d{2}/\d{2}/\d{2} \d{2}:\d{2})\s*$")
_SIGNATURE_FIELD_RE = re.compile(r"(?m)^SIGNATURE:")
_ATM_START = "https://data.nasa.gov/ontologies/atmonto/ATM#effectiveStartTime"
_ATM_END = "https://data.nasa.gov/ontologies/atmonto/ATM#effectiveEndTime"
_T = TypeVar("_T", bound=BaseModel)


def parse_advisory_signature(content: str) -> datetime | None:
    """Parse the exact ATCSCC ``SIGNATURE`` field as a UTC decision clock."""

    match = _SIGNATURE_RE.search(content)
    if match is None:
        if _SIGNATURE_FIELD_RE.search(content):
            raise ValueError("malformed SIGNATURE field")
        return None
    try:
        parsed = datetime.strptime(match.group("stamp"), "%y/%m/%d %H:%M")
    except ValueError as exc:
        raise ValueError("malformed SIGNATURE field") from exc
    return parsed.replace(tzinfo=UTC)


def _parse_accepted_datetime(facts: list[Any], predicate_iri: str) -> datetime:
    values = [
        fact.object_value
        for fact in facts
        if fact.predicate_iri == predicate_iri and fact.object_kind == "literal"
    ]
    if len(values) != 1:
        raise ValueError(f"accepted core facts require exactly one {predicate_iri}")
    parsed = datetime.fromisoformat(values[0].replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("accepted operational period must be timezone-aware")
    return parsed.astimezone(UTC)


def _resolve_facility(ctx: Any, state: dict[str, Any]) -> CanonicalEntity:
    result = state.get("facility_authority_result")
    card = getattr(result, "evidence_card", None)
    status = getattr(getattr(card, "status", None), "value", None)
    if status != "resolved" or card is None:
        raise LookupError("canonical facility was not resolved")
    refs = sorted(set(card.canonical_refs))
    if len(refs) != 1:
        raise LookupError("canonical facility resolution is not unique")
    matches = [
        candidate
        for candidate in ctx.facility_candidates
        if getattr(candidate, "entity_id", None) == refs[0]
    ]
    if len(matches) != 1:
        raise LookupError("canonical facility is absent from accepted candidates")
    return matches[0]


def _build_event(ctx: Any, state: dict[str, Any]) -> TMIEventContext:
    validation = state.get("validation")
    if validation is None or not validation.publishable:
        raise LookupError("core event is not publishable")
    issued_at = parse_advisory_signature(ctx.advisory.content)
    if issued_at is None:
        raise LookupError("advisory SIGNATURE is missing")
    start = _parse_accepted_datetime(validation.accepted, _ATM_START)
    end = _parse_accepted_datetime(validation.accepted, _ATM_END)
    event_uri = str(state.get("event_uri") or "")
    if not event_uri:
        raise LookupError("accepted event ID is missing")
    return TMIEventContext(
        run_id=ctx.run_id,
        event_id=_absolute_event_iri(event_uri),
        advisory_source_id=ctx.advisory.source_id,
        advisory_issued_at=issued_at,
        operational_start=start,
        operational_end=end,
    )


def _validate_public_observations(
    bundle: BTSPublicObservationBundle,
    *,
    event: TMIEventContext,
    facility: CanonicalEntity,
    registry: SourceSnapshotRegistry,
) -> None:
    if bundle.status != "ok":
        if bundle.summaries:
            raise ValueError("non-ok BTS bundle contains summaries")
        return
    identifiers = [summary.summary_id for summary in bundle.summaries]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate BTS public observation summary ID")
    phases = [summary.phase for summary in bundle.summaries]
    if (
        len(phases) != 3
        or len(phases) != len(set(phases))
        or set(phases)
        != {
            "baseline",
            "active",
            "recovery",
        }
    ):
        raise ValueError("BTS public observation bundle requires exactly one summary per phase")
    expected_windows = {
        "baseline": (
            event.operational_start - timedelta(hours=2),
            event.operational_start,
        ),
        "active": (event.operational_start, event.operational_end),
        "recovery": (
            event.operational_end,
            event.operational_end + timedelta(hours=6),
        ),
    }
    for summary in bundle.summaries:
        clocks = (summary.window_start, summary.window_end)
        if any(clock.tzinfo is None or clock.utcoffset() is None for clock in clocks):
            raise ValueError("BTS public observation windows must be timezone-aware")
        expected_start, expected_end = expected_windows[summary.phase]
        if summary.window_start.astimezone(UTC) != expected_start.astimezone(
            UTC
        ) or summary.window_end.astimezone(UTC) != expected_end.astimezone(UTC):
            raise ValueError("BTS public observation window mismatch")
        snapshot = registry.get(summary.source_id)
        if snapshot is None or snapshot.family != SourceFamily.BTS_ON_TIME:
            raise ValueError("BTS public observation source is not registered")
        if (
            summary.run_id != event.run_id
            or summary.event_id != event.event_id
            or summary.facility_id != facility.entity_id
            or summary.source_snapshot_sha256 != snapshot.content_sha256
            or summary.causal_claim is not False
        ):
            raise ValueError("BTS public observation binding mismatch")


def _write_typed_jsonl(
    path: Path,
    rows: list[_T],
    *,
    id_field: str,
) -> Path:
    identifiers = [str(getattr(row, id_field)) for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"duplicate {id_field}")
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda row: str(getattr(row, id_field)))
    path.write_text(
        "".join(row.model_dump_json() + "\n" for row in ordered),
        encoding="utf-8",
    )
    return path


def _read_typed_jsonl(path: str | Path, model: type[_T], *, id_field: str) -> list[_T]:
    rows: list[_T] = []
    for line_number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(),
        1,
    ):
        if not line:
            continue
        try:
            rows.append(model.model_validate_json(line))
        except Exception as exc:
            raise ValueError(f"invalid {path} row at line {line_number}") from exc
    identifiers = [str(getattr(row, id_field)) for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"duplicate {id_field}")
    return rows


def read_context_associations(path: str | Path) -> list[WeatherContextAssociation]:
    return _read_typed_jsonl(
        path,
        WeatherContextAssociation,
        id_field="association_id",
    )


def read_bts_observation_summaries(path: str | Path) -> list[BTSPublicObservationSummary]:
    return _read_typed_jsonl(path, BTSPublicObservationSummary, id_field="summary_id")


def read_weather_fact_traces(path: str | Path) -> list[WeatherFactTrace]:
    return _read_typed_jsonl(path, WeatherFactTrace, id_field="fact_id")


def read_fact_traces(path: str | Path) -> list[FactTraceRow]:
    """Read the Formal Graph Kernel's source-text audit rows."""

    return _read_typed_jsonl(path, FactTraceRow, id_field="fact_id")


def write_observation_derivations(
    output_dir: str | Path,
    rows: list[ObservationDerivation],
) -> Path:
    """Write the canonical derivation audit bridge."""

    return _write_typed_jsonl(
        Path(output_dir) / "observation_derivations.jsonl",
        rows,
        id_field="derivation_id",
    )


def read_observation_derivations(
    path: str | Path,
) -> list[ObservationDerivation]:
    """Read a strict, duplicate-free derivation artifact."""

    return _read_typed_jsonl(
        path,
        ObservationDerivation,
        id_field="derivation_id",
    )


def write_observation_fact_traces(
    output_dir: str | Path,
    rows: list[ObservationFactTrace],
) -> Path:
    """Write canonical typed observation fact provenance."""

    return _write_typed_jsonl(
        Path(output_dir) / "observation_fact_trace.jsonl",
        rows,
        id_field="fact_id",
    )


def read_observation_fact_traces(
    path: str | Path,
) -> list[ObservationFactTrace]:
    """Read a strict, duplicate-free observation fact trace artifact."""

    return _read_typed_jsonl(
        path,
        ObservationFactTrace,
        id_field="fact_id",
    )


def _artifact_metadata(
    path: Path,
    *,
    status: str,
    failure_reason: str = "",
) -> dict[str, Any]:
    count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line)
    metadata: dict[str, Any] = {
        "path": path.name,
        "count": count,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "status": status,
    }
    if status == "blocked":
        metadata["failure_reason"] = failure_reason
    return metadata


def _empty_weather(status: str, reason: str) -> WeatherContextBundle:
    return WeatherContextBundle(status=status, failure_reason=reason)


def _empty_public_observations(status: str, reason: str) -> BTSPublicObservationBundle:
    return BTSPublicObservationBundle(status=status, failure_reason=reason)


def _empty_observations(status: str, reason: str) -> BTSObservationBundle:
    return BTSObservationBundle(status=status, failure_reason=reason)


def _formal_layer_metadata(
    profile_registry: Any,
    *,
    layer: str,
    status: str,
    formal_fact_count: int,
    failure_reason: str = "",
) -> dict[str, Any]:
    profile = next(profile for profile in profile_registry.profiles if profile.ref.layer == layer)
    metadata: dict[str, Any] = {
        "status": status,
        "profile_id": profile.ref.profile_id,
        "profile_checksum": profile.ref.profile_checksum,
        "formal_fact_count": formal_fact_count,
    }
    if status == "blocked":
        metadata["failure_reason"] = failure_reason
    return metadata


def _public_observation_publication(
    bundle: BTSObservationBundle,
    *,
    profile_registry: Any,
    snapshot_registry: SourceSnapshotRegistry,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {"status": bundle.status}
    if bundle.status == "blocked":
        metadata["failure_reason"] = bundle.failure_reason or ""
    if bundle.status != "ok":
        return metadata
    public_profile = next(
        profile
        for profile in profile_registry.profiles
        if profile.ref.layer == "public_operational_observation"
    )
    procedure = public_profile.aggregation_procedure
    if procedure is None:
        raise ValueError("public-observation profile has no aggregation procedure")
    all_facts = bundle.formal_facts
    class_counts = {
        "observation_count": "http://www.w3.org/ns/sosa/Observation",
        "result_count": "http://www.w3.org/ns/sosa/Result",
        "interval_count": "http://www.w3.org/2006/time#Interval",
        "instant_count": "http://www.w3.org/2006/time#Instant",
        "activity_count": "http://www.w3.org/ns/prov#Activity",
        "procedure_count": "http://www.w3.org/ns/sosa/Procedure",
    }
    metadata.update(
        {
            "aggregation_procedure_id": procedure.procedure_id,
            "aggregation_procedure_checksum": procedure.checksum,
            "source_ids": sorted(
                {
                    source_id
                    for fact in all_facts
                    for source_id in fact.source_ids
                }
            ),
            **{
                field: len(
                    {fact.subject_iri for fact in all_facts if fact.subject_class_iri == class_iri}
                )
                for field, class_iri in class_counts.items()
            },
        }
    )
    if len(metadata["source_ids"]) != 1:
        raise ValueError("public observations require exactly one BTS source")
    bts_source_id = metadata["source_ids"][0]
    bts_snapshot = snapshot_registry.get(bts_source_id)
    if (
        bts_snapshot is None
        or bts_snapshot.family != SourceFamily.BTS_ON_TIME
    ):
        raise ValueError("public observation BTS source binding is unavailable")
    metadata["bts_source_id"] = bts_source_id
    metadata["bts_source_snapshot_sha256"] = bts_snapshot.content_sha256
    return metadata


def _build_candidate_event(
    ctx: Any,
    state: dict[str, Any],
) -> TMIEventContext:
    """Build the pre-Kernel event candidate from deterministic parse output."""

    if state.get("validation") is not None:
        return _build_event(ctx, state)
    issued_at = parse_advisory_signature(ctx.advisory.content)
    if issued_at is None:
        raise LookupError("advisory SIGNATURE is missing")
    mentions = state.get("mentions")
    start_value = getattr(mentions, "effective_start", "") if mentions else ""
    end_value = getattr(mentions, "effective_end", "") if mentions else ""
    if not start_value or not end_value:
        raise LookupError("candidate operational period is missing")
    start = datetime.fromisoformat(start_value.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_value.replace("Z", "+00:00"))
    event_uri = str(state.get("formal_event_uri_hint") or state.get("event_uri") or "")
    if not event_uri:
        raise LookupError("candidate event ID is missing")
    return TMIEventContext(
        run_id=ctx.run_id,
        event_id=_absolute_event_iri(event_uri),
        advisory_source_id=ctx.advisory.source_id,
        advisory_issued_at=issued_at,
        operational_start=start,
        operational_end=end,
    )


def prepare_event_context(ctx: Any, state: dict[str, Any]) -> dict[str, Any]:
    """Prepare and validate optional context before event-evidence integration."""

    event_context: TMIEventContext | None = None
    facility: CanonicalEntity | None = None
    integration_result = state.get("event_evidence_integration_result")
    preflight_status = state.get("resolution_preflight_status")
    if getattr(getattr(integration_result, "proposal", None), "integration_status", None) is EventEvidenceIntegrationStatus.BLOCKED:
        common_status = "blocked"
        common_reason = state.get("integration_failure_reason") or "event evidence integration was blocked"
    elif preflight_status in {"blocked", "insufficient"}:
        common_status = preflight_status
        common_reason = state.get(
            "resolution_preflight_reason",
            "required resolution preflight did not pass",
        )
    else:
        common_status = "ok"
        common_reason = ""
        try:
            event_context = _build_candidate_event(ctx, state)
            facility = _resolve_facility(ctx, state)
        except LookupError as exc:
            common_status = "insufficient"
            common_reason = str(exc)
        except (TypeError, ValueError) as exc:
            common_status = "blocked"
            common_reason = str(exc)

    weather_bundle = _empty_weather(common_status, common_reason)
    weather_records_by_id: dict[str, SourceRecord] = {}
    if common_status == "ok" and event_context is not None and facility is not None:
        if ctx.weather_failure_reason:
            weather_bundle = _empty_weather("blocked", ctx.weather_failure_reason)
        elif not ctx.weather_sources:
            weather_bundle = _empty_weather(
                "insufficient",
                "no weather sources were provided",
            )
        else:
            try:
                weather_records_by_id = {record.source_id: record for record in ctx.weather_sources}
                transient_registry = build_source_snapshot_registry(
                    [ctx.advisory, *ctx.weather_sources]
                )
                weather_bundle = build_weather_context(
                    event_context,
                    facility,
                    transient_registry,
                )
                validate_weather_context_bundle(
                    weather_bundle,
                    event=event_context,
                    facility=facility,
                    registry=transient_registry,
                )
            except (TypeError, ValueError) as exc:
                weather_bundle = _empty_weather("blocked", str(exc))

    public_observations = _empty_public_observations(common_status, common_reason)
    bts_record: SourceRecord | None = None
    if common_status == "ok" and event_context is not None and facility is not None:
        if ctx.bts_failure_reason:
            public_observations = _empty_public_observations("blocked", ctx.bts_failure_reason)
        elif ctx.bts_source is None or not ctx.bts_rows:
            public_observations = _empty_public_observations(
                "insufficient",
                "no BTS normalized snapshot was provided",
            )
        elif ctx.bts_manifest_binding is None:
            public_observations = _empty_public_observations(
                "blocked",
                "BTS manifest binding was not provided",
            )
        else:
            try:
                bts_record = ctx.bts_source
                bts_registry = build_source_snapshot_registry([bts_record])
                bts_snapshot = bts_registry.snapshots[0]
                profile_registry = load_validation_profile_registry(
                    decision_guide=ctx.guide or load_schema_guide()
                )
                public_profile = next(
                    profile
                    for profile in profile_registry.profiles
                    if profile.ref.layer == "public_operational_observation"
                )
                if public_profile.aggregation_procedure is None:
                    raise ValueError("public-observation profile has no aggregation procedure")
                public_observations = build_bts_public_observation_summaries(
                    event_context,
                    facility,
                    ctx.bts_rows,
                    source_id=bts_record.source_id,
                    source_snapshot_sha256=bts_snapshot.content_sha256,
                    manifest_binding=ctx.bts_manifest_binding,
                    aggregation_procedure=public_profile.aggregation_procedure,
                )
                _validate_public_observations(
                    public_observations,
                    event=event_context,
                    facility=facility,
                    registry=bts_registry,
                )
            except (TypeError, ValueError) as exc:
                public_observations = _empty_public_observations("blocked", str(exc))

    profile_registry = load_validation_profile_registry(
        decision_guide=ctx.guide or load_schema_guide()
    )
    selected_records = [ctx.advisory]
    if weather_bundle.status == "ok":
        selected_records.extend(
            weather_records_by_id[source_id]
            for source_id in sorted(
                {association.source_id for association in weather_bundle.associations}
            )
        )
    if public_observations.status == "ok" and bts_record is not None:
        selected_records.append(bts_record)
    selected_registry = build_source_snapshot_registry(selected_records)
    observation_bundle = _empty_observations(
        public_observations.status,
        public_observations.failure_reason,
    )
    if (
        public_observations.status == "ok"
        and event_context is not None
        and facility is not None
    ):
        try:
            observation_bundle = build_bts_observation_facts(
                event_context,
                facility,
                public_observations,
                selected_registry,
                profile_registry,
            )
        except (TypeError, ValueError) as exc:
            observation_bundle = _empty_observations("blocked", str(exc))
    return {
        "event_context_prepared": True,
        "event_context_event": event_context,
        "weather_context": weather_bundle,
        "public_observation_context": public_observations,
        "observation_context": observation_bundle,
        "prepared_source_snapshot": selected_registry,
        "model_calls": [],
    }


def _source_version_for_snapshot(
    source_versions: tuple[SourceVersionRecord, ...],
    *,
    source_id: str,
    content_sha256: str,
) -> SourceVersionRecord:
    matches = [
        version
        for version in source_versions
        if version.source_id == source_id
        and version.content_sha256 == content_sha256
    ]
    if len(matches) != 1:
        raise ValueError(
            f"source version is not uniquely registered: {source_id}"
        )
    return matches[0]


def _event_weather_associations(
    associations: list[WeatherContextAssociation],
    *,
    source_versions: tuple[SourceVersionRecord, ...],
) -> tuple[EventWeatherAssociation, ...]:
    """Bind prepared Weather associations to immutable source versions."""

    rows = []
    for association in associations:
        version = _source_version_for_snapshot(
            source_versions,
            source_id=association.source_id,
            content_sha256=association.source_snapshot_sha256,
        )
        rows.append(
            EventWeatherAssociation(
                association_id=association.association_id,
                event_id=association.event_id,
                publication_id="pending-publication",
                report_id=association.report_id,
                facility_id=association.facility_id,
                relation_type=association.relation_type,
                selection_method=association.selection_method,
                relevant_times=dict(association.relevant_times),
                source_version_id=version.source_version_id,
                causal_claim=False,
            )
        )
    return tuple(sorted(rows, key=lambda row: row.association_id))


def _local_name(iri: str) -> str:
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _public_observation_records(
    observation_bundle: BTSObservationBundle,
    *,
    event_id: str,
    source_versions: tuple[SourceVersionRecord, ...],
) -> tuple[PublicObservationRecord, ...]:
    """Build query-ready BTS rows from Kernel-bound formal observations."""

    facts = observation_bundle.formal_facts
    facts_by_id = {fact.fact_id: fact for fact in facts}
    rows: list[PublicObservationRecord] = []
    for trace in sorted(
        observation_bundle.fact_traces,
        key=lambda row: (row.observation_id, row.metric_key, row.fact_id),
    ):
        numeric_fact = facts_by_id.get(trace.fact_id)
        if numeric_fact is None:
            raise ValueError(
                "observation trace references a missing formal fact"
            )
        observation_facts = [
            fact
            for fact in facts
            if fact.subject_iri == trace.observation_id
        ]
        result_id = next(
            (
                fact.object_value
                for fact in observation_facts
                if _local_name(fact.predicate_iri) == "hasResult"
            ),
            None,
        )
        interval_id = next(
            (
                fact.object_value
                for fact in observation_facts
                if _local_name(fact.predicate_iri) == "phenomenonTime"
            ),
            None,
        )
        related_facts = [
            fact
            for fact in facts
            if fact.subject_iri
            in {trace.observation_id, result_id, interval_id}
        ]
        phase_fact = next(
            (
                fact
                for fact in related_facts
                if fact.subject_iri == interval_id
                and fact.object_value.rsplit(":", 1)[-1]
                in {"baseline", "active", "recovery"}
            ),
            None,
        )
        if phase_fact is None:
            raise ValueError("formal observation has no phase")
        phase = phase_fact.object_value.rsplit(":", 1)[-1]
        unit_fact = next(
            (
                fact
                for fact in related_facts
                if fact.subject_iri == result_id
                and _local_name(fact.predicate_iri) == "unit"
            ),
            None,
        )
        version = _source_version_for_snapshot(
            source_versions,
            source_id=trace.source_id,
            content_sha256=trace.source_snapshot_sha256,
        )
        fact_ids = tuple(
            sorted({fact.fact_id for fact in related_facts})
        )
        rows.append(
            PublicObservationRecord(
                observation_id=stable_id(
                    "public-observation",
                    event_id,
                    trace.observation_id,
                    trace.metric_key,
                    version.source_version_id,
                ),
                event_id=event_id,
                publication_id="pending-publication",
                phase=phase,
                metric_key=trace.metric_key,
                value=trace.canonical_value,
                unit_iri=(
                    unit_fact.object_value
                    if unit_fact is not None
                    else None
                ),
                fact_ids=fact_ids,
                profile_id=numeric_fact.validation_profile.profile_id,
                profile_checksum=(
                    numeric_fact.validation_profile.profile_checksum
                ),
                source_version_id=version.source_version_id,
            )
        )
    return tuple(sorted(rows, key=lambda row: row.observation_id))


def integrate_event_context(ctx: Any, state: dict[str, Any]) -> dict[str, Any]:
    """Build one write-free, transaction-ready event publication package."""

    prepared = (
        state
        if state.get("event_context_prepared")
        else {**state, **prepare_event_context(ctx, state)}
    )
    event_context = prepared.get("event_context_event")
    weather_bundle = prepared["weather_context"]
    public_observations = prepared["public_observation_context"]
    observation_bundle = prepared["observation_context"]
    weather_records_by_id = {record.source_id: record for record in ctx.weather_sources}
    bts_record = ctx.bts_source

    validation = state.get("validation")
    common_status = "ok"
    common_reason = ""
    if validation is None:
        preflight_status = state.get("resolution_preflight_status")
        integration_result = state.get("event_evidence_integration_result")
        integration_status = getattr(
            getattr(integration_result, "proposal", None), "integration_status", None
        )
        if integration_status is EventEvidenceIntegrationStatus.BLOCKED:
            common_status = "blocked"
            common_reason = state.get("integration_failure_reason") or "event evidence integration was blocked"
        elif integration_status is EventEvidenceIntegrationStatus.INSUFFICIENT:
            common_status = "insufficient"
            common_reason = (
                state.get("integration_failure_reason")
                or "event evidence integration has insufficient required evidence"
            )
        elif preflight_status in {"blocked", "insufficient"}:
            common_status = preflight_status
            common_reason = state.get(
                "resolution_preflight_reason",
                "required resolution preflight did not pass",
            )
        else:
            common_status = "blocked"
            common_reason = "core event is not publishable"
    elif not validation.publishable:
        common_status = "blocked"
        common_reason = "core event is not publishable"
    elif event_context is None:
        common_status = "insufficient"
        common_reason = (
            "required event context could not be reconstructed"
        )
    else:
        try:
            accepted_event = _build_event(ctx, state)
        except (LookupError, TypeError, ValueError) as exc:
            accepted_event = None
            common_status = "blocked"
            common_reason = str(exc)
        if accepted_event != event_context:
            common_status = "blocked"
            common_reason = (
                "prepared TMI event context differs from Formal Graph Kernel accepted event"
            )
    if common_status == "blocked":
        weather_bundle = _empty_weather("blocked", common_reason)
        public_observations = _empty_public_observations("blocked", common_reason)
        observation_bundle = _empty_observations("blocked", common_reason)
    elif weather_bundle.status == "blocked":
        common_status = "blocked"
        common_reason = weather_bundle.failure_reason
    elif observation_bundle.status == "blocked":
        common_status = "blocked"
        common_reason = observation_bundle.failure_reason or ""

    authority_registry = state.get("authority_source_records")
    authority_status = getattr(
        getattr(authority_registry, "status", None),
        "value",
        getattr(authority_registry, "status", "ok"),
    )
    authority_records = (
        list(getattr(authority_registry, "records", ())) if authority_status == "ok" else []
    )
    persisted_records = [ctx.advisory, *authority_records]
    if weather_bundle.status == "ok":
        selected_source_ids = sorted(
            {association.source_id for association in weather_bundle.associations}
        )
        persisted_records.extend(
            weather_records_by_id[source_id] for source_id in selected_source_ids
        )
    if public_observations.status == "ok" and bts_record is not None:
        persisted_records.append(bts_record)
    persisted_registry = build_source_snapshot_registry(persisted_records)
    source_versions = tuple(
        sorted(
            (build_source_version(record) for record in persisted_records),
            key=lambda row: row.source_version_id,
        )
    )

    profile_registry = load_validation_profile_registry(
        decision_guide=ctx.guide or load_schema_guide()
    )

    associations = weather_bundle.associations if weather_bundle.status == "ok" else []
    traces = weather_bundle.fact_traces if weather_bundle.status == "ok" else []
    observation_fact_traces = (
        observation_bundle.fact_traces if observation_bundle.status == "ok" else []
    )
    direct_traces = tuple(state.get("direct_fact_traces") or ())
    profile_gaps = tuple(state.get("profile_gap_rows") or ())
    formal_publication = None
    ingestion_package = None
    if (
        validation is not None
        and validation.publishable
        and common_status == "ok"
    ):
        formal_facts = list(validation.accepted)
        if weather_bundle.status == "ok":
            formal_facts.extend(weather_bundle.formal_facts)
        if observation_bundle.status == "ok":
            formal_facts.extend(observation_bundle.formal_facts)
        formal_publication = run_formal_publication_kernel(
            facts=formal_facts,
            profile_registry=profile_registry,
            source_snapshot=persisted_registry,
            fact_traces=list(direct_traces),
            weather_fact_traces=traces,
            observation_fact_traces=observation_fact_traces,
        )
        event_weather = _event_weather_associations(
            associations,
            source_versions=source_versions,
        )
        public_observation_rows = _public_observation_records(
            observation_bundle,
            event_id=event_context.event_id,
            source_versions=source_versions,
        ) if observation_bundle.status == "ok" else ()
        advisory_source_version = next(
            version
            for version in source_versions
            if version.source_id == ctx.advisory.source_id
        )
        ingestion_package = build_event_ingestion_package(
            publication=formal_publication,
            event_context=event_context,
            advisory_source_version_id=(
                advisory_source_version.source_version_id
            ),
            source_versions=source_versions,
            direct_fact_traces=direct_traces,
            weather_fact_traces=tuple(traces),
            observation_fact_traces=tuple(observation_fact_traces),
            profile_gaps=profile_gaps,
            weather_associations=event_weather,
            public_observations=public_observation_rows,
        )

    decision_status = (
        "ok"
        if (
            validation is not None
            and validation.publishable
            and common_status == "ok"
        )
        else common_status
    )
    formal_layers = {
        "decision": _formal_layer_metadata(
            profile_registry,
            layer="decision",
            status=decision_status,
            formal_fact_count=(
                len(validation.accepted) if validation is not None and validation.publishable else 0
            ),
            failure_reason=common_reason,
        ),
        "weather": _formal_layer_metadata(
            profile_registry,
            layer="weather",
            status=weather_bundle.status,
            formal_fact_count=(
                len(weather_bundle.formal_facts) if weather_bundle.status == "ok" else 0
            ),
            failure_reason=weather_bundle.failure_reason,
        ),
        "public_operational_observation": _formal_layer_metadata(
            profile_registry,
            layer="public_operational_observation",
            status=observation_bundle.status,
            formal_fact_count=(
                len(observation_bundle.formal_facts)
                if observation_bundle.status == "ok"
                else 0
            ),
            failure_reason=observation_bundle.failure_reason or "",
        ),
    }
    return {
        "event_context_event": event_context,
        "weather_context": weather_bundle,
        "public_observation_context": public_observations,
        "observation_context": observation_bundle,
        "formal_layers": formal_layers,
        "public_observation_publication": _public_observation_publication(
            observation_bundle,
            profile_registry=profile_registry,
            snapshot_registry=persisted_registry,
        ),
        "source_snapshot": persisted_registry,
        "source_versions": source_versions,
        "formal_publication": formal_publication,
        "ingestion_package": ingestion_package,
        "publication_status": common_status,
        "publication_failure_reason": common_reason,
        "model_calls": [],
    }
