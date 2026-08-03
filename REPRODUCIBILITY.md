# Reproducibility

Last updated: 2026-08-02

This is the current ingestion-first cross-domain aviation workflow. Historical
experiments remain governed by `docs/repository_artifact_policy.md`; they are not the
default execution path.

This file is authoritative for executable procedures and source bindings only.
Current implementation status and evaluation observations belong to
`RESEARCH_AUDIT.md`; copied counts or run summaries here do not define the
research scope.

## Environment

- Python: 3.11 or newer.
- Package manager: `uv`.
- Supported development platforms: macOS and Linux.

```bash
uv sync --extra dev --extra agent-system --extra neo4j \
  --extra tmi-event-retrieval
uv run aviation-ai agent-system --help
```

`agent-system` supplies the active model/tool runtime. `neo4j` is needed only
for optional database loading. `tmi-event-retrieval` supplies Chroma and the
Sentence Transformers encoder.

## Source Snapshot Preflight

The advisory JSONL, terminology seed, Weather inputs, and BTS snapshot are
tracked. The pinned FAA NASR ZIP is intentionally ignored because of its size.
Obtain and verify it before ingesting eligible events:

```bash
NASR_DIR=data/raw/nasa_atmonto/2026-05-14/faa_nasr
NASR_ZIP="$NASR_DIR/28DaySubscription_Effective_2026-05-14.zip"
mkdir -p "$NASR_DIR"
curl -L --fail \
  "https://nfdc.faa.gov/webContent/28DaySub/28DaySubscription_Effective_2026-05-14.zip" \
  -o "$NASR_ZIP"
uv run python -c \
  'import hashlib,pathlib,sys; expected="db4793352229c1fd74e9b3d924762376abfa224fe6388768cad25d084c7aeed3"; actual=hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest(); print(actual); raise SystemExit(actual != expected)' \
  "$NASR_ZIP"
```

The tracked context inputs are:

```text
data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_metar.jsonl
data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_taf.jsonl
data/sources/bts_on_time_2026_05_manifest.json
data/sources/bts_on_time_2026_05_nyc.jsonl
```

Do not replace a pinned source implicitly during an ordinary ingestion run.

## Flight And Airspace Sources

The active top-level config composes three files:

```text
configs/aviation_knowledge_v1.yaml
  -> configs/runtime/aviation_knowledge_v1.yaml
  -> configs/sources/aviation_knowledge_v1.yaml
  -> configs/datasets/aviation_knowledge_v1.yaml
```

They separate runtime/storage settings, source locations and pinned source
checksums, and dataset/temporal-scope metadata. The configured Flight/Airspace
domain includes the public NASA ATMONTO July 2014 sample plus a bounded May
2026 operational-source slice. Their temporal-domain identifiers remain
distinct and cross-temporal joins are prohibited.

`ingest` prints `resolved_config_sha256`, a canonical SHA-256 over the fully
composed mapping. This records the exact resolved configuration used for a
run; the store's knowledge revision remains content-driven and is not replaced
by configuration identity.

Required ignored inputs and checksums are declared in the source and dataset
config files. Ingest the Flight/Airspace domain with:

```bash
uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/aviation-knowledge-2026-05-v1 \
  --domain flight-airspace
```

This publishes Flight, Aircraft/Model, Airport/ARTCC, Route, TrackPoint,
Sector, Weather, and reviewed association roots through the same generic
publication spine used by the TMI domain.

## Optional Web Evidence Sidecar

Web Evidence is a separate, opt-in ingestion domain. The tracked configuration
keeps `sources.web_evidence.enabled: false`, so ordinary `ingest` and
`--domain all` runs make no sidecar calls. Start a pinned Wigolo `0.2.1`
sidecar separately, then use a local composed configuration that enables the
approved seed and allowlist. The sidecar is an acquisition adapter only; the
project persists fetched content, immutable source versions, anchors, and FTS
chunks in the same SQLite store. A sidecar failure does not roll back TMI or
Flight/Airspace publications.

