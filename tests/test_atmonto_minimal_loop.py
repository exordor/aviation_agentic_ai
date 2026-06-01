from __future__ import annotations

from pathlib import Path

from aviation_agentic_ai.ontology.atmonto_minimal_loop import (
    CatalogIndex,
    build_atcscc_schema_slice,
    build_extraction_json_schema,
    build_nasa_atmonto_schema_catalog,
    validate_candidate_fact,
)


SAMPLE_ATMONTO = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
     ontologyIRI="https://data.nasa.gov/ontologies/atmonto/ATM">
    <Prefix name="atm" IRI="https://data.nasa.gov/ontologies/atmonto/ATM#"/>
    <Prefix name="nas" IRI="https://data.nasa.gov/ontologies/atmonto/NAS#"/>
    <Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>
    <Prefix name="xsd" IRI="http://www.w3.org/2001/XMLSchema#"/>
    <Declaration><Class IRI="#TrafficManagementInitiative"/></Declaration>
    <Declaration><Class IRI="#GroundStopTMI"/></Declaration>
    <Declaration><Class IRI="#TFMcontrolElement"/></Declaration>
    <Declaration><Class abbreviatedIRI="nas:Airport"/></Declaration>
    <Declaration><ObjectProperty IRI="#controlledNASelement"/></Declaration>
    <Declaration><DataProperty IRI="#advisoryNumber"/></Declaration>
    <Declaration><DataProperty IRI="#extensionProbability"/></Declaration>
    <SubClassOf>
        <Class IRI="#GroundStopTMI"/>
        <Class IRI="#TrafficManagementInitiative"/>
    </SubClassOf>
    <SubClassOf>
        <Class abbreviatedIRI="nas:Airport"/>
        <Class IRI="#TFMcontrolElement"/>
    </SubClassOf>
    <SubClassOf>
        <Class IRI="#GroundStopTMI"/>
        <ObjectAllValuesFrom>
            <ObjectProperty IRI="#controlledNASelement"/>
            <Class abbreviatedIRI="nas:Airport"/>
        </ObjectAllValuesFrom>
    </SubClassOf>
    <SubClassOf>
        <Class IRI="#GroundStopTMI"/>
        <DataAllValuesFrom>
            <DataProperty IRI="#extensionProbability"/>
            <DataOneOf>
                <Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral">HIGH</Literal>
                <Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral">MEDIUM</Literal>
            </DataOneOf>
        </DataAllValuesFrom>
    </SubClassOf>
    <ObjectPropertyDomain>
        <ObjectProperty IRI="#controlledNASelement"/>
        <Class IRI="#TrafficManagementInitiative"/>
    </ObjectPropertyDomain>
    <ObjectPropertyRange>
        <ObjectProperty IRI="#controlledNASelement"/>
        <Class IRI="#TFMcontrolElement"/>
    </ObjectPropertyRange>
    <DataPropertyDomain>
        <DataProperty IRI="#advisoryNumber"/>
        <Class IRI="#TrafficManagementInitiative"/>
    </DataPropertyDomain>
    <DataPropertyRange>
        <DataProperty IRI="#advisoryNumber"/>
        <Datatype abbreviatedIRI="xsd:integer"/>
    </DataPropertyRange>
    <DataPropertyDomain>
        <DataProperty IRI="#extensionProbability"/>
        <Class IRI="#TrafficManagementInitiative"/>
    </DataPropertyDomain>
    <DataPropertyRange>
        <DataProperty IRI="#extensionProbability"/>
        <Datatype abbreviatedIRI="xsd:string"/>
    </DataPropertyRange>
    <AnnotationAssertion>
        <AnnotationProperty abbreviatedIRI="rdfs:label"/>
        <IRI>#GroundStopTMI</IRI>
        <Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral">Ground stop TMI</Literal>
    </AnnotationAssertion>
</Ontology>
"""


def build_sample_slice(tmp_path: Path) -> dict[str, object]:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir()
    (ontology_dir / "ATM.owl").write_text(SAMPLE_ATMONTO, encoding="utf-8")
    catalog = build_nasa_atmonto_schema_catalog(ontology_dir, repo_root=tmp_path)
    return build_atcscc_schema_slice(catalog)


def test_owl_xml_catalog_preserves_declarations_domains_ranges_and_constraints(
    tmp_path: Path,
) -> None:
    schema_slice = build_sample_slice(tmp_path)

    assert schema_slice["counts"]["classes"] >= 4
    assert schema_slice["counts"]["object_properties"] == 1
    assert schema_slice["counts"]["datatype_properties"] == 2
    assert schema_slice["counts"]["class_property_constraints"] == 2

    extraction_schema = build_extraction_json_schema(schema_slice)
    fact_schema = extraction_schema["properties"]["facts"]["items"]["properties"]
    assert "GroundStopTMI" in fact_schema["subject_class"]["enum"]
    assert "controlledNASelement" in fact_schema["predicate"]["anyOf"][0]["enum"]


def test_validator_repairs_local_identifiers_and_accepts_schema_valid_fact(
    tmp_path: Path,
) -> None:
    schema_slice = build_sample_slice(tmp_path)
    index = CatalogIndex(schema_slice)
    source_text = "ATCSCC ADVZY 002 DCA/ZDC 05/14/2026 CDM GROUND STOP"

    result = validate_candidate_fact(
        {
            "fact_id": "fact-1",
            "source_id": "2026-05-14:002",
            "fact_type": "datatype_property",
            "subject": "urn:test",
            "subject_class": "GroundStopTMI",
            "predicate": "advisoryNumber",
            "value": "2",
            "datatype": "xsd:integer",
            "evidence_text": "ATCSCC ADVZY 002 DCA/ZDC 05/14/2026 CDM GROUND STOP",
        },
        source_text=source_text,
        index=index,
    )

    assert result["status"] == "repaired_accepted"
    assert result["accepted"] is True
    assert result["validated_fact"]["value"] == 2


def test_validator_rejects_schema_and_evidence_errors(tmp_path: Path) -> None:
    schema_slice = build_sample_slice(tmp_path)
    index = CatalogIndex(schema_slice)

    result = validate_candidate_fact(
        {
            "fact_id": "fact-2",
            "source_id": "2026-05-14:002",
            "fact_type": "object_property",
            "subject": "urn:test",
            "subject_class": "GroundStopTMI",
            "predicate": "controlledNASelement",
            "object": "urn:nas:ZDC",
            "object_class": "TrafficManagementInitiative",
            "evidence_text": "not in source",
        },
        source_text="CTL ELEMENT: DCA",
        index=index,
    )

    assert result["accepted"] is False
    assert result["status"] == "rejected_evidence"
    assert "range_violation" in result["errors"]
    assert "evidence_not_found_in_source" in result["errors"]
