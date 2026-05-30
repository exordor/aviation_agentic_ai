from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path


REVISED_THESIS_CLAIM = (
    "This thesis does not assume that GraphRAG universally improves retrieval "
    "Recall@k over vector-only RAG. Instead, it investigates a narrower and more "
    "safety-relevant claim: in aviation training question answering, an "
    "ontology-constrained GraphRAG pipeline can add inspectable KG/path "
    "evidence, expose structured evidence coverage, and support "
    "insufficient-evidence abstention checks. The "
    "system is therefore evaluated with layered metrics: retrieval quality, KG "
    "evidence quality, answer citation quality, and safety-aware abstention are "
    "measured separately rather than collapsed into a single overall score."
)

RESEARCH_QUESTIONS = [
    {
        "id": "RQ1",
        "question": "How can a lightweight aviation ontology constrain KG extraction from aviation training text?",
    },
    {
        "id": "RQ2",
        "question": "Does ontology-constrained KG extraction add inspectable evidence-traceability signals compared with vector-only RAG?",
    },
    {
        "id": "RQ3",
        "question": "When does graph evidence help aviation QA, and when is vector retrieval sufficient?",
    },
    {
        "id": "RQ4",
        "question": "Can evidence-aware GraphRAG better identify unsupported or unsafe aviation questions?",
    },
]

HYPOTHESES = [
    {
        "id": "H1",
        "hypothesis": "Ontology constraints reduce unsupported KG triples and preserve provenance.",
    },
    {
        "id": "H2",
        "hypothesis": "GraphRAG adds inspectable evidence-traceability signals compared with vector-only RAG.",
    },
    {
        "id": "H3",
        "hypothesis": "GraphRAG does not always improve Recall@k but can improve structured evidence coverage.",
    },
    {
        "id": "H4",
        "hypothesis": "Evidence sufficiency checking improves abstention on unsupported aviation questions.",
    },
    {
        "id": "H5",
        "hypothesis": (
            "KG evidence is most useful for relation-oriented, causal, and cross-page "
            "questions, and less useful for simple factual definition questions."
        ),
    },
]

CONTRIBUTIONS = [
    "A task ontology for PHAK Chapter 4 that constrains aviation KG extraction.",
    "Validated KG/ABox artifacts with source provenance for extracted triples.",
    "A CLI-first GraphRAG pipeline with vector, graph, and hybrid retrieval modes.",
    "Layered evaluation reports that keep retrieval, KG evidence, answer quality, and abstention separate.",
    "An explicit aviation learning and decision-support boundary for demonstrations.",
]

EVALUATION_LAYERS = [
    {
        "layer": "Retrieval quality",
        "metrics": ["Recall@k", "MRR@k", "Context Precision@k"],
        "purpose": "Measure whether the retriever returns source chunks near the top of the ranking.",
    },
    {
        "layer": "KG evidence quality",
        "metrics": ["key entity coverage", "triple coverage", "provenance completeness"],
        "purpose": "Measure whether graph evidence covers the entities and relations needed by the question.",
    },
    {
        "layer": "Answer quality",
        "metrics": ["citation correctness", "faithfulness", "relevance"],
        "purpose": "Measure whether generated answers are supported by cited evidence.",
    },
    {
        "layer": "Safety-aware abstention",
        "metrics": ["abstention correctness", "false answer rate", "boundary violations"],
        "purpose": "Measure whether the system refuses unsupported or unsafe aviation questions.",
    },
]

