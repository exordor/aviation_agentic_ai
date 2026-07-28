# Decision-Case Semantic Core and Graph Retrieval v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every publishable ATCSCC event own an explicit formal `DecisionCase` graph independently of optional BTS data, then answer one real multi-hop competency question through a case-scoped graph view.

**Architecture:** The deterministic Decision Case reconstruction identity is prepared from the accepted event, selected source bindings, validation profiles, and available optional-layer inputs. Weather and BTS remain independent evidence layers. After their facts are available, a core graph builder publishes the `DecisionCase`, reconstruction, and membership edges. Corpus v2 remains the canonical source of truth; a read-only `CorpusGraphView` builds a case-scoped adjacency index over its formal facts. RDF, Neo4j, and Chroma remain rebuildable projections or indexes.

**Tech Stack:** Python 3.12, Pydantic v2, existing `ValidatedFact` and corpus v2 contracts, rdflib materialization, Chroma sidecar unchanged, pytest, Ruff, editable draw.io architecture source.

## Global Constraints

- Keep all active code, tests, contracts, CLI output, and documentation in English.
- Do not add an Agent, provider call, planner, retry loop, vector collection, external database requirement, or public CLI command.
- Preserve the three declared-reason states exactly:
  - Ground Stop `123`: source-bound profile gap;
  - GDP `138`: formal `weather`;
  - cancellation `020`: missing.
- Weather membership means only “included in the same historical reconstruction.” It must not create `causedBy`, `motivatedBy`, `affectedBy`, or any equivalent causal edge.
- BTS remains source-qualified public operational observation data. It must not become FAA demand, AAR, capacity, EDCT, causal outcome, or decision-effectiveness evidence.
- Optional Weather or BTS absence must not suppress the formal DecisionCase core.
- Corpus v2 remains authoritative. Old generated corpora are rebuilt; do not add a migration or compatibility path.
- The graph query is case-scoped and closed. Do not expose arbitrary predicates, hop counts, SPARQL, or Cypher to users or models.
- Use one bounded review pass, focused tests during implementation, and one final repository verification.

---

## 1. Diagnostic Basis and Approved Increment

The architecture review exposed two implementation gaps rather than drawing-only issues.

### Gap 1: DecisionCase identity is owned by an optional source layer

`build_bts_observation_facts()` currently creates:

```text
case:DecisionCase
case:DecisionCaseReconstruction
prov:specializationOf
prov:hadMember
```

When BTS evidence is `insufficient` or `blocked`, those facts are not produced. The corpus still has a `CorpusCase` catalog row, but RDF and Neo4j may contain only the TMI event and Weather reports, without a formal DecisionCase node.

### Gap 2: runtime questions filter triples but do not traverse the graph

`CorpusQueryStore` reads canonical facts, but current deterministic questions group or filter them by predicate. RDF and Neo4j are projections; Neo4j has no read adapter. The system therefore uses graph-shaped facts but does not yet demonstrate graph-native path retrieval.

### Capability advanced

The system will gain:

> a source-independent formal DecisionCase semantic core plus one deterministic multi-hop graph retrieval capability over the canonical corpus.

### Smallest end-to-end result

For GDP `138`, the query:

```text
Which weather reports and active-window BTS public observations belong to this reconstructed decision case?
```

returns formal graph paths connecting:

```text
DecisionCase
  <- prov:specializationOf - DecisionCaseReconstruction
  -> prov:hadMember - TMI event
  -> prov:hadMember - METAR / TAF report
  -> prov:hadMember - active BTS public observation
```

and continues from the report/observation to its facility, metric, result, numeric value, unit, and source-bound fact IDs where available.

### Minimum components

- one dedicated Decision Case core validation profile;
- one deterministic reconstruction seed/finalizer;
- a BTS observation builder that no longer owns case identity;
- corpus catalog fields for formal case and reconstruction IRIs;
- a case-scoped adjacency view over `CorpusFact`;
- one exact, zero-model competency question.

### Evidence that it works

