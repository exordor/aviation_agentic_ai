from __future__ import annotations

from aviation_agentic_ai.ontology.atmonto_experiment import normalize_llm_facts


def _schema_slice() -> dict[str, object]:
    atm = "https://data.nasa.gov/ontologies/atmonto/ATM#"
    xsd = "http://www.w3.org/2001/XMLSchema#"
    return {
        "classes": [
            {
                "iri": f"{atm}ReRouteTMI",
                "prefixed_name": "atm:ReRouteTMI",
                "local_name": "ReRouteTMI",
            },
            {
                "iri": f"{atm}TFMcontrolElement",
                "prefixed_name": "atm:TFMcontrolElement",
                "local_name": "TFMcontrolElement",
            },
        ],
        "object_properties": [
            {
                "iri": f"{atm}controlledNASelement",
                "prefixed_name": "atm:controlledNASelement",
                "local_name": "controlledNASelement",
                "range_set": ["atm:TFMcontrolElement"],
            }
        ],
        "datatype_properties": [
            {
                "iri": f"{atm}advisoryNumber",
                "prefixed_name": "atm:advisoryNumber",
                "local_name": "advisoryNumber",
                "datatype_set": ["xsd:integer"],
            },
            {
                "iri": f"{atm}issuedTime",
                "prefixed_name": "atm:issuedTime",
                "local_name": "issuedTime",
                "datatype_set": ["xsd:dateTime"],
            },
        ],
        "class_hierarchy": [],
        "class_property_constraints": [],
        "prefixes": {"atm": atm, "xsd": xsd},
    }


def _task() -> dict[str, object]:
    return {
        "system_id": "S2_llm_schema_slice",
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-19:032",
        "source_family": "atcscc_advisories",
    }


def test_normalize_llm_fact_uses_schema_spec_for_datatype_property_object_payload() -> None:
    facts, skipped = normalize_llm_facts(
        payload={
            "facts": [
                {
                    "predicate": "atm:advisoryNumber",
                    "fact_type": "object_property",
                    "subject": {"type": "atm:ReRouteTMI", "value": "RRDCC032"},
                    "object": {"type": "xsd:integer", "value": "032"},
                    "evidence_text": "ATCSCC ADVZY 032",
                }
            ]
        },
        task=_task(),
        schema_slice=_schema_slice(),
    )

    assert skipped == 0
    assert len(facts) == 1
    fact = facts[0]
    assert fact["fact_type"] == "datatype_property"
    assert fact["subject"] == "RRDCC032"
    assert fact["subject_class"] == "atm:ReRouteTMI"
    assert fact["value"] == "032"
    assert fact["datatype"] == "xsd:integer"
    assert "object" not in fact
    assert "object_class" not in fact


def test_normalize_llm_fact_uses_schema_range_for_object_property_dict_payload() -> None:
    facts, skipped = normalize_llm_facts(
        payload={
            "facts": [
                {
                    "predicate": "atm:controlledNASelement",
                    "subject": {"type": "atm:ReRouteTMI", "value": "RRDCC032"},
                    "object": {"label": "ZNY", "value": "ZNY"},
                    "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                }
            ]
        },
        task=_task(),
        schema_slice=_schema_slice(),
    )

    assert skipped == 0
    assert len(facts) == 1
    fact = facts[0]
    assert fact["fact_type"] == "object_property"
    assert fact["subject"] == "RRDCC032"
    assert fact["subject_class"] == "atm:ReRouteTMI"
    assert fact["object"] == "ZNY"
    assert fact["object_class"] == "atm:TFMcontrolElement"
    assert fact["object_label"] == "ZNY"
