# Adversarial Review Report: aviation_agentic_ai

**Date**: 2026-05-30
**Reviewer**: Claude Agent (4 parallel adversarial sub-agents)
**Scope**: Full project — architecture, scientific rigor, test quality, CLAUDE.md compliance
**Project Scale**: ~24K lines source / ~7K lines tests / 47 commits / 34 test files

---

## Executive Summary

Four independent adversarial review agents examined the project across different dimensions:

1. **Architecture & Code Quality** — coupling, dead code, error handling, type safety, duplication
2. **Scientific Rigor & Methodology** — metric validity, statistical soundness, reproducibility
3. **Test Quality & Coverage** — coverage gaps, assertion quality, mock quality, edge cases
4. **CLAUDE.md Compliance** — repository boundaries, artifact policy, architecture constraints, dependency management

A total of **19 findings** were identified: 4 Critical, 8 Important, 7 Minor.

**Top-priority fixes:**

| # | Finding | Impact |
|---|---------|--------|
| C1 | LLM call failures crash entire KG extraction | Production reliability |
| C4 | Sufficiency evaluation has circular dependency on gold labels | Thesis credibility |
| C2 | `graph_hops` parameter silently ignored | Experiment transparency |
| I2 | `bootstrap_ci` has zero direct tests | Statistical reliability |
| I4 | `run_retrieval` / `run_query` have no integration tests | Regression detection |

---

## 🔴 Critical Findings (4)

### C1. LLM Call Failures Crash Entire KG Extraction Pipeline

**Confidence: 90** | **Severity: Critical**

**Location**: `src/aviation_agentic_ai/kg/extraction.py:204-213`

`_llm_triples_for_chunk` calls `_invoke_llm_text` and immediately does `json.loads()` on the result. If the LLM returns malformed JSON, the API key is missing, rate limits hit, or a network timeout occurs, the raw `json.JSONDecodeError` (or whatever exception LangChain throws) propagates up through `extract_kg_file` and kills the entire extraction run. There is no per-chunk try/except, no retry, and no graceful degradation.

The same pattern exists in `src/aviation_agentic_ai/retrieval/hybrid.py:249-253` — `generate_grounded_answer` also has no exception handling around the LLM invoke.

Per CLAUDE.md: "LLM calls must be explicit and configured through environment variables or config files." A single LLM hiccup on chunk 47 of 200 should not discard all prior work.

**Suggested fix**: Wrap the per-chunk LLM call in `_llm_triples_for_chunk` with a try/except that logs the failure and returns an empty list for that chunk (or a configurable retry). At minimum, the error should be collected into the validation report rather than aborting the whole run.

---

### C2. `graph_hops` Parameter Silently Discarded in Lexical Graph Search

**Confidence: 95** | **Severity: Critical**

**Location**: `src/aviation_agentic_ai/retrieval/hybrid.py:52-55`

```python
def graph_search(
    question: str,
    kg_path: str | Path,
    chunks_path: str | Path,
    top_k: int = 8,
    graph_hops: int = 2,
) -> ...:
    _ = graph_hops  # <-- silently ignored
```

The `graph_hops` parameter is accepted and explicitly silenced with `_ = graph_hops`. All callers that pass `graph_hops` (the CLI, hybrid_rag reporting, retrieval ablation) are passing a parameter that does nothing. When `graph_method="lexical"`, the hops value is meaningless — but the caller has no way to know this. This is a leaky abstraction that produces misleading experiment configurations.

**Suggested fix**: Either remove the parameter from `graph_search` (and have callers only pass it when using traversal), document in the docstring that it is unused for lexical mode, or raise a warning.

---

### C3. `read_kg_jsonl` Silently Swallows Malformed JSON — No Error Handling

**Confidence: 95** | **Severity: Critical**

**Location**: `src/aviation_agentic_ai/kg/extraction.py:339`

`read_kg_jsonl` does `KGTriple(**json.loads(line))` inside a loop with no try/except. A single corrupted or malformed line in a KG JSONL file will crash the entire read with an unhandled `json.JSONDecodeError` or `TypeError` from `KGTriple(**...)`. This is the primary I/O path for loading KG artifacts for retrieval, validation, and reporting.

