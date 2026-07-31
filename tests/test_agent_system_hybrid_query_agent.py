"""Software-contract tests for the bounded HybridRAG Query Agent loop."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryAnswer,
    HybridQueryEvidence,
    HybridQueryScope,
    HybridQueryStatement,
    HybridQuerySupportRecord,
    HybridQueryToolObservation,
    ModelCallRecord,
    ModelToolCall,
    QueryGraphEdge,
    QueryGraphPath,
    SourceFamily,
)
from aviation_agentic_ai.agent_system.hybrid_query_agent import (
    run_hybrid_query_agent,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn


class _EventInput(BaseModel):
    event_id: str = Field(min_length=1)


class _SourceInput(BaseModel):
    source_version_id: str = Field(min_length=1)


def _scope() -> HybridQueryScope:
    return HybridQueryScope(
        event_id="urn:event:138",
        candidate_scope="archive",
        offset=0,
        limit=20,
    )


def _observation(*, status: str = "ok") -> dict[str, object]:
    return HybridQueryToolObservation(
        status=status,
        content=(
            "The formal event fact states that the controlled facility is KEWR."
            if status == "ok"
            else "No matching formal event fact was found."
        ),
        details=HybridQueryEvidence(
            event_ids=("urn:event:138",),
            fact_ids=("urn:fact:facility",) if status == "ok" else (),
            source_ids=("atcscc:2026-05-20:138",),
        ),
        support_records=(
            (
                HybridQuerySupportRecord(
                    kind="source_fact",
                    event_ids=("urn:event:138",),
                    fact_ids=("urn:fact:facility",),
                    source_ids=("atcscc:2026-05-20:138",),
                ),
            )
            if status == "ok"
            else ()
        ),
        limitation="" if status == "ok" else "Formal evidence is insufficient.",
    ).model_dump(mode="json")


@tool("read_tmi_event_facts", args_schema=_EventInput)
def _read_tmi_event_facts(event_id: str) -> dict[str, object]:
    """Read formal facts for one corpus event."""

    assert event_id == "urn:event:138"
    return _observation()


@tool("read_weather_context", args_schema=_EventInput)
def _read_weather_context(event_id: str) -> dict[str, object]:
    """Read non-causal Weather context for one corpus event."""

    assert event_id == "urn:event:138"
    return HybridQueryToolObservation(
        status="ok",
        content="One TAF report is retained as non-causal context.",
        details=HybridQueryEvidence(
            event_ids=("urn:event:138",),
            fact_ids=("urn:fact:taf",),
            context_association_ids=("urn:association:taf",),
            source_ids=("taf:KEWR:2026-05-20T12:00Z",),
        ),
        support_records=(
            HybridQuerySupportRecord(
                kind="non_causal_context",
                event_ids=("urn:event:138",),
                fact_ids=("urn:fact:taf",),
                context_association_ids=("urn:association:taf",),
                source_ids=("taf:KEWR:2026-05-20T12:00Z",),
            ),
        ),
    ).model_dump(mode="json")


def _answer(
    *,
    status: str = "ok",
    answer: str = "KEWR is the controlled facility.",
    event_ids: tuple[str, ...] = ("urn:event:138",),
    fact_ids: tuple[str, ...] = ("urn:fact:facility",),
    context_ids: tuple[str, ...] = (),
    source_ids: tuple[str, ...] = ("atcscc:2026-05-20:138",),
    kind: str = "source_fact",
) -> str:
    return HybridQueryAnswer(
        status=status,
        statements=(
            (
                HybridQueryStatement(
                    kind=kind,
                    text=answer,
                    support_event_ids=event_ids,
                    support_fact_ids=fact_ids,
                    support_context_association_ids=context_ids,
                    support_source_ids=source_ids,
                ),
            )
            if status == "ok"
            else ()
        ),
        limitations=(
            (answer,)
            if status == "insufficient"
            else ()
        ),
    ).model_dump_json()


class _LoopModel:
    def __init__(
        self,
        *,
        calls: list[dict[str, object]] | None = None,
        final_content: str | None = None,
        first_error: str | None = None,
        responses: list[AIMessage] | None = None,
    ) -> None:
        self.calls = (
            [
                {
                    "id": "call-1",
                    "name": "read_tmi_event_facts",
                    "args": {"event_id": "urn:event:138"},
                }
            ]
            if calls is None
            else calls
        )
        self.final_content = final_content or _answer()
        self.first_error = first_error
        self.responses = responses or [
            AIMessage(content="", tool_calls=self.calls),
            AIMessage(content=self.final_content),
        ]
        self.phases: list[str] = []
        self.messages: list[list[Any]] = []

    def invoke(self, messages: list[Any], *, phase: str) -> ToolModelTurn:
        self.phases.append(phase)
        self.messages.append(list(messages))
        assert phase == "query_step"
        message = self.responses[len(self.phases) - 1]
        tool_calls = [dict(call) for call in message.tool_calls]
        return ToolModelTurn(
            message=message,
            record=ModelCallRecord(
                agent="query",
                raw_response=str(message.content or ""),
                provider="scripted",
                model="scripted",
                error=self.first_error if len(self.phases) == 1 else None,
                attempt=len(self.phases),
                tool_calls=[
                    ModelToolCall(
                        call_id=str(call["id"]),
                        name=str(call["name"]),
                        arguments=dict(call["args"]),  # type: ignore[arg-type]
                    )
                    for call in tool_calls
                ],
            ),
        )


def _run(
    model: _LoopModel,
    *,
    question: str = "Which airport does this record control?",
    tools: list[Any] | None = None,
):
    return run_hybrid_query_agent(
        question=question,
        scope=_scope(),
        tools=tools or [_read_tmi_event_facts],
        model_factory=lambda _tools: model,
    )


def test_every_natural_language_question_activates_the_model() -> None:
    for question in (
        "Which airport does this record control?",
        "Could you tell me the airport constrained by this advisory?",
        "\u8fd9\u4efd\u901a\u544a\u63a7\u5236\u7684\u662f\u54ea\u4e2a"
        "\u673a\u573a\uff1f",
    ):
        model = _LoopModel()
        outcome = _run(model, question=question)

        assert outcome.status == "ok"
        assert model.phases == ["query_step", "query_step"]
        assert len(outcome.model_calls) == 2
        assert outcome.tool_calls[0].tool == "read_tmi_event_facts"
        assert outcome.answer_statements
        assert outcome.support_records


def test_flight_and_aggregate_evidence_ids_survive_the_agent_loop() -> None:
    class _SectorInput(BaseModel):
        sector_id: str = Field(min_length=1)

    @tool("analyze_sector_traffic", args_schema=_SectorInput)
    def analyze_sector_traffic(sector_id: str) -> dict[str, object]:
        """Return one source-bound sector aggregation."""

        assert sector_id == "urn:sector:ZTL040"
        return HybridQueryToolObservation(
            status="ok",
            content="Two distinct flights have accepted passages in the interval.",
            details=HybridQueryEvidence(
                flight_ids=("urn:flight:1", "urn:flight:2"),
                publication_ids=("urn:publication:1", "urn:publication:2"),
                sector_passage_ids=("urn:passage:1", "urn:passage:2"),
                derivation_ids=("urn:query-derivation:1",),
                source_ids=("source:nasa:flight",),
            ),
            support_records=(
                HybridQuerySupportRecord(
                    kind="aggregate_result",
                    flight_ids=("urn:flight:1", "urn:flight:2"),
                    publication_ids=("urn:publication:1", "urn:publication:2"),
                    sector_passage_ids=("urn:passage:1", "urn:passage:2"),
                    derivation_ids=("urn:query-derivation:1",),
                    source_ids=("source:nasa:flight",),
                ),
            ),
        ).model_dump(mode="json")

    answer = HybridQueryAnswer(
        status="ok",
        statements=(
            HybridQueryStatement(
                kind="aggregate_result",
                text="Two distinct flights are recorded in the selected sector interval.",
                support_flight_ids=("urn:flight:1", "urn:flight:2"),
                support_publication_ids=(
                    "urn:publication:1",
                    "urn:publication:2",
                ),
                support_sector_passage_ids=("urn:passage:1", "urn:passage:2"),
                support_derivation_ids=("urn:query-derivation:1",),
                support_source_ids=("source:nasa:flight",),
            ),
        ),
    ).model_dump_json()
    model = _LoopModel(
        calls=[
            {
                "id": "call-sector",
                "name": "analyze_sector_traffic",
                "args": {"sector_id": "urn:sector:ZTL040"},
            }
        ],
        final_content=answer,
    )

    outcome = _run(model, tools=[analyze_sector_traffic])

    assert outcome.status == "ok"
    assert outcome.retrieved_flight_ids == ["urn:flight:1", "urn:flight:2"]
    assert outcome.retrieved_sector_passage_ids == [
        "urn:passage:1",
        "urn:passage:2",
    ]
    assert outcome.retrieved_derivation_ids == ["urn:query-derivation:1"]
    assert outcome.tool_calls[0].derivation_ids == ["urn:query-derivation:1"]


def test_multiple_model_selected_tools_feed_the_answer_turn() -> None:
    model = _LoopModel(
        calls=[
            {
                "id": "call-facts",
                "name": "read_tmi_event_facts",
                "args": {"event_id": "urn:event:138"},
            },
            {
                "id": "call-weather",
                "name": "read_weather_context",
                "args": {"event_id": "urn:event:138"},
            },
        ],
        final_content=HybridQueryAnswer(
            status="ok",
            statements=(
                HybridQueryStatement(
                    kind="source_fact",
                    text="KEWR is the controlled facility.",
                    support_event_ids=("urn:event:138",),
                    support_fact_ids=("urn:fact:facility",),
                    support_source_ids=("atcscc:2026-05-20:138",),
                ),
                HybridQueryStatement(
                    kind="non_causal_context",
                    text="One TAF report is retained as non-causal context.",
                    support_event_ids=("urn:event:138",),
                    support_fact_ids=("urn:fact:taf",),
                    support_context_association_ids=("urn:association:taf",),
                    support_source_ids=("taf:KEWR:2026-05-20T12:00Z",),
                ),
            ),
            limitations=(),
        ).model_dump_json(),
    )

    outcome = _run(
        model,
        tools=[_read_tmi_event_facts, _read_weather_context],
    )

    assert outcome.status == "ok"
    assert len(outcome.tool_calls) == 2
    answer_messages = model.messages[-1]
    tool_messages = [
        message for message in answer_messages if isinstance(message, ToolMessage)
    ]
    assert [message.tool_call_id for message in tool_messages] == [
        "call-facts",
        "call-weather",
    ]
    assert "non-causal" in str(tool_messages[1].content)
    assert '"evidence":' not in str(tool_messages[1].content)


def test_graph_paths_are_visible_to_and_citable_by_the_answer_turn() -> None:
    path = QueryGraphPath(
        path_id="urn:path:weather",
        path_kind="weather_context_at_controlled_facility",
        edges=(
            QueryGraphEdge(
                fact_id="urn:fact:controlled",
                subject_iri="urn:event:138",
                predicate_iri="atm:controlledNASelement",
                object_kind="iri",
                object_value="urn:airport:KEWR",
                source_ids=("atcscc:2026-05-20:138",),
            ),
            QueryGraphEdge(
                fact_id="urn:fact:forecast-airport",
                subject_iri="urn:weather:taf",
                predicate_iri="data:forecastingAirport",
                object_kind="iri",
                object_value="urn:airport:KEWR",
                source_ids=("taf:KEWR:2026-05-20T12:00Z",),
            ),
        ),
        source_ids=(
            "atcscc:2026-05-20:138",
            "taf:KEWR:2026-05-20T12:00Z",
        ),
    )

    @tool("read_tmi_event_graph", args_schema=_EventInput)
    def graph_tool(event_id: str) -> dict[str, object]:
        """Return one source-bound Weather context path."""

        assert event_id == "urn:event:138"
        return HybridQueryToolObservation(
            status="ok",
            content="One Weather context path is available.",
            details=HybridQueryEvidence(
                event_ids=("urn:event:138",),
                fact_ids=(
                    "urn:fact:controlled",
                    "urn:fact:forecast-airport",
                ),
                context_association_ids=("urn:association:taf",),
                graph_path_ids=(path.path_id,),
                source_ids=path.source_ids,
            ),
            support_records=(
                HybridQuerySupportRecord(
                    kind="non_causal_context",
                    event_ids=("urn:event:138",),
                    fact_ids=(
                        "urn:fact:controlled",
                        "urn:fact:forecast-airport",
                    ),
                    context_association_ids=("urn:association:taf",),
                    graph_path_ids=(path.path_id,),
                    source_ids=path.source_ids,
                ),
            ),
            graph_paths=(path,),
        ).model_dump(mode="json")

    model = _LoopModel(
        calls=[
            {
                "id": "graph",
                "name": "read_tmi_event_graph",
                "args": {"event_id": "urn:event:138"},
            }
        ],
        final_content=HybridQueryAnswer(
            status="ok",
            statements=(
                HybridQueryStatement(
                    kind="non_causal_context",
                    text=(
                        "The retained TAF and the TMI are connected to KEWR "
                        "without asserting causation."
                    ),
                    support_event_ids=("urn:event:138",),
                    support_fact_ids=(
                        "urn:fact:controlled",
                        "urn:fact:forecast-airport",
                    ),
                    support_context_association_ids=(
                        "urn:association:taf",
                    ),
                    support_graph_path_ids=(path.path_id,),
                    support_source_ids=path.source_ids,
                ),
            ),
        ).model_dump_json(),
    )

    outcome = _run(model, tools=[graph_tool])
    tool_message = next(
        message
        for message in model.messages[-1]
        if isinstance(message, ToolMessage)
    )
    model_observation = json.loads(str(tool_message.content))

    assert outcome.status == "ok"
    assert model_observation["graph_paths"][0]["path_id"] == path.path_id
    assert outcome.retrieved_graph_path_ids == [path.path_id]
    assert outcome.retrieved_graph_paths == [path]


def test_zero_tool_calls_is_blocked() -> None:
    model = _LoopModel(
        calls=[],
        responses=[AIMessage(content=_answer())],
    )

    outcome = _run(model)

    assert outcome.status == "blocked"
    assert "did not select" in outcome.failure_reason
    assert model.phases == ["query_step"]


def test_more_than_three_tool_calls_is_blocked_before_execution() -> None:
    calls = [
        {
            "id": f"call-{index}",
            "name": "read_tmi_event_facts",
            "args": {"event_id": "urn:event:138"},
        }
        for index in range(4)
    ]
    model = _LoopModel(calls=calls)

    outcome = _run(model)

    assert outcome.status == "blocked"
    assert "tool-call budget" in outcome.failure_reason
    assert outcome.tool_calls == []


def test_unknown_tool_and_invalid_arguments_are_blocked() -> None:
    unknown = _LoopModel(
        calls=[{"id": "call-1", "name": "delete_corpus", "args": {}}]
    )
    invalid = _LoopModel(
        calls=[
            {
                "id": "call-1",
                "name": "read_tmi_event_facts",
                "args": {"event_id": ""},
            }
        ]
    )

    unknown_outcome = _run(unknown)
    invalid_outcome = _run(invalid)

    assert unknown_outcome.status == "blocked"
    assert "unknown" in unknown_outcome.failure_reason
    assert invalid_outcome.status == "blocked"
    assert "arguments" in invalid_outcome.failure_reason


def test_provider_error_and_turn_budget_are_blocked() -> None:
    provider_error = _LoopModel(first_error="provider unavailable")
    repeated = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": f"call-{index}",
                    "name": "read_tmi_event_facts",
                    "args": {"event_id": "urn:event:138"},
                }
            ],
        )
        for index in range(1, 5)
    ]
    turn_budget = _LoopModel(
        responses=repeated,
    )

    first = _run(provider_error)
    second = _run(turn_budget)

    assert first.status == "blocked"
    assert first.failure_reason == "provider unavailable"
    assert second.status == "blocked"
    assert "turn budget" in second.failure_reason


def test_malformed_or_unsupported_answer_is_blocked() -> None:
    malformed = _LoopModel(final_content="KEWR")
    unsupported = _LoopModel(
        final_content=_answer(
            fact_ids=("urn:fact:invented",),
        )
    )

    malformed_outcome = _run(malformed)
    unsupported_outcome = _run(unsupported)

    assert malformed_outcome.status == "blocked"
    assert "JSON" in malformed_outcome.failure_reason
    assert unsupported_outcome.status == "blocked"
    assert "unsupported" in unsupported_outcome.failure_reason


def test_single_json_code_fence_is_accepted_without_using_surrounding_prose() -> None:
    wrapped = (
        "I inspected the tool result.\n\n"
        "```json\n"
        f"{_answer()}\n"
        "```\n"
    )

    outcome = _run(_LoopModel(final_content=wrapped))

    assert outcome.status == "ok"
    assert outcome.answer == "KEWR is the controlled facility."


def test_ok_answer_requires_sufficient_retrieval() -> None:
    @tool("read_tmi_event_facts", args_schema=_EventInput)
    def insufficient_tool(event_id: str) -> dict[str, object]:
        """Return an honest insufficient observation."""

        assert event_id == "urn:event:138"
        return _observation(status="insufficient")

    model = _LoopModel()

    outcome = _run(model, tools=[insufficient_tool])

    assert outcome.status == "blocked"
    assert "insufficient tool evidence" in outcome.failure_reason


def test_honest_insufficient_answer_is_preserved() -> None:
    @tool("read_tmi_event_facts", args_schema=_EventInput)
    def insufficient_tool(event_id: str) -> dict[str, object]:
        """Return an honest insufficient observation."""

        assert event_id == "urn:event:138"
        return _observation(status="insufficient")

    model = _LoopModel(
        final_content=_answer(
            status="insufficient",
            answer="The corpus does not record the requested reason.",
            fact_ids=(),
        )
    )

    outcome = _run(model, tools=[insufficient_tool])

    assert outcome.status == "insufficient"
    assert "does not record" in outcome.answer
    assert json.loads(model.final_content)["status"] == "insufficient"


class _NoInput(BaseModel):
    pass


@tool("find_tmi_events", args_schema=_NoInput)
def _find_tmi_events() -> dict[str, object]:
    """Find the event referenced by the user's natural-language question."""

    return HybridQueryToolObservation(
        status="ok",
        content="GDP 138 resolves to event urn:event:138.",
        details=HybridQueryEvidence(
            event_ids=("urn:event:138",),
            source_ids=("atcscc:2026-05-20:138",),
        ),
        support_records=(
            HybridQuerySupportRecord(
                kind="source_fact",
                event_ids=("urn:event:138",),
                source_ids=("atcscc:2026-05-20:138",),
            ),
        ),
    ).model_dump(mode="json")


