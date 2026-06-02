from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1, sha256
import json
from pathlib import Path
from random import Random
import re
import sys
from typing import Any, Callable

from aviation_agentic_ai.llm.providers import configured_llm_model, configured_llm_provider, get_llm
from aviation_agentic_ai.ontology.atmonto_minimal_loop import (
    classify_controlled_element,
    classify_tmi,
    nas_entity_iri,
    source_entity_iri,
    validate_candidate_payloads,
)
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.utils.json_extraction import (
    JSONPayloadExtractionError,
    extract_json_object,
)


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
LLMInvoker = Callable[[list[dict[str, str]]], str]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    payload = "\n".join(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload + ("\n" if payload else ""), encoding="utf-8")
    tmp.replace(path)


def append_jsonl_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        handle.flush()


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonl_semantically_equal(
    left: list[dict[str, Any]], right: list[dict[str, Any]]
) -> bool:
    """Compare two JSONL record lists for semantic equality, normalising key order."""
    if len(left) != len(right):
        return False
    for a, b in zip(left, right):
        if json.dumps(a, sort_keys=True, ensure_ascii=False) != json.dumps(
            b, sort_keys=True, ensure_ascii=False
        ):
            return False
    return True


def compact_text(value: object) -> str:
    return " ".join(str(value or "").split())


def ceil_div(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    return -(-numerator // denominator)


def term_name(value: object) -> str:
    text = str(value or "")
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text and text.startswith(("http://", "https://", "urn:")):
        return text.rstrip("/").rsplit("/", 1)[-1]
    if ":" in text and not text.startswith(("http://", "https://", "urn:")):
        return text.rsplit(":", 1)[-1]
    return text


FactKey = tuple[str, str, str, str, str, str, str]


def fact_with_source_id(fact: dict[str, Any], source_id: object) -> dict[str, Any]:
    if fact.get("source_id") not in (None, "") or source_id in (None, ""):
        return fact
    return {**fact, "source_id": source_id}


def canonical_fact_key(fact: dict[str, Any]) -> FactKey:
    value = fact.get("object") if fact.get("fact_type") == "object_property" else fact.get("value")
    return (
        compact_text(fact.get("source_id")),
        term_name(fact.get("subject_class")),
        term_name(fact.get("predicate")),
        compact_text(value).lower(),
        term_name(fact.get("object_class")),
        term_name(fact.get("datatype")),
        compact_text(fact.get("evidence_text")).lower(),
    )


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


def gold_annotation_status(gold_records: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = Counter(
        str(record.get("gold_annotation", {}).get("annotation_status", "missing_status"))
        for record in gold_records
    )
    reviewed = statuses.get(REVIEWED_GOLD_STATUS, 0)
    pending = len(gold_records) - reviewed
    completed = reviewed == len(gold_records) and bool(gold_records)
    valid_fact_count = sum(
        len(record.get("gold_annotation", {}).get("valid_facts", []))
        for record in gold_records
    )
    missing_fact_count = sum(
        len(record.get("gold_annotation", {}).get("missing_facts", []))
        for record in gold_records
    )
    return {
        "record_count": len(gold_records),
        "status_counts": dict(sorted(statuses.items())),
        "reviewed_record_count": reviewed,
        "pending_record_count": pending,
        "valid_fact_count": valid_fact_count,
        "missing_fact_count": missing_fact_count,
        "complete": completed,
    }


def fact_key_predicate(key: FactKey) -> str:
    return key[2]


def gold_fact_keys(gold_records: list[dict[str, Any]]) -> set[FactKey]:
    keys: set[FactKey] = set()
    for record in gold_records:
        for fact in record.get("gold_annotation", {}).get("valid_facts", []):
            if isinstance(fact, dict):
                keys.add(canonical_fact_key(fact_with_source_id(fact, record.get("source_id"))))
        for fact in record.get("gold_annotation", {}).get("missing_facts", []):
            if isinstance(fact, dict):
                keys.add(canonical_fact_key(fact_with_source_id(fact, record.get("source_id"))))
    return keys


def accepted_prediction_facts(
    validations: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for item in validations:
        if item.get("accepted") and isinstance(item.get("validated_fact"), dict):
            facts.append(fact_with_source_id(item["validated_fact"], item.get("source_id")))
    return facts


def semantic_metric_values(
    *,
    predicted_count: int,
    gold_count: int,
    true_positive_count: int,
) -> dict[str, float]:
    precision = true_positive_count / predicted_count if predicted_count else 0.0
    recall = true_positive_count / gold_count if gold_count else 0.0
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "manual_semantic_correctness": precision,
    }


def source_key_groups(keys: set[FactKey]) -> dict[str, set[FactKey]]:
    groups: dict[str, set[FactKey]] = {}
    for key in keys:
        groups.setdefault(key[0], set()).add(key)
    return groups


def percentile_interval(values: list[float], *, lower_q: float = 0.025, upper_q: float = 0.975) -> dict[str, float]:
    ordered = sorted(values)
    if not ordered:
        return {"low": 0.0, "high": 0.0}
    lower_index = int((len(ordered) - 1) * lower_q)
    upper_index = int((len(ordered) - 1) * upper_q)
    return {"low": ordered[lower_index], "high": ordered[upper_index]}


def semantic_bootstrap_confidence_intervals(
    *,
    prediction_keys: set[FactKey],
    gold_keys: set[FactKey],
    iterations: int = SEMANTIC_BOOTSTRAP_ITERATIONS,
    seed: int = SEMANTIC_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    source_ids = sorted(source_id for source_id in {key[0] for key in gold_keys | prediction_keys} if source_id)
    if not source_ids:
        return {
            "available": False,
            "reason": "source_ids_missing",
            "method": "record_bootstrap_by_source_id",
            "iterations": iterations,
            "seed": seed,
        }

    predictions_by_source = source_key_groups(prediction_keys)
    gold_by_source = source_key_groups(gold_keys)
    rng = Random(seed)
    samples: dict[str, list[float]] = {
        "precision": [],
        "recall": [],
        "f1": [],
        "manual_semantic_correctness": [],
    }
    for _ in range(iterations):
        predicted_count = 0
        gold_count = 0
        true_positive_count = 0
        for source_id in (rng.choice(source_ids) for _ in source_ids):
            predicted = predictions_by_source.get(source_id, set())
            gold = gold_by_source.get(source_id, set())
            predicted_count += len(predicted)
            gold_count += len(gold)
            true_positive_count += len(predicted & gold)
        values = semantic_metric_values(
            predicted_count=predicted_count,
            gold_count=gold_count,
            true_positive_count=true_positive_count,
        )
        for key in samples:
            samples[key].append(values[key])

    return {
        "available": True,
        "method": "record_bootstrap_by_source_id",
        "level": 0.95,
        "iterations": iterations,
        "seed": seed,
        "sampled_source_id_count": len(source_ids),
        "intervals": {
            key: percentile_interval(values)
            for key, values in sorted(samples.items())
        },
    }


def structural_metrics(
    validations: list[dict[str, Any]],
    *,
    repair_applicable: bool = False,
) -> dict[str, Any]:
    candidate_count = len(validations)
    rejected = [item for item in validations if not item.get("accepted")]
    accepted = [item for item in validations if item.get("accepted")]
    repaired = [item for item in accepted if item.get("repairs")]
    initially_invalid = len(repaired) + len(rejected)
    repair_success_rate = (
        (len(repaired) / initially_invalid)
        if repair_applicable and initially_invalid
        else None
    )
    return {
        "candidate_fact_count": candidate_count,
        "accepted_fact_count": len(accepted),
        "rejected_fact_count": len(rejected),
        "structural_acceptance_rate": (len(accepted) / candidate_count) if candidate_count else None,
        "schema_violation_rate": (len(rejected) / candidate_count) if candidate_count else None,
        "repair_applicable": repair_applicable,
        "repair_attempted_fact_count": initially_invalid if repair_applicable else None,
        "repair_accepted_fact_count": len(repaired) if repair_applicable else None,
        "repair_success_rate": repair_success_rate,
        "status_counts": dict(sorted(Counter(str(item.get("status")) for item in validations).items())),
        "error_counts": dict(
            sorted(
                Counter(
                    str(error)
                    for item in validations
                    for error in item.get("errors", [])
                ).items()
            )
        ),
    }


def json_adherence_from_payloads(payloads: list[dict[str, Any]], selected_ids: set[str]) -> dict[str, Any]:
    attempted = len(selected_ids)
    valid = sum(1 for payload in payloads if str(payload.get("source_id")) in selected_ids)
    return {
        "attempted_record_count": attempted,
        "valid_json_payload_count": valid,
        "json_adherence": (valid / attempted) if attempted else None,
    }


def semantic_metrics(
    *,
    predictions: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
) -> dict[str, Any]:
    gold_keys = gold_fact_keys(gold_records)
    if not gold_keys:
        return {
            "available": False,
            "reason": "manual_gold_facts_missing",
            "precision": None,
            "recall": None,
            "f1": None,
            "manual_semantic_correctness": None,
            "confidence_intervals": None,
        }
    prediction_keys = {canonical_fact_key(fact) for fact in predictions}
    true_positive = prediction_keys & gold_keys
    false_positive = prediction_keys - gold_keys
    false_negative = gold_keys - prediction_keys
    metric_values = semantic_metric_values(
        predicted_count=len(prediction_keys),
        gold_count=len(gold_keys),
        true_positive_count=len(true_positive),
    )
    return {
        "available": True,
        "predicted_fact_count": len(prediction_keys),
        "gold_fact_count": len(gold_keys),
        "true_positive_count": len(true_positive),
        "false_positive_count": len(false_positive),
        "false_negative_count": len(false_negative),
        **metric_values,
        "confidence_intervals": semantic_bootstrap_confidence_intervals(
            prediction_keys=prediction_keys,
            gold_keys=gold_keys,
        ),
    }


def evidence_in_source(evidence_text: object, source_text: object) -> bool:
    evidence = str(evidence_text or "")
    source = str(source_text or "")
    if not evidence:
        return False
    if evidence in source:
        return True
    return compact_text(evidence) in compact_text(source)


def fact_has_object_or_value(fact: dict[str, Any]) -> bool:
    if fact.get("fact_type") == "object_property":
        return any(fact.get(key) not in (None, "") for key in ("object", "object_id"))
    if fact.get("fact_type") == "datatype_property":
        return "value" in fact and fact.get("datatype") not in (None, "")
    return False


def validate_gold_fact(
    *,
    fact: dict[str, Any],
    record: dict[str, Any],
    fact_path: str,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for field in ("fact_type", "subject_class", "predicate", "evidence_text"):
        if fact.get(field) in (None, ""):
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": fact_path,
                    "error": f"missing_{field}",
                }
            )
    if fact.get("fact_type") not in {"object_property", "datatype_property"}:
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": fact_path,
                "error": "invalid_fact_type",
            }
        )
    if not fact_has_object_or_value(fact):
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": fact_path,
                "error": "missing_object_or_value",
            }
        )
    if fact.get("source_id") and str(fact.get("source_id")) != str(record.get("source_id")):
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": fact_path,
                "error": "fact_source_id_mismatch",
            }
        )
    if not evidence_in_source(fact.get("evidence_text"), record.get("source_text")):
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": fact_path,
                "error": "evidence_not_found_in_source_text",
            }
        )
    return errors


def rejected_fact_ids(record: dict[str, Any]) -> set[str]:
    return {
        str(item.get("fact_id"))
        for item in record.get("validator_results", [])
        if isinstance(item, dict) and item.get("accepted") is False and item.get("fact_id")
    }


def review_checklist_template(value: bool = False) -> dict[str, bool]:
    return {field: value for field in REVIEW_CHECKLIST_FIELDS}


def incomplete_review_checklist_fields(checklist: Any) -> list[str]:
    if not isinstance(checklist, dict):
        return list(REVIEW_CHECKLIST_FIELDS)
    return [field for field in REVIEW_CHECKLIST_FIELDS if checklist.get(field) is not True]


def validate_review_checklist(record: dict[str, Any]) -> list[dict[str, Any]]:
    annotation = record.get("gold_annotation", {})
    incomplete = incomplete_review_checklist_fields(annotation.get("review_checklist"))
    if not incomplete:
        return []
    return [
        {
            "sample_id": record.get("sample_id"),
            "source_id": record.get("source_id"),
            "path": "gold_annotation.review_checklist",
            "error": "incomplete_review_checklist",
            "fields": incomplete,
        }
    ]


def validate_rejection_adjudications(record: dict[str, Any]) -> list[dict[str, Any]]:
    annotation = record.get("gold_annotation", {})
    adjudications = annotation.get("rejected_fact_adjudications", [])
    errors: list[dict[str, Any]] = []
    if not isinstance(adjudications, list):
        return [
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": "gold_annotation.rejected_fact_adjudications",
                "error": "not_a_list",
            }
        ]

    rejected_ids = rejected_fact_ids(record)
    by_fact_id = {
        str(item.get("fact_id")): item
        for item in adjudications
        if isinstance(item, dict) and item.get("fact_id")
    }
    if rejected_ids and set(by_fact_id) != rejected_ids:
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": "gold_annotation.rejected_fact_adjudications",
                "error": "rejected_fact_adjudication_ids_do_not_match_validator_rejections",
                "expected_fact_ids": sorted(rejected_ids),
                "actual_fact_ids": sorted(by_fact_id),
            }
        )
    for fact_id, adjudication in by_fact_id.items():
        decision = str(adjudication.get("decision", ""))
        if decision not in ALLOWED_REJECTION_ADJUDICATIONS:
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": f"gold_annotation.rejected_fact_adjudications[{fact_id}].decision",
                    "error": "invalid_rejection_adjudication_decision",
                    "allowed_values": sorted(ALLOWED_REJECTION_ADJUDICATIONS),
                }
            )
        for field in ("rationale", "recommended_action"):
            if not adjudication.get(field):
                errors.append(
                    {
                        "sample_id": record.get("sample_id"),
                        "source_id": record.get("source_id"),
                        "path": f"gold_annotation.rejected_fact_adjudications[{fact_id}].{field}",
                        "error": f"missing_{field}",
                    }
                )
    return errors


def validate_gold_annotation_records(
    *,
    gold_records: list[dict[str, Any]],
    selected_source_ids: set[str],
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    source_ids = [str(record.get("source_id")) for record in gold_records]
    source_counter = Counter(source_ids)
    duplicate_source_ids = sorted(source_id for source_id, count in source_counter.items() if count > 1)
    missing_source_ids = sorted(selected_source_ids - set(source_ids))
    unexpected_source_ids = sorted(set(source_ids) - selected_source_ids)

    if duplicate_source_ids:
        errors.append({"error": "duplicate_source_ids", "source_ids": duplicate_source_ids})
    if missing_source_ids:
        errors.append({"error": "missing_selected_source_ids", "source_ids": missing_source_ids})
    if unexpected_source_ids:
        errors.append({"error": "unexpected_source_ids", "source_ids": unexpected_source_ids})

    for record in gold_records:
        annotation = record.get("gold_annotation")
        if not isinstance(annotation, dict):
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": "gold_annotation",
                    "error": "missing_gold_annotation",
                }
            )
            continue
        status = str(annotation.get("annotation_status", ""))
        if status == PENDING_GOLD_STATUS:
            warnings.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "warning": "pending_manual_gold_annotation",
                }
            )
            continue
        if status != REVIEWED_GOLD_STATUS:
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": "gold_annotation.annotation_status",
                    "error": "invalid_annotation_status",
                    "allowed_values": [PENDING_GOLD_STATUS, REVIEWED_GOLD_STATUS],
                }
            )
            continue
        if not annotation.get("annotator_id"):
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": "gold_annotation.annotator_id",
                    "error": "missing_annotator_id",
                }
            )
        errors.extend(validate_review_checklist(record))
        for field in ("valid_facts", "invalid_candidate_fact_ids", "missing_facts"):
            if not isinstance(annotation.get(field), list):
                errors.append(
                    {
                        "sample_id": record.get("sample_id"),
                        "source_id": record.get("source_id"),
                        "path": f"gold_annotation.{field}",
                        "error": "not_a_list",
                    }
                )
        candidate_fact_ids = {
            str(fact.get("fact_id"))
            for fact in record.get("candidate_facts", [])
            if isinstance(fact, dict) and fact.get("fact_id")
        }
        invalid_ids = [str(value) for value in annotation.get("invalid_candidate_fact_ids", [])]
        unknown_invalid = sorted(set(invalid_ids) - candidate_fact_ids)
        if unknown_invalid:
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": "gold_annotation.invalid_candidate_fact_ids",
                    "error": "unknown_candidate_fact_ids",
                    "fact_ids": unknown_invalid,
                }
            )
        for index, fact in enumerate(annotation.get("valid_facts", [])):
            if isinstance(fact, dict):
                errors.extend(
                    validate_gold_fact(
                        fact=fact,
                        record=record,
                        fact_path=f"gold_annotation.valid_facts[{index}]",
                    )
                )
            else:
                errors.append(
                    {
                        "sample_id": record.get("sample_id"),
                        "source_id": record.get("source_id"),
                        "path": f"gold_annotation.valid_facts[{index}]",
                        "error": "not_an_object",
                    }
                )
        for index, fact in enumerate(annotation.get("missing_facts", [])):
            if isinstance(fact, dict):
                errors.extend(
                    validate_gold_fact(
                        fact=fact,
                        record=record,
                        fact_path=f"gold_annotation.missing_facts[{index}]",
                    )
                )
            else:
                errors.append(
                    {
                        "sample_id": record.get("sample_id"),
                        "source_id": record.get("source_id"),
                        "path": f"gold_annotation.missing_facts[{index}]",
                        "error": "not_an_object",
                    }
                )
        errors.extend(validate_rejection_adjudications(record))

    status = "ready_for_scoring"
    if errors:
        status = "needs_revision"
    elif warnings:
        status = "pending_manual_annotation"

    return {
        "status": status,
        "record_count": len(gold_records),
        "selected_source_id_count": len(selected_source_ids),
        "reviewed_record_count": sum(
            1
            for record in gold_records
            if record.get("gold_annotation", {}).get("annotation_status") == REVIEWED_GOLD_STATUS
        ),
        "pending_record_count": sum(
            1
            for record in gold_records
            if record.get("gold_annotation", {}).get("annotation_status") != REVIEWED_GOLD_STATUS
        ),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors[:100],
        "warnings": warnings[:100],
        "completion_gate": (
            "Gold annotations are usable for formal precision/recall/F1 only when status is "
            "ready_for_scoring."
        ),
    }


def build_gold_annotation_validation_report(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    selected_source_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    validation = validate_gold_annotation_records(
        gold_records=gold_records,
        selected_source_ids=selected_source_ids,
    )
    return {
        "source_family": "nasa_atmonto_gold_annotation_validation",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        **validation,
    }


def gold_validation_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Annotation Validation",
        "",
        f"- Status: `{report['status']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Gold manifest: `{report['gold_manifest']}`",
        f"- Records: {report['record_count']}",
        f"- Reviewed records: {report['reviewed_record_count']}",
        f"- Pending records: {report['pending_record_count']}",
        f"- Errors: {report['error_count']}",
        f"- Warnings: {report['warning_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Required Rejection Decisions",
        "",
        "- For each reviewed record, every rejected validator fact must have a "
        "`rejected_fact_adjudications` entry.",
        "- Allowed decisions: "
        + ", ".join(f"`{value}`" for value in sorted(ALLOWED_REJECTION_ADJUDICATIONS)),
        "",
        "## Current Warnings",
        "",
    ]
    for warning in report["warnings"][:20]:
        lines.append(
            f"- `{warning.get('sample_id')}` / `{warning.get('source_id')}`: "
            f"{warning.get('warning')}"
        )
    if len(report["warnings"]) > 20:
        lines.append(f"- ... {len(report['warnings']) - 20} more warnings omitted")
    lines.extend(["", "## Current Errors", ""])
    for error in report["errors"][:20]:
        lines.append(f"- `{error.get('path', '<manifest>')}`: {error.get('error')}")
    if len(report["errors"]) > 20:
        lines.append(f"- ... {len(report['errors']) - 20} more errors omitted")
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines).rstrip() + "\n"


def run_gold_annotation_validation(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_gold_annotation_validation_report(repo_root)
    write_json(repo_root / GOLD_VALIDATION_REPORT_JSON, report)
    (repo_root / GOLD_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_VALIDATION_REPORT_MD).write_text(
        gold_validation_markdown(report),
        encoding="utf-8",
    )
    return {
        "report_json": project_relative_path(repo_root / GOLD_VALIDATION_REPORT_JSON, repo_root),
        "report_markdown": project_relative_path(repo_root / GOLD_VALIDATION_REPORT_MD, repo_root),
        "status": report["status"],
        "error_count": report["error_count"],
        "warning_count": report["warning_count"],
    }


def build_gold_freeze_status(
    repo_root: str | Path = PROJECT_ROOT,
    output_path: str | Path = GOLD_REVIEWED_PATH,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    output = Path(output_path)
    if output.is_absolute():
        output = output.relative_to(repo_root)
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    selected_source_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    validation = validate_gold_annotation_records(
        gold_records=gold_records,
        selected_source_ids=selected_source_ids,
    )
    ready = validation["status"] == "ready_for_scoring"
    output_file = repo_root / output
    output_exists = output_file.exists()
    output_matches_template = output_exists and _jsonl_semantically_equal(read_jsonl(output_file), gold_records)
    status = "blocked_pending_review"
    if ready and output_matches_template:
        status = "frozen"
    elif ready:
        status = "ready_to_freeze"
    return {
        "source_family": "nasa_atmonto_gold_freeze_status",
        "status": status,
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "reviewed_gold_output": project_relative_path(output_file, repo_root),
        "selected_source_id_count": len(selected_source_ids),
        "record_count": validation["record_count"],
        "validation_status": validation["status"],
        "reviewed_record_count": validation["reviewed_record_count"],
        "pending_record_count": validation["pending_record_count"],
        "error_count": validation["error_count"],
        "warning_count": validation["warning_count"],
        "output_exists": output_exists,
        "output_matches_template": output_matches_template,
        "output_sha256": file_sha256(output_file) if output_exists else None,
        "completion_gate": (
            "The reviewed gold JSONL may be frozen only when gold annotation validation "
            "status is ready_for_scoring."
        ),
    }


def gold_freeze_status_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# NASA ATMONTO Gold Freeze Status",
            "",
            f"- Status: `{report['status']}`",
            f"- Validation status: `{report['validation_status']}`",
            f"- Gold template: `{report['gold_template']}`",
            f"- Reviewed gold output: `{report['reviewed_gold_output']}`",
            f"- Records: {report['record_count']}",
            f"- Reviewed records: {report['reviewed_record_count']}",
            f"- Pending records: {report['pending_record_count']}",
            f"- Errors: {report['error_count']}",
            f"- Warnings: {report['warning_count']}",
            f"- Output exists: `{report['output_exists']}`",
            f"- Output matches template: `{report['output_matches_template']}`",
            f"- Output SHA-256: `{report['output_sha256']}`",
            "",
            "## Completion Gate",
            "",
            f"- {report['completion_gate']}",
        ]
    ) + "\n"


def freeze_reviewed_gold_set(
    repo_root: str | Path = PROJECT_ROOT,
    output_path: str | Path = GOLD_REVIEWED_PATH,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    output = Path(output_path)
    if output.is_absolute():
        output = output.relative_to(repo_root)
    status = build_gold_freeze_status(repo_root, output)
    if status["status"] != "ready_to_freeze":
        write_json(repo_root / GOLD_FREEZE_REPORT_JSON, status)
        (repo_root / GOLD_FREEZE_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
        (repo_root / GOLD_FREEZE_REPORT_MD).write_text(
            gold_freeze_status_markdown(status),
            encoding="utf-8",
        )
        return status

    records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    output_file = repo_root / output
    write_jsonl(output_file, records)
    frozen_status = {
        **build_gold_freeze_status(repo_root, output),
        "status": "frozen",
        "frozen_at": utc_timestamp(),
        "output_exists": True,
        "output_sha256": file_sha256(output_file),
    }
    write_json(repo_root / GOLD_FREEZE_REPORT_JSON, frozen_status)
    (repo_root / GOLD_FREEZE_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_FREEZE_REPORT_MD).write_text(
        gold_freeze_status_markdown(frozen_status),
        encoding="utf-8",
    )
    return frozen_status


def rejection_group_lookup(rejection_analysis: dict[str, Any]) -> dict[tuple[str, tuple[str, ...]], dict[str, Any]]:
    lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
    for group in rejection_analysis.get("groups", []):
        if not isinstance(group, dict):
            continue
        predicate = str(group.get("predicate", ""))
        errors = tuple(str(error) for error in group.get("errors", []))
        lookup[(predicate, errors)] = group
    return lookup


def summarize_rejected_fact(
    *,
    record: dict[str, Any],
    validator_result: dict[str, Any],
    candidate_by_id: dict[str, dict[str, Any]],
    group_lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]],
) -> dict[str, Any]:
    fact_id = str(validator_result.get("fact_id", ""))
    candidate = candidate_by_id.get(fact_id, {})
    errors = tuple(str(error) for error in validator_result.get("errors", []))
    predicate = str(candidate.get("predicate", ""))
    group = group_lookup.get((predicate, errors), {})
    return {
        "fact_id": fact_id,
        "predicate": predicate,
        "errors": list(errors),
        "subject_class": candidate.get("subject_class"),
        "object_class": candidate.get("object_class"),
        "object": candidate.get("object"),
        "value": candidate.get("value"),
        "evidence_text": candidate.get("evidence_text"),
        "suggested_decision": group.get("decision"),
        "suggested_rationale": group.get("rationale"),
        "suggested_action": group.get("recommended_action"),
    }


def build_gold_review_worklist(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    rejection_analysis = read_json(repo_root / REJECTION_ANALYSIS_JSON)
    group_lookup = rejection_group_lookup(rejection_analysis)

    work_records: list[dict[str, Any]] = []
    total_rejected_facts = 0
    records_with_rejections = 0
    class_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    suggested_decision_counts: Counter[str] = Counter()

    for record in gold_records:
        annotation = record.get("gold_annotation", {})
        status = str(annotation.get("annotation_status", "missing_status"))
        status_counts[status] += 1
        class_name = str(record.get("candidate_subject_class", ""))
        class_counts[class_name] += 1
        candidate_by_id = {
            str(candidate.get("fact_id")): candidate
            for candidate in record.get("candidate_facts", [])
            if isinstance(candidate, dict) and candidate.get("fact_id")
        }
        rejected = [
            summarize_rejected_fact(
                record=record,
                validator_result=result,
                candidate_by_id=candidate_by_id,
                group_lookup=group_lookup,
            )
            for result in record.get("validator_results", [])
            if isinstance(result, dict) and result.get("accepted") is False
        ]
        if rejected:
            records_with_rejections += 1
        total_rejected_facts += len(rejected)
        for item in rejected:
            if item.get("suggested_decision"):
                suggested_decision_counts[str(item["suggested_decision"])] += 1
        work_records.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "source_url": record.get("source_url"),
                "advisory_date": record.get("advisory_date"),
                "advisory_number": record.get("advisory_number"),
                "candidate_subject_class": record.get("candidate_subject_class"),
                "annotation_status": status,
                "candidate_fact_count": record.get("candidate_fact_count", 0),
                "accepted_fact_count": record.get("accepted_fact_count", 0),
                "rejected_fact_count": len(rejected),
                "source_text_excerpt": record.get("source_text_excerpt", ""),
                "required_tasks": [
                    "mark valid candidate facts",
                    "mark invalid candidate fact IDs",
                    "add missing gold facts with evidence_text",
                    "adjudicate validator-rejected facts",
                ],
                "rejected_facts_to_adjudicate": rejected,
            }
        )

    return {
        "source_family": "nasa_atmonto_gold_review_worklist",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "annotation_guide": "docs/nasa_atmonto_gold_annotation_guide.md",
        "selected_source_id_count": len(manifest["selected_source_ids"]),
        "record_count": len(work_records),
        "records_with_rejections": records_with_rejections,
        "total_rejected_facts_to_adjudicate": total_rejected_facts,
        "status_counts": dict(sorted(status_counts.items())),
        "candidate_subject_class_counts": dict(sorted(class_counts.items())),
        "suggested_decision_counts": dict(sorted(suggested_decision_counts.items())),
        "records": work_records,
        "completion_gate": (
            "Use this worklist to complete reviewed gold annotations; scoring still requires "
            "the JSONL template to pass gold annotation validation."
        ),
    }


def gold_review_worklist_markdown(worklist: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Annotation Review Worklist",
        "",
        f"- Gold template: `{worklist['gold_template']}`",
        f"- Annotation guide: `{worklist['annotation_guide']}`",
        f"- Records: {worklist['record_count']}",
        f"- Records with validator rejections: {worklist['records_with_rejections']}",
        f"- Rejected facts to adjudicate: {worklist['total_rejected_facts_to_adjudicate']}",
        f"- Status counts: `{json.dumps(worklist['status_counts'], sort_keys=True)}`",
        f"- Suggested decisions: `{json.dumps(worklist['suggested_decision_counts'], sort_keys=True)}`",
        "",
        "## Review Queue",
        "",
        "| Sample | Source | Class | Candidates | Accepted | Rejected | Status |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for record in worklist["records"]:
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"`{record['candidate_subject_class']}` | "
            f"{record['candidate_fact_count']} | "
            f"{record['accepted_fact_count']} | "
            f"{record['rejected_fact_count']} | "
            f"`{record['annotation_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Rejected Facts Needing Adjudication",
            "",
            "| Sample | Fact | Predicate | Errors | Suggested decision | Evidence |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in worklist["records"]:
        for fact in record["rejected_facts_to_adjudicate"]:
            evidence = compact_text(fact.get("evidence_text"))[:140]
            lines.append(
                "| "
                f"`{record['sample_id']}` | "
                f"`{fact['fact_id']}` | "
                f"`{fact['predicate']}` | "
                f"`{', '.join(fact['errors'])}` | "
                f"`{fact.get('suggested_decision')}` | "
                f"{evidence} |"
            )
    lines.extend(["", "## Completion Gate", "", f"- {worklist['completion_gate']}"])
    return "\n".join(lines).rstrip() + "\n"


def run_gold_review_worklist(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    worklist = build_gold_review_worklist(repo_root)
    write_json(repo_root / GOLD_REVIEW_WORKLIST_JSON, worklist)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).write_text(
        gold_review_worklist_markdown(worklist),
        encoding="utf-8",
    )
    return {
        "worklist_json": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_JSON, repo_root),
        "worklist_markdown": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_MD, repo_root),
        "record_count": worklist["record_count"],
        "records_with_rejections": worklist["records_with_rejections"],
        "total_rejected_facts_to_adjudicate": worklist["total_rejected_facts_to_adjudicate"],
    }


def candidate_review_value(fact: dict[str, Any]) -> object:
    if fact.get("object") not in (None, ""):
        return fact.get("object")
    if fact.get("value") not in (None, ""):
        return fact.get("value")
    properties = fact.get("properties")
    if isinstance(properties, dict) and properties:
        return json.dumps(properties, sort_keys=True, ensure_ascii=False)
    for key, value in sorted(fact.items()):
        if key.startswith("atm:") and value not in (None, ""):
            if isinstance(value, dict):
                return value.get("label") or json.dumps(value, sort_keys=True, ensure_ascii=False)
            return value
    return ""


def candidate_review_predicate(fact: dict[str, Any]) -> str:
    if fact.get("predicate"):
        return term_name(fact.get("predicate"))
    properties = fact.get("properties")
    if isinstance(properties, dict) and len(properties) == 1:
        return term_name(next(iter(properties)))
    if isinstance(properties, dict) and len(properties) > 1:
        return "property_bundle"
    for key in sorted(fact):
        if key.startswith("atm:"):
            return term_name(key)
    return "unmapped_payload"


def candidate_review_object_class(fact: dict[str, Any]) -> str:
    if fact.get("object_class"):
        return term_name(fact.get("object_class"))
    for key, value in sorted(fact.items()):
        if key.startswith("atm:") and isinstance(value, dict) and value.get("type"):
            return term_name(value["type"])
    return ""


def candidate_review_subject_class(fact: dict[str, Any]) -> str:
    return term_name(fact.get("subject_class") or fact.get("type") or "")


def candidate_review_kind(fact: dict[str, Any]) -> str:
    if fact.get("fact_type") in {"object_property", "datatype_property"}:
        return "canonical_fact"
    if isinstance(fact.get("properties"), dict):
        return "property_bundle"
    if any(str(key).startswith("atm:") for key in fact):
        return "schema_shaped_object"
    return "freeform_or_unmapped_fact"


def candidate_review_signature(fact: dict[str, Any]) -> tuple[str, str, str, str, str, str, str]:
    return (
        candidate_review_kind(fact),
        candidate_review_subject_class(fact),
        candidate_review_predicate(fact),
        compact_text(candidate_review_value(fact)).lower(),
        candidate_review_object_class(fact),
        term_name(fact.get("datatype")),
        compact_text(fact.get("evidence_text")).lower(),
    )


def candidate_review_fields(fact: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_kind": candidate_review_kind(fact),
        "subject_class": candidate_review_subject_class(fact),
        "predicate": candidate_review_predicate(fact),
        "value_or_object": candidate_review_value(fact),
        "object_class": candidate_review_object_class(fact),
        "datatype": term_name(fact.get("datatype")),
        "evidence_text": compact_text(fact.get("evidence_text")),
    }


