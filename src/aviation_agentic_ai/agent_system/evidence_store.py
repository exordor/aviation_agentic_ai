"""Persistent SQLite evidence store for aviation source versions."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from aviation_agentic_ai.agent_system.agent_usage import AgentUsageRecord
from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.ingestion_package import IngestionAttempt
from aviation_agentic_ai.agent_system.knowledge_publication import (
    KnowledgePublicationBatch,
    KnowledgePublicationPackage,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    EventEvidenceLink,
    EventProfileGapRecord,
    EventWeatherAssociation,
    IngestionResult,
    KnowledgeIngestionResult,
    PublicObservationRecord,
    SemanticFactRecord,
    SourceAnchorRecord,
    SourceAssetRecord,
    SourceChunkRecord,
    SourceVersionRecord,
    TMIEventPage,
    TMIEventQuery,
    TMIEventRecord,
    VectorIndexStateRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


SCHEMA_VERSION = "aviation-evidence-store-v2"
DATABASE_FILENAME = "aviation_evidence.sqlite3"


class AviationEvidenceStore:
    """Dataset-bound SQLite store for immutable source and semantic evidence."""

    def __init__(
        self,
        root: Path,
        connection: sqlite3.Connection,
        dataset_id: str,
    ) -> None:
        self.root = root
        self._connection = connection
        self.dataset_id = dataset_id

    @classmethod
    def open(
        cls,
        root: str | Path,
        *,
        dataset_id: str,
        create: bool = False,
    ) -> AviationEvidenceStore:
        store_root = Path(root)
        database_path = store_root / DATABASE_FILENAME
        database_exists = database_path.exists()
        if not database_exists and not create:
            raise FileNotFoundError(f"evidence store does not exist: {database_path}")
        store_root.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        if database_exists:
            try:
                metadata = dict(
                    connection.execute(
                        "SELECT key, value FROM store_metadata ORDER BY key"
                    ).fetchall()
                )
            except sqlite3.DatabaseError as exc:
                connection.close()
                raise ValueError("invalid evidence store schema") from exc
            if metadata.get("schema_version") != SCHEMA_VERSION:
                connection.close()
                raise ValueError("evidence store schema version mismatch")
            if metadata.get("dataset_id") != dataset_id:
                connection.close()
                raise ValueError("evidence store dataset does not match")
        if create and not database_exists:
            now = datetime.now(UTC).isoformat()
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS store_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                connection.executemany(
                    """
                    INSERT OR IGNORE INTO store_metadata(key, value)
                    VALUES (?, ?)
                    """,
                    (
                        ("schema_version", SCHEMA_VERSION),
                        ("dataset_id", dataset_id),
                        ("knowledge_revision", "0"),
                        ("created_at", now),
                        ("updated_at", now),
                    ),
                )
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS source_assets (
                        asset_id TEXT PRIMARY KEY,
                        asset_key TEXT NOT NULL,
                        family TEXT NOT NULL,
                        local_path TEXT NOT NULL,
                        source_url TEXT,
                        media_type TEXT NOT NULL,
                        content_sha256 TEXT NOT NULL,
                        byte_count INTEGER NOT NULL,
                        effective_start TEXT,
                        effective_end TEXT,
                        UNIQUE(asset_key, content_sha256)
                    );

                    CREATE TABLE IF NOT EXISTS sources (
                        source_id TEXT PRIMARY KEY,
                        family TEXT NOT NULL,
                        latest_observed_version_id TEXT,
                        latest_accepted_version_id TEXT
                    );

                    CREATE TABLE IF NOT EXISTS source_versions (
                        source_version_id TEXT PRIMARY KEY,
                        source_id TEXT NOT NULL
                            REFERENCES sources(source_id),
                        family TEXT NOT NULL,
                        asset_id TEXT
                            REFERENCES source_assets(asset_id),
                        content TEXT NOT NULL,
                        content_sha256 TEXT NOT NULL,
                        source_url TEXT,
                        logical_time TEXT,
                        metadata_json TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS
                        idx_source_versions_source
                    ON source_versions(source_id, source_version_id);

                    CREATE TABLE IF NOT EXISTS source_anchors (
                        source_anchor_id TEXT PRIMARY KEY,
                        source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        char_start INTEGER NOT NULL,
                        char_end INTEGER NOT NULL,
                        anchor_kind TEXT NOT NULL,
                        UNIQUE(source_version_id, char_start, char_end),
                        CHECK(char_start >= 0),
                        CHECK(char_end > char_start),
                        CHECK(anchor_kind IN ('full_record', 'text_span'))
                    );

                    CREATE INDEX IF NOT EXISTS
                        idx_source_anchors_version
                    ON source_anchors(
                        source_version_id,
                        char_start,
                        char_end
                    );

                    CREATE TABLE IF NOT EXISTS ingestion_results (
                        source_version_id TEXT PRIMARY KEY
                            REFERENCES source_versions(source_version_id),
                        source_id TEXT NOT NULL
                            REFERENCES sources(source_id),
                        status TEXT NOT NULL,
                        event_id TEXT,
                        publication_id TEXT,
                        reason TEXT NOT NULL,
                        provider_call_count INTEGER NOT NULL,
                        tmi_family TEXT,
                        preflight_eligible INTEGER,
                        CHECK(status IN ('ok', 'insufficient', 'blocked'))
                    );

                    CREATE INDEX IF NOT EXISTS idx_ingestion_results_status
                    ON ingestion_results(status, source_version_id);

                    CREATE TABLE IF NOT EXISTS knowledge_roots (
                        root_id TEXT PRIMARY KEY,
                        root_kind TEXT NOT NULL,
                        temporal_domain_id TEXT NOT NULL,
                        active_publication_id TEXT
                            REFERENCES knowledge_publications(publication_id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_knowledge_roots_kind
                    ON knowledge_roots(
                        root_kind,
                        temporal_domain_id,
                        root_id
                    );

                    CREATE TABLE IF NOT EXISTS knowledge_publications (
                        publication_id TEXT PRIMARY KEY,
                        root_id TEXT NOT NULL
                            REFERENCES knowledge_roots(root_id),
                        primary_source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        publication_digest TEXT NOT NULL,
                        temporal_domain_id TEXT NOT NULL,
                        published_at TEXT NOT NULL,
                        UNIQUE(
                            root_id,
                            primary_source_version_id,
                            publication_digest
                        )
                    );

                    CREATE INDEX IF NOT EXISTS idx_knowledge_publications_root
                    ON knowledge_publications(root_id, publication_id);

                    CREATE TABLE IF NOT EXISTS publication_sources (
                        membership_id TEXT PRIMARY KEY,
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        source_role TEXT NOT NULL,
                        UNIQUE(publication_id, source_version_id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_publication_sources_version
                    ON publication_sources(source_version_id, publication_id);

                    CREATE TABLE IF NOT EXISTS publication_facts (
                        membership_id TEXT PRIMARY KEY,
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        fact_id TEXT NOT NULL
                            REFERENCES semantic_facts(fact_id),
                        UNIQUE(publication_id, fact_id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_publication_facts_fact
                    ON publication_facts(fact_id, publication_id);

                    CREATE TABLE IF NOT EXISTS publication_evidence_links (
                        evidence_link_id TEXT PRIMARY KEY,
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        owner_kind TEXT NOT NULL,
                        owner_id TEXT NOT NULL,
                        source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        source_anchor_id TEXT
                            REFERENCES source_anchors(source_anchor_id),
                        evidence_text TEXT,
                        evidence_ref TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS
                        idx_publication_evidence_links_publication
                    ON publication_evidence_links(
                        publication_id,
                        evidence_link_id
                    );

                    CREATE TABLE IF NOT EXISTS deterministic_derivations (
                        derivation_id TEXT PRIMARY KEY,
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        temporal_domain_id TEXT NOT NULL,
                        procedure_id TEXT NOT NULL,
                        procedure_checksum TEXT NOT NULL,
                        normalized_parameters_json TEXT NOT NULL,
                        input_publication_ids_json TEXT NOT NULL,
                        input_source_version_ids_json TEXT NOT NULL,
                        input_entity_ids_json TEXT NOT NULL,
                        result_checksum TEXT NOT NULL,
                        result_summary TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_derivations_publication
                    ON deterministic_derivations(
                        publication_id,
                        derivation_id
                    );

                    CREATE TABLE IF NOT EXISTS knowledge_ingestion_results (
                        source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        adapter_id TEXT NOT NULL,
                        adapter_version TEXT NOT NULL,
                        profile_checksum TEXT,
                        status TEXT NOT NULL,
                        root_id TEXT REFERENCES knowledge_roots(root_id),
                        publication_id TEXT
                            REFERENCES knowledge_publications(publication_id),
                        reason TEXT NOT NULL,
                        recorded_at TEXT NOT NULL,
                        PRIMARY KEY(
                            source_version_id,
                            adapter_id,
                            adapter_version
                        ),
                        CHECK(status IN ('ok', 'insufficient', 'blocked'))
                    );

                    CREATE INDEX IF NOT EXISTS
                        idx_knowledge_ingestion_results_status
                    ON knowledge_ingestion_results(status, source_version_id);

                    CREATE TABLE IF NOT EXISTS tmi_publication_details (
                        publication_id TEXT PRIMARY KEY
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        event_id TEXT NOT NULL,
                        effective_start TEXT,
                        effective_end TEXT,
                        issued_at TEXT,
                        reason_status TEXT NOT NULL,
                        reason_value TEXT,
                        CHECK(
                            reason_status IN (
                                'formal',
                                'profile_gap',
                                'missing'
                            )
                        )
                    );

                    CREATE TABLE IF NOT EXISTS flights (
                        flight_id TEXT PRIMARY KEY,
                        temporal_domain_id TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS flight_publications (
                        publication_id TEXT PRIMARY KEY
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        flight_id TEXT NOT NULL REFERENCES flights(flight_id),
                        service_date TEXT,
                        reporting_carrier TEXT,
                        flight_number TEXT,
                        tail_number TEXT,
                        origin_airport_id TEXT,
                        destination_airport_id TEXT,
                        scheduled_departure_time TEXT,
                        actual_departure_time TEXT,
                        time_basis TEXT NOT NULL,
                        cancelled INTEGER NOT NULL DEFAULT 0,
                        diverted INTEGER NOT NULL DEFAULT 0,
                        CHECK(cancelled IN (0, 1)),
                        CHECK(diverted IN (0, 1))
                    );

                    CREATE INDEX IF NOT EXISTS idx_flight_publications_filters
                    ON flight_publications(
                        service_date,
                        origin_airport_id,
                        destination_airport_id,
                        reporting_carrier,
                        tail_number
                    );

                    CREATE TABLE IF NOT EXISTS air_carriers (
                        carrier_id TEXT PRIMARY KEY,
                        code TEXT NOT NULL,
                        name TEXT
                    );

                    CREATE TABLE IF NOT EXISTS aircraft_models (
                        aircraft_model_id TEXT PRIMARY KEY,
                        manufacturer_name TEXT,
                        model_name TEXT
                    );

                    CREATE TABLE IF NOT EXISTS aircraft (
                        aircraft_id TEXT PRIMARY KEY,
                        registration_mark TEXT
                    );

                    CREATE TABLE IF NOT EXISTS flight_aircraft_snapshot_matches (
                        snapshot_match_id TEXT PRIMARY KEY,
                        flight_publication_id TEXT NOT NULL
                            REFERENCES flight_publications(publication_id),
                        aircraft_publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id),
                        model_publication_id TEXT
                            REFERENCES knowledge_publications(publication_id),
                        procedure_id TEXT NOT NULL,
                        procedure_checksum TEXT NOT NULL,
                        temporal_domain_id TEXT NOT NULL,
                        limitation TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS airports (
                        airport_id TEXT PRIMARY KEY,
                        identifier TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS artccs (
                        artcc_id TEXT PRIMARY KEY,
                        identifier TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS airport_artcc_assignments (
                        assignment_id TEXT PRIMARY KEY,
                        airport_publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id),
                        artcc_publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id),
                        assignment_role TEXT NOT NULL,
                        effective_start TEXT,
                        effective_end TEXT,
                        procedure_id TEXT NOT NULL,
                        procedure_checksum TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_airport_artcc_lookup
                    ON airport_artcc_assignments(
                        artcc_publication_id,
                        assignment_role,
                        effective_start,
                        effective_end
                    );

                    CREATE TABLE IF NOT EXISTS navigation_fixes (
                        fix_id TEXT PRIMARY KEY,
                        identifier TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS sectors (
                        sector_id TEXT PRIMARY KEY,
                        identifier TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS routes (
                        route_id TEXT PRIMARY KEY,
                        flight_publication_id TEXT NOT NULL
                            REFERENCES flight_publications(publication_id)
                    );

                    CREATE TABLE IF NOT EXISTS track_points (
                        track_point_id TEXT PRIMARY KEY,
                        route_id TEXT NOT NULL REFERENCES routes(route_id),
                        sequence_number INTEGER NOT NULL,
                        reporting_time TEXT,
                        fix_id TEXT REFERENCES navigation_fixes(fix_id),
                        latitude REAL,
                        longitude REAL,
                        ground_speed REAL,
                        UNIQUE(route_id, sequence_number)
                    );

                    CREATE INDEX IF NOT EXISTS idx_track_points_route_sequence
                    ON track_points(route_id, sequence_number, reporting_time);

                    CREATE TABLE IF NOT EXISTS sector_passages (
                        sector_passage_id TEXT PRIMARY KEY,
                        sector_id TEXT NOT NULL REFERENCES sectors(sector_id),
                        flight_publication_id TEXT NOT NULL
                            REFERENCES flight_publications(publication_id),
                        track_point_id TEXT NOT NULL
                            REFERENCES track_points(track_point_id),
                        passage_time TEXT NOT NULL,
                        procedure_id TEXT NOT NULL,
                        procedure_checksum TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_sector_passages_lookup
                    ON sector_passages(
                        sector_id,
                        passage_time,
                        flight_publication_id
                    );

                    CREATE TABLE IF NOT EXISTS weather_observations (
                        weather_observation_id TEXT PRIMARY KEY,
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id),
                        station_id TEXT NOT NULL,
                        observed_at TEXT NOT NULL,
                        report_type TEXT NOT NULL,
                        raw_report TEXT NOT NULL,
                        time_basis TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_weather_observations_lookup
                    ON weather_observations(station_id, observed_at);

                    CREATE TABLE IF NOT EXISTS flight_weather_associations (
                        association_id TEXT PRIMARY KEY,
                        flight_publication_id TEXT NOT NULL
                            REFERENCES flight_publications(publication_id),
                        weather_publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id),
                        delta_seconds INTEGER NOT NULL,
                        procedure_id TEXT NOT NULL,
                        procedure_checksum TEXT NOT NULL,
                        temporal_domain_id TEXT NOT NULL,
                        causal_claim INTEGER NOT NULL DEFAULT 0,
                        CHECK(causal_claim = 0)
                    );

                    CREATE TABLE IF NOT EXISTS flight_tmi_applicability (
                        applicability_id TEXT PRIMARY KEY,
                        flight_publication_id TEXT NOT NULL
                            REFERENCES flight_publications(publication_id),
                        tmi_publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id),
                        status TEXT NOT NULL,
                        rule_id TEXT NOT NULL,
                        rule_version TEXT NOT NULL,
                        input_checksum TEXT NOT NULL,
                        temporal_domain_id TEXT NOT NULL,
                        limitation TEXT NOT NULL,
                        CHECK(
                            status IN (
                                'candidate',
                                'unknown',
                                'not_applicable'
                            )
                        )
                    );

                    CREATE INDEX IF NOT EXISTS idx_flight_tmi_applicability
                    ON flight_tmi_applicability(
                        tmi_publication_id,
                        flight_publication_id,
                        status
                    );

                    CREATE TABLE IF NOT EXISTS tmi_events (
                        event_id TEXT PRIMARY KEY,
                        advisory_source_id TEXT NOT NULL
                            REFERENCES sources(source_id)
                    );

                    CREATE TABLE IF NOT EXISTS event_types (
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        event_type_iri TEXT NOT NULL,
                        PRIMARY KEY(publication_id, event_type_iri)
                    );

                    CREATE INDEX IF NOT EXISTS idx_event_types_type
                    ON event_types(event_type_iri, publication_id);

                    CREATE TABLE IF NOT EXISTS event_facilities (
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        facility_id TEXT NOT NULL,
                        PRIMARY KEY(publication_id, facility_id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_event_facilities_facility
                    ON event_facilities(facility_id, publication_id);

                    CREATE TABLE IF NOT EXISTS semantic_facts (
                        fact_id TEXT PRIMARY KEY,
                        subject_iri TEXT NOT NULL,
                        subject_class_iri TEXT NOT NULL,
                        predicate_iri TEXT NOT NULL,
                        object_kind TEXT NOT NULL,
                        object_value TEXT NOT NULL,
                        object_class_iri TEXT,
                        datatype_iri TEXT,
                        profile_id TEXT NOT NULL,
                        profile_checksum TEXT NOT NULL,
                        validation_layer TEXT NOT NULL,
                        evidence_mode TEXT NOT NULL,
                        CHECK(object_kind IN ('iri', 'literal')),
                        CHECK(
                            evidence_mode IN (
                                'source_text',
                                'deterministic_derivation',
                                'profile_definition'
                            )
                        )
                    );

                    CREATE INDEX IF NOT EXISTS idx_semantic_facts_spo
                    ON semantic_facts(
                        subject_iri,
                        predicate_iri,
                        object_value,
                        fact_id
                    );

                    CREATE TABLE IF NOT EXISTS ingestion_runs (
                        ingestion_run_id TEXT PRIMARY KEY,
                        started_at TEXT NOT NULL,
                        ended_at TEXT,
                        status TEXT NOT NULL,
                        attempted_count INTEGER NOT NULL DEFAULT 0,
                        ok_count INTEGER NOT NULL DEFAULT 0,
                        insufficient_count INTEGER NOT NULL DEFAULT 0,
                        blocked_count INTEGER NOT NULL DEFAULT 0
                    );

                    CREATE TABLE IF NOT EXISTS profile_gaps (
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        gap_id TEXT NOT NULL,
                        event_id TEXT NOT NULL
                            REFERENCES tmi_events(event_id),
                        field_name TEXT NOT NULL,
                        value TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        source_anchor_id TEXT
                            REFERENCES source_anchors(source_anchor_id),
                        evidence_text TEXT,
                        evidence_ref TEXT NOT NULL,
                        profile_id TEXT NOT NULL,
                        profile_checksum TEXT NOT NULL,
                        validation_layer TEXT NOT NULL,
                        PRIMARY KEY(publication_id, gap_id)
                    );

                    CREATE TABLE IF NOT EXISTS weather_associations (
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        association_id TEXT NOT NULL,
                        event_id TEXT NOT NULL
                            REFERENCES tmi_events(event_id),
                        report_id TEXT NOT NULL,
                        facility_id TEXT NOT NULL,
                        relation_type TEXT NOT NULL,
                        selection_method TEXT NOT NULL,
                        relevant_times_json TEXT NOT NULL,
                        source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        causal_claim INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY(publication_id, association_id),
                        CHECK(causal_claim = 0)
                    );

                    CREATE TABLE IF NOT EXISTS public_observations (
                        publication_id TEXT NOT NULL
                            REFERENCES knowledge_publications(publication_id)
                            ON DELETE CASCADE,
                        observation_id TEXT NOT NULL,
                        event_id TEXT NOT NULL
                            REFERENCES tmi_events(event_id),
                        phase TEXT NOT NULL,
                        metric_key TEXT NOT NULL,
                        value_json TEXT,
                        unit_iri TEXT,
                        profile_id TEXT NOT NULL,
                        profile_checksum TEXT NOT NULL,
                        source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        PRIMARY KEY(publication_id, observation_id),
                        CHECK(phase IN ('baseline', 'active', 'recovery'))
                    );

                    CREATE TABLE IF NOT EXISTS observation_facts (
                        publication_id TEXT NOT NULL,
                        observation_id TEXT NOT NULL,
                        fact_id TEXT NOT NULL
                            REFERENCES semantic_facts(fact_id),
                        PRIMARY KEY(
                            publication_id,
                            observation_id,
                            fact_id
                        ),
                        FOREIGN KEY(publication_id, observation_id)
                            REFERENCES public_observations(
                                publication_id,
                                observation_id
                            )
                            ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS source_chunks (
                        chunk_id TEXT PRIMARY KEY,
                        source_version_id TEXT NOT NULL
                            REFERENCES source_versions(source_version_id),
                        event_id TEXT,
                        chunk_kind TEXT NOT NULL,
                        text TEXT NOT NULL,
                        char_start INTEGER NOT NULL,
                        char_end INTEGER NOT NULL,
                        source_anchor_id TEXT NOT NULL
                            REFERENCES source_anchors(source_anchor_id),
                        representation_version TEXT NOT NULL,
                        metadata_json TEXT NOT NULL,
                        CHECK(
                            chunk_kind IN (
                                'source_record',
                                'tmi_event_summary'
                            )
                        ),
                        CHECK(char_start >= 0),
                        CHECK(char_end > char_start)
                    );

                    CREATE INDEX IF NOT EXISTS idx_source_chunks_version
                    ON source_chunks(
                        source_version_id,
                        chunk_id
                    );

                    CREATE VIRTUAL TABLE IF NOT EXISTS source_chunks_fts
                    USING fts5(
                        text,
                        content='source_chunks',
                        content_rowid='rowid'
                    );

                    CREATE TRIGGER IF NOT EXISTS source_chunks_fts_insert
                    AFTER INSERT ON source_chunks BEGIN
                        INSERT INTO source_chunks_fts(rowid, text)
                        VALUES (new.rowid, new.text);
                    END;

                    CREATE TRIGGER IF NOT EXISTS source_chunks_fts_delete
                    AFTER DELETE ON source_chunks BEGIN
                        INSERT INTO source_chunks_fts(
                            source_chunks_fts,
                            rowid,
                            text
                        )
                        VALUES ('delete', old.rowid, old.text);
                    END;

                    CREATE TRIGGER IF NOT EXISTS source_chunks_fts_update
                    AFTER UPDATE ON source_chunks BEGIN
                        INSERT INTO source_chunks_fts(
                            source_chunks_fts,
                            rowid,
                            text
                        )
                        VALUES ('delete', old.rowid, old.text);
                        INSERT INTO source_chunks_fts(rowid, text)
                        VALUES (new.rowid, new.text);
                    END;

                    CREATE TABLE IF NOT EXISTS vector_index_state (
                        collection_name TEXT PRIMARY KEY,
                        representation_version TEXT NOT NULL,
                        embedding_model_id TEXT NOT NULL,
                        embedding_dimension INTEGER NOT NULL,
                        indexed_knowledge_revision INTEGER NOT NULL,
                        document_count INTEGER NOT NULL,
                        vector_count INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        failure_reason TEXT
                    );

                    CREATE TABLE IF NOT EXISTS agent_usage (
                        ingestion_run_id TEXT NOT NULL
                            REFERENCES ingestion_runs(ingestion_run_id)
                            ON DELETE CASCADE,
                        source_id TEXT NOT NULL,
                        event_id TEXT,
                        task_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        task_scope TEXT NOT NULL,
                        execution_mode TEXT NOT NULL,
                        outcome TEXT NOT NULL,
                        detail_status TEXT NOT NULL,
                        activation_reason TEXT NOT NULL,
                        provider_call_count INTEGER NOT NULL DEFAULT 0,
                        tool_call_count INTEGER NOT NULL DEFAULT 0,
                        input_tokens INTEGER NOT NULL DEFAULT 0,
                        output_tokens INTEGER NOT NULL DEFAULT 0,
                        provider_latency_ms REAL NOT NULL DEFAULT 0,
                        tool_latency_ms REAL NOT NULL DEFAULT 0,
                        PRIMARY KEY(
                            ingestion_run_id,
                            source_id,
                            role,
                            task_scope
                        )
                    );
                    """
                )
        try:
            metadata = dict(
                connection.execute(
                    "SELECT key, value FROM store_metadata ORDER BY key"
                ).fetchall()
            )
        except sqlite3.DatabaseError as exc:
            connection.close()
            raise ValueError("invalid evidence store schema") from exc
        if metadata.get("schema_version") != SCHEMA_VERSION:
            connection.close()
            raise ValueError("evidence store schema version mismatch")
        if metadata.get("dataset_id") != dataset_id:
            connection.close()
            raise ValueError("evidence store dataset does not match")
        return cls(store_root, connection, dataset_id)

    def close(self) -> None:
        """Close the underlying SQLite connection."""

        self._connection.close()

    def register_source_asset(
        self,
        asset: SourceAssetRecord,
    ) -> None:
        """Register immutable metadata for a configured external source file."""

        existing = self.get_source_asset(asset.asset_id)
        if existing is not None:
            if existing != asset:
                raise ValueError("source asset is immutable")
            return
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO source_assets(
                    asset_id,
                    asset_key,
                    family,
                    local_path,
                    source_url,
                    media_type,
                    content_sha256,
                    byte_count,
                    effective_start,
                    effective_end
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    asset.asset_id,
                    asset.asset_key,
                    asset.family.value,
                    asset.local_path,
                    asset.source_url,
                    asset.media_type,
                    asset.content_sha256,
                    asset.byte_count,
                    asset.effective_start,
                    asset.effective_end,
                ),
            )

    def get_source_asset(
        self,
        asset_id: str,
    ) -> SourceAssetRecord | None:
        """Return immutable metadata for one external source asset."""

        row = self._connection.execute(
            """
            SELECT *
            FROM source_assets
            WHERE asset_id = ?
            """,
            (asset_id,),
        ).fetchone()
        if row is None:
            return None
        return SourceAssetRecord(
            asset_id=row["asset_id"],
            asset_key=row["asset_key"],
            family=SourceFamily(row["family"]),
            local_path=row["local_path"],
            source_url=row["source_url"],
            media_type=row["media_type"],
            content_sha256=row["content_sha256"],
            byte_count=row["byte_count"],
            effective_start=row["effective_start"],
            effective_end=row["effective_end"],
        )

    def register_source_version(
        self,
        version: SourceVersionRecord,
    ) -> str:
        """Register one immutable exact source version."""

        existing = self.get_source_version(version.source_version_id)
        if existing is not None:
            if existing != version:
                raise ValueError("source version is immutable")
            return "existing"

        metadata_json = json.dumps(
            version.metadata,
            sort_keys=True,
            separators=(",", ":"),
        )
        with self._connection:
            source = self._connection.execute(
                "SELECT family FROM sources WHERE source_id = ?",
                (version.source_id,),
            ).fetchone()
            if source is not None and source["family"] != version.family.value:
                raise ValueError("source family cannot change across versions")
            self._connection.execute(
                """
                INSERT INTO sources(
                    source_id,
                    family,
                    latest_observed_version_id,
                    latest_accepted_version_id
                )
                VALUES (?, ?, ?, NULL)
                ON CONFLICT(source_id) DO UPDATE SET
                    latest_observed_version_id =
                        excluded.latest_observed_version_id
                """,
                (
                    version.source_id,
                    version.family.value,
                    version.source_version_id,
                ),
            )
            self._connection.execute(
                """
                INSERT INTO source_versions(
                    source_version_id,
                    source_id,
                    family,
                    asset_id,
                    content,
                    content_sha256,
                    source_url,
                    logical_time,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version.source_version_id,
                    version.source_id,
                    version.family.value,
                    version.asset_id,
                    version.content,
                    version.content_sha256,
                    version.source_url,
                    version.logical_time,
                    metadata_json,
                ),
            )
        return "inserted"

    def get_source_version(
        self,
        source_version_id: str,
    ) -> SourceVersionRecord | None:
        """Return an exact immutable source version by identity."""

        row = self._connection.execute(
            """
            SELECT *
            FROM source_versions
            WHERE source_version_id = ?
            """,
            (source_version_id,),
        ).fetchone()
        return self._source_version_from_row(row) if row is not None else None

    def get_latest_source_version(
        self,
        source_id: str,
    ) -> SourceVersionRecord | None:
        """Return the latest observed version of one logical source."""

        row = self._connection.execute(
            """
            SELECT version.*
            FROM sources AS source
            JOIN source_versions AS version
              ON version.source_version_id =
                 source.latest_observed_version_id
            WHERE source.source_id = ?
            """,
            (source_id,),
        ).fetchone()
        return self._source_version_from_row(row) if row is not None else None

    def list_source_versions(
        self,
        *,
        current_only: bool = False,
        families: tuple[SourceFamily, ...] = (),
    ) -> tuple[SourceVersionRecord, ...]:
        """Return immutable source versions in stable order."""

        predicates: list[str] = []
        parameters: list[object] = []
        if current_only:
            predicates.append(
                """
                version.source_version_id =
                source.latest_observed_version_id
                """
            )
        if families:
            placeholders = ", ".join("?" for _ in families)
            predicates.append(f"version.family IN ({placeholders})")
            parameters.extend(family.value for family in families)
        where_clause = (
            "WHERE " + " AND ".join(predicates)
            if predicates
            else ""
        )
        rows = self._connection.execute(
            f"""
            SELECT version.*
            FROM source_versions AS version
            JOIN sources AS source
              ON source.source_id = version.source_id
            {where_clause}
            ORDER BY version.source_version_id
            """,
            parameters,
        ).fetchall()
        return tuple(self._source_version_from_row(row) for row in rows)

    def register_source_anchor(
        self,
        source_version_id: str,
        *,
        char_start: int,
        char_end: int,
    ) -> SourceAnchorRecord:
        """Create or return one exact span in an immutable source version."""

        version = self.get_source_version(source_version_id)
        if version is None:
            raise ValueError("source version does not exist")
        if char_start < 0 or char_end <= char_start:
            raise ValueError("source anchor span is invalid")
        if char_end > len(version.content):
            raise ValueError("source anchor exceeds source version content")
        anchor = SourceAnchorRecord(
            source_anchor_id=stable_id(
                "source-anchor",
                source_version_id,
                char_start,
                char_end,
            ),
            source_version_id=source_version_id,
            char_start=char_start,
            char_end=char_end,
            anchor_kind=(
                "full_record"
                if char_start == 0 and char_end == len(version.content)
                else "text_span"
            ),
        )
        with self._connection:
            self._connection.execute(
                """
                INSERT OR IGNORE INTO source_anchors(
                    source_anchor_id,
                    source_version_id,
                    char_start,
                    char_end,
                    anchor_kind
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    anchor.source_anchor_id,
                    anchor.source_version_id,
                    anchor.char_start,
                    anchor.char_end,
                    anchor.anchor_kind,
                ),
            )
        stored = self.get_source_anchor(anchor.source_anchor_id)
        if stored != anchor:
            raise ValueError("source anchor identity collision")
        return anchor

    def get_source_anchor(
        self,
        source_anchor_id: str,
    ) -> SourceAnchorRecord | None:
        """Return one exact immutable source anchor."""

        row = self._connection.execute(
            """
            SELECT *
            FROM source_anchors
            WHERE source_anchor_id = ?
            """,
            (source_anchor_id,),
        ).fetchone()
        if row is None:
            return None
        return SourceAnchorRecord(
            source_anchor_id=row["source_anchor_id"],
            source_version_id=row["source_version_id"],
            char_start=row["char_start"],
            char_end=row["char_end"],
            anchor_kind=row["anchor_kind"],
        )

    def read_source_anchor(
        self,
        source_anchor_id: str,
        *,
        source_version_id: str | None = None,
        max_chars: int,
    ) -> str:
        """Read one exact span without allowing an unbounded source read."""

        if max_chars < 1:
            raise ValueError("source anchor read limit must be positive")
        anchor = self.get_source_anchor(source_anchor_id)
        if anchor is None:
            raise KeyError(f"source anchor does not exist: {source_anchor_id}")
        if (
            source_version_id is not None
            and anchor.source_version_id != source_version_id
        ):
            raise ValueError("source anchor belongs to another source version")
        char_count = anchor.char_end - anchor.char_start
        if char_count > max_chars:
            raise ValueError("source anchor exceeds read limit")
        row = self._connection.execute(
            """
            SELECT substr(content, ?, ?) AS evidence_text
            FROM source_versions
            WHERE source_version_id = ?
            """,
            (
                anchor.char_start + 1,
                char_count,
                anchor.source_version_id,
            ),
        ).fetchone()
        if row is None:
            raise ValueError("source anchor references a missing source version")
        return str(row["evidence_text"])

    def anchor_source_text(
        self,
        source_version_id: str,
        evidence_text: str,
    ) -> SourceAnchorRecord:
        """Anchor the lowest exact occurrence of source-text evidence."""

        if not evidence_text:
            raise ValueError("source evidence text must not be empty")
        version = self.get_source_version(source_version_id)
        if version is None:
            raise ValueError("source version does not exist")
        char_start = version.content.find(evidence_text)
        if char_start < 0:
            raise ValueError("source evidence text was not found")
        return self.register_source_anchor(
            source_version_id,
            char_start=char_start,
            char_end=char_start + len(evidence_text),
        )

    def apply_knowledge_publication(
        self,
        package: KnowledgePublicationPackage,
    ) -> str:
        """Atomically publish one semantic root through the common spine."""

        publication = package.publication
        if package.root.root_kind == "tmi_event":
            raise ValueError(
                "TMI publications require the atomic event publication path"
            )
        if self._connection.execute(
            "SELECT 1 FROM knowledge_publications WHERE publication_id = ?",
            (publication.publication_id,),
        ).fetchone() is not None:
            return "unchanged"
        versions = {
            membership.source_version_id: self.get_source_version(
                membership.source_version_id
            )
            for membership in package.publication_sources
        }
        missing = sorted(
            source_version_id
            for source_version_id, version in versions.items()
            if version is None
        )
        if missing:
            raise ValueError(
                f"publication source version does not exist: {missing[0]}"
            )
        existing_root = self._connection.execute(
            "SELECT * FROM knowledge_roots WHERE root_id = ?",
            (package.root.root_id,),
        ).fetchone()
        if existing_root is not None:
            if existing_root["root_kind"] != package.root.root_kind:
                raise ValueError("knowledge root kind cannot change")
            if (
                existing_root["temporal_domain_id"]
                != package.root.temporal_domain_id
            ):
                raise ValueError("knowledge root temporal domain cannot change")
        outcome = (
            "activated"
            if existing_root is not None
            and existing_root["active_publication_id"] is not None
            else "inserted"
        )
        now = datetime.now(UTC).isoformat()
        with self._connection:
            for anchor in package.source_anchors:
                version = versions[anchor.source_version_id]
                if version is None or anchor.char_end > len(version.content):
                    raise ValueError("source anchor exceeds source content")
                self._connection.execute(
                    """
                    INSERT OR IGNORE INTO source_anchors(
                        source_anchor_id,
                        source_version_id,
                        char_start,
                        char_end,
                        anchor_kind
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        anchor.source_anchor_id,
                        anchor.source_version_id,
                        anchor.char_start,
                        anchor.char_end,
                        anchor.anchor_kind,
                    ),
                )
            for link in package.evidence_links:
                if link.source_anchor_id is None:
                    continue
                anchor = self.get_source_anchor(link.source_anchor_id)
                version = versions[link.source_version_id]
                if anchor is None or version is None:
                    raise ValueError("evidence source anchor does not exist")
                anchored = version.content[anchor.char_start : anchor.char_end]
                if link.evidence_text != anchored:
                    raise ValueError(
                        "evidence text does not match source anchor"
                    )
            if existing_root is None:
                self._connection.execute(
                    """
                    INSERT INTO knowledge_roots(
                        root_id,
                        root_kind,
                        temporal_domain_id,
                        active_publication_id
                    ) VALUES (?, ?, ?, NULL)
                    """,
                    (
                        package.root.root_id,
                        package.root.root_kind,
                        package.root.temporal_domain_id,
                    ),
                )
            self._connection.execute(
                """
                INSERT INTO knowledge_publications(
                    publication_id,
                    root_id,
                    primary_source_version_id,
                    publication_digest,
                    temporal_domain_id,
                    published_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    publication.publication_id,
                    publication.root_id,
                    publication.primary_source_version_id,
                    publication.formal_publication_digest,
                    publication.temporal_domain_id,
                    now,
                ),
            )
            self._connection.executemany(
                """
                INSERT INTO publication_sources(
                    membership_id,
                    publication_id,
                    source_version_id,
                    source_role
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    (
                        membership.membership_id,
                        membership.publication_id,
                        membership.source_version_id,
                        membership.source_role,
                    )
                    for membership in package.publication_sources
                ),
            )
            for fact in package.facts:
                self._upsert_semantic_fact(fact)
            self._connection.executemany(
                """
                INSERT INTO publication_facts(
                    membership_id,
                    publication_id,
                    fact_id
                )
                VALUES (?, ?, ?)
                """,
                (
                    (
                        membership.membership_id,
                        membership.publication_id,
                        membership.fact_id,
                    )
                    for membership in package.fact_memberships
                ),
            )
            self._connection.executemany(
                """
                INSERT INTO deterministic_derivations(
                    derivation_id,
                    publication_id,
                    temporal_domain_id,
                    procedure_id,
                    procedure_checksum,
                    normalized_parameters_json,
                    input_publication_ids_json,
                    input_source_version_ids_json,
                    input_entity_ids_json,
                    result_checksum,
                    result_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (
                        row.derivation_id,
                        row.publication_id,
                        row.temporal_domain_id,
                        row.procedure_id,
                        row.procedure_checksum,
                        json.dumps(
                            row.normalized_parameters,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        json.dumps(row.input_publication_ids),
                        json.dumps(row.input_source_version_ids),
                        json.dumps(row.input_entity_ids),
                        row.result_checksum,
                        row.result_summary,
                    )
                    for row in package.derivations
                ),
            )
            self._connection.executemany(
                """
                INSERT INTO publication_evidence_links(
                    evidence_link_id,
                    publication_id,
                    owner_kind,
                    owner_id,
                    source_version_id,
                    source_anchor_id,
                    evidence_text,
                    evidence_ref
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (
                        row.evidence_link_id,
                        row.publication_id,
                        row.owner_kind,
                        row.owner_id,
                        row.source_version_id,
                        row.source_anchor_id,
                        row.evidence_text,
                        row.evidence_ref,
                    )
                    for row in package.evidence_links
                ),
            )
            self._connection.execute(
                """
                UPDATE knowledge_roots
                SET active_publication_id = ?
                WHERE root_id = ?
                """,
                (publication.publication_id, publication.root_id),
            )
            for source_version_id in sorted(versions):
                self._connection.execute(
                    """
                    UPDATE sources
                    SET latest_accepted_version_id = ?
                    WHERE source_id = (
                        SELECT source_id FROM source_versions
                        WHERE source_version_id = ?
                    )
                    """,
                    (source_version_id, source_version_id),
                )
            self._increment_knowledge_revision(now)
        return outcome

    def apply_knowledge_publication_batch(
        self,
        batch: KnowledgePublicationBatch,
    ) -> dict[str, str]:
        """Apply independent semantic-root partitions with failure isolation."""

        outcomes: dict[str, str] = {}
        for package in batch.packages:
            publication_id = package.publication.publication_id
            try:
                outcomes[publication_id] = self.apply_knowledge_publication(
                    package
                )
            except (ValueError, sqlite3.IntegrityError):
                outcomes[publication_id] = "blocked"
        return outcomes

    def record_knowledge_ingestion_result(
        self,
        result: KnowledgeIngestionResult,
    ) -> None:
        """Record one deterministic adapter outcome for resumable ingestion."""

        if self.get_source_version(result.source_version_id) is None:
            raise ValueError("ingestion source version does not exist")
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO knowledge_ingestion_results(
                    source_version_id,
                    adapter_id,
                    adapter_version,
                    profile_checksum,
                    status,
                    root_id,
                    publication_id,
                    reason,
                    recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    source_version_id,
                    adapter_id,
                    adapter_version
                ) DO UPDATE SET
                    profile_checksum = excluded.profile_checksum,
                    status = excluded.status,
                    root_id = excluded.root_id,
                    publication_id = excluded.publication_id,
                    reason = excluded.reason,
                    recorded_at = excluded.recorded_at
                """,
                (
                    result.source_version_id,
                    result.adapter_id,
                    result.adapter_version,
                    result.profile_checksum,
                    result.status,
                    result.root_id,
                    result.publication_id,
                    result.reason,
                    result.recorded_at.isoformat(),
                ),
            )

    def get_knowledge_ingestion_result(
        self,
        *,
        source_version_id: str,
        adapter_id: str,
        adapter_version: str,
    ) -> KnowledgeIngestionResult | None:
        """Return one generic adapter outcome used by resume logic."""

        row = self._connection.execute(
            """
            SELECT *
            FROM knowledge_ingestion_results
            WHERE source_version_id = ?
              AND adapter_id = ?
              AND adapter_version = ?
            """,
            (source_version_id, adapter_id, adapter_version),
        ).fetchone()
        if row is None:
            return None
        return KnowledgeIngestionResult(
            source_version_id=row["source_version_id"],
            adapter_id=row["adapter_id"],
            adapter_version=row["adapter_version"],
            profile_checksum=row["profile_checksum"],
            status=row["status"],
            root_id=row["root_id"],
            publication_id=row["publication_id"],
            reason=row["reason"],
            recorded_at=datetime.fromisoformat(row["recorded_at"]),
        )

    def apply_ingestion_attempt(
        self,
        attempt: IngestionAttempt,
    ) -> str:
        """Apply one source outcome and semantic publication atomically."""

        primary_version = self.get_source_version(
            attempt.result.source_version_id
        )
        if primary_version is None:
            raise ValueError("ingestion source version does not exist")
        if primary_version.source_id != attempt.result.source_id:
            raise ValueError("ingestion source ID does not match source version")
        if attempt.result.status != "ok":
            existing = self._get_ingestion_result(
                attempt.result.source_version_id
            )
            if existing == attempt.result:
                return "unchanged"
            with self._connection:
                self._write_ingestion_result(attempt.result)
            return "inserted"

        package = attempt.package
        if package is None:
            raise ValueError("ok ingestion requires a publication")
        event = package.event
        if (
            event.publication_source_version_id
            != attempt.result.source_version_id
        ):
            raise ValueError(
                "event publication source must match the ingestion source"
            )
        if primary_version.source_id != event.advisory_source_id:
            raise ValueError(
                "event advisory source must own the publication source version"
            )
        publication_digest = package.formal_publication_digest
        for source_version_id in package.source_version_ids:
            if self.get_source_version(source_version_id) is None:
                raise ValueError(
                    f"publication source version does not exist: "
                    f"{source_version_id}"
                )
        existing_publication = self._connection.execute(
            """
            SELECT publication_id
            FROM knowledge_publications
            WHERE publication_id = ?
            """,
            (event.publication_id,),
        ).fetchone()
        if existing_publication is not None:
            return "unchanged"
        existing_event = self._connection.execute(
            """
            SELECT
                event.advisory_source_id,
                root.active_publication_id,
                root.temporal_domain_id
            FROM tmi_events AS event
            JOIN knowledge_roots AS root
              ON root.root_id = event.event_id
            WHERE event.event_id = ?
            """,
            (event.event_id,),
        ).fetchone()
        outcome = (
            "activated"
            if existing_event is not None
            and existing_event["active_publication_id"] is not None
            else "inserted"
        )
        now = datetime.now(UTC).isoformat()
        temporal_domain_id = self._event_temporal_domain_id(
            event,
            primary_version,
        )

        with self._connection:
            for anchor in sorted(
                package.source_anchors,
                key=lambda row: row.source_anchor_id,
            ):
                version = self.get_source_version(anchor.source_version_id)
                if version is None:
                    raise ValueError("source anchor version does not exist")
                if anchor.char_end > len(version.content):
                    raise ValueError("source anchor exceeds source content")
                self._connection.execute(
                    """
                    INSERT OR IGNORE INTO source_anchors(
                        source_anchor_id,
                        source_version_id,
                        char_start,
                        char_end,
                        anchor_kind
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        anchor.source_anchor_id,
                        anchor.source_version_id,
                        anchor.char_start,
                        anchor.char_end,
                        anchor.anchor_kind,
                    ),
                )
            if existing_event is None:
                self._connection.execute(
                    """
                    INSERT INTO knowledge_roots(
                        root_id,
                        root_kind,
                        temporal_domain_id,
                        active_publication_id
                    )
                    VALUES (?, 'tmi_event', ?, NULL)
                    """,
                    (event.event_id, temporal_domain_id),
                )
                self._connection.execute(
                    """
                    INSERT INTO tmi_events(event_id, advisory_source_id)
                    VALUES (?, ?)
                    """,
                    (event.event_id, event.advisory_source_id),
                )
            elif existing_event["advisory_source_id"] != event.advisory_source_id:
                raise ValueError("event advisory source identity cannot change")
            elif existing_event["temporal_domain_id"] != temporal_domain_id:
                raise ValueError("event temporal domain cannot change")
            self._connection.execute(
                """
                INSERT INTO knowledge_publications(
                    publication_id,
                    root_id,
                    primary_source_version_id,
                    publication_digest,
                    temporal_domain_id,
                    published_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.publication_id,
                    event.event_id,
                    event.publication_source_version_id,
                    publication_digest,
                    temporal_domain_id,
                    now,
                ),
            )
            self._connection.execute(
                """
                INSERT INTO tmi_publication_details(
                    publication_id,
                    event_id,
                    effective_start,
                    effective_end,
                    issued_at,
                    reason_status,
                    reason_value
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.publication_id,
                    event.event_id,
                    self._datetime_text(event.effective_start),
                    self._datetime_text(event.effective_end),
                    self._datetime_text(event.issued_at),
                    event.reason_status,
                    event.reason_value,
                ),
            )
            self._connection.executemany(
                """
                INSERT INTO event_types(publication_id, event_type_iri)
                VALUES (?, ?)
                """,
                (
                    (event.publication_id, event_type_iri)
                    for event_type_iri in sorted(set(event.event_type_iris))
                ),
            )
            self._connection.executemany(
                """
                INSERT INTO event_facilities(publication_id, facility_id)
                VALUES (?, ?)
                """,
                (
                    (event.publication_id, facility_id)
                    for facility_id in sorted(set(event.facility_ids))
                ),
            )
            self._connection.executemany(
                """
                INSERT INTO publication_sources(
                    membership_id,
                    publication_id,
                    source_version_id,
                    source_role
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    (
                        stable_id(
                            "publication-source",
                            event.publication_id,
                            source_version_id,
                            (
                                "primary"
                                if source_version_id
                                == event.publication_source_version_id
                                else "supporting"
                            ),
                        ),
                        event.publication_id,
                        source_version_id,
                        (
                            "primary"
                            if source_version_id
                            == event.publication_source_version_id
                            else "supporting"
                        ),
                    )
                    for source_version_id in sorted(package.source_version_ids)
                ),
            )
            publication_fact_ids = {fact.fact_id for fact in package.facts}
            publication_gap_ids = {
                gap.profile_gap_id for gap in package.profile_gaps
            }
            publication_association_ids = {
                association.association_id
                for association in package.weather_associations
            }
            publication_observation_ids = {
                observation.observation_id
                for observation in package.public_observations
            }
            owner_ids = {
                "fact": publication_fact_ids,
                "profile_gap": publication_gap_ids,
                "weather_association": publication_association_ids,
                "public_observation": publication_observation_ids,
            }
            fact_links: dict[str, list[EventEvidenceLink]] = {
                fact_id: [] for fact_id in publication_fact_ids
            }
            for link in package.evidence_links:
                if link.owner_id not in owner_ids[link.owner_kind]:
                    raise ValueError(
                        "evidence link owner is outside publication"
                    )
                version = self.get_source_version(link.source_version_id)
                if version is None:
                    raise ValueError("evidence source version does not exist")
                if link.source_anchor_id is not None:
                    anchor = self.get_source_anchor(link.source_anchor_id)
                    if anchor is None:
                        raise ValueError("evidence source anchor does not exist")
                    if anchor.source_version_id != link.source_version_id:
                        raise ValueError(
                            "evidence anchor belongs to another source version"
                        )
                    anchored_text = version.content[
                        anchor.char_start : anchor.char_end
                    ]
                    if link.evidence_text != anchored_text:
                        raise ValueError(
                            "evidence text does not match source anchor"
                        )
                if link.owner_kind == "fact":
                    fact_links[link.owner_id].append(link)
            for fact in package.facts:
                if fact.evidence_mode != "source_text":
                    continue
                if not any(
                    link.source_anchor_id is not None
                    for link in fact_links[fact.fact_id]
                ):
                    raise ValueError(
                        "source-text evidence requires an exact source anchor"
                    )

            for gap in package.profile_gaps:
                version = self.get_source_version(gap.source_version_id)
                if version is None:
                    raise ValueError("profile gap source version does not exist")
                anchor = self.get_source_anchor(gap.source_anchor_id)
                if anchor is None:
                    raise ValueError("profile gap source anchor does not exist")
                if anchor.source_version_id != gap.source_version_id:
                    raise ValueError(
                        "profile gap anchor belongs to another source version"
                    )
                if (
                    version.content[anchor.char_start : anchor.char_end]
                    != gap.evidence_text
                ):
                    raise ValueError(
                        "profile gap evidence text does not match source anchor"
                    )

            for fact in sorted(package.facts, key=lambda row: row.fact_id):
                self._upsert_semantic_fact(fact)
                self._connection.execute(
                    """
                    INSERT INTO publication_facts(
                        membership_id,
                        publication_id,
                        fact_id
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        stable_id(
                            "publication-fact",
                            event.publication_id,
                            fact.fact_id,
                        ),
                        event.publication_id,
                        fact.fact_id,
                    ),
                )
            for gap in sorted(
                package.profile_gaps,
                key=lambda row: row.profile_gap_id,
            ):
                profile = gap.validation_profile
                self._connection.execute(
                    """
                    INSERT INTO profile_gaps(
                        publication_id,
                        gap_id,
                        event_id,
                        field_name,
                        value,
                        reason,
                        source_version_id,
                        source_anchor_id,
                        evidence_text,
                        evidence_ref,
                        profile_id,
                        profile_checksum,
                        validation_layer
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        gap.publication_id,
                        gap.profile_gap_id,
                        gap.event_id,
                        gap.field,
                        gap.value,
                        gap.reason,
                        gap.source_version_id,
                        gap.source_anchor_id,
                        gap.evidence_text,
                        gap.evidence_ref,
                        profile.profile_id,
                        profile.profile_checksum,
                        profile.layer,
                    ),
                )
            for link in sorted(
                package.evidence_links,
                key=lambda row: row.evidence_link_id,
            ):
                self._connection.execute(
                    """
                    INSERT INTO publication_evidence_links(
                        evidence_link_id,
                        publication_id,
                        owner_kind,
                        owner_id,
                        source_version_id,
                        source_anchor_id,
                        evidence_text,
                        evidence_ref
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        link.evidence_link_id,
                        link.publication_id,
                        link.owner_kind,
                        link.owner_id,
                        link.source_version_id,
                        link.source_anchor_id,
                        link.evidence_text,
                        link.evidence_ref,
                    ),
                )
            for association in sorted(
                package.weather_associations,
                key=lambda row: row.association_id,
            ):
                if self.get_source_version(
                    association.source_version_id
                ) is None:
                    raise ValueError(
                        "weather association source version does not exist"
                    )
                self._connection.execute(
                    """
                    INSERT INTO weather_associations(
                        publication_id,
                        association_id,
                        event_id,
                        report_id,
                        facility_id,
                        relation_type,
                        selection_method,
                        relevant_times_json,
                        source_version_id,
                        causal_claim
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (
                        association.publication_id,
                        association.association_id,
                        association.event_id,
                        association.report_id,
                        association.facility_id,
                        association.relation_type,
                        association.selection_method,
                        json.dumps(
                            association.relevant_times,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        association.source_version_id,
                    ),
                )
            for observation in sorted(
                package.public_observations,
                key=lambda row: row.observation_id,
            ):
                if self.get_source_version(
                    observation.source_version_id
                ) is None:
                    raise ValueError(
                        "public observation source version does not exist"
                    )
                if not set(observation.fact_ids) <= publication_fact_ids:
                    raise ValueError(
                        "public observation fact is outside publication"
                    )
                self._connection.execute(
                    """
                    INSERT INTO public_observations(
                        publication_id,
                        observation_id,
                        event_id,
                        phase,
                        metric_key,
                        value_json,
                        unit_iri,
                        profile_id,
                        profile_checksum,
                        source_version_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        observation.publication_id,
                        observation.observation_id,
                        observation.event_id,
                        observation.phase,
                        observation.metric_key,
                        self._observation_value_json(observation.value),
                        observation.unit_iri,
                        observation.profile_id,
                        observation.profile_checksum,
                        observation.source_version_id,
                    ),
                )
                self._connection.executemany(
                    """
                    INSERT INTO observation_facts(
                        publication_id,
                        observation_id,
                        fact_id
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        (
                            observation.publication_id,
                            observation.observation_id,
                            fact_id,
                        )
                        for fact_id in sorted(
                            set(
                                package.observation_fact_ids[
                                    observation.observation_id
                                ]
                            )
                        )
                    ),
                )
            self._connection.execute(
                """
                UPDATE knowledge_roots
                SET active_publication_id = ?
                WHERE root_id = ?
                """,
                (event.publication_id, event.event_id),
            )
            for source_version_id in sorted(package.source_version_ids):
                self._connection.execute(
                    """
                    UPDATE sources
                    SET latest_accepted_version_id = ?
                    WHERE source_id = (
                        SELECT source_id
                        FROM source_versions
                        WHERE source_version_id = ?
                    )
                    """,
                    (source_version_id, source_version_id),
                )
            self._write_ingestion_result(attempt.result)
            self._increment_knowledge_revision(now)
        return outcome

    def get_event(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> TMIEventRecord | None:
        """Return the active or explicitly selected immutable publication."""

        selected_publication_id = self._select_publication_id(
            event_id,
            publication_id,
        )
        if selected_publication_id is None:
            return None
        row = self._connection.execute(
            """
            SELECT
                publication.publication_id,
                publication.primary_source_version_id
                    AS publication_source_version_id,
                detail.event_id,
                detail.effective_start,
                detail.effective_end,
                detail.issued_at,
                detail.reason_status,
                detail.reason_value,
                event.advisory_source_id
            FROM knowledge_publications AS publication
            JOIN tmi_publication_details AS detail
              ON detail.publication_id = publication.publication_id
            JOIN tmi_events AS event
              ON event.event_id = detail.event_id
            WHERE publication.publication_id = ?
              AND detail.event_id = ?
            """,
            (selected_publication_id, event_id),
        ).fetchone()
        if row is None:
            return None
        event_type_iris = tuple(
            item["event_type_iri"]
            for item in self._connection.execute(
                """
                SELECT event_type_iri
                FROM event_types
                WHERE publication_id = ?
                ORDER BY event_type_iri
                """,
                (selected_publication_id,),
            ).fetchall()
        )
        facility_ids = tuple(
            item["facility_id"]
            for item in self._connection.execute(
                """
                SELECT facility_id
                FROM event_facilities
                WHERE publication_id = ?
                ORDER BY facility_id
                """,
                (selected_publication_id,),
            ).fetchall()
        )
        return TMIEventRecord(
            event_id=row["event_id"],
            publication_id=row["publication_id"],
            advisory_source_id=row["advisory_source_id"],
            publication_source_version_id=row[
                "publication_source_version_id"
            ],
            event_type_iris=event_type_iris,
            facility_ids=facility_ids,
            effective_start=self._parse_datetime(row["effective_start"]),
            effective_end=self._parse_datetime(row["effective_end"]),
            issued_at=self._parse_datetime(row["issued_at"]),
            reason_status=row["reason_status"],
            reason_value=row["reason_value"],
        )

    def list_tmi_event_publications(
        self,
        *,
        active_only: bool = False,
    ) -> tuple[TMIEventRecord, ...]:
        """Return active or all immutable TMI event publications."""

        if active_only:
            rows = self._connection.execute(
                """
                SELECT
                    event.event_id,
                    root.active_publication_id AS publication_id
                FROM tmi_events AS event
                JOIN knowledge_roots AS root
                  ON root.root_id = event.event_id
                WHERE root.active_publication_id IS NOT NULL
                ORDER BY event.event_id
                """
            ).fetchall()
        else:
            rows = self._connection.execute(
                """
                SELECT detail.event_id, detail.publication_id
                FROM tmi_publication_details AS detail
                ORDER BY detail.event_id, detail.publication_id
                """
            ).fetchall()
        return tuple(
            event
            for row in rows
            if (
                event := self.get_event(
                    row["event_id"],
                    publication_id=row["publication_id"],
                )
            )
            is not None
        )

    def find_tmi_events(
        self,
        query: TMIEventQuery,
    ) -> TMIEventPage:
        """Return one bounded deterministic page of active TMI events."""

        predicates: list[str] = []
        parameters: list[object] = []
        if query.event_type_iri is not None:
            predicates.append(
                """
                EXISTS (
                    SELECT 1
                    FROM event_types AS type
                    WHERE type.publication_id =
                          root.active_publication_id
                      AND type.event_type_iri = ?
                )
                """
            )
            parameters.append(query.event_type_iri)
        if query.facility_id is not None:
            predicates.append(
                """
                EXISTS (
                    SELECT 1
                    FROM event_facilities AS facility
                    WHERE facility.publication_id =
                          root.active_publication_id
                      AND facility.facility_id = ?
                )
                """
            )
            parameters.append(query.facility_id)
        if query.reason_status is not None:
            predicates.append("detail.reason_status = ?")
            parameters.append(query.reason_status)
        if query.reason_value is not None:
            predicates.append("detail.reason_value = ?")
            parameters.append(query.reason_value)
        where_clause = (
            "WHERE " + " AND ".join(predicates)
            if predicates
            else ""
        )
        base_query = f"""
            FROM tmi_events AS event
            JOIN knowledge_roots AS root
              ON root.root_id = event.event_id
            JOIN tmi_publication_details AS detail
              ON detail.publication_id = root.active_publication_id
            {where_clause}
        """
        total_matches = self._connection.execute(
            f"SELECT COUNT(*) {base_query}",
            parameters,
        ).fetchone()[0]
        selected = self._connection.execute(
            f"""
            SELECT event.event_id, root.active_publication_id
            {base_query}
            ORDER BY event.event_id
            LIMIT ? OFFSET ?
            """,
            [*parameters, query.limit, query.offset],
        ).fetchall()
        events = tuple(
            event_record
            for row in selected
            if (
                event_record := self.get_event(
                    row["event_id"],
                    publication_id=row["active_publication_id"],
                )
            )
            is not None
        )
        return TMIEventPage(
            dataset_id=self.dataset_id,
            total_matches=total_matches,
            offset=query.offset,
            limit=query.limit,
            events=events,
        )

    def get_event_facts(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> tuple[SemanticFactRecord, ...]:
        """Return deterministically ordered facts for one publication."""

        selected_publication_id = self._select_publication_id(
            event_id,
            publication_id,
        )
        if selected_publication_id is None:
            return ()
        rows = self._connection.execute(
            """
            SELECT fact.*
            FROM publication_facts AS membership
            JOIN semantic_facts AS fact
              ON fact.fact_id = membership.fact_id
            WHERE membership.publication_id = ?
            ORDER BY fact.fact_id
            """,
            (selected_publication_id,),
        ).fetchall()
        return tuple(self._semantic_fact_from_row(row) for row in rows)

    def get_event_evidence(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> tuple[EventEvidenceLink, ...]:
        """Return event-scoped evidence for one immutable publication."""

        selected_publication_id = self._select_publication_id(
            event_id,
            publication_id,
        )
        if selected_publication_id is None:
            return ()
        rows = self._connection.execute(
            """
            SELECT *
            FROM publication_evidence_links
            WHERE publication_id = ?
            ORDER BY evidence_link_id
            """,
            (selected_publication_id,),
        ).fetchall()
        return tuple(
            EventEvidenceLink(
                evidence_link_id=row["evidence_link_id"],
                event_id=event_id,
                publication_id=row["publication_id"],
                owner_kind=row["owner_kind"],
                owner_id=row["owner_id"],
                source_version_id=row["source_version_id"],
                source_anchor_id=row["source_anchor_id"],
                evidence_text=row["evidence_text"],
                evidence_ref=row["evidence_ref"],
            )
            for row in rows
        )

    def get_event_sources(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> tuple[SourceVersionRecord, ...]:
        """Return ordered exact source versions bound to one publication."""

        selected_publication_id = self._select_publication_id(
            event_id,
            publication_id,
        )
        if selected_publication_id is None:
            return ()
        rows = self._connection.execute(
            """
            SELECT version.*
            FROM publication_sources AS binding
            JOIN source_versions AS version
              ON version.source_version_id = binding.source_version_id
            WHERE binding.publication_id = ?
            ORDER BY version.source_version_id
            """,
            (selected_publication_id,),
        ).fetchall()
        return tuple(self._source_version_from_row(row) for row in rows)

    def get_active_event_ids_by_source_version(
        self,
        source_version_ids: Sequence[str],
    ) -> dict[str, tuple[str, ...]]:
        """Map exact source versions to active TMI events that bind them."""

        selected = tuple(sorted(set(source_version_ids)))
        if not selected:
            return {}
        placeholders = ", ".join("?" for _value in selected)
        rows = self._connection.execute(
            f"""
            SELECT
                binding.source_version_id,
                detail.event_id
            FROM publication_sources AS binding
            JOIN tmi_publication_details AS detail
              ON detail.publication_id = binding.publication_id
            JOIN knowledge_roots AS root
              ON root.root_id = detail.event_id
             AND root.active_publication_id = detail.publication_id
            WHERE binding.source_version_id IN ({placeholders})
            ORDER BY binding.source_version_id, detail.event_id
            """,
            selected,
        ).fetchall()
        mapped: dict[str, list[str]] = {}
        for row in rows:
            mapped.setdefault(row["source_version_id"], []).append(
                row["event_id"]
            )
        return {
            source_version_id: tuple(event_ids)
            for source_version_id, event_ids in mapped.items()
        }

    def get_event_weather(
        self,
        event_id: str,
    ) -> tuple[EventWeatherAssociation, ...]:
        """Return active, non-causal weather associations for one event."""

        publication_id = self._select_publication_id(event_id, None)
        if publication_id is None:
            return ()
        rows = self._connection.execute(
            """
            SELECT *
            FROM weather_associations
            WHERE event_id = ?
              AND publication_id = ?
            ORDER BY association_id
            """,
            (event_id, publication_id),
        ).fetchall()
        return tuple(
            EventWeatherAssociation(
                association_id=row["association_id"],
                event_id=row["event_id"],
                publication_id=row["publication_id"],
                report_id=row["report_id"],
                facility_id=row["facility_id"],
                relation_type=row["relation_type"],
                selection_method=row["selection_method"],
                relevant_times=json.loads(row["relevant_times_json"]),
                source_version_id=row["source_version_id"],
                causal_claim=False,
            )
            for row in rows
        )

    def get_event_profile_gaps(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> tuple[EventProfileGapRecord, ...]:
        """Return profile gaps for the active or selected publication."""

        selected_publication_id = self._select_publication_id(
            event_id,
            publication_id,
        )
        if selected_publication_id is None:
            return ()
        rows = self._connection.execute(
            """
            SELECT *
            FROM profile_gaps
            WHERE event_id = ?
              AND publication_id = ?
            ORDER BY gap_id
            """,
            (event_id, selected_publication_id),
        ).fetchall()
        from aviation_agentic_ai.agent_system.contracts import (
            ValidationProfileRef,
        )

        return tuple(
            EventProfileGapRecord(
                profile_gap_id=row["gap_id"],
                event_id=row["event_id"],
                publication_id=row["publication_id"],
                field=row["field_name"],
                value=row["value"],
                evidence_text=row["evidence_text"],
                reason=row["reason"],
                source_version_id=row["source_version_id"],
                source_anchor_id=row["source_anchor_id"],
                evidence_ref=row["evidence_ref"],
                validation_profile=ValidationProfileRef(
                    profile_id=row["profile_id"],
                    profile_checksum=row["profile_checksum"],
                    layer=row["validation_layer"],
                ),
            )
            for row in rows
        )

    def get_event_observations(
        self,
        event_id: str,
        phases: tuple[str, ...],
    ) -> tuple[PublicObservationRecord, ...]:
        """Return active public observations filtered to explicit phases."""

        publication_id = self._select_publication_id(event_id, None)
        if publication_id is None:
            return ()
        allowed_phases = {"baseline", "active", "recovery"}
        if not set(phases) <= allowed_phases:
            raise ValueError("unknown public observation phase")
        predicates = ["observation.event_id = ?"]
        parameters: list[object] = [event_id, publication_id]
        predicates.append("observation.publication_id = ?")
        if phases:
            placeholders = ", ".join("?" for _ in phases)
            predicates.append(f"observation.phase IN ({placeholders})")
            parameters.extend(phases)
        rows = self._connection.execute(
            f"""
            SELECT observation.*
            FROM public_observations AS observation
            WHERE {" AND ".join(predicates)}
            ORDER BY
                observation.phase,
                observation.metric_key,
                observation.observation_id
            """,
            parameters,
        ).fetchall()
        observations: list[PublicObservationRecord] = []
        for row in rows:
            fact_ids = tuple(
                fact_row["fact_id"]
                for fact_row in self._connection.execute(
                    """
                    SELECT fact_id
                    FROM observation_facts
                    WHERE publication_id = ?
                      AND observation_id = ?
                    ORDER BY fact_id
                    """,
                    (
                        row["publication_id"],
                        row["observation_id"],
                    ),
                ).fetchall()
            )
            observations.append(
                PublicObservationRecord(
                    observation_id=row["observation_id"],
                    event_id=row["event_id"],
                    publication_id=row["publication_id"],
                    phase=row["phase"],
                    metric_key=row["metric_key"],
                    value=self._observation_value_from_json(
                        row["value_json"]
                    ),
                    unit_iri=row["unit_iri"],
                    fact_ids=fact_ids,
                    profile_id=row["profile_id"],
                    profile_checksum=row["profile_checksum"],
                    source_version_id=row["source_version_id"],
                )
            )
        return tuple(observations)

    def search_source_text(
        self,
        query: str,
        *,
        source_version_ids: tuple[str, ...] | None = None,
        families: tuple[SourceFamily, ...] = (),
        event_id: str | None = None,
        current_only: bool = True,
        limit: int = 10,
    ) -> tuple[SourceChunkRecord, ...]:
        """Search bounded source chunks with optional family and event scope."""

        if not query.strip():
            raise ValueError("source text query must not be empty")
        if limit < 1 or limit > 100:
            raise ValueError("source text search limit must be between 1 and 100")
        if source_version_ids == ():
            return ()
        predicates = ["source_chunks_fts MATCH ?"]
        parameters: list[object] = [query]
        if source_version_ids is not None:
            selected_version_ids = tuple(sorted(set(source_version_ids)))
            placeholders = ", ".join("?" for _ in selected_version_ids)
            predicates.append(
                f"chunk.source_version_id IN ({placeholders})"
            )
            parameters.extend(selected_version_ids)
        if families:
            placeholders = ", ".join("?" for _ in families)
            predicates.append(f"version.family IN ({placeholders})")
            parameters.extend(family.value for family in families)
        if event_id is not None:
            predicates.append("chunk.event_id = ?")
            parameters.append(event_id)
        if current_only:
            predicates.append(
                """
                chunk.source_version_id =
                source.latest_observed_version_id
                """
            )
        parameters.append(limit)
        rows = self._connection.execute(
            f"""
            SELECT chunk.*
            FROM source_chunks_fts
            JOIN source_chunks AS chunk
              ON chunk.rowid = source_chunks_fts.rowid
            JOIN source_versions AS version
              ON version.source_version_id = chunk.source_version_id
            JOIN sources AS source
              ON source.source_id = version.source_id
            WHERE {" AND ".join(predicates)}
            ORDER BY bm25(source_chunks_fts), chunk.chunk_id
            LIMIT ?
            """,
            parameters,
        ).fetchall()
        return tuple(self._source_chunk_from_row(row) for row in rows)

    def upsert_source_chunks(
        self,
        chunks: Sequence[SourceChunkRecord],
    ) -> int:
        """Persist immutable derived chunks and their exact source anchors."""

        inserted = 0
        with self._connection:
            for chunk in chunks:
                existing = self.get_source_chunk(chunk.chunk_id)
                if existing is not None:
                    if existing != chunk:
                        raise ValueError("source chunk is immutable")
                    continue
                version = self.get_source_version(chunk.source_version_id)
                if version is None:
                    raise ValueError("source chunk version does not exist")
                if chunk.char_end > len(version.content):
                    raise ValueError("source chunk exceeds source content")
                if (
                    chunk.chunk_kind == "source_record"
                    and version.content[
                        chunk.char_start : chunk.char_end
                    ]
                    != chunk.text
                ):
                    raise ValueError(
                        "source-record chunk must match exact source text"
                    )
                anchor = SourceAnchorRecord(
                    source_anchor_id=chunk.source_anchor_id,
                    source_version_id=chunk.source_version_id,
                    char_start=chunk.char_start,
                    char_end=chunk.char_end,
                    anchor_kind=(
                        "full_record"
                        if (
                            chunk.char_start == 0
                            and chunk.char_end == len(version.content)
                        )
                        else "text_span"
                    ),
                )
                self._connection.execute(
                    """
                    INSERT OR IGNORE INTO source_anchors(
                        source_anchor_id,
                        source_version_id,
                        char_start,
                        char_end,
                        anchor_kind
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        anchor.source_anchor_id,
                        anchor.source_version_id,
                        anchor.char_start,
                        anchor.char_end,
                        anchor.anchor_kind,
                    ),
                )
                self._connection.execute(
                    """
                    INSERT INTO source_chunks(
                        chunk_id,
                        source_version_id,
                        event_id,
                        chunk_kind,
                        text,
                        char_start,
                        char_end,
                        source_anchor_id,
                        representation_version,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk.chunk_id,
                        chunk.source_version_id,
                        chunk.event_id,
                        chunk.chunk_kind,
                        chunk.text,
                        chunk.char_start,
                        chunk.char_end,
                        chunk.source_anchor_id,
                        chunk.representation_version,
                        json.dumps(
                            chunk.metadata,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                    ),
                )
                inserted += 1
            if inserted:
                self._increment_knowledge_revision(
                    datetime.now(UTC).isoformat()
                )
        return inserted

    def get_source_chunk(
        self,
        chunk_id: str,
    ) -> SourceChunkRecord | None:
        """Return one immutable source chunk."""

        row = self._connection.execute(
            """
            SELECT *
            FROM source_chunks
            WHERE chunk_id = ?
            """,
            (chunk_id,),
        ).fetchone()
        return self._source_chunk_from_row(row) if row is not None else None

    def list_source_chunks(
        self,
        *,
        source_version_ids: tuple[str, ...] = (),
        event_id: str | None = None,
        chunk_kind: str | None = None,
    ) -> tuple[SourceChunkRecord, ...]:
        """Return derived chunks under explicit optional bounds."""

        predicates: list[str] = []
        parameters: list[object] = []
        if source_version_ids:
            placeholders = ", ".join("?" for _ in source_version_ids)
            predicates.append(
                f"source_version_id IN ({placeholders})"
            )
            parameters.extend(source_version_ids)
        if event_id is not None:
            predicates.append("event_id = ?")
            parameters.append(event_id)
        if chunk_kind is not None:
            predicates.append("chunk_kind = ?")
            parameters.append(chunk_kind)
        where_clause = (
            "WHERE " + " AND ".join(predicates)
            if predicates
            else ""
        )
        rows = self._connection.execute(
            f"""
            SELECT *
            FROM source_chunks
            {where_clause}
            ORDER BY chunk_id
            """,
            parameters,
        ).fetchall()
        return tuple(self._source_chunk_from_row(row) for row in rows)

    def get_knowledge_revision(self) -> int:
        """Return the current authoritative semantic-store revision."""

        row = self._connection.execute(
            """
            SELECT value
            FROM store_metadata
            WHERE key = 'knowledge_revision'
            """
        ).fetchone()
        if row is None:
            raise ValueError("knowledge revision metadata is missing")
        return int(row["value"])

    def set_vector_index_state(
        self,
        state: VectorIndexStateRecord,
    ) -> None:
        """Publish rebuildable vector-index status."""

        with self._connection:
            self._connection.execute(
                """
                INSERT INTO vector_index_state(
                    collection_name,
                    representation_version,
                    embedding_model_id,
                    embedding_dimension,
                    indexed_knowledge_revision,
                    document_count,
                    vector_count,
                    status,
                    updated_at,
                    failure_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(collection_name) DO UPDATE SET
                    representation_version =
                        excluded.representation_version,
                    embedding_model_id = excluded.embedding_model_id,
                    embedding_dimension = excluded.embedding_dimension,
                    indexed_knowledge_revision =
                        excluded.indexed_knowledge_revision,
                    document_count = excluded.document_count,
                    vector_count = excluded.vector_count,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    failure_reason = excluded.failure_reason
                """,
                (
                    state.collection_name,
                    state.representation_version,
                    state.embedding_model_id,
                    state.embedding_dimension,
                    state.indexed_knowledge_revision,
                    state.document_count,
                    state.vector_count,
                    state.status,
                    state.updated_at.isoformat(),
                    state.failure_reason,
                ),
            )

    def get_vector_index_state(
        self,
        collection_name: str,
    ) -> VectorIndexStateRecord | None:
        """Return rebuildable state for one vector collection."""

        row = self._connection.execute(
            """
            SELECT *
            FROM vector_index_state
            WHERE collection_name = ?
            """,
            (collection_name,),
        ).fetchone()
        if row is None:
            return None
        return VectorIndexStateRecord(
            collection_name=row["collection_name"],
            representation_version=row["representation_version"],
            embedding_model_id=row["embedding_model_id"],
            embedding_dimension=row["embedding_dimension"],
            indexed_knowledge_revision=row[
                "indexed_knowledge_revision"
            ],
            document_count=row["document_count"],
            vector_count=row["vector_count"],
            status=row["status"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
            failure_reason=row["failure_reason"],
        )

    def _select_publication_id(
        self,
        event_id: str,
        publication_id: str | None,
    ) -> str | None:
        if publication_id is not None:
            row = self._connection.execute(
                """
                SELECT publication.publication_id
                FROM knowledge_publications AS publication
                JOIN tmi_publication_details AS detail
                  ON detail.publication_id = publication.publication_id
                WHERE detail.event_id = ?
                  AND publication.publication_id = ?
                """,
                (event_id, publication_id),
            ).fetchone()
        else:
            row = self._connection.execute(
                """
                SELECT active_publication_id AS publication_id
                FROM knowledge_roots
                WHERE root_id = ? AND root_kind = 'tmi_event'
                """,
                (event_id,),
            ).fetchone()
        if row is None:
            return None
        return row["publication_id"]

    @staticmethod
    def _event_temporal_domain_id(
        event: TMIEventRecord,
        primary_version: SourceVersionRecord,
    ) -> str:
        configured = primary_version.metadata.get("temporal_domain_id")
        if isinstance(configured, str) and configured:
            return configured
        timestamp = event.effective_start or event.issued_at
        if timestamp is not None:
            return f"atcscc:{timestamp.astimezone(UTC):%Y-%m}"
        if primary_version.logical_time:
            try:
                logical_time = datetime.fromisoformat(
                    primary_version.logical_time.replace("Z", "+00:00")
                )
            except ValueError:
                pass
            else:
                if logical_time.tzinfo is not None:
                    return f"atcscc:{logical_time.astimezone(UTC):%Y-%m}"
        return "atcscc:undated"

    def _upsert_semantic_fact(self, fact: SemanticFactRecord) -> None:
        row = self._connection.execute(
            "SELECT * FROM semantic_facts WHERE fact_id = ?",
            (fact.fact_id,),
        ).fetchone()
        if row is not None:
            if self._semantic_fact_from_row(row) != fact:
                raise ValueError("semantic fact identity collision")
            return
        profile = fact.validation_profile
        self._connection.execute(
            """
            INSERT INTO semantic_facts(
                fact_id,
                subject_iri,
                subject_class_iri,
                predicate_iri,
                object_kind,
                object_value,
                object_class_iri,
                datatype_iri,
                profile_id,
                profile_checksum,
                validation_layer,
                evidence_mode
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fact.fact_id,
                fact.subject_iri,
                fact.subject_class_iri,
                fact.predicate_iri,
                fact.object_kind,
                fact.object_value,
                fact.object_class_iri,
                fact.datatype_iri,
                profile.profile_id,
                profile.profile_checksum,
                profile.layer,
                fact.evidence_mode,
            ),
        )

    @staticmethod
    def _semantic_fact_from_row(
        row: sqlite3.Row,
    ) -> SemanticFactRecord:
        from aviation_agentic_ai.agent_system.contracts import (
            ValidationProfileRef,
        )

        return SemanticFactRecord(
            fact_id=row["fact_id"],
            subject_iri=row["subject_iri"],
            subject_class_iri=row["subject_class_iri"],
            predicate_iri=row["predicate_iri"],
            object_kind=row["object_kind"],
            object_value=row["object_value"],
            object_class_iri=row["object_class_iri"],
            datatype_iri=row["datatype_iri"],
            validation_profile=ValidationProfileRef(
                profile_id=row["profile_id"],
                profile_checksum=row["profile_checksum"],
                layer=row["validation_layer"],
            ),
            evidence_mode=row["evidence_mode"],
        )

    def _write_ingestion_result(self, result: IngestionResult) -> None:
        self._connection.execute(
            """
            INSERT INTO ingestion_results(
                source_version_id,
                source_id,
                status,
                event_id,
                publication_id,
                reason,
                provider_call_count,
                tmi_family,
                preflight_eligible
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_version_id) DO UPDATE SET
                status = excluded.status,
                event_id = excluded.event_id,
                publication_id = excluded.publication_id,
                reason = excluded.reason,
                provider_call_count = excluded.provider_call_count,
                tmi_family = excluded.tmi_family,
                preflight_eligible = excluded.preflight_eligible
            """,
            (
                result.source_version_id,
                result.source_id,
                result.status,
                result.event_id,
                result.publication_id,
                result.reason,
                result.provider_call_count,
                result.tmi_family,
                (
                    None
                    if result.preflight_eligible is None
                    else int(result.preflight_eligible)
                ),
            ),
        )

    def _get_ingestion_result(
        self,
        source_version_id: str,
    ) -> IngestionResult | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM ingestion_results
            WHERE source_version_id = ?
            """,
            (source_version_id,),
        ).fetchone()
        if row is None:
            return None
        return IngestionResult(
            source_version_id=row["source_version_id"],
            source_id=row["source_id"],
            status=row["status"],
            event_id=row["event_id"],
            publication_id=row["publication_id"],
            reason=row["reason"],
            provider_call_count=row["provider_call_count"],
            tmi_family=row["tmi_family"],
            preflight_eligible=(
                None
                if row["preflight_eligible"] is None
                else bool(row["preflight_eligible"])
            ),
        )

    def get_ingestion_result(
        self,
        source_version_id: str,
    ) -> IngestionResult | None:
        """Return the latest operational outcome for one source version."""

        return self._get_ingestion_result(source_version_id)

    def start_ingestion_run(
        self,
        ingestion_run_id: str,
        *,
        started_at: datetime,
    ) -> None:
        """Open one operational ingestion run."""

        with self._connection:
            self._connection.execute(
                """
                INSERT INTO ingestion_runs(
                    ingestion_run_id,
                    started_at,
                    status
                )
                VALUES (?, ?, 'running')
                """,
                (ingestion_run_id, started_at.isoformat()),
            )

    def finish_ingestion_run(
        self,
        ingestion_run_id: str,
        *,
        status: str,
        attempted_count: int,
        ok_count: int,
        insufficient_count: int,
        blocked_count: int,
        ended_at: datetime,
    ) -> None:
        """Close one ingestion run with its compact outcome counts."""

        with self._connection:
            self._connection.execute(
                """
                UPDATE ingestion_runs
                SET ended_at = ?,
                    status = ?,
                    attempted_count = ?,
                    ok_count = ?,
                    insufficient_count = ?,
                    blocked_count = ?
                WHERE ingestion_run_id = ?
                """,
                (
                    ended_at.isoformat(),
                    status,
                    attempted_count,
                    ok_count,
                    insufficient_count,
                    blocked_count,
                    ingestion_run_id,
                ),
            )

    def replace_agent_usage(
        self,
        ingestion_run_id: str,
        records: Sequence[AgentUsageRecord],
    ) -> None:
        """Persist payload-free Agent usage for one ingestion run."""

        if not records:
            return
        with self._connection:
            self._connection.executemany(
                """
                INSERT OR REPLACE INTO agent_usage(
                    ingestion_run_id,
                    source_id,
                    event_id,
                    task_id,
                    role,
                    task_scope,
                    execution_mode,
                    outcome,
                    detail_status,
                    activation_reason,
                    provider_call_count,
                    tool_call_count,
                    input_tokens,
                    output_tokens,
                    provider_latency_ms,
                    tool_latency_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (
                        ingestion_run_id,
                        row.source_id,
                        row.event_id,
                        row.task_id,
                        row.role,
                        row.task_scope,
                        row.execution_mode,
                        row.outcome,
                        row.detail_status,
                        row.activation_reason,
                        row.provider_call_count,
                        row.tool_call_count,
                        row.input_tokens,
                        row.output_tokens,
                        row.provider_latency_ms,
                        row.tool_latency_ms,
                    )
                    for row in records
                ),
            )

    def list_agent_usage(
        self,
        *,
        ingestion_run_id: str | None = None,
    ) -> tuple[AgentUsageRecord, ...]:
        """Return payload-free Agent usage in stable order."""

        if ingestion_run_id is None:
            rows = self._connection.execute(
                """
                SELECT *
                FROM agent_usage
                ORDER BY ingestion_run_id, source_id, role, task_scope
                """
            ).fetchall()
        else:
            rows = self._connection.execute(
                """
                SELECT *
                FROM agent_usage
                WHERE ingestion_run_id = ?
                ORDER BY source_id, role, task_scope
                """,
                (ingestion_run_id,),
            ).fetchall()
        return tuple(
            AgentUsageRecord(
                source_id=row["source_id"],
                event_id=row["event_id"],
                task_id=row["task_id"],
                role=row["role"],
                task_scope=row["task_scope"],
                execution_mode=row["execution_mode"],
                outcome=row["outcome"],
                detail_status=row["detail_status"],
                activation_reason=row["activation_reason"],
                provider_call_count=row["provider_call_count"],
                tool_call_count=row["tool_call_count"],
                input_tokens=row["input_tokens"],
                output_tokens=row["output_tokens"],
                provider_latency_ms=row["provider_latency_ms"],
                tool_latency_ms=row["tool_latency_ms"],
            )
            for row in rows
        )

    def _increment_knowledge_revision(self, updated_at: str) -> None:
        self._connection.execute(
            """
            UPDATE store_metadata
            SET value = CAST(value AS INTEGER) + 1
            WHERE key = 'knowledge_revision'
            """
        )
        self._connection.execute(
            """
            UPDATE store_metadata
            SET value = ?
            WHERE key = 'updated_at'
            """,
            (updated_at,),
        )

    @staticmethod
    def _observation_value_json(
        value: int | Decimal | None,
    ) -> str:
        if value is None:
            payload: dict[str, object] = {"kind": "none", "value": None}
        elif isinstance(value, Decimal):
            payload = {"kind": "decimal", "value": str(value)}
        else:
            payload = {"kind": "int", "value": value}
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _observation_value_from_json(
        value_json: str | None,
    ) -> int | Decimal | None:
        if value_json is None:
            return None
        payload = json.loads(value_json)
        if payload["kind"] == "none":
            return None
        if payload["kind"] == "decimal":
            return Decimal(payload["value"])
        return int(payload["value"])

    @staticmethod
    def _datetime_text(value: datetime | None) -> str | None:
        return value.isoformat() if value is not None else None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value is not None else None

    @staticmethod
    def _source_version_from_row(row: sqlite3.Row) -> SourceVersionRecord:
        return SourceVersionRecord(
            source_version_id=row["source_version_id"],
            source_id=row["source_id"],
            family=SourceFamily(row["family"]),
            asset_id=row["asset_id"],
            content=row["content"],
            content_sha256=row["content_sha256"],
            source_url=row["source_url"],
            logical_time=row["logical_time"],
            metadata=json.loads(row["metadata_json"]),
        )

    @staticmethod
    def _source_chunk_from_row(row: sqlite3.Row) -> SourceChunkRecord:
        return SourceChunkRecord(
            chunk_id=row["chunk_id"],
            source_version_id=row["source_version_id"],
            event_id=row["event_id"],
            chunk_kind=row["chunk_kind"],
            text=row["text"],
            char_start=row["char_start"],
            char_end=row["char_end"],
            source_anchor_id=row["source_anchor_id"],
            representation_version=row["representation_version"],
            metadata=json.loads(row["metadata_json"]),
        )
