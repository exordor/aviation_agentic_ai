"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from pathlib import Path
from dataclasses import dataclass

# PROJECT_ROOT is re-exported via the package __init__ for dependents that
# import it from atmonto_experiment; keep it even though unused locally.
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path  # noqa: F401

GOLD_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json")

GOLD_TEMPLATE_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl")

GOLD_REVIEWED_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl")

GOLD_REVIEW_WORKLIST_JSON = Path("data/evaluation/nasa_atmonto/atcscc_gold_review_worklist.json")

GOLD_REVIEW_WORKLIST_MD = Path("data/evaluation/nasa_atmonto/atcscc_gold_review_worklist.md")

GOLD_CANDIDATE_REVIEW_JSONL = Path(
    "data/evaluation/nasa_atmonto/atcscc_system_candidate_review.jsonl"
)

GOLD_CANDIDATE_REVIEW_MD = Path(
    "data/evaluation/nasa_atmonto/atcscc_system_candidate_review.md"
)

GOLD_REVIEW_BATCH_DIR = Path("data/evaluation/nasa_atmonto/review_batches")

GOLD_REVIEW_BATCH_INDEX_MD = GOLD_REVIEW_BATCH_DIR / "index.md"

GOLD_REVIEW_PROGRESS_JSON = Path("data/evaluation/nasa_atmonto/gold_review_progress.json")

GOLD_REVIEW_PROGRESS_MD = Path("data/evaluation/nasa_atmonto/gold_review_progress.md")

GOLD_REVIEW_WORKLOAD_PLAN_JSON = Path(
    "reports/stages/nasa_atmonto_gold_review_workload_plan.json"
)

GOLD_REVIEW_WORKLOAD_PLAN_MD = Path(
    "reports/stages/nasa_atmonto_gold_review_workload_plan.md"
)

GOLD_SEMANTIC_GROUPS_JSON = Path("reports/stages/nasa_atmonto_gold_semantic_groups.json")

GOLD_SEMANTIC_GROUPS_MD = Path("reports/stages/nasa_atmonto_gold_semantic_groups.md")

GOLD_REVIEW_SESSION_PLAN_JSON = Path(
    "reports/stages/nasa_atmonto_gold_review_session_plan.json"
)

GOLD_REVIEW_SESSION_PLAN_MD = Path(
    "reports/stages/nasa_atmonto_gold_review_session_plan.md"
)

GOLD_REVIEW_PRIORITY_PACKET_JSON = Path(
    "reports/stages/nasa_atmonto_gold_review_priority_packets.json"
)

GOLD_REVIEW_PRIORITY_PACKET_DIR = Path("data/evaluation/nasa_atmonto/review_priority_packets")

GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD = GOLD_REVIEW_PRIORITY_PACKET_DIR / "index.md"

GOLD_REVIEW_DECISION_DIR = Path("data/evaluation/nasa_atmonto/review_decisions")

GOLD_REVIEW_DECISION_INDEX_MD = GOLD_REVIEW_DECISION_DIR / "index.md"

GOLD_REVIEW_DECISION_PROGRESS_JSON = Path(
    "data/evaluation/nasa_atmonto/gold_review_decision_progress.json"
)

GOLD_REVIEW_DECISION_PROGRESS_MD = Path(
    "data/evaluation/nasa_atmonto/gold_review_decision_progress.md"
)

GOLD_REVIEW_DECISION_DRAFT_PATH = Path(
    "data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.reviewed_draft.jsonl"
)

REJECTION_ANALYSIS_JSON = Path("reports/stages/nasa_atmonto_rejection_error_analysis.json")

REJECTION_ADJUDICATION_JSON = Path("reports/stages/nasa_atmonto_rejection_adjudication.json")

REJECTION_ADJUDICATION_MD = Path("reports/stages/nasa_atmonto_rejection_adjudication.md")

SCHEMA_SLICE_PATH = Path("data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json")

EXTRACTION_SCHEMA_PATH = Path(
    "data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json"
)

S0_CANDIDATES_PATH = Path(
    "data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_candidates.jsonl"
)