**Bug that slips through**: Any pipeline stage that reads KG JSONL (validation, graph search, hybrid retrieval, report generation) will fail with an uncaught exception on a single bad line instead of reporting the error.

**Suggested fix**: Wrap the per-line parse in try/except, accumulate errors, and either skip the line or raise a descriptive error with the line number. Add tests for: (a) a file with one malformed JSON line among valid lines, (b) a file with a valid JSON object missing required KGTriple fields.

---

### C4. Sufficiency Evaluation Has Circular Dependency on Gold Labels

**Confidence: 90** | **Severity: Critical**

**Location**: `src/aviation_agentic_ai/retrieval/sufficiency.py:147-196`

`evaluate_evidence_sufficiency` makes an answer/abstain decision that partially depends on `gold_label` (if provided). When `gold_label` is present and not an abstention, the function checks whether retrieved evidence matches expected benchmark chunks or spans. This means the evaluation pipeline uses the gold standard to determine whether the system should answer — **it is not a purely evidence-quality-based decision**.

For thesis defense, a reviewer would question whether this constitutes circular evaluation: "You're using the answer key to decide whether to answer."

**Suggested fix**: In the thesis, explicitly document that sufficiency evaluation operates in two modes:
1. **Gold-aided mode** — for benchmark validation (uses gold labels to measure retrieval quality against known answers)
2. **Evidence-only mode** — for real deployment (purely based on lexical overlap and evidence signals)

Report results for both modes separately.

---

## 🟠 Important Findings (8)

### I1. STOPWORDS Defined Independently in 3 Files with Divergent Contents

**Confidence: 92** | **Severity: Important**

Three locations define STOPWORDS sets:
- `src/aviation_agentic_ai/retrieval/hybrid.py:14-36` — 24 entries
- `src/aviation_agentic_ai/retrieval/graph_traversal.py:16-41` — 27 entries (adds "when", "where", "which")
- `src/aviation_agentic_ai/chunking/chunks.py` — inline `_tokenize` with no stopwords

The same question gets different token sets depending on which module tokenizes it, leading to inconsistent scoring across retrieval strategies.

**Related**: `_tokenize()` function duplicated identically in 2 files (`chunking/chunks.py:316`, `retrieval/graph_traversal.py:123`), and `retrieval/hybrid.py:39` has a similar public `tokenize()` with slight differences.

**Suggested fix**: Extract a shared `tokenize` function and `STOPWORDS` constant (e.g., in `utils/text.py`) and import everywhere.

---

### I2. `bootstrap_ci` Has Zero Direct Tests

**Confidence: 90** | **Severity: Important**

**Location**: `src/aviation_agentic_ai/evaluation/bootstrap_ci.py` (64 lines, entire file)

The function is used in `test_sufficiency_eval.py` indirectly (via `write_sufficiency_evaluation`), but `bootstrap_ci` and `bootstrap_metric_ci` are never called directly in tests with known inputs to verify the interval calculation.

The lower/upper index calculation uses `int((alpha / 2.0) * samples)` and `int((1.0 - alpha / 2.0) * samples) - 1`. With `confidence=0.95, samples=1000`, these give `lower_index=25` and `upper_index=974`. This is a standard percentile method but the implementation is never verified against a known result. The empty input case returns `mean=0.0, lower=0.0, upper=0.0` which may mislead callers (the mean of no data is undefined, not zero).

**Bug that slips through**: An off-by-one error in the percentile indices would silently produce incorrect confidence intervals used in thesis evaluation reporting.

**Suggested fix**: Add `tests/test_bootstrap_ci.py` that calls `bootstrap_ci([1.0, 0.0, 1.0, 1.0, 0.0], seed=42)` and asserts exact mean, lower, and upper bounds. Test the empty-list edge case.

---

### I3. `cost_latency.py` Has Zero Tests

**Confidence: 88** | **Severity: Important**

