"""Contracts for the bounded tool-using KG Construction Agent."""

from __future__ import annotations

from langchain_core.messages import AIMessage, ToolMessage

from aviation_agentic_ai.agent_system.agents import (
    KGConstructionInput,
    run_kg_construction_agent,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    AgentTask,
    EvidenceCard,
    EvidenceClaim,
    ModelCallRecord,
    ModelToolCall,
    SourceFamily,
    SourceRecord,
    ToolTraceEntry,
)
from aviation_agentic_ai.agent_system.kg_tool_graph import run_kg_tool_agent
from aviation_agentic_ai.agent_system.kg_tools import (
    KGConstructionToolGateway,
    build_kg_construction_tools,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn

SOURCE_ID = "example:001"
EVENT_URI = "urn:example:event:001"
EVENT_CLASS = "atm:GroundStopTMI"
FACILITY_ID = "urn:example:facility:airport:KZZQ"


class _ScriptedToolModel:
    def __init__(self, turns: list[ToolModelTurn]) -> None:
        self.turns = list(turns)
        self.invocations: list[tuple[str, list]] = []

    def invoke(self, messages, *, phase):
        self.invocations.append((phase, list(messages)))
        return self.turns.pop(0)


def _selection_turn(calls: list[dict]) -> ToolModelTurn:
    message = AIMessage(content="", tool_calls=calls)
    return ToolModelTurn(
        message=message,
        record=ModelCallRecord(
            agent="knowledge_graph_construction",
            raw_response="",
            prompt_set_id="prompt:test",
            prompt_version="knowledge-graph-construction-agent-v4",
            tool_calls=[
                ModelToolCall(
                    call_id=str(call["id"]),
                    name=str(call["name"]),
                    arguments=dict(call["args"]),
                )
                for call in calls
            ],
        ),
    )


def _draft_turn(raw: str, *, tool_calls: list[dict] | None = None) -> ToolModelTurn:
    calls = list(tool_calls or [])
    return ToolModelTurn(
        message=AIMessage(content=raw, tool_calls=calls),
        record=ModelCallRecord(
            agent="knowledge_graph_construction",
            raw_response=raw,
            prompt_set_id="prompt:test",
            prompt_version="knowledge-graph-construction-agent-v4",
            tool_calls=[
                ModelToolCall(
                    call_id=str(call["id"]),
                    name=str(call["name"]),
                    arguments=dict(call["args"]),
                )
                for call in calls
            ],
        ),
    )


def _cards(*, facility_status: AgentStatus = AgentStatus.RESOLVED):
    advisory = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="event_type",
                value="GROUND STOP",
                evidence_text="GROUND STOP",
                source_id=SOURCE_ID,
            )
        ],
        source_ids=[SOURCE_ID],
    )
    facility_claims = []
    canonical_refs = []
    if facility_status == AgentStatus.RESOLVED:
        facility_claims = [
            EvidenceClaim(
                field_name="controlled_facility",
                value="ZZQ",
                ontology_target="nas:Airport",
                evidence_text="CTL ELEMENT: ZZQ",
                source_id=SOURCE_ID,
                canonical_ref=FACILITY_ID,
            )
        ]
        canonical_refs = [FACILITY_ID]
    facility = EvidenceCard(
        agent_role="facility",
        status=facility_status,
        claims=facility_claims,
        canonical_refs=canonical_refs,
        source_ids=[SOURCE_ID],
    )
    terminology = EvidenceCard(
        agent_role="terminology",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="operational_term",
                value="Ground Stop",
                ontology_target=EVENT_CLASS,
                evidence_text="GROUND STOP",
                source_id=SOURCE_ID,
            )
        ],
        source_ids=[SOURCE_ID],
    )
    return {
        "advisory": advisory,
        "facility": facility,
        "terminology": terminology,
    }


