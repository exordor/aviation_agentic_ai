# ATMONTO-Centered Aviation Knowledge Integration And HybridRAG

Status: normative current architecture

Date: 2026-07-31

## 1. Purpose

This document defines the runnable system for converting retrospective FAA
ATCSCC records and bounded cross-source evidence into ATMONTO-aligned TMI event
knowledge and evidence-supported natural-language answers.

The current vertical slice covers GDP, GS, and ReRoute. It is a validation
vehicle for a reusable aviation knowledge-integration architecture, not a claim
of complete ATM coverage.

The system does not provide:

- live ATC decision support;
- a complete aviation ontology;
- an internal FAA decision-process model;
- causal explanation;
- operational effectiveness or optimality;
- TMI recommendation.

## 2. Architecture

![ATMONTO-centered TMI event knowledge construction](figures/tmi_event_construction_architecture.png)

Editable source:
[tmi_event_construction_architecture.drawio](figures/tmi_event_construction_architecture.drawio).

![TMI event HybridRAG retrieval and answer validation](figures/tmi_event_retrieval_architecture.png)

Editable source:
[tmi_event_retrieval_architecture.drawio](figures/tmi_event_retrieval_architecture.drawio).

```text
718 ATCSCC records + bounded FAA/Weather/BTS sources
  -> source-specific deterministic adapters
  -> ATMONTO-aligned TMI classification and preflight
  -> FAA facility and terminology authority services
     -> Semantic Resolution Agent only for genuine ambiguity
  -> Weather and BTS evidence preparation
  -> deterministic Event Evidence Integration service
     -> sealed evidence task
     -> source-supported proposal or honest insufficient
  -> task-bound admissibility validation
  -> Formal Publication Kernel
  -> canonical TMI Event Corpus v3
     -> exact corpus read view
     -> event graph view with cross-source evidence paths
     -> metadata-conditioned TMI event ranking index
     -> offline RDF/Turtle and Neo4j exports
  -> bounded LLM Query Agent
  -> evidence support validation
  -> answer / insufficient / blocked
```

The coordinator, adapters, parsers, authority services, profile loaders,
validators, materializers, and search implementations are deterministic. They
are not Agents.

Only two roles make bounded model-mediated choices:

1. Semantic Resolution Agent;
2. Query Agent.

Event Evidence Integration is a deterministic construction service, not an
Agent.

## 3. Semantic Alignment

### 3.1 ATMONTO

ATMONTO is the schema/TBox target. The formal root is:

```text
atm:TrafficManagementInitiative
```

Active application-profile families are:

```text
atm:GroundDelayProgramTMI
atm:GroundStopTMI
atm:ReRouteTMI
```

One registry drives:

- source-family detection;
- required-field preflight;
- admitted predicates and values;
- publication-profile selection;
- retrieval labels.

The profile is versioned and checksum-pinned. It constrains publication; it is
not a complete aviation ontology and cannot be extended implicitly by an LLM.

### 3.2 ATMGRAPH

ATMGRAPH is the ABox construction and query reference. The implementation adopts
these principles:

- source-specific translation;
- stable cross-source identities;
- explicit event and report time;
- provenance-preserving links;
- graph patterns for cross-source queries.

No ATMGRAPH dataset is imported, and the project does not claim an exact
replica of the historical system.

## 4. Source And Evidence Roles

The source families remain distinct:

| Source family | Permitted role |
| --- | --- |
| ATCSCC advisories | Published TMI fields and source-declared reasons. |
| FAA NASR / ARTCC | Facility authority and canonical identity. |
| FAA terminology | Operational-term authority and schema alignment. |
| METAR / TAF | Time-bounded Weather report facts and non-causal context. |
| BTS On-Time | Source-qualified public operational observations. |

Authority evidence can resolve an identity but cannot authorize a TMI event
fact. A Weather report can provide context but cannot fill a missing declared
reason. A BTS row cannot become an FAA demand or capacity record.

Every accepted fact carries:

- an owning profile identifier and checksum;
- source identity;
- source snapshot binding;
- evidence text or evidence reference;
- an auditable fact trace.

## 5. Deterministic Intake

`AdvisoryParser` extracts source-supported structured fields and mentions. It
does not canonicalize facilities, choose ontology terms, call a provider, or
write a graph.

The facility and terminology authority services:

- build candidates from their own source family;
- validate candidate evidence and task scope;
- accept a unique supported candidate deterministically;
- return `insufficient` or `blocked` when evidence or dependencies fail;
- activate Semantic Resolution only when more than one eligible candidate
  remains.

The versioned development intake has 718 discovered and 68 selected records:

| State | Count |
| --- | ---: |
| Active GDP/GS/ReRoute eligible | 46 |
| Incomplete fields | 3 |
| Boundary notices | 18 |
| Deferred ReRoute cancellation | 1 |
| Zero-call preflight `insufficient` | 22 |

## 6. Semantic Resolution Agent

The Semantic Resolution Agent receives a sealed task with:

- a closed authority candidate set;
- source-qualified evidence;
- ontology constraints;
- a fixed tool/model budget.

It may accept an eligible candidate or abstain. It cannot create a candidate,
canonical ID, source, class, predicate, or definition.

