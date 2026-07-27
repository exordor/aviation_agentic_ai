# Three-Agent Decision Case Architecture Design

Status: approved design; Batch A contracts and authority evidence implemented

Date: 2026-07-27

Branch: `codex/decision-case-semantic-expansion-design`

Normative parent design:
`docs/multi_agent_kg_system_design.md`

Related designs:

- `docs/superpowers/specs/2026-07-27-decision-case-graph-v1-design.md`
- `docs/superpowers/specs/2026-07-27-decision-case-semantic-expansion-design.md`

## 1. Purpose

The current system exposes five named roles:

1. Advisory Agent;
2. Facility Agent;
3. Terminology Agent;
4. Knowledge Graph Construction Agent;
5. Query Agent.

Those names overstate the autonomy of the first three roles. Advisory
interpretation is currently deterministic. Facility and terminology
resolution are also deterministic for zero or one eligible candidate and use
at most a closed-list model selection for ambiguous candidates. The Knowledge
Graph Construction Agent has the clearest tool-observation loop. The Query
Agent is hybrid: simple registered questions use deterministic fast paths,
while only bounded compound questions use a model-mediated tool path.

The approved architecture replaces the five-role description with three
conditionally activated Agents whose boundaries correspond to genuine
decisions:

1. Semantic Resolution Agent;
2. Decision Case Assembly Agent;
3. Decision Case Analysis Agent.

Source acquisition, parsing, candidate generation, unique resolution, temporal
alignment, aggregation, rule evaluation, validation, and graph writing remain
deterministic tools or services. The system does not create one Agent per data
source and does not introduce a general Coordinator Agent.

This is an architecture correction, not an Agent-count experiment. The goal
is to make the term `Agent` operationally honest:

> An Agent observes typed state, chooses among bounded actions or tools,
> receives typed feedback, updates working state, and explicitly continues,
> abstains, blocks, or stops.

## 2. Stage Header

| Item | Decision |
| --- | --- |
| User-facing or system capability | Resolve genuine cross-source ambiguity, assemble provenance-bound decision cases, and answer bounded multi-step case questions through three explicit Agent loops. |
| Smallest end-to-end result | Resolve one ambiguous mention, assemble one validated multi-source decision case, and answer one compound case question with a primary and evidence-driven follow-up tool. |
| Minimum components | Existing deterministic parsers and source adapters, authority candidate tools, three typed Agent contracts, Formal Graph Kernel, validated shared knowledge graph, and bounded read-only case-analysis tools. |
| Expected evidence | State transitions, selected tools, typed observations, authority and source bindings, validation feedback, termination reasons, model-call counts, and unchanged three-record semantic regressions. |
| Success condition | Each Agent has at least one evidence-dependent action trace; deterministic fast paths remain zero-model; no Agent invents a candidate, fact, cause, source, or graph write; and all published facts pass the Formal Graph Kernel. |
| Failure condition | The change only renames roles, terminology decisions still receive placeholder definitions, every record unnecessarily invokes every Agent, an Agent bypasses the Kernel, missing evidence is completed from model knowledge, or case similarity uses target decisions or outcomes as decision-time features. |
| Explicitly deferred | Coordinator, Critic, Verifier, Memory, Weather, BTS, ASPM, Lifecycle, or Similarity specialist Agents; free-form inter-Agent chat; long-term autonomous learning; causal explanation; TMI recommendation; unrestricted graph or web search; and Agent-count comparisons. |
| Classification | Critical Path for architecture honesty and system extensibility; prompt grounding, evidence binding, and representative traces are Evidence Quality gates. |

## 3. Relationship to Existing Designs

For future planning, this design supersedes the five-Agent target role
decomposition in Section 4.1 of
`2026-07-27-decision-case-semantic-expansion-design.md` and refines the
Decision Case Analysis activation protocol while retaining that design's
two-provider-call budget. It does not change the active runtime or current
reader-facing description by itself, and it does not supersede the accepted
semantic, evidence, scope-pinning, bound-step, or fail-closed boundaries in the
related documents.

For role structure only, this approval also supersedes that parent design's
Section 4.7 exclusion of a Cross-Source Resolution Agent and the Section 12
invariant that all batches retain five Agent roles. The replacement governs
Batch B and later implementation work after Batch A's contract gate passes.
Every other Section 12 invariant remains in force. Runtime and public naming
change only as the corresponding implementation gates pass, and the complete
three-Agent public claim still waits for all three reviewed-trace gates.

The normative parent design is amended incrementally by each implementation
batch. Until a new Agent's implementation gate and reviewed trace pass, active
documentation must describe the corresponding current component honestly.
The public three-Agent system claim is permitted only after all three gates in
Section 19 pass. Batch A therefore changes contracts and evidence inputs only;
it does not authorize a new runtime architecture claim.

The following behavior remains unchanged:

- one immutable source record remains the unit of record ingest;
- source-specific adapters preserve source family, source ID, record ID, and
  snapshot checksum;
- Ground Stop `2026-05-19:123` retains a source-bound reason profile gap;
- GDP `2026-05-19:138` retains the formal normalized reason `weather`;
- GDP cancellation `2026-05-20:020` retains a missing declared reason;
- Weather context remains time-bounded and non-causal;
- BTS observations retain their BTS reporting scope and are not FAA demand,
  AAR, capacity, EDCT, or proof of TMI effect;
