from __future__ import annotations

import json
from typing import Any

from aviation_agentic_ai.ontology.atmonto_experiment import term_name
from aviation_agentic_ai.utils.json_extraction import (
    JSONPayloadExtractionError,
    extract_json_object,
)


def build_repair_planner_messages(
    *,
    record: dict[str, Any],
    accepted_facts: list[dict[str, Any]],
    validator_rejections: list[dict[str, Any]],
    critic_quarantine: list[dict[str, Any]],
    missing_predicates: list[str],
    blocked_keys: list[str],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are the Repair planner agent for a bounded ATCSCC extraction loop. "
                "Return strict JSON only. Emit repair_targets and blocked_keys. "
                "Repair targets are instructions for the next extractor pass, never facts."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "source_id": record.get("source_id"),
                    "source_text": record.get("source_text"),
                    "accepted_predicates": sorted(
                        {term_name(fact.get("predicate")) for fact in accepted_facts}
                    ),
                    "missing_predicates": missing_predicates,
                    "validator_rejections": validator_rejections,
                    "critic_quarantine": critic_quarantine,
                    "blocked_keys": blocked_keys,
                    "required_output": {
                        "repair_targets": [
                            {
                                "predicate": "examplePredicate",
                                "reason": "why another extraction pass is needed",
                                "instruction": "what evidence to look for",
                            }
                        ],
                        "blocked_keys": blocked_keys,
                    },
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        },
    ]


def parse_repair_plan(raw_response: str) -> dict[str, Any]:
    parse_ok = True
    try:
        payload = extract_json_object(raw_response)
    except JSONPayloadExtractionError:
        parse_ok = False
        payload = {}
    targets = payload.get("repair_targets", [])
    blocked = payload.get("blocked_keys", [])
    if not isinstance(targets, list):
        targets = []
    if not isinstance(blocked, list):
        blocked = []
    return {
        "repair_targets": [target for target in targets if isinstance(target, dict)],
        "blocked_keys": [str(item) for item in blocked if item],
        "parse_ok": parse_ok,
    }


def deterministic_repair_targets(
    *,
    validator_rejections: list[dict[str, Any]],
    critic_quarantine: list[dict[str, Any]],
    missing_predicates: list[str],
) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    seen: set[str] = set()
    for predicate in missing_predicates:
        key = term_name(predicate)
        if key in seen:
            continue
        seen.add(key)
        targets.append(
            {
                "predicate": key,
                "reason": "required CQ predicate missing from accepted facts",
                "instruction": f"Look for copied evidence supporting {key}.",
            }
        )
    for item in validator_rejections + critic_quarantine:
        predicate = term_name(item.get("predicate"))
        if not predicate or predicate in seen:
            continue
        seen.add(predicate)
        targets.append(
            {
                "predicate": predicate,
                "reason": "previous candidate was rejected or quarantined",
                "instruction": f"Re-extract {predicate} only if a new copied evidence span supports it.",
            }
        )
    return targets
