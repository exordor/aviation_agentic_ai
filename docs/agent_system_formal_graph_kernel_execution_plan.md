# Formal Graph Kernel Execution Plan

Status: approved for bounded implementation
Date: 2026-07-26
Branch: `codex/multi-agent-kg-system`
Normative parent: `docs/multi_agent_kg_system_design.md`

## 1. Purpose

The next step is not another round of isolated prompt or parser patches. It is
to establish one trustworthy boundary between model output and the formal
knowledge graph:

```text
Evidence Cards + LLM Graph Patch
  -> deterministic Formal Graph Kernel
  -> ValidatedFact
  -> JSONL / ATMONTO RDF / Neo4j / Query
```

The core system claim for this stage is:

> The existing role-separated workflow can turn one real ATCSCC advisory into
> an authority-grounded, ontology-valid, provenance-complete event graph that
> is materialized in RDF and Neo4j and supports graph-grounded questions.

This work is on the critical path. Without it, the end-to-end system can run
but cannot claim that its RDF, Neo4j graph, or answers represent validated
ATMONTO facts.

## 2. Minimum End-to-End Case

Use the already selected advisory:

```text
source_id: 2026-05-19:123
event type: Ground Stop
controlled facility: JFK / KJFK
effective start: 2026-05-19T21:00:00Z
effective end: 2026-05-19T22:45:00Z
extension probability: MEDIUM
impacting condition: weather
```

The source contains the following directly observable evidence:

```text
ATCSCC ADVZY 123 JFK/ZNY 05/19/2026 CDM GROUND STOP
CTL ELEMENT: JFK
GROUND STOP PERIOD: 19/2100Z - 19/2245Z
PROBABILITY OF EXTENSION: MEDIUM
IMPACTING CONDITION: WEATHER / THUNDERSTORMS
```

The stage succeeds only when this record can be ingested, materialized,
merged into Neo4j, and queried without relying on model memory or accepting
unknown entities and sources.

## 3. Work Classification

### Critical Path

- Provider and Graph Patch failures must stop formal materialization.
- Every formal fact must pass authority, schema, source, and evidence checks.
- RDF must use real ATMONTO, RDF, PROV, and XSD IRIs.
- Neo4j must be loaded with real parameterized `MERGE` operations.
- Query retrieval must return no evidence when no relevant graph fact exists.
- Every accepted fact must be traceable to exact source evidence.

### Evidence Quality

- Persist the source snapshot and checksum.
- Persist a fact-level trace file.
- Persist the exact graph facts passed to the Query Agent.
- Persist model-call and Neo4j-load summaries.

### Deferred Hardening

- Concurrent ingest and removal of the module-level context holder.
- General retry policies, performance work, and long-running service behavior.
- Full 718-record execution.
- Weather, generic RAG, cross-source QA, and new source families.
- New Agent roles, Critic Agents, prompt A/B tests, and repeated live trials.

## 4. Fixed Architecture Decisions

### 4.1 One canonical internal fact representation

Graph Patch, RDF, Neo4j, and Query must not interpret the same strings
independently. Introduce one small internal Pydantic contract:

```python
ValidatedFact(
    fact_id: str,
    subject_iri: str,
    subject_class_iri: str,
    predicate_iri: str,
    object_kind: Literal["iri", "literal"],
    object_value: str,
    object_class_iri: str | None,
    datatype_iri: str | None,
    source_ids: list[str],
    evidence_texts: list[str],
)
```

The model still emits the existing line-oriented Graph Patch. It is not
required to emit JSON or provider JSON Schema.

### 4.2 Provenance is deterministic infrastructure

Do not depend on the KG Construction Agent to remember
`prov:wasDerivedFrom`. The Formal Graph Kernel derives provenance from each
accepted Graph Patch line, its source IDs, and its bound EvidenceClaims.

### 4.3 No new Verification Agent

Authority, schema, evidence, and endpoint checks are deterministic
infrastructure. They must not be implemented as another LLM Agent.

### 4.4 Model-call policy

For this structured vertical slice:

- Advisory Agent uses deterministic structured fields and exact source spans.
- Facility Agent uses the unique NASR authority candidate.
- Terminology Agent uses the unique authority term mapping.
- KG Construction Agent performs the LLM graph-generation call.
- Query Agent performs one LLM call only after relevant graph retrieval.

