# Adversarial Finding Verification - 2026-05-30

Input report: `reports/reviews/adversarial-review-2026-05-30.md`

This file records a current-state verification pass. The adversarial report was
used as input, but each item was checked against the repository before changes
were made. The hardening iteration fixes reliability, claim-clarity, and
test-coverage items that were still valid and low risk. Larger refactors are left as a
verified backlog rather than silently mixed into this iteration.

## Fixed Or Mitigated In This Iteration

| ID | Verification | Action |
| --- | --- | --- |
| C1 | Still valid. `_llm_triples_for_chunk` could abort an extraction run on malformed JSON or provider failure; `generate_grounded_answer` could abort answer generation on LLM invoke failure. | `extract_kg_file` now records per-chunk LLM extraction errors and continues with remaining chunks. `generate_grounded_answer` now returns an explicit non-answer fallback when the LLM invocation fails. |
| C2 | Still valid. Lexical `graph_search` accepted `graph_hops` and discarded it. | Removed the lexical `graph_search` hop argument and added `graph_hops_requested`, `graph_hops_effective`, and a lexical-hop note to `run_retrieval`. |
| C3 | Partly valid. `read_kg_jsonl` did not swallow errors, but it raised raw JSON/dataclass exceptions without file and line context. | Added `KGReadError` with KG path and line number for malformed JSON or invalid record shape. |
| C4 | Still valid as a thesis-defense risk. Sufficiency benchmark mode used expected chunks/spans from gold labels. | Sufficiency decisions now label `gold_aided_benchmark` vs `evidence_only` mode, and the report emits separate evidence-only diagnostic metrics. Documentation now warns that these modes are not equivalent. |
| I2 | Still valid. Bootstrap helpers had no direct tests. | Added deterministic direct tests for `bootstrap_ci` and `bootstrap_metric_ci`, including empty input. |
| I3 | Still valid. Cost/latency helpers had no direct tests. | Added tests for missing paths, file and directory sizes, rounded latency, relative paths, and token usage. |
| I4 | Partly valid. `run_retrieval` lacked an integration-style lexical hybrid test and the weak-overlap guarded fusion branch was not covered. | Added tests for lexical hybrid `run_retrieval`, lexical hop transparency, and weak-overlap `vector_first_guarded_fusion`. Direct `run_query` with real LLM remains intentionally out of scope for offline tests. |
| I5 | Still valid. `get_llm` had no return annotation. | Added a `BaseChatModel` return annotation behind `TYPE_CHECKING` so optional LangChain imports remain lazy. |
| I1 | Still valid. Retrieval, graph traversal, chunking, and source-scope modules carried independent tokenizer/stopword logic. | Added `aviation_agentic_ai.utils.text` with shared normalization, token regex, stopwords, and tokenization helpers. Existing local wrappers now delegate to the shared utility. |
| I6 | Still partly valid. `.env` loading was scattered across LLM provider, evaluation metadata, web readiness, and ontology generation. | Added `config.load_environment()` as the single dotenv loading entry point and updated LLM access/reporting paths to use it. Provider selection remains explicit at call sites. |
| I7 | Still valid. `cli.py` remains a large Click file with many direct subsystem imports. | Completed the report-command extraction path by moving `web serve` into `aviation_agentic_ai.cli_web`, `chunk build` into `aviation_agentic_ai.cli_chunk`, `index build` into `aviation_agentic_ai.cli_index`, the top-level `query` command into `aviation_agentic_ai.cli_query`, the `kg extract`/`kg validate` group into `aviation_agentic_ai.cli_kg`, top-level `cqs` gold-label utilities into `aviation_agentic_ai.cli_cqs`, the ontology command group into `aviation_agentic_ai.cli_ontology`, web-demo report commands into `aviation_agentic_ai.cli_report_web`, chunking report commands into `aviation_agentic_ai.cli_report_chunking`, LLM-review report commands into `aviation_agentic_ai.cli_report_llm`, benchmark report commands into `aviation_agentic_ai.cli_report_benchmark`, stage/admin report commands into `aviation_agentic_ai.cli_report_stage`, thesis/final-document report commands into `aviation_agentic_ai.cli_report_thesis`, and retrieval/evaluation report commands into `aviation_agentic_ai.cli_report_evaluation`, registering the commands from `cli.py` without changing public command surfaces. |
| I8 | Still valid as a broader maintenance concern. Several modules duplicated JSON report loading/writing and lightweight normalization. | Added `aviation_agentic_ai.reporting.io` and `aviation_agentic_ai.utils.io`; migrated the evidence-card, evidence-evaluation, answer-evaluation, sufficiency, GraphRAG review, benchmark-review-pack, KG-comparison, thesis-dashboard helpers, sorted report JSON writers, stage/admin overnight, generation-run, review-progress JSON paths, project-report JSON evidence loading, triple semantic annotation loading, robustness-case JSON loading, and non-reporting report-style JSON writers for gold drafts, query results, KG validation, ontology stats/evaluation, and source-scope outputs. Chunk JSONL loading now raises `ChunkReadError` with file and line context, and gold-label loading now raises `GoldLabelReadError` with JSONL line or label-index context, matching the KG reader hardening pattern. Missing-file/non-object/list-input behavior and JSON formatting are preserved. |
| M3 | Still valid as wording polish. Retrieval-only ablation used `provider: none`, which could read like a missing setting rather than intentional no-LLM execution. | Retrieval ablation manifests now record `provider: not_used_retrieval_only` and an explicit usage note that no generation or LLM judge is used. |
| M1 | Still valid. Chroma collection deletion swallowed every exception. | Reset now suppresses only missing/not-found collection errors and re-raises unexpected failures. |
| M2 | Still valid. `_extract_json_payload` had no direct tests. | Added direct tests for fenced JSON, bare JSON, embedded JSON, and empty input. |
| M4 | Still valid. Lexical graph no-result behavior was not tested. | Added a no-overlap `graph_search` test. |
| M5 | Still valid. Retrieval and answer metrics had missing empty-input tests. | Added explicit empty-input retrieval and answer metric tests. |
| M6 | Still valid. Evaluation protocol tests were mostly structural. | Added value-level assertions for the review/certification limitation language in `EVIDENCE_GAPS`. |
| M7 | Still valid. Empty KG JSONL round-trip was not tested. | Added `write_kg_jsonl([])` / `read_kg_jsonl` round-trip coverage. |

