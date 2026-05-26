import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.evidence_cards import (
    build_evidence_cards,
    write_evidence_cards,
)


def _chunk(
    chunk_id: str,
    *,
    page: int = 0,
    rank: int = 1,
    source: str = "vector",
    text: str = "Angle of attack affects lift.",
) -> dict:
    return {
        "chunk_id": chunk_id,
        "page": page,
        "rank": rank,
        "source": source,
        "text": text,
    }


def _triple(
    triple_id: str,
    *,
    chunk_id: str = "doc-p00-c00",
    page: int = 0,
    subject: str = "angle of attack",
    predicate: str = "affects",
    object_: str = "lift",
    evidence_text: str = "Angle of attack affects lift.",
) -> dict:
    return {
        "triple_id": triple_id,
        "chunk_id": chunk_id,
        "page": page,
        "rank": 1,
        "subject": subject,
        "predicate": predicate,
        "object": object_,
        "evidence_text": evidence_text,
    }


def _metrics(
    *,
    hit: bool,
    first_rank: int | None,
    pages: list[int],
    chunks: list[str],
    kg_covered: bool = False,
    covered_entities: list[str] | None = None,
    citation_complete: bool = True,
    abstained: bool = False,
) -> dict:
    return {
        "retrieval": {
            "recall_at_5": hit,
            "first_relevant_rank": first_rank,
            "retrieved_source_pages": pages,
            "retrieved_chunk_ids": chunks,
        },
        "kg_evidence": {
            "evidence_coverage": kg_covered,
            "key_entity_coverage": kg_covered,
            "key_entities_covered": covered_entities or [],
        },
        "llm_answer": {
            "citation_completeness": citation_complete,
            "valid_citations": chunks[:1] if citation_complete else [],
            "insufficient_evidence_abstention": abstained,
            "answer_present": True,
        },
    }


def _mode_result(
    *,
    chunks: list[dict],
    triples: list[dict] | None = None,
    hit: bool | None = None,
    first_rank: int | None = None,
    kg_covered: bool = False,
    covered_entities: list[str] | None = None,
    citation_complete: bool = True,
    abstained: bool = False,
) -> dict:
    inferred_hit = bool(chunks and chunks[0]["chunk_id"] == "doc-p00-c00") if hit is None else hit
    inferred_rank = 1 if inferred_hit and first_rank is None else first_rank
    return {
        "fused_chunks": chunks,
        "graph_triples": triples or [],
        "answer": "Angle of attack affects lift. Citations: doc-p00-c00"
        if citation_complete
        else "Angle of attack affects lift.",
        "metrics": _metrics(
            hit=inferred_hit,
            first_rank=inferred_rank,
            pages=[chunk["page"] for chunk in chunks[:5]],
            chunks=[chunk["chunk_id"] for chunk in chunks[:5]],
            kg_covered=kg_covered,
            covered_entities=covered_entities,
            citation_complete=citation_complete,
            abstained=abstained,
        ),
    }


def _experiment(
    *,
    vector: dict,
    graph: dict,
    hybrid: dict,
    gold: dict | None = None,
) -> dict:
    return {
        "metadata": {"run_manifest": {"run_id": "run-1"}},
        "records": [
            {
                "cq_id": "CQ_012",
                "question": "How does angle of attack affect lift?",
                "source_page": 0,
                "key_entities": ["angle of attack", "lift"],
                "gold": gold
                or {
                    "cq_id": "CQ_012",
                    "question": "How does angle of attack affect lift?",
                    "source_document": "doc",
                    "source_page": 0,
                    "expected_chunk_ids": ["doc-p00-c00"],
                    "evidence_spans": [
                        {"page": 0, "text": "Angle of attack affects lift."}
                    ],
                    "key_entities": ["angle of attack", "lift"],
                    "gold_level": "span",
                    "expected_abstention": False,
                },
                "results": {
                    "vector": vector,
                    "graph": graph,
                    "hybrid": hybrid,
                },
            }
        ],
    }


def _single_card(experiment: dict) -> dict:
    result = build_evidence_cards(experiment)
    assert result["metadata"]["cards_total"] == 1
    return result["cards"][0]


def test_evidence_card_success_includes_gold_and_layered_retrieval_summary() -> None:
    useful = _triple("t1")
    card = _single_card(
        _experiment(
            vector=_mode_result(chunks=[_chunk("doc-p00-c00")]),
            graph=_mode_result(
                chunks=[_chunk("doc-p00-c00", source="graph")],
                triples=[useful],
                kg_covered=True,
                covered_entities=["angle of attack", "lift"],
            ),
            hybrid=_mode_result(
                chunks=[_chunk("doc-p00-c00", source="graph+vector")],
                triples=[useful],
                kg_covered=True,
                covered_entities=["angle of attack", "lift"],
            ),
        )
    )

    assert card["failure_category"] == "success"
    assert card["gold_evidence"]["expected_page"] == 0
    assert card["gold_evidence"]["expected_chunk_ids"] == ["doc-p00-c00"]
    assert card["vector_retrieval"]["hit"] is True
    assert card["vector_retrieval"]["first_relevant_rank"] == 1
    assert card["graph_retrieval"]["entity_coverage"]["covered"] is True
    assert card["graph_retrieval"]["useful_triples"][0]["triple_id"] == "t1"
    assert card["hybrid_retrieval"]["graph_effect"] == "neutral"
    assert card["hybrid_retrieval"]["citation_status"]["citation_completeness"] is True