Codex approves one metadata-only policy clarification:

```text
advisory invocation policy:
structured_fields_incomplete_or_ambiguous_only
```

ZCode must not change prompt wording, few-shot examples, role count, model
parameters, or the Graph Patch output contract.

## 5. Implementation Batch One: Evidence and Formal Graph Gate

This batch is entirely offline. It ends at a mandatory checkpoint.

### 5.1 Allowed files

- `src/aviation_agentic_ai/agent_system/contracts.py`
- `src/aviation_agentic_ai/agent_system/agents.py`
- `src/aviation_agentic_ai/agent_system/graph_patch.py`
- `src/aviation_agentic_ai/agent_system/schema_guide.py`
- `src/aviation_agentic_ai/agent_system/sources.py`
- `src/aviation_agentic_ai/agent_system/workflow.py`
- `src/aviation_agentic_ai/agent_system/materialize.py`
- one new small module:
  `src/aviation_agentic_ai/agent_system/formal_graph.py`
- `configs/prompts/agent_system_v1.yaml`, metadata-only invocation-policy edit
- `tests/test_agent_system.py`
- one new focused test:
  `tests/test_agent_system_graph_kernel.py`

No other files are in scope.

### 5.2 Exact-evidence extraction

Extend the deterministic advisory fields with:

- `extension_probability`
- `impacting_condition`

Every EvidenceClaim must carry text copied from the source record. Synthetic
phrases such as `event mention GS`, `term mention GS`, or
`period start 19/2100Z` are not valid evidence.

At minimum, the fixed advisory must produce exact source spans for:

- event type;
- controlled facility;
- advisory number;
- effective period;
- extension probability;
- impacting condition.

Before a claim can support a formal fact, assert:

```python
claim.source_id == source_record.source_id
claim.evidence_text in source_record.content
```

Write `source_snapshot.json` containing:

- source ID and family;
- source URL when available;
- exact source content;
- content SHA-256;
- snapshot timestamp.

### 5.3 Fail-closed Agent behavior

KG Construction Agent behavior is fixed:

- non-empty `ModelCallRecord.error` -> `BLOCKED`;
- empty response -> `BLOCKED`;
- missing `GRAPH_PATCH` section -> `BLOCKED`;
- malformed Graph Patch row -> `BLOCKED`;
- correctly parsed response with no formal facts -> `ABSTAIN`;
- only a resolved, parse-complete patch may reach the Formal Graph Kernel.

The workflow must not create successful KG artifacts for `BLOCKED` or
`ABSTAIN`.

The raw model response and provider error remain in the run trace.

### 5.4 Formal Graph Kernel

Provide one entry point:

```python
validate_graph_patch(
    block,
    event_iri,
    event_class,
    schema_guide,
    canonical_entities,
    known_source_ids,
    evidence_cards,
    source_snapshot,
) -> GraphValidationResult
```

`GraphValidationResult` contains:

- accepted `ValidatedFact` objects;
- rejected rows with reasons;
- graph-level errors;
- `publishable: bool`.

Each proposed fact must pass these checks in order:

1. Subject is the program-supplied event IRI or a known canonical entity.
2. Class and property belong to the active Schema Guide.
3. An object-property object exists in the canonical registry.
4. Object class satisfies the declared range.
5. Subject class satisfies the declared domain.
6. Literal datatype is the Schema Guide datatype.
7. Enumerated value is in the active allowed-value set.
8. Every source ID is registered and non-empty.
9. Every fact binds to source-contained evidence.
10. Applicable exact-cardinality constraints are satisfied.

For `atm:GroundStopTMI`, enforce at least:

- exactly one `atm:controlledNASelement`;
- exactly one `atm:extensionProbability`;
- the active allowed values for extension probability;
- the active allowed values for impacting condition when present.

Unknown entities, unknown sources, forged provenance endpoints, missing
required properties, and invalid enum values make the result non-publishable.

### 5.5 Fact trace

Write `fact_trace.jsonl`, one row per accepted fact:

```text
fact_id
graph_patch_line
source_id
evidence_text
evidence_agent_role
source_snapshot_sha256
```

Normalized graph values may differ from their source spelling, but the
original evidence must remain exact.

### 5.6 Batch-one acceptance

Required tests:

1. Provider failure returns `BLOCKED` and produces no KG artifacts.
2. Empty or malformed Graph Patch returns `BLOCKED`.
3. Unknown canonical object is rejected.
4. Unknown source and forged provenance endpoint are rejected.
5. Invalid `extensionProbability` is rejected.
6. Missing required Ground Stop property makes the graph non-publishable.
7. Non-source-contained evidence cannot support a formal fact.
8. The fixed Ground Stop case produces publishable `ValidatedFact` objects.
9. Every accepted fact has an exact evidence binding.

Commands:

```bash
uv run pytest -q \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system.py \
  tests/test_agent_system_prompt_catalog.py

uv run ruff check .
uv run pytest -q
git diff --check
```

No live-model call is authorized in this batch.

ZCode must return:

```text
CHECKPOINT
```

or:

```text
BLOCKED
```

It must not continue into RDF, Neo4j, Query, or live execution before Codex
reviews this checkpoint.

## 6. Implementation Batch Two: RDF, Neo4j, and Query

This batch is queued but not yet authorized. It begins only after Codex accepts
batch one.

### 6.1 ATMONTO-aware RDF

Create RDF directly from `ValidatedFact` and Schema Guide IRIs:

- event IDs are absolute `urn:aviation-agentic-ai:event:*` URIs;
- class and property IRIs come from Schema Guide;
- `rdf:type` uses the standard RDF predicate;
- canonical facilities remain URIRefs;
- advisory number is `xsd:integer`;
- effective times are `xsd:dateTime`;
- string/enumerated values use their declared datatypes;
- literals are never converted to resource nodes;
- PROV source nodes use stable URIs and retain the display source ID;
- each fact has a reified statement or equivalent fact trace connected to its
  source and evidence.

The writer must not construct `example.org/...#atm:*` IRIs.

### 6.2 Neo4j projection and load

Use the existing Neo4j connection, batching, and parameterized-MERGE machinery
through a narrow projection adapter. Do not create a second general-purpose
Neo4j framework.

Projection row contracts:

```text
Node: id, label, properties
Relationship: id, type, start_id, end_id, properties
```

Minimum nodes:

- `AviationEvent`
- `Facility`
- `SourceRecord`

Minimum relationships:

- `CONTROLLED_NAS_ELEMENT`
- `DERIVED_FROM`

Datatype properties belong on the event node. Do not create Literal nodes.
Every relationship retains the original ontology predicate IRI in its
properties.

`neo4j-export` must connect to Neo4j and execute parameterized `MERGE`.
Missing credentials, failed connectivity, or a load error returns `BLOCKED`.
It must never clear unrelated graph data.

### 6.3 Query behavior

Remove the whole-graph fallback. No keyword or intent match means an empty
result.

Fixed behavior:

- no matching graph fact -> `Insufficient graph evidence.`;
- missing provenance -> do not call the model;
- provider failure -> `BLOCKED`;
- answer source IDs must be a subset of retrieved fact source IDs;
- internal `ANSWER` and `SOURCES` headers are parsed but not displayed;
- unrelated questions cause zero provider calls.

Write `query_run.json` containing:

- question;
- retrieved facts;
- ontology labels;
- source IDs;
- final answer;
- model-call metadata.

### 6.4 Batch-two acceptance

RDF tests must parse the Turtle with rdflib and assert:

- actual NASA GroundStopTMI IRI exists;
- actual controlledNASelement IRI exists;
- advisory number is an integer literal;
- times are dateTime literals;
- provenance exists;
- example-namespace ATMONTO terms count is zero.

Neo4j tests must assert:

- no Literal nodes;
- all relationship endpoints exist;
- parameterized `MERGE` is used;
- loading twice does not increase node or relationship counts;
- an unrelated sentinel node is preserved.

Query tests must assert:

- a supported event/facility/time question sees only matching facts;
- an unrelated LAX runway question returns `Insufficient graph evidence.`;
- the unrelated question makes zero provider calls.