def test_agent_can_resolve_a_case_then_retrieve_its_context() -> None:
    model = _LoopModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {"id": "find", "name": "find_tmi_events", "args": {}},
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "weather",
                        "name": "read_weather_context",
                        "args": {"event_id": "urn:event:138"},
                    }
                ],
            ),
            AIMessage(
                content=_answer(
                    answer="One TAF report is retained as non-causal context.",
                    fact_ids=("urn:fact:taf",),
                    context_ids=("urn:association:taf",),
                    source_ids=("taf:KEWR:2026-05-20T12:00Z",),
                    kind="non_causal_context",
                )
            ),
        ]
    )
    scope = _scope().model_copy(update={"event_id": None})

    outcome = run_hybrid_query_agent(
        question="What weather context is recorded for GDP 138?",
        scope=scope,
        tools=[_find_tmi_events, _read_weather_context],
        model_factory=lambda _tools: model,
    )

    assert outcome.status == "ok"
    assert model.phases == ["query_step", "query_step", "query_step"]
    assert any(
        isinstance(message, ToolMessage) and message.tool_call_id == "find"
        for message in model.messages[1]
    )
    assert len(outcome.tool_calls) == 2


def test_claim_boundary_rejects_causation_and_recommendation() -> None:
    causal = _LoopModel(
        final_content=_answer(
            answer="The TAF caused the GDP.",
            fact_ids=("urn:fact:facility",),
            kind="non_causal_context",
        )
    )
    recommendation = _LoopModel(
        final_content=_answer(
            answer="ATCSCC should use the same GDP.",
            kind="similarity",
        )
    )

    causal_outcome = _run(causal)
    recommendation_outcome = _run(recommendation)

    assert causal_outcome.status == "blocked"
    assert "claim boundary" in causal_outcome.failure_reason
    assert recommendation_outcome.status == "blocked"
    assert "claim boundary" in recommendation_outcome.failure_reason


