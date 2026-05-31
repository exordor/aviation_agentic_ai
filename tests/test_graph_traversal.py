from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.chunking.chunks import SourceChunk, write_chunks_jsonl
from aviation_agentic_ai.cli import main
from aviation_agentic_ai.evaluation.gold import GoldLabel
from aviation_agentic_ai.kg.extraction import KGTriple, read_kg_jsonl, write_kg_jsonl
from aviation_agentic_ai.retrieval.graph_traversal import (
    build_kg_graph,
    graph_search_traversal,
    link_question_entities,
    traverse_paths,
)
from aviation_agentic_ai.retrieval.hybrid import (
    graph_search,
    run_retrieval,
    vector_first_guarded_fusion,
)
from aviation_agentic_ai.reporting.graph_traversal_ablation import (
    _record_path_metrics,
    write_graph_traversal_ablation,
)


def _chunk(chunk_id: str, page: int, text: str) -> SourceChunk:
    return SourceChunk(
        chunk_id=chunk_id,
        source_document="doc",
        source_path="data/raw/doc.pdf",
        page=page,
        chunk_index=page,
        char_start=0,
        char_end=len(text),
        text=text,
        strategy="structure_aware",
    )


def _triple(
    triple_id: str,
    subject: str,
    predicate: str,
    obj: str,
    chunk_id: str,
    page: int,
    evidence_text: str,
) -> KGTriple:
    return KGTriple(
        triple_id=triple_id,
        subject=subject,
        predicate=predicate,
        object=obj,
        subject_class=f"Cl_{subject.title().replace(' ', '')}",
        object_class=f"Cl_{obj.title().replace(' ', '')}",
        source_document="doc",
        page=page,
        section=f"page-{page}",
        chunk_id=chunk_id,
        evidence_text=evidence_text,
        model="test",
        confidence=0.9,
        extracted_at="2026-05-18T00:00:00+00:00",
    )


def _write_synthetic_graph(tmp_path: Path) -> tuple[Path, Path]:
    chunks = [
        _chunk("c1", 1, "Angle of attack affects lift."),
        _chunk("c2", 2, "Lift causes induced drag."),
        _chunk("c3", 3, "Lift applies to air density conditions."),
        _chunk("c4", 4, "Induced drag affects performance."),
        _chunk("c5", 5, "Performance affects angle of attack."),
    ]
    triples = [
        _triple("t1", "angle of attack", "affects", "lift", "c1", 1, chunks[0].text),
        _triple("t2", "lift", "causes", "induced drag", "c2", 2, chunks[1].text),
        _triple("t3", "lift", "appliesTo", "air density", "c3", 3, chunks[2].text),
        _triple("t4", "induced drag", "affects", "performance", "c4", 4, chunks[3].text),
        _triple("t5", "performance", "affects", "angle of attack", "c5", 5, chunks[4].text),
    ]
    chunks_path = write_chunks_jsonl(chunks, tmp_path / "chunks.jsonl")
    kg_path = write_kg_jsonl(triples, tmp_path / "kg.jsonl")
    return kg_path, chunks_path


def test_traverse_paths_respects_graph_hops_and_avoids_cycles(tmp_path: Path) -> None:
    kg_path, _chunks_path = _write_synthetic_graph(tmp_path)
    graph = build_kg_graph(read_kg_jsonl(kg_path))

    one_hop = traverse_paths(graph, ["angle of attack"], max_hops=1)
    two_hop = traverse_paths(graph, ["angle of attack"], max_hops=2)
    four_hop = traverse_paths(graph, ["angle of attack"], max_hops=4)

    assert one_hop
    assert all(path.hops == 1 for path in one_hop)
    assert any(path.hops == 2 and path.nodes[-1] == "induced drag" for path in two_hop)
    assert all(len(path.nodes) == len(set(path.nodes)) for path in four_hop)


def test_aliases_link_aoa_to_angle_of_attack(tmp_path: Path) -> None:
    kg_path, _chunks_path = _write_synthetic_graph(tmp_path)
    graph = build_kg_graph(read_kg_jsonl(kg_path))

    seeds = link_question_entities(
        "How does AOA affect induced drag?",
        graph,
        aliases={"angle of attack": ["AOA", "angle-of-attack"]},
    )

    assert "angle of attack" in seeds
    assert graph.graph["last_seed_sources"]["angle of attack"] == "alias"


def test_graph_search_traversal_returns_paths_and_ranked_evidence(tmp_path: Path) -> None:
    kg_path, chunks_path = _write_synthetic_graph(tmp_path)
    aliases_path = tmp_path / "aliases.yaml"
    aliases_path.write_text("angle of attack:\n  - AOA\n", encoding="utf-8")

    hits, triples, paths = graph_search_traversal(
        "How does AOA cause induced drag?",
        kg_path,
        chunks_path,
        top_k=5,
        graph_hops=2,
        aliases_path=aliases_path,
    )

    assert hits
    assert triples
    assert any(path["hops"] == 2 for path in paths)
    path = next(item for item in paths if item["hops"] == 2)
    assert path["path_id"]
    assert path["nodes"]
    assert path["edges"]
    assert path["chunk_ids"] == ["c1", "c2"]
    assert path["pages"] == [1, 2]


def test_run_retrieval_can_use_traversal_graph_method(tmp_path: Path) -> None:
    kg_path, chunks_path = _write_synthetic_graph(tmp_path)

    result = run_retrieval(
        "How does angle of attack cause induced drag?",
        "graph",
        chunks_path,
        kg_path,
        tmp_path / "chroma",
        graph_method="traversal",
        graph_hops=2,
    )

    assert result["graph_method"] == "traversal"
    assert result["graph_paths"]
    assert any(path["hops"] == 2 for path in result["graph_paths"])