- profile gaps remain audit records outside the formal graph;
- unsupported or absent questions fail before provider construction;
- the Formal Graph Kernel remains the only publication gate;
- RDF and Neo4j remain projections of accepted formal facts rather than
  independent semantic authorities.

The active runtime is not changed by this document. Each implementation batch
must amend the normative parent design, prompts, contracts, manifests, tests,
and reader-facing claims together.

## 4. Approved Architecture

```text
Heterogeneous source records
  -> deterministic source adapters and parsers
  -> immutable SourceSnapshotRegistry and EvidenceClaims
  -> deterministic candidate and support gates
       -> unique valid result: deterministic acceptance
       -> no valid resolution candidate: insufficient
       -> genuine ambiguity: Semantic Resolution Agent
  -> deterministic assembly-complexity gate
       -> fixed complete mapping: deterministic case compiler
       -> evidence or schema choice: Decision Case Assembly Agent
  -> deterministic preflight validation
       -> valid proposal: Formal Graph Kernel
       -> repairable feedback: one bounded Assembly revision
       -> hard violation: blocked
  -> validated Decision Case Knowledge Graph
  -> deterministic query support and scope gate
       -> simple scalar fact: deterministic query
       -> episode, situation, applicability, or similarity task:
          Decision Case Analysis Agent
  -> evidence-grounded answer, insufficient, or blocked
```

The orchestration is deterministic. It routes typed work according to
candidate counts, evidence availability, registered task support, and
validation status. It is not a fourth Agent.

A source-supported field that the active ontology profile cannot publish is
handled later as a profile gap. The resolution gate does not convert a missing
candidate into a profile gap.

The three Agents do not exchange free-form messages. They communicate through
immutable or append-only typed artifacts in shared workflow state.

## 5. Deterministic Components

The following remain tools or services:

- `AdvisoryParser`;
- ATCSCC, NASR, FAA terminology, Weather, BTS, ASPM, and flight-data adapters;
- source snapshot and checksum validation;
- candidate generation and exact matching;
- canonical ID construction;
- deterministic unique-candidate acceptance;
- timestamp parsing, interval overlap, and temporal eligibility;
- aggregation and quantity calculation;
- episode-link candidate generation;
- operational-situation feature calculation;
- applicability rules;
- similarity feature calculation and scoring;
- schema loading and constraint checks;
- Formal Graph Kernel;
- RDF and Neo4j materialization;
- manifest and audit-trace writing.

These components may be exposed as bounded Agent tools, but they do not become
Agents merely because an Agent can call them.

## 6. Semantic Resolution Agent

### 6.1 Goal

Resolve a mention to one registered canonical entity or concept only when
deterministic authority rules cannot produce a unique valid result.

The Agent may accept a supplied candidate, reject candidates, or abstain. It
must never invent a candidate, source, definition, ontology class, or
canonical ID.

### 6.2 State

```text
ResolutionTask
mention
structural_slot
expected_entity_type
candidate_ids
candidate_evidence
authority_source_ids
ontology_constraints
rejected_candidate_ids
remaining_tool_budget
decision
```

`structural_slot` and `expected_entity_type` are mandatory when the upstream
parser knows them. A known slot must not be replaced with `UNCLASSIFIED TEXT`
or another generic fallback.

### 6.3 Tools

```text
get_resolution_candidates
get_authority_record
get_ontology_context
check_candidate_constraints
compare_candidate_evidence
```

All tools are read-only, typed, candidate-bounded, and source-aware. They
return IDs and structured evidence rather than unbounded text.

### 6.4 Action Space

```text
inspect_candidate
compare_candidates
accept_candidate
reject_candidate
abstain
```

### 6.5 Policy and Budget

- zero candidates return `insufficient` without provider construction;
- one authority-valid and type-compatible candidate is accepted
  deterministically without provider construction;
- only multiple eligible candidates or conflicting constraints activate the
  Agent;
- one Agent action may request a batch of at most three read-only tool calls;
- the Agent receives the typed results and makes one final decision;
- the path therefore permits at most two provider calls;
- a selected ID must belong to the supplied eligible candidate set;
- insufficient distinguishing evidence must terminate as `abstained`.

### 6.6 Memory and Termination

Working memory is the current `ResolutionTask` state. Audit memory is the
immutable tool and decision trace. There is no long-term learning loop.

Termination states are:

```text
accepted
abstained
insufficient
blocked
```

### 6.7 Output

```text
ResolutionProposal
contract_version
payload_checksum
resolution_proposal_id
run_id
task_id
event_id
mention
structural_slot
expected_entity_type
selected_candidate_id | null
rejected_candidate_ids
decision: ResolutionDecision
supporting_evidence_claim_ids
authority_source_ids
tool_trace_ids
limitation | null
```

## 7. Terminology and Facility Tool Families

Facility and terminology authority boundaries remain separate even though
their ambiguous decisions are owned by one Agent.

Facility tools may expose:

```text
lookup_nasr_facility
lookup_artcc
resolve_facility_alias
get_facility_authority_record
check_facility_type_constraint
```

Terminology tools may expose:

```text
lookup_authority_term
get_authority_definition
get_term_source_reference
query_ontology_hierarchy
check_schema_compatibility
```

Before the Semantic Resolution Agent is enabled for terminology, every term
candidate must carry:

```text
term_id
preferred_label
abbreviation or surface form
real authority definition
authority source reference
source snapshot checksum
candidate ontology class
schema compatibility result
```

Literal placeholder definitions, including `an authority term definition`,
are forbidden. The prompt must not claim that the Agent received an authority
definition or source when the runtime contract did not supply one.

## 8. Decision Case Assembly Agent

### 8.1 Goal

Assemble a coherent, provenance-bound `CaseAssemblyProposal` from verified
event facts, accepted resolution proposals, admitted context layers, and a
frozen schema profile.

The Agent selects evidence and schema tools and proposes facts. It never
publishes directly.

### 8.2 State

```text
CaseAssemblyTask
core_event_facts
resolution_proposal_ids
available_evidence_layers
required_case_slots
optional_case_slots
missing_slots
schema_profile_id
schema_context
selected_evidence_claim_ids
proposed_facts
profile_gaps
context_associations
omitted_slots
validation_feedback
remaining_tool_budget
```

### 8.3 Tools

```text
get_case_requirements
get_schema_context
get_source_evidence
get_resolution_result
get_context_associations
get_public_observations
```

All tools are read-only except that the Agent may emit a proposal into working
state. The proposal is not a graph write.

`preflight_validate_proposal` is a deterministic orchestration service rather
than a model-selectable Agent tool. Orchestration runs it after the initial
proposal and, when one semantic revision is allowed, after the revised
proposal. These at most two deterministic validations are recorded in the
audit trace but do not consume the Agent's six-call read-only tool budget.

### 8.4 Action Space

```text
inspect_evidence_layer
request_resolution
select_schema_mapping
propose_fact
record_profile_gap
omit_unsupported_slot
submit_proposal
abort
```

A `request_resolution` action emits a typed `ResolutionTask`. Deterministic
orchestration invokes the Semantic Resolution Agent and returns the registered
`ResolutionProposal`; the Agents do not converse directly.

### 8.5 Policy and Budget

- deterministic assembly is used when every required mapping is complete and
  no evidence or schema choice remains;
- otherwise the Agent may make at most six model-selected read-only tool calls
  across the complete activation;
- one case may activate at most two Semantic Resolution tasks; required slots
  are ordered before optional slots;
- child Semantic Resolution provider calls and Assembly provider calls are
  charged to one record-ingest ledger with an aggregate maximum of eight
  provider calls;
- if a third unresolved required slot remains, assembly returns
  `insufficient`; an unresolved optional slot is omitted with an explicit
  limitation;
- preflight validation returns typed constraint IDs and allowed corrections;
- repairable feedback permits one constrained revision;
- hard violations terminate immediately as `blocked`;
- the complete path permits at most three provider calls: tool selection,
  proposal generation, and one optional revision;
- the Formal Graph Kernel independently validates the final proposal and owns
  the publication decision.

### 8.6 Semantic Boundaries

The Agent must not:

- convert temporal or spatial co-occurrence into causation;
- use Weather context to create or complete an ATCSCC declared reason;
- represent BTS observations as FAA demand, AAR, capacity, or EDCT;
- treat a profile gap as a rejected fact or formal graph fact;
- replace a null observation with zero;
- assert lifecycle, applicability, or similarity relations without the
  corresponding approved deterministic derivation and profile;
- create a class or predicate outside the frozen schema profile;
- bypass the Formal Graph Kernel.

### 8.7 Validation Feedback

Validation feedback has the following contract:

```text
ValidationFeedback
feedback_id
violation_code
constraint_id
affected_proposal_item_id
repairable
allowed_corrections
evidence_ids
```

The revision is called validation-guided revision. It is not described as
free-form self-reflection. A repair may only select an allowed correction; it
may not introduce new facts or sources.

### 8.8 Output

```text
CaseAssemblyProposal
contract_version
payload_checksum
case_assembly_proposal_id
run_id
task_id
case_id
assembly_status: AssemblyStatus
component_layer_results
proposed_facts
evidence_bindings
resolution_proposal_ids
context_associations
profile_gaps
omitted_slots
limitations
tool_trace_ids
revision_count
```

## 9. Decision Case Analysis Agent

### 9.1 Goal

Answer a registered decision-case question by selecting the minimum sufficient
read-only tools over the validated graph and its audit artifacts.

The approved question families are:

1. decision episode and lifecycle;
2. decision-time and operational situation;
3. applicability and impact;
4. historical case similarity and comparison.

### 9.2 State

```text
CaseAnalysisTask
question
intent_family
event_or_case_scope
query_plan_id
available_bound_step_ids
executed_bound_step_ids
requested_evidence_layers
retrieved_fact_ids
retrieved_derivation_ids
retrieved_profile_gap_ids
retrieved_assessment_ids
retrieved_source_ids
component_layer_results
missing_evidence
remaining_step_budget
answer_status
answer_contract_id
```

### 9.3 Bound Query Gateway

The following are internal router operations, not model-visible tool names:

```text
get_episode_timeline
get_operational_situation
get_applicable_entities
get_observed_flight_outcome
find_similar_cases
compare_cases
get_fact_provenance
```

