from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from rdflib import Graph

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.ontology.cq import (
    CQValidationError,
    load_cq_artifact,
    normalize_cq_artifact,
    normalize_odp_hint,
)
from aviation_agentic_ai.ontology.evaluation import (
    analyze_cq_coverage,
    build_quality_gates,
    collect_semantic_smells,
    collect_structural_metrics,
    evaluate_ontology,
    load_cqs,
    parse_ai_review_response,
    stratified_sample_cqs,
)


TTL = """@prefix : <http://www.example.org/aviation/phak#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:Cl_Thing a owl:Class ;
    rdfs:label "Thing" .
:Cl_ChildThing a owl:Class ;
    rdfs:subClassOf :Cl_Thing .
:Cl_Isolated a owl:Class .
:Cl_BernoulliPrinciple a owl:Class ;
    rdfs:subClassOf :Cl_Thing .

:hasChild a owl:ObjectProperty ;
    rdfs:domain :Cl_Thing ;
    rdfs:range :Cl_ChildThing .
:missingRange a owl:ObjectProperty ;
    rdfs:domain :Cl_Thing .
:hasValue a owl:DatatypeProperty ;
    rdfs:domain :Cl_Thing ;
    rdfs:range xsd:string .

:exampleThing a :Cl_ChildThing .
"""


CLEAN_TTL = """@prefix : <http://www.example.org/aviation/phak#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:ontology a owl:Ontology .

:Cl_Thing a owl:Class ;
    rdfs:label "Thing" ;
    rdfs:comment "A test class." .
:Cl_ChildThing a owl:Class ;
    rdfs:label "Child thing" ;
    rdfs:comment "A test subclass." ;
    rdfs:subClassOf :Cl_Thing .

:hasChild a owl:ObjectProperty ;
    rdfs:label "has child" ;
    rdfs:comment "Connects a thing to a child thing." ;
    rdfs:domain :Cl_Thing ;
    rdfs:range :Cl_ChildThing .
"""


SMELL_TTL = """@prefix : <http://www.example.org/aviation/phak#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:ontology a owl:Ontology .

:Cl_QuantityAssertion a owl:Class .
:Cl_Pressure a owl:Class ;
    rdfs:subClassOf :Cl_QuantityAssertion ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty :hasQuantity ;
        owl:someValuesFrom :Cl_Pressure
    ] ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty :lessThanAtmosphericPressure ;
        owl:someValuesFrom :Cl_AtmosphericPressure
    ] ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty :greaterThanAtmosphericPressure ;
        owl:someValuesFrom :Cl_AtmosphericPressure
    ] .
:Cl_AtmosphericPressure a owl:Class ;
    rdfs:subClassOf :Cl_Pressure .
:Cl_PerfectlyDryAir a owl:Class ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty :hasConstituent ;
        owl:someValuesFrom :Cl_WaterVapor
    ] .
:Cl_WaterVapor a owl:Class .

:hasQuantity a owl:ObjectProperty ;
    rdfs:domain owl:Thing ;
    rdfs:range :Cl_QuantityAssertion .
:lessThanAtmosphericPressure a owl:ObjectProperty ;
    rdfs:domain :Cl_Pressure ;
    rdfs:range :Cl_AtmosphericPressure .
:greaterThanAtmosphericPressure a owl:ObjectProperty ;
    rdfs:domain :Cl_Pressure ;
    rdfs:range :Cl_AtmosphericPressure .
:hasConstituent a owl:ObjectProperty ;
    rdfs:domain owl:Thing ;
    rdfs:range owl:Thing .
"""


def write_cq_fixture(path: Path) -> None:
    data = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "What class represents a thing?",
                        "key_entities": ["thing", "missing concept"],
                        "odp_hint": "Taxonomy",
                        "expected_answer": "Thing",
                    },
                    {
                        "competency_question": "What relation connects a thing to a child?",
                        "key_entities": ["has child", "child thing"],
                        "odp_hint": "Relation",
                        "expected_answer": "hasChild",
                    },
                    {
                        "competency_question": "What class represents Bernoulli's principle?",
                        "key_entities": ["Bernoulli's principle"],
                        "odp_hint": "Taxonomy",
                        "expected_answer": "BernoulliPrinciple",
                    },
                ],
                "1": [
                    {
                        "competency_question": "What value does a thing have?",
                        "key_entities": ["has value"],
                        "odp_hint": "Quantity",
                        "expected_answer": "hasValue",
                    }
                ],
            }
        }
    )
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")