def truncated_candidate_payload(fact: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in sorted(fact.items()):
        if key == "evidence_text":
            payload[key] = compact_text(value)[:500]
        elif isinstance(value, str):
            payload[key] = compact_text(value)[:500]
        else:
            payload[key] = value
    return payload


def validator_results_by_fact_id(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for result in record.get("validator_results", []):
        if isinstance(result, dict) and result.get("fact_id") and str(result["fact_id"]) not in results:
            results[str(result["fact_id"])] = result
    return results


def system_candidate_facts(system: SystemDefinition, record: dict[str, Any]) -> list[dict[str, Any]]:
    field = "candidate_facts" if system.system_id == "S0_rule_only" else "facts"
    return [fact for fact in record.get(field, []) if isinstance(fact, dict)]


def build_system_candidate_review_package(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])

    prediction_records_by_system: dict[str, dict[str, dict[str, Any]]] = {}
    output_status_by_system: dict[str, bool] = {}
    raw_fact_counts_by_system: Counter[str] = Counter()
    for system in SYSTEMS:
        parse_result = read_jsonl_lenient(repo_root / system.expected_output)
        output_status_by_system[system.system_id] = bool(parse_result["exists"])
        records = valid_prediction_records(parse_result, selected_ids) if parse_result["exists"] else []
        prediction_records_by_system[system.system_id] = {
            str(record.get("source_id")): record
            for record in records
            if isinstance(record, dict)
        }
        for record in records:
            raw_fact_counts_by_system[system.system_id] += len(system_candidate_facts(system, record))

    review_records: list[dict[str, Any]] = []
    cluster_count_by_system: Counter[str] = Counter()
    accepted_cluster_count = 0
    rejected_cluster_count = 0
    candidate_kind_counts: Counter[str] = Counter()
    schema_error_counts: Counter[str] = Counter()

    for gold_record in gold_records:
        source_id = str(gold_record.get("source_id"))
        clusters: dict[tuple[str, str, str, str, str, str, str], dict[str, Any]] = {}
        for system in SYSTEMS:
            prediction_record = prediction_records_by_system[system.system_id].get(source_id)
            if not prediction_record:
                continue
            validations = validator_results_by_fact_id(prediction_record)
            for fact in system_candidate_facts(system, prediction_record):
                signature = candidate_review_signature(fact)
                candidate_id = "cand-" + sha1(
                    json.dumps(
                        [source_id, *signature],
                        sort_keys=True,
                        ensure_ascii=False,
                    ).encode("utf-8")
                ).hexdigest()[:16]
                cluster = clusters.setdefault(
                    signature,
                    {
                        "candidate_id": candidate_id,
                        "review_fields": candidate_review_fields(fact),
                        "source_systems": [],
                        "system_observations": [],
                        "schema_status_counts": {},
                        "schema_error_counts": {},
                    },
                )
                if system.system_id not in cluster["source_systems"]:
                    cluster["source_systems"].append(system.system_id)
                fact_id = str(fact.get("fact_id", ""))
                validation = validations.get(fact_id, {})
                accepted = validation.get("accepted")
                errors = [str(error) for error in validation.get("errors", [])]
                status = str(validation.get("status", "not_validated"))
                cluster["system_observations"].append(
                    {
                        "system_id": system.system_id,
                        "fact_id": fact_id,
                        "accepted_by_validator": accepted,
                        "validator_status": status,
                        "validator_errors": errors,
                        "repairs": validation.get("repairs", []),
                        "fact_payload": truncated_candidate_payload(fact),
                    }
                )

        candidate_clusters = []
        for cluster in clusters.values():
            status_counts = Counter(
                observation["validator_status"]
                for observation in cluster["system_observations"]
            )
            error_counts = Counter(
                error
                for observation in cluster["system_observations"]
                for error in observation["validator_errors"]
            )
            source_systems = sorted(cluster["source_systems"])
            for system_id in source_systems:
                cluster_count_by_system[system_id] += 1
            accepted_by_any = any(
                observation["accepted_by_validator"] is True
                for observation in cluster["system_observations"]
            )
            rejected_by_all = all(
                observation["accepted_by_validator"] is False
                for observation in cluster["system_observations"]
                if observation["accepted_by_validator"] is not None
            )
            if accepted_by_any:
                accepted_cluster_count += 1
            elif rejected_by_all:
                rejected_cluster_count += 1
            candidate_kind_counts[str(cluster["review_fields"]["candidate_kind"])] += 1
            schema_error_counts.update(error_counts)
            candidate_clusters.append(
                {
                    **cluster,
                    "source_systems": source_systems,
                    "schema_status_counts": dict(sorted(status_counts.items())),
                    "schema_error_counts": dict(sorted(error_counts.items())),
                    "accepted_by_any_system_validator": accepted_by_any,
                    "rejected_by_all_system_validators": rejected_by_all,
                    "review_action_options": [
                        "accept_as_gold_fact",
                        "reject_semantically",
                        "add_corrected_missing_fact",
                        "ignore_structurally_invalid_payload",
                    ],
                }
            )

        candidate_clusters.sort(key=lambda item: item["candidate_id"])
        review_records.append(
            {
                "sample_id": gold_record.get("sample_id"),
                "source_id": source_id,
                "source_url": gold_record.get("source_url"),
                "candidate_subject_class": gold_record.get("candidate_subject_class"),
                "annotation_status": gold_record.get("gold_annotation", {}).get(
                    "annotation_status"
                ),
                "source_text_excerpt": gold_record.get("source_text_excerpt", ""),
                "candidate_cluster_count": len(candidate_clusters),
                "candidate_clusters": candidate_clusters,
            }
        )

    summary = {
        "source_family": "nasa_atmonto_system_candidate_review",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "candidate_review_jsonl": project_relative_path(
            repo_root / GOLD_CANDIDATE_REVIEW_JSONL,
            repo_root,
        ),
        "candidate_review_markdown": project_relative_path(
            repo_root / GOLD_CANDIDATE_REVIEW_MD,
            repo_root,
        ),
        "selected_source_id_count": len(selected_ids),
        "record_count": len(review_records),
        "system_ids": [system.system_id for system in SYSTEMS],
        "prediction_outputs_exist_by_system": dict(sorted(output_status_by_system.items())),
        "raw_fact_counts_by_system": dict(sorted(raw_fact_counts_by_system.items())),
        "candidate_cluster_count": sum(record["candidate_cluster_count"] for record in review_records),
        "candidate_cluster_counts_by_system": dict(sorted(cluster_count_by_system.items())),
        "accepted_cluster_count": accepted_cluster_count,
        "rejected_cluster_count": rejected_cluster_count,
        "candidate_kind_counts": dict(sorted(candidate_kind_counts.items())),
        "schema_error_counts": dict(sorted(schema_error_counts.items())),
        "records": review_records,
        "completion_gate": (
            "Use this cross-system candidate package during manual gold review so S1-S3 "
            "facts are considered alongside the rule-only baseline. It is not itself "
            "reviewed gold and must not be scored as manual truth."
        ),
    }
    return summary


def system_candidate_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Cross-System Candidate Review",
        "",
        f"- Gold template: `{report['gold_template']}`",
        f"- Candidate review JSONL: `{report['candidate_review_jsonl']}`",
        f"- Records: {report['record_count']}",
        f"- Candidate clusters: {report['candidate_cluster_count']}",
        f"- Raw fact counts by system: `{json.dumps(report['raw_fact_counts_by_system'], sort_keys=True)}`",
        f"- Cluster counts by system: `{json.dumps(report['candidate_cluster_counts_by_system'], sort_keys=True)}`",
        f"- Candidate kinds: `{json.dumps(report['candidate_kind_counts'], sort_keys=True)}`",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Review Queue",
        "",
        "| Sample | Source | Class | Candidate clusters | Status |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for record in report["records"]:
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"`{record['candidate_subject_class']}` | "
            f"{record['candidate_cluster_count']} | "
            f"`{record['annotation_status']}` |"
        )
    lines.extend(
        [
            "",
            "## High-Load Samples",
            "",
            "| Sample | Source | Candidate clusters | Dominant systems |",
            "| --- | --- | ---: | --- |",
        ]
    )
    top_records = sorted(
        report["records"],
        key=lambda item: int(item["candidate_cluster_count"]),
        reverse=True,
    )[:20]
    for record in top_records:
        systems = Counter(
            system_id
            for cluster in record["candidate_clusters"]
            for system_id in cluster["source_systems"]
        )
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"{record['candidate_cluster_count']} | "
            f"`{json.dumps(dict(sorted(systems.items())), sort_keys=True)}` |"
        )
    return "\n".join(lines) + "\n"