The deterministic router freezes operation arguments, scope manifest and
checksum, evidence groups, result limit, temporal view, and result contract in
an immutable `QueryPlan`. The model receives step IDs and descriptions only.
Its sole model-visible tool is:

```text
execute_bound_query_step(step_id)
```

This design retains the bound-step security contract in Section 9 of
`2026-07-27-decision-case-semantic-expansion-design.md`. It does not expose the
internal high-level operations directly and does not permit the model to edit
their arguments. Arbitrary Cypher, SPARQL, filesystem access, raw-source
search, web search, and graph writes remain unavailable.

### 9.4 Policy and Budget

- deterministic support, scope, event identity, and artifact-integrity checks
  run before provider construction;
- unsupported questions, absent required evidence, and missing events return
  without a provider call;
- simple scalar fact questions remain deterministic;
- a supported compound question activates the Agent;
- before Agent activation, deterministic orchestration executes every required
  primary step through the same bound-step gateway and verifies its typed
  result;
- a blocked required step returns deterministic Query `blocked`, and an
  insufficient required step returns deterministic Query `insufficient`,
  before provider construction;
- only an all-required-`ok` plan may activate the Agent;
- optional steps with a known non-`ok` preflight status are not exposed to the
  Agent;
- the Agent's first provider call observes those required results and either
  returns a supported answer or selects one exposed optional bound-step ID;
- when an optional step is selected, deterministic orchestration executes it
  and the second and final provider call observes the result and returns the
  answer;
- if an exposed optional step becomes corrupt during execution, orchestration
  returns deterministic Query `blocked` without a second provider call;
- a single-family plan normally contains one required primary step and at most
  one optional evidence-driven follow-up step;
- a registered composite plan may contain up to the existing maximum of three
  bound steps when all required steps fit the reserved call budget;
- optional steps become available only after required steps succeed;
- the current model-tool-model provider budget remains unchanged, with at
  most two provider calls;
- the Agent then answers, returns `insufficient`, or returns `blocked`;
- it never falls back to model knowledge or an unregistered source.

### 9.5 Frozen Model and Tool Budgets

The first implementation freezes the following limits. A lower limit may be
configured for an individual test, but a run may not raise these values
without a reviewed contract change.

| Agent | Provider calls per activation | Read-only tool calls | Maximum rendered input | Maximum output |
| --- | ---: | ---: | ---: | ---: |
| Semantic Resolution Agent | 2 | 3 | 4,096 tokens | 256 tokens |
| Decision Case Assembly Agent | 3 | 6 | 4,096 tokens | 512 tokens |
| Decision Case Analysis Agent | 2 | 3 bound steps | 4,096 tokens | 512 tokens |

The Decision Case Assembly row excludes child activations only for the
per-Agent column. Child Semantic Resolution calls and Assembly calls still
share the record-ingest ledger and its aggregate maximum of eight provider
calls. The two-child policy in Section 8.5 means that the designed worst case
is seven provider calls: two calls for each of two resolution tasks and three
Assembly calls.

The runtime checks the rendered-input cap before provider construction and
configures the provider output cap explicitly. A malformed response does not
receive a formatting-repair retry. Every attempted provider call consumes the
relevant call budget even when the provider fails or omits token-usage
metadata. Provider-reported input and output usage is retained when available.

### 9.6 Output

```text
QueryEvidenceBundle
contract_version
payload_checksum
query_id
run_id
task_id
answer_status: QueryStatus
answer_contract_id
component_statuses
component_layer_results
executed_step_ids
unexecuted_required_step_ids
retrieved_fact_ids
retrieved_derivation_ids
retrieved_profile_gap_ids
retrieved_assessment_ids
retrieved_source_ids
tool_trace
answer_statements
limitations
```

Each `answer_statements` row carries `text`, `statement_kind`, and non-empty
support IDs when its kind requires evidence. A reader must be able to
distinguish source facts, deterministic derivations, Agent synthesis, and
limitations.

`component_layer_results` contains only the layers selected by the frozen
`QueryPlan`; unrelated case layers are omitted. The rows are part of the
canonical payload checksum, so a missing or blocked layer cannot be removed
from an already validated bundle without invalidating it.
`component_statuses` is the deterministic ordered status projection retained
for compatibility with the parent `QueryTerminalResult`; it, the executed and
unexecuted step IDs, assessment IDs, and `answer_contract_id` are covered by
the same checksum.

## 10. Memory Model

The architecture uses three kinds of memory without creating a Memory Agent:

```text
working memory   = current LangGraph or workflow state
knowledge memory = validated Decision Case Knowledge Graph
audit memory     = immutable run artifacts, manifests, and traces
```

Long-term self-learning, autonomous prompt revision, and experience replay are
out of scope.

## 11. Status and Error Propagation

Status is not one shared enum. Each boundary uses a separate discriminated
domain:

```text
ResolutionDecision =
  accepted | abstained | insufficient | blocked

AssemblyStatus =
  ok | partial | insufficient | blocked

ComponentLayerStatus =
  ok | insufficient | blocked

FactDisposition =
  formal_fact | profile_gap | rejected

QueryStatus =
  ok | insufficient | blocked | unsupported
```

