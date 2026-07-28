"""Compact smoke evaluation for historical case retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import aviation_agentic_ai.agent_system.case_retrieval_evaluation as evaluation
from aviation_agentic_ai.agent_system.case_retrieval_contracts import (
    CaseSimilarityResult,
)
from aviation_agentic_ai.agent_system.contracts import CaseSimilarityMatch
from aviation_agentic_ai.agent_system.corpus_store import CorpusCase


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
GDP = f"{ATM}GroundDelayProgramTMI"
KJFK = "urn:aviation-agentic-ai:facility:airport:KJFK"


def _case(name: str, source_id: str) -> CorpusCase:
    return CorpusCase(
        case_id=f"case:{name}",
        case_iri=f"urn:decision-case:{name}",
        reconstruction_iri=f"urn:decision-case-reconstruction:{name}",
        event_id=f"event:{name}",
        run_ids=[f"run:{name}"],
        advisory_source_id=source_id,
        event_type_iris=[GDP],
        facility_ids=[KJFK],
        operational_start="2026-05-19T10:00:00+00:00",
        operational_end="2026-05-19T11:00:00+00:00",
        reason_status="formal",
        reason_value="weather",
    )


def _gold(path: Path, queries: list[dict[str, object]]) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "version": "case-retrieval-smoke-v1",
                "queries": queries,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _ranked_match(
    *,
    rank: int,
    name: str,
    source_id: str,
) -> CaseSimilarityMatch:
    return CaseSimilarityMatch(
        rank=rank,
        case_id=f"case:{name}",
        event_id=f"event:{name}",
        advisory_source_id=source_id,
        score=1.0 - rank / 10,
        tmi_type_iri=GDP,
        facility_ids=(KJFK,),
        reason_status="formal",
        reason_value="weather",
    )


def _install_scripted_backend(
    monkeypatch,
    tmp_path: Path,
    *,
    by_event: dict[str, CaseSimilarityResult],
) -> None:
    cases = [
        _case("q1", "source:q1"),
        _case("q2", "source:q2"),
        _case("q3", "source:q3"),
        _case("r1", "source:r1"),
        _case("r2", "source:r2"),
        _case("other", "source:other"),
    ]
    store = SimpleNamespace(
        root=tmp_path / "corpus",
        cases=tuple(cases),
        manifest=SimpleNamespace(corpus_id="corpus:test"),
    )
    index = SimpleNamespace(
        manifest=SimpleNamespace(
            representation_version="decision-record-v1",
            embedding_model_id="test/model",
        )
    )
    monkeypatch.setattr(
        evaluation,
        "CorpusQueryStore",
        lambda _corpus_dir: store,
    )
    monkeypatch.setattr(
        evaluation,
        "ChromaCaseRetrievalIndex",
        lambda received_store, _index_dir: (
            index if received_store is store else None
        ),
    )
    monkeypatch.setattr(
        evaluation,
        "find_similar_cases",
        lambda received_store, received_index, query: (
            by_event[query.reference_event_id]
            if received_store is store and received_index is index
            else None
        ),
    )


def test_smoke_metrics_compute_ranked_and_insufficient_cases(
    tmp_path: Path,
    monkeypatch,
) -> None:
    filters = {
        "event_type_iri": GDP,
        "facility_id": KJFK,
        "reason_status": "formal",
        "reason_value": "weather",
    }
    gold_path = _gold(
        tmp_path / "gold.yaml",
        [
            {
                "query_source_id": "source:q1",
                "expected_status": "ok",
                "filters": filters,
                "relevant_source_ids": ["source:r1"],
            },
            {
                "query_source_id": "source:q2",
                "expected_status": "ok",
                "filters": filters,
                "relevant_source_ids": ["source:r2"],
            },
            {
                "query_source_id": "source:q3",
                "expected_status": "insufficient",
                "filters": filters,
            },
        ],
    )
    query_one = evaluation.CaseSimilarityQuery(
        reference_event_id="event:q1",
        **filters,
    )
    query_two = evaluation.CaseSimilarityQuery(
        reference_event_id="event:q2",
        **filters,
    )
    query_three = evaluation.CaseSimilarityQuery(
        reference_event_id="event:q3",
        **filters,
    )
    _install_scripted_backend(
        monkeypatch,
        tmp_path,
        by_event={
            "event:q1": CaseSimilarityResult(
                status="ok",
                query=query_one,
                candidate_count=3,
                representation_version="decision-record-v1",
                embedding_model_id="test/model",
                matches=(
                    _ranked_match(
                        rank=1,
                        name="r1",
                        source_id="source:r1",
                    ),
                ),
            ),
            "event:q2": CaseSimilarityResult(
                status="ok",
                query=query_two,
                candidate_count=3,
                representation_version="decision-record-v1",
                embedding_model_id="test/model",
                matches=(
                    _ranked_match(
                        rank=1,
                        name="other",
                        source_id="source:other",
                    ),
                    _ranked_match(
                        rank=2,
                        name="r2",
                        source_id="source:r2",
                    ),
                ),
            ),
            "event:q3": CaseSimilarityResult(
                status="insufficient",
                query=query_three,
                candidate_count=0,
                representation_version="decision-record-v1",
                embedding_model_id="test/model",
                limitation="No exact candidates.",
            ),
        },
    )

    metrics = evaluation.evaluate_case_retrieval_smoke(
        corpus_dir=tmp_path / "corpus",
        gold_path=gold_path,
    )

    assert metrics.query_count == 3
    assert metrics.ranked_query_count == 2
    assert metrics.hit_count_at_1 == 1
    assert metrics.hit_count_at_3 == 2
    assert metrics.hit_rate_at_1 == pytest.approx(0.5)
    assert metrics.hit_rate_at_3 == pytest.approx(1.0)
    assert metrics.mean_reciprocal_rank == pytest.approx(0.75)
    assert metrics.expected_insufficient_count == 1
    assert metrics.expected_insufficient_pass_count == 1


def test_unknown_query_source_blocks_evaluation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _install_scripted_backend(monkeypatch, tmp_path, by_event={})
    gold_path = _gold(
        tmp_path / "gold.yaml",
        [
            {
                "query_source_id": "source:unknown",
                "expected_status": "insufficient",
                "filters": {},
            }
        ],
    )

    with pytest.raises(ValueError, match="unknown query_source_id"):
        evaluation.evaluate_case_retrieval_smoke(
            corpus_dir=tmp_path / "corpus",
            gold_path=gold_path,
        )


@pytest.mark.parametrize("violation", ["anchor", "filter"])
def test_invalid_ranked_result_blocks_evaluation(
    tmp_path: Path,
    monkeypatch,
    violation: str,
) -> None:
    filters = {
        "event_type_iri": GDP,
        "facility_id": KJFK,
        "reason_status": "formal",
        "reason_value": "weather",
    }
    gold_path = _gold(
        tmp_path / "gold.yaml",
        [
            {
                "query_source_id": "source:q1",
                "expected_status": "ok",
                "filters": filters,
                "relevant_source_ids": ["source:r1"],
            }
        ],
    )
    query = evaluation.CaseSimilarityQuery(
        reference_event_id="event:q1",
        **filters,
    )
    match = (
        _ranked_match(
            rank=1,
            name="q1",
            source_id="source:q1",
        )
        if violation == "anchor"
        else _ranked_match(
            rank=1,
            name="r1",
            source_id="source:r1",
        ).model_copy(update={"facility_ids": ("facility:other",)})
    )
    _install_scripted_backend(
        monkeypatch,
        tmp_path,
        by_event={
            "event:q1": CaseSimilarityResult(
                status="ok",
                query=query,
                candidate_count=1,
                representation_version="decision-record-v1",
                embedding_model_id="test/model",
                matches=(match,),
            )
        },
    )

    with pytest.raises(ValueError, match=violation):
        evaluation.evaluate_case_retrieval_smoke(
            corpus_dir=tmp_path / "corpus",
            gold_path=gold_path,
        )


def test_module_main_prints_canonical_metrics_json(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    metrics = evaluation.RetrievalSmokeMetrics(
        query_count=1,
        ranked_query_count=0,
        hit_count_at_1=0,
        hit_count_at_3=0,
        hit_rate_at_1=0.0,
        hit_rate_at_3=0.0,
        mean_reciprocal_rank=0.0,
        expected_insufficient_count=1,
        expected_insufficient_pass_count=1,
    )
    monkeypatch.setattr(
        evaluation,
        "evaluate_case_retrieval_smoke",
        lambda **_kwargs: metrics,
    )

    result = evaluation.main(
        [
            "--corpus-dir",
            str(tmp_path / "corpus"),
            "--gold",
            str(tmp_path / "gold.yaml"),
        ]
    )

    assert result == 0
    assert json.loads(capsys.readouterr().out) == metrics.model_dump(
        mode="json"
    )
