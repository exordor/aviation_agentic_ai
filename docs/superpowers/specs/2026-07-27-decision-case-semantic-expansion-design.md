# Decision Case Semantic Expansion Design

Status: approved design, implementation not started

Date: 2026-07-27

Branch: `codex/decision-case-semantic-expansion-design`

Normative parent design:
`docs/multi_agent_kg_system_design.md`

Predecessor design:
`docs/superpowers/specs/2026-07-27-decision-case-graph-v1-design.md`

## 1. Purpose

Decision Case Graph v1 proves that one ATCSCC record can be reconstructed with
canonical facilities, source-bound Weather reports, and BTS-reported public
operational observations. The next system increment must make that graph
semantically useful across records without turning the project into an
unbounded question-answering system or an automatic TMI recommender.

The approved expansion supports four user questions:

1. How did a TMI decision evolve from initial publication through update,
   extension, or cancellation?
2. What operational situation was timestamp-eligible under the admitted
   source policy by decision time, observed during the TMI, and observed
   afterward?
3. Which facilities or flights were explicitly in scope, potentially
   applicable, confirmed as controlled, or associated with an observed
   operational outcome?
4. Which historical decision records or decision-time situations are similar,
   and which verified features make them similar or different?

The four questions are implemented as sequential semantic capabilities. They
do not become four new Agent roles. Existing Agents remain responsible for
bounded source interpretation, canonical resolution, graph construction, and
query orchestration. Deterministic components perform cross-record linking,
time alignment, rule evaluation, aggregation, and similarity calculation.

## 2. Stage Header

| Item | Decision |
| --- | --- |
| User-facing capability | Inspect the evolution, context, applicability, and historical neighbors of retrospective ATCSCC decision records with explicit evidence boundaries. |
| Smallest end-to-end result | Link the three BNA Ground Stop records into one auditable episode, reconstruct one JFK decision-time situation, expose declared scope separately from flight-level applicability, and retrieve a small set of temporally eligible similar cases. |
| Minimum components | Existing five-Agent system, validated record runs, source-specific deterministic adapters, independent validation profiles, a corpus assembly workflow, bounded read-only query tools, and versioned rule/feature profiles. |
| Expected evidence | Stable record and episode identities, source/checksum bindings, explicit temporal roles, profile-owned facts, derivation traces, honest missing states, and zero unsupported model completions. |
| Success condition | All four question classes can be answered from validated record or corpus artifacts while preserving formal fact, derived assessment, audit association, profile-gap, insufficient, and blocked distinctions. |
| Failure condition | Records from different TMI families are grouped, post-decision evidence leaks into decision-time views, a BTS row is treated as proof of TMI control, missing scope is interpreted, similarity uses the selected decision or outcome as a decision-state feature, or an unsupported question reaches a provider. |
| Explicitly deferred | Causal explanation, optimality, TMI recommendation, unrestricted GraphRAG, ontology auto-expansion, a new Agent role, live operational use, and full-corpus model execution. |
| Classification | Critical Path for the system's semantic usefulness; source admission, temporal integrity, and identity review are Evidence Quality gates. |

This is a system and framework construction stage. It does not compare
Single-Agent and Multi-Agent architectures and does not claim that additional
Agent roles improve accuracy.

## 3. Relationship To Existing Designs

This document extends, rather than replaces, the following accepted behavior:

- one immutable source record remains the unit of ingest;
- each record retains its own ATMONTO TMI identity and source provenance;
- Ground Stop `2026-05-19:123` retains a source-bound reason profile gap;
- GDP `2026-05-19:138` retains the formal normalized reason `weather`;
- GDP cancellation `2026-05-20:020` retains a missing declared reason;
- Weather context remains non-causal;
- BTS observations retain their BTS reporting scope and are not FAA demand,
  AAR, capacity, EDCT, or proof of TMI effect;
- no optional semantic layer can invalidate an already verified ATCSCC record;
- unsupported or missing registered questions are resolved before provider
  construction.

This document is the approved design for future sequential batches. It does
not, by itself, change the active runtime scope of the normative parent.
Before each batch is implemented, the implementation change must version and
amend the parent design so its active scope, profiles, deterministic
components, query tools, artifacts, and acceptance requirements agree with the
implemented batch.

The intended amendments are explicit:

- parent Section 2.2's deferred cross-advisory coreference is narrowed to the
  bounded, deterministic episode reconstruction in Batch 1; general event
  coreference remains deferred;
- parent Section 5.2's three-layer graph is extended only by the independently
  approved profile for the batch being implemented;
- ASPM remains deferred until the Batch 2B source-admission gate passes;
- parent Section 12.3's router-only boundary for high-level context tools is
  preserved through bound query steps in Section 9 of this design;
- parent Sections 13, 14, 15, 18, and 20 are amended incrementally when their
  corresponding deterministic component, artifact, or acceptance contract is
  implemented;
- parent Section 22 continues to block unapproved source families and new
  classes or properties. A reviewed source catalog entry and checksum-pinned
  profile are approval prerequisites, not exceptions to that gate.

This design also supersedes the tentative `Lifecycle Link Audit v0` note in
Section 12 of the predecessor design. A uniquely supported, deterministic
episode-membership assessment may enter a separate reconstruction layer.
However, it must not be represented as a source-asserted revision edge.
`prov:wasRevisionOf` remains restricted to records whose source explicitly
identifies the predecessor or revision relation.

The current one-record commands remain valid. Corpus assembly is a separate
operation over validated run artifacts and does not require repeating model
ingest for records that have already passed validation.

This design extends the predecessor namespace set with:

```text
case:       urn:aviation-agentic-ai:decision-case-schema:
caseaction: urn:aviation-agentic-ai:decision-action:
```

Only the application concepts explicitly frozen in a reviewed profile may use
these namespaces.

## 4. Approved Architecture Adaptation

### 4.1 Keep the five Agent roles

The active roles remain:

1. Advisory Agent;
2. Facility Agent;
3. Terminology Agent;
4. Knowledge Graph Construction Agent;
5. Query Agent.

No Weather Agent, BTS Agent, Lifecycle Agent, Applicability Agent, Similarity
Agent, or one-Agent-per-source pattern is introduced.

This boundary is intentional:

- source parsing, temporal filtering, aggregation, and rule evaluation are
  deterministic;
- source-specific authority is expressed through profiles and adapters;
- cross-record semantic assembly must be reproducible without model sampling;
- the Query Agent gains meaningful tool choice without receiving unrestricted
  graph access;
- a new Agent is justified only if a later observed ambiguity cannot be
  resolved by deterministic authority rules.

### 4.2 Separate record ingest from corpus assembly

The architecture has two workflows:

```text
Record Ingest Workflow

ATCSCC source record
  -> existing construction Agents
  -> deterministic Formal Graph Kernel
  -> validated record graph
  -> source-specific deterministic adapters
  -> independently validated semantic layers
  -> immutable record-run artifacts
```

```text
Corpus Assembly Workflow

validated record-run artifacts
  -> CorpusRegistry
  -> EpisodeLinker
  -> OperationalSituationBuilder
  -> ApplicabilityEngine
  -> CaseFeatureBuilder and CaseIndexer
  -> corpus-level decision-case graph and audit artifacts
```

The corpus workflow reads only validated artifacts whose manifests, source
snapshots, profiles, and checksums agree. It does not reopen arbitrary raw
files, call the construction Agents, or silently repair a blocked record.

It writes a separate immutable corpus directory. It never edits a member
record-run directory. The corpus formal graph is a validated union that:

- preserves member record fact IDs unchanged;
- deduplicates canonical entities by canonical ID;
- appends only corpus-owned episode, situation, applicability, or other
  approved assertions;
- records every member run and manifest checksum in `corpus_manifest.json`;
- emits corpus JSONL, RDF, and Neo4j projections with stable identities.

The common formal outputs are:

```text
corpus_kg.jsonl
corpus_kg.ttl
corpus_neo4j_nodes.jsonl
corpus_neo4j_relationships.jsonl
```

Corpus assembly must receive its state explicitly. Module-global mutable state
or a shared context holder is not an accepted runtime contract because it
would make parallel, repeated, or multi-run assembly unsafe.

### 4.3 Source catalog and common source-layer contract

Source metadata is separated from run snapshots:

- `SourceCatalog` is a tracked registry of source-family definitions;
- `SourceSnapshotRegistry` records the exact immutable source records used by
  one record or corpus run.

Each `SourceCatalog` entry freezes only the integration metadata needed by this
system:

```text
source family and authority
record schema/version
identifier and canonicalization policy
temporal-field roles
spatial or facility scope
coverage and known limitations
license or redistribution constraint
adapter ID/version
owning validation profile
```

The catalog does not contain run data and is not a new Agent. A source cannot
be admitted because a snapshot exists; its catalog entry and profile must
first define what its fields are allowed to mean.

Every optional or future source adapter emits a typed `SourceLayerBundle`:

```python
class SourceLayerBundle:
    layer_id: str
    source_family: str
    source_snapshot_ids: tuple[str, ...]
    profile_id: str
    profile_checksum: str
    temporal_roles: tuple[str, ...]
    canonical_entity_refs: tuple[str, ...]
    formal_facts: tuple[ValidatedFact, ...]
    derived_assertion_proposals: tuple[DerivedAssertionProposal, ...]
    audit_only_associations: tuple[AuditAssociation, ...]
    fact_traces: tuple[FactTraceRef, ...]
    status: Literal["ok", "insufficient", "blocked"]
    failure_reason: str | None
```

The three semantic payload categories are disjoint:

- `formal_facts`: profile-admitted statements eligible for JSONL, RDF, and
  Neo4j materialization;
- `derived_assertion_proposals`: deterministic membership or rule-assessment
  candidates that have not yet passed the Formal Graph Kernel;