Their meanings are:

| Domain | Value | Meaning |
| --- | --- | --- |
| Resolution | `accepted` | One supplied candidate has sufficient authority support. |
| Resolution | `abstained` | Eligible candidates exist, but evidence cannot distinguish them. |
| Resolution | `insufficient` | No eligible candidate or required resolution evidence exists. |
| Resolution | `blocked` | Resolution contract, authority record, or checksum is corrupt. |
| Assembly | `ok` | Required case evidence is valid and no requested slot is unresolved. |
| Assembly | `partial` | Core case evidence is valid, but an optional slot or layer is absent, abstained, or blocked. |
| Assembly | `insufficient` | A required case slot lacks sufficient evidence or resolution. |
| Assembly | `blocked` | Core input, proposal, profile, or validation binding is corrupt. |
| Layer | `ok` | The specific semantic layer is available and validated. |
| Layer | `insufficient` | The specific layer has no qualifying evidence. |
| Layer | `blocked` | The specific layer is present but corrupt or mismatched. |
| Fact | `formal_fact` | The Formal Graph Kernel admitted the statement. |
| Fact | `profile_gap` | A source statement exists but the profile cannot publish it. |
| Fact | `rejected` | The proposed statement failed validation and is not published. |
| Query | `ok` | The registered question is answered from validated evidence. |
| Query | `insufficient` | Required answer evidence does not exist. |
| Query | `blocked` | A required query artifact or evidence binding is corrupt. |
| Query | `unsupported` | The question is outside the registered capability surface. |

`profile_gap` is a fact disposition and audit record, not an Agent, layer, or
query terminal status.

The deterministic roll-up rules are:

- a required `abstained` resolution maps to Assembly `insufficient`;
- an optional `abstained` resolution maps to Assembly `partial`;
- a blocked core input maps to Assembly `blocked`;
- a blocked optional layer leaves the verified core case available as
  Assembly `partial`, while retaining that layer's `blocked` status;
- any query requiring a blocked layer returns Query `blocked`;
- an `insufficient` optional query layer may coexist with verified statements,
  but the answer must expose the component status;
- an unsupported intent returns Query `unsupported` before provider
  construction.

Downstream components must not weaken a decision, status, or disposition:

```text
blocked      must not become insufficient
abstained    must not become accepted
profile_gap  must not become a formal fact
partial      must not be presented as complete
insufficient must not be completed from model knowledge
```

An optional blocked layer does not invalidate an already verified core ATCSCC
event, but a query requiring that layer returns `blocked`.

## 12. Typed Collaboration Protocol

The shared workflow state contains IDs rather than copied prose wherever
possible:

```text
SourceSnapshotRegistry
EvidenceClaimRegistry
ResolutionTaskRegistry
ResolutionProposalRegistry
CaseAssemblyTask
CaseAssemblyProposal
ValidationFeedback
ValidatedFactRegistry
CaseAnalysisTask
QueryEvidenceBundle
```

Each cross-stage object is bound to:

```text
contract_version
payload_checksum
run_id
task_id
event_id or case_id
source IDs where applicable
snapshot checksums where applicable
prompt version for model-mediated steps
tool version for deterministic steps
```

No Agent may reinterpret an upstream status or silently substitute a new
source record.

### 12.1 Strict Runtime Contracts

All cross-stage contracts are strict Pydantic models with:

```text
extra = forbid
frozen = true after validation
explicit Literal or enum discriminators
tuple collections with deterministic sorting
UTC-aware timestamps
runtime-computed canonical payload checksum
```

`contract_version` is a frozen literal for one schema generation.
`payload_checksum` is computed by the runtime over canonical JSON after
excluding the checksum field itself. The model never supplies either field.

The minimum discriminators are:

```text
ResolutionProposal.decision: ResolutionDecision
CaseAssemblyProposal.assembly_status: AssemblyStatus
ComponentLayerResult.status: ComponentLayerStatus
FactAssessment.disposition: FactDisposition
QueryEvidenceBundle.answer_status: QueryStatus
AnswerStatement.statement_kind:
  source_fact | deterministic_derivation | agent_synthesis | limitation
```

`ComponentLayerResult` has the minimum fields:

```text
layer_id: str
status: ComponentLayerStatus
required_for_task: bool
artifact_ids: tuple[str, ...]
missing_reason_code: str | null
blocking_error_id: str | null
```

An `ok` layer requires at least one validated artifact ID. An `insufficient`
layer requires a missing-reason code and no blocking-error ID. A `blocked`
layer requires a blocking-error ID. Assembly proposals carry results for every
attempted case layer; query bundles carry only results selected by the frozen
plan.

`AnswerStatement` is statement-level rather than one free-form answer section:

```text
AnswerStatement
statement_id: str
statement_kind: AnswerStatementKind
text: str
support_fact_ids: tuple[str, ...]
support_derivation_ids: tuple[str, ...]
support_profile_gap_ids: tuple[str, ...]
support_source_ids: tuple[str, ...]
support_statement_ids: tuple[str, ...]
```

`source_fact` requires a fact or profile-gap support ID and a source ID.
`deterministic_derivation` requires a derivation ID and its supporting fact or
source IDs. `agent_synthesis` requires at least one prior supported statement
ID in the final answer envelope. `limitation` may have no evidence ID only
when it states an absence already represented by a component status.