def run_system_candidate_review_package(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_system_candidate_review_package(repo_root)
    records = report["records"]
    write_jsonl(repo_root / GOLD_CANDIDATE_REVIEW_JSONL, records)
    (repo_root / GOLD_CANDIDATE_REVIEW_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_CANDIDATE_REVIEW_MD).write_text(
        system_candidate_review_markdown(report),
        encoding="utf-8",
    )
    batch_report = build_gold_review_batches(repo_root, candidate_review=report)
    (repo_root / GOLD_REVIEW_BATCH_DIR).mkdir(parents=True, exist_ok=True)
    for batch in batch_report["batches"]:
        (repo_root / batch["path"]).write_text(
            gold_review_batch_markdown(batch),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_BATCH_INDEX_MD).write_text(
        gold_review_batch_index_markdown(batch_report),
        encoding="utf-8",
    )
    return {
        "candidate_review_jsonl": report["candidate_review_jsonl"],
        "candidate_review_markdown": report["candidate_review_markdown"],
        "batch_index_markdown": batch_report["batch_index_markdown"],
        "batch_count": batch_report["batch_count"],
        "record_count": report["record_count"],
        "candidate_cluster_count": report["candidate_cluster_count"],
        "raw_fact_counts_by_system": report["raw_fact_counts_by_system"],
        "candidate_cluster_counts_by_system": report["candidate_cluster_counts_by_system"],
    }


def markdown_cell(value: object, *, max_chars: int = 180) -> str:
    text = compact_text(value)
    if len(text) > max_chars:
        text = text[: max_chars - 3].rstrip() + "..."
    return text.replace("|", "\\|")


def build_gold_review_batches(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
    candidate_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if candidate_review is None:
        candidate_review = build_system_candidate_review_package(repo_root)
    records = list(candidate_review["records"])
    batches: list[dict[str, Any]] = []
    for start in range(0, len(records), batch_size):
        batch_records = records[start : start + batch_size]
        batch_number = len(batches) + 1
        batch_id = f"batch_{batch_number:02d}"
        candidate_cluster_count = sum(
            int(record.get("candidate_cluster_count", 0)) for record in batch_records
        )
        batches.append(
            {
                "batch_id": batch_id,
                "batch_number": batch_number,
                "path": project_relative_path(
                    repo_root / GOLD_REVIEW_BATCH_DIR / f"{batch_id}.md",
                    repo_root,
                ),
                "record_count": len(batch_records),
                "first_sample_id": batch_records[0]["sample_id"] if batch_records else None,
                "last_sample_id": batch_records[-1]["sample_id"] if batch_records else None,
                "candidate_cluster_count": candidate_cluster_count,
                "records": batch_records,
            }
        )
    return {
        "source_family": "nasa_atmonto_gold_review_batches",
        "batch_size": batch_size,
        "batch_count": len(batches),
        "record_count": len(records),
        "candidate_cluster_count": sum(
            int(record.get("candidate_cluster_count", 0)) for record in records
        ),
        "candidate_review_jsonl": candidate_review["candidate_review_jsonl"],
        "gold_template": candidate_review["gold_template"],
        "batch_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_BATCH_INDEX_MD,
            repo_root,
        ),
        "batches": batches,
        "completion_gate": (
            "Review every batch, then transfer reviewed decisions into "
            "data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl and run "
            "gold validation before freezing the formal gold set."
        ),
    }


def gold_review_batch_markdown(batch: dict[str, Any]) -> str:
    lines = [
        f"# NASA ATMONTO Gold Review {batch['batch_id']}",
        "",
        f"- Samples: `{batch['first_sample_id']}` to `{batch['last_sample_id']}`",
        f"- Records: {batch['record_count']}",
        f"- Candidate clusters: {batch['candidate_cluster_count']}",
        "",
        "## Batch Checklist",
        "",
        "- [ ] Read every source text excerpt and URL when needed.",
        "- [ ] Mark semantically valid candidate facts.",
        "- [ ] Mark semantically invalid candidate fact IDs.",
        "- [ ] Add missing gold facts with evidence text.",
        "- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.",
        "",
    ]
    for record in batch["records"]:
        lines.extend(
            [
                f"## {record['sample_id']} / {record['source_id']}",
                "",
                f"- Source URL: {record.get('source_url')}",
                f"- Candidate class: `{record.get('candidate_subject_class')}`",
                f"- Current status: `{record.get('annotation_status')}`",
                f"- Candidate clusters: {record.get('candidate_cluster_count')}",
                "",
                "Source excerpt:",
                "",
                f"> {markdown_cell(record.get('source_text_excerpt'), max_chars=900)}",
                "",
                "Review actions:",
                "",
                "- [ ] valid facts selected",
                "- [ ] invalid candidate fact IDs selected",
                "- [ ] missing facts added",
                "- [ ] rejected facts adjudicated if applicable",
                "",
                "| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for cluster in record["candidate_clusters"]:
            fields = cluster["review_fields"]
            validator = json.dumps(cluster["schema_status_counts"], sort_keys=True)
            errors = json.dumps(cluster["schema_error_counts"], sort_keys=True)
            lines.append(
                "| "
                f"`{cluster['candidate_id']}` | "
                f"`{', '.join(cluster['source_systems'])}` | "
                f"`{markdown_cell(fields.get('candidate_kind'), max_chars=80)}` | "
                f"`{markdown_cell(fields.get('predicate'), max_chars=80)}` | "
                f"{markdown_cell(fields.get('value_or_object'), max_chars=160)} | "
                f"`{markdown_cell(validator, max_chars=120)}` | "
                f"`{markdown_cell(errors, max_chars=120)}` | "
                f"{markdown_cell(fields.get('evidence_text'), max_chars=220)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def gold_review_batch_index_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Batches",
        "",
        f"- Candidate review: `{report['candidate_review_jsonl']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Records: {report['record_count']}",
        f"- Batches: {report['batch_count']}",
        f"- Candidate clusters: {report['candidate_cluster_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Batches",
        "",
        "| Batch | Samples | Records | Candidate clusters | File |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for batch in report["batches"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['first_sample_id']}`-`{batch['last_sample_id']}` | "
            f"{batch['record_count']} | "
            f"{batch['candidate_cluster_count']} | "
            f"`{batch['path']}` |"
        )
    return "\n".join(lines) + "\n"


def run_gold_review_batches(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    candidate_review = build_system_candidate_review_package(repo_root)
    report = build_gold_review_batches(
        repo_root,
        batch_size=batch_size,
        candidate_review=candidate_review,
    )
    (repo_root / GOLD_REVIEW_BATCH_DIR).mkdir(parents=True, exist_ok=True)
    for batch in report["batches"]:
        (repo_root / batch["path"]).write_text(
            gold_review_batch_markdown(batch),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_BATCH_INDEX_MD).write_text(
        gold_review_batch_index_markdown(report),
        encoding="utf-8",
    )
    return {
        "batch_index_markdown": report["batch_index_markdown"],
        "batch_count": report["batch_count"],
        "record_count": report["record_count"],
        "candidate_cluster_count": report["candidate_cluster_count"],
        "batch_files": [batch["path"] for batch in report["batches"]],
    }


def record_cross_system_cluster_count(record: dict[str, Any]) -> int:
    return sum(
        1
        for cluster in record.get("candidate_clusters", [])
        if isinstance(cluster, dict)
        and any(system != "S0_rule_only" for system in cluster.get("source_systems", []))
    )


def record_workload_score(
    *,
    candidate_cluster_count: int,
    cross_system_cluster_count: int,
    rejected_fact_count: int,
    source_word_count: int,
) -> int:
    return (
        candidate_cluster_count
        + cross_system_cluster_count
        + (rejected_fact_count * 3)
        + (source_word_count // 80)
    )


def review_complexity_tier(workload_score: int) -> str:
    if workload_score <= 40:
        return "light"
    if workload_score <= 65:
        return "medium"
    return "heavy"


def review_priority_lane(record: dict[str, Any]) -> str:
    if int(record["rejected_fact_count"]) > 0:
        return "1_rejection_adjudication"
    if record["complexity_tier"] == "heavy":
        return "2_high_cross_system_coverage"
    return "3_standard_review"


SEMANTIC_GROUP_DEFINITIONS: dict[str, dict[str, str]] = {
    "ground_stop_lifecycle": {
        "label": "Ground stop lifecycle",
        "description": "CDM ground-stop creation, extension, and cancellation notices.",
    },
    "reroute_or_route_constraint": {
        "label": "Reroute or route constraint",
        "description": "Route-required, oceanic-route-closure, reroute-cancellation, CDR, or SWAP advisories.",
    },
    "volcanic_activity_bulletin": {
        "label": "Volcanic activity bulletin",
        "description": "Volcanic-ash advisories carried through ATCSCC as generic traffic-management notices.",
    },
    "ground_delay_program_lifecycle": {
        "label": "Ground delay program lifecycle",
        "description": "CDM ground-delay program, proposed GDP, and GDP cancellation notices.",
    },
    "airport_arrival_or_scheduling_delay": {
        "label": "Airport arrival or scheduling delay",
        "description": "Airport arrival-delay, airport-scheduling-delay, and compacted-demand notices.",
    },
    "hotline_or_webpage_status": {
        "label": "Hotline or webpage status",
        "description": "TCA/hotline page activation or termination status messages.",
    },
    "airport_diversion_recovery": {
        "label": "Airport diversion recovery",
        "description": "Airport diversion-recovery activation notices.",
    },
    "special_or_flow_constraint_fyi": {
        "label": "Special mission or flow-constraint FYI",
        "description": "Planning-only or FYI notices that are not clean active reroute/GDP/GS events.",
    },
    "flight_plan_drop_time_status": {
        "label": "Flight plan drop time status",
        "description": "Extended flight-plan drop-time implementation notices.",
    },
    "other_tmi_status": {
        "label": "Other TMI status",
        "description": "Residual ATCSCC status notices not captured by a higher-precedence group.",
    },
}


def atcscc_advisory_headline(source_text: object) -> str:
    for line in str(source_text or "").splitlines():
        headline = compact_text(line)
        if headline.startswith("ATCSCC ADVZY"):
            return headline
    return ""


def classify_atcscc_semantic_group(headline: str) -> tuple[str, str]:
    text = headline.upper()
    if "VOLCANIC ACTIVITY BULLETIN" in text:
        return "volcanic_activity_bulletin", "headline contains VOLCANIC ACTIVITY BULLETIN"
    if "GROUND DELAY PROGRAM" in text:
        return "ground_delay_program_lifecycle", "headline contains GROUND DELAY PROGRAM"
    if "GROUND STOP" in text or "CDM GS CNX" in text:
        return "ground_stop_lifecycle", "headline contains GROUND STOP or CDM GS CNX"
    if (
        "AIRPORT ARRIVAL DELAYS" in text
        or "AIRPORTS ARRIVAL DELAYS" in text
        or "AIRPORT SCHEDULING DELAYS" in text
    ):
        return (
            "airport_arrival_or_scheduling_delay",
            "headline contains airport arrival/scheduling delay language",
        )
    if (
        "ROUTE RQD" in text
        or "ROUTE CLOSURE" in text
        or "REROUTE" in text
        or "CDRS" in text
        or "SWAP" in text
    ):
        return "reroute_or_route_constraint", "headline contains route, CDR, reroute, or SWAP language"
    if "DIVERSION RECOVERY" in text:
        return "airport_diversion_recovery", "headline contains DIVERSION RECOVERY"
    if "HOTLINE" in text or "WEB PAGE" in text:
        return "hotline_or_webpage_status", "headline contains HOTLINE or WEB PAGE"
    if "FLIGHT PLAN DROP TIMES" in text:
        return "flight_plan_drop_time_status", "headline contains FLIGHT PLAN DROP TIMES"
    if "STARSHIP" in text or "CAPPING TUNNELING" in text:
        return "special_or_flow_constraint_fyi", "headline contains STARSHIP or CAPPING TUNNELING"
    return "other_tmi_status", "no higher-precedence semantic headline rule matched"


def build_gold_semantic_groups(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    workload_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    workload_plan = workload_plan or build_gold_review_workload_plan(repo_root)
    source_records = {record["sample_id"]: record for record in read_jsonl(repo_root / GOLD_TEMPLATE_PATH)}
    group_records: list[dict[str, Any]] = []
    group_counts: Counter[str] = Counter()
    group_class_counts: dict[str, Counter[str]] = {}
    group_date_counts: dict[str, Counter[str]] = {}
    group_priority_counts: dict[str, Counter[str]] = {}
    class_counts: Counter[str] = Counter()
    date_counts: Counter[str] = Counter()

    for review_record in workload_plan["records"]:
        sample_id = str(review_record["sample_id"])
        source_record = source_records.get(sample_id)
        if source_record is None:
            raise ValueError(
                f"sample_id {sample_id!r} found in workload plan but not in gold template"
            )
        headline = atcscc_advisory_headline(source_record.get("source_text"))
        group_id, rationale = classify_atcscc_semantic_group(headline)
        candidate_class = str(review_record.get("candidate_subject_class") or "")
        source_date = str(source_record.get("advisory_date") or str(review_record["source_id"]).split(":", 1)[0])
        priority_lane = str(review_record.get("priority_lane") or "")
        group_counts[group_id] += 1
        class_counts[candidate_class] += 1
        date_counts[source_date] += 1
        group_class_counts.setdefault(group_id, Counter())[candidate_class] += 1
        group_date_counts.setdefault(group_id, Counter())[source_date] += 1
        group_priority_counts.setdefault(group_id, Counter())[priority_lane] += 1
        group_records.append(
            {
                "sample_id": sample_id,
                "source_id": review_record["source_id"],
                "advisory_date": source_date,
                "batch_id": review_record["batch_id"],
                "priority_lane": priority_lane,
                "candidate_subject_class": candidate_class,
                "semantic_group_id": group_id,
                "semantic_group_label": SEMANTIC_GROUP_DEFINITIONS[group_id]["label"],
                "classification_basis": "ATCSCC advisory headline heuristic",
                "classification_rationale": rationale,
                "headline": headline,
            }
        )

    groups = []
    for group_id, count in group_counts.most_common():
        records = [record for record in group_records if record["semantic_group_id"] == group_id]
        groups.append(
            {
                "group_id": group_id,
                "label": SEMANTIC_GROUP_DEFINITIONS[group_id]["label"],
                "description": SEMANTIC_GROUP_DEFINITIONS[group_id]["description"],
                "record_count": count,
                "candidate_subject_class_counts": dict(sorted(group_class_counts[group_id].items())),
                "source_date_counts": dict(sorted(group_date_counts[group_id].items())),
                "priority_lane_counts": dict(sorted(group_priority_counts[group_id].items())),
                "sample_ids": [record["sample_id"] for record in records],
                "example_headlines": [
                    {
                        "sample_id": record["sample_id"],
                        "headline": record["headline"],
                    }
                    for record in records[:5]
                ],
            }
        )

    min_group_count = min(group_counts.values()) if group_counts else 0
    return {
        "source_family": "nasa_atmonto_gold_semantic_groups",
        "status": "ready_for_stratified_reporting",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "workload_plan": project_relative_path(repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD, repo_root),
        "semantic_groups_json": project_relative_path(repo_root / GOLD_SEMANTIC_GROUPS_JSON, repo_root),
        "semantic_groups_markdown": project_relative_path(repo_root / GOLD_SEMANTIC_GROUPS_MD, repo_root),
        "record_count": len(group_records),
        "semantic_group_count": len(groups),
        "semantic_group_counts": dict(group_counts.most_common()),
        "candidate_subject_class_counts": dict(sorted(class_counts.items())),
        "source_date_counts": dict(sorted(date_counts.items())),
        "minimum_semantic_group_count": min_group_count,
        "records": group_records,
        "groups": groups,
        "use_in_experiment": (
            "Use these groups for stratified error analysis and per-group reporting. "
            "They are not train/dev/test splits and do not create gold truth by themselves."
        ),
        "limitations": [
            "Grouping is based on deterministic headline heuristics, not domain-expert taxonomy.",
            "Small groups should be merged or reported descriptively if confidence intervals are unstable.",
            "Ontology candidate classes and operational semantic groups intentionally differ for status/cancellation/FYI notices.",
        ],
    }


def gold_semantic_groups_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Semantic Groups",
        "",
        "## Material Passport",
        "",
        "- Artifact: semantic grouping report for the 100-record ATCSCC gold-set candidate.",
        f"- Gold template: `{report['gold_template']}`",
        f"- Workload plan: `{report['workload_plan']}`",
        "- Classification method: deterministic ATCSCC advisory headline heuristics.",
        "- Boundary: grouping is for stratified analysis; it is not an annotation decision and not a train/dev/test split.",
        "",
        "## Summary",
        "",
        f"- Records: {report['record_count']}",
        f"- Semantic groups: {report['semantic_group_count']}",
        f"- Minimum group size: {report['minimum_semantic_group_count']}",
        f"- Candidate class counts: `{json.dumps(report['candidate_subject_class_counts'], sort_keys=True)}`",
        f"- Source-date counts: `{json.dumps(report['source_date_counts'], sort_keys=True)}`",
        "",
        "## Semantic Groups",
        "",
        "| Group | Label | Records | Candidate classes | Priority lanes | Example samples |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for group in report["groups"]:
        lines.append(
            "| "
            f"`{group['group_id']}` | "
            f"{group['label']} | "
            f"{group['record_count']} | "
            f"`{json.dumps(group['candidate_subject_class_counts'], sort_keys=True)}` | "
            f"`{json.dumps(group['priority_lane_counts'], sort_keys=True)}` | "
            f"`{', '.join(group['sample_ids'][:8])}` |"
        )

    lines.extend(
        [
            "",
            "## Records",
            "",
            "| Sample | Source | Date | Batch | Candidate class | Semantic group | Headline |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"`{record['advisory_date']}` | "
            f"`{record['batch_id']}` | "
            f"`{record['candidate_subject_class']}` | "
            f"`{record['semantic_group_id']}` | "
            f"{record['headline']} |"
        )
    lines.extend(["", "## Use In Experiment", "", f"- {report['use_in_experiment']}", ""])
    lines.append("## Limitations")
    lines.append("")
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    return "\n".join(lines).rstrip() + "\n"


def estimate_review_minutes(
    *,
    candidate_cluster_count: int,
    cross_system_cluster_count: int,
    rejected_fact_count: int,
    source_word_count: int,
) -> int:
    return (
        3
        + ceil_div(candidate_cluster_count, 4)
        + ceil_div(cross_system_cluster_count, 6)
        + (rejected_fact_count * 2)
        + ceil_div(source_word_count, 120)
    )


def build_gold_review_workload_plan(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    worklist = build_gold_review_worklist(repo_root)
    candidate_review = build_system_candidate_review_package(repo_root)
    batch_report = build_gold_review_batches(
        repo_root,
        batch_size=batch_size,
        candidate_review=candidate_review,
    )
    worklist_by_sample = {record["sample_id"]: record for record in worklist["records"]}
    batch_by_sample: dict[str, str] = {}
    for batch in batch_report["batches"]:
        for record in batch["records"]:
            batch_by_sample[str(record["sample_id"])] = str(batch["batch_id"])

    workload_records: list[dict[str, Any]] = []
    complexity_counts: Counter[str] = Counter()
    lane_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()

    for candidate_record in candidate_review["records"]:
        sample_id = str(candidate_record["sample_id"])
        work_record = worklist_by_sample[sample_id]
        candidate_cluster_count = int(candidate_record.get("candidate_cluster_count", 0))
        cross_system_count = record_cross_system_cluster_count(candidate_record)
        rejected_fact_count = int(work_record.get("rejected_fact_count", 0))
        source_word_count = len(compact_text(candidate_record.get("source_text_excerpt")).split())
        workload_score = record_workload_score(
            candidate_cluster_count=candidate_cluster_count,
            cross_system_cluster_count=cross_system_count,
            rejected_fact_count=rejected_fact_count,
            source_word_count=source_word_count,
        )
        estimated_minutes = estimate_review_minutes(
            candidate_cluster_count=candidate_cluster_count,
            cross_system_cluster_count=cross_system_count,
            rejected_fact_count=rejected_fact_count,
            source_word_count=source_word_count,
        )
        record = {
            "sample_id": sample_id,
            "source_id": candidate_record.get("source_id"),
            "batch_id": batch_by_sample[sample_id],
            "candidate_subject_class": candidate_record.get("candidate_subject_class"),
            "annotation_status": work_record.get("annotation_status"),
            "candidate_cluster_count": candidate_cluster_count,
            "cross_system_candidate_cluster_count": cross_system_count,
            "rejected_fact_count": rejected_fact_count,
            "source_word_count": source_word_count,
            "workload_score": workload_score,
            "complexity_tier": review_complexity_tier(workload_score),
            "estimated_review_minutes": estimated_minutes,
        }
        record["priority_lane"] = review_priority_lane(record)
        complexity_counts[str(record["complexity_tier"])] += 1
        lane_counts[str(record["priority_lane"])] += 1
        class_counts[str(record["candidate_subject_class"])] += 1
        workload_records.append(record)

    records_by_sample = {record["sample_id"]: record for record in workload_records}
    batch_summaries: list[dict[str, Any]] = []
    for batch in batch_report["batches"]:
        records = [records_by_sample[str(record["sample_id"])] for record in batch["records"]]
        batch_summaries.append(
            {
                "batch_id": batch["batch_id"],
                "path": batch["path"],
                "record_count": len(records),
                "first_sample_id": batch["first_sample_id"],
                "last_sample_id": batch["last_sample_id"],
                "candidate_cluster_count": sum(
                    int(record["candidate_cluster_count"]) for record in records
                ),
                "cross_system_candidate_cluster_count": sum(
                    int(record["cross_system_candidate_cluster_count"]) for record in records
                ),
                "rejected_fact_count": sum(int(record["rejected_fact_count"]) for record in records),
                "estimated_review_minutes": sum(
                    int(record["estimated_review_minutes"]) for record in records
                ),
                "complexity_counts": dict(
                    sorted(Counter(str(record["complexity_tier"]) for record in records).items())
                ),
                "priority_lane_counts": dict(
                    sorted(Counter(str(record["priority_lane"]) for record in records).items())
                ),
            }
        )

    review_order = sorted(
        workload_records,
        key=lambda record: (
            str(record["priority_lane"]),
            -int(record["rejected_fact_count"]),
            -int(record["workload_score"]),
            str(record["sample_id"]),
        ),
    )
    total_minutes = sum(int(record["estimated_review_minutes"]) for record in workload_records)
    return {
        "source_family": "nasa_atmonto_gold_review_workload_plan",
        "gold_template": worklist["gold_template"],
        "worklist_markdown": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_MD, repo_root),
        "candidate_review_jsonl": candidate_review["candidate_review_jsonl"],
        "batch_index_markdown": batch_report["batch_index_markdown"],
        "decision_templates": project_relative_path(repo_root / GOLD_REVIEW_DECISION_INDEX_MD, repo_root),
        "progress_markdown": project_relative_path(repo_root / GOLD_REVIEW_PROGRESS_MD, repo_root),
        "record_count": len(workload_records),
        "batch_count": batch_report["batch_count"],
        "records_with_rejections": worklist["records_with_rejections"],
        "total_rejected_facts_to_adjudicate": worklist[
            "total_rejected_facts_to_adjudicate"
        ],
        "estimated_total_review_minutes": total_minutes,
        "estimated_total_review_hours": round(total_minutes / 60, 2),
        "complexity_counts": dict(sorted(complexity_counts.items())),
        "priority_lane_counts": dict(sorted(lane_counts.items())),
        "candidate_subject_class_counts": dict(sorted(class_counts.items())),
        "records": workload_records,
        "recommended_review_order": review_order,
        "batches": batch_summaries,
        "completion_gate": (
            "All 100 records still need source-reviewed decisions before semantic scoring; "
            "this workload plan only prioritizes manual review and does not create gold truth."
        ),
    }


def gold_review_workload_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Workload Plan",
        "",
        f"- Gold template: `{plan['gold_template']}`",
        f"- Worklist: `{plan['worklist_markdown']}`",
        f"- Candidate review: `{plan['candidate_review_jsonl']}`",
        f"- Batch index: `{plan['batch_index_markdown']}`",
        f"- Decision templates: `{plan['decision_templates']}`",
        f"- Progress tracker: `{plan['progress_markdown']}`",
        f"- Records: {plan['record_count']}",
        f"- Batches: {plan['batch_count']}",
        f"- Records with validator rejections: {plan['records_with_rejections']}",
        f"- Rejected facts to adjudicate: {plan['total_rejected_facts_to_adjudicate']}",
        f"- Estimated total review time: {plan['estimated_total_review_minutes']} minutes "
        f"({plan['estimated_total_review_hours']} hours)",
        f"- Complexity counts: `{json.dumps(plan['complexity_counts'], sort_keys=True)}`",
        f"- Priority lanes: `{json.dumps(plan['priority_lane_counts'], sort_keys=True)}`",
        "",
        "## Priority Lanes",
        "",
        "| Lane | Meaning |",
        "| --- | --- |",
        "| `1_rejection_adjudication` | Review first: these records need both semantic gold decisions and rejected-fact adjudications. |",
        "| `2_high_cross_system_coverage` | Review next: no pilot rejection, but many cross-system candidate alternatives need source checks. |",
        "| `3_standard_review` | Complete after the higher-workload lanes; still required for final recall/F1. |",
        "",
        "## Batch Workload",
        "",
        "| Batch | Samples | Records | Clusters | Cross-system clusters | Rejected facts | Est. min | Complexity | Lanes | File |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for batch in plan["batches"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['first_sample_id']}`-`{batch['last_sample_id']}` | "
            f"{batch['record_count']} | "
            f"{batch['candidate_cluster_count']} | "
            f"{batch['cross_system_candidate_cluster_count']} | "
            f"{batch['rejected_fact_count']} | "
            f"{batch['estimated_review_minutes']} | "
            f"`{json.dumps(batch['complexity_counts'], sort_keys=True)}` | "
            f"`{json.dumps(batch['priority_lane_counts'], sort_keys=True)}` | "
            f"`{batch['path']}` |"
        )
    lines.extend(
        [
            "",
            "## Recommended Review Order",
            "",
            "| Order | Sample | Batch | Lane | Tier | Score | Est. min | Clusters | Cross-system | Rejected | Class |",
            "| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for index, record in enumerate(plan["recommended_review_order"], start=1):
        lines.append(
            "| "
            f"{index} | "
            f"`{record['sample_id']}` | "
            f"`{record['batch_id']}` | "
            f"`{record['priority_lane']}` | "
            f"`{record['complexity_tier']}` | "
            f"{record['workload_score']} | "
            f"{record['estimated_review_minutes']} | "
            f"{record['candidate_cluster_count']} | "
            f"{record['cross_system_candidate_cluster_count']} | "
            f"{record['rejected_fact_count']} | "
            f"`{record['candidate_subject_class']}` |"
        )
    lines.extend(["", "## Completion Gate", "", f"- {plan['completion_gate']}"])
    return "\n".join(lines).rstrip() + "\n"


def run_gold_review_workload_plan(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    plan = build_gold_review_workload_plan(repo_root)
    write_json(repo_root / GOLD_REVIEW_WORKLOAD_PLAN_JSON, plan)
    (repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD).write_text(
        gold_review_workload_plan_markdown(plan),
        encoding="utf-8",
    )
    return {
        "workload_plan_json": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_JSON,
            repo_root,
        ),
        "workload_plan_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD,
            repo_root,
        ),
        "record_count": plan["record_count"],
        "batch_count": plan["batch_count"],
        "estimated_total_review_minutes": plan["estimated_total_review_minutes"],
        "complexity_counts": plan["complexity_counts"],
        "priority_lane_counts": plan["priority_lane_counts"],
    }


def decision_progress_record_lookup(
    decision_progress: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for batch in decision_progress.get("batch_progress", []):
        if not isinstance(batch, dict):
            continue
        for record in batch.get("records", []):
            if isinstance(record, dict) and record.get("source_id"):
                records[str(record["source_id"])] = record
    return records


def review_session_id(index: int) -> str:
    return f"session_{index:02d}"


def gold_review_session_summary(
    *,
    session_id: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    status_counts = Counter(str(record["decision_status"]) for record in records)
    if status_counts.get("needs_revision"):
        status = "needs_revision"
    elif records and status_counts.get("ready_to_apply", 0) == len(records):
        status = "ready_to_apply"
    elif status_counts.get("ready_to_apply") or status_counts.get("in_progress"):
        status = "in_progress"
    else:
        status = "pending_manual_review"
    return {
        "session_id": session_id,
        "status": status,
        "record_count": len(records),
        "ready_to_apply_record_count": status_counts.get("ready_to_apply", 0),
        "remaining_record_count": len(records) - status_counts.get("ready_to_apply", 0),
        "estimated_review_minutes": sum(
            int(record["estimated_review_minutes"]) for record in records
        ),
        "rejected_fact_count": sum(int(record["rejected_fact_count"]) for record in records),
        "pending_rejected_fact_decision_count": sum(
            int(record["pending_rejected_fact_decision_count"]) for record in records
        ),
        "priority_lane_counts": dict(
            sorted(Counter(str(record["priority_lane"]) for record in records).items())
        ),
        "decision_status_counts": dict(sorted(status_counts.items())),
        "records": records,
    }


def build_gold_review_session_plan(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    target_session_minutes: int = 90,
    workload_plan: dict[str, Any] | None = None,
    decision_progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    workload_plan = workload_plan or build_gold_review_workload_plan(repo_root)
    decision_progress = decision_progress or build_gold_review_decision_progress(repo_root)
    progress_by_source_id = decision_progress_record_lookup(decision_progress)
    review_records: list[dict[str, Any]] = []
    for record in workload_plan["recommended_review_order"]:
        progress = progress_by_source_id.get(str(record.get("source_id")), {})
        progress_status = progress.get("status", "not_started")
        review_records.append(
            {
                **record,
                "decision_status": progress_status,
                "decision_issue_count": progress.get("issue_count", 0),
                "pending_rejected_fact_decision_count": progress.get(
                    "rejected_fact_decisions",
                    {},
                ).get("pending", 0),
                "decision_template": project_relative_path(
                    repo_root / GOLD_REVIEW_DECISION_DIR / f"{record['batch_id']}.jsonl",
                    repo_root,
                ),
                "priority_packet": project_relative_path(
                    repo_root
                    / GOLD_REVIEW_PRIORITY_PACKET_DIR
                    / f"{record['priority_lane']}.md",
                    repo_root,
                ),
            }
        )

    sessions: list[dict[str, Any]] = []
    current_records: list[dict[str, Any]] = []
    current_minutes = 0
    for record in review_records:
        minutes = int(record["estimated_review_minutes"])
        if current_records and current_minutes + minutes > target_session_minutes:
            sessions.append(
                gold_review_session_summary(
                    session_id=review_session_id(len(sessions) + 1),
                    records=current_records,
                )
            )
            current_records = []
            current_minutes = 0
        current_records.append(record)
        current_minutes += minutes
    if current_records:
        sessions.append(
            gold_review_session_summary(
                session_id=review_session_id(len(sessions) + 1),
                records=current_records,
            )
        )
    remaining_records = [
        record for record in review_records if record["decision_status"] != "ready_to_apply"
    ]
    next_session = next(
        (session for session in sessions if session["status"] != "ready_to_apply"),
        None,
    )

    return {
        "source_family": "nasa_atmonto_gold_review_session_plan",
        "status": "ready_for_manual_review" if remaining_records else "ready_to_apply",
        "workload_plan": project_relative_path(repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD, repo_root),
        "decision_progress": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD,
            repo_root,
        ),
        "session_plan_json": project_relative_path(
            repo_root / GOLD_REVIEW_SESSION_PLAN_JSON,
            repo_root,
        ),
        "session_plan_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_SESSION_PLAN_MD,
            repo_root,
        ),
        "target_session_minutes": target_session_minutes,
        "record_count": len(review_records),
        "ready_to_apply_record_count": len(review_records) - len(remaining_records),
        "remaining_record_count": len(remaining_records),
        "estimated_remaining_review_minutes": sum(
            int(record["estimated_review_minutes"]) for record in remaining_records
        ),
        "session_count": len(sessions),
        "completed_session_count": sum(
            1 for session in sessions if session["status"] == "ready_to_apply"
        ),
        "next_session": next_session,
        "sessions": sessions,
        "completion_gate": (
            "Session plans are manual-review queues only. A record becomes gold only after "
            "the reviewer confirms decisions in review_decisions JSONL, applies the draft, "
            "validates annotations, and freezes the reviewed gold set."
        ),
    }


def gold_review_session_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Session Plan",
        "",
        f"- Status: `{plan['status']}`",
        f"- Workload plan: `{plan['workload_plan']}`",
        f"- Decision progress: `{plan['decision_progress']}`",
        f"- Target session length: {plan['target_session_minutes']} minutes",
        f"- Ready-to-apply records: {plan['ready_to_apply_record_count']}",
        f"- Remaining records: {plan['remaining_record_count']}",
        f"- Estimated remaining review time: {plan['estimated_remaining_review_minutes']} minutes",
        f"- Completed sessions: {plan['completed_session_count']} / {plan['session_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {plan['completion_gate']}",
        "",
    ]
    if not plan["sessions"]:
        return "\n".join(lines + ["## Sessions", "", "- No remaining review records."]) + "\n"

    next_session = plan.get("next_session")
    if next_session:
        lines.extend(
            [
                "## Next Session",
                "",
                f"- Session: `{next_session['session_id']}`",
                f"- Status: `{next_session['status']}`",
                f"- Records: {next_session['record_count']}",
                f"- Ready / remaining records: {next_session['ready_to_apply_record_count']} / {next_session['remaining_record_count']}",
                f"- Estimated minutes: {next_session['estimated_review_minutes']}",
                f"- Pending rejected-fact decisions: {next_session['pending_rejected_fact_decision_count']}",
                "",
                "| Order | Sample | Source | Status | Batch | Lane | Est. min | Rejected pending | Decision file | Priority packet |",
                "| ---: | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
            ]
        )
        for index, record in enumerate(next_session["records"], start=1):
            lines.append(
                "| "
                f"{index} | "
                f"`{record['sample_id']}` | "
                f"`{record['source_id']}` | "
                f"`{record['decision_status']}` | "
                f"`{record['batch_id']}` | "
                f"`{record['priority_lane']}` | "
                f"{record['estimated_review_minutes']} | "
                f"{record['pending_rejected_fact_decision_count']} | "
                f"`{record['decision_template']}` | "
                f"`{record['priority_packet']}` |"
            )
    else:
        lines.extend(["## Next Session", "", "- No remaining review records."])

    lines.extend(
        [
            "",
            "## Sessions",
            "",
            "| Session | Status | Records | Ready | Remaining | Est. min | Rejected facts | Pending rejected decisions | Lanes |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for session in plan["sessions"]:
        lines.append(
            "| "
            f"`{session['session_id']}` | "
            f"`{session['status']}` | "
            f"{session['record_count']} | "
            f"{session['ready_to_apply_record_count']} | "
            f"{session['remaining_record_count']} | "
            f"{session['estimated_review_minutes']} | "
            f"{session['rejected_fact_count']} | "
            f"{session['pending_rejected_fact_decision_count']} | "
            f"`{json.dumps(session['priority_lane_counts'], sort_keys=True)}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def run_gold_review_session_plan(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    plan = build_gold_review_session_plan(repo_root)
    write_json(repo_root / GOLD_REVIEW_SESSION_PLAN_JSON, plan)
    (repo_root / GOLD_REVIEW_SESSION_PLAN_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_SESSION_PLAN_MD).write_text(
        gold_review_session_plan_markdown(plan),
        encoding="utf-8",
    )
    return {
        "session_plan_json": plan["session_plan_json"],
        "session_plan_markdown": plan["session_plan_markdown"],
        "status": plan["status"],
        "ready_to_apply_record_count": plan["ready_to_apply_record_count"],
        "remaining_record_count": plan["remaining_record_count"],
        "session_count": plan["session_count"],
        "completed_session_count": plan["completed_session_count"],
    }


def priority_lane_label(lane: str) -> str:
    labels = {
        "1_rejection_adjudication": "Rejected-fact adjudication first",
        "2_high_cross_system_coverage": "High cross-system candidate coverage",
        "3_standard_review": "Standard source review",
    }
    return labels.get(lane, lane)


def cluster_copy_ids(cluster: dict[str, Any]) -> dict[str, list[str]]:
    s0_ids: list[str] = []
    cross_system_ids: list[str] = []
    all_ids: list[str] = []
    for observation in cluster.get("system_observations", []):
        if not isinstance(observation, dict):
            continue
        fact_id = str(observation.get("fact_id", ""))
        if not fact_id:
            continue
        all_ids.append(fact_id)
        system_id = str(observation.get("system_id", ""))
        if system_id == "S0_rule_only":
            s0_ids.append(fact_id)
        elif observation.get("accepted_by_validator") is True:
            cross_system_ids.append(fact_id)
    return {
        "s0_fact_ids": sorted(set(s0_ids)),
        "schema_valid_cross_system_fact_ids": sorted(set(cross_system_ids)),
        "all_fact_ids": sorted(set(all_ids)),
    }


def review_packet_candidate_cluster(cluster: dict[str, Any]) -> dict[str, Any]:
    copy_ids = cluster_copy_ids(cluster)
    return {
        "candidate_id": cluster.get("candidate_id"),
        "source_systems": cluster.get("source_systems", []),
        "schema_status_counts": cluster.get("schema_status_counts", {}),
        "schema_error_counts": cluster.get("schema_error_counts", {}),
        "accepted_by_any_system_validator": cluster.get("accepted_by_any_system_validator"),
        "rejected_by_all_system_validators": cluster.get("rejected_by_all_system_validators"),
        "review_fields": cluster.get("review_fields", {}),
        **copy_ids,
    }


def build_gold_review_priority_packets(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    workload_plan = build_gold_review_workload_plan(repo_root, batch_size=batch_size)
    candidate_review = build_system_candidate_review_package(repo_root)
    worklist = build_gold_review_worklist(repo_root)
    candidate_by_sample = {
        str(record["sample_id"]): record for record in candidate_review["records"]
    }
    worklist_by_sample = {str(record["sample_id"]): record for record in worklist["records"]}

    lanes: dict[str, dict[str, Any]] = {}
    for workload_record in workload_plan["recommended_review_order"]:
        lane_id = str(workload_record["priority_lane"])
        sample_id = str(workload_record["sample_id"])
        candidate_record = candidate_by_sample[sample_id]
        work_record = worklist_by_sample[sample_id]
        lane = lanes.setdefault(
            lane_id,
            {
                "lane_id": lane_id,
                "label": priority_lane_label(lane_id),
                "path": project_relative_path(
                    repo_root / GOLD_REVIEW_PRIORITY_PACKET_DIR / f"{lane_id}.md",
                    repo_root,
                ),
                "records": [],
            },
        )
        decision_template = (
            GOLD_REVIEW_DECISION_DIR / f"{workload_record['batch_id']}.jsonl"
        )
        lane["records"].append(
            {
                **workload_record,
                "source_url": candidate_record.get("source_url"),
                "source_text_excerpt": candidate_record.get("source_text_excerpt", ""),
                "decision_template": project_relative_path(
                    repo_root / decision_template,
                    repo_root,
                ),
                "batch_markdown": project_relative_path(
                    repo_root / GOLD_REVIEW_BATCH_DIR / f"{workload_record['batch_id']}.md",
                    repo_root,
                ),
                "candidate_clusters": [
                    review_packet_candidate_cluster(cluster)
                    for cluster in candidate_record.get("candidate_clusters", [])
                    if isinstance(cluster, dict)
                ],
                "rejected_facts_to_adjudicate": work_record.get(
                    "rejected_facts_to_adjudicate",
                    [],
                ),
            }
        )

    lane_reports: list[dict[str, Any]] = []
    for lane_id in sorted(lanes):
        lane = lanes[lane_id]
        records = lane["records"]
        lane_reports.append(
            {
                **lane,
                "record_count": len(records),
                "estimated_review_minutes": sum(
                    int(record["estimated_review_minutes"]) for record in records
                ),
                "candidate_cluster_count": sum(
                    int(record["candidate_cluster_count"]) for record in records
                ),
                "cross_system_candidate_cluster_count": sum(
                    int(record["cross_system_candidate_cluster_count"])
                    for record in records
                ),
                "rejected_fact_count": sum(
                    int(record["rejected_fact_count"]) for record in records
                ),
            }
        )

    return {
        "source_family": "nasa_atmonto_gold_review_priority_packets",
        "workload_plan": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD,
            repo_root,
        ),
        "candidate_review_jsonl": candidate_review["candidate_review_jsonl"],
        "decision_templates": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_INDEX_MD,
            repo_root,
        ),
        "packet_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
            repo_root,
        ),
        "record_count": workload_plan["record_count"],
        "lane_count": len(lane_reports),
        "priority_lane_counts": workload_plan["priority_lane_counts"],
        "lanes": lane_reports,
        "completion_gate": (
            "Priority packets are reviewer work aids. They do not make a record reviewed; "
            "final decisions must still be entered in review_decisions JSONL and validated."
        ),
    }


def gold_review_priority_packet_index_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Priority Packets",
        "",
        f"- Workload plan: `{report['workload_plan']}`",
        f"- Candidate review: `{report['candidate_review_jsonl']}`",
        f"- Decision templates: `{report['decision_templates']}`",
        f"- Records: {report['record_count']}",
        f"- Priority lanes: `{json.dumps(report['priority_lane_counts'], sort_keys=True)}`",
        "",
        "## Packets",
        "",
        "| Lane | Records | Est. min | Candidate clusters | Cross-system clusters | Rejected facts | File |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for lane in report["lanes"]:
        lines.append(
            "| "
            f"`{lane['lane_id']}` | "
            f"{lane['record_count']} | "
            f"{lane['estimated_review_minutes']} | "
            f"{lane['candidate_cluster_count']} | "
            f"{lane['cross_system_candidate_cluster_count']} | "
            f"{lane['rejected_fact_count']} | "
            f"`{lane['path']}` |"
        )
    lines.extend(["", "## Completion Gate", "", f"- {report['completion_gate']}"])
    return "\n".join(lines).rstrip() + "\n"


def gold_review_priority_packet_summary(report: dict[str, Any]) -> dict[str, Any]:
    lanes: list[dict[str, Any]] = []
    for lane in report["lanes"]:
        lanes.append(
            {
                key: value
                for key, value in lane.items()
                if key != "records"
            }
            | {
                "records": [
                    {
                        key: record[key]
                        for key in (
                            "sample_id",
                            "source_id",
                            "batch_id",
                            "candidate_subject_class",
                            "priority_lane",
                            "complexity_tier",
                            "workload_score",
                            "estimated_review_minutes",
                            "candidate_cluster_count",
                            "cross_system_candidate_cluster_count",
                            "rejected_fact_count",
                            "decision_template",
                            "batch_markdown",
                        )
                    }
                    for record in lane["records"]
                ]
            }
        )
    return {
        key: value
        for key, value in report.items()
        if key not in {"lanes"}
    } | {"lanes": lanes}


def gold_review_priority_packet_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# NASA ATMONTO Gold Review Priority Packet: {packet['lane_id']}",
        "",
        f"- Label: {packet['label']}",
        f"- Records: {packet['record_count']}",
        f"- Estimated review time: {packet['estimated_review_minutes']} minutes",
        f"- Candidate clusters: {packet['candidate_cluster_count']}",
        f"- Cross-system clusters: {packet['cross_system_candidate_cluster_count']}",
        f"- Rejected facts: {packet['rejected_fact_count']}",
        "",
        "## Packet Checklist",
        "",
        "- [ ] Read the source excerpt and open the source URL when the excerpt is insufficient.",
        "- [ ] Copy source-supported S0 IDs into `valid_candidate_fact_ids`.",
        "- [ ] Copy source-supported schema-valid S1-S3 IDs into `valid_cross_system_fact_ids`.",
        "- [ ] Add corrected or missing facts manually when no candidate is source-correct.",
        "- [ ] Complete rejected-fact adjudications when present.",
        "",
    ]
    for record in packet["records"]:
        lines.extend(
            [
                f"## {record['sample_id']} / {record['source_id']}",
                "",
                f"- Batch: `{record['batch_id']}`",
                f"- Decision template: `{record['decision_template']}`",
                f"- Batch checklist: `{record['batch_markdown']}`",
                f"- Priority lane: `{record['priority_lane']}`",
                f"- Complexity: `{record['complexity_tier']}` (score={record['workload_score']}, est={record['estimated_review_minutes']} min)",
                f"- Candidate class: `{record['candidate_subject_class']}`",
                f"- Candidate clusters: {record['candidate_cluster_count']}",
                f"- Cross-system clusters: {record['cross_system_candidate_cluster_count']}",
                f"- Rejected facts: {record['rejected_fact_count']}",
                f"- Source URL: {record.get('source_url')}",
                "",
                "Source excerpt:",
                "",
                f"> {markdown_cell(record.get('source_text_excerpt'), max_chars=900)}",
                "",
            ]
        )
        if record["rejected_facts_to_adjudicate"]:
            lines.extend(
                [
                    "Rejected facts to adjudicate:",
                    "",
                    "| Fact ID | Predicate | Errors | Suggested decision | Evidence |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for fact in record["rejected_facts_to_adjudicate"]:
                lines.append(
                    "| "
                    f"`{fact.get('fact_id')}` | "
                    f"`{fact.get('predicate')}` | "
                    f"`{', '.join(fact.get('errors', []))}` | "
                    f"`{fact.get('suggested_decision')}` | "
                    f"{markdown_cell(fact.get('evidence_text'), max_chars=220)} |"
                )
            lines.append("")
        lines.extend(
            [
                "Candidate clusters:",
                "",
                "| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for cluster in record["candidate_clusters"]:
            fields = cluster["review_fields"]
            lines.append(
                "| "
                f"`{cluster['candidate_id']}` | "
                f"`{', '.join(cluster['source_systems'])}` | "
                f"`{markdown_cell(fields.get('predicate'), max_chars=80)}` | "
                f"{markdown_cell(fields.get('value_or_object'), max_chars=140)} | "
                f"`{', '.join(cluster['s0_fact_ids'])}` | "
                f"`{', '.join(cluster['schema_valid_cross_system_fact_ids'])}` | "
                f"`{markdown_cell(json.dumps(cluster['schema_status_counts'], sort_keys=True), max_chars=100)}` | "
                f"`{markdown_cell(json.dumps(cluster['schema_error_counts'], sort_keys=True), max_chars=100)}` | "
                f"{markdown_cell(fields.get('evidence_text'), max_chars=180)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run_gold_review_priority_packets(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_gold_review_priority_packets(repo_root)
    write_json(repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON, gold_review_priority_packet_summary(report))
    (repo_root / GOLD_REVIEW_PRIORITY_PACKET_DIR).mkdir(parents=True, exist_ok=True)
    for lane in report["lanes"]:
        (repo_root / lane["path"]).write_text(
            gold_review_priority_packet_markdown(lane),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD).write_text(
        gold_review_priority_packet_index_markdown(report),
        encoding="utf-8",
    )
    return {
        "priority_packet_json": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON,
            repo_root,
        ),
        "priority_packet_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
            repo_root,
        ),
        "record_count": report["record_count"],
        "lane_count": report["lane_count"],
        "priority_lane_counts": report["priority_lane_counts"],
        "packet_files": [lane["path"] for lane in report["lanes"]],
    }


def gold_review_record_progress(record: dict[str, Any]) -> dict[str, Any]:
    annotation = record.get("gold_annotation", {})
    status = str(annotation.get("annotation_status", "missing_status"))
    return {
        "sample_id": record.get("sample_id"),
        "source_id": record.get("source_id"),
        "annotation_status": status,
        "review_complete": status == REVIEWED_GOLD_STATUS,
        "valid_fact_count": len(annotation.get("valid_facts", [])),
        "missing_fact_count": len(annotation.get("missing_facts", [])),
        "invalid_candidate_fact_count": len(annotation.get("invalid_candidate_fact_ids", [])),
        "rejected_fact_adjudication_count": len(
            annotation.get("rejected_fact_adjudications", [])
        ),
        "notes_present": bool(str(annotation.get("notes", "")).strip()),
    }


def build_gold_review_progress(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
    batch_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    if batch_report is None:
        batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)
    validation = validate_gold_annotation_records(
        gold_records=gold_records,
        selected_source_ids=selected_ids,
    )
    progress_by_source_id = {
        str(record.get("source_id")): gold_review_record_progress(record)
        for record in gold_records
    }
    batch_progress: list[dict[str, Any]] = []
    for batch in batch_report["batches"]:
        records = [
            progress_by_source_id.get(str(record.get("source_id")))
            for record in batch["records"]
        ]
        concrete_records = [record for record in records if isinstance(record, dict)]
        reviewed_count = sum(1 for record in concrete_records if record["review_complete"])
        pending_count = len(concrete_records) - reviewed_count
        if pending_count == 0 and concrete_records:
            status = "complete"
        elif reviewed_count == 0:
            status = "not_started"
        else:
            status = "in_progress"
        batch_progress.append(
            {
                "batch_id": batch["batch_id"],
                "path": batch["path"],
                "status": status,
                "record_count": len(concrete_records),
                "reviewed_record_count": reviewed_count,
                "pending_record_count": pending_count,
                "candidate_cluster_count": batch["candidate_cluster_count"],
                "first_sample_id": batch["first_sample_id"],
                "last_sample_id": batch["last_sample_id"],
                "records": concrete_records,
            }
        )

    reviewed_total = sum(batch["reviewed_record_count"] for batch in batch_progress)
    pending_total = sum(batch["pending_record_count"] for batch in batch_progress)
    return {
        "source_family": "nasa_atmonto_gold_review_progress",
        "status": (
            "ready_for_freeze"
            if validation["status"] == "ready_for_scoring"
            else "pending_manual_review"
        ),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "batch_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_BATCH_INDEX_MD,
            repo_root,
        ),
        "review_progress_json": project_relative_path(
            repo_root / GOLD_REVIEW_PROGRESS_JSON,
            repo_root,
        ),
        "review_progress_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PROGRESS_MD,
            repo_root,
        ),
        "record_count": len(gold_records),
        "reviewed_record_count": reviewed_total,
        "pending_record_count": pending_total,
        "batch_count": len(batch_progress),
        "complete_batch_count": sum(
            1 for batch in batch_progress if batch["status"] == "complete"
        ),
        "validation_status": validation["status"],
        "validation_error_count": validation["error_count"],
        "validation_warning_count": validation["warning_count"],
        "batch_progress": batch_progress,
        "completion_gate": (
            "All batches must be complete and gold annotation validation must be "
            "ready_for_scoring before freezing atcscc_gold_v1.reviewed.jsonl."
        ),
    }


def gold_review_progress_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Progress",
        "",
        f"- Status: `{report['status']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Batch index: `{report['batch_index_markdown']}`",
        f"- Records: {report['record_count']}",
        f"- Reviewed records: {report['reviewed_record_count']}",
        f"- Pending records: {report['pending_record_count']}",
        f"- Complete batches: {report['complete_batch_count']} / {report['batch_count']}",
        f"- Validation status: `{report['validation_status']}`",
        f"- Validation errors: {report['validation_error_count']}",
        f"- Validation warnings: {report['validation_warning_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Batch Progress",
        "",
        "| Batch | Status | Reviewed | Pending | Candidate clusters | File |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for batch in report["batch_progress"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['status']}` | "
            f"{batch['reviewed_record_count']} | "
            f"{batch['pending_record_count']} | "
            f"{batch['candidate_cluster_count']} | "
            f"`{batch['path']}` |"
        )
    return "\n".join(lines) + "\n"


def run_gold_review_progress(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_gold_review_progress(repo_root, batch_size=batch_size)
    write_json(repo_root / GOLD_REVIEW_PROGRESS_JSON, report)
    (repo_root / GOLD_REVIEW_PROGRESS_MD).write_text(
        gold_review_progress_markdown(report),
        encoding="utf-8",
    )
    return {
        "review_progress_json": report["review_progress_json"],
        "review_progress_markdown": report["review_progress_markdown"],
        "status": report["status"],
        "reviewed_record_count": report["reviewed_record_count"],
        "pending_record_count": report["pending_record_count"],
        "complete_batch_count": report["complete_batch_count"],
        "batch_count": report["batch_count"],
    }


def rejection_adjudication_decision_lookup(
    rejection_adjudication: dict[str, Any],
) -> dict[tuple[str, tuple[str, ...]], dict[str, Any]]:
    lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
    for group in rejection_adjudication.get("groups", []):
        predicate = str(group.get("predicate", ""))
        errors = tuple(str(error) for error in group.get("errors", []))
        lookup[(predicate, errors)] = group
    return lookup


def rejected_fact_decision_template(
    record: dict[str, Any],
    *,
    rejection_adjudication_lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]]
    | None = None,
) -> list[dict[str, Any]]:
    candidate_by_id = {
        str(candidate.get("fact_id")): candidate
        for candidate in record.get("candidate_facts", [])
        if isinstance(candidate, dict) and candidate.get("fact_id")
    }
    templates: list[dict[str, Any]] = []
    for result in record.get("validator_results", []):
        if not isinstance(result, dict) or result.get("accepted") is not False:
            continue
        fact_id = str(result.get("fact_id", ""))
        candidate = candidate_by_id.get(fact_id, {})
        predicate = term_name(candidate.get("predicate"))
        errors = tuple(str(error) for error in result.get("errors", []))
        suggestion = (
            (rejection_adjudication_lookup or {}).get((predicate, errors), {})
        )
        templates.append(
            {
                "fact_id": fact_id,
                "predicate": predicate,
                "errors": list(errors),
                "evidence_text": compact_text(candidate.get("evidence_text")),
                "decision": "",
                "rationale": "",
                "recommended_action": "",
                "suggested_decision": suggestion.get("final_decision", ""),
                "suggested_confidence": suggestion.get("confidence", ""),
                "suggested_rationale": suggestion.get("decision_basis", ""),
                "suggested_recommended_action": suggestion.get("required_follow_up", ""),
            }
        )
    return templates


def validator_accepted_candidate_fact_ids(record: dict[str, Any]) -> list[str]:
    candidate_fact_ids = [
        str(candidate.get("fact_id"))
        for candidate in record.get("candidate_facts", [])
        if isinstance(candidate, dict) and candidate.get("fact_id")
    ]
    accepted_fact_ids = {
        str(result.get("fact_id"))
        for result in record.get("validator_results", [])
        if isinstance(result, dict)
        and result.get("accepted") is True
        and result.get("fact_id")
    }
    return [fact_id for fact_id in candidate_fact_ids if fact_id in accepted_fact_ids]


def cross_system_candidate_options(record: dict[str, Any]) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for cluster in record.get("candidate_clusters", []):
        if not isinstance(cluster, dict):
            continue
        review_fields = cluster.get("review_fields", {})
        for observation in cluster.get("system_observations", []):
            if not isinstance(observation, dict):
                continue
            system_id = str(observation.get("system_id", ""))
            fact_id = str(observation.get("fact_id", ""))
            if system_id == "S0_rule_only" or not fact_id:
                continue
            if observation.get("accepted_by_validator") is not True:
                continue
            options.append(
                {
                    "fact_id": fact_id,
                    "candidate_id": cluster.get("candidate_id"),
                    "system_id": system_id,
                    "validator_status": observation.get("validator_status"),
                    "review_fields": review_fields,
                }
            )
    return options


def gold_review_decision_record(
    *,
    batch_id: str,
    record: dict[str, Any],
    gold_record: dict[str, Any],
    rejection_adjudication_lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]]
    | None = None,
) -> dict[str, Any]:
    cross_system_options = cross_system_candidate_options(record)
    accepted_candidate_fact_ids = validator_accepted_candidate_fact_ids(gold_record)
    return {
        "batch_id": batch_id,
        "sample_id": record.get("sample_id"),
        "source_id": record.get("source_id"),
        "source_url": record.get("source_url"),
        "annotation_status": PENDING_GOLD_STATUS,
        "annotator_id": "",
        "reviewed_at": "",
        "notes": "",
        "review_checklist": review_checklist_template(),
        "valid_candidate_fact_ids": [],
        "valid_cross_system_fact_ids": [],
        "invalid_candidate_fact_ids": [],
        "missing_facts": [],
        "suggested_valid_candidate_fact_ids": accepted_candidate_fact_ids,
        "rejected_fact_adjudications": rejected_fact_decision_template(
            gold_record,
            rejection_adjudication_lookup=rejection_adjudication_lookup,
        ),
        "review_context": {
            "candidate_cluster_count": record.get("candidate_cluster_count"),
            "candidate_cluster_ids": [
                cluster.get("candidate_id") for cluster in record.get("candidate_clusters", [])
            ],
            "candidate_fact_ids": [
                candidate.get("fact_id")
                for candidate in gold_record.get("candidate_facts", [])
                if isinstance(candidate, dict)
            ],
            "validator_accepted_candidate_fact_ids": accepted_candidate_fact_ids,
            "cross_system_fact_ids": [option["fact_id"] for option in cross_system_options],
            "cross_system_candidate_options": cross_system_options,
        },
        "instructions": (
            "Set annotation_status to reviewed only after source-text review. Put accepted "
            "rule-baseline fact IDs in valid_candidate_fact_ids, rejected rule-baseline IDs "
            "in invalid_candidate_fact_ids, put accepted S1-S3 schema-valid fact IDs in "
            "valid_cross_system_fact_ids, add corrected/manual facts to missing_facts, and "
            "complete every rejected_fact_adjudications decision. Set all review_checklist "
            "items to true only after completing the source-text, semantic-rubric, profile-gap, "
            "and missing-fact checks. The suggested_valid_candidate_fact_ids field lists "
            "validator-accepted S0 facts, and rejected-fact suggested_* fields are copied from "
            "property-level rejection adjudication. All suggestions must be confirmed, edited, "
            "or rejected by the reviewer before scoring."
        ),
    }


def build_gold_review_decision_templates(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
    batch_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    if batch_report is None:
        batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)
    gold_records_by_source_id = {
        str(record.get("source_id")): record for record in read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    }
    rejection_adjudication = build_rejection_adjudication_report(repo_root)
    adjudication_lookup = rejection_adjudication_decision_lookup(rejection_adjudication)
    batches: list[dict[str, Any]] = []
    for batch in batch_report["batches"]:
        decision_records = [
            gold_review_decision_record(
                batch_id=batch["batch_id"],
                record=record,
                gold_record=gold_records_by_source_id[str(record.get("source_id"))],
                rejection_adjudication_lookup=adjudication_lookup,
            )
            for record in batch["records"]
        ]
        batches.append(
            {
                "batch_id": batch["batch_id"],
                "path": project_relative_path(
                    repo_root / GOLD_REVIEW_DECISION_DIR / f"{batch['batch_id']}.jsonl",
                    repo_root,
                ),
                "record_count": len(decision_records),
                "first_sample_id": batch["first_sample_id"],
                "last_sample_id": batch["last_sample_id"],
                "rejected_fact_adjudication_count": sum(
                    len(record["rejected_fact_adjudications"]) for record in decision_records
                ),
                "suggested_valid_candidate_fact_count": sum(
                    len(record["suggested_valid_candidate_fact_ids"])
                    for record in decision_records
                ),
                "records": decision_records,
            }
        )
    return {
        "source_family": "nasa_atmonto_gold_review_decision_templates",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "decision_template_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_INDEX_MD,
            repo_root,
        ),
        "decision_dir": project_relative_path(repo_root / GOLD_REVIEW_DECISION_DIR, repo_root),
        "batch_count": len(batches),
        "record_count": sum(batch["record_count"] for batch in batches),
        "suggested_valid_candidate_fact_count": sum(
            batch["suggested_valid_candidate_fact_count"] for batch in batches
        ),
        "batches": batches,
        "completion_gate": (
            "Decision templates are editable review inputs. Applying them with all records "
            "still pending must not produce reviewed gold; set records to reviewed only after "
            "manual source-text review."
        ),
    }


def gold_review_decision_index_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Decision Templates",
        "",
        f"- Gold template: `{report['gold_template']}`",
        f"- Decision directory: `{report['decision_dir']}`",
        f"- Records: {report['record_count']}",
        f"- Batches: {report['batch_count']}",
        f"- Suggested valid S0 candidate facts: {report['suggested_valid_candidate_fact_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "- `review_checklist` items must all be true before a record can be "
        "applied as reviewed.",
        "- `suggested_valid_candidate_fact_ids` lists S0 facts accepted by the schema "
        "validator; copy only source-supported IDs into `valid_candidate_fact_ids`.",
        "- Rejected-fact `suggested_*` fields are copied from "
        "`reports/stages/nasa_atmonto_rejection_adjudication.md`; leave `decision`, "
        "`rationale`, and `recommended_action` empty until a reviewer confirms them.",
        "",
        "## Decision Files",
        "",
        "| Batch | Samples | Records | Suggested valid S0 facts | Rejected facts | File |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for batch in report["batches"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['first_sample_id']}`-`{batch['last_sample_id']}` | "
            f"{batch['record_count']} | "
            f"{batch['suggested_valid_candidate_fact_count']} | "
            f"{batch['rejected_fact_adjudication_count']} | "
            f"`{batch['path']}` |"
        )
    return "\n".join(lines) + "\n"


def run_gold_review_decision_templates(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)
    report = build_gold_review_decision_templates(repo_root, batch_report=batch_report)
    (repo_root / GOLD_REVIEW_DECISION_DIR).mkdir(parents=True, exist_ok=True)
    for batch in report["batches"]:
        write_jsonl(repo_root / batch["path"], batch["records"])
    (repo_root / GOLD_REVIEW_DECISION_INDEX_MD).write_text(
        gold_review_decision_index_markdown(report),
        encoding="utf-8",
    )
    return {
        "decision_template_index_markdown": report["decision_template_index_markdown"],
        "decision_dir": report["decision_dir"],
        "batch_count": report["batch_count"],
        "record_count": report["record_count"],
        "decision_files": [batch["path"] for batch in report["batches"]],
    }


def read_gold_review_decisions(decision_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(decision_dir.glob("batch_*.jsonl")):
        records.extend(read_jsonl(path))
    return records


def gold_review_decision_has_manual_edits(decision: dict[str, Any]) -> bool:
    if str(decision.get("annotation_status", PENDING_GOLD_STATUS)) != PENDING_GOLD_STATUS:
        return True
    if str(decision.get("annotator_id", "")).strip():
        return True
    if str(decision.get("reviewed_at", "")).strip():
        return True
    if str(decision.get("notes", "")).strip():
        return True
    checklist = decision.get("review_checklist")
    if isinstance(checklist, dict) and any(checklist.get(field) for field in REVIEW_CHECKLIST_FIELDS):
        return True
    for field in (
        "valid_candidate_fact_ids",
        "valid_cross_system_fact_ids",
        "invalid_candidate_fact_ids",
        "missing_facts",
    ):
        if decision.get(field):
            return True
    for adjudication in decision.get("rejected_fact_adjudications", []):
        if not isinstance(adjudication, dict):
            continue
        if any(
            str(adjudication.get(field, "")).strip()
            for field in ("decision", "rationale", "recommended_action")
        ):
            return True
    return False


def rejection_decision_completion_counts(decision: dict[str, Any]) -> dict[str, int]:
    adjudications = [
        item
        for item in decision.get("rejected_fact_adjudications", [])
        if isinstance(item, dict)
    ]
    completed = 0
    for adjudication in adjudications:
        if (
            str(adjudication.get("decision", "")) in ALLOWED_REJECTION_ADJUDICATIONS
            and str(adjudication.get("rationale", "")).strip()
            and str(adjudication.get("recommended_action", "")).strip()
        ):
            completed += 1
    total = len(adjudications)
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
    }


def build_cross_system_fact_lookup(
    *,
    repo_root: Path,
    selected_ids: set[str],
) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for system in SYSTEMS:
        if system.system_id == "S0_rule_only":
            continue
        parse_result = read_jsonl_lenient(repo_root / system.expected_output)
        if not parse_result["exists"]:
            continue
        for record in valid_prediction_records(parse_result, selected_ids):
            for fact in system_candidate_facts(system, record):
                fact_id = str(fact.get("fact_id", ""))
                if not fact_id:
                    continue
                enriched = dict(fact)
                enriched.setdefault("source_id", record.get("source_id"))
                enriched["source_system_id"] = system.system_id
                enriched["selected_as_gold_from_cross_system_candidate"] = True
                lookup[fact_id] = enriched
    return lookup


def unique_facts_by_id(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for index, fact in enumerate(facts):
        fact_id = str(fact.get("fact_id") or f"manual-missing-{index}")
        if fact_id in seen:
            continue
        seen.add(fact_id)
        unique.append(fact)
    return unique


def apply_gold_review_decision_to_record(
    *,
    gold_record: dict[str, Any],
    decision: dict[str, Any],
    cross_system_fact_lookup: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    source_id = str(gold_record.get("source_id"))
    cross_system_fact_lookup = cross_system_fact_lookup or {}
    candidate_by_id = {
        str(candidate.get("fact_id")): candidate
        for candidate in gold_record.get("candidate_facts", [])
        if isinstance(candidate, dict) and candidate.get("fact_id")
    }
    valid_ids = [str(value) for value in decision.get("valid_candidate_fact_ids", [])]
    cross_system_valid_ids = [
        str(value) for value in decision.get("valid_cross_system_fact_ids", [])
    ]
    invalid_ids = [str(value) for value in decision.get("invalid_candidate_fact_ids", [])]
    unknown_valid = sorted(set(valid_ids) - set(candidate_by_id))
    unknown_cross_system_valid = sorted(
        set(cross_system_valid_ids) - set(cross_system_fact_lookup)
    )
    unknown_invalid = sorted(set(invalid_ids) - set(candidate_by_id))
    if unknown_valid:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "unknown_valid_candidate_fact_ids",
                "fact_ids": unknown_valid,
            }
        )
    if unknown_cross_system_valid:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "unknown_valid_cross_system_fact_ids",
                "fact_ids": unknown_cross_system_valid,
            }
        )
    if unknown_invalid:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "unknown_invalid_candidate_fact_ids",
                "fact_ids": unknown_invalid,
            }
        )
    source_mismatch_ids = sorted(
        fact_id
        for fact_id in cross_system_valid_ids
        if str(cross_system_fact_lookup.get(fact_id, {}).get("source_id")) != source_id
    )
    if source_mismatch_ids:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "valid_cross_system_fact_source_mismatch",
                "fact_ids": source_mismatch_ids,
            }
        )
    if errors:
        return gold_record, errors

    status = str(decision.get("annotation_status", PENDING_GOLD_STATUS))
    if status not in {PENDING_GOLD_STATUS, REVIEWED_GOLD_STATUS}:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "invalid_annotation_status",
                "annotation_status": status,
            }
        )
        return gold_record, errors

    review_checklist = decision.get("review_checklist")
    incomplete_checklist = incomplete_review_checklist_fields(review_checklist)
    if status == REVIEWED_GOLD_STATUS and incomplete_checklist:
        errors.append(
            {
                "source_id": source_id,
                "sample_id": gold_record.get("sample_id"),
                "error": "incomplete_review_checklist",
                "fields": incomplete_checklist,
            }
        )
        return gold_record, errors

    updated = dict(gold_record)
    annotation = dict(updated.get("gold_annotation", {}))
    manual_missing_facts = [
        fact for fact in decision.get("missing_facts", []) if isinstance(fact, dict)
    ]
    cross_system_missing_facts = [
        cross_system_fact_lookup[fact_id] for fact_id in cross_system_valid_ids
    ]
    annotation.update(
        {
            "annotation_status": status,
            "annotator_id": str(decision.get("annotator_id", "")),
            "valid_facts": [candidate_by_id[fact_id] for fact_id in valid_ids],
            "invalid_candidate_fact_ids": invalid_ids,
            "missing_facts": unique_facts_by_id(
                [*manual_missing_facts, *cross_system_missing_facts]
            ),
            "review_checklist": (
                review_checklist_template(True)
                if status == REVIEWED_GOLD_STATUS
                else {
                    field: (
                        isinstance(review_checklist, dict)
                        and review_checklist.get(field) is True
                    )
                    for field in REVIEW_CHECKLIST_FIELDS
                }
            ),
            "rejected_fact_adjudications": [
                adjudication
                for adjudication in decision.get("rejected_fact_adjudications", [])
                if isinstance(adjudication, dict)
            ],
            "notes": str(decision.get("notes", "")),
        }
    )
    updated["gold_annotation"] = annotation
    return updated, []


