# Multi-Agent Aviation Event Knowledge System

Status: normative implementation design
Version: 1.0
Date: 2026-07-25

## 1. Purpose

This document is the single design source for the first runnable version of the
multi-Agent aviation event knowledge system.

The system reads one retrospective FAA ATCSCC advisory together with
authoritative facility and terminology sources, coordinates source-specialist
Agents, constructs an ontology-guided event knowledge graph, materializes it as
RDF and a Neo4j projection, and answers a user question from that graph with
source references.

The project objective is to build a useful and extensible system. It is not
currently a Single-Agent versus Multi-Agent comparison experiment, a Gold-set
project, or an attempt to prove that role count alone improves quality.

The required vertical slice is:

```text
ATCSCC advisory
    -> Advisory Agent
    -> Facility Agent and Terminology Agent
    -> Knowledge Graph Construction Agent
    -> ontology-constrained Graph Patch
    -> RDF and Neo4j
    -> Query Agent
    -> graph-grounded answer with source IDs
```

## 2. Scope

### 2.1 Included

- One real ATCSCC advisory per ingest command.
- NASR and ARTCC authority data for facility resolution.
- FAA terminology and the existing operational-term registry.
- The existing NASA ATMONTO-derived ATCSCC schema profile.
- Five named Agent roles:
  - Advisory Agent
  - Facility Agent
  - Terminology Agent
  - Knowledge Graph Construction Agent
  - Query Agent
- LangGraph for the fixed collaboration topology.
- LangChain for model invocation.
- Pydantic for internal Python contracts.
- A tolerant line-oriented Graph Patch model output.
- RDF, Neo4j projection, canonical-ID merging, and provenance.
- A bounded real DeepSeek end-to-end smoke run.

### 2.2 Deferred

- Single-Agent versus Multi-Agent comparisons.
- Gold construction, benchmark scoring, and go/no-go research claims.
- Critic, Verifier, Self-Refine, debate, voting, and repair Agents.
- Weather ingestion and weather Agents.
- Cross-advisory event coreference.
- Full-corpus model execution over all 718 advisories.
- Generic RAG, vector-memory expansion, and automatic prompt learning.
- Web UI and production hardening.
- Dynamic unbounded planning loops.
- Creation of a new aviation ontology.

## 3. Design Principles

1. **Use Agents only where bounded reasoning or tool choice is useful.**
   Deterministic parsing, schema validation, and graph writing are not Agents.
2. **Authority data outranks model knowledge.** A model cannot invent a
   facility, canonical term, ontology class, property, or source.
3. **Ontology is a shared contract, not another Agent.**
4. **Evidence moves between Agents, not hidden reasoning.**
5. **Model output stays simple.** Python state can be typed with Pydantic, but
   provider JSON Schema is not required.
6. **The knowledge graph is shared long-term system memory.**
7. **Unresolved information remains unresolved.** `abstain`, `profile_gap`, and
   `blocked` are normal outcomes.
8. **The first implementation remains bounded.** No Agent has an open-ended
   loop or unrestricted tool access.

## 4. System Architecture

```mermaid
flowchart LR
    A["ATCSCC Source Record"] --> B["Advisory Agent"]
    B --> C["Facility Mention"]
    B --> D["Operational-Term Mention"]
    C --> E["Facility Agent"]
    D --> F["Terminology Agent"]
    G["NASR / ARTCC Tools"] --> E
    H["FAA Glossary / Term Registry"] --> F
    I["ATCSCC Schema Guide"] --> B
    I --> F
    I --> J["Knowledge Graph Construction Agent"]
    B --> J
    E --> J
    F --> J
    J --> K["Graph Patch Parser"]
    K --> L["Schema Validator"]
    L --> M["RDF / Neo4j Materializer"]
    M --> N["Knowledge Graph"]
    O["User Question"] --> P["Query Agent"]
    P --> Q["Graph Search Tools"]
    Q --> N
    N --> Q
    Q --> P
    P --> R["Answer with Source IDs"]
```

The Workflow Coordinator is a deterministic LangGraph controller. It creates
tasks, performs fan-out and join, and records state transitions. It does not
call an LLM and is not counted as an Agent role.

