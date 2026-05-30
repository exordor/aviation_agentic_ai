import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.thesis_claims import (
    REVISED_THESIS_CLAIM,
    detect_unsafe_claims,
    write_thesis_claims_review,
)


def test_thesis_claim_report_generation_includes_revised_claim(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "GraphRAG is evaluated with layered metrics and no mixed overall score.\n",
        encoding="utf-8",
    )

    json_path, md_path, result = write_thesis_claims_review(
        tmp_path / "reports" / "stages",
        project_root=tmp_path,
        scan_paths=[readme],
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["revised_thesis_claim"] == REVISED_THESIS_CLAIM
    assert result["unsafe_claims_status"] == "not_found"
    assert "Evidence gaps before thesis submission".lower() in md_path.read_text(
        encoding="utf-8"
    ).lower()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["research_questions"][0]["id"] == "RQ1"
    assert data["hypotheses"][-1]["id"] == "H5"


def test_unsafe_wording_detector_catches_overclaims() -> None:
    text = "\n".join(
        [
            "GraphRAG always improves Recall.",
            "Hybrid always outperforms vector retrieval.",
            "This is a certified aviation assistant.",
            "The tool can replace POH procedures.",
            "The tool can replace ATC clearances.",
            "Use it for an operational flight decision.",
            "The benchmark is human reviewed.",
            "These are expert gold labels.",
            "The KG has semantically correct triples.",
            "The system is flight-ready.",
        ]
    )

    findings = detect_unsafe_claims(text)

    pattern_ids = {finding["pattern_id"] for finding in findings}
    assert "graphrag_universal_recall" in pattern_ids
    assert "hybrid_always_beats_vector" in pattern_ids
    assert "certified_aviation_assistant" in pattern_ids
    assert "replace_poh" in pattern_ids
    assert "replace_atc" in pattern_ids
    assert "operational_flight_decision" in pattern_ids
    assert "human_review_claim" in pattern_ids
    assert "expert_review_claim" in pattern_ids
    assert "semantic_triple_overclaim" in pattern_ids
    assert "proven_safe" in pattern_ids


def test_unsafe_wording_detector_ignores_boundary_negation() -> None:
    text = (
        "This system is for aviation learning and decision-support only. "
        "Do not claim to replace the aircraft POH, approved checklists, ATC "
        "instructions, instructor guidance, or pilot judgment."
    )

    assert detect_unsafe_claims(text) == []


def test_cli_report_thesis_claims_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_write_thesis_claims_review(output_dir, **kwargs):
        output = Path(output_dir)
        json_path = output / "thesis_claims_review.json"
        md_path = output / "thesis_claims_review.md"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text("{}", encoding="utf-8")
        md_path.write_text("# Thesis Claims Review\n", encoding="utf-8")
        assert kwargs["report_name"] == "thesis_claims_review"
        return json_path, md_path, {"metadata": {"unsafe_claims_total": 0}}

    monkeypatch.setattr(cli, "write_thesis_claims_review", fake_write_thesis_claims_review)

    result = CliRunner().invoke(
        main,
        ["report", "thesis-claims", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert "unsafe claims found: 0" in result.output
