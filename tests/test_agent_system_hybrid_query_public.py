"""Public natural-language query tests over the live knowledge runtime."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryAnswer,
    HybridQueryScope,
    HybridQueryStatement,
    ModelCallRecord,
    ModelToolCall,
)
from aviation_agentic_ai.agent_system.knowledge_query import (
    answer_question,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn


_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "live_hybrid_query_fixture",
    Path(__file__).with_name("test_agent_system_hybrid_query_tools.py"),
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_fixture = importlib.util.module_from_spec(_FIXTURE_SPEC)
sys.modules[_FIXTURE_SPEC.name] = _fixture
_FIXTURE_SPEC.loader.exec_module(_fixture)

EVENT_ID = _fixture.FORMAL_EVENT_ID


class _EvidenceModel:
    def __init__(self, scenario) -> None:  # type: ignore[no-untyped-def]
        event = scenario.store.get_event(EVENT_ID)
        assert event is not None
        fact = next(
            fact
            for fact in scenario.store.get_event_facts(EVENT_ID)
            if fact.predicate_iri.endswith("impactingCondition")
        )
        link = next(
            link
            for link in scenario.store.get_event_evidence(EVENT_ID)
            if link.owner_kind == "fact" and link.owner_id == fact.fact_id
        )
        source = scenario.store.get_source_version(link.source_version_id)
        assert source is not None
        self.event = event
        self.fact = fact
        self.link = link
        self.source = source
        self.turn = 0
        self.questions: list[str] = []

    def invoke(
        self,
        messages: list[Any],
        *,
        phase: str,
    ) -> ToolModelTurn:
        assert phase == "query_step"
        self.turn += 1
        self.questions.append(str(messages[1].content))
        if self.turn == 1:
            call = {
                "id": "facts",
                "name": "read_tmi_event_facts",
                "args": {"event_id": EVENT_ID},
            }
            return ToolModelTurn(
                message=AIMessage(content="", tool_calls=[call]),
                record=ModelCallRecord(
                    agent="query",
                    raw_response="",
                    provider="scripted",
                    model="scripted",
                    tool_calls=[
                        ModelToolCall(
                            call_id="facts",
                            name="read_tmi_event_facts",
                            arguments={"event_id": EVENT_ID},
                        )
                    ],
                ),
            )
        response = HybridQueryAnswer(
            status="ok",
            statements=(
                HybridQueryStatement(
                    kind="source_fact",
                    text=(
                        "The advisory records weather as its "
                        "declared reason."
                    ),
                    support_event_ids=(self.event.event_id,),
                    support_fact_ids=(self.fact.fact_id,),
                    support_source_ids=(self.source.source_id,),
                    support_source_version_ids=(
                        self.source.source_version_id,
                    ),
                    support_source_anchor_ids=(
                        self.link.source_anchor_id,
                    ),
                ),
            ),
        ).model_dump_json()
        return ToolModelTurn(
            message=AIMessage(content=response),
            record=ModelCallRecord(
                agent="query",
                raw_response=response,
                provider="scripted",
                model="scripted",
                attempt=2,
            ),
        )


def test_public_query_uses_model_routing_without_a_corpus_manifest(
    tmp_path: Path,
) -> None:
    scenario = _fixture._live_store(tmp_path)
    runtime = QueryRuntime(
        store=scenario.store,
        source_index=None,
        event_index=None,
    )

    for question in (
        "Could you summarize the reason in this GDP record?",
        "这份 GDP 通告中记录的原因是什么？",
    ):
        model = _EvidenceModel(scenario)
        outcome = answer_question(
            runtime=runtime,
            question=question,
            scope=HybridQueryScope(event_id=EVENT_ID),
            model_factory=lambda _tools, model=model: model,
        )

        assert outcome.status == "ok"
        assert len(outcome.model_calls) == 2
        assert outcome.tool_calls[0].tool == "read_tmi_event_facts"
        assert question in model.questions[0]
    assert not (scenario.store.root / "corpus_manifest.json").exists()
    scenario.store.close()


def test_valid_runtime_without_a_model_factory_is_blocked(
    tmp_path: Path,
) -> None:
    scenario = _fixture._live_store(tmp_path)
    outcome = answer_question(
        runtime=QueryRuntime(
            store=scenario.store,
            source_index=None,
            event_index=None,
        ),
        question="Tell me what this record says.",
        scope=HybridQueryScope(event_id=EVENT_ID),
        model_factory=None,
    )

    assert outcome.status == "blocked"
    assert "model factory" in outcome.failure_reason
    assert outcome.model_calls == []
    scenario.store.close()
