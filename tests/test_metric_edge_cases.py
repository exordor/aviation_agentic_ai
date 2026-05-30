from aviation_agentic_ai.evaluation.gold import GoldLabel
from aviation_agentic_ai.evaluation.metrics import answer_metrics, retrieval_metrics


def test_retrieval_metrics_empty_hits_for_supported_label() -> None:
    metrics = retrieval_metrics(
        [],
        GoldLabel(
            cq_id="q1",
            source_document="doc",
            source_page=3,
            expected_chunk_ids=("c1",),
            gold_level="chunk",
        ),
    )

    assert metrics["recall_at_5"] is False
    assert metrics["recall_at_10"] is False
    assert metrics["precision_at_5"] == 0.0
    assert metrics["mrr_at_5"] == 0.0
    assert metrics["context_recall"] == 0.0
    assert metrics["first_relevant_rank"] is None
    assert metrics["retrieved_chunk_ids"] == []
    assert metrics["matched_chunk_ids"] == []


def test_retrieval_metrics_empty_hits_for_expected_abstention() -> None:
    metrics = retrieval_metrics(
        [],
        GoldLabel(
            cq_id="q1",
            source_document="doc",
            source_page=-1,
            expected_abstention=True,
            gold_level="no_answer",
        ),
    )

    assert metrics["expected_abstention"] is True
    assert metrics["recall_at_5"] is False
    assert metrics["context_recall"] == 1.0


def test_retrieval_metrics_do_not_match_unset_page_minus_one() -> None:
    metrics = retrieval_metrics(
        [{"chunk_id": "bad", "page": -1, "text": "metadata error"}],
        GoldLabel(
            cq_id="q1",
            source_document="doc",
            source_page=-1,
            gold_level="page",
        ),
    )

    assert metrics["recall_at_5"] is False
    assert metrics["ndcg_at_10"] == 0.0


def test_answer_metrics_empty_answer_without_context() -> None:
    metrics = answer_metrics({"answer": "", "fused_chunks": [], "graph_triples": []})

    assert metrics["answer_present"] is False
    assert metrics["insufficient_evidence_abstention"] is False
    assert metrics["citation_completeness"] is False
    assert metrics["citation_precision"] == 0.0
    assert metrics["citation_recall"] == 0.0


def test_answer_metrics_abstention_without_context_gets_citation_credit() -> None:
    metrics = answer_metrics(
        {
            "answer": "Insufficient evidence in the retrieved context.",
            "fused_chunks": [],
            "graph_triples": [],
        }
    )

    assert metrics["insufficient_evidence_abstention"] is True
    assert metrics["citation_precision"] == 1.0
    assert metrics["citation_recall"] == 1.0