- a publishable no-BTS case still materializes `DecisionCase`, reconstruction, and event membership;
- GDP `138` returns Weather and active BTS paths with exact formal fact IDs;
- all path fact IDs belong to that case in `case_facts.jsonl`;
- no context association is promoted into a formal edge;
- no model factory is constructed;
- the three canonical reason states remain unchanged.

### Success conditions

- Every publishable event has exactly one conceptual case IRI and one reconstruction IRI in corpus v2.
- Optional Weather and BTS members are added only when their formal layers are `ok`.
- Case graph facts are owned by the new core profile, not the BTS public-observation profile.
- The registered graph question executes adjacency traversal rather than scanning an audit summary table.
- Query output includes deterministic path records, retrieved formal fact IDs, and source IDs.

### Failure conditions

- BTS absence removes the DecisionCase core.
- Weather membership is presented as cause, motivation, or declared reason.
- A path crosses into another case.
- `context_associations.jsonl` is treated as a formal graph edge.
- Query execution depends on Neo4j availability or a model call.
- Existing declared-reason semantics change.

### Explicitly deferred

- Neo4j or SPARQL as a required query runtime;
- arbitrary graph exploration or variable-length paths;
- formalizing Weather context association roles;
- parsing METAR/TAF text into structured wind, visibility, ceiling, or phenomenon facts;
- operational-situation-aware embeddings;
- decision episodes, causal explanation, effectiveness claims, and TMI recommendation;
- changes to Agent roles or Analysis Agent planning.

---

## 2. File Structure

### Add

```text
data/ontology/curated/decision_case_core_slice.json
src/aviation_agentic_ai/agent_system/decision_case_graph.py
src/aviation_agentic_ai/agent_system/corpus_graph.py
tests/test_agent_system_decision_case_core.py
tests/test_agent_system_corpus_graph.py
```

### Modify

```text
data/ontology/curated/decision_case_public_observation_slice.json
src/aviation_agentic_ai/agent_system/contracts.py
src/aviation_agentic_ai/agent_system/validation_profiles.py
src/aviation_agentic_ai/agent_system/public_observations.py
src/aviation_agentic_ai/agent_system/context_artifacts.py
src/aviation_agentic_ai/agent_system/query_context_store.py
src/aviation_agentic_ai/agent_system/materialize.py
src/aviation_agentic_ai/agent_system/corpus_store.py
src/aviation_agentic_ai/agent_system/query_tool_graph.py
src/aviation_agentic_ai/agent_system/corpus_query.py
tests/test_agent_system_public_observations.py
tests/test_agent_system_multisource_context.py
tests/test_agent_system_corpus_store.py
tests/test_agent_system_corpus_projection.py
tests/test_agent_system_case_retrieval_documents.py
tests/test_agent_system_case_retrieval_evaluation.py
tests/test_agent_system_case_retrieval_index.py
tests/test_agent_system_case_retrieval_search.py
tests/test_agent_system_query_tool_graph.py
README.md
GOALS.md
TODO.md
RESEARCH_AUDIT.md
docs/multi_agent_kg_system_design.md
docs/figures/current_project_architecture.drawio
docs/figures/current_project_architecture.png
```

Do not modify visualization-branch code or generated corpus directories.

---

## 3. Public and Internal Contracts

### Validation layer

Extend the exact profile layer union:

```python
Literal[
    "decision",
    "decision_case_core",
    "weather",
    "public_operational_observation",
]
```

The new core profile admits only `system_membership` evidence. Its vocabulary is:

```text
Classes
  case:DecisionCase
  case:DecisionCaseReconstruction
  prov:Entity
  prov:Collection

Properties
  prov:specializationOf
  prov:hadMember
```

The public-observation profile continues to own SOSA/QUDT/PROV observation facts, but no longer owns `DecisionCase`, `DecisionCaseReconstruction`, `specializationOf`, or `hadMember`.

### Reconstruction contracts

Add to `contracts.py`:

```python
class DecisionCaseReconstructionSeed(StrictModel):
    conceptual_case_iri: str
    reconstruction_iri: str
    reconstruction_trace_id: str
    reconstruction_input_sha256: str
    profile_refs: tuple[ValidationProfileRef, ...]
    source_bindings: tuple[SourceBinding, ...]
    builder_id: str
    builder_checksum: str
    aggregation_procedure_id: str | None = None
    aggregation_procedure_checksum: str | None = None


class ReconstructionTrace(
    DecisionCaseReconstructionSeed
):
    member_iris: tuple[str, ...]


class DecisionCaseMemberBinding(StrictModel):
    member_iri: str
    member_kind: Literal[
        "event",
        "weather_report",
        "public_observation",
    ]
    source_ids: tuple[str, ...]


class DecisionCaseGraphBundle(StrictModel):
    status: Literal["ok", "blocked"]
    case_iri: str | None = None
    reconstruction_iri: str | None = None
    formal_facts: list[ValidatedFact] = Field(default_factory=list)
    reconstruction_trace: ReconstructionTrace | None = None
    failure_reason: str = ""
```

`ReconstructionTrace` remains the existing internal contract name, but its
owner becomes the Decision Case core. `builder_id` and `builder_checksum` are
always present. The aggregation fields are populated only when admitted BTS
public observations exist; they are `None` for a reconstruction without BTS.
Do not add an alias or loader for the old BTS-owned shape.

Refactor `BTSObservationBundle` to own only the public-observation layer:

```python
class BTSObservationBundle(StrictModel):
    status: Literal["ok", "insufficient", "blocked"]
    formal_facts: list[ValidatedFact] = Field(default_factory=list)
    observation_ids: tuple[str, ...] = ()
    fact_traces: list[ObservationFactTrace] = Field(default_factory=list)
    derivations: list[ObservationDerivation] = Field(default_factory=list)
    failure_reason: str | None = None
```

There is no compatibility alias for `case_facts`, `activity_facts`, or the BTS-owned `reconstruction_trace`.

### Corpus catalog

Make formal graph identities explicit:

```python
class CorpusCase(StrictModel):
    case_id: str
    case_iri: str
    reconstruction_iri: str
    event_id: str
    # existing fields unchanged
```

Keep `case_id` as the catalog identity. `case_iri` and `reconstruction_iri` are extracted from accepted core facts and must each be unique for the case.

### Graph query records

Add to `contracts.py`:

```python
class QueryGraphEdge(StrictModel):
    fact_id: str
    subject_iri: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    datatype_iri: str | None = None
    source_ids: tuple[str, ...] = ()


class QueryGraphPath(StrictModel):
    path_id: str
    path_kind: Literal[
        "event_member",
        "weather_member",
        "active_public_observation",
    ]
    edges: tuple[QueryGraphEdge, ...]
    source_ids: tuple[str, ...] = ()
```

Extend `QueryToolOutcome`:

```python
retrieved_graph_paths: list[QueryGraphPath] = Field(default_factory=list)
```

No path accepts user-supplied predicates or hop counts.

---

## 4. Task 1 — Freeze the Semantic-Core Failure as Tests

**Files:**

- Add: `tests/test_agent_system_decision_case_core.py`
- Modify: `tests/test_agent_system_public_observations.py`
- Modify: `tests/test_agent_system_multisource_context.py`

- [ ] Add a no-BTS fixture with a publishable event and, separately, an optional valid Weather bundle.
- [ ] Write a failing test asserting a DecisionCase and reconstruction exist when BTS is `insufficient`.
- [ ] Write a failing test asserting an event is always a member, while Weather/BTS members depend on their own layer status.
- [ ] Write a failing test asserting the public-observation builder emits no `DecisionCase`, `DecisionCaseReconstruction`, `prov:specializationOf`, or `prov:hadMember` facts.
- [ ] Write a failing test asserting no core or optional-layer fact contains a forbidden causal predicate.

Required test shape:

```python
def test_publishable_event_has_case_core_without_bts() -> None:
    bundle = build_decision_case_graph(
        seed=seed_without_bts,
        members=(
            DecisionCaseMemberBinding(
                member_iri=event.event_id,
                member_kind="event",
                source_ids=(event.advisory_source_id,),
            ),
        ),
        profile_registry=registry,
    )

    assert bundle.status == "ok"
    assert {
        fact.object_value
        for fact in bundle.formal_facts
        if fact.predicate_iri == RDF_TYPE_IRI
    } >= {
        CASE_DECISION_CASE_IRI,
        CASE_RECONSTRUCTION_IRI,
    }
    assert any(
        fact.predicate_iri == PROV_HAD_MEMBER_IRI
        and fact.object_value == event.event_id
        for fact in bundle.formal_facts
    )
```

- [ ] Run the focused tests and confirm they fail for the expected ownership reason:

```bash
uv run pytest -q \
  tests/test_agent_system_decision_case_core.py \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_multisource_context.py
```

- [ ] Do not commit failing tests separately; continue to Task 2.

---

## 5. Task 2 — Add the Core Profile and Deterministic Reconstruction Builder

**Files:**

- Add: `data/ontology/curated/decision_case_core_slice.json`
- Add: `src/aviation_agentic_ai/agent_system/decision_case_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/validation_profiles.py`
- Modify: `src/aviation_agentic_ai/agent_system/materialize.py`

- [ ] Add the `decision_case_core` layer to `ValidationProfileRef` and `ValidationLayer`.
- [ ] Load the new checksum-pinned profile in `load_validation_profile_registry()`.
- [ ] Define its evidence policy as `system_membership` across already registered source families.
- [ ] Remove case/reconstruction ownership from `decision_case_public_observation_slice.json`.
- [ ] Implement the stable reconstruction seed.

The seed payload must be deterministic and contain only:

```python
{
    "builder_id": BUILDER_ID,
    "event_id": event.event_id,
    "facility_id": canonical_facility.entity_id,
    "profile_refs": sorted_profile_refs,
    "selected_weather_report_ids": sorted_weather_ids,
    "selected_bts_summary_ids": sorted_summary_ids,
    "source_bindings": sorted_source_bindings,
}
```

Use:

```python
conceptual_case_iri = stable_iri(
    "urn:aviation-agentic-ai:decision-case:",
    event.event_id,
)
reconstruction_iri = (
    "urn:aviation-agentic-ai:decision-case-reconstruction:"
    + reconstruction_input_sha256
)
reconstruction_trace_id = (
    "reconstruction-trace:" + reconstruction_input_sha256
)
```

- [ ] Implement these exact interfaces:

```text
prepare_decision_case_reconstruction(
    event: DecisionContextEvent,
    canonical_facility: CanonicalEntity,
    weather_bundle: WeatherContextBundle,
    outcome_bundle: BTSOutcomeBundle,
    snapshot_registry: SourceSnapshotRegistry,
    profile_registry: ValidationProfileRegistry,
) -> DecisionCaseReconstructionSeed

build_decision_case_graph(
    seed: DecisionCaseReconstructionSeed,
    members: tuple[DecisionCaseMemberBinding, ...],
    profile_registry: ValidationProfileRegistry,
) -> DecisionCaseGraphBundle
```

- [ ] In the finalizer, emit exactly one conceptual case, one reconstruction, one `specializationOf`, and one `hadMember` per unique accepted member.
- [ ] Type every member as `prov:Entity` through the core profile without changing its domain class.
- [ ] Bind membership facts to the reconstruction trace and to the exact `DecisionCaseMemberBinding.source_ids` that establish the member.
- [ ] Update materialization validation to use the core-owned `ReconstructionTrace` as the owner of all `system_membership` facts.
- [ ] Keep Neo4j labels and `HAS_MEMBER` / `SPECIALIZATION_OF` mappings, but make them profile-independent.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_decision_case_core.py \
  tests/test_agent_system_public_observations.py
```

- [ ] Commit:

```bash
git add \
  data/ontology/curated/decision_case_core_slice.json \
  data/ontology/curated/decision_case_public_observation_slice.json \
  src/aviation_agentic_ai/agent_system/contracts.py \
  src/aviation_agentic_ai/agent_system/validation_profiles.py \
  src/aviation_agentic_ai/agent_system/decision_case_graph.py \
  src/aviation_agentic_ai/agent_system/materialize.py \
  tests/test_agent_system_decision_case_core.py \
  tests/test_agent_system_public_observations.py
