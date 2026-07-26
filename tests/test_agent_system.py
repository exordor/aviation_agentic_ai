"""Acceptance tests for the multi-Agent KG system (design §20.1).

Covers: tool boundaries; Advisory Agent does not canonicalize; unique authority
paths make no model call; unresolved candidates abstain; every EvidenceClaim
carries source_id+evidence_text; Facility/Terminology fan out and join; Graph
Patch uses the active Schema Guide vocabulary; invalid domain/range ->
schema_violation; real unsupported fields -> profile_gap; profile gaps never
enter RDF/Neo4j; run manifest records schema_slice_id+checksum; no custom cs:*
core predicates; re-ingest idempotency; no missing relationship endpoints;
Query Agent sees graph-tool results not raw sources; missing evidence ->
"Insufficient graph evidence."; no chain-of-thought/credentials stored.

Regression coverage added for the §16/§17/§20 core-correctness fixes: frozen
prompt catalog is the sole prompt source; runtime assembles the fixed 6-message
sequence and records a per-call ledger; no default GDP fallback (missing event
type -> abstain, no graph); Ground Stop is not answered as a Ground Delay
Program; every Neo4j relationship endpoint is a node; PROFILE_GAPS NONE/header
rows parse correctly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system import graph_patch, prompts
from aviation_agentic_ai.agent_system.agents import (
    FacilityCandidates,
    TermCandidates,
    parse_structured_fields,
    run_advisory_agent,
    run_facility_agent,
    run_terminology_agent,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    AgentTask,
    ModelCallRecord,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.materialize import materialize_graph_patch
from aviation_agentic_ai.agent_system.query import answer_question, ontology_labels_for
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.workflow import build_ingest_graph


@pytest.fixture(scope="module")
def guide():
    return load_schema_guide()


@pytest.fixture(scope="module")
def catalog():
    return prompts.load_prompt_catalog()


# ---------------------------------------------------------------------------
# §16: Frozen prompt catalog (sole prompt source)
# ---------------------------------------------------------------------------


def test_catalog_is_frozen_with_all_five_roles(catalog):
    assert catalog.status == "frozen"
    assert catalog.prompt_set_id == "multi-agent-aviation-kg-system-prompts-v3"
    for role in ("advisory", "facility", "terminology", "knowledge_graph_construction", "query"):
        assert role in catalog.roles
        assert catalog.roles[role].prompt_version


def test_catalog_has_no_parallel_hardcoded_prompts():
    """Runtime must not carry hardcoded prompts parallel to the catalog."""

    for forbidden in (
        "ADVISORY_AGENT_PROMPT",
        "FACILITY_AGENT_PROMPT",
        "TERMINOLOGY_AGENT_PROMPT",
        "KG_CONSTRUCTION_AGENT_PROMPT",
        "QUERY_AGENT_PROMPT",
    ):
        assert not hasattr(prompts, forbidden), f"parallel hardcoded prompt {forbidden!r} present"


def test_assembled_prompt_is_fixed_six_message_order(catalog):
    assembled = prompts.assemble_prompt("advisory", {"source_id": "x", "source_text": "t"})
    roles = [role for role, _ in assembled.messages]
    assert roles == ["system", "user", "assistant", "user", "assistant", "user"]
    assert assembled.prompt_set_id == catalog.prompt_set_id
    assert assembled.prompt_version == catalog.roles["advisory"].prompt_version


def test_catalog_prompt_no_chain_of_thought_or_credentials(catalog):
    forbidden = ("chain-of-thought", "api key", "secret")
    for role in catalog.roles.values():
        blob = f"{role.system}\n{role.user_template}\n"
        for pair in role.few_shot:
            blob += f"{pair[0]}\n{pair[1]}\n"
        low = blob.lower()
        for token in forbidden:
            assert token not in low, f"role {role.role!r} contains {token!r}"


# ---------------------------------------------------------------------------
# §20.1: Schema Guide
# ---------------------------------------------------------------------------


def test_schema_guide_loads_active_slice_with_checksum(guide):
    assert guide.schema_slice_id == "nasa_atmonto_atcscc_tmi_slice"
    assert len(guide.checksum) == 64


def test_gdp_maps_to_ground_delay_program_tmi(guide):
    assert guide.event_class_for_term("GDP") == "atm:GroundDelayProgramTMI"


def test_gs_maps_to_ground_stop_tmi(guide):
    assert guide.event_class_for_term("GS") == "atm:GroundStopTMI"


def test_controlled_nas_element_domain_range(guide):
    assert guide.object_property_domain_ok("atm:controlledNASelement", "atm:GroundDelayProgramTMI")
    assert guide.object_property_range_ok("atm:controlledNASelement", "nas:Airport")


def test_time_props_are_xsd_dateTime(guide):
    assert guide.datatype_property_ok("atm:effectiveStartTime", "atm:GroundStopTMI")
    assert "xsd:dateTime" in guide.datatype_for("atm:effectiveStartTime")
    assert "xsd:dateTime" in guide.datatype_for("atm:effectiveEndTime")


# ---------------------------------------------------------------------------
# §20.1: Graph Patch parsing (§11.5) — including NONE / header rows
# ---------------------------------------------------------------------------


def test_graph_patch_parser_handles_sections_and_ignores(tmp_path):
    raw = """\
