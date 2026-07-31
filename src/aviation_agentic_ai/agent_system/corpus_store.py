"""Deterministic cross-run storage for validated ATMONTO TMI events."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from aviation_agentic_ai.agent_system.contracts import (
    ObservationFactTrace,
    PersistedProfileGap,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    StrictModel,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.context_artifacts import (
    read_context_associations,
    read_observation_fact_traces,
)
from aviation_agentic_ai.agent_system.corpus_event_graph import CorpusEventGraphView
from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore
from aviation_agentic_ai.agent_system.materialize import (
    build_validated_facts_neo4j_projection,
    write_validated_facts_jsonl,
    write_validated_facts_rdf,
)
from aviation_agentic_ai.agent_system.ontology_alignment import (
    build_corpus_alignment_audit,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.tmi_profiles import (
    active_tmi_profiles,
    registered_tmi_profiles,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


_RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


class CorpusArtifactMetadata(StrictModel):
    """One content-verified artifact in a corpus build."""

    path: str = Field(min_length=1)
    count: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)


class CorpusBuildManifest(StrictModel):
    """Stable summary of one materialized cross-run corpus."""

    manifest_version: Literal["tmi-event-corpus-v3"] = "tmi-event-corpus-v3"
    corpus_id: str = Field(min_length=1)
    run_count: int = Field(ge=0)
    event_count: int = Field(ge=0)
    fact_count: int = Field(ge=0)
    source_binding_count: int = Field(ge=0)
    source_object_count: int = Field(ge=0)
    evidence_link_count: int = Field(default=0, ge=0)
    profile_gap_count: int = Field(default=0, ge=0)
    context_association_count: int = Field(default=0, ge=0)
    observation_count: int = Field(default=0, ge=0)
    artifacts: dict[str, CorpusArtifactMetadata]


class ArtifactRef(StrictModel):
    """One globally deduplicated content-addressed source object."""

    artifact_id: str = Field(min_length=64, max_length=64)
    content_sha256: str = Field(min_length=64, max_length=64)
    object_key: str = Field(min_length=64, max_length=64)


class CorpusFact(ValidatedFact):
    """A verified fact with a semantic, provenance-independent identity."""


class EvidenceLink(StrictModel):
    """One source-artifact link for a fact or non-formal corpus record."""

    evidence_link_id: str = Field(min_length=1)
    owner_kind: Literal["fact", "profile_gap", "context_association", "observation"]
    owner_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    artifact_id: str = Field(min_length=64, max_length=64)
    evidence_text: str | None = None
    evidence_ref: str | None = None


class CorpusProfileGap(PersistedProfileGap):
    """Source-bound profile gap retained outside the formal fact table."""


class CorpusContextAssociation(StrictModel):
    """Stable non-causal event-to-weather association."""

    association_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    report_id: str = Field(min_length=1)
    facility_id: str = Field(min_length=1)
    relation_type: Literal[
        "latest_forecast_known_at_issue",
        "latest_observation_at_or_before_issue",
        "observation_during_operation",
    ]
    selection_method: str = Field(min_length=1)
    relevant_times: dict[str, str] = Field(default_factory=dict)
    source_id: str = Field(min_length=1)
    source_artifact_id: str = Field(min_length=64, max_length=64)
    causal_claim: Literal[False] = False


class CorpusObservation(StrictModel):
    """Query-ready BTS public observation derived from admitted formal facts."""

    observation_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    phase: Literal["baseline", "active", "recovery"]
    metric_key: str = Field(min_length=1)
    value: int | Decimal | None
    unit_iri: str | None = None
    fact_ids: tuple[str, ...]
    profile_id: str = Field(min_length=1)
    profile_checksum: str = Field(min_length=64, max_length=64)
    source_id: str = Field(min_length=1)
    source_artifact_id: str = Field(min_length=64, max_length=64)


class CorpusBuildResult(StrictModel):
    """One selected advisory's corpus-normalization result."""

    source_id: str = Field(min_length=1)
    status: Literal["ok", "insufficient", "blocked"]
    event_id: str | None = None
    reason: str = ""
    provider_call_count: int = Field(default=0, ge=0)
    tmi_family: str | None = None
    preflight_eligible: bool | None = None


