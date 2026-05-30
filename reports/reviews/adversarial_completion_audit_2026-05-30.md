# Adversarial Review Completion Audit - 2026-05-30

Input report: `reports/reviews/adversarial-review-2026-05-30.md`

This audit checks the current repository state against the 19 findings in the
uploaded adversarial review. The review was used as input, but each item below is
judged from current code, tests, and report artifacts rather than by trusting the
review text. The goal of this audit is not to claim a perfect codebase; it is to
verify whether the concrete risks raised by the review have been handled without
changing or overstating the scientific results.

## Overall Result

All 19 concrete findings from the adversarial review are closed or mitigated in
the current branch. Two broad maintenance themes remain as accepted residual
work:

- I7: future CLI additions should keep using the split registration pattern.
- I8: small domain-specific readers, normalizers, and formatting helpers remain
  where centralization would risk behavior drift or change scientific outputs.

These residuals do not contradict closure of the original findings because the
review's specific god-file CLI and high-risk duplication examples have been
addressed or narrowed to explicitly documented future maintenance.

## Critical Findings

| ID | Current status | Evidence |
| --- | --- | --- |
| C1 | Closed. LLM failures no longer abort the whole KG extraction or answer path. | `extract_kg_file` records per-chunk extraction errors and continues; `generate_grounded_answer` catches LLM invocation failures and returns an explicit non-answer with `Citations: none`. Tests: `test_generate_grounded_answer_returns_non_answer_when_llm_fails`, `test_generate_grounded_answer_abstains_without_retrieved_evidence`, KG extraction failure coverage. |
| C2 | Closed. Lexical graph search no longer silently accepts an unused hop parameter, and retrieval records hop applicability. | `graph_search` has no `graph_hops` argument; `run_retrieval` emits `graph_hops_requested`, `graph_hops_effective`, and a lexical-hop note. Test: `test_run_retrieval_hybrid_records_lexical_hops_as_not_applicable`. |
| C3 | Closed. KG JSONL parse failures now include file and line context. | `KGReadError` wraps malformed JSON and invalid record shapes in `read_kg_jsonl`. Tests cover malformed JSON, missing fields, and downstream comparison reporting. |
| C4 | Closed as a thesis-defensibility risk. Gold-aided and evidence-only sufficiency modes are separated. | `evaluate_evidence_sufficiency` reports `gold_aided_benchmark` vs `evidence_only`; `write_sufficiency_evaluation` reports evidence-only diagnostics. `docs/evaluation_protocol.md` documents the distinction. Tests assert both modes and markdown wording. |

## Important Findings

| ID | Current status | Evidence |
| --- | --- | --- |
| I1 | Closed. Shared lexical utilities now cover retrieval, traversal, KG evidence checks, chunking, and source scope. | `aviation_agentic_ai.utils.text` defines shared normalization, token regex, and stopword sets. Tests: `tests/test_text_utils.py`. |
| I2 | Closed. Bootstrap CI helpers have direct deterministic tests. | `tests/test_bootstrap_ci.py` covers known values, empty input, and metric mapping. |
| I3 | Closed. Cost/latency helpers have direct tests. | `tests/test_cost_latency.py` covers missing paths, files, directories, rounding, and relative paths. |
| I4 | Closed. `run_retrieval` and `run_query` now have integration-style tests without external services. | `tests/test_hybrid_retrieval.py` covers lexical hybrid retrieval, graph no-overlap abstention, hybrid prompt routing into a mocked LLM, and weak-overlap guarded fusion. |
| I5 | Closed. LLM provider entry point is typed and directly tested. | `get_llm(...) -> "BaseChatModel"` with lazy optional import; `tests/test_llm_providers.py` covers OpenAI, DeepSeek, vLLM, missing keys, and unsupported providers. |
| I6 | Closed by centralization rather than pydantic-settings adoption. | `config.load_environment()` is the single dotenv entry point used by LLM provider/review paths; tests cover caching, force reload, missing dotenv, provider routing, and key errors. |
| I7 | Closed for the concrete god-file risk; future additions remain a maintenance guardrail. | `cli.py` is 48 lines and delegates to focused `cli_*` modules plus report registration functions. CLI surface tests cover extracted command groups. |
| I8 | Closed for the high-risk duplication examples; accepted residual remains for domain-specific helpers. | Shared helpers now cover report JSON I/O, JSON document errors, text/token utilities, question/gold label loading, retrieval hit/triple summaries, nested report accessors, and report text normalization. Direct tests cover the shared helpers and migrated behavior. |

## Minor Findings

| ID | Current status | Evidence |
| --- | --- | --- |
| M1 | Closed. Chroma collection deletion no longer swallows every exception. | `build_chroma_index` suppresses only missing/not-found collection errors and re-raises unexpected failures. Tests cover the reset behavior. |
| M2 | Closed. JSON payload extraction has direct tests. | `tests/test_kg_extraction.py` and `tests/test_json_utils.py` cover fenced JSON, bare JSON, embedded JSON, and empty input. |
| M3 | Closed. Retrieval-only ablation metadata no longer uses ambiguous `provider: none`. | Retrieval ablation manifests use `provider: not_used_retrieval_only` and explicit no-LLM usage notes. |
| M4 | Closed. Lexical graph no-result behavior is tested end to end. | Tests cover graph search no-overlap and `run_query` abstaining without invoking an LLM. |
| M5 | Closed. Empty retrieval and answer metric edge cases are tested. | `tests/test_metric_edge_cases.py` covers empty retrieval hits and empty answer inputs. |
| M6 | Closed. Evaluation protocol tests assert values and interpretation notes, not just structure. | `tests/test_evaluation_protocol_metrics.py` checks metric catalog values, implemented/pending sets, CI/precision notes, and limitation language. |
| M7 | Closed. Empty KG JSONL round-trip is tested. | `tests/test_kg_extraction.py` covers `write_kg_jsonl([])` followed by `read_kg_jsonl`. |

## Claim Safety

The hardening work did not add expert-certification, operational-readiness, or
universal superiority claims. Where review or LLM artifacts exist, project
wording distinguishes deterministic metrics, heuristic diagnostics, LLM judge
outputs, and absent human/external expert certification. The sufficiency and
chunking reports explicitly separate benchmark-specific diagnostics from
deployment or universal claims.

## Verification Scope

Current-state evidence was checked with targeted repository searches over code,
tests, docs, and reports. Final verification for this audit should include:

- `uv run ruff check .`
- `uv run pytest`
- `make validate`