def test_evidence_card_marks_retrieval_miss_when_no_mode_recovers_gold() -> None:
    miss = _mode_result(chunks=[_chunk("wrong", page=3, text="unrelated")], hit=False)

    card = _single_card(_experiment(vector=miss, graph=miss, hybrid=miss))

    assert card["failure_category"] == "retrieval miss"
    assert "no retrieval mode recovered the gold evidence" in card["failure_reasons"][0]


def test_evidence_card_marks_chunk_boundary_problem_for_right_page_wrong_span() -> None:
    boundary = _mode_result(
        chunks=[_chunk("wrong", page=0, text="same page but not the expected span")],
        hit=False,
    )

    card = _single_card(_experiment(vector=boundary, graph=boundary, hybrid=boundary))

    assert card["failure_category"] == "chunk boundary problem"


def test_evidence_card_marks_kg_sparsity_when_graph_has_no_useful_evidence() -> None:
    empty_graph = _mode_result(
        chunks=[_chunk("doc-p00-c00")],
        triples=[],
        hit=True,
        kg_covered=False,
    )

    card = _single_card(
        _experiment(
            vector=_mode_result(chunks=[_chunk("doc-p00-c00")]),
            graph=empty_graph,
            hybrid=_mode_result(chunks=[_chunk("doc-p00-c00")]),
        )
    )

    assert card["failure_category"] == "KG sparsity"


def test_evidence_card_marks_graph_noise_when_noisy_triples_dominate() -> None:
    useful = _triple("t-useful")
    noisy_1 = _triple(
        "t-noisy-1",
        chunk_id="wrong-1",
        page=3,
        subject="weather",
        object_="cloud",
        evidence_text="Weather details.",
    )
    noisy_2 = _triple(
        "t-noisy-2",
        chunk_id="wrong-2",
        page=4,
        subject="runway",
        object_="light",
        evidence_text="Runway lighting details.",
    )

    card = _single_card(
        _experiment(
            vector=_mode_result(chunks=[_chunk("doc-p00-c00")]),
            graph=_mode_result(
                chunks=[_chunk("doc-p00-c00", source="graph")],
                triples=[useful, noisy_1, noisy_2],
                kg_covered=True,
                covered_entities=["lift"],
            ),
            hybrid=_mode_result(
                chunks=[_chunk("doc-p00-c00")],
                triples=[useful, noisy_1, noisy_2],
                kg_covered=True,
            ),
        )
    )

    assert card["failure_category"] == "graph noise"
    assert len(card["graph_retrieval"]["noisy_triples"]) == 2


def test_evidence_card_marks_hybrid_fusion_dilution_when_vector_hit_is_lost() -> None:
    card = _single_card(
        _experiment(
            vector=_mode_result(chunks=[_chunk("doc-p00-c00")], hit=True, first_rank=1),
            graph=_mode_result(chunks=[_chunk("wrong", page=3)], hit=False),
            hybrid=_mode_result(chunks=[_chunk("wrong", page=3)], hit=False),
        )
    )

    assert card["failure_category"] == "hybrid fusion dilution"
    assert card["hybrid_retrieval"]["graph_effect"] == "hurt"


def test_evidence_card_marks_citation_mismatch_for_uncited_gold_hit() -> None:
    useful = _triple("t1")
    card = _single_card(
        _experiment(
            vector=_mode_result(chunks=[_chunk("doc-p00-c00")]),
            graph=_mode_result(
                chunks=[_chunk("doc-p00-c00")],
                triples=[useful],
                kg_covered=True,
            ),
            hybrid=_mode_result(
                chunks=[_chunk("doc-p00-c00")],
                triples=[useful],
                kg_covered=True,
                citation_complete=False,
            ),
        )
    )

    assert card["failure_category"] == "citation mismatch"


def test_evidence_card_marks_abstention_failure_for_no_answer_gold() -> None:
    gold = {
        "cq_id": "CQ_013",
        "question": "What is the current METAR?",
        "source_document": "doc",
        "source_page": -1,
        "expected_chunk_ids": [],
        "evidence_spans": [],
        "key_entities": ["METAR"],
        "gold_level": "no_answer",
        "expected_abstention": True,
    }
    card = _single_card(
        _experiment(
            vector=_mode_result(chunks=[], hit=False),
            graph=_mode_result(chunks=[], hit=False),
            hybrid=_mode_result(chunks=[], hit=False, citation_complete=False, abstained=False),
            gold=gold,
        )
    )

    assert card["failure_category"] == "abstention failure"


def test_write_evidence_cards_and_cli_generate_json_and_markdown(tmp_path: Path) -> None:
    report_path = tmp_path / "hybrid.json"
    report_path.write_text(
        json.dumps(
            _experiment(
                vector=_mode_result(chunks=[_chunk("doc-p00-c00")]),
                graph=_mode_result(chunks=[_chunk("doc-p00-c00")], triples=[_triple("t1")]),
                hybrid=_mode_result(chunks=[_chunk("doc-p00-c00")], triples=[_triple("t1")]),
            )
        )
        + "\n",
        encoding="utf-8",
    )

    json_path, md_path, result = write_evidence_cards(tmp_path, hybrid_report_path=report_path)

    assert json_path.exists()
    assert md_path.exists()
    assert result["cards"][0]["cq_id"] == "CQ_012"
    markdown = md_path.read_text(encoding="utf-8")
    assert "## Per-Question Evidence Cards" in markdown
    assert "Failure category: success" in markdown

    cli_result = CliRunner().invoke(
        main,
        [
            "report",
            "evidence-cards",
            "--hybrid-report",
            str(report_path),
            "--output-dir",
            str(tmp_path / "cli"),
        ],
    )

    assert cli_result.exit_code == 0, cli_result.output
    assert "Wrote" in cli_result.output
