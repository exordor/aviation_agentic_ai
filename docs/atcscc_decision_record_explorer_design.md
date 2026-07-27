# ATCSCC Decision Record Explorer

Status: query foundation implemented on `main`; browser implementation paused on
`codex/kg-visualization-research`
Approved: 2026-07-26
Language: English
Primary user goal: understand and verify a published ATCSCC decision record

## Stage Header

| Required item | Decision |
| --- | --- |
| Current objective | Expose one validated ATCSCC decision record as a source-traceable user task. |
| Minimum experiment | Two positive real advisories plus one real missing-reason cancellation control, five field questions, and one combined-record question. |
| Minimum components | Existing run artifacts, Query Agent, read-only graph tools, and one local explorer page. |
| Expected evidence | Correct record fields, fact and source provenance, honest insufficiency, and no unsupported claims. |
| Success condition | A user can verify the recorded query result offline from one frozen bundle. |
| Failure condition | Any displayed answer is unsupported, any missing field is guessed, or the explorer requires a new data source. |
| Explicitly deferred | Lifecycle grouping, weather, ASPM, flights, similarity ranking, recommendation, and production hardening. |

This stage established that the validated graph and provenance path support a
useful bounded user task. The query foundation is complete on `main`. The
frozen-bundle browser implementation is reviewed on the separate visualization
branch and is paused; no new Agent, source, or ontology module was added.

## 1. Purpose

This stage makes the existing multi-Agent event knowledge system inspectable by
a non-technical user without changing the graph or rerunning an Agent.

After an operator selects one completed query run, a user should be able to
verify:

- which traffic-management measure was published;
- which airport or NAS element it controlled;
- when it was effective;
- which reason the advisory explicitly declared;
- which graph facts and source records support each statement.

This stage explains an already-published decision record. It does not recommend
a new Traffic Management Initiative and does not reconstruct the complete FAA
decision process.

## 2. Current Foundation

The current system provides:

- deterministic advisory parsing and facility/terminology authority services;
- a shared Semantic Resolution Agent only for genuine ambiguity;
- a canonical compiler or bounded Decision Case Assembly Agent;
- a source-bounded Graph Patch;
- deterministic formal-graph validation;
- RDF and Neo4j projections with provenance;
- bounded native tool use in the conditional Assembly and Query Agents;
- stable canonical facility identifiers and idempotent Neo4j merge behavior;
- explicit `ok`, `insufficient`, and `blocked` outcomes.

The visualization branch addresses the remaining presentation gap with a
bounded read-only surface over one completed query run.

## 3. User Task

The supported task is:

> Inspect one published ATCSCC decision record and trace every displayed
> statement to validated graph evidence.

The Query Agent supports five field-question families plus one combined-record
question. The read-only page displays one already recorded question and its
frozen result; it does not accept a new question.

| Question family | Example | Required graph evidence |
| --- | --- | --- |
| Traffic-management measure | What measure was published? | `rdf:type` |
| Controlled facility | Which airport was controlled? | `atm:controlledNASelement` |
| TMI operational period | When did the measure apply? | `atm:effectiveStartTime`, `atm:effectiveEndTime` |
| Declared reason | What reason did the advisory state? | `atm:impactingCondition` when valid, otherwise a source-bound `ProfileGap` |
| Evidence and provenance | Which source supports this statement? | fact ID, source ID, evidence text, provenance edge |

Natural-language wording may vary, but the request must map to one or more of
these registered families. An unsupported request must be rejected before any
provider call.

## 4. Evidence Language

The interface must keep three evidence categories separate.

### Source statement

A value explicitly contained in the advisory, for example:

> The advisory records WEATHER as the impacting condition.

### System association

A deterministic or authority-grounded graph relation, for example:

> The event is associated with the canonical KLGA airport entity.

### Unsupported inference

A causal or prescriptive statement not established by the available graph, for
example:

> Thunderstorms caused the capacity reduction and therefore Ground Stop was the
> optimal decision.

Unsupported inference must not be displayed as an answer. Missing evidence is
shown as missing, not completed from model knowledge.

## 5. Minimum Case Set

The bounded demonstrator uses two positive real advisories plus one real
missing-reason cancellation control:

- one Ground Stop advisory;
- one Ground Delay Program advisory;
- one Ground Delay Program cancellation used as a missing-reason control.

The records cover distinct airports or decision forms. The missing-reason
control verifies field-level insufficiency and must not trigger fabricated
completion.

The case set is a system demonstrator, not a Gold benchmark and not evidence of
operational decision quality.

## 6. System Boundary

### Reused components

- the existing ATCSCC source loader;
- the existing NASA ATMONTO-derived schema slice;
- the four construction Agents;
- the Formal Graph Kernel;
- validated run artifacts;
- the existing Query Agent and its read-only graph tools;
- the existing Neo4j projection for optional graph exploration.

### Small extensions allowed

- ensure source-supported advisory number and declared-reason facts are
  materialized when present and valid under the existing schema;
- add advisory number and declared-reason predicates to the Query Agent's
  registered read surface;
- expose source-bound profile gaps through a read-only tool without promoting
  them to formal facts;
- add bounded intent routing for the five field questions and the combined
  record question;
