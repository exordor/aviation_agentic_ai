from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import write_json_report


REVISED_THESIS_CLAIM = (
    "This thesis investigates a retrospective and source-bounded claim: for FAA "
    "ATCSCC advisories, a lightweight NASA ATMONTO-derived application schema "
    "can constrain LLM extraction of advisory events, support agentic "
    "validation/refinement, and provide an inspectable advisory event graph for "
    "KG-RAG question answering. The system is evaluated with layered metrics: "
    "schema-valid extraction, evidence-linked relation correctness on reviewed "
    "subsets, repair/critic behavior, retrieval and answer quality, citation "
    "quality, and failure/human-review boundaries are reported separately."
)

RESEARCH_QUESTIONS = [
    {
        "id": "RQ1",
        "question": (
            "Can schema-constrained LLM extraction produce valid and evidence-linked "
            "event records from ATCSCC advisories?"
        ),
    },
    {
        "id": "RQ2",
        "question": (
            "Does an agentic validation-refinement loop reduce schema violations and "
            "unsupported relations?"
        ),
    },
    {
        "id": "RQ3",
        "question": (
            "Does KG-RAG improve evidence grounding and citation quality compared "
            "with vector-only RAG?"
        ),
    },
    {
        "id": "RQ4",
        "question": (
            "What failure types remain, and where does human review remain necessary?"
        ),
    },
]

HYPOTHESES = [
    {
        "id": "H1",
        "hypothesis": (
            "Schema constraints increase valid, evidence-linked advisory event records "
            "compared with unconstrained or weakly constrained extraction."
        ),
    },
    {
        "id": "H2",
        "hypothesis": (
            "A validator/refiner/critic loop reduces schema violations, unsupported "
            "relations, and parser artifacts before graph insertion."
        ),
    },
    {
        "id": "H3",
        "hypothesis": (
            "KG-RAG improves source-bounded grounding, answer-set quality, and citation "
            "behavior on relation-oriented ATCSCC questions, while vector-only "
            "retrieval can remain sufficient for simple source-local questions."
        ),
    },
    {
        "id": "H4",
        "hypothesis": (
            "Failure analysis can separate extraction errors, profile/gold-boundary "
            "gaps, retrieval context errors, answer overreach, and cases requiring "
            "human review."
        ),
    },
]

CONTRIBUTIONS = [
    "A lightweight ATCSCC application schema/profile derived from NASA ATMONTO terms and restricted to advisory-event extraction.",
    "An advisory event graph with source IDs and evidence spans for extracted facts.",
    "An agentic extraction loop with extractor, validator, refiner, and critic roles that records repair and rejection outcomes.",
    "A reproducible vector, graph, and hybrid KG-RAG evaluation pipeline over retrospective ATCSCC advisories.",
    "A layered evaluation and claim-boundary protocol that separates schema validity, evidence support, answer quality, and human-review requirements.",
]

EVALUATION_LAYERS = [
    {
        "layer": "Schema-constrained extraction",
        "metrics": [
            "schema validity",
            "structural acceptance rate",
            "rejected fact count",
            "repaired fact count",
        ],
        "purpose": "Measure whether generated event records obey the application schema before graph insertion.",
    },
    {
        "layer": "Evidence support",
        "metrics": [
            "evidence-span coverage",
            "unsupported relation rate",
            "provenance completeness",
            "reviewed-subset precision/recall/F1",
        ],
        "purpose": "Measure whether accepted facts can be traced to advisory text.",
    },
    {
        "layer": "Agentic loop behavior",
        "metrics": [
            "violation reduction",
            "repair success",
            "critic rejection count",
            "post-loop extraction F1",
        ],
        "purpose": "Measure whether validation/refinement improves extraction quality.",
    },
    {
        "layer": "Retrieval and KG-RAG answer quality",
        "metrics": [
            "answer-set F1",
            "target-source hit rate",
            "citation precision/recall",
            "evidence faithfulness",
        ],
        "purpose": "Measure whether vector, graph, and hybrid modes support grounded answers.",
    },
    {
        "layer": "Failure and human-review boundary",
        "metrics": [
            "failure category counts",
            "abstention correctness",
            "profile/gold-boundary cases",
            "human-review completion status",
        ],
        "purpose": "Measure what remains unresolved and which claims require review.",
    },
]

