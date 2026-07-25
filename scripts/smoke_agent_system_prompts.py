#!/usr/bin/env python3
"""Bounded live smoke test for the frozen Agent-system prompts.

This is implementation QA, not a semantic benchmark. By default it performs
exactly five provider calls: Advisory, Facility, Terminology, Knowledge Graph
Construction, and Query. ``--roles`` permits a bounded targeted regression
after an observed prompt failure. It does not retry, resample, or print
credentials.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from string import Template
from typing import Any

import yaml
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from aviation_agentic_ai.llm.providers import get_llm


ROLE_ORDER = (
    "advisory",
    "facility",
    "terminology",
    "knowledge_graph_construction",
    "query",
)


def _load_prompts(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload.get("status") != "frozen":
        raise RuntimeError("Prompt catalog must be frozen before live smoke testing.")
    if tuple(payload["roles"]) != ROLE_ORDER:
        raise RuntimeError("Prompt role order or membership drifted.")
    return payload


def _advisory_text(path: Path, source_id: str) -> str:
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("source_id") == source_id:
                return str(row["text"])
    raise KeyError(f"source_id not found: {source_id}")


def _invoke(llm: Any, role: str, prompt: dict[str, Any], values: dict[str, str]) -> dict[str, Any]:
    user = Template(prompt["user_template"]).substitute(values)
    messages: list[Any] = [SystemMessage(content=prompt["system"])]
    for example in prompt.get("few_shot", []):
        messages.extend(
            [
                HumanMessage(content=example["user"]),
                AIMessage(content=example["assistant"]),
            ]
        )
    messages.append(HumanMessage(content=user))
    started = time.perf_counter()
    response = llm.invoke(messages)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    content = str(getattr(response, "content", response)).strip()
    return {
        "role": role,
        "prompt_version": prompt["prompt_version"],
        "response": content,
        "elapsed_ms": elapsed_ms,
        "response_metadata": dict(getattr(response, "response_metadata", {}) or {}),
        "usage_metadata": dict(getattr(response, "usage_metadata", {}) or {}),
    }


def _checks(outputs: dict[str, dict[str, Any]], facility_id: str, source_id: str) -> dict[str, list[str]]:
    failures: dict[str, list[str]] = {}

    def require(role: str, condition: bool, message: str) -> None:
        if not condition:
            failures.setdefault(role, []).append(message)

    if "advisory" in outputs:
        advisory = outputs["advisory"]["response"]
        require(
            "advisory",
            advisory.startswith("ADVISORY_EVIDENCE"),
            "missing contract header",
        )
        require(
            "advisory",
            f"SOURCE_ID: {source_id}" in advisory,
            "exact source ID line missing",
        )
        require("advisory", "DCA" in advisory, "facility mention DCA missing")
        require("advisory", "GROUND STOP" in advisory.upper(), "ground-stop mention missing")
        require("advisory", source_id in advisory, "source ID missing")

    if "facility" in outputs:
        facility = outputs["facility"]["response"]
        require(
            "facility",
            facility.startswith("FACILITY_DECISION"),
            "missing contract header",
        )
        require(
            "facility",
            "STATUS: resolved" in facility,
            "unique authority candidate not resolved",
        )
        require(
            "facility",
            facility_id in facility,
            "provided canonical facility ID not preserved",
        )

    if "terminology" in outputs:
        terminology = outputs["terminology"]["response"]
        require(
            "terminology",
            terminology.startswith("TERMINOLOGY_DECISION"),
            "missing contract header",
        )
        require(
            "terminology",
            "STATUS: resolved" in terminology,
            "unique term not resolved",
        )
        require(
            "terminology",
            "atm:GroundStopTMI" in terminology,
            "provided ontology class not preserved",
        )

    if "knowledge_graph_construction" in outputs:
        kg = outputs["knowledge_graph_construction"]["response"]
        require("knowledge_graph_construction", "GRAPH_PATCH" in kg, "missing graph section")
        require("knowledge_graph_construction", "PROFILE_GAPS" in kg, "missing gap section")
        require("knowledge_graph_construction", "atm:GroundStopTMI" in kg, "event class missing")
        require(
            "knowledge_graph_construction",
            "atm:controlledNASelement" in kg,
            "controlled element relation missing",
        )
        require("knowledge_graph_construction", facility_id in kg, "canonical facility missing")
        require("knowledge_graph_construction", "cs:" not in kg, "custom core predicate emitted")
        gap_body = kg.split("PROFILE_GAPS", maxsplit=1)[-1].strip()
        require(
            "knowledge_graph_construction",
            gap_body == "NONE",
            "spurious profile gap emitted for an already represented fact",
        )

    if "query" in outputs:
        query = outputs["query"]["response"]
        require("query", query.startswith("ANSWER"), "missing answer header")
        require("query", "SOURCES" in query, "missing sources section")
        require("query", source_id in query, "supporting source ID missing")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-config", type=Path, required=True)
    parser.add_argument("--advisory-jsonl", type=Path, required=True)
    parser.add_argument("--source-id", default="2026-05-14:002")
    parser.add_argument("--model", default="deepseek-v4-pro")
    parser.add_argument("--roles", default=",".join(ROLE_ORDER))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    os.environ["LLM_PROVIDER"] = "deepseek"
    os.environ["MODEL_NAME"] = args.model

    catalog = _load_prompts(args.prompt_config)
    prompts = catalog["roles"]
    selected_roles = tuple(role.strip() for role in args.roles.split(",") if role.strip())
    if not selected_roles or len(set(selected_roles)) != len(selected_roles):
        raise ValueError("--roles must contain one or more unique role names")
    unknown_roles = set(selected_roles).difference(ROLE_ORDER)
    if unknown_roles:
        raise ValueError(f"Unknown --roles: {sorted(unknown_roles)}")
    source_text = _advisory_text(args.advisory_jsonl, args.source_id)
    facility_id = "urn:aviation-agentic-ai:facility:airport:KDCA"
    event_uri = f"urn:aviation-agentic-ai:event:{args.source_id}"

    llm = get_llm(temperature=0, max_tokens=512, timeout=120)
    inputs = {
        "advisory": {
            "source_id": args.source_id,
            "schema_event_classes": (
                "atm:GroundStopTMI | Ground Stop TMI | traffic-management "
                "initiative that holds departures on the ground\n"
                "atm:GroundDelayProgramTMI | Ground Delay Program TMI | "
                "traffic-management initiative that manages arrival demand"
            ),
            "structured_fields": (
                "EFFECTIVE_START=2026-05-14T00:21:00Z\n"
                "EFFECTIVE_END=2026-05-14T02:30:00Z"
            ),
            "source_text": source_text,
        },
        "facility": {
            "source_id": args.source_id,
            "facility_mention": "DCA",
            "structural_slot": "CTL ELEMENT with ELEMENT TYPE: APT",
            "advisory_evidence": "CTL ELEMENT: DCA ELEMENT TYPE: APT",
            "authority_candidates": (
                f"{facility_id} | Ronald Reagan Washington National Airport | "
                "nas:Airport | FAA airport facility record | NASR snapshot"
            ),
        },
        "terminology": {
            "source_id": args.source_id,
            "term_mention": "GROUND STOP",
            "advisory_evidence": "CDM GROUND STOP",
            "authority_candidates": (
                "urn:aviation-agentic-ai:term:ground-stop | Ground Stop | "
                "atm:GroundStopTMI | traffic-management initiative that holds "
                "departures on the ground | FAA Pilot/Controller Glossary"
            ),
        },
        "knowledge_graph_construction": {
            "event_uri": event_uri,
            "allowed_source_ids": (
                f"{args.source_id}; nasr:KDCA; faa-term:ground-stop"
            ),
            "known_canonical_entities": f"{facility_id} -> nas:Airport",
            "schema_context": (
                "Class: atm:GroundStopTMI | Ground Stop TMI | "
                "traffic-management initiative that holds departures\n"
                "Object property: atm:controlledNASelement | controlled NAS "
                "element | domain atm:GroundStopTMI | range nas:Airport\n"
                "Datatype property: atm:advisoryNumber | advisory number\n"
                "Datatype property: atm:effectiveStartTime | effective start\n"
                "Datatype property: atm:effectiveEndTime | effective end\n"
                "Datatype property: atm:impactingCondition | impacting condition\n"
                "Trace property: prov:wasDerivedFrom | source provenance"
            ),
            "advisory_evidence_card": (
                f"source={args.source_id}\n"
                "event=GROUND STOP evidence='CDM GROUND STOP'\n"
                "facility=DCA evidence='CTL ELEMENT: DCA ELEMENT TYPE: APT'\n"
                "start=2026-05-14T00:21:00Z evidence='EFFECTIVE TIME: 140021-140230'\n"
                "end=2026-05-14T02:30:00Z evidence='EFFECTIVE TIME: 140021-140230'"
            ),
            "facility_evidence_card": (
                f"status=resolved canonical_id={facility_id} "
                "class=nas:Airport source=nasr:KDCA"
            ),
            "terminology_evidence_card": (
                "status=resolved term=Ground Stop class=atm:GroundStopTMI "
                "source=faa-term:ground-stop"
            ),
        },
        "query": {
            "user_question": (
                "这条通告实施了什么流量管理措施、影响哪个机场、有效时间是什么？"
            ),
            "ontology_labels": (
                "atm:GroundStopTMI=Ground Stop; "
                "atm:controlledNASelement=controlled NAS element; "
                "atm:effectiveStartTime=effective start; "
                "atm:effectiveEndTime=effective end"
            ),
            "graph_evidence": (
                f"{event_uri} rdf:type atm:GroundStopTMI [{args.source_id}]\n"
                f"{event_uri} atm:controlledNASelement {facility_id} "
                f"[{args.source_id},nasr:KDCA]\n"
                f"{event_uri} atm:effectiveStartTime 2026-05-14T00:21:00Z "
                f"[{args.source_id}]\n"
                f"{event_uri} atm:effectiveEndTime 2026-05-14T02:30:00Z "
                f"[{args.source_id}]"
            ),
        },
    }

    outputs: dict[str, dict[str, Any]] = {}
    for role in selected_roles:
        outputs[role] = _invoke(llm, role, prompts[role], inputs[role])

    failures = _checks(outputs, facility_id, args.source_id)
    artifact = {
        "prompt_set_id": catalog["prompt_set_id"],
        "provider": "deepseek",
        "requested_model": args.model,
        "source_id": args.source_id,
        "provider_calls": len(outputs),
        "passed": not failures,
        "failures": failures,
        "outputs": outputs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "prompt_set_id": artifact["prompt_set_id"],
                "provider_calls": artifact["provider_calls"],
                "passed": artifact["passed"],
                "failed_roles": sorted(failures),
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )
    return 0 if artifact["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