git commit -m "feat(agent-system): add decision-case semantic core"
```

---

## 6. Task 3 — Remove BTS Ownership and Integrate the Core for Every Event

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/public_observations.py`
- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_context_store.py`
- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_agent_system_query_tools.py`

- [ ] Change `build_bts_observation_facts()` to accept a prepared reconstruction seed.
- [ ] Reuse `seed.reconstruction_iri` only to produce stable observation, activity, and interval identities.
- [ ] Return one deduplicated `formal_facts` list and explicit `observation_ids`.
- [ ] Remove all conceptual-case, reconstruction, `specializationOf`, and `hadMember` creation from `public_observations.py`.
- [ ] In `prepare_decision_context()`, prepare the reconstruction seed after Weather and BTS selection status is known and before public observation facts are built.
- [ ] In `integrate_decision_context()`, always finalize the core case graph after the Formal Graph Kernel accepted the event.
- [ ] Add optional members according to:

```text
event accepted        -> event member
Weather status == ok  -> selected METAR/TAF members
BTS status == ok      -> emitted public observation members
```

- [ ] Compose formal facts in this order before deterministic deduplication:

```python
formal_facts = [
    *validation.accepted,
    *weather_bundle.formal_facts_if_ok,
    *observation_bundle.formal_facts_if_ok,
    *decision_case_graph.formal_facts,
]
```

- [ ] A blocked optional layer must not remove core event/case/reconstruction facts. Preserve that layer's own `blocked` status and omit only its members.
- [ ] Persist the reconstruction trace from `DecisionCaseGraphBundle`, not from `BTSObservationBundle`.
- [ ] Update `query_context_store.py` so BTS derivation checks use the optional aggregation fields only when public observations are present; a no-BTS reconstruction must not be rejected for having `None` aggregation fields.
- [ ] Update artifact metadata so `decision_case_core` has its own profile ID, checksum, fact count, and status.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_query_tools.py \
  tests/test_agent_system_public_observations.py
```

- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/public_observations.py \
  src/aviation_agentic_ai/agent_system/context_artifacts.py \
  src/aviation_agentic_ai/agent_system/query_context_store.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_query_tools.py
git commit -m "refactor(agent-system): decouple case identity from BTS"
```

---

## 7. Task 4 — Align Corpus Catalog Identity with the Formal Graph

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/corpus_store.py`
- Modify: `tests/test_agent_system_corpus_store.py`
- Modify: `tests/test_agent_system_corpus_projection.py`
- Modify: `tests/test_agent_system_case_retrieval_documents.py`
- Modify: `tests/test_agent_system_case_retrieval_evaluation.py`
- Modify: `tests/test_agent_system_case_retrieval_index.py`
- Modify: `tests/test_agent_system_case_retrieval_search.py`

- [ ] Add `case_iri` and `reconstruction_iri` to `CorpusCase`.
- [ ] During normalization, find exactly one core `DecisionCase` type fact and exactly one reconstruction `specializationOf` fact assigned to the event's case.
- [ ] Verify the reconstruction contains a `prov:hadMember` edge to the event.
- [ ] Reject only semantic conflicts: missing/duplicate case identity or a reconstruction that does not contain the event.
- [ ] Preserve semantic fact deduplication and one-to-many `EvidenceLink` behavior.
- [ ] Confirm all formal core facts enter `facts.jsonl`, `case_facts.jsonl`, `kg.jsonl`, RDF, and Neo4j.
- [ ] Confirm audit-only Weather context associations remain excluded from all formal projections.
- [ ] Add a no-BTS corpus test:

```python
case = CorpusQueryStore(corpus_dir).get_case(event.event_id)
assert case is not None
assert case.case_iri.startswith(
    "urn:aviation-agentic-ai:decision-case:"
)
assert case.reconstruction_iri.startswith(
    "urn:aviation-agentic-ai:decision-case-reconstruction:"
)
```

- [ ] Rebuild expectations instead of loading old corpus-v2 fixtures through compatibility code.
- [ ] Update case-retrieval test fixtures to provide the now-required formal `case_iri` and `reconstruction_iri`; do not weaken the new fields with defaults.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_agent_system_case_retrieval_documents.py \
  tests/test_agent_system_case_retrieval_evaluation.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_agent_system_case_retrieval_search.py
```

- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/corpus_store.py \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_agent_system_case_retrieval_documents.py \
  tests/test_agent_system_case_retrieval_evaluation.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_agent_system_case_retrieval_search.py
git commit -m "feat(agent-system): align corpus cases with formal graph identity"
```

---

## 8. Task 5 — Add a Case-Scoped Graph View

**Files:**

- Add: `src/aviation_agentic_ai/agent_system/corpus_graph.py`
- Add: `tests/test_agent_system_corpus_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/corpus_store.py`

- [ ] Implement `CorpusGraphView` over only the selected case's `CorpusFact` rows.
- [ ] Build deterministic outgoing and incoming indexes sorted by:

```text
subject_iri, predicate_iri, object_value, fact_id
```

- [ ] Implement:

```python
class CorpusGraphView:
    def neighbors(
        self,
        entity_iri: str,
        *,
        direction: Literal["out", "in"],
        predicate_iris: tuple[str, ...] = (),
    ) -> tuple[QueryGraphEdge, ...]:
        index = (
            self._outgoing
            if direction == "out"
            else self._incoming
        )
        allowed = set(predicate_iris)
        return tuple(
            edge
            for edge in index.get(entity_iri, ())
            if not allowed or edge.predicate_iri in allowed
        )

    def follow(
        self,
        entity_iris: tuple[str, ...],
        *,
        direction: Literal["out", "in"],
        predicate_iri: str,
    ) -> tuple[QueryGraphEdge, ...]:
        return tuple(
            edge
            for entity_iri in sorted(set(entity_iris))
            for edge in self.neighbors(
                entity_iri,
                direction=direction,
                predicate_iris=(predicate_iri,),
            )
        )
```

- [ ] Add:

```python
def graph_for_event(self, event_id: str) -> CorpusGraphView:
    return CorpusGraphView(self.get_case_facts(event_id))
```

to `CorpusQueryStore`.

- [ ] Implement the closed domain function:

```text
get_reconstructed_case_evidence_paths(
    graph: CorpusGraphView,
    case_iri: str,
    reconstruction_iri: str,
) -> tuple[QueryGraphPath, ...]
```

`corpus_graph.py` imports graph fact contracts only. It must not import
`CorpusQueryStore` or `CorpusCase`; this keeps `corpus_store.py ->
corpus_graph.py` one-directional and avoids a runtime import cycle.

- [ ] The function may traverse only these formal predicates:

```text
rdf:type
prov:specializationOf
prov:hadMember
data:forecastingAirport
sosa:hasFeatureOfInterest
sosa:phenomenonTime
sosa:observedProperty
sosa:hasResult
prov:wasDerivedFrom
dcterms:type
qudt:numericValue
qudt:unit
```

- [ ] Select active observations through the formal path:

```text
Observation
  -> sosa:phenomenonTime
  -> time:Interval
  -> dcterms:type
  -> phase:active
```

Do not read `observations.jsonl` to decide which formal observation is active.

- [ ] Build Weather paths only for report IRIs that are formal reconstruction members and have formal `data:forecastingAirport` facts.
- [ ] Derive each path ID from its ordered fact IDs.
- [ ] Include only source IDs carried by those formal facts.
- [ ] Add tests for:
  - incoming and outgoing traversal;
  - literal terminal edges;
  - stable ordering;
  - active-phase filtering;
  - strict case isolation;
  - absence of audit-only context association IDs.
- [ ] Run:

```bash
uv run pytest -q tests/test_agent_system_corpus_graph.py
```

- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/contracts.py \
  src/aviation_agentic_ai/agent_system/corpus_graph.py \
  src/aviation_agentic_ai/agent_system/corpus_store.py \
  tests/test_agent_system_corpus_graph.py
git commit -m "feat(agent-system): add case-scoped graph traversal"
```