CLAIM_SAFETY_MATRIX = [
    {
        "claim": "Ontology constrains KG extraction.",
        "current_evidence": "Extraction profile terms map to the curated ontology; KG validation rejects unsupported schema terms.",
        "supported_strength": "strong",
        "safe_wording": "The task ontology constrains which focused classes and relations can enter the KG.",
        "unsafe_wording_to_avoid": "The ontology fully models aviation knowledge.",
        "evidence_files": [
            "docs/ontology_design.md",
            "configs/extraction_profile.yaml",
            "reports/stages/kg_validation.json",
            "reports/stages/structure_aware_kg_validation.json",
        ],
    },
    {
        "claim": "KG triples preserve provenance.",
        "current_evidence": "KG validation reports zero missing-provenance errors in the current fixed-window and structure-aware artifacts.",
        "supported_strength": "strong",
        "safe_wording": "Current extracted triples carry source chunk provenance checked by deterministic validation.",
        "unsafe_wording_to_avoid": "Every KG triple is semantically correct.",
        "evidence_files": [
            "data/kg/06_phak_ch4_0.kg.jsonl",
            "data/kg/06_phak_ch4_0.structure_aware.kg.jsonl",
            "reports/stages/kg_validation.json",
            "reports/stages/structure_aware_kg_validation.json",
        ],
    },
    {
        "claim": "GraphRAG improves Recall@5.",
        "current_evidence": "Expanded retrieval ablation shows vector Recall@5 can be higher than default hybrid Recall@5.",
        "supported_strength": "not supported",
        "safe_wording": "GraphRAG does not always improve Recall@5; report Recall separately from KG evidence coverage.",
        "unsafe_wording_to_avoid": "GraphRAG always improves Recall@5.",
        "evidence_files": [
            "reports/stages/retrieval_ablation.json",
            "reports/stages/graphrag_review.json",
            "reports/stages/hybrid_rag_experiment.json",
            "reports/stages/hybrid_rag_structure_aware.json",
        ],
    },
    {
        "claim": "GraphRAG improves structured evidence support.",
        "current_evidence": "Graph and hybrid modes expose KG coverage, provenance, triples, and evidence-level answer support.",
        "supported_strength": "moderate",
        "safe_wording": "GraphRAG improves inspectable structured evidence support in the current benchmark.",
        "unsafe_wording_to_avoid": "GraphRAG is always more accurate than vector retrieval.",
        "evidence_files": [
            "reports/stages/graphrag_review.json",
            "reports/stages/evidence_level_evaluation.json",
            "reports/stages/kg_extraction_comparison.json",
        ],
    },
    {
        "claim": "Hybrid RAG always beats vector-only RAG.",
        "current_evidence": "Fixed-window and expanded ablations include cases where vector retrieval is equal or better on Recall@5.",
        "supported_strength": "not supported",
        "safe_wording": "Hybrid RAG can add KG evidence coverage while vector retrieval can remain sufficient for simple factual questions.",
        "unsafe_wording_to_avoid": "Hybrid RAG always beats vector-only RAG.",
        "evidence_files": [
            "reports/stages/retrieval_ablation.json",
            "reports/stages/hybrid_rag_experiment.json",
            "reports/stages/graphrag_review.json",
        ],
    },
    {
        "claim": "The system can answer aviation operational questions.",
        "current_evidence": "The advisory boundary limits the system to learning and decision support; live operational data and official procedures are out of scope.",
        "supported_strength": "not supported",
        "safe_wording": "The system can answer aviation training questions when evidence is sufficient and should abstain otherwise.",
        "unsafe_wording_to_avoid": "The system can support operational flight decisions.",
        "evidence_files": [
            "src/aviation_agentic_ai/advisory.py",
            "docs/document_expansion_protocol.md",
            "reports/stages/robustness_evaluation.json",
        ],
    },
    {
        "claim": "The system can support aviation learning questions.",
        "current_evidence": "The pipeline answers PHAK Chapter 4 training questions with citations and evidence panels.",
        "supported_strength": "moderate",
        "safe_wording": "The prototype supports aviation learning questions over its scoped source material.",
        "unsafe_wording_to_avoid": "The prototype is a certified aviation assistant.",
        "evidence_files": [
            "reports/stages/answer_evaluation.json",
            "reports/stages/evidence_cards.md",
            "reports/stages/web_demo_readiness.json",
        ],
    },
    {
        "claim": "The system can replace POH/checklists/ATC/instructor judgment.",
        "current_evidence": "The advisory boundary explicitly rejects replacement of official sources or human judgment.",
        "supported_strength": "not supported",
        "safe_wording": "The system does not replace POH, approved checklists, ATC, instructor guidance, or pilot judgment.",
        "unsafe_wording_to_avoid": "The system can replace POH, checklists, ATC, or instructor judgment.",
        "evidence_files": ["src/aviation_agentic_ai/advisory.py", "GOALS.md", "README.md"],
    },
    {
        "claim": "The benchmark is externally aviation-expert certified.",
        "current_evidence": "Current labels are reviewed course-project / thesis-oriented gold, not external examiner certification.",
        "supported_strength": "not supported",
        "safe_wording": "The benchmark is course-project / thesis-oriented gold with documented limitations.",
        "unsafe_wording_to_avoid": "The benchmark is externally aviation-expert certified.",
        "evidence_files": [
            "data/cqs/06_phak_ch4_0.gold.json",
            "data/cqs/06_phak_ch4_0.expanded.gold.json",
            "reports/stages/final_evaluation_review.json",
        ],
    },
    {
        "claim": "The benchmark is course-project / thesis-oriented gold.",
        "current_evidence": "Reports identify the 10-question and expanded 35-question labels as project/thesis evidence.",
        "supported_strength": "strong",
        "safe_wording": "The benchmark is course-project / thesis-oriented gold, useful for internal evaluation but not external certification.",
        "unsafe_wording_to_avoid": "The benchmark proves aviation-domain correctness.",
        "evidence_files": [
            "data/cqs/06_phak_ch4_0.gold.json",
            "data/cqs/06_phak_ch4_0.expanded.gold.json",
            "docs/benchmark_design.md",
            "reports/stages/final_evaluation_review.json",
        ],
    },
]

EVIDENCE_GAPS = [
    "Need larger benchmark beyond 35 questions",
    "Need stronger no-answer / insufficient-evidence evaluation",
    "Need triple-level semantic correctness review",
    "Need graph traversal or path-based retrieval if claiming multi-hop graph reasoning",
    "Need manual or expert review if claiming aviation-domain correctness",
    "Need embedding/index comparison if claiming retrieval backend optimality",
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
        "certified_aviation_assistant",
        re.compile(
            r"\bcertified\b.{0,30}\baviation\b.{0,30}\bassistant\b"
            r"|\baviation\b.{0,30}\bassistant\b.{0,30}\bcertified\b",
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
            "created_at": datetime.now(UTC).isoformat(),
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
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


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