def _session(*, facility_status: AgentStatus = AgentStatus.RESOLVED):
    cards = _cards(facility_status=facility_status)
    canonical = (
        {FACILITY_ID: "nas:Airport"}
        if facility_status == AgentStatus.RESOLVED
        else {}
    )
    gateway = KGConstructionToolGateway(
        guide=load_schema_guide(),
        event_class=EVENT_CLASS,
        evidence_cards=cards,
        canonical_entities=canonical,
        allowed_source_ids={SOURCE_ID},
    )
    return cards, canonical, build_kg_construction_tools(gateway)


def _required_calls(*, include_canonical: bool = True) -> list[dict]:
    calls = [
        {
            "id": "call:schema",
            "name": "get_schema_context",
            "args": {"event_class": EVENT_CLASS},
            "type": "tool_call",
        },
        {
            "id": "call:evidence",
            "name": "get_source_evidence",
            "args": {
                "roles": (
                    ["advisory", "facility", "terminology"]
                    if include_canonical
                    else ["advisory", "terminology"]
                )
            },
            "type": "tool_call",
        },
    ]
    if include_canonical:
        calls.append(
            {
                "id": "call:canonical",
                "name": "resolve_canonical_ref",
                "args": {"canonical_ref": FACILITY_ID},
                "type": "tool_call",
            }
        )
    return calls


def _patch(*, include_facility: bool = True) -> str:
    lines = [
        "GRAPH_PATCH",
        f"{EVENT_URI} | rdf:type | {EVENT_CLASS} | {SOURCE_ID}",
    ]
    if include_facility:
        lines.append(
            f"{EVENT_URI} | atm:controlledNASelement | {FACILITY_ID} | {SOURCE_ID}"
        )
    lines.extend(["", "PROFILE_GAPS", "NONE"])
    return "\n".join(lines)


def _run(model, *, facility_status: AgentStatus = AgentStatus.RESOLVED):
    cards, canonical, tools = _session(facility_status=facility_status)
    return run_kg_tool_agent(
        model=model,
        tools=tools,
        event_uri=EVENT_URI,
        event_class=EVENT_CLASS,
        schema_slice_id=load_schema_guide().schema_slice_id,
        allowed_source_ids={SOURCE_ID},
        canonical_entities=canonical,
        evidence_cards=cards,
    )


def test_model_selects_context_tools_then_emits_text_graph_patch():
    model = _ScriptedToolModel(
        [
            _selection_turn(_required_calls()),
            _draft_turn(_patch()),
        ]
    )
    result = _run(model)
    assert result.status == AgentStatus.RESOLVED
    assert result.graph_patch is not None
    assert len(result.graph_patch.patch_lines) == 2
    assert len(result.model_calls) == 2
    assert [trace.tool for trace in result.evidence_card.tool_trace] == [
        "get_schema_context",
        "get_source_evidence",
        "resolve_canonical_ref",
    ]
    assert result.evidence_card.agent_role == "knowledge_graph_construction"
    assert [phase for phase, _ in model.invocations] == [
        "select_tool",
        "final_answer",
    ]
    second_messages = model.invocations[1][1]
    assert sum(isinstance(message, ToolMessage) for message in second_messages) == 3


def test_agent_entrypoint_prefers_the_tool_model_factory():
    model = _ScriptedToolModel(
        [_selection_turn(_required_calls()), _draft_turn(_patch())]
    )
    cards = _cards()
    result = run_kg_construction_agent(
        task=AgentTask(
            run_id="run:example",
            source_id=SOURCE_ID,
            objective="construct event graph patch",
            allowed_tools=[
                "get_schema_context",
                "resolve_canonical_ref",
                "get_source_evidence",
            ],
        ),
        inputs=KGConstructionInput(
            advisory=SourceRecord(
                source_id=SOURCE_ID,
                family=SourceFamily.ATCSCC_ADVISORY,
                content="GROUND STOP CTL ELEMENT: ZZQ",
            ),
            advisory_card=cards["advisory"],
            facility_card=cards["facility"],
            terminology_card=cards["terminology"],
            event_uri=EVENT_URI,
            event_class=EVENT_CLASS,
            guide=load_schema_guide(),
            allowed_source_ids={SOURCE_ID},
        ),
        tool_model_factory=lambda tools: model,
    )
    assert result.status == AgentStatus.RESOLVED
    assert len(result.model_calls) == 2
    assert len(result.evidence_card.tool_trace) == 3