def test_statement_kind_must_match_the_tool_evidence_layer() -> None:
    model = _LoopModel(
        calls=[
            {
                "id": "weather",
                "name": "read_weather_context",
                "args": {"event_id": "urn:event:138"},
            }
        ],
        final_content=_answer(
            answer="The TAF report is retained as context.",
            fact_ids=("urn:fact:taf",),
            source_ids=("taf:KEWR:2026-05-20T12:00Z",),
            kind="source_fact",
        ),
    )

    outcome = _run(model, tools=[_read_weather_context])

    assert outcome.status == "blocked"
    assert "evidence binding" in outcome.failure_reason


def test_statement_cannot_mix_a_fact_with_an_unrelated_source() -> None:
    @tool("read_tmi_event_facts", args_schema=_EventInput)
    def two_facts(event_id: str) -> dict[str, object]:
        """Return two independently sourced formal facts."""

        assert event_id == "urn:event:138"
        return HybridQueryToolObservation(
            status="ok",
            content="Two formal facts are available.",
            details=HybridQueryEvidence(
                event_ids=("urn:event:138",),
                fact_ids=("urn:fact:facility", "urn:fact:time"),
                source_ids=("source:facility", "source:time"),
            ),
            support_records=(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    event_ids=("urn:event:138",),
                    fact_ids=("urn:fact:facility",),
                    source_ids=("source:facility",),
                ),
                HybridQuerySupportRecord(
                    kind="source_fact",
                    event_ids=("urn:event:138",),
                    fact_ids=("urn:fact:time",),
                    source_ids=("source:time",),
                ),
            ),
        ).model_dump(mode="json")

    model = _LoopModel(
        final_content=_answer(
            fact_ids=("urn:fact:facility",),
            source_ids=("source:time",),
        )
    )

    outcome = _run(model, tools=[two_facts])

    assert outcome.status == "blocked"
    assert "evidence binding" in outcome.failure_reason


