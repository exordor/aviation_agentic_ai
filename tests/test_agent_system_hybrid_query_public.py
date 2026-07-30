"""Public corpus-query cutover tests for free natural-language questions."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from click.testing import CliRunner
from langchain_core.messages import AIMessage

import aviation_agentic_ai.cli_agent_system as cli_module
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryAnswer,
    HybridQueryStatement,
    ModelCallRecord,
    ModelToolCall,
    QueryToolOutcome,
)
from aviation_agentic_ai.agent_system.corpus_query import (
    answer_corpus_question,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusQueryStore,
    build_corpus,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn


_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "hybrid_query_public_fixture",
    Path(__file__).with_name("test_agent_system_corpus_store.py"),
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_fixture = importlib.util.module_from_spec(_FIXTURE_SPEC)
_FIXTURE_SPEC.loader.exec_module(_fixture)

EVENT_ID = "urn:event:public-query"


def _corpus(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    _fixture._write_run(
        run_dir,
        event_id=EVENT_ID,
        suffix="public-query",
        event_type="atm:GroundDelayProgramTMI",
        formal_reason="weather",
    )
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_dir], corpus_dir)
    return corpus_dir


class _EvidenceModel:
    def __init__(self, store: CorpusQueryStore) -> None:
        case = store.get_case(EVENT_ID)
        assert case is not None
        fact = next(
            fact
            for fact in store.get_event_facts(EVENT_ID)
            if fact.predicate_iri.endswith("impactingCondition")
        )
        self.case = case
        self.fact = fact
        self.turn = 0
        self.questions: list[str] = []

    def invoke(self, messages: list[Any], *, phase: str) -> ToolModelTurn:
        assert phase == "query_step"
        self.turn += 1
        self.questions.append(str(messages[1].content))
        if self.turn == 1:
            calls = [
                {
                    "id": "facts",
                    "name": "read_case_facts",
                    "args": {"event_id": EVENT_ID},
                }
            ]
            return ToolModelTurn(
                message=AIMessage(content="", tool_calls=calls),
                record=ModelCallRecord(
                    agent="query",
                    raw_response="",
                    provider="scripted",
                    model="scripted",
                    tool_calls=[
                        ModelToolCall(
                            call_id="facts",
                            name="read_case_facts",
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
                    text="The advisory records weather as its declared reason.",
                    support_case_ids=(self.case.case_id,),
                    support_fact_ids=(self.fact.fact_id,),
                    support_source_ids=tuple(self.fact.source_ids),
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


def test_public_query_uses_the_model_for_paraphrases_and_chinese(
    tmp_path: Path,
) -> None:
    corpus_dir = _corpus(tmp_path)
    store = CorpusQueryStore(corpus_dir)

    for question in (
        "Could you summarize the reason in this GDP record?",
        "\u8fd9\u4efd GDP \u901a\u544a\u4e2d\u8bb0\u5f55\u7684\u539f"
        "\u56e0\u662f\u4ec0\u4e48\uff1f",
    ):
        model = _EvidenceModel(store)
        outcome = answer_corpus_question(
            corpus_dir=corpus_dir,
            question=question,
            event_id=EVENT_ID,
            model_factory=lambda _tools, model=model: model,
        )

        assert outcome.status == "ok"
        assert len(outcome.model_calls) == 2
        assert outcome.tool_calls[0].tool == "read_case_facts"
        assert question in model.questions[0]


def test_valid_corpus_without_a_model_factory_is_blocked(tmp_path: Path) -> None:
    outcome = answer_corpus_question(
        corpus_dir=_corpus(tmp_path),
        question="Tell me what this record says.",
        event_id=EVENT_ID,
    )

    assert outcome.status == "blocked"
    assert "model factory" in outcome.failure_reason
    assert outcome.model_calls == []


def test_ask_cli_rejects_the_removed_live_model_flag(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--corpus-dir",
            str(_corpus(tmp_path)),
            "--event-id",
            EVENT_ID,
            "--question",
            "What reason is recorded?",
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 2
    assert "No such option '--allow-live-model'" in result.output


def test_ask_cli_constructs_the_query_role(
    tmp_path: Path,
    monkeypatch,
) -> None:
    roles: list[str] = []

    def fake_model_factory(*, tools, role):  # type: ignore[no-untyped-def]
        roles.append(role)
        return object()

    def fake_answer(**kwargs):  # type: ignore[no-untyped-def]
        kwargs["model_factory"]([])
        return QueryToolOutcome(status="insufficient", answer="No evidence.")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        fake_model_factory,
    )
    monkeypatch.setattr(
        cli_module,
        "answer_corpus_question",
        fake_answer,
    )

    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--corpus-dir",
            str(_corpus(tmp_path)),
            "--event-id",
            EVENT_ID,
            "--question",
            "\u4efb\u610f\u81ea\u7136\u8bed\u8a00\u95ee\u9898",
        ],
    )

    assert result.exit_code == 0, result.output
    assert roles == ["query"]
