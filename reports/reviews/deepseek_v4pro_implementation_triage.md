# DeepSeek V4Pro Implementation Triage - 2026-05-30

Input report: `reports/reviews/adversarial-review-implementation-2026-05-30.md`

This triage treats the DeepSeek V4Pro implementation review as input, not ground
truth. Each finding was checked against the current repository before any code
changes were made. The goal is implementation hardening and test reliability
without changing scientific conclusions or strengthening thesis claims.

## Policy

- No code changes before this triage artifact.
- Do not fabricate experimental results or change metrics without deterministic
  regeneration.
- Preserve public CLI compatibility unless a change is explicitly documented.
- Keep exact provenance stricter than fuzzy/diagnostic evidence matching.
- Do not claim human review, external aviation expert certification, operational
  readiness, universal GraphRAG Recall@k superiority, or a single mixed score.

## Triage Table

| ID | Severity | Current Status | Evidence From Current Code | Planned Action |
| --- | --- | --- | --- | --- |
| C1 | P1 | partially_valid | The four modules now delegate to `aviation_agentic_ai.utils.json`, so the report's "four divergent implementations" claim is stale. The shared utility is still object-oriented and lacks the requested `parse_json_payload`/typed-error surface and array-focused tests. | Extend the shared JSON extraction surface and add `tests/test_json_extraction.py` while preserving existing wrapper compatibility. |
| C2 | P2 | partially_valid | `_window_text` already has a word-boundary fallback, but paragraph/sentence/whitespace preference is still coupled to a single `max_chars // 2` threshold. | Refactor boundary selection into explicit helpers that preserve progress and valid char ranges. |
| I3 | P2 | already_fixed | `_hit_matches_gold` returns `False` when `gold.source_page < 0`; no-answer labels are excluded before page matching. | No code change; retain metric regression tests. |
| I6 | P4 | partially_valid | Strict containment remains the acceptance criterion by design. Filtered triple counts, reasons, and diagnostic evidence near-misses already exist. | Keep exact provenance as accepted evidence; optionally add clearer exact/normalized/fuzzy diagnostic helpers later. |
| M3 | P1 | already_fixed | `_proposition_segments` forward-merges leading short fragments; `test_proposition_like_merges_leading_short_fragment` covers it. | No code change unless chunking refactor reveals a regression. |
| NF1 | P3 | still_valid | `_source_set` splits on literal `"+"`; current labels are safe but the invariant is undocumented and unguarded. | Add delimiter constant/helper and tests while preserving output strings. |
| NF2 | P3 | still_valid | `llm_runtime_available` still reads `LLM_PROVIDER` directly instead of using `configured_llm_provider`. | Use centralized provider helper and preserve API-key checks. |
| NF3 | P4 | partially_valid | Partial TTL/manifest are already written, but failure paths still raise generic `RuntimeError`. | Defer unless higher-priority phases complete; potential typed exception for programmatic callers. |
| NF4 | P2 | still_valid | `_score` returns `0.0` for missing/non-numeric scores. Behavior is deterministic but undocumented and not directly tested. | Document behavior and add direct tests. |
| NF5 | P3 | still_valid | `load_questions_and_gold_labels` can parse the same gold-label file twice when labels lack question text. | Pass preloaded labels through the fallback path and test one-load behavior. |

## Details

### C1: JSON Extraction

Current status: `partially_valid`.

Files inspected:

- `src/aviation_agentic_ai/utils/json.py`
- `src/aviation_agentic_ai/kg/extraction.py`
- `src/aviation_agentic_ai/ontology/generation.py`
- `src/aviation_agentic_ai/ontology/evaluation.py`
- `src/aviation_agentic_ai/evaluation/llm_review.py`
- `tests/test_json_utils.py`
- `tests/test_kg_extraction.py`

Evidence:

- Current private functions delegate to `utils/json.py`, so the duplicated
  parser implementation risk has already been reduced.
- The requested implementation surface is broader than the current utility:
  bare arrays, explicit parse helper, typed extraction error, malformed payload
  diagnostics, and multiple brace-like sections need direct coverage.

Risk if unfixed: LLM response parsing remains underspecified outside object-only
review paths.

Tests required: `tests/test_json_extraction.py` plus existing JSON utility and KG
extraction tests.

Documentation/report impact: remediation summary only; no metrics change.