def test_case_metadata_cannot_borrow_a_source_from_an_unrelated_fact() -> None:
    @tool("read_tmi_event_facts", args_schema=_EventInput)
    def case_and_fact(event_id: str) -> dict[str, object]:
        """Return advisory event metadata and one separately sourced fact."""

        assert event_id == "urn:event:138"
        return HybridQueryToolObservation(
            status="ok",
            content="Event metadata and one formal fact are available.",
            details=HybridQueryEvidence(
                event_ids=("urn:event:138",),
                fact_ids=("urn:fact:weather",),
                source_ids=("source:advisory", "source:weather"),
            ),
            support_records=(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    event_ids=("urn:event:138",),
                    source_ids=("source:advisory",),
                ),
                HybridQuerySupportRecord(
                    kind="source_fact",
                    event_ids=("urn:event:138",),
                    fact_ids=("urn:fact:weather",),
                    source_ids=("source:weather",),
                ),
            ),
        ).model_dump(mode="json")

    model = _LoopModel(
        final_content=_answer(
            fact_ids=(),
            source_ids=("source:weather",),
        )
    )

    outcome = _run(model, tools=[case_and_fact])

    assert outcome.status == "blocked"
    assert "evidence binding" in outcome.failure_reason


def test_causal_language_is_rejected_even_when_labeled_source_fact() -> None:
    for text in (
        "Weather triggered the GDP.",
        "Weather drove the GDP.",
        "Weather led to the GDP.",
    ):
        outcome = _run(_LoopModel(final_content=_answer(answer=text)))

        assert outcome.status == "blocked"
        assert "claim boundary" in outcome.failure_reason


