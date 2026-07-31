# Aviation Agentic AI

Aviation Agentic AI is an ontology-grounded aviation knowledge-integration and
HybridRAG system. Its current vertical slice turns retrospective FAA ATCSCC
records into ATMONTO-aligned Traffic Management Initiative (TMI) event
knowledge, then answers natural-language questions through an evidence-bound
LLM Query Agent.

```text
ATCSCC + FAA authority + Weather + BTS sources
  -> deterministic parsing, normalization, and preflight
  -> selective Semantic Resolution for genuine authority ambiguity
  -> deterministic Event Evidence Integration
  -> Formal Publication Kernel
  -> canonical TMI Event Corpus v3
  -> exact event, cross-source graph-path, and metadata-ranking views
  -> bounded LLM Query Agent
  -> supported answer / insufficient / blocked
```

The admitted ATMONTO `atm:TrafficManagementInitiative` instance is the formal
root. GDP, GS, and ReRoute are the active application-profile families.
ATMONTO supplies the admitted schema terms. ATMGRAPH supplies ABox construction
and cross-source-query principles; the project does not import an ATMGRAPH
dataset or claim an exact replica.

## Quick Start

Install the active system:

```bash
uv sync --extra dev --extra ontology-generation --extra neo4j \
  --extra tmi-event-retrieval
uv run aviation-ai agent-system --help
```

Python 3.11 or newer is required. Before building eligible events, obtain the
pinned FAA NASR snapshot described in
[REPRODUCIBILITY.md](REPRODUCIBILITY.md).

Build five GDP, GS, and ReRoute development/regression records:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/smoke-v3 \
  --selection cohort \
  --source-id 2026-05-19:123 \
  --source-id 2026-05-19:138 \
  --source-id 2026-05-19:108 \
  --source-id 2026-05-20:020 \
  --source-id 2026-05-20:137
```

Complete source-supported records use the deterministic compiler with zero
provider calls; source IDs do not select that path. Event Evidence Integration
never calls a model. Add `--allow-live-model` only when genuine authority
ambiguity may activate the Semantic Resolution Agent. Without authorization,
such a record remains `insufficient` instead of being silently sent to a
provider. Credentials remain in ignored local environment files.

Build or resume the versioned development cohort:

```bash
uv run aviation-ai agent-system build-corpus \
  --config configs/cross_source_v1.yaml \
  --output-dir data/corpus/agent_system/cross-source-2026-05-v3 \
  --selection cohort \
  --allow-live-model \
  --resume
```

The versioned intake has 718 discovered and 68 selected records: 46 active-family
eligible records, 3 incomplete records, 18 boundary notices, and 1 deferred
ReRoute cancellation. The 22 preflight insufficiencies use zero model calls.
A final manifest is published only when no result is `blocked`; `--resume`
retries only blocked records.

## Canonical TMI Event Corpus v3

A successful build writes a `tmi-event-corpus-v3` manifest with counts and
SHA-256 checksums:

```text
corpus_manifest.json
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

`events.jsonl` catalogs admitted ATMONTO TMI event identities.
`event_facts.jsonl` organizes accepted facts under those identities without
creating a formal decision-process object. Semantic facts are deduplicated
independently from provenance; `evidence_links.jsonl` preserves one-to-many
source support. Source content is deduplicated by SHA-256.

The Formal Publication Kernel accepts three formal profile layers:

1. ATCSCC TMI event facts;
2. METAR/TAF Weather report facts;
3. BTS-reported public operational observations.

Weather context associations remain outside the formal graph with
`causal_claim=false`. BTS observations are not FAA demand, capacity, AAR,
EDCT, decision rationale, effectiveness, or proof that a TMI caused an
outcome.

Corpus v3 is authoritative. The event graph view, RDF/Turtle, Neo4j, and Chroma
are rebuildable projections and do not write back into the corpus.

## Metadata-Conditioned TMI Event Ranking

Build one vector document per admitted TMI event:

```bash
uv run --extra tmi-event-retrieval aviation-ai agent-system index-events \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v3 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

The `tmi_event_index/` sidecar is bound to the corpus ID. Its compact
representation contains TMI type, canonical facility, declared-reason
state/value, UTC time of day, and duration bucket. It excludes raw source text,
Weather context, BTS observations, operational effectiveness, and
recommendations. Exact metadata filters run before cosine recall.

## Ask And Export

Ask a natural-language question:

```bash
uv run aviation-ai agent-system ask \
  --corpus-dir data/corpus/agent_system/smoke-v3 \
  --event-id <event-id-from-events.jsonl> \
  --question "What was published, what reason did the source declare, and what weather context was retained?"
```

Every valid `ask` activates the configured Query Agent. It must retrieve before
answering and can select six deterministic, read-only tools:

- `find_tmi_events`;
- `read_tmi_event_facts`;
- `read_weather_context`;
- `read_public_observations`;
- `read_tmi_event_graph`;
- `rank_tmi_events_by_metadata`.

CLI event IDs, filters, pagination, and candidate scope form an immutable upper
bound around tool access. The Agent can make at most four provider turns, at
most three tool calls in one turn, and at most six tool calls in total. Every
statement must cite the retrieved event, fact, gap, context, observation,
graph-path, and source IDs appropriate to its claim type.

The ranking orders historical TMI records by the compact metadata
representation after exact filtering. It is not operational-situation
similarity, effectiveness analysis, a recommendation, or evidence that a past
TMI should be reused.

Export one bounded event:

```bash
uv run aviation-ai agent-system export-event \
  --corpus-dir data/corpus/agent_system/smoke-v3 \
  --event-id <event-id-from-events.jsonl> \
  --output-dir data/corpus/agent_system/export-selected-event
```

Load the complete rebuildable property-graph projection:

```bash
uv run aviation-ai agent-system neo4j-export \
  --corpus-dir data/corpus/agent_system/smoke-v3
```

The public command surface is:

```text
build-corpus
index-events
ask
neo4j-export
export-event
```

There is no persistent one-record ingest command, run-directory query path,
old-corpus reader, or compatibility alias.

## Regression Semantics

- GS `2026-05-19:123` retains a source-bound profile-gap reason.
- GDP `2026-05-19:138` retains formal `weather`.
- GDP cancellation `2026-05-20:020` retains an honestly missing reason.
- ReRoute `2026-05-19:108` and `2026-05-20:137` publish
  `atm:ReRouteTMI`; their ARTCC scope remains a profile gap because the active
  ATMONTO range does not admit it as `controlledNASelement`.

These records are development/regression fixtures, not special runtime routes,
evaluation samples, or a representative benchmark.

## Evaluation Boundary

Fake and scripted models verify software contracts only. The tracked v1-v3
DeepSeek suites and reports predate the capability-centered runtime or remain
historical compatibility artifacts. No frozen post-cutover evaluation set
currently exists: `future_frozen_evaluation` is `NOT CONSTRUCTED`. A future
claim requires an explicitly designed suite and a separately authorized,
verified real-provider run.

The system does not provide live ATC support, causal explanation, operational
effectiveness scoring, TMI recommendation, complete aviation coverage, or a
formal model of decision inputs, alternatives, constraints, and rationale.

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for source checks and commands,
[RESEARCH_AUDIT.md](RESEARCH_AUDIT.md) for current project truth, and
[docs/multi_agent_kg_system_design.md](docs/multi_agent_kg_system_design.md)
for the normative architecture.
