from aviation_agentic_ai.evaluation.bootstrap_ci import bootstrap_ci, bootstrap_metric_ci


def test_bootstrap_ci_is_deterministic_for_known_values() -> None:
    ci = bootstrap_ci([1.0, 0.0, 1.0, 1.0, 0.0], seed=42)

    assert ci == {
        "mean": 0.6,
        "lower": 0.2,
        "upper": 1.0,
        "samples": 1000,
        "n": 5,
        "confidence": 0.95,
        "seed": 42,
    }


def test_bootstrap_ci_empty_input_reports_n_zero() -> None:
    ci = bootstrap_ci([], seed=42)

    assert ci["n"] == 0
    assert ci["mean"] == 0.0
    assert ci["lower"] == 0.0
    assert ci["upper"] == 0.0


def test_bootstrap_ci_single_sample_has_valid_bounds() -> None:
    ci = bootstrap_ci([1.0], seed=42, samples=1)

    assert ci["n"] == 1
    assert ci["lower"] == 1.0
    assert ci["upper"] == 1.0


def test_bootstrap_metric_ci_maps_records_before_sampling() -> None:
    ci = bootstrap_metric_ci(
        [{"hit": True}, {"hit": False}, {"hit": True}],
        lambda record: record["hit"],
        seed=7,
        samples=100,
    )

    assert ci["mean"] == 0.6667
    assert ci["n"] == 3
    assert ci["seed"] == 7
