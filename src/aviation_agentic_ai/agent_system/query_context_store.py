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
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal, TypeVar

from pydantic import BaseModel

from aviation_agentic_ai.agent_system.contracts import (
    BTSOutcomeSummary,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    WeatherContextAssociation,
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
class OutcomeSummaryRead:
    """Validated result for one event's BTS-reported operational observations."""

    status: Literal["ok", "insufficient"]
    summaries: tuple[BTSOutcomeSummary, ...] = ()
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


class QueryContextStore:
    """Lazy validator for one run's optional Weather and BTS read layers."""

    def __init__(self, run_dir: str | Path, *, graph_store: Any) -> None:
        self.run_dir = Path(run_dir).resolve()
        self.graph_store = graph_store
        self._manifest_cache: dict[str, Any] | None = None
        self._snapshots_cache: SourceSnapshotRegistry | None = None

    def _manifest(self) -> dict[str, Any] | None:
        if self._manifest_cache is not None:
            return self._manifest_cache
        path = self.run_dir / "run_manifest.json"
        if not path.exists():
            return None
        if path.is_symlink() or not path.resolve().is_relative_to(self.run_dir):
            raise QueryContextError("run manifest escapes the requested run directory")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise QueryContextError("invalid run manifest") from exc
        if not isinstance(payload, dict):
            raise QueryContextError("run manifest is not a JSON object")
        run_id = payload.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            raise QueryContextError("run manifest has no valid run_id")
        artifacts = payload.get("context_artifacts", {})
        if not isinstance(artifacts, dict):
            raise QueryContextError("run manifest context_artifacts is malformed")
        self._manifest_cache = payload
        return payload

    @property
    def run_id(self) -> str | None:
        manifest = self._manifest()
        return str(manifest["run_id"]) if manifest is not None else None

    def _artifact(self, key: str, filename: str) -> _Artifact | None:
        manifest = self._manifest()
        if manifest is None:
            if (self.run_dir / filename).exists():
                raise QueryContextError(
                    f"{key} artifact exists without manifest registration"
                )
            return None
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
        if manifest is None:
            if registry_path.exists():
                raise QueryContextError(
                    "source snapshot registry exists without manifest registration"
                )
            return None
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
        """Return requested, validated BTS-reported summaries."""

        self._reject_reserved_graph_namespace(
            "bts-outcome:",
            label="BTS outcome audit identity",
        )
        artifact = self._artifact("outcome_summaries", "outcome_summaries.jsonl")
        if artifact is None:
            snapshots = self._registered_snapshots()
            if snapshots is not None:
                raise QueryContextError(
                    "registered multi-source run has no outcome summary artifact"
                )
            return OutcomeSummaryRead(status="insufficient")
        if artifact.status == "blocked":
            if any(line.strip() for line in artifact.data.splitlines()):
                raise QueryContextError(
                    "blocked outcome summary artifact contains rows"
                )
            raise QueryContextError("outcome summary artifact status is blocked")
        summaries = self._typed_rows(
            artifact,
            BTSOutcomeSummary,
            id_field="summary_id",
            artifact_name="outcome_summaries",
        )
        if artifact.status == "insufficient":
            if summaries:
                raise QueryContextError(
                    "insufficient outcome summary artifact contains rows"
                )
            snapshots = self._snapshots()
            self._validate_source_family_formal_rows(
                snapshots,
                families={SourceFamily.BTS_ON_TIME},
                allowed_fact_ids=set(),
                label="BTS",
            )
            return OutcomeSummaryRead(status="insufficient")
        if not summaries:
            raise QueryContextError("ok outcome summary artifact is empty")
        requested = tuple(str(phase) for phase in phases)
        if (
            not requested
            or len(requested) != len(set(requested))
            or set(requested) - set(_PHASES)
        ):
            raise QueryContextError(
                "outcome phases must be unique baseline, active, or recovery values"
        )
        run_id = self.run_id
        snapshots = self._snapshots()
        self._validate_source_family_formal_rows(
            snapshots,
            families={SourceFamily.BTS_ON_TIME},
            allowed_fact_ids=set(),
            label="BTS",
        )
        facility_id, _issued_at, start, end = self._event_bindings(
            event_id,
            snapshots,
        )
        expected_windows = {
            "baseline": (start - timedelta(hours=2), start),
            "active": (start, end),
            "recovery": (end, end + timedelta(hours=6)),
        }
        by_phase: dict[str, BTSOutcomeSummary] = {}
        source_ids: set[str] = set()
        for summary in summaries:
            if summary.run_id != run_id:
                raise QueryContextError(
                    f"outcome summary run binding mismatch: {summary.summary_id}"
                )
            if summary.event_id not in self.graph_store.event_ids:
                raise QueryContextError(
                    f"outcome summary references unregistered event: "
                    f"{summary.summary_id}"
                )
            if summary.event_id != event_id:
                raise QueryContextError(
                    f"outcome summary cross-event binding: {summary.summary_id}"
                )
            if summary.facility_id != facility_id:
                raise QueryContextError(
                    f"outcome summary facility binding mismatch: "
                    f"{summary.summary_id}"
                )
            if summary.phase in by_phase:
                raise QueryContextError(
                    f"duplicate outcome phase: {summary.phase}"
                )
            snapshot = snapshots.get(summary.source_id)
            if (
                snapshot is None
                or snapshot.family != SourceFamily.BTS_ON_TIME
                or summary.source_snapshot_sha256 != snapshot.content_sha256
                or summary.causal_claim is not False
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
            if summary.reporting_scope != _BTS_REPORTING_SCOPE:
                raise QueryContextError(
                    f"outcome summary semantic boundary mismatch: "
                    f"{summary.summary_id}"
                )
            expected_summary_id = self._expected_bts_summary_id(
                run_id=str(run_id),
                event_id=event_id,
                facility_id=facility_id,
                phase=summary.phase,
                window_start=expected_start,
                window_end=expected_end,
                source_id=summary.source_id,
                source_checksum=summary.source_snapshot_sha256,
            )
            if summary.summary_id != expected_summary_id:
                raise QueryContextError(
                    f"outcome summary ID is not deterministic: "
                    f"{summary.summary_id}"
                )
            self._reject_graph_identity_collision(
                summary.summary_id,
                label="BTS outcome summary ID",
            )
            by_phase[summary.phase] = summary
            source_ids.add(summary.source_id)
        if set(by_phase) != set(_PHASES):
            raise QueryContextError(
                "outcome summaries require exactly one baseline, active, and recovery row"
            )
        selected = tuple(by_phase[phase] for phase in _PHASES if phase in requested)
        if len(selected) != len(requested):
            raise QueryContextError("requested outcome phase is missing")
        return OutcomeSummaryRead(
            status="ok",
            summaries=selected,
            source_ids=tuple(sorted(source_ids)),
        )