## 5. Ontology and Schema Guide

### 5.1 Existing artifacts

The system must reuse:

- `data/ontology/external/icarus_ontology/NASA/ATM.owl`
- `data/ontology/external/icarus_ontology/NASA/NAS.owl`
- `data/ontology/curated/nasa_atmonto_schema_catalog.json`
- `data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json`
- `data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json`
- `reports/stages/atcscc_ontology_profile_overview.md`

The full OWL files are the ontology source. The schema catalog is the
machine-readable inventory. The ATCSCC schema slice is the active application
profile. The extraction JSON schema is a machine-readable reference for the
existing extraction fields and constraints; it is not a requirement that the
LLM use JSON or provider-side JSON Schema.

### 5.2 Schema Guide service

`SchemaGuide` is a deterministic service. It exposes:

- schema-slice identifier and checksum;
- class IRI, prefixed name, label, comment, and parent classes;
- object-property domain and range;
- datatype-property domain and datatype;
- available cardinality and enumerated-value constraints;
- operational-term to event-class mapping;
- compact context selection for the current event class.

The Knowledge Graph Construction Agent receives only a compact relevant slice,
not the complete OWL ontology.

### 5.3 Initial ontology mappings

| Source meaning | Ontology representation |
| --- | --- |
| Ground Delay Program | `rdf:type -> atm:GroundDelayProgramTMI` |
| Ground Stop | `rdf:type -> atm:GroundStopTMI` |
| Controlled airport or NAS element | `atm:controlledNASelement` |
| Advisory number | `atm:advisoryNumber` |
| Effective start | `atm:effectiveStartTime` |
| Effective end | `atm:effectiveEndTime` |
| Impacting condition, when supported | `atm:impactingCondition` |
| Source provenance | `prov:wasDerivedFrom` |

The formal event graph must not replace these terms with parallel custom
properties such as `cs:eventType`, `cs:affectsFacility`,
`cs:usesMeasure`, `cs:effectiveStart`, or `cs:effectiveEnd`.

If a source-supported field has no valid representation in the active profile,
it is recorded as a `profile_gap`; it is not silently assigned a newly invented
property.

### 5.4 Canonical identity versus ontology type

Canonical identity and ontology typing solve different problems:

- the facility registry decides that `JFK` and `KJFK` denote the same facility;
- the canonical facility ID is the Neo4j/RDF entity identity;
- `nas:Airport` describes the entity type;
- `atm:controlledNASelement` describes the event-to-facility relationship;
- the terminology registry normalizes `GS` and `GROUND STOP`;
- the Schema Guide maps that normalized concept to `atm:GroundStopTMI`.

## 6. Shared Agent Contracts

The Python runtime uses small Pydantic contracts. These contracts do not imply
that LLMs must emit JSON.

### 6.1 AgentTask

```text
run_id
source_id
objective
context_refs
allowed_tools
schema_slice_id
```

### 6.2 EvidenceClaim

```text
field_name
value
ontology_target
evidence_text
source_id
canonical_ref
uncertainty
```

### 6.3 EvidenceCard

```text
agent_role
status: resolved | abstain | profile_gap | blocked
claims
canonical_refs
source_ids
uncertainties
tool_trace
decision_basis
```

### 6.4 AgentResult

```text
status
artifact_ref
evidence_card
failure_reason
```

`decision_basis` is a concise evidence summary. The runtime must not request or
store hidden chain-of-thought.

## 7. Common Agent Lifecycle

Every Agent follows the same bounded lifecycle:

```text
receive AgentTask
    -> inspect permitted context
    -> choose an allowed tool, when needed
    -> collect authority-backed evidence
    -> decide resolved / abstain / profile_gap / blocked
    -> emit an EvidenceCard, Graph Patch, or answer
```

Common rules:

- an Agent may call only the tools named in `allowed_tools`;
- every accepted claim must carry `source_id` and `evidence_text`;
- missing evidence produces `abstain`, not model completion from memory;
- tool traces record tool name, safe parameters, result references, and timing;
- credentials and hidden model reasoning are never stored;
- model and tool-call budgets are checked before invocation.