S0_VALIDATED_PATH = Path(
    "data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl"
)

FORMAL_OUTPUT_DIR = Path("data/experiments/nasa_atmonto/formal")

FORMAL_SMOKE_OUTPUT_DIR = FORMAL_OUTPUT_DIR / "smoke"

FORMAL_INPUT_RECORDS_PATH = FORMAL_OUTPUT_DIR / "input_records.jsonl"

FORMAL_SYSTEM_SPECS_PATH = FORMAL_OUTPUT_DIR / "system_specs.json"

S1_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s1_llm_only_prompt_batch.jsonl"

S2_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s2_llm_schema_slice_prompt_batch.jsonl"

S3_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s3_llm_schema_slice_validator_repair_prompt_batch.jsonl"

S1B_PREDICTIONS_PATH = FORMAL_OUTPUT_DIR / "s1b_llm_canonicalized_predictions.jsonl"

S4_PREDICTIONS_PATH = FORMAL_OUTPUT_DIR / "s4_hybrid_backbone_enrichment_predictions.jsonl"

READINESS_REPORT_JSON = Path("reports/stages/nasa_atmonto_formal_experiment_readiness.json")

READINESS_REPORT_MD = Path("reports/stages/nasa_atmonto_formal_experiment_readiness.md")

SCORING_REPORT_JSON = Path("reports/stages/nasa_atmonto_formal_experiment_scoring.json")

SCORING_REPORT_MD = Path("reports/stages/nasa_atmonto_formal_experiment_scoring.md")

SEMANTIC_BOOTSTRAP_ITERATIONS = 200

SEMANTIC_BOOTSTRAP_SEED = 1701

GOLD_VALIDATION_REPORT_JSON = Path(
    "reports/stages/nasa_atmonto_gold_annotation_validation.json"
)

GOLD_VALIDATION_REPORT_MD = Path(
    "reports/stages/nasa_atmonto_gold_annotation_validation.md"
)

GOLD_FREEZE_REPORT_JSON = Path("reports/stages/nasa_atmonto_gold_freeze_status.json")

GOLD_FREEZE_REPORT_MD = Path("reports/stages/nasa_atmonto_gold_freeze_status.md")

PREDICTION_OUTPUT_VALIDATION_REPORT_JSON = Path(
    "reports/stages/nasa_atmonto_prediction_output_validation.json"
)

PREDICTION_OUTPUT_VALIDATION_REPORT_MD = Path(
    "reports/stages/nasa_atmonto_prediction_output_validation.md"
)

REVIEWED_GOLD_STATUS = "reviewed"

PENDING_GOLD_STATUS = "pending_manual_gold_annotation"

ALLOWED_REJECTION_ADJUDICATIONS = {
    "extractor_bug",
    "profile_gap",
    "source_ambiguity",
    "manual_review_only",
}

REVIEW_CHECKLIST_FIELDS: tuple[str, ...] = (
    "source_text_checked",
    "semantic_rubric_checked",
    "profile_gap_boundary_checked",
    "missing_facts_checked",
)

@dataclass(frozen=True)
class SystemDefinition:
    system_id: str
    label: str
    description: str
    expected_output: Path
    prompt_batch: Path | None
    requires_llm: bool
    uses_schema_slice: bool
    uses_validator_repair: bool

