# Storage Batch S2 Completion — Corpus-First Storage

> Execute with the Subagent-Driven workflow. Complete tasks in order. Each
> implementation task gets one focused review and one commit. Prefer the
> smallest coherent architecture change over production-grade hardening.

## Goal

Replace the persistent single-run storage path with a corpus-first architecture
that can select the frozen 68-record cohort from 718 advisories, process every
selected record independently, and serve query, RDF, Neo4j, and case exports
directly from a validated corpus.

## Target behavior

- Frozen intake counts: 718 discovered, 68 selected, 42 Agent-eligible,
  23 unsupported TMI records, and 3 records with incomplete core fields.
- Every selected advisory receives one `CorpusBuildResult`.
- The 26 deterministic preflight failures are `insufficient` with zero model
  calls. The remaining 42 use the existing sequential multi-Agent workflow.
- Agent abstention is a valid `insufficient` result. Provider or workflow
  failures are `blocked`, do not stop the batch, and are the only entries
  retried by `--resume`.
- A final manifest is published only when blocked count is zero.
- Query, RDF, Neo4j, and case export use corpus tables and content-addressed
  source objects, not persisted per-case run directories.
- GS 123 remains a profile gap, GDP 138 retains formal `weather`, and GDP
  Cancellation 020 retains a missing reason.
- Weather context remains non-causal. BTS observations are never represented
  as FAA demand, capacity, or decision rationale.

## Public CLI after cutover

```text
aviation-ai agent-system build-corpus
  --config <config>
  --output-dir <corpus-dir>
  [--selection cohort|all]
  [--source-id <id> ...]
  --allow-live-model
  [--resume]

aviation-ai agent-system ask
  --corpus-dir <corpus-dir>
  --question <question>
  [--event-id <event-id>]
  [existing structured filters and pagination]

aviation-ai agent-system export-case
  --corpus-dir <corpus-dir>
  --event-id <event-id>
  --output-dir <export-dir>

aviation-ai agent-system neo4j-export
  --corpus-dir <corpus-dir>
  [existing Neo4j connection options]
```

Remove the public `ask-corpus` command, `build-corpus --runs-root`,
`ask --run-dir`, `neo4j-export --run-dir`, and the persistent single-case
`ingest` entry point. A single-case debug run uses `build-corpus --source-id`.
There is no v1 corpus migration or compatibility layer.

## Global constraints

- Use English for code, contracts, tests, CLI output, and active docs.
- Do not add an Agent role, prompt, provider round, vector store, community
  detection, similarity ranking, TMI recommendation, or parallel execution.
- Reuse the current Agent workflow and its eight-call per-case maximum.
- Load shared schema, authority, Weather, and BTS resources once per batch.
- Keep execution sequential because the current workflow has process-local
  context.
- Tests use fake model factories. No real provider calls occur during test
  implementation.
- Use stable IDs and deterministic JSONL ordering. Avoid adversarial or
  production-hardening tests beyond the approved semantics.
- Preserve unrelated user changes.

---

## Task 1 — S2A: Corpus v2 contracts and multisource normalization

### Capability

Store validated decision cases, formal facts, evidence, profile gaps, Weather
context, and BTS observations in a provenance-aware corpus without retaining
per-case run directories.

### Required corpus layout

```text
corpus_manifest.json
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

Manifest format is `decision-case-corpus-v2` and registers every table and
projection with count and checksum.

### Contracts

- `ArtifactRef`: content-addressed source object identified by content SHA-256.
- `SourceBinding`: binds `case_id + logical source_id` to an artifact version.
- `CorpusFact`: verified semantic fact; provenance is not part of identity.
- `EvidenceLink`: one-to-many links from fact, gap, context, or observation to
  source artifacts.
- `CorpusContextAssociation`: event-to-METAR/TAF temporal association with
  `causal_claim=false`.
- `CorpusObservation`: query-friendly BTS metrics derived from already admitted
  public-observation facts, preserving phase, metric, value, unit, fact IDs,
  profile, and source artifact.
- `CorpusProfileGap`: preserves exact original evidence text.
- `CorpusBuildResult`: `ok | insufficient | blocked`, optional event/case ID,
  concise reason, and provider call count for every selected advisory.

### Merge rules

- Merge identical semantic facts into one fact and retain distinct evidence
  through multiple links.
- Deduplicate identical source content globally.
- Use stable IDs for associations, observations, and profile gaps.
- Block only semantic content conflicts, not provenance differences.
- Preserve numeric zero and preserve null as null.

### TDD

Extend `tests/test_agent_system_corpus_store.py` first to cover duplicate fact
provenance, profile-gap source text, formal/context separation, BTS zero/null,
complete manifest registration, and byte-stable rebuilds.

### Verification and commit

Run the focused corpus-store tests and Ruff on touched files. Commit:

```text
feat(agent-system): add corpus v2 multisource storage
```

---

## Task 2 — S2B: Resumable 68/718 corpus build

### Capability

Build a corpus from the configured advisory collection through deterministic
selection and preflight, then sequentially run the existing Agent workflow only
for eligible records.

### Orchestration

```text
718 advisory rows
  -> cohort/all selection and optional source-id restriction
  -> deterministic preflight
  -> insufficient without model for unsupported/incomplete records
  -> existing multi-Agent workflow for eligible records
  -> temporary validated package
  -> corpus v2 normalization
  -> delete persistent run bundle after finalization
