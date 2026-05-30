from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.nasa_sources import (
    DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    write_cross_source_ontology_validation,
    write_multisource_retrieval_smoke,
    write_nasa_benchmark_summary,
    write_nasa_chunking_summary,
    write_nasa_kg_validation_report,
    write_ontology_boundary_nasa_report,
)
from aviation_agentic_ai.sources.nasa_web import (
    write_nasa_source_discovery_report,
    write_nasa_source_validation_report,
)


def register_nasa_report_commands(report: click.Group) -> None:
    @report.command("nasa-source-discovery")
    @click.option("--manifest", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="nasa_source_discovery", show_default=True)
    def report_nasa_source_discovery(
        manifest: Path | None,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Compare the NASA BGA landing-page links with the tracked manifest."""
        config = load_default_config()
        manifest_path = manifest or resolve_project_path(
            "data/sources/nasa_bga_aerodynamics_sources.yaml"
        )
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_nasa_source_discovery_report(
            manifest_path,
            report_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            "NASA source discovery coverage: "
            f"{result['metadata']['covered_unique_urls_total']} of "
            f"{result['metadata']['discovered_unique_urls_total']} discovered unique URLs."
        )

    @report.command("nasa-source-validation")
    @click.option("--raw-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--metadata-path", type=click.Path(path_type=Path), default=None)
    @click.option("--sections-path", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="nasa_source_validation", show_default=True)
    def report_nasa_source_validation(
        raw_dir: Path | None,
        output_dir: Path | None,
        metadata_path: Path | None,
        sections_path: Path | None,
        report_name: str,
    ) -> None:
        """Validate normalized NASA BGA source pages and write metadata artifacts."""
        config = load_default_config()
        source_dir = raw_dir or resolve_project_path("data/raw/nasa_bga_aerodynamics")
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        metadata_output = metadata_path or resolve_project_path(
            "data/sources/nasa_bga_aerodynamics_metadata.json"
        )
        sections_output = sections_path or resolve_project_path(
            "data/sources/nasa_bga_aerodynamics_sections.json"
        )
        json_path, md_path, result = write_nasa_source_validation_report(
            source_dir,
            report_dir,
            metadata_path=metadata_output,
            sections_path=sections_output,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            f"Validated {result['metadata']['valid_pages']} of "
            f"{result['metadata']['pages_total']} NASA pages."
        )

    @report.command("nasa-chunking-summary")
    @click.option("--raw-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--chunks-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option(
        "--embedding-model",
        default=DEFAULT_SEMANTIC_EMBEDDING_MODEL,
        show_default=True,
    )
    @click.option("--semantic-download/--no-semantic-download", default=True, show_default=True)
    @click.option("--report-name", default="nasa_chunking_summary", show_default=True)
    def report_nasa_chunking_summary(
        raw_dir: Path | None,
        chunks_dir: Path | None,
        output_dir: Path | None,
        embedding_model: str,
        semantic_download: bool,
        report_name: str,
    ) -> None:
        """Build deterministic chunks from normalized NASA BGA pages."""
        config = load_default_config()
        source_dir = raw_dir or resolve_project_path("data/raw/nasa_bga_aerodynamics")
        chunk_output = chunks_dir or resolve_project_path("data/chunks")
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_nasa_chunking_summary(
            source_dir,
            chunk_output,
            report_dir,
            embedding_model=embedding_model,
            semantic_download=semantic_download,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(f"Built NASA chunks for {len(result['strategies'])} strategies.")

    @report.command("ontology-boundary-nasa")
    @click.option("--raw-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--manifest", type=click.Path(path_type=Path), default=None)
    @click.option("--ontology-file", type=click.Path(path_type=Path), default=None)
    @click.option("--profile", "profile_path", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--proposal-path", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="ontology_boundary_nasa", show_default=True)
    def report_ontology_boundary_nasa(
        raw_dir: Path | None,
        manifest: Path | None,
        ontology_file: Path | None,
        profile_path: Path | None,
        output_dir: Path | None,
        proposal_path: Path | None,
        report_name: str,
    ) -> None:
        """Validate current ontology boundary against NASA BGA aerodynamics pages."""
        config = load_default_config()
        source_dir = raw_dir or resolve_project_path("data/raw/nasa_bga_aerodynamics")
        manifest_path = manifest or resolve_project_path(
            "data/sources/nasa_bga_aerodynamics_sources.yaml"
        )
        ontology_path = ontology_file or resolve_project_path(config["paths"]["curated_ontology"])
        extraction_profile = profile_path or resolve_project_path("configs/extraction_profile.yaml")
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        proposal_output = proposal_path or resolve_project_path(
            "data/ontology/proposals/nasa_aerodynamics_extension.proposal.ttl"
        )
        json_path, md_path, result = write_ontology_boundary_nasa_report(
            ontology_path,
            source_dir,
            manifest_path,
            extraction_profile,
            report_dir,
            proposal_path=proposal_output,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            "Class candidates: "
            f"{len(result['recommended_class_additions'])}; "
            f"alias candidates: {len(result['alias_candidates'])}."
        )

    @report.command("nasa-benchmark-summary")
    @click.option("--raw-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--seed-path", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="nasa_benchmark_summary", show_default=True)
    def report_nasa_benchmark_summary(
        raw_dir: Path | None,
        seed_path: Path | None,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Generate and summarize the NASA BGA seed benchmark."""
        config = load_default_config()
        source_dir = raw_dir or resolve_project_path("data/raw/nasa_bga_aerodynamics")
        seed_output = seed_path or resolve_project_path("data/cqs/nasa_bga_aerodynamics.seed.gold.json")
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_nasa_benchmark_summary(
            source_dir,
            seed_output,
            report_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(f"Generated {result['metadata']['labels_total']} NASA seed labels.")

    @report.command("nasa-kg-validation")
    @click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
    @click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
    @click.option("--profile", "profile_path", type=click.Path(path_type=Path), default=None)
    @click.option("--ontology-file", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="nasa_kg_validation", show_default=True)
    def report_nasa_kg_validation(
        kg_path: Path | None,
        chunks_path: Path | None,
        profile_path: Path | None,
        ontology_file: Path | None,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Write NASA-specific KG validation metrics from an existing KG artifact."""
        config = load_default_config()
        kg_file = kg_path or resolve_project_path(
            "data/kg/nasa_bga_aerodynamics.structure_aware_large.kg.jsonl"
        )
        chunks_file = chunks_path or resolve_project_path(
            "data/chunks/nasa_bga_aerodynamics.structure_aware_large.jsonl"
        )
        profile = profile_path or resolve_project_path("configs/extraction_profile.yaml")
        ontology_path = ontology_file or resolve_project_path(config["paths"]["curated_ontology"])
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_nasa_kg_validation_report(
            kg_file,
            chunks_file,
            profile,
            ontology_path,
            report_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            f"Validated {result['valid_triples']} of "
            f"{result['triples_total']} NASA KG triples."
        )

    @report.command("cross-source-ontology-validation")
    @click.option("--raw-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--nasa-seed", type=click.Path(path_type=Path), default=None)
    @click.option("--cross-seed", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="cross_source_ontology_validation", show_default=True)
    def report_cross_source_ontology_validation(
        raw_dir: Path | None,
        nasa_seed: Path | None,
        cross_seed: Path | None,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Generate cross-source seed labels and ontology-routing diagnostics."""
        config = load_default_config()
        source_dir = raw_dir or resolve_project_path("data/raw/nasa_bga_aerodynamics")
        nasa_seed_path = nasa_seed or resolve_project_path(
            "data/cqs/nasa_bga_aerodynamics.seed.gold.json"
        )
        cross_seed_path = cross_seed or resolve_project_path(
            "data/cqs/faa_phak_nasa_cross_source.seed.gold.json"
        )
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_cross_source_ontology_validation(
            source_dir,
            nasa_seed_path,
            cross_seed_path,
            report_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(f"Generated {result['metadata']['labels_total']} cross-source labels.")

    @report.command("multisource-retrieval-smoke")
    @click.option("--nasa-seed", type=click.Path(path_type=Path), default=None)
    @click.option("--cross-seed", type=click.Path(path_type=Path), default=None)
    @click.option("--nasa-chunks", type=click.Path(path_type=Path), default=None)
    @click.option("--faa-chunks", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="multisource_retrieval_smoke", show_default=True)
    def report_multisource_retrieval_smoke(
        nasa_seed: Path | None,
        cross_seed: Path | None,
        nasa_chunks: Path | None,
        faa_chunks: Path | None,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Run a small deterministic FAA/NASA source-routing smoke report."""
        config = load_default_config()
        nasa_seed_path = nasa_seed or resolve_project_path(
            "data/cqs/nasa_bga_aerodynamics.seed.gold.json"
        )
        cross_seed_path = cross_seed or resolve_project_path(
            "data/cqs/faa_phak_nasa_cross_source.seed.gold.json"
        )
        nasa_chunks_path = nasa_chunks or resolve_project_path(
            "data/chunks/nasa_bga_aerodynamics.structure_aware_large.jsonl"
        )
        faa_chunks_path = faa_chunks or resolve_project_path(
            "data/chunks/06_phak_ch4_0.structure_aware_large.benchmark_v2.jsonl"
        )
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_multisource_retrieval_smoke(
            nasa_seed_path,
            cross_seed_path,
            nasa_chunks_path,
            faa_chunks_path,
            report_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            "Smoke labels: "
            f"{result['metadata']['labels_total']} with FAA+NASA "
            f"Recall@5={result['scenarios']['faa_plus_nasa']['recall_at_5']}."
        )
