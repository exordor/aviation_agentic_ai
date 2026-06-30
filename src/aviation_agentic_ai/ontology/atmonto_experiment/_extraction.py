"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from collections.abc import Iterable
from pathlib import Path
import json
import re
from hashlib import sha1

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.ontology.atmonto_minimal_loop import (
    classify_controlled_element,
    classify_tmi,
    nas_entity_iri,
    source_entity_iri,
    validate_candidate_payloads,
)

from ._io import (
    compact_text,
    read_json,
    read_jsonl,
    term_name,
    write_json,
    write_jsonl,
)
from ._fact_keys import (
    FactKey,
    canonical_fact_key,
)
from ._system_defs import (
    EXTRACTION_SCHEMA_PATH,
    FORMAL_INPUT_RECORDS_PATH,
    FORMAL_SMOKE_OUTPUT_DIR,
    FORMAL_SYSTEM_SPECS_PATH,
    GOLD_MANIFEST_PATH,
    GOLD_TEMPLATE_PATH,
    S0_CANDIDATES_PATH,
    S0_VALIDATED_PATH,
    S1_PROMPT_BATCH_PATH,
    S2_PROMPT_BATCH_PATH,
    S3_PROMPT_BATCH_PATH,
    SCHEMA_SLICE_PATH,
    SYSTEMS,
    SystemDefinition,
    system_by_id,
    system_definitions,
    system_run_metadata_path,
)
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

IMPACTING_CONDITION_CATEGORY_MAP: dict[str, str] = {
    "staffing": "staffing",
    "weather": "weather",
    "thunderstorm": "weather",
    "wind shear": "weather",
    "low ceilings": "weather",
    "visibility": "weather",
    "snow": "weather",
    "ice": "weather",
    "fog": "weather",
    "volume": "volume",
    "demand": "volume",
    "runway": "runway",
    "equipment": "equipment",
    "outage": "equipment",
    "navaid": "equipment",
}

def derive_impacting_condition_category(
    source_text: str,
    facts: list[dict[str, Any]],
) -> str | None:
    """Derive an impactingCondition enum value from the message text or source text.

    Checks the extracted impactingConditionMessage value first, then falls back
    to the advisory source text. Returns None when no condition category matches.
    """
    for fact in facts:
        if term_name(fact.get("predicate")) == "impactingConditionMessage":
            message = str(fact.get("value", "")).lower()
            for keyword, category in IMPACTING_CONDITION_CATEGORY_MAP.items():
                if keyword in message:
                    return category
    text = source_text.lower()
    marker = "impacting condition"
    marker_pos = text.find(marker)
    if marker_pos >= 0:
        window = text[marker_pos : marker_pos + 120]
        cut = window.find("comment")
        if cut > 0:
            window = window[:cut]
        window = window.splitlines()[0]
        for keyword, category in IMPACTING_CONDITION_CATEGORY_MAP.items():
            if keyword in window:
                return category
    return None

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

    # Deterministic impactingCondition derivation: categorize the condition
    # message/source text so S4 does not depend on S3 LLM for this enum field.
    # This is a backbone-level derivation that takes priority over S3 enrichment.
    # It only overrides S3 when the derived category disagrees with (or is absent
    # from) S3's accepted impactingCondition, so records S3 already categorizes
    # correctly keep their better subject/evidence alignment.
    derived_condition = derive_impacting_condition_category(source_text, facts)
    s0_has_impacting_condition = any(
        term_name(item.get("validated_fact", {}).get("predicate")) == "impactingCondition"
        for item in accepted_validation_items(s0_record or {})
    )
    s3_existing_condition: str | None = None
    for item in accepted_validation_items(s3_record or {}):
        fact = item.get("validated_fact", {})
        if term_name(fact.get("predicate")) == "impactingCondition":
            s3_existing_condition = str(fact.get("value", ""))
            break
    if (
        derived_condition is not None
        and not s0_has_impacting_condition
        and derived_condition != s3_existing_condition
        and "impactingCondition" not in existing_deterministic_predicates
    ):
        backbone_facts = accepted_validation_items(s0_record or {})
        backbone_subject = ""
        backbone_subject_class = ""
        backbone_evidence = ""
        for item in backbone_facts:
            fact = item.get("validated_fact", {})
            if term_name(fact.get("predicate")) == "impactingConditionMessage":
                backbone_subject = str(fact.get("subject", ""))
                backbone_subject_class = str(fact.get("subject_class", ""))
                backbone_evidence = str(fact.get("evidence_text", ""))
                break
        if not backbone_subject:
            for item in backbone_facts:
                fact = item.get("validated_fact", {})
                if fact.get("subject"):
                    backbone_subject = str(fact.get("subject", ""))
                    backbone_subject_class = str(fact.get("subject_class", ""))
                    break
        if not backbone_evidence:
            for fact in facts:
                if term_name(fact.get("predicate")) == "impactingConditionMessage":
                    backbone_evidence = str(fact.get("evidence_text", ""))
                    break
        if not backbone_evidence and source_text:
            lower = source_text.lower()
            marker_pos = lower.find("impacting condition")
            if marker_pos >= 0:
                window = source_text[marker_pos : marker_pos + 80]
                cut = window.lower().find("comment")
                if cut > 0:
                    window = window[:cut]
                window = window.splitlines()[0]
                backbone_evidence = window.strip()
        derived_fact = {
            "fact_id": f"S4_derived_impactingCondition:{source_id}",
            "fact_type": "datatype_property",
            "predicate": "https://data.nasa.gov/ontologies/atmonto/ATM#impactingCondition",
            "value": derived_condition,
            "datatype": "http://www.w3.org/2001/XMLSchema#string",
            "evidence_text": backbone_evidence or "IMPACTING CONDITION",
            "subject": backbone_subject,
            "subject_class": backbone_subject_class,
            "extraction_method": "deterministic_condition_categorization",
            "extractor": "S4_hybrid_backbone_enrichment",
            "hybrid_role": "deterministic_backbone_derived",
            "hybrid_source_system": "S0_rule_only",
            "source_id": source_id,
        }
        facts.append(derived_fact)
        accepted_keys.add(canonical_fact_key(derived_fact))
        existing_deterministic_predicates.add("impactingCondition")
        validator_results.append(
            {
                "fact_id": derived_fact["fact_id"],
                "accepted": True,
                "status": "hybrid_backbone_derived_accepted",
                "validated_fact": derived_fact,
                "hybrid_role": "deterministic_backbone_derived",
                "candidate": derived_fact,
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
        elif (
            predicate == "impactingCondition"
            and "impactingCondition" in existing_deterministic_predicates
        ):
            reason = "deterministic_backbone_derived_takes_priority"
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
    from ._llm_runtime import normalizer_version
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
