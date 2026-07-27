from __future__ import annotations

import re
from pathlib import Path
from string import Template

import yaml


PROMPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "prompts"
    / "decision_case_agents_v1.yaml"
)

EXPECTED_ROLES = {
    "query",
    "semantic_resolution",
    "decision_case_assembly",
}

EXPECTED_PLACEHOLDERS = {
    "query": {
        "user_question",
        "ontology_labels",
        "graph_scope",
        "allowed_predicates",
    },
    "semantic_resolution": {
        "task_id",
        "mention",
        "structural_slot",
        "expected_entity_type",
        "eligible_candidate_ids",
        "authority_source_ids",
        "schema_slice_id",
    },
    "decision_case_assembly": {
        "case_id",
        "required_case_slots",
        "optional_case_slots",
        "missing_slots",
        "schema_profile_id",
        "available_evidence_layer_ids",
        "selected_evidence_claim_ids",
        "resolution_proposal_ids",
        "context_association_ids",
        "public_observation_ids",
    },
}


def _catalog() -> dict:
    return yaml.safe_load(PROMPT_PATH.read_text(encoding="utf-8"))


def _placeholders(text: str) -> set[str]:
    return set(re.findall(r"\$\{([a-z_]+)\}", text))


def test_prompt_catalog_contains_only_activated_model_roles() -> None:
    catalog = _catalog()
    assert catalog["status"] == "frozen"
    assert catalog["prompt_set_id"] == "aviation-decision-case-agents-v1"
    assert set(catalog["roles"]) == EXPECTED_ROLES


def test_every_role_has_version_policy_and_bounded_output() -> None:
    expected_versions = {
        "query": "query-agent-v4",
        "semantic_resolution": "semantic-resolution-agent-v1",
        "decision_case_assembly": "decision-case-assembly-v1",
    }
    for role, prompt in _catalog()["roles"].items():
        assert prompt["prompt_version"] == expected_versions[role]
        assert prompt["invocation_policy"]
        assert 1 <= prompt["max_output_tokens"] <= 512
        assert prompt["system"].strip()
        assert prompt["user_template"].strip()
        assert role.replace("_", " ") in prompt["system"].lower()


def test_every_role_has_two_fictional_contrastive_few_shot_pairs() -> None:
    expected_headers = {
        "query": {"ANSWER", "Insufficient graph evidence."},
        "semantic_resolution": {"{"},
        "decision_case_assembly": {"GRAPH_PATCH"},
    }
    forbidden_real_tokens = re.compile(r"\b(?:DCA|SFO|MIA|CLT|GDP|GS)\b")
    for role, prompt in _catalog()["roles"].items():
        assert len(prompt["few_shot"]) == 2
        for example in prompt["few_shot"]:
            assert set(example) == {"user", "assistant"}
            combined = f"{example['user']}\n{example['assistant']}"
            assert "example:" in combined or role == "query"
            assert "urn:aviation-agentic-ai:" not in combined
            assert not forbidden_real_tokens.search(combined)
            assert any(example["assistant"].startswith(header) for header in expected_headers[role])

    roles = _catalog()["roles"]
    assert roles["query"]["few_shot"][1]["assistant"].strip() == "Insufficient graph evidence."


def test_templates_expose_only_the_declared_placeholders() -> None:
    for role, prompt in _catalog()["roles"].items():
        assert _placeholders(prompt["user_template"]) == EXPECTED_PLACEHOLDERS[role]


def test_templates_render_without_unresolved_variables() -> None:
    for role, prompt in _catalog()["roles"].items():
        values = {name: f"test-{name}" for name in EXPECTED_PLACEHOLDERS[role]}
        rendered = Template(prompt["user_template"]).substitute(values)
        assert "${" not in rendered
        for value in values.values():
            assert value in rendered


def test_prompts_do_not_request_provider_json_schema_or_hidden_reasoning() -> None:
    forbidden = {
        "response_format",
        "json schema response",
        "show your chain of thought",
        "reveal your reasoning",
        "api_key",
        "secret key",
    }
    for prompt in _catalog()["roles"].values():
        examples = "\n".join(
            f"{example['user']}\n{example['assistant']}" for example in prompt["few_shot"]
        )
        combined = f"{prompt['system']}\n{examples}\n{prompt['user_template']}".lower()
        normalized = " ".join(combined.split())
        for phrase in forbidden:
            assert phrase not in normalized
        assert "hidden reasoning" in normalized


def test_query_prompt_requires_native_tool_evidence_and_english_answer() -> None:
    system = _catalog()["roles"]["query"]["system"]
    normalized = " ".join(system.split())
    assert "Select and call a bound read-only graph tool before answering" in normalized
    assert "Do not answer before receiving a ToolMessage" in normalized
    assert "get_event_facts" in normalized
    assert "Do not use model memory, external knowledge, or raw advisory text" in normalized
    assert "Insufficient graph evidence." in normalized
    assert "SOURCES" in normalized
    assert "Always answer in English" in normalized


def test_semantic_resolution_prompt_requires_a_bounded_tool_then_strict_decision() -> None:
    role = _catalog()["roles"]["semantic_resolution"]
    system = " ".join(role["system"].split())
    assert role["invocation_policy"] == "multiple_eligible_candidates_only"
    assert role["max_output_tokens"] == 256
    assert "one batch of one to three" in system
    assert "After ToolMessages, return one JSON object and no tool call" in system
    assert "Do not invent source IDs" in system


def test_model_defaults_are_reproducibility_oriented() -> None:
    defaults = _catalog()["model_defaults"]
    assert defaults == {
        "temperature": 0,
        "thinking": "disabled",
        "max_retries": 0,
        "timeout_seconds": 120,
    }