## 8. Advisory Agent

### 8.1 Goal

Convert one raw ATCSCC advisory into a source-bounded evidence card containing
event-type, facility, operational-term, time, and status mentions.

### 8.2 Input

- one `SourceRecord`;
- a compact list of relevant ATCSCC event classes;
- deterministic structured-field parse results.

### 8.3 Allowed tools

- `get_advisory`
- `parse_structured_fields`
- `get_schema_event_classes`

### 8.4 Internal process

1. Read the advisory and metadata.
2. Inspect deterministic field-parser output.
3. Identify the event-type mention.
4. Identify facility and operational-term mentions.
5. Identify effective start, effective end, and source status expressions.
6. Attach exact source spans to every claim.
7. Leave facility and terminology canonicalization to downstream Agents.
8. Emit `AdvisoryEvidenceCard`.

### 8.5 Limits

- at most three deterministic tool calls;
- at most one model call;
- no facility or terminology registry access;
- no graph construction.

### 8.6 Stop conditions

- missing source record: `blocked`;
- no event evidence: `abstain`;
- unsupported but real source field: retain the claim for later
  `profile_gap` handling.

## 9. Facility Agent

### 9.1 Goal

Resolve a facility mention to an authoritative canonical facility entity and
its ontology type.

### 9.2 Input

- facility mention;
- structural slot;
- exact advisory evidence span;
- advisory source ID.

### 9.3 Allowed tools

- `lookup_nasr_facility`
- `lookup_artcc`
- `resolve_facility_alias`

### 9.4 Internal process

1. Use the structural slot to select an authority lookup.
2. Retrieve authority candidates.
3. Accept a unique authority candidate.
4. If multiple candidates remain, use the local evidence context only.
5. If context does not uniquely resolve the mention, return `abstain`.
6. Emit canonical ID, authority source, and `nas:Airport`, `nas:ARTCC`, or the
   applicable existing profile type.

### 9.5 Limits

- at most three tool calls;
- no model call for a unique authority candidate;
- at most one model call for a genuine multi-candidate case;
- no model-created facility IDs.

### 9.6 Stop conditions

- zero candidates: `abstain`;
- unresolved multiple candidates: `abstain`;
- authority-source failure: `blocked`.

## 10. Terminology Agent

### 10.1 Goal

Expand and normalize an operational-term mention, resolve its canonical term,
and map the term to an existing ATCSCC ontology class when supported.

### 10.2 Input

- operational-term mention;
- exact advisory evidence span;
- advisory source ID.

### 10.3 Allowed tools

- `lookup_faa_glossary`
- `lookup_pcg_term`
- `resolve_term_registry`
- `resolve_schema_event_class`

### 10.4 Internal process

1. Expand the abbreviation when an authority definition exists.
2. Normalize surface variants to the canonical operational term.
3. Retrieve the authority definition and source reference.
4. Map the canonical term to an existing ATMONTO class.
5. Accept a unique authority mapping.
6. Return `abstain` when genuine ambiguity remains.
7. Emit `TerminologyEvidenceCard`.

### 10.5 Limits

- at most four tool calls;
- no model call for a unique authority mapping;
- at most one model call for a genuine multi-candidate case;
- no new ontology class or property.

### 10.6 Stop conditions

- no authority candidate: `abstain`;
- canonical term exists but no schema mapping: `profile_gap`;
- authority-source failure: `blocked`.

## 11. Knowledge Graph Construction Agent

### 11.1 Goal

Plan a small event graph and generate an ontology-constrained Graph Patch from
the source record and the three evidence cards.

### 11.2 Input

- `SourceRecord`;
- `AdvisoryEvidenceCard`;
- `FacilityEvidenceCard`;
- `TerminologyEvidenceCard`;
- compact `SchemaGuide` context.

### 11.3 Allowed tools

- `get_schema_context`
- `resolve_canonical_ref`
- `get_source_evidence`

### 11.4 Internal process

