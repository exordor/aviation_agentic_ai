from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path


GOLD_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json")
GOLD_TEMPLATE_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl")
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
FORMAL_INPUT_RECORDS_PATH = FORMAL_OUTPUT_DIR / "input_records.jsonl"
FORMAL_SYSTEM_SPECS_PATH = FORMAL_OUTPUT_DIR / "system_specs.json"
S1_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s1_llm_only_prompt_batch.jsonl"
S2_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s2_llm_schema_slice_prompt_batch.jsonl"
S3_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s3_llm_schema_slice_validator_repair_prompt_batch.jsonl"
READINESS_REPORT_JSON = Path("reports/stages/nasa_atmonto_formal_experiment_readiness.json")
READINESS_REPORT_MD = Path("reports/stages/nasa_atmonto_formal_experiment_readiness.md")


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
)


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
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    payload = "\n".join(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload + ("\n" if payload else ""), encoding="utf-8")


def compact_text(value: object) -> str:
    return " ".join(str(value or "").split())


def term_name(value: object) -> str:
    text = str(value or "")
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text and text.startswith(("http://", "https://", "urn:")):
        return text.rstrip("/").rsplit("/", 1)[-1]
    if ":" in text and not text.startswith(("http://", "https://", "urn:")):
        return text.rsplit(":", 1)[-1]
    return text


def canonical_fact_key(fact: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    value = fact.get("object") if fact.get("fact_type") == "object_property" else fact.get("value")
    return (
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
            "requires_llm": system.requires_llm,
            "uses_schema_slice": system.uses_schema_slice,
            "uses_validator_repair": system.uses_validator_repair,
        }
        for system in SYSTEMS
    ]


def gold_annotation_status(gold_records: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = Counter(
        str(record.get("gold_annotation", {}).get("annotation_status", "missing_status"))
        for record in gold_records
    )
    pending = sum(count for status, count in statuses.items() if status.startswith("pending"))
    reviewed = len(gold_records) - pending
    completed = pending == 0 and bool(gold_records)
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


def gold_fact_keys(gold_records: list[dict[str, Any]]) -> set[tuple[str, str, str, str, str, str]]:
    keys: set[tuple[str, str, str, str, str, str]] = set()
    for record in gold_records:
        for fact in record.get("gold_annotation", {}).get("valid_facts", []):
            if isinstance(fact, dict):
                keys.add(canonical_fact_key(fact))
        for fact in record.get("gold_annotation", {}).get("missing_facts", []):
            if isinstance(fact, dict):
                keys.add(canonical_fact_key(fact))
    return keys


def accepted_prediction_facts(
    validations: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for item in validations:
        if item.get("accepted") and isinstance(item.get("validated_fact"), dict):
            facts.append(item["validated_fact"])
    return facts


def structural_metrics(validations: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_count = len(validations)
    rejected = [item for item in validations if not item.get("accepted")]
    accepted = [item for item in validations if item.get("accepted")]
    repaired = [item for item in accepted if item.get("repairs")]
    initially_invalid = len(repaired) + len(rejected)
    return {
        "candidate_fact_count": candidate_count,
        "accepted_fact_count": len(accepted),
        "rejected_fact_count": len(rejected),
        "schema_violation_rate": (len(rejected) / candidate_count) if candidate_count else None,
        "repair_success_rate": (len(repaired) / initially_invalid) if initially_invalid else None,
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
        }
    prediction_keys = {canonical_fact_key(fact) for fact in predictions}
    true_positive = prediction_keys & gold_keys
    false_positive = prediction_keys - gold_keys
    false_negative = gold_keys - prediction_keys
    precision = len(true_positive) / len(prediction_keys) if prediction_keys else 0.0
    recall = len(true_positive) / len(gold_keys) if gold_keys else 0.0
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "available": True,
        "predicted_fact_count": len(prediction_keys),
        "gold_fact_count": len(gold_keys),
        "true_positive_count": len(true_positive),
        "false_positive_count": len(false_positive),
        "false_negative_count": len(false_negative),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "manual_semantic_correctness": precision,
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
    return (
        "Extract a compact knowledge-graph fact payload from one ATCSCC advisory. "
        "Return strict JSON only. Use descriptive class and predicate labels derived "
        "from the text. Do not use any external ontology term list or schema "
        "vocabulary. Every fact must quote evidence_text from the advisory."
    )


def schema_slice_system_prompt(schema_context: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Extract a compact knowledge-graph fact payload from one ATCSCC advisory.",
            "Return strict JSON only.",
            "Use only the provided NASA ATMONTO ATCSCC schema-slice classes and properties.",
            "Every fact must quote evidence_text from the advisory.",
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
        "systems": system_definitions(repo_root),
        "common_output_contract": extraction_output_contract(),
        "schema_context_summary": {
            "schema_slice_id": schema_context["schema_slice_id"],
            "class_count": len(schema_context["classes"]),
            "object_property_count": len(schema_context["object_properties"]),
            "datatype_property_count": len(schema_context["datatype_properties"]),
        },
        "execution_boundary": (
            "Prompt batches prepare model inputs only. LLM outputs are not fabricated; "
            "formal scoring waits for reviewed gold annotations and S1-S3 predictions."
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
            system=SYSTEMS[1],
            input_records=input_records,
            schema_context=schema_context,
        ),
        S2_PROMPT_BATCH_PATH: build_prompt_batch(
            system=SYSTEMS[2],
            input_records=input_records,
            schema_context=schema_context,
        ),
        S3_PROMPT_BATCH_PATH: build_prompt_batch(
            system=SYSTEMS[3],
            input_records=input_records,
            schema_context=schema_context,
        ),
    }

    write_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH, input_records)
    write_jsonl(repo_root / SYSTEMS[0].expected_output, s0_predictions)
    for path, records in prompt_batches.items():
        write_jsonl(repo_root / path, records)
    write_json(repo_root / FORMAL_SYSTEM_SPECS_PATH, build_system_specs(repo_root, schema_context))

    return {
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "input_record_count": len(input_records),
        "s0_predictions": project_relative_path(repo_root / SYSTEMS[0].expected_output, repo_root),
        "s0_prediction_record_count": len(s0_predictions),
        "prompt_batches": {
            path.as_posix(): len(records)
            for path, records in sorted(
                prompt_batches.items(),
                key=lambda item: item[0].as_posix(),
            )
        },
        "system_specs": project_relative_path(repo_root / FORMAL_SYSTEM_SPECS_PATH, repo_root),
    }


def build_formal_experiment_readiness(
    repo_root: str | Path = PROJECT_ROOT,
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

    s0_structural = structural_metrics(s0_validations)
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

    return {
        "source_family": "nasa_atmonto_formal_experiment_readiness",
        "status": "ready_for_manual_gold_and_llm_runs" if missing_inputs else "ready_for_scoring",
        "protocol": "docs/experiment_protocol.md",
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
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
            "manual gold annotations and S1-S3 outputs are present."
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
        "schema_violation_rate",
        "repair_success_rate",
    ):
        lines.append(f"- `{key}`: {s0.get(key)}")
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
    report = build_formal_experiment_readiness(repo_root)
    write_json(repo_root / READINESS_REPORT_JSON, report)
    (repo_root / READINESS_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / READINESS_REPORT_MD).write_text(markdown_report(report), encoding="utf-8")
    return {
        "prepared_inputs": prepared,
        "report_json": project_relative_path(repo_root / READINESS_REPORT_JSON, repo_root),
        "report_markdown": project_relative_path(repo_root / READINESS_REPORT_MD, repo_root),
        "status": report["status"],
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
