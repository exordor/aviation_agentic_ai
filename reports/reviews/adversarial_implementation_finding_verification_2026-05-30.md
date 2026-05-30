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
| M2 | Valid. `_cosine_similarity` silently truncated mismatched vectors with `zip`. | Mismatched vector lengths now raise `ValueError`. |

## Verified Backlog

| ID | Current assessment | Reason deferred |
| --- | --- | --- |
| I6 | Valid as a recall/observability concern. Strict quote containment can drop near-valid LLM evidence. | Fuzzy acceptance changes KG semantics and should be evaluated separately; this iteration only adds filter counters. |
| M1 | Partly valid. Empty bootstrap intervals return `n=0` plus zero values. | Changing to `None` would require report-consumer audit; current reports already expose `n=0`. |
| M3 | Valid low-severity edge case. Leading short proposition segments can remain below `min_chars`. | Could alter chunking experiment artifacts; defer to chunking-specific iteration. |
| M4 | Valid documentation nuance. Context Precision@k and Precision@k intentionally use different denominators when fewer than k hits are returned. | Needs metric protocol wording rather than code change. |
| Duplication | Still partly valid. JSON extraction and tokenizer duplication are reduced; broader normalization/report I/O duplication remains. | Broader utility extraction would be cross-cutting and should be split into a separate refactor. |
| Original I7/I8 | Still valid. `cli.py` and report helpers remain large/duplicated. | Architectural refactors are high churn and not necessary for this correctness batch. |

## Verification Commands

- `uv run ruff check .`
- `uv run pytest tests/test_json_utils.py tests/test_chunking.py tests/test_metric_edge_cases.py tests/test_hybrid_retrieval.py tests/test_kg_extraction.py tests/test_llm_review_reports.py tests/test_ontology_evaluation.py tests/test_ontology_generation.py`
- `uv run pytest tests/test_ontology_generation.py`
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
