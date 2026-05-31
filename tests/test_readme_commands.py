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
        "aviation-ai report benchmark-llm-review",
        "aviation-ai report triple-semantic-llm-review",
        "aviation-ai report graph-path-llm-review",
        "aviation-ai report answer-generation-benchmark-subset",
        "aviation-ai report answer-llm-judge",
        "aviation-ai report llm-review-consistency",
        "aviation-ai source ingest-nasa",
        "aviation-ai report nasa-source-discovery",
        "aviation-ai report nasa-source-validation",
        "aviation-ai report nasa-chunking-summary",
        "aviation-ai report ontology-boundary-nasa",
        "aviation-ai report nasa-kg-validation",
        "aviation-ai report nasa-benchmark-summary",
        "aviation-ai report cross-source-ontology-validation",
        "aviation-ai report multisource-retrieval-smoke",
        "aviation-ai report pdf-extraction-comparison",
        "aviation-ai report pdf-backend-chunking-comparison",
    ]:
        assert command in readme
