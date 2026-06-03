from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report

DEFAULT_REPORT_NAME = "nasa_atmonto_sota_goal_audit"


SOTA_REQUIREMENTS: tuple[dict[str, Any], ...] = (
    {
        "id": "R1",
        "requirement": "Literature-derived SOTA criteria are consolidated.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/agentic_ontology_graphrag_mainline_literature_search.md",
            "reports/stages/sota_comparison_matrix.md",
            "reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md",
        ],
        "limitation": "The mapping is thesis-scoped and should not be treated as a full systematic review.",
    },
    {
        "id": "R2",
        "requirement": "The ATCSCC data source and event-centric extraction target are explicit.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/atcscc_data_format_and_processing_flow.md",
            "reports/stages/atcscc_event_centric_extraction_framing.md",
            "reports/stages/atcscc_source_brief.md",
        ],
        "limitation": "The source family is retrospective ATCSCC advisories, not live operations.",
    },
    {
        "id": "R3",
        "requirement": "NASA ATMONTO is used as an application-profile constraint, not full truth.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/atcscc_ontology_profile_overview.md",
            "data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json",
            "reports/stages/nasa_atmonto_rejection_adjudication.md",
        ],
        "limitation": "Completeness and correctness are profile-relative and CQ-relative.",
    },
    {
        "id": "R4",
        "requirement": "Ontology-guided KG extraction is scored with schema and semantic layers separated.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/nasa_atmonto_formal_experiment_scoring.json",
            "reports/stages/nasa_atmonto_prediction_output_validation.json",
            "reports/stages/nasa_atmonto_cq_evaluation.md",
        ],
        "limitation": "S4 is the current strongest scored extraction system; not all LLM systems perform well.",
    },
    {
        "id": "R5",
        "requirement": "Multi-agent artifact contract is executable enough to drive S5/S6 diagnostics.",
        "status": "mostly_satisfied",
        "evidence": [
            "reports/stages/atcscc_agentic_artifact_contract.md",
            "reports/stages/nasa_atmonto_agentic_loop.md",
            "reports/stages/nasa_atmonto_s5_s6_agentic_loop.md",
        ],
        "limitation": "S5/S6 currently wraps S4 output; it is not yet an autonomous extractor/critic/refiner run.",
    },
    {
        "id": "R6",
        "requirement": "Graph-use gate, token-matched retrieval, and graph health are evaluated.",
        "status": "mostly_satisfied",
        "evidence": [
            "reports/stages/atcscc_graph_use_plan.md",
            "reports/stages/nasa_atmonto_s7_retrieval.md",
            "reports/stages/nasa_atmonto_s7_graph_health.md",
        ],
        "limitation": "Graph health is diagnostic evidence, not certification of semantic truth.",
    },
    {
        "id": "R7",
        "requirement": "Answer generation and failure analysis are source-bounded and reported.",
        "status": "mostly_satisfied",
        "evidence": [
            "reports/stages/nasa_atmonto_s7_answer_generation.md",
            "reports/stages/nasa_atmonto_s7_llm_answer_generation.md",
            "reports/stages/nasa_atmonto_s7_candidate_adjudication.md",
            "reports/stages/nasa_atmonto_s7_profile_decision.md",
        ],
        "limitation": "Broad human/expert answer review remains future work.",
    },
    {
        "id": "R8",
        "requirement": "Completeness, correctness, limitations, and story claims are thesis-ready.",
        "status": "mostly_satisfied",
        "evidence": [
            "reports/stages/current_pipeline_sota_gap_audit.md",
            "reports/stages/thesis_experiment_dashboard.md",
            "reports/stages/nasa_atmonto_experiment_chapter_draft.md",
        ],
        "limitation": "The final thesis should keep the claim wording profile-relative and retrospective.",
    },
    {
        "id": "R9",
        "requirement": "The method can be described as domain-independent and transferable.",
        "status": "partial",
        "evidence": [
            "reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md",
            "templates/agentic_artifact_contract.md",
        ],
        "limitation": "No second-domain transfer run has been executed yet.",
    },
)


