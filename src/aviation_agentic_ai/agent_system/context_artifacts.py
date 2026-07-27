"""Validated artifacts for deterministic weather and public outcome context."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from aviation_agentic_ai.agent_system.bts_outcomes import (
    build_bts_outcome_summaries,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    BTSObservationBundle,
    BTSOutcomeBundle,
    BTSOutcomeSummary,
    DecisionContextEvent,
    FactTraceRow,
    ObservationDerivation,
    ObservationFactTrace,
    ReconstructionTrace,
    SourceFamily,
    SourceRecord,
    SourceSnapshotRegistry,
    WeatherContextAssociation,
    WeatherContextBundle,
    WeatherFactTrace,
)
from aviation_agentic_ai.agent_system.materialize import (
    _absolute_event_iri,
    materialize_validated_facts,
)
from aviation_agentic_ai.agent_system.public_observations import (
    build_bts_observation_facts,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot_registry,
    write_source_snapshot_registry,
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


_SIGNATURE_RE = re.compile(
    r"(?m)^SIGNATURE:\s*\n(?P<stamp>\d{2}/\d{2}/\d{2} \d{2}:\d{2})\s*$"
)
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
    result = state.get("facility_result")
    card = getattr(result, "evidence_card", None)
    status = getattr(getattr(result, "status", None), "value", None)
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


def _build_event(ctx: Any, state: dict[str, Any]) -> DecisionContextEvent:
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
    return DecisionContextEvent(
        run_id=ctx.run_id,
        event_id=_absolute_event_iri(event_uri),
        advisory_source_id=ctx.advisory.source_id,
        advisory_issued_at=issued_at,
        operational_start=start,
        operational_end=end,
    )


def _validate_outcomes(
    bundle: BTSOutcomeBundle,
    *,
    event: DecisionContextEvent,
    facility: CanonicalEntity,
    registry: SourceSnapshotRegistry,
) -> None:
    if bundle.status != "ok":
        if bundle.summaries:
            raise ValueError("non-ok BTS bundle contains summaries")
        return
    identifiers = [summary.summary_id for summary in bundle.summaries]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate BTS outcome summary ID")
    phases = [summary.phase for summary in bundle.summaries]
    if len(phases) != 3 or len(phases) != len(set(phases)) or set(phases) != {
        "baseline",
        "active",
        "recovery",
    }:
        raise ValueError("BTS outcome bundle requires exactly one summary per phase")
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
            raise ValueError("BTS outcome windows must be timezone-aware")
        expected_start, expected_end = expected_windows[summary.phase]
        if (
            summary.window_start.astimezone(UTC) != expected_start.astimezone(UTC)
            or summary.window_end.astimezone(UTC) != expected_end.astimezone(UTC)
        ):
            raise ValueError("BTS outcome window mismatch")
        snapshot = registry.get(summary.source_id)
        if snapshot is None or snapshot.family != SourceFamily.BTS_ON_TIME:
            raise ValueError("BTS outcome source is not registered")
        if (
            summary.run_id != event.run_id
            or summary.event_id != event.event_id
            or summary.facility_id != facility.entity_id
            or summary.source_snapshot_sha256 != snapshot.content_sha256
            or summary.causal_claim is not False
        ):
            raise ValueError("BTS outcome binding mismatch")


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


def read_outcome_summaries(path: str | Path) -> list[BTSOutcomeSummary]:
    return _read_typed_jsonl(path, BTSOutcomeSummary, id_field="summary_id")


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


def write_reconstruction_trace(
    output_dir: str | Path,
    trace: ReconstructionTrace | None,
) -> Path:
    """Write the one immutable reconstruction input binding."""

    path = Path(output_dir) / "reconstruction_trace.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        trace.model_dump_json() + "\n" if trace is not None else "",
        encoding="utf-8",
    )
    return path


def read_reconstruction_trace(path: str | Path) -> ReconstructionTrace:
    """Read and strictly validate the reconstruction input binding."""

    try:
        return ReconstructionTrace.model_validate_json(
            Path(path).read_text(encoding="utf-8")
        )
    except Exception as exc:
        raise ValueError("invalid reconstruction trace JSON") from exc


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


def _empty_outcomes(status: str, reason: str) -> BTSOutcomeBundle:
    return BTSOutcomeBundle(status=status, failure_reason=reason)


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
    profile = next(
        profile for profile in profile_registry.profiles if profile.ref.layer == layer
    )
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
) -> dict[str, Any]:
    metadata: dict[str, Any] = {"status": bundle.status}
    if bundle.status == "blocked":
        metadata["failure_reason"] = bundle.failure_reason or ""
    if bundle.status != "ok" or bundle.reconstruction_trace is None:
        return metadata
    public_profile = next(
        profile
        for profile in profile_registry.profiles
        if profile.ref.layer == "public_operational_observation"
    )
    procedure = public_profile.aggregation_procedure
    if procedure is None:
        raise ValueError("public-observation profile has no aggregation procedure")
    trace = bundle.reconstruction_trace
    all_facts = [
        *bundle.case_facts,
        *bundle.activity_facts,
        *bundle.observation_facts,
    ]
    class_counts = {
        "observation_count": "http://www.w3.org/ns/sosa/Observation",
        "result_count": "http://www.w3.org/ns/sosa/Result",
        "interval_count": "http://www.w3.org/2006/time#Interval",
        "instant_count": "http://www.w3.org/2006/time#Instant",
        "activity_count": "http://www.w3.org/ns/prov#Activity",
        "procedure_count": "http://www.w3.org/ns/sosa/Procedure",
        "conceptual_case_count": (
            "urn:aviation-agentic-ai:decision-case-schema:DecisionCase"
        ),
        "reconstruction_count": (
            "urn:aviation-agentic-ai:decision-case-schema:"
            "DecisionCaseReconstruction"
        ),
    }
    metadata.update(
        {
            "aggregation_procedure_id": procedure.procedure_id,
            "aggregation_procedure_checksum": procedure.checksum,
            "source_bindings": [
                binding.model_dump(mode="json")
                for binding in trace.source_bindings
            ],
            **{
                field: len(
                    {
                        fact.subject_iri
                        for fact in all_facts
                        if fact.subject_class_iri == class_iri
                    }
                )
                for field, class_iri in class_counts.items()
            },
        }
    )
    bts_bindings = [
        binding
        for binding in trace.source_bindings
        if binding.source_family == SourceFamily.BTS_ON_TIME
    ]
    if len(bts_bindings) != 1:
        raise ValueError("reconstruction requires exactly one BTS source binding")
    metadata["bts_source_id"] = bts_bindings[0].source_id
    metadata["bts_source_snapshot_sha256"] = bts_bindings[0].snapshot_sha256
    return metadata


def _build_candidate_event(
    ctx: Any,
    state: dict[str, Any],
) -> DecisionContextEvent:
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
    event_uri = str(
        state.get("formal_event_uri_hint")
        or state.get("event_uri")
        or ""
    )
    if not event_uri:
        raise LookupError("candidate event ID is missing")
    return DecisionContextEvent(
        run_id=ctx.run_id,
        event_id=_absolute_event_iri(event_uri),
        advisory_source_id=ctx.advisory.source_id,
        advisory_issued_at=issued_at,
        operational_start=start,
        operational_end=end,
    )


def prepare_decision_context(ctx: Any, state: dict[str, Any]) -> dict[str, Any]:
    """Prepare and validate optional context in memory before Assembly."""

    decision_event: DecisionContextEvent | None = None
    facility: CanonicalEntity | None = None
    kg_result = state.get("kg_result")
    preflight_status = state.get("resolution_preflight_status")
    if (
        kg_result is not None
        and getattr(kg_result, "status", None) is AgentStatus.BLOCKED
    ):
        common_status = "blocked"
        common_reason = (
            getattr(kg_result, "failure_reason", None)
            or "knowledge graph construction was blocked"
        )
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
            decision_event = _build_candidate_event(ctx, state)
            facility = _resolve_facility(ctx, state)
        except LookupError as exc:
            common_status = "insufficient"
            common_reason = str(exc)
        except (TypeError, ValueError) as exc:
            common_status = "blocked"
            common_reason = str(exc)

    weather_bundle = _empty_weather(common_status, common_reason)
    weather_records_by_id: dict[str, SourceRecord] = {}
    if common_status == "ok" and decision_event is not None and facility is not None:
        if ctx.weather_failure_reason:
            weather_bundle = _empty_weather("blocked", ctx.weather_failure_reason)
        elif not ctx.weather_sources:
            weather_bundle = _empty_weather(
                "insufficient",
                "no weather sources were provided",
            )
        else:
            try:
                weather_records_by_id = {
                    record.source_id: record for record in ctx.weather_sources
                }
                transient_registry = build_source_snapshot_registry(
                    [ctx.advisory, *ctx.weather_sources]
                )
                weather_bundle = build_weather_context(
                    decision_event,
                    facility,
                    transient_registry,
                )
                validate_weather_context_bundle(
                    weather_bundle,
                    event=decision_event,
                    facility=facility,
                    registry=transient_registry,
                )
            except (TypeError, ValueError) as exc:
                weather_bundle = _empty_weather("blocked", str(exc))

    outcome_bundle = _empty_outcomes(common_status, common_reason)
    bts_record: SourceRecord | None = None
    if common_status == "ok" and decision_event is not None and facility is not None:
        if ctx.bts_failure_reason:
            outcome_bundle = _empty_outcomes("blocked", ctx.bts_failure_reason)
        elif ctx.bts_source is None or not ctx.bts_rows:
            outcome_bundle = _empty_outcomes(
                "insufficient",
                "no BTS normalized snapshot was provided",
            )
        elif ctx.bts_manifest_binding is None:
            outcome_bundle = _empty_outcomes(
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
                outcome_bundle = build_bts_outcome_summaries(
                    decision_event,
                    facility,
                    ctx.bts_rows,
                    source_id=bts_record.source_id,
                    source_snapshot_sha256=bts_snapshot.content_sha256,
                    manifest_binding=ctx.bts_manifest_binding,
                    aggregation_procedure=public_profile.aggregation_procedure,
                )
                _validate_outcomes(
                    outcome_bundle,
                    event=decision_event,
                    facility=facility,
                    registry=bts_registry,
                )
            except (TypeError, ValueError) as exc:
                outcome_bundle = _empty_outcomes("blocked", str(exc))

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
    if outcome_bundle.status == "ok" and bts_record is not None:
        selected_records.append(bts_record)
    selected_registry = build_source_snapshot_registry(selected_records)
    observation_bundle = _empty_observations(
        outcome_bundle.status,
        outcome_bundle.failure_reason,
    )
    if (
        outcome_bundle.status == "ok"
        and decision_event is not None
        and facility is not None
    ):
        try:
            observation_bundle = build_bts_observation_facts(
                decision_event,
                facility,
                outcome_bundle,
                selected_registry,
                profile_registry,
            )
        except (TypeError, ValueError) as exc:
            observation_bundle = _empty_observations("blocked", str(exc))
        if (
            observation_bundle.status == "ok"
            and observation_bundle.reconstruction_trace is not None
        ):
            expected_weather_ids = set(
                (
                    f"urn:aviation-agentic-ai:{report_id}"
                    for report_id in weather_bundle.selected_report_ids
                )
                if weather_bundle.status == "ok"
                else ()
            )
            published_weather_ids = {
                member
                for member in observation_bundle.reconstruction_trace.member_iris
                if member.startswith("urn:aviation-agentic-ai:weather-report:")
            }
            if expected_weather_ids != published_weather_ids:
                observation_bundle = _empty_observations(
                    "blocked",
                    (
                        "reconstruction trace weather members do not match "
                        "validated weather members"
                    ),
                )
    return {
        "decision_context_prepared": True,
        "decision_context_event": decision_event,
        "weather_context": weather_bundle,
        "outcome_context": outcome_bundle,
        "observation_context": observation_bundle,
        "prepared_source_snapshot": selected_registry,
        "model_calls": [],
    }


def integrate_decision_context(ctx: Any, state: dict[str, Any]) -> dict[str, Any]:
    """Publish prepared context after revalidating the Kernel-accepted event."""

    output_dir = Path(ctx.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    core_materialization = state.get("materialization")
    prepared = (
        state
        if state.get("decision_context_prepared")
        else {**state, **prepare_decision_context(ctx, state)}
    )
    decision_event = prepared.get("decision_context_event")
    weather_bundle = prepared["weather_context"]
    outcome_bundle = prepared["outcome_context"]
    observation_bundle = prepared["observation_context"]
    weather_records_by_id = {
        record.source_id: record for record in ctx.weather_sources
    }
    bts_record = ctx.bts_source

    validation = state.get("validation")
    common_status = "ok"
    common_reason = ""
    if validation is None:
        preflight_status = state.get("resolution_preflight_status")
        kg_result = state.get("kg_result")
        if (
            kg_result is not None
            and getattr(kg_result, "status", None) is AgentStatus.BLOCKED
        ):
            common_status = "blocked"
            common_reason = (
                getattr(kg_result, "failure_reason", None)
                or "knowledge graph construction was blocked"
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
    elif decision_event is not None:
        try:
            accepted_event = _build_event(ctx, state)
        except (LookupError, TypeError, ValueError) as exc:
            accepted_event = None
            common_status = "blocked"
            common_reason = str(exc)
        if accepted_event != decision_event:
            common_status = "blocked"
            common_reason = (
                "prepared decision context event differs from "
                "Formal Graph Kernel accepted event"
            )
    if common_status == "blocked":
        weather_bundle = _empty_weather("blocked", common_reason)
        outcome_bundle = _empty_outcomes("blocked", common_reason)
        observation_bundle = _empty_observations("blocked", common_reason)

    authority_registry = state.get("authority_source_records")
    authority_status = getattr(
        getattr(authority_registry, "status", None),
        "value",
        getattr(authority_registry, "status", "ok"),
    )
    authority_reason = (
        getattr(authority_registry, "reason_code", None)
        or getattr(authority_registry, "error_id", None)
        or ""
    )
    authority_records = (
        list(getattr(authority_registry, "records", ()))
        if authority_status == "ok"
        else []
    )
    persisted_records = [ctx.advisory, *authority_records]
    if weather_bundle.status == "ok":
        selected_source_ids = sorted(
            {association.source_id for association in weather_bundle.associations}
        )
        persisted_records.extend(
            weather_records_by_id[source_id] for source_id in selected_source_ids
        )
    if outcome_bundle.status == "ok" and bts_record is not None:
        persisted_records.append(bts_record)
    persisted_registry = build_source_snapshot_registry(persisted_records)
    snapshots_path = write_source_snapshot_registry(
        persisted_registry,
        output_dir,
    )

    profile_registry = load_validation_profile_registry(
        decision_guide=ctx.guide or load_schema_guide()
    )

    materialization = core_materialization

    associations = (
        weather_bundle.associations if weather_bundle.status == "ok" else []
    )
    traces = weather_bundle.fact_traces if weather_bundle.status == "ok" else []
    summaries = outcome_bundle.summaries if outcome_bundle.status == "ok" else []
    association_path = _write_typed_jsonl(
        output_dir / "context_associations.jsonl",
        associations,
        id_field="association_id",
    )
    outcome_path = _write_typed_jsonl(
        output_dir / "outcome_summaries.jsonl",
        summaries,
        id_field="summary_id",
    )
    trace_path = _write_typed_jsonl(
        output_dir / "weather_fact_trace.jsonl",
        traces,
        id_field="fact_id",
    )
    observation_derivations = (
        observation_bundle.derivations if observation_bundle.status == "ok" else []
    )
    observation_fact_traces = (
        observation_bundle.fact_traces if observation_bundle.status == "ok" else []
    )
    reconstruction_trace = (
        observation_bundle.reconstruction_trace
        if observation_bundle.status == "ok"
        else None
    )
    derivation_path = write_observation_derivations(
        output_dir,
        observation_derivations,
    )
    observation_trace_path = write_observation_fact_traces(
        output_dir,
        observation_fact_traces,
    )
    reconstruction_path = write_reconstruction_trace(
        output_dir,
        reconstruction_trace,
    )

    validation = state.get("validation")
    fact_trace_path = output_dir / "fact_trace.jsonl"
    if (
        validation is not None
        and validation.publishable
        and fact_trace_path.exists()
    ):
        direct_traces = read_fact_traces(fact_trace_path)
        formal_facts = list(validation.accepted)
        if weather_bundle.status == "ok":
            formal_facts.extend(weather_bundle.formal_facts)
        if observation_bundle.status == "ok":
            formal_facts.extend(
                [
                    *observation_bundle.case_facts,
                    *observation_bundle.activity_facts,
                    *observation_bundle.observation_facts,
                ]
            )
        try:
            materialization = materialize_validated_facts(
                facts=formal_facts,
                profile_registry=profile_registry,
                source_snapshot=persisted_registry,
                fact_traces=direct_traces,
                weather_fact_traces=traces,
                observation_fact_traces=observation_fact_traces,
                reconstruction_trace=reconstruction_trace,
                output_dir=output_dir,
            )
        except ValueError as exc:
            if observation_bundle.status != "ok":
                raise
            observation_bundle = _empty_observations("blocked", str(exc))
            write_observation_derivations(output_dir, [])
            write_observation_fact_traces(output_dir, [])
            write_reconstruction_trace(output_dir, None)
            formal_facts = list(validation.accepted)
            if weather_bundle.status == "ok":
                formal_facts.extend(weather_bundle.formal_facts)
            materialization = materialize_validated_facts(
                facts=formal_facts,
                profile_registry=profile_registry,
                source_snapshot=persisted_registry,
                fact_traces=direct_traces,
                weather_fact_traces=traces,
                output_dir=output_dir,
            )

    context_artifacts = {
        "source_snapshots": _artifact_metadata(
            snapshots_path,
            status=authority_status,
            failure_reason=authority_reason,
        ),
        "context_associations": _artifact_metadata(
            association_path,
            status=weather_bundle.status,
            failure_reason=weather_bundle.failure_reason,
        ),
        "outcome_summaries": _artifact_metadata(
            outcome_path,
            status=outcome_bundle.status,
            failure_reason=outcome_bundle.failure_reason,
        ),
        "weather_fact_trace": _artifact_metadata(
            trace_path,
            status=weather_bundle.status,
            failure_reason=weather_bundle.failure_reason,
        ),
        "observation_derivations": _artifact_metadata(
            derivation_path,
            status=observation_bundle.status,
            failure_reason=observation_bundle.failure_reason or "",
        ),
        "observation_fact_trace": _artifact_metadata(
            observation_trace_path,
            status=observation_bundle.status,
            failure_reason=observation_bundle.failure_reason or "",
        ),
        "reconstruction_trace": _artifact_metadata(
            reconstruction_path,
            status=observation_bundle.status,
            failure_reason=observation_bundle.failure_reason or "",
        ),
    }
    decision_status = (
        "ok"
        if validation is not None and validation.publishable
        else common_status
    )
    formal_layers = {
        "decision": _formal_layer_metadata(
            profile_registry,
            layer="decision",
            status=decision_status,
            formal_fact_count=(
                len(validation.accepted)
                if validation is not None and validation.publishable
                else 0
            ),
            failure_reason=common_reason,
        ),
        "weather": _formal_layer_metadata(
            profile_registry,
            layer="weather",
            status=weather_bundle.status,
            formal_fact_count=(
                len(weather_bundle.formal_facts)
                if weather_bundle.status == "ok"
                else 0
            ),
            failure_reason=weather_bundle.failure_reason,
        ),
        "public_operational_observation": _formal_layer_metadata(
            profile_registry,
            layer="public_operational_observation",
            status=observation_bundle.status,
            formal_fact_count=(
                len(observation_bundle.case_facts)
                + len(observation_bundle.activity_facts)
                + len(observation_bundle.observation_facts)
                if observation_bundle.status == "ok"
                else 0
            ),
            failure_reason=observation_bundle.failure_reason or "",
        ),
    }
    return {
        "decision_context_event": decision_event,
        "weather_context": weather_bundle,
        "outcome_context": outcome_bundle,
        "observation_context": observation_bundle,
        "context_artifacts": context_artifacts,
        "formal_layers": formal_layers,
        "public_observation_publication": _public_observation_publication(
            observation_bundle,
            profile_registry=profile_registry,
        ),
        "source_snapshot": persisted_registry,
        "materialization": materialization,
        "model_calls": [],
    }