See [`docs/wigolo_web_evidence_operations.md`](docs/wigolo_web_evidence_operations.md)
for the loopback REST boundary, external scheduling, failure states, and the
no-vendor/AGPL-3.0 distribution policy. Wigolo is not a project dependency;
the adapter is tested against its pinned REST contract.

With that local configuration, the reproducible entry point is:

```bash
uv run aviation-ai agent-system ingest \
  --config /path/to/local/web-enabled-aviation-knowledge.yaml \
  --store-dir data/stores/aviation/aviation-knowledge-web-v1 \
  --domain web \
  --allow-live-web
```

`--allow-live-web` is a second runtime authorization gate. Without both the
configuration flag and this option, the domain returns a no-call disabled or
unauthorized status. Search/research and answer-synthesis capabilities are not
accepted by the ingestion adapter; retrieved web pages remain source evidence,
not generated claims.

### Historical Competency Supplement

The F1/F3S/S4/S1S supplement is retained as report-only historical evidence;
it is no longer a supported runtime command. The old Python runner was retired
with the ingestion-first cutover and must not be invoked as a current
reproduction step.

Its checksum-bound source manifest is
`configs/flight_competency_v1.yaml`. It pins:

- the published NASA `atmontoPlus` 2014 flight/sector sample;
- the complete BTS May 2026 on-time archive;
- the FAA NASR 2026-05-14 cycle;
- the FAA 2026-07-28 releasable aircraft registry, read only for technical
  manufacturer/model fields; and
- KATL routine and special METAR observations for 2026-05-14 through
  2026-05-22 from the IEM ASOS archive.

Raw files and the former runner are intentionally outside the active runtime.
The pinned historical outputs record:

| Query | Executed form | Result |
| --- | --- | ---: |
| F1 | Modern May 2026 proxy | 616 actual DL-reporting A319 departures |
| F3S | Modern KATL rain-time association | 81 departures |
| S4 | NASA 2014 sample, hour 02 UTC | KLGA airport sector: 12 distinct flights / 146 track-point bindings |
| S1S | NASA 2014 sample, `ZTLsector040` | 3 flight pairs |

F1 and F3S are explicitly modern proxies because the recovered NASA archive
does not contain the original 2012 KATL data. F3S is non-causal. S4 keeps both
counts because the appendix's `COUNT(?flight)` counts track-point bindings,
while the English question asks for distinct flights. The reports are retained
in the external historical archive described by
`docs/repository_artifact_policy.md`:

```text
../aviation_agentic_ai-research-archive-2026-08-01/reports/legacy_runtime/atmonto_competency_query_supplement_v1.json
../aviation_agentic_ai-research-archive-2026-08-01/reports/legacy_runtime/atmonto_competency_query_supplement_v1.md
```

## Persistent Store

The composed active configuration declares the dataset identity and default
store root:

```text
data/stores/aviation/aviation-knowledge-2026-05-v1/
  aviation_evidence.sqlite3
  chroma/
  exports/
```

The SQLite database is authoritative. It holds immutable source assets and
versions, anchors, ingestion results, active and historical event
publications, accepted semantic facts, provenance, profile gaps, Weather
associations, public observations, source chunks, FTS5 data, vector-index
state, compact Agent usage telemetry, Flight/Airspace domain records,
deterministic derivations, and cross-source associations.

The store uses a knowledge revision to bind rebuildable vector indexes and
evaluation runs to an exact semantic state. It opens directly from SQLite; no
batch manifest is required.

## Ingest Source Data

### Ontology-Grounded Document KG: FAA Chapter 18 Adapter

The pinned FAA JO 7210.3EE PDF and its checksum are declared in
`configs/sources/aviation_knowledge_v1.yaml`. The configured Chapter 18 scope
contains 26 sections, 159 numbered paragraphs, and 168 recursive extraction
chunks under the current 500-token/50-token-overlap configuration. Build the
authoritative source records first:

```bash
uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/chapter18-atmonto-kg-v1 \
  --domain document
```

