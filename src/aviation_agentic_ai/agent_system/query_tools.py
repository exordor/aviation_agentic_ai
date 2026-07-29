"""Typed read-only tools for the bounded Query Agent.

The model never receives a filesystem path, Cypher, SPARQL, or a graph-write
operation.  A gateway is scoped to one materialized run and exposes only
registered event/entity IDs and predicates from the active competency question.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from aviation_agentic_ai.agent_system.agents import parse_structured_fields
from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    ObservationFactTrace,
    PersistedProfileGap,
    ReconstructionTrace,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
    ValidationProfileRef,
    WeatherFactTrace,
)
from aviation_agentic_ai.agent_system.context_artifacts import (
    read_fact_traces,
    read_observation_fact_traces,
    read_reconstruction_trace,
    read_weather_fact_traces,
)
from aviation_agentic_ai.agent_system.materialize import (
    validate_fact_publication,
)
from aviation_agentic_ai.agent_system.schema_guide import TERM_TO_EVENT_CLASS
from aviation_agentic_ai.agent_system.runtime import RUN_MANIFEST_VERSION
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    LoadedValidationProfile,
    ValidationProfileRegistry,
    load_validation_profile_registry,
)

_REGISTERED_EVENT_CLASSES = frozenset(TERM_TO_EVENT_CLASS.values())
_RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


class QueryToolError(RuntimeError):
    """Raised when a read-only graph operation cannot be executed safely."""


class QueryPredicate(str, Enum):
    """Predicates available to the first Query Agent vertical slice."""

    EVENT_TYPE = "rdf:type"
    CONTROLLED_NAS_ELEMENT = "atm:controlledNASelement"
    EFFECTIVE_START = "atm:effectiveStartTime"
    EFFECTIVE_END = "atm:effectiveEndTime"
    ADVISORY_NUMBER = "atm:advisoryNumber"
    IMPACTING_CONDITION = "atm:impactingCondition"


def _split_source_ids(value: Any) -> list[str]:
    return [
        source_id.strip()
        for source_id in str(value or "").split(";")
        if source_id.strip()
    ]


class QueryGraphStore:
    """Validated read-only view of one run's ``kg.jsonl``."""

    def __init__(self, run_dir: str | Path) -> None:
        root = Path(run_dir).resolve()
        manifest, snapshots, profile_refs, formal_layers, profile_registry = (
            self._load_current_run(root)
        )
        (
            fact_traces,
            weather_fact_traces,
            observation_fact_traces,
            reconstruction_trace,
        ) = self._load_publication_evidence(
            root,
            manifest=manifest,
            formal_layers=formal_layers,
        )
        graph_path = root / "kg.jsonl"
        if not graph_path.exists():
            raise QueryToolError(f"materialized graph not found: {graph_path}")
        resolved_graph = graph_path.resolve()
        if not resolved_graph.is_relative_to(root):
            raise QueryToolError("materialized graph escapes the requested run directory")

        rows: list[dict[str, Any]] = []
        facts: list[ValidatedFact] = []
        seen_fact_ids: set[str] = set()
        for line_number, line in enumerate(
            resolved_graph.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise QueryToolError(
                    f"invalid graph JSON at line {line_number}"
                ) from exc
            if not isinstance(row, dict):
                raise QueryToolError(
                    f"graph row {line_number} is not a JSON object"
                )
            normalized = self._validate_current_fact_row(
                row,
                line_number=line_number,
                snapshots=snapshots,
                profile_refs=profile_refs,
                formal_layers=formal_layers,
            )
            fact_id = str(normalized["triple_id"]).strip()
            if not fact_id:
                raise QueryToolError(f"graph row {line_number} has no fact ID")
            if fact_id in seen_fact_ids:
                raise QueryToolError(f"duplicate graph fact ID: {fact_id}")
            subject = str(normalized.get("subject") or "").strip()
            predicate = str(normalized.get("predicate") or "").strip()
            if not subject or not predicate:
                raise QueryToolError(
                    f"graph row {line_number} is missing subject or predicate"
                )
            normalized["fact_id"] = fact_id
            rows.append(normalized)
            facts.append(
                self._validated_fact_from_row(
                    normalized,
                    profile_registry=profile_registry,
                    line_number=line_number,
                )
            )
            seen_fact_ids.add(fact_id)

        try:
            validate_fact_publication(
                facts=facts,
                profile_registry=profile_registry,
                snapshot_registry=snapshots,
                fact_traces=fact_traces,
                weather_fact_traces=weather_fact_traces,
                observation_fact_traces=observation_fact_traces,
                reconstruction_trace=reconstruction_trace,
                require_source_text_in_snapshot=True,
            )
        except ValueError as exc:
            raise QueryToolError(
                f"graph row violates the current publication contract: {exc}"
            ) from exc
        self._validate_materialized_counts(
            manifest,
            rows,
            profile_refs=profile_refs,
            formal_layers=formal_layers,
        )
        self.run_dir = root
        self.manifest = manifest
        self.source_snapshots = snapshots
        self.graph_path = resolved_graph
        self.rows = rows
        self._validated_facts = tuple(facts)
        self.fact_by_id = {row["fact_id"]: row for row in rows}
        self.event_ids = sorted(
            {
                str(row["subject"])
                for row in rows
                if row["predicate"] == QueryPredicate.EVENT_TYPE
                and str(row.get("object") or "") in _REGISTERED_EVENT_CLASSES
            }
        )
        entity_ids = set(self.event_ids)
        for row in rows:
            if str(row.get("object_kind") or "") == "iri":
                entity_ids.add(str(row.get("object") or ""))
            elif str(row.get("predicate") or "") == QueryPredicate.CONTROLLED_NAS_ELEMENT:
                entity_ids.add(str(row.get("object") or ""))
        self.entity_ids = {entity_id for entity_id in entity_ids if entity_id}
        self.profile_gaps = self._load_profile_gaps(root)
        self.profile_gap_by_id = {
            gap.profile_gap_id: gap for gap in self.profile_gaps
        }

    @property
    def validated_facts(self) -> tuple[ValidatedFact, ...]:
        """Return the validated canonical facts frozen for this run."""

        return self._validated_facts

    @staticmethod
    def _load_current_run(
        root: Path,
    ) -> tuple[
        dict[str, Any],
        SourceSnapshotRegistry,
        set[ValidationProfileRef],
        dict[str, dict[str, Any]],
        ValidationProfileRegistry,
    ]:
        manifest_path = root / "run_manifest.json"
        if (
            manifest_path.is_symlink()
            or not manifest_path.exists()
            or not manifest_path.is_file()
            or not manifest_path.resolve().is_relative_to(root)
        ):
            raise QueryToolError("current run manifest is missing or unsafe")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise QueryToolError("invalid current run manifest") from exc
        if not isinstance(manifest, dict):
            raise QueryToolError("current run manifest is not a JSON object")
        if manifest.get("manifest_version") != RUN_MANIFEST_VERSION:
            raise QueryToolError(
                "run manifest is not the current run manifest version"
            )
        if not isinstance(manifest.get("run_id"), str) or not str(
            manifest["run_id"]
        ).strip():
            raise QueryToolError("current run manifest has no valid run_id")

        materialization = manifest.get("materialization")
        if (
            not isinstance(materialization, dict)
            or materialization.get("materialized") is not True
        ):
            raise QueryToolError(
                "current run manifest has no current materialization"
            )
        fact_count = materialization.get("fact_count")
        if (
            not isinstance(fact_count, int)
            or isinstance(fact_count, bool)
            or fact_count < 1
        ):
            raise QueryToolError(
                "current run materialization fact_count is invalid"
            )
        raw_profile_refs = materialization.get("profile_refs")
        if not isinstance(raw_profile_refs, list) or not raw_profile_refs:
            raise QueryToolError(
                "current run materialization has no profile_refs"
            )
        try:
            profile_refs = {
                ValidationProfileRef.model_validate(value)
                for value in raw_profile_refs
            }
        except Exception as exc:
            raise QueryToolError(
                "current run materialization profile_refs are invalid"
            ) from exc
        if len(profile_refs) != len(raw_profile_refs):
            raise QueryToolError(
                "current run materialization has duplicate profile_refs"
            )
        layer_fact_counts = materialization.get("layer_fact_counts")
        if not isinstance(layer_fact_counts, dict):
            raise QueryToolError(
                "current run materialization layer_fact_counts are invalid"
            )
        artifacts = materialization.get("artifacts")
        kg_path = artifacts.get("kg_jsonl") if isinstance(artifacts, dict) else None
        if not isinstance(kg_path, str) or Path(kg_path).name != "kg.jsonl":
            raise QueryToolError(
                "current run materialization does not register kg.jsonl"
            )

        current_profiles = load_validation_profile_registry(
            decision_guide=load_schema_guide()
        )
        for ref in profile_refs:
            try:
                current_profiles.resolve(ref)
            except ValueError as exc:
                raise QueryToolError(
                    f"current run uses an unknown validation profile: "
                    f"{ref.profile_id}"
                ) from exc

        raw_layers = manifest.get("formal_layers")
        required_layers = {
            "decision",
            "decision_case_core",
            "weather",
            "public_operational_observation",
        }
        if not isinstance(raw_layers, dict) or set(raw_layers) != required_layers:
            raise QueryToolError("current run formal_layers are malformed")
        formal_layers: dict[str, dict[str, Any]] = {}
        for layer, entry in raw_layers.items():
            if not isinstance(entry, dict):
                raise QueryToolError(
                    f"current run formal layer is malformed: {layer}"
                )
            status = entry.get("status")
            count = entry.get("formal_fact_count")
            if status not in {"ok", "insufficient", "blocked"}:
                raise QueryToolError(
                    f"current run formal layer status is invalid: {layer}"
                )
            if (
                not isinstance(count, int)
                or isinstance(count, bool)
                or count < 0
                or (status != "ok" and count != 0)
            ):
                raise QueryToolError(
                    f"current run formal layer fact count is invalid: {layer}"
                )
            try:
                ref = ValidationProfileRef(
                    profile_id=entry["profile_id"],
                    profile_checksum=entry["profile_checksum"],
                    layer=layer,
                )
                current_profiles.resolve(ref)
            except (KeyError, ValueError) as exc:
                raise QueryToolError(
                    f"current run formal layer profile is invalid: {layer}"
                ) from exc
            formal_layers[layer] = entry
            if ref not in profile_refs and status == "ok":
                raise QueryToolError(
                    f"current run formal layer profile is absent from "
                    f"materialization: {layer}"
                )
        if formal_layers["decision"]["status"] != "ok":
            raise QueryToolError("current run decision layer is not queryable")

        context_artifacts = manifest.get("context_artifacts")
        entry = (
            context_artifacts.get("source_snapshots")
            if isinstance(context_artifacts, dict)
            else None
        )
        if not isinstance(entry, dict):
            raise QueryToolError(
                "current run manifest does not register source_snapshots.jsonl"
            )
        if (
            entry.get("path") != "source_snapshots.jsonl"
            or entry.get("status") != "ok"
        ):
            raise QueryToolError(
                "current run source_snapshots.jsonl registration is invalid"
            )
        registry_path = root / "source_snapshots.jsonl"
        if (
            registry_path.is_symlink()
            or not registry_path.exists()
            or not registry_path.is_file()
            or not registry_path.resolve().is_relative_to(root)
        ):
            raise QueryToolError(
                "current run source_snapshots.jsonl is missing or unsafe"
            )
        try:
            data = registry_path.read_bytes()
        except OSError as exc:
            raise QueryToolError(
                "current run source_snapshots.jsonl cannot be read"
            ) from exc
        if (
            not isinstance(entry.get("sha256"), str)
            or hashlib.sha256(data).hexdigest() != entry["sha256"]
        ):
            raise QueryToolError(
                "current run source_snapshots.jsonl checksum mismatch"
            )
        row_count = sum(1 for line in data.splitlines() if line.strip())
        if (
            not isinstance(entry.get("count"), int)
            or isinstance(entry.get("count"), bool)
            or entry["count"] != row_count
        ):
            raise QueryToolError(
                "current run source_snapshots.jsonl row count mismatch"
            )
        try:
            snapshots = SourceSnapshotRegistry.read_jsonl(registry_path)
        except ValueError as exc:
            raise QueryToolError(
                "current run source_snapshots.jsonl is invalid"
            ) from exc
        return (
            manifest,
            snapshots,
            profile_refs,
            formal_layers,
            current_profiles,
        )

    @classmethod
    def _load_publication_evidence(
        cls,
        root: Path,
        *,
        manifest: dict[str, Any],
        formal_layers: dict[str, dict[str, Any]],
    ) -> tuple[
        list[FactTraceRow],
        list[WeatherFactTrace],
        list[ObservationFactTrace],
        ReconstructionTrace | None,
    ]:
        decision_trace_path = cls._registered_artifact_path(
            root,
            manifest=manifest,
            key="fact_trace",
            filename="fact_trace.jsonl",
            expected_status=formal_layers["decision"]["status"],
        )
        weather_trace_path = cls._registered_artifact_path(
            root,
            manifest=manifest,
            key="weather_fact_trace",
            filename="weather_fact_trace.jsonl",
            expected_status=formal_layers["weather"]["status"],
        )
        observation_trace_path = cls._registered_artifact_path(
            root,
            manifest=manifest,
            key="observation_fact_trace",
            filename="observation_fact_trace.jsonl",
            expected_status=formal_layers[
                "public_operational_observation"
            ]["status"],
        )
        reconstruction_path = cls._registered_artifact_path(
            root,
            manifest=manifest,
            key="reconstruction_trace",
            filename="reconstruction_trace.json",
            expected_status=formal_layers["decision_case_core"]["status"],
        )
        try:
            direct = read_fact_traces(decision_trace_path)
            weather = read_weather_fact_traces(weather_trace_path)
            observations = read_observation_fact_traces(
                observation_trace_path
            )
            reconstruction = (
                read_reconstruction_trace(reconstruction_path)
                if formal_layers["decision_case_core"]["status"] == "ok"
                else None
            )
        except ValueError as exc:
            raise QueryToolError(
                "current run publication evidence is invalid"
            ) from exc
        return direct, weather, observations, reconstruction

    @staticmethod
    def _registered_artifact_path(
        root: Path,
        *,
        manifest: dict[str, Any],
        key: str,
        filename: str,
        expected_status: str,
    ) -> Path:
        context_artifacts = manifest.get("context_artifacts")
        entry = (
            context_artifacts.get(key)
            if isinstance(context_artifacts, dict)
            else None
        )
        if not isinstance(entry, dict):
            raise QueryToolError(
                f"current run manifest does not register {filename}"
            )
        if (
            entry.get("path") != filename
            or entry.get("status") != expected_status
        ):
            raise QueryToolError(
                f"current run {filename} registration is invalid"
            )
        path = root / filename
        if (
            path.is_symlink()
            or not path.exists()
            or not path.is_file()
            or not path.resolve().is_relative_to(root)
        ):
            raise QueryToolError(
                f"current run {filename} is missing or unsafe"
            )
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise QueryToolError(
                f"current run {filename} cannot be read"
            ) from exc
        if (
            not isinstance(entry.get("sha256"), str)
            or hashlib.sha256(data).hexdigest() != entry["sha256"]
        ):
            raise QueryToolError(
                f"current run {filename} checksum mismatch"
            )
        count = sum(1 for line in data.splitlines() if line.strip())
        if (
            not isinstance(entry.get("count"), int)
            or isinstance(entry.get("count"), bool)
            or entry["count"] != count
            or (expected_status != "ok" and count != 0)
        ):
            raise QueryToolError(
                f"current run {filename} row count mismatch"
            )
        return path

    @staticmethod
    def _validated_fact_from_row(
        row: dict[str, Any],
        *,
        profile_registry: ValidationProfileRegistry,
        line_number: int,
    ) -> ValidatedFact:
        ref = ValidationProfileRef(
            profile_id=row["profile_id"],
            profile_checksum=row["profile_checksum"],
            layer=row["validation_layer"],
        )
        profile = profile_registry.resolve(ref)
        try:
            subject_class = QueryGraphStore._profile_iri(
                profile,
                str(row["subject_class"]),
                mapping_kind="class",
            )
            predicate = (
                _RDF_TYPE_IRI
                if row["predicate"] == QueryPredicate.EVENT_TYPE
                else QueryGraphStore._profile_iri(
                    profile,
                    str(row["predicate"]),
                    mapping_kind="property",
                )
            )
            object_class_value = str(row.get("object_class") or "")
            object_class = (
                QueryGraphStore._profile_iri(
                    profile,
                    object_class_value,
                    mapping_kind="class",
                )
                if object_class_value
                else None
            )
            object_value = str(row["object"])
            if predicate == _RDF_TYPE_IRI:
                object_value = QueryGraphStore._profile_iri(
                    profile,
                    object_value,
                    mapping_kind="class",
                )
            evidence_text = str(row.get("evidence_text") or "")
            return ValidatedFact(
                fact_id=str(row["triple_id"]),
                subject_iri=str(row["subject"]),
                subject_class_iri=subject_class,
                predicate_iri=predicate,
                object_kind=row["object_kind"],
                object_value=object_value,
                object_class_iri=object_class,
                datatype_iri=str(row.get("datatype_iri") or "") or None,
                source_ids=list(row["source_ids"]),
                evidence_texts=[evidence_text] if evidence_text else [],
                validation_profile=ref,
                evidence_mode=row["evidence_mode"],
                evidence_ref=str(row["evidence_ref"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise QueryToolError(
                f"graph row {line_number} cannot be reconstructed under "
                f"its validation profile"
            ) from exc

    @staticmethod
    def _profile_iri(
        profile: LoadedValidationProfile,
        value: str,
        *,
        mapping_kind: Literal["class", "property"],
    ) -> str:
        mappings = (
            profile.class_mappings
            if mapping_kind == "class"
            else profile.property_mappings
        )
        mapping = mappings.get(value)
        if mapping is not None:
            return mapping["iri"]
        matches = [
            item["iri"]
            for item in mappings.values()
            if item["iri"] == value
        ]
        if len(matches) == 1:
            return matches[0]
        raise ValueError(
            f"{mapping_kind} is not admitted by profile: {value}"
        )

    @staticmethod
    def _validate_current_fact_row(
        row: dict[str, Any],
        *,
        line_number: int,
        snapshots: SourceSnapshotRegistry,
        profile_refs: set[ValidationProfileRef],
        formal_layers: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        required_fields = {
            "triple_id",
            "subject",
            "predicate",
            "object",
            "subject_class",
            "object_class",
            "object_kind",
            "source_document",
            "evidence_text",
            "profile_id",
            "profile_checksum",
            "validation_layer",
            "evidence_mode",
            "evidence_ref",
            "source_ids",
            "source_snapshot_checksums",
        }
        missing = sorted(required_fields - set(row))
        if missing:
            raise QueryToolError(
                f"graph row {line_number} is not a current profile-owned fact: "
                f"missing {missing[0]}"
            )
        try:
            ref = ValidationProfileRef(
                profile_id=row["profile_id"],
                profile_checksum=row["profile_checksum"],
                layer=row["validation_layer"],
            )
        except ValueError as exc:
            raise QueryToolError(
                f"graph row {line_number} has invalid profile ownership"
            ) from exc
        if ref not in profile_refs:
            raise QueryToolError(
                f"graph row {line_number} profile is absent from materialization"
            )
        if formal_layers[ref.layer]["status"] != "ok":
            raise QueryToolError(
                f"graph row {line_number} belongs to a non-ok formal layer"
            )
        evidence_mode = row.get("evidence_mode")
        if evidence_mode not in {
            "source_text",
            "deterministic_derivation",
            "profile_definition",
            "system_membership",
        }:
            raise QueryToolError(
                f"graph row {line_number} has invalid evidence_mode"
            )
        if not isinstance(row.get("evidence_ref"), str) or not row[
            "evidence_ref"
        ].strip():
            raise QueryToolError(
                f"graph row {line_number} has no evidence_ref"
            )
        source_ids = row.get("source_ids")
        if (
            not isinstance(source_ids, list)
            or any(
                not isinstance(source_id, str) or not source_id.strip()
                for source_id in source_ids
            )
            or len(source_ids) != len(set(source_ids))
        ):
            raise QueryToolError(
                f"graph row {line_number} has invalid source_ids"
            )
        if set(source_ids) != set(_split_source_ids(row["source_document"])):
            raise QueryToolError(
                f"graph row {line_number} source fields disagree"
            )
        checksums = row.get("source_snapshot_checksums")
        if not isinstance(checksums, dict) or set(checksums) != set(source_ids):
            raise QueryToolError(
                f"graph row {line_number} has incomplete snapshot checksums"
            )
        for source_id in source_ids:
            snapshot = snapshots.get(source_id)
            if (
                snapshot is None
                or checksums[source_id] != snapshot.content_sha256
            ):
                raise QueryToolError(
                    f"graph row {line_number} source snapshot checksum mismatch"
                )
        if evidence_mode in {
            "source_text",
            "deterministic_derivation",
        } and not source_ids:
            raise QueryToolError(
                f"graph row {line_number} has no evidence source"
            )
        normalized = dict(row)
        normalized["source_ids"] = list(source_ids)
        return normalized

    @staticmethod
    def _validate_materialized_counts(
        manifest: dict[str, Any],
        rows: list[dict[str, Any]],
        *,
        profile_refs: set[ValidationProfileRef],
        formal_layers: dict[str, dict[str, Any]],
    ) -> None:
        materialization = manifest["materialization"]
        if materialization["fact_count"] != len(rows):
            raise QueryToolError(
                "current run materialization fact count does not match kg.jsonl"
            )
        actual_layer_counts: dict[str, int] = {}
        actual_refs: set[ValidationProfileRef] = set()
        for row in rows:
            layer = str(row["validation_layer"])
            actual_layer_counts[layer] = actual_layer_counts.get(layer, 0) + 1
            actual_refs.add(
                ValidationProfileRef(
                    profile_id=row["profile_id"],
                    profile_checksum=row["profile_checksum"],
                    layer=row["validation_layer"],
                )
            )
        if materialization["layer_fact_counts"] != actual_layer_counts:
            raise QueryToolError(
                "current run materialization layer counts do not match kg.jsonl"
            )
        if actual_refs != profile_refs:
            raise QueryToolError(
                "current run materialization profile refs do not match kg.jsonl"
            )
        for layer, entry in formal_layers.items():
            if entry["formal_fact_count"] != actual_layer_counts.get(layer, 0):
                raise QueryToolError(
                    f"current run formal layer count does not match kg.jsonl: "
                    f"{layer}"
                )

    def _load_profile_gaps(self, root: Path) -> list[PersistedProfileGap]:
        entry = self.manifest.get("profile_gaps")
        if not isinstance(entry, dict):
            raise QueryToolError(
                "current run manifest does not register profile_gaps.jsonl"
            )
        expected_status = self.manifest["formal_layers"]["decision"]["status"]
        if (
            entry.get("path") != "profile_gaps.jsonl"
            or entry.get("status") != expected_status
        ):
            raise QueryToolError(
                "current run profile_gaps.jsonl registration is invalid"
            )
        path = root / "profile_gaps.jsonl"
        if (
            path.is_symlink()
            or not path.exists()
            or not path.is_file()
            or not path.resolve().is_relative_to(root)
        ):
            raise QueryToolError(
                "current run profile_gaps.jsonl is missing or unsafe"
            )
        data = path.read_bytes()
        if (
            not isinstance(entry.get("sha256"), str)
            or hashlib.sha256(data).hexdigest() != entry["sha256"]
        ):
            raise QueryToolError(
                "current run profile_gaps.jsonl checksum mismatch"
            )
        row_count = sum(1 for line in data.splitlines() if line.strip())
        if (
            not isinstance(entry.get("count"), int)
            or isinstance(entry.get("count"), bool)
            or entry["count"] != row_count
            or (expected_status != "ok" and row_count)
        ):
            raise QueryToolError(
                "current run profile_gaps.jsonl row count mismatch"
            )

        gaps: list[PersistedProfileGap] = []
        seen_ids: set[str] = set()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise QueryToolError(
                "current run profile_gaps.jsonl is not valid UTF-8"
            ) from exc
        event_sources = {
            event_id: {
                source_id
                for row in self.rows
                if row["subject"] == event_id
                for source_id in row["source_ids"]
            }
            for event_id in self.event_ids
        }
        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                gap = PersistedProfileGap.model_validate_json(line)
            except Exception as exc:
                raise QueryToolError(
                    f"invalid profile-gap JSON at line {line_number}"
                ) from exc
            if gap.profile_gap_id in seen_ids:
                raise QueryToolError(
                    f"duplicate profile-gap ID: {gap.profile_gap_id}"
                )
            if gap.event_id not in self.event_ids:
                raise QueryToolError(
                    f"profile gap references an unregistered event: {gap.event_id}"
                )
            if gap.source_id not in event_sources[gap.event_id]:
                raise QueryToolError(
                    f"profile gap source is not bound to its event: {gap.profile_gap_id}"
                )
            if gap.source_id != self.manifest.get("source_id"):
                raise QueryToolError(
                    f"profile gap source is not the run advisory: {gap.profile_gap_id}"
                )
            decision_layer = self.manifest["formal_layers"]["decision"]
            expected_profile = ValidationProfileRef(
                profile_id=decision_layer["profile_id"],
                profile_checksum=decision_layer["profile_checksum"],
                layer="decision",
            )
            if gap.validation_profile != expected_profile:
                raise QueryToolError(
                    f"profile gap does not use the current decision profile: "
                    f"{gap.profile_gap_id}"
                )
            guide = load_schema_guide()
            event_class = self.event_class(gap.event_id)
            predicate = {
                "impacting_condition": "atm:impactingCondition",
            }.get(gap.field)
            if (
                predicate is None
                or gap.reason != "not_in_profile"
                or not guide.has_property(predicate)
                or guide.datatype_property_ok(predicate, event_class)
            ):
                raise QueryToolError(
                    f"profile gap has invalid field or schema mapping: "
                    f"{gap.profile_gap_id}"
                )
            seen_ids.add(gap.profile_gap_id)
            gaps.append(gap)
        snapshots = self._load_profile_gap_snapshots(
            {gap.source_id for gap in gaps},
        )
        for gap in gaps:
            snapshot = snapshots.get(gap.source_id)
            if (
                snapshot is None
                or gap.source_snapshot_sha256 != snapshot.content_sha256
            ):
                raise QueryToolError(
                    f"profile gap does not match the run snapshot: {gap.profile_gap_id}"
                )
            if snapshot.family.value != "atcscc_advisory":
                raise QueryToolError(
                    f"profile gap does not use an advisory source: {gap.profile_gap_id}"
                )
            mentions = parse_structured_fields(snapshot.content)
            exact_value = getattr(mentions, gap.field, None)
            exact_evidence = mentions.evidence_spans.get(gap.field)
            if (
                exact_value != gap.value
                or exact_evidence != gap.evidence_text
            ):
                raise QueryToolError(
                    f"profile gap lacks exact field-specific evidence: "
                    f"{gap.profile_gap_id}"
                )
        return gaps

    def _load_profile_gap_snapshots(
        self,
        required_source_ids: set[str],
    ) -> dict[str, SourceSnapshot]:
        if not required_source_ids:
            return {}
        selected = {
            source_id: snapshot
            for source_id in required_source_ids
            if (snapshot := self.source_snapshots.get(source_id)) is not None
        }
        missing = sorted(required_source_ids - set(selected))
        if missing:
            raise QueryToolError(
                "profile-gap source is missing from source_snapshots.jsonl: "
                f"{missing[0]}"
            )
        return selected

    def event_class(self, event_id: str) -> str:
        for row in self.rows:
            if row["subject"] == event_id and row["predicate"] == QueryPredicate.EVENT_TYPE:
                return str(row.get("object") or row.get("subject_class") or "")
        for row in self.rows:
            if row["subject"] == event_id:
                return str(row.get("subject_class") or "")
        return ""

    def get_event_rows(self, *, event_id: str) -> tuple[dict[str, Any], ...]:
        """Return the current validated formal facts for one registered event."""

        if event_id not in self.event_ids:
            raise QueryToolError(f"unregistered event ID: {event_id}")
        return tuple(
            sorted(
                (row for row in self.rows if row["subject"] == event_id),
                key=lambda row: str(row["fact_id"]),
            )
        )