### C2: Chunk Window Boundaries

Current status: `partially_valid`.

Files inspected:

- `src/aviation_agentic_ai/chunking/chunks.py`
- `tests/test_chunking.py`

Evidence:

- A word-boundary fallback exists now.
- Paragraph, sentence, and word boundaries are still selected through a single
  `max_chars // 2` threshold instead of an explicit preference policy.

Risk if unfixed: fixed-window chunks can remain less readable than necessary,
especially in fixed-small-style chunking.

Tests required: short paragraph, sentence break, whitespace fallback,
no-whitespace hard cut, overlap progress, invalid overlap, no infinite loop.

Documentation/report impact: no metric change unless chunking reports are
regenerated.

### I3: Page-Unset Retrieval Metrics

Current status: `already_fixed`.

Files inspected:

- `src/aviation_agentic_ai/evaluation/metrics.py`
- `tests/test_metric_edge_cases.py`

Evidence:

- Page fallback matching requires `gold.source_page >= 0`.
- No-answer labels return false before page matching.

Planned action: no code change; rerun metric tests.

### I6: LLM Evidence Containment

Current status: `partially_valid`.

Files inspected:

- `src/aviation_agentic_ai/kg/extraction.py`
- `tests/test_kg_extraction.py`

Evidence:

- Exact containment is still required for accepted triples.
- Filtered triple counts, filter reasons, and diagnostic-only evidence near
  misses already exist.

Risk if unfixed: diagnostics can be clearer, but accepting fuzzy evidence would
risk provenance overclaiming.

Planned action: defer acceptance changes; optionally add named diagnostic
helpers in Phase 2.

### M3: Proposition Short Leading Segment

Current status: `already_fixed`.

Files inspected:

- `src/aviation_agentic_ai/chunking/chunks.py`
- `tests/test_chunking.py`

Evidence:

- Leading short segments are forward-merged when another segment exists.
- Existing test coverage verifies the edge case.

Planned action: no code change unless C2 changes reveal a regression.

### NF1: Source Delimiter

Current status: `still_valid`.

Files inspected:

- `src/aviation_agentic_ai/retrieval/hybrid.py`
- `tests/test_hybrid_retrieval.py`

Evidence: source strings are joined and split using literal `"+"`; this is
currently safe for existing labels but not documented or guarded.

Planned action: add a delimiter constant/helper and direct tests.

### NF2: Central Provider Lookup

Current status: `still_valid`.

Files inspected:

- `src/aviation_agentic_ai/evaluation/llm_review.py`
- `src/aviation_agentic_ai/llm/providers.py`
- `tests/test_llm_review_reports.py`

Evidence: `llm_runtime_available` duplicates provider lookup with raw
`os.getenv`.

Planned action: use `configured_llm_provider`.

### NF3: Partial Ontology Exception Type

Current status: `partially_valid`.

Files inspected:

- `src/aviation_agentic_ai/ontology/generation.py`
- `tests/test_ontology_generation.py`

Evidence: partial TTL and manifest are preserved, but programmatic callers still
receive a generic `RuntimeError`.

Planned action: defer until higher-priority phases unless time permits.

### NF4: Missing Score Semantics

Current status: `still_valid`.

Files inspected:

- `src/aviation_agentic_ai/retrieval/hybrid.py`
- `tests/test_hybrid_retrieval.py`

Evidence: `_score` returns `0.0` for missing or invalid scores; this deterministic
policy is not directly tested or documented.

Planned action: document and add tests.

### NF5: Gold Label Double Load

Current status: `still_valid`.

Files inspected:

- `src/aviation_agentic_ai/evaluation/gold.py`
- `tests/test_experiment_protocol.py`

Evidence: when labels lack embedded question text, the current function can load
the gold-label file once for inspection and again during fallback overlay.

Planned action: pass loaded labels through fallback and add spy tests proving one
load.

## Phase Plan

1. Phase 1: JSON extraction surface, chunk boundary behavior, and verification
   that I3/M3 remain fixed.
2. Phase 2: Evidence matching diagnostics and retrieval source/score robustness.
3. Phase 3: Provider lookup consistency, gold-label loader double-load, optional
   ontology typed exception.
4. Phase 4: Remediation summary plus dashboard/final-report wording only if
   implementation-review remediation should be surfaced.
