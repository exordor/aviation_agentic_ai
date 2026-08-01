# Artifact Index

Last updated: 2026-08-01

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
| `docs/flagship_gdp138_walkthrough.md` | Historical pre-family-router real-provider walkthrough for the GDP 138 TMI slice. |
| `docs/figures/flagship_gdp138_live_trace.{drawio,png}` | Historical observed GDP 138 Query Agent trace; not a current family-router trace. |
| `docs/figures/heterogeneous_source_formats.{drawio,png}` | Supporting source-format and normalization figure. |
| `src/aviation_agentic_ai/agent_system/` | Active implementation. |
| `tests/test_agent_system*.py`, `tests/test_cli_agent_system.py` | Focused acceptance surface. |
| `configs/aviation_knowledge_v1.yaml` | Active composition entrypoint. |
| `configs/runtime/aviation_knowledge_v1.yaml` | Runtime, storage, and retrieval settings. |
| `configs/sources/aviation_knowledge_v1.yaml` | Source locations, checksums, and source URLs. |
| `configs/datasets/aviation_knowledge_v1.yaml` | Dataset, role, temporal-domain, and bounded-selection metadata. |
| `configs/prompts/tmi_event_agents_v1.yaml` | Current Query and Semantic Resolution prompt catalog. |
| `data/ontology/curated/atmonto_application_profile_v1.json` | Active ATMONTO TMI application profile. |
| `data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json` | Curated Weather report profile. |
| `data/ontology/curated/public_observation_slice.json` | Source-qualified BTS public-observation profile. |
| `data/evaluation/agent_system/live_ingestion_hybridrag_smoke_v1.yaml` | Ingestion-first Query Agent compatibility-smoke contract; no result implied. |
| `reports/stages/agent_system_live_ingestion_hybridrag_smoke_v1.{json,md}` | Verified persistent-store smoke: 6/6 returned real calls, 1/3 tasks accepted, and two answer-contract/evidence failures; not a benchmark. |
| `data/evaluation/agent_system/live_flagship_gdp138_walkthrough_v1.yaml` | One-question, natural-language GDP 138 system-walkthrough contract; no result implied by the suite alone. |
| `reports/stages/agent_system_live_flagship_gdp138_walkthrough_v1.{json,md}` | Verified historical pre-family-router walkthrough: 3/3 real calls succeeded, the one task passed, and raw/parsed binding was valid; `live_smoke`, not current-runtime acceptance. |
| `data/evaluation/agent_system/live_hybridrag_cross_domain_v1.yaml` | Six-task natural-language TMI/Flight/Weather/Sector/cross-domain/insufficient smoke contract. |
| `reports/stages/live_hybridrag_cross_domain_v1.{json,md}` | Verified real-provider smoke: 33/33 calls returned, routing/retrieval 6/6, grounding/answer 5/6; one preserved insufficient stop-policy failure. |
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
- active and historical generic knowledge-root publications, including TMI and
  Flight/Airspace roots;
- semantic facts, root membership, and evidence links;
- profile gaps, non-causal Weather associations, and public observations;
- source chunks and an FTS5 lexical index;
- vector-index state and payload-free Agent usage telemetry.

The TMI slice is rooted at an admitted ATMONTO TMI instance. Other active root
kinds use the same generic publication spine. Root membership is an
organization relation for accepted knowledge; it does not assert a
reconstructed decision process. Weather associations are non-causal. Admitted
BTS observations remain source-bound formal facts under their own profile.

## Rebuildable Indexes And Exports

The `chroma/` directory contains two derived collections:

- `aviation_source_chunks_v1` for semantic source discovery;
- `tmi_events_v1` for metadata-conditioned TMI event retrieval.

SQLite FTS5 supplies lexical source search. Both Chroma collections are
rebuildable from SQLite and are usable only when their recorded knowledge
revision matches the store. They do not publish semantic facts.

`export-event` creates a bounded event package with exact referenced source
versions and anchors. `neo4j-export` first builds current all-root JSONL,
RDF/Turtle, and property-graph files under `exports/`, then loads the Neo4j
projection.
Export manifests record checksums for interchange and inspection only; the
Query Agent does not require them.

## Current Evaluation Contracts

Live-evaluation suites bind directly to an existing store revision and current
vector-index state. Their detailed provider responses, parsed outputs, and
bindings belong under ignored local evaluation paths. Sanitized reports should
be tracked only after a completed run is independently verified.

No suite file is itself evidence that an experiment ran. The tracked
ingestion-first compatibility, flagship walkthrough, and cross-domain smoke
reports are bound to ignored raw and parsed artifacts with checksums. The
cross-domain smoke covers six task categories but is not a frozen evaluation
set; no frozen post-cutover evaluation set currently exists.

## Historical Compatibility Evidence

The following tracked artifacts are frozen historical evidence and are not
current role, persistent-store, or cross-family results:

