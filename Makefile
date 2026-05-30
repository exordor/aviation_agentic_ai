.PHONY: validate reports-core reports-main-experiments reports-review thesis-dashboard thesis-all

validate:
	uv run ruff check .
	uv run pytest

reports-core:
	uv run aviation-ai report thesis-claims
	uv run aviation-ai report evaluation-protocol
	uv run aviation-ai report benchmark-v2

reports-main-experiments:
	uv run aviation-ai report retrieval-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name retrieval_ablation_benchmark_v2
	uv run aviation-ai report graph-traversal-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name graph_traversal_ablation_benchmark_v2
	uv run aviation-ai report sufficiency-eval --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json

reports-review:
	uv run aviation-ai report triple-semantic-review --sample-size 100
	uv run aviation-ai report benchmark-llm-review --max-items 60
	uv run aviation-ai report triple-semantic-llm-review --max-items 50
	uv run aviation-ai report graph-path-llm-review --max-items 50
	uv run aviation-ai report answer-generation-benchmark-subset --max-questions 45
	uv run aviation-ai report answer-llm-judge --max-items 60
	uv run aviation-ai report llm-review-consistency
	uv run aviation-ai report benchmark-review-pack --no-write-reviewed
	uv run aviation-ai report benchmark-reviewed-subset
	uv run aviation-ai report answer-eval-subset
	uv run aviation-ai report answer-eval --gold-labels data/cqs/06_phak_ch4_0.answer_eval_subset.gold.json --report-name answer_evaluation_benchmark_subset

thesis-dashboard:
	uv run aviation-ai report thesis-experiment-dashboard

thesis-all: reports-core reports-main-experiments reports-review thesis-dashboard validate
