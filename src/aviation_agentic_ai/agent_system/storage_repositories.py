"""Focused repository facades over the authoritative aviation store.

The SQLite implementation remains the single persistence boundary.  These
small facades separate source/evidence registration, semantic publication,
and read-side retrieval so callers do not need to depend on the storage
implementation's entire surface.  They are deliberately delegating facades:
the next storage migration can move an area behind one repository without
changing query or ingestion code.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore


class _Repository:
    """Base facade that keeps the authoritative store private to the facade."""

    def __init__(self, store: AviationEvidenceStore) -> None:
        self._store = store


class SourceRepository(_Repository):
    """Source assets, versions, anchors, and source-text chunks."""

    def register_source_asset(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.register_source_asset(*args, **kwargs)

    def get_source_asset(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_source_asset(*args, **kwargs)

    def register_source_version(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.register_source_version(*args, **kwargs)

    def register_source_versions(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.register_source_versions(*args, **kwargs)

    def get_source_version(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_source_version(*args, **kwargs)

    def get_latest_source_version(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_latest_source_version(*args, **kwargs)

    def list_source_versions(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.list_source_versions(*args, **kwargs)

    def register_source_anchor(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.register_source_anchor(*args, **kwargs)

    def get_source_anchor(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_source_anchor(*args, **kwargs)

    def read_source_anchor(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.read_source_anchor(*args, **kwargs)

    def anchor_source_text(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.anchor_source_text(*args, **kwargs)

    def upsert_source_chunks(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.upsert_source_chunks(*args, **kwargs)

    def get_source_chunk(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_source_chunk(*args, **kwargs)

    def list_source_chunks(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.list_source_chunks(*args, **kwargs)

    def search_source_text(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.search_source_text(*args, **kwargs)


class SemanticRepository(_Repository):
    """Formal publication, ingestion status, and semantic-store telemetry."""

    def apply_knowledge_publication(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.apply_knowledge_publication(*args, **kwargs)

    def apply_knowledge_publication_batch(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.apply_knowledge_publication_batch(*args, **kwargs)

    def apply_flight_airspace_publication(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.apply_flight_airspace_publication(*args, **kwargs)

    def apply_flight_airspace_publication_batch(
        self, *args: Any, **kwargs: Any
    ) -> Any:
        return self._store.apply_flight_airspace_publication_batch(*args, **kwargs)

    def apply_cross_source_association_materialization(
        self, *args: Any, **kwargs: Any
    ) -> Any:
        return self._store.apply_cross_source_association_materialization(
            *args, **kwargs
        )

    def record_knowledge_ingestion_result(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.record_knowledge_ingestion_result(*args, **kwargs)

    def record_knowledge_ingestion_results(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.record_knowledge_ingestion_results(*args, **kwargs)

    def get_knowledge_ingestion_result(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_knowledge_ingestion_result(*args, **kwargs)

    def apply_ingestion_attempt(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.apply_ingestion_attempt(*args, **kwargs)

    def list_active_formal_fact_bindings(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.list_active_formal_fact_bindings(*args, **kwargs)

    def get_knowledge_revision(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_knowledge_revision(*args, **kwargs)

    def set_vector_index_state(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.set_vector_index_state(*args, **kwargs)

    def get_vector_index_state(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_vector_index_state(*args, **kwargs)

    def replace_agent_usage(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.replace_agent_usage(*args, **kwargs)

    def list_agent_usage(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.list_agent_usage(*args, **kwargs)


class RetrievalRepository(_Repository):
    """Read-only event, graph, and source retrieval operations."""

    def get_event(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_event(*args, **kwargs)

    def list_tmi_event_publications(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.list_tmi_event_publications(*args, **kwargs)

    def find_tmi_events(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.find_tmi_events(*args, **kwargs)

    def get_event_facts(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_event_facts(*args, **kwargs)

    def get_event_evidence(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_event_evidence(*args, **kwargs)

    def get_event_sources(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_event_sources(*args, **kwargs)

    def get_active_event_ids_by_source_version(
        self, *args: Any, **kwargs: Any
    ) -> Any:
        return self._store.get_active_event_ids_by_source_version(*args, **kwargs)

    def get_event_weather(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_event_weather(*args, **kwargs)

    def get_event_profile_gaps(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_event_profile_gaps(*args, **kwargs)

    def get_event_observations(self, *args: Any, **kwargs: Any) -> Any:
        return self._store.get_event_observations(*args, **kwargs)


__all__ = ["RetrievalRepository", "SemanticRepository", "SourceRepository"]
