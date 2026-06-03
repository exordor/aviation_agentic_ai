from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_bga_domain_transfer_pilot import (
    build_nasa_bga_domain_transfer_pilot,
    write_nasa_bga_domain_transfer_pilot,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _write_transfer_fixture(root: Path) -> None:
    _write_json(
        root / "reports/stages/nasa_source_ingestion.json",
        {
            "metadata": {
                "pages_total": 90,
                "valid_pages": 89,
                "invalid_pages": 1,
                "source_type": "nasa_web_educational_page",
                "source_authority": "NASA Glenn Research Center",
            }
        },
    )
    _write_json(
        root / "reports/stages/nasa_benchmark_summary.json",
        {
            "metadata": {
                "labels_total": 50,
                "supported_total": 45,
                "no_answer_total": 5,
                "review_status": "llm_or_project_seed_not_expert_certified",
            },
            "label_distribution": {
                "concept_factual": 25,
                "relation_causal": 10,
                "insufficient_evidence": 5,
            },
        },
    )
    _write_json(
        root / "reports/stages/nasa_kg_validation.json",
        {
            "triples_total": 2,
            "valid_triples": 2,
            "errors_total": 0,
            "evidence_in_source_rate": 1.0,
            "provenance_completeness": 1.0,
            "rejected_triple_count": 0,
            "unsupported_class_count": 0,
            "unsupported_property_count": 0,
        },
    )
    _write_json(
        root / "reports/stages/ontology_boundary_nasa.json",
        {"metadata": {"experiment_pages_total": 8}},
    )
    _write_json(
        root / "reports/stages/nasa_chunking_summary.json",
        {"metadata": {"strategies": ["structure_aware_large"]}},
    )
    _write_json(
        root / "reports/stages/multisource_retrieval_smoke.json",
        {"metadata": {"status": "smoke_experiment", "labels_total": 25}},
    )
    _write_json(
        root / "data/cqs/nasa_bga_aerodynamics.seed.gold.json",
        {
            "review_status": "llm_or_project_seed_not_expert_certified",
            "labels": [{"cq_id": "nasa-concept-001"}],
        },
    )
    _write_jsonl(
        root / "data/chunks/nasa_bga_aerodynamics.structure_aware_large.jsonl",
        [{"chunk_id": "chunk-1"}, {"chunk_id": "chunk-2"}],
    )
    _write_jsonl(
        root / "data/kg/nasa_bga_aerodynamics.structure_aware_large.kg.jsonl",
        [
            {
                "source_document": "nasa_bga_lift",
                "predicate": "causes",
                "subject": "airflow",
                "object": "lift",
            },
            {
                "source_document": "nasa_bga_drag",
                "predicate": "hasDefinition",
                "subject": "drag",
                "object": "aerodynamic force component",
            },
        ],
    )


def test_bga_domain_transfer_pilot_summarizes_second_source_family(tmp_path: Path) -> None:
    _write_transfer_fixture(tmp_path)

    result = build_nasa_bga_domain_transfer_pilot(repo_root=tmp_path)

    assert result["status"] == "second_domain_transfer_pilot_created"
    assert result["metadata"]["non_atm_source_family"] is True
    assert result["metadata"]["event_centric"] is False
    assert result["metadata"]["human_review"] is False
    assert result["source_snapshot"]["valid_pages"] == 89
    assert result["cq_contract"]["labels_total"] == 50
    assert result["kg_contract"]["chunks_total"] == 2
    assert result["kg_contract"]["triples_total"] == 2
    assert result["kg_contract"]["predicate_counts"] == {
        "causes": 1,
        "hasDefinition": 1,
    }
    statuses = {item["step"]: item["status"] for item in result["contract_coverage"]}
    assert statuses["source_snapshot"] == "satisfied"
    assert statuses["kg_construction_and_validation"] == "satisfied"
    assert statuses["retrieval_or_graphrag_smoke"] == "partial"
    assert "not a full GraphRAG answer-generation ablation" in result["claim_boundary"]


def test_write_bga_domain_transfer_pilot_outputs_reports(tmp_path: Path) -> None:
    _write_transfer_fixture(tmp_path)
    output_dir = tmp_path / "reports/stages"

    json_path, md_path, result = write_nasa_bga_domain_transfer_pilot(
        output_dir=output_dir,
        repo_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["kg_contract"]["evidence_in_source_rate"] == 1.0
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA BGA Domain Transfer Pilot" in markdown
    assert "Artifact Contract Coverage" in markdown
    assert "not human-reviewed" in markdown or "Human review: `False`" in markdown