Batch two ends with another `CHECKPOINT` or `BLOCKED`.

## 7. Final Real Vertical Slice

This stage is queued but not yet authorized. It begins only after both offline
checkpoints pass.

Execution:

1. Create an unrelated sentinel node in Neo4j.
2. Live-ingest `2026-05-19:123`.
3. Live-ingest the same source again.
4. MERGE both projections into the same Neo4j database.
5. Ask:
   `What traffic management measure, controlled airport, and effective time are recorded in this advisory?`
6. Ask:
   `What is the runway surface at LAX?`
7. Independently query the RDF and Neo4j artifacts.

Expected provider calls:

- two KG Construction Agent calls;
- one supported Query Agent call;
- zero calls for the unrelated question.

Expected total: 3. Hard stop: 4 attempted calls, including failures.
No retry, resampling, prompt editing, or post-result tuning is permitted.

Required final artifacts:

- `source_snapshot.json`
- `fact_trace.jsonl`
- `kg.jsonl`
- `kg.ttl`
- `neo4j_nodes.jsonl`
- `neo4j_relationships.jsonl`
- `neo4j_load.json`
- `query_run.json`
- `run_manifest.json`

Final success requires all of the following:

- provider and parse failures cannot create a formal graph;
- zero unknown-entity and unknown-source accepts;
- actual ATMONTO, RDF, PROV, and XSD IRIs in RDF;
- no literal resources;
- every formal fact has exact source evidence;
- one merged Ground Stop event, one KJFK facility, and one source node;
- second load produces no count increase;
- sentinel node remains;
- supported answer is correct and cites `2026-05-19:123`;
- unrelated answer is `Insufficient graph evidence.` with zero model calls.

Any failure returns `BLOCKED`. ZCode must not repair the result by changing
prompts or adding model calls.

## 8. Ownership and Repository Boundaries

Codex owns:

- this architecture and task order;
- prompt policy and prompt text;
- checkpoint review;
- final validation;
- commit decomposition.

ZCode owns:

- implementation within the authorized batch;
- batch-local tests;
- exact checkpoint evidence.

ZCode must not modify:

- Agent roles or LangGraph topology;
- prompt wording or few-shot examples;
- ontology classes, properties, or the frozen schema slice;
- `alignment_mve`;
- Gold, Critic, or Self-Refine workflows;
- weather/linking or generic RAG code;
- `reports/final/figure_descriptions.md`;
- `.superpowers/`;
- `.zcode/`;
- existing run artifacts.

ZCode must not commit or push.

## 9. Executor Packet

```text
PLAN|id=formal-graph-kernel-20260726|tasks=T1:exact-evidence-and-fail-closed,T2:validated-fact-and-authority-schema-gate,T3:offline-tests-and-checkpoint,T4:atmonto-rdf,T5:neo4j-merge-and-query,T6:real-vertical-slice|deps=T2<-T1,T3<-T2,T4<-T3+Codex-review,T5<-T4,T6<-T5+Codex-review|parallel=none|accept=batch-one-focused-tests+full-tests+ruff+diff-check;batch-two-rdflib+neo4j-merge+query-tests;final-real-ingest+idempotent-merge+supported-and-unsupported-query|boundaries=single-Ground-Stop-path,no-new-Agent,no-prompt-text-change,no-ontology-change,no-weather,no-RAG,no-alignment-MVE,no-commit,no-push

TASK|run=formal-graph-kernel-20260726|task=T1-T3|depends_on=none|inputs=docs/multi_agent_kg_system_design.md,docs/agent_system_formal_graph_kernel_execution_plan.md,existing-frozen-prompt-catalog,existing-schema-slice|scope=batch-one-allowed-files-only|produces=ValidatedFact-contract,source_snapshot.json-contract,fact_trace.jsonl-contract,fail-closed-workflow,focused-offline-tests|accept=commands-in-plan-section-5.6-and-all-assertions-in-section-5|on_deviation=BLOCKED|reply=CHECKPOINT-or-BLOCKED

GOAL|run=formal-graph-kernel-20260726|objective=establish-a-fail-closed-authority-and-evidence-validated-formal-graph-kernel-for-one-real-ATCSCC-Ground-Stop-path|plan=formal-graph-kernel-20260726|executor_subagents=none|done_when=batch-one-artifacts-and-commands-pass-and-executor-stops-at-checkpoint|report=CHECKPOINT-or-BLOCKED|autonomy=execute-approved-batch-one-only-and-block-on-deviation
```

