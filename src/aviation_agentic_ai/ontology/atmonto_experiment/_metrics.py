"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from collections import Counter
from collections.abc import Iterable
from random import Random

from ._fact_keys import (
    FactKey,
    canonical_fact_key,
    fact_with_source_id,
)
from ._system_defs import (
    REVIEWED_GOLD_STATUS,
    SEMANTIC_BOOTSTRAP_ITERATIONS,
    SEMANTIC_BOOTSTRAP_SEED,
)

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
    prediction_keys: set[tuple[str, ...]],
    gold_keys: set[tuple[str, ...]],
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

def _semantic_metric_block(
    *,
    prediction_keys: set[tuple[str, ...]],
    gold_keys: set[tuple[str, ...]],
) -> dict[str, Any]:
    true_positive = prediction_keys & gold_keys
    values = semantic_metric_values(
        predicted_count=len(prediction_keys),
        gold_count=len(gold_keys),
        true_positive_count=len(true_positive),
    )
    return {
        "predicted_fact_count": len(prediction_keys),
        "gold_fact_count": len(gold_keys),
        "true_positive_count": len(true_positive),
        "false_positive_count": len(prediction_keys - gold_keys),
        "false_negative_count": len(gold_keys - prediction_keys),
        **values,
        "confidence_intervals": semantic_bootstrap_confidence_intervals(
            prediction_keys=prediction_keys,
            gold_keys=gold_keys,
        ),
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
            "evidence_tolerant": None,
        }
    prediction_keys = {canonical_fact_key(fact) for fact in predictions}
    # Evidence-tolerant keys drop the evidence_text span (the 7th key element),
    # so facts that agree on everything except their quoted evidence match.
    tolerant_prediction_keys = {key[:6] for key in prediction_keys}
    tolerant_gold_keys = {key[:6] for key in gold_keys}
    return {
        "available": True,
        **_semantic_metric_block(prediction_keys=prediction_keys, gold_keys=gold_keys),
        "evidence_tolerant": _semantic_metric_block(
            prediction_keys=tolerant_prediction_keys,
            gold_keys=tolerant_gold_keys,
        ),
    }
