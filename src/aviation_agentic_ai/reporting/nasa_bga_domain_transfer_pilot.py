from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report

DEFAULT_REPORT_NAME = "nasa_bga_domain_transfer_pilot"

SOURCE_INGESTION_REPORT = Path("reports/stages/nasa_source_ingestion.json")
BENCHMARK_REPORT = Path("reports/stages/nasa_benchmark_summary.json")
KG_VALIDATION_REPORT = Path("reports/stages/nasa_kg_validation.json")
ONTOLOGY_BOUNDARY_REPORT = Path("reports/stages/ontology_boundary_nasa.json")
CHUNKING_REPORT = Path("reports/stages/nasa_chunking_summary.json")
MULTISOURCE_SMOKE_REPORT = Path("reports/stages/multisource_retrieval_smoke.json")
CQ_SEED_PATH = Path("data/cqs/nasa_bga_aerodynamics.seed.gold.json")
CHUNKS_PATH = Path("data/chunks/nasa_bga_aerodynamics.structure_aware_large.jsonl")
KG_PATH = Path("data/kg/nasa_bga_aerodynamics.structure_aware_large.kg.jsonl")


def build_nasa_bga_domain_transfer_pilot(
    *,
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_ingestion = read_json_object_or_empty(root / SOURCE_INGESTION_REPORT)
    benchmark = read_json_object_or_empty(root / BENCHMARK_REPORT)
    kg_validation = read_json_object_or_empty(root / KG_VALIDATION_REPORT)
    ontology_boundary = read_json_object_or_empty(root / ONTOLOGY_BOUNDARY_REPORT)
    chunking = read_json_object_or_empty(root / CHUNKING_REPORT)
    multisource_smoke = read_json_object_or_empty(root / MULTISOURCE_SMOKE_REPORT)
    cq_seed = read_json_object_or_empty(root / CQ_SEED_PATH)
    kg_records = _read_jsonl(root / KG_PATH)
    chunk_count = _count_jsonl(root / CHUNKS_PATH)
    labels = cq_seed.get("labels", []) if isinstance(cq_seed.get("labels"), list) else []
    label_distribution = (
        benchmark.get("label_distribution")
        if isinstance(benchmark.get("label_distribution"), dict)
        else cq_seed.get("label_distribution", {})
    )
    contract_coverage = _contract_coverage(
        root,
        source_ingestion,
        benchmark,
        kg_validation,
        ontology_boundary,
        chunking,
        multisource_smoke,
        labels,
        chunk_count,
        kg_records,
    )
    return {
        "source_family": "nasa_bga_aerodynamics",
        "status": "second_domain_transfer_pilot_created",
        "metadata": {
            "transfer_domain": "NASA Beginner's Guide to Aerodynamics",
            "transfer_type": "second_source_family_non_atm_reference_pilot",
            "source_type": source_ingestion.get("metadata", {}).get(
                "source_type",
                "nasa_web_educational_page",
            ),
            "source_authority": source_ingestion.get("metadata", {}).get(
                "source_authority",
                "NASA Glenn Research Center",
            ),
            "non_atm_source_family": True,
            "event_centric": False,
            "concept_centric_reference_domain": True,
            "human_review": False,
            "external_aviation_expert_certified": False,
            "operational_readiness_claimed": False,
        },
        "source_snapshot": {
            "pages_total": source_ingestion.get("metadata", {}).get("pages_total"),
            "valid_pages": source_ingestion.get("metadata", {}).get("valid_pages"),
            "invalid_pages": source_ingestion.get("metadata", {}).get("invalid_pages"),
            "experiment_subset_pages": ontology_boundary.get("metadata", {}).get(
                "experiment_pages_total"
            ),
            "source_report": project_relative_path(root / SOURCE_INGESTION_REPORT, root),
        },
        "cq_contract": {
            "labels_total": benchmark.get("metadata", {}).get(
                "labels_total",
                len(labels),
            ),
            "supported_total": benchmark.get("metadata", {}).get("supported_total"),
            "no_answer_total": benchmark.get("metadata", {}).get("no_answer_total"),
            "label_distribution": label_distribution,
            "review_status": benchmark.get("metadata", {}).get(
                "review_status",
                cq_seed.get("review_status"),
            ),
            "seed_path": project_relative_path(root / CQ_SEED_PATH, root),
        },
        "kg_contract": {
            "chunks_total": chunk_count,
            "triples_total": kg_validation.get("triples_total", len(kg_records)),
            "valid_triples": kg_validation.get("valid_triples"),
            "errors_total": kg_validation.get("errors_total"),
            "evidence_in_source_rate": kg_validation.get("evidence_in_source_rate"),
            "provenance_completeness": kg_validation.get("provenance_completeness"),
            "rejected_triple_count": kg_validation.get("rejected_triple_count"),
            "unsupported_class_count": kg_validation.get("unsupported_class_count"),
            "unsupported_property_count": kg_validation.get("unsupported_property_count"),
            "predicate_counts": dict(
                sorted(Counter(str(item.get("predicate") or "") for item in kg_records).items())
            ),
            "source_documents_with_triples": len(
                {str(item.get("source_document") or "") for item in kg_records}
            ),
            "kg_path": project_relative_path(root / KG_PATH, root),
        },
        "contract_coverage": contract_coverage,
        "transfer_interpretation": _transfer_interpretation(contract_coverage),
        "claim_boundary": (
            "This pilot shows that the artifact contract can be applied to a second "
            "NASA source family with source, CQ, chunking, KG, and validation artifacts. "
            "It is not a second event-centric operational domain, not human-reviewed, "
            "and not a full GraphRAG answer-generation ablation."
        ),
        "next_actions": [
            "Add reviewed answer labels if this reference-domain pilot becomes a thesis chapter.",
            "Run retrieval and answer-generation ablations only after the seed labels are reviewed.",
            "Use a truly non-aviation event source for stronger domain-general claims.",
        ],
    }


def write_nasa_bga_domain_transfer_pilot_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_bga_domain_transfer_pilot_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA BGA Domain Transfer Pilot",
        "",
        "## Boundary",
        "",
        result["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Status: `{result['status']}`",
        f"- Transfer domain: {result['metadata']['transfer_domain']}",
        f"- Source type: `{result['metadata']['source_type']}`",
        f"- Non-ATM source family: `{result['metadata']['non_atm_source_family']}`",
        f"- Event-centric: `{result['metadata']['event_centric']}`",
        f"- Human review: `{result['metadata']['human_review']}`",
        "",
        "## Source Snapshot",
        "",
        f"- Pages total: {result['source_snapshot']['pages_total']}",
        f"- Valid pages: {result['source_snapshot']['valid_pages']}",
        f"- Experiment subset pages: {result['source_snapshot']['experiment_subset_pages']}",
        "",
        "## CQ and KG Contract",
        "",
        f"- CQ labels: {result['cq_contract']['labels_total']}",
        f"- Supported labels: {result['cq_contract']['supported_total']}",
        f"- No-answer labels: {result['cq_contract']['no_answer_total']}",
        f"- Label distribution: `{result['cq_contract']['label_distribution']}`",
        f"- Chunks: {result['kg_contract']['chunks_total']}",
        f"- Triples: {result['kg_contract']['triples_total']}",
        f"- Valid triples: {result['kg_contract']['valid_triples']}",
        f"- KG errors: {result['kg_contract']['errors_total']}",
        f"- Evidence-in-source rate: {result['kg_contract']['evidence_in_source_rate']}",
        f"- Provenance completeness: {result['kg_contract']['provenance_completeness']}",
        "",
        "## Artifact Contract Coverage",
        "",
        "| Step | Status | Evidence | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for item in result["contract_coverage"]:
        evidence = "<br>".join(f"`{path}`" for path in item["evidence"])
        lines.append(
            f"| {item['step']} | `{item['status']}` | {evidence} | {item['limitation']} |"
        )
    lines.extend(
        [
            "",
            "## Transfer Interpretation",
            "",
        ]
    )
    for item in result["transfer_interpretation"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in result["next_actions"])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_bga_domain_transfer_pilot(
    *,
    output_dir: str | Path,
    report_name: str = DEFAULT_REPORT_NAME,
    repo_root: str | Path = PROJECT_ROOT,
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    result = build_nasa_bga_domain_transfer_pilot(repo_root=repo_root)
    json_path = write_nasa_bga_domain_transfer_pilot_json(
        result,
        output / f"{report_name}.json",
    )
    md_path = write_nasa_bga_domain_transfer_pilot_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result


def _contract_coverage(
    root: Path,
    source_ingestion: dict[str, Any],
    benchmark: dict[str, Any],
    kg_validation: dict[str, Any],
    ontology_boundary: dict[str, Any],
    chunking: dict[str, Any],
    multisource_smoke: dict[str, Any],
    labels: list[Any],
    chunk_count: int,
    kg_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "step": "source_snapshot",
            "status": _status(
                (root / SOURCE_INGESTION_REPORT).exists()
                and int(source_ingestion.get("metadata", {}).get("valid_pages") or 0) > 0
            ),
            "evidence": [project_relative_path(root / SOURCE_INGESTION_REPORT, root)],
            "limitation": "educational NASA pages, not operational event advisories",
        },
        {
            "step": "ontology_profile_boundary",
            "status": _status((root / ONTOLOGY_BOUNDARY_REPORT).exists()),
            "evidence": [project_relative_path(root / ONTOLOGY_BOUNDARY_REPORT, root)],
            "limitation": "uses an existing curated aviation profile, not a new reviewed domain ontology",
        },
        {
            "step": "competency_question_contract",
            "status": _status(
                (root / CQ_SEED_PATH).exists()
                and int(benchmark.get("metadata", {}).get("labels_total") or len(labels)) > 0
            ),
            "evidence": [
                project_relative_path(root / CQ_SEED_PATH, root),
                project_relative_path(root / BENCHMARK_REPORT, root),
            ],
            "limitation": "seed labels are project/LLM generated and not human reviewed",
        },
        {
            "step": "chunking_and_indexable_units",
            "status": _status((root / CHUNKS_PATH).exists() and chunk_count > 0),
            "evidence": [
                project_relative_path(root / CHUNKS_PATH, root),
                project_relative_path(root / CHUNKING_REPORT, root),
            ],
            "limitation": "chunking is diagnostic and not optimized for this second domain",
        },
        {
            "step": "kg_construction_and_validation",
            "status": _status(
                (root / KG_PATH).exists()
                and bool(kg_records)
                and int(kg_validation.get("errors_total") or 0) == 0
            ),
            "evidence": [
                project_relative_path(root / KG_PATH, root),
                project_relative_path(root / KG_VALIDATION_REPORT, root),
            ],
            "limitation": "schema-valid triples do not prove semantic correctness",
        },
        {
            "step": "retrieval_or_graphrag_smoke",
            "status": "partial" if (root / MULTISOURCE_SMOKE_REPORT).exists() else "missing",
            "evidence": [project_relative_path(root / MULTISOURCE_SMOKE_REPORT, root)],
            "limitation": "retrieval smoke exists, but S7-style answer-generation ablations are not run",
        },
    ]


def _transfer_interpretation(contract_coverage: list[dict[str, Any]]) -> list[str]:
    satisfied = sum(1 for item in contract_coverage if item["status"] == "satisfied")
    partial = sum(1 for item in contract_coverage if item["status"] == "partial")
    missing = sum(1 for item in contract_coverage if item["status"] == "missing")
    return [
        (
            f"Artifact contract coverage: {satisfied} satisfied, {partial} partial, "
            f"{missing} missing."
        ),
        (
            "The transfer evidence is sufficient to replace the previous 'no second-domain "
            "run' gap with a bounded source-family transfer pilot."
        ),
        (
            "The evidence is not sufficient for a broad domain-general GraphRAG claim because "
            "the pilot is concept-centric, seed-labelled, and lacks full answer-generation ablations."
        ),
    ]


def _status(condition: bool) -> str:
    return "satisfied" if condition else "missing"


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                records.append(payload)
    return records