```

Add a batch orchestration service. Keep CLI code limited to argument handling
and user output.

### Recovery semantics

- Continue after a blocked case.
- Persist recoverable staging and all build results.
- `--resume` skips `ok` and `insufficient`, retries only `blocked`.
- Repeated resume must not duplicate cases, facts, evidence, or objects.
- Do not publish `corpus_manifest.json` until blocked count is zero.
- On success, remove staging case bundles and keep the corpus plus compact
  `build_results.jsonl`.

### Resource and model constraints

- Load schema guide, authority catalog, Weather data, and BTS data once.
- Execute eligible cases sequentially.
- Reuse only current semantic-resolution and case-assembly model paths.
- Preserve the existing eight-provider-call maximum per case.

### TDD

Add `tests/test_agent_system_corpus_batch.py` with fake model factories covering
718/68/42/23/3 counts, shared-resource reuse, zero calls for 26 insufficient
records, continuation after blocked, blocked-only resume, idempotent resume,
and one result per selected record.

### Verification and commit

Run focused batch/corpus tests and Ruff on touched files. Commit:

```text
feat(agent-system): add resumable cohort corpus build
```

---

## Task 3 — S2C: Corpus query, projections, export, and CLI cutover

### Capability

Make the corpus the only persisted read backend for questions, full-corpus RDF
and Neo4j projection, and bounded single-case export.

### Query API

`CorpusQueryStore` must provide:

```text
find_cases(filters, offset, limit)
get_event_facts(event_id)
get_decision_context(event_id)
get_outcome_observations(event_id, phases)
get_case_evidence(event_id)
```

Support the existing four question families:

1. formal event/facility/time/declared-reason facts;
2. TAF known at decision time plus pre-decision and operational METAR context;
3. baseline/active/recovery BTS public observations;
4. reconstructed decision case.

Profile-gap answers use corpus evidence text. Missing reason is never filled by
Weather or BTS. Registered deterministic questions remain zero-model. Existing
analysis questions may use the current Query Agent only with
`--allow-live-model`. Similar historical case questions remain deterministic
`insufficient` until S3.

### Projections

- Build full-corpus `kg.jsonl`, `kg.ttl`, and Neo4j projection from
  `CorpusFact + EvidenceLink`.
- Represent provenance with source-version artifact identities.
- Exclude context associations from formal RDF and Neo4j.
- Retain already admitted public-observation facts in the formal graph.
- `neo4j-export --corpus-dir` loads the full stable-ID projection with MERGE.

### Case export

`export-case` writes only the selected event:

```text
case_export_manifest.json
case.json
facts.jsonl
evidence_links.jsonl
profile_gaps.jsonl
context_associations.jsonl
observations.jsonl
source_bindings.jsonl
source_objects/
kg.ttl
```

It does not fabricate a run manifest, provider ledger, or replayable run.

### Cutover

Implement the approved CLI and remove the obsolete public commands/options.
Do not retain dual-track compatibility.

### TDD

Cover the three known reason states, GDP 138 Weather/BTS reads, Cancellation 020
reason isolation, all four question families without run directories, formal
fact equality across corpus/RDF/Neo4j, context exclusion, bounded case exports,
and idempotent Neo4j loading.

### Verification and commit

Run focused projection/query/CLI tests and Ruff on touched files. Commit:

```text
feat(agent-system): move query and projections to corpus
```

---

## Task 4 — Documentation, final verification, and real corpus build

Update `README.md`, `REPRODUCIBILITY.md`, `TODO.md`, `RESEARCH_AUDIT.md`, the
normative design document, and `AGENTS.md` so they describe only the
corpus-first main path. Commit:

```text
docs(agent-system): document corpus-first storage
```

Run once after all code batches:

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

Then create an untracked three-source smoke corpus and verify GS 123, GDP 138,
and GDP 020. If credentials and providers are available, execute the approved
68-case command with `--resume` until blocked is zero:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --selection cohort \
  --allow-live-model \
  --resume
```

Expected final intake ledger:

```text
discovered = 718
selected = 68
eligible = 42
unsupported = 23
incomplete = 3
build_results = 68
blocked = 0
```

Real corpus, staging, and provider outputs remain ignored and uncommitted.
Do not merge or push.

## Deferred

Case embeddings, vector databases, similarity ranking, TMI recommendation,
community detection, full LightRAG, parallel Agent execution, and 718-record
live model execution.
