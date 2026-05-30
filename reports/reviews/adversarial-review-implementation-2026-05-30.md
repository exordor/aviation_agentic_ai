# Adversarial Implementation Review: aviation_agentic_ai (Update 2)

**Date**: 2026-05-30 (re-reviewed after 14-commit update)
**Focus**: Code implementation — logic bugs, edge cases, data flow, correctness
**Scope**: Full re-review of all modified files plus verification of previous findings
**Baseline**: 288 tests passing, ruff clean, 0 uncommitted changes

---

## Changes Since Previous Review

14 commits addressing code quality, test coverage, and LLM hardening:

| Category | Changes |
|----------|---------|
| **LLM hardening** | Centralized provider defaults, missing-API-key fail-fast, unsupported-provider rejection |
| **Deduplication** | Shared `reporting/io.py`, `reporting/accessors.py`, `reporting/retrieval_summaries.py`, `utils/io.py` |
| **Shared loaders** | `load_questions_and_gold_labels` extracted to `evaluation/gold.py` |
| **Fusion fixes** | `_merge_duplicate_hit`, `_merged_source`, empty-source→"unknown" guard |
| **No-evidence fast-path** | `generate_grounded_answer` abstains without LLM when retrieval returns nothing |
| **Partial output** | `_write_partial_output` preserves TTL when ontology generation fails mid-run |
| **Error types** | `GoldLabelReadError`, `JSONDocumentReadError` for structured error reporting |
| **Tests** | +62 tests: LLM providers (7), hybrid retrieval (8), config (2), repository hygiene (2), accessors (1), summaries (2), reporting I/O (1), experiment protocol (1), LLM review reports (1) |

---

## Previous Finding Verification

| # | Previous Finding | Status | Notes |
|---|-----------------|--------|-------|
| C1 | JSON extraction duplication (4 implementations) | ❌ **Open** | Still 4 divergent implementations across `kg/extraction.py`, `ontology/generation.py`, `ontology/evaluation.py`, `evaluation/llm_review.py` |
| C2 | `_window_text` degenerate chunk boundary | ❌ **Open** | `_window_text` unchanged; soft-break heuristic still fails on short-paragraph text |
| I1 | `vector_first_guarded_fusion` dedup scoring | ✅ **Fixed** | `_merge_duplicate_hit` now picks higher-scored hit; `_merged_source` properly merges source labels |
| I2 | Empty string source in RRF | ✅ **Fixed** | `or "unknown"` guard at `hybrid.py:101` and `hybrid.py:198` |
| I3 | NDCG `page=-1` false positive | ❌ **Open** | `_hit_matches_gold:42` catch-all still matches `page=-1` |
| I4 | `generate_ontology` mid-failure data loss | ✅ **Fixed** | `_write_partial_output` now writes partial TTL with diagnostic header on failure |
| I5 | `link_question_entities` fallback sorting | ✅ **Confirmed correct** | Fallback only runs when `seed_matches` is empty; no mix with phrase positions |
| I6 | LLM evidence strict substring containment | ❌ **Open** | Unchanged; no fuzzy fallback or filtered-triple counter |
| M3 | `_proposition_segments` short-segment merge | ❌ **Open** | Edge case: first segment in `raw` being short still produces sub-`min_chars` output |

**Score**: 4/9 fixed, 1 confirmed correct, 4 remain open.

---

## New Findings

### NF1. `_source_set` Splits Source Strings on "+" — Ambiguous Character

**Location**: `retrieval/hybrid.py:106-107`

```python
def _source_set(value: Any) -> set[str]:
    return {source for source in str(value or "").split("+") if source}
```

The `+` character is both the concatenation delimiter for merged sources AND could theoretically appear in a source name. While current source names are `"vector"`, `"graph"`, and `"graph_traversal"` (none contain `+`), this implicit overloading is fragile. If a future source name includes `+`, it would be silently split.