1. Select the event ontology class from the resolved terminology evidence.
2. Use the program-supplied stable event URI.
3. Plan only facts supported by evidence cards.
4. Map each fact to an allowed ontology property.
5. Use resolved canonical entity IDs as graph objects.
6. Generate `GRAPH_PATCH`.
7. Place real but unmapped source facts under `PROFILE_GAPS`.
8. Omit unresolved or abstained entities from the formal patch.

### 11.5 Output format

```text
GRAPH_PATCH
subject | predicate | object | source_ids

PROFILE_GAPS
field | value | evidence | reason
```

The parser ignores blank lines, code fences, and lines beginning with `#`.

### 11.6 Limits

- at most three read-only tool calls;
- at most one model call;
- no direct RDF, Turtle, Cypher, or provider JSON Schema output;
- no new ontology vocabulary;
- no writing to Neo4j.

### 11.7 Stop conditions

- missing resolved event type: `abstain`;
- missing required source evidence: `abstain`;
- missing Schema Guide: `blocked`;
- output parse failure: `blocked`, with the raw response preserved.

## 12. Query Agent

### 12.1 Goal

Answer a user question using only the materialized knowledge graph and its
provenance.

### 12.2 Input

- user question;
- graph-store handle;
- registered event IDs as graph-scope metadata;
- ontology labels and property descriptions.

### 12.3 Allowed tools

- `find_events`
- `get_event_facts`
- `get_neighbors`
- `get_provenance`

### 12.4 Internal process

1. Identify whether the question asks about events, facilities, time, event
   type, or provenance.
2. Select the smallest suitable graph query.
3. Inspect graph results.
4. Perform another graph query only when the first result reveals a necessary
   adjacent entity.
5. Retrieve provenance for every answer claim.
6. Generate a concise natural-language answer.
7. List the supporting source IDs.

### 12.5 Limits

- at most three graph-tool calls;
- at most two model calls for one bounded model-tool-model cycle;
- no raw advisory reader;
- no external web or model-memory answer fallback.

### 12.6 Stop conditions

- no supporting graph evidence: answer `Insufficient graph evidence.`;
- missing provenance: omit the unsupported claim;
- graph-store failure: `blocked`.

## 13. Deterministic Components

The following are infrastructure, not Agents:

- Workflow Coordinator;
- source loaders;
- structured-field parser;
- Schema Guide;
- Graph Patch parser;
- schema validator;
- canonical-ID resolver;
- RDF writer;
- Neo4j materializer;
- run-trace store.

The schema validator checks:

- class and property membership in the active schema slice;
- property domain and range;
- datatype and enumerated values;
- available cardinality constraints;
- canonical-reference existence;
- source-reference existence;
- graph endpoint existence.

Validation outcomes are:

- `accepted`: eligible for materialization;
- `schema_violation`: invalid under the active profile and not written;
- `profile_gap`: source-supported but not represented by the active profile;
- `parse_error`: malformed Graph Patch;
- `blocked`: required system dependency failed.

This validation does not use an LLM and is not a Verification Agent.

## 14. Collaboration Topology

The ingest graph is:

```text
START
  -> Advisory Agent
  -> parallel fan-out:
       Facility Agent
       Terminology Agent
  -> evidence-card join
  -> Knowledge Graph Construction Agent
  -> Graph Patch parser
  -> schema validator
  -> RDF/Neo4j materializer
  -> END
```

The Query Agent is a separate graph:

```text
START
  -> interpret question
  -> choose graph tool
  -> retrieve graph evidence
  -> optional bounded follow-up graph query
  -> retrieve provenance
  -> compose answer
  -> END
```

## 15. Memory Model

The system has three memory layers:

1. **Working state:** LangGraph state for the current ingest or query run.
2. **Knowledge memory:** canonical RDF/Neo4j graph shared across runs.
3. **Audit memory:** versioned run directory with source references, evidence
   cards, tool traces, model responses, Graph Patch, schema version, and graph
   artifacts.

There is no Memory Agent in this version. There is no vectorized conversation
history, autonomous experience replay, or automatic prompt modification.

## 16. Prompt Policy

The normative role prompts are stored in:

`configs/prompts/agent_system_v1.yaml`

This frozen catalog is authored and tested independently from executor
implementation. Runtime code loads the catalog; it must not rewrite, extend, or
silently replace the prompt text.

Runtime message assembly is fixed:

```text
SystemMessage(role.system)
HumanMessage(role.few_shot[0].user)
AIMessage(role.few_shot[0].assistant)
HumanMessage(role.few_shot[1].user)
AIMessage(role.few_shot[1].assistant)
HumanMessage(render(role.user_template, current_input))
```

The trace records the prompt-set ID, role prompt version, rendered current
input hash, model parameters, and raw response. ZCode may implement this loader
and trace, but it must not add a hidden system prefix or rewrite examples.

Each role prompt contains only:

- role goal;
- authority-source priority;
- permitted tools or supplied tool results;
- information boundary;
- abstain rule;
- output template;
- one minimal fictional positive example and one fictional boundary example for
  format and abstention stability.

### 16.1 Literature-grounded prompt design

The prompt design borrows narrow, reusable mechanisms from established work
without claiming to reproduce those systems:

- **Text2Event:** adopt a compact linearized structure that can be parsed back
  deterministically, and condition generation on an explicit event schema. In
  this project the linearized representation is Graph Patch. The project does
  not claim to implement Text2Event's trie-based constrained decoder.
- **VerifiNER:** present retrieved authority evidence and a closed candidate
  set, require the selected meaning to be supported by both knowledge and local
  context, and retain an explicit abstain outcome. The system never falls back
  to unsupported model memory and does not use multi-sample consistency voting.
- **EA-Agent:** expose only task-relevant evidence and invoke semantic facility
  or terminology resolution only when deterministic authority lookup leaves a
  real ambiguity. The current fixed topology does not implement learned path
  planning, policy optimization, or a Reflector.
- **Self-Refine:** use task-specific input-output examples to stabilize the
  expected representation. The examples are fictional and source-disjoint.
  Iterative self-feedback and revision are not part of this system version.
- **CRITIC:** treat external source evidence as more reliable than unsupported
  self-critique. No Critic Agent or correction loop is added in this version.

These adaptations produce five concrete prompt-engineering mechanisms:

1. explicit role and information boundaries;
2. delimited untrusted source, evidence, schema, and graph blocks;
3. closed candidate and vocabulary constraints with abstention;
4. character-for-character copying of identifiers and provenance;
5. two fictional, contrastive in-context input-output pairs per role.

The examples demonstrate representation and decision boundaries only. They do
not contain the real advisory, facility codes, operational terms, canonical
identifiers, or expected answer used by the live smoke input.

All model calls use the configured DeepSeek endpoint with:

- temperature `0`;
- thinking disabled;
- no automatic provider retry;
- bounded output tokens;
- recorded provider, model, usage, latency, and prompt version.

Temperature `0` reduces sampling variance but does not guarantee universal
determinism. Reproducibility comes from preserved prompts, inputs, outputs, and
versioned sources.

Prompt acceptance has two layers:

1. `tests/test_agent_system_prompt_catalog.py` checks roles, versions,
   placeholders, information boundaries, output contracts, ontology terms,
   refusal language, and model defaults without a provider call.
2. `scripts/smoke_agent_system_prompts.py` performs a bounded five-call
   DeepSeek smoke test, one call per role, using a fixed advisory and fixed
   authority/schema inputs. It validates format adherence, canonical reference
   preservation, ATMONTO predicate use, absence of parallel custom core
   predicates, and graph-source citations. It is implementation QA, not a
   semantic benchmark.

The prompt-engineering QA permits one fixed-input diagnostic pass and one
fixed-input confirmation pass after correcting observed prompt failures. This
is capped at ten provider calls in total. It is not best-of-N sampling, prompt
search, a model comparison, or evidence of semantic accuracy. If manual review
of the confirmation output reveals a newly specified contract failure, one
targeted call for the affected role is allowed after adding a deterministic
regression check; the other roles are not rerun.

## 17. Provenance and Trace

Every accepted graph fact must be traceable through:

```text
graph fact
  -> Graph Patch line
  -> EvidenceClaim
  -> source ID and evidence text
  -> versioned source snapshot
```

The trace stores concise decisions and evidence. It must not store credentials,
hidden chain-of-thought, or unrelated environment values.

## 18. File Layout

The intended package is:

```text
src/aviation_agentic_ai/agent_system/
  __init__.py
  contracts.py
  prompts.py
  sources.py
  schema_guide.py
  agents.py
  graph_patch.py
  materialize.py
  workflow.py
  query.py
  runtime.py

src/aviation_agentic_ai/cli_agent_system.py
```

Existing loaders, registries, KG writers, graph projection code, and LLM
providers must be reused through narrow imports. They must not be copied into
the new package.

## 19. Command Interface

```text
aviation-ai agent-system ingest \
  --source-id <source-id> \
  --config configs/cross_source_v1.yaml \
  [--allow-live-model]

aviation-ai agent-system neo4j-export \
  --run-dir <run-directory>

aviation-ai agent-system ask \
  --run-dir <run-directory> \
  --question "<question>" \
  [--allow-live-model]
```

The ingest command writes a versioned run directory. The ask command must
retrieve from that run's materialized graph and must not answer directly from
the raw advisory.

## 20. Acceptance Requirements

### 20.1 Component tests

- Every Agent can call only its declared tools.
- The Advisory Agent does not canonicalize facilities or terms.
- Unique authority facility and terminology paths make no model call.
- Unresolved multiple candidates produce `abstain`.
- Every EvidenceClaim carries source ID and evidence text.
- Facility and Terminology Agents fan out and join after the Advisory Agent.
- Unresolved canonical references cannot enter a formal Graph Patch.
- Graph Patch facts use the active Schema Guide vocabulary.
- Invalid domain/range facts produce `schema_violation`.
- Real unsupported fields produce `profile_gap`.
- Profile gaps never enter RDF or Neo4j.
- The run manifest records schema-slice ID and checksum.
- The formal graph contains no parallel custom core predicates replacing the
  ATMONTO profile terms.
- Reingesting the same source creates the same event ID.
- Reingesting produces no duplicate canonical nodes or relationships.
- No materialized relationship has a missing endpoint.
- The Query Agent sees graph-tool results, not raw source documents.
- Missing graph evidence produces `Insufficient graph evidence.`.
- No trace stores chain-of-thought or credentials.

### 20.2 Repository checks

```text
uv run ruff check .
uv run pytest -q
git diff --check
```

### 20.3 Real vertical-slice smoke

After all offline tests pass:

1. deterministically select one real advisory with one facility, a clear GDP
   or GS event, and complete effective times;
2. run live ingest;
3. ingest the same source again and check idempotency;
4. export with Neo4j `MERGE` semantics without clearing unrelated nodes;
5. ask one event/facility/time question;
6. confirm that the answer cites actual graph provenance.

Provider calls are capped at six, with a hard maximum of eight. There is no
calibration, A/B prompt test, resampling, or post-result prompt tuning.

## 21. Protected Areas

The implementation must not modify:

- `alignment_mve`;
- alignment Gold, Critic, or Self-Refine workflows;
- weather/linking code;
- `reports/final/figure_descriptions.md`;
- `.superpowers/`;
- `.zcode/`;
- NASA ATMONTO source OWL files;
- the content of the existing ATCSCC schema slice.

No commit or push is made before Codex review.

## 22. Executor Protocol

ZCode implements this document; it does not redesign it.

ZCode must return `BLOCKED` when implementation requires:

- a new Agent role;
- a new ontology class or property;
- a change to the ATCSCC schema profile;
- a second Agent framework;
- an unbounded Agent loop;
- a new source family;
- a broader live-model run.

Completion evidence must report:

- implemented Agent contracts;
- tool boundaries;
- LangGraph fan-out and join;
- schema-slice ID and checksum;
- formal-graph custom core predicate count;
- tests;
- real source ID;
- provider calls;
- idempotency result;
- Neo4j result;
- graph-grounded answer and source IDs;
- remaining limitations.