Then execute the generic ontology-construction path. This command requires the
configured real provider and does not substitute fake, replayed, or cached
responses:

```bash
uv run aviation-ai agent-system build-kg \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/chapter18-atmonto-kg-v1 \
  --domain document \
  --allow-live-model
```

`--max-items <n>` limits recursive extraction chunks for a live smoke. Omit it
for the complete configured chapter. In `live_experiment` mode, raw provider
responses, parsed outputs, and their integrity manifest are written under the
gitignored directory
`data/evaluation_runs/agent_system/ontology-kg-live-v1/` (with a
`smoke-max-<n>` suffix when `--max-items` is used).

Rebuild `knowledge_entities_v1` with the ordinary `reindex` command and ask
free-form questions with the ordinary `ask` command; no FAA- or
document-specific query entry point is required.

Ingest the three reason-state regression records:

```bash
uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --domain tmi \
  --advisory-id 2026-05-19:123 \
  --advisory-id 2026-05-19:138 \
  --advisory-id 2026-05-20:020 \
  --allow-live-model \
  --allow-model-download
```

`--advisory-id` is an operator-facing targeted construction/backfill selector.
It is valid only with `--domain tmi` and registers only the named advisory
records plus shared authority and context evidence. Omit the option to process
all advisories in the explicitly selected TMI source configuration. This is an
ingestion choice, not a research-scope definition. `--domain all` is the
default; `--domain flight-airspace` runs only the other active ingestion
domain.

The pipeline:

1. registers source assets and immutable source versions;
2. loads shared schema, authority, Weather, and BTS resources once;
3. skips previously terminal `ok` or `insufficient` source versions;
4. runs deterministic preflight and bounded semantic processing;
5. sends the complete formal set through the Formal Publication Kernel;
6. commits each accepted event publication independently;
7. writes source-record chunks and attempts an incremental Chroma update.

A blocked record does not erase earlier accepted data. Repeating the same
command skips terminal versions and retries blocked versions. Semantic
publication remains valid if vector indexing fails.

The command reports `retrieval_indexes` separately as `updated`, `not_needed`,
`blocked`, or `not_applicable`. Do not infer semantic-ingestion failure from a
blocked rebuildable index; inspect the semantic counts and knowledge revision.

Complete source-supported records use deterministic Event Evidence Integration.
`--allow-live-model` authorizes live Semantic Resolution only when genuine
authority ambiguity remains. It does not prove that a model call occurred.
Store `DEEPSEEK_API_KEY` and any optional `DEEPSEEK_BASE_URL` only in ignored
local environment files.

## Rebuild Retrieval Indexes

SQLite FTS5 is maintained from stored source chunks. Rebuild all Chroma
collections from the authoritative store with:

```bash
uv run --extra agent-system aviation-ai agent-system reindex \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

The collections are:

```text
aviation_source_chunks_v1
tmi_events_v1
knowledge_entities_v1
```

The first permitted run may download the embedding model. Later runs can omit
`--allow-model-download` when the model is local. A collection is attached to
the Query Agent only when its representation version, embedding model,
dimension, counts, dataset identity, and indexed knowledge revision match the
store.

Source vectors discover candidate source versions. TMI event vectors encode a
compact representation of event type, canonical facility, declared-reason
state/value, UTC time-of-day, and duration bucket. Neither index represents
causality, effectiveness, or a recommended action. Knowledge-entity vectors
use published labels, class identity, accepted relation summaries, and source
anchors for discovery; exact claims still require graph and source reads.

## Ask Natural-Language Questions

```bash
uv run aviation-ai agent-system ask \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --question "What forecast was available when ATCSCC Advisory 138 was issued?" \
  --allow-model-download
```

Every valid request activates the configured Query Agent. The model must
retrieve before answering. A dedicated first model call selects one or more
tool families:

```text
source (3 tools)
  search_source_text
  semantic_search_sources
  read_source

tmi (6 tools)
  find_tmi_events
  read_tmi_event_facts
  read_tmi_operational_context
  read_public_observations
  read_tmi_event_graph
  find_similar_tmi_events

