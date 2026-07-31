# Reproducibility

Last updated: 2026-07-31

This is the current corpus-first TMI-event workflow. Historical experiments
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

`ontology-generation` supplies the LangChain/LangGraph runtime. `neo4j` is
needed only for database loading. `tmi-event-retrieval` supplies Chroma and the
Sentence Transformers encoder.

## Source Snapshot Preflight

The advisory JSONL, terminology seed, Weather inputs, and BTS snapshot are
tracked. The pinned FAA NASR ZIP is intentionally ignored because of its size.
Obtain and verify it before building eligible events:

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

Do not replace a pinned source snapshot implicitly during an ordinary build.

## Build A Corpus

`build-corpus` is the only persistent evidence writer. It selects advisory
records, performs deterministic preflight, runs eligible records sequentially,
and publishes a checksum-verified `tmi-event-corpus-v3`.

The frozen cohort has:

| State | Count |
| --- | ---: |
| Discovered | 718 |
| Selected | 68 |
| Active GDP/GS/ReRoute eligible | 46 |
| Incomplete core fields | 3 |
| Boundary notices | 18 |
| Deferred ReRoute cancellation | 1 |
| Deterministic preflight `insufficient` | 22 |

Build the five tracked cross-family regression records:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/smoke-v3 \
  --source-id 2026-05-19:123 \
  --source-id 2026-05-19:138 \
  --source-id 2026-05-19:108 \
  --source-id 2026-05-20:020 \
  --source-id 2026-05-20:137 \
  --allow-live-model
```

Build or resume the frozen cohort:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/cross-source-2026-05-v3 \
  --selection cohort \
  --allow-live-model \
  --resume
```

Eligible records require `--allow-live-model`, even when the complete evidence
is expected to use the deterministic zero-call path. Store `DEEPSEEK_API_KEY`
and any optional `DEEPSEEK_BASE_URL` only in ignored local environment files.

The 22 preflight insufficiencies use zero provider calls. A blocked provider or
workflow result does not stop later records, but it prevents final-manifest
publication. Repeating the command with `--resume` retries only blocked rows.

## Corpus v3 Layout

`corpus_manifest.json` has manifest version `tmi-event-corpus-v3` and registers
path, count, and SHA-256 for every table and projection:

```text
build_results.jsonl
artifacts.jsonl
source_objects/<sha256>.txt
source_bindings.jsonl
events.jsonl
facts.jsonl
event_facts.jsonl
evidence_links.jsonl
profile_gaps.jsonl
context_associations.jsonl
observations.jsonl
alignment_audit.json
tmi_coverage.json
kg.jsonl
kg.ttl
neo4j_nodes.jsonl
neo4j_relationships.jsonl
```

Important interpretation rules:

- `events.jsonl` catalogs admitted ATMONTO TMI instances;
- `event_facts.jsonl` attaches accepted facts to those events for storage and
  retrieval;
- `facts.jsonl` uses semantic identity independent of provenance;
- `evidence_links.jsonl` preserves one-to-many source support;
- `profile_gaps.jsonl` stays outside the formal graph;
- `context_associations.jsonl` is non-causal and excluded from formal graph
  projections;
- admitted BTS public-observation facts remain formal and source-bound;
- `alignment_audit.json` and `tmi_coverage.json` are rebuildable summaries, not
  additional publication authorities.

Corpus v3 is canonical. RDF/Turtle, Neo4j, the runtime event graph, and Chroma
are rebuildable projections.

## Build The TMI Event Index

```bash
uv run --extra tmi-event-retrieval aviation-ai agent-system index-events \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v3 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

The first permitted run may download the embedding model. Later runs may omit
`--allow-model-download` when it is already local.

The derived `tmi_event_index/` directory contains:

```text
tmi_event_index_manifest.json
tmi_event_documents.jsonl
chroma/
```

The representation includes TMI type, canonical facility, declared-reason
state/value, UTC time-of-day, and duration bucket. Exact filters precede cosine
recall. Weather, BTS observations, effectiveness, and recommendations are not
encoded.

## Ask A Natural-Language Question

```bash
uv run aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/smoke-v3 \
  --event-id <event-id-from-events.jsonl> \
  --question "What forecast was known when this TMI was issued?"
