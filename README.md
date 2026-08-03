# Aviation Agentic AI

**ATMONTO-Grounded Agentic HybridRAG for Heterogeneous Aviation Knowledge
Integration**

This research framework integrates heterogeneous aviation sources into an
ATMONTO-aligned knowledge layer, then uses a bounded LLM Query Agent to select
evidence tools and answer natural-language questions with source support. The
current adapters cover traffic-management records, FAA authority documents,
weather, public operational observations, flight/airspace material, and a
document-to-KG construction path. A regression slice is included for
development, but it does not define the framework's research boundary.

![ATMONTO-grounded Agentic HybridRAG architecture](docs/figures/aviation_hybridrag_system_architecture.png)

## Core Capabilities

- Incremental, source-versioned ingestion across configured aviation domains.
- ATMONTO and application-profile constrained publication with evidence anchors.
- Optional LLM candidate-fact construction for source documents; the model
  proposes facts, while deterministic validation controls publication.
- Natural-language HybridRAG: an LLM routes each question to bounded read-only
  source, TMI, knowledge, and flight/airspace retrieval tools.
- Rebuildable lexical, vector, RDF/Turtle, and Neo4j views over accepted facts.

## Quick Start

Python 3.11 or newer is required.

```bash
uv sync --extra dev --extra agent-system --extra neo4j --extra tmi-event-retrieval
uv run aviation-ai agent-system --help
```

The following small GDP ingestion is an installation smoke example. Obtain the
pinned FAA NASR source first, as described in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

```bash
uv run aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/gdp-smoke \
  --domain tmi \
  --advisory-id 2026-05-19:138 \
  --allow-model-download

uv run aviation-ai agent-system reindex \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/gdp-smoke \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download

uv run aviation-ai agent-system ask \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/gdp-smoke \
  --question "What traffic-management measure did ATCSCC Advisory 138 publish?" \
  --allow-model-download
```

## Public Commands

```text
aviation-ai agent-system ingest       register and publish configured source evidence
aviation-ai agent-system reindex      rebuild lexical/vector retrieval views
aviation-ai agent-system ask          answer a natural-language question through the Query Agent
aviation-ai agent-system build-kg     run opt-in ontology-grounded document KG construction
aviation-ai agent-system neo4j-export export current semantic knowledge to Neo4j
aviation-ai agent-system export-event export one published TMI event and its evidence
```

`ingest` selects a configured domain such as `tmi`, `document`, or
`flight-airspace`. `ask` is the normal user entry point: users supply a
natural-language question, not an internal source or event identifier. See
[REPRODUCIBILITY.md](REPRODUCIBILITY.md) for full commands, source bindings,
and local setup.

## Knowledge And Retrieval Boundary

Canonical semantic store preserves accepted ATMONTO-aligned facts, source
versions, evidence anchors, and provenance. The current local implementation
uses SQLite; FTS5, Chroma, RDF/Turtle, and Neo4j are rebuildable retrieval or
export views.

LLMs never directly publish facts. They can select retrieval tools for a
question and, in the opt-in document path, propose typed entity and relation
candidates from bounded evidence. Deterministic normalization, ontology
constraints, evidence checks, and the Formal Publication Kernel decide what
enters the semantic store.

## Research Boundaries

The system does not provide live ATC support, causal explanation, operational
effectiveness scoring, TMI recommendation, complete aviation coverage, or a
formal reconstruction of internal FAA decision processes. Weather context and
public observations retain their original source roles and are not converted
into causal or decision-rationale claims.

Offline tests establish software behavior only. Model-dependent claims require
separately versioned real-provider evaluation; current status belongs to
[RESEARCH_AUDIT.md](RESEARCH_AUDIT.md).

## Documentation Map

- [RESEARCH_AUDIT.md](RESEARCH_AUDIT.md): current implementation and evaluation status.
- [GOALS.md](GOALS.md): durable goals, boundaries, and deferred work.
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md): commands, source bindings, and setup.
- [System architecture](docs/system_architecture.md): normative design and contracts.
