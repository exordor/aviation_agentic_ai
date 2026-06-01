from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.ontology.airm_o import (
    AIRM_O_ALIGNMENT_JSONL,
    collect_airm_o_pipeline,
    parse_airm_o_ontology,
    parse_atmonto_airm_alignment,
)


SAMPLE_AIRM_OWL = """<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#">
  <owl:Ontology rdf:about="https://w3id.org/airm-o/ontology">
    <owl:versionIRI rdf:resource="https://w3id.org/airm-o/ontology/1.0"/>
    <rdfs:comment>AIRM-O sample.</rdfs:comment>
  </owl:Ontology>
  <owl:Class rdf:about="https://w3id.org/airm-o/ontology#Aircraft">
    <rdfs:comment>An aircraft.</rdfs:comment>
  </owl:Class>
  <owl:Class rdf:about="https://w3id.org/airm-o/ontology#Airspace"/>
  <owl:ObjectProperty rdf:about="https://w3id.org/airm-o/ontology#AirTrafficControlService-clientAirspace">
    <rdfs:domain rdf:resource="https://w3id.org/airm-o/ontology#AirTrafficControlService"/>
    <rdfs:range rdf:resource="https://w3id.org/airm-o/ontology#Airspace"/>
    <rdfs:comment>The airspace for which ATC service is provided.</rdfs:comment>
  </owl:ObjectProperty>
  <owl:DatatypeProperty rdf:about="https://w3id.org/airm-o/ontology#Airspace-designator">
    <rdfs:domain rdf:resource="https://w3id.org/airm-o/ontology#Airspace"/>
    <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
  </owl:DatatypeProperty>
  <owl:NamedIndividual rdf:about="https://w3id.org/airm-o/ontology#IFR"/>
</rdf:RDF>
"""


SAMPLE_ALIGNMENT_RDF = """<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:align="http://knowledgeweb.semanticweb.org/heterogeneity/alignment#">
  <align:Alignment>
    <align:map>
      <align:Cell>
        <align:entity1 rdf:resource="https://data.nasa.gov/ontologies/atmonto/NAS#PhysicalRunway"/>
        <align:entity2 rdf:resource="https://w3id.org/airm-o/ontology#Runway"/>
        <align:relation>=</align:relation>
        <align:measure rdf:datatype="http://www.w3.org/2001/XMLSchema#float">1.0</align:measure>
      </align:Cell>
    </align:map>
    <align:map>
      <align:Cell>
        <align:entity1 rdf:resource="https://data.nasa.gov/ontologies/atmonto/equipment#BallBearing"/>
        <align:entity2 rdf:resource="https://w3id.org/airm-o/ontology#AirframeEquipment"/>
        <align:relation>&lt;</align:relation>
        <align:measure rdf:datatype="http://www.w3.org/2001/XMLSchema#float">0.95</align:measure>
      </align:Cell>
    </align:map>
  </align:Alignment>
</rdf:RDF>
"""


def test_parse_airm_o_ontology_counts_schema_and_keeps_domain_range() -> None:
    inventory = parse_airm_o_ontology(SAMPLE_AIRM_OWL.encode("utf-8"))

    assert inventory["ontology_iri"] == "https://w3id.org/airm-o/ontology"
    assert inventory["version_iri"] == "https://w3id.org/airm-o/ontology/1.0"
    assert inventory["counts"]["classes"] == 2
    assert inventory["counts"]["object_properties"] == 1
    assert inventory["counts"]["datatype_properties"] == 1
    assert inventory["counts"]["named_individuals"] == 1
    assert inventory["counts"]["domain_axioms"] == 2
    assert inventory["counts"]["range_axioms"] == 2
    assert inventory["terms"]["classes"]["Aircraft"]["comment"] == "An aircraft."
    assert inventory["terms"]["object_properties"][
        "AirTrafficControlService-clientAirspace"
    ]["range"] == ["Airspace"]


def test_parse_atmonto_airm_alignment_preserves_relation_direction() -> None:
    cells = parse_atmonto_airm_alignment(
        SAMPLE_ALIGNMENT_RDF.encode("utf-8"),
        source_id="sample_alignment",
        source_file="sample.rdf",
    )

    assert cells[0]["relation_kind"] == "equivalent"
    assert cells[0]["atmonto_term"] == "PhysicalRunway"
    assert cells[0]["airm_term"] == "Runway"

    assert cells[1]["relation_symbol"] == "<"
    assert cells[1]["relation_kind"] == "atmonto_subclass_of_airm"
    assert cells[1]["confidence"] == 0.95
    assert cells[1]["source_file"] == "sample.rdf"


def test_collect_airm_o_pipeline_writes_manifest_alignment_jsonl_and_reports(
    tmp_path: Path,
) -> None:
    def fake_fetch(url: str, _timeout: int) -> bytes:
        if url.endswith("airm-o.owl"):
            return SAMPLE_AIRM_OWL.encode("utf-8")
        if url.endswith("ontology.ttl"):
            return b"@prefix airm: <https://w3id.org/airm-o/ontology#> .\n"
        if "EQUIVALENCE" in url or "SUBSUMPTION" in url:
            return SAMPLE_ALIGNMENT_RDF.encode("utf-8")
        if url.endswith("README.md"):
            return b"# AIRM-O\n"
        raise AssertionError(url)

    result = collect_airm_o_pipeline(
        tmp_path,
        snapshot_date="2026-06-01",
        fetch_bytes=fake_fetch,
    )

    manifest = json.loads((tmp_path / "data/ontology/external/airm_o/manifest.json").read_text())
    assert manifest["source_family"] == "airm_o_external_ontology"
    assert manifest["role"] == "external_reference_ontology"
    assert manifest["boundary"] == "external_reference_not_experiment_ground_truth"
    assert manifest["ontology_inventory"]["counts"]["classes"] == 2

    mapping_path = tmp_path / AIRM_O_ALIGNMENT_JSONL
    mappings = [json.loads(line) for line in mapping_path.read_text().splitlines()]
    assert len(mappings) == 4
    assert {item["relation_kind"] for item in mappings} == {
        "equivalent",
        "atmonto_subclass_of_airm",
    }

    report = json.loads((tmp_path / "reports/stages/airm_o_ontology_alignment.json").read_text())
    assert report["mapping_record_count"] == 4
    assert result["alignment_jsonl"] == AIRM_O_ALIGNMENT_JSONL.as_posix()
    assert (tmp_path / "reports/stages/airm_o_ontology_alignment.md").exists()