| Artifact | Safe interpretation |
| --- | --- |
| `data/evaluation/agent_system/live_agent_smoke_v1.yaml` | Retired one-shot five-task contract. |
| `reports/stages/agent_system_live_agent_smoke_v1.{json,md}` | Historical 0/5 acceptance result under the retired runtime. |
| `data/evaluation/agent_system/live_agent_experiment_v1.yaml` | Retired repeated five-task contract. |
| `reports/stages/agent_system_live_agent_experiment_v1.{json,md}` | Historical 108/108 provider-call result with 0/60 task acceptance. |
| external archive `data/evaluation/agent_system/live_agent_smoke_v2.yaml` | Pre-cutover current-query compatibility contract; moved out of the runtime checkout. |
| external archive `reports/stages/agent_system_live_agent_smoke_v2.{json,md}` | Historical pre-cutover one-shot result; moved out of the runtime checkout. |
| external archive `data/evaluation/agent_system/live_agent_experiment_v2.yaml` | Pre-cutover repeated compatibility contract; moved out of the runtime checkout. |
| external archive `reports/stages/agent_system_live_agent_experiment_v2.{json,md}` | Historical 120-call result; moved out of the runtime checkout. |
| external archive `data/evaluation/agent_system/live_agent_smoke_v3.yaml` | Superseded event-centered construction/query contract; moved out of the runtime checkout. |
| external archive `data/evaluation/agent_system/live_agent_experiment_v3.yaml` | Superseded repeated construction/query contract; moved out of the runtime checkout. |
| `data/evaluation/agent_system/live_agent_smoke_v4.yaml` | Superseded pre-ingestion-first Query Agent compatibility contract. |
| `reports/stages/agent_system_live_agent_smoke_v4.{json,md}` | Historical 11-call, 5/5 compatibility result; retained only for compatibility tests and not evidence for the persistent-store runtime. |
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
| external archive `docs/superpowers/specs/decision-case-*` | Superseded planning/specification history. |
| former `docs/figures/decision_case_*_architecture.*` | Superseded figures retained through Git history, not current documentation. |
| external archive `docs/legacy_runtime/` | Superseded cross-source, extractor/critic/refiner, PHAK annotation, and snapshot-projection designs. |
| external archive `docs/legacy_runtime/thesis_writing_spine.md` | Superseded thesis scaffold for the former extraction pipeline. |
| external archive `docs/legacy_runtime/` | Historical authority-model and snapshot-projection guides for the former pipeline. |
| `codex/kg-visualization-research` | Paused read-only browser prototype on a separate branch. |

Historical names in this section are references, not accepted current
interfaces. Their bodies and recorded results remain unchanged.

## Optional Evaluation And Research Tracks

| Family | Use |
| --- | --- |
| external archive `docs/legacy_runtime/{RESEARCH_QUESTIONS,HYPOTHESES,EXPERIMENTS,RESULTS}.md` | Historical or explicitly reactivated formal evaluation. |
| `src/aviation_agentic_ai/alignment_mve/` | Optional alignment comparison. |
| external archive `src/legacy_runtime/` | Retired source packages, root CLI wrappers, and helper scripts from the pre-ingestion architecture. |
| external archive `tests/legacy_runtime/` | Tests for retired packages; preserved for historical review, not collected by the current suite. |
| external archive `data/legacy_runtime/` | Retired evaluation and experiment inputs. |
| external archive `reports/legacy_runtime/` | Formal extraction, cross-source, AIRM-O, and PHAK-era evaluation history. |
| external archive `reports/stages/` (literature/roadmap summaries) | Reports with no supported runtime or test dependency; the exact moved filenames are preserved in the dated archive. |
| external archive `docs/archive/`, `reports/phak_era_archive/` | Archived method, review, and presentation history; not in the default checkout. |
| `reports/final/atcscc_thesis_report_outline.md` | Current ingestion-first ATCSCC thesis report spine. |
| `reports/final/atcscc_defense_deck_outline.md` | Current ingestion-first ATCSCC defense deck spine. |
| `reports/final/README.md` | Entry map separating current deliverables from historical presentation material. |
| `reports/final/` remaining files | Historical thesis, PHAK, and superseded presentation material unless explicitly marked current. |

These artifacts may support a future task. They do not establish current
performance or external expert certification.

The external archive location and retention policy are documented in
[`docs/repository_artifact_policy.md`](docs/repository_artifact_policy.md).

The retired cross-source, PHAK chunk/index/query/demo/agent, ontology, source,
CQ, and report groups are not registered on the supported root CLI. Their
source modules, tests, and helper scripts now live in the dated external
archive rather than in the importable package. They are historical material,
not compatibility interfaces.

The following data is retained only as historical research input in the dated
external archive:

- external archive `data/legacy_runtime/nasa_atmonto/`;
- external archive `data/legacy_runtime/formal_experiments/`;
- external archive `data/legacy_runtime/airm_o/` and non-NASA Icarus files;
- external archive `data/legacy_runtime/ntrs_ontology_selection/`.

These are legacy research inputs, not current Agent-runtime knowledge. Do not
add new production or Query Agent dependencies to them. The active semantic
authority is limited to the curated profile and its six checksum-pinned NASA
OWL files under `data/ontology/external/icarus_ontology/NASA/`.

## Ignored Local Material

| Path | Policy |
| --- | --- |
| `data/runs/agent_system/` | Legacy/internal run and debug packages. |
| `data/evaluation_runs/agent_system/` | Current ignored raw provider responses, parsed outputs, bindings, and query traces; never a knowledge store. |
| `data/corpus/agent_system/` | Retired-path quarantine for sensitive artifacts left by older checkouts; never create or read it in the current runtime. |
| `data/stores/aviation/` | Current ignored SQLite stores, Chroma indexes, and optional exports. |
| local live-evaluation output directories | Raw provider responses, parsed outputs, and binding artifacts; keep ignored. |
| `outputs/` | Scratch and mixed-branch outputs. |
| vector/model caches | Rebuild locally; do not commit. |
| `.env` and credentials | Never commit or print. |

Tracked live-evaluation reports are immutable historical execution records.
They preserve the artifact locations recorded when each run occurred, even
when a retained local copy has since moved. See
[`docs/evaluation_artifact_relocations.md`](docs/evaluation_artifact_relocations.md)
for the explicit old-to-new mapping. No file under the evaluation-runs root is
part of the authoritative knowledge store.

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
