# Reproducibility

Last updated: 2026-07-31

This is the current ingestion-first TMI-event workflow. Historical experiments
remain discoverable through `ARTIFACT_INDEX.md`; they are not the default
execution path.

## Environment

- Python: 3.11 or newer.
- Package manager: `uv`.
- Supported development platforms: macOS and Linux.

```bash
uv sync --extra dev --extra ontology-generation --extra neo4j \
  --extra tmi-event-retrieval
uv run aviation-ai agent-system --help
```

`ontology-generation` supplies the model/tool runtime. `neo4j` is needed only
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

## Persistent Store

`configs/cross_source_v1.yaml` declares the dataset identity and default store
root:

```text
data/stores/aviation/cross-source-2026-05-v1/
  aviation_evidence.sqlite3
  chroma/
  exports/
```

The SQLite database is authoritative. It holds immutable source assets and
versions, anchors, ingestion results, active and historical event
publications, accepted semantic facts, provenance, profile gaps, Weather
associations, public observations, source chunks, FTS5 data, vector-index
state, and compact Agent usage telemetry.

The store uses a knowledge revision to bind rebuildable vector indexes and
evaluation runs to an exact semantic state. It opens directly from SQLite; no
batch manifest is required.

## Ingest Source Data

Ingest the three reason-state regression records:

```bash
uv run aviation-ai agent-system ingest \
  --config configs/cross_source_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --source-id 2026-05-19:123 \
  --source-id 2026-05-19:138 \
  --source-id 2026-05-20:020 \
  --allow-live-model \
  --allow-model-download
```

`--source-id` bounds semantic event construction, but ingestion still registers
configured immutable source versions so source retrieval is not restricted to
three hand-built records. Omit the option to process all 718 configured
advisories.

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

Complete source-supported records use deterministic Event Evidence Integration.
`--allow-live-model` authorizes live Semantic Resolution only when genuine
authority ambiguity remains. It does not prove that a model call occurred.
Store `DEEPSEEK_API_KEY` and any optional `DEEPSEEK_BASE_URL` only in ignored
local environment files.

## Rebuild Retrieval Indexes

SQLite FTS5 is maintained from stored source chunks. Rebuild both Chroma
collections from the authoritative store with:

```bash
uv run --extra tmi-event-retrieval aviation-ai agent-system reindex \
  --config configs/cross_source_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

The collections are:

```text
aviation_source_chunks_v1
tmi_events_v1
```

The first permitted run may download the embedding model. Later runs can omit
`--allow-model-download` when the model is local. A collection is attached to
the Query Agent only when its representation version, embedding model,
dimension, counts, dataset identity, and indexed knowledge revision match the
store.

Source vectors discover candidate source versions. TMI event vectors encode a
compact representation of event type, canonical facility, declared-reason
state/value, UTC time-of-day, and duration bucket. Neither index represents
causality, effectiveness, or a recommended action.

## Ask Natural-Language Questions

```bash
uv run aviation-ai agent-system ask \
  --config configs/cross_source_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --event-id <event-id> \
  --question "What forecast was available when this TMI was issued?" \
  --allow-model-download
```

Every valid request activates the configured Query Agent. The model must
retrieve before answering and may choose:

```text
find_tmi_events
read_tmi_event_facts
read_tmi_operational_context
read_public_observations
read_tmi_event_graph
find_similar_tmi_events
search_source_text
semantic_search_sources
read_source
```

Scope hints such as `--source-id`, `--source-family`, `--event-type-iri`,
`--facility-id`, `--reason-status`, `--reason-value`, `--offset`, `--limit`,
and `--candidate-scope` bound tool access. They do not select a hard-coded
answer route.

Lexical and semantic searches return candidates, not final source support.
For a source-record statement the Agent must follow discovery with
`read_source`, which returns an exact immutable version and anchor.

Example metadata-conditioned event question:

```bash
uv run --extra tmi-event-retrieval aviation-ai agent-system ask \
  --config configs/cross_source_v1.yaml \
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
  --config configs/cross_source_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --event-id <event-id> \
  --output-dir data/stores/aviation/exports/selected-event
```

The package includes event, fact, evidence, profile-gap, Weather-association,
public-observation, source-version, source-anchor, JSONL KG, RDF/Turtle, and
Neo4j projection files plus an export manifest. It is not a replay directory or
a query dependency.

Load the current formal projection into Neo4j:

```bash
uv run aviation-ai agent-system neo4j-export \
  --config configs/cross_source_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1
```

Neo4j loading returns `blocked` when credentials or connectivity are
unavailable. RDF/Turtle and Neo4j remain rebuildable offline products.

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

After building and indexing the bounded store, run the ingestion-first
Query Agent compatibility smoke only with explicit authorization:

```bash
uv run python -m aviation_agentic_ai.agent_system.live_agent_evaluation \
  --config configs/cross_source_v1.yaml \
  --suite data/evaluation/agent_system/live_ingestion_hybridrag_smoke_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --output-dir data/corpus/agent_system/live-ingestion-hybridrag-smoke-v1 \
  --report-dir reports/stages \
  --allow-live-model \
  --repetitions 1
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
raw responses:
  data/corpus/agent_system/live-ingestion-hybridrag-smoke-v1/raw_responses_v4.jsonl
parsed outputs:
  data/corpus/agent_system/live-ingestion-hybridrag-smoke-v1/live_evaluation_results_v4.jsonl
```

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