SYSTEMS: tuple[SystemDefinition, ...] = (
    SystemDefinition(
        system_id="S0_rule_only",
        label="Rule-only",
        description="Deterministic ATCSCC surface-pattern extractor used by the pilot.",
        expected_output=FORMAL_OUTPUT_DIR / "s0_rule_only_predictions.jsonl",
        prompt_batch=None,
        requires_llm=False,
        uses_schema_slice=True,
        uses_validator_repair=False,
    ),
    SystemDefinition(
        system_id="S1_llm_only",
        label="LLM-only",
        description="LLM extractor without NASA ATMONTO schema terms in the prompt.",
        expected_output=FORMAL_OUTPUT_DIR / "s1_llm_only_predictions.jsonl",
        prompt_batch=S1_PROMPT_BATCH_PATH,
        requires_llm=True,
        uses_schema_slice=False,
        uses_validator_repair=False,
    ),
    SystemDefinition(
        system_id="S1b_llm_canonicalized",
        label="LLM-only + post-hoc canonicalization",
        description=(
            "Post-hoc canonicalization of schema-free S1 facts into the ATMONTO "
            "ATCSCC scoring profile."
        ),
        expected_output=S1B_PREDICTIONS_PATH,
        prompt_batch=None,
        requires_llm=False,
        uses_schema_slice=True,
        uses_validator_repair=False,
    ),
    SystemDefinition(
        system_id="S2_llm_schema_slice",
        label="LLM + schema slice",
        description="LLM extractor constrained by the ATCSCC schema slice and JSON shape.",
        expected_output=FORMAL_OUTPUT_DIR / "s2_llm_schema_slice_predictions.jsonl",
        prompt_batch=S2_PROMPT_BATCH_PATH,
        requires_llm=True,
        uses_schema_slice=True,
        uses_validator_repair=False,
    ),
    SystemDefinition(
        system_id="S3_llm_schema_slice_validator_repair",
        label="LLM + schema slice + validator/repair",
        description="S2 with custom validation and one repair attempt for invalid payloads.",
        expected_output=FORMAL_OUTPUT_DIR
        / "s3_llm_schema_slice_validator_repair_predictions.jsonl",
        prompt_batch=S3_PROMPT_BATCH_PATH,
        requires_llm=True,
        uses_schema_slice=True,
        uses_validator_repair=True,
    ),
    SystemDefinition(
        system_id="S4_hybrid_backbone_enrichment",
        label="Hybrid backbone + semantic enrichment",
        description=(
            "S0 deterministic backbone merged with S3 semantic enrichment through "
            "evidence and validator gates."
        ),
        expected_output=S4_PREDICTIONS_PATH,
        prompt_batch=None,
        requires_llm=False,
        uses_schema_slice=True,
        uses_validator_repair=True,
    ),
)

LLM_RUN_SYSTEM_IDS = {system.system_id for system in SYSTEMS if system.requires_llm}

def system_definitions(repo_root: Path) -> list[dict[str, Any]]:
    return [
        {
            "system_id": system.system_id,
            "label": system.label,
            "description": system.description,
            "expected_output": project_relative_path(repo_root / system.expected_output, repo_root),
            "prompt_batch": (
                project_relative_path(repo_root / system.prompt_batch, repo_root)
                if system.prompt_batch
                else None
            ),
            "run_metadata": project_relative_path(
                repo_root / system_run_metadata_path(system),
                repo_root,
            ),
            "requires_llm": system.requires_llm,
            "uses_schema_slice": system.uses_schema_slice,
            "uses_validator_repair": system.uses_validator_repair,
        }
        for system in SYSTEMS
    ]

def system_output_stem(system: SystemDefinition) -> str:
    return system.expected_output.name.removesuffix("_predictions.jsonl")

def system_run_metadata_path(system: SystemDefinition) -> Path:
    return FORMAL_OUTPUT_DIR / f"{system_output_stem(system)}_run_metadata.json"

def llm_run_output_dir(
    *,
    limit: int | None,
    output_dir: str | Path | None,
) -> Path:
    if output_dir is not None:
        return Path(output_dir)
    if limit is not None:
        return FORMAL_SMOKE_OUTPUT_DIR
    return FORMAL_OUTPUT_DIR

def llm_run_prediction_path(system: SystemDefinition, output_dir: str | Path) -> Path:
    return Path(output_dir) / system.expected_output.name

def llm_run_metadata_path(system: SystemDefinition, output_dir: str | Path) -> Path:
    return Path(output_dir) / f"{system_output_stem(system)}_run_metadata.json"

def system_by_id(system_id: str) -> SystemDefinition:
    for system in SYSTEMS:
        if system.system_id == system_id:
            return system
    raise ValueError(f"Unknown system_id: {system_id}")