# comment
```text
GRAPH_PATCH
evt:1 | rdf:type | atm:GroundDelayProgramTMI | src:1
evt:1 | atm:controlledNASelement | urn:facility:KSFO | src:1

PROFILE_GAPS
unused | value | evidence | reason
```
"""
    block = graph_patch.parse_graph_patch_block(raw)
    assert len(block.patch_lines) == 2
    assert len(block.profile_gaps) == 1
    assert block.patch_lines[0].predicate == "rdf:type"
    assert block.patch_lines[0].source_ids == ["src:1"]


def test_profile_gaps_none_marker_is_not_a_gap():
    raw = """\
GRAPH_PATCH
evt:1 | rdf:type | atm:GroundDelayProgramTMI | src:1

PROFILE_GAPS
NONE
"""
    block = graph_patch.parse_graph_patch_block(raw)
    assert block.profile_gaps == []


def test_profile_gaps_header_row_is_not_a_gap():
    raw = """\
GRAPH_PATCH
evt:1 | rdf:type | atm:GroundDelayProgramTMI | src:1

PROFILE_GAPS
field | value | evidence | reason
real_field | real_value | real_evidence | not in profile
"""
    block = graph_patch.parse_graph_patch_block(raw)
    assert len(block.profile_gaps) == 1
    assert block.profile_gaps[0].field == "real_field"


def test_graph_patch_normalizes_rdf_typed_literal_objects():
    """§11.5 tolerant parser: RDF typed-literal/quoted objects normalize to bare literals."""

    raw = (
        "GRAPH_PATCH\n"
        'evt:1 | atm:advisoryNumber | "123"^^xsd:integer | src:1\n'
        'evt:1 | atm:effectiveStartTime | "2026-05-19T21:00:00Z"^^xsd:dateTime | src:1\n'
    )
    block = graph_patch.parse_graph_patch_block(raw)
    assert [line.object for line in block.patch_lines] == ["123", "2026-05-19T21:00:00Z"]


# ---------------------------------------------------------------------------
# §20.1: Materialization / schema validator (§13)
# ---------------------------------------------------------------------------


def _event_uri(source_id: str, event_class: str) -> str:
    from aviation_agentic_ai.agent_system.materialize import _event_uri as _eu

    return _eu(source_id, event_class)


def test_valid_gdp_patch_materializes(guide, tmp_path):
    evt = _event_uri("src:1", "atm:GroundDelayProgramTMI")
    raw = f"""\
GRAPH_PATCH
{evt} | rdf:type | atm:GroundDelayProgramTMI | src:1
{evt} | atm:controlledNASelement | urn:facility:KSFO | src:1
{evt} | atm:effectiveStartTime | 2026-05-14T00:00:00Z | src:1
"""
    mat = materialize_graph_patch(
        graph_patch_raw=raw,
        advisory_source_id="src:1",
        event_class="atm:GroundDelayProgramTMI",
        guide=guide,
        canonical_entities={"urn:facility:KSFO": "nas:Airport"},
        known_source_ids={"src:1"},
        output_dir=tmp_path,
    )
    assert mat.valid_count == 3
    assert mat.schema_violation_count == 0
    assert mat.schema_slice_id == guide.schema_slice_id
    assert Path(mat.jsonl_path).exists()
    assert Path(mat.ttl_path).exists()


def test_invalid_domain_range_is_schema_violation(guide, tmp_path):
    evt = _event_uri("src:1", "atm:GroundDelayProgramTMI")
    raw = f"""\