def test_agent_entrypoint_does_not_fallback_to_card_or_advisory_source_ids():
    """An empty accepted-claim allowlist cannot be widened by envelope metadata."""

    model = _ScriptedToolModel(
        [_selection_turn(_required_calls()), _draft_turn(_patch())]
    )
    cards = _cards()
    cards["facility"] = cards["facility"].model_copy(
        update={"source_ids": [SOURCE_ID, "authority:nasr:KZZQ"]}
    )

    result = run_kg_construction_agent(
        task=AgentTask(
            run_id="run:example",
            source_id=SOURCE_ID,
            objective="construct event graph patch",
            allowed_tools=[
                "get_schema_context",
                "resolve_canonical_ref",
                "get_source_evidence",
            ],
        ),
        inputs=KGConstructionInput(
            advisory=SourceRecord(
                source_id=SOURCE_ID,
                family=SourceFamily.ATCSCC_ADVISORY,
                content="GROUND STOP CTL ELEMENT: ZZQ",
            ),
            advisory_card=cards["advisory"],
            facility_card=cards["facility"],
            terminology_card=cards["terminology"],
            event_uri=EVENT_URI,
            event_class=EVENT_CLASS,
            guide=load_schema_guide(),
            allowed_source_ids=set(),
        ),
        tool_model_factory=lambda tools: model,
    )

    assert result.status is AgentStatus.BLOCKED
    assert "accepted event evidence" in str(result.failure_reason)
    assert model.invocations == []


def test_agent_entrypoint_blocks_without_a_native_tool_model():
    cards = _cards()
    result = run_kg_construction_agent(
        task=AgentTask(
            run_id="run:example",
            source_id=SOURCE_ID,
            objective="construct event graph patch",
            allowed_tools=[
                "get_schema_context",
                "resolve_canonical_ref",
                "get_source_evidence",
            ],
        ),
        inputs=KGConstructionInput(
            advisory=SourceRecord(
                source_id=SOURCE_ID,
                family=SourceFamily.ATCSCC_ADVISORY,
                content="GROUND STOP CTL ELEMENT: ZZQ",
            ),
            advisory_card=cards["advisory"],
            facility_card=cards["facility"],
            terminology_card=cards["terminology"],
            event_uri=EVENT_URI,
            event_class=EVENT_CLASS,
            guide=load_schema_guide(),
            allowed_source_ids={SOURCE_ID},
        ),
    )
    assert result.status == AgentStatus.BLOCKED
    assert "native tool-calling model" in str(result.failure_reason)


def test_abstained_facility_does_not_require_canonical_lookup():
    model = _ScriptedToolModel(
        [
            _selection_turn(_required_calls(include_canonical=False)),
            _draft_turn(_patch(include_facility=False)),
        ]
    )
    result = _run(model, facility_status=AgentStatus.ABSTAIN)
    assert result.status == AgentStatus.RESOLVED
    assert [trace.tool for trace in result.evidence_card.tool_trace] == [
        "get_schema_context",
        "get_source_evidence",
    ]


def test_missing_required_context_tool_is_blocked_before_execution():
    model = _ScriptedToolModel(
        [
            _selection_turn(_required_calls(include_canonical=False)),
        ]
    )
    result = _run(model)
    assert result.status == AgentStatus.BLOCKED
    assert result.model_calls and len(result.model_calls) == 1
    assert result.evidence_card.tool_trace == []
    assert "resolve_canonical_ref" in str(result.failure_reason)


def test_out_of_scope_tool_is_blocked():
    model = _ScriptedToolModel(
        [
            _selection_turn(
                [
                    {
                        "id": "call:write",
                        "name": "write_neo4j",
                        "args": {},
                        "type": "tool_call",
                    }
                ]
            )
        ]
    )
    result = _run(model)
    assert result.status == AgentStatus.BLOCKED
    assert "unknown KG Construction Agent tool" in str(result.failure_reason)