def test_lexical_graph_search_still_returns_matching_triples(tmp_path: Path) -> None:
    kg_path, chunks_path = _write_synthetic_graph(tmp_path)

    chunks, triples = graph_search("What affects lift?", kg_path, chunks_path)

    assert chunks[0]["chunk_id"] == "c1"
    assert triples[0]["triple_id"] == "t1"


def test_vector_first_guarded_fusion_preserves_top_vector_hits() -> None:
    vector_hits = [
        {"chunk_id": "v1", "rank": 1, "source": "vector", "text": "Angle of attack affects lift."},
        {"chunk_id": "v2", "rank": 2, "source": "vector", "text": "Lift depends on airflow."},
        {"chunk_id": "v3", "rank": 3, "source": "vector", "text": "Other vector evidence."},
    ]
    graph_hits = [
        {"chunk_id": "g1", "rank": 1, "source": "graph", "text": "Angle of attack affects lift."},
        {"chunk_id": "g2", "rank": 2, "source": "graph", "text": "Graph evidence."},
    ]
    triples = [
        {
            "subject": "angle of attack",
            "predicate": "affects",
            "object": "lift",
            "evidence_text": "Angle of attack affects lift.",
        }
    ]

    fused = vector_first_guarded_fusion(
        "How does angle of attack affect lift?",
        vector_hits,
        graph_hits,
        triples,
        [],
        top_k=4,
    )

    assert [item["chunk_id"] for item in fused[:2]] == ["v1", "v2"]
    assert "g1" in [item["chunk_id"] for item in fused]


def test_graph_traversal_ablation_reports_heuristic_path_metrics(tmp_path: Path) -> None:
    gold_path = tmp_path / "gold.json"
    gold_path.write_text(
        """
{
  "labels": [
    {
      "cq_id": "q1",
      "source_document": "doc",
      "source_page": 1,
      "question": "How does angle of attack affect lift?",
      "question_type": "relation_causal",
      "expected_chunk_ids": ["c1"],
      "evidence_spans": [],
      "key_entities": ["angle of attack", "lift"],
      "answer_key": "Angle of attack affects lift.",
      "gold_level": "chunk",
      "expected_abstention": false
    }
  ]
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    def fake_query_runner(*_args, **_kwargs):
        return {
            "fused_chunks": [{"chunk_id": "c1", "page": 1, "text": "Angle of attack affects lift."}],
            "graph_triples": [
                {
                    "triple_id": "t1",
                    "chunk_id": "c1",
                    "page": 1,
                    "subject": "angle of attack",
                    "predicate": "affects",
                    "object": "lift",
                    "evidence_text": "Angle of attack affects lift.",
                }
            ],
            "graph_paths": [
                {
                    "path_id": "p1",
                    "hops": 1,
                    "chunk_ids": ["c1"],
                    "pages": [1],
                    "nodes": [{"node_id": "angle of attack"}, {"node_id": "lift"}],
                    "edges": [{"predicate": "affects", "chunk_id": "c1", "page": 1}],
                }
            ],
        }

    _json_path, _md_path, result = write_graph_traversal_ablation(
        tmp_path / "boundary.json",
        tmp_path / "chunks.jsonl",
        tmp_path / "kg.jsonl",
        tmp_path / "chroma",
        tmp_path,
        gold_labels_path=gold_path,
        scenarios=(
            {
                "name": "traversal",
                "label": "Traversal",
                "mode": "graph",
                "graph_method": "traversal",
                "graph_hops": 1,
            },
        ),
        query_runner=fake_query_runner,
    )

    paths = result["scenarios"]["traversal"]["aggregate"]["graph_paths"]
    assert paths["path_recall_at_5"] == 1.0
    assert paths["path_precision_at_5"] == 1.0
    assert paths["supporting_path_rate"] == 1.0
    assert paths["irrelevant_path_rate"] == 0.0
    assert paths["requires_model_review"] is True
    assert paths["human_review"] is False


def test_graph_path_metrics_handles_missing_source_page() -> None:
    gold = GoldLabel(
        cq_id="q1",
        source_document="doc",
        source_page=None,
        question="How does lift affect drag?",
        expected_chunk_ids=(),
        key_entities=("lift",),
        gold_level="chunk",
    )

    metrics = _record_path_metrics(
        "How does lift affect drag?",
        {
            "graph_paths": [
                {
                    "path_id": "p1",
                    "hops": 1,
                    "pages": [1],
                    "chunk_ids": [],
                    "nodes": [{"label": "lift"}],
                    "edges": [],
                }
            ],
            "graph_triples": [],
        },
        gold,
    )

    assert metrics["path_count"] == 1
    assert metrics["path_recall_at_5"] == 1.0


def test_cli_report_graph_traversal_ablation_uses_mocked_writer(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli_report_evaluation

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "graph_traversal_ablation.json"
        md_path = tmp_path / "graph_traversal_ablation.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"scenarios_total": 7, "questions_total": 2}}

    monkeypatch.setattr(
        cli_report_evaluation,
        "write_graph_traversal_ablation",
        fake_writer,
    )

    result = CliRunner().invoke(
        main,
        [
            "report",
            "graph-traversal-ablation",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Evaluated 7 graph traversal scenarios" in result.output
