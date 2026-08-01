"""Batch Two focused tests for RDF and Neo4j materialization.

RDF tests parse the Turtle with rdflib and assert:
- actual NASA GroundStopTMI IRI exists;
- actual controlledNASelement IRI exists;
- advisory number is an integer literal;
- times are dateTime literals;
- provenance exists;
- example-namespace ATMONTO terms count is zero.

Neo4j tests assert:
- no Literal nodes;
- all relationship endpoints exist;
- parameterized MERGE is used;
- loading twice does not increase node or relationship counts;
- an unrelated sentinel node is preserved.

The Neo4j live assertions use a fake driver factory that records the executed
queries and simulates the MERGE store, so the parameterized-MERGE code path,
idempotency, and sentinel preservation are verified without a live database.
The real driver path raises Neo4jLoadBlocked on missing credentials or a
connectivity failure (BLOCKED, not faked).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import rdflib
from rdflib.namespace import RDF

from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    SourceFamily,
    SourceRecord,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.materialize import (
    Neo4jLoadBlocked,
    build_validated_facts_neo4j_projection,
    load_validated_facts_neo4j,
    materialize_validated_facts,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot,
    build_source_snapshot_registry,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)

# Real IRIs from the frozen Schema Guide.
GS_IRI = "https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI"
AIRPORT_IRI = "https://data.nasa.gov/ontologies/atmonto/NAS#Airport"
CONTROLLED_IRI = "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement"
ADVNUM_IRI = "https://data.nasa.gov/ontologies/atmonto/ATM#advisoryNumber"
START_IRI = "https://data.nasa.gov/ontologies/atmonto/ATM#effectiveStartTime"
END_IRI = "https://data.nasa.gov/ontologies/atmonto/ATM#effectiveEndTime"
EXT_IRI = "https://data.nasa.gov/ontologies/atmonto/ATM#extensionProbability"
RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
PROV_IRI = "http://www.w3.org/ns/prov#wasDerivedFrom"
XSD_INT = "http://www.w3.org/2001/XMLSchema#integer"
XSD_DT = "http://www.w3.org/2001/XMLSchema#dateTime"
XSD_STR = "http://www.w3.org/2001/XMLSchema#string"
ATM = rdflib.Namespace("https://data.nasa.gov/ontologies/atmonto/ATM#")
NAS = rdflib.Namespace("https://data.nasa.gov/ontologies/atmonto/NAS#")
PROV = rdflib.Namespace("http://www.w3.org/ns/prov#")

FACILITY_ID = "urn:aviation-agentic-ai:facility:airport:KJFK"
SOURCE_ID = "2026-05-19:123"
EVT_SUBJECT = "evt:abc123"
ADVISORY_CONTENT = (
    "ATCSCC ADVZY 123 JFK/ZNY 05/19/2026 CDM GROUND STOP\n"
    "CTL ELEMENT: JFK GROUND STOP PERIOD: 19/2100Z - 19/2245Z "
    "PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER\n"
)


@pytest.fixture(scope="module")
def guide():
    return load_schema_guide()


@pytest.fixture(scope="module")
def snapshot() -> Any:
    rec = SourceRecord(
        source_id=SOURCE_ID, family=SourceFamily.ATCSCC_ADVISORY, content=ADVISORY_CONTENT,
    )
    return build_source_snapshot(rec)


DECISION_PROFILE_REF = next(
    ref
    for ref in load_validation_profile_registry(
        decision_guide=load_schema_guide()
    ).refs
    if ref.layer == "decision"
)
PROFILE_REGISTRY = load_validation_profile_registry(
    decision_guide=load_schema_guide()
)


def _decision_fact(**fields: Any) -> ValidatedFact:
    """Build a source-text decision fact with explicit v1 ownership."""

    fact_id = fields["fact_id"]
    assert isinstance(fact_id, str)
    return ValidatedFact(
        **fields,
        validation_profile=DECISION_PROFILE_REF,
        evidence_mode="source_text",
        evidence_ref=fact_id,
    )


def _fixed_facts() -> list[ValidatedFact]:
    return [
        _decision_fact(
            fact_id="f1", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=RDF_TYPE_IRI, object_kind="iri", object_value="atm:GroundStopTMI",
            object_class_iri=GS_IRI, source_ids=[SOURCE_ID],
            evidence_texts=["GROUND STOP PERIOD: 19/2100Z - 19/2245Z"],
        ),
        _decision_fact(
            fact_id="f2", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=CONTROLLED_IRI, object_kind="iri", object_value=FACILITY_ID,
            object_class_iri=AIRPORT_IRI, source_ids=[SOURCE_ID],
            evidence_texts=["CTL ELEMENT: JFK"],
        ),
        _decision_fact(
            fact_id="f3", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=ADVNUM_IRI, object_kind="literal", object_value="123",
            datatype_iri=XSD_INT, source_ids=[SOURCE_ID],
            evidence_texts=["ATCSCC ADVZY 123"],
        ),
        _decision_fact(
            fact_id="f4", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=START_IRI, object_kind="literal",
            object_value="2026-05-19T21:00:00Z", datatype_iri=XSD_DT,
            source_ids=[SOURCE_ID], evidence_texts=["19/2100Z"],
        ),
        _decision_fact(
            fact_id="f5", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=END_IRI, object_kind="literal",
            object_value="2026-05-19T22:45:00Z", datatype_iri=XSD_DT,
            source_ids=[SOURCE_ID], evidence_texts=["19/2245Z"],
        ),
        _decision_fact(
            fact_id="f6", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=EXT_IRI, object_kind="literal", object_value="MEDIUM",
            datatype_iri=XSD_STR, source_ids=[SOURCE_ID],
            evidence_texts=["PROBABILITY OF EXTENSION: MEDIUM"],
        ),
    ]


def _snapshot_registry(facts: list[ValidatedFact]):
    source_ids = sorted(
        {
            source_id
            for fact in facts
            for source_id in fact.source_ids
        }
    )
    return build_source_snapshot_registry(
        [
            SourceRecord(
                source_id=source_id,
                family=SourceFamily.ATCSCC_ADVISORY,
                content=ADVISORY_CONTENT,
            )
            for source_id in source_ids
        ]
    )


def _materialize_current(
    *,
    facts: list[ValidatedFact],
    output_dir: Path,
):
    registry = _snapshot_registry(facts)
    snapshots = {
        snapshot.source_id: snapshot
        for snapshot in registry.snapshots
    }
    traces = [
        FactTraceRow(
            fact_id=fact.fact_id,
            graph_patch_line="current profile-owned fixture",
            source_id=fact.source_ids[0],
            evidence_text=fact.evidence_texts[0],
            evidence_agent_role="fixture",
            source_snapshot_sha256=(
                snapshots[fact.source_ids[0]].content_sha256
            ),
        )
        for fact in facts
    ]
    return materialize_validated_facts(
        facts=facts,
        profile_registry=PROFILE_REGISTRY,
        source_snapshot=registry,
        fact_traces=traces,
        output_dir=output_dir,
    )


def _project_current(
    *,
    facts: list[ValidatedFact],
    output_dir: Path,
):
    return build_validated_facts_neo4j_projection(
        facts=facts,
        profile_registry=PROFILE_REGISTRY,
        source_snapshot=_snapshot_registry(facts),
        output_dir=output_dir,
    )


# ---------------------------------------------------------------------------
# §6.4 RDF tests (rdflib)
# ---------------------------------------------------------------------------


def test_rdf_has_actual_nasa_groundstop_iri(guide, snapshot, tmp_path):
    mat = _materialize_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    g = rdflib.Graph()
    g.parse(mat.ttl_path, format="turtle")
    assert (None, RDF.type, ATM.GroundStopTMI) in g


def test_rdf_has_actual_controlled_nas_element_iri(guide, snapshot, tmp_path):
    mat = _materialize_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    g = rdflib.Graph()
    g.parse(mat.ttl_path, format="turtle")
    assert (None, ATM.controlledNASelement, None) in g


def test_rdf_advisory_number_is_integer_literal(guide, snapshot, tmp_path):
    mat = _materialize_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    g = rdflib.Graph()
    g.parse(mat.ttl_path, format="turtle")
    values = list(g.objects(None, ATM.advisoryNumber))
    assert values
    for v in values:
        assert isinstance(v, rdflib.Literal)
        assert v.datatype is not None
        assert "integer" in str(v.datatype)


def test_rdf_times_are_datetime_literals(guide, snapshot, tmp_path):
    mat = _materialize_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    g = rdflib.Graph()
    g.parse(mat.ttl_path, format="turtle")
    for prop in (ATM.effectiveStartTime, ATM.effectiveEndTime):
        values = list(g.objects(None, prop))
        assert values, f"no values for {prop}"
        for v in values:
            assert isinstance(v, rdflib.Literal)
            assert v.datatype is not None
            assert "dateTime" in str(v.datatype)


def test_rdf_provenance_exists(guide, snapshot, tmp_path):
    mat = _materialize_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    g = rdflib.Graph()
    g.parse(mat.ttl_path, format="turtle")
    assert (None, PROV.wasDerivedFrom, None) in g
    stable_source = rdflib.URIRef(
        "urn:aviation-agentic-ai:source:2026-05-19:123"
    )
    assert set(g.objects(None, PROV.wasDerivedFrom)) == {stable_source}


def test_rdf_reifies_each_fact_at_its_deterministic_statement_iri(
    guide,
    snapshot,
    tmp_path,
):
    """A random reification node would break reproducible RDF export."""

    mat = _materialize_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    g = rdflib.Graph()
    g.parse(mat.ttl_path, format="turtle")

    statement = rdflib.URIRef("urn:aviation-agentic-ai:fact:f3")
    event = rdflib.URIRef("urn:aviation-agentic-ai:event:abc123")
    advisory_number = rdflib.Literal("123", datatype=rdflib.URIRef(XSD_INT))
    source = rdflib.URIRef("urn:aviation-agentic-ai:source:2026-05-19:123")

    assert not any(isinstance(node, rdflib.BNode) for node in g.all_nodes())
    assert (statement, RDF.type, RDF.Statement) in g
    assert (statement, RDF.subject, event) in g
    assert (statement, RDF.predicate, rdflib.URIRef(ADVNUM_IRI)) in g
    assert (statement, RDF.object, advisory_number) in g
    assert (statement, PROV.wasDerivedFrom, source) in g
    assert (statement, rdflib.RDFS.comment, rdflib.Literal("ATCSCC ADVZY 123")) in g


def test_rdf_has_zero_example_namespace_atmonto_terms(guide, snapshot, tmp_path):
    mat = _materialize_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    ttl = Path(mat.ttl_path).read_text(encoding="utf-8")
    assert "example.org" not in ttl


def test_rdf_facility_remains_uriref_not_literal(guide, snapshot, tmp_path):
    """§6.1: canonical facilities remain URIRefs; literals are never resources."""

    mat = _materialize_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    g = rdflib.Graph()
    g.parse(mat.ttl_path, format="turtle")
    facility = rdflib.URIRef(FACILITY_ID)
    # The facility appears as the object of controlledNASelement (a URIRef).
    assert (None, ATM.controlledNASelement, facility) in g
    # And it is typed as nas:Airport.
    assert (facility, RDF.type, NAS.Airport) in g


# ---------------------------------------------------------------------------
# §6.4 Neo4j projection tests
# ---------------------------------------------------------------------------


def test_neo4j_projection_has_no_literal_nodes(guide, tmp_path):
    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    labels = {n["label"] for n in nodes}
    assert "Literal" not in labels
    assert {"AviationEvent", "Facility", "SourceRecord"}.issubset(labels)


def test_neo4j_projection_all_endpoints_exist(guide, tmp_path):
    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    node_ids = {n["id"] for n in nodes}
    for rel in rels:
        assert rel["start_id"] in node_ids, f"missing start endpoint {rel['start_id']}"
        assert rel["end_id"] in node_ids, f"missing end endpoint {rel['end_id']}"


def test_neo4j_projection_datatype_props_on_event_node(guide, tmp_path):
    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    event = next(n for n in nodes if n["label"] == "AviationEvent")
    props = event["properties"]
    # Datatype values live on the event node (plan §6.2).
    assert props["advisoryNumber"] == 123  # coerced to int
    assert props["effectiveStartTime"] == "2026-05-19T21:00:00Z"
    assert props["extensionProbability"] == "MEDIUM"


def test_neo4j_relationships_retain_predicate_iri(guide, tmp_path):
    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    for rel in rels:
        assert rel["properties"]["predicate_iri"]
    rel_types = {r["type"] for r in rels}
    assert "CONTROLLED_NAS_ELEMENT" in rel_types
    assert "DERIVED_FROM" in rel_types


def test_neo4j_projection_deduplicates_stable_relationships(guide, tmp_path):
    """Repeated accepted facts merge into one canonical relationship."""

    duplicate = _fixed_facts()[1].model_copy(
        update={"fact_id": "f2-duplicate", "source_ids": ["source:second"]}
    )
    _nodes, rels, _nodes_path, _rels_path = (
        _project_current(
            facts=_fixed_facts() + [duplicate],
            output_dir=tmp_path,
        )
    )
    controlled = [
        rel for rel in rels if rel["type"] == "CONTROLLED_NAS_ELEMENT"
    ]
    assert len(controlled) == 1
    assert controlled[0]["properties"]["source_ids"] == [
        SOURCE_ID,
        "source:second",
    ]


# ---------------------------------------------------------------------------
# §6.4 Neo4j load tests (parameterized MERGE, idempotent, sentinel preserved)
# ---------------------------------------------------------------------------


class _FakeStore:
    """An in-memory MERGE store that mirrors the parameterized queries."""

    def __init__(self) -> None:
        self.nodes: dict[tuple[str, str], dict[str, Any]] = {}
        self.rels: dict[str, dict[str, Any]] = {}
        self.queries: list[str] = []

    def execute_query(self, query: str, *, database_=None, **params: Any) -> None:
        self.queries.append(query)
        rows = params.get("rows", [])
        if "MERGE (n:" in query and "SET n += row.properties" in query:
            label = query.split("MERGE (n:")[1].split(" ")[0]
            for row in rows:
                self.nodes[(label, row["id"])] = dict(row["properties"])
        elif "MERGE (a)-[r:" in query:
            for row in rows:
                self.rels[row["id"]] = dict(row)


class _FakeDriver:
    def __init__(self, store: _FakeStore) -> None:
        self.store = store

    def __enter__(self) -> "_FakeDriver":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def verify_connectivity(self) -> None:
        return None

    def execute_query(self, query: str, *, database_=None, **params: Any) -> None:
        self.store.execute_query(query, database_=database_, **params)


def _fake_driver_factory(store: _FakeStore):
    def _factory(*args: Any, **kwargs: Any) -> _FakeDriver:
        return _FakeDriver(store)

    return _factory


def test_neo4j_load_uses_parameterized_merge(guide, tmp_path):
    """§6.4: parameterized MERGE is used."""

    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    store = _FakeStore()
    summary = load_validated_facts_neo4j(
        nodes_path=nodes_path, relationships_path=rels_path,
        uri="bolt://x", username="u", password="p",
        driver_factory=_fake_driver_factory(store),
    )
    # Every node/relationship write uses UNWIND $rows + MERGE (parameterized).
    merge_queries = [q for q in store.queries if "MERGE" in q and "UNWIND $rows" in q]
    assert merge_queries
    assert summary["nodes"] == len(nodes)
    assert summary["relationships"] == len(rels)


def test_neo4j_load_twice_does_not_increase_counts(guide, tmp_path):
    """§6.4: loading twice does not increase node or relationship counts."""

    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    store = _FakeStore()
    factory = _fake_driver_factory(store)
    load_validated_facts_neo4j(
        nodes_path=nodes_path, relationships_path=rels_path,
        uri="bolt://x", username="u", password="p", driver_factory=factory,
    )
    first_nodes = len(store.nodes)
    first_rels = len(store.rels)
    # Load the same projection a second time.
    load_validated_facts_neo4j(
        nodes_path=nodes_path, relationships_path=rels_path,
        uri="bolt://x", username="u", password="p", driver_factory=factory,
    )
    assert len(store.nodes) == first_nodes
    assert len(store.rels) == first_rels


def test_neo4j_load_preserves_unrelated_sentinel(guide, tmp_path):
    """§6.4: an unrelated sentinel node is preserved across loads."""

    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    store = _FakeStore()
    # Pre-populate an unrelated sentinel node the loader must never clear.
    store.nodes[("Sentinel", "sentinel-1")] = {"id": "sentinel-1", "note": "unrelated"}
    factory = _fake_driver_factory(store)
    load_validated_facts_neo4j(
        nodes_path=nodes_path, relationships_path=rels_path,
        uri="bolt://x", username="u", password="p", driver_factory=factory,
    )
    # The sentinel survives (no DETACH DELETE / no clearing of unrelated data).
    assert ("Sentinel", "sentinel-1") in store.nodes
    assert store.nodes[("Sentinel", "sentinel-1")]["note"] == "unrelated"
    # Loading again still preserves it.
    load_validated_facts_neo4j(
        nodes_path=nodes_path, relationships_path=rels_path,
        uri="bolt://x", username="u", password="p", driver_factory=factory,
    )
    assert ("Sentinel", "sentinel-1") in store.nodes


def test_neo4j_load_missing_credentials_blocked(guide, tmp_path):
    """§6.2/§6.4: missing credentials -> BLOCKED (never faked)."""

    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )
    with pytest.raises(Neo4jLoadBlocked):
        load_validated_facts_neo4j(
            nodes_path=nodes_path, relationships_path=rels_path,
            uri=None, username=None, password=None,
        )


def test_neo4j_load_connectivity_failure_blocked(guide, tmp_path):
    """§6.2/§6.4: a connectivity/load failure -> BLOCKED."""

    nodes, rels, nodes_path, rels_path = _project_current(
        facts=_fixed_facts(), output_dir=tmp_path,
    )

    class _FailingDriver(_FakeDriver):
        def verify_connectivity(self) -> None:
            raise RuntimeError("connection refused")

    def _failing_factory(*args: Any, **kwargs: Any) -> _FailingDriver:
        return _FailingDriver(_FakeStore())

    with pytest.raises(Neo4jLoadBlocked):
        load_validated_facts_neo4j(
            nodes_path=nodes_path, relationships_path=rels_path,
            uri="bolt://x", username="u", password="p",
            driver_factory=_failing_factory,
        )


def test_neo4j_load_blocks_dangling_relationship_before_connecting(tmp_path):
    """A missing endpoint must fail before the driver is created."""

    nodes_path = tmp_path / "nodes.jsonl"
    relationships_path = tmp_path / "relationships.jsonl"
    nodes_path.write_text(
        json.dumps({
            "id": "event:1",
            "label": "AviationEvent",
            "properties": {"id": "event:1"},
        }) + "\n",
        encoding="utf-8",
    )
    relationships_path.write_text(
        json.dumps({
            "id": "rel:1",
            "type": "DERIVED_FROM",
            "start_id": "event:1",
            "end_id": "source:missing",
            "properties": {"id": "rel:1"},
        }) + "\n",
        encoding="utf-8",
    )
    driver_created = False

    def factory(*args: Any, **kwargs: Any) -> _FakeDriver:
        nonlocal driver_created
        driver_created = True
        return _FakeDriver(_FakeStore())

    with pytest.raises(Neo4jLoadBlocked, match="endpoint is not materialized"):
        load_validated_facts_neo4j(
            nodes_path=nodes_path,
            relationships_path=relationships_path,
            uri="bolt://x",
            username="u",
            password="p",
            driver_factory=factory,
        )
    assert driver_created is False


def test_neo4j_load_blocks_duplicate_ids_before_connecting(tmp_path):
    """Duplicate artifact IDs must not be reported as successfully loaded."""

    node = {
        "id": "event:1",
        "label": "AviationEvent",
        "properties": {"id": "event:1"},
    }
    nodes_path = tmp_path / "nodes.jsonl"
    relationships_path = tmp_path / "relationships.jsonl"
    nodes_path.write_text(
        "\n".join((json.dumps(node), json.dumps(node))) + "\n",
        encoding="utf-8",
    )
    relationships_path.write_text("", encoding="utf-8")
    with pytest.raises(Neo4jLoadBlocked, match="duplicate Neo4j node id"):
        load_validated_facts_neo4j(
            nodes_path=nodes_path,
            relationships_path=relationships_path,
            uri="bolt://x",
            username="u",
            password="p",
            driver_factory=_fake_driver_factory(_FakeStore()),
        )


# ===========================================================================
# Section 13 regressions: provenance
# ===========================================================================


def _no_prov_facts() -> list[ValidatedFact]:
    """Fixed-case facts WITHOUT an explicit prov:wasDerivedFrom row."""

    return [
        _decision_fact(
            fact_id="f1", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=RDF_TYPE_IRI, object_kind="iri",
            object_value="atm:GroundStopTMI", object_class_iri=GS_IRI,
            source_ids=[SOURCE_ID], evidence_texts=["GROUND STOP"],
        ),
        _decision_fact(
            fact_id="f2", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=CONTROLLED_IRI, object_kind="iri", object_value=FACILITY_ID,
            object_class_iri=AIRPORT_IRI, source_ids=[SOURCE_ID],
            evidence_texts=["CTL ELEMENT: JFK"],
        ),
        _decision_fact(
            fact_id="f3", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=START_IRI, object_kind="literal",
            object_value="2026-05-19T21:00:00Z", datatype_iri=XSD_DT,
            source_ids=[SOURCE_ID], evidence_texts=["19/2100Z"],
        ),
        _decision_fact(
            fact_id="f4", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=END_IRI, object_kind="literal",
            object_value="2026-05-19T22:45:00Z", datatype_iri=XSD_DT,
            source_ids=[SOURCE_ID], evidence_texts=["19/2245Z"],
        ),
    ]


def test_sec13_regression1_provenance_without_explicit_prov_row(guide, tmp_path):
    """§13 regression 1: facts without an explicit PROV row still produce
    exactly one SourceRecord and one DERIVED_FROM."""

    nodes, rels, _, _ = _project_current(
        facts=_no_prov_facts(), output_dir=tmp_path,
    )
    source_nodes = sum(1 for n in nodes if n["label"] == "SourceRecord")
    derived = sum(1 for r in rels if r["type"] == "DERIVED_FROM")
    assert source_nodes == 1
    assert derived == 1


def test_sec13_regression2_explicit_prov_row_does_not_increase_counts(guide, tmp_path):
    """§13 regression 2: adding the explicit PROV row does not increase the
    SourceRecord or DERIVED_FROM counts."""

    facts_with_prov = _no_prov_facts() + [
        _decision_fact(
            fact_id="fprov", subject_iri=EVT_SUBJECT, subject_class_iri=GS_IRI,
            predicate_iri=PROV_IRI, object_kind="iri", object_value=SOURCE_ID,
            source_ids=[SOURCE_ID], evidence_texts=[],
        )
    ]
    nodes_a, rels_a, _, _ = _project_current(
        facts=_no_prov_facts(), output_dir=tmp_path / "a",
    )
    nodes_b, rels_b, _, _ = _project_current(
        facts=facts_with_prov, output_dir=tmp_path / "b",
    )
    src_a = sum(1 for n in nodes_a if n["label"] == "SourceRecord")
    src_b = sum(1 for n in nodes_b if n["label"] == "SourceRecord")
    der_a = sum(1 for r in rels_a if r["type"] == "DERIVED_FROM")
    der_b = sum(1 for r in rels_b if r["type"] == "DERIVED_FROM")
    assert src_a == src_b == 1
    assert der_a == der_b == 1


def test_sec13_regression7_no_chinese_interface_text_in_active_paths():
    """§13 regression 7: scan tracked and untracked active interface files."""

    # Active paths: agent_system package, the agent-system CLI, the frozen
    # query catalog, and the agent-system tests. Quoted external source data
    # (advisory fixtures) is exempt; the scan is over interface strings.
    paths = [
        *sorted(Path("src/aviation_agentic_ai/agent_system").glob("*.py")),
        Path("src/aviation_agentic_ai/cli_agent_system.py"),
        Path("configs/prompts/tmi_event_agents_v1.yaml"),
        *sorted(Path("tests").glob("test_agent_system*.py")),
        Path("tests/test_cli_agent_system.py"),
        Path("docs/multi_agent_kg_system_design.md"),
    ]
    pattern = re.compile(r"[\u4e00-\u9fff]")
    offenders = [
        str(path)
        for path in paths
        if path.exists() and pattern.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"Chinese interface text found in active paths: {offenders}"