def write_answerability_cq_fixture(path: Path) -> None:
    data = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "What relation connects a thing to a child?",
                        "key_entities": ["thing", "child thing", "has child"],
                        "odp_hint": "Relation",
                        "expected_answer": "hasChild",
                    },
                    {
                        "competency_question": "What value does a thing have?",
                        "key_entities": ["thing", "missing concept"],
                        "odp_hint": "Quantity",
                        "expected_answer": "hasValue",
                    },
                    {
                        "competency_question": "What relation connects pressure to altitude?",
                        "key_entities": ["pressure", "altitude"],
                        "odp_hint": "Relation",
                        "expected_answer": "aboveAltitude",
                    },
                ]
            }
        }
    )
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")


def test_collect_structural_metrics_reports_schema_gaps(tmp_path: Path) -> None:
    ttl_path = tmp_path / "ontology.ttl"
    ttl_path.write_text(TTL, encoding="utf-8")

    metrics = collect_structural_metrics(ttl_path)

    assert metrics.rdf_valid
    assert metrics.classes == 4
    assert metrics.object_properties == 2
    assert metrics.datatype_properties == 1
    assert metrics.non_schema_typed_resources == 1
    assert not metrics.tbox_only
    assert metrics.isolated_classes == 1
    assert metrics.properties_missing_range == ["missingRange"]
    assert metrics.class_label_coverage == 0.25
    assert not metrics.rdf_valid_tbox_extraction_prototype
    assert not metrics.valid_tbox_prototype


def test_conservative_tbox_verdict_requires_quality_basics(tmp_path: Path) -> None:
    ttl_path = tmp_path / "clean.ttl"
    ttl_path.write_text(CLEAN_TTL, encoding="utf-8")

    metrics = collect_structural_metrics(ttl_path)
    graph = Graph()
    graph.parse(data=CLEAN_TTL, format="turtle")
    gates = build_quality_gates(metrics, {"unique_entity_coverage_ratio": 1.0}, [])

    assert metrics.rdf_valid_tbox_extraction_prototype
    assert metrics.valid_tbox_prototype
    assert not collect_semantic_smells(graph)
    assert all(gate["passed"] for gate in gates)


def test_semantic_smell_checks_flag_known_bad_patterns() -> None:
    graph = Graph()
    graph.parse(data=SMELL_TTL, format="turtle")

    smells = collect_semantic_smells(graph)

    assert {item["id"] for item in smells} == {
        "opposing-Cl_Pressure-lessThanAtmosphericPressure-greaterThanAtmosphericPressure-Cl_AtmosphericPressure",
        "perfectly-dry-air-has-water-vapor",
        "self-quantity-Cl_Pressure",
    }


def test_cq_coverage_and_sampling_are_deterministic(tmp_path: Path) -> None:
    cq_path = tmp_path / "cqs.json"
    write_cq_fixture(cq_path)
    cqs = load_cqs(cq_path)
    graph = Graph()
    graph.parse(data=TTL, format="turtle")

    coverage = analyze_cq_coverage(cqs, graph)
    sample_a = stratified_sample_cqs(cqs, sample_size=2, seed=7)
    sample_b = stratified_sample_cqs(cqs, sample_size=2, seed=7)

    assert len(cqs) == 4
    assert coverage["cqs_total"] == 4
    assert coverage["matched_entity_mentions"] >= 3
    assert coverage["by_page"]["0"]["cqs"] == 3
    assert coverage["by_odp_id"]["taxonomy"]["cqs"] == 2
    assert [item.cq_id for item in sample_a] == [item.cq_id for item in sample_b]
    assert any(item.canonical_entities == ["bernoulli principle"] for item in cqs)


def test_answerability_metrics_cover_yes_partial_no_and_expected_answers(tmp_path: Path) -> None:
    cq_path = tmp_path / "answerability-cqs.json"
    write_answerability_cq_fixture(cq_path)
    cqs = load_cqs(cq_path)
    graph = Graph()
    graph.parse(data=TTL, format="turtle")

    coverage = analyze_cq_coverage(cqs, graph)
    metrics = coverage["answerability_metrics"]
    per_cq = metrics["per_cq"]

    assert metrics["metric_standard"].startswith("Deterministic silver heuristic")
    assert metrics["yes"] == 1
    assert metrics["partial"] == 1
    assert metrics["no"] == 1
    assert metrics["expected_answer_term_coverage_ratio"] == 0.6667
    assert metrics["property_relation_coverage_ratio"] == 0.6667
    assert metrics["connected_class_property_ratio"] == 0.6667
    assert metrics["object_property_matches"] == 1
    assert metrics["datatype_property_matches"] == 1
    assert per_cq[0]["support"] == "yes"
    assert per_cq[0]["connected_class_property_pairs"]
    assert per_cq[1]["support"] == "partial"
    assert per_cq[1]["matched_datatype_properties"] == ["hasValue"]
    assert per_cq[2]["support"] == "no"


