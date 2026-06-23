from __future__ import annotations

import json
from collections import Counter
from typing import Any

from aviation_agentic_ai.agents.end_to_end_agent import ATCSCCEndToEndAgent
from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run_agents import (
    predicate_route_map,
)


SOURCE_TEXT = (
    "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS "
    "EFFECTIVE TIME: 151918-160030 USERS CAN EXPECT ARRIVAL DELAYS "
    "DUE TO WEATHER. IMPACTING CONDITION WEATHER. CTL ELEMENT ZLA."
)


class FakeAgentInvoker:
    def __init__(self, responses_by_role: dict[str, list[dict[str, Any]]]) -> None:
        self.responses_by_role = responses_by_role
        self.counts: Counter[str] = Counter()

    def __call__(self, messages: list[dict[str, str]]) -> str:
        system = messages[0]["content"]
        role = (
            "extractor"
            if "Extractor agent" in system
            else "critic"
            if "Critic agent" in system
            else "repair_planner"
            if "Repair planner" in system
            else "refiner"
            if "Refiner agent" in system
            else None
        )
        assert role is not None, system
        self.counts[role] += 1
        if role == "refiner" and role not in self.responses_by_role:
            payload = json.loads(messages[-1]["content"])
            return json.dumps(payload["required_output"])
        return json.dumps(self.responses_by_role[role][self.counts[role] - 1])


def _record() -> dict[str, Any]:
    return {
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-15:063",
        "source_family": "atcscc_advisories",
        "candidate_subject_class": "TrafficManagementInitiative",
        "source_text": SOURCE_TEXT,
    }


def _schema_slice() -> dict[str, Any]:
    return {
        "classes": [
            {
                "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#TrafficManagementInitiative",
                "prefixed_name": "atm:TrafficManagementInitiative",
                "local_name": "TrafficManagementInitiative",
            },
            {
                "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#TFMcontrolElement",
                "prefixed_name": "atm:TFMcontrolElement",
                "local_name": "TFMcontrolElement",
            },
        ],
        "object_properties": [
            {
                "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement",
                "prefixed_name": "atm:controlledNASelement",
                "local_name": "controlledNASelement",
                "domain_set": ["TrafficManagementInitiative"],
                "range_set": ["TFMcontrolElement"],
            }
        ],
        "datatype_properties": [
            {
                "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#advisoryNumber",
                "prefixed_name": "atm:advisoryNumber",
                "local_name": "advisoryNumber",
                "domain_set": ["TrafficManagementInitiative"],
                "datatype_set": ["xsd:integer"],
            },
            {
                "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#impactingCondition",
                "prefixed_name": "atm:impactingCondition",
                "local_name": "impactingCondition",
                "domain_set": ["TrafficManagementInitiative"],
                "datatype_set": ["xsd:string"],
            },
        ],
        "class_hierarchy": [],
        "class_property_constraints": [],
    }


def _route_map() -> dict[str, dict[str, set[str]]]:
    return predicate_route_map(
        {
            "cqs": [
                {
                    "cq_id": "QT-Q01-AFFECTED-NAS-ELEMENTS",
                    "route_label": "graph",
                    "graph_use_decision": "use_for_answer_set",
                    "required_predicates": ["controlledNASelement"],
                },
                {
                    "cq_id": "QT-Q01-CAUSE-CONDITION",
                    "route_label": "graph",
                    "graph_use_decision": "use_for_answer_set",
                    "required_predicates": ["impactingCondition"],
                },
            ]
        }
    )


def _payload(*facts: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": "2026-05-15:063",
        "source_family": "atcscc_advisories",
        "facts": list(facts),
    }


def _condition_fact() -> dict[str, Any]:
    return {
        "fact_id": "f-condition",
        "fact_type": "datatype_property",
        "subject": "urn:test:tmi:063",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "impactingCondition",
        "datatype": "xsd:string",
        "value": "WEATHER",
        "evidence_text": "IMPACTING CONDITION WEATHER",
    }


def _nas_fact() -> dict[str, Any]:
    return {
        "fact_id": "f-zla",
        "fact_type": "object_property",
        "subject": "urn:test:tmi:063",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "controlledNASelement",
        "object": "urn:aviation-agentic-ai:nas-element:ZLA",
        "object_label": "ZLA",
        "object_class": "TFMcontrolElement",
        "evidence_text": "CTL ELEMENT ZLA",
    }


def test_end_to_end_agent_answers_from_l1_graph_facts_with_citations() -> None:
    invoker = FakeAgentInvoker(
        {
            "extractor": [_payload(_condition_fact(), _nas_fact())],
            "critic": [{"drop_fact_ids": [], "concerns": [], "global_notes": []}],
            "repair_planner": [{"repair_targets": [], "blocked_keys": []}],
        }
    )
    agent = ATCSCCEndToEndAgent(schema_slice=_schema_slice(), route_map=_route_map())

    result = agent.process(
        _record(),
        question="What caused this ATCSCC advisory?",
        invoker=invoker,
        invoker_label="test_invoker",
    )

    assert result.abstain is False
    assert result.answer_values == ["WEATHER"]
    assert result.citations == [
        {
            "source_id": "2026-05-15:063",
            "fact_id": "f-condition",
            "evidence_text": "IMPACTING CONDITION WEATHER",
        }
    ]
    assert result.trace.extraction.iterations_used == 1
    assert [step["role"] for step in result.trace.l2_steps] == [
        "boundary_gate",
        "router",
        "retriever",
        "answerer",
        "self_eval",
    ]
    assert result.trace.l2_steps[1]["output_summary"]["template_id"] == "QT-Q01-CAUSE-CONDITION"


def test_end_to_end_agent_abstains_before_retrieval_for_live_operational_question() -> None:
    invoker = FakeAgentInvoker(
        {
            "extractor": [_payload(_condition_fact(), _nas_fact())],
            "critic": [{"drop_fact_ids": [], "concerns": [], "global_notes": []}],
            "repair_planner": [{"repair_targets": [], "blocked_keys": []}],
        }
    )
    agent = ATCSCCEndToEndAgent(schema_slice=_schema_slice(), route_map=_route_map())

    result = agent.process(
        _record(),
        question="Should I reroute aircraft around ZLA right now?",
        invoker=invoker,
        invoker_label="test_invoker",
    )

    assert result.abstain is True
    assert result.answer_values == []
    assert "live operational" in result.rationale
    assert invoker.counts == Counter()
    assert [step["role"] for step in result.trace.l2_steps] == ["boundary_gate"]
