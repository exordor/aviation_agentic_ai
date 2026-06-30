"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any, Callable
from pathlib import Path
from datetime import datetime, timezone
import json
from hashlib import sha1
import sys

from aviation_agentic_ai.utils.json_extraction import (
    JSONPayloadExtractionError,
    extract_json_object,
)
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.llm.providers import configured_llm_model, configured_llm_provider, get_llm
from aviation_agentic_ai.ontology.atmonto_minimal_loop import (
    validate_candidate_payloads,
)

from ._io import (
    append_jsonl_record,
    read_json,
    read_json_lenient,
    read_jsonl,
    read_jsonl_lenient,
    term_name,
    write_json,
    write_jsonl,
)
from ._system_defs import (
    FORMAL_INPUT_RECORDS_PATH,
    FORMAL_OUTPUT_DIR,
    SCHEMA_SLICE_PATH,
    SystemDefinition,
    llm_run_output_dir,
    system_by_id,
    system_output_stem,
)
LLMInvoker = Callable[[list[dict[str, str]]], str]

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
            object_payload = normalized.pop("object", None)
            raw_value = object_payload if object_payload is not None else normalized.get("value")
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
    from ._scoring import prediction_payloads_for_validation
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