- `audit_only_associations`: selections or co-occurrences that must not be
  interpreted as ontology facts.

One payload cannot be silently promoted into another category.

A derived proposal has the following minimum contract:

```python
class DerivedAssertionProposal:
    proposal_id: str
    subject_id: str
    subject_class_iris: tuple[str, ...]
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_id: str | None
    object_class_iris: tuple[str, ...]
    literal_value: object | None
    literal_datatype_iri: str | None
    profile_id: str
    profile_checksum: str
    evidence_mode: Literal["system_membership", "rule_assessment"]
    evidence_ref: str
    supporting_fact_ids: tuple[str, ...]
    source_binding_ids: tuple[str, ...]
    procedure_or_rule_id: str
    procedure_or_rule_checksum: str
```

The deterministic Formal Graph Kernel remains the sole publication gate:

```python
class DerivedAssertionKernelContext:
    schema_guide_id: str
    schema_guide_checksum: str
    validation_profile_registry: ValidationProfileRegistry
    evidence_trace_registry: EvidenceTraceRegistry
    procedure_registry: ProcedureRegistry
    source_snapshot_registry: SourceSnapshotRegistry
    canonical_type_index: CanonicalTypeIndex
    validated_fact_index: ValidatedFactIndex


validate_derived_assertions(
    proposals: tuple[DerivedAssertionProposal, ...],
    context: DerivedAssertionKernelContext,
) -> DerivedAssertionValidationResult
```

The context is immutable and checksum-pinned for one validation execution. It
contains every registry needed to validate profile ownership, predicate
domain/range, datatype, evidence references, source reachability, procedure
identity, and canonical entity type.

New graph nodes are validated as an atomic proposal batch. Every new node must
have one or more profile-admitted `rdf:type` proposals in the same batch. The
kernel builds a provisional type closure from:

1. canonical types already accepted in `canonical_type_index`;
2. accepted existing `rdf:type` facts;
3. same-batch `rdf:type` proposals whose classes are allowed by the owning
   profile.

It then validates dependent object and datatype assertions against that type
closure. A failed required type proposal blocks every dependent assertion.
Self-consistent but profile-unapproved class/predicate combinations remain
schema violations; a builder cannot invent a class merely to satisfy its own
domain/range proposal.

`object_kind="iri"` requires `object_id`, forbids `literal_value` and
`literal_datatype_iri`, and validates object classes. `object_kind="literal"`
requires a canonical literal and admitted datatype, forbids `object_id`, and
requires an empty object-class tuple.

Each proposal receives exactly one outcome:

```text
accepted
schema_violation
evidence_violation
blocked
```

Only `accepted` proposals are converted into canonical `ValidatedFact`
instances. RDF and Neo4j materializers accept `ValidatedFact` inputs only;
they never accept a `DerivedAssertionProposal`, an audit association, or a
builder-specific assertion type. This prevents deterministic builders from
bypassing the same schema, evidence, source-binding, and identity checks
applied to source-derived facts.

A violation on a proposal required by the selected layer makes that component
`blocked`; a non-required invalid proposal remains only in the validation
artifact and cannot affect published facts. Accepted fact IDs are derived from
the validated canonical statement, profile checksum, evidence mode, and
evidence reference, not merely copied from the proposal ID.

Proposal outcomes and their evidence are persisted in
`derived_assertion_validation.jsonl`; its path, count, checksum, profile, and
status are registered in the relevant run or corpus manifest.

Audit-only associations pass their own deterministic schema, source-binding,
identity, and checksum validator before persistence or query exposure. Passing
that validator makes them readable audit records, never formal graph facts.

### 4.4 Temporal roles

Every source family declares the time role of each timestamp it contributes:

```text
issue_time
available_time
observation_time
valid_time
operational_time
retrieval_time
```

The roles are not interchangeable. In particular:

- `retrieval_time` never proves that information was available to a decision
  maker;
- a forecast's `issue_time` must not occur after the decision cutoff;
- a report version must be proven to exist by the cutoff under its
  source-specific publication or availability policy;
- an observation after a decision may describe operational context or outcome
  but not decision-time knowledge;
- a TMI's literal advisory `EFFECTIVE TIME` remains separate from the
  operational period parsed from the TMI message;
- a later record's issue time must not be used to enrich an earlier decision
  state unless the user explicitly requests a retrospective full-history view.

### 4.5 Extensible semantic layers

The formal graph and its associated audit outputs are partitioned by profile
ownership:

```text
decision_record
weather_observation
public_operational_observation
decision_episode
operational_situation
applicability_assessment
observed_flight_outcome
```

Historical similarity is initially an assessment artifact, not a permanent KG
relationship. A similarity result may be materialized later only after its
feature profile, temporal policy, and lifecycle have been separately approved.

Every layer records:

- profile ID and checksum;
- source IDs and snapshot checksums;
- status `ok`, `insufficient`, or `blocked`;
- accepted fact or assertion counts;
- artifact path and checksum;
- exact dependencies on record-run or corpus artifacts.

### 4.6 Failure isolation

A semantic layer is:

- `ok` when all required bindings, profiles, and derivations validate;
- `insufficient` when admissible source evidence is absent;
- `blocked` when evidence exists but a checksum, schema, identity, temporal,
  or derivation invariant fails.

Failure is local to the layer. For example:

- a blocked episode layer does not delete the three member record graphs;
- absent ASPM produces an insufficient demand-capacity view while Weather and
  BTS views remain available;
- unknown flight-scope semantics prevent a flight applicability assertion but
  do not remove the source-declared airport or ARTCC scope;
- insufficient similarity coverage does not change the source cases.

Every composite read also carries component-level status:

```python
class ComponentLayerStatus:
    layer: str
    required: bool
    status: Literal["ok", "insufficient", "blocked"]
    artifact_ids: tuple[str, ...]
    failure_reason: str | None
```

Status roll-up is deterministic and introduces no fourth internal state:

1. a requested component marked `blocked` makes the composite result
   `blocked`;
2. otherwise, a required component marked `insufficient` makes the composite
   result `insufficient`;
3. otherwise, the composite result is `ok`;
4. an optional `insufficient` component remains visible but does not downgrade
   an otherwise `ok` result;
5. a component not requested by the plan is not evaluated and cannot affect
   the result.

Verified payload from an `ok` component may remain visible in an
`insufficient` composite result. A blocked component is never silently
omitted.

### 4.7 Conditional future Cross-Source Resolution Agent

A Cross-Source Resolution Agent is not part of this design. It may be proposed
later only when all of the following are observed:

1. deterministic candidate generation produces more than one credible
   canonical target or episode link;
2. authority, source type, identifier, time, and structural constraints do not
   resolve the ambiguity;
3. the ambiguity blocks a required user capability;
4. a bounded candidate set and independently testable abstention contract can
   be frozen.

If admitted, it may choose or abstain among deterministic candidates. It may
not create candidates, edit source facts, bypass profile validation, or write
directly to the graph.

## 5. Batch 1 — Decision Episode Reconstruction

### 5.1 User question

The capability answers:

> How did this TMI evolve from initial publication through update, extension,
> or cancellation?

It reconstructs a retrospective episode from independently published records.
It does not claim access to an internal FAA decision process.

### 5.2 Minimum real episode

The first positive episode is the BNA Ground Stop sequence:

| Record | Reconstructed role | Operational period | Issue time | Source signal |
| --- | --- | --- | --- | --- |
| `2026-05-14:083` | initial Ground Stop | `2026-05-14T21:12:00Z` to `2026-05-14T22:30:00Z` | `2026-05-14T21:25:00Z` | `CDM GROUND STOP` |
| `2026-05-14:089` | update and extension | `2026-05-14T21:12:00Z` to `2026-05-14T23:00:00Z` | `2026-05-14T22:25:00Z` | `EXTENDED UPDATE TIME OF 2300` |
| `2026-05-14:092` | Ground Stop cancellation | `2026-05-14T22:50:00Z` to `2026-05-15T01:35:00Z` | `2026-05-14T22:52:00Z` | `CDM GS CNX`, `OBJECTIVES MET` |

The cancellation record's own cancellation period remains a record fact. It
does not replace the earlier Ground Stop operational periods.

Required negative controls are:

- Ground Stop `2026-05-19:123` and GDP `2026-05-19:138` share KJFK and
  overlapping time but have different TMI families and must not be grouped;
- EWR GDP cancellation `2026-05-20:020` has no uniquely verified predecessor
  in the bounded input and must remain unresolved rather than being attached to
  the nearest GDP.

### 5.3 Semantic model

Each advisory remains an independently sourced ATMONTO TMI record.

The stable conceptual episode is:

```text
case:DecisionEpisode
  rdfs:subClassOf prov:Entity
```

Its ID is derived from:

```text
canonical controlled facility
normalized TMI family
canonical source ID of the earliest accepted root record
episode identity-profile ID and checksum
```

The root record may be selected only from a complete candidate scope. If later
source discovery reveals an earlier credible root, the system creates a new
conceptual episode identity and retains the old identity and reconstruction
for audit; it does not silently reuse the old ID.

One execution-specific reconstruction is:

```text
case:DecisionEpisodeReconstruction
  rdfs:subClassOf prov:Collection
```

It is also explicitly typed `prov:Entity` and linked to its conceptual episode
with `prov:specializationOf`. Its stable ID is derived from:

```text
ordered member record IDs
member run IDs and manifest checksums
episode-link profile ID and checksum
linker procedure ID and checksum
accepted link-assessment IDs
```

Members are connected with `prov:hadMember`. Membership means:

> These source records were accepted by the versioned episode-link procedure
> as one retrospective TMI episode reconstruction.

Membership does not mean that one advisory caused another or that the source
explicitly named the predecessor.

Source-explicit record action roles use `dcterms:type` with versioned SKOS
concepts:

```text
caseaction:update
caseaction:extension
caseaction:cancellation
```

A record may be both `update` and `extension`. Every direct record role requires
an exact source signal. The concepts do not replace the record's TMI class.

`initial` is not a global record type because it is relative to one
reconstruction. Episode position is represented by a reconstruction-scoped
assessment:

```python
class EpisodeMembershipAssessment:
    membership_assessment_id: str
    conceptual_episode_id: str
    reconstruction_id: str
    record_id: str
    position_role: Literal["initial", "intermediate", "terminal"]
    source_action_roles: tuple[
        Literal["update", "extension", "cancellation"],
        ...,
    ]
    evidence_mode: Literal["system_membership"]
    supporting_assessment_ids: tuple[str, ...]
    supporting_fact_ids: tuple[str, ...]
    membership_trace_id: str
    profile_id: str
    profile_checksum: str
    procedure_id: str
    procedure_checksum: str
```

Only a validated membership proposal may publish an assessment node. The
record itself is never given a source-style `initial` assertion unless that
wording is explicitly present and separately admitted.

`prov:wasRevisionOf` is published only when the source explicitly names the
predecessor or an equivalent explicit revision relation. The BNA sequence does
not gain `prov:wasRevisionOf` merely because deterministic episode membership
is accepted.

### 5.4 Episode-link contract

Every eligible predecessor-successor pair in the complete candidate scope
produces:

```python
class EpisodeLinkAssessment:
    assessment_id: str
    candidate_pair_id: str | None
    predecessor_record_id: str | None
    successor_record_id: str
    normalized_tmi_family: str
    action_roles: tuple[str, ...]
    decision: Literal[
        "accepted",
        "rejected",
        "ambiguous",
        "unresolved",
    ]
    satisfied_condition_fact_ids: tuple[str, ...]
    failed_conditions: tuple[str, ...]
    competing_predecessor_ids: tuple[str, ...]
    candidate_scope_id: str
    candidate_scope_checksum: str
    source_signal_refs: tuple[str, ...]
    rule_profile_id: str
    rule_profile_checksum: str
```

The normalized TMI family is derived deterministically from the source header
and reviewed terminology mapping. A cancellation record such as `GS CNX`
belongs to the Ground Stop family even if its current record class is a more
general `TrafficManagementInitiative`.

An episode link is accepted only when all mandatory conditions hold:

1. the canonical controlled facility is identical;
2. the normalized TMI family is identical;
3. successor issue time is strictly later;
4. operational or cancellation intervals are compatible under the frozen
   episode-link profile;
5. the successor contains a source-supported update, extension, cancellation,
   or continuation signal;
6. no second credible predecessor remains under the same rules.

Facility and time proximity alone are never sufficient.

The profile freezes:

- allowed TMI-family mappings;
- accepted source action markers;
- maximum chronology gaps;
- interval compatibility rules by action type;
- tie and ambiguity behavior;
- whether a missing required field returns `insufficient` or `blocked`.

No model scores, repairs, or selects an episode link.

The linker also requires an `EpisodeCandidateScope`:

```python
class EpisodeCandidateScope:
    candidate_scope_id: str
    source_snapshot_ids: tuple[str, ...]
    canonical_facility_id: str
    normalized_tmi_family: str
    search_start: datetime
    search_end: datetime
    included_record_ids: tuple[str, ...]
    eligible_pair_ids: tuple[str, ...]
    source_enumeration_artifact_id: str
    source_enumeration_artifact_checksum: str
    source_enumeration_procedure_id: str
    source_enumeration_procedure_checksum: str
    coverage: Literal["complete", "partial", "unknown"]
    scope_checksum: str
```

Eligible pairs are enumerated exhaustively from all included records with the
same canonical facility and normalized TMI family where predecessor issue time
is earlier than successor issue time and both records fall within the frozen
search window. Action markers and interval compatibility are evaluated after
enumeration; they cannot be used to omit a pair before it receives an
assessment.

An accepted episode link requires `coverage="complete"` for the frozen search
window. Completeness must come from a checksum-pinned source enumeration or
equivalent reviewed corpus inventory, not from the absence of another record
in a hand-selected fixture. `partial` or `unknown` coverage yields
`unresolved`.

Before acceptance, the linker compares the sorted pair IDs from the candidate
scope with the sorted pair IDs represented by
non-summary `EpisodeLinkAssessment` rows. Missing or unexpected pair
assessments block the
episode layer. A successor with no eligible predecessor receives one explicit
`unresolved` summary assessment with `predecessor_record_id=None`; absence of a
row is not evidence that no predecessor exists. Only this summary row may have
`candidate_pair_id=None`.

The accepted episode graph also enforces:

- one record belongs to at most one accepted reconstruction under one profile;
- every successor has at most one accepted predecessor;
- accepted links are acyclic;
- a fork, overlap, or second credible predecessor is `ambiguous` in v0.

The corpus registry additionally enforces:

- byte-identical re-ingests with the same canonical source ID, source snapshot
  checksum, and validated-fact checksum collapse to one record identity;
- conflicting validated runs for the same canonical source record block
  corpus assembly unless the source version is explicitly represented;
- same-concept exclusion in retrieval uses `case:DecisionEpisode`, not a
  reconstruction ID.

### 5.5 Artifacts

The corpus output includes:

```text
decision_episodes.jsonl
episode_membership_assessments.jsonl
episode_link_assessments.jsonl
episode_candidate_scopes.jsonl
episode_fact_trace.jsonl
corpus_manifest.json
```

`decision_episodes.jsonl` contains only accepted episode reconstructions.
Rejected, ambiguous, and unresolved assessments remain in
`episode_link_assessments.jsonl`.

The corpus manifest pins:

- member run directories and run-manifest checksums;
- record, facility, and TMI-family identities;
- conceptual episode IDs and reconstruction IDs;
- episode identity-profile ID/checksum, episode-link profile ID/checksum, and
  linker procedure checksum;
- candidate-scope source-enumeration artifact/procedure checksums;
- episode, membership, candidate-scope, and link-assessment artifact paths,
  counts, and checksums;
- layer status and failure reason.

### 5.6 Query surface

Add the read-only high-level tool:

```python
get_decision_episode(
    record_id: str | None = None,
    conceptual_episode_id: str | None = None,
    reconstruction_id: str | None = None,
) -> DecisionEpisodeRead
```

The result contains:

- conceptual episode ID and reconstruction ID;
- ordered member records;
- each record's source-explicit action roles, reconstruction-relative position,
  issue time, and operational period;
- source-supported comments or action markers;
- accepted membership/link assessment IDs and supporting fact IDs;
- ambiguous or unresolved status when no accepted episode exists;
- source IDs, profile checksum, and procedure checksum.

The answer separates:

1. source records;
2. system-reconstructed episode membership;
3. source-explicit revision statements, if any;
4. unresolved or competing links.

### 5.7 Batch 1 acceptance

Batch 1 succeeds when:

- BNA `083`, `089`, and `092` form one ordered Ground Stop episode;
- the conceptual episode and reconstruction have distinct stable IDs linked by
  `prov:specializationOf`;
- `083` is `initial` only in its membership assessment, not by a fabricated
  source-text record type;
- `089` is classified as update and extension;
- `092` is classified as cancellation;
- the earlier periods and the cancellation record's own period remain
  separately queryable;
- KJFK Ground Stop `123` and GDP `138` remain separate;
- EWR cancellation `020` is unresolved in the bounded corpus;
- repeated assembly yields identical episode and assessment IDs;
- byte-identical re-ingests collapse, while conflicting runs for one source
  record block assembly;
- discovery of an earlier accepted root creates a new conceptual identity and
  retains the old reconstruction;
- the BNA candidate window is checksum-pinned and complete;
- removing an eligible rival record or marking coverage partial makes the link
  unresolved rather than accepted;
- every eligible pair in the persisted candidate scope has exactly one
  assessment, and a missing or extra assessment blocks publication;
- candidate scope, source-enumeration provenance, identity profile, and link
  profile are all checksum-pinned in the corpus manifest;
- no record is accepted into two episodes and no accepted path contains a
  cycle or unresolved fork;
- no `prov:wasRevisionOf` edge is fabricated;
- no Agent or provider call is added.

It fails when a cross-family link is accepted, an ambiguous predecessor is
silently chosen, an individual record is overwritten by an episode summary, or
a source-explicit update, extension, or cancellation role is asserted without
exact source evidence.

## 6. Batch 2 — Operational Situation Reconstruction

### 6.1 User question

The capability answers:

> What timestamp-eligible information was available by decision time, what was
> observed during the TMI, and what was observed afterward?

The answer is a temporally partitioned evidence reconstruction, not a causal
explanation of why the FAA selected a TMI.

### 6.2 Three evidence views

The views are:

1. `decision_time`: information whose exact source record version satisfies
   the admitted source's publication or availability policy at or before the
   selected record's issue time;
2. `operational`: observations whose phenomenon or operational time falls
   within the record or episode operational interval;
3. `outcome`: observations in an explicitly defined post-operation or
   cross-operation window.

Each view records its cutoff and time policy. A record-level query defaults to
that record's issue time. An episode-level query must identify the episode
member whose decision point is being reconstructed; it cannot merge later
updates into the initial decision-time view.

`decision_time` means timestamp-eligible under a source-specific policy. It
does not prove that an FAA decision maker actually read or relied on the
report. The policy must declare which timestamp proves that the exact version
existed. If a source exposes a distinct `available_time`, it is mandatory. If
the official report `issue_time` is the publication timestamp, the profile may
use it explicitly. Retrieval time is never a substitute.

An amended, corrected, or revised report is a separate version with its own
issue or availability time. A later version cannot be backdated into an
earlier view merely because its observation or valid time precedes the cutoff.
If the exact version's publication time cannot be established, the
decision-time group is `insufficient`.

