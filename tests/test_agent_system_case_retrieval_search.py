"""Exact corpus filtering followed by case-level vector recall."""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

from aviation_agentic_ai.agent_system.case_retrieval_contracts import (
    CaseSimilarityQuery,
    CaseVectorHit,
)
from aviation_agentic_ai.agent_system.case_retrieval_search import (
    find_similar_cases,
)
from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusArtifactMetadata,
    CorpusBuildManifest,
    CorpusCase,
    CorpusQueryStore,
)


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
KJFK = "urn:aviation-agentic-ai:facility:airport:KJFK"
KEWR = "urn:aviation-agentic-ai:facility:airport:KEWR"


def _case(
    name: str,
    *,
    facility_id: str = KJFK,
    start: str = "2026-05-19T08:00:00+00:00",
    end: str = "2026-05-19T10:00:00+00:00",
    reason_status: str = "formal",
    reason_value: str | None = "weather",
) -> CorpusCase:
    return CorpusCase(
        case_id=f"case:{name}",
        case_iri=f"urn:decision-case:{name}",
        reconstruction_iri=f"urn:decision-case-reconstruction:{name}",
        event_id=f"event:{name}",
        run_ids=[f"run:{name}"],
        advisory_source_id=f"2026-05-19:{name}",
        event_type_iris=[f"{ATM}GroundDelayProgramTMI"],
        facility_ids=[facility_id],
        operational_start=start,
        operational_end=end,
        reason_status=reason_status,
        reason_value=reason_value,
    )