Its candidate-bounded tools are:

```text
get_resolution_candidates
get_authority_record
get_ontology_context
check_candidate_constraints
compare_candidate_evidence
```

A blocked, insufficient, zero-candidate, or unique-candidate path uses no
provider. Synthetic ambiguity fixtures validate this orchestration offline;
the development cohort currently contains no natural ambiguity suitable for a
model-performance claim.

## 7. Weather And Public Observations

Weather and BTS preparation is deterministic and precedes evidence integration.

Weather rules:

- a TAF must be issued no later than the advisory signature time and overlap
  the operational period;
- METAR selection uses the permitted pre-issue and half-open operational
  windows;
- Weather report facts enter the graph only through the Weather profile;
- event-to-Weather associations remain outside the formal graph and carry
  `causal_claim=false`.

BTS rules:

- baseline, active, and recovery windows are `[-2h, start)`, `[start, end)`,
  and `[end, +6h)`;
- the public-observation profile owns quantities, units, derivations, and
  source traces;
- numeric zero remains zero;
- missing source values do not become numeric zero;
- observations never become FAA demand, AAR, capacity, EDCT, decision
  rationale, effectiveness, or proof of a caused outcome.

Neither evidence role changes the source-declared TMI reason.

## 8. Deterministic Event Evidence Integration

After deterministic parsing, authority resolution, and optional-layer
preparation, the runtime seals an `EventEvidenceIntegrationTask`. The task
binds:

- TMI event identity;
- admitted core event facts;
- source and evidence references;
- profile gaps;
- authority resolutions;
- Weather associations and report facts;
- public observations;
- component states and source snapshots;
- required and optional event slots.

The deterministic compiler produces the proposal with zero provider calls when
all required slots are source-supported. Source identifiers never select a
special path.

If required evidence is absent, the service returns `insufficient`; it does not
ask a model to invent or choose evidence that is not present. Malformed or
out-of-task evidence is `blocked`. The task-bound check is an admissibility
gate, not publication.

## 9. Formal Publication Kernel

The Formal Publication Kernel is write-free and is the sole final publication
authority. It validates the complete admitted formal set once before any
projection is written.

It accepts only these profile layers:

1. `decision`: ATCSCC TMI event facts under the ATMONTO profile;
2. `weather`: admitted METAR/TAF report facts;
3. `public_operational_observation`: admitted BTS public-observation facts.

The Kernel checks:

- profile and checksum identity;
- source-snapshot bindings;
- evidence and fact traces;
- datatype and domain/range constraints;
- graph constraints;
- layer-specific semantic boundaries.

Normal optional-layer insufficiency is omitted before final publication. A
malformed layer already admitted to the final set blocks the event and produces
no formal projection. The system does not silently discard it and retry a
smaller publication.

No model writes directly to JSONL, RDF/Turtle, Neo4j, or Chroma.

## 10. Canonical TMI Event Corpus v3

`build-corpus` is the only persistent evidence writer. The manifest version is:

```text
tmi-event-corpus-v3
```

The canonical layout is:

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

`CorpusTMIEvent` is the event catalog record. Its identity is the admitted
ATMONTO TMI event IRI. It stores event type, facility, effective interval,
issue time, declared-reason state/value, fact IDs, and source IDs.

`CorpusEventFact` connects one event ID to one accepted semantic fact ID for
storage and retrieval. It is not a formal decision-process or causal relation.

Source content is globally deduplicated by SHA-256. Semantic facts are
deduplicated independently of provenance. Evidence links preserve all
supporting artifacts.

Corpus v3 is authoritative. These are derived:

- checksum-verified exact corpus views;
- corpus-backed event graph with derived cross-source evidence paths;
- RDF/Turtle export;
- Neo4j property-graph export;
- metadata-conditioned Chroma ranking index.

Derived stores do not write back into the corpus.

The graph view can derive two event-scoped evidence patterns at read time:

```text
TMI event -> controlled airport <- Weather report
TMI event -> controlled airport <- BTS public observation
```

Each path carries its formal fact IDs, context-association or observation IDs,
and source IDs. Weather paths remain `causal_claim=false`; public-observation
paths do not become FAA demand, capacity, rationale, or effectiveness facts.

## 11. Agent Usage Sidecar

A successful build can publish:

```text
agent_usage/
  agent_usage.jsonl
  agent_usage_manifest.json
```

Eligible records contribute facility and terminology Semantic Resolution usage
rows when those scopes are reached. Deterministic
Event Evidence Integration does not create an Agent usage row. The sidecar
distinguishes:

- actual model activation;
- deterministic bypass;
- role not reached;
- accepted, abstained, blocked, or not-applicable result;
- provider/tool calls, tokens, and recorded latency.

It stores no prompt, raw response, tool arguments, tool results, or model
reasoning. It is bound to the corpus ID but excluded from canonical corpus
identity. It is operational telemetry, not model-quality evaluation.

## 12. Metadata-Conditioned TMI Event Ranking Index

`index-events` creates a rebuildable `tmi_event_index/` sidecar with:

```text
tmi_event_index_manifest.json
tmi_event_documents.jsonl
chroma/
```

The `tmi_events` collection uses one compact document per accepted event:

- TMI type;
- canonical facility;
- declared-reason state/value;
- UTC time-of-day;
- duration bucket.

Exact metadata filters run before cosine ranking. The anchor event is excluded.
Weather, BTS observations, operational effectiveness, outcome quality, and
recommended actions are not encoded. The index does not represent operational
situation similarity.

The index is bound to `corpus_id` and must be rebuilt after corpus changes.

## 13. Always-On Hybrid Query Agent

The public `ask` command accepts free natural language. There is no exact
question registry, keyword classifier, or deterministic answer bypass.

```text
question + immutable CLI scope
  -> LLM selects bounded read-only tool(s)
  -> typed tool observations
  -> continue retrieval or emit typed answer
  -> statement-support and claim-boundary validation
  -> answer / insufficient / blocked
```

The loop permits:

- at most four provider turns;
- at most three tool calls in one turn;
- at most six tool calls in total.

The six tools are:

| Tool | Capability |
| --- | --- |
| `find_tmi_events` | Exact event filters and bounded paging. |
| `read_tmi_event_facts` | Formal facts, profile gaps, and reason state. |
| `read_weather_context` | Non-causal Weather associations and admitted report facts. |
| `read_public_observations` | Source-qualified BTS public observations. |
| `read_tmi_event_graph` | Event-scoped formal edges and source-bound cross-source evidence paths. |
| `rank_tmi_events_by_metadata` | Exact-filtered metadata-conditioned vector ranking. |

The CLI event ID, exact filters, paging window, and archive/prior candidate
scope form an immutable upper bound. The model may narrow but cannot widen it.
No arbitrary SPARQL, Cypher, graph write, external web access, or long-term
Agent memory is available.

Each answer statement declares a semantic kind and cites the retrieved support
IDs appropriate to that kind. The validator rejects:

- unknown support IDs;
- unsupported factual statements;
- causal language over Weather associations;
- reinterpretation of BTS observations as FAA operational metrics or decision
  rationale;
- recommendation, optimality, or effectiveness claims over metadata ranking.

Answer prose is never written back into the corpus or its projections.

## 14. Public Commands

```text
aviation-ai agent-system build-corpus \
  --config <config> \
  --output-dir <corpus-dir> \
  --selection cohort|all \
  [--source-id <id> ...] \
  --allow-live-model \
  [--resume]

aviation-ai agent-system index-events \
  --corpus-dir <corpus-dir> \
  [--model-name <model>] \
  [--allow-model-download]

aviation-ai agent-system ask \
  --corpus-dir <corpus-dir> \
  --question "<question>" \
  [--event-id <event-id>] \
  [exact filters and paging]

aviation-ai agent-system neo4j-export \
  --corpus-dir <corpus-dir>

aviation-ai agent-system export-event \
  --corpus-dir <corpus-dir> \
  --event-id <event-id> \
  --output-dir <export-dir>
```

The cutover is intentionally breaking. There is no migration reader, command
alias, or run-directory persistence path.

## 15. Regression Contracts

| Source ID | Required semantic state |
| --- | --- |
| `2026-05-19:123` | Ground Stop reason is a source-bound profile gap. |
| `2026-05-19:138` | GDP reason is formal `weather`. |
| `2026-05-20:020` | GDP cancellation reason is honestly missing. |
| `2026-05-19:108` | Formal ReRoute with unsupported ARTCC scope retained as a profile gap. |
| `2026-05-20:137` | Formal ReRoute with unsupported ARTCC scope retained as a profile gap. |

All five use the general zero-call integration path when their required slots
are complete. They are development/regression fixtures, not evaluation samples,
representative coverage, or special source-ID routes.

## 16. Evaluation Boundary

Offline fake/scripted providers validate software contracts only. They do not
establish extraction, reasoning, tool-selection, or Agent quality.

Tracked v1-v3 reports and later compact-selection runs are historical
compatibility artifacts for their named contracts and must not be relabeled as
current performance.

No frozen post-cutover evaluation set currently exists:
`future_frozen_evaluation` is `NOT CONSTRUCTED`. A future model claim requires
an independently designed suite and an explicitly authorized real-provider run
with verified raw responses, parsed outputs, call bindings, tokens, and
manifest checksums.

## 17. Deferred Work

- Formal decision-state inputs, alternatives, constraints, rationale, and
  trade-offs.
- Decision lifecycle/episode identity.
- National Playbook PDF grounding.
- F1/F3S/S4/S1S flight and sector data.
- ASPM demand, capacity, AAR, EDCT, and runway configuration.
- Weather-based causal explanation.
- Operational effectiveness and outcome-aware similarity.
- TMI recommendation.
- General-purpose aviation QA.
- Automatic ontology expansion.
- Production deployment and production-only hardening.

## 18. Verification

The final repository gate is:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

Software tests may use scripted providers. Model-dependent claims require the
separate live-evaluation path and may not substitute an offline result.

Each mainline implementation batch must add or simplify a user-visible
capability. A validator-only batch requires a reproduced failure through a
supported workflow or an explicit user request.