## Verified Backlog

| ID | Current assessment | Reason deferred |
| --- | --- | --- |
| I7 remainder | Mostly addressed for current report-command scope. `cli.py` is now a small registration module rather than the 2000-line command implementation file cited by the review. | Future CLI additions should follow the existing subsystem registration pattern; no broad behavior refactor is mixed into this iteration. |
| I8 remainder | Still partly valid, but narrower. A smaller set of custom readers/writers remains where parsing semantics are more domain-specific, such as benchmark chunk validation JSONL ingestion, prompt formatting, or compatibility wrappers that already delegate to shared I/O. | Sorted writers, low-risk unsorted stage/admin writers, object/list report readers, report-style non-reporting JSON writers, chunk JSONL error-context handling, and gold-label loading error-context handling have been migrated/hardened in batches; continue only where behavior can be preserved exactly. |

## Verification Commands

- `uv run ruff check .`
- `uv run pytest tests/test_kg_extraction.py tests/test_hybrid_retrieval.py tests/test_sufficiency_eval.py tests/test_bootstrap_ci.py tests/test_cost_latency.py tests/test_metric_edge_cases.py tests/test_graph_traversal.py`
- `uv run pytest tests/test_text_utils.py tests/test_experiment_protocol.py tests/test_experimental_expansion.py tests/test_evaluation_protocol_metrics.py tests/test_chunking.py`
- `uv run pytest tests/test_reporting_io.py tests/test_evidence_cards.py tests/test_evidence_eval.py tests/test_sufficiency_eval.py tests/test_graphrag_review.py tests/test_thesis_dashboard.py tests/test_review_pack_and_triples.py tests/test_experimental_expansion.py tests/test_final_evaluation.py`
- `uv run pytest tests/test_chunking_comparison.py tests/test_hybrid_rag_reporting.py tests/test_graph_traversal.py tests/test_llm_review_reports.py tests/test_project_report.py tests/test_web_demo.py tests/test_generation_run_reporting.py tests/test_overnight_reporting.py tests/test_report_hygiene.py`
- `uv run pytest tests/test_web_demo.py::test_cli_web_serve_uses_mocked_server tests/test_web_demo.py::test_cli_report_web_demo_readiness_uses_mocked_writer tests/test_web_demo.py::test_cli_report_web_demo_smoke_uses_mocked_writer`
- `uv run aviation-ai web --help`
- `uv run aviation-ai web serve --help`
- `uv run pytest tests/test_hybrid_cli.py::test_cli_chunk_build_uses_default_command_shape tests/test_hybrid_cli.py::test_cli_index_build_uses_mocked_builder tests/test_hybrid_cli.py::test_cli_query_uses_mocked_runner`
- `uv run aviation-ai chunk --help`
- `uv run aviation-ai chunk build --help`
- `uv run aviation-ai index --help`
- `uv run aviation-ai index build --help`
- `uv run pytest tests/test_hybrid_cli.py::test_cli_query_uses_mocked_runner`
- `uv run aviation-ai query --help`
- `uv run pytest tests/test_hybrid_cli.py::test_cli_kg_extract_uses_configured_token_budget tests/test_hybrid_cli.py::test_cli_kg_extract_max_tokens_override tests/test_hybrid_cli.py::test_cli_kg_extract_can_write_ttl_export tests/test_hybrid_cli.py::test_cli_kg_validate_passes_report_name`
- `uv run aviation-ai kg --help`
- `uv run aviation-ai kg extract --help`
- `uv run aviation-ai kg validate --help`
- `uv run pytest tests/test_hybrid_cli.py::test_cli_cqs_gold_draft_uses_mocked_builder tests/test_hybrid_cli.py::test_cli_cqs_validate_benchmark_uses_mocked_validator`
- `uv run aviation-ai cqs --help`
- `uv run aviation-ai cqs gold-draft --help`
- `uv run aviation-ai cqs validate-benchmark --help`
- `uv run pytest tests/test_ontology_evaluation.py::test_cli_ontology_evaluate_no_ai_review tests/test_ontology_evaluation.py::test_cli_ontology_evaluate_defaults_to_deterministic_report_name tests/test_ontology_evaluation.py::test_cli_ontology_validate_cqs`
- `uv run aviation-ai ontology --help`
- `uv run aviation-ai ontology evaluate --help`
- `uv run aviation-ai ontology validate-cqs --help`
- `uv run pytest tests/test_web_demo.py::test_cli_report_web_demo_readiness_uses_mocked_writer tests/test_web_demo.py::test_cli_report_web_demo_smoke_uses_mocked_writer`
- `uv run aviation-ai report web-demo-readiness --help`
- `uv run aviation-ai report web-demo-smoke --help`
- `uv run pytest tests/test_hybrid_cli.py::test_cli_report_chunking_comparison_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_chunking_comparison_v2_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_chunking_implementation_audit_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_chunking_topk_and_category_use_mocked_writers`
- `uv run aviation-ai report chunking-comparison --help`
- `uv run aviation-ai report chunking-comparison-v2 --help`
- `uv run aviation-ai report chunking-implementation-audit --help`
- `uv run aviation-ai report chunking-topk-sensitivity-v2 --help`
- `uv run aviation-ai report chunking-category-analysis-v2 --help`
- `uv run pytest tests/test_hybrid_cli.py::test_cli_llm_review_commands_use_mocked_writers`
- `uv run aviation-ai report benchmark-llm-review --help`
- `uv run aviation-ai report triple-semantic-llm-review --help`
- `uv run aviation-ai report graph-path-llm-review --help`
- `uv run aviation-ai report answer-generation-benchmark-subset --help`
- `uv run aviation-ai report answer-llm-judge --help`
- `uv run aviation-ai report llm-review-consistency --help`
- `uv run pytest tests/test_hybrid_cli.py::test_cli_report_benchmark_v2_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_benchmark_review_pack_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_benchmark_reviewed_subset_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_answer_eval_subset_uses_mocked_writer`
- `uv run aviation-ai report benchmark-v2 --help`
- `uv run aviation-ai report benchmark-review-pack --help`
- `uv run aviation-ai report benchmark-reviewed-subset --help`
- `uv run aviation-ai report answer-eval-subset --help`
- `uv run pytest tests/test_overnight_reporting.py::test_cli_report_stages_writes_available_stage_reports tests/test_review_reporting.py::test_cli_report_reviews_writes_progress tests/test_generation_run_reporting.py::test_cli_report_generation_runs tests/test_overnight_reporting.py::test_cli_report_overnight_writes_summary tests/test_report_hygiene.py::test_cli_report_hygiene_dry_run_does_not_move_files tests/test_report_hygiene.py::test_cli_report_hygiene_apply_writes_index`
- `uv run aviation-ai report stages --help`
- `uv run aviation-ai report reviews --help`
- `uv run aviation-ai report generation-runs --help`
- `uv run aviation-ai report overnight --help`
- `uv run aviation-ai report hygiene --help`
- `uv run pytest tests/test_project_report.py::test_cli_report_project_no_ai_writes_outputs tests/test_project_report.py::test_cli_report_project_ai_uses_writer_flag tests/test_thesis_claims.py::test_cli_report_thesis_claims_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_evaluation_protocol_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_thesis_dashboard_uses_mocked_writer tests/test_academic_outputs.py::test_cli_academic_outputs_write_expected_files`
- `uv run aviation-ai report project --help`
- `uv run aviation-ai report thesis-claims --help`
- `uv run aviation-ai report evaluation-protocol --help`
- `uv run aviation-ai report thesis-experiment-dashboard --help`
- `uv run aviation-ai report academic-paper --help`
- `uv run aviation-ai report defense-notes --help`
- `uv run aviation-ai report defense-deck-outline --help`
- `uv run aviation-ai report visual-assets --help`
- `uv run pytest tests/test_hybrid_cli.py::test_cli_report_hybrid_rag_passes_report_name tests/test_hybrid_cli.py::test_cli_report_graphrag_review_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_evidence_eval_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_retrieval_ablation_uses_mocked_writer tests/test_graph_traversal.py::test_cli_report_graph_traversal_ablation_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_kg_extraction_comparison_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_answer_eval_uses_mocked_writer tests/test_hybrid_cli.py::test_cli_report_sufficiency_and_triple_review_use_mocked_writers tests/test_hybrid_cli.py::test_cli_report_robustness_uses_mocked_writer tests/test_final_evaluation.py::test_cli_report_final_evaluation_uses_mocked_writer tests/test_evidence_cards.py::test_write_evidence_cards_and_cli_generate_json_and_markdown`
- `uv run aviation-ai report hybrid-rag --help`
- `uv run aviation-ai report graphrag-review --help`
- `uv run aviation-ai report evidence-eval --help`
- `uv run aviation-ai report evidence-cards --help`
- `uv run aviation-ai report retrieval-ablation --help`
- `uv run aviation-ai report graph-traversal-ablation --help`
- `uv run aviation-ai report kg-extraction-comparison --help`
- `uv run aviation-ai report answer-eval --help`
- `uv run aviation-ai report sufficiency-eval --help`
- `uv run aviation-ai report triple-semantic-review --help`
- `uv run aviation-ai report robustness --help`
- `uv run aviation-ai report final-evaluation --help`

Focused and full verification passed after this iteration.