## 11. Codex Checkpoint Review: Fact-Level Evidence Correction

Status: correction required before RDF, Neo4j, or Query implementation
Review date: 2026-07-26

### Current objective

Make the Formal Graph Kernel prove that each accepted fact is supported by the
specific EvidenceClaim for that fact. Merely finding any source-contained text
from the same source is not an evidence binding.

### Observed result-invalidating failure

The first checkpoint passes its registered tests, but a direct adversarial
check shows that the current source-level evidence index accepts a patch with:

```text
atm:extensionProbability | LOW
atm:advisoryNumber | 999
```

even though the source says:

```text
PROBABILITY OF EXTENSION: MEDIUM
ATCSCC ADVZY 123
```

The result is incorrectly marked `publishable=True`. The current implementation
also attaches all source evidence to every accepted fact, so the fact trace does
not identify which claim supports which fact.

This failure directly invalidates the system's authority-grounded KG claim.
Batch two is therefore not authorized yet.

### Minimum correction

1. Replace the source-only evidence test with a deterministic fact-to-claim
   binding. There must be no generic fallback from a source ID to arbitrary
   evidence in that source.
2. Bind the fixed predicates as follows:
   - `rdf:type` -> a terminology claim whose `ontology_target` equals the
     proposed class;
   - `atm:controlledNASelement` -> a facility claim whose `canonical_ref`
     equals the proposed object;
   - `atm:advisoryNumber` -> the advisory-number claim with the same normalized
     value;
   - `atm:effectiveStartTime` and `atm:effectiveEndTime` -> their corresponding
     advisory claims after deterministic date-time normalization;
   - `atm:extensionProbability` -> the extension-probability claim with the
     same normalized value;
   - `atm:impactingCondition` -> the impacting-condition claim with the same
     normalized value when the active schema permits the property;
   - deterministic provenance -> the cited registered source snapshot.
3. Store only the matched claim evidence on each `ValidatedFact`.
   `fact_trace.jsonl` must use that same binding and must not select the first
   unrelated claim from the source.
4. Facility and Terminology Agent claims must use the exact advisory evidence
   span passed to them. Synthetic strings such as `unique authority candidate
   ...` and `canonical term ...` are not evidence. If exact advisory evidence
   is unavailable, the Agent must abstain.
5. Preserve canonical-registry membership as the authority gate for the
   resolved facility and term. Do not invent a second ontology or provenance
   framework in this correction.

### Required adversarial tests

- Source `MEDIUM`, patch `LOW` -> rejected and non-publishable.
- Source advisory number `123`, patch `999` -> rejected and non-publishable.
- A schema-valid but source-incorrect effective time -> rejected.
- The controlled-facility fact binds specifically to the `CTL ELEMENT: JFK`
  evidence, not to an unrelated Ground Stop span.
- The event type binds to the exact Ground Stop mention through the terminology
  claim.
- Facility and terminology claims contain exact source substrings.
- The valid fixed case remains publishable and its fact trace has one relevant
  evidence binding per accepted fact.

### Ontology decision

Do not edit the frozen ontology slice.

`atm:impactingCondition` has a declared Ground Delay Program domain while the
slice also contains a Ground Stop value constraint. For this vertical slice,
retain the exact `IMPACTING CONDITION` evidence and record the field as an
explicit profile gap. It must not enter the formal Ground Stop graph. This
inconsistency is evidence about the active ontology profile, not permission to
silently change the ontology.

### Success and stop condition

Run the same batch-one acceptance commands plus the adversarial tests above.
Return `CHECKPOINT` only when all pass. Do not begin RDF, Neo4j, Query, live
model execution, ontology changes, prompt changes, commits, or pushes.

