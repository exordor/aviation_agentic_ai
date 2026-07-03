SNAPSHOT_DATE ?= 2026-06-01
PAPER ?=
SLUG ?=

.PHONY: validate reports-core reports-main-experiments reports-review thesis-all airm-o paper-inspect sync-windows sync-windows-dry-run sync-windows-list

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

airm-o:
	uv run python scripts/collect_airm_o_pipeline.py --snapshot-date $(SNAPSHOT_DATE)

paper-inspect:
	@test -n "$(PAPER)" || (echo "Usage: make paper-inspect PAPER=data/papers/example.pdf [SLUG=example_paper]" >&2; exit 2)
	scripts/inspect_paper_pdf.sh "$(PAPER)" "$(SLUG)"

sync-windows:
	uv run python scripts/sync_windows_workspace.py

sync-windows-dry-run:
	uv run python scripts/sync_windows_workspace.py --dry-run

sync-windows-list:
	uv run python scripts/sync_windows_workspace.py --list-only

thesis-all: reports-core reports-main-experiments reports-review validate