GRAPH_PATCH
{evt} | rdf:type | atm:GroundDelayProgramTMI | src:1
{evt} | atm:controlledNASelement | urn:facility:WRONG | src:1
"""
    mat = materialize_graph_patch(
        graph_patch_raw=raw,
        advisory_source_id="src:1",
        event_class="atm:GroundDelayProgramTMI",
        guide=guide,
        canonical_entities={"urn:facility:WRONG": "atm:AirportSpec"},
        known_source_ids={"src:1"},
        output_dir=tmp_path,
    )
    assert any(o.outcome == "schema_violation" for o in mat.line_outcomes)
    assert mat.valid_count == 1


def test_bad_datatype_value_is_schema_violation(guide, tmp_path):
    evt = _event_uri("src:1", "atm:GroundStopTMI")
    raw = f"""\
GRAPH_PATCH
{evt} | rdf:type | atm:GroundStopTMI | src:1
{evt} | atm:effectiveStartTime | not-a-timestamp | src:1
"""
    mat = materialize_graph_patch(
        graph_patch_raw=raw,
        advisory_source_id="src:1",
        event_class="atm:GroundStopTMI",
        guide=guide,
        known_source_ids={"src:1"},
        output_dir=tmp_path,
    )
    assert any(
        o.outcome == "schema_violation" and "xsd:dateTime" in o.reason for o in mat.line_outcomes
    )
    assert mat.valid_count == 1


def test_profile_gap_never_enters_rdf_or_neo4j(guide, tmp_path):
    evt = _event_uri("src:1", "atm:GroundDelayProgramTMI")
    raw = f"""\
GRAPH_PATCH
{evt} | rdf:type | atm:GroundDelayProgramTMI | src:1
{evt} | custom:unsupportedProperty | value | src:1

PROFILE_GAPS
some_field | some_value | some_evidence | not in profile
"""
    mat = materialize_graph_patch(
        graph_patch_raw=raw,
        advisory_source_id="src:1",
        event_class="atm:GroundDelayProgramTMI",
        guide=guide,
        known_source_ids={"src:1"},
        output_dir=tmp_path,
    )
    assert mat.profile_gap_count == 1
    assert mat.valid_count == 1
    triples_text = Path(mat.jsonl_path).read_text(encoding="utf-8")
    assert "custom:unsupportedProperty" not in triples_text


def test_no_custom_core_predicates_in_formal_graph(guide, tmp_path):
    evt = _event_uri("src:1", "atm:GroundDelayProgramTMI")
    raw = f"""\
GRAPH_PATCH
{evt} | rdf:type | atm:GroundDelayProgramTMI | src:1
{evt} | cs:eventType | GDP | src:1
{evt} | cs:affectsFacility | urn:facility:KSFO | src:1
"""
    mat = materialize_graph_patch(
        graph_patch_raw=raw,
        advisory_source_id="src:1",
        event_class="atm:GroundDelayProgramTMI",
        guide=guide,
        known_source_ids={"src:1"},
        output_dir=tmp_path,
    )
    triples_text = Path(mat.jsonl_path).read_text(encoding="utf-8")
    for forbidden in ("cs:eventType", "cs:affectsFacility", "cs:usesMeasure", "cs:effectiveStart", "cs:effectiveEnd"):
        assert forbidden not in triples_text


def test_reingest_produces_same_event_id_and_no_duplicates(guide, tmp_path):
    evt = _event_uri("src:1", "atm:GroundStopTMI")
    raw = f"""\
GRAPH_PATCH
{evt} | rdf:type | atm:GroundStopTMI | src:1
{evt} | atm:controlledNASelement | urn:facility:KSFO | src:1
"""
    mat1 = materialize_graph_patch(
        graph_patch_raw=raw, advisory_source_id="src:1", event_class="atm:GroundStopTMI",
        guide=guide, canonical_entities={"urn:facility:KSFO": "nas:Airport"},
        known_source_ids={"src:1"}, output_dir=tmp_path / "run1",
    )
    mat2 = materialize_graph_patch(
        graph_patch_raw=raw, advisory_source_id="src:1", event_class="atm:GroundStopTMI",
        guide=guide, canonical_entities={"urn:facility:KSFO": "nas:Airport"},
        known_source_ids={"src:1"}, output_dir=tmp_path / "run2",
    )
    ids1 = sorted(t.triple_id for t in mat1.triples)
    ids2 = sorted(t.triple_id for t in mat2.triples)
    assert ids1 == ids2
    node_files = list(Path(mat1.nodes_path).read_text(encoding="utf-8").splitlines())
    node_ids = [json.loads(n)["entity_id"] for n in node_files if n.strip()]
    assert len(node_ids) == len(set(node_ids))


def test_every_neo4j_relationship_endpoint_is_a_node(guide, tmp_path):
    """§20.1: no materialized relationship has a missing endpoint.

    This is the strengthened check: the object-side canonical facility (e.g.
    the controlled airport) MUST be promoted to a node, not just appear in a
    relationship row.
    """

    evt = _event_uri("src:1", "atm:GroundStopTMI")
    facility = "urn:facility:KSFO"
    raw = f"""\
