# Artifact Index

Last updated: 2026-07-29

This file routes project context. It does not assert that every tracked artifact
is current.

## Active Context

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Authoritative operational instructions. |
| `RESEARCH_AUDIT.md` | Default context router and current branch-level truth. |
| `GOALS.md` | Durable system goal and boundaries. |
| `README.md` | Current user-facing system overview and commands. |
| `TODO.md` | Active execution queue only. |
| `docs/multi_agent_kg_system_design.md` | Normative multi-Agent system design. |
| `src/aviation_agentic_ai/agent_system/` | Active Agent-system implementation. |
| `tests/test_agent_system*.py`, `tests/test_cli_agent_system.py` | Focused Agent-system acceptance surface. |
| `configs/cross_source_v1.yaml` | Admitted ATCSCC, facility, terminology, Weather-context, and BTS On-Time source configuration. |
| `configs/prompts/decision_case_agents_v1.yaml` | Versioned Agent-system prompt configuration. |
| `data/evaluation/agent_system/live_agent_smoke_v1.yaml` | Frozen five-task DeepSeek live-smoke suite. |
| `reports/stages/agent_system_live_agent_smoke_v1.{json,md}` | Sanitized single-run live-smoke result; 0/5 accepted, not a benchmark. |
| `data/evaluation/agent_system/live_agent_experiment_v1.yaml` | Frozen five-task, 12-cycle repeated real-provider suite. |
| `reports/stages/agent_system_live_agent_experiment_v1.{json,md}` | Sanitized repeated DeepSeek result: 108/108 provider calls succeeded; task acceptance 0/60. |
| `data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json` | Curated formal vocabulary for Weather report nodes only. |
| `data/ontology/curated/decision_case_public_observation_slice.json` | Source-qualified formal profile for BTS-reported public operational observations. |
| `data/sources/bts_on_time_2026_05_manifest.json` | Pinned BTS archive/member checksums, normalization contract, and source identity. |
| `data/sources/bts_on_time_2026_05_nyc.jsonl` | Tracked 1,978-row normalized JFK/EWR/LGA snapshot for 2026-05-19/20. |

## Decision-Record Reference

| Artifact | Status |
| --- | --- |
| `docs/atcscc_decision_record_explorer_design.md` | Query and evidence contract implemented on `main`; browser layer paused. |
| `docs/atcscc_decision_record_explorer_cases.md` | Source-audited Ground Stop, GDP, and missing-reason acceptance cases. |
| `codex/kg-visualization-research` | Separate branch containing the reviewed read-only visualization; not merged into `main`. |

## Generated Runtime Artifacts

`agent-system build-corpus` is the only persistent evidence writer. During a
build, the ignored corpus directory uses `.staging/` for resumable progress and
temporary per-case packages. The packages under `.staging/case_runs/` are
internal compiler inputs and are removed after successful normalization; they
are not a supported persistence or query contract. Legacy packages under
`data/runs/agent_system/` are likewise internal historical/debug material, not
the current public path.

A published `decision-case-corpus-v2` directory contains:

- `corpus_manifest.json`;
- `build_results.jsonl`;
- `artifacts.jsonl`;
- content-addressed `source_objects/<sha256>.txt`;
- `source_bindings.jsonl`;
- `cases.jsonl`;
- canonical `facts.jsonl`;
- `case_facts.jsonl`;
- `evidence_links.jsonl`;
- `profile_gaps.jsonl`;
- non-causal `context_associations.jsonl`;
- source-qualified `observations.jsonl`;
- rebuildable `kg.jsonl` and `kg.ttl`;
- rebuildable `neo4j_nodes.jsonl` and `neo4j_relationships.jsonl`.

The manifest registers counts and checksums and is published only when no build
result is `blocked`. Corpus v2 removes cross-run source and semantic-fact
duplication while preserving evidence bindings. It is the authoritative
persisted knowledge and read contract, not a recommendation artifact.
`agent-system ask --corpus-dir <corpus-dir>` reads the registered tables
without writing query results into the corpus.

Two ignored, corpus-bound sidecars remain outside canonical corpus identity:

- `agent_usage/agent_usage.jsonl` and
  `agent_usage/agent_usage_manifest.json` contain payload-free activation,
  bypass, outcome, call, token, and latency telemetry;
- `case_index/` contains the rebuildable Chroma decision-record index and
  `case_index_manifest.json`, bound to the corpus ID.

Neither sidecar is formal evidence or query authority. The case index can be
rebuilt from corpus v2, and Agent usage is operational telemetry rather than
model evaluation.

