from __future__ import annotations

from pathlib import Path


def test_readme_lists_thesis_ready_report_commands() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for command in [
        "aviation-ai cqs validate-benchmark",
        "aviation-ai report benchmark-v2",
        "aviation-ai report graph-traversal-ablation",
        "aviation-ai report sufficiency-eval",
        "aviation-ai report triple-semantic-review",
    ]:
        assert command in readme
