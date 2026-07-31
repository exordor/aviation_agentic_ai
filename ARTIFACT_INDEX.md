# Artifact Index

Last updated: 2026-07-31

This file routes project context. It distinguishes current contracts,
rebuildable outputs, optional evaluation material, and historical artifacts.

## Active Context

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Authoritative operational instructions. |
| `RESEARCH_AUDIT.md` | Default current-context router. |
| `GOALS.md` | Durable system goal and boundaries. |
| `README.md` | Current user-facing overview and commands. |
| `TODO.md` | Active execution queue only. |
| `docs/multi_agent_kg_system_design.md` | Normative event-centered system design. |
| `docs/figures/tmi_event_construction_architecture.{drawio,png}` | Editable and rendered construction architecture. |
| `docs/figures/tmi_event_retrieval_architecture.{drawio,png}` | Editable and rendered retrieval architecture. |
| `src/aviation_agentic_ai/agent_system/` | Active implementation. |
| `tests/test_agent_system*.py`, `tests/test_cli_agent_system.py` | Focused acceptance surface. |
| `configs/cross_source_v1.yaml` | ATCSCC, FAA authority, Weather, and BTS source configuration. |
| `configs/prompts/tmi_event_agents_v1.yaml` | Current Query and Semantic Resolution prompt catalog. |
| `data/ontology/curated/atmonto_application_profile_v1.json` | Active ATMONTO TMI application profile. |
| `data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json` | Curated Weather report profile. |
| `data/ontology/curated/public_observation_slice.json` | Source-qualified BTS public-observation profile. |
| `data/evaluation/agent_system/live_agent_smoke_v4.yaml` | Query-only compatibility-smoke contract; no result implied. |
| `reports/stages/agent_system_live_agent_smoke_v4.{json,md}` | Verified v4 compatibility smoke: 11 real calls and 5/5 accepted Query Agent tasks; not a frozen holdout. |
| `data/evaluation/agent_system/live_agent_experiment_v4.yaml` | Query-only repeated-measurement contract; no result implied. |
| `data/evaluation/agent_system/tmi_event_retrieval_smoke_v1.yaml` | Development metadata-ranking smoke set. |

## Canonical Runtime Artifacts

`agent-system build-corpus` is the only persistent evidence writer. A
successfully published `tmi-event-corpus-v3` directory contains:

- `corpus_manifest.json`;
- `build_results.jsonl`;
- `artifacts.jsonl`;
- content-addressed `source_objects/<sha256>.txt`;
- `source_bindings.jsonl`;
- `events.jsonl`;
- canonical `facts.jsonl`;
- `event_facts.jsonl`;
- `evidence_links.jsonl`;
- `profile_gaps.jsonl`;
- non-causal `context_associations.jsonl`;
- source-qualified `observations.jsonl`;
- `alignment_audit.json`;
- `tmi_coverage.json`;
- rebuildable `kg.jsonl` and `kg.ttl`;
- rebuildable `neo4j_nodes.jsonl` and `neo4j_relationships.jsonl`.

The manifest registers counts and checksums and is written only when no selected
record is blocked. Corpus v3 is the canonical persisted knowledge and read
contract.

The ATMONTO TMI event is the formal root. `event_facts.jsonl` is a corpus
membership table for accepted knowledge; it does not assert a reconstructed
decision process. Weather context associations are non-causal and stay outside
the formal KG. Admitted BTS observations remain source-bound formal facts under
their own profile.

Temporary `.staging/` packages support resumable construction and are removed
after successful normalization. They are not a public query backend.

## Rebuildable Sidecars

Two ignored sidecars remain outside canonical corpus identity:

- `agent_usage/agent_usage.jsonl` and
  `agent_usage/agent_usage_manifest.json` contain payload-free activation,
  bypass, outcome, call, token, and latency telemetry;
- `tmi_event_index/` contains
  `tmi_event_index_manifest.json`, `tmi_event_documents.jsonl`, and the
  rebuildable Chroma `tmi_events` collection.

Neither sidecar is formal evidence or an additional publication authority.
Agent usage is operational telemetry, not model-quality evaluation. The vector
index must be rebuilt when the bound corpus ID changes.

## Current Evaluation Contracts

The v4 live-suite configurations use:

- the always-on `query` role only;
- TMI event identities;
- the six current read-only HybridRAG tool names, including cross-source graph
  paths and metadata-conditioned ranking;
- real-provider capture rules when live execution is explicitly authorized.