flight_airspace (9 tools)
  find_flights
  read_flight
  find_airports
  read_flight_trajectory
  find_sector_passages
  analyze_sector_traffic
  find_flight_weather_associations
  find_tmi_applicability_candidates
  read_aviation_graph

knowledge (3 tools)
  search_knowledge_entities
  find_knowledge_roots
  read_knowledge_graph
  shared exact reader: read_source
```

The evidence loop is bounded at 7 retrieval turns, 6 tool calls in one turn,
and 16 evidence-tool calls in total. If retrieval reaches a boundary after
collecting evidence, one tool-free Answer Formation turn receives a compact
Evidence Packet. Routing is LLM-mediated; it is not a fixed question registry
or keyword classifier.

Scope hints such as `--source-family`, `--event-type-iri`,
`--facility-id`, `--reason-status`, `--reason-value`, `--offset`, `--limit`,
and `--candidate-scope` bound tool access. They do not select a hard-coded
answer route.

Lexical and semantic searches return candidates, not final source support.
For a source-record statement the Agent must follow discovery with
`read_source`, which returns an exact immutable version and anchor.

Example metadata-conditioned event question:

```bash
uv run --extra agent-system aviation-ai agent-system ask \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --event-id <reference-event-id> \
  --question "Which prior TMI records are closest under the indexed event representation?" \
  --event-type-iri <exact-tmi-iri> \
  --facility-id <canonical-facility-id> \
  --reason-status formal \
  --reason-value weather \
  --candidate-scope prior \
  --allow-model-download
```

This is metadata-conditioned retrieval, not operational-situation similarity,
causal explanation, effectiveness, optimality, or recommendation.

## Optional Exports

Export one active event, its accepted facts, and only referenced source
versions and anchors:

```bash
uv run aviation-ai agent-system export-event \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --event-id <event-id> \
  --output-dir data/stores/aviation/exports/selected-event
```

The event package includes event, fact, evidence, profile-gap, Weather-association,
public-observation, source-version, source-anchor, JSONL KG, RDF/Turtle, and
Neo4j projection files plus an export manifest. It is not a replay directory or
a query dependency.

Load the current formal projection into Neo4j:

```bash
uv run aviation-ai agent-system neo4j-export \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1
```

The store-wide export includes accepted facts from every active formal
knowledge root, including TMI and Flight/Airspace roots, with publication and
provenance bindings. Neo4j loading returns `blocked` when credentials or
connectivity are unavailable. RDF/Turtle and Neo4j remain rebuildable offline
products.

## Acceptance Semantics

| Source ID | Required result |
| --- | --- |
| `2026-05-19:123` | Profile-gap declared reason; no formal `atm:impactingCondition`. |
| `2026-05-19:138` | Formal `weather`; evidence ends at `THUNDERSTORMS`. |
| `2026-05-20:020` | Missing declared reason; Weather/BTS cannot fill it. |
| `2026-05-19:108` | Formal `atm:ReRouteTMI` with `reRouteTimeType=ETD`; ARTCC scope is a profile gap. |
| `2026-05-20:137` | Formal `atm:ReRouteTMI` with `reRouteTimeType=ETD`; ARTCC scope is a profile gap. |

Weather associations remain non-causal. BTS observations are source-qualified
public observations and are never FAA demand, AAR, capacity, EDCT, decision
rationale, effectiveness, or caused outcomes.

## Live Compatibility And Evaluation

Offline fake/scripted tests validate software behavior only. They must not be
reported as LLM or Agent performance.

### GDP 138 Flagship Live Walkthrough

The flagship walkthrough is a historical pre-family-router TMI-slice run. It
used one natural-language cross-source question with the real configured
DeepSeek provider. The commands below rebuild its bounded evidence store and
both rebuildable indexes, but the tracked result is not current-runtime
acceptance:

```bash
uv run --extra agent-system aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
  --domain tmi \
  --advisory-id 2026-05-19:138

uv run --extra agent-system aviation-ai agent-system reindex \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

