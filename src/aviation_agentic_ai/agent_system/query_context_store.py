"""Fail-closed read surface for optional decision-context artifacts.

The core Query Agent store deliberately does not load these artifacts.  This
module validates an optional layer only when a decision-context tool requests
it, so corruption in an optional Weather or BTS artifact cannot disable the
older core decision-record questions.
"""

from __future__ import annotations

import hashlib
import json
import re
import statistics
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Literal, TypeVar

from pydantic import BaseModel

from aviation_agentic_ai.agent_system.contracts import (
    BTSOnTimeRow,
    BTSOutcomeSummary,
    ObservationDerivation,
    ObservationFactTrace,
    OutcomeObservationRead,
    OutcomeSummaryRead,
    ReconstructionTrace,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    WeatherContextAssociation,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.runtime import RUN_MANIFEST_VERSION
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.agent_system.weather_context import (
    FORECASTING_AIRPORT,
    FORECAST_ISSUE_TIME,
    INTERVAL_END,
    INTERVAL_START,
    METAR_STRING,
    RDF_TYPE,
    TAF_STRING,
    XSD_DATETIME,
    XSD_STRING,
)
from aviation_agentic_ai.agent_system.weather_context_validation import (
    expected_weather_fact_id,
)

_METEOROLOGICAL_REPORT = (
    "https://data.nasa.gov/ontologies/atmonto/data#MeteorologicalReport"
)
_PREDICATE_IRIS = {
    "rdf:type": RDF_TYPE,
    "data:forecastingAirport": FORECASTING_AIRPORT,
    "data:metarReportString": METAR_STRING,
    "data:tafReportString": TAF_STRING,
    "data:dataIntervalStartTime": INTERVAL_START,
    "data:dataIntervalEndTime": INTERVAL_END,
    "data:forecastIssueTime": FORECAST_ISSUE_TIME,
}
_WEATHER_PREDICATES = frozenset(
    {
        "rdf:type",
        "data:forecastingAirport",
        "data:metarReportString",
        "data:tafReportString",
        "data:dataIntervalStartTime",
        "data:dataIntervalEndTime",
        "data:forecastIssueTime",
    }
)
_PHASES = ("baseline", "active", "recovery")
_BTS_REPORTING_SCOPE = (
    "BTS On-Time reporting carriers and scheduled domestic passenger operations."
)
_SOSA = "http://www.w3.org/ns/sosa/"
_TIME = "http://www.w3.org/2006/time#"
_QUDT = "http://qudt.org/schema/qudt/"
_DCTERMS = "http://purl.org/dc/terms/"
_PHASE = "urn:aviation-agentic-ai:observation-phase:"
_METRIC_FIELDS = {
    "scheduled_arrival_count": "scheduled-arrival-count",
    "completed_arrival_count": "completed-arrival-count",
    "cancelled_count": "cancelled-count",
    "diverted_count": "diverted-count",
    "arrival_delay_15_count": "arrival-delay-15-count",
    "mean_arrival_delay_minutes": "mean-arrival-delay",
    "median_arrival_delay_minutes": "median-arrival-delay",
    "carrier_reported_weather_delay_minutes": "carrier-attributed-weather-delay",
    "carrier_reported_nas_delay_minutes": "carrier-attributed-nas-delay",
}
_SIGNATURE_RE = re.compile(
    r"(?m)^SIGNATURE:\s*\n(?P<stamp>\d{2}/\d{2}/\d{2} \d{2}:\d{2})\s*$"
)
_SIGNATURE_FIELD_RE = re.compile(r"(?m)^SIGNATURE:")
_ICAO_AIRPORT_CODE = re.compile(r"[A-Z]{4}\Z")
_URN_PREFIX = "urn:aviation-agentic-ai:"
_T = TypeVar("_T", bound=BaseModel)


class QueryContextError(RuntimeError):
    """Raised when optional context cannot be safely exposed."""


@dataclass(frozen=True)
class DecisionContextRead:
    """Validated result for one event's non-causal Weather context."""

    status: Literal["ok", "insufficient"]
    associations: tuple[WeatherContextAssociation, ...] = ()
    formal_fact_rows: tuple[dict[str, Any], ...] = ()
    source_records: tuple[SourceSnapshot, ...] = ()
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Artifact:
    status: Literal["ok", "insufficient", "blocked"]
    data: bytes


@dataclass(frozen=True)
class _SourceWeatherReport:
    snapshot: SourceSnapshot
    family: SourceFamily
    station: str
    logical_time: datetime
    interval_start: datetime
    interval_end: datetime
    raw: str
    report_id: str


def _parse_datetime(value: Any, *, field: str) -> datetime:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return datetime.fromtimestamp(value, tz=UTC)
        except (OverflowError, OSError, ValueError) as exc:
            raise QueryContextError(f"invalid {field} datetime") from exc
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise QueryContextError(f"invalid {field} datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise QueryContextError(f"{field} datetime is not timezone-aware")
    return parsed.astimezone(UTC)


def _source_ids(row: dict[str, Any]) -> set[str]:
    return {
        source_id.strip()
        for source_id in str(row.get("source_document") or "").split(";")
        if source_id.strip()
    }


def _time_token(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _report_id(
    family: SourceFamily,
    station: str,
    logical_time: datetime,
    raw: str,
    source_checksum: str,
) -> str:
    raw_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return (
        f"weather-report:{family.value}:{station}:{_time_token(logical_time)}:"
        f"{raw_hash}:{source_checksum[:16]}"
    )


def _parse_advisory_issue_time(content: str) -> datetime:
    match = _SIGNATURE_RE.search(content)
    if match is None:
        if _SIGNATURE_FIELD_RE.search(content):
            raise QueryContextError("advisory SIGNATURE is malformed")
        raise QueryContextError("advisory SIGNATURE is missing")
    try:
        parsed = datetime.strptime(match.group("stamp"), "%y/%m/%d %H:%M")
    except ValueError as exc:
        raise QueryContextError("advisory SIGNATURE is malformed") from exc
    return parsed.replace(tzinfo=UTC)


def _parse_source_weather_report(
    snapshot: SourceSnapshot,
) -> _SourceWeatherReport:
    try:
        row = json.loads(snapshot.content)
    except json.JSONDecodeError as exc:
        raise QueryContextError(
            f"weather snapshot is not canonical JSON: {snapshot.source_id}"
        ) from exc
    if not isinstance(row, dict):
        raise QueryContextError(
            f"weather snapshot row is not an object: {snapshot.source_id}"
        )
    station = row.get("icaoId")
    if (
        not isinstance(station, str)
        or not _ICAO_AIRPORT_CODE.fullmatch(station)
    ):
        raise QueryContextError(
            f"weather snapshot has invalid ICAO station: {snapshot.source_id}"
        )
    if snapshot.family == SourceFamily.METAR:
        if any(
            field in row
            for field in ("issueTime", "validTimeFrom", "validTimeTo")
        ):
            raise QueryContextError(
                f"weather snapshot family does not match METAR: "
                f"{snapshot.source_id}"
            )
        raw = row.get("rawOb")
        if not isinstance(raw, str) or not raw:
            raise QueryContextError(
                f"METAR snapshot has no raw observation: {snapshot.source_id}"
            )
        observed = _parse_datetime(
            row.get("reportTime"),
            field=f"METAR reportTime for {snapshot.source_id}",
        )
        return _SourceWeatherReport(
            snapshot=snapshot,
            family=SourceFamily.METAR,
            station=station,
            logical_time=observed,
            interval_start=observed,
            interval_end=observed,
            raw=raw,
            report_id=_report_id(
                SourceFamily.METAR,
                station,
                observed,
                raw,
                snapshot.content_sha256,
            ),
        )
    if snapshot.family == SourceFamily.TAF:
        if "reportTime" in row or "rawOb" in row:
            raise QueryContextError(
                f"weather snapshot family does not match TAF: "
                f"{snapshot.source_id}"
            )
        raw = row.get("rawTAF")
        if not isinstance(raw, str) or not raw:
            raise QueryContextError(
                f"TAF snapshot has no raw forecast: {snapshot.source_id}"
            )
        issue = _parse_datetime(
            row.get("issueTime"),
            field=f"TAF issueTime for {snapshot.source_id}",
        )
        start = _parse_datetime(
            row.get("validTimeFrom"),
            field=f"TAF validTimeFrom for {snapshot.source_id}",
        )
        end = _parse_datetime(
            row.get("validTimeTo"),
            field=f"TAF validTimeTo for {snapshot.source_id}",
        )
        if end <= start:
            raise QueryContextError(
                f"TAF snapshot has an invalid interval: {snapshot.source_id}"
            )
        return _SourceWeatherReport(
            snapshot=snapshot,
            family=SourceFamily.TAF,
            station=station,
            logical_time=issue,
            interval_start=start,
            interval_end=end,
            raw=raw,
            report_id=_report_id(
                SourceFamily.TAF,
                station,
                issue,
                raw,
                snapshot.content_sha256,
            ),
        )
    raise QueryContextError(
        f"unsupported weather snapshot family: {snapshot.source_id}"
    )


def _identity_aliases(value: str) -> set[str]:
    normalized = value.strip()
    if not normalized:
        return set()
    if normalized.startswith(_URN_PREFIX):
        return {normalized, normalized.removeprefix(_URN_PREFIX)}
    return {normalized, f"{_URN_PREFIX}{normalized}"}


def _local_identity(value: str) -> str:
    return value.strip().removeprefix(_URN_PREFIX)


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
    ).hexdigest()


class QueryContextStore:
    """Lazy validator for one run's optional Weather and BTS read layers."""

    def __init__(self, run_dir: str | Path, *, graph_store: Any) -> None:
        self.run_dir = Path(run_dir).resolve()
        self.graph_store = graph_store
        self._manifest_cache: dict[str, Any] | None = None
        self._snapshots_cache: SourceSnapshotRegistry | None = None
        self.last_outcome_summary_ids: tuple[str, ...] = ()
        self._manifest()

    def _manifest(self) -> dict[str, Any]:
        if self._manifest_cache is not None:
            return self._manifest_cache
        path = self.run_dir / "run_manifest.json"
        if not path.exists():
            raise QueryContextError("current run manifest is missing")
        if path.is_symlink() or not path.resolve().is_relative_to(self.run_dir):
            raise QueryContextError("run manifest escapes the requested run directory")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise QueryContextError("invalid run manifest") from exc
        if not isinstance(payload, dict):
            raise QueryContextError("run manifest is not a JSON object")
        if payload.get("manifest_version") != RUN_MANIFEST_VERSION:
            raise QueryContextError(
                "run manifest is not the current run manifest version"
            )
        run_id = payload.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            raise QueryContextError("run manifest has no valid run_id")
        artifacts = payload.get("context_artifacts", {})
        if not isinstance(artifacts, dict):
            raise QueryContextError("run manifest context_artifacts is malformed")
        materialization = payload.get("materialization")
        if (
            not isinstance(materialization, dict)
            or materialization.get("materialized") is not True
        ):
            raise QueryContextError(
                "current run manifest has no current materialization"
            )
        layers = payload.get("formal_layers")
        if not isinstance(layers, dict):
            raise QueryContextError("current run formal_layers are malformed")
        self._manifest_cache = payload
        return payload

    @property
    def run_id(self) -> str:
        manifest = self._manifest()
        return str(manifest["run_id"])

    def _artifact(self, key: str, filename: str) -> _Artifact | None:
        manifest = self._manifest()
        entry = manifest["context_artifacts"].get(key)
        if entry is None:
            if (self.run_dir / filename).exists():
                raise QueryContextError(
                    f"{key} artifact exists without manifest registration"
                )
            return None
        if not isinstance(entry, dict):
            raise QueryContextError(f"{key} manifest entry is malformed")
        if entry.get("path") != filename:
            raise QueryContextError(f"{key} manifest path must be {filename}")
        status = entry.get("status")
        if status not in {"ok", "insufficient", "blocked"}:
            raise QueryContextError(f"{key} manifest status is invalid")
        path = self.run_dir / filename
        if (
            path.is_symlink()
            or not path.exists()
            or not path.is_file()
            or not path.resolve().is_relative_to(self.run_dir)
        ):
            raise QueryContextError(
                f"{key} artifact is missing, symlinked, or outside the run directory"
            )
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise QueryContextError(f"{key} artifact cannot be read") from exc
        expected_sha = entry.get("sha256")
        if (
            not isinstance(expected_sha, str)
            or hashlib.sha256(data).hexdigest() != expected_sha
        ):
            raise QueryContextError(f"{key} artifact checksum mismatch")
        expected_count = entry.get("count")
        actual_count = sum(1 for line in data.splitlines() if line.strip())
        if (
            not isinstance(expected_count, int)
            or isinstance(expected_count, bool)
            or expected_count < 0
            or actual_count != expected_count
        ):
            raise QueryContextError(f"{key} artifact row count mismatch")
        return _Artifact(status=status, data=data)

    def _typed_rows(
        self,
        artifact: _Artifact,
        model: type[_T],
        *,
        id_field: str,
        artifact_name: str,
    ) -> list[_T]:
        rows: list[_T] = []
        try:
            text = artifact.data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise QueryContextError(f"{artifact_name} is not UTF-8") from exc
        for line_number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(model.model_validate_json(line))
            except Exception as exc:
                raise QueryContextError(
                    f"invalid {artifact_name} row at line {line_number}"
                ) from exc
        identifiers = [str(getattr(row, id_field)) for row in rows]
        if len(identifiers) != len(set(identifiers)):
            raise QueryContextError(f"duplicate {artifact_name} ID")
        return rows

    def _snapshots(self) -> SourceSnapshotRegistry:
        if self._snapshots_cache is not None:
            return self._snapshots_cache
        artifact = self._artifact("source_snapshots", "source_snapshots.jsonl")
        if artifact is None:
            raise QueryContextError("optional context has no source snapshot registry")
        if artifact.status != "ok":
            raise QueryContextError(
                f"source snapshot registry status is {artifact.status}"
            )
        snapshots = self._typed_rows(
            artifact,
            SourceSnapshot,
            id_field="source_id",
            artifact_name="source_snapshots",
        )
        try:
            registry = SourceSnapshotRegistry(snapshots=tuple(snapshots))
        except Exception as exc:
            raise QueryContextError("invalid source snapshot registry") from exc
        self._snapshots_cache = registry
        return registry

    def _registered_snapshots(self) -> SourceSnapshotRegistry | None:
        manifest = self._manifest()
        registry_path = self.run_dir / "source_snapshots.jsonl"
        if "source_snapshots" not in manifest["context_artifacts"]:
            if registry_path.exists():
                raise QueryContextError(
                    "source snapshot registry exists without manifest registration"
                )
            return None
        return self._snapshots()

    def _event_bindings(
        self,
        event_id: str,
        snapshots: SourceSnapshotRegistry,
    ) -> tuple[str, datetime, datetime, datetime]:
        if event_id not in self.graph_store.event_ids:
            raise QueryContextError(f"unregistered event ID: {event_id}")

        def values(predicate: str) -> list[str]:
            return [
                str(row.get("object") or "")
                for row in self.graph_store.rows
                if row["subject"] == event_id and row["predicate"] == predicate
            ]

        facilities = values("atm:controlledNASelement")
        starts = values("atm:effectiveStartTime")
        ends = values("atm:effectiveEndTime")
        if len(facilities) != 1 or not facilities[0]:
            raise QueryContextError("event has no singular controlled facility")
        if len(starts) != 1 or len(ends) != 1:
            raise QueryContextError("event has no singular operational period")
        start = _parse_datetime(starts[0], field="operational start")
        end = _parse_datetime(ends[0], field="operational end")
        if end <= start:
            raise QueryContextError("event operational period is invalid")
        event_source_ids = {
            source_id
            for row in self.graph_store.rows
            if row["subject"] == event_id
            for source_id in row["source_ids"]
        }
        advisory_snapshots = [
            snapshot
            for snapshot in snapshots.snapshots
            if snapshot.family == SourceFamily.ATCSCC_ADVISORY
            and snapshot.source_id in event_source_ids
        ]
        if len(advisory_snapshots) != 1:
            raise QueryContextError(
                "event has no singular source-bound advisory snapshot"
            )
        issued_at = _parse_advisory_issue_time(advisory_snapshots[0].content)
        return facilities[0], issued_at, start, end

    def _graph_identity_set(self) -> set[str]:
        identities: set[str] = set()
        for row in self.graph_store.rows:
            for value in (
                str(row.get("fact_id") or ""),
                str(row.get("subject") or ""),
                str(row.get("object") or ""),
            ):
                identities.update(_identity_aliases(value))
        for entity_id in self.graph_store.entity_ids:
            identities.update(_identity_aliases(str(entity_id)))
        return identities

    def _reject_graph_identity_collision(
        self,
        identifier: str,
        *,
        label: str,
    ) -> None:
        if _identity_aliases(identifier).intersection(self._graph_identity_set()):
            raise QueryContextError(f"{label} collides with a formal graph identity")

    def _reject_reserved_graph_namespace(
        self,
        namespace: str,
        *,
        label: str,
    ) -> None:
        for row in self.graph_store.rows:
            identity_values = [
                str(row.get("fact_id") or ""),
                str(row.get("subject") or ""),
            ]
            if str(row.get("object_kind") or "") == "iri":
                identity_values.append(str(row.get("object") or ""))
            if any(
                _local_identity(value).startswith(namespace)
                for value in identity_values
            ):
                raise QueryContextError(
                    f"{label} appears in the formal graph"
                )

    def _validate_source_family_formal_rows(
        self,
        snapshots: SourceSnapshotRegistry,
        *,
        families: set[SourceFamily],
        allowed_fact_ids: set[str],
        label: str,
    ) -> None:
        family_source_ids = {
            snapshot.source_id
            for snapshot in snapshots.snapshots
            if snapshot.family in families
        }
        actual_fact_ids = {
            str(row["fact_id"])
            for row in self.graph_store.rows
            if _source_ids(row).intersection(family_source_ids)
        }
        if actual_fact_ids != allowed_fact_ids:
            raise QueryContextError(
                f"{label} formal graph rows violate the source-family boundary"
            )

    @staticmethod
    def _facility_code(facility_id: str) -> str:
        code = facility_id.rsplit(":", 1)[-1]
        if not _ICAO_AIRPORT_CODE.fullmatch(code):
            raise QueryContextError(
                "controlled facility has no canonical ICAO airport code"
            )
        return code

    @staticmethod
    def _deduplicate_weather_reports(
        reports: list[_SourceWeatherReport],
    ) -> list[_SourceWeatherReport]:
        by_anchor: dict[
            tuple[SourceFamily, str, datetime],
            list[_SourceWeatherReport],
        ] = {}
        for report in reports:
            anchor = (report.family, report.station, report.logical_time)
            by_anchor.setdefault(anchor, []).append(report)
        selected: list[_SourceWeatherReport] = []
        for anchor in sorted(by_anchor):
            matches = by_anchor[anchor]
            identities = {
                (report.raw, report.interval_start, report.interval_end)
                for report in matches
            }
            if len(identities) > 1:
                raise QueryContextError(
                    "conflicting duplicate weather logical anchor"
                )
            selected.append(
                min(
                    matches,
                    key=lambda report: (
                        report.snapshot.source_id,
                        report.snapshot.content_sha256,
                    ),
                )
            )
        return selected

    def _expected_weather_selections(
        self,
        *,
        snapshots: SourceSnapshotRegistry,
        facility_id: str,
        issued_at: datetime,
        operational_start: datetime,
        operational_end: datetime,
    ) -> list[
        tuple[
            _SourceWeatherReport,
            Literal[
                "latest_forecast_known_at_issue",
                "latest_observation_at_or_before_issue",
                "observation_during_operation",
            ],
            str,
        ]
    ]:
        facility_code = self._facility_code(facility_id)
        parsed = [
            _parse_source_weather_report(snapshot)
            for snapshot in snapshots.snapshots
            if snapshot.family in {SourceFamily.METAR, SourceFamily.TAF}
        ]
        reports = self._deduplicate_weather_reports(
            [report for report in parsed if report.station == facility_code]
        )
        selections: list[
            tuple[
                _SourceWeatherReport,
                Literal[
                    "latest_forecast_known_at_issue",
                    "latest_observation_at_or_before_issue",
                    "observation_during_operation",
                ],
                str,
            ]
        ] = []
        tafs = [
            report
            for report in reports
            if report.family == SourceFamily.TAF
            and report.logical_time <= issued_at
            and report.interval_start < operational_end
            and report.interval_end > operational_start
        ]
        if tafs:
            latest_issue = max(report.logical_time for report in tafs)
            latest = min(
                [report for report in tafs if report.logical_time == latest_issue],
                key=lambda report: (
                    report.snapshot.source_id,
                    report.snapshot.content_sha256,
                ),
            )
            selections.append(
                (
                    latest,
                    "latest_forecast_known_at_issue",
                    "latest eligible TAF by issue time",
                )
            )

        metars = [
            report
            for report in reports
            if report.family == SourceFamily.METAR
        ]
        pre_issue = [
            report
            for report in metars
            if issued_at - timedelta(hours=2)
            <= report.logical_time
            <= issued_at
        ]
        if pre_issue:
            latest_time = max(report.logical_time for report in pre_issue)
            latest = min(
                [
                    report
                    for report in pre_issue
                    if report.logical_time == latest_time
                ],
                key=lambda report: (
                    report.snapshot.source_id,
                    report.snapshot.content_sha256,
                ),
            )
            selections.append(
                (
                    latest,
                    "latest_observation_at_or_before_issue",
                    "latest METAR within two hours",
                )
            )
        during = sorted(
            [
                report
                for report in metars
                if operational_start
                <= report.logical_time
                < operational_end
            ],
            key=lambda report: (
                report.logical_time,
                report.report_id,
                report.snapshot.source_id,
            ),
        )
        selections.extend(
            (
                report,
                "observation_during_operation",
                "METAR in half-open operational period",
            )
            for report in during
        )
        return selections

    @staticmethod
    def _expected_relevant_times(
        *,
        report: _SourceWeatherReport,
        issued_at: datetime,
        operational_start: datetime,
        operational_end: datetime,
    ) -> dict[str, str]:
        values = {
            "advisory_issued_at": issued_at.isoformat(),
            "operational_end": operational_end.isoformat(),
            "operational_start": operational_start.isoformat(),
        }
        if report.family == SourceFamily.METAR:
            values["observation_time"] = report.logical_time.isoformat()
        else:
            values["forecast_issue_time"] = report.logical_time.isoformat()
            values["forecast_valid_from"] = report.interval_start.isoformat()
            values["forecast_valid_to"] = report.interval_end.isoformat()
        return values

    @staticmethod
    def _expected_association_id(
        *,
        run_id: str,
        event_id: str,
        report_id: str,
        facility_id: str,
        relation_type: str,
        source_checksum: str,
    ) -> str:
        digest = hashlib.sha256(
            "|".join(
                (
                    run_id,
                    event_id,
                    report_id,
                    facility_id,
                    relation_type,
                    source_checksum,
                )
            ).encode("utf-8")
        ).hexdigest()[:24]
        return f"weather-association:{digest}"

    @staticmethod
    def _expected_bts_summary_id(
        *,
        run_id: str,
        event_id: str,
        facility_id: str,
        phase: str,
        window_start: datetime,
        window_end: datetime,
        source_id: str,
        source_checksum: str,
    ) -> str:
        digest = hashlib.sha256(
            json.dumps(
                {
                    "event_id": event_id,
                    "facility_id": facility_id,
                    "phase": phase,
                    "run_id": run_id,
                    "source_id": source_id,
                    "source_snapshot_sha256": source_checksum,
                    "window_end": window_end.isoformat(),
                    "window_start": window_start.isoformat(),
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:24]
        return f"bts-outcome:{source_id}:{digest}"

    @staticmethod
    def _report_subject(report_id: str) -> str:
        if report_id.startswith("urn:"):
            return report_id
        return f"urn:aviation-agentic-ai:{report_id}"

    def _validate_report(
        self,
        report: _SourceWeatherReport,
        *,
        facility_id: str,
    ) -> list[dict[str, Any]]:
        subject = self._report_subject(report.report_id)
        rows = [
            row
            for row in self.graph_store.rows
            if row["subject"] == subject
            and str(row["predicate"]) in _WEATHER_PREDICATES
        ]
        if not rows:
            raise QueryContextError(
                f"weather report has no formal graph facts: {report.report_id}"
            )
        if any(
            _source_ids(row) != {report.snapshot.source_id}
            for row in rows
        ):
            raise QueryContextError(
                f"weather report source binding mismatch: {report.report_id}"
            )

        expected: dict[str, tuple[str, str, str, str]] = {
            "rdf:type": (
                _METEOROLOGICAL_REPORT,
                "iri",
                "data:MeteorologicalReport",
                "",
            ),
            "data:forecastingAirport": (
                facility_id,
                "iri",
                "nas:Airport",
                "",
            ),
            "data:dataIntervalStartTime": (
                report.interval_start.isoformat(),
                "literal",
                "",
                XSD_DATETIME,
            ),
            "data:dataIntervalEndTime": (
                report.interval_end.isoformat(),
                "literal",
                "",
                XSD_DATETIME,
            ),
        }
        raw_predicate = (
            "data:tafReportString"
            if report.family == SourceFamily.TAF
            else "data:metarReportString"
        )
        expected[raw_predicate] = (
            report.raw,
            "literal",
            "",
            XSD_STRING,
        )
        if report.family == SourceFamily.TAF:
            expected["data:forecastIssueTime"] = (
                report.logical_time.isoformat(),
                "literal",
                "",
                XSD_DATETIME,
            )
        by_predicate: dict[str, dict[str, Any]] = {}
        for row in rows:
            predicate = str(row["predicate"])
            if predicate in by_predicate:
                raise QueryContextError(
                    f"weather report has duplicate formal predicate: "
                    f"{report.report_id}"
                )
            by_predicate[predicate] = row
        if set(by_predicate) != set(expected):
            raise QueryContextError(
                f"weather report formal facts do not match source: "
                f"{report.report_id}"
            )

        for predicate, (
            value,
            object_kind,
            object_class,
            datatype_iri,
        ) in expected.items():
            row = by_predicate[predicate]
            expected_fact_id = expected_weather_fact_id(
                report.report_id,
                _PREDICATE_IRIS[predicate],
                value,
            )
            if (
                str(row.get("fact_id") or "") != expected_fact_id
                or str(row.get("subject") or "") != subject
                or str(row.get("predicate") or "") != predicate
                or str(row.get("object") or "") != value
                or str(row.get("subject_class") or "")
                != "data:MeteorologicalReport"
                or str(row.get("object_class") or "") != object_class
                or str(row.get("object_kind") or "") != object_kind
                or str(row.get("datatype_iri") or "") != datatype_iri
                or str(row.get("source_document") or "")
                != report.snapshot.source_id
                or str(row.get("evidence_text") or "") != report.raw
            ):
                raise QueryContextError(
                    f"weather report formal fact shape does not match source: "
                    f"{report.report_id}"
                )
        return sorted(rows, key=lambda row: str(row["fact_id"]))

    def get_decision_context(self, event_id: str) -> DecisionContextRead:
        """Return validated non-causal associations and their formal report facts."""

        self._reject_reserved_graph_namespace(
            "weather-association:",
            label="weather association audit identity",
        )
        artifact = self._artifact(
            "context_associations",
            "context_associations.jsonl",
        )
        if artifact is None:
            snapshots = self._registered_snapshots()
            if snapshots is not None:
                raise QueryContextError(
                    "registered multi-source run has no decision context artifact"
                )
            return DecisionContextRead(status="insufficient")
        if artifact.status == "blocked":
            if any(line.strip() for line in artifact.data.splitlines()):
                raise QueryContextError(
                    "blocked decision context artifact contains rows"
                )
            raise QueryContextError("decision context artifact status is blocked")
        associations = self._typed_rows(
            artifact,
            WeatherContextAssociation,
            id_field="association_id",
            artifact_name="context_associations",
        )
        run_id = self.run_id
        snapshots = self._snapshots()
        facility_id, issued_at, start, end = self._event_bindings(
            event_id,
            snapshots,
        )
        expected_selections = self._expected_weather_selections(
            snapshots=snapshots,
            facility_id=facility_id,
            issued_at=issued_at,
            operational_start=start,
            operational_end=end,
        )
        if artifact.status == "insufficient":
            if associations:
                raise QueryContextError(
                    "insufficient decision context artifact contains rows"
                )
            if expected_selections:
                raise QueryContextError(
                    "insufficient decision context omits eligible weather reports"
                )
            self._validate_source_family_formal_rows(
                snapshots,
                families={SourceFamily.METAR, SourceFamily.TAF},
                allowed_fact_ids=set(),
                label="Weather",
            )
            return DecisionContextRead(status="insufficient")
        if not associations:
            raise QueryContextError("ok decision context artifact is empty")
        if not expected_selections:
            raise QueryContextError(
                "ok decision context has no eligible source-derived reports"
            )
        if any(association.event_id != event_id for association in associations):
            raise QueryContextError("decision context contains a cross-event row")
        for association in associations:
            if association.run_id != run_id:
                raise QueryContextError(
                    f"decision context run binding mismatch: "
                    f"{association.association_id}"
                )
            if association.facility_id != facility_id:
                raise QueryContextError(
                    f"decision context facility binding mismatch: "
                    f"{association.association_id}"
                )
            snapshot = snapshots.get(association.source_id)
            if (
                snapshot is None
                or association.source_snapshot_sha256
                != snapshot.content_sha256
            ):
                raise QueryContextError(
                    f"decision context source binding mismatch: "
                    f"{association.association_id}"
                )

        expected_associations: dict[
            str,
            tuple[WeatherContextAssociation, _SourceWeatherReport],
        ] = {}
        for report, relation_type, selection_method in expected_selections:
            association_id = self._expected_association_id(
                run_id=str(run_id),
                event_id=event_id,
                report_id=report.report_id,
                facility_id=facility_id,
                relation_type=relation_type,
                source_checksum=report.snapshot.content_sha256,
            )
            self._reject_graph_identity_collision(
                association_id,
                label="weather association ID",
            )
            expected_associations[association_id] = (
                WeatherContextAssociation(
                    association_id=association_id,
                    run_id=str(run_id),
                    event_id=event_id,
                    report_id=report.report_id,
                    facility_id=facility_id,
                    relation_type=relation_type,
                    selection_method=selection_method,
                    relevant_times=self._expected_relevant_times(
                        report=report,
                        issued_at=issued_at,
                        operational_start=start,
                        operational_end=end,
                    ),
                    source_id=report.snapshot.source_id,
                    source_snapshot_sha256=report.snapshot.content_sha256,
                    causal_claim=False,
                ),
                report,
            )
        actual_by_id = {
            association.association_id: association
            for association in associations
        }
        if set(actual_by_id) != set(expected_associations):
            raise QueryContextError(
                "decision context associations do not match source-derived "
                "selection"
            )
        formal_rows: dict[str, dict[str, Any]] = {}
        source_ids: set[str] = set()
        selected: list[WeatherContextAssociation] = []
        for association_id in sorted(expected_associations):
            expected, report = expected_associations[association_id]
            association = actual_by_id[association_id]
            if association.model_dump(mode="json") != expected.model_dump(
                mode="json"
            ):
                raise QueryContextError(
                    f"decision context row does not match source-derived "
                    f"selection: "
                    f"{association.association_id}"
                )
            for row in self._validate_report(
                report,
                facility_id=facility_id,
            ):
                formal_rows[str(row["fact_id"])] = row
            selected.append(association)
            source_ids.add(association.source_id)
        self._validate_source_family_formal_rows(
            snapshots,
            families={SourceFamily.METAR, SourceFamily.TAF},
            allowed_fact_ids=set(formal_rows),
            label="Weather",
        )
        return DecisionContextRead(
            status="ok",
            associations=tuple(
                sorted(selected, key=lambda item: item.association_id)
            ),
            formal_fact_rows=tuple(
                formal_rows[fact_id] for fact_id in sorted(formal_rows)
            ),
            source_records=tuple(
                snapshots.get(source_id)
                for source_id in sorted(source_ids)
                if snapshots.get(source_id) is not None
            ),
            source_ids=tuple(sorted(source_ids)),
        )

    def get_outcome_summaries(
        self,
        event_id: str,
        phases: tuple[str, ...],
    ) -> OutcomeSummaryRead:
        """Return profile-owned observations reconstructed from formal facts."""

        self.last_outcome_summary_ids = ()
        try:
            return self._get_formal_outcome_observations(event_id, phases)
        except QueryContextError as exc:
            return OutcomeSummaryRead(
                status="blocked",
                event_id=event_id,
                failure_reason=str(exc),
            )

    def _get_formal_outcome_observations(
        self,
        event_id: str,
        phases: tuple[str, ...],
    ) -> OutcomeSummaryRead:
        self._reject_reserved_graph_namespace(
            "bts-outcome:",
            label="BTS outcome audit identity",
        )
        requested = tuple(str(phase) for phase in phases)
        if (
            not requested
            or len(requested) != len(set(requested))
            or set(requested) - set(_PHASES)
        ):
            raise QueryContextError(
                "outcome phases must be unique baseline, active, or recovery values"
            )
        manifest = self._manifest()
        layers = manifest.get("formal_layers")
        if not isinstance(layers, dict):
            raise QueryContextError("current run formal_layers are malformed")
        layer = layers.get("public_operational_observation")
        if not isinstance(layer, dict):
            raise QueryContextError(
                "current run public observation layer is malformed"
            )
        layer_status = layer.get("status")
        if layer_status == "insufficient":
            self._require_empty_observation_artifacts()
            self._require_no_bts_formal_rows()
            return OutcomeSummaryRead(status="insufficient", event_id=event_id)
        if layer_status == "blocked":
            self._require_empty_observation_artifacts()
            self._require_no_bts_formal_rows()
            return OutcomeSummaryRead(
                status="blocked",
                event_id=event_id,
                failure_reason=str(
                    layer.get("failure_reason")
                    or "public observation layer is blocked"
                ),
            )
        if layer_status != "ok":
            raise QueryContextError("public observation layer status is invalid")

        snapshots = self._snapshots()
        facility_id, _issued_at, start, end = self._event_bindings(
            event_id,
            snapshots,
        )
        summaries = self._read_ok_rows(
            "outcome_summaries",
            "outcome_summaries.jsonl",
            BTSOutcomeSummary,
            "summary_id",
        )
        traces = self._read_ok_rows(
            "observation_fact_trace",
            "observation_fact_trace.jsonl",
            ObservationFactTrace,
            "fact_id",
        )
        derivations = self._read_ok_rows(
            "observation_derivations",
            "observation_derivations.jsonl",
            ObservationDerivation,
            "derivation_id",
        )
        reconstruction_artifact = self._artifact(
            "reconstruction_trace",
            "reconstruction_trace.json",
        )
        if reconstruction_artifact is None or reconstruction_artifact.status != "ok":
            raise QueryContextError("formal observations have no reconstruction trace")
        try:
            reconstruction = ReconstructionTrace.model_validate_json(
                reconstruction_artifact.data
            )
        except Exception as exc:
            raise QueryContextError("invalid reconstruction trace") from exc

        registry = load_validation_profile_registry(
            decision_guide=load_schema_guide()
        )
        profile_candidates = [
            candidate
            for candidate in registry.profiles
            if candidate.ref.layer == "public_operational_observation"
        ]
        if len(profile_candidates) != 1:
            raise QueryContextError(
                "exactly one public observation profile is required"
            )
        profile = registry.require_layer(
            profile_candidates[0].ref,
            "public_operational_observation",
        )
        profile_ref = profile.ref
        if (
            layer.get("profile_id") != profile_ref.profile_id
            or layer.get("profile_checksum") != profile_ref.profile_checksum
        ):
            raise QueryContextError("public observation profile binding mismatch")
        publication = manifest.get("public_observation_publication")
        if not isinstance(publication, dict) or publication.get("status") != "ok":
            raise QueryContextError("public observation publication is not ok")
        procedure = profile.aggregation_procedure
        if procedure is None:
            raise QueryContextError("public observation profile has no procedure")
        if (
            publication.get("aggregation_procedure_id")
            != procedure.procedure_id
            or publication.get("aggregation_procedure_checksum")
            != procedure.checksum
            or reconstruction.aggregation_procedure_id
            != procedure.procedure_id
            or reconstruction.aggregation_procedure_checksum
            != procedure.checksum
        ):
            raise QueryContextError("public observation procedure binding mismatch")
        if profile_ref not in reconstruction.profile_refs:
            raise QueryContextError(
                "reconstruction omits the public observation profile"
            )

        bts_snapshots = [
            snapshot
            for snapshot in snapshots.snapshots
            if snapshot.family == SourceFamily.BTS_ON_TIME
        ]
        if len(bts_snapshots) != 1:
            raise QueryContextError(
                "formal observations require exactly one BTS snapshot"
            )
        bts_snapshot = bts_snapshots[0]
        if (
            publication.get("bts_source_id") != bts_snapshot.source_id
            or publication.get("bts_source_snapshot_sha256")
            != bts_snapshot.content_sha256
        ):
            raise QueryContextError("BTS publication source binding mismatch")
        source_bindings = {
            binding.source_id: binding for binding in reconstruction.source_bindings
        }
        bts_binding = source_bindings.get(bts_snapshot.source_id)
        if (
            bts_binding is None
            or bts_binding.source_family != SourceFamily.BTS_ON_TIME
            or bts_binding.snapshot_sha256 != bts_snapshot.content_sha256
        ):
            raise QueryContextError("reconstruction BTS source binding mismatch")
        if publication.get("source_bindings") != [
            binding.model_dump(mode="json")
            for binding in reconstruction.source_bindings
        ]:
            raise QueryContextError(
                "publication and reconstruction source bindings differ"
            )

        summary_by_id = self._validated_audit_summaries(
            summaries=summaries,
            event_id=event_id,
            facility_id=facility_id,
            snapshots=snapshots,
            start=start,
            end=end,
        )
        derivation_by_id = {
            derivation.derivation_id: derivation
            for derivation in derivations
        }
        if len(derivation_by_id) != len(derivations):
            raise QueryContextError("duplicate observation derivation ID")
        rows_by_id = self._normalized_bts_rows(bts_snapshot)
        metric_payload = json.loads(Path(profile.source_path).read_text("utf-8"))
        metrics = metric_payload.get("metrics")
        if not isinstance(metrics, dict):
            raise QueryContextError("public observation profile metrics are malformed")
        formal_rows = [
            row
            for row in self.graph_store.rows
            if row.get("validation_layer")
            == "public_operational_observation"
        ]
        expected_count = layer.get("formal_fact_count")
        if (
            not isinstance(expected_count, int)
            or isinstance(expected_count, bool)
            or expected_count != len(formal_rows)
        ):
            raise QueryContextError("public observation formal fact count mismatch")
        if any(
            row.get("profile_id") != profile_ref.profile_id
            or row.get("profile_checksum") != profile_ref.profile_checksum
            for row in formal_rows
        ):
            raise QueryContextError("formal observation profile ownership mismatch")
        formal_members = {
            str(row["object"])
            for row in formal_rows
            if row.get("subject") == reconstruction.reconstruction_iri
            and row.get("predicate") == "prov:hadMember"
        }
        if formal_members != set(reconstruction.member_iris):
            raise QueryContextError(
                "formal reconstruction membership differs from its trace"
            )
        self._validate_source_family_formal_rows(
            snapshots,
            families={SourceFamily.BTS_ON_TIME},
            allowed_fact_ids={
                str(row["fact_id"])
                for row in formal_rows
                if bts_snapshot.source_id in row["source_ids"]
            },
            label="BTS",
        )
        graph_by_id = {str(row["fact_id"]): row for row in formal_rows}
        observations: list[OutcomeObservationRead] = []
        seen_observations: set[str] = set()
        selected_summary_ids: set[str] = set()
        for trace in sorted(
            traces,
            key=lambda item: (item.metric_key, item.observation_id),
        ):
            derivation = derivation_by_id.get(trace.derivation_id)
            summary = summary_by_id.get(trace.summary_id)
            if derivation is None or summary is None:
                raise QueryContextError("observation trace has no audit binding")
            self._validate_trace_and_derivation(
                trace=trace,
                derivation=derivation,
                summary=summary,
                snapshot=bts_snapshot,
                rows_by_id=rows_by_id,
                procedure_id=procedure.procedure_id,
                procedure_checksum=procedure.checksum,
            )
            if summary.phase not in requested:
                continue
            if trace.observation_id in seen_observations:
                raise QueryContextError("duplicate formal observation ID")
            seen_observations.add(trace.observation_id)
            selected_summary_ids.add(summary.summary_id)
            observation = self._reconstruct_observation(
                trace=trace,
                summary=summary,
                graph_by_id=graph_by_id,
                metrics=metrics,
                profile_id=profile_ref.profile_id,
                profile_checksum=profile_ref.profile_checksum,
                procedure_id=procedure.procedure_id,
                activity_iri=derivation.activity_iri,
            )
            if observation.observation_id not in reconstruction.member_iris:
                raise QueryContextError(
                    "formal observation is absent from reconstruction membership"
                )
            observations.append(observation)
        expected_traces = [
            trace
            for trace in traces
            if summary_by_id.get(trace.summary_id) is not None
            and summary_by_id[trace.summary_id].phase in requested
        ]
        if len(observations) != len(expected_traces):
            raise QueryContextError("formal observation trace coverage mismatch")
        if not observations:
            return OutcomeSummaryRead(status="insufficient", event_id=event_id)
        self.last_outcome_summary_ids = tuple(sorted(selected_summary_ids))
        return OutcomeSummaryRead(
            status="ok",
            event_id=event_id,
            observations=tuple(
                sorted(
                    observations,
                    key=lambda item: (
                        _PHASES.index(item.phase),
                        item.metric_key,
                        item.observation_id,
                    ),
                )
            ),
            source_ids=(bts_snapshot.source_id,),
        )

    def _read_ok_rows(
        self,
        key: str,
        filename: str,
        model: type[_T],
        id_field: str,
    ) -> list[_T]:
        artifact = self._artifact(key, filename)
        if artifact is None or artifact.status != "ok":
            raise QueryContextError(f"formal observations have no ok {key} artifact")
        rows = self._typed_rows(
            artifact,
            model,
            id_field=id_field,
            artifact_name=key,
        )
        if not rows:
            raise QueryContextError(f"ok {key} artifact is empty")
        return rows

    def _require_empty_observation_artifacts(self) -> None:
        for key, filename in (
            ("observation_derivations", "observation_derivations.jsonl"),
            ("observation_fact_trace", "observation_fact_trace.jsonl"),
            ("reconstruction_trace", "reconstruction_trace.json"),
        ):
            artifact = self._artifact(key, filename)
            if artifact is None:
                continue
            if any(line.strip() for line in artifact.data.splitlines()):
                raise QueryContextError(
                    f"{key} must be empty when observations are not published"
                )

    def _require_no_bts_formal_rows(self) -> None:
        snapshots = self._registered_snapshots()
        if snapshots is None:
            return
        self._validate_source_family_formal_rows(
            snapshots,
            families={SourceFamily.BTS_ON_TIME},
            allowed_fact_ids=set(),
            label="BTS",
        )

    def _validated_audit_summaries(
        self,
        *,
        summaries: list[BTSOutcomeSummary],
        event_id: str,
        facility_id: str,
        snapshots: SourceSnapshotRegistry,
        start: datetime,
        end: datetime,
    ) -> dict[str, BTSOutcomeSummary]:
        expected_windows = {
            "baseline": (start - timedelta(hours=2), start),
            "active": (start, end),
            "recovery": (end, end + timedelta(hours=6)),
        }
        run_id = self.run_id
        by_phase: dict[str, BTSOutcomeSummary] = {}
        for summary in summaries:
            if (
                summary.run_id != run_id
                or summary.event_id != event_id
                or summary.facility_id != facility_id
                or summary.causal_claim is not False
                or summary.reporting_scope != _BTS_REPORTING_SCOPE
            ):
                raise QueryContextError(
                    f"outcome summary binding mismatch: {summary.summary_id}"
                )
            if summary.phase in by_phase:
                raise QueryContextError(f"duplicate outcome phase: {summary.phase}")
            snapshot = snapshots.get(summary.source_id)
            if (
                snapshot is None
                or snapshot.family != SourceFamily.BTS_ON_TIME
                or summary.source_snapshot_sha256 != snapshot.content_sha256
            ):
                raise QueryContextError(
                    f"outcome summary source binding mismatch: {summary.summary_id}"
                )
            expected_start, expected_end = expected_windows[summary.phase]
            if (
                summary.window_start.astimezone(UTC) != expected_start
                or summary.window_end.astimezone(UTC) != expected_end
            ):
                raise QueryContextError(
                    f"outcome summary window mismatch: {summary.summary_id}"
                )
            expected_id = self._expected_bts_summary_id(
                run_id=str(run_id),
                event_id=event_id,
                facility_id=facility_id,
                phase=summary.phase,
                window_start=expected_start,
                window_end=expected_end,
                source_id=summary.source_id,
                source_checksum=summary.source_snapshot_sha256,
            )
            if summary.summary_id != expected_id:
                raise QueryContextError(
                    f"outcome summary ID is not deterministic: {summary.summary_id}"
                )
            by_phase[summary.phase] = summary
        if set(by_phase) != set(_PHASES):
            raise QueryContextError(
                "outcome summaries require baseline, active, and recovery"
            )
        return {summary.summary_id: summary for summary in by_phase.values()}

    @staticmethod
    def _normalized_bts_rows(snapshot: SourceSnapshot) -> dict[str, BTSOnTimeRow]:
        rows: dict[str, BTSOnTimeRow] = {}
        for line_number, line in enumerate(snapshot.content.splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = BTSOnTimeRow.model_validate_json(line)
            except Exception as exc:
                raise QueryContextError(
                    f"invalid normalized BTS row at line {line_number}"
                ) from exc
            if row.row_id in rows:
                raise QueryContextError("duplicate normalized BTS row ID")
            rows[row.row_id] = row
        return rows

    def _validate_trace_and_derivation(
        self,
        *,
        trace: ObservationFactTrace,
        derivation: ObservationDerivation,
        summary: BTSOutcomeSummary,
        snapshot: SourceSnapshot,
        rows_by_id: dict[str, BTSOnTimeRow],
        procedure_id: str,
        procedure_checksum: str,
    ) -> None:
        summary_hash = _canonical_digest(summary.model_dump(mode="json"))
        if (
            trace.summary_sha256 != summary_hash
            or derivation.summary_sha256 != summary_hash
            or derivation.summary_id != summary.summary_id
            or trace.source_id != summary.source_id
            or derivation.source_id != summary.source_id
            or trace.source_snapshot_sha256 != snapshot.content_sha256
            or derivation.source_snapshot_sha256 != snapshot.content_sha256
        ):
            raise QueryContextError("observation audit source or summary mismatch")
        if (
            trace.aggregation_procedure_id != procedure_id
            or derivation.aggregation_procedure_id != procedure_id
            or trace.aggregation_procedure_checksum != procedure_checksum
            or derivation.aggregation_procedure_checksum != procedure_checksum
        ):
            raise QueryContextError("observation audit procedure mismatch")
        if (
            derivation.selected_row_ids
            != tuple(sorted(derivation.selected_row_ids))
            or derivation.selected_row_ids_sha256
            != _canonical_digest(derivation.selected_row_ids)
        ):
            raise QueryContextError("observation selected-row digest mismatch")
        expected_derivation_id = "bts-derivation:" + _canonical_digest(
            {
                "aggregation_procedure_checksum": (
                    derivation.aggregation_procedure_checksum
                ),
                "aggregation_procedure_id": derivation.aggregation_procedure_id,
                "archive_sha256": derivation.archive_sha256,
                "selected_row_ids_sha256": derivation.selected_row_ids_sha256,
                "source_id": derivation.source_id,
                "source_snapshot_sha256": (
                    derivation.source_snapshot_sha256
                ),
                "summary_id": derivation.summary_id,
                "summary_sha256": derivation.summary_sha256,
            }
        )[:24]
        if derivation.derivation_id != expected_derivation_id:
            raise QueryContextError("observation derivation ID mismatch")
        if any(row_id not in rows_by_id for row_id in derivation.selected_row_ids):
            raise QueryContextError("observation selected row is missing")
        for row_id in derivation.selected_row_ids:
            row = rows_by_id[row_id]
            natural_key = (
                row.FlightDate,
                str(row.DOT_ID_Reporting_Airline),
                str(row.Flight_Number_Reporting_Airline),
                str(row.OriginAirportSeqID),
                str(row.DestAirportSeqID),
                str(row.CRSDepTime),
            )
            expected_row_id = "bts-row:" + hashlib.sha256(
                "|".join((derivation.archive_sha256, *natural_key)).encode()
            ).hexdigest()
            if row.row_id != expected_row_id:
                raise QueryContextError("normalized BTS row ID is not source-bound")
        expected_selection = tuple(
            sorted(
                row.row_id
                for row in rows_by_id.values()
                if row.Dest == summary.facility_id.rsplit(":", 1)[-1].removeprefix("K")
                and summary.window_start.astimezone(UTC)
                <= row.scheduled_arrival_utc.astimezone(UTC)
                < summary.window_end.astimezone(UTC)
            )
        )
        if derivation.selected_row_ids != expected_selection:
            raise QueryContextError("observation selected rows do not match window")
        selected = [rows_by_id[row_id] for row_id in expected_selection]
        completed = [
            row
            for row in selected
            if row.Cancelled == 0 and row.Diverted == 0
        ]
        delays = [row.ArrDelay for row in completed if row.ArrDelay is not None]
        weather_delays = [
            row.WeatherDelay for row in selected if row.WeatherDelay is not None
        ]
        nas_delays = [
            row.NASDelay for row in selected if row.NASDelay is not None
        ]
        expected_values: dict[str, int | float | None] = {
            "scheduled_arrival_count": len(selected),
            "completed_arrival_count": len(completed),
            "cancelled_count": sum(row.Cancelled == 1 for row in selected),
            "diverted_count": sum(row.Diverted == 1 for row in selected),
            "arrival_delay_15_count": sum(
                row.ArrDel15 == 1 for row in completed
            ),
            "mean_arrival_delay_minutes": (
                statistics.mean(delays) if delays else None
            ),
            "median_arrival_delay_minutes": (
                statistics.median(delays) if delays else None
            ),
            "carrier_reported_weather_delay_minutes": (
                sum(weather_delays) if weather_delays else None
            ),
            "carrier_reported_nas_delay_minutes": (
                sum(nas_delays) if nas_delays else None
            ),
        }
        expected_value = expected_values.get(trace.metric_key)
        summary_value = getattr(summary, trace.metric_key, None)
        if expected_value is None or summary_value is None:
            if expected_value is not summary_value:
                raise QueryContextError(
                    "outcome summary differs from selected source rows"
                )
        elif Decimal(str(expected_value)) != Decimal(str(summary_value)):
            raise QueryContextError(
                "outcome summary differs from selected source rows"
            )
        if trace.canonical_value is None or (
            summary_value is not None
            and Decimal(str(trace.canonical_value))
            != Decimal(str(summary_value))
        ):
            raise QueryContextError(
                "observation trace differs from the audit summary"
            )

    @staticmethod
    def _rows_for_subject(
        graph_by_id: dict[str, dict[str, Any]],
        subject: str,
    ) -> list[dict[str, Any]]:
        return [
            row for row in graph_by_id.values() if str(row["subject"]) == subject
        ]

    def _reconstruct_observation(
        self,
        *,
        trace: ObservationFactTrace,
        summary: BTSOutcomeSummary,
        graph_by_id: dict[str, dict[str, Any]],
        metrics: dict[str, Any],
        profile_id: str,
        profile_checksum: str,
        procedure_id: str,
        activity_iri: str,
    ) -> OutcomeObservationRead:
        numeric = graph_by_id.get(trace.fact_id)
        if numeric is None or numeric.get("predicate") != "qudt:numericValue":
            raise QueryContextError("observation numeric fact is missing")
        if (
            numeric.get("subject") is None
            or numeric.get("evidence_ref") != trace.fact_id
            or numeric.get("source_ids") != [trace.source_id]
        ):
            raise QueryContextError("observation numeric fact binding mismatch")
        result_id = str(numeric["subject"])
        observation_rows = self._rows_for_subject(
            graph_by_id,
            trace.observation_id,
        )

        def one(predicate: str) -> dict[str, Any]:
            matches = [
                row for row in observation_rows if row.get("predicate") == predicate
            ]
            if len(matches) != 1:
                raise QueryContextError(
                    f"observation requires one {predicate} fact"
                )
            return matches[0]

        property_row = one("sosa:observedProperty")
        interval_row = one("sosa:phenomenonTime")
        result_row = one("sosa:hasResult")
        procedure_row = one("sosa:usedProcedure")
        generated_row = one("prov:wasGeneratedBy")
        derived_row = one("prov:wasDerivedFrom")
        expected_source_iri = (
            "urn:aviation-agentic-ai:source-record:"
            + _canonical_digest(trace.source_id)
        )
        if (
            result_row.get("object") != result_id
            or procedure_row.get("object") != procedure_id
            or generated_row.get("object") != activity_iri
            or derived_row.get("object") != expected_source_iri
            or any(
                row.get("evidence_ref") != trace.fact_id
                for row in observation_rows
            )
        ):
            raise QueryContextError("observation formal binding mismatch")
        local_name = _METRIC_FIELDS.get(trace.metric_key)
        descriptor = metrics.get(local_name) if local_name else None
        if (
            not isinstance(descriptor, dict)
            or property_row.get("object") != descriptor.get("iri")
        ):
            raise QueryContextError("observation metric profile mismatch")
        interval_id = str(interval_row["object"])
        phase_rows = [
            row
            for row in self._rows_for_subject(graph_by_id, interval_id)
            if row.get("predicate") == "dcterms:type"
        ]
        if (
            len(phase_rows) != 1
            or phase_rows[0].get("object") != _PHASE + summary.phase
        ):
            raise QueryContextError("observation phase binding mismatch")
        unit_rows = [
            row
            for row in self._rows_for_subject(graph_by_id, result_id)
            if row.get("predicate") == "qudt:unit"
        ]
        if (
            len(unit_rows) != 1
            or unit_rows[0].get("object") != descriptor.get("unit")
            or numeric.get("datatype_iri") != descriptor.get("datatype")
        ):
            raise QueryContextError("observation unit or datatype mismatch")
        try:
            value = (
                int(str(numeric["object"]))
                if descriptor["datatype"].endswith("#integer")
                else Decimal(str(numeric["object"]))
            )
        except (ValueError, InvalidOperation) as exc:
            raise QueryContextError("observation numeric value is invalid") from exc
        canonical = trace.canonical_value
        if canonical is None or Decimal(str(value)) != Decimal(str(canonical)):
            raise QueryContextError("observation value differs from trace")
        support_rows = {
            row["fact_id"]: row
            for row in (
                observation_rows
                + self._rows_for_subject(graph_by_id, result_id)
                + self._rows_for_subject(graph_by_id, interval_id)
            )
            if row.get("evidence_ref") == trace.fact_id
            or row["fact_id"] == trace.fact_id
        }
        return OutcomeObservationRead(
            observation_id=trace.observation_id,
            fact_ids=tuple(sorted(support_rows)),
            phase=summary.phase,
            metric_key=trace.metric_key,
            label=str(descriptor["label"]),
            value=value,
            datatype_iri=str(descriptor["datatype"]),
            unit_iri=str(descriptor["unit"]),
            derivation_id=trace.derivation_id,
            evidence_ref=trace.fact_id,
            source_id=trace.source_id,
            source_snapshot_sha256=trace.source_snapshot_sha256,
            profile_id=profile_id,
            profile_checksum=profile_checksum,
        )
