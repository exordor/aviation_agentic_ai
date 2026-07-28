# Reproducibility

Last updated: 2026-07-28

This is the corpus-first Agent-system workflow. Historical experiments remain
available through `EXPERIMENTS.md`, but they are not the default path.

## Environment

- Python: 3.11 or newer; see `pyproject.toml`.
- Package manager: `uv`.
- Supported development platforms: macOS and Linux.

```bash
uv sync --extra dev --extra ontology-generation --extra neo4j
uv run aviation-ai agent-system --help
```

The `ontology-generation` extra supplies the LangChain and LangGraph runtime.
The `neo4j` extra is required only for database loading.

## Source Snapshot Preflight

The advisory JSONL and terminology seed are tracked. The pinned FAA NASR ZIP is
238 MB and intentionally ignored by Git. Obtain and verify it before an
eligible corpus build:

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

The local source manifest pins the FAA cycle. Do not replace the snapshot
implicitly during an ordinary build.

The build also consumes tracked normalized Weather inputs and the tracked
1,978-row BTS snapshot:

```text
data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_metar.jsonl
data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_taf.jsonl
data/sources/bts_on_time_2026_05_manifest.json
data/sources/bts_on_time_2026_05_nyc.jsonl
```

## Build A Corpus

The only persistent writer is `build-corpus`. It selects advisory records,
performs deterministic preflight, runs eligible cases sequentially, normalizes
their validated packages into corpus v2, and removes temporary case bundles
only after finalization.

The frozen cohort has 718 discovered advisories and this required ledger:

| State | Count |
| --- | ---: |
| Selected | 68 |
| Agent-eligible | 42 |
| Unsupported TMI | 23 |
| Incomplete core fields | 3 |
| Deterministic preflight `insufficient` | 26 |

Build the three tracked acceptance sources into an ignored smoke directory:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/smoke-v2 \
  --source-id 2026-05-19:123 \
  --source-id 2026-05-19:138 \
  --source-id 2026-05-20:020 \
  --allow-live-model
```

Build or resume the approved cohort:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --selection cohort \
  --allow-live-model \
  --resume
```

Eligible cases require `--allow-live-model`. Put `DEEPSEEK_API_KEY` and any
optional `DEEPSEEK_BASE_URL` in ignored local environment files. The 26
preflight failures are `insufficient` with zero model calls. Provider or
workflow failures become `blocked`, do not stop the batch, and are the only
results retried by the same `--resume` command. A final manifest is published
only when the blocked count is zero.

## Corpus Layout And Read Commands

`corpus_manifest.json` has manifest version `decision-case-corpus-v2` and
registers path, count, and SHA-256 for every corpus table and projection:

```text
build_results.jsonl
artifacts.jsonl
source_objects/<sha256>.txt
source_bindings.jsonl
cases.jsonl
facts.jsonl
case_facts.jsonl
evidence_links.jsonl
profile_gaps.jsonl
context_associations.jsonl
observations.jsonl
kg.jsonl
kg.ttl
neo4j_nodes.jsonl
neo4j_relationships.jsonl
```

Ask a deterministic registered question:

```bash
uv run aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/smoke-v2 \
  --event-id event:2026-05-19:138 \
  --question "What forecast was known at decision time?"
```

Exact catalog filters are `--event-type-iri`, `--facility-id`,
`--reason-status`, `--reason-value`, `--offset`, and `--limit`. Decision Case
Analysis requires `--allow-live-model` for its exact registered questions.

Export one bounded case:

```bash
uv run aviation-ai agent-system export-case \
  --corpus-dir data/corpus/agent_system/smoke-v2 \
  --event-id event:2026-05-19:138 \
  --output-dir data/corpus/agent_system/export-gdp-138
```

Load the full projection:

```bash
uv run aviation-ai agent-system neo4j-export \
  --corpus-dir data/corpus/agent_system/smoke-v2
```

The loader uses parameterized `MERGE`, preserves unrelated data, and returns
`BLOCKED` for missing credentials or failed connectivity.

## Acceptance States

| Source ID | Required result |
| --- | --- |
| `2026-05-19:123` | Profile-gap declared reason; no formal `atm:impactingCondition`. |
| `2026-05-19:138` | Formal `weather`; evidence ends at `THUNDERSTORMS`. |
| `2026-05-20:020` | Missing declared reason; deterministic `insufficient`. |

Weather associations remain non-causal. BTS observations are source-qualified
public observations and are never FAA demand, AAR, capacity, EDCT, or a
decision rationale.

## Verification

Run after the storage batches:

```bash
uv run pytest -q \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_batch.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py

uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

Real corpora, `.staging` directories, provider output, and case exports are
ignored and must remain uncommitted. Do not treat a changing test count as a
durable project claim; record the command, commit, environment, and date for a
specific result.