The former `live_agent_evaluation` compatibility harness and its v1/v4
suites are historical archive material. The current runtime equivalent is a
normal natural-language `ask` after the store and indexes have been built:

```bash
uv run aviation-ai agent-system ask \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
  --question "For ATCSCC Advisory 138 on 19 May 2026, what was published, what reason did the source declare, and what weather context was retained?"
```

This command produces a current runtime answer; it does not recreate the
archived v4 report byte-for-byte.

The verified run completed and passed. It used
`deepseek/deepseek-v4-pro`, temperature `0`, thinking disabled, and zero
retries. It recorded 3 attempted, 3 successful, and 0 failed real calls; 5
bound read-only tool executions; 72,409 input and 4,447 output tokens; and
74,354.468 ms provider plus 82.551 ms tool latency. The observed tool order
was:

```text
read_tmi_event_facts
search_source_text
read_source
read_tmi_operational_context
read_public_observations
```

Runtime artifact integrity for the retained local copy is shown below. The
tracked run report preserves its original at-run locations; the files were
relocated without changing their bytes. See
[`docs/evaluation_artifact_relocations.md`](docs/evaluation_artifact_relocations.md).

```text
raw provider responses:
  data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/raw_responses_v4.jsonl
  sha256 469f3343fee058431814cd931a5e2ba196fdf9fbf45833bb0c1585787c9c0f51
parsed trial outputs:
  data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/live_evaluation_results_v4.jsonl
  sha256 c6ab95d8051b94c4164238885c77c9431985cf0f848b5fe046754d27a7c99dff
sanitized query run:
  data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/hybrid_query_runs/flagship-cross-source-gdp138/hybrid_query_run.json
  sha256 b6124bf1058c12f63a6b330c504ecde9dd18b762076ab32878c1b3fea921d923
raw / parsed binding: valid
evaluation data binding:
  data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/evaluation_data_binding.json
  sha256 677341ac4f59024459a96ee2279a08e3cc9a1e2dd91348a85cf2927acd1b5a8b
```

See the reader-facing
[walkthrough](docs/flagship_gdp138_walkthrough.md), the tracked sanitized
[Markdown report](reports/evidence/agent_system_live_flagship_gdp138_walkthrough_v1.md),
and the tracked sanitized
[JSON report](reports/evidence/agent_system_live_flagship_gdp138_walkthrough_v1.json).
This is a `live_smoke / system walkthrough`, not a frozen holdout or a
statistical benchmark. Weather associations remain non-causal, and BTS public
observations are not FAA demand, capacity, AAR, EDCT, decision-input,
effectiveness, or recommendation evidence.

### Cross-Domain HybridRAG Live Smoke

Build one store containing both configured domains, then run the six ordinary
natural-language tasks:

```bash
uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/cross-domain-smoke-v1 \
  --domain flight-airspace

uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/cross-domain-smoke-v1 \
  --domain tmi \
  --advisory-id 2026-05-19:138 \
  --allow-model-download

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
EVAL_RUN_DIR="data/evaluation_runs/agent_system/live-hybridrag-cross-domain-v1-${RUN_ID}"

uv run python -m aviation_agentic_ai.agent_system.live_cross_domain_smoke \
  --config configs/aviation_knowledge_v1.yaml \
  --suite data/evaluation/agent_system/live_hybridrag_cross_domain_v1.yaml \
  --store-dir data/stores/aviation/cross-domain-smoke-v1 \
  --output-dir "$EVAL_RUN_DIR" \
  --report-dir "$EVAL_RUN_DIR/reports" \
  --allow-live-model
```

The verified run used `deepseek-v4-pro`, temperature 0, thinking disabled,
and zero retries. It recorded 33 attempted, 33 successful, and 0 failed real
calls; 265,691 input and 10,352 output tokens; and valid raw/trial binding.
Routing and retrieval passed all 6 tasks. Grounding and answer acceptance
passed 5/6: TMI, Flight, Weather, Sector, and TMI-applicability tasks passed.
For the unsupported actual-control/causal question, the Agent retrieved the
right candidate evidence but exhausted its 10-tool budget instead of stopping
with `insufficient`, so the task remained `blocked`. Preserve this as a
stop-policy failure.