def test_wrong_tool_argument_is_blocked_and_safely_traced():
    calls = _required_calls()
    calls[0]["args"] = {"event_class": "schema:OutsideTask"}
    model = _ScriptedToolModel([_selection_turn(calls)])
    result = _run(model)
    assert result.status == AgentStatus.BLOCKED
    assert result.evidence_card.tool_trace[0].status == "blocked"
    assert "outside the current task" in str(result.evidence_card.tool_trace[0].error)


def test_second_round_tool_request_is_blocked():
    second_tool_call = [
        {
            "id": "call:again",
            "name": "get_schema_context",
            "args": {"event_class": EVENT_CLASS},
            "type": "tool_call",
        }
    ]
    model = _ScriptedToolModel(
        [
            _selection_turn(_required_calls()),
            _draft_turn("", tool_calls=second_tool_call),
        ]
    )
    result = _run(model)
    assert result.status == AgentStatus.BLOCKED
    assert "requested another tool" in str(result.failure_reason)


def test_missing_event_class_abstains_without_model_or_tool_call():
    model = _ScriptedToolModel([])
    cards, canonical, tools = _session()
    result = run_kg_tool_agent(
        model=model,
        tools=tools,
        event_uri=EVENT_URI,
        event_class="",
        schema_slice_id=load_schema_guide().schema_slice_id,
        allowed_source_ids={SOURCE_ID},
        canonical_entities=canonical,
        evidence_cards=cards,
    )
    assert result.status == AgentStatus.ABSTAIN
    assert result.model_calls == []
    assert model.invocations == []


def test_tool_trace_contains_references_not_evidence_payload():
    model = _ScriptedToolModel(
        [_selection_turn(_required_calls()), _draft_turn(_patch())]
    )
    result = _run(model)
    trace_text = str(
        [trace.model_dump(mode="json") for trace in result.evidence_card.tool_trace]
    )
    assert "CTL ELEMENT: ZZQ" not in trace_text
    assert "GROUND STOP" not in trace_text
    assert "evidence:advisory" in trace_text


def test_kg_source_evidence_projection_excludes_authority_audit_internals():
    """The KG model sees accepted event claims, not authority-audit internals."""

    authority_source = "authority:pcg:ground-stop"
    facility = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="controlled_facility",
                value="ZZQ",
                ontology_target="nas:Airport",
                evidence_text="CTL ELEMENT: ZZQ",
                source_id=SOURCE_ID,
                canonical_ref=FACILITY_ID,
                uncertainty="PRIVATE CLAIM NOTE",
            ),
            EvidenceClaim(
                field_name="authority_definition",
                value="Ground Stop",
                evidence_text="PRIVATE AUTHORITY RAW TEXT",
                source_id=authority_source,
                canonical_ref="term:private",
            ),
        ],
        canonical_refs=[FACILITY_ID, "term:private"],
        source_ids=[SOURCE_ID, authority_source],
        uncertainties=["PRIVATE CARD UNCERTAINTY"],
        tool_trace=[
            ToolTraceEntry(
                tool="lookup_nasr_facility",
                result_refs=["resolution-task:private"],
                source_ids=[authority_source],
            )
        ],
        decision_basis="PRIVATE DECISION BASIS",
    )
    gateway = KGConstructionToolGateway(
        guide=load_schema_guide(),
        event_class=EVENT_CLASS,
        evidence_cards={"facility": facility},
        canonical_entities={FACILITY_ID: "nas:Airport"},
        allowed_source_ids={SOURCE_ID},
    )

    result = gateway.get_source_evidence(roles=["facility"])
    projected = result.payload["evidence_cards"][0]

    assert set(projected) == {
        "agent_role",
        "status",
        "claims",
        "canonical_refs",
    }
    assert result.source_ids == [SOURCE_ID]
    assert projected["canonical_refs"] == [FACILITY_ID]
    assert [claim["source_id"] for claim in projected["claims"]] == [SOURCE_ID]
    assert projected["claims"][0]["uncertainty"] is None
    assert "PRIVATE" not in str(result.payload)