def test_query_scope_carries_logical_source_and_family_bounds() -> None:
    scope = HybridQueryScope(
        source_ids=("source:advisory:138",),
        source_families=(SourceFamily.ATCSCC_ADVISORY, SourceFamily.METAR),
    )

    assert scope.model_dump(mode="json")["source_ids"] == [
        "source:advisory:138"
    ]
    assert scope.model_dump(mode="json")["source_families"] == [
        "atcscc_advisory",
        "metar",
    ]


def _source_record_observation(
    *,
    include_support: bool,
    include_anchor: bool = True,
) -> dict[str, object]:
    source_anchor_ids = ("anchor:advisory:138",) if include_anchor else ()
    return HybridQueryToolObservation(
        status="ok",
        content="Exact source text says REASON: WEATHER.",
        details=HybridQueryEvidence(
            source_ids=("source:advisory:138",),
            source_version_ids=("version:advisory:138:v1",),
            source_anchor_ids=source_anchor_ids,
            chunk_ids=("chunk:advisory:138:reason",),
        ),
        support_records=(
            (
                HybridQuerySupportRecord(
                    kind="source_record",
                    source_ids=("source:advisory:138",),
                    source_version_ids=("version:advisory:138:v1",),
                    source_anchor_ids=source_anchor_ids,
                    chunk_ids=("chunk:advisory:138:reason",),
                ),
            )
            if include_support
            else ()
        ),
    ).model_dump(mode="json")


