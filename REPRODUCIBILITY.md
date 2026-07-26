# Reproducibility

Last updated: 2026-07-26

This file describes the current Agent-system path. Historical formal experiments
remain reproducible through `EXPERIMENTS.md` but are not the default workflow.

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

## Verification

Focused Agent-system checks:

```bash
uv run pytest -q \
  tests/test_agent_system.py \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system_query_tools.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py
```

Repository checks:

```bash
uv run ruff check .
uv run pytest -q
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
- Weather explanation, decision episodes, case ranking, and recommendation are
  not current reproduction targets.