def gold_review_decision_record_progress(
    *,
    gold_record: dict[str, Any],
    decision: dict[str, Any] | None,
    cross_system_fact_lookup: dict[str, dict[str, Any]],
    duplicate_source_ids: set[str],
) -> dict[str, Any]:
    sample_id = gold_record.get("sample_id")
    source_id = str(gold_record.get("source_id"))
    if decision is None:
        return {
            "sample_id": sample_id,
            "source_id": source_id,
            "annotation_status": "missing_decision_record",
            "status": "missing_decision",
            "manual_edits_present": False,
            "ready_to_apply": False,
            "issue_count": 1,
            "issues": [{"error": "missing_decision_record"}],
            "rejected_fact_decisions": {"total": 0, "completed": 0, "pending": 0},
        }

    errors: list[dict[str, Any]] = []
    if source_id in duplicate_source_ids:
        errors.append({"error": "duplicate_decision_source_id", "source_id": source_id})

    manual_edits_present = gold_review_decision_has_manual_edits(decision)
    rejection_counts = rejection_decision_completion_counts(decision)
    annotation_status = str(decision.get("annotation_status", PENDING_GOLD_STATUS))
    updated, apply_errors = apply_gold_review_decision_to_record(
        gold_record=gold_record,
        decision=decision,
        cross_system_fact_lookup=cross_system_fact_lookup,
    )
    errors.extend(apply_errors)

    if not apply_errors and annotation_status == REVIEWED_GOLD_STATUS:
        validation = validate_gold_annotation_records(
            gold_records=[updated],
            selected_source_ids={source_id},
        )
        errors.extend(validation["errors"])

    if errors:
        status = "needs_revision"
    elif annotation_status == REVIEWED_GOLD_STATUS:
        status = "ready_to_apply"
    elif manual_edits_present:
        status = "in_progress"
    else:
        status = "not_started"

    suggested_valid_candidate_fact_ids = decision.get("suggested_valid_candidate_fact_ids")
    if not isinstance(suggested_valid_candidate_fact_ids, list):
        suggested_valid_candidate_fact_ids = validator_accepted_candidate_fact_ids(gold_record)

    return {
        "sample_id": sample_id,
        "source_id": source_id,
        "annotation_status": annotation_status,
        "status": status,
        "manual_edits_present": manual_edits_present,
        "ready_to_apply": status == "ready_to_apply",
        "issue_count": len(errors),
        "issues": errors[:20],
        "suggested_valid_candidate_fact_count": len(suggested_valid_candidate_fact_ids),
        "rejected_fact_decisions": rejection_counts,
    }


def build_gold_review_decision_progress(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
    batch_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    if batch_report is None:
        batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)

    decision_root = repo_root / GOLD_REVIEW_DECISION_DIR
    decisions = read_gold_review_decisions(decision_root) if decision_root.exists() else []
    decision_source_ids = [str(decision.get("source_id")) for decision in decisions]
    duplicate_source_ids = {
        source_id for source_id, count in Counter(decision_source_ids).items() if count > 1
    }
    decisions_by_source_id = {
        str(decision.get("source_id")): decision
        for decision in decisions
        if decision.get("source_id")
    }
    gold_records_by_source_id = {
        str(record.get("source_id")): record for record in gold_records
    }
    cross_system_fact_lookup = build_cross_system_fact_lookup(
        repo_root=repo_root,
        selected_ids=selected_ids,
    )

    progress_by_source_id: dict[str, dict[str, Any]] = {}
    for source_id, gold_record in gold_records_by_source_id.items():
        progress_by_source_id[source_id] = gold_review_decision_record_progress(
            gold_record=gold_record,
            decision=decisions_by_source_id.get(source_id),
            cross_system_fact_lookup=cross_system_fact_lookup,
            duplicate_source_ids=duplicate_source_ids,
        )

    missing_decision_source_ids = sorted(set(gold_records_by_source_id) - set(decisions_by_source_id))
    unexpected_decision_source_ids = sorted(set(decisions_by_source_id) - set(gold_records_by_source_id))
    batch_progress: list[dict[str, Any]] = []
    for batch in batch_report["batches"]:
        records = [
            progress_by_source_id[str(record.get("source_id"))]
            for record in batch["records"]
            if str(record.get("source_id")) in progress_by_source_id
        ]
        status_counts = Counter(record["status"] for record in records)
        if status_counts.get("needs_revision", 0):
            status = "needs_revision"
        elif records and status_counts.get("ready_to_apply", 0) == len(records):
            status = "ready_to_apply"
        elif status_counts.get("in_progress", 0) or status_counts.get("ready_to_apply", 0):
            status = "in_progress"
        elif status_counts.get("missing_decision", 0):
            status = "missing_decisions"
        else:
            status = "not_started"
        rejected_counts = Counter()
        suggested_valid_candidate_count = 0
        for record in records:
            rejected_counts.update(record["rejected_fact_decisions"])
            suggested_valid_candidate_count += record["suggested_valid_candidate_fact_count"]
        batch_progress.append(
            {
                "batch_id": batch["batch_id"],
                "decision_path": project_relative_path(
                    repo_root / GOLD_REVIEW_DECISION_DIR / f"{batch['batch_id']}.jsonl",
                    repo_root,
                ),
                "status": status,
                "record_count": len(records),
                "ready_to_apply_record_count": status_counts.get("ready_to_apply", 0),
                "in_progress_record_count": status_counts.get("in_progress", 0),
                "not_started_record_count": status_counts.get("not_started", 0),
                "needs_revision_record_count": status_counts.get("needs_revision", 0),
                "missing_decision_record_count": status_counts.get("missing_decision", 0),
                "suggested_valid_candidate_fact_count": suggested_valid_candidate_count,
                "rejected_fact_decision_count": rejected_counts["total"],
                "completed_rejected_fact_decision_count": rejected_counts["completed"],
                "pending_rejected_fact_decision_count": rejected_counts["pending"],
                "records": records,
            }
        )

    total_status_counts = Counter(
        record["status"] for record in progress_by_source_id.values()
    )
    rejected_totals = Counter()
    suggested_valid_candidate_total = 0
    for record in progress_by_source_id.values():
        rejected_totals.update(record["rejected_fact_decisions"])
        suggested_valid_candidate_total += record["suggested_valid_candidate_fact_count"]
    status = (
        "ready_to_apply"
        if progress_by_source_id
        and total_status_counts.get("ready_to_apply", 0) == len(progress_by_source_id)
        and not unexpected_decision_source_ids
        and not duplicate_source_ids
        else "needs_revision"
        if total_status_counts.get("needs_revision", 0)
        or unexpected_decision_source_ids
        or duplicate_source_ids
        else "in_progress"
        if total_status_counts.get("in_progress", 0)
        or total_status_counts.get("ready_to_apply", 0)
        else "missing_decisions"
        if total_status_counts.get("missing_decision", 0)
        else "not_started"
    )
    return {
        "source_family": "nasa_atmonto_gold_review_decision_progress",
        "status": status,
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "decision_dir": project_relative_path(decision_root, repo_root),
        "decision_progress_json": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON,
            repo_root,
        ),
        "decision_progress_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD,
            repo_root,
        ),
        "record_count": len(gold_records_by_source_id),
        "decision_record_count": len(decisions),
        "ready_to_apply_record_count": total_status_counts.get("ready_to_apply", 0),
        "in_progress_record_count": total_status_counts.get("in_progress", 0),
        "not_started_record_count": total_status_counts.get("not_started", 0),
        "needs_revision_record_count": total_status_counts.get("needs_revision", 0),
        "missing_decision_record_count": total_status_counts.get("missing_decision", 0),
        "duplicate_decision_source_ids": sorted(duplicate_source_ids),
        "missing_decision_source_ids": missing_decision_source_ids,
        "unexpected_decision_source_ids": unexpected_decision_source_ids,
        "suggested_valid_candidate_fact_count": suggested_valid_candidate_total,
        "rejected_fact_decision_count": rejected_totals["total"],
        "completed_rejected_fact_decision_count": rejected_totals["completed"],
        "pending_rejected_fact_decision_count": rejected_totals["pending"],
        "batch_count": len(batch_progress),
        "ready_to_apply_batch_count": sum(
            1 for batch in batch_progress if batch["status"] == "ready_to_apply"
        ),
        "batch_progress": batch_progress,
        "completion_gate": (
            "All 100 decision records must be ready_to_apply before the reviewed draft can "
            "be treated as complete manual gold. Pending suggested_valid_candidate_fact_ids "
            "and rejected-fact suggested_* fields do not count until copied or edited into "
            "reviewer decision fields."
        ),
    }


def gold_review_decision_progress_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Review Decision Progress",
        "",
        f"- Status: `{report['status']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Decision directory: `{report['decision_dir']}`",
        f"- Records: {report['record_count']}",
        f"- Decision records: {report['decision_record_count']}",
        f"- Ready to apply: {report['ready_to_apply_record_count']}",
        f"- In progress: {report['in_progress_record_count']}",
        f"- Not started: {report['not_started_record_count']}",
        f"- Needs revision: {report['needs_revision_record_count']}",
        f"- Missing decisions: {report['missing_decision_record_count']}",
        f"- Suggested valid S0 candidate facts: {report['suggested_valid_candidate_fact_count']}",
        "- Rejected-fact decisions confirmed: "
        f"{report['completed_rejected_fact_decision_count']} / "
        f"{report['rejected_fact_decision_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Batch Progress",
        "",
        "| Batch | Status | Ready | In progress | Not started | Needs revision | "
        "Missing | Suggested valid S0 | Rejected decisions | File |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for batch in report["batch_progress"]:
        lines.append(
            "| "
            f"`{batch['batch_id']}` | "
            f"`{batch['status']}` | "
            f"{batch['ready_to_apply_record_count']} | "
            f"{batch['in_progress_record_count']} | "
            f"{batch['not_started_record_count']} | "
            f"{batch['needs_revision_record_count']} | "
            f"{batch['missing_decision_record_count']} | "
            f"{batch['suggested_valid_candidate_fact_count']} | "
            f"{batch['completed_rejected_fact_decision_count']} / "
            f"{batch['rejected_fact_decision_count']} | "
            f"`{batch['decision_path']}` |"
        )

    attention_records = [
        (batch["batch_id"], record)
        for batch in report["batch_progress"]
        for record in batch["records"]
        if record["status"] != "ready_to_apply"
    ][:25]
    lines.extend(["", "## Records Needing Attention", ""])
    if not attention_records:
        lines.append("- None.")
    else:
        lines.extend(
            [
                "| Batch | Sample | Status | Issues | Rejected pending |",
                "| --- | --- | --- | ---: | ---: |",
            ]
        )
        for batch_id, record in attention_records:
            lines.append(
                "| "
                f"`{batch_id}` | "
                f"`{record['sample_id']}` | "
                f"`{record['status']}` | "
                f"{record['issue_count']} | "
                f"{record['rejected_fact_decisions']['pending']} |"
            )
        remaining = sum(
            1
            for batch in report["batch_progress"]
            for record in batch["records"]
            if record["status"] != "ready_to_apply"
        ) - len(attention_records)
        if remaining > 0:
            lines.append(f"- ... {remaining} more records omitted")

    if report["duplicate_decision_source_ids"]:
        lines.extend(["", "## Duplicate Decision Source IDs", ""])
        lines.append(", ".join(f"`{value}`" for value in report["duplicate_decision_source_ids"]))
    if report["unexpected_decision_source_ids"]:
        lines.extend(["", "## Unexpected Decision Source IDs", ""])
        lines.append(", ".join(f"`{value}`" for value in report["unexpected_decision_source_ids"]))
    return "\n".join(lines) + "\n"


