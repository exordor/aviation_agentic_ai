"""Deterministic formalization of checksum-bound BTS public observations."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import (
    BTSObservationBundle,
    BTSOnTimeRow,
    BTSPublicObservationBundle,
    BTSPublicObservationSummary,
    TMIEventContext,
    ObservationDerivation,
    ObservationDerivationSeed,
    ObservationFactTrace,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.bts_observations import resolve_bts_destination
from aviation_agentic_ai.agent_system.validation_profiles import (
    LoadedValidationProfile,
    ValidationProfileRegistry,
)
from aviation_agentic_ai.cross_source.contracts import CanonicalEntity, EntityType

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
XSD_DATETIME = "http://www.w3.org/2001/XMLSchema#dateTimeStamp"
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"

SOSA = "http://www.w3.org/ns/sosa/"
TIME = "http://www.w3.org/2006/time#"
PROV = "http://www.w3.org/ns/prov#"
QUDT = "http://qudt.org/schema/qudt/"
SKOS = "http://www.w3.org/2004/02/skos/core#"
DCTERMS = "http://purl.org/dc/terms/"
PUBLIC_OBSERVATION = "urn:aviation-agentic-ai:public-observation-schema:"
PHASE = "urn:aviation-agentic-ai:observation-phase:"

_PHASES = ("baseline", "active", "recovery")
_COUNT_FIELDS = {
    "scheduled_arrival_count": "scheduled-arrival-count",
    "completed_arrival_count": "completed-arrival-count",
    "cancelled_count": "cancelled-count",
    "diverted_count": "diverted-count",
    "arrival_delay_15_count": "arrival-delay-15-count",
}
_MINUTE_FIELDS = {
    "mean_arrival_delay_minutes": "mean-arrival-delay",
    "median_arrival_delay_minutes": "median-arrival-delay",
    "carrier_reported_weather_delay_minutes": "carrier-attributed-weather-delay",
    "carrier_reported_nas_delay_minutes": "carrier-attributed-nas-delay",
}
_METRIC_FIELDS = {**_COUNT_FIELDS, **_MINUTE_FIELDS}
_EXPECTED_UNIT = {
    **{key: "http://qudt.org/vocab/unit/NUM" for key in _COUNT_FIELDS},
    **{key: "http://qudt.org/vocab/unit/MIN" for key in _MINUTE_FIELDS},
}
_EXPECTED_DATATYPE = {
    **{key: "http://www.w3.org/2001/XMLSchema#integer" for key in _COUNT_FIELDS},
    **{key: "http://www.w3.org/2001/XMLSchema#decimal" for key in _MINUTE_FIELDS},
}
_REPORTING_SCOPE = (
    "BTS On-Time reporting carriers and scheduled domestic passenger operations."
)


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
    return namespace + hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _source_iri(source_id: str) -> str:
    return _stable_iri("urn:aviation-agentic-ai:source-record:", source_id)


def _canonical_datetime(value: Any) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _canonical_decimal(value: int | float | Decimal) -> Decimal:
    return Decimal(str(value))


def _fact(
    *,
    subject: str,
    subject_class: str,
    predicate: str,
    object_kind: str,
    object_value: str,
    profile: LoadedValidationProfile,
    evidence_mode: str,
    evidence_ref: str,
    object_class: str | None = None,
    datatype: str | None = None,
    source_ids: tuple[str, ...] = (),
) -> ValidatedFact:
    payload = {
        "datatype": datatype,
        "object_class": object_class,
        "object_kind": object_kind,
        "object_value": object_value,
        "predicate": predicate,
        "profile": profile.ref.model_dump(mode="json"),
        "subject": subject,
        "subject_class": subject_class,
    }
    return ValidatedFact(
        fact_id="observation-fact:" + _digest(payload),
        subject_iri=subject,
        subject_class_iri=subject_class,
        predicate_iri=predicate,
        object_kind=object_kind,
        object_value=object_value,
        object_class_iri=object_class,
        datatype_iri=datatype,
        source_ids=list(sorted(source_ids)),
        evidence_texts=[],
        validation_profile=profile.ref,
        evidence_mode=evidence_mode,
        evidence_ref=evidence_ref,
    )


def _typed_fact(
    resource: str,
    resource_class: str,
    *,
    profile: LoadedValidationProfile,
    evidence_mode: str,
    evidence_ref: str,
    source_ids: tuple[str, ...] = (),
) -> ValidatedFact:
    return _fact(
        subject=resource,
        subject_class=resource_class,
        predicate=RDF_TYPE,
        object_kind="iri",
        object_value=resource_class,
        object_class=resource_class,
        profile=profile,
        evidence_mode=evidence_mode,
        evidence_ref=evidence_ref,
        source_ids=source_ids,
    )


def _dedupe_facts(facts: list[ValidatedFact]) -> list[ValidatedFact]:
    by_id: dict[str, ValidatedFact] = {}
    for fact in facts:
        previous = by_id.setdefault(fact.fact_id, fact)
        if previous != fact:
            raise ValueError(f"conflicting duplicate observation fact: {fact.fact_id}")
    return sorted(by_id.values(), key=lambda fact: fact.fact_id)


def _public_profile(
    registry: ValidationProfileRegistry,
) -> tuple[LoadedValidationProfile, dict[str, dict[str, str]]]:
    candidates = [
        profile
        for profile in registry.profiles
        if profile.ref.layer == "public_operational_observation"
    ]
    if len(candidates) != 1:
        raise ValueError("exactly one public-observation profile is required")
    profile = candidates[0]
    path = Path(profile.source_path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != profile.ref.profile_checksum:
        raise ValueError("public-observation profile checksum mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    metrics = payload.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != set(_METRIC_FIELDS.values()):
        raise ValueError("public-observation profile has unknown or missing metrics")
    for field, local_name in _METRIC_FIELDS.items():
        descriptor = metrics.get(local_name)
        if not isinstance(descriptor, dict):
            raise ValueError(f"malformed metric definition: {local_name}")
        expected = {
            "iri": f"urn:aviation-agentic-ai:observable-property:bts:{local_name}",
            "unit": _EXPECTED_UNIT[field],
            "datatype": _EXPECTED_DATATYPE[field],
        }
        if any(descriptor.get(key) != value for key, value in expected.items()):
            raise ValueError(f"metric unit, datatype, or IRI mismatch: {local_name}")
        if not isinstance(descriptor.get("label"), str) or not descriptor["label"]:
            raise ValueError(f"metric label is missing: {local_name}")
    if payload.get("reporting_scope") != _REPORTING_SCOPE:
        raise ValueError("public-observation reporting scope mismatch")
    return profile, metrics


def _parse_snapshot_rows(snapshot: SourceSnapshot) -> dict[str, BTSOnTimeRow]:
    if snapshot.family != SourceFamily.BTS_ON_TIME:
        raise ValueError("BTS source family mismatch")
    rows: dict[str, BTSOnTimeRow] = {}
    for line_number, line in enumerate(snapshot.content.splitlines(), 1):
        if not line:
            continue
        try:
            row = BTSOnTimeRow.model_validate_json(line)
        except Exception as exc:
            raise ValueError(
                f"invalid normalized BTS snapshot row at line {line_number}"
            ) from exc
        if row.row_id in rows:
            raise ValueError("duplicate selected row ID in normalized BTS snapshot")
        rows[row.row_id] = row
    return rows


def _validate_bundle(
    event: TMIEventContext,
    facility: CanonicalEntity,
    public_observations: BTSPublicObservationBundle,
    snapshots: SourceSnapshotRegistry,
    profile: LoadedValidationProfile,
) -> list[tuple[BTSPublicObservationSummary, ObservationDerivationSeed]]:
    if facility.entity_type != EntityType.AIRPORT:
        raise ValueError("public observations require a canonical airport facility")
    if public_observations.status != "ok":
        raise ValueError(
            public_observations.failure_reason
            or f"BTS public-observation layer is {public_observations.status}"
        )
    summaries = {
        summary.phase: summary for summary in public_observations.summaries
    }
    seeds = {
        seed.summary_id for seed in public_observations.derivation_seeds
    }
    seeds_by_summary = {
        seed.summary_id: seed for seed in public_observations.derivation_seeds
    }
    if (
        set(summaries) != set(_PHASES)
        or len(public_observations.summaries) != len(_PHASES)
    ):
        raise ValueError(
            "BTS public-observation bundle requires exactly one summary per phase"
        )
    if len(seeds) != len(_PHASES):
        raise ValueError(
            "BTS public-observation bundle requires exactly one derivation seed per phase"
        )
    if profile.aggregation_procedure is None:
        raise ValueError("public-observation profile has no aggregation procedure")
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
    pairs: list[tuple[BTSPublicObservationSummary, ObservationDerivationSeed]] = []
    bts_snapshot: SourceSnapshot | None = None
    for phase in _PHASES:
        summary = summaries[phase]
        seed = seeds_by_summary.get(summary.summary_id)
        if seed is None:
            raise ValueError("summary has no matching derivation seed")
        if (
            summary.run_id != event.run_id
            or summary.event_id != event.event_id
            or summary.facility_id != facility.entity_id
        ):
            raise ValueError(
                "BTS public-observation event or facility binding mismatch"
            )
        expected_start, expected_end = expected_windows[phase]
        if (
            summary.window_start.astimezone(UTC) != expected_start.astimezone(UTC)
            or summary.window_end.astimezone(UTC) != expected_end.astimezone(UTC)
        ):
            raise ValueError("BTS public-observation phase window mismatch")
        if summary.reporting_scope != _REPORTING_SCOPE or summary.causal_claim is not False:
            raise ValueError(
                "BTS public-observation reporting scope or causal flag mismatch"
            )
        snapshot = snapshots.get(summary.source_id)
        if snapshot is None:
            raise ValueError("BTS public-observation source is not registered")
        if snapshot.family != SourceFamily.BTS_ON_TIME:
            raise ValueError("BTS public-observation source family mismatch")
        if summary.source_snapshot_sha256 != snapshot.content_sha256:
            raise ValueError("BTS public-observation source checksum mismatch")
        if bts_snapshot is not None and bts_snapshot.source_id != snapshot.source_id:
            raise ValueError("BTS phases use different sources")
        bts_snapshot = snapshot
        summary_sha = _digest(summary.model_dump(mode="json"))
        if seed.summary_sha256 != summary_sha:
            raise ValueError("stale BTS summary hash")
        if (
            seed.source_id != summary.source_id
            or seed.source_snapshot_sha256 != summary.source_snapshot_sha256
        ):
            raise ValueError("BTS derivation source mismatch")
        procedure = profile.aggregation_procedure
        if (
            seed.aggregation_procedure_id != procedure.procedure_id
            or seed.aggregation_procedure_checksum != procedure.checksum
        ):
            raise ValueError("BTS aggregation procedure mismatch")
        if seed.selected_row_ids != tuple(sorted(seed.selected_row_ids)):
            raise ValueError("selected row IDs are not sorted")
        if seed.selected_row_ids_sha256 != _digest(seed.selected_row_ids):
            raise ValueError("selected row digest mismatch")
        expected_seed_payload = {
            "aggregation_procedure_checksum": seed.aggregation_procedure_checksum,
            "aggregation_procedure_id": seed.aggregation_procedure_id,
            "archive_sha256": seed.archive_sha256,
            "selected_row_ids_sha256": seed.selected_row_ids_sha256,
            "source_id": seed.source_id,
            "source_snapshot_sha256": seed.source_snapshot_sha256,
            "summary_id": seed.summary_id,
            "summary_sha256": seed.summary_sha256,
        }
        expected_id = "bts-derivation:" + _digest(expected_seed_payload)[:24]
        if seed.derivation_id != expected_id:
            raise ValueError("BTS derivation ID mismatch")
        pairs.append((summary, seed))
    assert bts_snapshot is not None
    row_index = _parse_snapshot_rows(bts_snapshot)
    destination = resolve_bts_destination(facility)
    for summary, seed in pairs:
        missing = [row_id for row_id in seed.selected_row_ids if row_id not in row_index]
        if missing:
            raise ValueError(f"selected row ID is absent from pinned snapshot: {missing[0]}")
        exact_selection = tuple(
            sorted(
                row.row_id
                for row in row_index.values()
                if row.Dest == destination
                and summary.window_start.astimezone(UTC)
                <= row.scheduled_arrival_utc.astimezone(UTC)
                < summary.window_end.astimezone(UTC)
            )
        )
        if seed.selected_row_ids != exact_selection:
            raise ValueError(
                "selected row IDs do not match the canonical facility and phase window"
            )
    return pairs


def _profile_definition_facts(
    profile: LoadedValidationProfile,
    metrics: dict[str, dict[str, str]],
) -> list[ValidatedFact]:
    evidence_ref = f"{profile.ref.profile_id}:{profile.ref.profile_checksum}"
    facts: list[ValidatedFact] = []
    for unit in ("http://qudt.org/vocab/unit/NUM", "http://qudt.org/vocab/unit/MIN"):
        facts.append(
            _typed_fact(
                unit,
                QUDT + "Unit",
                profile=profile,
                evidence_mode="profile_definition",
                evidence_ref=evidence_ref,
            )
        )
    procedure = profile.aggregation_procedure
    assert procedure is not None
    facts.extend(
        [
            _typed_fact(
                procedure.procedure_id,
                SOSA + "Procedure",
                profile=profile,
                evidence_mode="profile_definition",
                evidence_ref=evidence_ref,
            ),
            _typed_fact(
                procedure.procedure_id,
                PROV + "Plan",
                profile=profile,
                evidence_mode="profile_definition",
                evidence_ref=evidence_ref,
            ),
        ]
    )
    for phase in _PHASES:
        phase_iri = PHASE + phase
        facts.extend(
            [
                _typed_fact(
                    phase_iri,
                    PUBLIC_OBSERVATION + "ObservationPhase",
                    profile=profile,
                    evidence_mode="profile_definition",
                    evidence_ref=evidence_ref,
                ),
                _typed_fact(
                    phase_iri,
                    SKOS + "Concept",
                    profile=profile,
                    evidence_mode="profile_definition",
                    evidence_ref=evidence_ref,
                ),
            ]
        )
    for local_name in sorted(metrics):
        descriptor = metrics[local_name]
        property_iri = descriptor["iri"]
        facts.extend(
            [
                _typed_fact(
                    property_iri,
                    SOSA + "ObservableProperty",
                    profile=profile,
                    evidence_mode="profile_definition",
                    evidence_ref=evidence_ref,
                ),
                _fact(
                    subject=property_iri,
                    subject_class=SOSA + "ObservableProperty",
                    predicate=SKOS + "prefLabel",
                    object_kind="literal",
                    object_value=descriptor["label"],
                    datatype=XSD_STRING,
                    profile=profile,
                    evidence_mode="profile_definition",
                    evidence_ref=evidence_ref,
                ),
                _fact(
                    subject=property_iri,
                    subject_class=SOSA + "ObservableProperty",
                    predicate=SKOS + "scopeNote",
                    object_kind="literal",
                    object_value=_REPORTING_SCOPE,
                    datatype=XSD_STRING,
                    profile=profile,
                    evidence_mode="profile_definition",
                    evidence_ref=evidence_ref,
                ),
            ]
        )
    return facts


def build_bts_observation_facts(
    event: TMIEventContext,
    canonical_facility: CanonicalEntity,
    observation_bundle: BTSPublicObservationBundle,
    snapshot_registry: SourceSnapshotRegistry,
    profile_registry: ValidationProfileRegistry,
) -> BTSObservationBundle:
    """Project an already aggregated, source-bound BTS bundle into formal facts."""

    if observation_bundle.status == "insufficient":
        return BTSObservationBundle(
            status="insufficient",
            failure_reason=(
                observation_bundle.failure_reason
                or "BTS public-observation evidence is insufficient"
            ),
        )
    try:
        profile, metrics = _public_profile(profile_registry)
        pairs = _validate_bundle(
            event,
            canonical_facility,
            observation_bundle,
            snapshot_registry,
            profile,
        )
        procedure = profile.aggregation_procedure
        assert procedure is not None

        derivations: list[ObservationDerivation] = []
        activity_facts: list[ValidatedFact] = []
        observation_facts: list[ValidatedFact] = []
        fact_traces: list[ObservationFactTrace] = []
        observation_ids: list[str] = []
        interval_ids: dict[str, str] = {}
        structural_facts = _profile_definition_facts(profile, metrics)

        for summary, seed in pairs:
            phase = summary.phase
            interval = _stable_iri(
                "urn:aviation-agentic-ai:observation-interval:",
                {
                    "end": _canonical_datetime(summary.window_end),
                    "event_id": event.event_id,
                    "facility_id": canonical_facility.entity_id,
                    "phase": phase,
                    "start": _canonical_datetime(summary.window_start),
                    "source_id": summary.source_id,
                    "source_snapshot_sha256": summary.source_snapshot_sha256,
                },
            )
            interval_ids[phase] = interval
            start_instant = _stable_iri(
                "urn:aviation-agentic-ai:time-instant:",
                {
                    "boundary": "start",
                    "event_id": event.event_id,
                    "facility_id": canonical_facility.entity_id,
                    "phase": phase,
                    "timestamp": _canonical_datetime(summary.window_start),
                },
            )
            end_instant = _stable_iri(
                "urn:aviation-agentic-ai:time-instant:",
                {
                    "boundary": "end",
                    "event_id": event.event_id,
                    "facility_id": canonical_facility.entity_id,
                    "phase": phase,
                    "timestamp": _canonical_datetime(summary.window_end),
                },
            )
            phase_structural_facts = [
                _typed_fact(
                        interval,
                        TIME + "Interval",
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref="pending",
                        source_ids=(summary.source_id,),
                ),
                _typed_fact(
                        start_instant,
                        TIME + "Instant",
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref="pending",
                        source_ids=(summary.source_id,),
                ),
                _typed_fact(
                        end_instant,
                        TIME + "Instant",
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref="pending",
                        source_ids=(summary.source_id,),
                ),
                _fact(
                        subject=interval,
                        subject_class=TIME + "Interval",
                        predicate=TIME + "hasBeginning",
                        object_kind="iri",
                        object_value=start_instant,
                        object_class=TIME + "Instant",
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref="pending",
                        source_ids=(summary.source_id,),
                ),
                _fact(
                        subject=interval,
                        subject_class=TIME + "Interval",
                        predicate=TIME + "hasEnd",
                        object_kind="iri",
                        object_value=end_instant,
                        object_class=TIME + "Instant",
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref="pending",
                        source_ids=(summary.source_id,),
                ),
                _fact(
                        subject=interval,
                        subject_class=TIME + "Interval",
                        predicate=DCTERMS + "type",
                        object_kind="iri",
                        object_value=PHASE + phase,
                        object_class=PUBLIC_OBSERVATION + "ObservationPhase",
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref="pending",
                        source_ids=(summary.source_id,),
                ),
                _fact(
                        subject=start_instant,
                        subject_class=TIME + "Instant",
                        predicate=TIME + "inXSDDateTimeStamp",
                        object_kind="literal",
                        object_value=_canonical_datetime(summary.window_start),
                        datatype=XSD_DATETIME,
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref="pending",
                        source_ids=(summary.source_id,),
                ),
                _fact(
                        subject=end_instant,
                        subject_class=TIME + "Instant",
                        predicate=TIME + "inXSDDateTimeStamp",
                        object_kind="literal",
                        object_value=_canonical_datetime(summary.window_end),
                        datatype=XSD_DATETIME,
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref="pending",
                        source_ids=(summary.source_id,),
                ),
            ]
            activity = _stable_iri(
                "urn:aviation-agentic-ai:observation-activity:",
                {
                    "event_id": event.event_id,
                    "facility_id": canonical_facility.entity_id,
                    "phase": phase,
                    "procedure_checksum": procedure.checksum,
                    "source_id": summary.source_id,
                    "source_snapshot_sha256": summary.source_snapshot_sha256,
                },
            )
            derivation = ObservationDerivation(
                **seed.model_dump(),
                activity_iri=activity,
            )
            derivations.append(derivation)
            phase_trace_ids: list[str] = []
            for metric_key, local_name in _METRIC_FIELDS.items():
                raw_value = getattr(summary, metric_key)
                if raw_value is None:
                    continue
                canonical_value = (
                    int(raw_value)
                    if metric_key in _COUNT_FIELDS
                    else _canonical_decimal(raw_value)
                )
                property_iri = metrics[local_name]["iri"]
                observation = _stable_iri(
                    "urn:aviation-agentic-ai:observation:",
                    {
                        "event_id": event.event_id,
                        "facility_id": canonical_facility.entity_id,
                        "metric": property_iri,
                        "phase": phase,
                        "procedure_checksum": procedure.checksum,
                        "source_id": summary.source_id,
                        "source_snapshot_sha256": summary.source_snapshot_sha256,
                    },
                )
                result = _stable_iri(
                    "urn:aviation-agentic-ai:observation-result:", observation
                )
                numeric_fact = _fact(
                    subject=result,
                    subject_class=QUDT + "QuantityValue",
                    predicate=QUDT + "numericValue",
                    object_kind="literal",
                    object_value=(
                        str(canonical_value)
                        if isinstance(canonical_value, int)
                        else format(canonical_value, "f")
                    ),
                    datatype=_EXPECTED_DATATYPE[metric_key],
                    profile=profile,
                    evidence_mode="deterministic_derivation",
                    evidence_ref="pending",
                    source_ids=(summary.source_id,),
                )
                numeric_fact = numeric_fact.model_copy(
                    update={"evidence_ref": numeric_fact.fact_id}
                )
                trace = ObservationFactTrace(
                    fact_id=numeric_fact.fact_id,
                    observation_id=observation,
                    derivation_id=derivation.derivation_id,
                    summary_id=summary.summary_id,
                    metric_key=metric_key,
                    canonical_value=canonical_value,
                    source_id=summary.source_id,
                    source_snapshot_sha256=summary.source_snapshot_sha256,
                    summary_sha256=seed.summary_sha256,
                    aggregation_procedure_id=procedure.procedure_id,
                    aggregation_procedure_checksum=procedure.checksum,
                )
                fact_traces.append(trace)
                phase_trace_ids.append(trace.fact_id)
                evidence_ref = trace.fact_id
                source_ids = (summary.source_id,)
                observation_facts.extend(
                    [
                        _typed_fact(
                            observation,
                            SOSA + "Observation",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _typed_fact(
                            observation,
                            PROV + "Entity",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _fact(
                            subject=observation,
                            subject_class=SOSA + "Observation",
                            predicate=SOSA + "hasFeatureOfInterest",
                            object_kind="iri",
                            object_value=canonical_facility.entity_id,
                            object_class=SOSA + "FeatureOfInterest",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _fact(
                            subject=observation,
                            subject_class=SOSA + "Observation",
                            predicate=SOSA + "observedProperty",
                            object_kind="iri",
                            object_value=property_iri,
                            object_class=SOSA + "ObservableProperty",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _fact(
                            subject=observation,
                            subject_class=SOSA + "Observation",
                            predicate=SOSA + "phenomenonTime",
                            object_kind="iri",
                            object_value=interval,
                            object_class=TIME + "Interval",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _fact(
                            subject=observation,
                            subject_class=SOSA + "Observation",
                            predicate=SOSA + "hasResult",
                            object_kind="iri",
                            object_value=result,
                            object_class=SOSA + "Result",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _fact(
                            subject=observation,
                            subject_class=SOSA + "Observation",
                            predicate=SOSA + "usedProcedure",
                            object_kind="iri",
                            object_value=procedure.procedure_id,
                            object_class=SOSA + "Procedure",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _fact(
                            subject=observation,
                            subject_class=SOSA + "Observation",
                            predicate=PROV + "wasGeneratedBy",
                            object_kind="iri",
                            object_value=activity,
                            object_class=PROV + "Activity",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _fact(
                            subject=observation,
                            subject_class=SOSA + "Observation",
                            predicate=PROV + "wasDerivedFrom",
                            object_kind="iri",
                            object_value=_source_iri(summary.source_id),
                            object_class=PROV + "Entity",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _typed_fact(
                            result,
                            SOSA + "Result",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _typed_fact(
                            result,
                            QUDT + "QuantityValue",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        numeric_fact,
                        _fact(
                            subject=result,
                            subject_class=QUDT + "QuantityValue",
                            predicate=QUDT + "unit",
                            object_kind="iri",
                            object_value=_EXPECTED_UNIT[metric_key],
                            object_class=QUDT + "Unit",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                        _fact(
                            subject=activity,
                            subject_class=PROV + "Activity",
                            predicate=PROV + "generated",
                            object_kind="iri",
                            object_value=observation,
                            object_class=SOSA + "Observation",
                            profile=profile,
                            evidence_mode="deterministic_derivation",
                            evidence_ref=evidence_ref,
                            source_ids=source_ids,
                        ),
                    ]
                )
                observation_ids.append(observation)
            if not phase_trace_ids:
                raise ValueError("BTS phase has no emitted observation trace")
            activity_evidence_ref = sorted(phase_trace_ids)[0]
            structural_facts.extend(
                fact.model_copy(update={"evidence_ref": activity_evidence_ref})
                for fact in phase_structural_facts
            )
            activity_source_ids = (summary.source_id,)
            activity_facts.extend(
                [
                    _typed_fact(
                        activity,
                        PROV + "Activity",
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref=activity_evidence_ref,
                        source_ids=activity_source_ids,
                    ),
                    _fact(
                        subject=activity,
                        subject_class=PROV + "Activity",
                        predicate=PROV + "used",
                        object_kind="iri",
                        object_value=_source_iri(summary.source_id),
                        object_class=PROV + "Entity",
                        profile=profile,
                        evidence_mode="deterministic_derivation",
                        evidence_ref=activity_evidence_ref,
                        source_ids=activity_source_ids,
                    ),
                ]
            )

        return BTSObservationBundle(
            status="ok",
            formal_facts=_dedupe_facts(
                [*structural_facts, *activity_facts, *observation_facts]
            ),
            observation_ids=tuple(sorted(set(observation_ids))),
            fact_traces=sorted(fact_traces, key=lambda trace: trace.fact_id),
            derivations=sorted(
                derivations, key=lambda derivation: derivation.derivation_id
            ),
        )
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        return BTSObservationBundle(status="blocked", failure_reason=str(exc))


__all__ = ["build_bts_observation_facts"]
