# Aviation Agentic AI

**ATMONTO-Grounded Agentic HybridRAG for Heterogeneous Aviation Knowledge
Integration**

Aviation Agentic AI integrates ATCSCC publication records, FAA authority data,
Weather reports, BTS records, and the public NASA ATMONTO flight/airspace
sample into a shared semantic knowledge layer. Deterministic ingestion
preserves source roles and evidence anchors; ATMONTO constrains formal
publication; an LLM Query Agent first selects relevant capability families and
then combines exact, graph, lexical, vector, and source retrieval to answer
free-form questions with verifiable support. An optional, separately running
Wigolo Web Evidence sidecar can add allowlisted public documents without
becoming a required runtime dependency or a source of aviation facts by
itself.

```text
Evidence Plane
  -> Deterministic Ingestion Orchestration
  -> Semantic and Trust Plane
  -> Knowledge and Retrieval Plane
  -> Agent Interaction Plane
```

![ATMONTO-grounded Agentic HybridRAG architecture](docs/figures/aviation_hybridrag_system_architecture.png)

The repository includes a GDP/Ground Stop/ReRoute regression slice and a
one-day public ATMONTO cross-source sample. The same publication spine also
admits Flight, Aircraft, Airport/ARTCC, Route, TrackPoint, Sector, Weather,
and reviewed cross-source association roots. Dataset and temporal-scope
configuration select the research material; neither the legacy ATCSCC
inventory nor the regression slice defines the system boundary. ATMONTO
supplies admitted schema terms; ATMGRAPH supplies ABox-construction and
cross-source-query principles.

The document-to-KG path is a framework capability. Public interfaces use the
generic `document` ingestion domain and `knowledge` retrieval family; the
`faa_order_*` modules and their `PolicyRule` concepts belong only to the
current JO 7210.3EE adapter.

The [normative design](docs/multi_agent_kg_system_design.md) documents the
architecture, runtime, and evidence contracts. `RESEARCH_AUDIT.md` is the
authority for current implementation status.

## Quick Start

The commands below exercise a small GDP regression slice for installation and
pipeline verification. They do not define the research dataset; choose the
required source families and temporal scope in the composed configuration.

Python 3.11 or newer is required. Install the active system:

```bash
uv sync --extra dev --extra agent-system --extra neo4j \
  --extra tmi-event-retrieval
uv run aviation-ai agent-system --help
```

Obtain the pinned FAA NASR source described in
[REPRODUCIBILITY.md](REPRODUCIBILITY.md) before ingesting eligible events.

Build a small GDP regression slice:

```bash
uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --domain tmi \
  --advisory-id 2026-05-19:138 \
  --allow-model-download
```

Build the rebuildable retrieval indexes and ask a source-grounded question without
supplying an internal source or event ID:

```bash
uv run --extra agent-system aviation-ai agent-system reindex \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download

uv run aviation-ai agent-system ask \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --question "For ATCSCC Advisory 138 on 19 May 2026, what was published, what reason did the source declare, and what weather context was retained?" \
  --allow-model-download
```

`configs/aviation_knowledge_v1.yaml` composes separate runtime, source, and
dataset/temporal-scope files. Omit `--advisory-id` to process all configured
advisories in the TMI domain. A targeted run
registers only the named advisory records plus the shared authority and context
evidence needed by the construction path. The command skips terminal `ok` or
`insufficient` versions on later runs, retries blocked versions, and commits
each accepted publication independently. It does not need a completed batch
manifest before the data can be queried.