GRAPH_PATCH
{evt} | rdf:type | atm:GroundStopTMI | src:1
{evt} | atm:controlledNASelement | {facility} | src:1
{evt} | prov:wasDerivedFrom | src:1 | src:1
"""
    mat = materialize_graph_patch(
        graph_patch_raw=raw, advisory_source_id="src:1", event_class="atm:GroundStopTMI",
        guide=guide, canonical_entities={facility: "nas:Airport"},
        known_source_ids={"src:1"}, output_dir=tmp_path,
    )
    nodes = [json.loads(n) for n in Path(mat.nodes_path).read_text(encoding="utf-8").splitlines() if n.strip()]
    rels = [json.loads(r) for r in Path(mat.relationships_path).read_text(encoding="utf-8").splitlines() if r.strip()]
    node_ids = {n["entity_id"] for n in nodes}
    for rel in rels:
        assert rel["from"] in node_ids, f"endpoint {rel['from']} missing as node"
        assert rel["to"] in node_ids, f"endpoint {rel['to']} missing as node"
    # The controlled facility and the source record must both be nodes.
    assert facility in node_ids
    assert "src:1" in node_ids


# ---------------------------------------------------------------------------
# §20.1: Agent tool boundaries + lifecycle (§§8-10)
# ---------------------------------------------------------------------------


def _advisory_record() -> SourceRecord:
    return SourceRecord(
        source_id="2026-05-14:002",
        family=SourceFamily.ATCSCC_ADVISORY,
        content=(
            "ATCSCC ADVZY 002 DCA/ZDC 05/14/2026 CDM GROUND STOP\n"
            "MESSAGE:\nCTL ELEMENT: DCA ELEMENT TYPE: APT\n"
            "GROUND STOP PERIOD: 13/2307Z - 14/0130Z\n"
        ),
    )


def test_advisory_agent_does_not_canonicalize():
    task = AgentTask(
        run_id="r", source_id="2026-05-14:002", objective="extract mentions",
        allowed_tools=["get_advisory", "parse_structured_fields", "get_schema_event_classes"],
    )
    mentions = parse_structured_fields(_advisory_record().content)
    result = run_advisory_agent(
        task=task, advisory=_advisory_record(), event_classes=["atm:GroundStopTMI"],
        mentions=mentions,
    )
    fac_claim = next(c for c in result.evidence_card.claims if c.field_name == "controlled_facility")
    assert fac_claim.value == "DCA"  # raw mention, not canonicalized
    assert fac_claim.canonical_ref is None


def test_every_claim_carries_source_id_and_evidence_text():
    task = AgentTask(
        run_id="r", source_id="2026-05-14:002", objective="extract mentions",
        allowed_tools=["get_advisory", "parse_structured_fields", "get_schema_event_classes"],
    )
    mentions = parse_structured_fields(_advisory_record().content)
    result = run_advisory_agent(
        task=task, advisory=_advisory_record(), event_classes=["atm:GroundStopTMI"],
        mentions=mentions,
    )
    for claim in result.evidence_card.claims:
        assert claim.source_id
        assert claim.evidence_text


def test_unique_facility_authority_makes_no_model_call():
    @dataclass
    class FakeEntity:
        entity_id: str
        preferred_label: str
        entity_type: type  # noqa

    from enum import Enum

    class EType(Enum):
        AIRPORT = "airport"

    entity = FakeEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KDCA",
        preferred_label="RONALD REAGAN WASHINGTON NTL",
        entity_type=EType.AIRPORT,
    )
    task = AgentTask(
        run_id="r", source_id="src", objective="resolve facility",
        allowed_tools=["lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias"],
    )
    called = []

    def invoker(agent_role, template_vars):
        called.append((agent_role, template_vars))
        return ModelCallRecord(agent=agent_role, raw_response="", prompt_version="facility-agent-v2")

    result = run_facility_agent(
        task=task,
        candidates=FacilityCandidates(
            mention="DCA", candidates=[entity], source_id="src",
            advisory_evidence="CTL ELEMENT: DCA",
        ),
        model_invoker=invoker,
    )
    assert called == []
    assert result.status == AgentStatus.RESOLVED
    assert result.evidence_card.canonical_refs == [entity.entity_id]
    # §11.4: the facility claim carries the exact advisory span, not a synthetic
    # string such as "unique authority candidate ...".
    claim = result.evidence_card.claims[0]
    assert claim.evidence_text == "CTL ELEMENT: DCA"


def test_facility_agent_abstains_without_exact_advisory_evidence():
    """§11.4: no exact advisory span -> abstain (no synthetic evidence)."""

    @dataclass
    class FakeEntity:
        entity_id: str
        preferred_label: str

    task = AgentTask(
        run_id="r", source_id="src", objective="resolve facility",
        allowed_tools=["lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias"],
    )
    result = run_facility_agent(
        task=task,
        candidates=FacilityCandidates(
            mention="DCA",
            candidates=[FakeEntity("urn:facility:KDCA", "KDCA")],
            source_id="src",
            advisory_evidence="",  # no exact span supplied
        ),
        model_invoker=None,
    )
    assert result.status == AgentStatus.ABSTAIN
    assert result.evidence_card.claims == []


def test_unresolved_facility_candidates_abstain():
    @dataclass
    class FakeEntity:
        entity_id: str
        preferred_label: str

    task = AgentTask(
        run_id="r", source_id="src", objective="resolve facility",
        allowed_tools=["lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias"],
    )
    cands = FacilityCandidates(
        mention="X",
        candidates=[FakeEntity("a", "A"), FakeEntity("b", "B")],
        source_id="src",
    )
    result = run_facility_agent(task=task, candidates=cands, model_invoker=None)
    assert result.status == AgentStatus.ABSTAIN


def test_term_with_no_schema_mapping_is_profile_gap(guide):
    @dataclass
    class FakeTerm:
        term_id: str
        preferred_label: str
        abbreviation: str
        term_category: type  # noqa

    from enum import Enum

    class Cat(Enum):
        OPERATIONAL_PROCEDURE = "operational_procedure"

    term = FakeTerm("urn:term:operational_procedure:LDA", "Landing Distance Available", "LDA", Cat.OPERATIONAL_PROCEDURE)
    task = AgentTask(
        run_id="r", source_id="src", objective="resolve term",
        allowed_tools=["lookup_faa_glossary", "lookup_pcg_term", "resolve_term_registry", "resolve_schema_event_class"],
    )
    result = run_terminology_agent(
        task=task,
        candidates=TermCandidates(mention="LDA", candidates=[term], source_id="src", guide=guide),
        model_invoker=None,
    )
    assert result.status == AgentStatus.PROFILE_GAP


def test_agent_tool_boundary_enforced():
    from aviation_agentic_ai.agent_system.agents import ToolNotAllowedError, _check_tool

    task = AgentTask(
        run_id="r", source_id="src", objective="x",
        allowed_tools=["only_this_tool"],
    )
    with pytest.raises(ToolNotAllowedError):
        _check_tool(task, "forbidden_tool")


# ---------------------------------------------------------------------------
# §20.1: Workflow topology (fan-out + join) + no default GDP fallback
# ---------------------------------------------------------------------------


def test_ingest_graph_compiles():
    graph = build_ingest_graph()
    assert graph is not None


def test_missing_event_type_abstains_and_constructs_no_graph(guide, tmp_path):
    """§11.6: missing resolved event type -> abstain, no formal patch.

    Drives the KG Construction Agent directly with an empty event class and
    asserts no model call is made and no graph patch is produced.
    """

    from aviation_agentic_ai.agent_system.agents import (
        KGConstructionInput,
        run_kg_construction_agent,
    )
    from aviation_agentic_ai.agent_system.contracts import EvidenceCard

    called = []

    def invoker(agent_role, template_vars):
        called.append((agent_role, template_vars))
        return ModelCallRecord(agent=agent_role, raw_response="GRAPH_PATCH\n")

    task = AgentTask(
        run_id="r", source_id="src:1", objective="construct patch",
        allowed_tools=["get_schema_context", "resolve_canonical_ref", "get_source_evidence"],
    )
    inputs = KGConstructionInput(
        advisory=SourceRecord(source_id="src:1", family=SourceFamily.ATCSCC_ADVISORY, content="x"),
        advisory_card=EvidenceCard(agent_role="advisory", status=AgentStatus.RESOLVED),
        facility_card=EvidenceCard(agent_role="facility", status=AgentStatus.ABSTAIN),
        terminology_card=EvidenceCard(agent_role="terminology", status=AgentStatus.ABSTAIN),
        event_uri="evt:placeholder",
        event_class="",  # unresolved
        guide=guide,
    )
    result = run_kg_construction_agent(task=task, inputs=inputs, model_invoker=invoker)
    assert called == []  # no model call when event type unresolved
    assert result.status == AgentStatus.ABSTAIN
    assert result.graph_patch is None


# ---------------------------------------------------------------------------
# §16/§17: Runtime prompt wiring + per-call ledger
# ---------------------------------------------------------------------------


def test_runtime_invoker_assembles_catalog_and_records_ledger(monkeypatch):
    """The live invoker assembles the frozen 6-message prompt and records the
    per-call ledger (agent, prompt_set_id, prompt_version, attempt)."""

    captured = {}

    class FakeChat:
        def invoke(self, messages):
            captured["messages"] = messages
            captured["message_count"] = len(messages)
            captured["roles"] = [m.type for m in messages]

            class _Usage:
                input_tokens = 10
                output_tokens = 5
                reasoning_tokens = 0

            class _Result:
                content = "ANSWER\nx"
                usage_metadata = {
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "reasoning_tokens": 0,
                }
                response_metadata = {
                    "model_name": "deepseek-v4-pro",
                    "system_fingerprint": "fp_test",
                    "finish_reason": "stop",
                }

            return _Result()

    monkeypatch.setattr(
        "aviation_agentic_ai.llm.providers.get_deepseek_mve_llm",
        lambda **_: FakeChat(),
    )

    from aviation_agentic_ai.agent_system.runtime import make_live_model_invoker

    invoker = make_live_model_invoker()
    rec = invoker(
        "query",
        {
            "user_question": "what event",
            "ontology_labels": "atm:GroundStopTMI=Ground Stop (GS)",
            "graph_evidence": "evt:1 rdf:type atm:GroundStopTMI [src:1]",
        },
    )
    assert captured["message_count"] == 6
    assert captured["roles"] == ["system", "human", "ai", "human", "ai", "human"]
    assert rec.agent == "query"
    assert rec.prompt_set_id == "multi-agent-aviation-kg-system-prompts-v3"
    assert rec.prompt_version == "query-agent-v3"
    assert rec.attempt == 1
    assert rec.input_tokens == 10 and rec.output_tokens == 5
    assert rec.system_fingerprint == "fp_test"


def test_runtime_invoker_records_per_role_attempt_and_failures(monkeypatch):
    """The ledger increments attempts per role and records failed attempts."""

    class FailingChat:
        def __init__(self):
            self.calls = 0

        def invoke(self, messages):
            self.calls += 1
            raise RuntimeError("provider down")

    chat = FailingChat()
    monkeypatch.setattr(
        "aviation_agentic_ai.llm.providers.get_deepseek_mve_llm",
        lambda **_: chat,
    )

    from aviation_agentic_ai.agent_system.runtime import make_live_model_invoker

    invoker = make_live_model_invoker()
    rec1 = invoker("query", {"user_question": "q1", "ontology_labels": "", "graph_evidence": "x"})
    rec2 = invoker("query", {"user_question": "q2", "ontology_labels": "", "graph_evidence": "y"})
    assert rec1.attempt == 1 and rec2.attempt == 2  # per-role attempt counter
    assert rec1.error and rec2.error  # both attempts recorded, no silent retry


# ---------------------------------------------------------------------------
# §20.1: Query Agent (§12)
# ---------------------------------------------------------------------------


def test_missing_graph_evidence_answers_insufficient(tmp_path):
    (tmp_path / "kg.jsonl").write_text("", encoding="utf-8")
    called = []

    def invoker(agent_role, template_vars):
        called.append(1)
        return ModelCallRecord(agent="query", raw_response="")

    status, answer, sources, rec, facts = answer_question(
        run_dir=tmp_path, question="what is the event", model_invoker=invoker
    )
    assert called == []
    assert status == "insufficient"
    assert answer == "Insufficient graph evidence."
    assert sources == []
    assert rec.error  # fail-closed: the no-call record carries an error reason


def test_query_agent_lists_source_ids(tmp_path):
    triple = {
        "subject": "evt:1", "predicate": "rdf:type",
        "object": "atm:GroundDelayProgramTMI", "source_document": "src:1",
    }
    (tmp_path / "kg.jsonl").write_text(json.dumps(triple), encoding="utf-8")

    def invoker(agent_role, template_vars):
        return ModelCallRecord(
            agent="query",
            raw_response="It is a Ground Delay Program.\nSOURCES\n- src:1",
        )

    # §6.3: the question must match a graph fact keyword (no whole-graph
    # fallback). "delay" matches the GroundDelayProgramTMI object.
    status, answer, sources, rec, facts = answer_question(
        run_dir=tmp_path, question="delay program", model_invoker=invoker
    )
    assert "src:1" in sources
    assert facts


def test_query_agent_uses_graph_not_raw_source(tmp_path):
    triple = {
        "subject": "evt:1", "predicate": "atm:controlledNASelement",
        "object": "urn:facility:KSFO", "source_document": "src:1",
    }
    (tmp_path / "kg.jsonl").write_text(json.dumps(triple), encoding="utf-8")

    def invoker(agent_role, template_vars):
        rendered = template_vars.get("graph_evidence", "")
        assert "ATCSCC ADVZY" not in rendered
        assert "controlledNASelement" in rendered or "KSFO" in rendered
        return ModelCallRecord(agent="query", raw_response="affected KSFO\nSOURCES\n- src:1")

    # §6.3: "airport" matches the controlled-facility fact via KSFO/facility.
    status, answer, sources, rec, facts = answer_question(
        run_dir=tmp_path, question="KSFO airport", model_invoker=invoker
    )
    assert "src:1" in sources


def test_query_agent_pins_ground_stop_label_from_ontology(guide, tmp_path):
    """§12: the Query Agent receives controlled ontology labels so a Ground
    Stop event is not rendered as a Ground Delay Program."""

    gs_triple = {
        "subject": "evt:1", "predicate": "rdf:type",
        "object": "atm:GroundStopTMI", "subject_class": "atm:GroundStopTMI",
        "object_class": "atm:GroundStopTMI", "source_document": "src:1",
    }
    (tmp_path / "kg.jsonl").write_text(json.dumps(gs_triple), encoding="utf-8")
    labels_seen = {}

    def invoker(agent_role, template_vars):
        labels_seen["labels"] = template_vars.get("ontology_labels", "")
        return ModelCallRecord(
            agent="query",
            raw_response="The graph records a Ground Stop.\nSOURCES\n- src:1",
        )

    status, answer, sources, rec, facts = answer_question(
        run_dir=tmp_path, question="ground stop event", model_invoker=invoker, guide=guide
    )
    # Controlled ontology label for GroundStopTMI is surfaced to the Agent.
    assert "Ground Stop" in labels_seen["labels"]
    # And the answer never turns a Ground Stop into a Ground Delay Program.
    assert "Ground Delay Program" not in answer


def test_ontology_labels_include_event_and_property_labels(guide, tmp_path):
    triples = [
        {
            "subject": "evt:1", "predicate": "rdf:type", "object": "atm:GroundStopTMI",
            "subject_class": "atm:GroundStopTMI", "object_class": "atm:GroundStopTMI",
            "source_document": "src:1",
        },
        {
            "subject": "evt:1", "predicate": "atm:controlledNASelement",
            "object": "urn:facility:KSFO", "subject_class": "atm:GroundStopTMI",
            "object_class": "nas:Airport", "source_document": "src:1",
        },
    ]
    (tmp_path / "kg.jsonl").write_text("\n".join(json.dumps(t) for t in triples), encoding="utf-8")
    labels = ontology_labels_for(
        [json.loads(t) for t in (tmp_path / "kg.jsonl").read_text(encoding="utf-8").splitlines()],
        guide,
    )
    assert labels["atm:GroundStopTMI"] == "Ground Stop (GS)"
    assert labels["nas:Airport"] == "Airport"
    assert "atm:controlledNASelement" in labels