The same rule applies to ASPM. If an ASPM row or revision does not expose an
authoritative publication or availability time under its admitted profile, it
cannot enter `decision_time`, even when its interval precedes the advisory. It
may appear only in a clearly labeled retrospective `operational` or `outcome`
view.

`operational` and `outcome` are query projections rather than mutually
exclusive partitions: an active-period BTS observation may describe activity
during the TMI and also be part of a retrospective outcome comparison. The
same observation ID is reused when it appears in both projections.

### 6.3 Minimum real case

The first case is GDP `2026-05-19:138` for KJFK:

```text
issue time:         2026-05-19T22:07:00Z
operational period: 2026-05-19T22:05:00Z to 2026-05-20T02:59:00Z
```

The minimum sources are the already admitted ATCSCC record, canonical KJFK,
eligible TAF/METAR reports, and BTS-reported observations.

### 6.4 Operational-situation model

The reconstruction is:

```text
case:OperationalSituationReconstruction
  rdfs:subClassOf prov:Collection
```

It is a `prov:Entity` with a stable identity derived from:

```text
record or episode decision-point ID
as-of time
view
member fact and observation IDs
source snapshot checksums
profile IDs and checksums
builder procedure ID and checksum
```

`prov:hadMember` identifies graph entities included in the reconstruction,
such as a decision record, Weather report, or observation. Individual fact IDs
remain in the reconstruction trace rather than being treated as collection
members unless the graph explicitly represents them as provenance entities.
Membership does not mean cause, motivation, justification, or outcome
attribution.

The design reuses:

- NASA ATMONTO Weather report and airport-statistics vocabulary;
- SOSA for observations;
- OWL-Time for intervals and instants;
- PROV-O for source and derivation;
- QUDT for values and units.

No broad custom operational ontology is created.

### 6.5 Batch 2A — Existing evidence assembly

Batch 2A uses only currently admitted evidence.

The decision-time view may contain:

- the latest eligible TAF version published or available at or before advisory
  issue time whose valid period overlaps the TMI period;
- the latest eligible METAR version published or available at or before issue
  time, whose observation time is within the configured pre-issue window;
- the official ATCSCC decision record and its source-declared fields.

The operational view may contain:

- METAR observations selected within the half-open TMI operational period;
- the active-period BTS-reported public observations, clearly labeled as
  public operational observations rather than decision inputs.

The outcome view may contain:

- BTS-reported observations from the approved baseline, active, and recovery
  windows;
- later Weather observations only when the selected view explicitly asks for
  them and labels them as retrospective observations.

Weather context associations remain audit-only and `causal_claim=false`.
BTS observations remain formal source-qualified observations under their own
profile. Neither expands or repairs the ATCSCC declared reason.

If no demand or capacity source is admitted, the response must state that the
demand-capacity state is unavailable. It must not approximate those fields
from BTS scheduled or completed arrivals.

### 6.6 Batch 2B — ASPM source admission

ASPM is admitted only after:

- access and redistribution constraints are documented;
- official field definitions are pinned;
- one immutable source snapshot and checksum are available;
- airport and time identities are validated;
- a dedicated ASPM profile is reviewed;
- null, unit, interval, and revision behavior are frozen.

The minimum desired fields are:

```text
arrival demand
Airport Arrival Rate
actual arrivals
runway configuration
EDCT observations
```

The profile may reuse:

```text
data:AirportStatisticsData
data:arrivalDemand
data:airportArrivalRate
```

and approved ATMONTO runway or flight-management vocabulary when the official
field definitions support it.

A demand-capacity difference may be deterministically derived only when demand
and AAR:

- refer to the same canonical airport;
- use compatible units;
- cover the same time interval;
- originate from an admitted snapshot;
- have non-null values;
- retain their source and derivation trace.

The difference does not prove that the imbalance caused, justified, or made a
TMI optimal.

Absence of ASPM leaves the demand-capacity group `insufficient`; it does not
block Batch 2A.

### 6.7 Operational-situation artifact

Each read or persisted reconstruction contains:

```python
class TemporalViewPolicyRef:
    policy_id: str
    policy_checksum: str
    cutoff_role: str
    interval_boundary: Literal["half_open"]


class TemporalWindow:
    start: datetime
    end: datetime
    role: str


class TemporalMemberBinding:
    member_id: str
    source_time_role: str
    source_time: datetime
    authoritative_available_time: datetime | None
    trace_id: str


class OperationalSituationRead:
    situation_id: str
    subject_id: str
    decision_point_record_id: str
    view: Literal["decision_time", "operational", "outcome"]
    as_of_time: datetime
    temporal_policy: TemporalViewPolicyRef
    selected_windows: tuple[TemporalWindow, ...]
    member_temporal_bindings: tuple[TemporalMemberBinding, ...]
    temporal_binding_trace_ids: tuple[str, ...]
    member_fact_ids: tuple[str, ...]
    member_observation_ids: tuple[str, ...]
    missing_evidence_groups: tuple[str, ...]
    component_statuses: tuple[ComponentLayerStatus, ...]
    source_ids: tuple[str, ...]
    profile_refs: tuple[ValidationProfileRef, ...]
    status: Literal["ok", "insufficient", "blocked"]
    failure_reason: str | None
```

The builder persists a derivation trace showing why every member was included
and which temporal predicate satisfied the selected view.

`missing_evidence_groups` uses a frozen typed vocabulary such as
`weather_forecast`, `weather_observation`, `demand`, `capacity`,
`runway_configuration`, and `public_operational_observation`; it does not use
free-form model labels.

`authoritative_available_time` is mandatory and non-null for every
`decision_time` member. It may be `None` for a retrospective `operational` or
`outcome` member when the admitted source does not expose publication time;
such a member is selected only by its declared observation or phenomenon-time
policy and can never be reused as decision-time knowledge or a historically
available similarity feature.

For an episode subject, `decision_point_record_id` is mandatory. The router
must reject or return `insufficient` before any tool or model construction when
it is absent or is not a member of the selected reconstruction.
For a record subject, the field is deterministically equal to that record ID.

The corpus artifacts are:

```text
operational_situations.jsonl
operational_situation_trace.jsonl
```

Their paths, counts, checksums, profile references, and layer status are
registered in `corpus_manifest.json`.

### 6.8 Query surface

Add:

```python
get_operational_situation(
    subject_id: str,
    view: Literal["decision_time", "operational", "outcome"],
    decision_point_record_id: str | None = None,
) -> OperationalSituationRead
```

The answer uses these sections:

1. Official decision record;
2. Available by issue time under the source-timestamp policy;
3. Observed during operation;
4. Observed afterward;
5. Missing evidence;
6. Provenance and limitations.

Sections not requested by the selected view are omitted rather than labeled
missing.

### 6.9 Batch 2 acceptance

Batch 2A succeeds when:

- GDP `138` returns only TAF/METAR evidence satisfying the frozen issue-time
  and valid-time rules;
- post-issue TAFs do not enter the decision-time view;
- a correction or amendment published after issue does not replace the exact
  earlier report version in the decision-time view;
- delayed, corrected, or revised METAR, TAF, and ASPM versions are admitted
  only when their exact authoritative availability time satisfies the selected
  temporal policy;
- a source that requires `available_time` but lacks it returns
  `insufficient`;
- every included member exposes its source-time role, selected window,
  temporal trace, and authoritative-availability field; the field is non-null
  for decision-time members and may be null only under the retrospective rule
  in Section 6.7;
- an episode-level request without a valid decision-point member makes zero
  provider calls;
- operational Weather and BTS observations are clearly separated from
  decision-time knowledge;
- missing demand and capacity are explicit;
- the ATCSCC reason remains `weather` without semantic expansion;
- Ground Stop `123` remains a reason profile gap;
- cancellation `020` remains missing reason;
- no Agent or provider call is added by the builder.

Batch 2B succeeds only after independently admitted ASPM evidence can be
queried with exact airport, time, unit, source, and profile provenance.

The batch fails if retrospective evidence appears as decision-time knowledge,
BTS is renamed as demand or capacity, or the system states a causal explanation
from temporal co-occurrence.

## 7. Batch 3 — Scope, Applicability, And Observed Flight Outcome

### 7.1 User question

The capability answers:

> Which facilities or flights were in scope, potentially applicable,
> confirmed as controlled, or associated with an observed operational
> outcome?

The system must not collapse these meanings into a single `affectedBy`
relationship.

### 7.2 Assessment dimensions and states

The approved states are:

```text
explicitly_in_scope
explicitly_out_of_scope
potentially_applicable
confirmed_controlled
not_applicable
insufficient
```

They belong to three assessment dimensions:

| Dimension | Allowed states |
| --- | --- |
| `declared_scope` | `explicitly_in_scope`, `explicitly_out_of_scope`, `insufficient` |
| `potential_applicability` | `potentially_applicable`, `not_applicable`, `insufficient` |
| `confirmed_control` | `confirmed_controlled`, `insufficient` |

A subject may have one assessment in each dimension. The states are not
mutually exclusive across dimensions: a flight may be potentially applicable,
later confirmed controlled, and also have an observed outcome.

`observed_operational_outcome` is an evidence category, not an assessment
state and not proof of control. It is returned alongside assessments when a
source reports an operational outcome for the same canonical flight identity.

The meanings are:

- `explicitly_in_scope`: the advisory directly includes a facility, geographic
  region, flight class, or named flight;
- `explicitly_out_of_scope`: the advisory directly excludes it;
- `potentially_applicable`: every condition in a reviewed applicability rule
  is verified for a flight. This is rule-based eligibility and is independent
  of whether a separate authoritative control record is available;
- `confirmed_controlled`: an admitted authoritative FAA control source
  explicitly identifies the flight or control action;
- `not_applicable`: at least one mandatory reviewed condition is verified
  false;