@tool("read_source", args_schema=_SourceInput)
def _read_source(source_version_id: str) -> dict[str, object]:
    """Read exact bounded source content."""

    assert source_version_id == "version:advisory:138:v1"
    return _source_record_observation(include_support=True)


def _source_record_answer(*, include_anchor: bool = True) -> str:
    return HybridQueryAnswer(
        status="ok",
        statements=(
            HybridQueryStatement(
                kind="source_record",
                text="The exact advisory text records WEATHER.",
                support_source_ids=("source:advisory:138",),
                support_source_version_ids=("version:advisory:138:v1",),
                support_source_anchor_ids=(
                    ("anchor:advisory:138",) if include_anchor else ()
                ),
                support_chunk_ids=("chunk:advisory:138:reason",),
            ),
        ),
    ).model_dump_json()


def test_exact_source_read_support_survives_trace_and_final_outcome() -> None:
    model = _LoopModel(
        calls=[
            {
                "id": "read-source",
                "name": "read_source",
                "args": {"source_version_id": "version:advisory:138:v1"},
            }
        ],
        final_content=_source_record_answer(),
    )

    outcome = _run(model, tools=[_read_source])

    assert outcome.status == "ok"
    assert outcome.retrieved_source_version_ids == [
        "version:advisory:138:v1"
    ]
    assert outcome.retrieved_source_anchor_ids == ["anchor:advisory:138"]
    assert outcome.retrieved_chunk_ids == ["chunk:advisory:138:reason"]
    assert outcome.tool_calls[0].source_version_ids == [
        "version:advisory:138:v1"
    ]
    assert outcome.tool_calls[0].source_anchor_ids == ["anchor:advisory:138"]
    assert outcome.tool_calls[0].chunk_ids == ["chunk:advisory:138:reason"]
    assert set(outcome.tool_calls[0].result_refs) >= {
        "version:advisory:138:v1",
        "anchor:advisory:138",
        "chunk:advisory:138:reason",
    }


