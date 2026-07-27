# Reproducibility

Last updated: 2026-07-27

This file describes the current Agent-system path. Historical formal experiments
remain reproducible through `EXPERIMENTS.md` but are not the default workflow.

Batch C.1 is a breaking cutover. Regenerate an old run rather than attempting
to read or extend it with the current runtime. `ingest`, `neo4j-export`, and
`ask` retain useful current names only; they are not compatibility guarantees.

## Environment

- Python: 3.11 or newer; see `pyproject.toml`.
- Package manager: `uv`.
- Supported development platforms: macOS and Linux.

Install the active system:

```bash
uv sync --extra dev --extra ontology-generation --extra neo4j
uv run aviation-ai agent-system --help
```

The `ontology-generation` extra supplies the current LangChain and LangGraph
runtime dependencies. The `neo4j` extra is required only for database loading.

## Source Snapshot Preflight

The advisory JSONL and terminology seed are tracked. The pinned FAA NASR ZIP is
238 MB and intentionally ignored by Git. A clean checkout must obtain it before
ingest:

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

The URL and checksum come from the local source manifest for the selected FAA
cycle. Do not replace the snapshot implicitly during an ordinary run.

Decision Case Graph v1 also uses tracked normalized Weather inputs and the
tracked 1,978-row BTS snapshot:

```text
data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_metar.jsonl
data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_taf.jsonl
data/sources/bts_on_time_2026_05_manifest.json
data/sources/bts_on_time_2026_05_nyc.jsonl
```

The full BTS ZIP is an ignored audit source. To verify it independently:

```bash
BTS_DIR=data/raw/bts
BTS_ZIP="$BTS_DIR/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_5.zip"
mkdir -p "$BTS_DIR"
curl -L --fail \
  "https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_5.zip" \
  -o "$BTS_ZIP"
uv run python -c \
  'import hashlib,pathlib,sys; expected="4e7b96999440afec8c92dd23bfbc68a5852e14d9a56c3d0d366f884542ea80b3"; actual=hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest(); print(actual); raise SystemExit(actual != expected)' \
  "$BTS_ZIP"
```

The tracked BTS manifest pins the archive member, normalized checksum, source
fields, 1,978-row filter, natural key, and `America/New_York` timezone. Null
values remain null. Derived observations are always labelled as BTS-reported
and are not FAA demand, AAR, capacity, EDCT, or ASPM records.

## Build One Validated Run

```bash
uv run aviation-ai agent-system ingest \
  --source-id 2026-05-19:123 \
  --config configs/cross_source_v1.yaml \
  --allow-live-model
```

The command processes one selected advisory. It does not execute a full-corpus
model run. A live run requires `DEEPSEEK_API_KEY`; `DEEPSEEK_BASE_URL` is
optional. The active Agent system does not silently substitute `LLM_PROVIDER`.
Credentials must remain in ignored local environment files.

A publishable run contains the validated graph and audit artifacts described in
`ARTIFACT_INDEX.md`. Non-publishable runs may preserve audit records but must
not publish formal KG files.

For every current multi-source run, `source_snapshots.jsonl` is the canonical
registry. The deterministic post-validation branch writes
`context_associations.jsonl`, `outcome_summaries.jsonl`, and
`weather_fact_trace.jsonl`. It also writes `observation_derivations.jsonl`,
`observation_fact_trace.jsonl`, and `reconstruction_trace.json` for formal
public operational observations. Each manifest entry is `ok`, `insufficient`,
or `blocked`. A failed optional layer does not invalidate already validated
core ATCSCC facts, but that layer is not exposed.

## Query A Validated Run

Deterministic registered field query:

```bash
uv run aviation-ai agent-system ask \
  --run-dir <validated-run-directory> \
  --question "What reason did the advisory state?"
```

Supported deterministic fields include measure, facility, operational period,
declared reason, and provenance. Missing or unsupported evidence returns an
insufficient state without a provider call.

Decision Case Graph v1 adds four deterministic question families:

```bash
uv run aviation-ai agent-system ask \
  --run-dir <validated-run-directory> \
  --question "What forecast was known at decision time?"

uv run aviation-ai agent-system ask \
  --run-dir <validated-run-directory> \
  --question "What observed weather context is recorded?"

uv run aviation-ai agent-system ask \
  --run-dir <validated-run-directory> \
  --question "What BTS-reported public operational observations are recorded?"

uv run aviation-ai agent-system ask \
  --run-dir <validated-run-directory> \
  --question "Reconstruct the decision case."
```

These registered questions are resolved through validated read-only tools and
make no provider call. They never infer a stated reason from Weather context.

The combined decision-record question uses the bounded Query Agent model loop
and therefore requires:

```bash
uv run aviation-ai agent-system ask \
  --run-dir <validated-run-directory> \
  --question "What traffic management measure, controlled airport, and effective time are recorded in this advisory?" \
  --allow-live-model
```

## Load The Neo4j Projection

```bash
uv run aviation-ai agent-system neo4j-export \
  --run-dir <validated-run-directory>
```

Connection values can be provided through command options or:

```text
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
```

The loader uses parameterized `MERGE`, preserves unrelated graph data, and
returns `BLOCKED` when credentials, connectivity, or loading fail.

## Decision-Record Acceptance Cases

The tracked case contract is
`docs/atcscc_decision_record_explorer_cases.md`:

- Ground Stop `2026-05-19:123`;
- Ground Delay Program `2026-05-19:138`;
- missing-reason cancellation `2026-05-20:020`.

Routine verification uses deterministic tests and does not require provider
calls. Temporary run directories belong outside Git.

The active-window BTS-reported acceptance values are:

| Case | Scheduled arrivals | Completed arrivals | Cancellations | Diversions |
| --- | ---: | ---: | ---: | ---: |
| Ground Stop 123 / KJFK | 20 | 18 | 2 | 0 |
| GDP 138 / KJFK | 77 | 68 | 4 | 5 |
| GDP cancellation 020 / KEWR | 50 | 49 | 1 | 0 |

Ground Stop 123 retains a source-bound profile-gap reason and no formal
`atm:impactingCondition`; GDP 138 retains formal `weather` with source evidence
ending at `THUNDERSTORMS`; and cancellation 020 remains missing-reason and is
`insufficient` before model construction. Weather context never changes these
reason states.

## Verification

Focused Agent-system checks:

```bash
uv run pytest -q \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_weather_context.py \
  tests/test_agent_system_bts_outcomes.py \
  tests/test_agent_system_query_tools.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_agent_system.py \
  tests/test_cli_agent_system.py
```

Repository checks:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

Do not record a changing test count as a durable project claim. Record the
command, commit, environment, and date when a specific verification result is
needed.

## Optional Historical Evaluation

The earlier extraction, alignment, cross-source weather, retrieval, and answer
experiments remain documented in:

- `EXPERIMENTS.md`;
- `RESEARCH_QUESTIONS.md`;
- `HYPOTHESES.md`;
- `RESULTS.md`;
- the corresponding `reports/stages/` and `data/evaluation/` families.

Run those paths only for an explicitly reactivated evaluation task. Their
outputs do not change the current system scope automatically.

## Known Boundaries

- Live construction and combined-query runs require provider access.
- Neo4j loading requires a reachable local or remote Neo4j instance.
- The browser explorer is not present on `main`; it remains on
  `codex/kg-visualization-research`.
- Weather-based causal explanation, decision episodes, case ranking, and
  recommendation are not current reproduction targets.
- `WeatherDelay` and `NASDelay` remain carrier-reported attributions, not causal
  labels.