- `insufficient`: at least one mandatory condition is unknown and none is
  verified false.

Absence from an advisory inclusion list is not evidence of exclusion. It
remains unknown unless the admitted source definition and profile explicitly
declare that field exhaustive under closed-world semantics. Incomplete
coverage therefore yields `insufficient`, not `explicitly_out_of_scope` or
`not_applicable`.

### 7.3 Assessment contract

```python
class ApplicabilityAssessment:
    assessment_id: str
    decision_record_or_episode_id: str
    reconstruction_id: str | None
    decision_point_record_id: str
    as_of_time: datetime
    temporal_policy_id: str
    temporal_policy_checksum: str
    subject_entity_id: str
    assessment_dimension: Literal[
        "declared_scope",
        "potential_applicability",
        "confirmed_control",
    ]
    assessment_state: Literal[
        "explicitly_in_scope",
        "explicitly_out_of_scope",
        "potentially_applicable",
        "confirmed_controlled",
        "not_applicable",
        "insufficient",
    ]
    rule_profile_id: str
    rule_profile_checksum: str
    satisfied_condition_fact_ids: tuple[str, ...]
    failed_condition_fact_ids: tuple[str, ...]
    unknown_conditions: tuple[str, ...]
    source_ids: tuple[str, ...]
    source_snapshot_ids: tuple[str, ...]
    derivation_trace_id: str
```

Every assessment is a deterministic, versioned assertion. It never overwrites
the source-declared scope facts. The tuple
`(decision_record_or_episode_id, reconstruction_id,
decision_point_record_id, as_of_time, subject_entity_id,
assessment_dimension, rule_profile_checksum, temporal_policy_checksum)`
identifies at most one assessment result.

For a record subject, `reconstruction_id` is `None` and
`decision_point_record_id` equals that record ID. For an episode subject,
`reconstruction_id` and a member `decision_point_record_id` are mandatory.
The scope, interval, and rule inputs are frozen as of that member's decision
point; the engine cannot merge later episode updates into an earlier
assessment. An episode request without this anchor is `insufficient` before
tool or model construction.

### 7.4 Batch 3A — Source-declared scope

The first sub-batch publishes only source-declared scope under a dedicated
profile.

Candidate scope fields include:

- controlled airport;
- included or excluded departure ARTCCs;
- included or excluded departure airports;
- geographical or tier scope;
- flight inclusion or exclusion classes;
- operational interval.

The profile reuses ATMONTO concepts and predicates when supported:

```text
atm:AirportSpec
atm:FlightSpec
atm:departureScope
atm:flightInclusionSpec
atm:flightExclusionSpec
atm:includesAirport
atm:excludesAirport
atm:excludesARTCC
atm:includesFlight
atm:excludesFlight
```

The exact admitted IRIs must be verified against the tracked ontology source
before implementation. An unavailable predicate remains a profile gap rather
than being replaced by an unreviewed project synonym.

The existing ATMONTO predicate `nas:includesARTCC` is not admitted for this
mapping because its declared domain is `nas:ARTCCtier`, not
`atm:AirportSpec`. Applying it directly to an advisory scope would create a
domain-incompatible statement. Included ARTCC tokens remain source-bound scope
statements or profile gaps until a reviewed, ontology-compatible intermediate
pattern is approved.

For Ground Stop `2026-05-19:123`, the source-declared facility list contains:

```text
ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB
```

After canonical facility resolution, only entries whose entity type and
profile mapping validate may become formal included-scope facts. An entry with
unknown facility type or unsupported scope vocabulary remains an explicit
profile gap or unknown condition.

The exact source list remains retrievable with evidence even when some entries
cannot become formal scope facts. In Ground Stop `123`, only mappings supported
by admitted airport or other compatible predicates enter the formal graph;
ARTCC tokens are not forced into an invalid relation.

The GDP `DEP SCOPE: 1000` token must not be interpreted as a geographic
distance, tier, or rule until an FAA authority definition for that exact field
is admitted. It remains source text, profile gap, or unknown scope semantics.

### 7.5 Batch 3B — Potential flight applicability

Potential applicability requires:

- an admitted flight or schedule source;
- stable canonical flight identity;
- verified origin and destination;
- a reviewed TMI-family-specific applicability rule;
- a reviewed authority definition for the relevant time basis;
- canonical airport-to-ARTCC or scope membership where the rule requires it;
- a compatible operational interval.

A positive assessment is allowed only when every mandatory condition is
verified. The rule profile must state whether the time test uses scheduled
departure, controlled departure, estimated arrival, or another authority
field. The implementation must not choose a convenient timestamp because it
produces a positive match.

Until that authority rule is frozen, the possible Ground Stop `123` example
flight `YX5713` from DCA to JFK remains a test candidate, not an accepted
`potentially_applicable` assertion.

A candidate such as a PHX-to-JFK flight may support a negative test only after
the origin's canonical ARTCC and the advisory's included/excluded scope
semantics are verified.

The graph represents the assessment node and its supporting condition facts.
It must not add a direct:

```text
Flight affectedBy GroundStop
```

edge.

### 7.6 Batch 3C — Confirmed control and observed outcome

`confirmed_controlled` requires an admitted authoritative FAA source such as a
flight-level TMI list, TFMS/ASPM EDCT record, or equivalent official control
record whose field definition explicitly supports the claim. The evidence
must link the canonical flight to the exact selected advisory, program, or a
uniquely resolved official program identifier. A generic EDCT or delay record
without that decision binding is insufficient.

BTS can report:

- scheduled operation;
- completion;
- delay;
- cancellation;
- diversion;
- carrier-reported delay attribution.

BTS cannot prove that a flight was subject to a Ground Stop, GDP, EDCT, or
other TMI.

ADS-B or another trajectory source may report a flown path, holding pattern,
or diversion. It still cannot prove the administrative control decision unless
an authoritative source links that operation to the TMI.

Observed outcome records use a separate contract:

```python
class ObservedFlightOutcome:
    outcome_id: str
    canonical_flight_id: str
    source_family: str
    phenomenon_start: datetime
    phenomenon_end: datetime
    observation_fact_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    causal_claim: Literal[False]
```

An outcome is not given a formal decision edge from facility/time overlap.
When a user asks for outcomes in the context of a TMI, a separate audit-only
association is required:

```python
class OutcomeContextAssociation:
    association_id: str
    decision_id: str
    outcome_id: str
    temporal_relation: str
    facility_match_fact_ids: tuple[str, ...]
    selection_method_id: str
    source_ids: tuple[str, ...]
    causal_claim: Literal[False]
```

The association supports retrieval context only. It is neither
`confirmed_controlled` nor a causal outcome relation.

The corpus artifacts are:

```text
applicability_assessments.jsonl
applicability_derivations.jsonl
observed_flight_outcomes.jsonl
outcome_context_associations.jsonl
```

All four paths, row counts, checksums, profile references, and component
statuses are recorded in `corpus_manifest.json`. A query with `decision_id`
reads only a persisted, validated `OutcomeContextAssociation`; it does not
recreate one from facility and time proximity at read time.

The formal scope facts and admitted assessment nodes also appear in the corpus
formal graph. Rejected, insufficient, and incomplete rule attempts remain in
the audit artifacts only.

### 7.7 Query surface

Add:

```python
get_applicable_entities(
    decision_id: str,
    reconstruction_id: str | None = None,
    decision_point_record_id: str | None = None,
    entity_kind: Literal["facility", "flight", "all"] = "all",
    states: tuple[str, ...] | None = None,
) -> ApplicabilityRead

get_observed_flight_outcome(
    canonical_flight_id: str,
    decision_id: str | None = None,
) -> ObservedFlightOutcomeRead
```

The answer separates:

1. Explicit source scope;
2. Potential applicability;
3. Confirmed control;
4. Observed operational outcome;
5. Unknown conditions;
6. Evidence and limitations.

The generic word `affected` is avoided unless the answer immediately qualifies
which of these states it means.

### 7.8 Batch 3 acceptance

Batch 3A succeeds when Ground Stop `123` exposes the canonical included
departure scope list with exact evidence, publishes only
ontology-compatible formal relations, retains unsupported ARTCC mappings
outside the graph, and leaves `DEP SCOPE: 1000` uninterpreted.

Batch 3B succeeds when:

- the reviewed rule produces reproducible assessments;
- scope, potential-applicability, and confirmed-control assessments can coexist
  without overwriting one another;
- `potentially_applicable` remains a rule-based eligibility result even when a
  separate confirmed-control assessment exists;
- every assessment binds an as-of time, temporal-policy checksum, and exact
  source-snapshot set;
- an episode-level request without a valid reconstruction member decision
  point returns `insufficient` with zero provider calls;
- one failed mandatory condition yields `not_applicable`;
- one unknown mandatory condition yields `insufficient`;
- absence from an inclusion list remains unknown unless the frozen profile
  proves exhaustive closed-world coverage;
- incomplete scope coverage cannot yield `explicitly_out_of_scope` or
  `not_applicable`;
- a positive result requires every mandatory condition;
- no direct affected-flight edge is emitted.

Batch 3C succeeds only when authoritative control evidence can distinguish
`confirmed_controlled` from an observed BTS or trajectory outcome.

It also requires:

- the control evidence to identify the exact advisory or uniquely resolved
  official program;
- a generic EDCT or delay record without that binding to remain
  `insufficient`;
- two operations with the same flight number but different operation dates do
  not collapse to one canonical flight;
- an EDCT attached to the same flight but a different official program does
  not prove control by the queried decision;
- an outcome-context association to retain its interval, facility support, and
  `causal_claim=false`;
- no outcome-context association to enter the formal graph as a control or
  causal edge.

The batch fails if BTS is used as proof of TMI control, an unknown scope field
is guessed, canonical flight identities are joined on an incomplete natural
key, or an operational outcome is described as caused by the TMI.