**Location**: `src/aviation_agentic_ai/evaluation/cost_latency.py` (42 lines, entire file)

No test file exists. `artifact_size_bytes` handles None, non-existent paths, files, and directories. `cost_latency_block` formats elapsed time and artifact sizes. None of these code paths are tested. `artifact_size_bytes` returns `None` for non-existent paths, and uses `sum(item.stat().st_size for item in source.rglob("*") if item.is_file())` for directories — the directory branch is easy to get wrong (e.g., permission errors on macOS `.DS_Store` files).

**Suggested fix**: Add `tests/test_cost_latency.py` with tests for: `artifact_size_bytes(None)`, `artifact_size_bytes(nonexistent_path)`, `artifact_size_bytes` on a real file, and `cost_latency_block` verifying relative paths and rounding.

---

### I4. `run_retrieval` and `run_query` Have Zero Integration Tests Without ChromaDB

**Confidence: 92** | **Severity: Important**

**Location**: `src/aviation_agentic_ai/retrieval/hybrid.py:256-382`

`tests/test_hybrid_retrieval.py` tests individual functions (`reciprocal_rank_fusion`, `build_answer_prompt`, `graph_search`) but never calls `run_retrieval` or `run_query` directly. The only "integration" test is `test_cli_query_uses_mocked_runner` in `tests/test_hybrid_cli.py`, which monkeypatches `run_query` to a lambda returning a dict — it never exercises the actual retrieval logic.

`run_retrieval` contains mode routing logic, graph_fusion_policy branching, and the integration of vector + graph results. None of these code paths are tested with actual data.

**Related**: `vector_first_guarded_fusion` is only tested in the "strong overlap" branch — the "no overlap" concatenation path is completely untested. The existing test passes triples with "angle of attack" and "lift" as subjects/objects, which triggers `_strong_graph_overlap` returning True. The else branch (`[*vector_hits, *graph_hits]`) is never tested.

**Bug that slips through**: Incorrect mode routing (e.g., `"hybrid"` mode silently falling back to graph-only due to a typo), or the `vector_first_guarded_fusion` path never being exercised via `run_retrieval` with the correct `graph_fusion_policy` parameter.

**Suggested fix**: Add a test that calls `run_retrieval` with `mode="hybrid"` and `graph_method="lexical"` using a synthetic kg.jsonl + chunks.jsonl pair. Test at least the `"rrf"` and `"vector_first_guarded"` fusion policy branches.

---

### I5. `get_llm()` Has No Return Type Annotation

**Confidence: 85** | **Severity: Important**

**Location**: `src/aviation_agentic_ai/llm/providers.py:8`

```python
def get_llm(temperature: float = 0.3, max_tokens: int = 4096):
```

The function returns a `ChatOpenAI` instance but is annotated with no return type at all. CLAUDE.md says "Prefer typed functions for project-owned modules." This is the single most important function in the LLM layer — every LLM call in the project flows through it. The missing return type means mypy/pyright cannot catch misuse.

**Suggested fix**:
```python
from langchain_core.language_models.chat_models import BaseChatModel
def get_llm(temperature: float = 0.3, max_tokens: int = 4096) -> BaseChatModel:
```

---

### I6. `load_dotenv()` Called in 3 Different Places at LLM Access Time, Not at Config Layer

**Confidence: 82** | **Severity: Important**

**Locations**:
- `src/aviation_agentic_ai/llm/providers.py:18`
- `src/aviation_agentic_ai/ontology/generation.py:197`
- `src/aviation_agentic_ai/web/app.py:35`

The parent `CLAUDE.md` convention says "Python: pydantic-settings, .env from .env.example". This project's `config.py` only reads YAML files. Environment variables are read raw via `os.getenv()` in `llm/providers.py` and `ontology/generation.py` without any validation or defaults management. API keys are passed directly to `ChatOpenAI` without checking if they are `None`.

If `OPENAI_API_KEY` is not set, `ChatOpenAI` receives `api_key=None`, which will fail at call time with an opaque error rather than a clear startup-time message.