CLAIM_SAFETY_MATRIX = [
    {
        "claim": "Lightweight schema constrains advisory event extraction.",
        "current_evidence": (
            "ATCSCC profile terms, schema validation, and prediction-output "
            "validation reports constrain accepted event fields."
        ),
        "supported_strength": "strong",
        "safe_wording": (
            "The application schema constrains which advisory event fields and "
            "relations can enter the graph."
        ),
        "unsafe_wording_to_avoid": "The ontology fully models aviation knowledge.",
        "evidence_files": [
            "reports/stages/atcscc_ontology_profile_overview.md",
            "data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json",
            "reports/stages/nasa_atmonto_prediction_output_validation.json",
            "reports/stages/nasa_atmonto_formal_experiment_scoring.json",
        ],
    },
    {
        "claim": "Accepted facts preserve provenance.",
        "current_evidence": "KG and prediction validation reports check source IDs and evidence spans.",
        "supported_strength": "strong",
        "safe_wording": (
            "Accepted facts carry source-bounded provenance checked by deterministic "
            "validation."
        ),
        "unsafe_wording_to_avoid": "Every KG triple is semantically correct.",
        "evidence_files": [
            "reports/stages/nasa_atmonto_prediction_output_validation.json",
            "reports/stages/nasa_atmonto_formal_experiment_scoring.json",
            "reports/stages/nasa_atmonto_cq_evaluation.json",
        ],
    },
    {
        "claim": "Agentic validation improves extraction quality.",
        "current_evidence": "S5/S6 reports record validator, refiner, critic, repair, and rejection behavior.",
        "supported_strength": "moderate",
        "safe_wording": (
            "The agentic loop reduces specific schema and support failures in the "
            "current ATCSCC pipeline."
        ),
        "unsafe_wording_to_avoid": "Autonomous agents construct a correct ontology.",
        "evidence_files": [
            "reports/stages/nasa_atmonto_s5_s6_agentic_loop.json",
            "reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.json",
            "reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.json",
            "reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.json",
        ],
    },
    {
        "claim": "KG-RAG improves grounded ATCSCC QA diagnostics.",
        "current_evidence": (
            "S7 retrieval, graph-health, and LLM answer-generation diagnostics report "
            "answer-set, citation, and target-source metrics."
        ),
        "supported_strength": "moderate",
        "safe_wording": (
            "KG-RAG improves some source-bounded grounding diagnostics on this "
            "benchmark."
        ),
        "unsafe_wording_to_avoid": "GraphRAG is always more accurate than vector retrieval.",
        "evidence_files": [
            "reports/stages/nasa_atmonto_s7_retrieval.json",
            "reports/stages/nasa_atmonto_s7_graph_health.json",
            "reports/stages/nasa_atmonto_s7_llm_answer_generation.json",
        ],
    },
    {
        "claim": "GraphRAG universally improves retrieval.",
        "current_evidence": (
            "S7 reports vector, graph, and routed modes separately; graph use is "
            "template-dependent."
        ),
        "supported_strength": "not supported",
        "safe_wording": (
            "KG-RAG should be reported as a source-bounded grounding and evidence "
            "diagnostic, not a universal Recall@k improvement."
        ),
        "unsafe_wording_to_avoid": "GraphRAG always improves Recall@k.",
        "evidence_files": [
            "reports/stages/nasa_atmonto_s7_retrieval.json",
            "reports/stages/nasa_atmonto_s7_graph_health.json",
        ],
    },
    {
        "claim": "The system can answer operational ATC questions.",
        "current_evidence": "The advisory boundary limits the system to retrospective research diagnostics.",
        "supported_strength": "not supported",
        "safe_wording": (
            "The system analyzes retrospective advisories and must not be used for "
            "live operational decisions."
        ),
        "unsafe_wording_to_avoid": "The system can support operational flight or ATC decisions.",
        "evidence_files": [
            "src/aviation_agentic_ai/advisory.py",
            "reports/stages/nasa_atmonto_reviewer_defense_audit.json",
        ],
    },
    {
        "claim": "Automated diagnostics replace human review.",
        "current_evidence": "Reviewer-defense and SOTA audits keep automated diagnostics separate from human review.",
        "supported_strength": "not supported",
        "safe_wording": (
            "Automated diagnostics are internal error-discovery tools and do not "
            "replace human or expert review."
        ),
        "unsafe_wording_to_avoid": "The benchmark is human reviewed or expert certified.",
        "evidence_files": [
            "reports/stages/nasa_atmonto_sota_goal_audit.json",
            "reports/stages/nasa_atmonto_reviewer_defense_audit.json",
            "reports/stages/nasa_atmonto_s7_automated_adversarial_review.json",
        ],
    },
    {
        "claim": "The benchmark is externally aviation-expert certified.",
        "current_evidence": (
            "Current labels and diagnostics are project/thesis evidence with documented "
            "review gaps."
        ),
        "supported_strength": "not supported",
        "safe_wording": (
            "The benchmark is thesis-oriented and source-bounded, with explicit review "
            "limitations."
        ),
        "unsafe_wording_to_avoid": "The benchmark is externally aviation-expert certified.",
        "evidence_files": [
            "reports/stages/nasa_atmonto_s7_answer_review_decisions.json",
            "reports/stages/nasa_atmonto_reviewer_defense_audit.json",
        ],
    },
    {
        "claim": "The method is domain-general.",
        "current_evidence": "A bounded second-source-family pilot exists, but it is not a full cross-domain benchmark.",
        "supported_strength": "weak",
        "safe_wording": (
            "The method is designed to be domain-adaptable, with only pilot-level "
            "transfer evidence so far."
        ),
        "unsafe_wording_to_avoid": "The method is proven domain-general.",
        "evidence_files": [
            "reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md",
            "reports/stages/nasa_bga_domain_transfer_pilot.json",
        ],
    },
]

