from __future__ import annotations

import re
from pathlib import Path
from string import Template

import yaml


PROMPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "prompts"
    / "agent_system_v1.yaml"
)

EXPECTED_ROLES = {
    "advisory",
    "facility",
    "terminology",
    "knowledge_graph_construction",
    "query",
}

EXPECTED_PLACEHOLDERS = {
    "advisory": {
        "source_id",
        "schema_event_classes",
        "structured_fields",
        "source_text",
    },
    "facility": {
        "source_id",
        "facility_mention",
        "structural_slot",
        "advisory_evidence",
        "authority_candidates",
    },
    "terminology": {
        "source_id",
        "term_mention",
        "advisory_evidence",
        "authority_candidates",
    },
    "knowledge_graph_construction": {
        "event_uri",
        "allowed_source_ids",
        "known_canonical_entities",
        "schema_context",
        "advisory_evidence_card",
        "facility_evidence_card",
        "terminology_evidence_card",
    },
    "query": {
        "user_question",
        "ontology_labels",
        "graph_evidence",
    },
}


def _catalog() -> dict:
    return yaml.safe_load(PROMPT_PATH.read_text(encoding="utf-8"))


def _placeholders(text: str) -> set[str]:
    return set(re.findall(r"\$\{([a-z_]+)\}", text))


def test_prompt_catalog_is_frozen_and_has_exact_roles() -> None:
    catalog = _catalog()
    assert catalog["status"] == "frozen"
    assert catalog["prompt_set_id"] == "multi-agent-aviation-kg-system-prompts-v3"
    assert set(catalog["roles"]) == EXPECTED_ROLES


def test_every_role_has_version_policy_and_bounded_output() -> None:
    expected_versions = {
        "advisory": "advisory-agent-v2",
        "facility": "facility-agent-v2",
        "terminology": "terminology-agent-v2",
        "knowledge_graph_construction": "knowledge-graph-construction-agent-v3",
        "query": "query-agent-v2",
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
        "advisory": {"ADVISORY_EVIDENCE"},
        "facility": {"FACILITY_DECISION"},
        "terminology": {"TERMINOLOGY_DECISION"},
        "knowledge_graph_construction": {"GRAPH_PATCH"},
        "query": {"ANSWER", "图中证据不足"},
    }
    forbidden_real_tokens = re.compile(r"\b(?:DCA|SFO|MIA|CLT|GDP|GS)\b")
    for role, prompt in _catalog()["roles"].items():
        assert len(prompt["few_shot"]) == 2
        for example in prompt["few_shot"]:
            assert set(example) == {"user", "assistant"}
            combined = f"{example['user']}\n{example['assistant']}"
            assert "example:" in combined
            assert "urn:aviation-agentic-ai:" not in combined
            assert not forbidden_real_tokens.search(combined)
            assert any(
                example["assistant"].startswith(header)
                for header in expected_headers[role]
            )

    roles = _catalog()["roles"]
    assert "STATUS: abstain" in roles["advisory"]["few_shot"][1]["assistant"]
    assert "STATUS: abstain" in roles["facility"]["few_shot"][1]["assistant"]
    assert "STATUS: abstain" in roles["terminology"]["few_shot"][1]["assistant"]
    assert "PROFILE_GAPS\nEXAMPLE PRIORITY" in (
        roles["knowledge_graph_construction"]["few_shot"][1]["assistant"]
    )
    assert roles["query"]["few_shot"][1]["assistant"].strip() == "图中证据不足"


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
            f"{example['user']}\n{example['assistant']}"
            for example in prompt["few_shot"]
        )
        combined = f"{prompt['system']}\n{examples}\n{prompt['user_template']}".lower()
        normalized = " ".join(combined.split())
        for phrase in forbidden:
            assert phrase not in normalized
        assert "hidden reasoning" in normalized


def test_advisory_prompt_preserves_role_boundary() -> None:
    system = _catalog()["roles"]["advisory"]["system"]
    assert "Do not resolve airport or ARTCC identities" in system
    assert "Do not expand or normalize operational terminology" in system
    assert "Copy evidence exactly" in system
    assert "FACILITY_MENTIONS:" in system
    assert "OPERATIONAL_TERM_MENTIONS:" in system
    assert "Copy SOURCE_ID character-for-character" in system


def test_facility_and_terminology_prompts_have_abstain_and_closed_candidates() -> None:
    roles = _catalog()["roles"]
    for role in ("facility", "terminology"):
        system = roles[role]["system"]
        assert "AUTHORITY_CANDIDATES" in system
        assert "abstain" in system
        assert "Never invent" in system or "Do not use model memory" in system
        assert "copy the complete" in system.lower()
        assert roles[role]["invocation_policy"] == "ambiguous_candidates_only"


def test_kg_prompt_uses_atmonto_graph_patch_contract() -> None:
    system = _catalog()["roles"]["knowledge_graph_construction"]["system"]
    assert "NASA ATMONTO-derived Schema Guide" in system
    assert "GRAPH_PATCH" in system
    assert "PROFILE_GAPS" in system
    assert "rdf:type" in system
    assert "prov:wasDerivedFrom" in system
    assert "cs:" not in system
    assert "Never create a new class, property, canonical ID, source ID, or fact" in system
    assert "PROFILE_GAPS is not a summary of unused mentions" in system


def test_query_prompt_is_graph_only_and_has_exact_insufficient_evidence_response() -> None:
    system = _catalog()["roles"]["query"]["system"]
    assert "using only GRAPH_EVIDENCE" in system
    assert "Do not use model memory, external knowledge, or the raw advisory" in system
    assert "图中证据不足" in system
    assert "SOURCES" in system


def test_model_defaults_are_reproducibility_oriented() -> None:
    defaults = _catalog()["model_defaults"]
    assert defaults == {
        "temperature": 0,
        "thinking": "disabled",
        "max_retries": 0,
        "timeout_seconds": 120,
    }