### 12.2 Model Output Encoding and Parse Failure

The provider-facing output remains simpler than the internal contracts and
does not require provider-side JSON Schema support.

Semantic Resolution emits one JSON object containing only:

```text
decision
selected_candidate_id
rejected_candidate_ids
limitation
```

The runtime supplies IDs, versions, checksums, source bindings, and tool traces
before constructing and validating `ResolutionProposal`.

Decision Case Assembly retains the provider-compatible tagged text form:

```text
GRAPH_PATCH
{"proposal_item_id":"...", "subject_id":"...", "predicate_iri":"...",
 "object_kind":"iri|literal", "object_value":"...",
 "evidence_claim_ids":["..."], "derivation_ids":["..."],
 "validation_profile_id":"..."}
PROFILE_GAPS
{"proposal_item_id":"...", "event_id":"...", "field":"...",
 "normalized_value":"...", "evidence_claim_ids":["..."],
 "schema_mapping_reason_code":"...", "validation_profile_id":"..."}
```

The section markers remain compatible with the current provider interaction,
but each non-empty line is one JSON object with explicit proposal and support
IDs. The Batch A parser update creates candidate patch and gap rows from those
objects. The runtime derives source and snapshot bindings from the referenced
claims or derivations, adds task, resolution, status, and trace metadata, and
then validates one strict `CaseAssemblyProposal`.

Every formal-fact row requires at least one supplied evidence-claim or
derivation ID and one supplied validation-profile ID. Every profile-gap row
requires at least one evidence-claim ID and one supplied validation-profile
ID. Referenced IDs must have been present in the Agent's typed input. A
reference that is absent, belongs to another event or run, has an incompatible
profile, or resolves to zero or multiple registered objects returns
`blocked`. Source IDs alone are never used to infer an evidence binding.

Decision Case Analysis emits one JSON object containing an ordered
`answer_statements` array. The runtime verifies statement support against the
executed bound-step observations before constructing the final immutable
`QueryEvidenceBundle`.

When supported by a provider, JSON-object response mode may be used. Full
provider-side JSON Schema support is not required. Local Pydantic validation
is always authoritative.

There is no automatic parse-repair retry:

- malformed or extra model output returns `blocked`;
- an unknown enum, candidate, statement kind, or support ID returns `blocked`;
- Assembly's one validation-guided revision is reserved for a parsed,
  semantically repairable proposal and is not a parse retry;
- the parse failure and raw-response checksum are recorded without persisting
  hidden reasoning.

## 13. Capability Coverage

| Capability | Semantic Resolution | Case Assembly | Case Analysis |
| --- | --- | --- | --- |
| Goal-directed decision | yes | yes | yes |
| Dynamic bounded tool selection | yes | yes | yes |
| State update after observation | yes | yes | yes |
| Evidence retrieval | yes | yes | yes |
| Classification or ranking | yes | no | yes |
| Planning | local | bounded | bounded |
| Verification feedback | constraint check | one revision | evidence sufficiency |
| Abstention or honest missing state | yes | yes | yes |
| Structured generation | resolution proposal | case proposal | evidence bundle and answer |
| Graph write permission | no | no | no |

The system does not claim negotiation, unrestricted planning, free-form
self-reflection, or long-term learning.

## 14. Migration from the Five Named Roles

| Current role | Approved destination |
| --- | --- |
| Advisory Agent | deterministic `AdvisoryParser` service |
| Facility Agent | facility authority tools plus Semantic Resolution Agent for genuine ambiguity |
| Terminology Agent | terminology and ontology tools plus Semantic Resolution Agent for genuine ambiguity |
| Knowledge Graph Construction Agent | Decision Case Assembly Agent |
| Query Agent | Decision Case Analysis Agent |
| Formal Graph Kernel | unchanged deterministic publication authority |

Compatibility wrappers may retain old callable names during migration, but
reader-facing documentation and traces must distinguish a deterministic
component from an activated Agent. Wrappers must be deprecated only after the
new contracts and regression tests pass.

## 15. Migration Batches

### Batch A: Contracts and Authority Evidence

Implementation status: complete. Three-Agent runtime migration has not
started, and the current workflow and reader-facing role names remain the
compatibility runtime.

- add the three task and result contract families;
- carry `structural_slot` and `expected_entity_type` through resolution tasks;
- supply real term definitions, source references, and snapshot checksums;
- add schema-compatibility results to term candidates;
- remove placeholder definitions;
- keep existing CLI commands and persisted artifacts compatible;
- retain old role functions as temporary wrappers.

### Batch B: Semantic Resolution Agent

- consolidate ambiguous facility and terminology decisions;
- keep source-specific authority tools separate;
- preserve zero-model unique-candidate paths;
- add accepted, abstained, insufficient, and blocked traces;
- test candidate-set containment and source binding.

### Batch C: Decision Case Assembly Agent

- evolve the current graph-construction tool loop into case-slot-aware
  assembly;
- expose admitted multi-source evidence through typed tools;
- add deterministic preflight validation and one bounded revision;
- preserve independent Formal Graph Kernel validation;
- keep deterministic assembly for fixed complete mappings.