class CorpusTMIEvent(StrictModel):
    """Catalog row whose identity is one admitted ATMONTO TMI instance."""

    event_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    event_type_iris: list[str] = Field(default_factory=list)
    facility_ids: list[str] = Field(default_factory=list)
    effective_start: datetime | None = None
    effective_end: datetime | None = None
    issued_at: datetime | None = None
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None = None
    fact_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)

    @field_validator("effective_start", "effective_end", "issued_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        """Reject ambiguous local timestamps in the canonical event catalog."""

        if value is not None and value.tzinfo is None:
            raise ValueError("TMI event timestamps must include a timezone")
        return value


class CorpusSourceBinding(StrictModel):
    """Bind one event source to a shared content-addressed object."""

    event_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_family: str = Field(min_length=1)
    source_url: str | None = None
    snapshot_timestamps: list[str] = Field(min_length=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    object_key: str = Field(min_length=64, max_length=64)


class CorpusEventFact(StrictModel):
    """Corpus membership edge from one TMI event to an admitted fact."""

    event_id: str = Field(min_length=1)
    fact_id: str = Field(min_length=1)


class CorpusEventQuery(StrictModel):
    """Exact, bounded filters over the normalized event catalog."""

    event_type_iri: str | None = Field(default=None, min_length=1)
    facility_id: str | None = Field(default=None, min_length=1)
    reason_status: Literal["formal", "profile_gap", "missing"] | None = None
    reason_value: str | None = Field(default=None, min_length=1)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class CorpusEventPage(StrictModel):
    """One deterministic page of exact event-catalog matches."""

    corpus_id: str = Field(min_length=1)
    total_matches: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    events: tuple[CorpusTMIEvent, ...] = ()


class CorpusQueryStore:
    """Read-only indexed view of one normalized TMI-event corpus."""

    _REQUIRED_ARTIFACTS = (
        "events",
        "facts",
        "event_facts",
        "source_bindings",
    )
    _OPTIONAL_ARTIFACTS = (
        "evidence_links",
        "profile_gaps",
        "context_associations",
        "observations",
    )

    def __init__(self, corpus_dir: str | Path) -> None:
        root = Path(corpus_dir).resolve()
        manifest_path = root / "corpus_manifest.json"
        try:
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("invalid corpus manifest") from exc
        if manifest_payload.get("manifest_version") != "tmi-event-corpus-v3":
            raise ValueError(
                "unsupported corpus manifest; rebuild the corpus as tmi-event-corpus-v3"
            )
        try:
            manifest = CorpusBuildManifest.model_validate(manifest_payload)
        except ValueError as exc:
            raise ValueError("invalid corpus manifest") from exc

        artifact_rows: dict[str, list[dict[str, object]]] = {}
        for name in (*self._REQUIRED_ARTIFACTS, *self._OPTIONAL_ARTIFACTS):
            metadata = manifest.artifacts.get(name)
            if metadata is None and name in self._REQUIRED_ARTIFACTS:
                raise ValueError(f"corpus manifest is missing artifact: {name}")
            if metadata is None:
                artifact_rows[name] = []
                continue
            path = (root / metadata.path).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError(f"corpus artifact is missing: {name}")
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != metadata.sha256:
                raise ValueError(f"corpus artifact checksum mismatch: {name}")
            rows = _read_jsonl(path)
            if len(rows) != metadata.count:
                raise ValueError(f"corpus artifact count mismatch: {name}")
            artifact_rows[name] = rows

        events = tuple(
            CorpusTMIEvent.model_validate(row)
            for row in artifact_rows["events"]
        )
        facts = tuple(
            CorpusFact.model_validate(row)
            for row in artifact_rows["facts"]
        )
        memberships = tuple(
            CorpusEventFact.model_validate(row)
            for row in artifact_rows["event_facts"]
        )
        self.source_bindings = tuple(
            CorpusSourceBinding.model_validate(row)
            for row in artifact_rows["source_bindings"]
        )
        self.evidence_links = tuple(
            EvidenceLink.model_validate(row)
            for row in artifact_rows["evidence_links"]
        )
        self.profile_gaps = tuple(
            CorpusProfileGap.model_validate(row)
            for row in artifact_rows["profile_gaps"]
        )
        self.context_associations = tuple(
            CorpusContextAssociation.model_validate(row)
            for row in artifact_rows["context_associations"]
        )
        self.observations = tuple(
            CorpusObservation.model_validate(row)
            for row in artifact_rows["observations"]
        )
        self.root = root
        self.manifest = manifest
        self.events = tuple(sorted(events, key=lambda row: row.event_id))
        self.facts = tuple(sorted(facts, key=lambda row: row.fact_id))
        self._event_by_id = {event.event_id: event for event in self.events}
        self._fact_by_id = {fact.fact_id: fact for fact in self.facts}
        source_artifacts_by_event: dict[str, set[tuple[str, str]]] = defaultdict(set)
        for binding in self.source_bindings:
            source_artifacts_by_event[binding.event_id].add(
                (binding.source_id, binding.content_sha256)
            )
        self._source_artifacts_by_event = {
            event_id: frozenset(source_artifacts)
            for event_id, source_artifacts in source_artifacts_by_event.items()
        }
        source_artifacts_by_fact: dict[str, set[tuple[str, str]]] = defaultdict(set)
        for link in self.evidence_links:
            if link.owner_kind == "fact":
                source_artifacts_by_fact[link.owner_id].add(
                    (link.source_id, link.artifact_id)
                )
        self._source_artifacts_by_fact = {
            fact_id: frozenset(source_artifacts)
            for fact_id, source_artifacts in source_artifacts_by_fact.items()
        }
        self._fact_ids_by_event: dict[str, tuple[str, ...]] = {}
        for event in self.events:
            self._fact_ids_by_event[event.event_id] = tuple(
                sorted(
                    row.fact_id
                    for row in memberships
                    if row.event_id == event.event_id
                )
            )

    @property
    def event_ids(self) -> tuple[str, ...]:
        """Return all corpus events in deterministic order."""

        return tuple(event.event_id for event in self.events)

    def find_events(
        self,
        filters: CorpusEventQuery | dict[str, object] | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> CorpusEventPage:
        """Return one page of exact catalog matches."""

        query = (
            filters
            if isinstance(filters, CorpusEventQuery)
            else CorpusEventQuery.model_validate(
                {
                    **(filters or {}),
                    **({"offset": offset} if offset is not None else {}),
                    **({"limit": limit} if limit is not None else {}),
                }
            )
        )

        matches = [
            event
            for event in self.events
            if (
                query.event_type_iri is None
                or query.event_type_iri in event.event_type_iris
            )
            and (
                query.facility_id is None
                or query.facility_id in event.facility_ids
            )
            and (
                query.reason_status is None
                or query.reason_status == event.reason_status
            )
            and (
                query.reason_value is None
                or query.reason_value == event.reason_value
            )
        ]
        return CorpusEventPage(
            corpus_id=self.manifest.corpus_id,
            total_matches=len(matches),
            offset=query.offset,
            limit=query.limit,
            events=tuple(matches[query.offset : query.offset + query.limit]),
        )

    def get_event(self, event_id: str) -> CorpusTMIEvent | None:
        """Return one catalog row by its canonical TMI event ID."""

        return self._event_by_id.get(event_id)

    def get_event_facts(self, event_id: str) -> tuple[CorpusFact, ...]:
        """Return all admitted formal facts assigned to one TMI event."""

        event = self.get_event(event_id)
        if event is None:
            return ()
        event_source_artifacts = self._source_artifacts_by_event.get(
            event.event_id,
            frozenset(),
        )
        return tuple(
            self._fact_by_id[fact_id].model_copy(
                update={
                    "source_ids": sorted(
                        set(self._fact_by_id[fact_id].source_ids)
                        & {
                            source_id
                            for source_id, artifact_id in (
                                self._source_artifacts_by_fact.get(
                                    fact_id,
                                    frozenset(),
                                )
                            )
                            if (source_id, artifact_id) in event_source_artifacts
                        }
                    )
                }
            )
            for fact_id in self._fact_ids_by_event.get(event.event_id, ())
            if fact_id in self._fact_by_id
        )

    def graph_for_event(self, event_id: str) -> CorpusEventGraphView:
        """Build one read-only graph view over only the selected event."""

        return CorpusEventGraphView(self.get_event_facts(event_id))

    def get_weather_context(
        self, event_id: str
    ) -> tuple[CorpusContextAssociation, ...]:
        """Return non-causal weather associations for one selected event."""

        return tuple(
            sorted(
                (
                    row
                    for row in self.context_associations
                    if row.event_id == event_id
                ),
                key=lambda row: row.association_id,
            )
        )

    def get_public_observations(
        self,
        event_id: str,
        phases: tuple[str, ...] | list[str] | None = None,
    ) -> tuple[CorpusObservation, ...]:
        """Return selected BTS public observations without creating a model."""

        selected_phases = set(phases) if phases is not None else None
        return tuple(
            sorted(
                (
                    row
                    for row in self.observations
                    if row.event_id == event_id
                    and (
                        selected_phases is None
                        or row.phase in selected_phases
                    )
                ),
                key=lambda row: row.observation_id,
            )
        )

    def get_event_evidence(self, event_id: str) -> tuple[EvidenceLink, ...]:
        """Return evidence links owned by the selected event's retained rows."""

        event = self.get_event(event_id)
        if event is None:
            return ()
        owner_ids = {
            *self._fact_ids_by_event.get(event.event_id, ()),
            *(row.profile_gap_id for row in self.profile_gaps if row.event_id == event_id),
            *(row.association_id for row in self.context_associations if row.event_id == event_id),
            *(row.observation_id for row in self.observations if row.event_id == event_id),
        }
        return tuple(
            sorted(
                (row for row in self.evidence_links if row.owner_id in owner_ids),
                key=lambda row: row.evidence_link_id,
            )
        )


def _formal_event_types(
    facts: list[ValidatedFact],
    *,
    event_id: str,
) -> tuple[str, ...]:
    """Return the admitted ATMONTO type that establishes a TMI event."""

    event_types = {
        fact.object_value
        for fact in facts
        if fact.subject_iri == event_id
        and fact.validation_profile.layer == "decision"
        if fact.predicate_iri == _RDF_TYPE_IRI
    }
    active_types = {
        profile.ontology_class
        for profile in active_tmi_profiles()
        if profile.ontology_class is not None
    }
    admitted_types = event_types & active_types
    if len(admitted_types) != 1:
        raise ValueError(
            "corpus event requires exactly one admitted ATMONTO TMI type"
        )
    return tuple(sorted(admitted_types))


def _build_tmi_coverage(
    results: list[CorpusBuildResult],
    events: list[CorpusTMIEvent],
) -> dict[str, object]:
    """Build one deterministic coverage summary from selected rows and events."""

    profiles = registered_tmi_profiles()
    profiles_by_code = {profile.code: profile for profile in profiles}
    exact_class_to_code = {
        profile.ontology_class: profile.code
        for profile in profiles
        if profile.ontology_class is not None
    }
    event_family_by_source: dict[str, str] = {}
    published_counts: dict[str, int] = defaultdict(int)
    for event in events:
        matches = {
            exact_class_to_code[event_type]
            for event_type in event.event_type_iris
            if event_type in exact_class_to_code
        }
        family = next(iter(matches)) if len(matches) == 1 else "UNCLASSIFIED"
        event_family_by_source[event.advisory_source_id] = family
        published_counts[family] += 1

    counters: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "detected_count": 0,
            "eligible_count": 0,
            "eligibility_unknown_count": 0,
            "ok_count": 0,
            "insufficient_count": 0,
            "blocked_count": 0,
            "published_count": 0,
        }
    )
    for result in results:
        family = (
            result.tmi_family
            or event_family_by_source.get(result.source_id)
            or "UNCLASSIFIED"
        )
        counters[family]["detected_count"] += 1
        if result.preflight_eligible is True:
            counters[family]["eligible_count"] += 1
        elif result.preflight_eligible is None:
            counters[family]["eligibility_unknown_count"] += 1
        counters[family][f"{result.status}_count"] += 1
    for family, count in published_counts.items():
        counters[family]["published_count"] = count

    family_order = [profile.code for profile in profiles]
    if "UNCLASSIFIED" in counters:
        family_order.append("UNCLASSIFIED")
    families = []
    for family in family_order:
        profile = profiles_by_code.get(family)
        families.append(
            {
                "family": family,
                "publication_status": (
                    profile.publication_status
                    if profile is not None
                    else "unclassified"
                ),
                "ontology_class": (
                    profile.ontology_class if profile is not None else None
                ),
                **counters[family],
            }
        )
    return {
        "report_version": "tmi-coverage-v1",
        "selected_count": len(results),
        "eligible_count": sum(
            result.preflight_eligible is True for result in results
        ),
        "eligibility_unknown_count": sum(
            result.preflight_eligible is None for result in results
        ),
        "published_event_count": len(events),
        "families": families,
    }


