from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from typing import TypeVar


T = TypeVar("T")


def bootstrap_ci(
    values: Sequence[float | int | bool],
    *,
    confidence: float = 0.95,
    samples: int = 1000,
    seed: int = 17,
) -> dict[str, float | int]:
    """Return a deterministic bootstrap confidence interval for a mean."""
    numeric = [float(value) for value in values]
    if not numeric:
        return {
            "mean": 0.0,
            "lower": 0.0,
            "upper": 0.0,
            "samples": samples,
            "n": 0,
            "confidence": confidence,
            "seed": seed,
        }
    rng = random.Random(seed)
    n = len(numeric)
    means: list[float] = []
    for _ in range(samples):
        means.append(sum(numeric[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    alpha = 1.0 - confidence
    lower_index = max(0, int((alpha / 2.0) * samples))
    upper_index = max(0, min(samples - 1, int((1.0 - alpha / 2.0) * samples) - 1))
    return {
        "mean": round(sum(numeric) / n, 4),
        "lower": round(means[lower_index], 4),
        "upper": round(means[upper_index], 4),
        "samples": samples,
        "n": n,
        "confidence": confidence,
        "seed": seed,
    }


def bootstrap_metric_ci(
    records: Sequence[T],
    metric: Callable[[T], float | int | bool],
    *,
    confidence: float = 0.95,
    samples: int = 1000,
    seed: int = 17,
) -> dict[str, float | int]:
    return bootstrap_ci(
        [metric(record) for record in records],
        confidence=confidence,
        samples=samples,
        seed=seed,
    )
