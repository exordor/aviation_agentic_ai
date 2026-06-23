from __future__ import annotations

import json
from collections import Counter
from typing import Any

from aviation_agentic_ai.agents.extraction_agent import ExtractionAgent
from aviation_agentic_ai.agents.types import evidence_span_hash
from aviation_agentic_ai.ontology.atmonto_experiment import term_name
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
        self.calls: list[dict[str, Any]] = []
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
        self.calls.append({"role": role, "messages": messages})
        self.counts[role] += 1
        if role == "refiner" and role not in self.responses_by_role:
            payload = json.loads(messages[-1]["content"])
            return json.dumps(payload["required_output"])
        responses = self.responses_by_role[role]
        response = responses[self.counts[role] - 1]
        return json.dumps(response)


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
                    "cq_id": "CQ-D01",
                    "route_label": "deterministic",
                    "graph_use_decision": "avoid_by_default",
                    "required_predicates": ["advisoryNumber"],
                },
                {
                    "cq_id": "CQ-D02",
                    "route_label": "graph",
                    "graph_use_decision": "use_for_answer_set",
                    "required_predicates": ["controlledNASelement", "impactingCondition"],
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


def _number_fact(fact_id: str = "f-number", evidence: str = "ATCSCC ADVZY 063") -> dict[str, Any]:
    return {
        "fact_id": fact_id,
        "fact_type": "datatype_property",
        "subject": "urn:test:tmi:063",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "advisoryNumber",
        "datatype": "xsd:integer",
        "value": 63,
        "evidence_text": evidence,
    }


def _condition_fact(
    fact_id: str = "f-condition",
    evidence: str = "IMPACTING CONDITION WEATHER",
) -> dict[str, Any]:
    return {
        "fact_id": fact_id,
        "fact_type": "datatype_property",
        "subject": "urn:test:tmi:063",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "impactingCondition",
        "datatype": "xsd:string",
        "value": "WEATHER",
        "evidence_text": evidence,
    }


def _nas_fact(
    fact_id: str = "f-zla",
    label: str = "ZLA",
    evidence: str = "CTL ELEMENT ZLA",
) -> dict[str, Any]:
    return {
        "fact_id": fact_id,
        "fact_type": "object_property",
        "subject": "urn:test:tmi:063",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "controlledNASelement",
        "object": f"urn:aviation-agentic-ai:nas-element:{label}",
        "object_label": label,
        "object_class": "TFMcontrolElement",
        "evidence_text": evidence,
    }


def _run_agent(fake: FakeAgentInvoker, max_iterations: int = 2):
    return ExtractionAgent(
        schema_slice=_schema_slice(),
        route_map=_route_map(),
        max_iterations=max_iterations,
    ).run(_record(), invoker=fake, invoker_label="test_invoker")


def test_repair_adds_missing_field() -> None:
    fake = FakeAgentInvoker(
        {
            "extractor": [_payload(_number_fact()), _payload(_condition_fact())],
            "critic": [
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
            ],
            "repair_planner": [
                {
                    "repair_targets": [
                        {
                            "predicate": "impactingCondition",
                            "reason": "required CQ predicate missing",
                            "instruction": "Extract weather cause from the advisory text.",
                        }
                    ],
                    "blocked_keys": [],
                },
                {"repair_targets": [], "blocked_keys": []},
            ],
        }
    )

    result = _run_agent(fake)

    assert {term_name(fact["predicate"]) for fact in result.facts} == {
        "advisoryNumber",
        "impactingCondition",
    }
    assert result.trace.iterations_used == 2
    assert fake.counts["extractor"] == 2
    assert result.metadata["live_llm_run"] is False
    second_extractor_prompt = fake.calls[3]["messages"][-1]["content"]
    assert "impactingCondition" in second_extractor_prompt
    assert "blocked_keys" in second_extractor_prompt


def test_repair_does_not_drop_prior_accepted() -> None:
    fake = FakeAgentInvoker(
        {
            "extractor": [_payload(_number_fact()), _payload(_condition_fact())],
            "critic": [
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
            ],
            "repair_planner": [
                {"repair_targets": [{"predicate": "impactingCondition"}], "blocked_keys": []},
                {"repair_targets": [], "blocked_keys": []},
            ],
            "refiner": [_payload(_condition_fact())],
        }
    )

    result = _run_agent(fake)

    by_predicate = {term_name(fact["predicate"]): fact for fact in result.facts}
    assert by_predicate["advisoryNumber"]["value"] == 63
    assert by_predicate["impactingCondition"]["value"] == "WEATHER"
    assert {fact["agentic_system_id"] for fact in result.facts} == {"L1_agentic_extraction"}


def test_rejected_fact_not_re_admitted_with_same_evidence() -> None:
    bad_users = _nas_fact("f-users-1", label="USERS", evidence="USERS CAN EXPECT ARRIVAL DELAYS")
    good_zla = _nas_fact("f-zla-2", label="ZLA", evidence="CTL ELEMENT ZLA")
    fake = FakeAgentInvoker(
        {
            "extractor": [
                _payload(bad_users),
                _payload(_nas_fact("f-users-2", label="USERS", evidence=bad_users["evidence_text"])),
                _payload(good_zla),
            ],
            "critic": [
                {"drop_fact_ids": ["f-users-1"], "concerns": [], "global_notes": []},
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
            ],
            "repair_planner": [
                {"repair_targets": [{"predicate": "controlledNASelement"}], "blocked_keys": []},
                {"repair_targets": [{"predicate": "controlledNASelement"}], "blocked_keys": []},
                {"repair_targets": [], "blocked_keys": []},
            ],
        }
    )

    result = _run_agent(fake, max_iterations=3)

    assert [fact.get("object_label") for fact in result.facts] == ["ZLA"]
    assert result.trace.blocked_repeat_count == 1
    assert result.trace.accepted_evidence_hashes["controlledNASelement"] == evidence_span_hash(
        "CTL ELEMENT ZLA"
    )
    assert result.trace.blocked_evidence_hashes["controlledNASelement"] != evidence_span_hash(
        "CTL ELEMENT ZLA"
    )


def test_accepted_not_silently_overwritten() -> None:
    fake = FakeAgentInvoker(
        {
            "extractor": [
                _payload(_number_fact("f-number-1")),
                _payload(_number_fact("f-number-2", evidence="NOT IN SOURCE")),
            ],
            "critic": [
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
            ],
            "repair_planner": [
                {"repair_targets": [{"predicate": "impactingCondition"}], "blocked_keys": []},
                {"repair_targets": [], "blocked_keys": []},
            ],
        }
    )

    result = _run_agent(fake)

    assert len(result.facts) == 1
    assert result.facts[0]["fact_id"] == "f-number-1"
    assert result.facts[0]["evidence_text"] == "ATCSCC ADVZY 063"
    assert any(
        event["event"] == "validator_rejected" and event["predicate"] == "advisoryNumber"
        for event in result.trace.events
    )


def test_accepted_and_blocked_disjoint_after_regrounding() -> None:
    bad_number = _number_fact("f-number-bad", evidence="SAN AIRPORT ARRIVAL DELAYS")
    good_number = _number_fact("f-number-good", evidence="ATCSCC ADVZY 063")
    fake = FakeAgentInvoker(
        {
            "extractor": [
                _payload(bad_number),
                _payload(good_number),
                _payload(_condition_fact()),
            ],
            "critic": [
                {"drop_fact_ids": ["f-number-bad"], "concerns": [], "global_notes": []},
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
            ],
            "repair_planner": [
                {"repair_targets": [{"predicate": "advisoryNumber"}], "blocked_keys": []},
                {"repair_targets": [{"predicate": "impactingCondition"}], "blocked_keys": []},
                {"repair_targets": [], "blocked_keys": []},
            ],
        }
    )

    result = _run_agent(fake, max_iterations=3)

    assert {term_name(fact["predicate"]) for fact in result.facts} == {
        "advisoryNumber",
        "impactingCondition",
    }
    assert result.trace.accepted_identity_keys.isdisjoint(result.trace.blocked_identity_keys)
    third_extractor_prompt = [call for call in fake.calls if call["role"] == "extractor"][2][
        "messages"
    ][-1]["content"]
    assert "advisoryNumber" not in third_extractor_prompt.split("blocked_keys: ")[-1]


def test_evidence_hash_reproducible() -> None:
    assert evidence_span_hash("  CTL   ELEMENT ZLA ") == evidence_span_hash("CTL ELEMENT ZLA")
    assert len(evidence_span_hash("CTL ELEMENT ZLA")) == 64


def test_unsupported_stays_quarantined() -> None:
    fake = FakeAgentInvoker(
        {
            "extractor": [_payload(_nas_fact("f-bad", label="USERS", evidence="NOT IN SOURCE"))],
            "critic": [{"drop_fact_ids": [], "concerns": [], "global_notes": []}],
            "repair_planner": [{"repair_targets": [], "blocked_keys": []}],
        }
    )

    result = _run_agent(fake, max_iterations=1)

    assert result.facts == []
    assert result.blocked
    assert any(
            "evidence_not_contained_after_normalization" in event.get("reasons", [])
            or "rejected_evidence" in event.get("reasons", [])
            or "evidence_not_found_in_source" in event.get("reasons", [])
            for event in result.trace.events
        )


def test_budget_exhausted_recorded() -> None:
    fake = FakeAgentInvoker(
        {
            "extractor": [_payload(_number_fact()), _payload()],
            "critic": [
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
                {"drop_fact_ids": [], "concerns": [], "global_notes": []},
            ],
            "repair_planner": [
                {"repair_targets": [{"predicate": "impactingCondition"}], "blocked_keys": []},
                {"repair_targets": [{"predicate": "impactingCondition"}], "blocked_keys": []},
            ],
        }
    )

    result = _run_agent(fake, max_iterations=2)

    assert result.trace.budget_exhausted is True
    assert result.trace.iterations_used == 2
    assert [term_name(fact["predicate"]) for fact in result.facts] == ["advisoryNumber"]
