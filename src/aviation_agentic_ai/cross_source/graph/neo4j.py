from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from aviation_agentic_ai.cross_source.artifacts import read_jsonl, write_jsonl
from aviation_agentic_ai.cross_source.contracts import (
    AlignmentDecision,
    AlignmentStatus,
    CanonicalEntity,
    CrossSourceLink,
    Mention,
    TermConcept,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


DriverFactory = Callable[..., Any]

RELATIONSHIP_TYPES = {
    "DENOTES",
    "DERIVED_FROM",
    "HAS_CONTEMPORANEOUS_OBSERVATION",
    "HAS_OVERLAPPING_FORECAST",
}


@dataclass(frozen=True)
class Neo4jArtifacts:
    nodes_path: Path
    relationships_path: Path
    node_count: int
    relationship_count: int


def _node(
    node_id: str,
    label: str,
    *,
    snapshot_set_id: str,
    **properties: Any,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "label": label,
        "properties": {
            "id": node_id,
            "snapshot_set_id": snapshot_set_id,
            **properties,
        },
    }


def _relationship(
    relationship_id: str,
    relationship_type: str,
    start_id: str,
    end_id: str,
    **properties: Any,
) -> dict[str, Any]:
    if relationship_type not in RELATIONSHIP_TYPES:
        raise ValueError(f"Unsupported Neo4j relationship type: {relationship_type}")
    return {
        "id": relationship_id,
        "type": relationship_type,
        "start_id": start_id,
        "end_id": end_id,
        "properties": {"id": relationship_id, **properties},
    }


def build_neo4j_projection(
    *,
    facilities: Iterable[CanonicalEntity],
    terms: Iterable[TermConcept],
    mentions: Iterable[Mention],
    decisions: Iterable[AlignmentDecision],
    links: Iterable[CrossSourceLink],
    snapshot_set_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Project the accepted canonical graph into a Neo4j property graph."""
    nodes: dict[str, dict[str, Any]] = {}
    relationships: dict[str, dict[str, Any]] = {}

    for facility in facilities:
        nodes[facility.entity_id] = _node(
            facility.entity_id,
            "Facility",
            snapshot_set_id=snapshot_set_id,
            preferred_label=facility.preferred_label,
            entity_type=facility.entity_type.value,
            codes=[f"{code.scheme}:{code.value}" for code in facility.codes],
            aliases=facility.aliases,
            source_refs=facility.source_refs,
        )
    for term in terms:
        nodes[term.term_id] = _node(
            term.term_id,
            "OperationalTerm",
            snapshot_set_id=snapshot_set_id,
            preferred_label=term.preferred_label,
            abbreviation=term.abbreviation,
            term_category=term.term_category.value,
            aliases=term.aliases,
            source_refs=term.source_refs,
        )

    mention_by_id = {mention.mention_id: mention for mention in mentions}
    for decision in decisions:
        if decision.status is not AlignmentStatus.ACCEPTED or not decision.target_id:
            continue
        mention = mention_by_id[decision.mention_id]
        mention_id = f"urn:aviation-agentic-ai:mention:{mention.mention_id}"
        source_id = f"urn:aviation-agentic-ai:source-record:{mention.source_id}"
        nodes[mention_id] = _node(
            mention_id,
            "AcceptedMention",
            snapshot_set_id=snapshot_set_id,
            surface_form=mention.surface_form,
            normalized_form=mention.normalized_form,
            mention_type=mention.mention_type.value,
            evidence_text=mention.evidence_text,
            gate_score=decision.gate_score,
            alignment_method=decision.method.value,
        )
        nodes.setdefault(
            source_id,
            _node(
                source_id,
                "SourceRecord",
                snapshot_set_id=snapshot_set_id,
                source_id=mention.source_id,
                source_family=mention.source_family,
            ),
        )
        denotes_id = stable_id("neo4j-rel", mention_id, "DENOTES", decision.target_id)
        relationships[denotes_id] = _relationship(
            denotes_id,
            "DENOTES",
            mention_id,
            decision.target_id,
            gate_score=decision.gate_score,
            method=decision.method.value,
        )
        derived_id = stable_id("neo4j-rel", mention_id, "DERIVED_FROM", source_id)
        relationships[derived_id] = _relationship(
            derived_id,
            "DERIVED_FROM",
            mention_id,
            source_id,
        )

    predicate_types = {
        "hasContemporaneousObservation": "HAS_CONTEMPORANEOUS_OBSERVATION",
        "hasOverlappingForecast": "HAS_OVERLAPPING_FORECAST",
    }
    for link in links:
        relationship_type = predicate_types.get(link.predicate)
        if relationship_type is None:
            raise ValueError(f"Unsupported cross-source predicate for Neo4j: {link.predicate}")
        start_id = f"urn:aviation-agentic-ai:source-record:{link.subject_id}"
        end_id = f"urn:aviation-agentic-ai:source-record:{link.object_id}"
        nodes.setdefault(
            start_id,
            _node(
                start_id,
                "SourceRecord",
                snapshot_set_id=snapshot_set_id,
                source_id=link.subject_id,
                source_family="atcscc_advisories",
            ),
        )
        nodes.setdefault(
            end_id,
            _node(
                end_id,
                "WeatherRecord",
                snapshot_set_id=snapshot_set_id,
                source_id=link.object_id,
                source_family=(
                    "aviationweather_metar"
                    if relationship_type == "HAS_CONTEMPORANEOUS_OBSERVATION"
                    else "aviationweather_taf"
                ),
            ),
        )
        relationships[link.link_id] = _relationship(
            link.link_id,
            relationship_type,
            start_id,
            end_id,
            link_method=link.link_method,
            facility_id=link.facility_id,
            advisory_start=link.advisory_interval.start.isoformat(),
            advisory_end=link.advisory_interval.end.isoformat(),
            evidence_start=link.evidence_interval.start.isoformat(),
            evidence_end=link.evidence_interval.end.isoformat(),
            authority_sources=link.authority_sources,
            evidence_text=link.evidence_text,
            causal_claim=False,
        )

    return (
        [nodes[key] for key in sorted(nodes)],
        [relationships[key] for key in sorted(relationships)],
    )


def write_neo4j_projection(
    *,
    nodes: Iterable[dict[str, Any]],
    relationships: Iterable[dict[str, Any]],
    nodes_path: str | Path,
    relationships_path: str | Path,
) -> Neo4jArtifacts:
    node_rows = list(nodes)
    relationship_rows = list(relationships)
    node_target = Path(nodes_path)
    relationship_target = Path(relationships_path)
    write_jsonl(node_target, node_rows)
    write_jsonl(relationship_target, relationship_rows)
    return Neo4jArtifacts(
        nodes_path=node_target,
        relationships_path=relationship_target,
        node_count=len(node_rows),
        relationship_count=len(relationship_rows),
    )


def load_neo4j_projection(
    *,
    uri: str,
    username: str,
    password: str,
    database: str,
    nodes_path: str | Path,
    relationships_path: str | Path,
    snapshot_set_id: str,
    replace_snapshot: bool = False,
    batch_size: int = 1000,
    driver_factory: DriverFactory | None = None,
) -> dict[str, int]:
    """Load a validated projection with parameterized, retryable driver queries."""
    driver_errors: tuple[type[Exception], ...] = ()
    if driver_factory is None:
        try:
            from neo4j import GraphDatabase
            from neo4j.exceptions import DriverError, Neo4jError
        except ImportError as exc:  # pragma: no cover - depends on optional install
            raise RuntimeError(
                "Neo4j support is not installed; run `uv sync --extra neo4j`."
            ) from exc
        driver_factory = GraphDatabase.driver
        driver_errors = (DriverError, Neo4jError)

    nodes = read_jsonl(nodes_path)
    relationships = read_jsonl(relationships_path)
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    unknown_labels = sorted({row["label"] for row in nodes} - {
        "Facility", "OperationalTerm", "AcceptedMention", "SourceRecord", "WeatherRecord"
    })
    unknown_types = sorted({row["type"] for row in relationships} - RELATIONSHIP_TYPES)
    if unknown_labels or unknown_types:
        raise ValueError(
            f"Projection contains unsupported labels/types: labels={unknown_labels}, "
            f"types={unknown_types}"
        )

    try:
        with driver_factory(uri, auth=(username, password)) as driver:
            driver.verify_connectivity()
            driver.execute_query(
                "CREATE CONSTRAINT cross_source_entity_id IF NOT EXISTS "
                "FOR (n:CrossSourceEntity) REQUIRE n.id IS UNIQUE",
                database_=database,
            )
            if replace_snapshot:
                driver.execute_query(
                    "MATCH (n:CrossSourceEntity {snapshot_set_id: $snapshot_set_id}) "
                    "DETACH DELETE n",
                    snapshot_set_id=snapshot_set_id,
                    database_=database,
                )
            for label in (
                "Facility",
                "OperationalTerm",
                "AcceptedMention",
                "SourceRecord",
                "WeatherRecord",
            ):
                rows = [row for row in nodes if row["label"] == label]
                for start in range(0, len(rows), batch_size):
                    driver.execute_query(
                        "UNWIND $rows AS row MERGE (n:CrossSourceEntity {id: row.id}) "
                        f"SET n += row.properties SET n:{label}",
                        rows=rows[start : start + batch_size],
                        database_=database,
                    )
            for relationship_type in sorted(RELATIONSHIP_TYPES):
                rows = [row for row in relationships if row["type"] == relationship_type]
                for start in range(0, len(rows), batch_size):
                    driver.execute_query(
                        "UNWIND $rows AS row "
                        "MATCH (a:CrossSourceEntity {id: row.start_id}) "
                        "MATCH (b:CrossSourceEntity {id: row.end_id}) "
                        f"MERGE (a)-[r:{relationship_type} {{id: row.id}}]->(b) "
                        "SET r += row.properties",
                        rows=rows[start : start + batch_size],
                        database_=database,
                    )
    except driver_errors as exc:  # pragma: no cover - requires a live Neo4j failure
        raise RuntimeError(f"Neo4j load failed: {exc}") from exc
    return {"nodes": len(nodes), "relationships": len(relationships)}
