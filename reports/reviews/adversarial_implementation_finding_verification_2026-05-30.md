# Adversarial Implementation Finding Verification - 2026-05-30

Input report: `reports/reviews/adversarial-review-implementation-2026-05-30.md`

This second verification pass treats the implementation-level review as an
input, not as ground truth. Each item below was checked against the current
repository state before changes were made. This iteration fixes low-risk,
directly testable correctness issues. Higher-churn behavior changes remain a
verified backlog.

## Fixed Or Mitigated In This Iteration

| ID | Verification | Action |
| --- | --- | --- |
| C1 | Valid. JSON extraction logic was duplicated across KG extraction, ontology generation, ontology evaluation, and LLM review with slightly different fence handling. | Added `aviation_agentic_ai.utils.json` with canonical JSON payload/object extraction. Existing private functions now delegate to it for compatibility. |
| C2 | Valid as a chunk-quality edge case. `_window_text` made hard cuts when no paragraph or sentence break appeared late enough. | Added word-boundary fallback before hard character cuts. |
| I1 | Valid. Weak-overlap `vector_first_guarded_fusion` kept the first duplicate hit even when a later duplicate had a stronger score. | Duplicate hits are now merged; non-protected duplicates keep the higher score and combine source attribution. |
| I2 | Valid. RRF could emit an empty `source` string when input hits lacked source metadata. | RRF now emits `source="unknown"` when no non-empty source exists. |
| I3 | Valid. Page-level matching could treat `source_page=-1` as a real page and match malformed hits with `page=-1`. | Page fallback matching now requires `source_page >= 0`; regression tests cover NDCG/recall for unset pages. |
| I4 | Valid. Ontology generation failure paths could leave only page-level checkpoints and no main output when a later page failed. | Failure paths now write a clearly labelled partial ontology to the configured output path and record `output_complete=false`, `partial_output_written=true`, and a failure stage in the manifest. |
| I5 | Valid as observability gap. LLM-returned KG triples rejected by deterministic filters were silently absent from reports. | KG extraction now reports candidate triples, filtered triples, and filter reasons. |
| I6 | Valid as a recall/observability concern. Strict quote containment can drop near-valid LLM evidence. | KG extraction now records diagnostic-only filtered evidence near-misses using token-overlap metadata. These candidates remain rejected and are not accepted as KG evidence, so KG semantics and scientific results do not change. |
| Original I7 | Still valid as a broad architecture issue. `cli.py` remains large and imports many subsystem functions directly. | Continued incremental CLI modularization by moving the web command group into `aviation_agentic_ai.cli_web`, the chunk command group into `aviation_agentic_ai.cli_chunk`, the index command group into `aviation_agentic_ai.cli_index`, the top-level query command into `aviation_agentic_ai.cli_query`, the KG extraction/validation group into `aviation_agentic_ai.cli_kg`, and the top-level CQ gold-label utilities into `aviation_agentic_ai.cli_cqs`; command behavior and help output were verified. |
| Duplication | Still valid as a broad maintenance concern. JSON extraction/tokenizer duplication was already reduced, but reporting modules still repeated JSON report I/O and lightweight normalization. | Added `aviation_agentic_ai.reporting.io`; migrated the first low-risk reporting batch and the next batch of sorted JSON report writers while preserving existing missing-file, non-object, and formatting semantics. |
| M1 | Partly valid. Empty bootstrap intervals returned `n=0` with zero-valued compatibility fields, which could be overread as a measured zero. | Evaluation protocol review now states that `n=0` CI statistics are undefined and that numeric fields are placeholders, not measured zero performance. The bootstrap API is left compatible. |
| M2 | Valid. `_cosine_similarity` silently truncated mismatched vectors with `zip`. | Mismatched vector lengths now raise `ValueError`. |
| M3 | Valid low-severity edge case. Leading short proposition segments could remain below `min_chars` when a page began with a short fragment before normal content. | `proposition_like` now forward-merges leading short fragments when a following segment exists. The benchmark-v2 chunking artifacts were regenerated after the behavior change. |
| M4 | Valid documentation nuance. Context Precision@k and Precision@k intentionally use different denominators when fewer than k hits are returned. | Evaluation protocol review now documents the fixed-cutoff denominator for Precision@5 and returned-context denominator for Context Precision@5. |

## Verified Backlog

| ID | Current assessment | Reason deferred |
| --- | --- | --- |
| I6 acceptance | Still intentionally deferred. Near-miss evidence is now visible in extraction diagnostics, but fuzzy acceptance could admit paraphrases as provenance. | Accepting fuzzy evidence changes KG semantics and should require a separate evaluation protocol and claim update. |
| Duplication remainder | Still partly valid. A smaller set of custom readers and unsorted JSON writers remains. | Continue only where exact behavior can be preserved; intentionally unsorted outputs were not migrated in this batch. |
| Original I7/I8 remainder | Still valid. Most report commands and the ontology command group still live in `cli.py`, and a smaller set of custom report readers/writers remains. | Continue in reviewable batches rather than mixing broad mechanical churn with behavior changes; ontology and report groups are larger CLI slices and report I/O cleanup should remain scoped to exact behavior preservation. |

## Verification Commands

- `uv run ruff check .`
- `uv run pytest tests/test_json_utils.py tests/test_chunking.py tests/test_metric_edge_cases.py tests/test_hybrid_retrieval.py tests/test_kg_extraction.py tests/test_llm_review_reports.py tests/test_ontology_evaluation.py tests/test_ontology_generation.py`
- `uv run pytest tests/test_kg_extraction.py`
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
- `uv run pytest tests/test_ontology_generation.py`
- `uv run pytest tests/test_evaluation_protocol_metrics.py tests/test_bootstrap_ci.py`
- `uv run aviation-ai report chunking-comparison-v2 --no-semantic-download`
- `uv run aviation-ai report chunking-comparison-v2 --evaluation-mode fixed_context_budget --no-semantic-download`
- `uv run aviation-ai report chunking-topk-sensitivity-v2 --no-semantic-download`
- `uv run aviation-ai report chunking-category-analysis-v2 --no-semantic-download`
- `uv run aviation-ai kg validate --output-dir reports/stages`
- `uv run aviation-ai kg validate --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output-dir reports/stages --report-name structure_aware_kg_validation`
- `make reports-main-experiments`
- `uv run aviation-ai report retrieval-ablation`
- `uv run aviation-ai report thesis-experiment-dashboard`
- `uv run aviation-ai report academic-paper --no-ai`
- `uv run aviation-ai report project --no-ai`
- `uv run aviation-ai report thesis-claims`
- `make validate`

Focused and full verification passed after regenerating affected reports.