## 8. Batch 4 — Historical Case Retrieval

### 8.1 User question

The capability answers two different questions:

1. Which published decision records are similar?
2. Which decision-time operational situations are similar?

These retrieval modes must not be combined because they use different feature
sets and answer different user needs.

### 8.2 Similar Decision Records

Record-level retrieval may compare:

- normalized TMI family;
- canonical controlled facility or reviewed facility class;
- source-declared reason and detailed reason category;
- operational-period duration;
- source-declared scope;
- lifecycle action and episode position;
- selected TMI parameters whose definitions are admitted.

This mode is useful for finding records with similar published structure. It
does not answer whether the underlying operational situation was similar.

### 8.3 Similar Decision-Time Situations

Decision-time situation retrieval may compare only evidence available at or
before the selected issue time:

- canonical airport and reviewed airport characteristics;
- Weather conditions and forecast categories;
- admitted ASPM demand and AAR;
- runway configuration;
- derived demand-capacity difference;
- other future source fields explicitly admitted by the feature profile.

It must exclude:

- the selected TMI family or action as a feature;
- the ATCSCC source-declared reason, detailed reason, and any reason profile
  gap;
- source-declared scope or parameters chosen as part of that TMI;
- post-decision Weather observations;
- BTS active or recovery outcomes;
- cancellations, diversions, and delay outcomes;
- later episode updates;
- any field unavailable at the query decision time.

Excluding the selected decision and outcome prevents target and hindsight
leakage when retrieval is later used as decision reference.

Without ASPM or another admitted demand-capacity source, this mode must be
labeled `Weather-context similarity`, not complete operational-situation
similarity.

### 8.4 Case feature contract

```python
class FeatureValue:
    feature_name: str
    shape: Literal[
        "numeric",
        "boolean",
        "nominal",
        "ontology_concept",
        "categorical_set",
        "numeric_interval",
        "duration",
    ]
    canonical_value: object
    datatype_or_concept_iri: str | None
    evidence_kind: Literal[
        "formal_fact",
        "validated_profile_gap",
        "deterministic_derivation",
    ]
    evidence_ids: tuple[str, ...]
    authoritative_available_time: datetime
    exhaustive: bool | None


class CaseFeatureSet:
    case_id: str
    retrieval_mode: Literal[
        "decision_record",
        "decision_time_situation",
    ]
    feature_profile_id: str
    feature_profile_checksum: str
    as_of_time: datetime
    feature_values: dict[str, FeatureValue]
    feature_fact_ids: dict[str, tuple[str, ...]]
    missing_feature_mask: tuple[str, ...]
    source_ids: tuple[str, ...]
    temporal_cutoff: datetime
    latest_feature_available_time: datetime


class FeatureProfileProvenance:
    parameter_origin: Literal[
        "domain_definition",
        "expert_frozen",
        "pre_registered_calibration",
    ]
    source_definition_refs: tuple[str, ...]
    calibration_manifest_id: str | None
    calibration_manifest_checksum: str | None
    calibration_cutoff: datetime | None
    calibration_feature_ids: tuple[str, ...]
    frozen_at: datetime
    uses_selected_tmi_or_outcome_labels: Literal[False]
```

Formal facts are the default feature authority. A validated profile gap may
participate only when the versioned feature profile explicitly admits that
evidence kind; it remains labeled as a profile-gap feature and never becomes a
graph fact. Raw source text, model output, and unvalidated audit associations
are not feature authorities. A genuine numeric zero is a value; `null`,
unknown, and an absent feature are missing.

The versioned feature profile freezes:

- feature definitions and semantic source;
- datatype and unit;
- categorical hierarchy;
- normalization range for numeric features;
- per-feature weight;
- mandatory feature groups;
- minimum coverage;
- temporal cutoff policy;
- candidate eligibility rules;
- tie-breaking order.

It also embeds `FeatureProfileProvenance`. The Query Agent cannot modify these
settings.

The initial v0 profile uses only `domain_definition` or `expert_frozen`
parameters documented before the acceptance cases are ranked. It is not tuned
against the selected TMI, lifecycle result, BTS outcome, later cancellation,
or any target label.

A later data-calibrated profile must pin the immutable calibration corpus,
checksum, latest source-availability cutoff, and exact non-target feature IDs.
For a `historically_available` query, its calibration cutoff must be at or
before the query temporal cutoff. Post-cutoff cases or outcomes cannot affect
its weights, ranges, hierarchy credit, coverage threshold, or tie-breaking.
Changing post-cutoff archive content must leave both the selected profile
checksum and historically available ranking unchanged.

### 8.5 Similarity calculation

The initial method is deterministic weighted Gower similarity for mixed
feature types:

```text
similarity =
  sum(weight_i * comparable_similarity_i)
  / sum(weight_i for comparable features)

coverage =
  sum(weight_i for comparable features)
  / sum(weight_i for all profile features)
```

Numeric similarity uses the profile's reviewed normalization range. Boolean and
nominal features use exact equality. Controlled ontology concepts use only
profile-declared equivalence or parent-category credit. The profile must define
the parent-category score; the runtime cannot infer one from lexical
similarity.

The initial per-shape rules are:

- `numeric`, `numeric_interval`, and `duration` use the profile's reviewed
  range and clamp the distance contribution to `[0, 1]`;
- `duration` is converted to the profile's canonical unit before numeric
  comparison;
- `numeric_interval` requires both bounds and uses the mean of the normalized
  lower-bound and upper-bound similarities; a one-sided interval is missing;
- `boolean` and scalar `nominal` values use exact equality;
- `ontology_concept` values use exact identity or a profile-approved
  parent-category score only;
- `categorical_set` uses a profile-declared comparator, initially Jaccard over
  canonical concept IDs;
- two empty sets score `1` only when both source fields are authoritatively
  exhaustive; otherwise the feature is missing;
- multi-valued action-role and scope sets receive one feature weight each, not
  one weight per set member.

A numeric normalization range with `maximum <= minimum` blocks the feature
profile; the runtime cannot repair it.

Missing values are excluded from the similarity numerator and denominator.
They are never converted to zero. A result below the minimum coverage, or
missing a mandatory feature group, returns `insufficient`. If no feature is
comparable, the denominator is zero and the result is `insufficient`, never
`0` or `1`.

Every result contains:

- overall similarity score;
- coverage score;
- per-feature contribution;
- matched features;
- differing features;
- missing features;
- supporting evidence IDs, evidence kinds, and sources.

No embedding, LLM similarity judgment, generated feature, or free-text
semantic guess is used in the initial method.

### 8.6 Temporal eligibility

The default historical policy requires both:

```text
candidate eligibility end < query case issue time
latest authoritative feature availability <= query temporal cutoff
```

The first condition ensures that the candidate case itself had completed. The
second ensures that every feature version contributing to the comparison
actually existed under the source-specific availability policy by the query
cutoff.

`candidate eligibility end` is the accepted episode end for an episode case
and the operational end for a record case. A candidate with an unresolved end
is ineligible in the default historical mode.

For every candidate feature, the exact source version must have existed by the
cutoff. A feature with unknown authoritative availability is omitted and
masked; if that omission violates a mandatory group or minimum coverage, the
candidate is `insufficient`. A case whose operation ended before the query
issue time but whose lifecycle or feature evidence became available only later
is not historically eligible with that later evidence.

An explicitly requested retrospective archive mode may include later cases,
but the result must be labeled `full historical archive` and must not be
presented as evidence available at the original decision time.

The query case itself and reconstructions sharing the same conceptual case are
excluded.

### 8.7 Sub-batches

Batch 4A implements decision-record retrieval over an identity-reviewed corpus.

Batch 4B implements decision-time-situation retrieval after the required
source groups are admitted. Before ASPM, it exposes only the narrower
Weather-context mode.

The minimum development corpus contains:

- at least six identity-reviewed JFK, EWR, or LGA decision episodes;
- both GDP and Ground Stop families;
- one query case;
- at least five temporally eligible candidates under the selected mode.

This corpus is a system acceptance fixture. It is not a Gold benchmark and
does not establish retrieval effectiveness for the full ATCSCC archive.

### 8.8 Artifacts

```text
case_catalog.jsonl
case_feature_sets.jsonl
case_feature_profile.json
similarity_assessments.jsonl
case_index_manifest.json
```

The catalog contains only validated record or episode identities. Every entry
has a `conceptual_case_id`: an episode member uses its
`case:DecisionEpisode` ID, while an independently published record outside an
accepted episode uses its canonical record ID. Feature sets and assessments
bind to the catalog checksum and exact source/profile inputs.

Similarity remains a query assessment. No permanent `similarTo` graph edge is
created in this batch.

### 8.9 Query surface

Add:

```python
find_similar_cases(
    case_id: str,
    retrieval_mode: Literal[
        "decision_record",
        "decision_time_situation",
    ],
    limit: int = 5,
    archive_mode: Literal[
        "historically_available",
        "full_historical_archive",
    ] = "historically_available",
) -> SimilarCaseRead

compare_cases(
    left_case_id: str,
    right_case_id: str,
    retrieval_mode: str,
    as_of_time: datetime | None = None,
    archive_mode: Literal[
        "historically_available",
        "full_historical_archive",
    ] = "historically_available",
) -> CaseComparisonRead
```

For `historically_available`, `as_of_time` defaults deterministically to the
left case's issue time. The router binds both temporal arguments before any
model-visible step. `full_historical_archive` is available only when the user
explicitly requests a retrospective archive comparison.

The answer reports:

1. Retrieval mode and temporal policy;
2. Ranked cases;
3. Similar and different verified features;
4. Coverage and missing features;
5. Source and feature-profile provenance;
6. Scope limitation.

It must not say that a historical TMI is recommended, correct, optimal, or
causally effective.