Their detailed raw responses, parsed outputs, manifests, and local corpora
belong under ignored `data/corpus/agent_system/` paths. Sanitized reports should
be tracked only after a completed run is independently verified.

No suite file is itself evidence that an experiment ran. The five familiar
records are development/regression fixtures only. No frozen post-cutover
evaluation set currently exists; `future_frozen_evaluation` is
`NOT CONSTRUCTED`.

## Historical Compatibility Evidence

The following tracked artifacts are frozen historical evidence and are not
current role, corpus, or cross-family results:

| Artifact | Safe interpretation |
| --- | --- |
| `data/evaluation/agent_system/live_agent_smoke_v1.yaml` | Retired one-shot five-task contract. |
| `reports/stages/agent_system_live_agent_smoke_v1.{json,md}` | Historical 0/5 acceptance result under the retired runtime. |
| `data/evaluation/agent_system/live_agent_experiment_v1.yaml` | Retired repeated five-task contract. |
| `reports/stages/agent_system_live_agent_experiment_v1.{json,md}` | Historical 108/108 provider-call result with 0/60 task acceptance. |
| `data/evaluation/agent_system/live_agent_smoke_v2.yaml` | Pre-cutover current-query compatibility contract. |
| `reports/stages/agent_system_live_agent_smoke_v2.{json,md}` | Historical pre-cutover one-shot result. |
| `data/evaluation/agent_system/live_agent_experiment_v2.yaml` | Pre-cutover repeated compatibility contract. |
| `reports/stages/agent_system_live_agent_experiment_v2.{json,md}` | Historical 120-call result; repeated GDP query passed, former construction tasks failed. |
| `data/evaluation/agent_system/live_agent_smoke_v3.yaml` | Superseded event-centered construction/query contract. |
| `data/evaluation/agent_system/live_agent_experiment_v3.yaml` | Superseded repeated construction/query contract. |

Later compact-selection and 10,000-token runs are also pre-cutover,
GDP-biased compatibility evidence. The v3 contracts are likewise superseded
construction-role compatibility artifacts. None may be presented as current v4,
representative cross-family, independent-sample, or model-quality results.

Do not rewrite historical report bytes to use current role names.

## Historical Design References

| Artifact | Status |
| --- | --- |
| `docs/atcscc_decision_record_explorer_design.md` | Historical user-story and evidence-contract reference; not current architecture. |
| `docs/atcscc_decision_record_explorer_cases.md` | Historical source audit behind three regression fixtures. |
| `docs/superpowers/specs/decision-case-*` | Superseded planning/specification history. |
| former `docs/figures/decision_case_*_architecture.*` | Superseded figures retained through Git history, not current documentation. |
| `codex/kg-visualization-research` | Paused read-only browser prototype on a separate branch. |

Historical names in this section are references, not accepted current
interfaces. Their bodies and recorded results remain unchanged.

## Optional Evaluation And Research Tracks

| Family | Use |
| --- | --- |
| `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`, `RESULTS.md` | Historical or explicitly reactivated formal evaluation. |
| `src/aviation_agentic_ai/alignment_mve/` | Optional alignment comparison. |
| `src/aviation_agentic_ai/cross_source/` | Earlier broad Weather/RAG implementation. |
| `data/evaluation/nasa_atmonto/` | Extraction-evaluation material. |
| `data/evaluation/cross_source/` | Alignment and cross-source calibration. |
| `reports/stages/nasa_atmonto_*` | Formal extraction/validation history. |
| `reports/stages/cross_source_*` | Cross-source design and evaluation history. |
| `docs/archive/`, `reports/phak_era_archive/`, `reports/final/` | Archived method and presentation history. |

These artifacts may support a future task. They do not establish current
performance or external expert certification.

## Ignored Local Material

| Path | Policy |
| --- | --- |
| `data/runs/agent_system/` | Legacy/internal run and debug packages. |
| `data/corpus/agent_system/` | Current local corpora, staging, indexes, exports, and provider artifacts. |
| `outputs/` | Scratch and mixed-branch outputs. |
| vector/model caches | Rebuild locally; do not commit. |
| `.env` and credentials | Never commit or print. |

## Admission Policy

A new tracked artifact must have:

- a clear owner or producing command;
- declared inputs and outputs;
- a current, optional, generated, or historical classification;
- a reason it must be tracked instead of regenerated;
- no credentials, complete private prompts, or hidden model reasoning.

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