```text
TASK|run=formal-graph-kernel-20260726|task=fact-level-evidence-correction|depends_on=batch-one-checkpoint-review|inputs=docs/agent_system_formal_graph_kernel_execution_plan.md#11,current-batch-one-diff|scope=batch-one-allowed-files-only|produces=fact-specific-evidence-binding,exact-facility-and-term-evidence,adversarial-regressions,explicit-impacting-condition-profile-gap|accept=section-11-adversarial-tests+section-5.6-commands|on_deviation=BLOCKED|reply=CHECKPOINT-or-BLOCKED
```

## 12. Codex Checkpoint Review: Full-Date Binding and Useful Model Calls

Status: correction required before the batch-one implementation can be
committed
Review date: 2026-07-26

### Current objective

Close the two remaining contract-level failures in the fixed Ground Stop path:

1. a time fact must bind to the complete source date and time, not merely the
   day and clock time;
2. a model call must have a defined effect on an Agent result. The system must
   not pay for an Advisory Agent response that is discarded.

These are Critical Path corrections. They can change whether a false fact is
published and whether the registered three-call vertical slice is respected.
RDF, Neo4j, Query, and live execution remain unauthorized.

### Independently reproduced failures

The source record and title identify `2026-05-19`, and the source period says
`19/2100Z`. The current normalizer reduces both the source and proposed value to
`19T21:00`. Consequently both of these false patch values are accepted and the
result is marked `publishable=True`:

```text
2026-06-19T21:00:00Z
2027-05-19T21:00:00Z
```

The same checkpoint also leaves a complete structured advisory on the
unconditional model-call path. A fake invoker receives one Advisory Agent call
even though all fixed fields were parsed, and its response is not used in any
claim. This contradicts the registered final vertical slice, which permits only
two Knowledge Graph Construction Agent calls and one supported Query Agent
call.

Finally, a rejected `atm:impactingCondition` patch row is not an explicit
profile gap. It is a `RejectedFact` and makes the patch non-publishable. The
fixed case must demonstrate a parsed, source-supported `PROFILE_GAPS` entry;
the checkpoint must not describe a domain rejection as if it were that entry.

### Minimum correction

#### Complete date-time binding

- Anchor advisory period tokens to the full date already present in source
  metadata or the advisory header before they become EvidenceClaim values.
- Preserve the raw source substring separately as `evidence_text`.
- Compare complete normalized UTC timestamps in the Formal Graph Kernel.
- Do not discard year or month during comparison.
- If a raw period cannot be anchored to one full date deterministically, omit
  that time claim and abstain on the corresponding fact. Do not guess.
- Keep the conversion in the deterministic advisory parsing/source layer. The
  Formal Graph Kernel consumes canonical claim values; it must not infer a
  missing calendar context from a proposed patch.

The current vertical slice needs only the fixed, unambiguous
`2026-05-19:123` case. Do not generalize the correction into a new temporal
framework.

#### Advisory Agent invocation policy

- A complete deterministic parse of the fixed record makes zero Advisory Agent
  model calls.
- Do not call a model when its response is not consumed by a bounded output
  parser and cannot change the EvidenceCard.
- For this vertical slice, an incomplete or ambiguous deterministic parse may
  abstain without a model call. A future model-assisted fallback is deferred
  until its output contract and consumer are explicitly designed.
- Keep the existing prompt text and few-shot examples unchanged. This is a
  runtime policy correction, not prompt tuning.
- The expected final live budget remains exactly three successful provider
  calls: two graph-construction calls and one supported query call.

#### Explicit profile-gap evidence

- Add a fixed-case fixture whose `PROFILE_GAPS` section contains the real
  `impacting_condition`, normalized value, exact source evidence, and a short
  schema-mapping reason.
- Assert that it parses as one `ProfileGap` and is not represented as a formal
  Ground Stop fact.
- Assert that the profile-gap evidence is a verbatim source substring.
- Do not change the frozen ontology slice and do not reinterpret a rejected
  graph row as a profile gap.

### Required regression tests

- Exact `2026-05-19T21:00:00Z` binds and remains publishable.
- `2026-06-19T21:00:00Z` is rejected.
- `2027-05-19T21:00:00Z` is rejected.
- A value with the wrong day or clock time remains rejected.
- The complete fixed advisory makes zero Advisory Agent model calls.
- No no-op model response is recorded in the fixed ingest ledger.
- The fixed `impacting_condition` appears as one source-contained
  `ProfileGap`, not as an accepted fact or a domain-rejection substitute.