- add a read-only explorer over validated run artifacts;
- create one sanitized frozen demonstration bundle without credentials or raw
  provider reasoning.

### Prohibited expansion

- no new Agent role;
- no ontology class or property outside the active schema slice;
- no weather, ASPM, flight, NOTAM, or live operational source;
- no cross-advisory lifecycle grouping;
- no similarity ranking or case-based recommendation;
- no unrestricted general chat;
- no graph edits from the interface;
- no causal or optimal-decision claim.

## 7. Interaction Flow

```text
Operator selects one completed query run at server startup
  -> validate its source, graph, profile-gap, and query artifacts
  -> build one QueryVisualizationBundle
  -> freeze the bundle in memory
  -> serve local static assets and the frozen bundle
  -> display the recorded answer, query-local graph, properties, and evidence
```

The validated run artifacts are the reproducible record for the explorer.
Neo4j remains a separate debugging projection and is neither an explorer
dependency nor a second source of truth.

## 8. User Interface

The implemented browser view contains four panels:

1. **Answer and status**
   - recorded question as read-only text;
   - recorded answer;
   - `ok`, `insufficient`, or `blocked` status;
   - “Query-local evidence” and “Read only” labels.

2. **Retrieved knowledge graph**
   - only nodes and edges contained in the frozen query bundle;
   - formal fact edges shown separately from derived provenance;
   - no graph expansion or graph write.

3. **Query-scoped properties**
   - only properties retrieved for the recorded question;
   - no unrelated record reconstruction;
   - missing requested evidence shown only when the query requested it.

4. **Evidence and provenance**
   - exact evidence text;
   - fact and source identifiers;
   - profile gaps as audit cards rather than graph facts;
   - an explicit empty state for insufficient evidence.

The run directory is selected by the operator when the local server starts.
The server validates and freezes one `QueryVisualizationBundle` in memory.
There is no browser-side case selector, active question input, Agent execution,
Neo4j connection, or live-model mode.

## 9. Success Criteria

The stage succeeds only when:

- both positive real advisories and the real missing-reason cancellation
  control ingest into validated decision records;
- the registered real-case question checks return the correct status;
- every positive answer claim maps to a fact ID and real source ID;
- every source-only reason maps to a source-bound profile-gap record;
- every displayed evidence phrase occurs in the registered source record;
- declared reasons are phrased as advisory statements, not proven causes;
- the missing-reason control shows the missing field without a provider call;
- unsupported questions produce no provider call;
- repeated ingest creates no duplicate event, facility, or relationship;
- the explorer works offline from the frozen bundle;
- repeated reads return the same frozen bundle without rereading artifacts;
- repository lint and tests pass.

## 10. Failure Conditions

The stage is not complete if:

- the page hard-codes decision values outside a frozen artifact;
- a Query Agent answer uses model memory or the raw advisory instead of graph
  tools;
- the interface displays a reason that is absent from the graph;
- a positive statement lacks provenance;
- the local graph and displayed evidence disagree;
- an unsupported question is presented as a successful answer;
- a missing field is silently replaced by a guessed value;
- Neo4j and the validated run artifact are treated as competing authorities.

## 11. Provider Budget

The read-only browser has a provider-call budget of zero. It consumes an
existing `QueryVisualizationBundle` and cannot invoke a model factory.

The budget below remains only as a historical upper bound for a separate
future live Query Agent acceptance smoke; it is not part of the browser
implementation.

The final real smoke is limited to:

- two construction-model calls per newly ingested real case;
- one bounded Query Agent cycle per real case;
- no prompt resampling or post-result tuning;
- no more than eight provider calls for the complete smoke.

If the expected call count exceeds eight, stop and request a scope decision.

## 12. Implementation Record

### Completed on `main`

- Source-audited case selection.
- Cross-midnight operational-period parsing.
- Formal GDP-reason normalization and exact source-span boundaries.
- Source-bound Ground Stop profile-gap persistence and retrieval.
- Registered measure, facility, operational-period, declared-reason,
  provenance, and combined-record query routing.
- Early insufficient handling for missing and unsupported questions.
- Referential and canonical-identity checks.

### Completed on the isolated visualization branch

- Frozen query-local visualization bundle.
- Read-only four-panel browser interface.
- Formal-fact, provenance, profile-gap, and missing-state presentation.
- Desktop, narrow-layout, keyboard, and interaction verification.

### Paused

- Merge of `codex/kg-visualization-research` into `main`.
- Optional live-model acceptance smoke.
- Any broader multi-record or interactive search API.

The Explorer contract consumes current, regenerated run artifacts. Batch C.1
does not provide a reader for earlier run formats; the retained command names
are current UX, not a compatibility promise.

## 13. Explicitly Deferred Work

After this Explorer stage, the separately approved Decision Context Case v0
increment is superseded by Decision Case Graph v1. The active branch adds
time-bounded TAF/METAR context and source-qualified BTS-reported public
operational observations for the same three records. It preserves the
Explorer's reason semantics, creates no causal event-to-weather fact, and does
not merge the paused browser branch.

Decision-episode grouping, ASPM demand/capacity evidence, flight-level impact,
historical similarity, candidate ranking, and TMI recommendation remain later
stages.
