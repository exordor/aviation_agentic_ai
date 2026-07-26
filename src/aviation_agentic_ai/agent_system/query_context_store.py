"""Fail-closed read surface for optional decision-context artifacts.

The core Query Agent store deliberately does not load these artifacts.  This
module validates an optional layer only when a decision-context tool requests
it, so corruption in an optional Weather or BTS artifact cannot disable the
older core decision-record questions.
"""

from __future__ import annotations

import hashlib
import json
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

_METEOROLOGICAL_REPORT = (
    "https://data.nasa.gov/ontologies/atmonto/data#MeteorologicalReport"
)
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
_APPROVED_RELATIONS = frozenset(
    {
        "latest_forecast_known_at_issue",
        "latest_observation_at_or_before_issue",
        "observation_during_operation",
    }
)
_PHASES = ("baseline", "active", "recovery")
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
    """Validated result for one event's public BTS outcome proxies."""

    status: Literal["ok", "insufficient"]
    summaries: tuple[BTSOutcomeSummary, ...] = ()
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Artifact:
    status: Literal["ok", "insufficient", "blocked"]
    data: bytes


def _parse_datetime(value: Any, *, field: str) -> datetime:
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

    def _event_bindings(
        self,
        event_id: str,
    ) -> tuple[str, datetime, datetime]:
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
        return facilities[0], start, end

    @staticmethod
    def _report_subject(report_id: str) -> str:
        if report_id.startswith("urn:"):
            return report_id
        return f"urn:aviation-agentic-ai:{report_id}"

    def _validate_report(
        self,
        association: WeatherContextAssociation,
        *,
        snapshot: SourceSnapshot,
    ) -> list[dict[str, Any]]:
        subject = self._report_subject(association.report_id)
        rows = [
            row
            for row in self.graph_store.rows
            if row["subject"] == subject
            and str(row["predicate"]) in _WEATHER_PREDICATES
        ]
        if not rows:
            raise QueryContextError(
                f"weather report has no formal graph facts: {association.report_id}"
            )
        if any(association.source_id not in _source_ids(row) for row in rows):
            raise QueryContextError(
                f"weather report source binding mismatch: {association.report_id}"
            )

        def values(predicate: str) -> list[str]:
            return [
                str(row.get("object") or "")
                for row in rows
                if row["predicate"] == predicate
            ]

        report_types = values("rdf:type")
        if report_types != [_METEOROLOGICAL_REPORT]:
            raise QueryContextError(
                f"weather report is not a singular MeteorologicalReport: "
                f"{association.report_id}"
            )
        facilities = values("data:forecastingAirport")
        if facilities != [association.facility_id]:
            raise QueryContextError(
                f"weather report facility mismatch: {association.report_id}"
            )
        expected_family = (
            SourceFamily.TAF
            if association.relation_type == "latest_forecast_known_at_issue"
            else SourceFamily.METAR
        )
        if snapshot.family != expected_family:
            raise QueryContextError(
                f"weather relation source family mismatch: {association.association_id}"
            )
        raw_predicate = (
            "data:tafReportString"
            if expected_family == SourceFamily.TAF
            else "data:metarReportString"
        )
        raw_values = values(raw_predicate)
        if len(raw_values) != 1:
            raise QueryContextError(
                f"weather report has no singular raw report: {association.report_id}"
            )
        try:
            source_row = json.loads(snapshot.content)
        except json.JSONDecodeError as exc:
            raise QueryContextError(
                f"weather snapshot is not canonical JSON: {association.source_id}"
            ) from exc
        source_key = "rawTAF" if expected_family == SourceFamily.TAF else "rawOb"
        if (
            not isinstance(source_row, dict)
            or source_row.get(source_key) != raw_values[0]
        ):
            raise QueryContextError(
                f"weather report does not match its source snapshot: "
                f"{association.report_id}"
            )
        return rows

    def get_decision_context(self, event_id: str) -> DecisionContextRead:
        """Return validated non-causal associations and their formal report facts."""

        artifact = self._artifact(
            "context_associations",
            "context_associations.jsonl",
        )
        if artifact is None:
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
        if artifact.status == "insufficient":
            if associations:
                raise QueryContextError(
                    "insufficient decision context artifact contains rows"
                )
            return DecisionContextRead(status="insufficient")
        if not associations:
            raise QueryContextError("ok decision context artifact is empty")
        run_id = self.run_id
        facility_id, _start, _end = self._event_bindings(event_id)
        snapshots = self._snapshots()
        formal_rows: dict[str, dict[str, Any]] = {}
        source_ids: set[str] = set()
        selected: list[WeatherContextAssociation] = []
        for association in associations:
            if association.run_id != run_id:
                raise QueryContextError(
                    f"decision context run binding mismatch: "
                    f"{association.association_id}"
                )
            if association.event_id not in self.graph_store.event_ids:
                raise QueryContextError(
                    f"decision context references unregistered event: "
                    f"{association.association_id}"
                )
            if association.event_id != event_id:
                raise QueryContextError(
                    f"decision context cross-event binding: "
                    f"{association.association_id}"
                )
            if association.facility_id != facility_id:
                raise QueryContextError(
                    f"decision context facility binding mismatch: "
                    f"{association.association_id}"
                )
            if (
                association.relation_type not in _APPROVED_RELATIONS
                or association.causal_claim is not False
            ):
                raise QueryContextError(
                    f"decision context relation is not approved: "
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
            for row in self._validate_report(association, snapshot=snapshot):
                formal_rows[str(row["fact_id"])] = row
            selected.append(association)
            source_ids.add(association.source_id)
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
        """Return requested, validated BTS proxy summaries."""

        artifact = self._artifact("outcome_summaries", "outcome_summaries.jsonl")
        if artifact is None:
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
        facility_id, start, end = self._event_bindings(event_id)
        snapshots = self._snapshots()
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
