from aviation_agentic_ai.cross_source.artifacts import read_jsonl


def test_active_automated_regression_has_24_scored_cases_and_four_gs_expectations() -> None:
    rows = read_jsonl("data/evaluation/cross_source/v1/automated_regression_v1.jsonl")

    assert len(rows) == 24
    assert {row["evaluation_status"] for row in rows} == {"automated_regression"}
    assert all(row["expected_abstain"] is False for row in rows)
    assert sum(row.get("expected_alignment") == "Ground Stop" for row in rows) == 4


def test_hard_ambiguity_challenge_covers_resolution_and_quarantine() -> None:
    rows = read_jsonl("data/evaluation/cross_source/v1/hard_ambiguity_v1.jsonl")

    assert len(rows) == 20
    assert sum(row["expected_status"] == "accepted" for row in rows) == 14
    assert sum(row["expected_status"] == "quarantined" for row in rows) == 6
    assert {row["category"] for row in rows} == {
        "ground_stop",
        "glide_slope",
        "neutral",
        "conflicting",
    }