---

## 9. Task 6 — Route One Real Multi-Hop Competency Question

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/query_tool_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/corpus_query.py`
- Modify: `tests/test_agent_system_query_tool_graph.py`

- [ ] Add:

```python
RECONSTRUCTION_EVIDENCE_PATH_QUESTION = (
    "Which weather reports and active-window BTS public observations "
    "belong to this reconstructed decision case?"
)
```

- [ ] Add a dedicated deterministic intent. Do not route it through Decision Case Analysis.
- [ ] Require `event_id`; an unknown event returns `insufficient` before any model factory is used.
- [ ] Load `case = store.get_case(event_id)` and
  `graph = store.graph_for_event(event_id)`, then invoke only
  `get_reconstructed_case_evidence_paths(graph, case.case_iri,
  case.reconstruction_iri)`.
- [ ] Return:
  - `retrieved_case_ids`;
  - `retrieved_graph_paths`;
  - the union of exact path `fact_id` values;
  - the union of path `source_ids`;
  - one `QueryToolTrace` naming the bounded graph-path operation.
- [ ] Use this answer wording:

```text
The validated reconstruction contains <W> Weather reports and <O>
active-window BTS public observations for <facility>. These records are
co-members of the same retrospective decision-case reconstruction; the graph
does not assert that Weather caused the traffic-management decision.
```

- [ ] Return `insufficient` if the case core is present but the question's required Weather or active BTS path is absent. Preserve the retrieved core path IDs so the missing layer is inspectable.
- [ ] Add GDP `138` acceptance assertions:
  - Weather path count is non-zero;
  - active public-observation path count is non-zero;
  - facility is KJFK;
  - every returned fact ID belongs to GDP `138`;
  - every returned source is bound to GDP `138`;
  - `model_calls == []`;
  - no association ID appears as a graph fact or path edge.
- [ ] Add no-BTS and cancellation `020` assertions:
  - the core remains queryable;
  - the new question is `insufficient` if the requested optional layer is absent;
  - reason state remains missing for `020`;
  - no placeholder reason is created.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_corpus_graph.py \
  tests/test_agent_system_query_tool_graph.py
```

- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/query_tool_graph.py \
  src/aviation_agentic_ai/agent_system/corpus_query.py \
  tests/test_agent_system_query_tool_graph.py
git commit -m "feat(agent-system): query decision-case evidence paths"
```

---

## 10. Task 7 — Three-Case and Optional-Layer Acceptance

**Files:**

- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_agent_system_corpus_projection.py`
- Modify: `tests/test_cli_agent_system.py` only if CLI JSON serialization needs the new path field

- [ ] Build bounded corpora for GS `123`, GDP `138`, and cancellation `020` with the existing fake-model fixtures.
- [ ] Assert all three have one formal DecisionCase and one reconstruction, independently of optional-layer status.
- [ ] Assert:

```text
GS 123  -> profile_gap, no formal impactingCondition
GDP 138 -> formal weather, exact advisory evidence unchanged
GDP 020 -> missing reason, no Weather/BTS reason substitution
```

