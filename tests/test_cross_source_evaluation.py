from types import SimpleNamespace

from aviation_agentic_ai.cross_source.contracts import (
    AnswerCitation,
    CrossSourceAnswer,
    EvidenceLayer,
    EvidenceStatement,
)
from aviation_agentic_ai.cross_source.evaluation.benchmark import evaluate_benchmark
from aviation_agentic_ai.cross_source.evaluation.mainline import evaluate_answer_baselines


def test_automated_regression_rows_are_scored_as_policy_checks(monkeypatch) -> None:
    answer = SimpleNamespace(
        abstain=False,
        model_dump=lambda mode: {
            "abstain": False,
            "source_assertions": [],
            "observation_evidence": [],
            "forecast_evidence": [],
            "system_associations": [],
            "citations": [],
        },
    )
    monkeypatch.setattr(
        "aviation_agentic_ai.cross_source.evaluation.benchmark.answer_from_build",
        lambda *args, **kwargs: answer,
    )
    monkeypatch.setattr(
        "aviation_agentic_ai.cross_source.evaluation.benchmark.AnswerEvidenceCritic.validate",
        lambda *args, **kwargs: [],
    )
    build = SimpleNamespace(config={"snapshot_set_id": "snapshot:test"})

    report = evaluate_benchmark(
        [
            {
                "case_id": "case-1",
                "source_id": "adv:1",
                "question": "question",
                "evaluation_status": "automated_regression",
                "expected_abstain": False,
            }
        ],
        build=build,
    )

    assert report["summary"]["scored_cases"] == 1
    assert report["summary"]["unscored_cases"] == 0
    assert report["summary"]["scored_abstain_cases"] == 1
    assert report["summary"]["expected_abstain_accuracy"] == 1


def test_matched_baselines_report_required_layer_coverage(monkeypatch) -> None:
    statements = {
        layer: EvidenceStatement(
            layer=layer,
            text=f"{layer.value} statement",
            source_id=f"source:{layer.value}",
            evidence_text=f"{layer.value} evidence",
        )
        for layer in EvidenceLayer
    }
    full = CrossSourceAnswer(
        question="question",
        source_assertions=[statements[EvidenceLayer.SOURCE_ASSERTION]],
        observation_evidence=[statements[EvidenceLayer.OBSERVATION]],
        forecast_evidence=[statements[EvidenceLayer.FORECAST]],
        system_associations=[statements[EvidenceLayer.SYSTEM_ASSOCIATION]],
        citations=[
            AnswerCitation(
                source_id=statement.source_id,
                evidence_text=statement.evidence_text,
                layer=statement.layer,
            )
            for statement in statements.values()
        ],
        abstain=False,
        rationale="full",
        snapshot_set_id="snapshot:test",
        trace_id="trace:test",
    )
    monkeypatch.setattr(
        "aviation_agentic_ai.cross_source.evaluation.mainline.answer_from_build",
        lambda *args, **kwargs: full,
    )
    build = SimpleNamespace(config={"snapshot_set_id": "snapshot:test"})

    report = evaluate_answer_baselines(
        [
            {
                "case_id": "case-1",
                "source_id": "adv:1",
                "question": "question",
                "evaluation_status": "automated_regression",
                "expected_abstain": False,
            }
        ],
        build=build,
    )

    summaries = report["systems"]
    assert summaries["B0_source_only"]["required_evidence_layer_coverage"] == 0.25
    assert summaries["B1_linked_text"]["required_evidence_layer_coverage"] == 0.75
    assert summaries["S_cross_source_kg"]["required_evidence_layer_coverage"] == 1.0