def build_corpus(
    run_dirs: list[str | Path] | tuple[str | Path, ...],
    output_dir: str | Path,
    *,
    build_results: list[CorpusBuildResult] | tuple[CorpusBuildResult, ...] | None = None,
) -> CorpusBuildManifest:
    """Normalize validated runs into a provenance-aware TMI-event corpus.

    Facts are merged by semantic content.  Their source IDs, verbatim evidence,
    and source-object versions are retained as ``EvidenceLink`` rows rather
    than participating in fact identity.
    """

    stores = [
        QueryGraphStore(run_dir)
        for run_dir in sorted(run_dirs, key=lambda value: str(Path(value).resolve()))
    ]
    facts_by_id: dict[str, CorpusFact] = {}
    events_by_id: dict[str, CorpusTMIEvent] = {}
    bindings_by_id: dict[tuple[str, str, str], CorpusSourceBinding] = {}
    event_facts_by_id: dict[tuple[str, str], CorpusEventFact] = {}
    source_objects: dict[str, str] = {}
    evidence_links_by_id: dict[str, EvidenceLink] = {}
    gaps_by_id: dict[str, CorpusProfileGap] = {}
    associations_by_id: dict[str, CorpusContextAssociation] = {}
    observations_by_id: dict[str, CorpusObservation] = {}
    build_results_by_event: dict[str, CorpusBuildResult] = {}

    for store in stores:
        if len(store.event_ids) != 1:
            raise ValueError("each corpus run must contain exactly one event")
        event_id = store.event_ids[0]
        facts = sorted(store.validated_facts, key=lambda fact: fact.fact_id)
        event_type_iris = _formal_event_types(
            facts,
            event_id=event_id,
        )
        semantic_ids_by_run_fact_id: dict[str, str] = {}

        for fact in facts:
            semantic_id = _semantic_fact_id(fact)
            semantic_ids_by_run_fact_id[fact.fact_id] = semantic_id
            payload = _canonical_fact_payload(fact, fact_id=semantic_id)
            corpus_fact = CorpusFact.model_validate(payload)
            previous = facts_by_id.get(semantic_id)
            if previous is None:
                facts_by_id[semantic_id] = corpus_fact
            else:
                facts_by_id[semantic_id] = _merge_fact_provenance(
                    previous,
                    corpus_fact,
                )
            membership = CorpusEventFact(
                event_id=event_id,
                fact_id=semantic_id,
            )
            event_facts_by_id[(event_id, semantic_id)] = membership

        event_facts = [
            fact for fact in facts if fact.subject_iri == event_id
        ]
        event_profile = next(
            (
                profile
                for profile in active_tmi_profiles()
                if profile.ontology_class in event_type_iris
            ),
            None,
        )
        formal_reason_predicates = {
            predicate
            for field in ("impacting_condition", "re_route_reason")
            if event_profile is not None
            and (predicate := event_profile.field_mappings.get(field))
        }
        formal_reasons = sorted(
            {
                fact.object_value
                for fact in event_facts
                if fact.predicate_iri in formal_reason_predicates
            }
        )
        reason_gaps = sorted(
            (
                gap
                for gap in store.profile_gaps
                if gap.event_id == event_id
                and gap.field == "impacting_condition"
            ),
            key=lambda gap: gap.profile_gap_id,
        )
        if formal_reasons:
            reason_status = "formal"
            reason_value = formal_reasons[0]
        elif reason_gaps:
            reason_status = "profile_gap"
            reason_value = reason_gaps[0].value
        else:
            reason_status = "missing"
            reason_value = None

        snapshots = sorted(
            store.source_snapshots.snapshots,
            key=lambda snapshot: snapshot.source_id,
        )
        for snapshot in snapshots:
            source_objects.setdefault(
                snapshot.content_sha256,
                snapshot.content,
            )
            binding = CorpusSourceBinding(
                event_id=event_id,
                source_id=snapshot.source_id,
                source_family=snapshot.family.value,
                source_url=snapshot.source_url,
                snapshot_timestamps=[snapshot.snapshot_timestamp],
                content_sha256=snapshot.content_sha256,
                object_key=snapshot.content_sha256,
            )
            binding_key = (
                event_id,
                snapshot.source_id,
                snapshot.content_sha256,
            )
            previous_binding = bindings_by_id.get(binding_key)
            if previous_binding is not None:
                previous_payload = previous_binding.model_dump(mode="json")
                current_payload = binding.model_dump(mode="json")
                previous_payload.pop("snapshot_timestamps")
                current_payload.pop("snapshot_timestamps")
                if previous_payload != current_payload:
                    raise ValueError(
                        f"conflicting source binding for event: {event_id}"
                    )
                binding = previous_binding.model_copy(
                    update={
                        "snapshot_timestamps": sorted(
                            set(previous_binding.snapshot_timestamps)
                            | set(binding.snapshot_timestamps)
                        )
                    }
                )
            bindings_by_id[binding_key] = binding

        for fact in facts:
            semantic_id = semantic_ids_by_run_fact_id[fact.fact_id]
            for source_id in fact.source_ids:
                artifact_id = _source_artifact_id(store, source_id)
                for evidence_text in fact.evidence_texts or [None]:
                    link = _evidence_link(
                        owner_kind="fact",
                        owner_id=semantic_id,
                        source_id=source_id,
                        artifact_id=artifact_id,
                        evidence_text=evidence_text,
                        evidence_ref=fact.evidence_ref,
                    )
                    evidence_links_by_id[link.evidence_link_id] = link

        for gap in store.profile_gaps:
            corpus_gap = CorpusProfileGap.model_validate(gap.model_dump(mode="json"))
            gaps_by_id[corpus_gap.profile_gap_id] = corpus_gap
            artifact_id = _source_artifact_id(store, corpus_gap.source_id)
            link = _evidence_link(
                owner_kind="profile_gap",
                owner_id=corpus_gap.profile_gap_id,
                source_id=corpus_gap.source_id,
                artifact_id=artifact_id,
                evidence_text=corpus_gap.evidence_text,
                evidence_ref=corpus_gap.evidence_ref,
            )
            evidence_links_by_id[link.evidence_link_id] = link

        for association in _optional_context_associations(store):
            artifact_id = _source_artifact_id(store, association.source_id)
            corpus_association = CorpusContextAssociation(
                association_id=stable_id(
                    "corpus-weather-association",
                    association.event_id,
                    association.report_id,
                    association.facility_id,
                    association.relation_type,
                    association.selection_method,
                    _canonical_json(association.relevant_times),
                    association.source_id,
                    artifact_id,
                ),
                event_id=association.event_id,
                report_id=association.report_id,
                facility_id=association.facility_id,
                relation_type=association.relation_type,
                selection_method=association.selection_method,
                relevant_times=association.relevant_times,
                source_id=association.source_id,
                source_artifact_id=artifact_id,
                causal_claim=False,
            )
            associations_by_id[corpus_association.association_id] = corpus_association
            link = _evidence_link(
                owner_kind="context_association",
                owner_id=corpus_association.association_id,
                source_id=association.source_id,
                artifact_id=artifact_id,
            )
            evidence_links_by_id[link.evidence_link_id] = link

        for trace in _optional_observation_traces(store):
            observation = _corpus_observation(
                event_id=event_id,
                trace=trace,
                run_facts=facts,
                semantic_ids_by_run_fact_id=semantic_ids_by_run_fact_id,
            )
            observations_by_id[observation.observation_id] = observation
            link = _evidence_link(
                owner_kind="observation",
                owner_id=observation.observation_id,
                source_id=observation.source_id,
                artifact_id=observation.source_artifact_id,
            )
            evidence_links_by_id[link.evidence_link_id] = link

        event = CorpusTMIEvent(
            event_id=event_id,
            advisory_source_id=str(store.manifest["source_id"]),
            event_type_iris=sorted(event_type_iris),
            facility_ids=sorted(
                {
                    fact.object_value
                    for fact in event_facts
                    if _local_name(fact.predicate_iri)
                    == "controlledNASelement"
                }
            ),
            effective_start=_first_object(
                event_facts,
                "effectiveStartTime",
            ),
            effective_end=_first_object(
                event_facts,
                "effectiveEndTime",
            ),
            issued_at=_first_object(event_facts, "issuedTime"),
            reason_status=reason_status,
            reason_value=reason_value,
            fact_ids=sorted(set(semantic_ids_by_run_fact_id.values())),
            source_ids=[snapshot.source_id for snapshot in snapshots],
        )
        previous_event = events_by_id.get(event_id)
        if previous_event is None:
            events_by_id[event_id] = event
        else:
            previous_payload = previous_event.model_dump(mode="json")
            current_payload = event.model_dump(mode="json")
            previous_payload.pop("fact_ids")
            previous_payload.pop("source_ids")
            current_payload.pop("fact_ids")
            current_payload.pop("source_ids")
            if previous_payload != current_payload:
                raise ValueError(f"conflicting event content for event ID: {event_id}")
            events_by_id[event_id] = previous_event.model_copy(
                update={
                    "fact_ids": sorted(
                        set(previous_event.fact_ids) | set(event.fact_ids)
                    ),
                    "source_ids": sorted(
                        set(previous_event.source_ids) | set(event.source_ids)
                    ),
                }
            )

        result = CorpusBuildResult(
            source_id=str(store.manifest["source_id"]),
            status="ok",
            event_id=event_id,
            reason="validated run normalized",
            provider_call_count=len(store.manifest.get("model_calls") or []),
            tmi_family=(event_profile.code if event_profile is not None else None),
            preflight_eligible=True,
        )
        previous_result = build_results_by_event.get(event_id)
        if previous_result is None or result.source_id < previous_result.source_id:
            build_results_by_event[event_id] = result

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    object_dir = output / "source_objects"
    object_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, CorpusArtifactMetadata] = {}
    for object_key, content in sorted(source_objects.items()):
        object_path = object_dir / f"{object_key}.txt"
        object_path.write_text(content, encoding="utf-8")
    artifact_refs_path = output / "artifacts.jsonl"
    build_results_path = output / "build_results.jsonl"
    bindings_path = output / "source_bindings.jsonl"
    events_path = output / "events.jsonl"
    facts_path = output / "facts.jsonl"
    event_facts_path = output / "event_facts.jsonl"
    evidence_links_path = output / "evidence_links.jsonl"
    profile_gaps_path = output / "profile_gaps.jsonl"
    associations_path = output / "context_associations.jsonl"
    observations_path = output / "observations.jsonl"
    alignment_audit_path = output / "alignment_audit.json"
    tmi_coverage_path = output / "tmi_coverage.json"
    kg_path = output / "kg.jsonl"
    ttl_path = output / "kg.ttl"
    neo4j_nodes_path = output / "neo4j_nodes.jsonl"
    neo4j_relationships_path = output / "neo4j_relationships.jsonl"
    inferred_results_by_source = {
        row.source_id: row
        for row in build_results_by_event.values()
    }
    raw_result_rows = (
        sorted(build_results, key=lambda row: row.source_id)
        if build_results is not None
        else sorted(
            build_results_by_event.values(),
            key=lambda row: (row.event_id or "", row.source_id),
        )
    )
    result_rows = [
        row.model_copy(
            update={
                "tmi_family": (
                    row.tmi_family
                    or getattr(
                        inferred_results_by_source.get(row.source_id),
                        "tmi_family",
                        None,
                    )
                ),
                "preflight_eligible": (
                    row.preflight_eligible
                    if row.preflight_eligible is not None
                    else getattr(
                        inferred_results_by_source.get(row.source_id),
                        "preflight_eligible",
                        None,
                    )
                ),
            }
        )
        for row in raw_result_rows
    ]
    if build_results is not None and len({row.source_id for row in result_rows}) != len(result_rows):
        raise ValueError("corpus build results must have one row per source ID")
    _write_jsonl(
        build_results_path,
        [
            row.model_dump(mode="json")
            for row in result_rows
        ],
    )
    _write_jsonl(
        artifact_refs_path,
        [
            ArtifactRef(
                artifact_id=object_key,
                content_sha256=object_key,
                object_key=object_key,
            ).model_dump(mode="json")
            for object_key in sorted(source_objects)
        ],
    )
    _write_jsonl(
        bindings_path,
        [
            binding.model_dump(mode="json")
            for binding in sorted(
                bindings_by_id.values(),
                key=lambda row: (row.event_id, row.source_id, row.object_key),
            )
        ],
    )
    _write_jsonl(
        events_path,
        [
            event.model_dump(mode="json")
            for event in sorted(events_by_id.values(), key=lambda row: row.event_id)
        ],
    )
    _write_jsonl(
        facts_path,
        [
            facts_by_id[fact_id].model_dump(mode="json")
            for fact_id in sorted(facts_by_id)
        ],
    )
    _write_jsonl(
        event_facts_path,
        [
            row.model_dump(mode="json")
            for row in sorted(
                event_facts_by_id.values(),
                key=lambda value: (value.event_id, value.fact_id),
            )
        ],
    )
    _write_jsonl(
        evidence_links_path,
        [
            row.model_dump(mode="json")
            for row in sorted(evidence_links_by_id.values(), key=lambda row: row.evidence_link_id)
        ],
    )
    _write_jsonl(
        profile_gaps_path,
        [
            row.model_dump(mode="json")
            for row in sorted(gaps_by_id.values(), key=lambda row: row.profile_gap_id)
        ],
    )
    _write_jsonl(
        associations_path,
        [
            row.model_dump(mode="json")
            for row in sorted(associations_by_id.values(), key=lambda row: row.association_id)
        ],
    )
    _write_jsonl(
        observations_path,
        [
            row.model_dump(mode="json")
            for row in sorted(observations_by_id.values(), key=lambda row: row.observation_id)
        ],
    )
    alignment_audit_path.write_text(
        json.dumps(
            build_corpus_alignment_audit(facts_by_id.values()),
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    tmi_coverage_path.write_text(
        json.dumps(
            _build_tmi_coverage(
                result_rows,
                list(events_by_id.values()),
            ),
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_corpus_projection(
        output_dir=output,
        facts=list(facts_by_id.values()),
        evidence_links=list(evidence_links_by_id.values()),
        bindings=list(bindings_by_id.values()),
        source_objects=source_objects,
    )
    for name, path, count in (
        ("build_results", build_results_path, len(result_rows)),
        ("artifacts", artifact_refs_path, len(source_objects)),
        ("source_bindings", bindings_path, len(bindings_by_id)),
        ("events", events_path, len(events_by_id)),
        ("facts", facts_path, len(facts_by_id)),
        ("event_facts", event_facts_path, len(event_facts_by_id)),
        ("evidence_links", evidence_links_path, len(evidence_links_by_id)),
        ("profile_gaps", profile_gaps_path, len(gaps_by_id)),
        ("context_associations", associations_path, len(associations_by_id)),
        ("observations", observations_path, len(observations_by_id)),
        ("alignment_audit", alignment_audit_path, 1),
        ("tmi_coverage", tmi_coverage_path, 1),
        ("kg", kg_path, _jsonl_count(kg_path)),
        ("kg_ttl", ttl_path, _jsonl_count(ttl_path)),
        ("neo4j_nodes", neo4j_nodes_path, _jsonl_count(neo4j_nodes_path)),
        ("neo4j_relationships", neo4j_relationships_path, _jsonl_count(neo4j_relationships_path)),
    ):
        artifacts[name] = _artifact_metadata(output, path, count=count)
    artifacts["source_objects"] = _source_objects_metadata(
        output,
        source_objects,
    )

    corpus_seed = {
        name: artifact.sha256
        for name, artifact in sorted(artifacts.items())
    }
    corpus_id = hashlib.sha256(
        _canonical_json(corpus_seed).encode("utf-8")
    ).hexdigest()
    manifest = CorpusBuildManifest(
        corpus_id=corpus_id,
        run_count=len(stores),
        event_count=len(events_by_id),
        fact_count=len(facts_by_id),
        source_binding_count=len(bindings_by_id),
        source_object_count=len(source_objects),
        evidence_link_count=len(evidence_links_by_id),
        profile_gap_count=len(gaps_by_id),
        context_association_count=len(associations_by_id),
        observation_count=len(observations_by_id),
        artifacts=artifacts,
    )
    (output / "corpus_manifest.json").write_text(
        json.dumps(
            manifest.model_dump(mode="json"),
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def load_event_catalog(corpus_dir: str | Path) -> tuple[CorpusTMIEvent, ...]:
    """Load the stable TMI event catalog for a materialized corpus."""

    return tuple(
        CorpusTMIEvent.model_validate(row)
        for row in _read_jsonl(Path(corpus_dir) / "events.jsonl")
    )


def load_corpus_facts(
    corpus_dir: str | Path,
    event_id: str | None = None,
) -> tuple[CorpusFact, ...]:
    """Load canonical facts, optionally restricted to one TMI event."""

    root = Path(corpus_dir)
    facts = {
        fact.fact_id: fact
        for fact in (
            CorpusFact.model_validate(row)
            for row in _read_jsonl(root / "facts.jsonl")
        )
    }
    if event_id is None:
        selected_ids = set(facts)
    else:
        selected_ids = {
            str(row["fact_id"])
            for row in _read_jsonl(root / "event_facts.jsonl")
            if str(row.get("event_id") or "") == event_id
        }
    return tuple(
        facts[fact_id]
        for fact_id in sorted(selected_ids)
        if fact_id in facts
    )


def export_event(
    *,
    corpus_dir: str | Path,
    event_id: str,
    output_dir: str | Path,
) -> Path:
    """Write a bounded, non-replayable artifact bundle for one TMI event."""

    store = CorpusQueryStore(corpus_dir)
    event = store.get_event(event_id)
    if event is None:
        raise ValueError("requested event is not present in this corpus")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    facts = list(store.get_event_facts(event_id))
    event_facts = [
        CorpusEventFact(event_id=event_id, fact_id=fact.fact_id)
        for fact in facts
    ]
    gaps = [row for row in store.profile_gaps if row.event_id == event_id]
    associations = list(store.get_weather_context(event_id))
    observations = list(store.get_public_observations(event_id))
    evidence = list(store.get_event_evidence(event_id))
    bindings = [
        CorpusSourceBinding.model_validate(row)
        for row in _read_jsonl(store.root / "source_bindings.jsonl")
        if str(row.get("event_id") or "") == event.event_id
    ]
    _write_jsonl(output / "facts.jsonl", [row.model_dump(mode="json") for row in facts])
    _write_jsonl(
        output / "event_facts.jsonl",
        [row.model_dump(mode="json") for row in event_facts],
    )
    _write_jsonl(
        output / "evidence_links.jsonl",
        [row.model_dump(mode="json") for row in evidence],
    )
    _write_jsonl(
        output / "profile_gaps.jsonl", [row.model_dump(mode="json") for row in gaps]
    )
    _write_jsonl(
        output / "context_associations.jsonl",
        [row.model_dump(mode="json") for row in associations],
    )
    _write_jsonl(
        output / "observations.jsonl", [row.model_dump(mode="json") for row in observations]
    )
    _write_jsonl(
        output / "source_bindings.jsonl",
        [row.model_dump(mode="json") for row in bindings],
    )
    (output / "event.json").write_text(
        json.dumps(event.model_dump(mode="json"), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    source_objects = {
        binding.object_key: (store.root / "source_objects" / f"{binding.object_key}.txt")
        for binding in bindings
    }
    object_dir = output / "source_objects"
    object_dir.mkdir(exist_ok=True)
    for object_key, source_path in sorted(source_objects.items()):
        (object_dir / f"{object_key}.txt").write_bytes(source_path.read_bytes())
    _write_corpus_projection(
        output_dir=output,
        facts=facts,
        evidence_links=evidence,
        bindings=bindings,
        source_objects={
            object_key: source_path.read_text(encoding="utf-8")
            for object_key, source_path in source_objects.items()
        },
        include_jsonl=False,
        include_neo4j=False,
    )
    (output / "tmi_event_export_manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "tmi-event-export-v1",
                "corpus_id": store.manifest.corpus_id,
                "event_id": event_id,
            },
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return output


def _projection_inputs(
    *,
    facts: list[CorpusFact],
    evidence_links: list[EvidenceLink],
    bindings: list[CorpusSourceBinding],
    source_objects: dict[str, str],
) -> tuple[list[ValidatedFact], SourceSnapshotRegistry]:
    """Bind projection provenance to content-addressed source artifacts."""

    binding_by_artifact = {
        row.object_key: row
        for row in sorted(bindings, key=lambda row: (row.object_key, row.source_id))
    }
    links_by_fact: dict[str, list[EvidenceLink]] = {}
    for link in evidence_links:
        if link.owner_kind == "fact":
            links_by_fact.setdefault(link.owner_id, []).append(link)
    artifact_ids = sorted(
        {
            link.artifact_id
            for rows in links_by_fact.values()
            for link in rows
        }
    )
    snapshots = []
    for artifact_id in artifact_ids:
        binding = binding_by_artifact.get(artifact_id)
        content = source_objects.get(artifact_id)
        if binding is None or content is None:
            raise ValueError("corpus projection source artifact is missing")
        snapshots.append(
            SourceSnapshot(
                source_id=f"artifact:{artifact_id}",
                family=SourceFamily(binding.source_family),
                source_url=binding.source_url,
                content=content,
                content_sha256=artifact_id,
                snapshot_timestamp=min(binding.snapshot_timestamps),
            )
        )
    projected_facts = []
    for fact in sorted(facts, key=lambda row: row.fact_id):
        links = links_by_fact.get(fact.fact_id, [])
        projected_facts.append(
            fact.model_copy(
                update={
                    "source_ids": sorted(
                        {f"artifact:{link.artifact_id}" for link in links}
                    )
                }
            )
        )
    if not snapshots and projected_facts:
        raise ValueError("corpus projection facts have no evidence links")
    return projected_facts, SourceSnapshotRegistry(snapshots=tuple(snapshots))


def _write_corpus_projection(
    *,
    output_dir: Path,
    facts: list[CorpusFact],
    evidence_links: list[EvidenceLink],
    bindings: list[CorpusSourceBinding],
    source_objects: dict[str, str],
    include_jsonl: bool = True,
    include_neo4j: bool = True,
) -> None:
    """Materialize only formal corpus facts; context remains audit-only."""

    if not facts:
        if include_jsonl:
            _write_jsonl(output_dir / "kg.jsonl", [])
        (output_dir / "kg.ttl").write_text("", encoding="utf-8")
        if include_neo4j:
            _write_jsonl(output_dir / "neo4j_nodes.jsonl", [])
            _write_jsonl(output_dir / "neo4j_relationships.jsonl", [])
        return

    projected_facts, snapshots = _projection_inputs(
        facts=facts,
        evidence_links=evidence_links,
        bindings=bindings,
        source_objects=source_objects,
    )
    profiles = load_validation_profile_registry(decision_guide=load_schema_guide())
    if include_jsonl:
        write_validated_facts_jsonl(
            facts=projected_facts,
            output_dir=output_dir,
            profile_registry=profiles,
            source_snapshot=snapshots,
        )
    write_validated_facts_rdf(
        facts=projected_facts,
        output_dir=output_dir,
        profile_registry=profiles,
        source_snapshot=snapshots,
    )
    _canonicalize_turtle(output_dir / "kg.ttl")
    if include_neo4j:
        build_validated_facts_neo4j_projection(
            facts=projected_facts,
            output_dir=output_dir,
            profile_registry=profiles,
            source_snapshot=snapshots,
        )


def _jsonl_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line)


def _canonicalize_turtle(path: Path) -> None:
    """Write a byte-stable N-Triples corpus projection at the RDF artifact path."""

    from rdflib import Graph

    graph = Graph().parse(path, format="turtle")
    rows = sorted(graph.serialize(format="nt").splitlines())
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def _canonical_fact_payload(
    fact: ValidatedFact,
    *,
    fact_id: str | None = None,
) -> dict[str, object]:
    payload = fact.model_dump(mode="json")
    if fact_id is not None:
        payload["fact_id"] = fact_id
    payload["source_ids"] = sorted(payload["source_ids"])
    payload["evidence_texts"] = sorted(payload["evidence_texts"])
    return payload


def _semantic_fact_id(fact: ValidatedFact) -> str:
    """Return the stable ID for exactly the non-provenance fact content."""

    payload = fact.model_dump(mode="json")
    for key in ("fact_id", "source_ids", "evidence_texts", "evidence_ref"):
        payload.pop(key, None)
    return stable_id("corpus-fact", _canonical_json(payload))


def _merge_fact_provenance(
    first: CorpusFact,
    second: CorpusFact,
) -> CorpusFact:
    """Merge audit fields after the semantic identity has already matched."""

    first_payload = first.model_dump(mode="json")
    second_payload = second.model_dump(mode="json")
    for key in ("source_ids", "evidence_texts", "evidence_ref"):
        first_payload.pop(key, None)
        second_payload.pop(key, None)
    if first_payload != second_payload:
        raise ValueError("conflicting semantic fact content")
    return first.model_copy(
        update={
            "source_ids": sorted(set(first.source_ids) | set(second.source_ids)),
            "evidence_texts": sorted(
                set(first.evidence_texts) | set(second.evidence_texts)
            ),
            "evidence_ref": min(first.evidence_ref, second.evidence_ref),
        }
    )


def _source_artifact_id(store: QueryGraphStore, source_id: str) -> str:
    snapshot = store.source_snapshots.get(source_id)
    if snapshot is None:
        raise ValueError(f"source artifact is missing for source ID: {source_id}")
    return snapshot.content_sha256


def _evidence_link(
    *,
    owner_kind: Literal["fact", "profile_gap", "context_association", "observation"],
    owner_id: str,
    source_id: str,
    artifact_id: str,
    evidence_text: str | None = None,
    evidence_ref: str | None = None,
) -> EvidenceLink:
    return EvidenceLink(
        evidence_link_id=stable_id(
            "corpus-evidence",
            owner_kind,
            owner_id,
            source_id,
            artifact_id,
            evidence_text or "",
            evidence_ref or "",
        ),
        owner_kind=owner_kind,
        owner_id=owner_id,
        source_id=source_id,
        artifact_id=artifact_id,
        evidence_text=evidence_text,
        evidence_ref=evidence_ref,
    )


def _optional_context_associations(store: QueryGraphStore) -> list[object]:
    entry = (store.manifest.get("context_artifacts") or {}).get(
        "context_associations"
    )
    if not isinstance(entry, dict) or entry.get("status") != "ok":
        return []
    path = store.run_dir / str(entry.get("path") or "")
    return read_context_associations(path)


def _optional_observation_traces(
    store: QueryGraphStore,
) -> list[ObservationFactTrace]:
    entry = (store.manifest.get("context_artifacts") or {}).get(
        "observation_fact_trace"
    )
    if not isinstance(entry, dict) or entry.get("status") != "ok":
        return []
    path = store.run_dir / str(entry.get("path") or "")
    return read_observation_fact_traces(path)


def _corpus_observation(
    *,
    event_id: str,
    trace: ObservationFactTrace,
    run_facts: list[ValidatedFact],
    semantic_ids_by_run_fact_id: dict[str, str],
) -> CorpusObservation:
    observation_rows = [
        fact
        for fact in run_facts
        if fact.subject_iri == trace.observation_id
    ]
    numeric_fact = next(
        (fact for fact in run_facts if fact.fact_id == trace.fact_id),
        None,
    )
    if numeric_fact is None:
        raise ValueError("observation trace references a missing formal fact")
    result_id = next(
        (
            fact.object_value
            for fact in observation_rows
            if _local_name(fact.predicate_iri) == "hasResult"
        ),
        None,
    )
    interval_id = next(
        (
            fact.object_value
            for fact in observation_rows
            if _local_name(fact.predicate_iri) == "phenomenonTime"
        ),
        None,
    )
    rows = [
        fact
        for fact in run_facts
        if fact.subject_iri in {trace.observation_id, result_id, interval_id}
    ]
    fact_ids = tuple(
        sorted(
            semantic_ids_by_run_fact_id[fact.fact_id]
            for fact in rows
            if fact.fact_id in semantic_ids_by_run_fact_id
        )
    )
    phase_fact = next(
        (
            fact
            for fact in rows
            if fact.subject_iri == interval_id
            and fact.object_value.rsplit(":", 1)[-1]
            in {"baseline", "active", "recovery"}
        ),
        None,
    )
    if phase_fact is None:
        raise ValueError("formal observation has no phase")
    phase = phase_fact.object_value.rsplit(":", 1)[-1]
    if phase not in {"baseline", "active", "recovery"}:
        raise ValueError("formal observation phase is invalid")
    unit_fact = next(
        (
            fact
            for fact in rows
            if fact.subject_iri == result_id
            and _local_name(fact.predicate_iri) == "unit"
        ),
        None,
    )
    artifact_id = trace.source_snapshot_sha256
    observation_id = stable_id(
        "corpus-observation",
        event_id,
        trace.observation_id,
        trace.metric_key,
        _canonical_json(list(fact_ids)),
        trace.source_id,
        artifact_id,
    )
    return CorpusObservation(
        observation_id=observation_id,
        event_id=event_id,
        phase=phase,
        metric_key=trace.metric_key,
        value=trace.canonical_value,
        unit_iri=unit_fact.object_value if unit_fact is not None else None,
        fact_ids=fact_ids,
        profile_id=numeric_fact.validation_profile.profile_id,
        profile_checksum=numeric_fact.validation_profile.profile_checksum,
        source_id=trace.source_id,
        source_artifact_id=artifact_id,
    )


def _local_name(iri: str) -> str:
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _first_object(
    facts: list[ValidatedFact],
    predicate_name: str,
) -> str | None:
    values = sorted(
        {
            fact.object_value
            for fact in facts
            if _local_name(fact.predicate_iri) == predicate_name
        }
    )
    return values[0] if values else None


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    text = "".join(f"{_canonical_json(row)}\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _artifact_metadata(
    root: Path,
    path: Path,
    *,
    count: int,
) -> CorpusArtifactMetadata:
    data = path.read_bytes()
    return CorpusArtifactMetadata(
        path=path.relative_to(root).as_posix(),
        count=count,
        sha256=hashlib.sha256(data).hexdigest(),
    )


def _source_objects_metadata(
    root: Path,
    source_objects: dict[str, str],
) -> CorpusArtifactMetadata:
    """Register the content-addressed object directory deterministically."""

    object_dir = root / "source_objects"
    digest_rows = [
        {
            "path": f"source_objects/{object_key}.txt",
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        }
        for object_key, content in sorted(source_objects.items())
    ]
    return CorpusArtifactMetadata(
        path=object_dir.relative_to(root).as_posix(),
        count=len(source_objects),
        sha256=hashlib.sha256(_canonical_json(digest_rows).encode("utf-8")).hexdigest(),
    )