The tracked report preserves the original at-run path. The retained local copy
was moved to the evaluation-runs root without changing its bytes; see the
[relocation index](docs/evaluation_artifact_relocations.md).

```text
raw provider responses:
  data/evaluation_runs/agent_system/live-hybridrag-cross-domain-v1/raw_provider_responses.jsonl
  sha256 18e2028b57f392a058c63b2c87efd33e9ca4e0002e809148bcbbf537b7cf3ece
parsed trial outputs:
  data/evaluation_runs/agent_system/live-hybridrag-cross-domain-v1/parsed_trial_outputs.jsonl
  sha256 856fafb8a8dd8842345d91b3d90fc9d19626e2a87ec081b1b80f06fae5f99af9
artifact integrity: verified
```

The tracked sanitized reports are
`reports/evidence/live_hybridrag_cross_domain_v1.{json,md}`. This is a
`live_smoke`, not a benchmark or causal/recommendation evaluation.

### Persistent-Store Compatibility Smoke

The former standalone `live_agent_evaluation` smoke runner and its v1 suite
are archived. For a current persistent-store compatibility check, use the
supported natural-language `ask` command (or the current cross-domain smoke
runner described above) after building the store:

```bash
uv run aviation-ai agent-system ask \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --question "What public operational situation is recorded for ATCSCC Advisory 138?"
```

Every smoke trial must use the configured real provider. Verify provider/model,
attempted/successful/failed calls, token use, tool calls, latency, store/index
binding, raw artifact location, parsed artifact location, and task acceptance
before reporting a result. A smoke is a compatibility check, not a statistical
benchmark.

The verified run recorded:

```text
provider / model: deepseek / deepseek-v4-pro
attempted / returned / provider-error calls: 6 / 6 / 0
task acceptance: 1 passed / 2 failed / 0 blocked
input / output tokens: 113806 / 5774
retained local raw / parsed artifacts: not present
```

The tracked historical report preserves the original raw and parsed artifact
locations and checksums. No retained local copy was available during the
2026-08-01 relocation, so those locations are not current reproduction
targets.

The tracked sanitized report records both artifact checksums. The two task
failures are preserved; successful provider calls are not counted as accepted
answers. The report also records `raw_parsed_binding_status=valid`.

Historical v1-v4 reports remain frozen under their recorded runtimes and must
not be relabeled as ingestion-first performance. A `live_experiment` additionally
requires the approved minimum successful real-provider calls and its captured
raw/parsed artifact integrity; it cannot substitute cached or fake responses.

## Verification

Focused current-path checks:

```bash
uv run --extra tmi-event-retrieval pytest -q \
  tests/test_agent_system_evidence_store.py \
  tests/test_agent_system_ingestion_pipeline.py \
  tests/test_agent_system_query_runtime.py \
  tests/test_agent_system_tmi_event_graph.py \
  tests/test_agent_system_tmi_event_retrieval_documents.py \
  tests/test_agent_system_tmi_event_retrieval_index.py \
  tests/test_agent_system_tmi_event_retrieval_search.py \
  tests/test_config.py \
  tests/test_agent_system_flight_airspace_query.py \
  tests/test_agent_system_cross_domain_live_smoke.py \
  tests/test_agent_system_hybrid_query_agent.py \
  tests/test_agent_system_hybrid_query_tools.py \
  tests/test_agent_system_hybrid_query_public.py \
  tests/test_agent_system_evidence_export.py \
  tests/test_agent_system_evaluation_binding.py \
  tests/test_cli_agent_system.py \
  tests/test_readme_commands.py
```

Final repository verification:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

Generated stores, Chroma indexes, exports, provider outputs, and evaluation
bindings are ignored and must remain uncommitted. Report commands, commit,
environment, store revision, and artifact checksums rather than a changing test
count as a durable result.
