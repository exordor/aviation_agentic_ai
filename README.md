# Aviation Agentic AI

Aviation Agentic AI is an ontology-grounded aviation knowledge-integration and
HybridRAG system. Its current end-to-end vertical slice builds an
evidence-bounded corpus of retrospective FAA ATCSCC TMI records. It classifies
GDP, GS, and ReRoute under an ATMONTO-aligned application profile, resolves
bounded FAA authority records, prepares non-causal Weather and BTS context,
and publishes only facts accepted by the Formal Publication Kernel.

```text
718 discovered advisories
  -> frozen 68-record cohort or explicit source-ID subset
  -> ATMONTO-aligned TMI classification
  -> deterministic preflight
  -> 22 insufficient boundary/deferred/incomplete results with zero model calls
  -> sequential workflow for the 46 active-family eligible records
  -> event-patch admissibility check
  -> final decision/profile/membership publication kernel
  -> canonical corpus v2 with TMI-event identities
  -> read-only Corpus, event-graph, and metadata-conditioned vector tools
  -> always-on bounded LLM query loop
  -> per-statement evidence support
  -> answer, insufficient, or blocked
```

The public persisted interface is corpus-first. `build-corpus` is the only
evidence writer; `index-events` creates a rebuildable vector-index sidecar, while
`ask`, `neo4j-export`, and `export-event` read the validated corpus. There is no
persistent single-case ingest path, run-directory query path, or v1 migration
layer. Use `build-corpus --source-id` for a bounded single-case debug build.

## Quick Start

Install the active system and development dependencies:

```bash
uv sync --extra dev --extra ontology-generation --extra neo4j \
  --extra tmi-event-retrieval
uv run aviation-ai agent-system --help
```

Python 3.11 or newer is required. Before any eligible build, obtain the pinned
FAA NASR ZIP described in [REPRODUCIBILITY.md](REPRODUCIBILITY.md); it is
intentionally ignored by Git.

Build five tracked cross-family regression sources into an ignored smoke
corpus:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/smoke-v2 \
  --source-id 2026-05-19:123 \
  --source-id 2026-05-19:138 \
  --source-id 2026-05-19:108 \
  --source-id 2026-05-20:020 \
  --source-id 2026-05-20:137 \
  --allow-live-model
```

`--allow-live-model` permits the bounded semantic-resolution or case-assembly
path only when it genuinely activates. Complete active-profile records use the
zero-call deterministic compiler; source identifiers do not select the path.
The flag is required for eligible corpus builds. Keep `DEEPSEEK_API_KEY` and
any optional `DEEPSEEK_BASE_URL` in ignored local environment files; the
system does not substitute an ambient provider.

Build or resume the frozen cohort:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --selection cohort \
  --allow-live-model \
  --resume
```

The frozen intake is 718 discovered and 68 selected: 46 active-family eligible
records, 3 incomplete records, 18 boundary notices, and 1 deferred ReRoute
cancellation. Every selected advisory gets one `CorpusBuildResult`. The 22
preflight insufficiencies use zero model calls. Provider or workflow failures
are `blocked`; `--resume` retries only blocked records. A final manifest is
written only when blocked is zero. The completion summary also reports
bounded-Agent activations, deterministic bypasses, outcomes, calls, tokens,
and recorded latency.

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
alignment_audit.json
tmi_coverage.json
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

Corpus v2 is the canonical persisted knowledge layer. Each accepted case has a
stable conceptual case IRI and a reconstruction IRI. Formal membership facts
bind the ATCSCC event and admitted Weather/BTS members to that reconstruction.
RDF/Turtle and Neo4j are offline, rebuildable KG exports. Chroma is a
rebuildable metadata-conditioned retrieval index. None is authoritative
runtime storage.

The active schema/TBox target is a versioned application profile over exact
ATMONTO terms. ATMGRAPH is the reference for source-specific ABox construction,
stable cross-source identity, explicit time, and cross-source graph queries; it
is not imported as a dataset and this project does not claim an exact
ATMGRAPH replica. `alignment_audit.json` and `tmi_coverage.json` are compact,
rebuildable corpus summaries of that alignment and TMI-family coverage. They
are not per-run audit ledgers or additional publication gates.

## Evaluation Boundary

