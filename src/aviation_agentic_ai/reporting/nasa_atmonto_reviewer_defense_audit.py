from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report

DEFAULT_REPORT_NAME = "nasa_atmonto_reviewer_defense_audit"

SOTA_AUDIT_PATH = Path("reports/stages/nasa_atmonto_sota_goal_audit.json")
FORMAL_SCORING_PATH = Path("reports/stages/nasa_atmonto_formal_experiment_scoring.json")
S7_RETRIEVAL_PATH = Path("reports/stages/nasa_atmonto_s7_retrieval.json")
S7_LLM_ANSWER_PATH = Path("reports/stages/nasa_atmonto_s7_llm_answer_generation.json")
S7_AUTOMATED_DIAGNOSTIC_PATH = Path(
    "reports/stages/nasa_atmonto_s7_automated_adversarial_review.json"
)

PRIMARY_RETRIEVAL_MODES = (
    "token_matched_live_tfidf_vector",
    "token_matched_dense_embedding_vector",
    "routed_token_matched_live_tfidf_graphrag",
    "routed_token_matched_dense_graphrag",
)


def build_nasa_atmonto_reviewer_defense_audit(
    *,
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(repo_root)
    sota_audit = read_json_object_or_empty(root / SOTA_AUDIT_PATH)
    scoring = read_json_object_or_empty(root / FORMAL_SCORING_PATH)
    retrieval = read_json_object_or_empty(root / S7_RETRIEVAL_PATH)
    llm_answer = read_json_object_or_empty(root / S7_LLM_ANSWER_PATH)
    automated_diagnostic = read_json_object_or_empty(root / S7_AUTOMATED_DIAGNOSTIC_PATH)

    metadata = _metadata(
        root=root,
        sota_audit=sota_audit,
        scoring=scoring,
        retrieval=retrieval,
        llm_answer=llm_answer,
        automated_diagnostic=automated_diagnostic,
    )
    findings = _reviewer_findings(metadata)
    return {
        "source_family": "nasa_atmonto_reviewer_defense_audit",
        "status": "reviewer_defense_audit_created",
        "metadata": metadata,
        "reviewer_findings": findings,
        "safe_thesis_claim": (
            "This thesis presents a retrospective, source-bounded study of "
            "schema-constrained Agentic KG-RAG for FAA ATCSCC advisories. A "
            "lightweight NASA ATMONTO-derived application schema constrains advisory "
            "event extraction; the research contribution is evidence-linked event "
            "extraction, agentic validation/refinement, and source-bounded KG-RAG "
            "evaluation. The strongest claims are structural schema conformance, "
            "evidence traceability, benchmark-specific retrieval and answer "
            "diagnostics, and failure-boundary analysis. Automated consistency "
            "diagnostics are an internal error-discovery layer, not human review, "
            "expert certification, domain-general proof, or operational aviation "
            "validation."
        ),
    }


def write_nasa_atmonto_reviewer_defense_audit_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_reviewer_defense_audit_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = result["metadata"]
    lines = [
        "# NASA ATMONTO Reviewer Defense Audit",
        "",
        "## Scope",
        "",
        (
            "This report converts the parallel reviewer-style audit into explicit "
            "claim gates and defensive experiment/report improvements."
        ),
        "",
        f"- SOTA audit status: `{metadata['sota_audit_status']}`",
        f"- Completion claim: `{metadata['completion_claim']}`",
        f"- Completion scope: `{metadata['completion_scope']}`",
        f"- Internal diagnostic gate passed: `{metadata['internal_diagnostic_gate_passed']}`",
        f"- Human answer review completed: `{metadata['human_answer_review_completed']}`",
        f"- Expert certification completed: `{metadata['expert_certification_completed']}`",
        f"- S7 retrieval labels: {metadata['retrieval_case_count']}",
        f"- S7 LLM selected cases: {metadata['s7_llm_selected_case_count']}",
        f"- S7 LLM cases per template/mode: {metadata['s7_llm_max_cases_per_template']}",
        f"- Automated diagnostic cases: {metadata['automated_diagnostic_case_count']}",
        "",
        "## Main Guardrail",
        "",
        result["safe_thesis_claim"],
        "",
        "## Claim Scope Gates",
        "",
        "| Scope | Passed | Status | Blocked by |",
        "| --- | --- | --- | --- |",
    ]
    for gate in metadata["claim_scope_gates"]:
        blocked_by = ", ".join(gate["blocked_by"]) if gate["blocked_by"] else "none"
        lines.append(
            f"| `{gate['id']}` | `{gate['passed']}` | {gate['status']} | {blocked_by} |"
        )
    lines.extend(
        [
            "",
            "## Formal KG Extraction Snapshot",
            "",
            "| System | Accepted facts | Rejected facts | Precision | Recall | F1 | Structural acceptance |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for system in metadata["formal_systems"]:
        lines.append(
            f"| `{system['system_id']}` | {system['accepted_fact_count']} | "
            f"{system['rejected_fact_count']} | {_display(system['precision'])} | "
            f"{_display(system['recall'])} | {_display(system['f1'])} | "
            f"{_display(system['structural_acceptance_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## Retrieval And Answer Diagnostic Snapshot",
            "",
            "| Mode | Source | Cases | Answer F1 | Answer correctness | Citation recall | Target hit | Context tokens |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode in metadata["retrieval_modes"]:
        lines.append(
            f"| `{mode['mode']}` | retrieval | {mode['cases']} | "
            f"{_display(mode['answer_micro_f1'])} | n/a | n/a | "
            f"{_display(mode['target_source_hit_rate'])} | {_display(mode['avg_context_tokens'])} |"
        )
    for mode in metadata["answer_modes"]:
        lines.append(
            f"| `{mode['mode']}` | LLM selected sample | {mode['cases']} | n/a | "
            f"{_display(mode['answer_correctness'])} | {_display(mode['citation_recall'])} | "
            f"n/a | {_display(mode['avg_context_tokens'])} |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Findings And Defensive Improvements",
            "",
            "| ID | Severity | Reviewer angle | Risk | Defensive action | Claim boundary |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for finding in result["reviewer_findings"]:
        lines.append(
            f"| `{finding['id']}` | `{finding['severity']}` | {finding['reviewer_angle']} | "
            f"{finding['risk']} | {finding['defensive_improvement']} | "
            f"{finding['claim_boundary']} |"
        )
    lines.extend(
        [
            "",
            "## No-Go Claims",
            "",
            "- Do not treat the lightweight ATCSCC application schema as a complete aviation ontology.",
            "- Do not claim that automated diagnostics replace human or expert answer review.",
            "- Do not claim operational FAA/ATC decision-support readiness.",
            "- Do not claim domain-general validation from the bounded ATCSCC plus NASA BGA pilot.",
            "- Do not collapse schema conformance into semantic correctness.",
            "- Do not present selected 60-case LLM diagnostics as the full 317-label answer benchmark.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_reviewer_defense_audit(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = DEFAULT_REPORT_NAME,
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    result = build_nasa_atmonto_reviewer_defense_audit(repo_root=repo_root)
    json_path = write_nasa_atmonto_reviewer_defense_audit_json(
        result,
        output / f"{report_name}.json",
    )
    md_path = write_nasa_atmonto_reviewer_defense_audit_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result


def _metadata(
    *,
    root: Path,
    sota_audit: dict[str, Any],
    scoring: dict[str, Any],
    retrieval: dict[str, Any],
    llm_answer: dict[str, Any],
    automated_diagnostic: dict[str, Any],
) -> dict[str, Any]:
    sota_metadata = sota_audit.get("metadata", {}) if isinstance(sota_audit, dict) else {}
    retrieval_metadata = retrieval.get("metadata", {})
    llm_metadata = llm_answer.get("metadata", {})
    automated_metadata = automated_diagnostic.get("metadata", {})
    return {
        "sota_audit_path": project_relative_path(root / SOTA_AUDIT_PATH, root),
        "sota_audit_status": sota_audit.get("status"),
        "completion_claim": sota_audit.get("completion_claim"),
        "completion_scope": sota_metadata.get("s7_completion_scope"),
        "internal_diagnostic_gate_passed": sota_audit.get("completion_gate", {}).get(
            "passed"
        ),
        "claim_scope_gates": sota_audit.get("claim_scope_gates", []),
        "human_answer_review_completed": sota_metadata.get(
            "s7_human_answer_review_completed"
        ),
        "expert_certification_completed": sota_metadata.get(
            "s7_expert_certification_completed"
        ),
        "formal_scoring_status": scoring.get("status"),
        "gold_record_count": scoring.get("gold_status", {}).get("record_count"),
        "formal_systems": _formal_systems(scoring),
        "retrieval_status": retrieval.get("status"),
        "retrieval_case_count": retrieval_metadata.get("retrieval_case_count"),
        "retrieval_modes": _retrieval_modes(retrieval),
        "s7_llm_status": llm_answer.get("status"),
        "s7_llm_selected_case_count": llm_metadata.get("selected_case_count"),
        "s7_llm_max_cases_per_template": llm_metadata.get("max_cases_per_template"),
        "s7_llm_model": llm_metadata.get("reviewer_model"),
        "answer_modes": _answer_modes(llm_answer),
        "automated_diagnostic_status": automated_diagnostic.get("status"),
        "automated_diagnostic_case_count": automated_metadata.get("reviewed_case_count"),
        "automated_diagnostic_accepted_case_count": automated_metadata.get(
            "accepted_case_count"
        ),
        "automated_diagnostic_rejected_case_count": automated_metadata.get(
            "rejected_case_count"
        ),
    }


def _formal_systems(scoring: dict[str, Any]) -> list[dict[str, Any]]:
    systems = scoring.get("systems", [])
    if not isinstance(systems, list):
        return []
    selected = {
        "S2_llm_schema_slice",
        "S3_llm_schema_slice_validator_repair",
        "S4_hybrid_backbone_enrichment",
    }
    return [_system_summary(system) for system in systems if system.get("system_id") in selected]


def _system_summary(system: dict[str, Any]) -> dict[str, Any]:
    structural = system.get("structural_metrics", {})
    semantic = system.get("semantic_metrics", {})
    return {
        "system_id": system.get("system_id"),
        "accepted_fact_count": structural.get("accepted_fact_count"),
        "rejected_fact_count": structural.get("rejected_fact_count"),
        "structural_acceptance_rate": structural.get("structural_acceptance_rate"),
        "precision": semantic.get("precision"),
        "recall": semantic.get("recall"),
        "f1": semantic.get("f1"),
    }


def _retrieval_modes(retrieval: dict[str, Any]) -> list[dict[str, Any]]:
    aggregate = retrieval.get("aggregate_by_mode", {})
    result = []
    for mode in PRIMARY_RETRIEVAL_MODES:
        metrics = aggregate.get(mode, {})
        answer_set = metrics.get("answer_set", {})
        result.append(
            {
                "mode": mode,
                "cases": retrieval.get("metadata", {}).get("retrieval_case_count"),
                "answer_micro_f1": answer_set.get("micro_f1"),
                "target_source_hit_rate": metrics.get("target_source_hit_rate"),
                "avg_context_tokens": metrics.get("avg_estimated_context_tokens"),
            }
        )
    return result


def _answer_modes(llm_answer: dict[str, Any]) -> list[dict[str, Any]]:
    aggregate = llm_answer.get("answer_quality", {}).get("aggregate_by_mode", {})
    return [
        {
            "mode": mode,
            "cases": metrics.get("selected_total"),
            "answer_correctness": metrics.get("answer_correctness"),
            "citation_recall": metrics.get("citation_recall"),
            "evidence_faithfulness": metrics.get("evidence_faithfulness"),
            "unsupported_claim_rate": metrics.get("unsupported_claim_rate"),
            "avg_context_tokens": metrics.get("avg_estimated_context_tokens"),
        }
        for mode, metrics in sorted(aggregate.items())
    ]


def _reviewer_findings(metadata: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "id": "D1",
            "severity": "high",
            "reviewer_angle": "methodology / claim gate",
            "risk": "Automated checks may be mistaken for human answer review.",
            "defensive_improvement": (
                "Split completion into internal diagnostic, human review, expert "
                "certification, and operational scopes."
            ),
            "claim_boundary": f"Current scope is `{metadata['completion_scope']}`.",
        },
        {
            "id": "D2",
            "severity": "high",
            "reviewer_angle": "GraphRAG answer evaluation",
            "risk": "The selected 60-case LLM sample can be overread as the full S7 benchmark.",
            "defensive_improvement": (
                "Report 317 retrieval labels separately from the selected 60-case "
                "LLM diagnostic, with per-mode sample counts."
            ),
            "claim_boundary": "LLM metrics are selected-sample diagnostics, not full-label coverage.",
        },
        {
            "id": "D3",
            "severity": "high",
            "reviewer_angle": "schema-guided event extraction / KG evidence",
            "risk": "Schema conformance can be conflated with semantic correctness.",
            "defensive_improvement": (
                "Keep structural acceptance, semantic precision/recall/F1, and evidence "
                "support as separate columns."
            ),
            "claim_boundary": "Schema validity is not equivalent to domain truth.",
        },
        {
            "id": "D4",
            "severity": "medium",
            "reviewer_angle": "citation and evidence support",
            "risk": "Citation precision alone hides incomplete evidence coverage.",
            "defensive_improvement": (
                "Report citation recall and describe future span-level adequacy checks."
            ),
            "claim_boundary": "Citation validity does not prove full source-span support.",
        },
        {
            "id": "D5",
            "severity": "medium",
            "reviewer_angle": "baseline fairness",
            "risk": "GraphRAG gains may depend on route, top-k, or token budget choices.",
            "defensive_improvement": (
                "Separate primary token-matched comparisons from diagnostic dense/vector "
                "sensitivity modes."
            ),
            "claim_boundary": "Results support source-bounded routed GraphRAG diagnostics.",
        },
        {
            "id": "D6",
            "severity": "medium",
            "reviewer_angle": "reproducibility",
            "risk": "LLM provider, prompt, and selected-case provenance can be underspecified.",
            "defensive_improvement": (
                "Surface model, sample counts, prompt boundary, and required regeneration "
                "artifacts in the report."
            ),
            "claim_boundary": "Reproducibility is artifact-level unless raw provider traces are added.",
        },
    ]


def _display(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)
