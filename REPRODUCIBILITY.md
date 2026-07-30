# Reproducibility

Last updated: 2026-07-29

This is the corpus-first Agent-system workflow. Historical experiments remain
available through `EXPERIMENTS.md`, but they are not the default path.

## Environment

- Python: 3.11 or newer; see `pyproject.toml`.
- Package manager: `uv`.
- Supported development platforms: macOS and Linux.

```bash
uv sync --extra dev --extra ontology-generation --extra neo4j \
  --extra case-retrieval
uv run aviation-ai agent-system --help
```

The `ontology-generation` extra supplies the LangChain and LangGraph runtime.
The `neo4j` extra is required only for database loading. The `case-retrieval`
extra supplies the local Chroma vector database and Sentence Transformers
encoder.

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

The only persistent evidence writer is `build-corpus`. It selects advisory
records, performs deterministic preflight, runs eligible cases sequentially,
normalizes their validated packages into corpus v2, and removes temporary case
bundles only after finalization. `index-cases` writes only a rebuildable
derived sidecar.

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

Ask a free natural-language question. A valid corpus query always activates the
configured Query Agent; the model selects bounded, read-only retrieval tools and
the runtime validates each final statement against returned evidence IDs:

```bash
uv run aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/smoke-v2 \
  --event-id <event-id-from-cases.jsonl> \
  --question "What forecast was known at decision time?"
```

Scope hints are `--event-type-iri`, `--facility-id`, `--reason-status`,
`--reason-value`, `--offset`, and `--limit`. They bound tool access; they do not
select an answer branch. The `ask` command has no `--allow-live-model` flag:
running it is the explicit request to use the configured provider. If the
provider cannot be constructed, the query returns `blocked` without a
deterministic fallback.

Build the rebuildable case-level vector index:

```bash
uv run --extra case-retrieval aviation-ai agent-system index-cases \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

The first permitted run may download the pinned embedding model. Later runs can
omit `--allow-model-download` when the model is already local. The resulting
`case_index/` directory is a derived, ignored sidecar bound to the corpus ID.

Run one bounded archive or prior-case query. The Query Agent decides whether
the metadata-conditioned vector tool is relevant:

```bash
uv run --extra case-retrieval aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --event-id <reference-event-id> \
  --question "Which historical case is most similar?" \
  --event-type-iri <exact-tmi-iri> \
  --facility-id <canonical-facility-id> \
  --reason-status formal \
  --reason-value weather \
  --candidate-scope prior
```

Evaluate the tracked six-query relevance smoke set:

```bash
uv run --extra case-retrieval python -m \
  aviation_agentic_ai.agent_system.case_retrieval_evaluation \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --gold data/evaluation/agent_system/case_retrieval_smoke_v1.yaml
```

The reviewed 38-case run produced four rank-one analogue hits, Hit@1 and
Hit@3 of `1.0`, MRR of `1.0`, and two of two expected `insufficient` results.
These values describe only the small tracked relevance smoke set; they are not
expert Gold, operational effectiveness, or decision-quality results.

Export one bounded case:

```bash
uv run aviation-ai agent-system export-case \
  --corpus-dir data/corpus/agent_system/smoke-v2 \
  --event-id <event-id-from-cases.jsonl> \
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

## Live Agent Smoke Evaluation

Fake and scripted model tests validate software behavior and data flow only.
They must not be reported as LLM or Agent performance. Run the separately
authorized live smoke with the frozen DeepSeek configuration:

```bash
uv run python -m aviation_agentic_ai.agent_system.live_agent_evaluation \
  --config configs/cross_source_v1.yaml \
  --suite data/evaluation/agent_system/live_agent_smoke_v2.yaml \
  --output-dir data/corpus/agent_system/live-agent-smoke-v2 \
  --report-dir reports/stages \
  --allow-live-model \
  --repetitions 1
```