The live Agent evaluator writes detailed provider output under ignored
`data/corpus/agent_system/live-agent-smoke-v1/` storage. Only the sanitized JSON
and Markdown reports listed above are tracked. Offline fake/scripted tests
remain software checks; the recorded DeepSeek `deepseek-v4-pro` run used
temperature `0.0`, thinking disabled, and zero retries. It passed `0/5` trials:
three Assembly token-cap failures, one malformed Assembly contract, and one
Analysis answer/support-contract failure. Semantic Resolution was not evaluated
because no natural cohort ambiguity activated it.

The repeated real-provider experiment uses DeepSeek `deepseek-v4-pro`,
temperature `0.0`, thinking disabled, zero retries, and disabled local model
cache. It completed 12 cycles with 108 attempted and successful provider calls,
zero provider failures, 431,018 input tokens, and 89,148 output tokens.
Task-level acceptance was `0/60`: 48 Assembly output-token-cap failures and 12
Analysis answer/support-contract failures. These are repeated measurements of
five tasks, not 60 independent tasks. DeepSeek reported 396,928
prompt-cache-hit tokens and 34,090 prompt-cache-miss tokens from its automatic
input-prefix context cache; this was not cached-response replay, and the 108
provider response IDs were unique.

Its raw responses, parsed outputs, manifests, and per-cycle artifacts remain
ignored under
`data/corpus/agent_system/live-agent-experiment-v1/`. The ignored
`live-agent-experiment-v1-invalid-observer-phase/` and
`live-agent-experiment-v1-normalized-response-only/` siblings are excluded
local diagnostics, not part of the tracked result.

## Optional Evaluation Tracks

The following families are retained but are not default context:

| Family | Use |
| --- | --- |
| `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`, `RESULTS.md` | Historical or explicitly reactivated formal evaluation. |
| `src/aviation_agentic_ai/alignment_mve/` | Optional alignment comparison experiment. |
| `src/aviation_agentic_ai/cross_source/` | Earlier broad cross-source, weather, and RAG implementation. |
| `data/evaluation/nasa_atmonto/` | Reviewed extraction-evaluation material. |
| `data/evaluation/cross_source/` | Alignment and cross-source calibration/evaluation material. |
| `data/experiments/nasa_atmonto/formal/` | Formal extraction experiment inputs and outputs. |
| `reports/stages/nasa_atmonto_*` | Formal extraction, validation, retrieval, and answer reports. |
| `reports/stages/cross_source_*` | Cross-source design and evaluation history. |

These artifacts may support a future evaluation task. They do not define the
current system goal and must not be presented as external expert certification.

## Historical Context

| Family | Safe use |
| --- | --- |
| `docs/archive/phak_era/` | Earlier PHAK ontology and GraphRAG method history. |
| `docs/archive/governance_era/` | Superseded governance and thesis-first planning. |
| `reports/phak_era_archive/` | Historical review and prototype evidence. |
| older `reports/stages/*web_demo*`, `*chunking*`, `*hybrid_rag*` | Explicit historical comparison only. |
| `reports/final/` | Draft and historical presentation material; not current system truth. |

Do not batch-rewrite historical reports merely to make their dated language
look current. Keep them out of default context instead.

Superseded execution debris, including byte-identical comparison snapshots,
old role-specific prompt reports, and completed internal handoffs, is preserved
in Git history rather than retained as active tracked artifacts. Reactivate it
only through an explicit historical or comparison task.

## Ignored Local Material

| Path | Policy |
| --- | --- |
| `data/runs/agent_system/` | Legacy/internal per-case runs and debug packages; not the current persistence or read contract. |
| `data/corpus/agent_system/` | Current local corpora, transient staging, provider artifacts, and corpus-bound sidecars; ignored and environment-specific. |
| `outputs/` | Scratch and mixed-branch outputs. |
| `reports/archive/` | Local archived reports. |
| vector indexes and model caches | Rebuild locally; do not commit. |
| `.env` and credentials | Never commit or print. |

## Admission Policy

A new tracked artifact must have:

- a clear owner or producing command;
- declared inputs and outputs;
- a current, optional, generated, or historical classification;
- a reason it must be tracked rather than regenerated;
- no credentials or hidden model reasoning.

Unknown artifacts are preserved, classified, and routed. They are not silently
deleted or promoted into current context.

## Audit Commands

```bash
git status --short
git ls-files
git grep -n -E '<pattern>' -- \
  AGENTS.md CLAUDE.md README.md RESEARCH_AUDIT.md GOALS.md TODO.md \
  ARTIFACT_INDEX.md REPRODUCIBILITY.md docs src tests
```

Use tracked-file scans for context hygiene. Broad filesystem scans can include
ignored runs and obsolete local archives.
