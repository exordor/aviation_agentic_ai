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
| I8 | Still valid as a broader maintenance concern. Several reporting modules duplicated JSON report loading/writing and lightweight normalization. | Added `aviation_agentic_ai.reporting.io`; migrated the evidence-card, evidence-evaluation, answer-evaluation, sufficiency, GraphRAG review, benchmark-review-pack, KG-comparison, thesis-dashboard helpers, plus the next batch of sorted report JSON writers. Missing-file/non-object behavior and JSON formatting are preserved. |
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
| I7 | Still valid. `cli.py` remains a large Click god-file. | Architectural CLI modularization is high churn and not needed for the first reliability/test hardening patch. |
| I8 remainder | Still partly valid. A smaller set of custom readers and unsorted JSON writers remains. | Sorted report writers have been migrated in batches; custom loaders and intentionally unsorted outputs should continue only where behavior can be preserved exactly. |

## Verification Commands

- `uv run ruff check .`
- `uv run pytest tests/test_kg_extraction.py tests/test_hybrid_retrieval.py tests/test_sufficiency_eval.py tests/test_bootstrap_ci.py tests/test_cost_latency.py tests/test_metric_edge_cases.py tests/test_graph_traversal.py`
- `uv run pytest tests/test_text_utils.py tests/test_experiment_protocol.py tests/test_experimental_expansion.py tests/test_evaluation_protocol_metrics.py tests/test_chunking.py`
- `uv run pytest tests/test_reporting_io.py tests/test_evidence_cards.py tests/test_evidence_eval.py tests/test_sufficiency_eval.py tests/test_graphrag_review.py tests/test_thesis_dashboard.py tests/test_review_pack_and_triples.py tests/test_experimental_expansion.py tests/test_final_evaluation.py`
- `uv run pytest tests/test_chunking_comparison.py tests/test_hybrid_rag_reporting.py tests/test_graph_traversal.py tests/test_llm_review_reports.py tests/test_project_report.py tests/test_web_demo.py tests/test_generation_run_reporting.py tests/test_overnight_reporting.py tests/test_report_hygiene.py`

Focused and full verification passed after this iteration.