**Suggested fix**: Centralize environment loading. Either use `pydantic-settings` as the parent CLAUDE.md prescribes, or at minimum call `load_dotenv()` once at a well-defined entry point (CLI startup, server startup) rather than inside `get_llm()`.

---

### I7. CLI Is 2027 Lines and Imports from Every Reporting Module — God-File Anti-Pattern

**Confidence: 82** | **Severity: Important**

**Location**: `src/aviation_agentic_ai/cli.py`

The CLI file directly imports from 22 reporting modules, the chunking module, the retrieval module, the kg module, the ontology modules, the evaluation modules, and the web module. Per CLAUDE.md architecture constraints: "Keep public workflows behind the aviation-ai CLI" — but the CLI should delegate to subsystem entry points, not know about every individual `write_*` function in every reporting module.

This makes it impossible to change reporting module APIs without modifying the CLI. Adding a new report command requires editing this 2000-line file.

**Suggested fix**: Have each subsystem (reporting, ontology, kg, retrieval) register its own CLI commands via a Click group pattern, so `cli.py` imports subsystem groups rather than 70 individual functions.

---

### I8. Pervasive Code Duplication Across Reporting Modules

**Confidence: 85-92** | **Severity: Important**

| Pattern | Occurrences | Locations |
|---------|-------------|-----------|
| `_normalize()` | 8 files | `evaluation/gold_draft.py`, `evaluation/metrics.py`, `retrieval/sufficiency.py`, `reporting/evidence_cards.py`, `reporting/answer_eval.py`, `reporting/benchmark_review_pack.py`, `reporting/evidence_eval.py`, `reporting/kg_extraction_comparison.py` |
| `_load_json()` | 6 files | `reporting/evidence_cards.py`, `reporting/evidence_eval.py`, `reporting/answer_eval.py`, `reporting/sufficiency_eval.py`, `reporting/graphrag_review.py`, `reporting/thesis_dashboard.py` |
| `_tokenize()` / `tokenize()` | 3 files | `chunking/chunks.py`, `retrieval/graph_traversal.py`, `retrieval/hybrid.py` |
| `_questions_and_labels()` | 2 files | `reporting/hybrid_rag.py`, `reporting/retrieval_ablation.py` (character-for-character identical) |
| write-JSON boilerplate | 60+ times | All reporting modules; `chunking_comparison.py` alone has 13 occurrences |

All do the same thing with minor variations. This is classic copy-paste drift territory — fixing a bug in one `_normalize` won't propagate to the other 7.

**Suggested fix**: Extract shared utilities:
- `utils/text.py` — `normalize()`, `tokenize()`, `STOPWORDS`
- `utils/io.py` — `load_json()`, `write_json_report()`
- Reporting modules import from shared utils.

---

## 🟡 Minor Findings (7)

### M1. Silent `except Exception: pass` in ChromaDB Index Deletion

**Confidence: 80** | **Location**: `src/aviation_agentic_ai/retrieval/indexing.py:58`

```python
try:
    client.delete_collection(collection_name)
except Exception:
    pass
```

Swallows all exceptions including disk full, permission errors, corruption. If deletion fails for a real reason, subsequent `get_or_create_collection` may return a corrupted or stale collection.

**Fix**: Catch the specific ChromaDB "not found" exception and let others propagate.

---

### M2. `_extract_json_payload` Has No Direct Unit Tests

**Confidence: 85** | **Location**: `src/aviation_agentic_ai/kg/extraction.py:77-88`

Only indirectly tested via `test_extract_kg_llm_filters_unsupported_or_bad_evidence` which mocks `_invoke_llm_text`. The function handles three cases: (1) fenced markdown code blocks, (2) bare JSON starting with `{`, (3) extracting the first `{...}` from surrounding text. Case 3 is never tested — nested braces could produce invalid JSON.

**Fix**: Add direct unit tests for: fenced json, fenced without language tag, bare JSON, JSON inside text, JSON with preceding braces, empty string.

---

### M3. Retrieval Ablation Hardcodes Misleading `provider: none` in Run Manifest

