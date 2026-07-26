# Artifact Index

Last updated: 2026-07-26

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
| `configs/cross_source_v1.yaml` | Admitted ATCSCC, facility, terminology, Weather-context, and BTS-proxy source configuration. |
| `configs/prompts/agent_system_v1.yaml` | Versioned Agent-system prompt configuration. |
| `data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json` | Curated formal vocabulary for Weather report nodes only. |
| `data/sources/bts_on_time_2026_05_manifest.json` | Pinned BTS archive/member checksums, normalization contract, and source identity. |
| `data/sources/bts_on_time_2026_05_nyc.jsonl` | Tracked 1,978-row normalized JFK/EWR/LGA snapshot for 2026-05-19/20. |

## Decision-Record Reference

| Artifact | Status |
| --- | --- |
| `docs/atcscc_decision_record_explorer_design.md` | Query and evidence contract implemented on `main`; browser layer paused. |
| `docs/atcscc_decision_record_explorer_cases.md` | Source-audited Ground Stop, GDP, and missing-reason acceptance cases. |
| `codex/kg-visualization-research` | Separate branch containing the reviewed read-only visualization; not merged into `main`. |

## Generated Runtime Artifacts

Validated Agent-system runs are written under ignored local run directories and
may contain:

- `source_snapshot.json`;
- `source_snapshots.jsonl`;
- `run_manifest.json`;
- `fact_trace.jsonl`;
- `weather_fact_trace.jsonl`;
- `profile_gaps.jsonl`;
- `context_associations.jsonl`;
- `outcome_summaries.jsonl`;
- `kg.jsonl`;
- `kg.ttl`;
- `neo4j_nodes.jsonl`;
- `neo4j_relationships.jsonl`;
- optional `neo4j_load.json`;
- latest `query_run.json`.

These directories are reproducible, environment-specific, and may contain raw
provider material. Do not commit them. Summarize a selected run in a small
tracked report only when it supports a durable system claim.

`source_snapshot.json` is the compatibility snapshot for older single-source
runs. New runs use `source_snapshots.jsonl` as the canonical registry.
`context_associations.jsonl` and `outcome_summaries.jsonl` are audit-only:
Weather associations are non-causal and BTS summaries are public operational
proxies. Neither artifact is serialized as RDF or Neo4j relationships.

The run manifest owns the optional-layer publication state:

- `ok`: validated rows may be read within their declared layer;
- `insufficient`: no eligible evidence exists and the artifact is empty;
- `blocked`: checksum, schema, source binding, or validation failed and no
  rows are publishable.

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

## Ignored Local Material

| Path | Policy |
| --- | --- |
| `data/runs/agent_system/` | Reproducible local runs; never default context. |
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