- All fact-level binding tests from Section 11 continue to pass.

### Success and stop condition

Run the focused batch-one tests, the full test suite, Ruff, and
`git diff --check`. Return one `CHECKPOINT` only after the new adversarial tests
pass. Do not start batch two and do not commit or push.

```text
TASK|run=formal-graph-kernel-20260726|task=full-date-and-call-policy-correction|depends_on=fact-level-evidence-checkpoint-review|inputs=docs/agent_system_formal_graph_kernel_execution_plan.md#12,current-batch-one-diff|scope=batch-one-allowed-files-only|produces=full-date-evidence-values,strict-time-binding,zero-noop-advisory-calls,explicit-source-supported-profile-gap,regression-tests|accept=section-12-regressions+section-11-regressions+section-5.6-commands|on_deviation=BLOCKED|reply=CHECKPOINT-or-BLOCKED
```

## 13. Codex Checkpoint Review: Provenance, Query Intent, and Failure Status

Status: batch two not accepted; one root-level correction is required
Review date: 2026-07-26

### Current objective

Make the batch-two artifacts support the registered end-to-end behavior:

1. every accepted fact remains connected to its registered source in Neo4j;
2. the fixed Chinese competency question retrieves the required event facts;
3. a failed Query Agent call is reported as `BLOCKED`, not as missing evidence.

These are Critical Path corrections. They determine whether the final vertical
slice can run and whether its result is truthful. No additional Agent,
framework, prompt, ontology term, data source, or generalized retrieval system
is authorized.

### Independently reproduced failures

The checkpoint's focused tests pass, but direct checks against the registered
vertical slice reproduce three result-invalidating failures.

#### Neo4j provenance depends on an optional graph row

Every accepted `ValidatedFact` already carries registered `source_ids`.
However, the Neo4j projection creates a `SourceRecord` and `DERIVED_FROM` only
when the model separately emits a `prov:wasDerivedFrom` Graph Patch row.

The valid fixed-case graph used by the Formal Graph Kernel does not require that
extra row. Projecting its accepted facts therefore produces:

```text
labels = [AviationEvent, Facility]
relationship_types = [CONTROLLED_NAS_ELEMENT]
source_nodes = 0
derived_from = 0
```

This breaks the minimum Neo4j graph and makes provenance depend on redundant
model output even though the source binding is already present on every
validated fact.

#### The registered competency question retrieves no facts

The final registered question is:

```text
What traffic management measure, controlled airport, and effective time are recorded in this advisory?
```

The current whitespace keyword matcher does not map the question's semantic
roles to the corresponding schema predicates. It fails to retrieve the event
type and can return incomplete evidence. The intended supported Query Agent
call therefore cannot be trusted.

#### Provider failure is converted into an answer

When the Query Agent invoker returns a non-empty `ModelCallRecord.error`, the
current code parses the empty response and returns
`Insufficient graph evidence.`. No
`BLOCKED` status reaches the caller or CLI. This contradicts section 6.3 and
makes provider failure indistinguishable from genuine graph insufficiency.

### Minimum correction

#### Source projection is derived from validated facts

- For every accepted `ValidatedFact`, derive provenance from its registered
  `source_ids`.
- Create one `SourceRecord` per unique source ID.
- Create one stable `DERIVED_FROM` relationship from the fact's event to each
  unique source.
- An explicit accepted `prov:wasDerivedFrom` fact may confirm the same
  relationship, but must not be required and must not create a duplicate.
- Preserve the existing RDF provenance behavior, canonical IDs, parameterized
  `MERGE`, and no-delete policy.

#### Query retrieval is schema-guided, not raw-string-only

- Add one bounded deterministic intent layer for the registered competency
  question.
- Map the supported concepts to the existing schema predicates:
  traffic-management measure -> `rdf:type`;
  controlled airport -> `atm:controlledNASelement`;
  effective time -> `atm:effectiveStartTime` and
  `atm:effectiveEndTime`.
- The exact registered English question must retrieve those facts and invoke
  the Query Agent once.