**Confidence: 80** | **Location**: `src/aviation_agentic_ai/reporting/retrieval_ablation.py:313`

```python
llm={"provider": "none", "model": "not_used"},
```

This is technically correct (no LLM used for retrieval-only ablation) but obscures the fact that the ablation does not test answer quality. The manifest should explicitly state "no LLM used for retrieval-only ablation."

---

### M4. `graph_search` Returns Empty Results — "No Results" Case Never Tested

**Confidence: 85** | **Location**: `src/aviation_agentic_ai/retrieval/hybrid.py:47-103`

No test exists where the question has zero token overlap with all triples. In that case `graph_search` returns `([], [])`. Whether this is handled correctly by downstream answer generation and metric computation is untested end-to-end.

**Fix**: Add a test for `graph_search` with a question that has no lexical overlap with any triple. Consider testing `build_answer_prompt` with empty inputs to verify graceful degradation.

---

### M5. `retrieval_metrics` and `answer_metrics` Never Tested with Empty Inputs

**Confidence: 88** | **Location**: `src/aviation_agentic_ai/evaluation/metrics.py:129-160, 246-312`

All existing tests pass non-empty hits/chunks/triples. Edge cases like `retrieval_metrics([], gold)` or `answer_metrics({"answer": "", ...})` produce potentially surprising values (e.g., `first_relevant_rank=None`, `is_abstention=False` for empty answer) that are never asserted.

**Fix**: Add tests for empty-input edge cases with explicit assertions on each returned field.

---

### M6. Evaluation Report Test Only Validates Structure, Not Metric Values

**Confidence: 82** | **Location**: `tests/test_evaluation_protocol_metrics.py:56`

`test_evaluation_protocol_report_generation` calls `write_evaluation_protocol_review` and only checks that output files exist and have structural keys (`scoring_policy`, `layer`, `metric`). It never asserts that any metric value is correct. If `write_evaluation_protocol_review` computed incorrect aggregated metrics (e.g., averaging precision instead of recall), the test would pass.

**Fix**: Add assertions on actual metric values in the result dict. At minimum, assert that some retrieval and answer metrics are present and in valid ranges (0.0-1.0).

---

### M7. `write_kg_jsonl` Empty List Round-Trip Never Tested

**Confidence: 82** | **Location**: `src/aviation_agentic_ai/kg/extraction.py:267`

`write_kg_jsonl([], path)` writes an empty file. `read_kg_jsonl(path)` on that file returns `[]`. This round-trip appears correct but is never explicitly locked in by a test.

**Fix**: Add a two-line test: `write_kg_jsonl([], path); assert read_kg_jsonl(path) == []`.

---

## ✅ CLAUDE.md Compliance Audit

| Rule | Status | Notes |
|------|--------|-------|
| No nested git repositories | ✅ Pass | No `.git` sub-directories found |
| No vendored external repositories | ✅ Pass | |
| No `.env` committed | ✅ Pass | `.gitignore` covers `.env` |
| No API keys/tokens/credentials in source | ✅ Pass | `grep` scan found no leaks |
| No model weights committed | ✅ Pass | No `models/` directory |
| Vector indexes in `.gitignore` | ✅ Pass | `data/indexes/chroma/*.bin` not tracked |
| Baseline PHAK ontology at correct path | ✅ Pass | `data/ontology/baseline/06_phak_ch4_0.ttl` exists |
| Generated ontologies under `data/ontology/generated/` | ✅ Pass | |
| Curated ontology at `data/ontology/curated/` | ✅ Pass | `06_phak_ch4_0.curated.ttl` exists |
| Extraction profile is source of truth | ✅ Pass | `configs/extraction_profile.yaml` |
| Paths config-driven | ✅ Pass | `paths.py` + `config.py` + `resolve_project_path` |
| RDFLib for RDF/Turtle | ✅ Pass | Used throughout ontology modules |
| FastAPI kept out of core | ✅ Pass | `web/` module uses lazy imports inside function bodies |
| Heavy dependencies optional | ✅ Pass | `pyproject.toml` groups: `ontology-generation`, `graphrag`, `web`, `ontogpt` |
| Python 3.10+ compatible | ✅ Pass | `target-version = "py310"` in ruff config |
| JSON and Markdown for reports | ✅ Pass | All reports are `.json` or `.md` |
| Tests don't require external services | ✅ Pass | ChromaDB, LLM, sentence-transformers all mocked via `monkeypatch` |
| No hidden network calls in tests | ✅ Pass | |
| No `.env` reads in tests | ✅ Pass | `monkeypatch.setenv` used instead |
| `pydantic-settings` used | ❌ **Violation** | Parent repo convention specifies `pydantic-settings`, but this project uses raw `os.getenv()` scattered across 3 files |
| `@pytest.mark` for optional tests | ⚠️ Warning | No marks at all, but external deps are fully mocked so not a practical problem |
| Module size discipline | ⚠️ Warning | `cli.py` (2027 lines), `ontology/evaluation.py` (~1321 lines), `ontology/generation.py` (638 lines) are large |