def build_nasa_atmonto_sota_goal_audit(
    *,
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(repo_root)
    requirements = [_requirement_status(root, item) for item in SOTA_REQUIREMENTS]
    scoring = read_json_object_or_empty(root / "reports/stages/nasa_atmonto_formal_experiment_scoring.json")
    s5_s6 = read_json_object_or_empty(root / "reports/stages/nasa_atmonto_s5_s6_agentic_loop.json")
    s7_llm = read_json_object_or_empty(root / "reports/stages/nasa_atmonto_s7_llm_answer_generation.json")
    status_counts: dict[str, int] = {}
    for item in requirements:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
    return {
        "source_family": "nasa_atmonto_sota_goal_audit",
        "status": "sota_goal_audit_created",
        "completion_claim": "active_not_complete",
        "metadata": {
            "requirement_count": len(requirements),
            "status_counts": dict(sorted(status_counts.items())),
            "formal_scoring_status": scoring.get("status"),
            "s5_s6_status": s5_s6.get("status"),
            "s7_llm_status": s7_llm.get("status"),
        },
        "requirements": requirements,
        "remaining_blockers": [
            "Independent autonomous S5/S6 extractor/validator/critic/refiner run is not yet scored.",
            "Broad human/expert answer review is not yet complete.",
            "Second-domain transfer is not yet executed.",
        ],
        "claim_safe_summary": (
            "The current project is SOTA-comparable as a layered retrospective ATCSCC "
            "case study, but it is not complete enough for claims of universal GraphRAG "
            "superiority, full ATMONTO coverage, operational readiness, or domain-general "
            "validation."
        ),
    }


def write_nasa_atmonto_sota_goal_audit_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_sota_goal_audit_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO SOTA Goal Completion Audit",
        "",
        "## Completion Claim",
        "",
        f"- Goal status: `{result['completion_claim']}`",
        f"- Requirement count: {result['metadata']['requirement_count']}",
        f"- Status counts: {_format_status_counts(result['metadata']['status_counts'])}",
        f"- Formal scoring status: `{result['metadata']['formal_scoring_status']}`",
        f"- S5/S6 status: `{result['metadata']['s5_s6_status']}`",
        f"- S7 LLM status: `{result['metadata']['s7_llm_status']}`",
        "",
        "## Requirement Evidence",
        "",
        "| ID | Status | Requirement | Evidence coverage | Limitation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in result["requirements"]:
        coverage = f"{item['present_evidence_count']}/{item['evidence_count']}"
        lines.append(
            f"| `{item['id']}` | `{item['status']}` | {item['requirement']} | "
            f"{coverage} | {item['limitation']} |"
        )
    lines.extend(["", "## Evidence Index", ""])
    for item in result["requirements"]:
        lines.append(f"### {item['id']}: {item['requirement']}")
        for entry in item["evidence"]:
            marker = "present" if entry["present"] else "missing"
            lines.append(f"- `{marker}` `{entry['path']}`")
        if item["missing_evidence"]:
            missing = ", ".join(f"`{path}`" for path in item["missing_evidence"])
            lines.append(f"- Missing evidence: {missing}")
        lines.append("")
    lines.extend(["", "## Remaining Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in result["remaining_blockers"])
    lines.extend(["", "## Claim-Safe Summary", "", result["claim_safe_summary"], ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_sota_goal_audit(
    *,
    output_dir: str | Path,
    report_name: str = DEFAULT_REPORT_NAME,
    repo_root: str | Path = PROJECT_ROOT,
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    result = build_nasa_atmonto_sota_goal_audit(repo_root=repo_root)
    json_path = write_nasa_atmonto_sota_goal_audit_json(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_sota_goal_audit_markdown(result, output / f"{report_name}.md")
    return json_path, md_path, result


def _requirement_status(root: Path, item: dict[str, Any]) -> dict[str, Any]:
    evidence = [
        {
            "path": path,
            "present": (root / path).exists(),
        }
        for path in item["evidence"]
    ]
    return {
        **item,
        "evidence": evidence,
        "evidence_count": len(evidence),
        "present_evidence_count": sum(1 for entry in evidence if entry["present"]),
        "missing_evidence": [entry["path"] for entry in evidence if not entry["present"]],
    }


def _format_status_counts(status_counts: dict[str, int]) -> str:
    return ", ".join(f"`{status}`={count}" for status, count in status_counts.items())
