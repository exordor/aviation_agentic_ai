import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.ontology.cq import load_cq_artifact, normalize_cq_artifact
from aviation_agentic_ai.ontology.source_scope import (
    build_boundary_cq_artifact,
    build_cq_gap_review,
    build_source_scope,
    write_source_scope_reports,
)


PDF_PATH = Path("data/raw/06_phak_ch4_0.pdf")


def test_boundary_cq_artifact_is_normalized_and_source_linked() -> None:
    artifact = build_boundary_cq_artifact(PDF_PATH)
    document = artifact["06_phak_ch4_0"]
    items = [cq for page_items in document.values() for cq in page_items]

    assert len(items) == 10
    assert all("id" in item for item in items)
    assert all(item["source_document"] == "06_phak_ch4_0" for item in items)
    assert all(isinstance(item["source_page"], int) for item in items)
    assert all(item["canonical_entities"] for item in items)
    assert {
        "atmosphere",
        "air",
        "nitrogen",
        "oxygen",
    }.issubset(set(items[0]["canonical_entities"]))


def test_source_scope_shape_uses_pdf_pages() -> None:
    scope = build_source_scope(PDF_PATH)

    assert scope["source_document"] == "06_phak_ch4_0"
    assert scope["page_count"] >= 9
    assert len(scope["core_themes"]) == 10
    assert len(scope["in_scope_ontology_questions"]) == 10
    assert "no LLM" in scope["method"]
    assert not Path(scope["source_path"]).is_absolute()
    assert any("Atmosphere and air composition" in page["matched_topics"] for page in scope["page_summaries"])
    assert "wingtip vortex" in scope["key_concepts"]
    assert any("affects performance" == relation for relation in scope["relation_candidates"])


def test_gap_review_reports_covered_weak_missing_and_duplicates(tmp_path: Path) -> None:
    existing = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "How should air and oxygen composition be modeled?",
                        "key_entities": ["air", "oxygen", "composition"],
                        "odp_hint": "Material composition",
                        "expected_answer": "Air has oxygen as a constituent gas.",
                    },
                    {
                        "competency_question": "How should air and oxygen composition be represented?",
                        "key_entities": ["air", "oxygen", "composition"],
                        "odp_hint": "Material composition",
                        "expected_answer": "Air has oxygen as a constituent gas.",
                    },
                    {
                        "competency_question": "What class represents a checklist item?",
                        "key_entities": ["checklist"],
                        "odp_hint": "Taxonomy",
                        "expected_answer": "ChecklistItem.",
                    },
                    {
                        "competency_question": "What class represents density altitude?",
                        "key_entities": ["density altitude"],
                        "odp_hint": "Quantity",
                        "expected_answer": "DensityAltitude is an altitude quantity.",
                    },
                ]
            }
        }
    )
    boundary = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "How should air and oxygen composition be modeled?",
                        "key_entities": ["air", "oxygen", "composition"],
                        "odp_hint": "Material composition",
                        "expected_answer": "Air has oxygen as a constituent gas.",
                    },
                    {
                        "competency_question": "How should density altitude affect performance?",
                        "key_entities": ["density altitude", "performance"],
                        "odp_hint": "Causal relation",
                        "expected_answer": "Density altitude affects aircraft performance.",
                    },
                    {
                        "competency_question": "How should wingtip vortex and winglets be modeled?",
                        "key_entities": ["wingtip vortex", "winglet"],
                        "odp_hint": "Flow interaction",
                        "expected_answer": "Winglets mitigate wingtip vortex effects.",
                    },
                ]
            }
        }
    )
    existing_path = tmp_path / "existing.json"
    boundary_path = tmp_path / "boundary.json"
    existing_path.write_text(json.dumps(existing) + "\n", encoding="utf-8")
    boundary_path.write_text(json.dumps(boundary) + "\n", encoding="utf-8")

    review = build_cq_gap_review(existing_path, boundary_path)

    statuses = {item["boundary_question"]: item["status"] for item in review["boundary_matches"]}
    assert statuses["How should air and oxygen composition be modeled?"] == "covered"
    assert statuses["How should density altitude affect performance?"] == "weak"
    assert statuses["How should wingtip vortex and winglets be modeled?"] == "missing"
    assert review["summary"]["duplicate_pairs"] >= 1
    assert review["summary"]["out_of_scope_signals"] >= 1


def test_write_source_scope_reports_writes_loadable_artifacts(tmp_path: Path) -> None:
    boundary_path = tmp_path / "boundary.json"
    result = write_source_scope_reports(
        PDF_PATH,
        "data/cqs/06_phak_ch4_0.json",
        boundary_path,
        tmp_path,
    )

    assert Path(result["paths"]["source_scope_json"]).exists()
    assert Path(result["paths"]["source_scope_md"]).exists()
    assert Path(result["paths"]["cq_gap_review_json"]).exists()
    assert Path(result["paths"]["cq_gap_review_md"]).exists()
    assert all(not Path(path).is_absolute() for path in result["paths"].values())
    assert load_cq_artifact(boundary_path)["06_phak_ch4_0"]


def test_cli_ontology_scope_writes_reports(tmp_path: Path) -> None:
    boundary_path = tmp_path / "boundary.json"

    result = CliRunner().invoke(
        main,
        [
            "ontology",
            "scope",
            "--pdf",
            str(PDF_PATH),
            "--existing-cqs",
            "data/cqs/06_phak_ch4_0.json",
            "--boundary-output",
            str(boundary_path),
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert boundary_path.exists()
    assert (tmp_path / "source_scope.json").exists()
    assert (tmp_path / "cq_gap_review.json").exists()
    assert "Source scope completed" in result.output