def test_cq_validation_rejects_legacy_artifacts(tmp_path: Path) -> None:
    cq_path = tmp_path / "legacy-cqs.json"
    cq_path.write_text(
        json.dumps(
            {
                "doc": {
                    "0": [
                        {
                            "competency_question": "What class represents a thing?",
                            "key_entities": ["thing"],
                            "odp_hint": "Taxonomy",
                            "expected_answer": "Thing",
                        }
                    ]
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        load_cq_artifact(cq_path)
    except CQValidationError as exc:
        assert "missing normalized fields" in str(exc)
    else:
        raise AssertionError("Legacy CQ artifact should fail strict validation")


def test_odp_normalization_uses_controlled_vocabulary() -> None:
    assert normalize_odp_hint("Causal Relation / Event Reification") == "event_reification"
    assert normalize_odp_hint("PhysicalObject / SpatialContainment") == "spatial_relation"
    assert normalize_odp_hint("Unknown Pattern") == "other"


def test_repository_cq_artifact_is_normalized() -> None:
    data = load_cq_artifact("data/cqs/06_phak_ch4_0.json")

    total = sum(len(items) for pages in data.values() for items in pages.values())

    assert total == 334


def test_parse_ai_review_response_accepts_fenced_json() -> None:
    result = parse_ai_review_response(
        "cq-1",
        """```json
        {
          "supported": "YES",
          "confidence": 1.2,
          "matched_terms": ["Cl_Thing"],
          "missing_terms": [],
          "rationale": "The class is present.",
          "suggested_fixes": []
        }
        ```""",
    )

    assert result["supported"] == "yes"
    assert result["confidence"] == 1.0
    assert result["matched_terms"] == ["Cl_Thing"]


def test_evaluate_ontology_writes_reports_without_ai(tmp_path: Path) -> None:
    ttl_path = tmp_path / "ontology.ttl"
    cq_path = tmp_path / "cqs.json"
    out_dir = tmp_path / "reports"
    ttl_path.write_text(TTL, encoding="utf-8")
    write_cq_fixture(cq_path)

    result = evaluate_ontology(
        ontology_file=ttl_path,
        cq_file=cq_path,
        output_dir=out_dir,
        sample_size=2,
        seed=42,
        ai_review=False,
    )

    assert Path(result["output_paths"]["json"]).exists()
    assert Path(result["output_paths"]["markdown"]).exists()
    assert not result["judgment"]["valid_tbox_prototype"]
    assert "quality_gates" in result
    assert "semantic_smells" in result
    assert not Path(result["metadata"]["ontology_file"]).is_absolute()
    assert not Path(result["metadata"]["cq_file"]).is_absolute()
    assert not Path(result["output_paths"]["json"]).is_absolute()
    assert result["ai_review"]["summary"]["reviewed_cqs"] == 0
    markdown = (out_dir / "ontology_evaluation.md").read_text(encoding="utf-8")
    assert "Quality Gates" in markdown
    assert "Silver Answerability Heuristics" in markdown
    assert "not gold-standard answerability" in markdown
    assert "AI review skipped" in markdown


def test_cli_ontology_evaluate_no_ai_review(tmp_path: Path) -> None:
    ttl_path = tmp_path / "ontology.ttl"
    cq_path = tmp_path / "cqs.json"
    out_dir = tmp_path / "reports"
    ttl_path.write_text(TTL, encoding="utf-8")
    write_cq_fixture(cq_path)

    result = CliRunner().invoke(
        main,
        [
            "ontology",
            "evaluate",
            "--ontology-file",
            str(ttl_path),
            "--cq-file",
            str(cq_path),
            "--output-dir",
            str(out_dir),
            "--sample-size",
            "2",
            "--no-ai-review",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (out_dir / "ontology_evaluation.json").exists()
    assert "Evaluation completed without AI review." in result.output


def test_cli_ontology_evaluate_defaults_to_deterministic_report_name(tmp_path: Path) -> None:
    ttl_path = tmp_path / "ontology.ttl"
    cq_path = tmp_path / "cqs.json"
    out_dir = tmp_path / "reports"
    ttl_path.write_text(TTL, encoding="utf-8")
    write_cq_fixture(cq_path)

    result = CliRunner().invoke(
        main,
        [
            "ontology",
            "evaluate",
            "--ontology-file",
            str(ttl_path),
            "--cq-file",
            str(cq_path),
            "--output-dir",
            str(out_dir),
            "--report-name",
            "custom_eval",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (out_dir / "custom_eval.json").exists()
    assert (out_dir / "custom_eval.md").exists()
    assert "Evaluation completed without AI review." in result.output


def test_cli_ontology_validate_cqs(tmp_path: Path) -> None:
    cq_path = tmp_path / "cqs.json"
    write_cq_fixture(cq_path)

    result = CliRunner().invoke(
        main,
        [
            "ontology",
            "validate-cqs",
            "--cq-file",
            str(cq_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "OK: validated 4 normalized CQs" in result.output
