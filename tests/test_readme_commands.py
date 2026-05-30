from __future__ import annotations

from pathlib import Path


def test_readme_lists_thesis_ready_report_commands() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for command in [
        "aviation-ai cqs validate-benchmark",
        "aviation-ai report benchmark-v2",
        "aviation-ai report evaluation-protocol",
        "aviation-ai report graph-traversal-ablation",
        "aviation-ai report sufficiency-eval",
        "aviation-ai report triple-semantic-review",
        "aviation-ai report chunking-comparison-v2",
        "aviation-ai report chunking-comparison-v2 --evaluation-mode fixed_context_budget",
        "aviation-ai report chunking-implementation-audit",
        "aviation-ai report chunking-topk-sensitivity-v2",
        "aviation-ai report chunking-category-analysis-v2",
    ]:
        assert command in readme