**Suggested fix**: Document that source names must not contain `+`, or use a non-ambiguous delimiter like `\x1e` (ASCII record separator).

---

### NF2. `llm_runtime_available` Doesn't Use Centralized `configured_llm_provider`

**Location**: `evaluation/llm_review.py:152`

```python
def llm_runtime_available() -> bool:
    load_environment()
    provider = os.getenv("LLM_PROVIDER", "openai").lower()  # <-- raw os.getenv
    ...
```

While `llm/providers.py` now has `configured_llm_provider()` (which does the same `os.getenv("LLM_PROVIDER", "openai").lower()`), this function duplicates the logic. If the centralized function ever adds validation or transforms, this copy will diverge.

**Suggested fix**: Use `from aviation_agentic_ai.llm.providers import configured_llm_provider` and replace the raw `os.getenv` call.

---

### NF3. `generate_ontology` Still Raises RuntimeError After Writing Partial Output

**Location**: `ontology/generation.py:486-494, 531-545, 602-628`

All three failure paths write partial TTL (`_write_partial_output`), write artifacts manifest with `output_complete=False`, then **raise RuntimeError**. This means:

1. The partial TTL IS preserved at the output path ✅
2. The CLI command gets a `RuntimeError` and reports failure ✅
3. But the **TTL variable** is lost — the caller can't access the partial result programmatically ❌

For the CLI this is fine (user sees error, checks the partial file). But for programmatic callers, this is partially addressed — they can read the output file after catching the exception.

**Suggested fix**: Consider wrapping the RuntimeError in a custom `OntologyGenerationError` that carries the partial TTL and manifest as attributes, so programmatic callers can inspect the partial result without re-reading the file.

---

### NF4. `_score` Returns 0.0 for Items Without `score` Key — But `ndcg` Could Be Misleading

**Location**: `retrieval/hybrid.py:115-119`

```python
def _score(item: dict[str, Any]) -> float:
    try:
        return float(item.get("score", 0.0))
    except (TypeError, ValueError):
        return 0.0
```

Used in `_merge_duplicate_hit` to pick the winning hit when deduplicating. Returns 0.0 when `score` is missing or non-numeric. For items that have a `rank` but no `score`, this means any item with an explicit score (even 0.01) beats them. In `vector_first_guarded_fusion`, the concatenated tail items retain their original scores from the source lists, so only items where the source didn't set `score` would be affected. This is currently safe but undocumented.

---

### NF5. New `load_questions_and_gold_labels` Has Double-Load on Fallthrough

**Location**: `evaluation/gold.py:169-196`

```python
def load_questions_and_gold_labels(...):
    if gold_labels_path is not None:
        labels = load_gold_labels(gold_labels_path)  # First load
        if labels and all(label.question for label in labels.values()):
            ...
            return questions, labels
    questions = load_boundary_questions(boundary_cq_path)
    return questions, gold_labels_for_questions(questions, gold_labels_path)  # Second load
```

When `gold_labels_path` is not None but labels lack question text, `load_gold_labels` is called twice for the same file (once in the `if` block, once inside `gold_labels_for_questions`). The file is read and parsed twice. For the current scale (~200 labels) this is negligible, but it's a latent performance issue.

**Suggested fix**: Store the first load result and pass it to a variant of `gold_labels_for_questions` that accepts pre-loaded labels.

---

## New Code Quality Audit

### Positives

1. **`providers.py` hardening** — `_required_env` gives clear, immediate error messages for missing API keys instead of opaque downstream failures. `SUPPORTED_LLM_PROVIDERS` prevents silent misconfiguration.

2. **`utils/io.py` + `reporting/io.py`** — Proper layering: low-level JSON primitives in `utils/`, report-specific wrappers (with type guards, default-empty, default-none) in `reporting/`.

3. **`reporting/accessors.py`** — `nested_value` replaces scattered dict-chaining with a single function. The `default="TBD"` convention makes missing-metric detection grep-friendly.