---

## Test Coverage Gap Summary

| Source Module | Has Tests? | Notes |
|---|---|---|
| `evaluation/bootstrap_ci.py` | ❌ No direct tests | Used indirectly via sufficiency eval |
| `evaluation/cost_latency.py` | ❌ No tests at all | Completely untested |
| `evaluation/document_metadata.py` | ⚠️ Schema only | `test_experiment_protocol.py` only tests `to_dict()` shape |
| `evaluation/metrics.py` | ⚠️ Missing edge cases | Empty input, division by zero not tested |
| `kg/extraction.py` (`_extract_json_payload`) | ⚠️ Indirect only | Only tested through LLM mock |
| `llm/providers.py` | ⚠️ Indirect only | Tested via mocks in generation tests |
| `retrieval/hybrid.py` (`run_retrieval`, `run_query`) | ❌ No integration tests | Only individual function tests |
| `retrieval/hybrid.py` (`vector_first_guarded_fusion`) | ⚠️ Partial | Only "strong overlap" branch tested |
| `utils/pdf.py` | ⚠️ Indirect only | `extract_pages` always monkeypatched |
| `web/server.py` | ✅ Tested | Via test client in `test_web_demo.py` |
| `web/data.py` | ✅ Tested | In `test_web_demo.py` |
| `retrieval/sufficiency.py` | ✅ Tested | In `test_sufficiency_eval.py` |

---

## Severity Matrix

```
Severity      Count   Scope
──────────────────────────────────────────────────
Critical        4     KG extraction, retrieval, evaluation core pipeline
Important       8     Code quality, test coverage, type safety
Minor           7     Edge cases, metadata accuracy
──────────────────────────────────────────────────
Total          19
```

---

## Recommended Fix Priority

| Priority | Finding | Effort | Impact |
|----------|---------|--------|--------|
| **P0** | C1: LLM exception handling in KG extraction | Small (try/except per chunk) | Prevents catastrophic data loss |
| **P0** | C4: Document circular evaluation concern | Small (thesis text clarification) | Defends against thesis reviewer challenge |
| **P1** | C2: Remove or document dummy `graph_hops` parameter | Small | Experiment transparency |
| **P1** | C3: Add error handling to `read_kg_jsonl` | Small | Pipeline robustness |
| **P1** | I2: Add `tests/test_bootstrap_ci.py` | Small | Statistical validity |
| **P1** | I4: Add integration tests for `run_retrieval` | Medium | Regression safety net |
| **P2** | I5: Annotate `get_llm()` return type | Trivial | Type safety |
| **P2** | I6: Centralize `load_dotenv()` | Small | Config clarity |
| **P2** | I8: Extract shared utilities (normalize, load_json, etc.) | Medium | Maintenance burden |
| **P3** | I7: Restructure CLI into subsystem groups | Medium | Architectural cleanliness |
| **P3** | M1-M7: Minor fixes | Small each | Defense in depth |

---

*Report generated by 4 parallel adversarial review agents (architecture, scientific rigor, test quality, compliance). Each finding includes confidence level based on code evidence.*