- [ ] Assert Weather members are co-members only; no causal predicate enters formal facts, RDF, or Neo4j.
- [ ] Assert BTS public observations remain under their own profile and are not reclassified as decision outcomes.
- [ ] Assert `facts.jsonl`, RDF, and Neo4j contain the same formal core relationships.
- [ ] Assert repeated builds are byte-stable.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_decision_case_core.py \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_agent_system_corpus_graph.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py
```

- [ ] Commit any acceptance-only changes:

```bash
git add \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_cli_agent_system.py
git commit -m "test(agent-system): verify decision-case graph retrieval"
```

---

## 11. Task 8 — Update the Normative Architecture After the Code Works

**Files:**

- Modify: `README.md`
- Modify: `GOALS.md`
- Modify: `TODO.md`
- Modify: `RESEARCH_AUDIT.md`
- Modify: `docs/multi_agent_kg_system_design.md`
- Modify: `docs/figures/current_project_architecture.drawio`
- Modify: `docs/figures/current_project_architecture.png`

- [ ] Update prose only after the focused acceptance suite passes.
- [ ] Describe the system as a `Bounded-Agent Decision-Case Knowledge System`; do not add Agent roles.
- [ ] Add a compact Semantic Control band:

```text
ATMONTO Profiles · Authority Registry · Validation Rules
```

- [ ] Group sources by role:

```text
Decision record      ATCSCC
Authority evidence   NASR / ARTCC · FAA terminology
Weather context      METAR / TAF
Public observations  BTS On-Time
```

- [ ] Show the corrected runtime:

```text
Canonical Decision-Case Corpus
  -> Case-scoped Graph View -> Graph Path Retrieval -> Query Router
  -> Chroma Case Index      -> Similarity Retrieval  -> Query Router
  -> RDF / Neo4j            [rebuildable exports]
```

- [ ] Do not draw RDF/Neo4j as the runtime query backend in this batch.
- [ ] Label the center corpus:

```text
Decision facts · Scope · Context · Public observations · Provenance
```

- [ ] Use `QueryEvidenceBundle` only on the bounded Analysis Agent branch; do not invent a universal Answer Synthesizer.
- [ ] Keep the claim boundary visible:

```text
Retrospective evidence only
No causal or recommendation claims
```

- [ ] Use the draw.io skill to edit the source, export the PNG, inspect it, and keep the layout concise.
- [ ] Update `TODO.md` so the completed increment is recorded and the next choice remains one bounded subsystem:
  - structured Weather semantics;
  - optional Analysis Agent tool selection;
  - Neo4j read adapter only if scale or interactive traversal requires it.
- [ ] Run documentation checks:

```bash
git diff --check
uv run ruff check .
```

- [ ] Commit:

```bash
git add \
  README.md \
  GOALS.md \
  TODO.md \
  RESEARCH_AUDIT.md \
  docs/multi_agent_kg_system_design.md \
  docs/figures/current_project_architecture.drawio \
  docs/figures/current_project_architecture.png
git commit -m "docs(agent-system): document graph-grounded case core"
```

---

## 12. Final Verification

- [ ] Run the complete focused suite once:

```bash
uv run pytest -q \
  tests/test_agent_system_decision_case_core.py \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_agent_system_corpus_graph.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py
```

- [ ] Run repository verification once:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

- [ ] Build one temporary three-case corpus under `/tmp`; do not commit it.
- [ ] Run the new graph question for GDP `138` and inspect:
  - path kinds;
  - exact fact IDs;
  - KJFK reuse;
  - Weather and BTS source IDs;
  - zero model calls;
  - explicit non-causal wording.
- [ ] Run declared-reason questions for `123`, `138`, and `020`.
- [ ] Confirm repository output does not claim:
  - Weather caused the TMI;
  - BTS measured FAA demand/capacity;
  - the historical action was optimal;
  - RDF or Neo4j is the current runtime query backend.
- [ ] Perform one bounded review of the final diff. Fix only acceptance-relevant findings, rerun the focused suite, and stop.

---

## 13. Follow-On Batches, Not Part of This Plan

After this increment, use the revised architecture to choose one next subsystem:

1. **Structured Weather Semantics v1**
   - deterministically publish selected wind, visibility, ceiling, flight-category, and present-weather fields from existing records;
   - keep event-to-Weather context non-causal.

2. **Agentic Analysis Selection v1**
   - make some analysis-plan reads genuinely optional;
   - let the existing Analysis Agent choose among Weather, public-observation, and provenance reads without adding a model round or Agent role.

3. **Neo4j Graph Read Adapter**
   - implement the same closed graph-path contract over Neo4j only when corpus size, latency, or interactive exploration demonstrates a need;
   - keep Corpus as the source of truth and the local graph view as the test oracle.

4. **Context-Aware Case Retrieval v2**
   - enrich case documents with structured operational context only after Structured Weather Semantics exists;
   - do not rank decision quality or recommend a TMI.
