# Thesis Hardening Iteration Plan

## P0 - Claim And Workflow Consistency

- Update dashboard and final report language so benchmark v2 is provisional internal evidence pending review.
- Split `automated_consistency_passed`, `claim_readiness_passed`, and `all_passed`.
- Surface robustness safety metrics beside sufficiency metrics.
- Acceptance: no thesis-facing report treats manual-pending evidence as completed review.

## P1 - Benchmark Reviewed Subset

- Generate `data/cqs/06_phak_ch4_0.benchmark_v2.reviewed_subset.gold.json`.
- Selection: all `concept_definition`, all `relation_causal`, all `cross_page`, and all `insufficient_evidence` labels, for exactly 60 labels.
- Write `reports/stages/benchmark_reviewed_subset_summary.md/json`.
- Acceptance: every label has pending project-author review metadata and `external_aviation_expert_certified=false`.

## P2 - Triple Semantic Review Completion Path

- Preserve pending annotations unless explicit review fields are supplied.
- Report `reviewed_total`, `needs_review_total`, and only compute correctness/support rates when `reviewed_total > 0`.
- Add human review instructions to Markdown.
- Acceptance: no semantic correctness rate exists for an all-pending sample.

## P3 - Answer-Evaluation Subset

- Generate `data/cqs/06_phak_ch4_0.answer_eval_subset.gold.json`.
- Evaluate with `uv run aviation-ai report answer-eval --gold-labels data/cqs/06_phak_ch4_0.answer_eval_subset.gold.json --report-name answer_evaluation_benchmark_subset`.
- Keep deterministic heuristic labels visible.
- Acceptance: answer subset status is visible in the dashboard and final report.

## P4 - Confidence Intervals And Graph Interpretation

- Add missing CI metadata fields: `n`, `confidence`, `seed`, and `samples`.
- Show retrieval, graph traversal, and sufficiency CIs in Markdown/dashboard.
- Keep path metrics labelled heuristic and diagnostic.
- Acceptance: no graph traversal row implies Recall superiority without retrieval metrics.

## P5 - Safety Boundary Hardening

- Add a live-query pre-generation advisory-boundary gate.
- Apply sufficiency gating to deterministic robustness answers.
- Broaden risk triggers and boundary-violation phrases for operational prompts.
- Acceptance: unsupported operational robustness cases abstain or are reported as unresolved.

## P6 - Final Report Synchronization

- Regenerate dashboard and deterministic final report from updated artifacts.
- Keep limitations organized by RQ.
- Acceptance: final report states no external aviation expert certification, no operational flight readiness, no mixed overall score, and no universal GraphRAG Recall@k claim.

## Verification Commands

- `uv run pytest tests/test_review_reporting.py tests/test_review_pack_and_triples.py`
- `uv run pytest tests/test_thesis_dashboard.py tests/test_project_report.py`
- `uv run pytest tests/test_sufficiency_eval.py tests/test_graph_traversal.py`
- `uv run pytest tests/test_hybrid_cli.py tests/test_readme_commands.py`
- `make validate`
- `make reports-core`
- `make reports-main-experiments`
- `make reports-review`
- `make thesis-dashboard`
- `uv run aviation-ai report project --no-ai`
