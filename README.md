# Aviation Agentic AI

Aviation Agentic AI builds an evidence-bounded corpus of retrospective FAA
ATCSCC decision cases. It parses each selected advisory, resolves bounded FAA
authority records, prepares non-causal Weather and BTS context, validates a
sealed decision case, and publishes only facts accepted by the Formal Graph
Kernel.

```text
718 discovered advisories
  -> frozen 68-record cohort or explicit source-ID subset
  -> deterministic preflight
  -> 26 insufficient results with zero model calls
  -> sequential workflow for the 42 eligible records
  -> corpus v2 tables and full-corpus projections
  -> rebuildable case-level Chroma index
  -> bounded corpus query, case export, and Neo4j load
```

The public persisted interface is corpus-first. `build-corpus` is the only
evidence writer; `index-cases` creates a rebuildable vector-index sidecar, while
`ask`, `neo4j-export`, and `export-case` read the validated corpus. There is no
persistent single-case ingest path, run-directory query path, or v1 migration
layer. Use `build-corpus --source-id` for a bounded single-case debug build.

## Quick Start

Install the active system and development dependencies:

```bash
uv sync --extra dev --extra ontology-generation --extra neo4j \
  --extra case-retrieval
uv run aviation-ai agent-system --help
```

Python 3.11 or newer is required. Before any eligible build, obtain the pinned
FAA NASR ZIP described in [REPRODUCIBILITY.md](REPRODUCIBILITY.md); it is
intentionally ignored by Git.

Build the three tracked acceptance sources into an ignored smoke corpus:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/smoke-v2 \
  --source-id 2026-05-19:123 \
  --source-id 2026-05-19:138 \
  --source-id 2026-05-20:020 \
  --allow-live-model
```

`--allow-live-model` permits the bounded semantic-resolution or case-assembly
path only when it genuinely activates. The three acceptance records use the
zero-call canonical compiler, but the flag is required for eligible corpus
builds. Keep `DEEPSEEK_API_KEY` and any optional `DEEPSEEK_BASE_URL` in ignored
local environment files; the system does not substitute an ambient provider.

Build or resume the frozen cohort:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --selection cohort \
  --allow-live-model \
  --resume
```

The frozen intake ledger is 718 discovered, 68 selected, 42 Agent-eligible, 23
unsupported-TMI, and 3 incomplete-core-field records. Every selected advisory
gets one `CorpusBuildResult`. The 26 preflight outcomes are `insufficient` with
zero model calls. Provider or workflow failures are `blocked`; `--resume`
retries only blocked records. A final manifest is written only when blocked is
zero.

## Corpus v2

Each successful build writes a `decision-case-corpus-v2` manifest with counts
and SHA-256 checksums for its tables and projections:

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

Source payloads are globally deduplicated by content SHA-256. Semantic facts
are deduplicated independently from provenance; `evidence_links.jsonl` retains
all source bindings. Profile gaps preserve exact source evidence outside the
formal graph. Weather associations are non-causal, and BTS observations remain
source-qualified public observations rather than FAA demand, capacity, AAR,
EDCT, or decision rationale.

## Historical Case Retrieval

Build one decision-record vector per accepted case in a persistent local Chroma
sidecar:

```bash
uv run --extra case-retrieval aviation-ai agent-system index-cases \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

The compact representation includes the TMI type, canonical facility,
declared-reason state and value, UTC time of day, and duration bucket. It
excludes source IDs, raw text, dates, Weather context, BTS observations, and
outcomes. Exact metadata filters are applied before cosine vector recall, and
the reference case is excluded. The index is bound to the corpus ID and must be
rebuilt after the corpus changes.

## Read And Export

Ask a deterministic corpus question:

```bash
uv run aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/smoke-v2 \
  --event-id event:2026-05-19:138 \
  --question "What traffic management measure was published?"
```

`ask` supports exact event-type, facility, declared-reason, pagination, formal
record, Weather-context, BTS-observation, reconstructed-case, and historical
decision-record similarity questions. Registered deterministic questions,
including similarity retrieval, use zero chat-model calls. Exact registered
Decision Case Analysis questions require `--allow-live-model`.

```bash
uv run --extra case-retrieval aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --event-id <reference-event-id> \
  --question "Which historical case is most similar?" \
  --event-type-iri <exact-tmi-iri> \
  --facility-id <canonical-facility-id> \
  --reason-status formal \
  --reason-value weather \
  --candidate-scope archive
```

The tracked six-query smoke set over the 38 accepted cases returned all four
reviewed analogues at rank one and both unique-filter queries as
`insufficient`. This is a small relevance smoke test, not expert-certified
Gold, decision-quality evidence, or a recommendation benchmark.

Export one bounded, non-replayable case:

```bash
uv run aviation-ai agent-system export-case \
  --corpus-dir data/corpus/agent_system/smoke-v2 \
  --event-id event:2026-05-19:138 \
  --output-dir data/corpus/agent_system/export-gdp-138
```

Load the full corpus projection into Neo4j:

```bash
uv run aviation-ai agent-system neo4j-export \
  --corpus-dir data/corpus/agent_system/smoke-v2
```

The Neo4j loader uses parameterized `MERGE`, preserves unrelated data, and
returns `BLOCKED` when credentials or connectivity are unavailable.

## Acceptance Semantics

- Ground Stop `2026-05-19:123` retains a source-bound profile-gap reason.
- Ground Delay Program `2026-05-19:138` retains formal `weather`, with source
  evidence ending at `THUNDERSTORMS`.
- GDP cancellation `2026-05-20:020` retains a missing declared reason and a
  deterministic `insufficient` declared-reason answer.

The system does not provide live ATC support, causal explanation,
operational-situation or outcome-aware similarity, TMI recommendation, general
aviation QA, or a complete aviation ontology. See
[REPRODUCIBILITY.md](REPRODUCIBILITY.md) for source checks, verification, and
corpus commands; see
[docs/multi_agent_kg_system_design.md](docs/multi_agent_kg_system_design.md)
for the normative architecture.