EVIDENCE_GAPS = [
    "Need final reviewed subset for triple-level and answer-level correctness",
    "Need explicit comparison against a naive/unconstrained extraction baseline",
    "Need clearer reporting of repair success and rejection reasons across the agentic loop",
    "Need final failure taxonomy with examples and claim impact",
    "Need optional second-domain pilot evidence only as transfer evidence, not as proof of domain-general validity",
]

DEFAULT_SCAN_PATHS = (
    "README.md",
    "GOALS.md",
    "reports/final/project_report.md",
    "reports/final/project_academic_report.md",
    "reports/final/project_defense_notes.md",
)

_SAFE_CONTEXT_MARKERS = (
    "do not",
    "does not",
    "must not",
    "should not",
    "not claim",
    "not supported",
    "not external",
    "not an external",
    "not certified",
    "not human",
    "human review is absent",
    "not expert",
    "no human",
    "no external",
    "false",
    "kept out",
    "not operational",
    "not a replacement",
    "not that",
    "rather than",
    "avoid",
    "cannot",
    "never",
    "no evidence",
    "without claiming",
)

_UNSAFE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "graphrag_universal_recall",
        re.compile(
            r"\bgraphrag\b.{0,60}\b(always|universally|guarantees?)\b"
            r".{0,60}\b(improves?|beats?|outperforms?)\b.{0,40}\brecall\b"
            r"|\bgraphrag\b.{0,40}\brecall\b.{0,60}"
            r"\b(always|universally|guaranteed)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "hybrid_always_beats_vector",
        re.compile(
            r"\bhybrid(?: rag)?\b.{0,60}\b(always|universally)\b.{0,60}"
            r"\b(beats?|outperforms?|improves over)\b.{0,40}\bvector(?:-only)?\b"
            r"|\bhybrid(?: rag)?\b.{0,60}\b(beats?|outperforms?)\b.{0,40}"
            r"\bvector(?:-only)?\b.{0,40}\b(always|universally)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "certified_aviation_qa_system",
        re.compile(
            r"\bcertified\b.{0,30}\baviation\b.{0,30}\bqa system\b"
            r"|\baviation\b.{0,30}\bqa system\b.{0,30}\bcertified\b",
            re.IGNORECASE,
        ),
    ),
    (
        "replace_poh",
        re.compile(
            r"\b(replace|replaces|replacement for)\b.{0,30}\b(poh|pilot operating handbook)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "replace_atc",
        re.compile(
            r"\b(replace|replaces|replacement for)\b.{0,30}\b(atc|air traffic control)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "operational_flight_decision",
        re.compile(
            r"\boperational flight decisions?\b|\boperationally safe\b|\bproduction cockpit\b",
            re.IGNORECASE,
        ),
    ),
    (
        "complete_aviation_ontology",
        re.compile(
            r"\b(complete|comprehensive|full)\b.{0,30}\baviation ontology\b",
            re.IGNORECASE,
        ),
    ),
    (
        "externally_certified_benchmark",
        re.compile(
            r"\b(externally|expert)\b.{0,40}\b(certified|validated)\b.{0,40}"
            r"\b(benchmark|gold|labels?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "human_review_claim",
        re.compile(r"\b(human|manual)\s+review(?:ed)?\b|\bmanual[- ]reviewed\b", re.IGNORECASE),
    ),
    (
        "expert_review_claim",
        re.compile(
            r"\bexpert\s+review(?:ed)?\b|\bexpert\s+gold\b|\baviation\s+expert\s+validated\b",
            re.IGNORECASE,
        ),
    ),
    (
        "certification_claim",
        re.compile(r"\bcertified\b|\bcertification\b", re.IGNORECASE),
    ),
    (
        "semantic_triple_overclaim",
        re.compile(r"\bsemantically\s+correct\s+triples\b", re.IGNORECASE),
    ),
    (
        "proven_safe",
        re.compile(r"\bproven\s+safe\b|\bflight[- ]ready\b|\boperationally\s+safe\b", re.IGNORECASE),
    ),
)


def _is_safe_context(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in _SAFE_CONTEXT_MARKERS)


def detect_unsafe_claims(
    text: str,
    *,
    source_path: str = "inline",
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        context = " ".join(lines[max(0, index - 2) : min(len(lines), index + 4)])
        if _is_safe_context(context):
            continue
        for pattern_id, pattern in _UNSAFE_PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            findings.append(
                {
                    "source_path": source_path,
                    "line": index + 1,
                    "pattern_id": pattern_id,
                    "matched_text": match.group(0).strip(),
                    "line_text": line.strip(),
                }
            )
    return findings


def _resolve_scan_paths(project_root: Path, scan_paths: list[str | Path] | None) -> list[Path]:
    configured = scan_paths if scan_paths is not None else list(DEFAULT_SCAN_PATHS)
    resolved: list[Path] = []
    for item in configured:
        path = Path(item)
        resolved.append(path if path.is_absolute() else project_root / path)
    return resolved


def _evidence_file_status(project_root: Path) -> list[dict[str, Any]]:
    files = sorted(
        {
            evidence_file
            for row in CLAIM_SAFETY_MATRIX
            for evidence_file in row["evidence_files"]
        }
        | {"docs/thesis_positioning.md"}
    )
    return [
        {
            "path": path,
            "present": (project_root / path).exists(),
        }
        for path in files
    ]


def build_thesis_claims_review(
    *,
    project_root: str | Path = PROJECT_ROOT,
    scan_paths: list[str | Path] | None = None,
) -> dict[str, Any]:
    root = Path(project_root)
    resolved_scan_paths = _resolve_scan_paths(root, scan_paths)
    unsafe_claims: list[dict[str, Any]] = []
    scanned_files: list[dict[str, Any]] = []
    for path in resolved_scan_paths:
        rel_path = project_relative_path(path, base=root)
        if not path.exists():
            scanned_files.append({"path": rel_path, "present": False})
            continue
        text = path.read_text(encoding="utf-8")
        findings = detect_unsafe_claims(text, source_path=rel_path)
        unsafe_claims.extend(findings)
        scanned_files.append(
            {
                "path": rel_path,
                "present": True,
                "unsafe_claims": len(findings),
            }
        )
    return {
        "metadata": {
            "created_at": "static-for-reproducible-report",
            "timestamp_policy": "wall-clock generation time is omitted to keep tracked reports reproducible",
            "project_root": project_relative_path(root, base=root),
            "scanned_files": scanned_files,
            "unsafe_claims_total": len(unsafe_claims),
        },
        "revised_thesis_claim": REVISED_THESIS_CLAIM,
        "research_questions": RESEARCH_QUESTIONS,
        "hypotheses": HYPOTHESES,
        "contributions": CONTRIBUTIONS,
        "evaluation_philosophy": (
            "Negative or mixed Recall@k results are not hidden. They motivate layered "
            "evaluation and identify when vector retrieval is sufficient."
        ),
        "evaluation_layers": EVALUATION_LAYERS,
        "claim_safety_matrix": CLAIM_SAFETY_MATRIX,
        "evidence_files": _evidence_file_status(root),
        "unsafe_claims": unsafe_claims,
        "unsafe_claims_status": "not_found" if not unsafe_claims else "found",
        "remaining_evidence_gaps": EVIDENCE_GAPS,
        "advisory_boundary": ADVISORY_BOUNDARY,
    }


def write_thesis_claims_review_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path)


def _md_cell(value: Any) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|")
    return text


def write_thesis_claims_review_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Thesis Claims Review",
        "",
        "## Revised Thesis Claim",
        "",
        result["revised_thesis_claim"],
        "",
        "## Research Questions",
        "",
        *[
            f"- **{item['id']}**: {item['question']}"
            for item in result["research_questions"]
        ],
        "",
        "## Hypotheses",
        "",
        *[
            f"- **{item['id']}**: {item['hypothesis']}"
            for item in result["hypotheses"]
        ],
        "",
        "## Evaluation Framing",
        "",
        result["evaluation_philosophy"],
        "",
        "| Layer | Metrics | Purpose |",
        "| --- | --- | --- |",
    ]
    for layer in result["evaluation_layers"]:
        lines.append(
            f"| {_md_cell(layer['layer'])} | {_md_cell(', '.join(layer['metrics']))} | "
            f"{_md_cell(layer['purpose'])} |"
        )
    lines.extend(
        [
            "",
            "The report must not create or recommend a single mixed overall score.",
            "",
            "## Claim Safety Matrix",
            "",
            "| Claim | Current evidence | Supported strength | Safe wording | Unsafe wording to avoid |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in result["claim_safety_matrix"]:
        lines.append(
            f"| {_md_cell(row['claim'])} | {_md_cell(row['current_evidence'])} | "
            f"{_md_cell(row['supported_strength'])} | {_md_cell(row['safe_wording'])} | "
            f"{_md_cell(row['unsafe_wording_to_avoid'])} |"
        )
    lines.extend(["", "## Unsafe Claims Scan", ""])
    if result["unsafe_claims"]:
        lines.append("Unsafe or over-strong claims were found outside explicit limitation contexts:")
        for finding in result["unsafe_claims"]:
            lines.append(
                f"- `{finding['source_path']}:{finding['line']}` "
                f"{finding['pattern_id']}: {finding['line_text']}"
            )
    else:
        lines.append(
            "No unsupported unsafe claims were found in the scanned files outside "
            "explicit limitation or advisory-boundary contexts."
        )
    lines.extend(
        [
            "",
            "## Evidence Gaps Before Thesis Submission",
            "",
            *[f"- {gap}" for gap in result["remaining_evidence_gaps"]],
            "",
            "## Evidence Files",
            "",
        ]
    )
    for item in result["evidence_files"]:
        status = "present" if item["present"] else "missing"
        lines.append(f"- `{item['path']}`: {status}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_thesis_claims_review(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    scan_paths: list[str | Path] | None = None,
    report_name: str = "thesis_claims_review",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_thesis_claims_review(project_root=project_root, scan_paths=scan_paths)
    output = Path(output_dir)
    stem = Path(report_name).stem or "thesis_claims_review"
    json_path = write_thesis_claims_review_json(result, output / f"{stem}.json")
    md_path = write_thesis_claims_review_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