- Preserve keyword retrieval for simple matching questions.
- The unrelated LAX runway question must still retrieve nothing, return
  `Insufficient graph evidence.`, and make zero provider calls.
- Do not add vector search, generic RAG, translation calls, another model call,
  or question-specific answer text.

#### Query failure has an explicit blocked path

- A non-empty model-call error or empty provider response raises a narrow query
  blocked result before answer parsing.
- `query_run.json` records `status=blocked`, the failure reason, and the model
  call metadata.
- The `ask` command reports `BLOCKED` and exits non-zero.
- `Insufficient graph evidence.` remains reserved for a successful
  deterministic retrieval decision with no relevant graph evidence, not
  provider failure.

#### English-only active interface

- Define one shared exact fallback message:
  `Insufficient graph evidence.`
- The Query Agent must always answer in English.
- Change only the Query Agent prompt language contract and its insufficient
  evidence few-shot; bump its prompt version from `query-agent-v2` to
  `query-agent-v3`.
- Active source code, prompts, CLI output, tests, documentation, and generated
  system artifacts must contain no Chinese interface text.
- Do not rewrite quoted external source records; original-language source text
  remains valid evidence when a future source profile explicitly requires it.

### Required regressions

1. Accepted fixed-case facts without an explicit PROV graph row still produce
   exactly one `SourceRecord` and one `DERIVED_FROM`.
2. Adding the explicit PROV row does not increase those counts.
3. The exact registered English question retrieves the event type, KJFK
   controlled facility, and both effective-time facts, invokes the provider
   exactly once, and permits only retrieved source IDs.
4. The LAX runway question remains `Insufficient graph evidence.` with zero
   provider calls.
5. A Query Agent provider error produces `BLOCKED`, a non-zero CLI exit, and a
   blocked `query_run.json`.
6. Existing RDF assertions, endpoint completeness, parameterized-MERGE tests,
   and the full test suite remain green.
7. A tracked-file scan over the active Agent-system paths finds no Chinese
   interface text.

The fake Neo4j driver remains a unit/contract test only. It must not be
described as a live Neo4j acceptance result. Credentialed idempotency and
sentinel validation remain part of section 7.

### Success and stop condition

Run the section 6.4 focused checks, `uv run ruff check .`,
`uv run pytest -q`, `git diff --check`, and the registered active-path language
scan. Return `CHECKPOINT` only after all seven regressions above pass. Do not
start the live model run, credentialed Neo4j load, ontology editing, commits,
or pushes.

```text
PLAN|id=formal-graph-batch-two-root-fix-20260726|tasks=T1:derive-provenance-from-validated-facts,T2:add-schema-guided-competency-query-routing,T3:propagate-query-provider-failure-as-blocked,T4:migrate-active-query-interface-to-English,T5:run-focused-and-full-acceptance|deps=T2<-T1,T3<-T2,T4<-T3,T5<-T4|parallel=none|accept=section-13-seven-regressions+section-6.4-tests+ruff+full-pytest+diff-check+active-language-scan|boundaries=batch-two-only,query-prompt-language-change-only,no-ontology-change,no-new-Agent,no-new-framework,no-live-model,no-live-Neo4j,no-commit,no-push

TASK|run=formal-graph-batch-two-root-fix-20260726|task=T1-T5|depends_on=batch-two-checkpoint-review|inputs=docs/agent_system_formal_graph_kernel_execution_plan.md#13,current-batch-two-diff|scope=src/aviation_agentic_ai/agent_system/materialize.py,src/aviation_agentic_ai/agent_system/query.py,src/aviation_agentic_ai/agent_system/agents.py,src/aviation_agentic_ai/cli_agent_system.py,configs/prompts/agent_system_v1.yaml,tests/test_agent_system_batch_two.py,tests/test_agent_system_prompt_catalog.py,and-only-required-existing-query-tests|produces=source-complete-neo4j-projection,schema-guided-fixed-query,blocked-provider-path,English-only-query-interface,regression-evidence|accept=section-13-seven-regressions+section-6.4-tests+uv-run-ruff-check-dot+uv-run-pytest-q+git-diff-check+active-language-scan|on_deviation=BLOCKED|reply=CHECKPOINT-or-BLOCKED
```