```

Every valid request activates the Query Agent. The model must retrieve before
answering and may select:

```text
find_tmi_events
read_tmi_event_facts
read_weather_context
read_public_observations
read_tmi_event_graph
find_similar_tmi_events
```

Scope hints such as `--event-type-iri`, `--facility-id`, `--reason-status`,
`--reason-value`, `--offset`, `--limit`, and candidate scope bound tool access;
they do not select a hard-coded answer route. The `ask` command has no
deterministic fallback. If the configured provider cannot be constructed, the
result is `blocked`.

Example similarity question:

```bash
uv run --extra tmi-event-retrieval aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v3 \
  --event-id <reference-event-id> \
  --question "Which historical TMI event is most similar?" \
  --event-type-iri <exact-tmi-iri> \
  --facility-id <canonical-facility-id> \
  --reason-status formal \
  --reason-value weather \
  --candidate-scope prior
```

The similarity result is metadata-conditioned retrieval, not a causal,
effectiveness, optimality, or recommendation result.

## Export

Export one bounded, non-replayable event:

```bash
uv run aviation-ai agent-system export-event \
  --corpus-dir data/corpus/agent_system/smoke-v3 \
  --event-id <event-id-from-events.jsonl> \
  --output-dir data/corpus/agent_system/export-selected-event
```

Load the full property-graph projection:

```bash
uv run aviation-ai agent-system neo4j-export \
  --corpus-dir data/corpus/agent_system/smoke-v3
```

Neo4j loading uses parameterized `MERGE`, preserves unrelated data, and returns
`blocked` when credentials or connectivity are unavailable.

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

## Current Live Evaluation Contracts

Offline fake/scripted tests validate software behavior only. They must not be
reported as LLM or Agent performance.

Run the current event-centered live smoke only with explicit authorization:

```bash
uv run python -m aviation_agentic_ai.agent_system.live_agent_evaluation \
  --config configs/cross_source_v1.yaml \
  --suite data/evaluation/agent_system/live_agent_smoke_v3.yaml \
  --output-dir data/corpus/agent_system/live-agent-smoke-v3 \
  --report-dir reports/stages \
  --allow-live-model \
  --repetitions 1
```

Run the current repeated experiment only under its approved real-provider
protocol:

```bash
uv run python -m aviation_agentic_ai.agent_system.live_agent_experiment \
  --config configs/cross_source_v1.yaml \
  --suite data/evaluation/agent_system/live_agent_experiment_v3.yaml \
  --output-dir data/corpus/agent_system/live-agent-experiment-v3 \
  --report-dir reports/stages \
  --allow-live-model
```

The v3 suites use the Event Evidence Integration and current Query Agent role,
event identities, and six tool names. No post-cutover result exists until one
of these commands is explicitly authorized, executed with the real configured
provider, and its raw/parsed artifacts and manifest are independently verified.

Tracked v1/v2 reports and later compact-selection compatibility runs predate the
event-centered semantic cutover. They remain GDP-biased historical evidence
and must not be relabeled as current performance.

## Verification

Focused current-path checks:

```bash
uv run --extra tmi-event-retrieval pytest -q \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_batch.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_agent_system_corpus_event_graph.py \
  tests/test_agent_system_tmi_event_retrieval_documents.py \
  tests/test_agent_system_tmi_event_retrieval_index.py \
  tests/test_agent_system_tmi_event_retrieval_search.py \
  tests/test_agent_system_tmi_event_retrieval_evaluation.py \
  tests/test_agent_system_hybrid_query_agent.py \
  tests/test_agent_system_hybrid_query_tools.py \
  tests/test_agent_system_hybrid_query_public.py \
  tests/test_cli_agent_system.py
```

Final repository verification:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

Generated corpora, `.staging/`, indexes, provider output, and event exports are
ignored and must remain uncommitted. Report commands, commit, environment, and
artifact checksums rather than a changing test count as a durable result.