def _write_jsonl(
    path: Path,
    rows: list[StrictModel],
) -> CorpusArtifactMetadata:
    data = "".join(row.model_dump_json() + "\n" for row in rows).encode()
    path.write_bytes(data)
    return CorpusArtifactMetadata(
        path=path.name,
        count=len(rows),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def _store(tmp_path: Path, cases: list[CorpusCase]) -> CorpusQueryStore:
    artifacts = {
        "cases": _write_jsonl(tmp_path / "cases.jsonl", cases),
        "facts": _write_jsonl(tmp_path / "facts.jsonl", []),
        "case_facts": _write_jsonl(tmp_path / "case_facts.jsonl", []),
        "source_bindings": _write_jsonl(
            tmp_path / "source_bindings.jsonl",
            [],
        ),
    }
    manifest = CorpusBuildManifest(
        corpus_id="corpus:search-test",
        run_count=len(cases),
        case_count=len(cases),
        fact_count=0,
        source_binding_count=0,
        source_object_count=0,
        artifacts=artifacts,
    )
    (tmp_path / "corpus_manifest.json").write_text(
        manifest.model_dump_json() + "\n",
        encoding="utf-8",
    )
    return CorpusQueryStore(tmp_path)


class FakeIndex:
    def __init__(
        self,
        cases: list[CorpusCase],
        scores: dict[str, float],
    ) -> None:
        self.manifest = SimpleNamespace(
            representation_version="decision-record-v1",
            embedding_model_id="test/four-dimensional",
        )
        self._case_by_id = {case.case_id: case for case in cases}
        self._scores = scores
        self.last_candidate_case_ids: tuple[str, ...] = ()
        self.last_n_results = 0
        self.anchor_case_id = ""

    def get_case_vector(self, case_id: str) -> tuple[float, ...]:
        self.anchor_case_id = case_id
        return (1.0, 0.0, 0.0, 0.0)

    def query_candidates(
        self,
        *,
        query_vector,
        candidate_case_ids,
        n_results,
    ) -> tuple[CaseVectorHit, ...]:
        assert tuple(query_vector) == (1.0, 0.0, 0.0, 0.0)
        self.last_candidate_case_ids = tuple(candidate_case_ids)
        self.last_n_results = n_results
        reverse_ties = sorted(candidate_case_ids, reverse=True)
        ranked = sorted(
            reverse_ties,
            key=lambda case_id: self._scores[case_id],
            reverse=True,
        )
        return tuple(
            CaseVectorHit(
                case_id=case_id,
                event_id=self._case_by_id[case_id].event_id,
                advisory_source_id=self._case_by_id[
                    case_id
                ].advisory_source_id,
                distance=1.0 - self._scores[case_id],
                similarity=self._scores[case_id],
            )
            for case_id in ranked[:n_results]
        )


def test_exact_filters_are_applied_before_cosine_ranking(
    tmp_path: Path,
) -> None:
    cases = [
        _case("query"),
        _case("kjfk-nearest"),
        _case("kjfk-second"),
        _case("kewr-higher-score", facility_id=KEWR),
    ]
    store = _store(tmp_path, cases)
    index = FakeIndex(
        cases,
        {
            "case:query": 1.0,
            "case:kjfk-nearest": 0.91,
            "case:kjfk-second": 0.82,
            "case:kewr-higher-score": 0.99,
        },
    )

    result = find_similar_cases(
        store,
        index,
        CaseSimilarityQuery(
            reference_event_id="event:query",
            facility_id=KJFK,
            limit=3,
        ),
    )

    assert result.status == "ok"
    assert result.candidate_count == 2
    assert [row.event_id for row in result.matches] == [
        "event:kjfk-nearest",
        "event:kjfk-second",
    ]
    assert all(row.facility_ids == (KJFK,) for row in result.matches)
    assert index.anchor_case_id == "case:query"
    assert index.last_candidate_case_ids == (
        "case:kjfk-nearest",
        "case:kjfk-second",
    )


def test_prior_scope_excludes_same_time_and_later_cases(
    tmp_path: Path,
) -> None:
    cases = [
        _case(
            "query",
            start="2026-05-19T12:00:00+00:00",
            end="2026-05-19T14:00:00+00:00",
        ),
        _case("earlier", end="2026-05-19T11:59:59+00:00"),
        _case("same-time", end="2026-05-19T12:00:00+00:00"),
        _case("later", end="2026-05-19T13:00:00+00:00"),
    ]
    store = _store(tmp_path, cases)
    index = FakeIndex(
        cases,
        {
            "case:query": 1.0,
            "case:earlier": 0.7,
            "case:same-time": 0.99,
            "case:later": 0.98,
        },
    )

    result = find_similar_cases(
        store,
        index,
        CaseSimilarityQuery(
            reference_event_id="event:query",
            candidate_scope="prior",
        ),
    )

    assert result.status == "ok"
    assert result.candidate_count == 1
    assert [row.case_id for row in result.matches] == ["case:earlier"]
    assert index.last_candidate_case_ids == ("case:earlier",)


def test_equal_scores_are_tied_by_case_id(tmp_path: Path) -> None:
    cases = [
        _case("query"),
        _case("b"),
        _case("a"),
        _case("c"),
    ]
    store = _store(tmp_path, cases)
    index = FakeIndex(
        cases,
        {
            "case:query": 1.0,
            "case:a": 0.8,
            "case:b": 0.8,
            "case:c": 0.9,
        },
    )

    result = find_similar_cases(
        store,
        index,
        CaseSimilarityQuery(
            reference_event_id="event:query",
            limit=3,
        ),
    )

    assert [row.case_id for row in result.matches] == [
        "case:c",
        "case:a",
        "case:b",
    ]
    assert [row.rank for row in result.matches] == [1, 2, 3]


def test_offset_and_limit_are_applied_after_ranking(
    tmp_path: Path,
) -> None:
    cases = [
        _case("query"),
        _case("a"),
        _case("b"),
        _case("c"),
    ]
    store = _store(tmp_path, cases)
    index = FakeIndex(
        cases,
        {
            "case:query": 1.0,
            "case:a": 0.8,
            "case:b": 0.7,
            "case:c": 0.9,
        },
    )

    result = find_similar_cases(
        store,
        index,
        CaseSimilarityQuery(
            reference_event_id="event:query",
            offset=1,
            limit=1,
        ),
    )

    assert result.candidate_count == 3
    assert [row.case_id for row in result.matches] == ["case:a"]
    assert [row.rank for row in result.matches] == [2]
    assert index.last_n_results == 2


def test_empty_exact_candidate_set_is_insufficient(
    tmp_path: Path,
) -> None:
    cases = [_case("query"), _case("other", facility_id=KEWR)]
    store = _store(tmp_path, cases)
    index = FakeIndex(
        cases,
        {"case:query": 1.0, "case:other": 0.9},
    )

    result = find_similar_cases(
        store,
        index,
        CaseSimilarityQuery(
            reference_event_id="event:query",
            facility_id="urn:aviation-agentic-ai:facility:airport:KLGA",
        ),
    )

    assert result.status == "insufficient"
    assert result.candidate_count == 0
    assert result.matches == ()
    assert index.anchor_case_id == ""
