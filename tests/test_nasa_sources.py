from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.chunking.chunks import build_chunks_from_text_source
from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.nasa_sources import (
    build_ontology_boundary_nasa,
    write_cross_source_ontology_validation,
    write_multisource_retrieval_smoke,
    write_nasa_benchmark_summary,
    write_nasa_chunking_summary,
    write_ontology_boundary_nasa_report,
)
from aviation_agentic_ai.sources.nasa_web import (
    build_nasa_source_discovery,
    discover_nasa_aerodynamics_links,
    extract_main_content,
    ingest_nasa_sources,
    load_normalized_nasa_pages,
    normalize_nasa_page,
    read_nasa_source_manifest,
    write_nasa_source_discovery_report,
    write_nasa_source_validation_report,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "nasa_bga"


def _manifest(path: Path) -> Path:
    content = """
corpus_id: nasa_bga_aerodynamics_test
source_type: nasa_web_educational_page
source_authority: NASA Glenn Research Center
advisory_risk_level: learning
sources:
  - document_id: nasa_bga_aerodynamic_forces
    title: Aerodynamic Forces
    url: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/aerodynamic-forces/
    source_type: nasa_web_educational_page
    source_authority: NASA Glenn Research Center
    advisory_risk_level: learning
    source_section: Lessons in Aerodynamics
    is_interactive: false
    expected_topics: [lift, drag, aerodynamic force]
    expected_ontology_concepts: [Lift, Drag, AerodynamicForce]
    expected_relations: [dependsOn]
    status: planned
    include_in_corpus: true
    include_in_experiment: true
    experiment_scope: nasa_bga_lessons_in_aerodynamics
  - document_id: nasa_bga_lift_equation
    title: Lift Equation
    url: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation/
    source_type: nasa_web_educational_page
    source_authority: NASA Glenn Research Center
    advisory_risk_level: learning
    source_section: Lift
    is_interactive: false
    expected_topics: [lift equation, lift coefficient, velocity]
    expected_ontology_concepts: [LiftEquation, LiftCoefficient, Velocity]
    expected_relations: [hasVariable]
    status: planned
    include_in_corpus: true
    include_in_experiment: false
    experiment_scope: collected_not_used_in_current_experiment
"""
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def _ingest(tmp_path: Path) -> tuple[Path, Path, Path]:
    manifest = _manifest(tmp_path / "manifest.yaml")
    raw_dir = tmp_path / "raw"
    report_dir = tmp_path / "reports"
    ingest_nasa_sources(
        manifest,
        raw_output_dir=raw_dir,
        report_output_dir=report_dir,
        fixture_dir=FIXTURE_DIR,
    )
    return manifest, raw_dir, report_dir


def test_nasa_source_manifest_validation(tmp_path: Path) -> None:
    manifest = read_nasa_source_manifest(_manifest(tmp_path / "manifest.yaml"))

    assert len(manifest["sources"]) == 2
    assert manifest["sources"][0]["document_id"] == "nasa_bga_aerodynamic_forces"
    assert manifest["sources"][0]["source_section"] == "Lessons in Aerodynamics"
    assert manifest["sources"][0]["include_in_experiment"] is True
    assert manifest["sources"][1]["include_in_experiment"] is False


def test_nasa_source_discovery_separates_full_collection_and_experiment_subset(
    tmp_path: Path,
) -> None:
    landing_html = """
    <main>
      <h1>Guide to Aerodynamics</h1>
      <h2>Lessons in Aerodynamics</h2>
      <ul>
        <li><a href="/beginners-guide-to-aeronautics/aerodynamic-forces/">Aerodynamic Forces</a></li>
        <li><a href="/beginners-guide-to-aeronautics/dynamic-pressure/">Dynamic Pressure</a></li>
      </ul>
      <h2>Lift</h2>
      <ul>
        <li><a href="/beginners-guide-to-aeronautics/lift-equation/">Lift Equation</a></li>
        <li><a href="/beginners-guide-to-aeronautics/foilsimstudent/">Student Airfoil Interactive Simulator</a></li>
      </ul>
    </main>
    """
    discovery = discover_nasa_aerodynamics_links(landing_html)

    assert discovery["unique_urls_total"] == 4
    assert discovery["interactive_links_total"] == 1
    assert len(discovery["groups"]["Lessons in Aerodynamics"]) == 2

    json_path, md_path, report = write_nasa_source_discovery_report(
        _manifest(tmp_path / "manifest.yaml"),
        tmp_path / "stage",
        landing_html=landing_html,
    )
    direct = build_nasa_source_discovery(
        _manifest(tmp_path / "manifest2.yaml"),
        landing_html=landing_html,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert report["metadata"]["discovered_unique_urls_total"] == 4
    assert report["metadata"]["covered_unique_urls_total"] == 2
    assert report["metadata"]["missing_unique_urls_total"] == 2
    assert direct["metadata"]["experiment_subset_section"] == "Lessons in Aerodynamics"


def test_nasa_html_cleaning_removes_navigation_footer_and_keeps_lesson_content() -> None:
    html = (FIXTURE_DIR / "nasa_bga_aerodynamic_forces.html").read_text(encoding="utf-8")
    cleaned = extract_main_content(html)

    assert "Aerodynamic forces are generated" in cleaned
    assert "Diagram showing lift and drag" in cleaned
    assert "Enter Search Term" not in cleaned
    assert "Rate this page" not in cleaned
    assert "Glenn Research Center 21000" not in cleaned


def test_nasa_normalized_page_schema(tmp_path: Path) -> None:
    html = (FIXTURE_DIR / "nasa_bga_lift_equation.html").read_text(encoding="utf-8")
    record = read_nasa_source_manifest(_manifest(tmp_path / "manifest.yaml"))["sources"][1]
    page = normalize_nasa_page(record, html)

    assert page["document_id"] == "nasa_bga_lift_equation"
    assert page["source_type"] == "nasa_web_educational_page"
    assert page["advisory_risk_level"] == "learning"
    assert page["source_section"] == "Lift"
    assert page["include_in_corpus"] is True
    assert page["include_in_experiment"] is False
    assert page["page_last_updated"] == "May 14, 2024"
    assert page["content_hash"]
    assert page["sections"]
    assert page["equations"]
    assert page["validation_status"] == "valid"


def test_nasa_ingestion_and_source_validation_reports(tmp_path: Path) -> None:
    _manifest_path, raw_dir, _report_dir = _ingest(tmp_path)

    json_path, md_path, result = write_nasa_source_validation_report(
        raw_dir,
        tmp_path / "stage",
        metadata_path=tmp_path / "sources" / "metadata.json",
        sections_path=tmp_path / "sources" / "sections.json",
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["valid"] is True
    assert (tmp_path / "sources" / "metadata.json").exists()
    assert (tmp_path / "sources" / "sections.json").exists()


def test_web_source_chunks_have_section_ids_and_source_metadata(tmp_path: Path) -> None:
    _manifest_path, raw_dir, _report_dir = _ingest(tmp_path)
    page = load_normalized_nasa_pages(raw_dir)[0]

    chunks = build_chunks_from_text_source(
        page,
        source_path=raw_dir / f"{page['document_id']}.json",
        strategy="structure_aware_large",
    )

    assert chunks
    assert chunks[0].chunk_id.startswith(f"{page['document_id']}-structure_aware_large-s")
    assert "-c00" in chunks[0].chunk_id
    assert chunks[0].metadata["source_url"] == page["url"]
    assert chunks[0].metadata["source_type"] == "nasa_web_educational_page"
    assert chunks[0].metadata["section_id"]


def test_nasa_chunking_summary_writes_required_strategy_files(tmp_path: Path) -> None:
    _manifest_path, raw_dir, _report_dir = _ingest(tmp_path)

    json_path, md_path, result = write_nasa_chunking_summary(
        raw_dir,
        tmp_path / "chunks",
        tmp_path / "stage",
        semantic_download=False,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["metadata"]["corpus_pages_total"] == 2
    assert result["metadata"]["experiment_pages_total"] == 1
    assert result["metadata"]["experiment_subset"] == "Lessons in Aerodynamics"
    assert set(result["strategies"]) == {
        "structure_aware_large",
        "recursive_medium",
        "fixed_large",
        "embedding_semantic",
    }
    for strategy in result["strategies"]:
        assert (tmp_path / "chunks" / f"nasa_bga_aerodynamics.{strategy}.jsonl").exists()
        assert result["strategies"][strategy]["source_url_coverage"] == 1.0


def test_ontology_boundary_report_classifies_covered_candidate_and_out_of_scope(
    tmp_path: Path,
) -> None:
    manifest, raw_dir, _report_dir = _ingest(tmp_path)
    ontology = tmp_path / "ontology.ttl"
    ontology.write_text(
        """
@prefix : <http://example.test/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
:Cl_Lift a owl:Class .
:Cl_Drag a owl:Class .
:Cl_Density a owl:Class .
:Cl_AngleOfAttack a owl:Class .
""".strip()
        + "\n",
        encoding="utf-8",
    )
    profile = tmp_path / "profile.yaml"
    profile.write_text("profile: test\n", encoding="utf-8")

    result = build_ontology_boundary_nasa(ontology, raw_dir, manifest, profile)

    assert any(item["concept"] == "Lift" for item in result["existing_ontology_coverage"])
    assert any(item["concept"] == "AirDensity" for item in result["alias_candidates"])
    assert any(item["concept"] == "LiftEquation" for item in result["nasa_extension_candidates"])
    assert result["out_of_scope_detections"]

    json_path, md_path, written = write_ontology_boundary_nasa_report(
        ontology,
        raw_dir,
        manifest,
        profile,
        tmp_path / "stage",
        proposal_path=tmp_path / "proposal.ttl",
    )
    assert json_path.exists()
    assert md_path.exists()
    assert (tmp_path / "proposal.ttl").exists()
    assert written["metadata"]["external_aviation_expert_certified"] is False


def test_nasa_seed_cross_source_and_smoke_reports(tmp_path: Path) -> None:
    _manifest_path, raw_dir, _report_dir = _ingest(tmp_path)
    write_nasa_chunking_summary(raw_dir, tmp_path / "chunks", tmp_path / "stage", semantic_download=False)

    nasa_json, _nasa_md, nasa_result = write_nasa_benchmark_summary(
        raw_dir,
        tmp_path / "nasa.seed.json",
        tmp_path / "stage",
    )
    cross_json, _cross_md, cross_result = write_cross_source_ontology_validation(
        raw_dir,
        tmp_path / "nasa.seed.json",
        tmp_path / "cross.seed.json",
        tmp_path / "stage",
    )

    assert nasa_json.exists()
    assert cross_json.exists()
    assert nasa_result["metadata"]["labels_total"] == 50
    assert cross_result["metadata"]["labels_total"] == 30

    faa_chunks = tmp_path / "faa.jsonl"
    faa_chunks.write_text(
        json.dumps(
            {
                "chunk_id": "06_phak_ch4_0-structure_aware_large-p00-c00",
                "source_document": "06_phak_ch4_0",
                "source_path": "data/raw/06_phak_ch4_0.pdf",
                "page": 0,
                "chunk_index": 0,
                "char_start": 0,
                "char_end": 80,
                "text": "Lift and drag explain airfoil aerodynamics and pilot training framing.",
                "token_count": 10,
                "strategy": "structure_aware_large",
                "section": "Lift",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    smoke_json, smoke_md, smoke = write_multisource_retrieval_smoke(
        tmp_path / "nasa.seed.json",
        tmp_path / "cross.seed.json",
        tmp_path / "chunks" / "nasa_bga_aerodynamics.structure_aware_large.jsonl",
        faa_chunks,
        tmp_path / "stage",
    )

    assert smoke_json.exists()
    assert smoke_md.exists()
    assert smoke["metadata"]["status"] == "smoke_experiment"
    assert "faa_plus_nasa" in smoke["scenarios"]


def test_cli_nasa_source_validation_uses_fixture_ingestion(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path / "manifest.yaml")
    raw_dir = tmp_path / "raw"
    runner = CliRunner()

    ingest = runner.invoke(
        main,
        [
            "source",
            "ingest-nasa",
            "--manifest",
            str(manifest),
            "--raw-output-dir",
            str(raw_dir),
            "--output-dir",
            str(tmp_path / "stage"),
            "--fixture-dir",
            str(FIXTURE_DIR),
        ],
    )
    assert ingest.exit_code == 0, ingest.output

    validation = runner.invoke(
        main,
        [
            "report",
            "nasa-source-validation",
            "--raw-dir",
            str(raw_dir),
            "--output-dir",
            str(tmp_path / "stage"),
            "--metadata-path",
            str(tmp_path / "metadata.json"),
            "--sections-path",
            str(tmp_path / "sections.json"),
        ],
    )
    assert validation.exit_code == 0, validation.output
    assert "Validated 2 of 2 NASA pages" in validation.output


def test_cli_nasa_source_discovery_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_report_nasa

    calls: dict[str, Path | str] = {}

    def fake_writer(manifest_path: Path, output_dir: Path, *, report_name: str):
        calls["manifest_path"] = manifest_path
        calls["output_dir"] = output_dir
        calls["report_name"] = report_name
        json_path = output_dir / f"{report_name}.json"
        md_path = output_dir / f"{report_name}.md"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text("{}", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return (
            json_path,
            md_path,
            {
                "metadata": {
                    "covered_unique_urls_total": 90,
                    "discovered_unique_urls_total": 90,
                }
            },
        )

    monkeypatch.setattr(cli_report_nasa, "write_nasa_source_discovery_report", fake_writer)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "report",
            "nasa-source-discovery",
            "--manifest",
            str(_manifest(tmp_path / "manifest.yaml")),
            "--output-dir",
            str(tmp_path / "stage"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "90 of 90 discovered unique URLs" in result.output
    assert calls["report_name"] == "nasa_source_discovery"