### Batch D: Decision Case Analysis Agent

Add one high-level task family at a time:

1. `get_episode_timeline`;
2. `get_operational_situation`;
3. `get_applicable_entities` and `get_observed_flight_outcome`;
4. `find_similar_cases` and `compare_cases`.

Each sub-batch freezes its tool contract, admissible evidence, missing-state
behavior, prompt version, and acceptance cases before opening the next family.

### Batch E: Public Naming Cleanup

- start only after the implementation and reviewed-trace gates for Semantic
  Resolution, Case Assembly, and Case Analysis have all passed;
- remove old Agent names from reader-facing documentation and new traces;
- retain compatibility aliases only where removal would break a supported
  command or artifact reader;
- update the normative parent design and metadata;
- remove compatibility wrappers only after a separately reviewed migration.

## 16. Acceptance Scenarios

### 16.1 Semantic Resolution

Two frozen ambiguity fixtures are required:

1. a source-grounded ambiguity that can be resolved only after an authority or
   ontology tool observation;
2. a source-grounded ambiguity whose evidence remains insufficient and must
   terminate as `abstained`.

Acceptance requires:

- unique candidates make zero provider calls;
- ambiguous paths stay within the supplied candidate set;
- the Agent uses real authority definitions and source references;
- the resolvable case records the supporting tool observation;
- the unresolvable case abstains without invention;
- corrupted authority or checksum bindings return `blocked`;
- repeated deterministic stub or replay inputs produce the same IDs and audit
  structure.

### 16.2 Decision Case Assembly

The three real records remain mandatory regressions:

| Record | Required result |
| --- | --- |
| Ground Stop `2026-05-19:123` | canonical KJFK; reason remains a profile gap; no formal `atm:impactingCondition` fact |
| GDP `2026-05-19:138` | canonical KJFK; cross-midnight interval remains correct; formal reason remains `weather`; source evidence ends at `THUNDERSTORMS` |
| GDP cancellation `2026-05-20:020` | canonical KEWR; declared reason remains absent; context cannot fill it |

Assembly acceptance also requires:

- Weather reports remain temporally eligible and non-causal;
- public operational observations retain source-qualified semantics;
- null remains null and reported zero remains zero;
- optional missing layers produce `partial` without invalidating the core
  event;
- wrong source, event, run, profile, or checksum bindings fail closed;
- repeated materialization remains idempotent.

Two controlled proposal fixtures verify feedback:

1. a repairable datatype or allowed-value formatting error receives typed
   feedback, is revised once, and passes;
2. a forbidden causal or out-of-profile assertion receives a hard violation
   and is blocked without revision.

### 16.3 Decision Case Analysis

| Question family | Minimum accepted result |
| --- | --- |
| Episode and lifecycle | time-ordered, source-qualified episode evidence with source assertion separated from deterministic membership assessment |
| Operational situation | forecast, observation, public operational measurement, temporal role, and missing layer remain distinguishable |
| Applicability and impact | facility-, time-, scope-, or registered-object-level assessment, plus source-qualified observed outcome when requested, with rule and evidence IDs |
| Historical similarity | eligible historical cases, feature contributions, and differences without recommendation or target leakage |

Current source limitations remain explicit:

- without admitted flight-scope or flight-operation evidence, the system must
  not claim that a specific flight was actually controlled;
- a three-record demonstration is insufficient for credible similarity
  ranking;
- similarity enters `ok` only after a separately admitted comparable corpus
  and feature profile exist;
- the selected decision, declared reason, detailed reason, and outcome are
  excluded from decision-time situation similarity unless a later design
  explicitly approves a non-predictive comparison view.

Agent-path acceptance requires a trace containing:

```text
registered question classification
deterministic execution of required bound-step IDs
typed required-step observations delivered to the Agent
evidence-sufficiency decision
optional bound-step selection or supported stop
typed optional observation when selected
termination status
```

## 17. Representative Agent Traces

At least one reviewed trace per Agent is required before reader-facing claims
are changed.

### Trace A: Semantic Ambiguity

```text
ambiguous candidate set
  -> authority or ontology tool choice
  -> typed observation
  -> accept or abstain
```

### Trace B: Case Assembly

```text
available evidence layers
  -> schema and evidence tool selection
  -> case proposal
  -> typed validator feedback
  -> one bounded revision or block
  -> final submission
```

### Trace C: Multi-Step Case Analysis

```text
registered compound question
  -> deterministic required bound steps
  -> typed required observations
  -> Agent selects one exposed optional follow-up or stops with support
  -> optional typed observation when selected
  -> answer, insufficient, or blocked
```

Each trace records:

```text
agent name
prompt version
provider and model fingerprint
state transition IDs
tool names and bounded arguments
tool-result IDs
termination reason
token usage
latency
```

Hidden chain-of-thought is neither requested nor persisted.

### 17.1 Deterministic Acceptance and Live Semantic Smoke Tests

Automated acceptance uses deterministic stubs or captured provider replay.
Those runs must be byte-stable after canonical serialization and must prove
stable IDs, sorting, status roll-up, budget accounting, tool containment,
support binding, and audit structure.

As the final prerequisite to closing each Agent's implementation gate, one
bounded live semantic smoke test is reviewed separately:

- it uses a frozen source-grounded fixture and the same typed contracts;
- it cannot write directly to the graph or production artifacts;
- it must remain within the Agent's frozen model and tool budgets;
- it must produce the fixture's frozen expected semantic result: the selected
  candidate or abstention for Resolution, the admitted facts/profile gaps or
  block for Assembly, and the answer status plus support set for Analysis;
- it is accepted on contract validity, allowed tool use, evidence containment,
  statement-level support, termination status, and preserved raw-response
  checksum;
- it is not required to reproduce identical wording or byte-identical model
  output on repeated executions;
- it is not an accuracy benchmark and does not authorize a broad Agent claim.

Batch A creates contracts and deterministic fixtures only. The live smoke for
each Agent is a required final check inside that Agent's later implementation
gate in Batch B, C, or D. If a live provider is not authorized or available,
the gate remains pending and no public three-Agent claim is made. Full-suite
regression remains deterministic and makes no real provider call.

## 18. Test Matrix

| Layer | Required coverage |
| --- | --- |
| Contracts | schema validation, enums, stable IDs, run/event/source binding, checksums |
| Deterministic fast paths | zero provider calls for unique resolution, missing evidence, unsupported questions, and scalar facts |
| Agent behavior | evidence-dependent tool choice, candidate containment, abstention, feedback consumption, bounded revision |
| Evidence boundary | wrong source, event, run, profile, or checksum fails closed |
| Semantic regression | records 123, 138, and 020 preserve facility, time, reason, and provenance semantics |
| Graph safety | Agents cannot write; only Kernel-accepted facts reach JSONL, RDF, or Neo4j |
| Query safety | every answer statement is bounded by `QueryEvidenceBundle` |
| Prompt grounding | real authority definitions and source refs; no placeholder evidence or evaluation leakage |
| Reproducibility | byte-stable stub/replay artifacts and traces; bounded live smoke validated structurally rather than textually |
| Cost control | independent model, tool, token, and step limits per Agent |
| Compatibility | existing CLI and artifact readers work until an explicitly reviewed removal |

Implementation acceptance uses the repository-standard checks:

```bash
uv run ruff check .
uv run pytest -q
git diff --check
```

Each batch also runs focused tests for its contracts, Agent path, source
boundaries, and call-count invariants before the full suite.

## 19. Go and No-Go Gates

### Gate 1: Semantic Resolution

Go:

- real definitions and sources enter the candidate contract;
- one ambiguity resolves from tool evidence;
- one ambiguity abstains;
- unique candidates remain zero-model.
- the bounded live smoke returns its frozen expected selection or abstention
  with the required authority support.

No-Go:

- placeholder definitions remain;
- the Agent invents or broadens candidates;
- a known structural slot is discarded;
- authority corruption becomes ordinary insufficient evidence.

### Gate 2: Case Assembly

Go:

- the three real-record regressions pass;
- multi-source semantic layers remain separated;
- one allowed validation-guided revision succeeds;
- a hard semantic violation blocks;
- final publication remains Kernel-owned.
- the bounded live smoke preserves its frozen expected facts, profile gaps,
  limitations, and termination status.

No-Go:

- a profile gap enters the formal graph;
- Weather or public observations change the declared reason;
- the Agent writes directly;
- a repair introduces a new source or fact.

### Gate 3: Case Analysis

Go:

- episode, situation, and admitted applicability questions pass end to end;
- similarity passes only after its corpus and feature-profile gate;
- compound questions show bounded evidence-dependent tool choice;
- every answer remains traceable.
- the bounded live smoke returns its frozen expected answer status and exact
  support-ID set.

No-Go:

- target decisions or outcomes leak into decision-time similarity;
- absent flight evidence becomes a flight-impact claim;
- missing data is completed from model knowledge;
- arbitrary graph or web access becomes model-visible.

## 20. Claims

After all three Agent gates pass, the supported description is:

> A conditionally activated three-Agent system that resolves genuine semantic
> ambiguity, assembles provenance-bound decision cases, and performs bounded
> multi-step case analysis over a validated shared knowledge graph.

The following claims remain unsupported:

- all three Agents participate in every run;
- every query uses model reasoning;
- the system performs unrestricted planning;
- validation-guided revision is autonomous self-reflection;
- the system has long-term learning or experiential memory;
- the system establishes causal ATM explanations;
- the system recommends an optimal or correct TMI;
- a Multi-Agent architecture is more accurate than a Single-Agent baseline.

## 21. Explicitly Deferred

- one Agent per source;
- generic Data Agent;
- Coordinator or unrestricted Planner Agent;
- Critic, Verifier, or Memory Agent;
- Weather, BTS, ASPM, Lifecycle, Applicability, or Similarity specialist Agents;
- free-form Agent negotiation;
- arbitrary Cypher or SPARQL generation;
- web or raw-filesystem search from an Agent;
- autonomous ontology expansion;
- causal explanation;
- TMI recommendation or optimization;
- full-corpus live-model execution;
- Agent-count comparison and ablation experiments.

## 22. Planning Boundary

Batch A contracts and authority evidence are implemented. The Semantic
Resolution, Decision Case Assembly, and Decision Case Analysis Agent runtime
migration remains deferred to separately approved later batches.