### 8.10 Batch 4 acceptance

Batch 4A succeeds when:

- record-level rankings are deterministic;
- the same conceptual case is excluded;
- later records are excluded by default;
- each score can be recomputed from its feature contributions;
- missing values do not become zeros;
- a genuine zero remains comparable and is not masked as missing;
- two empty non-exhaustive sets remain missing rather than scoring equal;
- a zero comparable-feature denominator returns `insufficient`;
- low-coverage candidates return `insufficient`;
- the feature profile exposes parameter origin and any calibration
  corpus/checksum/cutoff;
- modifying post-cutoff cases or outcome fields cannot change a historically
  available profile or ranking.

Batch 4B succeeds only when decision-time features satisfy the temporal cutoff
and exclude selected TMI, declared reason or reason profile gap,
source-declared TMI scope/parameters, and outcome fields. Changing only a
source-declared reason or TMI scope value cannot change
decision-time-situation similarity.

A candidate whose operation ends before the query but whose required feature
version is published afterward is excluded or marked `insufficient` in
historically available mode.

The batch fails if record and situation similarity are conflated, later
evidence leaks into the historical view, the Query Agent changes weights, or
the answer presents frequency or similarity as a recommendation.

## 9. Query Agent Adaptation

### 9.1 Bounded planning contract

The new intents are additive. They do not replace the existing deterministic
intents for measure, facility, operational period, declared reason,
provenance, combined record, forecast known at decision time, observed Weather
context, public operational observations, or reconstructed decision case.

The deterministic router first freezes every semantic argument into bound
steps:

```python
ExistingQueryIntent = Literal[
    "measure",
    "facility",
    "operational_period",
    "declared_reason",
    "provenance",
    "combined_record",
    "forecast_known_at_decision_time",
    "observed_weather_context",
    "public_operational_observations",
    "reconstructed_decision_case",
]

class BoundStepBase:
    step_id: str
    gateway_tool_name: Literal["execute_bound_query_step"]
    arguments_checksum: str
    required: bool
    expected_evidence_groups: tuple[str, ...]
    maximum_results: int


class ExistingGraphReadStep(BoundStepBase):
    operation: Literal["existing_graph_read"]
    arguments: ExistingGraphReadArguments
    result_contract: Literal["ExistingGraphReadObservation"]


class DecisionEpisodeStep(BoundStepBase):
    operation: Literal["decision_episode"]
    arguments: DecisionEpisodeQueryArguments
    result_contract: Literal["DecisionEpisodeRead"]


class OperationalSituationStep(BoundStepBase):
    operation: Literal["operational_situation"]
    arguments: OperationalSituationQueryArguments
    result_contract: Literal["OperationalSituationRead"]


class ApplicabilityStep(BoundStepBase):
    operation: Literal["applicability"]
    arguments: ApplicabilityQueryArguments
    result_contract: Literal["ApplicabilityRead"]


class ObservedOutcomeStep(BoundStepBase):
    operation: Literal["observed_flight_outcome"]
    arguments: ObservedOutcomeQueryArguments
    result_contract: Literal["ObservedFlightOutcomeRead"]


class SimilarCasesStep(BoundStepBase):
    operation: Literal["similar_cases"]
    arguments: SimilarCaseQueryArguments
    result_contract: Literal["SimilarCaseRead"]


class CaseComparisonStep(BoundStepBase):
    operation: Literal["case_comparison"]
    arguments: CaseComparisonQueryArguments
    result_contract: Literal["CaseComparisonRead"]


BoundQueryStep = (
    ExistingGraphReadStep
    | DecisionEpisodeStep
    | OperationalSituationStep
    | ApplicabilityStep
    | ObservedOutcomeStep
    | SimilarCasesStep
    | CaseComparisonStep
)


class QueryScopeRef:
    scope_kind: Literal["record_run", "corpus"]
    manifest_id: str
    manifest_checksum: str


class QueryTerminalResult:
    status: Literal["ok", "insufficient", "blocked", "unsupported"]
    component_statuses: tuple[ComponentLayerStatus, ...]
    executed_step_ids: tuple[str, ...]
    unexecuted_required_step_ids: tuple[str, ...]
    retrieved_fact_ids: tuple[str, ...]
    retrieved_profile_gap_ids: tuple[str, ...]
    retrieved_assessment_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    answer_contract_id: str
```

The Query Agent receives a validated graph/corpus scope and an immutable
`QueryPlan`:

```python
class QueryPlan:
    intent: ExistingQueryIntent | Literal[
        "decision_episode",
        "operational_situation",
        "applicability",
        "observed_flight_outcome",
        "similar_cases",
        "case_comparison",
    ]
    scope: QueryScopeRef
    subject_ids: tuple[str, ...]
    bound_steps: tuple[BoundQueryStep, ...]
    required_evidence_groups: tuple[str, ...]
    optional_evidence_groups: tuple[str, ...]
    maximum_tool_calls: int
    deterministic_terminal_result: QueryTerminalResult | None
```

The deterministic router:

1. resolves registered record, episode, facility, flight, or case identifiers;
2. pins the exact run or corpus manifest and checksum;
3. binds semantic arguments such as view, decision-point record, assessment
   states, retrieval mode, archive mode, result limit, and pairwise case IDs;
4. checks that the requested capability and artifacts exist;
5. creates only the minimum bound steps required by the selected intent;
6. validates the discriminated operation/argument/result combination,
   arguments checksum, and call budget before a model can be constructed;
7. returns `unsupported`, `insufficient`, or `blocked` before model
   construction when appropriate.

For example, an operational-situation step binds `view`,
`decision_point_record_id`, and temporal-policy checksum. A similarity step
binds `retrieval_mode`, `archive_mode`, `as_of_time`, and `limit`. A pairwise
step binds both case IDs. The model receives step IDs and human-readable
descriptions, never mutable semantic arguments.

`arguments_checksum` covers the operation discriminator, canonical typed
arguments, result contract, and the selected scope-manifest checksum.

The model-visible registry exposes only:

```python
execute_bound_query_step(step_id: str) -> TypedQueryObservation
```

The model may select or order allowed step IDs, but it cannot change their
arguments, scope manifest, profile, temporal view, archive mode, or result
limit. `full_historical_archive` can be bound only when the deterministic
router recognizes an explicit user request for that retrospective mode.

The plan validator requires:

```text
required_step_count <= maximum_tool_calls
```

Required-call capacity is reserved before any optional step can execute. The
Agent may order required steps, but optional steps are exposed only after all
required steps have succeeded and unused capacity remains. Before synthesis,
every required step must have executed successfully. A plan that violates the
budget, operation/argument discriminator, required ordering, or result
contract terminates before model construction or synthesis with a typed
`blocked` result and no generation fallback.

This preserves the parent Section 12.3 rule that high-level context tools are
router-only. Existing low-level graph functions and the new high-level
semantic functions remain internal operations behind the bound-step gateway;
they are not added as model-editable tools.

For a supported free-form formulation, the existing Query Agent may choose
among the bound steps and compose an evidence-bound explanation. It cannot
access raw files, arbitrary Cypher or SPARQL, the web, graph writes,
unregistered feature profiles, or unrestricted tool discovery.

### 9.2 Tool mapping

The table names internal router operations, not model-visible tool names:

| Question class | Bound internal operation |
| --- | --- |
| Existing record facts and provenance | Existing bounded graph read |
| Decision evolution | `get_decision_episode` |
| Operational situation | `get_operational_situation` |
| Facility or flight scope | `get_applicable_entities` |
| Observed flight outcome | `get_observed_flight_outcome` |
| Similar historical cases | `find_similar_cases` |
| Pairwise explanation | `compare_cases` |

Each operation may perform multiple deterministic artifact reads internally,
but it returns one typed observation through
`execute_bound_query_step(step_id)`. The default maximum remains three bound
step calls for one user question.

### 9.3 Model-call boundary

The semantic builders, linkers, rule engine, and similarity engine add zero
provider calls.

Registered deterministic questions may be answered with zero provider calls.
When the existing Query Agent is used for supported natural-language
composition, its current bounded model-tool-model budget remains unchanged.

Unsupported questions, missing identifiers, absent required evidence, blocked
layers, and missing declared reasons make zero provider calls. No model
knowledge or raw-text fallback is permitted.

### 9.4 Answer status

Every answer returns one of:

```text
ok
insufficient
blocked
unsupported
```

The answer also reports the status of each requested semantic layer. A partial
answer may contain verified information from an `ok` layer while explicitly
marking another layer `insufficient`; it cannot silently omit a blocked layer.
The composite status follows the deterministic roll-up in Section 4.6.

## 10. Publication, Provenance, And Identity

### 10.1 Publication rule

Only canonical `ValidatedFact` instances may enter the formal
JSONL/RDF/Neo4j graph. Source-derived facts and accepted deterministic
proposals therefore share the same final publication type and Formal Graph
Kernel gate.

Audit-only associations, rejected links, ambiguous candidates, raw similarity
features, and incomplete rule attempts remain outside formal graph
materialization.

Every published fact records these common fields:

- stable fact ID;
- subject and object identity;
- owning profile ID and checksum;
- evidence mode;
- predicate IRI and canonical object or literal;
- the evidence reference required for its evidence mode.

Mode-specific provenance is not fabricated. The required and forbidden
bindings are:

| Evidence mode | Required bindings | Forbidden or omitted bindings |
| --- | --- | --- |
| `source_text` | exact `FactTrace`, canonical source ID, source snapshot checksum, evidence span | procedure or derivation claims not present in the source trace |
| `deterministic_derivation` | derivation trace, supporting fact IDs, reachable source bindings, procedure ID and checksum | claim that the derived value is exact source wording |
| `profile_definition` | profile ID and checksum, defined term or constraint reference | source span, source checksum, or derivation trace when none applies |
| `system_membership` | membership trace, member record IDs, accepted membership/link assessment IDs, profile and procedure checksums | exact source wording or a source-explicit revision claim |
| `rule_assessment` | rule-profile ID and checksum, supporting fact IDs, satisfied, failed, and unknown conditions, derivation trace with reachable source bindings | exact source wording or an untraced model judgment |