def run_gold_review_decision_progress(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    batch_size: int = 10,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    batch_report = build_gold_review_batches(repo_root, batch_size=batch_size)
    report = build_gold_review_decision_progress(
        repo_root,
        batch_report=batch_report,
    )
    write_json(repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON, report)
    (repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD).write_text(
        gold_review_decision_progress_markdown(report),
        encoding="utf-8",
    )
    return {
        "decision_progress_json": report["decision_progress_json"],
        "decision_progress_markdown": report["decision_progress_markdown"],
        "status": report["status"],
        "ready_to_apply_record_count": report["ready_to_apply_record_count"],
        "in_progress_record_count": report["in_progress_record_count"],
        "not_started_record_count": report["not_started_record_count"],
        "needs_revision_record_count": report["needs_revision_record_count"],
        "missing_decision_record_count": report["missing_decision_record_count"],
        "record_count": report["record_count"],
    }


def apply_gold_review_decisions(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    decision_dir: str | Path = GOLD_REVIEW_DECISION_DIR,
    output_path: str | Path = GOLD_REVIEW_DECISION_DRAFT_PATH,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    decision_root = Path(decision_dir)
    if not decision_root.is_absolute():
        decision_root = repo_root / decision_root
    output = Path(output_path)
    if not output.is_absolute():
        output = repo_root / output

    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    decisions = read_gold_review_decisions(decision_root)
    cross_system_fact_lookup = build_cross_system_fact_lookup(
        repo_root=repo_root,
        selected_ids=selected_ids,
    )
    decisions_by_source_id = {str(decision.get("source_id")): decision for decision in decisions}
    errors: list[dict[str, Any]] = []
    duplicate_source_ids = [
        source_id
        for source_id, count in Counter(str(decision.get("source_id")) for decision in decisions).items()
        if count > 1
    ]
    if duplicate_source_ids:
        errors.append({"error": "duplicate_decision_source_ids", "source_ids": duplicate_source_ids})

    updated_records: list[dict[str, Any]] = []
    for record in gold_records:
        source_id = str(record.get("source_id"))
        decision = decisions_by_source_id.get(source_id)
        if decision is None:
            updated_records.append(record)
            continue
        updated, record_errors = apply_gold_review_decision_to_record(
            gold_record=record,
            decision=decision,
            cross_system_fact_lookup=cross_system_fact_lookup,
        )
        errors.extend(record_errors)
        updated_records.append(updated)

    if not errors:
        write_jsonl(output, updated_records)

    validation = validate_gold_annotation_records(
        gold_records=updated_records,
        selected_source_ids=selected_ids,
    )
    return {
        "source_family": "nasa_atmonto_gold_review_decision_apply",
        "decision_dir": project_relative_path(decision_root, repo_root),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "output_path": project_relative_path(output, repo_root),
        "output_written": not errors,
        "decision_record_count": len(decisions),
        "updated_record_count": len(updated_records),
        "error_count": len(errors),
        "errors": errors[:100],
        "validation_status": validation["status"],
        "validation_error_count": validation["error_count"],
        "validation_warning_count": validation["warning_count"],
        "reviewed_record_count": validation["reviewed_record_count"],
        "pending_record_count": validation["pending_record_count"],
    }


def final_rejection_group_decision(group: dict[str, Any]) -> dict[str, Any]:
    predicate = str(group.get("predicate", ""))
    errors = {str(error) for error in group.get("errors", [])}
    value_counts = group.get("value_counts", {})
    object_counts = group.get("object_class_counts", {})
    subject_counts = group.get("subject_class_counts", {})

    if (
        predicate == "controlledNASelement"
        and "range_violation" in errors
        and object_counts == {"ARTCC": group.get("count")}
    ):
        return {
            "final_decision": "profile_gap",
            "confidence": "high",
            "decision_basis": (
                "ATCSCC source evidence identifies constrained ARTCC centers, while the "
                "runtime NASA ATMONTO profile requires controlledNASelement objects to be "
                "atm:TFMcontrolElement. The mismatch is a profile coverage gap, not a "
                "surface extraction error."
            ),
            "required_follow_up": (
                "Add a reviewed profile bridge or alternate property for ARTCC-controlled "
                "NAS elements; keep current facts rejected until that profile change is approved."
            ),
        }
    if (
        predicate == "impactingConditionMessage"
        and "domain_violation" in errors
        and subject_counts == {"GroundStopTMI": group.get("count")}
    ):
        return {
            "final_decision": "profile_gap",
            "confidence": "high",
            "decision_basis": (
                "Ground Stop advisories carry explicit impacting-condition message text, "
                "but the runtime profile only permits impactingConditionMessage on "
                "GroundDelayProgramTMI. The extracted text is source-supported; the domain "
                "constraint is too narrow for this ATCSCC subset."
            ),
            "required_follow_up": (
                "Review a GroundStopTMI domain extension for impactingConditionMessage, or "
                "store the message as provenance-only evidence until the profile is extended."
            ),
        }
    if (
        predicate == "extensionProbability"
        and "allowed_value_violation" in errors
        and set(value_counts) == {"MODERATE"}
    ):
        return {
            "final_decision": "extractor_bug",
            "confidence": "medium",
            "decision_basis": (
                "The source surface value is MODERATE, while the runtime profile accepts "
                "LOW, MEDIUM, HIGH, or NONE. This is a normalization gap in the extractor "
                "or mapping layer, not a need to broaden the ontology before scoring."
            ),
            "required_follow_up": (
                "Add a regression-tested normalization rule MODERATE -> MEDIUM and retain "
                "the raw surface value in provenance."
            ),
        }
    if (
        predicate == "impactingCondition"
        and "allowed_value_violation" in errors
        and set(value_counts) == {"staffing"}
    ):
        return {
            "final_decision": "profile_gap",
            "confidence": "medium",
            "decision_basis": (
                "The ATCSCC source explicitly uses STAFFING as an impacting condition, but "
                "the runtime NASA ATMONTO enum does not include a staffing category. Mapping "
                "it to other would lose a recurring operational distinction."
            ),
            "required_follow_up": (
                "Review STAFFING as a profile extension value, or map to other only with "
                "the raw staffing value preserved in impactingConditionMessage."
            ),
        }
    return {
        "final_decision": "manual_review_only",
        "confidence": "low",
        "decision_basis": (
            "This property/error pattern is not covered by deterministic adjudication rules."
        ),
        "required_follow_up": "Inspect source evidence and NASA ATMONTO terms manually.",
    }


def build_rejection_adjudication_report(
    repo_root: str | Path = PROJECT_ROOT,
    rejection_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    if rejection_analysis is None:
        rejection_analysis = read_json(repo_root / REJECTION_ANALYSIS_JSON)
    groups: list[dict[str, Any]] = []
    decision_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()

    for group in rejection_analysis.get("groups", []):
        decision = final_rejection_group_decision(group)
        count = int(group.get("count", 0))
        decision_counts[decision["final_decision"]] += count
        confidence_counts[decision["confidence"]] += count
        groups.append(
            {
                "predicate": group.get("predicate"),
                "errors": group.get("errors", []),
                "count": count,
                "initial_decision": group.get("decision"),
                "final_decision": decision["final_decision"],
                "confidence": decision["confidence"],
                "decision_basis": decision["decision_basis"],
                "required_follow_up": decision["required_follow_up"],
                "subject_class_counts": group.get("subject_class_counts", {}),
                "object_class_counts": group.get("object_class_counts", {}),
                "value_counts": group.get("value_counts", {}),
                "sample_rejections": group.get("sample_rejections", []),
            }
        )

    rejected_fact_count = int(rejection_analysis.get("rejected_fact_count", 0))
    grouped_fact_count = sum(group["count"] for group in groups)
    pending_fact_count = int(decision_counts.get("manual_review_only", 0))
    complete = rejected_fact_count == grouped_fact_count and pending_fact_count == 0
    return {
        "source_family": "nasa_atmonto_rejection_adjudication",
        "input_rejection_analysis": project_relative_path(
            repo_root / REJECTION_ANALYSIS_JSON,
            repo_root,
        ),
        "rejected_fact_count": rejected_fact_count,
        "grouped_fact_count": grouped_fact_count,
        "group_count": len(groups),
        "decision_counts_by_fact": dict(sorted(decision_counts.items())),
        "confidence_counts_by_fact": dict(sorted(confidence_counts.items())),
        "pending_fact_count": pending_fact_count,
        "property_level_complete": complete,
        "groups": groups,
        "boundary": (
            "This artifact finalizes property-level error categories for the "
            f"{rejected_fact_count} pilot rejections. It does not automatically approve "
            "profile extensions or convert validator-rejected facts into semantic gold facts."
        ),
    }


def rejection_adjudication_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Rejection Adjudication",
        "",
        f"- Input: `{report['input_rejection_analysis']}`",
        f"- Rejected facts: {report['rejected_fact_count']}",
        f"- Grouped facts: {report['grouped_fact_count']}",
        f"- Property-level complete: `{report['property_level_complete']}`",
        f"- Pending manual-review-only facts: {report['pending_fact_count']}",
        "",
        "## Final Decision Counts By Fact",
        "",
    ]
    for decision, count in report["decision_counts_by_fact"].items():
        lines.append(f"- `{decision}`: {count}")
    lines.extend(
        [
            "",
            "## Property-Level Decisions",
            "",
            "| Predicate | Errors | Count | Initial decision | Final decision | Confidence |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for group in report["groups"]:
        lines.append(
            "| "
            f"`{group['predicate']}` | "
            f"`{', '.join(group['errors'])}` | "
            f"{group['count']} | "
            f"`{group['initial_decision']}` | "
            f"`{group['final_decision']}` | "
            f"`{group['confidence']}` |"
        )
    lines.extend(["", "## Decision Rationale", ""])
    for group in report["groups"]:
        lines.extend(
            [
                f"### {group['predicate']} / {', '.join(group['errors'])}",
                "",
                f"- Final decision: `{group['final_decision']}`",
                f"- Basis: {group['decision_basis']}",
                f"- Follow-up: {group['required_follow_up']}",
                "",
            ]
        )
    lines.extend(["## Boundary", "", f"- {report['boundary']}"])
    return "\n".join(lines) + "\n"


def run_rejection_adjudication(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_rejection_adjudication_report(repo_root)
    write_json(repo_root / REJECTION_ADJUDICATION_JSON, report)
    (repo_root / REJECTION_ADJUDICATION_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / REJECTION_ADJUDICATION_MD).write_text(
        rejection_adjudication_markdown(report),
        encoding="utf-8",
    )
    return {
        "report_json": project_relative_path(repo_root / REJECTION_ADJUDICATION_JSON, repo_root),
        "report_markdown": project_relative_path(repo_root / REJECTION_ADJUDICATION_MD, repo_root),
        "property_level_complete": report["property_level_complete"],
        "decision_counts_by_fact": report["decision_counts_by_fact"],
    }


def selected_validations(
    validations: list[dict[str, Any]],
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    return [item for item in validations if str(item.get("source_id")) in selected_ids]


def selected_payloads(
    payloads: list[dict[str, Any]],
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    return [item for item in payloads if str(item.get("source_id")) in selected_ids]


def formal_input_records(gold_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for record in gold_records:
        records.append(
            {
                "sample_id": record["sample_id"],
                "source_id": record["source_id"],
                "source_family": record.get("source_family", "atcscc_advisories"),
                "source_url": record.get("source_url"),
                "advisory_date": record.get("advisory_date"),
                "advisory_number": record.get("advisory_number"),
                "candidate_subject_class": record.get("candidate_subject_class"),
                "source_text": record.get("source_text", ""),
                "source_text_excerpt": record.get("source_text_excerpt", ""),
            }
        )
    return records


def group_by_source_id(records: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record.get("source_id")), []).append(record)
    return grouped


def build_s0_prediction_records(
    *,
    input_records: list[dict[str, Any]],
    s0_validations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    validations_by_source = group_by_source_id(s0_validations)
    predictions: list[dict[str, Any]] = []
    for record in input_records:
        source_id = str(record["source_id"])
        validations = validations_by_source.get(source_id, [])
        accepted = [item for item in validations if item.get("accepted")]
        rejected = [item for item in validations if not item.get("accepted")]
        facts = [
            item["validated_fact"]
            for item in accepted
            if isinstance(item.get("validated_fact"), dict)
        ]
        predictions.append(
            {
                "system_id": "S0_rule_only",
                "sample_id": record["sample_id"],
                "source_id": source_id,
                "source_family": record["source_family"],
                "json_adherence": True,
                "facts": facts,
                "candidate_facts": [
                    item["candidate"]
                    for item in validations
                    if isinstance(item.get("candidate"), dict)
                ],
                "validator_results": validations,
                "candidate_fact_count": len(validations),
                "accepted_fact_count": len(facts),
                "rejected_fact_count": len(rejected),
                "rejected_candidate_fact_ids": [
                    item.get("fact_id") for item in rejected if item.get("fact_id")
                ],
                "claim_boundary": (
                    "Rule-only predictions are structurally validated pilot outputs; "
                    "manual gold review is still required for semantic correctness."
                ),
            }
        )
    return predictions


def build_s0_run_metadata(
    *,
    repo_root: Path,
    input_record_count: int,
    prediction_record_count: int,
) -> dict[str, Any]:
    return {
        "system_id": "S0_rule_only",
        "run_status": "completed",
        "runner": "schema_slice_rule_baseline",
        "requires_llm": False,
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "prediction_output": project_relative_path(repo_root / SYSTEMS[0].expected_output, repo_root),
        "input_record_count": input_record_count,
        "prediction_record_count": prediction_record_count,
        "source_candidates": project_relative_path(repo_root / S0_CANDIDATES_PATH, repo_root),
        "source_validations": project_relative_path(repo_root / S0_VALIDATED_PATH, repo_root),
        "claim_boundary": (
            "S0 is deterministic baseline output. It is not manual gold truth and "
            "semantic correctness must be evaluated against reviewed annotations."
        ),
    }


DETERMINISTIC_BACKBONE_PREDICATES = {
    "advisoryNumber",
    "issuedTime",
    "effectiveStartTime",
    "effectiveEndTime",
}

HYBRID_SEMANTIC_ENRICHMENT_PREDICATES = {
    "controlledNASelement",
    "departureScope",
    "extensionProbability",
    "impactingCondition",
    "impactingConditionMessage",
    "implementationStatus",
    "initiativeComments",
    "reRouteReason",
    "reRouteType",
}

S1B_EXTENSION_ENUMS = {"NONE", "LOW", "MEDIUM", "MODERATE", "HIGH"}
S1B_IMPLEMENTATION_ENUMS = {"FYI", "PLN", "RMD", "RQD"}
S1B_STOPWORDS = {
    "ADVZY",
    "AIRPORT",
    "ALL",
    "AND",
    "ARRIVAL",
    "CAN",
    "COMMENT",
    "COMMENTS",
    "DCC",
    "DEP",
    "DUE",
    "EVENT",
    "FAA",
    "FOR",
    "FROM",
    "GROUND",
    "INTO",
    "NOT",
    "ROUTE",
    "THE",
    "TIME",
    "USERS",
    "WILL",
}


def derived_fact_id(system_id: str, source_id: str, *parts: object) -> str:
    return (
        f"{system_id}:{source_id}:fact-"
        + sha1(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[
            :12
        ]
    )


def raw_open_text(value: object) -> str:
    if isinstance(value, dict):
        return " ".join(
            str(value.get(key, ""))
            for key in ("predicate", "label", "class", "text", "value", "type")
            if value.get(key) not in (None, "")
        )
    return str(value or "")


def normalized_open_text(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", raw_open_text(value).lower()).strip()


def fact_object_text(fact: dict[str, Any]) -> str:
    value = fact.get("object") if fact.get("object") not in (None, "") else fact.get("value")
    if isinstance(value, dict):
        return " ".join(
            str(value.get(key, ""))
            for key in ("label", "text", "value", "name", "type")
            if value.get(key) not in (None, "")
        )
    return str(value or "")


def evidence_is_supported(evidence_text: object, source_text: object) -> bool:
    evidence = compact_text(evidence_text)
    source = compact_text(source_text)
    return bool(evidence and source and evidence.lower() in source.lower())


def source_interval_value(input_record: dict[str, Any], basis: str, endpoint: str) -> object | None:
    alignment = input_record.get("temporal_alignment")
    if not isinstance(alignment, dict):
        return None
    for interval in alignment.get("parsed_intervals", []):
        if isinstance(interval, dict) and interval.get("basis") == basis:
            return interval.get(endpoint)
    return None


def canonical_subject_fields(input_record: dict[str, Any]) -> dict[str, str]:
    source_id = str(input_record["source_id"])
    source_text = str(input_record.get("source_text", ""))
    return {
        "subject": source_entity_iri(source_id),
        "subject_class": classify_tmi(source_text),
    }


def canonical_datatype_fact(
    *,
    system_id: str,
    source_id: str,
    input_record: dict[str, Any],
    predicate: str,
    value: object,
    datatype: str,
    evidence_text: str,
    source_fact_id: object,
    mapping_reason: str,
) -> dict[str, Any]:
    subject = canonical_subject_fields(input_record)
    return {
        "fact_id": derived_fact_id(system_id, source_id, predicate, value, evidence_text),
        "source_id": source_id,
        "source_family": "atcscc_advisories",
        "fact_type": "datatype_property",
        **subject,
        "predicate": f"atm:{predicate}",
        "value": value,
        "datatype": datatype,
        "evidence_text": evidence_text,
        "canonicalizer": system_id,
        "source_fact_id": source_fact_id,
        "mapping_reason": mapping_reason,
        "mapping_confidence": "heuristic_high",
    }


def canonical_object_fact(
    *,
    system_id: str,
    source_id: str,
    input_record: dict[str, Any],
    predicate: str,
    object_code: str,
    evidence_text: str,
    source_fact_id: object,
    mapping_reason: str,
) -> dict[str, Any]:
    subject = canonical_subject_fields(input_record)
    code = object_code.upper()
    return {
        "fact_id": derived_fact_id(system_id, source_id, predicate, code, evidence_text),
        "source_id": source_id,
        "source_family": "atcscc_advisories",
        "fact_type": "object_property",
        **subject,
        "predicate": f"atm:{predicate}",
        "object": nas_entity_iri(code),
        "object_label": code,
        "object_class": f"nas:{classify_controlled_element(code)}",
        "evidence_text": evidence_text,
        "canonicalizer": system_id,
        "source_fact_id": source_fact_id,
        "mapping_reason": mapping_reason,
        "mapping_confidence": "heuristic_high",
    }


def facility_codes_from_text(value: str) -> list[str]:
    codes: list[str] = []
    for code in re.findall(r"\b[A-Z][A-Z0-9]{2,4}\b", value.upper()):
        if code not in S1B_STOPWORDS and code not in codes:
            codes.append(code)
    return codes


def canonicalize_s1_fact(
    *,
    fact: dict[str, Any],
    input_record: dict[str, Any],
) -> list[dict[str, Any]]:
    source_id = str(input_record["source_id"])
    predicate_text = normalized_open_text(fact.get("predicate"))
    object_text = fact_object_text(fact)
    evidence_text = compact_text(fact.get("evidence_text"))
    source_fact_id = fact.get("fact_id")
    if not evidence_is_supported(evidence_text, input_record.get("source_text")):
        return []

    mapped: list[dict[str, Any]] = []
    if (
        "advisory" in predicate_text
        and any(token in predicate_text for token in ("number", "identifier", "title"))
        and input_record.get("advisory_number") is not None
    ) or re.search(r"\bADVZY\s+\d{3}\b", evidence_text.upper()):
        mapped.append(
            canonical_datatype_fact(
                system_id="S1b_llm_canonicalized",
                source_id=source_id,
                input_record=input_record,
                predicate="advisoryNumber",
                value=input_record["advisory_number"],
                datatype="xsd:integer",
                evidence_text=evidence_text,
                source_fact_id=source_fact_id,
                mapping_reason="open_advisory_identifier_to_advisoryNumber",
            )
        )

    if any(token in predicate_text for token in ("signature", "advisory time", "issued")):
        issued = source_interval_value(input_record, "issued_time", "start")
        if issued:
            mapped.append(
                canonical_datatype_fact(
                    system_id="S1b_llm_canonicalized",
                    source_id=source_id,
                    input_record=input_record,
                    predicate="issuedTime",
                    value=issued,
                    datatype="xsd:dateTime",
                    evidence_text=evidence_text,
                    source_fact_id=source_fact_id,
                    mapping_reason="open_issued_time_to_issuedTime",
                )
            )

    if any(token in predicate_text for token in ("effective", "event time", "valid during")):
        start = source_interval_value(input_record, "compact_effective_range", "start")
        end = source_interval_value(input_record, "compact_effective_range", "end")
        if start and end:
            for canonical_predicate, value in (
                ("effectiveStartTime", start),
                ("effectiveEndTime", end),
            ):
                mapped.append(
                    canonical_datatype_fact(
                        system_id="S1b_llm_canonicalized",
                        source_id=source_id,
                        input_record=input_record,
                        predicate=canonical_predicate,
                        value=value,
                        datatype="xsd:dateTime",
                        evidence_text=evidence_text,
                        source_fact_id=source_fact_id,
                        mapping_reason="open_effective_window_to_effective_interval",
                    )
                )

    if any(
        token in predicate_text
        for token in ("facility", "facilities", "control element", "airport", "departure")
    ):
        for code in facility_codes_from_text(object_text or evidence_text):
            mapped.append(
                canonical_object_fact(
                    system_id="S1b_llm_canonicalized",
                    source_id=source_id,
                    input_record=input_record,
                    predicate="controlledNASelement",
                    object_code=code,
                    evidence_text=evidence_text,
                    source_fact_id=source_fact_id,
                    mapping_reason="open_facility_to_controlledNASelement",
                )
            )

    enum_value = object_text.upper().strip()
    if "probability" in predicate_text and enum_value in S1B_EXTENSION_ENUMS:
        mapped.append(
            canonical_datatype_fact(
                system_id="S1b_llm_canonicalized",
                source_id=source_id,
                input_record=input_record,
                predicate="extensionProbability",
                value=enum_value,
                datatype="xsd:string",
                evidence_text=evidence_text,
                source_fact_id=source_fact_id,
                mapping_reason="open_extension_probability_to_extensionProbability",
            )
        )
    if (
        any(token in predicate_text for token in ("status", "required", "recommended"))
        and enum_value in S1B_IMPLEMENTATION_ENUMS
    ):
        mapped.append(
            canonical_datatype_fact(
                system_id="S1b_llm_canonicalized",
                source_id=source_id,
                input_record=input_record,
                predicate="implementationStatus",
                value=enum_value,
                datatype="xsd:string",
                evidence_text=evidence_text,
                source_fact_id=source_fact_id,
                mapping_reason="open_status_to_implementationStatus",
            )
        )
    if any(token in predicate_text for token in ("impacting condition", "cause", "reason")):
        value = compact_text(object_text).lower()
        if value and len(value) <= 80:
            mapped.append(
                canonical_datatype_fact(
                    system_id="S1b_llm_canonicalized",
                    source_id=source_id,
                    input_record=input_record,
                    predicate="impactingCondition",
                    value=value,
                    datatype="xsd:string",
                    evidence_text=evidence_text,
                    source_fact_id=source_fact_id,
                    mapping_reason="open_reason_to_impactingCondition",
                )
            )
    return mapped


def dedupe_facts(facts: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[FactKey] = set()
    for fact in facts:
        key = canonical_fact_key(fact)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(fact)
    return deduped


def build_s1b_prediction_record(
    *,
    input_record: dict[str, Any],
    s1_record: dict[str, Any] | None,
    schema_slice: dict[str, Any],
) -> dict[str, Any]:
    source_id = str(input_record["source_id"])
    raw_facts = [
        fact for fact in (s1_record or {}).get("facts", []) if isinstance(fact, dict)
    ]
    mapped_facts = dedupe_facts(
        fact
        for raw_fact in raw_facts
        for fact in canonicalize_s1_fact(fact=raw_fact, input_record=input_record)
    )
    validation_results = validate_candidate_payloads(
        [{"source_id": source_id, "facts": mapped_facts}],
        [{"source_id": source_id, "text": input_record.get("source_text", "")}],
        schema_slice,
    )
    accepted = [item for item in validation_results if item.get("accepted")]
    rejected = [item for item in validation_results if not item.get("accepted")]
    return {
        "system_id": "S1b_llm_canonicalized",
        "sample_id": input_record["sample_id"],
        "source_id": source_id,
        "source_family": input_record["source_family"],
        "json_adherence": True,
        "facts": mapped_facts,
        "validator_results": validation_results,
        "schema_valid": bool(mapped_facts) and not rejected,
        "candidate_fact_count": len(mapped_facts),
        "accepted_fact_count": len(accepted),
        "rejected_fact_count": len(rejected),
        "canonicalization_summary": {
            "raw_fact_count": len(raw_facts),
            "mapped_fact_count": len(mapped_facts),
            "accepted_mapped_fact_count": len(accepted),
            "mapping_yield": len(mapped_facts) / len(raw_facts) if raw_facts else 0.0,
            "unmapped_fact_count": max(len(raw_facts) - len(mapped_facts), 0),
        },
        "claim_boundary": (
            "S1b is a post-hoc canonicalization baseline. It is comparable under "
            "the ATMONTO profile, unlike direct S1_llm_only target-schema scoring."
        ),
    }


def accepted_validation_items(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in record.get("validator_results", [])
        if isinstance(item, dict) and item.get("accepted") and isinstance(item.get("validated_fact"), dict)
    ]


def semantic_repair_safe(item: dict[str, Any]) -> bool:
    repairs = [str(repair) for repair in item.get("repairs", [])]
    return all(
        repair.startswith(("identifier_expansion:", "datatype_expansion:"))
        for repair in repairs
    )


def hybrid_fact_from_item(
    item: dict[str, Any],
    *,
    source_system: str,
    role: str,
) -> dict[str, Any]:
    fact = dict(item["validated_fact"])
    fact["hybrid_source_system"] = source_system
    fact["hybrid_role"] = role
    fact["validator_status"] = item.get("status")
    fact["validator_repairs"] = item.get("repairs", [])
    fact["extractor"] = "S4_hybrid_backbone_enrichment"
    return fact


def build_s4_prediction_record(
    *,
    input_record: dict[str, Any],
    s0_record: dict[str, Any] | None,
    s3_record: dict[str, Any] | None,
) -> dict[str, Any]:
    source_id = str(input_record["source_id"])
    source_text = input_record.get("source_text", "")
    facts: list[dict[str, Any]] = []
    validator_results: list[dict[str, Any]] = []
    accepted_keys: set[FactKey] = set()
    existing_deterministic_predicates: set[str] = set()

    for item in accepted_validation_items(s0_record or {}):
        fact = hybrid_fact_from_item(item, source_system="S0_rule_only", role="deterministic_backbone")
        facts.append(fact)
        accepted_keys.add(canonical_fact_key(fact))
        predicate = term_name(fact.get("predicate"))
        if predicate in DETERMINISTIC_BACKBONE_PREDICATES:
            existing_deterministic_predicates.add(predicate)
        validator_results.append(
            {
                **item,
                "status": "hybrid_backbone_accepted",
                "validated_fact": fact,
                "hybrid_role": "deterministic_backbone",
            }
        )

    quarantine: list[dict[str, Any]] = []
    added_semantic_count = 0
    overwritten_deterministic_count = 0
    for item in accepted_validation_items(s3_record or {}):
        fact = item["validated_fact"]
        predicate = term_name(fact.get("predicate"))
        reason: str | None = None
        if predicate in DETERMINISTIC_BACKBONE_PREDICATES:
            reason = "deterministic_predicate_owned_by_s0"
            overwritten_deterministic_count += 1
        elif predicate not in HYBRID_SEMANTIC_ENRICHMENT_PREDICATES:
            reason = "predicate_not_in_semantic_enrichment_allowlist"
        elif not evidence_is_supported(fact.get("evidence_text"), source_text):
            reason = "unsupported_span"
        elif not semantic_repair_safe(item):
            reason = "semantic_changing_or_fuzzy_repair"
        elif canonical_fact_key(fact) in accepted_keys:
            reason = "duplicate_fact"

        if reason:
            quarantine.append(
                {
                    "source_system": "S3_llm_schema_slice_validator_repair",
                    "fact_id": item.get("fact_id"),
                    "predicate": predicate,
                    "reason": reason,
                    "evidence_text": fact.get("evidence_text"),
                }
            )
            continue

        hybrid_fact = hybrid_fact_from_item(
            item,
            source_system="S3_llm_schema_slice_validator_repair",
            role="semantic_enrichment",
        )
        facts.append(hybrid_fact)
        accepted_keys.add(canonical_fact_key(hybrid_fact))
        added_semantic_count += 1
        validator_results.append(
            {
                **item,
                "status": "hybrid_enrichment_accepted",
                "validated_fact": hybrid_fact,
                "hybrid_role": "semantic_enrichment",
            }
        )

    return {
        "system_id": "S4_hybrid_backbone_enrichment",
        "sample_id": input_record["sample_id"],
        "source_id": source_id,
        "source_family": input_record["source_family"],
        "json_adherence": True,
        "facts": facts,
        "validator_results": validator_results,
        "schema_valid": True,
        "candidate_fact_count": len(facts),
        "accepted_fact_count": len(facts),
        "rejected_fact_count": 0,
        "backbone_fact_count": len(accepted_validation_items(s0_record or {})),
        "hybrid_merge_summary": {
            "added_semantic_fact_count": added_semantic_count,
            "quarantined_fact_count": len(quarantine),
            "overwritten_deterministic_fact_count": 0,
            "deterministic_overwrite_attempt_count": overwritten_deterministic_count,
        },
        "quarantine": quarantine,
        "claim_boundary": (
            "S4 keeps S0 deterministic/header facts and only adds S3 semantic facts "
            "that pass evidence and validator gates."
        ),
    }


def build_derived_run_metadata(
    *,
    repo_root: Path,
    system: SystemDefinition,
    prediction_output: Path,
    records: list[dict[str, Any]],
    input_record_count: int,
    runner: str,
    source_systems: list[str],
) -> dict[str, Any]:
    return {
        "system_id": system.system_id,
        "run_status": "completed" if len(records) == input_record_count else "partial",
        "runner": runner,
        "requires_llm": False,
        "source_systems": source_systems,
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "prediction_output": project_relative_path(prediction_output, repo_root),
        "prediction_record_count": len(records),
        "completed_source_ids": sorted(str(record.get("source_id")) for record in records),
        "parse_error_count": 0,
        "schema_valid_record_count": sum(1 for record in records if record.get("schema_valid")),
        "repair_attempted_record_count": 0,
        "repair_success_record_count": 0,
        "normalizer_version": normalizer_version(),
        "flattened_schema_object_fact_count": 0,
        "claim_boundary": (
            "Derived corrected-stage predictions are deterministic post-processing of "
            "existing experiment outputs, not new model generations."
        ),
    }


def generate_corrected_stage_predictions(
    *,
    repo_root: Path,
    input_records: list[dict[str, Any]],
    schema_slice: dict[str, Any],
) -> dict[str, Any]:
    s1_system = system_by_id("S1_llm_only")
    s1b_system = system_by_id("S1b_llm_canonicalized")
    s0_system = system_by_id("S0_rule_only")
    s3_system = system_by_id("S3_llm_schema_slice_validator_repair")
    s4_system = system_by_id("S4_hybrid_backbone_enrichment")

    s1_path = repo_root / s1_system.expected_output
    s0_path = repo_root / s0_system.expected_output
    s3_path = repo_root / s3_system.expected_output
    if not (s1_path.exists() and s0_path.exists() and s3_path.exists()):
        return {
            "status": "skipped_missing_source_predictions",
            "missing": [
                project_relative_path(path, repo_root)
                for path in (s1_path, s0_path, s3_path)
                if not path.exists()
            ],
        }

    s1_by_source = {str(record.get("source_id")): record for record in read_jsonl(s1_path)}
    s0_by_source = {str(record.get("source_id")): record for record in read_jsonl(s0_path)}
    s3_by_source = {str(record.get("source_id")): record for record in read_jsonl(s3_path)}

    s1b_records = [
        build_s1b_prediction_record(
            input_record=record,
            s1_record=s1_by_source.get(str(record["source_id"])),
            schema_slice=schema_slice,
        )
        for record in input_records
    ]
    s4_records = [
        build_s4_prediction_record(
            input_record=record,
            s0_record=s0_by_source.get(str(record["source_id"])),
            s3_record=s3_by_source.get(str(record["source_id"])),
        )
        for record in input_records
    ]

    write_jsonl(repo_root / s1b_system.expected_output, s1b_records)
    write_jsonl(repo_root / s4_system.expected_output, s4_records)
    write_json(
        repo_root / system_run_metadata_path(s1b_system),
        build_derived_run_metadata(
            repo_root=repo_root,
            system=s1b_system,
            prediction_output=repo_root / s1b_system.expected_output,
            records=s1b_records,
            input_record_count=len(input_records),
            runner="s1_raw_open_fact_canonicalizer",
            source_systems=["S1_llm_only"],
        ),
    )
    write_json(
        repo_root / system_run_metadata_path(s4_system),
        build_derived_run_metadata(
            repo_root=repo_root,
            system=s4_system,
            prediction_output=repo_root / s4_system.expected_output,
            records=s4_records,
            input_record_count=len(input_records),
            runner="s0_s3_hybrid_backbone_enrichment_merger",
            source_systems=["S0_rule_only", "S3_llm_schema_slice_validator_repair"],
        ),
    )
    return {
        "status": "completed",
        "s1b_predictions": project_relative_path(repo_root / s1b_system.expected_output, repo_root),
        "s1b_prediction_record_count": len(s1b_records),
        "s1b_accepted_fact_count": sum(record["accepted_fact_count"] for record in s1b_records),
        "s4_predictions": project_relative_path(repo_root / s4_system.expected_output, repo_root),
        "s4_prediction_record_count": len(s4_records),
        "s4_added_semantic_fact_count": sum(
            record["hybrid_merge_summary"]["added_semantic_fact_count"]
            for record in s4_records
        ),
    }


def extraction_output_contract() -> dict[str, Any]:
    return {
        "required_top_level_fields": ["source_id", "source_family", "facts"],
        "fact_fields": [
            "fact_type",
            "subject",
            "subject_class",
            "predicate",
            "object",
            "object_class",
            "value",
            "datatype",
            "evidence_text",
        ],
        "fact_type_values": ["object_property", "datatype_property"],
        "evidence_rule": (
            "Every fact must include a short evidence_text copied from the advisory text. "
            "Do not invent evidence."
        ),
        "shape_rule": (
            "Return one flat fact object per predicate-value assertion. Do not return nested "
            "entity objects or a properties map; convert each property into its own fact."
        ),
        "empty_case": "If no fact is supported, return an empty facts list.",
    }


def compact_term(row: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "term": row.get("prefixed_name") or row.get("local_name") or row.get("iri"),
        "local_name": row.get("local_name"),
    }
    if row.get("domain_set"):
        compact["domain"] = row["domain_set"]
    if row.get("range_set"):
        compact["range"] = row["range_set"]
    if row.get("datatype_set"):
        compact["datatype"] = row["datatype_set"]
    if row.get("comment"):
        compact["comment"] = compact_text(row["comment"])
    return compact


def compact_schema_context(schema_slice: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_slice_id": schema_slice["schema_slice_id"],
        "classes": [compact_term(row) for row in schema_slice.get("classes", [])],
        "object_properties": [
            compact_term(row) for row in schema_slice.get("object_properties", [])
        ],
        "datatype_properties": [
            compact_term(row) for row in schema_slice.get("datatype_properties", [])
        ],
        "class_property_constraints": schema_slice.get("class_property_constraints", []),
        "boundary": (
            "Use only these schema-slice terms when a prompt condition says schema terms "
            "are allowed. The slice is a constraint, not manual ground truth."
        ),
    }


def prompt_user_content(record: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"sample_id: {record['sample_id']}",
            f"source_id: {record['source_id']}",
            f"source_family: {record['source_family']}",
            f"advisory_date: {record.get('advisory_date')}",
            f"advisory_number: {record.get('advisory_number')}",
            "",
            "ATCSCC advisory text:",
            str(record.get("source_text", "")),
        ]
    )


def llm_only_system_prompt() -> str:
    return "\n".join(
        [
            "Extract a compact knowledge-graph fact payload from one ATCSCC advisory.",
            "Return strict JSON only.",
            "Use descriptive class and predicate labels derived from the text.",
            "Do not use any external ontology term list or schema vocabulary.",
            "Every fact must quote evidence_text from the advisory.",
            "Output contract:",
            json.dumps(extraction_output_contract(), ensure_ascii=False, sort_keys=True),
        ]
    )


def schema_slice_system_prompt(schema_context: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Extract a compact knowledge-graph fact payload from one ATCSCC advisory.",
            "Return strict JSON only.",
            "Use only the provided NASA ATMONTO ATCSCC schema-slice classes and properties.",
            "Every fact must quote evidence_text from the advisory.",
            "Output contract:",
            json.dumps(extraction_output_contract(), ensure_ascii=False, sort_keys=True),
            "Schema slice:",
            json.dumps(schema_context, ensure_ascii=False, sort_keys=True),
        ]
    )


def validator_repair_system_prompt(schema_context: dict[str, Any]) -> str:
    return "\n".join(
        [
            schema_slice_system_prompt(schema_context),
            "",
            "Validator/repair condition:",
            "After the initial payload is checked, repair only facts called out by validator "
            "errors. Do not add unsupported facts during repair. Preserve raw source evidence "
            "and return strict JSON only for the repaired payload.",
        ]
    )


def build_prompt_batch(
    *,
    system: SystemDefinition,
    input_records: list[dict[str, Any]],
    schema_context: dict[str, Any],
) -> list[dict[str, Any]]:
    if system.system_id == "S1_llm_only":
        system_prompt = llm_only_system_prompt()
        schema_context_ref = None
        stages = ["initial_extraction"]
    elif system.system_id == "S2_llm_schema_slice":
        system_prompt = schema_slice_system_prompt(schema_context)
        schema_context_ref = SCHEMA_SLICE_PATH.as_posix()
        stages = ["initial_extraction"]
    elif system.system_id == "S3_llm_schema_slice_validator_repair":
        system_prompt = validator_repair_system_prompt(schema_context)
        schema_context_ref = SCHEMA_SLICE_PATH.as_posix()
        stages = ["initial_extraction", "validate", "repair_if_invalid"]
    else:
        raise ValueError(f"No LLM prompt batch for {system.system_id}")

    return [
        {
            "task_id": f"{system.system_id}:{record['sample_id']}",
            "system_id": system.system_id,
            "sample_id": record["sample_id"],
            "source_id": record["source_id"],
            "source_family": record["source_family"],
            "schema_context_ref": schema_context_ref,
            "stages": stages,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_user_content(record)},
            ],
            "expected_output_contract": extraction_output_contract(),
            "expected_output_record": {
                "source_id": record["source_id"],
                "source_family": record["source_family"],
                "facts": [],
            },
        }
        for record in input_records
    ]


def build_system_specs(repo_root: Path, schema_context: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_family": "nasa_atmonto_formal_experiment_system_specs",
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "schema_slice": project_relative_path(repo_root / SCHEMA_SLICE_PATH, repo_root),
        "extraction_schema": project_relative_path(repo_root / EXTRACTION_SCHEMA_PATH, repo_root),
        "llm_prediction_runner": "scripts/run_nasa_atmonto_llm_predictions.py",
        "llm_smoke_output_dir": project_relative_path(
            repo_root / FORMAL_SMOKE_OUTPUT_DIR,
            repo_root,
        ),
        "systems": system_definitions(repo_root),
        "common_output_contract": extraction_output_contract(),
        "schema_context_summary": {
            "schema_slice_id": schema_context["schema_slice_id"],
            "class_count": len(schema_context["classes"]),
            "object_property_count": len(schema_context["object_properties"]),
            "datatype_property_count": len(schema_context["datatype_properties"]),
        },
        "execution_boundary": (
            "Prompt batches prepare model inputs only. S1-S3 predictions are produced by "
            "the explicit LLM runner and are not fabricated; formal scoring waits for "
            "reviewed gold annotations and S1-S3 predictions."
        ),
    }


def prepare_formal_experiment_inputs(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    schema_slice = read_json(repo_root / SCHEMA_SLICE_PATH)
    s0_validations_all = read_jsonl(repo_root / S0_VALIDATED_PATH)

    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    input_records = formal_input_records(gold_records)
    if {str(record["source_id"]) for record in input_records} != selected_ids:
        raise ValueError("Formal input records do not match selected gold sample IDs")

    s0_validations = selected_validations(s0_validations_all, selected_ids)
    s0_predictions = build_s0_prediction_records(
        input_records=input_records,
        s0_validations=s0_validations,
    )
    schema_context = compact_schema_context(schema_slice)
    prompt_batches = {
        S1_PROMPT_BATCH_PATH: build_prompt_batch(
            system=system_by_id("S1_llm_only"),
            input_records=input_records,
            schema_context=schema_context,
        ),
        S2_PROMPT_BATCH_PATH: build_prompt_batch(
            system=system_by_id("S2_llm_schema_slice"),
            input_records=input_records,
            schema_context=schema_context,
        ),
        S3_PROMPT_BATCH_PATH: build_prompt_batch(
            system=system_by_id("S3_llm_schema_slice_validator_repair"),
            input_records=input_records,
            schema_context=schema_context,
        ),
    }

    write_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH, input_records)
    write_jsonl(repo_root / SYSTEMS[0].expected_output, s0_predictions)
    write_json(
        repo_root / system_run_metadata_path(SYSTEMS[0]),
        build_s0_run_metadata(
            repo_root=repo_root,
            input_record_count=len(input_records),
            prediction_record_count=len(s0_predictions),
        ),
    )
    for path, records in prompt_batches.items():
        write_jsonl(repo_root / path, records)
    write_json(repo_root / FORMAL_SYSTEM_SPECS_PATH, build_system_specs(repo_root, schema_context))
    corrected_stage = generate_corrected_stage_predictions(
        repo_root=repo_root,
        input_records=input_records,
        schema_slice=schema_slice,
    )

    return {
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "input_record_count": len(input_records),
        "s0_predictions": project_relative_path(repo_root / SYSTEMS[0].expected_output, repo_root),
        "s0_run_metadata": project_relative_path(
            repo_root / system_run_metadata_path(SYSTEMS[0]),
            repo_root,
        ),
        "s0_prediction_record_count": len(s0_predictions),
        "prompt_batches": {
            path.as_posix(): len(records)
            for path, records in sorted(
                prompt_batches.items(),
                key=lambda item: item[0].as_posix(),
            )
        },
        "system_specs": project_relative_path(repo_root / FORMAL_SYSTEM_SPECS_PATH, repo_root),
        "corrected_stage_predictions": corrected_stage,
    }


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def llm_response_text(response: object) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    parts.append(str(text))
            elif item:
                parts.append(str(item))
        return "\n".join(parts).strip()
    return str(content).strip()


def invoke_llm_messages(
    messages: list[dict[str, str]],
    *,
    temperature: float,
    max_tokens: int,
) -> str:
    return build_default_llm_invoker(temperature=temperature, max_tokens=max_tokens)(messages)


def build_langchain_messages(messages: list[dict[str, str]]) -> list[Any]:
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
    except ImportError as exc:
        raise RuntimeError(
            "NASA ATMONTO LLM prediction runs require optional LLM dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    chat_messages = []
    for message in messages:
        role = str(message.get("role", "user"))
        content = str(message.get("content", ""))
        if role == "system":
            chat_messages.append(SystemMessage(content=content))
        else:
            chat_messages.append(HumanMessage(content=content))
    return chat_messages


def build_default_llm_invoker(
    *,
    temperature: float,
    max_tokens: int,
) -> LLMInvoker:
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)

    def invoke(messages: list[dict[str, str]]) -> str:
        return llm_response_text(llm.invoke(build_langchain_messages(messages)))

    return invoke


def stable_llm_fact_id(
    *,
    system_id: str,
    sample_id: str,
    index: int,
    fact: dict[str, Any],
) -> str:
    material = json.dumps(fact, sort_keys=True, ensure_ascii=False)
    digest = sha1(material.encode("utf-8")).hexdigest()[:12]
    return f"{system_id}:{sample_id}:fact-{index + 1:02d}-{digest}"


def schema_property_specs(schema_slice: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not schema_slice:
        return {}
    specs: dict[str, dict[str, Any]] = {}
    for category, fact_type in (
        ("object_properties", "object_property"),
        ("datatype_properties", "datatype_property"),
    ):
        for row in schema_slice.get(category, []):
            if not isinstance(row, dict):
                continue
            spec = {
                "fact_type": fact_type,
                "predicate": row.get("prefixed_name") or row.get("local_name") or row.get("iri"),
                "domain": row.get("domain_set", []),
                "datatype": None,
                "range": row.get("range_set", []),
            }
            datatype_set = row.get("datatype_set") or []
            if fact_type == "datatype_property" and datatype_set:
                spec["datatype"] = datatype_set[0]
            for key in (
                row.get("iri"),
                row.get("prefixed_name"),
                row.get("local_name"),
                term_name(row.get("prefixed_name")),
                term_name(row.get("iri")),
            ):
                if key:
                    specs[str(key)] = spec
                    specs[str(key).lower()] = spec
    return specs


def schema_property_spec(
    property_name: object,
    property_specs: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    if not property_name:
        return None
    text = str(property_name)
    return (
        property_specs.get(text)
        or property_specs.get(text.lower())
        or property_specs.get(term_name(text))
        or property_specs.get(term_name(text).lower())
    )


def property_value_entries(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    return [value]


def first_schema_range(spec: dict[str, Any]) -> str | None:
    ranges = spec.get("range") or []
    if isinstance(ranges, list) and len(ranges) == 1:
        return str(ranges[0])
    return None


def first_schema_domain(spec: dict[str, Any]) -> str | None:
    domains = spec.get("domain") or []
    if isinstance(domains, list) and len(domains) == 1:
        return str(domains[0])
    return None


def object_value_parts(value: object, spec: dict[str, Any]) -> tuple[object, str | None, str | None]:
    if isinstance(value, dict):
        actual = value.get("value", value.get("object", value))
        object_class = (
            value.get("object_class")
            or value.get("type")
            or value.get("class")
        )
        label = value.get("label") or value.get("name") or value.get("id")
        if isinstance(actual, dict):
            object_class = (
                object_class
                or actual.get("object_class")
                or actual.get("type")
                or actual.get("class")
            )
            label = label or actual.get("label") or actual.get("name") or actual.get("id")
            actual = (
                actual.get("uri")
                or actual.get("object")
                or actual.get("id")
                or label
                or json.dumps(actual, sort_keys=True, ensure_ascii=False)
            )
        object_class = object_class or first_schema_range(spec)
        return actual, str(object_class) if object_class else None, str(label) if label else None
    return value, first_schema_range(spec), None


def literal_value_parts(value: object) -> tuple[object, str | None]:
    if isinstance(value, dict):
        datatype = value.get("datatype")
        return value.get("value", value.get("literal", "")), str(datatype) if datatype else None
    return value, None


def evidence_for_value(value: object, fallback: object) -> str:
    if isinstance(value, dict) and value.get("evidence_text"):
        return str(value["evidence_text"])
    return str(fallback or "")


def fact_subject_class(fact: dict[str, Any]) -> object:
    return fact.get("subject_class") or fact.get("class") or fact.get("type")


def flattened_schema_property_fact(
    *,
    raw_fact: dict[str, Any],
    property_name: object,
    property_value: object,
    property_specs: dict[str, dict[str, Any]],
    task: dict[str, Any],
) -> dict[str, Any] | None:
    spec = schema_property_spec(property_name, property_specs)
    if not spec:
        return None
    evidence_text = evidence_for_value(property_value, raw_fact.get("evidence_text"))
    base: dict[str, Any] = {
        "source_id": task["source_id"],
        "source_family": task.get("source_family", "atcscc_advisories"),
        "subject": raw_fact.get("subject") or f"urn:aviation-agentic-ai:tmi:{task['source_id']}",
        "subject_class": fact_subject_class(raw_fact) or first_schema_domain(spec),
        "predicate": spec["predicate"],
        "fact_type": spec["fact_type"],
        "evidence_text": evidence_text,
        "llm_normalization": "schema_object_flattened",
    }
    if raw_fact.get("fact_id"):
        base["source_raw_fact_id"] = raw_fact["fact_id"]

    if spec["fact_type"] == "object_property":
        object_value, object_class, object_label = object_value_parts(property_value, spec)
        base["object"] = object_value
        if object_class:
            base["object_class"] = object_class
        if object_label:
            base["object_label"] = object_label
    else:
        value, datatype = literal_value_parts(property_value)
        base["value"] = value
        base["datatype"] = datatype or spec.get("datatype")
    return base


def flatten_schema_object_fact(
    *,
    fact: dict[str, Any],
    property_specs: dict[str, dict[str, Any]],
    task: dict[str, Any],
) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    properties = fact.get("properties")
    if isinstance(properties, dict):
        for property_name, property_values in properties.items():
            for property_value in property_value_entries(property_values):
                flattened_fact = flattened_schema_property_fact(
                    raw_fact=fact,
                    property_name=property_name,
                    property_value=property_value,
                    property_specs=property_specs,
                    task=task,
                )
                if flattened_fact:
                    flattened.append(flattened_fact)

    reserved_keys = {
        "class",
        "evidence_text",
        "fact_id",
        "id",
        "properties",
        "source_family",
        "source_id",
        "subject",
        "subject_class",
        "type",
    }
    for property_name, property_value in fact.items():
        if property_name in reserved_keys:
            continue
        if not schema_property_spec(property_name, property_specs):
            continue
        for entry in property_value_entries(property_value):
            flattened_fact = flattened_schema_property_fact(
                raw_fact=fact,
                property_name=property_name,
                property_value=entry,
                property_specs=property_specs,
                task=task,
            )
            if flattened_fact:
                flattened.append(flattened_fact)
    return flattened


def subject_value_and_class(fact: dict[str, Any]) -> tuple[object | None, object | None]:
    subject = fact.get("subject")
    if isinstance(subject, dict):
        value = (
            subject.get("value")
            or subject.get("id")
            or subject.get("uri")
            or subject.get("label")
            or subject.get("name")
        )
        subject_class = (
            subject.get("subject_class")
            or subject.get("type")
            or subject.get("class")
        )
        return value, subject_class
    return subject, fact_subject_class(fact)


def normalize_flat_llm_fact(
    fact: dict[str, Any],
    task: dict[str, Any],
    property_specs: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized = dict(fact)
    normalized.setdefault("source_id", task["source_id"])
    normalized.setdefault("source_family", task.get("source_family", "atcscc_advisories"))
    subject, subject_class = subject_value_and_class(normalized)
    normalized["subject"] = subject or f"urn:aviation-agentic-ai:tmi:{task['source_id']}"
    if "subject_class" not in normalized:
        if subject_class:
            normalized["subject_class"] = subject_class
    spec = schema_property_spec(normalized.get("predicate"), property_specs or {})
    if spec:
        normalized["fact_type"] = spec["fact_type"]
        normalized.setdefault("subject_class", first_schema_domain(spec))
        if spec["fact_type"] == "datatype_property":
            raw_value = normalized.pop("object", normalized.get("value"))
            value, datatype = literal_value_parts(raw_value)
            normalized["value"] = value
            normalized["datatype"] = normalized.get("datatype") or datatype or spec.get("datatype")
            normalized.pop("object_class", None)
        elif spec["fact_type"] == "object_property" and "object" in normalized:
            object_value, object_class, object_label = object_value_parts(normalized["object"], spec)
            normalized["object"] = object_value
            if object_class and not normalized.get("object_class"):
                normalized["object_class"] = object_class
            if object_label and not normalized.get("object_label"):
                normalized["object_label"] = object_label
    elif "fact_type" not in normalized:
        if "value" in normalized:
            normalized["fact_type"] = "datatype_property"
        elif "object" in normalized:
            normalized["fact_type"] = "object_property"
    return normalized


def normalize_llm_facts(
    *,
    payload: dict[str, Any],
    task: dict[str, Any],
    schema_slice: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    facts_raw = payload.get("facts", [])
    if not isinstance(facts_raw, list):
        raise ValueError("facts_not_a_list")
    facts: list[dict[str, Any]] = []
    skipped = 0
    property_specs = schema_property_specs(schema_slice)
    for fact in facts_raw:
        if not isinstance(fact, dict):
            skipped += 1
            continue
        normalized_items = [normalize_flat_llm_fact(fact, task, property_specs)]
        flattened_items = flatten_schema_object_fact(
            fact=fact,
            property_specs=property_specs,
            task=task,
        )
        if flattened_items:
            normalized_items = flattened_items
        for normalized in normalized_items:
            normalized.setdefault("source_id", task["source_id"])
            normalized.setdefault(
                "source_family",
                task.get("source_family", "atcscc_advisories"),
            )
            normalized.setdefault(
                "subject",
                f"urn:aviation-agentic-ai:tmi:{task['source_id']}",
            )
            normalized.setdefault(
                "fact_id",
                stable_llm_fact_id(
                    system_id=str(task["system_id"]),
                    sample_id=str(task["sample_id"]),
                    index=len(facts),
                    fact=normalized,
                ),
            )
            facts.append(normalized)
    return facts, skipped


def normalizer_version() -> str:
    return "schema_object_flattening_v1"


def record_normalizer_metadata(record: dict[str, Any]) -> dict[str, Any]:
    facts = record.get("facts") or []
    flattened_count = sum(
        1
        for fact in facts
        if isinstance(fact, dict) and fact.get("llm_normalization") == "schema_object_flattened"
    )
    return {
        "normalizer_version": normalizer_version(),
        "flattened_schema_object_fact_count": flattened_count,
    }


def parse_llm_prediction_payload(
    *,
    raw_response: str,
    task: dict[str, Any],
    schema_slice: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        payload = extract_json_object(raw_response)
        facts, skipped_fact_count = normalize_llm_facts(
            payload=payload,
            task=task,
            schema_slice=schema_slice,
        )
    except (JSONPayloadExtractionError, ValueError) as exc:
        return {
            "system_id": task["system_id"],
            "sample_id": task["sample_id"],
            "source_id": task["source_id"],
            "source_family": task.get("source_family", "atcscc_advisories"),
            "json_adherence": False,
            "facts": None,
            "raw_response": raw_response,
            "parse_error": str(exc),
        }
    return {
        "system_id": task["system_id"],
        "sample_id": task["sample_id"],
        "source_id": str(payload.get("source_id") or task["source_id"]),
        "source_family": str(
            payload.get("source_family") or task.get("source_family", "atcscc_advisories")
        ),
        "json_adherence": True,
        "facts": facts,
        "raw_response": raw_response,
        "parse_error": None,
        "skipped_non_object_fact_count": skipped_fact_count,
        "normalizer_version": normalizer_version(),
        "flattened_schema_object_fact_count": sum(
            1
            for fact in facts
            if fact.get("llm_normalization") == "schema_object_flattened"
        ),
    }


def source_row_for_task(task: dict[str, Any], input_by_source_id: dict[str, dict[str, Any]]) -> dict[str, object]:
    source_id = str(task["source_id"])
    input_record = input_by_source_id[source_id]
    return {"source_id": source_id, "text": input_record.get("source_text", "")}


def validate_prediction_record(
    *,
    record: dict[str, Any],
    source_row: dict[str, object],
    schema_slice: dict[str, Any],
) -> list[dict[str, Any]]:
    if not record.get("json_adherence") or not isinstance(record.get("facts"), list):
        return []
    return validate_candidate_payloads(
        prediction_payloads_for_validation([record]),
        [source_row],
        schema_slice,
    )


def rejected_validation_summary(validation_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "fact_id": item.get("fact_id"),
            "errors": item.get("errors", []),
            "candidate": item.get("candidate"),
        }
        for item in validation_results
        if item.get("accepted") is False
    ]


def build_repair_messages(
    *,
    task: dict[str, Any],
    initial_record: dict[str, Any],
    validation_results: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rejected = rejected_validation_summary(validation_results)
    repair_context = {
        "sample_id": task["sample_id"],
        "source_id": task["source_id"],
        "parse_error": initial_record.get("parse_error"),
        "validator_rejections": rejected,
        "instruction": (
            "Return one complete corrected JSON object with source_id, source_family, and facts. "
            "Remove unsupported facts instead of inventing replacements. Keep evidence_text copied "
            "from the advisory."
        ),
    }
    messages = list(task["messages"])
    messages.append(
        {
            "role": "user",
            "content": "\n".join(
                [
                    "The initial extraction payload failed validation.",
                    "Initial raw response:",
                    str(initial_record.get("raw_response", "")),
                    "",
                    "Validation feedback:",
                    json.dumps(repair_context, ensure_ascii=False, sort_keys=True),
                ]
            ),
        }
    )
    return messages


def prediction_record_counts(record: dict[str, Any]) -> dict[str, int]:
    validation_results = [
        item for item in record.get("validator_results", []) if isinstance(item, dict)
    ]
    return {
        "candidate_fact_count": len(record.get("facts") or []),
        "accepted_fact_count": sum(1 for item in validation_results if item.get("accepted")),
        "rejected_fact_count": sum(1 for item in validation_results if not item.get("accepted")),
    }


def build_llm_prediction_record(
    *,
    system: SystemDefinition,
    task: dict[str, Any],
    raw_response: str,
    source_row: dict[str, object],
    schema_slice: dict[str, Any],
    invoker: LLMInvoker,
) -> dict[str, Any]:
    initial_record = parse_llm_prediction_payload(
        raw_response=raw_response,
        task=task,
        schema_slice=schema_slice,
    )
    initial_validation = validate_prediction_record(
        record=initial_record,
        source_row=source_row,
        schema_slice=schema_slice,
    )
    final_record = dict(initial_record)
    repair_attempted = False
    repair_raw_response = None
    repair_parse_error = None
    repair_reason = None

    should_repair = system.uses_validator_repair and (
        not initial_record.get("json_adherence")
        or any(item.get("accepted") is False for item in initial_validation)
    )
    if should_repair:
        repair_attempted = True
        repair_reason = "parse_error" if not initial_record.get("json_adherence") else "validator_rejections"
        repair_raw_response = invoker(
            build_repair_messages(
                task=task,
                initial_record=initial_record,
                validation_results=initial_validation,
            )
        )
        repaired_record = parse_llm_prediction_payload(
            raw_response=repair_raw_response,
            task=task,
            schema_slice=schema_slice,
        )
        repair_parse_error = repaired_record.get("parse_error")
        if repaired_record.get("json_adherence"):
            final_record = repaired_record

    final_validation = validate_prediction_record(
        record=final_record,
        source_row=source_row,
        schema_slice=schema_slice,
    )
    final_record["validator_results"] = final_validation
    final_record["initial_validator_results"] = initial_validation
    final_record["repair_attempted"] = repair_attempted
    final_record["repair_reason"] = repair_reason
    final_record["repair_raw_response"] = repair_raw_response
    final_record["repair_parse_error"] = repair_parse_error
    final_record["schema_valid"] = (
        final_record.get("json_adherence") is True
        and isinstance(final_record.get("facts"), list)
        and all(item.get("accepted") for item in final_validation)
    )
    final_record.update(prediction_record_counts(final_record))
    return final_record


def system_by_id(system_id: str) -> SystemDefinition:
    for system in SYSTEMS:
        if system.system_id == system_id:
            return system
    raise ValueError(f"Unknown system_id: {system_id}")


def build_llm_run_metadata(
    *,
    repo_root: Path,
    system: SystemDefinition,
    prediction_output: Path,
    prompt_count: int,
    records: list[dict[str, Any]],
    started_at: str,
    completed_at: str,
    temperature: float,
    max_tokens: int,
    limit: int | None,
    output_scope: str,
    resumed: bool = False,
    skipped_existing_record_count: int = 0,
) -> dict[str, Any]:
    repair_attempted = sum(1 for record in records if record.get("repair_attempted"))
    repair_success = sum(
        1
        for record in records
        if record.get("repair_attempted")
        and record.get("repair_parse_error") is None
        and record.get("schema_valid")
    )
    return {
        "system_id": system.system_id,
        "run_status": "completed" if limit is None or len(records) == prompt_count else "partial",
        "output_scope": output_scope,
        "resumed": resumed,
        "skipped_existing_record_count": skipped_existing_record_count,
        "runner": "nasa_atmonto_prompt_batch_llm_runner",
        "provider": configured_llm_provider(),
        "model": configured_llm_model(),
        "temperature": temperature,
        "max_tokens": max_tokens,
        "started_at": started_at,
        "completed_at": completed_at,
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "prompt_batch": project_relative_path(repo_root / system.prompt_batch, repo_root)
        if system.prompt_batch
        else None,
        "prediction_output": project_relative_path(prediction_output, repo_root),
        "prompt_count": prompt_count,
        "prediction_record_count": len(records),
        "completed_source_ids": sorted(str(record.get("source_id")) for record in records),
        "parse_error_count": sum(1 for record in records if not record.get("json_adherence")),
        "schema_valid_record_count": sum(1 for record in records if record.get("schema_valid")),
        "repair_attempted_record_count": repair_attempted,
        "repair_success_record_count": repair_success,
        "normalizer_version": normalizer_version(),
        "flattened_schema_object_fact_count": sum(
            int(record.get("flattened_schema_object_fact_count", 0) or 0)
            for record in records
        ),
        "limit": limit,
        "claim_boundary": (
            "LLM predictions are experiment outputs only; formal extraction effectiveness still "
            "requires reviewed gold annotations and scoring."
        ),
    }


def run_llm_prediction_system(
    *,
    system_id: str,
    repo_root: str | Path = PROJECT_ROOT,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    limit: int | None = None,
    output_dir: str | Path | None = None,
    resume: bool = False,
    progress: bool = False,
    invoker: LLMInvoker | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    system = system_by_id(system_id)
    if not system.requires_llm:
        raise ValueError(f"{system_id} is not an LLM prediction system")
    if not system.prompt_batch:
        raise ValueError(f"{system_id} does not define a prompt batch")
    if limit is not None and limit < 1:
        raise ValueError("limit must be >= 1 when provided")

    prompt_records = read_jsonl(repo_root / system.prompt_batch)
    input_records = read_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH)
    schema_slice = read_json(repo_root / SCHEMA_SLICE_PATH)
    input_by_source_id = {str(record["source_id"]): record for record in input_records}
    effective_records = prompt_records[:limit] if limit is not None else prompt_records
    run_output_dir = llm_run_output_dir(limit=limit, output_dir=output_dir)
    if run_output_dir.is_absolute():
        output_dir_abs = run_output_dir
    else:
        output_dir_abs = repo_root / run_output_dir
    prediction_output = output_dir_abs / system.expected_output.name
    metadata_output = output_dir_abs / f"{system_output_stem(system)}_run_metadata.json"
    output_scope = (
        "custom"
        if output_dir is not None
        else "smoke"
        if limit is not None
        else "formal"
    )
    effective_invoker = invoker or build_default_llm_invoker(
        temperature=temperature,
        max_tokens=max_tokens,
    )

    started_at = utc_timestamp()
    predictions: list[dict[str, Any]] = []
    skipped_existing_record_count = 0
    if resume and prediction_output.exists():
        existing = read_jsonl_lenient(prediction_output)
        predictions = [
            record
            for record in existing["records"]
            if str(record.get("source_id")) in {str(task["source_id"]) for task in effective_records}
        ]
        skipped_existing_record_count = len(predictions)
    else:
        prediction_output.parent.mkdir(parents=True, exist_ok=True)
        prediction_output.write_text("", encoding="utf-8")

    completed_source_ids = {str(record.get("source_id")) for record in predictions}
    for task in effective_records:
        if str(task["source_id"]) in completed_source_ids:
            continue
        source_row = source_row_for_task(task, input_by_source_id)
        if progress:
            print(
                (
                    f"[{system.system_id}] running "
                    f"{len(predictions) + 1}/{len(effective_records)} "
                    f"sample={task['sample_id']} source={task['source_id']}"
                ),
                file=sys.stderr,
                flush=True,
            )
        raw_response = effective_invoker(task["messages"])
        record = build_llm_prediction_record(
            system=system,
            task=task,
            raw_response=raw_response,
            source_row=source_row,
            schema_slice=schema_slice,
            invoker=effective_invoker,
        )
        predictions.append(record)
        completed_source_ids.add(str(task["source_id"]))
        append_jsonl_record(prediction_output, record)
        checkpoint_metadata = build_llm_run_metadata(
            repo_root=repo_root,
            system=system,
            prediction_output=prediction_output,
            prompt_count=len(prompt_records),
            records=predictions,
            started_at=started_at,
            completed_at=utc_timestamp(),
            temperature=temperature,
            max_tokens=max_tokens,
            limit=limit,
            output_scope=output_scope,
            resumed=resume,
            skipped_existing_record_count=skipped_existing_record_count,
        )
        write_json(metadata_output, checkpoint_metadata)
        if progress:
            print(
                (
                    f"[{system.system_id}] wrote {len(predictions)}/{len(effective_records)} "
                    f"json={record.get('json_adherence')} schema_valid={record.get('schema_valid')} "
                    f"facts={record.get('candidate_fact_count')}"
                ),
                file=sys.stderr,
                flush=True,
            )
    completed_at = utc_timestamp()
    metadata = build_llm_run_metadata(
        repo_root=repo_root,
        system=system,
        prediction_output=prediction_output,
        prompt_count=len(prompt_records),
        records=predictions,
        started_at=started_at,
        completed_at=completed_at,
        temperature=temperature,
        max_tokens=max_tokens,
        limit=limit,
        output_scope=output_scope,
        resumed=resume,
        skipped_existing_record_count=skipped_existing_record_count,
    )
    write_json(metadata_output, metadata)
    return {
        "system_id": system.system_id,
        "prediction_output": project_relative_path(prediction_output, repo_root),
        "run_metadata": project_relative_path(metadata_output, repo_root),
        "output_scope": output_scope,
        "run_status": metadata["run_status"],
        "prompt_count": len(prompt_records),
        "prediction_record_count": len(predictions),
        "parse_error_count": metadata["parse_error_count"],
        "schema_valid_record_count": metadata["schema_valid_record_count"],
        "repair_attempted_record_count": metadata["repair_attempted_record_count"],
        "repair_success_record_count": metadata["repair_success_record_count"],
    }


def rebuild_llm_prediction_record_from_saved_raw(
    *,
    system: SystemDefinition,
    existing_record: dict[str, Any],
    task: dict[str, Any],
    source_row: dict[str, object],
    schema_slice: dict[str, Any],
) -> dict[str, Any]:
    raw_response = str(existing_record.get("raw_response") or "")
    initial_record = parse_llm_prediction_payload(
        raw_response=raw_response,
        task=task,
        schema_slice=schema_slice,
    )
    initial_validation = validate_prediction_record(
        record=initial_record,
        source_row=source_row,
        schema_slice=schema_slice,
    )

    repair_attempted = bool(existing_record.get("repair_attempted"))
    repair_reason = existing_record.get("repair_reason")
    repair_raw_response = existing_record.get("repair_raw_response")
    repair_parse_error = existing_record.get("repair_parse_error")
    final_record = dict(initial_record)
    if repair_attempted and isinstance(repair_raw_response, str) and repair_raw_response:
        repaired_record = parse_llm_prediction_payload(
            raw_response=repair_raw_response,
            task=task,
            schema_slice=schema_slice,
        )
        repair_parse_error = repaired_record.get("parse_error")
        if repaired_record.get("json_adherence"):
            final_record = repaired_record

    final_validation = validate_prediction_record(
        record=final_record,
        source_row=source_row,
        schema_slice=schema_slice,
    )
    final_record["validator_results"] = final_validation
    final_record["initial_validator_results"] = initial_validation
    final_record["repair_attempted"] = repair_attempted
    final_record["repair_reason"] = repair_reason
    final_record["repair_raw_response"] = repair_raw_response
    final_record["repair_parse_error"] = repair_parse_error
    final_record["schema_valid"] = (
        final_record.get("json_adherence") is True
        and isinstance(final_record.get("facts"), list)
        and all(item.get("accepted") for item in final_validation)
    )
    final_record["reprocessed_from_saved_raw_response"] = True
    final_record.update(record_normalizer_metadata(final_record))
    final_record.update(prediction_record_counts(final_record))
    return final_record


def reprocess_llm_prediction_system_outputs(
    *,
    system_id: str,
    repo_root: str | Path = PROJECT_ROOT,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    system = system_by_id(system_id)
    if not system.requires_llm:
        raise ValueError(f"{system_id} is not an LLM prediction system")
    if not system.prompt_batch:
        raise ValueError(f"{system_id} does not define a prompt batch")

    run_output_dir = Path(output_dir) if output_dir is not None else FORMAL_OUTPUT_DIR
    output_dir_abs = run_output_dir if run_output_dir.is_absolute() else repo_root / run_output_dir
    prediction_output = output_dir_abs / system.expected_output.name
    metadata_output = output_dir_abs / f"{system_output_stem(system)}_run_metadata.json"
    existing = read_jsonl_lenient(prediction_output)
    if not existing["exists"]:
        raise FileNotFoundError(prediction_output)

    prompt_records = read_jsonl(repo_root / system.prompt_batch)
    input_records = read_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH)
    schema_slice = read_json(repo_root / SCHEMA_SLICE_PATH)
    tasks_by_source_id = {str(task["source_id"]): task for task in prompt_records}
    input_by_source_id = {str(record["source_id"]): record for record in input_records}
    rebuilt_records: list[dict[str, Any]] = []
    skipped_records: list[str] = []
    for existing_record in existing["records"]:
        source_id = str(existing_record.get("source_id"))
        task = tasks_by_source_id.get(source_id)
        input_record = input_by_source_id.get(source_id)
        if not task or not input_record or not existing_record.get("raw_response"):
            skipped_records.append(source_id)
            continue
        rebuilt_records.append(
            rebuild_llm_prediction_record_from_saved_raw(
                system=system,
                existing_record=existing_record,
                task=task,
                source_row={"source_id": source_id, "text": input_record.get("source_text", "")},
                schema_slice=schema_slice,
            )
        )

    write_jsonl(prediction_output, rebuilt_records)
    previous_metadata = read_json_lenient(metadata_output)
    metadata_payload = previous_metadata.get("payload") or {}
    metadata = {
        **metadata_payload,
        "run_status": "completed"
        if len(rebuilt_records) == len(prompt_records)
        else "partial_reprocessed",
        "runner": "nasa_atmonto_saved_raw_response_reprocessor",
        "prediction_output": project_relative_path(prediction_output, repo_root),
        "prediction_record_count": len(rebuilt_records),
        "completed_source_ids": sorted(str(record.get("source_id")) for record in rebuilt_records),
        "parse_error_count": sum(
            1 for record in rebuilt_records if not record.get("json_adherence")
        ),
        "schema_valid_record_count": sum(
            1 for record in rebuilt_records if record.get("schema_valid")
        ),
        "repair_attempted_record_count": sum(
            1 for record in rebuilt_records if record.get("repair_attempted")
        ),
        "repair_success_record_count": sum(
            1
            for record in rebuilt_records
            if record.get("repair_attempted")
            and record.get("repair_parse_error") is None
            and record.get("schema_valid")
        ),
        "normalizer_version": normalizer_version(),
        "flattened_schema_object_fact_count": sum(
            int(record.get("flattened_schema_object_fact_count", 0) or 0)
            for record in rebuilt_records
        ),
        "reprocessed_from_saved_raw_response": True,
        "skipped_reprocess_source_ids": skipped_records,
    }
    write_json(metadata_output, metadata)
    return {
        "system_id": system.system_id,
        "prediction_output": project_relative_path(prediction_output, repo_root),
        "run_metadata": project_relative_path(metadata_output, repo_root),
        "prediction_record_count": len(rebuilt_records),
        "skipped_record_count": len(skipped_records),
        "parse_error_count": metadata["parse_error_count"],
        "schema_valid_record_count": metadata["schema_valid_record_count"],
        "repair_attempted_record_count": metadata["repair_attempted_record_count"],
        "repair_success_record_count": metadata["repair_success_record_count"],
        "flattened_schema_object_fact_count": metadata["flattened_schema_object_fact_count"],
    }


def read_jsonl_lenient(path: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    invalid_lines: list[dict[str, Any]] = []
    if not path.exists():
        return {
            "exists": False,
            "records": records,
            "line_count": 0,
            "invalid_json_line_count": 0,
            "invalid_json_lines": invalid_lines,
        }
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                invalid_lines.append(
                    {
                        "line_number": line_number,
                        "error": exc.msg,
                    }
                )
                continue
            if isinstance(payload, dict):
                records.append(payload)
            else:
                invalid_lines.append(
                    {
                        "line_number": line_number,
                        "error": "top_level_json_value_is_not_object",
                    }
                )
    return {
        "exists": True,
        "records": records,
        "line_count": len(records) + len(invalid_lines),
        "invalid_json_line_count": len(invalid_lines),
        "invalid_json_lines": invalid_lines[:10],
    }


def read_json_lenient(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "payload": None, "error": None}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"exists": True, "payload": None, "error": exc.msg}
    if not isinstance(payload, dict):
        return {"exists": True, "payload": None, "error": "top_level_json_value_is_not_object"}
    return {"exists": True, "payload": payload, "error": None}


def is_valid_prediction_payload(record: dict[str, Any], selected_ids: set[str]) -> bool:
    return str(record.get("source_id")) in selected_ids and isinstance(record.get("facts"), list)


def prediction_json_metrics(
    *,
    parse_result: dict[str, Any],
    selected_ids: set[str],
) -> dict[str, Any]:
    records = [record for record in parse_result["records"] if isinstance(record, dict)]
    valid_records = [record for record in records if is_valid_prediction_payload(record, selected_ids)]
    valid_source_counts = Counter(str(record["source_id"]) for record in valid_records)
    valid_source_ids = set(valid_source_counts)
    duplicate_count = sum(count - 1 for count in valid_source_counts.values() if count > 1)
    invalid_payload_count = len(records) - len(valid_records)
    attempted = len(selected_ids)
    return {
        "attempted_record_count": attempted,
        "line_count": parse_result["line_count"],
        "valid_json_payload_count": len(valid_source_ids),
        "invalid_json_line_count": parse_result["invalid_json_line_count"],
        "invalid_payload_count": invalid_payload_count,
        "duplicate_output_record_count": duplicate_count,
        "missing_output_record_count": len(selected_ids - valid_source_ids),
        "json_adherence": (len(valid_source_ids) / attempted) if attempted else None,
    }


def valid_prediction_records(
    parse_result: dict[str, Any],
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for record in parse_result["records"]:
        source_id = str(record.get("source_id"))
        if source_id in seen or not is_valid_prediction_payload(record, selected_ids):
            continue
        seen.add(source_id)
        records.append(record)
    return records


def prompt_batch_validation(
    *,
    system: SystemDefinition,
    repo_root: Path,
    selected_ids: set[str],
) -> dict[str, Any]:
    if not system.prompt_batch:
        return {
            "path": None,
            "exists": None,
            "task_count": None,
            "valid_task_count": None,
            "missing_source_id_count": None,
            "duplicate_source_id_count": None,
            "invalid_json_line_count": None,
            "status": "not_applicable",
            "errors": [],
        }
    path = repo_root / system.prompt_batch
    parse_result = read_jsonl_lenient(path)
    errors: list[str] = []
    if not parse_result["exists"]:
        return {
            "path": project_relative_path(path, repo_root),
            "exists": False,
            "task_count": 0,
            "valid_task_count": 0,
            "missing_source_id_count": len(selected_ids),
            "duplicate_source_id_count": 0,
            "invalid_json_line_count": 0,
            "status": "missing",
            "errors": ["prompt_batch_missing"],
        }
    records = [record for record in parse_result["records"] if isinstance(record, dict)]
    valid_records = [
        record
        for record in records
        if str(record.get("source_id")) in selected_ids
        and record.get("system_id") == system.system_id
        and isinstance(record.get("messages"), list)
        and isinstance(record.get("expected_output_contract"), dict)
    ]
    source_counts = Counter(str(record.get("source_id")) for record in valid_records)
    duplicate_count = sum(count - 1 for count in source_counts.values() if count > 1)
    missing_count = len(selected_ids - set(source_counts))
    if parse_result["invalid_json_line_count"]:
        errors.append("prompt_batch_invalid_json")
    if len(valid_records) != len(records):
        errors.append("prompt_batch_invalid_task_shape")
    if duplicate_count:
        errors.append("prompt_batch_duplicate_source_ids")
    if missing_count:
        errors.append("prompt_batch_missing_source_ids")
    return {
        "path": project_relative_path(path, repo_root),
        "exists": True,
        "task_count": parse_result["line_count"],
        "valid_task_count": len(valid_records),
        "missing_source_id_count": missing_count,
        "duplicate_source_id_count": duplicate_count,
        "invalid_json_line_count": parse_result["invalid_json_line_count"],
        "status": "ready" if not errors else "needs_revision",
        "errors": errors,
    }


def run_metadata_validation(
    *,
    system: SystemDefinition,
    repo_root: Path,
    output_exists: bool,
) -> dict[str, Any]:
    path = repo_root / system_run_metadata_path(system)
    parse_result = read_json_lenient(path)
    errors: list[str] = []
    warnings: list[str] = []
    if not parse_result["exists"]:
        return {
            "path": project_relative_path(path, repo_root),
            "exists": False,
            "status": "missing" if system.requires_llm or output_exists else "optional_missing",
            "errors": [],
            "warnings": ["run_metadata_missing"],
        }
    payload = parse_result["payload"] or {}
    if parse_result["error"]:
        errors.append("run_metadata_invalid_json")
    if payload.get("system_id") != system.system_id:
        errors.append("run_metadata_system_id_mismatch")
    if output_exists and payload.get("run_status") not in {"completed", "reviewed"}:
        errors.append("run_metadata_run_status_not_completed")
    for field in ("prediction_output", "input_records"):
        if output_exists and not payload.get(field):
            errors.append(f"run_metadata_missing_{field}")
    return {
        "path": project_relative_path(path, repo_root),
        "exists": True,
        "status": "ready" if not errors else "needs_revision",
        "summary": {
            "normalizer_version": payload.get("normalizer_version"),
            "flattened_schema_object_fact_count": payload.get(
                "flattened_schema_object_fact_count"
            ),
            "reprocessed_from_saved_raw_response": payload.get(
                "reprocessed_from_saved_raw_response",
            ),
            "schema_valid_record_count": payload.get("schema_valid_record_count"),
            "repair_success_record_count": payload.get("repair_success_record_count"),
        },
        "errors": errors,
        "warnings": warnings,
    }


def validate_prediction_output_system(
    *,
    system: SystemDefinition,
    repo_root: Path,
    selected_ids: set[str],
) -> dict[str, Any]:
    output_path = repo_root / system.expected_output
    parse_result = read_jsonl_lenient(output_path)
    prompt_status = prompt_batch_validation(
        system=system,
        repo_root=repo_root,
        selected_ids=selected_ids,
    )
    metadata_status = run_metadata_validation(
        system=system,
        repo_root=repo_root,
        output_exists=parse_result["exists"],
    )
    errors: list[str] = []
    pending: list[str] = []
    json_metrics = None

    if prompt_status["status"] == "needs_revision":
        errors.extend(prompt_status["errors"])
    elif prompt_status["status"] == "missing":
        pending.append("prompt_batch_missing")

    if not parse_result["exists"]:
        pending.append("prediction_output_missing")
    else:
        json_metrics = prediction_json_metrics(parse_result=parse_result, selected_ids=selected_ids)
        if json_metrics["invalid_json_line_count"]:
            errors.append("prediction_output_invalid_json_lines")
        if json_metrics["invalid_payload_count"]:
            errors.append("prediction_output_invalid_payload_shape")
        if json_metrics["duplicate_output_record_count"]:
            errors.append("prediction_output_duplicate_source_ids")
        if json_metrics["missing_output_record_count"]:
            errors.append("prediction_output_missing_source_ids")

    if metadata_status["status"] == "needs_revision":
        errors.extend(metadata_status["errors"])
    elif metadata_status["status"] == "missing":
        pending.append("run_metadata_missing")

    if errors:
        status = "needs_revision"
    elif pending:
        status = "pending_required_outputs"
    else:
        status = "ready_for_scoring"

    return {
        "system_id": system.system_id,
        "label": system.label,
        "expected_output": project_relative_path(output_path, repo_root),
        "output_exists": parse_result["exists"],
        "prompt_batch": prompt_status,
        "run_metadata": metadata_status,
        "json_metrics": json_metrics,
        "status": status,
        "errors": errors,
        "pending": pending,
    }


def build_prediction_output_validation_report(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    system_reports = [
        validate_prediction_output_system(
            system=system,
            repo_root=repo_root,
            selected_ids=selected_ids,
        )
        for system in SYSTEMS
    ]
    error_count = sum(len(report["errors"]) for report in system_reports)
    pending_count = sum(len(report["pending"]) for report in system_reports)
    if error_count:
        status = "needs_revision"
    elif pending_count:
        status = "pending_required_outputs"
    else:
        status = "ready_for_scoring"
    return {
        "source_family": "nasa_atmonto_prediction_output_validation",
        "status": status,
        "selected_source_id_count": len(selected_ids),
        "systems": system_reports,
        "error_count": error_count,
        "pending_count": pending_count,
        "completion_gate": (
            "Prediction outputs are usable for formal scoring only when every system status is "
            "ready_for_scoring."
        ),
    }


def prediction_output_validation_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Prediction Output Validation",
        "",
        f"- Status: `{report['status']}`",
        f"- Selected source IDs: {report['selected_source_id_count']}",
        f"- Errors: {report['error_count']}",
        f"- Pending items: {report['pending_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Systems",
        "",
        "| System | Status | Output | Run Metadata | JSON adherence | Missing records | Normalizer | Flattened facts | Schema-valid records | Pending | Errors |",
        "| --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for system in report["systems"]:
        json_metrics = system.get("json_metrics") or {}
        metadata_summary = system.get("run_metadata", {}).get("summary") or {}
        flattened = metadata_summary.get("flattened_schema_object_fact_count")
        schema_valid_records = metadata_summary.get("schema_valid_record_count")
        lines.append(
            "| "
            f"`{system['system_id']}` | "
            f"`{system['status']}` | "
            f"`{system['output_exists']}` | "
            f"`{system['run_metadata']['exists']}` | "
            f"{json_metrics.get('json_adherence')} | "
            f"{json_metrics.get('missing_output_record_count')} | "
            f"`{metadata_summary.get('normalizer_version') or ''}` | "
            f"{'' if flattened is None else flattened} | "
            f"{'' if schema_valid_records is None else schema_valid_records} | "
            f"`{', '.join(system['pending'])}` | "
            f"`{', '.join(system['errors'])}` |"
        )
    return "\n".join(lines) + "\n"


def run_prediction_output_validation(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_prediction_output_validation_report(repo_root)
    write_json(repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON, report)
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).write_text(
        prediction_output_validation_markdown(report),
        encoding="utf-8",
    )
    return {
        "report_json": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON,
            repo_root,
        ),
        "report_markdown": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD,
            repo_root,
        ),
        "status": report["status"],
        "error_count": report["error_count"],
        "pending_count": report["pending_count"],
    }


def prediction_payloads_for_validation(
    records: list[dict[str, Any]],
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for record in records:
        facts: list[dict[str, Any]] = []
        for fact in record.get("facts", []):
            if isinstance(fact, dict):
                normalized = dict(fact)
                normalized.setdefault("source_id", record.get("source_id"))
                facts.append(normalized)
        payloads.append(
            {
                "source_id": record["source_id"],
                "source_family": record.get("source_family", "atcscc_advisories"),
                "facts": facts,
            }
        )
    return payloads


def source_rows_for_validation(input_records: list[dict[str, Any]]) -> list[dict[str, object]]:
    return [
        {
            "source_id": record["source_id"],
            "text": record.get("source_text", ""),
        }
        for record in input_records
    ]


def embedded_validator_results(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for record in records:
        for item in record.get("validator_results", []):
            if isinstance(item, dict):
                results.append(item)
    return results


def property_level_semantic_metrics(
    *,
    predictions: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    gold_keys = gold_fact_keys(gold_records)
    if not gold_keys:
        return []
    prediction_keys = {canonical_fact_key(fact) for fact in predictions}
    predicates = sorted({fact_key_predicate(key) for key in gold_keys | prediction_keys})
    rows: list[dict[str, Any]] = []
    for predicate in predicates:
        gold_for_predicate = {
            key for key in gold_keys if fact_key_predicate(key) == predicate
        }
        pred_for_predicate = {
            key for key in prediction_keys if fact_key_predicate(key) == predicate
        }
        true_positive = pred_for_predicate & gold_for_predicate
        false_positive = pred_for_predicate - gold_for_predicate
        false_negative = gold_for_predicate - pred_for_predicate
        precision = (
            len(true_positive) / len(pred_for_predicate)
            if pred_for_predicate
            else 0.0
        )
        recall = len(true_positive) / len(gold_for_predicate) if gold_for_predicate else 0.0
        f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
        rows.append(
            {
                "predicate": predicate,
                "predicted_fact_count": len(pred_for_predicate),
                "gold_fact_count": len(gold_for_predicate),
                "true_positive_count": len(true_positive),
                "false_positive_count": len(false_positive),
                "false_negative_count": len(false_negative),
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )
    return rows


def semantic_group_semantic_metrics(
    *,
    predictions: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
    semantic_groups: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    gold_by_source_id = {str(record.get("source_id")): record for record in gold_records}
    for group in semantic_groups.get("groups", []):
        source_ids = {
            str(record.get("source_id"))
            for record in semantic_groups.get("records", [])
            if record.get("semantic_group_id") == group.get("group_id")
        }
        group_gold_records = [
            gold_by_source_id[source_id]
            for source_id in sorted(source_ids)
            if source_id in gold_by_source_id
        ]
        group_predictions = [
            fact for fact in predictions if str(fact.get("source_id")) in source_ids
        ]
        rows.append(
            {
                "group_id": group["group_id"],
                "label": group["label"],
                "record_count": group["record_count"],
                "gold_fact_count": len(gold_fact_keys(group_gold_records)),
                "predicted_fact_count": len(
                    {canonical_fact_key(fact) for fact in group_predictions}
                ),
                "semantic_metrics": semantic_metrics(
                    predictions=group_predictions,
                    gold_records=group_gold_records,
                ),
            }
        )
    return rows


def semantic_scoring_validity(
    *,
    system: SystemDefinition,
    structural: dict[str, Any],
) -> dict[str, Any]:
    if (
        system.system_id == "S1_llm_only"
        and int(structural.get("candidate_fact_count") or 0) > 0
        and int(structural.get("accepted_fact_count") or 0) == 0
        and float(structural.get("schema_violation_rate") or 0.0) >= 0.999
    ):
        return {
            "scoring_validity": "invalid_direct_schema_scoring",
            "valid_for_baseline_comparison": False,
            "interpretation": (
                "The schema-free LLM output is JSON-adherent but all candidate facts "
                "are rejected by the target ATMONTO validator. Direct target-schema "
                "precision/recall/F1 are diagnostic zeros, not a valid semantic baseline. "
                "Use S1_raw_open_llm diagnostics and S1b_llm_canonicalized for future "
                "target-schema semantic comparisons."
            ),
        }
    return {
        "scoring_validity": "valid_target_schema_scoring",
        "valid_for_baseline_comparison": True,
        "interpretation": "Target-schema precision/recall/F1 are interpretable for this system.",
    }


def source_family_methodology_boundaries(repo_root: Path) -> dict[str, Any]:
    return {
        "status": "methodology_remediation",
        "scope_statement": (
            "The current scored run is a narrow FAA ATCSCC advisory / NASA ATMONTO "
            "ATCSCC schema-slice experiment. PDF reference documents are added only as "
            "a second source-family design for the next rerun; PDF definition/procedure "
            "metrics must not be mixed into the ATCSCC event F1 table."
        ),
        "source_families": [
            {
                "id": "A",
                "source_family": "faa_atcscc_advisories",
                "data_shape": "semi_structured_short_advisories",
                "task": "TMI/event ABox extraction",
                "preferred_system_design": (
                    "S0 deterministic backbone plus S3 semantic enrichment and validator gate"
                ),
                "current_gold": "100 reviewed advisories from 2026-05-14 through 2026-05-20",
            },
            {
                "id": "B",
                "source_family": "faa_nasa_pdf_reference_documents",
                "data_shape": "unstructured_or_long_form_reference_text",
                "task": (
                    "definition, terminology, procedure, and source-mapping evidence extraction"
                ),
                "candidate_documents": [
                    project_relative_path(
                        repo_root
                        / "data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/"
                        "PCG_Bsc_w_Chg_1_and_2_dtd_1-22-26.pdf",
                        repo_root,
                    ),
                    project_relative_path(
                        repo_root
                        / "data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/"
                        "7110.65BB_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf",
                        repo_root,
                    ),
                    project_relative_path(
                        repo_root
                        / "data/papers/ntrs_ontology_selection/"
                        "20170006095_nasa_air_traffic_management_ontology.pdf",
                        repo_root,
                    ),
                ],
                "allowed_predicates": [
                    "term_has_definition",
                    "term_has_alias",
                    "procedure_mentions_concept",
                    "document_defines_or_constrains",
                    "source_supports_mapping",
                ],
                "required_provenance_fields": [
                    "document_id",
                    "page",
                    "section",
                    "span",
                    "evidence_text",
                ],
                "backend_policy": {
                    "candidate_default": "hybrid_docling_pymupdf",
                    "legacy_baseline": "pymupdf_text_legacy",
                    "policy_reports": [
                        "reports/stages/pdf_extraction_comparison.md",
                        "reports/stages/pdf_backend_chunking_comparison.md",
                    ],
                },
            },
        ],
        "cross_source_metric_policy": (
            "Compare structural conformance, evidence grounding, and canonicalization yield "
            "across source families. Report semantic F1 within each task family only."
        ),
    }


def consensus_sota_remediation_constraints() -> dict[str, Any]:
    return {
        "status": "rerun_design_constraint",
        "scope_boundary": (
            "These constraints refine the narrow ATCSCC / ATMONTO rerun. They are "
            "not a pivot to a general aviation KG or an end-to-end GraphRAG claim."
        ),
        "s1_interpretation": {
            "current_system": "S1_llm_only",
            "current_label": "invalid_direct_schema_scoring",
            "future_raw_system": "S1_raw_open_llm",
            "future_comparable_system": "S1b_llm_canonicalized",
            "rule": (
                "Report raw S1 coverage, JSON adherence, and evidence containment only. "
                "Compute target-schema precision/recall/F1 only after canonicalization."
            ),
        },
        "nine_stage_pipeline": [
            "ATCSCC parsing",
            "S0 deterministic backbone",
            "schema-slice retrieval",
            "LLM semantic extraction",
            "canonicalization",
            "validator gate",
            "repair with trace",
            "graph materialization",
            "layered evaluation",
        ],
        "sota_adaptations": [
            {
                "anchor": "Extract-Define-Canonicalize",
                "implementation": "Split open extraction from target-schema canonicalization.",
                "claim_guardrail": "Do not score raw open LLM output with ATMONTO P/R/F1.",
            },
            {
                "anchor": "ontology_guided_domain_short_text_kgc",
                "implementation": (
                    "Use 10-20 reviewed dev examples for S2/S3 by advisory type and "
                    "predicate family."
                ),
                "claim_guardrail": "Do not draw examples from the held-out 100 scoring records.",
            },
            {
                "anchor": "llm_as_kg_assistant",
                "implementation": (
                    "Use LLMs as canonicalizer, semantic enrichment module, evidence checker, "
                    "and profile-gap explainer."
                ),
                "claim_guardrail": "Do not make pure LLM extraction the primary thesis system.",
            },
            {
                "anchor": "production_ontology_guided_pipeline",
                "implementation": (
                    "Combine pattern/rule extraction, ontology-guided prompting, grounding, "
                    "corroboration, and validator gating."
                ),
                "claim_guardrail": "Quarantine conflicts, unsupported spans, and rejected repairs.",
            },
            {
                "anchor": "source_family_separation",
                "implementation": (
                    "Keep ATCSCC event extraction and PDF reference extraction in separate "
                    "metric tables."
                ),
                "claim_guardrail": "Do not compare PDF definition F1 with ATCSCC event F1.",
            },
            {
                "anchor": "graph_rag_layered_evaluation",
                "implementation": (
                    "Report KG construction, graph retrieval, and answer generation metrics "
                    "as separate layers."
                ),
                "claim_guardrail": (
                    "Current remediation supports KG construction metrics only; no "
                    "end-to-end GraphRAG answer improvement claim."
                ),
            },
        ],
        "s4_merge_policy": {
            "primary_candidate_system": "S4_hybrid_backbone_enrichment",
            "s0_owns": [
                "advisoryNumber",
                "issuedTime",
                "effectiveStartTime",
                "effectiveEndTime",
                "header/template fields",
            ],
            "s3_s4_may_add_not_overwrite": sorted(HYBRID_SEMANTIC_ENRICHMENT_PREDICATES),
            "quarantine_conditions": [
                "conflict",
                "unsupported span",
                "fuzzy-only mapping",
                "validator rejected fact",
                "repair-only fact with semantic-change flag",
            ],
        },
        "planned_artifacts": [
            {
                "path": "schema/atcscc_tmi_profile.yaml",
                "required_fields": [
                    "class",
                    "predicate_uri",
                    "label",
                    "aliases",
                    "domain",
                    "range",
                    "cardinality",
                    "allowed_enum",
                    "normalizer",
                    "validator_rule",
                    "example_spans",
                    "profile_version",
                    "source_doc",
                    "commit_hash",
                ],
            },
            {"component": "predicate canonicalizer"},
            {"component": "enum canonicalizer"},
            {"component": "entity canonicalizer"},
            {"component": "time normalizer"},
            {
                "component": "repair trace",
                "fields": [
                    "pre_error",
                    "repair_action",
                    "post_validation_status",
                    "semantic_change_flag",
                    "evidence_status",
                ],
            },
            {
                "component": "error taxonomy",
                "categories": [
                    "format error",
                    "predicate drift",
                    "class/domain error",
                    "range error",
                    "enum error",
                    "entity canonicalization error",
                    "unsupported span",
                    "temporal normalization error",
                    "duplicate/merge error",
                ],
            },
        ],
        "unverified_search_leads": {
            "status": "requiring verification",
            "rule": "Do not cite these as formal evidence until fetched and checked directly.",
            "items": [
                "OntoLogX",
                "JSON-Schema-guided information extraction",
                "Graphusion",
                "RAKG",
                "RAGAS",
                "STaRK",
                "Microsoft GraphRAG",
            ],
        },
    }


def formal_scoring_gold_source(repo_root: Path, selected_ids: set[str]) -> dict[str, Any]:
    reviewed_path = repo_root / GOLD_REVIEWED_PATH
    template_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    template_validation = validate_gold_annotation_records(
        gold_records=template_records,
        selected_source_ids=selected_ids,
    )
    if not reviewed_path.exists():
        return {
            "source": "frozen_reviewed_gold_missing",
            "path": project_relative_path(reviewed_path, repo_root),
            "exists": False,
            "sha256": None,
            "records": [],
            "gold_status": gold_annotation_status([]),
            "template_validation_status": template_validation["status"],
            "template_reviewed_record_count": template_validation["reviewed_record_count"],
            "template_pending_record_count": template_validation["pending_record_count"],
            "ready_for_formal_scoring": False,
        }

    reviewed_records = read_jsonl(reviewed_path)
    reviewed_validation = validate_gold_annotation_records(
        gold_records=reviewed_records,
        selected_source_ids=selected_ids,
    )
    ready = reviewed_validation["status"] == "ready_for_scoring"
    return {
        "source": "frozen_reviewed_gold",
        "path": project_relative_path(reviewed_path, repo_root),
        "exists": True,
        "sha256": file_sha256(reviewed_path),
        "records": reviewed_records,
        "gold_status": gold_annotation_status(reviewed_records),
        "validation_status": reviewed_validation["status"],
        "error_count": reviewed_validation["error_count"],
        "warning_count": reviewed_validation["warning_count"],
        "template_validation_status": template_validation["status"],
        "template_reviewed_record_count": template_validation["reviewed_record_count"],
        "template_pending_record_count": template_validation["pending_record_count"],
        "ready_for_formal_scoring": ready,
    }


def score_system_predictions(
    *,
    system: SystemDefinition,
    repo_root: Path,
    selected_ids: set[str],
    input_records: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
    schema_slice: dict[str, Any],
    semantic_groups: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_path = repo_root / system.expected_output
    parse_result = read_jsonl_lenient(output_path)
    base = {
        "system_id": system.system_id,
        "label": system.label,
        "expected_output": project_relative_path(output_path, repo_root),
        "output_exists": parse_result["exists"],
    }
    if not parse_result["exists"]:
        return {
            **base,
            "available": False,
            "reason": "prediction_output_missing",
            "json_metrics": None,
            "structural_metrics": None,
            "semantic_metrics": None,
            "property_level_semantic_metrics": [],
            "semantic_group_metrics": [],
        }

    json_metrics = prediction_json_metrics(parse_result=parse_result, selected_ids=selected_ids)
    records = valid_prediction_records(parse_result, selected_ids)
    validation_results = embedded_validator_results(records)
    if not validation_results:
        validation_results = validate_candidate_payloads(
            prediction_payloads_for_validation(records),
            source_rows_for_validation(input_records),
            schema_slice,
        )
    prediction_facts = accepted_prediction_facts(validation_results)
    semantic = semantic_metrics(predictions=prediction_facts, gold_records=gold_records)
    structural = structural_metrics(
        validation_results,
        repair_applicable=system.uses_validator_repair,
    )
    semantic.update(
        semantic_scoring_validity(
            system=system,
            structural=structural,
        )
    )
    return {
        **base,
        "available": True,
        "reason": None,
        "json_metrics": json_metrics,
        "structural_metrics": structural,
        "semantic_metrics": semantic,
        "property_level_semantic_metrics": (
            property_level_semantic_metrics(
                predictions=prediction_facts,
                gold_records=gold_records,
            )
            if semantic["available"]
            else []
        ),
        "semantic_group_metrics": (
            semantic_group_semantic_metrics(
                predictions=prediction_facts,
                gold_records=gold_records,
                semantic_groups=semantic_groups,
            )
            if semantic["available"] and semantic_groups
            else []
        ),
    }


def system_score_by_id(system_scores: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(score["system_id"]): score for score in system_scores}


def nested_metric(score: dict[str, Any], group: str, key: str) -> Any:
    metrics = score.get(group)
    if not isinstance(metrics, dict):
        return None
    return metrics.get(key)


def property_metric_value(score: dict[str, Any], predicate: str, metric: str) -> float | None:
    for row in score.get("property_level_semantic_metrics", []):
        if row.get("predicate") == predicate and isinstance(row.get(metric), (int, float)):
            return float(row[metric])
    return None


def macro_property_metric(
    score: dict[str, Any],
    predicates: Iterable[str],
    metric: str,
) -> float | None:
    values = [
        value
        for predicate in predicates
        if (value := property_metric_value(score, predicate, metric)) is not None
    ]
    return sum(values) / len(values) if values else None


def metric_value_text(value: Any) -> str:
    return "n/a" if value is None else str(value)


def metric_interval_text(interval: dict[str, Any] | None) -> str:
    if interval is None:
        return "n/a"
    if not interval:
        return "n/a (empty)"
    return f"{metric_value_text(interval.get('low'))} - {metric_value_text(interval.get('high'))}"


def status_record(
    *,
    item_id: str,
    label: str,
    status: str,
    rationale: str,
    evidence: list[str] | None = None,
    falsification_criterion: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": item_id,
        "label": label,
        "status": status,
        "rationale": rationale,
        "evidence": evidence or [],
    }
    if falsification_criterion:
        record["falsification_criterion"] = falsification_criterion
    return record


def claim_and_hypothesis_statuses(
    *,
    system_scores: list[dict[str, Any]],
    gold_source: dict[str, Any],
    rejection_analysis: dict[str, Any],
    rejection_adjudication: dict[str, Any],
) -> dict[str, Any]:
    by_id = system_score_by_id(system_scores)
    s0 = by_id["S0_rule_only"]
    s1 = by_id["S1_llm_only"]
    s1b = by_id.get("S1b_llm_canonicalized")
    s2 = by_id["S2_llm_schema_slice"]
    s3 = by_id["S3_llm_schema_slice_validator_repair"]
    s4 = by_id.get("S4_hybrid_backbone_enrichment")
    reviewed_gold_ready = bool(gold_source.get("ready_for_formal_scoring"))
    s1_s2_ready = bool(s1.get("available") and s2.get("available"))
    s1b_s2_ready = bool(s1b and s1b.get("available") and s2.get("available"))
    s2_s3_ready = bool(s2.get("available") and s3.get("available"))
    all_llm_ready = bool(s1.get("available") and s2.get("available") and s3.get("available"))
    s4_ready = bool(s4 and s4.get("available"))
    semantic_ready = reviewed_gold_ready and all(
        bool((score.get("semantic_metrics") or {}).get("available"))
        for score in system_scores
    )
    rejection_count = int(rejection_analysis.get("rejected_fact_count", 0))
    rejection_group_total = sum(int(group.get("count", 0)) for group in rejection_analysis.get("groups", []))
    final_rejection_decisions = rejection_adjudication.get("decision_counts_by_fact", {})
    adjudication_complete = bool(rejection_adjudication.get("property_level_complete"))
    manual_review_only = int(final_rejection_decisions.get("manual_review_only", 0))

    s1_violation = nested_metric(s1, "structural_metrics", "schema_violation_rate")
    s1b_violation = (
        nested_metric(s1b, "structural_metrics", "schema_violation_rate") if s1b else None
    )
    s2_violation = nested_metric(s2, "structural_metrics", "schema_violation_rate")
    h1_delta = (
        s1b_violation - s2_violation
        if isinstance(s1b_violation, (int, float)) and isinstance(s2_violation, (int, float))
        else s1_violation - s2_violation
        if isinstance(s1_violation, (int, float)) and isinstance(s2_violation, (int, float))
        else None
    )
    s2_accepted = nested_metric(s2, "structural_metrics", "accepted_fact_count")
    s3_accepted = nested_metric(s3, "structural_metrics", "accepted_fact_count")
    s3_repair_success = nested_metric(s3, "structural_metrics", "repair_success_rate")
    s2_semantic = nested_metric(s2, "semantic_metrics", "manual_semantic_correctness")
    s3_semantic = nested_metric(s3, "semantic_metrics", "manual_semantic_correctness")
    s1_precision = nested_metric(s1, "semantic_metrics", "precision")
    s3_precision = nested_metric(s3, "semantic_metrics", "precision")
    s1_f1 = nested_metric(s1, "semantic_metrics", "f1")
    s3_f1 = nested_metric(s3, "semantic_metrics", "f1")
    s1_scoring_validity = nested_metric(s1, "semantic_metrics", "scoring_validity")
    s1_invalid_direct = s1_scoring_validity == "invalid_direct_schema_scoring"
    h3_semantic_predicates = ("implementationStatus", "reRouteReason", "reRouteType")
    h3_deterministic_predicates = tuple(sorted(DETERMINISTIC_BACKBONE_PREDICATES))
    s0_h3_semantic_f1 = macro_property_metric(s0, h3_semantic_predicates, "f1")
    s4_h3_semantic_f1 = macro_property_metric(s4 or {}, h3_semantic_predicates, "f1")
    s0_deterministic_f1 = macro_property_metric(s0, h3_deterministic_predicates, "f1")
    s4_deterministic_f1 = macro_property_metric(s4 or {}, h3_deterministic_predicates, "f1")

    if s1b_s2_ready:
        h1_baseline_label = "S1b_llm_canonicalized"
        if h1_delta is None:
            h1_status = "inconclusive_missing_metric"
            h1_rationale = "S1b/S2 outputs exist, but schema violation rates are unavailable."
        elif h1_delta >= 0.10:
            h1_status = "supported"
            h1_rationale = (
                "S2 schema guidance reduces target-schema violation rate versus the "
                "canonicalized S1b baseline by at least 10 percentage points."
            )
        else:
            h1_status = "falsified"
            h1_rationale = (
                "S2 did not reduce schema violation rate versus the canonicalized S1b "
                "baseline by the required 10 percentage points."
            )
    elif not s1_s2_ready:
        h1_baseline_label = "S1_llm_only"
        h1_status = "pending_required_inputs"
        h1_rationale = "S1 and S2 prediction outputs are required before schema-violation comparison."
    elif h1_delta is None:
        h1_baseline_label = "S1_llm_only"
        h1_status = "inconclusive_missing_metric"
        h1_rationale = "S1/S2 outputs exist, but schema violation rates are unavailable."
    elif s1_invalid_direct:
        h1_baseline_label = "S1_llm_only"
        h1_status = "inconclusive"
        h1_rationale = (
            "S2 reduces direct target-schema violations versus S1, but S1 is a "
            "schema-free output scored without a canonicalization bridge. Treat this as "
            "structural-drift diagnosis until S1_raw_open_llm and S1b_llm_canonicalized exist."
        )
    elif h1_delta >= 0.10:
        h1_baseline_label = "S1_llm_only"
        h1_status = "supported_structural_only" if not reviewed_gold_ready else "supported"
        h1_rationale = (
            "S2 schema violation rate is at least 10 percentage points lower than S1; "
            "gold-supported fact suppression still needs reviewed gold if unavailable."
        )
    else:
        h1_baseline_label = "S1_llm_only"
        h1_status = "falsified"
        h1_rationale = "S2 did not reduce schema violation rate by the required 10 percentage points."

    if not s2_s3_ready:
        h2_status = "pending_required_inputs"
        h2_rationale = "S2 and S3 prediction outputs are required before repair comparison."
    elif not semantic_ready:
        h2_status = "pending_manual_gold"
        h2_rationale = "Structural repair can be inspected, but semantic preservation requires reviewed gold."
    elif (
        isinstance(s3_repair_success, (int, float))
        and isinstance(s2_semantic, (int, float))
        and isinstance(s3_semantic, (int, float))
        and s3_repair_success >= 0.15
        and (s2_semantic - s3_semantic) <= 0.05
    ):
        h2_status = "supported"
        h2_rationale = "S3 meets the repair-success threshold and preserves semantic correctness."
    else:
        h2_status = "falsified"
        h2_rationale = "S3 failed the repair-success or semantic-preservation criterion."

    if s4_ready and semantic_ready:
        if (
            isinstance(s0_h3_semantic_f1, (int, float))
            and isinstance(s4_h3_semantic_f1, (int, float))
            and isinstance(s0_deterministic_f1, (int, float))
            and isinstance(s4_deterministic_f1, (int, float))
            and s4_h3_semantic_f1 > s0_h3_semantic_f1 + 0.05
            and s4_deterministic_f1 >= s0_deterministic_f1 - 0.02
        ):
            h3_status = "supported"
            h3_rationale = (
                "S4 improves the selected semantic predicate macro-F1 over S0 while "
                "preserving deterministic-field macro-F1 within tolerance."
            )
        else:
            h3_status = "falsified"
            h3_rationale = (
                "S4 did not improve selected semantic predicate macro-F1 over S0 while "
                "preserving deterministic-field macro-F1 within tolerance."
            )
    elif not all_llm_ready:
        h3_status = "pending_required_inputs"
        h3_rationale = "S1-S3 prediction outputs are required before precision/recall/F1 comparison."
    elif not semantic_ready:
        h3_status = "pending_manual_gold"
        h3_rationale = "Precision, recall, F1, and manual semantic correctness require reviewed gold."
    elif s1_invalid_direct:
        h3_status = "inconclusive"
        h3_rationale = (
            "S1 direct target-schema semantic scores are invalid because all schema-free "
            "facts were rejected at the ATMONTO scoring interface. S3>S1 is therefore not "
            "valid evidence for ontology-constrained semantic improvement."
        )
    elif (
        isinstance(s1_precision, (int, float))
        and isinstance(s3_precision, (int, float))
        and isinstance(s1_f1, (int, float))
        and isinstance(s3_f1, (int, float))
        and s3_precision > s1_precision
        and s3_f1 >= s1_f1 - 0.05
    ):
        h3_status = "supported"
        h3_rationale = "S3 improves precision and keeps F1 within the allowed loss threshold."
    else:
        h3_status = "falsified"
        h3_rationale = "S3 did not satisfy the precision/F1 tradeoff criterion."

    if rejection_group_total != rejection_count:
        h4_status = "incomplete_rejection_accounting"
        h4_rationale = (
            "The rejection analysis does not account for all "
            f"{rejection_count} pilot rejections."
        )
    elif not adjudication_complete:
        h4_status = "pending_manual_adjudication"
        h4_rationale = "Property-level adjudication still has unresolved manual-review-only facts."
    elif manual_review_only / rejection_count > 0.20:
        h4_status = "falsified"
        h4_rationale = "More than 20 percent of rejected facts remain manual-review-only."
    else:
        h4_status = "supported"
        h4_rationale = (
            f"All {rejection_count} rejections have final property-level action labels: "
            f"{json.dumps(final_rejection_decisions, sort_keys=True)}."
        )

    claims = [
        status_record(
            item_id="C1",
            label="Runtime NASA ATMONTO profile feasibility",
            status="supported_by_pilot",
            rationale=(
                "The pilot generated the schema catalog, ATCSCC schema slice, and validated "
                "candidate-fact artifact. This remains a schema-engineering claim."
            ),
            evidence=[
                "data/ontology/curated/nasa_atmonto_schema_catalog.json",
                "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json",
                "data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl",
            ],
        ),
        status_record(
            item_id="C2",
            label="Schema-slice constraint benefit",
            status=h1_status,
            rationale=h1_rationale,
            evidence=[
                f"{h1_baseline_label} structural metrics",
                "S2_llm_schema_slice structural metrics",
            ],
        ),
        status_record(
            item_id="C3",
            label="Validator/repair benefit",
            status=h2_status,
            rationale=h2_rationale,
            evidence=[
                "S2_llm_schema_slice structural and semantic metrics",
                "S3_llm_schema_slice_validator_repair structural and semantic metrics",
            ],
        ),
        status_record(
            item_id="C4",
            label="Rejection analysis utility",
            status=h4_status,
            rationale=h4_rationale,
            evidence=[
                "reports/stages/nasa_atmonto_rejection_error_analysis.md",
                "reports/stages/nasa_atmonto_rejection_adjudication.md",
            ],
        ),
    ]

    hypotheses = [
        status_record(
            item_id="H1",
            label="Schema guidance reduces structural drift",
            status=h1_status,
            rationale=h1_rationale,
            evidence=[
                f"s1_schema_violation_rate={s1_violation}",
                f"s1b_schema_violation_rate={s1b_violation}",
                f"s2_schema_violation_rate={s2_violation}",
                f"{h1_baseline_label}_minus_s2={h1_delta}",
                f"s1_semantic_scoring_validity={s1_scoring_validity}",
            ],
            falsification_criterion=(
                "Falsified if schema guidance does not reduce unsupported target-schema "
                "terms after a canonicalized S1b baseline exists, or if the reduction only "
                "comes from suppressing more than 25 percent of gold-supported facts."
            ),
        ),
        status_record(
            item_id="H2",
            label="Validator/repair improves valid yield",
            status=h2_status,
            rationale=h2_rationale,
            evidence=[
                f"s2_accepted_fact_count={s2_accepted}",
                f"s3_accepted_fact_count={s3_accepted}",
                f"s3_repair_success_rate={s3_repair_success}",
                f"s2_manual_semantic_correctness={s2_semantic}",
                f"s3_manual_semantic_correctness={s3_semantic}",
            ],
            falsification_criterion=(
                "Falsified if S3 repair success is below 15 percent of initially invalid "
                "facts, or if S3 manual semantic correctness is more than 5 percentage "
                "points lower than S2."
            ),
        ),
        status_record(
            item_id="H3",
            label="Hybrid backbone plus enrichment improves selected semantic predicates",
            status=h3_status,
            rationale=h3_rationale,
            evidence=[
                f"s1_precision={s1_precision}",
                f"s3_precision={s3_precision}",
                f"s1_f1={s1_f1}",
                f"s3_f1={s3_f1}",
                f"s1_semantic_scoring_validity={s1_scoring_validity}",
                f"s0_selected_semantic_macro_f1={s0_h3_semantic_f1}",
                f"s4_selected_semantic_macro_f1={s4_h3_semantic_f1}",
                f"s0_deterministic_macro_f1={s0_deterministic_f1}",
                f"s4_deterministic_macro_f1={s4_deterministic_f1}",
            ],
            falsification_criterion=(
                "Falsified if S4 hybrid does not improve selected semantic "
                "predicate F1 over S0 while preserving deterministic-field F1 within the "
                "pre-registered tolerance."
            ),
        ),
        status_record(
            item_id="H4",
            label="Rejection triage produces actionable engineering decisions",
            status=h4_status,
            rationale=h4_rationale,
            evidence=[
                f"rejected_fact_count={rejection_count}",
                "final_decision_counts_by_fact="
                f"{json.dumps(final_rejection_decisions, sort_keys=True)}",
            ],
            falsification_criterion=(
                "Falsified if more than 20 percent of rejected facts remain manual-review-only "
                "after review, or if profile extensions cannot be tied to source evidence and "
                "NASA ATMONTO terms."
            ),
        ),
    ]
    return {"claims": claims, "hypotheses": hypotheses}


def formal_completion_audit(
    *,
    manifest: dict[str, Any],
    protocol_text: str,
    gold_source: dict[str, Any],
    system_scores: list[dict[str, Any]],
    rejection_analysis: dict[str, Any],
    rejection_adjudication: dict[str, Any],
    claim_statuses: list[dict[str, Any]],
    hypothesis_statuses: list[dict[str, Any]],
) -> dict[str, Any]:
    sample_size = int(manifest.get("sample_size", 0))
    sample_ok = 80 <= sample_size <= 120
    systems_by_id = system_score_by_id(system_scores)
    all_system_outputs = all(score.get("output_exists") for score in system_scores)
    all_semantic = all(
        bool((score.get("semantic_metrics") or {}).get("available"))
        for score in system_scores
    )
    all_scores = all_system_outputs and all_semantic
    rejection_count = int(rejection_analysis.get("rejected_fact_count", 0))
    rejection_group_total = sum(int(group.get("count", 0)) for group in rejection_analysis.get("groups", []))
    final_rejection_decisions = rejection_adjudication.get("decision_counts_by_fact", {})
    adjudication_complete = bool(rejection_adjudication.get("property_level_complete"))
    terminal_statuses = {"supported", "supported_by_pilot", "falsified", "inconclusive"}
    final_claims = all(
        status["status"] in terminal_statuses
        for status in [*claim_statuses, *hypothesis_statuses]
    )
    pilot_positioning = all(
        marker in protocol_text
        for marker in [
            "Prior stage: pilot / feasibility study",
            "## Current Pilot Positioning",
            "bronze_until_reviewed",
            "structural validation is not semantic correctness",
        ]
    )
    protocol_fixed = all(
        marker in protocol_text
        for marker in [
            "## Research Claims",
            "## Hypotheses And Falsification Criteria",
            "## Baselines And Comparators",
            "## Metrics",
            "Falsified if",
            "JSON Adherence",
            "Manual Semantic Correctness",
        ]
    )

    requirements = [
        {
            "id": "R0",
            "requirement": "Position the current NASA ATMONTO loop as pilot / feasibility evidence, not a completed formal experiment.",
            "status": "satisfied" if pilot_positioning else "incomplete_claim_boundary",
            "evidence": "docs/experiment_protocol.md contains pilot/feasibility boundary and bronze-until-reviewed language.",
        },
        {
            "id": "R1",
            "requirement": "Sample 80-120 ATCSCC advisories for the formal gold set.",
            "status": "satisfied" if sample_ok else "incomplete",
            "evidence": f"sample_size={sample_size}; manifest=data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json",
        },
        {
            "id": "R2",
            "requirement": "Freeze reviewed gold annotations before semantic scoring.",
            "status": (
                "satisfied"
                if gold_source.get("ready_for_formal_scoring")
                else "pending_manual_input"
            ),
            "evidence": (
                f"gold_source={gold_source.get('source')}; "
                f"template_reviewed={gold_source.get('template_reviewed_record_count')}; "
                f"template_pending={gold_source.get('template_pending_record_count')}"
            ),
        },
        {
            "id": "R3",
            "requirement": (
                "Define the corrected system suite: S0, diagnostic S1, S1b, S2, S3, "
                "and S4."
            ),
            "status": (
                "satisfied"
                if set(systems_by_id) == {
                    "S0_rule_only",
                    "S1_llm_only",
                    "S1b_llm_canonicalized",
                    "S2_llm_schema_slice",
                    "S3_llm_schema_slice_validator_repair",
                    "S4_hybrid_backbone_enrichment",
                }
                else "incomplete"
            ),
            "evidence": f"systems={','.join(sorted(systems_by_id))}",
        },
        {
            "id": "R4",
            "requirement": "Run all corrected-stage systems on the identical sampled records.",
            "status": "satisfied" if all_system_outputs else "pending_model_output",
            "evidence": json.dumps(
                {
                    score["system_id"]: bool(score.get("output_exists"))
                    for score in system_scores
                },
                sort_keys=True,
            ),
        },
        {
            "id": "R5",
            "requirement": "Define JSON, schema, semantic, repair, and manual-correctness metrics.",
            "status": "satisfied",
            "evidence": "docs/experiment_protocol.md and reports/stages/nasa_atmonto_formal_experiment_scoring.json",
        },
        {
            "id": "R6",
            "requirement": "Report JSON adherence, schema violation rate, precision/recall/F1, repair success, and manual semantic correctness.",
            "status": "satisfied" if all_scores else "pending_scoring",
            "evidence": f"all_system_outputs={all_system_outputs}; all_semantic_metrics_available={all_semantic}",
        },
        {
            "id": "R7",
            "requirement": (
                "Account for all pilot rejections in property-level error analysis."
            ),
            "status": (
                "satisfied"
                if rejection_group_total == rejection_count
                else "incomplete_rejection_accounting"
            ),
            "evidence": f"rejected_fact_count={rejection_count}; grouped_fact_count={rejection_group_total}",
        },
        {
            "id": "R8",
            "requirement": "Finalize whether each rejection group is extractor bug, NASA ATMONTO profile gap, source ambiguity, or manual-review-only.",
            "status": "satisfied" if adjudication_complete else "pending_manual_adjudication",
            "evidence": json.dumps(final_rejection_decisions, sort_keys=True),
        },
        {
            "id": "R9",
            "requirement": "Assign supported, falsified, or inconclusive status to claims C1-C4 and hypotheses H1-H4.",
            "status": "satisfied" if final_claims else "pending_scoring",
            "evidence": json.dumps(
                {
                    status["id"]: status["status"]
                    for status in [*claim_statuses, *hypothesis_statuses]
                },
                sort_keys=True,
            ),
        },
        {
            "id": "R10",
            "requirement": "Fix the protocol artifact with claims, hypotheses, baselines, metrics, and falsification criteria.",
            "status": "satisfied" if protocol_fixed else "incomplete_protocol",
            "evidence": "docs/experiment_protocol.md",
        },
    ]
    blockers = [
        requirement["id"]
        for requirement in requirements
        if requirement["status"] != "satisfied"
    ]
    return {
        "overall_status": (
            "formal_experiment_complete" if not blockers else "formal_experiment_pending"
        ),
        "blocking_requirement_ids": blockers,
        "requirements": requirements,
        "claim_boundary": (
            "A satisfied audit means the formal experiment can be reported; pending items "
            "must remain described as pilot/prepared-state evidence."
        ),
    }


def build_formal_experiment_score_report(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    input_records = read_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH)
    schema_slice = read_json(repo_root / SCHEMA_SLICE_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_source = formal_scoring_gold_source(repo_root, selected_ids)
    gold_records = gold_source["records"]
    gold_status = gold_source["gold_status"]
    semantic_groups = build_gold_semantic_groups(repo_root)
    system_scores = [
        score_system_predictions(
            system=system,
            repo_root=repo_root,
            selected_ids=selected_ids,
            input_records=input_records,
            gold_records=gold_records,
            schema_slice=schema_slice,
            semantic_groups=semantic_groups,
        )
        for system in SYSTEMS
    ]
    rejection_analysis = read_json(repo_root / REJECTION_ANALYSIS_JSON)
    rejection_adjudication = build_rejection_adjudication_report(
        repo_root,
        rejection_analysis=rejection_analysis,
    )
    claim_hypothesis_status = claim_and_hypothesis_statuses(
        system_scores=system_scores,
        gold_source=gold_source,
        rejection_analysis=rejection_analysis,
        rejection_adjudication=rejection_adjudication,
    )
    protocol_text = (repo_root / "docs/experiment_protocol.md").read_text(encoding="utf-8")
    completion_audit = formal_completion_audit(
        manifest=manifest,
        protocol_text=protocol_text,
        gold_source=gold_source,
        system_scores=system_scores,
        rejection_analysis=rejection_analysis,
        rejection_adjudication=rejection_adjudication,
        claim_statuses=claim_hypothesis_status["claims"],
        hypothesis_statuses=claim_hypothesis_status["hypotheses"],
    )
    missing_inputs: list[str] = []
    if not gold_source["ready_for_formal_scoring"]:
        missing_inputs.append(
            f"frozen reviewed gold set at {gold_source['path']}"
        )
    if gold_source["template_validation_status"] != "ready_for_scoring":
        missing_inputs.append("completed manual gold annotations for 100 sampled advisories")
    for score in system_scores:
        if not score["output_exists"]:
            missing_inputs.append(f"{score['system_id']} predictions at {score['expected_output']}")
    if any(score["semantic_metrics"] and not score["semantic_metrics"]["available"] for score in system_scores):
        missing_inputs.append("manual semantic metrics require reviewed gold facts")

    return {
        "source_family": "nasa_atmonto_formal_experiment_scoring",
        "status": "scored" if not missing_inputs else "pending_required_inputs",
        "protocol": "docs/experiment_protocol.md",
        "gold_source": {
            key: value
            for key, value in gold_source.items()
            if key != "records"
        },
        "gold_status": gold_status,
        "semantic_groups": {
            key: value
            for key, value in semantic_groups.items()
            if key != "records"
        },
        "methodology_remediation": source_family_methodology_boundaries(repo_root),
        "consensus_sota_remediation": consensus_sota_remediation_constraints(),
        "systems": system_scores,
        "rejection_adjudication": {
            key: value
            for key, value in rejection_adjudication.items()
            if key != "groups"
        },
        "claim_statuses": claim_hypothesis_status["claims"],
        "hypothesis_statuses": claim_hypothesis_status["hypotheses"],
        "completion_audit": completion_audit,
        "missing_required_inputs": missing_inputs,
        "metrics_reported": [
            "json_adherence",
            "structural_acceptance_rate",
            "schema_violation_rate",
            "triple_precision",
            "triple_recall",
            "triple_f1",
            "semantic_group_triple_precision_recall_f1",
            "repair_success_rate",
            "manual_semantic_correctness",
        ],
        "claim_boundary": (
            "Formal metrics are descriptive until all four systems have predictions and "
            "the frozen reviewed gold set is available."
        ),
    }


def score_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Formal Experiment Scoring",
        "",
        f"- Status: `{report['status']}`",
        f"- Protocol: `{report['protocol']}`",
        "",
        "## Gold Source",
        "",
        f"- Source: `{report['gold_source']['source']}`",
        f"- Path: `{report['gold_source']['path']}`",
        f"- Exists: `{report['gold_source']['exists']}`",
        f"- Ready for scoring: `{report['gold_source']['ready_for_formal_scoring']}`",
        f"- SHA-256: `{report['gold_source']['sha256']}`",
        "",
        "## Gold Status",
        "",
    ]
    gold = report["gold_status"]
    lines.extend(
        [
            f"- Records: {gold['record_count']}",
            f"- Reviewed records: {gold['reviewed_record_count']}",
            f"- Pending records: {gold['pending_record_count']}",
            f"- Complete: `{gold['complete']}`",
            "",
            "## Methodology Remediation",
            "",
            f"- Status: `{report['methodology_remediation']['status']}`",
            f"- Scope: {report['methodology_remediation']['scope_statement']}",
            f"- Cross-source metric policy: {report['methodology_remediation']['cross_source_metric_policy']}",
            "",
            "| Source family | Data shape | Task | Boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for family in report["methodology_remediation"]["source_families"]:
        boundary = (
            "Current scored ATCSCC event extraction."
            if family["id"] == "A"
            else "Next-rerun PDF reference extraction; do not mix definition/procedure F1 with ATCSCC event F1."
        )
        lines.append(
            "| "
            f"`{family['source_family']}` | "
            f"`{family['data_shape']}` | "
            f"{family['task']} | "
            f"{boundary} |"
        )
    pdf_family = next(
        family
        for family in report["methodology_remediation"]["source_families"]
        if family["id"] == "B"
    )
    lines.extend(
        [
            "",
            "- PDF backend policy: `hybrid_docling_pymupdf` is the candidate default; "
            "`pymupdf_text_legacy` is a baseline only.",
            "- PDF target predicates: "
            f"`{', '.join(pdf_family['allowed_predicates'])}`.",
            "- PDF provenance fields: "
            f"`{', '.join(pdf_family['required_provenance_fields'])}`.",
            "",
            "## Consensus SOTA Constraints",
            "",
        ]
    )
    sota = report["consensus_sota_remediation"]
    lines.extend(
        [
            f"- Status: `{sota['status']}`",
            f"- Boundary: {sota['scope_boundary']}",
            "- S1 interpretation: "
            "`S1_raw_open_llm` is a drift diagnostic; "
            "`S1b_llm_canonicalized` is the comparable target-schema baseline.",
            "- Nine-stage pipeline: "
            f"`{' -> '.join(sota['nine_stage_pipeline'])}`.",
            "- Reviewed dev examples artifact: `reviewed_dev_examples`; use 10-20 "
            "examples outside the held-out 100 scoring records.",
            "",
            "| SOTA constraint | Implementation | Claim guardrail |",
            "| --- | --- | --- |",
        ]
    )
    for constraint in sota["sota_adaptations"]:
        lines.append(
            "| "
            f"`{constraint['anchor']}` | "
            f"{constraint['implementation']} | "
            f"{constraint['claim_guardrail']} |"
        )
    s4_policy = sota["s4_merge_policy"]
    artifact_names = [
        artifact.get("path") or artifact.get("component")
        for artifact in sota["planned_artifacts"]
    ]
    lines.extend(
        [
            "",
            "- S4 primary candidate: "
            f"`{s4_policy['primary_candidate_system']}`.",
            "- S0 owns deterministic fields: "
            f"`{', '.join(s4_policy['s0_owns'])}`.",
            "- S3/S4 may add but not overwrite semantic fields: "
            f"`{', '.join(s4_policy['s3_s4_may_add_not_overwrite'])}`.",
            "- Quarantine/review conditions: "
            f"`{', '.join(s4_policy['quarantine_conditions'])}`.",
            "- Planned artifacts/TODO: "
            f"`{', '.join(name for name in artifact_names if name)}`.",
            "- Unverified search leads remain `requiring verification`: "
            f"`{', '.join(sota['unverified_search_leads']['items'])}`.",
            "- GraphRAG boundary: report `KG construction`, `graph retrieval`, and "
            "`answer faithfulness/completeness/citation support` separately; current "
            "remediation makes no end-to-end GraphRAG answer improvement claim.",
            "",
            "## Corrected Stage Results",
            "",
        ]
    )
    score_by_id = {str(score["system_id"]): score for score in report["systems"]}
    s0_score = score_by_id.get("S0_rule_only", {})
    s1b_score = score_by_id.get("S1b_llm_canonicalized", {})
    s4_score = score_by_id.get("S4_hybrid_backbone_enrichment", {})
    if s1b_score:
        s1b_structural = s1b_score.get("structural_metrics") or {}
        s1b_semantic = s1b_score.get("semantic_metrics") or {}
        lines.append(
            "- `S1b_llm_canonicalized`: "
            f"accepted {s1b_structural.get('accepted_fact_count')} / "
            f"{s1b_structural.get('candidate_fact_count')} mapped facts; "
            f"target-schema F1={s1b_semantic.get('f1')}."
        )
    if s4_score:
        s4_semantic_macro = macro_property_metric(
            s4_score,
            ("implementationStatus", "reRouteReason", "reRouteType"),
            "f1",
        )
        s0_semantic_macro = macro_property_metric(
            s0_score,
            ("implementationStatus", "reRouteReason", "reRouteType"),
            "f1",
        )
        s4_deterministic_macro = macro_property_metric(
            s4_score,
            sorted(DETERMINISTIC_BACKBONE_PREDICATES),
            "f1",
        )
        s0_deterministic_macro = macro_property_metric(
            s0_score,
            sorted(DETERMINISTIC_BACKBONE_PREDICATES),
            "f1",
        )
        lines.append(
            "- `S4_hybrid_backbone_enrichment`: selected semantic macro-F1 "
            f"{s0_semantic_macro} -> {s4_semantic_macro}; deterministic macro-F1 "
            f"{s0_deterministic_macro} -> {s4_deterministic_macro}."
        )
    lines.extend(
        [
            "",
            "## System Metrics",
            "",
            "| System | Output | JSON adherence | Candidate facts | Accepted | Rejected | Structural acceptance | Schema violation rate | Repair success | Semantic metrics |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for score in report["systems"]:
        json_metrics = score.get("json_metrics") or {}
        structural = score.get("structural_metrics") or {}
        semantic = score.get("semantic_metrics") or {}
        semantic_text = (
            (
                "`invalid_direct_schema_scoring`; "
                f"diagnostic P={semantic.get('precision')}, R={semantic.get('recall')}, "
                f"F1={semantic.get('f1')}"
            )
            if semantic.get("scoring_validity") == "invalid_direct_schema_scoring"
            else f"P={semantic.get('precision')}, R={semantic.get('recall')}, F1={semantic.get('f1')}"
            if semantic.get("available")
            else f"pending:{semantic.get('reason') or score.get('reason')}"
        )
        lines.append(
            "| "
            f"`{score['system_id']}` | "
            f"`{score['output_exists']}` | "
            f"{metric_value_text(json_metrics.get('json_adherence'))} | "
            f"{metric_value_text(structural.get('candidate_fact_count'))} | "
            f"{metric_value_text(structural.get('accepted_fact_count'))} | "
            f"{metric_value_text(structural.get('rejected_fact_count'))} | "
            f"{metric_value_text(structural.get('structural_acceptance_rate'))} | "
            f"{metric_value_text(structural.get('schema_violation_rate'))} | "
            f"{metric_value_text(structural.get('repair_success_rate'))} | "
            f"{semantic_text} |"
        )
    ci_rows = [
        (score["system_id"], (score.get("semantic_metrics") or {}).get("confidence_intervals"))
        for score in report["systems"]
        if ((score.get("semantic_metrics") or {}).get("confidence_intervals") or {}).get("available")
        and (score.get("semantic_metrics") or {}).get("scoring_validity")
        != "invalid_direct_schema_scoring"
    ]
    if ci_rows:
        lines.extend(
            [
                "",
                "## Semantic Confidence Intervals",
                "",
                "| System | Method | Precision 95% CI | Recall 95% CI | F1 95% CI |",
                "| --- | --- | ---: | ---: | ---: |",
            ]
        )
        for system_id, intervals in ci_rows:
            values = intervals["intervals"]
            lines.append(
                "| "
                f"`{system_id}` | "
                f"`{intervals['method']}` ({intervals['iterations']} iter, seed={intervals['seed']}) | "
                f"{metric_interval_text(values['precision'])} | "
                f"{metric_interval_text(values['recall'])} | "
                f"{metric_interval_text(values['f1'])} |"
            )
    group_rows = [
        (score["system_id"], row)
        for score in report["systems"]
        for row in score.get("semantic_group_metrics", [])
        if (row.get("semantic_metrics") or {}).get("available")
        and (score.get("semantic_metrics") or {}).get("scoring_validity")
        != "invalid_direct_schema_scoring"
    ]
    if group_rows:
        lines.extend(
            [
                "",
                "## Semantic Group Metrics",
                "",
                "- Semantic groups are stratified reporting slices, not train/dev/test splits.",
                "",
                "| System | Group | Records | Gold facts | Predicted facts | Precision | Recall | F1 |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for system_id, row in group_rows:
            metrics = row["semantic_metrics"]
            lines.append(
                "| "
                f"`{system_id}` | "
                f"`{row['group_id']}` | "
                f"{row['record_count']} | "
                f"{row['gold_fact_count']} | "
                f"{row['predicted_fact_count']} | "
                f"{metric_value_text(metrics.get('precision'))} | "
                f"{metric_value_text(metrics.get('recall'))} | "
                f"{metric_value_text(metrics.get('f1'))} |"
            )
    adjudication = report["rejection_adjudication"]
    lines.extend(
        [
            "",
            "## Rejection Adjudication",
            "",
            f"- Property-level complete: `{adjudication['property_level_complete']}`",
            f"- Decision counts: `{json.dumps(adjudication['decision_counts_by_fact'], sort_keys=True)}`",
            f"- Pending facts: {adjudication['pending_fact_count']}",
        ]
    )
    lines.extend(
        [
            "",
            "## Claim Status",
            "",
            "| Claim | Status | Rationale |",
            "| --- | --- | --- |",
        ]
    )
    for claim in report["claim_statuses"]:
        lines.append(
            f"| `{claim['id']}` {claim['label']} | `{claim['status']}` | {claim['rationale']} |"
        )
    lines.extend(
        [
            "",
            "## Hypothesis Status",
            "",
            "| Hypothesis | Status | Falsification criterion |",
            "| --- | --- | --- |",
        ]
    )
    for hypothesis in report["hypothesis_statuses"]:
        lines.append(
            "| "
            f"`{hypothesis['id']}` {hypothesis['label']} | "
            f"`{hypothesis['status']}` | "
            f"{hypothesis.get('falsification_criterion', '')} |"
        )
    audit = report["completion_audit"]
    lines.extend(
        [
            "",
            "## Completion Audit",
            "",
            f"- Overall status: `{audit['overall_status']}`",
            f"- Blocking requirements: `{json.dumps(audit['blocking_requirement_ids'])}`",
            "",
            "| Requirement | Status | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for requirement in audit["requirements"]:
        lines.append(
            "| "
            f"`{requirement['id']}` {requirement['requirement']} | "
            f"`{requirement['status']}` | "
            f"{requirement['evidence']} |"
        )
    lines.extend(["", "## Missing Required Inputs", ""])
    for item in report["missing_required_inputs"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", f"- {report['claim_boundary']}"])
    return "\n".join(lines) + "\n"


def build_formal_experiment_readiness(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    session_plan: dict[str, Any] | None = None,
    decision_progress: dict[str, Any] | None = None,
    review_progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    s0_payloads = read_jsonl(repo_root / S0_CANDIDATES_PATH)
    s0_validations_all = read_jsonl(repo_root / S0_VALIDATED_PATH)

    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    s0_validations = selected_validations(s0_validations_all, selected_ids)
    s0_predictions = accepted_prediction_facts(s0_validations)
    gold_status = gold_annotation_status(gold_records)

    formal_input_status = {
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "input_records_exists": (repo_root / FORMAL_INPUT_RECORDS_PATH).exists(),
        "system_specs": project_relative_path(repo_root / FORMAL_SYSTEM_SPECS_PATH, repo_root),
        "system_specs_exists": (repo_root / FORMAL_SYSTEM_SPECS_PATH).exists(),
    }

    system_output_status: list[dict[str, Any]] = []
    for system in SYSTEMS:
        output_path = repo_root / system.expected_output
        prompt_path = repo_root / system.prompt_batch if system.prompt_batch else None
        system_output_status.append(
            {
                "system_id": system.system_id,
                "expected_output": project_relative_path(output_path, repo_root),
                "exists": output_path.exists(),
                "prompt_batch": (
                    project_relative_path(prompt_path, repo_root) if prompt_path else None
                ),
                "prompt_batch_exists": prompt_path.exists() if prompt_path else None,
                "required_before_formal_scoring": system.system_id != "S0_rule_only",
            }
        )

    s0_structural = structural_metrics(s0_validations, repair_applicable=False)
    s0_json = json_adherence_from_payloads(s0_payloads, selected_ids)
    s0_semantic = semantic_metrics(predictions=s0_predictions, gold_records=gold_records)

    missing_inputs = []
    if not formal_input_status["input_records_exists"]:
        missing_inputs.append("formal input records for the 100 sampled advisories")
    if not formal_input_status["system_specs_exists"]:
        missing_inputs.append("formal system specs for S0-S3")
    if not gold_status["complete"]:
        missing_inputs.append("completed manual gold annotations for 100 sampled advisories")
    for item in system_output_status:
        if item["prompt_batch"] and not item["prompt_batch_exists"]:
            missing_inputs.append(f"{item['system_id']} prompt batch at {item['prompt_batch']}")
        if item["required_before_formal_scoring"] and not item["exists"]:
            missing_inputs.append(f"{item['system_id']} predictions at {item['expected_output']}")

    if not missing_inputs:
        status = "ready_for_scoring"
    elif missing_inputs == ["completed manual gold annotations for 100 sampled advisories"]:
        status = "ready_for_manual_gold_review"
    else:
        status = "ready_for_manual_gold_and_llm_runs"
    session_plan = session_plan or build_gold_review_session_plan(repo_root)
    review_kickoff = build_manual_gold_review_kickoff(
        repo_root,
        gold_status=gold_status,
        session_plan=session_plan,
        decision_progress=decision_progress,
        review_progress=review_progress,
    )

    return {
        "source_family": "nasa_atmonto_formal_experiment_readiness",
        "status": status,
        "protocol": "docs/experiment_protocol.md",
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "manual_review_artifacts": {
            "worklist": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_MD, repo_root),
            "workload_plan": project_relative_path(
                repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD,
                repo_root,
            ),
            "semantic_groups": project_relative_path(
                repo_root / GOLD_SEMANTIC_GROUPS_MD,
                repo_root,
            ),
            "session_plan": project_relative_path(
                repo_root / GOLD_REVIEW_SESSION_PLAN_MD,
                repo_root,
            ),
            "priority_packets": project_relative_path(
                repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
                repo_root,
            ),
            "batch_index": project_relative_path(repo_root / GOLD_REVIEW_BATCH_INDEX_MD, repo_root),
            "decision_templates": project_relative_path(
                repo_root / GOLD_REVIEW_DECISION_INDEX_MD,
                repo_root,
            ),
            "progress": project_relative_path(repo_root / GOLD_REVIEW_PROGRESS_MD, repo_root),
        },
        "manual_gold_review_kickoff": review_kickoff,
        "gold_status": gold_status,
        "formal_input_status": formal_input_status,
        "systems": system_definitions(repo_root),
        "system_output_status": system_output_status,
        "current_s0_rule_only_structural_metrics": {
            **s0_json,
            **s0_structural,
            "semantic_metrics": s0_semantic,
        },
        "metrics_defined": [
            "json_adherence",
            "structural_acceptance_rate",
            "schema_violation_rate",
            "triple_precision",
            "triple_recall",
            "triple_f1",
            "repair_success_rate",
            "manual_semantic_correctness",
        ],
        "missing_required_inputs": missing_inputs,
        "claim_boundary": (
            "This readiness report does not claim formal extraction effectiveness until "
            "manual gold annotations are complete and all required system outputs are present."
        ),
    }


def read_json_if_exists(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {}


def build_manual_gold_review_kickoff(
    repo_root: Path,
    *,
    gold_status: dict[str, Any],
    session_plan: dict[str, Any] | None = None,
    decision_progress: dict[str, Any] | None = None,
    review_progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    priority_packets = read_json_if_exists(repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON)
    decision_progress = decision_progress or read_json_if_exists(
        repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON
    )
    review_progress = review_progress or read_json_if_exists(repo_root / GOLD_REVIEW_PROGRESS_JSON)
    session_plan = session_plan or read_json_if_exists(repo_root / GOLD_REVIEW_SESSION_PLAN_JSON)
    lanes = priority_packets.get("lanes", [])
    first_lane = lanes[0] if lanes else {}
    first_record = (first_lane.get("records") or [{}])[0]
    complete = bool(gold_status.get("complete"))
    next_session = (
        None
        if complete
        else session_plan.get("next_session") or (session_plan.get("sessions") or [{}])[0]
    )
    return {
        "status": "complete" if complete else "ready_for_manual_gold_review",
        "reviewed_record_count": gold_status.get("reviewed_record_count", 0),
        "pending_record_count": gold_status.get("pending_record_count", 0),
        "decision_progress_status": decision_progress.get("status"),
        "ready_to_apply_record_count": decision_progress.get("ready_to_apply_record_count"),
        "not_started_record_count": decision_progress.get("not_started_record_count"),
        "completed_rejected_fact_decision_count": decision_progress.get(
            "completed_rejected_fact_decision_count"
        ),
        "rejected_fact_decision_count": decision_progress.get("rejected_fact_decision_count"),
        "complete_batch_count": review_progress.get("complete_batch_count"),
        "batch_count": review_progress.get("batch_count"),
        "first_priority_lane": {
            "lane_id": first_lane.get("lane_id"),
            "label": first_lane.get("label"),
            "record_count": first_lane.get("record_count"),
            "estimated_review_minutes": first_lane.get("estimated_review_minutes"),
            "packet_markdown": first_lane.get("path"),
            "first_sample_id": first_record.get("sample_id"),
            "first_source_id": first_record.get("source_id"),
            "first_batch_id": first_record.get("batch_id"),
            "first_decision_template": first_record.get("decision_template"),
            "first_batch_markdown": first_record.get("batch_markdown"),
        },
        "next_review_session": None
        if complete
        else {
            "session_id": next_session.get("session_id"),
            "status": next_session.get("status"),
            "record_count": next_session.get("record_count"),
            "ready_to_apply_record_count": next_session.get("ready_to_apply_record_count"),
            "remaining_record_count": next_session.get("remaining_record_count"),
            "estimated_review_minutes": next_session.get("estimated_review_minutes"),
            "pending_rejected_fact_decision_count": next_session.get(
                "pending_rejected_fact_decision_count"
            ),
            "first_sample_id": (next_session.get("records") or [{}])[0].get("sample_id"),
            "first_source_id": (next_session.get("records") or [{}])[0].get("source_id"),
            "session_plan_markdown": session_plan.get("session_plan_markdown"),
        },
        "next_commands": [
            "uv run python scripts/prepare_nasa_atmonto_gold_review_decision_progress.py",
            "uv run python scripts/apply_nasa_atmonto_gold_review_decisions.py",
            "uv run python scripts/validate_nasa_atmonto_gold_annotations.py",
            "uv run python scripts/freeze_nasa_atmonto_gold_set.py",
            "uv run python scripts/run_nasa_atmonto_formal_experiment.py --skip-prepare-inputs",
        ],
        "review_boundary": (
            "Priority packets and suggested_* fields are work aids only. A record becomes "
            "gold only after source review, completed review_checklist, confirmed decisions, "
            "validation, and frozen reviewed output."
        ),
    }


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Formal Experiment Readiness",
        "",
        f"- Status: `{report['status']}`",
        f"- Protocol: `{report['protocol']}`",
        f"- Gold manifest: `{report['gold_manifest']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Workload plan: `{report['manual_review_artifacts']['workload_plan']}`",
        f"- Semantic groups: `{report['manual_review_artifacts']['semantic_groups']}`",
        f"- Session plan: `{report['manual_review_artifacts']['session_plan']}`",
        f"- Priority packets: `{report['manual_review_artifacts']['priority_packets']}`",
        f"- Review progress: `{report['manual_review_artifacts']['progress']}`",
        "",
        "## Gold Status",
        "",
    ]
    gold = report["gold_status"]
    lines.extend(
        [
            f"- Records: {gold['record_count']}",
            f"- Reviewed records: {gold['reviewed_record_count']}",
            f"- Pending records: {gold['pending_record_count']}",
            f"- Complete: `{gold['complete']}`",
            f"- Status counts: `{json.dumps(gold['status_counts'], sort_keys=True)}`",
            "",
            "## Manual Gold Review Kickoff",
            "",
        ]
    )
    kickoff = report["manual_gold_review_kickoff"]
    first_lane = kickoff["first_priority_lane"]
    next_session = kickoff["next_review_session"]
    lines.extend(
        [
            f"- Status: `{kickoff['status']}`",
            f"- Reviewed / pending records: {kickoff['reviewed_record_count']} / {kickoff['pending_record_count']}",
            f"- Decision progress: `{kickoff['decision_progress_status']}`",
            f"- Ready to apply / not started: {kickoff['ready_to_apply_record_count']} / {kickoff['not_started_record_count']}",
            "- Rejected-fact decisions confirmed: "
            f"{kickoff['completed_rejected_fact_decision_count']} / "
            f"{kickoff['rejected_fact_decision_count']}",
            "- First priority lane: "
            f"`{first_lane['lane_id']}` ({first_lane['record_count']} records, "
            f"{first_lane['estimated_review_minutes']} est. min)",
            f"- Start packet: `{first_lane['packet_markdown']}`",
            "- First sample: "
            f"`{first_lane['first_sample_id']}` / `{first_lane['first_source_id']}` "
            f"via `{first_lane['first_decision_template']}`",
            f"- Boundary: {kickoff['review_boundary']}",
            "",
        ]
    )
    next_section = ["", "### Next Commands", ""]
    if next_session:
        next_section[:0] = [
            "- Next session sample: "
            f"`{next_session['first_sample_id']}` / `{next_session['first_source_id']}`",
            "- Next review session: "
            f"`{next_session['session_id']}` ({next_session['record_count']} records, "
            f"{next_session['estimated_review_minutes']} est. min, "
            f"status=`{next_session['status']}`) "
            f"from `{next_session['session_plan_markdown']}`",
        ]
    else:
        next_section[:0] = ["- Next review session: `none`; gold review is complete."]
    for command in kickoff["next_commands"]:
        next_section.append(f"- `{command}`")
    lines.extend(next_section)
    lines.extend(
        [
            "",
            "## Formal Inputs",
            "",
            f"- Input records: `{report['formal_input_status']['input_records']}`",
            f"- Input records exists: `{report['formal_input_status']['input_records_exists']}`",
            f"- System specs: `{report['formal_input_status']['system_specs']}`",
            f"- System specs exists: `{report['formal_input_status']['system_specs_exists']}`",
            "",
            "## Systems",
            "",
        ]
    )
    output_status = {item["system_id"]: item for item in report["system_output_status"]}
    for system in report["systems"]:
        status = output_status[system["system_id"]]
        lines.append(
            f"- `{system['system_id']}`: {system['label']} "
            f"(LLM={system['requires_llm']}, schema={system['uses_schema_slice']}, "
            f"repair={system['uses_validator_repair']}, "
            f"prompt_ready={status['prompt_batch_exists']}, output_ready={status['exists']})"
        )
    lines.extend(["", "## Current S0 Structural Metrics", ""])
    s0 = report["current_s0_rule_only_structural_metrics"]
    for key in (
        "attempted_record_count",
        "valid_json_payload_count",
        "json_adherence",
        "candidate_fact_count",
        "accepted_fact_count",
        "rejected_fact_count",
        "structural_acceptance_rate",
        "schema_violation_rate",
        "repair_applicable",
        "repair_attempted_fact_count",
        "repair_accepted_fact_count",
        "repair_success_rate",
    ):
        lines.append(f"- `{key}`: {metric_value_text(s0.get(key))}")
    lines.extend(["", "## Missing Required Inputs", ""])
    for item in report["missing_required_inputs"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"- {report['claim_boundary']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_formal_experiment_readiness(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    prepare_inputs: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    prepared = prepare_formal_experiment_inputs(repo_root) if prepare_inputs else None
    gold_worklist = build_gold_review_worklist(repo_root)
    gold_validation = build_gold_annotation_validation_report(repo_root)
    gold_freeze_status = build_gold_freeze_status(repo_root)
    prediction_validation = build_prediction_output_validation_report(repo_root)
    candidate_review = build_system_candidate_review_package(repo_root)
    batch_report = build_gold_review_batches(repo_root, candidate_review=candidate_review)
    workload_plan = build_gold_review_workload_plan(repo_root)
    semantic_groups = build_gold_semantic_groups(repo_root, workload_plan=workload_plan)
    priority_packets = build_gold_review_priority_packets(repo_root)
    existing_decision_root = repo_root / GOLD_REVIEW_DECISION_DIR
    existing_decisions = (
        read_gold_review_decisions(existing_decision_root)
        if existing_decision_root.exists()
        else []
    )
    preserve_existing_decisions = any(
        gold_review_decision_has_manual_edits(decision)
        for decision in existing_decisions
    )
    decision_report = build_gold_review_decision_templates(
        repo_root,
        batch_report=batch_report,
    )
    progress_report = build_gold_review_progress(repo_root, batch_report=batch_report)
    rejection_adjudication = build_rejection_adjudication_report(repo_root)
    write_json(repo_root / GOLD_REVIEW_WORKLIST_JSON, gold_worklist)
    write_json(repo_root / GOLD_VALIDATION_REPORT_JSON, gold_validation)
    write_json(repo_root / GOLD_FREEZE_REPORT_JSON, gold_freeze_status)
    write_json(repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON, prediction_validation)
    write_json(repo_root / REJECTION_ADJUDICATION_JSON, rejection_adjudication)
    write_json(repo_root / GOLD_REVIEW_PROGRESS_JSON, progress_report)
    write_json(repo_root / GOLD_REVIEW_WORKLOAD_PLAN_JSON, workload_plan)
    write_json(repo_root / GOLD_SEMANTIC_GROUPS_JSON, semantic_groups)
    write_json(
        repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON,
        gold_review_priority_packet_summary(priority_packets),
    )
    write_jsonl(repo_root / GOLD_CANDIDATE_REVIEW_JSONL, candidate_review["records"])
    (repo_root / GOLD_REVIEW_WORKLIST_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).write_text(
        gold_review_worklist_markdown(gold_worklist),
        encoding="utf-8",
    )
    (repo_root / GOLD_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_VALIDATION_REPORT_MD).write_text(
        gold_validation_markdown(gold_validation),
        encoding="utf-8",
    )
    (repo_root / GOLD_FREEZE_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_FREEZE_REPORT_MD).write_text(
        gold_freeze_status_markdown(gold_freeze_status),
        encoding="utf-8",
    )
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).write_text(
        prediction_output_validation_markdown(prediction_validation),
        encoding="utf-8",
    )
    (repo_root / GOLD_CANDIDATE_REVIEW_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_CANDIDATE_REVIEW_MD).write_text(
        system_candidate_review_markdown(candidate_review),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_BATCH_DIR).mkdir(parents=True, exist_ok=True)
    for batch in batch_report["batches"]:
        (repo_root / batch["path"]).write_text(
            gold_review_batch_markdown(batch),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_BATCH_INDEX_MD).write_text(
        gold_review_batch_index_markdown(batch_report),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_DECISION_DIR).mkdir(parents=True, exist_ok=True)
    if not preserve_existing_decisions:
        for batch in decision_report["batches"]:
            write_jsonl(repo_root / batch["path"], batch["records"])
        (repo_root / GOLD_REVIEW_DECISION_INDEX_MD).write_text(
            gold_review_decision_index_markdown(decision_report),
            encoding="utf-8",
        )
    decision_progress = build_gold_review_decision_progress(
        repo_root,
        batch_report=batch_report,
    )
    session_plan = build_gold_review_session_plan(
        repo_root,
        workload_plan=workload_plan,
        decision_progress=decision_progress,
    )
    report = build_formal_experiment_readiness(
        repo_root,
        session_plan=session_plan,
        decision_progress=decision_progress,
        review_progress=progress_report,
    )
    score_report = build_formal_experiment_score_report(repo_root)
    write_json(repo_root / GOLD_REVIEW_SESSION_PLAN_JSON, session_plan)
    write_json(repo_root / READINESS_REPORT_JSON, report)
    write_json(repo_root / SCORING_REPORT_JSON, score_report)
    (repo_root / GOLD_REVIEW_SESSION_PLAN_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_SESSION_PLAN_MD).write_text(
        gold_review_session_plan_markdown(session_plan),
        encoding="utf-8",
    )
    write_json(repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON, decision_progress)
    (repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD).write_text(
        gold_review_decision_progress_markdown(decision_progress),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_PROGRESS_MD).write_text(
        gold_review_progress_markdown(progress_report),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD).write_text(
        gold_review_workload_plan_markdown(workload_plan),
        encoding="utf-8",
    )
    (repo_root / GOLD_SEMANTIC_GROUPS_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_SEMANTIC_GROUPS_MD).write_text(
        gold_semantic_groups_markdown(semantic_groups),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_PRIORITY_PACKET_DIR).mkdir(parents=True, exist_ok=True)
    for lane in priority_packets["lanes"]:
        (repo_root / lane["path"]).write_text(
            gold_review_priority_packet_markdown(lane),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD).write_text(
        gold_review_priority_packet_index_markdown(priority_packets),
        encoding="utf-8",
    )
    (repo_root / REJECTION_ADJUDICATION_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / REJECTION_ADJUDICATION_MD).write_text(
        rejection_adjudication_markdown(rejection_adjudication),
        encoding="utf-8",
    )
    (repo_root / READINESS_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / READINESS_REPORT_MD).write_text(markdown_report(report), encoding="utf-8")
    (repo_root / SCORING_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / SCORING_REPORT_MD).write_text(
        score_report_markdown(score_report),
        encoding="utf-8",
    )
    return {
        "prepared_inputs": prepared,
        "gold_review_worklist_json": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLIST_JSON,
            repo_root,
        ),
        "gold_review_worklist_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLIST_MD,
            repo_root,
        ),
        "gold_validation_report_json": project_relative_path(
            repo_root / GOLD_VALIDATION_REPORT_JSON,
            repo_root,
        ),
        "gold_validation_report_markdown": project_relative_path(
            repo_root / GOLD_VALIDATION_REPORT_MD,
            repo_root,
        ),
        "gold_freeze_status_json": project_relative_path(
            repo_root / GOLD_FREEZE_REPORT_JSON,
            repo_root,
        ),
        "gold_freeze_status_markdown": project_relative_path(
            repo_root / GOLD_FREEZE_REPORT_MD,
            repo_root,
        ),
        "prediction_output_validation_report_json": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON,
            repo_root,
        ),
        "prediction_output_validation_report_markdown": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD,
            repo_root,
        ),
        "candidate_review_jsonl": project_relative_path(
            repo_root / GOLD_CANDIDATE_REVIEW_JSONL,
            repo_root,
        ),
        "candidate_review_markdown": project_relative_path(
            repo_root / GOLD_CANDIDATE_REVIEW_MD,
            repo_root,
        ),
        "gold_review_batch_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_BATCH_INDEX_MD,
            repo_root,
        ),
        "gold_review_decision_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_INDEX_MD,
            repo_root,
        ),
        "gold_review_decision_progress_json": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON,
            repo_root,
        ),
        "gold_review_decision_progress_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD,
            repo_root,
        ),
        "gold_review_decision_templates_written": not preserve_existing_decisions,
        "gold_review_progress_json": project_relative_path(
            repo_root / GOLD_REVIEW_PROGRESS_JSON,
            repo_root,
        ),
        "gold_review_progress_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PROGRESS_MD,
            repo_root,
        ),
        "gold_review_workload_plan_json": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_JSON,
            repo_root,
        ),
        "gold_review_workload_plan_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD,
            repo_root,
        ),
        "gold_semantic_groups_json": project_relative_path(
            repo_root / GOLD_SEMANTIC_GROUPS_JSON,
            repo_root,
        ),
        "gold_semantic_groups_markdown": project_relative_path(
            repo_root / GOLD_SEMANTIC_GROUPS_MD,
            repo_root,
        ),
        "gold_review_session_plan_json": project_relative_path(
            repo_root / GOLD_REVIEW_SESSION_PLAN_JSON,
            repo_root,
        ),
        "gold_review_session_plan_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_SESSION_PLAN_MD,
            repo_root,
        ),
        "gold_review_priority_packet_json": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON,
            repo_root,
        ),
        "gold_review_priority_packet_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
            repo_root,
        ),
        "rejection_adjudication_json": project_relative_path(
            repo_root / REJECTION_ADJUDICATION_JSON,
            repo_root,
        ),
        "rejection_adjudication_markdown": project_relative_path(
            repo_root / REJECTION_ADJUDICATION_MD,
            repo_root,
        ),
        "report_json": project_relative_path(repo_root / READINESS_REPORT_JSON, repo_root),
        "report_markdown": project_relative_path(repo_root / READINESS_REPORT_MD, repo_root),
        "scoring_report_json": project_relative_path(repo_root / SCORING_REPORT_JSON, repo_root),
        "scoring_report_markdown": project_relative_path(repo_root / SCORING_REPORT_MD, repo_root),
        "gold_validation_status": gold_validation["status"],
        "prediction_output_validation_status": prediction_validation["status"],
        "status": report["status"],
        "scoring_status": score_report["status"],
        "missing_required_inputs": report["missing_required_inputs"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare NASA ATMONTO formal experiment inputs and readiness report."
    )
    parser.add_argument("--repo-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument(
        "--skip-prepare-inputs",
        action="store_true",
        help="Only rebuild the readiness report; do not regenerate input and prompt batches.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_formal_experiment_readiness(
        args.repo_root,
        prepare_inputs=not args.skip_prepare_inputs,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"NASA ATMONTO formal experiment readiness failed: {exc}", file=sys.stderr)
        raise