Offline fake or scripted tests validate software contracts only. Existing
DeepSeek runs are preserved as historical, GDP-biased compatibility evidence
under `reports/stages/`; they do not establish cross-family Query Agent,
HybridRAG, or model-quality performance. A representative live evaluation over
GDP, GS, and ReRoute remains a separate approved research task rather than a
mainline implementation gate. See [RESEARCH_AUDIT.md](RESEARCH_AUDIT.md) and
[ARTIFACT_INDEX.md](ARTIFACT_INDEX.md) for the detailed historical records.

## Historical TMI Event Retrieval

Build one decision-record vector per accepted TMI event in a persistent local Chroma
sidecar:

```bash
uv run --extra tmi-event-retrieval aviation-ai agent-system index-events \
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

Ask a natural-language question:

```bash
uv run aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/smoke-v2 \
  --event-id <event-id-from-events.jsonl> \
  --question "What was published, what reason did the source declare, and what weather context was retained?"
```

Every valid `ask` request invokes the configured Query Agent. The model does
not answer from memory: its first action must retrieve evidence, and it may
continue through a bounded action-observation loop. It selects among six
deterministic, read-only HybridRAG tools:

- exact TMI-event discovery and filtering;
- formal TMI-event facts and declared-reason state;
- non-causal Weather context;
- BTS public observations;
- event-scoped graph edges;
- exact-filtered, metadata-conditioned vector recall.

CLI filters, pagination, event ID, and candidate scope form an immutable upper
bound around every tool call. The Agent can make at most four provider turns,
at most three tool calls in one turn, and at most six tool calls in total.
Each final statement must cite the supporting event, fact, profile-gap, context,
observation, graph-path, and source IDs appropriate to its claim type.
Unsupported evidence yields `insufficient`; invalid contracts, unavailable
providers, or failed dependencies yield `blocked`.

```bash
uv run --extra tmi-event-retrieval aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --event-id <reference-event-id> \
  --question "Which historical TMI event is most similar?" \
  --event-type-iri <exact-tmi-iri> \
  --facility-id <canonical-facility-id> \
  --reason-status formal \
  --reason-value weather \
  --candidate-scope archive
```

Similarity remains a deterministic retrieval capability inside the LLM-routed
tool loop. It compares only the published decision-record representation and
cannot be promoted to operational effectiveness, recommendation, or
optimality. The pre-refactor six-query relevance smoke remains historical
retrieval evidence, not evidence of current Query Agent routing or answer
quality.

Export one bounded, non-replayable TMI event:

```bash
uv run aviation-ai agent-system export-event \
  --corpus-dir data/corpus/agent_system/smoke-v2 \
  --event-id <event-id-from-events.jsonl> \
  --output-dir data/corpus/agent_system/export-selected-event
```

Load the full corpus projection into Neo4j:

```bash
uv run aviation-ai agent-system neo4j-export \
  --corpus-dir data/corpus/agent_system/smoke-v2
```

Neo4j is an offline, rebuildable full-corpus export rather than an authoritative
runtime query store. Its loader uses parameterized `MERGE`, preserves unrelated
data, and returns `BLOCKED` when credentials or connectivity are unavailable.

## Cross-Family Regression Semantics

- Ground Stop `2026-05-19:123` retains a source-bound profile-gap reason.
- Ground Delay Program `2026-05-19:138` retains formal `weather`, with source
  evidence ending at `THUNDERSTORMS`.
- GDP cancellation `2026-05-20:020` retains a missing declared reason and a
  deterministic `insufficient` declared-reason answer.
- ReRoute `2026-05-19:108` and `2026-05-20:137` publish
  `atm:ReRouteTMI`, `reRouteTimeType=ETD`, implementation status, and the
  source-declared reason. Their ARTCC scope remains an explicit profile gap
  because the active ATMONTO range does not admit it as
  `controlledNASelement`.

These records are regression fixtures for distinct semantic states and TMI
families. They are not the storage boundary, a representative benchmark, or
special runtime routes.

The system does not provide live ATC support, causal explanation,
operational-situation or outcome-aware similarity, TMI recommendation, general
aviation chat beyond the bounded corpus tools, or a complete aviation ontology.
See
[REPRODUCIBILITY.md](REPRODUCIBILITY.md) for source checks, verification, and
corpus commands; see
[docs/multi_agent_kg_system_design.md](docs/multi_agent_kg_system_design.md)
for the normative architecture.
