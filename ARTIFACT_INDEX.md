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
| `docs/architecture_narrative.md` | Shared positioning, five-plane terminology, and running-example contract. |
| `docs/multi_agent_kg_system_design.md` | Normative ATMONTO-grounded Agentic HybridRAG design. |
| `docs/figures/cross_source_evidence_motivated_example.{drawio,png}` | Flagship Figure 1: cross-source motivated example. |
| `docs/figures/aviation_hybridrag_system_architecture.{drawio,png}` | Flagship Figure 2: five-plane system architecture. |
| `docs/figures/bounded_query_agent_workflow.{drawio,png}` | Flagship Figure 3: Query Agent action-observation-evidence loop. |
| `docs/figures/heterogeneous_source_formats.{drawio,png}` | Supporting source-format and normalization figure. |
| `src/aviation_agentic_ai/agent_system/` | Active implementation. |
| `tests/test_agent_system*.py`, `tests/test_cli_agent_system.py` | Focused acceptance surface. |
| `configs/aviation_knowledge_v1.yaml` | Active dataset identity, persistent-store paths, source files, and retrieval model configuration. |
| `configs/prompts/tmi_event_agents_v1.yaml` | Current Query and Semantic Resolution prompt catalog. |
| `data/ontology/curated/atmonto_application_profile_v1.json` | Active ATMONTO TMI application profile. |
| `data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json` | Curated Weather report profile. |
| `data/ontology/curated/public_observation_slice.json` | Source-qualified BTS public-observation profile. |
| `data/evaluation/agent_system/live_ingestion_hybridrag_smoke_v1.yaml` | Ingestion-first Query Agent compatibility-smoke contract; no result implied. |
| `reports/stages/agent_system_live_ingestion_hybridrag_smoke_v1.{json,md}` | Verified persistent-store smoke: 6/6 returned real calls, 1/3 tasks accepted, and two answer-contract/evidence failures; not a benchmark. |
| `data/evaluation/agent_system/tmi_event_retrieval_smoke_v1.yaml` | Development metadata-ranking smoke set. |

## Canonical Runtime Artifacts

`agent-system ingest` is the persistent evidence writer. The configured store
root contains:

```text
aviation_evidence.sqlite3
chroma/
exports/
```

`aviation_evidence.sqlite3` is the authoritative runtime artifact. It contains:

- store metadata and a monotonically increasing knowledge revision;
- immutable source assets, logical sources, source versions, and anchors;
- ingestion results and ingestion-run summaries;
- active and historical TMI event publications;
- semantic facts, event membership, and evidence links;
- profile gaps, non-causal Weather associations, and public observations;
- source chunks and an FTS5 lexical index;
- vector-index state and payload-free Agent usage telemetry.

The ATMONTO TMI event is the formal root. Event membership is an organization
relation for accepted knowledge; it does not assert a reconstructed decision
process. Weather associations are non-causal and remain outside formal graph
facts. Admitted BTS observations remain source-bound formal facts under their
own profile.

## Rebuildable Indexes And Exports

The `chroma/` directory contains two derived collections:

- `aviation_source_chunks_v1` for semantic source discovery;
- `tmi_events_v1` for metadata-conditioned TMI event retrieval.

SQLite FTS5 supplies lexical source search. Both Chroma collections are
rebuildable from SQLite and are usable only when their recorded knowledge
revision matches the store. They do not publish semantic facts.

`export-event` creates a bounded event package with exact referenced source
versions and anchors. `neo4j-export` first builds current JSONL, RDF/Turtle, and
property-graph files under `exports/`, then loads the Neo4j projection.
Export manifests record checksums for interchange and inspection only; the
Query Agent does not require them.

## Current Evaluation Contracts

Live-evaluation suites bind directly to an existing store revision and current
vector-index state. Their detailed provider responses, parsed outputs, and
bindings belong under ignored local evaluation paths. Sanitized reports should
be tracked only after a completed run is independently verified.

No suite file is itself evidence that an experiment ran. The tracked
ingestion-first smoke report is bound to ignored raw and parsed artifacts with
checksums. Its three familiar records are development/regression fixtures only;
no frozen post-cutover evaluation set currently exists.

## Historical Compatibility Evidence

The following tracked artifacts are frozen historical evidence and are not
current role, persistent-store, or cross-family results:

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
| `data/evaluation/agent_system/live_agent_smoke_v4.yaml` | Superseded pre-ingestion-first Query Agent compatibility contract. |
| `reports/stages/agent_system_live_agent_smoke_v4.{json,md}` | Historical 11-call, 5/5 compatibility result; not evidence for the persistent-store runtime. |
| `data/evaluation/agent_system/live_agent_experiment_v4.yaml` | Superseded pre-ingestion-first repeated-measurement contract. |

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
| `docs/cross_source_multi_agent_v2_design.md` | Superseded cross-source V2 plan and retired CLI. |
| `configs/cross_source_v1.yaml` | Historical cross-source configuration retaining the deterministic 68-record NYC full-text code-match experiment; not the active `agent-system` configuration. |
| `docs/atcscc_agent_architecture.md` | Superseded extractor/critic/refiner Agent design. |
| `docs/thesis_writing_spine.md` | Superseded thesis scaffold for the former extraction pipeline. |
| `docs/pipeline_authority_model.md` | Historical authority-model framing for the former pipeline. |
| `docs/neo4j_visualization.md` | Historical snapshot-projection guide; current export command is in `REPRODUCIBILITY.md`. |
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

The retired `cross-source`, PHAK chunk/index/query/demo/agent, and legacy KG
groups are not registered on the supported root CLI. Their modules remain
historical implementation material rather than compatibility interfaces.

## Ignored Local Material

| Path | Policy |
| --- | --- |
| `data/runs/agent_system/` | Legacy/internal run and debug packages. |
| `data/corpus/agent_system/` | Historical local snapshots and provider artifacts; never a current query backend. |
| `data/stores/aviation/` | Current ignored SQLite stores, Chroma indexes, and optional exports. |
| local live-evaluation output directories | Raw provider responses, parsed outputs, and binding artifacts; keep ignored. |
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