The suite fixes provider/model to DeepSeek `deepseek-v4-pro`, temperature to
`0.0`, thinking to disabled, automatic retries to `0`, and one repetition.
The v2 suite evaluates the always-on Hybrid Query Agent and writes evaluator-
owned, sanitized `hybrid_query_run.json` records containing statement types,
statement text, evidence IDs, tool names, tool statuses, and referenceable IDs.
It does not retain prompts, tool arguments, tool results, or model reasoning.
Semantic Resolution remains `not_evaluated_no_natural_ambiguity`; synthetic
ambiguity is not presented as cohort performance.

This five-task run is a compatibility and bounded-behavior smoke test, not a
benchmark or reliability estimate. Temperature zero reduces variance but does
not make provider behavior deterministic. A completed v2 run writes:

```text
reports/stages/agent_system_live_agent_smoke_v2.json
reports/stages/agent_system_live_agent_smoke_v2.md
```

The existing v1 suite and reports are frozen historical evidence for the
retired registered-analysis runtime. The v2 writer uses distinct filenames and
must not overwrite them. Credentials, complete prompts, raw responses, tool
arguments, tool results, and model reasoning remain ignored and untracked.

### Repeated Real-Provider Experiment

Keep the one-shot smoke as a separate compatibility check. Run the frozen
repeated experiment with:

```bash
uv run python -m aviation_agentic_ai.agent_system.live_agent_experiment \
  --config configs/cross_source_v1.yaml \
  --suite data/evaluation/agent_system/live_agent_experiment_v2.yaml \
  --output-dir data/corpus/agent_system/live-agent-experiment-v2 \
  --report-dir reports/stages \
  --allow-live-model
```

The experiment fixes DeepSeek `deepseek-v4-pro`, temperature `0.0`, thinking
disabled, automatic retries to `0`, and the local model cache to disabled. The
v2 experiment applies the existing provider-call integrity policy to the
Hybrid Query Agent. Every query measurement is scored from its evaluator-owned
statement/tool artifact, including per-statement citation and claim-boundary
checks. Repeated cycles remain repeated measurements of five fixed tasks, not
independent evaluation samples.

A completed v2 experiment writes sanitized reports:

```text
reports/stages/agent_system_live_agent_experiment_v2.json
reports/stages/agent_system_live_agent_experiment_v2.md
```

Ignored local evidence:

```text
data/corpus/agent_system/live-agent-experiment-v2/raw_responses_v2.jsonl
data/corpus/agent_system/live-agent-experiment-v2/parsed_outputs_v2.jsonl
data/corpus/agent_system/live-agent-experiment-v2/experiment_manifest_v2.json
data/corpus/agent_system/live-agent-experiment-v2/hybrid_query_runs/
data/corpus/agent_system/live-agent-experiment-v2/cycles/
```

The verified v2 run completed 12 cycles with 120 attempted and 120 successful
real calls, zero failed calls, 383,201 input tokens, and 69,986 output tokens.
The current Hybrid Query Agent passed 12/12 query measurements; the four
unchanged Assembly tasks failed 48/48 measurements. Independently recomputed
SHA-256 values were:

```text
raw_responses_v2.jsonl
  6b38bfc0b705fb802acc56a4468d07a90210422b8e694aca9b6bea9dab948053
parsed_outputs_v2.jsonl
  f567449dda7f76afe238f34673e3086c74605db7274e28b6c0a6cdb43384558e
```

The pre-refactor v1 suite, tracked reports, and ignored local artifacts remain
historical evidence only. They must not be relabeled as Hybrid Query Agent
results.

## Verification

Run after the storage and retrieval batches:

```bash
uv run pytest -q tests/test_agent_system_live_evaluation.py

uv run --extra case-retrieval pytest -q \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_batch.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_agent_system_case_retrieval_documents.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_agent_system_case_retrieval_search.py \
  tests/test_agent_system_case_retrieval_evaluation.py \
  tests/test_agent_system_hybrid_query_agent.py \
  tests/test_agent_system_hybrid_query_tools.py \
  tests/test_agent_system_hybrid_query_public.py \
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