def test_search_candidate_cannot_support_a_final_source_record_statement() -> None:
    @tool("search_source_text", args_schema=_SourceInput)
    def search_candidate(source_version_id: str) -> dict[str, object]:
        """Return a candidate that still requires exact source inspection."""

        assert source_version_id == "version:advisory:138:v1"
        return _source_record_observation(include_support=False)

    model = _LoopModel(
        calls=[
            {
                "id": "search-source",
                "name": "search_source_text",
                "args": {"source_version_id": "version:advisory:138:v1"},
            }
        ],
        final_content=_source_record_answer(),
    )

    outcome = _run(model, tools=[search_candidate])

    assert outcome.status == "blocked"
    assert "evidence binding" in outcome.failure_reason


def test_source_record_statement_requires_exact_version_and_anchor() -> None:
    @tool("read_source", args_schema=_SourceInput)
    def source_without_anchor(source_version_id: str) -> dict[str, object]:
        """Return an incomplete source binding without an exact anchor."""

        assert source_version_id == "version:advisory:138:v1"
        return _source_record_observation(
            include_support=True,
            include_anchor=False,
        )

    model = _LoopModel(
        calls=[
            {
                "id": "read-source",
                "name": "read_source",
                "args": {"source_version_id": "version:advisory:138:v1"},
            }
        ],
        final_content=_source_record_answer(include_anchor=False),
    )

    outcome = _run(model, tools=[source_without_anchor])

    assert outcome.status == "blocked"
    assert "source version and anchor" in outcome.failure_reason