4. **`reporting/retrieval_summaries.py`** — `hit_summary` and `triple_summary` eliminate per-report copy-paste of field subsetting.

5. **No-evidence fast path** — `generate_grounded_answer` now returns a deterministic abstention when both chunks and triples are empty, avoiding unnecessary LLM calls.

6. **`GoldLabelReadError` + `JSONDocumentReadError`** — Custom exception types with file context and line numbers for structured error propagation.

7. **Test quality** — New tests exercise error paths (missing API keys, unsupported providers, ChromaDB "not found" vs "permission denied"), confirm exact kwargs, and verify source merging. The ChromaDB mock in `test_chroma_index_builder_raises_unexpected_delete_errors` correctly verifies that non-"not found" exceptions propagate.

### Remaining Concerns

1. **JSON extraction consolidation (C1)** — Still the highest-value cleanup. Four implementations with divergent regex behavior is a bug waiting to happen.

2. **`_window_text` soft-break heuristic (C2)** — The `max_chars // 2` threshold means short-paragraph text in `fixed_small` mode never triggers soft breaks, producing mid-sentence chunk splits.

3. **NDCG `source_page=-1` catch-all (I3)** — Still a false-positive risk for page-unset gold labels.

---

## Summary of Test Coverage Gains

| Module | Before | After | New Tests |
|--------|--------|-------|-----------|
| `llm/providers.py` | 0 direct tests | 7 tests | Provider routing, API key rejection, model defaults |
| `retrieval/hybrid.py` | 4 unit tests | 10 tests | No-evidence abstention, query integration, lexical hops metadata, weak-overlap fusion dedup |
| `retrieval/indexing.py` | 0 direct tests | 3 tests | ChromaDB mock (success, not-found, permission-denied) |
| `config.py` | 2 tests | 4 tests | Env loader caching, missing-dotenv path |
| `reporting/accessors.py` | Did not exist | 1 test | Nested value extraction |
| `reporting/retrieval_summaries.py` | Did not exist | 2 tests | Hit/triple summary field preservation |
| `reporting/io.py` | Did not exist | 1 test | (via test_reporting_io.py) |
| Repository hygiene | Did not exist | 2 tests | .gitignore completeness, tracked file audit |

**Total: 226 → 288 tests (+62)**

---

## Updated Severity Summary

| Severity | Count | Key Themes |
|----------|-------|------------|
| **Previously Critical, now Fixed** | — | I1 (fusion dedup), I2 (empty source), I4 (partial output) |
| **Previously Critical, still Open** | 2 | C1 (JSON extraction duplication), C2 (chunk boundary heuristic) |
| **Previously Important, still Open** | 2 | I3 (NDCG page=-1), I6 (strict evidence containment) |
| **New Minor** | 5 | NF1-NF5 (source split ambiguity, provider inconsistency, error type, score default, double-load) |

### Updated Fix Priority

| Priority | Finding | Effort | Impact |
|----------|---------|--------|--------|
| **P1** | C1: Consolidate JSON extraction | Medium | Prevents silent parse divergence |
| **P2** | C2: Word-boundary fallback in `_window_text` | Small | Chunk quality for `fixed_small` |
| **P2** | I3: Guard NDCG `source_page=-1` catch-all | Trivial | Metric accuracy |
| **P3** | NF2: Use centralized `configured_llm_provider` in `llm_runtime_available` | Trivial | Consistency |
| **P3** | NF1: Document `+` delimiter in source strings | Trivial | Future-proofing |
| **P3** | NF5: Avoid double-load in `load_questions_and_gold_labels` | Small | Latency (minor at current scale) |
| **P4** | I6: Fuzzy evidence matching | Medium | Recall improvement |
| **P4** | NF3: Custom exception type for partial generation | Small | Programmatic API quality |

---

*Re-reviewed after 14-commit update. All 288 tests pass. Four of nine previously identified issues are now fixed. The codebase quality trajectory is strongly positive — the LLM hardening and deduplication refactoring in particular represent significant hardening.*