Complete source-supported records follow deterministic processing. The five
tracked cross-family records remain documented under
[Regression Semantics](#regression-semantics); they are not the default user
entry point.

`--allow-live-model` only authorizes the bounded Semantic Resolution Agent when
genuine authority ambiguity remains; it is not proof that a provider was
called. Credentials stay in ignored local environment files.

To run the document-to-KG framework with the FAA Chapter 18 adapter, first
ingest the configured FAA order, then run the generic ontology-construction
command with the real model:

```bash
uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/chapter18-atmonto-kg-v1 \
  --domain document

uv run aviation-ai agent-system build-kg \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/chapter18-atmonto-kg-v1 \
  --domain document \
  --allow-live-model
```

This path recursively chunks all configured Chapter 18 paragraphs, performs
schema-guided NER and relation extraction, and publishes only ontology- and
evidence-valid candidate facts. `--max-items` is an optional smoke limit over
extraction chunks, not a Chapter-specific execution path.

## Persistent Knowledge And Retrieval

The configured store contains:

```text
<store-dir>/
  aviation_evidence.sqlite3
  chroma/
  exports/
```

SQLite is authoritative. It stores:

- immutable source assets, source versions, and exact text anchors;
- ingestion results and ingestion runs;
- active and historical TMI event publications;
- ATMONTO-aligned semantic facts and event membership;
- one-to-many evidence links and source-bound profile gaps;
- non-causal Weather associations;
- source-qualified BTS public observations;
- Flight/Airspace records, formal knowledge roots, deterministic derivations,
  and temporal/applicability associations;
- optional `web_document` source versions, exact anchors, and normalized
  source chunks collected through the explicitly authorized Web Evidence
  sidecar;
- source chunks, FTS5 search data, vector-index state, and compact Agent usage
  telemetry.

The retired `Corpus v2` batch snapshot is not part of the current system.
Gitignored files under `data/evaluation_runs/agent_system/` are execution
evidence only; they are neither a knowledge store nor a query backend.

Historical plans, PHAK-era reports, and superseded compatibility contracts
are kept outside the default checkout in the dated sibling archive. They are
not runtime dependencies and do not change the supported commands.

| Location | Role |
| --- | --- |
| `data/stores/aviation/` | Authoritative SQLite knowledge plus rebuildable indexes and exports |
| `data/evaluation_runs/agent_system/` | Ignored raw and parsed execution evidence |

The Formal Publication Kernel is the sole authority for accepted formal facts.
SQLite FTS5 is a lexical index over exact source chunks, including admitted
`web_document` chunks. Chroma contains three rebuildable vector collections:

- source-record chunks for semantic source discovery;
- compact TMI event summaries for metadata-conditioned event retrieval.
- ontology-extracted knowledge entities for discovery before exact graph reads.

Web source chunks enter only the source-record collection. TMI event vectors
are built from admitted TMI event publications and do not become a general
web-document index.

The current source representation uses bounded full-record chunks with exact
source anchors. Search results are candidates: a final source-supported claim
must use `read_source` to retrieve the exact source version or anchor.

Ingestion attempts an incremental index update after semantic publication.
If the embedding model is unavailable, accepted evidence remains queryable
through exact and lexical paths. The CLI reports `retrieval_indexes` as
`updated`, `not_needed`, `blocked`, or `not_applicable` independently from
semantic ingestion counts. Rebuild all vector collections explicitly with:

```bash
uv run --extra agent-system aviation-ai agent-system reindex \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

Chroma is current only when its recorded knowledge revision matches SQLite.
Neither FTS nor Chroma writes semantic facts back into the store.

## Ask Natural-Language Questions

```bash
uv run aviation-ai agent-system ask \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --question "For ATCSCC Advisory 138 on 19 May 2026, what was published, what reason did the source declare, and what weather context was retained?" \
  --allow-model-download
```

Every valid `ask` activates the configured Query Agent. There is no fixed
question registry, keyword router, or deterministic prose fallback. A first
LLM routing step selects one or more bounded capability families; the Agent
then sees only the relevant subset of 21 deterministic, read-only evidence
tools:

- `source`: lexical/semantic discovery and exact source reading (3 tools);
- `tmi`: event discovery, facts, context, observations, graph, and
  metadata-conditioned retrieval (6 tools);
- `flight_airspace`: flights, airports, trajectories, sectors, Weather
  associations, TMI-applicability candidates, and the general aviation graph
  (9 tools).
- `knowledge`: ontology-entity discovery, structured relationship filtering,
  and ATMONTO-aligned graph reads (3 tools), plus the shared exact
  `read_source`.

When the operator explicitly enables the Web Evidence sidecar for query time,
the router may also expose one optional `web` family containing
`web_search`, `web_fetch`, and `web_extract`. This adds three tools only for
that authorized process; the default core remains the 21-tool
source/TMI/knowledge/Flight/Airspace registry.

The action-observation loop permits at most 7 retrieval turns, 6 tool calls in
one turn, and 16 evidence-tool calls in total, followed when needed by one
tool-free Evidence Packet answer turn. Family routing is a model call, not a
deterministic question classifier.

The default interaction requires only the natural-language question. Lexical
or semantic discovery returns any active TMI event IDs authoritatively bound to
the matched source version, so the Agent can continue to event facts, context,
observations, and graph tools without asking the user for an internal ID.
CLI answers render human-readable evidence labels, dates, authorities, and
source links; logical source IDs remain internal provenance metadata.

CLI event, family, metadata, paging, and candidate-scope filters form
an immutable upper bound around tool access. The Agent can narrow that scope
but cannot widen it. It may use exact SQLite reads, the store-backed semantic
graph view, SQLite FTS5, Chroma, and exact source reads in one bounded
action-observation loop.

Each final statement must cite returned support appropriate to its claim type.
Weather associations remain non-causal. BTS observations cannot be
reinterpreted as FAA demand, AAR, capacity, EDCT, decision rationale,
effectiveness, or caused outcomes. Metadata-conditioned event retrieval is not
operational-situation similarity and cannot support a TMI recommendation.

## Optional Web Evidence

The Web Evidence domain is disabled in the tracked configuration and makes no
network call during ordinary ingestion. It is activated only with a local
configuration overlay that sets an explicit seed and domain allowlist, plus
`--allow-live-web`. The sidecar runs separately on a controlled endpoint; the
project owns URL policy, checksum identity, anchors, persistence, and support
validation. It does not vendor Wigolo or add its AGPL-3.0 package to the core
runtime.

For installation, loopback REST operation, external scheduling, failure states,
and the no-vendor/license boundary, see
[`docs/wigolo_web_evidence_operations.md`](docs/wigolo_web_evidence_operations.md).

## Optional Exports

Export one active event and only its referenced evidence:

```bash
uv run aviation-ai agent-system export-event \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --event-id <event-id> \
  --output-dir data/stores/aviation/exports/selected-event
```

Load a rebuildable property-graph projection into Neo4j:

```bash
uv run aviation-ai agent-system neo4j-export \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1
```

RDF/Turtle, JSONL, and Neo4j are optional products of all active formal
knowledge roots in the authoritative store, not only TMI events. They are not
required by the Query Agent and do not become independent sources of truth.
Web records appear in these projections only when SQLite formal facts or
qualified evidence links explicitly bind to the web source version; a
standalone fetched page is not exported as a formal graph root.

The public command surface is:

```text
ingest
reindex
ask
build-kg
neo4j-export
export-event
```

At the repository root, `agent-system` is the only supported runtime group.
The former `ontology`, `source`, `cqs`, `report`, PHAK, demo, and
`cross-source` command surfaces are retired and are not registered as public
root commands. Their source, focused tests, and recorded artifacts are
historical evidence only; they are not compatibility interfaces.

The cutover is intentionally breaking. There is no run-directory query path,
batch-snapshot query requirement, legacy reader, or command compatibility
alias.

## Regression Semantics

- GS `2026-05-19:123` retains a source-bound profile-gap reason.
- GDP `2026-05-19:138` retains formal `weather`.
- GDP cancellation `2026-05-20:020` retains an honestly missing reason.
- ReRoute `2026-05-19:108` and `2026-05-20:137` publish
  `atm:ReRouteTMI`; their unsupported ARTCC scope remains a profile gap.

These are development/regression fixtures, not special runtime routes,
evaluation samples, or a representative benchmark.

## Flight And Airspace Knowledge

Flight, airport/ARTCC, trajectory, sector, Weather-association, and
TMI-applicability records now enter the same authoritative store through the
generic publication spine and are exposed through the `flight_airspace` Query
Agent tool family:

```bash
uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/aviation-knowledge-2026-05-v1 \
  --domain flight-airspace
```

The NASA July 2014 sample and the May 2026 operational-source slice remain
separate temporal domains; the runtime does not join them across time. Current
Flight/Airspace questions use the natural-language `agent-system ask` path.
See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for source bindings and
historical-material boundaries.

## Evaluation Boundary

Fake and scripted models verify software contracts only. Live results must use
the configured provider and separate provider-call success from task
acceptance. Historical experiments are outside the default checkout. See
`RESEARCH_AUDIT.md` for current status.

The system does not provide live ATC support, causal explanation, operational
effectiveness scoring, TMI recommendation, complete aviation coverage, or a
formal model of decision inputs, alternatives, constraints, and rationale.

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for source checks and commands,
[RESEARCH_AUDIT.md](RESEARCH_AUDIT.md) for current project truth, and
[docs/multi_agent_kg_system_design.md](docs/multi_agent_kg_system_design.md)
for the normative architecture.