Fields that do not apply are absent or typed `None` according to the contract;
they are never filled with dummy IDs.

### 10.2 Evidence modes

The existing evidence modes are extended with explicitly named deterministic
assessment modes:

```text
source_text
deterministic_derivation
profile_definition
system_membership
rule_assessment
```

`system_membership` supports reconstruction membership and binds to the
accepted membership trace. `rule_assessment` supports applicability or other
reviewed deterministic assertions and binds to the exact satisfied, failed,
and unknown conditions.

Neither mode may be presented as exact source wording. Both begin as
`DerivedAssertionProposal` instances and become graph facts only after Formal
Graph Kernel validation.

### 10.3 Canonical identity

All corpus-level joins use canonical IDs from validated record runs.

The corpus workflow fails closed when:

- two run artifacts assign different canonical IDs to the same pinned source
  record;
- one canonical ID is used for incompatible entity types;
- record or source snapshot checksums differ from the corpus manifest;
- a flight natural key is incomplete or non-unique;
- an airport, ARTCC, or Weather station mapping lacks admitted authority
  evidence.

Repeated assembly reuses KJFK, KEWR, KBNA, facility, Weather report, record,
observation, episode, situation, and assessment identities.

### 10.4 RDF and Neo4j parity

For every formal layer, RDF and Neo4j must retain:

- identical subject, object, and assertion IDs;
- original predicate IRIs;
- explicit semantic classes rather than fallback labels;
- source and profile provenance;
- stable idempotent merge keys.

A corpus-level materializer may append accepted assertions to the existing
record graphs. It must not rewrite or renumber record-run fact IDs.

## 11. Source Admission Roadmap

Source families are admitted because a required semantic question needs them,
not because they are available.

| Source | Question supported | Admission status |
| --- | --- | --- |
| ATCSCC advisories | Decision record, lifecycle signal, declared scope | Existing |
| NASR and authority facility records | Canonical airport, ARTCC, station, and scope identity | Existing |
| FAA terminology and ATMONTO | TMI family, schema, and profile vocabulary | Existing |
| METAR and TAF | Decision-time and operational Weather context | Existing |
| BTS On-Time aggregate observations | Source-qualified airport operational observations | Existing, never proof of control |
| BTS On-Time flight-level rows | Source-qualified observed flight outcome | Batch 3C, requires a flight-identity and outcome profile; never proof of control |
| ASPM | Demand, AAR, runway configuration, EDCT, actual operational state | Batch 2B/3C, requires admission |
| Flight schedule or plan source | Potential flight applicability | Batch 3B, requires admission |
| Authoritative TMI flight/control source | Confirmed controlled flights | Batch 3C, requires admission |
| TCF, CWA, SIGMET | Regional Weather situation | Deferred source increment |
| NOTAM | Runway, equipment, or airspace constraint | Deferred source increment |
| ADS-B | Observed trajectory outcome | Deferred source increment |

Each new source requires:

1. official definition and usage boundary;
2. immutable snapshot and checksum;
3. canonical identity rules;
4. explicit temporal roles;
5. independent validation profile;
6. deterministic adapter and failure behavior;
7. query wording that preserves the source's actual semantics.

## 12. Cross-Batch Acceptance Invariants

The following invariants apply to every batch:

- the five Agent roles remain unchanged;
- record ingest remains independently runnable;
- corpus assembly reads validated artifacts only;
- no semantic builder adds a provider call;
- exact source facts remain distinguishable from derived proposals and
  validated rule or membership facts;
- a derived proposal cannot reach JSONL, RDF, or Neo4j without Formal Graph
  Kernel acceptance;
- profile gaps never become formal facts;
- audit-only associations never become causal or ontology facts;
- optional-layer failure does not erase valid record facts;
- every temporal view declares its cutoff;
- every decision-time member proves exact-version availability under its
  source policy;
- every cross-source join uses canonical identity and source checksums;
- missing values never become zeros;
- absence from an inclusion list remains unknown without explicit
  source/profile closed-world semantics;
- every deterministic result is reproducible from a pinned profile and trace;
- every composite answer exposes deterministic component-status roll-up;
- episode conceptual identity remains distinct from one reconstruction;
- model-visible query steps cannot change pinned scope, view, profile,
  temporal policy, archive mode, or result limit;
- unsupported and absent-evidence questions make zero provider calls;
- all code, contracts, prompts, artifacts, tests, CLI messages, and active
  documentation remain English.

The existing three-case reason invariants remain mandatory after every batch:

| Record | Required reason state |
| --- | --- |
| Ground Stop `2026-05-19:123` | Source-bound profile gap; no formal `atm:impactingCondition` |
| GDP `2026-05-19:138` | Formal normalized `weather` with exact source evidence ending at `THUNDERSTORMS` |
| GDP cancellation `2026-05-20:020` | Missing reason; reason query returns `insufficient` with zero provider calls |

Cross-batch negative tests also require:

- partial episode candidate coverage cannot yield an accepted link;
- a post-cutoff report version cannot enter a decision-time situation;
- `0`, `null`, and absent fields remain distinct through aggregation and
  similarity;
- an empty or all-missing similarity denominator returns `insufficient`;
- a post-cutoff case or outcome cannot tune a historically available feature
  profile;
- changing only an ATCSCC declared reason or reason profile gap cannot change
  decision-time-situation similarity;
- a model cannot switch a historically available query to
  `full_historical_archive`;
- an operation cannot be paired with another operation's argument schema, and
  required query steps always fit within reserved tool-call capacity;
- an episode-level applicability request without a member decision point is
  rejected before provider construction;
- the same flight number on different operation dates remains two flight
  identities;
- a control record for a different official program cannot confirm control by
  the queried TMI.

## 13. Sequential Gates

The four user capabilities are reviewed and implemented in user-facing order:

```text
Batch 1 -> Batch 2 -> Batch 3 -> Batch 4
```

This review order is not a claim that every later sub-batch has every earlier
sub-batch as a hard data dependency. The hard inputs are:

| Sub-batch | Hard inputs |
| --- | --- |
| Batch 1 episode reconstruction | Validated ATCSCC records plus checksum-pinned, complete candidate coverage |
| Batch 2A existing operational situation | Validated record or episode identity, admitted Weather evidence, and BTS aggregate observations |
| Batch 2B demand-capacity situation | Batch 2 temporal contract plus independently admitted ASPM data |
| Batch 3A source-declared scope | Validated ATCSCC record and admitted facility/scope authority; Batch 2A is not required |
| Batch 3B potential flight applicability | Batch 3A scope semantics, admitted flight schedule or plan data, canonical flight identity, and reviewed time authority |
| Batch 3C-control confirmed control | Admitted authoritative control source with exact program binding; ASPM is sufficient only when its admitted fields actually prove that binding |
| Batch 3C-outcome observed outcome | Admitted BTS flight-level or trajectory source plus canonical flight identity; it is independent of confirmed control |
| Batch 4A decision-record retrieval | Identity-reviewed record/episode catalog and record feature profile; Batch 2 and Batch 3 are optional enrichment |
| Batch 4B Weather-context similarity | Batch 2A decision-time Weather evidence |
| Batch 4B complete operational-situation similarity | Batch 2B demand-capacity admission plus every mandatory source group in the feature profile |

The two Batch 3C capabilities remain separately gated even if implemented in
one code package: `confirmed_control` and `observed_outcome` do not certify one
another.

A later sub-batch may proceed while an unrelated source-dependent earlier
sub-batch is insufficient, but it may not claim unavailable semantics. For
example:

- Batch 4A can retrieve similar published records before ASPM;
- a Weather-only Batch 4B must be labeled Weather-context similarity;
- Batch 3A can expose scope before flight-level time semantics are admitted;
- Batch 3C-control cannot claim confirmed control merely because BTS outcomes
  exist;
- Batch 3C-outcome may expose an observed outcome without claiming
  applicability or control.

Each batch requires its own implementation plan, focused tests, self-review,
and reviewable commit. Approval of this architecture does not authorize all
batches to be implemented in one change.

## 14. Explicit Non-Goals

This design does not provide:

- automatic selection of GDP, Ground Stop, reroute, or another TMI;
- proof that a historical decision was correct or effective;
- causal attribution from Weather, demand, delay, or cancellation;
- live FAA operational decision support;
- a complete aviation ontology;
- unrestricted natural-language graph querying;
- learned or LLM-generated similarity;
- a graph-writing Query Agent;
- a planner that changes feature weights or rule semantics;
- automatic full-corpus model execution;
- a new Agent role without an observed and separately approved need.

## 15. Design Review Gate

Before an implementation plan is written, reviewers must confirm:

1. the four question classes remain semantically distinct;
2. the episode model does not fabricate source-explicit revision links;
3. decision-time and retrospective evidence cannot mix;
4. `potentially_applicable`, `confirmed_controlled`, and
   `observed_operational_outcome` remain separate;
5. record similarity and decision-time-situation similarity remain separate;
6. all new source requirements have an admission gate;
7. the existing three-case reason semantics and zero-call failures are
   preserved;
8. no new Agent role is implied by an adapter, builder, linker, or rule engine;
9. every derived graph fact still passes through the Formal Graph Kernel;
10. conceptual episode identity is distinct from reconstruction identity;
11. every decision-time feature proves exact-version availability;
12. bound query steps prevent the model from altering scope, time, or archive
    mode.

Only after this design is reviewed and accepted should the first batch receive
a file-level implementation plan.
