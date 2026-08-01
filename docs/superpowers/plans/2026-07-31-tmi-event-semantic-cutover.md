# ATMONTO-Centered TMI Event Semantic Cutover Implementation Plan

> **Historical and superseded.** This plan records the semantic cutover before
> the later ingestion-first persistence cutover. Its Corpus-oriented commands
> and storage contracts are not current interfaces. Current truth is defined
> by `RESEARCH_AUDIT.md`, `GOALS.md`, and
> `docs/multi_agent_kg_system_design.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the unsupported `DecisionCase` domain construct and rebuild
the active system around ATMONTO `TrafficManagementInitiative` events,
source-qualified evidence, non-causal context, and public operational
observations.

**Architecture:** The formal KG is rooted directly in exact, checksum-pinned
ATMONTO TMI instances. Corpus membership (`event_facts`), evidence links, and
context associations organize one event's records without inventing a formal
decision-process object. The bounded construction role becomes an Event
Evidence Integration Agent; corpus, graph, vector, query, and CLI identities
all use the TMI event ID.

**Tech Stack:** Python 3.12, Pydantic v2, LangGraph, RDFLib, Neo4j export,
ChromaDB, Click, pytest, Ruff, Draw.io.

## Global Constraints

- This is a breaking cutover. Do not add aliases, migration readers,
  deprecation shims, old CLI commands, or corpus-v2 compatibility.
- The domain root is the admitted ATMONTO
  `atm:TrafficManagementInitiative` instance and its active GDP, GS, and
  ReRoute subtypes.
- Do not replace `DecisionCase` with an isomorphic project class. No formal
  `TMIEventEvidenceBundle`, reconstruction collection, or synthetic decision
  process is required for publication.
- Keep ATCSCC event facts, Weather reports, BTS public observations, profile
  gaps, and provenance as distinct evidence roles.
- Weather associations remain `causal_claim=false`.
- BTS data remains a public operational observation; it is not FAA demand,
  capacity, AAR, EDCT, decision rationale, effectiveness, or a caused outcome.
- Preserve GS `2026-05-19:123` as a reason profile gap, GDP
  `2026-05-19:138` as formal `weather`, and GDP cancellation
  `2026-05-20:020` as an honestly missing reason.
- Preserve deterministic zero-model paths for unambiguous records and all
  zero-call preflight insufficiencies.
- Every valid public natural-language `ask` still activates the bounded Query
  Agent; this cutover must not restore fixed questions or deterministic answer
  routing.
- Fake/scripted providers are allowed only in `offline_software_test` tests.
  This refactor does not make model-quality claims and requires no live-model
  experiment.
- Preserve historical reports and captured evaluations as historical
  artifacts. Do not rewrite their old role names or metrics as current
  evidence.
- Do not add a new Agent, ontology framework, data source, causal model,
  recommendation feature, lifecycle episode, migration layer, or
  production-hardening guard.
- Use the existing ATMONTO-alignment worktree and branch. Do not merge or push
  in this batch.

## Capability and Acceptance Boundary

The smallest end-to-end result is:

```text
ATCSCC advisory
  -> ATMONTO-aligned TMI event facts
  -> optional Weather report facts
  -> optional BTS public-observation facts
  -> one Formal Publication Kernel
  -> tmi-event-corpus-v3
  -> exact event reads + event graph + event vector index
  -> LLM-routed Query Agent
  -> evidence-supported answer / insufficient / blocked
```

Evidence that the cutover works:

- one valid GDP, GS, and ReRoute builds without any `DecisionCase` fact;
- `facts.jsonl`, RDF/Turtle, and Neo4j contain the same formal fact IDs;
- `events.jsonl` and `event_facts.jsonl` organize those facts by event;
- Weather context and BTS observations retain their current evidence
  boundaries;
- `index-events`, `ask`, and `export-event` operate on event identity;
- old corpus, command, tool, role, and collection identifiers are absent from
  active code;
- focused tests, the complete repository suite, Ruff, build, and diff checks
  pass.

Failure conditions:

- publication or corpus admission still requires a project `DecisionCase`;
- a renamed class reproduces the same unsupported formal decision semantics;
- an event is identified by a source-dependent evidence bundle rather than
  its stable TMI event IRI;
- Weather or BTS supplies a missing declared reason;
- BTS is exposed as an outcome, effectiveness measure, demand, or capacity;
- the Query Agent regains a fixed question registry or deterministic response;
- old v2 files or commands remain accepted.

Explicitly deferred:

- decision-process inputs, alternatives, constraints, rationale, trade-offs,
  and attributable outcomes;
- `DecisionCase` as a future construct;
- TMI advisory lifecycle episodes;
- National Playbook PDF grounding;
- F1/F3S/S4/S1S flight and sector data;
- causal explanation, effectiveness scoring, or TMI recommendation;
- a new live-provider benchmark.

---

## File and Interface Map

### Public-observation boundary

- Rename `agent_system/bts_outcomes.py` to
  `agent_system/bts_observations.py`.
- Rename `BTSOutcomeSummary` / `BTSOutcomeBundle` to
  `BTSPublicObservationSummary` / `BTSPublicObservationBundle`.
- Rename `build_bts_outcome_summaries` to
  `build_bts_public_observation_summaries`.
- Rename `OutcomeObservationRead` / `OutcomeSummaryRead` to
  `PublicObservationRead` / `PublicObservationSetRead`.
- Rename `outcome_summaries.jsonl` to
  `bts_observation_summaries.jsonl`.
- Rename `get_outcome_observations` to `get_public_observations`.
- Rename the curated observation profile to
  `data/ontology/curated/public_observation_slice.json` and use
  `urn:aviation-agentic-ai:public-observation-schema:` for project terms.

### Construction Agent

- Rename `decision_case_contracts.py` to `construction_contracts.py`.
- Rename `case_assembly.py` to `event_evidence_integration.py`.
- Rename `case_assembly_tools.py` to
  `event_evidence_integration_tools.py`.
- Replace the `CaseAssembly*` family with `EventEvidenceIntegration*`.
- Replace role `decision_case_assembly` with
  `event_evidence_integration`.
- Replace task scope `decision_case` with `tmi_event_evidence`.
- Rename workflow node `decision_case_assembly` to
  `event_evidence_integration`.
- Rename the prompt catalog to `configs/prompts/tmi_event_agents_v1.yaml`;
  prompt set is `aviation-tmi-event-agents-v1`, integration prompt version is
  `event-evidence-integration-v1`.

The main integration interfaces are:

```python
build_event_evidence_integration_task(...) -> EventEvidenceIntegrationTask
compile_event_evidence_integration_proposal(
    task: EventEvidenceIntegrationTask,
) -> EventEvidenceIntegrationProposal
preflight_validate_event_evidence_proposal(
    task: EventEvidenceIntegrationTask,
    proposal: EventEvidenceIntegrationProposal,
) -> EventEvidenceIntegrationFeedback
run_event_evidence_integration_agent(
    task: EventEvidenceIntegrationTask,
    *,
    tool_model_factory: ToolModelFactory,
    catalog_path: str,
) -> EventEvidenceIntegrationResult
```

### Formal publication and corpus v3

- Delete `decision_case_graph.py`.
- Delete `data/ontology/curated/decision_case_core_slice.json`.
- Remove the `decision_case_core` validation layer and all
  `DecisionCase*` contracts.
- The Formal Publication Kernel accepts only admitted ATCSCC TMI, Weather,
  and public-observation layers.
- Use manifest version `tmi-event-corpus-v3`.
- Replace `CorpusCase` with `CorpusTMIEvent`.
- Replace `CorpusCaseFact` with `CorpusEventFact`.
- Remove `case_id`, `case_iri`, and `reconstruction_iri`; use the formal
  `event_id` everywhere.
- Replace `cases.jsonl` / `case_facts.jsonl` with
  `events.jsonl` / `event_facts.jsonl`.
- Change `CorpusSourceBinding.case_id` to
  `CorpusSourceBinding.event_id`.
- Replace `find_cases`, `get_case`, `get_case_facts`, `get_case_evidence`,
  and `get_decision_context` with `find_events`, `get_event`,
  `get_event_facts`, `get_event_evidence`, and `get_weather_context`.
- Replace `export_case` with `export_event` and use manifest
  `tmi-event-export-v1`.

`CorpusTMIEvent` is:

```python
class CorpusTMIEvent(StrictModel):
    event_id: str
    advisory_source_id: str
    event_type_iris: tuple[str, ...]
    facility_ids: tuple[str, ...]
    effective_start: datetime | None
    effective_end: datetime | None
    issued_at: datetime | None
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None
    fact_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
```

### Event retrieval and Query Agent

- Rename all `case_retrieval_*` modules to `tmi_event_retrieval_*`.
- Replace the `CaseRetrieval*` / `CaseSimilarity*` families with
  `TMIEventRetrieval*` / `TMIEventSimilarity*`.
- Use sidecar directory `tmi_event_index/`, manifest
  `tmi_event_index_manifest.json`, collection `tmi_events`, and
  representation `tmi-event-record-v1`.
- Replace tool names with:

```text
find_tmi_events
read_tmi_event_facts
read_weather_context
read_public_observations
read_tmi_event_graph
find_similar_tmi_events
```

- Replace `case_ids`, `support_case_ids`, and `retrieved_case_ids` with
  `event_ids`, `support_event_ids`, and `retrieved_event_ids`.
- Public commands become:

```text
build-corpus
index-events
ask
neo4j-export
export-event
```

No `index-cases`, `export-case`, or old tool aliases remain.

---

### Task 1: Separate BTS Public Observations from Decision Semantics

**Files:**
- Move: `src/aviation_agentic_ai/agent_system/bts_outcomes.py`
  -> `src/aviation_agentic_ai/agent_system/bts_observations.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/public_observations.py`
- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `src/aviation_agentic_ai/agent_system/sources.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/validation_profiles.py`
- Move: `data/ontology/curated/decision_case_public_observation_slice.json`
  -> `data/ontology/curated/public_observation_slice.json`
- Move: `tests/test_agent_system_bts_outcomes.py`
  -> `tests/test_agent_system_bts_observations.py`
- Modify: `tests/test_agent_system_public_observations.py`
- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_agent_system_query_tools.py`

**Interfaces:**
- Consumes: `TMIEventContext`, `CanonicalEntity`,
  `SourceSnapshotRegistry`, and the public-observation validation profile.
- Produces: `BTSPublicObservationBundle`,
  `BTSObservationBundle`, and `PublicObservationSetRead` without a
  DecisionCase/reconstruction dependency.

- [ ] **Step 1: Write failing semantic-boundary tests**

Add assertions equivalent to:

```python
bundle = build_bts_observation_facts(
    event=event,
    canonical_facility=facility,
    observation_bundle=public_observations,
    snapshot_registry=snapshots,
    profile_registry=profiles,
)
assert bundle.status == "ok"
assert all("DecisionCase" not in fact.object_value for fact in bundle.formal_facts)
assert all("decision-case-schema" not in fact.subject_iri for fact in bundle.formal_facts)
assert read.status == "ok"
assert read.observations[0].phase == "baseline"
```

Also assert that a numeric zero remains zero, a null source metric produces no
formal numeric fact, and neither source state can populate a TMI reason.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
uv run pytest -q \
  tests/test_agent_system_bts_observations.py \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_query_tools.py
```

Expected: import/name/signature failures for the new public-observation
contracts.

- [ ] **Step 3: Implement the public-observation cutover**

Perform the file/type/function renames, move the observation phase and metric
terms to the public-observation namespace, and generate observation IDs from:

```python
{
    "event_id": event.event_id,
    "facility_id": canonical_facility.entity_id,
    "phase": summary.phase,
    "metric": property_iri,
    "procedure_checksum": procedure.checksum,
    "source_id": summary.source_id,
    "source_snapshot_sha256": summary.source_snapshot_sha256,
}
```

Validate the BTS source directly against `SourceSnapshotRegistry`. Do not
require a reconstruction seed. Preserve the existing aggregation procedure,
phase windows, exact source binding, and fact traces.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the command from Step 2. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src tests data/ontology/curated
git commit -m "refactor(agent-system): clarify BTS public observations"
```

---

### Task 2: Rename the Construction Role to Event Evidence Integration

**Files:**
- Move: `src/aviation_agentic_ai/agent_system/decision_case_contracts.py`
  -> `src/aviation_agentic_ai/agent_system/construction_contracts.py`
- Move: `src/aviation_agentic_ai/agent_system/case_assembly.py`
  -> `src/aviation_agentic_ai/agent_system/event_evidence_integration.py`
- Move: `src/aviation_agentic_ai/agent_system/case_assembly_tools.py`
  -> `src/aviation_agentic_ai/agent_system/event_evidence_integration_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `src/aviation_agentic_ai/agent_system/graph_patch.py`
- Modify: `src/aviation_agentic_ai/agent_system/runtime.py`
- Modify: `src/aviation_agentic_ai/agent_system/corpus_batch.py`
- Modify: `src/aviation_agentic_ai/agent_system/agent_usage.py`
- Modify: `src/aviation_agentic_ai/agent_system/prompts.py`
- Modify: `src/aviation_agentic_ai/agent_system/authority_evidence.py`
- Modify: `src/aviation_agentic_ai/agent_system/authority_resolution.py`
- Modify: `src/aviation_agentic_ai/agent_system/resolution_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/semantic_resolution.py`
- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `src/aviation_agentic_ai/agent_system/live_agent_evaluation.py`
- Modify: `src/aviation_agentic_ai/agent_system/live_agent_experiment.py`
- Move: `configs/prompts/decision_case_agents_v1.yaml`
  -> `configs/prompts/tmi_event_agents_v1.yaml`
- Move: `tests/test_agent_system_case_assembly.py`
  -> `tests/test_agent_system_event_evidence_integration.py`
- Move: `tests/test_agent_system_decision_case_contracts.py`
  -> `tests/test_agent_system_construction_contracts.py`
- Modify: `tests/test_agent_system_prompt_catalog.py`
- Modify: `tests/test_agent_system_agent_usage.py`
- Modify: `tests/test_agent_system_runtime_binding.py`
- Modify: `tests/test_agent_system_live_evaluation.py`
- Modify: `tests/test_agent_system_live_experiment.py`
- Modify: `tests/test_agent_system_authority_evidence.py`
- Modify: `tests/test_agent_system_semantic_resolution.py`
- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_agent_system_current_architecture.py`
- Modify: `tests/test_agent_system_corpus_batch.py`
- Modify: `tests/test_agent_system_reroute.py`
- Modify: `tests/test_agent_system_tool_model.py`
- Modify: `tests/test_agent_system_multisource_contracts.py`
- Modify: `tests/test_agent_system_query_tools.py`
- Create: `data/evaluation/agent_system/live_agent_smoke_v3.yaml`
- Create: `data/evaluation/agent_system/live_agent_experiment_v3.yaml`

**Interfaces:**
- Consumes: the same sealed event fields, resolution proposals, evidence
  records, profiles, context, and source snapshots as the current bounded role.
- Produces: `EventEvidenceIntegrationProposal` or an honest abstention; it
  never creates a decision process, rationale, alternative, or graph write.

- [ ] **Step 1: Write failing role and workflow tests**

Assert:

```python
assert ROLE_KEYS == (
    "semantic_resolution",
    "event_evidence_integration",
    "query",
)
assert "event_evidence_integration" in compiled_graph.nodes
assert "decision_case_assembly" not in compiled_graph.nodes
assert usage.role == "event_evidence_integration"
assert usage.task_scope == "tmi_event_evidence"
```

Test both deterministic compilation and an activated scripted-tool path. Label
these tests `offline_software_test`; do not report them as Agent-quality
evidence.

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
uv run pytest -q \
  tests/test_agent_system_construction_contracts.py \
  tests/test_agent_system_event_evidence_integration.py \
  tests/test_agent_system_prompt_catalog.py \
  tests/test_agent_system_agent_usage.py \
  tests/test_agent_system_runtime_binding.py
```

Expected: new modules, roles, node names, and contract names are missing.

- [ ] **Step 3: Perform the breaking rename**

Rename the contract family, tool gateway, compiler, preflight validator,
runtime result, workflow state keys, model-factory field, prompt role, trace
role, and sidecar role/scope. Replace `case_id` inside the integration task
with `event_id`. Keep the action-observation budget, closed candidate set,
read-only tools, deterministic compiler, accepted/abstained behavior, and
Formal Publication Kernel handoff unchanged.

Update new metadata literals:

```text
aviation-tmi-event-agents-v1
event-evidence-integration-v1
tmi-event-construction-contracts-v1
tmi-event-run-v1
tmi-event-agent-usage-v1
deterministic_event_evidence_compiler
```

Historical committed result reports and v1/v2 suite files keep their original
labels and bytes. New v3 suite files use the new role; active evaluation code
targets v3. Do not make an old report point to a silently rewritten suite.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the command from Step 2 plus:

```bash
uv run pytest -q \
  tests/test_agent_system_live_evaluation.py \
  tests/test_agent_system_live_experiment.py
```

Expected: PASS without a provider call.

- [ ] **Step 5: Commit**

```bash
git add src tests configs
git commit -m "refactor(agent-system): rename assembly as evidence integration"
```

---

### Task 3: Remove the Formal DecisionCase Layer and Publish Corpus v3

**Files:**
- Delete: `src/aviation_agentic_ai/agent_system/decision_case_graph.py`
- Delete: `data/ontology/curated/decision_case_core_slice.json`
- Delete/replace: `tests/test_agent_system_decision_case_core.py`
- Create: `tests/test_agent_system_tmi_event_semantics.py`
- Move: `src/aviation_agentic_ai/agent_system/corpus_graph.py`
  -> `src/aviation_agentic_ai/agent_system/corpus_event_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `src/aviation_agentic_ai/agent_system/formal_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/validation_profiles.py`
- Modify: `src/aviation_agentic_ai/agent_system/materialize.py`
- Modify: `src/aviation_agentic_ai/agent_system/corpus_store.py`
- Modify: `src/aviation_agentic_ai/agent_system/corpus_batch.py`
- Modify: `src/aviation_agentic_ai/agent_system/corpus_query.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/__init__.py`
- Modify: `tests/test_agent_system_corpus_store.py`
- Modify: `tests/test_agent_system_corpus_batch.py`
- Move: `tests/test_agent_system_corpus_graph.py`
  -> `tests/test_agent_system_corpus_event_graph.py`
- Modify: `tests/test_agent_system_corpus_projection.py`
- Modify: `tests/test_agent_system_current_architecture.py`
- Modify: `tests/test_agent_system_ontology_alignment.py`

**Interfaces:**
- Consumes: accepted TMI event facts, optional Weather facts, optional public
  observations, evidence links, profile gaps, and context associations.
- Produces: `tmi-event-corpus-v3` with `CorpusTMIEvent`,
  `CorpusEventFact`, and event-centered read methods.

- [ ] **Step 1: Write failing construct-validity and corpus tests**

Add:

```python
assert not (root / "data/ontology/curated/decision_case_core_slice.json").exists()
assert all("DecisionCase" not in fact.object_value for fact in published_facts)
assert all("decision-case-schema" not in fact.subject_iri for fact in published_facts)
assert manifest.manifest_version == "tmi-event-corpus-v3"
assert manifest.event_count == 1
assert (corpus_dir / "events.jsonl").is_file()
assert (corpus_dir / "event_facts.jsonl").is_file()
assert not (corpus_dir / "cases.jsonl").exists()
assert not (corpus_dir / "case_facts.jsonl").exists()
```

Build one GDP, one GS, and one ReRoute fixture without any project
DecisionCase facts. Assert all three are admitted and their formal event IRIs
are the stable corpus identities.

Add a test that a v2 manifest is rejected with a concise “rebuild the corpus”
error and is never migrated.

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
uv run pytest -q \
  tests/test_agent_system_tmi_event_semantics.py \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_batch.py \
  tests/test_agent_system_corpus_event_graph.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_agent_system_ontology_alignment.py
```

Expected: old DecisionCase admission, files, contracts, and layer violate the
new assertions.

- [ ] **Step 3: Remove the formal wrapper and implement event membership**

Delete the DecisionCase profile, graph builder, contracts, workflow state,
context-artifact layer, materializer labels, and publication layer. Do not add
a replacement formal collection.

In `corpus_store.py`:

- parse the admitted ATMONTO TMI `rdf:type` fact for each event;
- create one `CorpusTMIEvent` keyed by `event_id`;
- attach every admitted formal fact from that build through
  `CorpusEventFact(event_id, fact_id)`;
- bind source artifacts through `CorpusSourceBinding.event_id`;
- deduplicate facts semantically and merge provenance through
  `EvidenceLink`;
- write `events.jsonl` and `event_facts.jsonl`;
- keep `context_associations` outside RDF/Neo4j;
- keep admitted public-observation facts inside formal projections;
- retain byte-stable ordering and content-addressed source objects.

Update manifest/count/checksum generation and all corpus read methods. The
event graph uses the selected event's `event_facts`; it does not require a
formal membership triple.

- [ ] **Step 4: Verify the three-source boundaries**

Add or retain assertions:

```python
assert gs123.reason_status == "profile_gap"
assert gdp138.reason_status == "formal"
assert gdp138.reason_value == "weather"
assert gdp020.reason_status == "missing"
assert all(row.causal_claim is False for row in weather_context)
```

Assert that optional Weather/BTS insufficiency still publishes the ATCSCC TMI
event and that a malformed admitted formal layer blocks before any projection
file is written.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run the command from Step 2 plus:

```bash
uv run pytest -q \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_graph_kernel.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src tests data/ontology/curated
git commit -m "refactor(agent-system): publish ATMONTO TMI event corpus v3"
```

---

### Task 4: Cut Retrieval, Hybrid Query, and CLI over to Event Identity

**Files:**
- Move: `src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py`
  -> `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_contracts.py`
- Move: `src/aviation_agentic_ai/agent_system/case_retrieval_documents.py`
  -> `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_documents.py`
- Move: `src/aviation_agentic_ai/agent_system/case_retrieval_index.py`
  -> `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_index.py`
- Move: `src/aviation_agentic_ai/agent_system/case_retrieval_search.py`
  -> `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_search.py`
- Move: `src/aviation_agentic_ai/agent_system/case_retrieval_evaluation.py`
  -> `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_evaluation.py`
- Modify: `src/aviation_agentic_ai/agent_system/hybrid_query_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/hybrid_query_agent.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/corpus_query.py`
- Modify: `src/aviation_agentic_ai/agent_system/live_agent_evaluation.py`
- Modify: `src/aviation_agentic_ai/agent_system/live_agent_experiment.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Move: `tests/test_agent_system_case_retrieval_documents.py`
  -> `tests/test_agent_system_tmi_event_retrieval_documents.py`
- Move: `tests/test_agent_system_case_retrieval_index.py`
  -> `tests/test_agent_system_tmi_event_retrieval_index.py`
- Move: `tests/test_agent_system_case_retrieval_search.py`
  -> `tests/test_agent_system_tmi_event_retrieval_search.py`
- Move: `tests/test_agent_system_case_retrieval_evaluation.py`
  -> `tests/test_agent_system_tmi_event_retrieval_evaluation.py`
- Modify: `tests/test_agent_system_hybrid_query_tools.py`
- Modify: `tests/test_agent_system_hybrid_query_agent.py`
- Modify: `tests/test_agent_system_hybrid_query_public.py`
- Modify: `tests/test_cli_agent_system.py`
- Modify: `tests/test_chroma_store.py`
- Modify: `tests/test_readme_commands.py`

**Interfaces:**
- Consumes: `CorpusQueryStore.events`, event-scoped fact/graph/context reads,
  and one event metadata document per indexed TMI event.
- Produces: exact/filter/graph/vector observations bound to event IDs for the
  existing bounded Query Agent.

- [ ] **Step 1: Write failing event-retrieval and CLI tests**

Assert the public help exposes exactly:

```text
build-corpus
index-events
ask
neo4j-export
export-event
```

Assert `index-cases` and `export-case` fail as unknown commands.

Assert the registered read-only tools are exactly the six event tool names
listed in the interface map. Assert statement support and final outcomes use
`support_event_ids` / `retrieved_event_ids`.

Assert the index artifact contract:

```python
assert manifest.manifest_version == "tmi-event-index-v1"
assert manifest.collection_name == "tmi_events"
assert manifest.representation_version == "tmi-event-record-v1"
assert (corpus_dir / "tmi_event_index/tmi_event_index_manifest.json").is_file()
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
uv run pytest -q \
  tests/test_agent_system_tmi_event_retrieval_documents.py \
  tests/test_agent_system_tmi_event_retrieval_index.py \
  tests/test_agent_system_tmi_event_retrieval_search.py \
  tests/test_agent_system_tmi_event_retrieval_evaluation.py \
  tests/test_agent_system_hybrid_query_tools.py \
  tests/test_agent_system_hybrid_query_agent.py \
  tests/test_agent_system_hybrid_query_public.py \
  tests/test_cli_agent_system.py
```

Expected: missing event modules, tools, fields, index, and commands.

- [ ] **Step 3: Implement event-centered retrieval**

Perform the file/type/function renames. Index the same bounded metadata:

```text
TMI type
canonical facility
declared-reason status and value
UTC time category
duration category
```

Do not add Weather, BTS, effectiveness, causal, or recommendation similarity.
Exact filters still run before cosine recall and the anchor event remains
excluded.

Update the Query Agent prompt and tool schemas so the model sees TMI events,
facts, Weather context, public observations, event graph edges, and historical
event similarity. Preserve the existing always-on LLM action-observation
loop, tool/turn budgets, immutable CLI scope, retrieval-before-answer rule, and
statement-level support validation.

- [ ] **Step 4: Implement breaking CLI and export names**

Use:

```text
index-events
export-event
matching_events
events_returned
similar_event
```

`export-event` writes:

```text
tmi_event_export_manifest.json
event.json
event_facts.jsonl
evidence_links.jsonl
profile_gaps.jsonl
context_associations.jsonl
observations.jsonl
source_bindings.jsonl
source_objects/
kg.ttl
```

It includes only the selected event and referenced source objects.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run the command from Step 2 plus:

```bash
uv run pytest -q \
  tests/test_chroma_store.py \
  tests/test_readme_commands.py \
  tests/test_agent_system_live_evaluation.py \
  tests/test_agent_system_live_experiment.py
```

Expected: PASS without a live provider.

- [ ] **Step 6: Commit**

```bash
git add src tests
git commit -m "refactor(agent-system): retrieve historical TMI events"
```

---

### Task 5: Update Active Documentation and Architecture Figures

**Files:**
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `README.md`
- Modify: `GOALS.md`
- Modify: `TODO.md`
- Modify: `RESEARCH_AUDIT.md`
- Modify: `RESEARCH_OVERVIEW.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `ARTIFACT_INDEX.md`
- Modify: `DECISION_LOG.md`
- Modify: `docs/multi_agent_kg_system_design.md`
- Create:
  `docs/figures/tmi_event_construction_architecture.drawio`
- Create: `docs/figures/tmi_event_construction_architecture.png`
- Create: `docs/figures/tmi_event_retrieval_architecture.drawio`
- Create: `docs/figures/tmi_event_retrieval_architecture.png`
- Delete: `docs/figures/decision_case_construction_architecture.drawio`
- Delete: `docs/figures/decision_case_construction_architecture.png`
- Delete: `docs/figures/decision_case_retrieval_architecture.drawio`
- Delete: `docs/figures/decision_case_retrieval_architecture.png`

**Interfaces:**
- Consumes: the implemented corpus-v3, integration-role, tool, index, and CLI
  names.
- Produces: one consistent current-project narrative; historical plans,
  reports, and captured evaluation artifacts remain explicitly historical.

- [ ] **Step 1: Write/update active-document checks**

Update `tests/test_agent_system_current_architecture.py` and
`tests/test_readme_commands.py` to assert:

```python
assert "ATMONTO" in active_design
assert "ATMGRAPH" in active_design
assert "TMI event" in active_design
assert "DecisionCase" not in active_design
assert "index-events" in readme
assert "export-event" in readme
assert "index-cases" not in readme
assert "export-case" not in readme
```

Historical directories are excluded from these assertions.

- [ ] **Step 2: Run document tests and verify RED**

Run:

```bash
uv run pytest -q \
  tests/test_agent_system_current_architecture.py \
  tests/test_readme_commands.py
```

Expected: active documents and figure paths still use DecisionCase names.

- [ ] **Step 3: Rewrite the current narrative**

State:

- ATMONTO defines the admitted TBox/application-profile terms.
- ATMGRAPH supplies ABox construction and cross-source-query principles; no
  ATMGRAPH dataset is imported and no exact replication is claimed.
- The active vertical slice is retrospective ATCSCC TMI event knowledge, not
  a complete ATM ontology or decision-process model.
- The Event Evidence Integration Agent selects only sealed evidence/schema
  candidates when deterministic construction is insufficient.
- Corpus v3 is the canonical persisted layer; RDF/Neo4j and Chroma are
  rebuildable projections.
- Weather is non-causal and BTS is public observation.
- A true `DecisionCase` is deferred until decision-state inputs,
  alternatives, constraints, rationale, and appropriately interpreted outcome
  evidence exist.

Append a new decision-log entry; do not rewrite earlier decisions. Mark old
Explorer/architecture documents as historical in `ARTIFACT_INDEX.md` rather
than rewriting their bodies. Keep old evaluation reports unchanged and label
them GDP-biased historical compatibility evidence.

- [ ] **Step 4: Rebuild the two Draw.io figures**

Use the Draw.io skill. The construction figure has one direction:

```text
Evidence sources
  -> deterministic adapters
  -> optional bounded integration Agent
  -> Formal Publication Kernel
  -> TMI Event Corpus v3
```

Show `ATMONTO application profile` as a semantic control input and
`ATMGRAPH ABox principles` as a construction reference. Do not show a
DecisionCase node.

The retrieval figure has:

```text
TMI Event Corpus v3
  -> exact event view
  -> event graph view
  -> metadata-conditioned TMI event index
  -> LLM Query Agent
  -> evidence support validation
  -> answer / insufficient / blocked
```

Use a single main direction, no crossed connectors, no more than two subtitle
lines per node, minimum 26 px text at export scale, and visually inspect both
PNGs.

- [ ] **Step 5: Run checks and verify GREEN**

Run:

```bash
uv run pytest -q \
  tests/test_agent_system_current_architecture.py \
  tests/test_readme_commands.py
git diff --check
```

Expected: PASS. Inspect both PNGs for clipping, overlap, and connector
crossings.

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md CLAUDE.md README.md GOALS.md TODO.md \
  RESEARCH_AUDIT.md RESEARCH_OVERVIEW.md REPRODUCIBILITY.md \
  ARTIFACT_INDEX.md DECISION_LOG.md docs tests
git commit -m "docs(agent-system): define ATMONTO-centered TMI event architecture"
```

---

### Task 6: Active-Tree Hygiene, Smoke Build, and Final Verification

**Files:**
- Modify only files that fail the acceptance checks.
- Do not modify historical reports merely to satisfy an unscoped global grep.

**Interfaces:**
- Consumes: Tasks 1-5.
- Produces: one verified branch ready for focused review, but not merged or
  pushed.

- [ ] **Step 1: Scan active code and current contracts**

Run:

```bash
git grep -n -E \
  'DecisionCase|decision_case|decision-case|CaseAssembly|case_assembly|BTSOutcome|outcome_summaries|index-cases|export-case' \
  -- \
  'src/**' \
  'configs/**' \
  'data/ontology/curated/**' \
  'AGENTS.md' 'CLAUDE.md' 'README.md' 'GOALS.md' 'TODO.md' \
  'RESEARCH_AUDIT.md' 'RESEARCH_OVERVIEW.md' 'REPRODUCIBILITY.md' \
  'docs/multi_agent_kg_system_design.md'
```

Expected: no matches. Generic runtime status fields named `outcome` are not
part of this prohibition.

- [ ] **Step 2: Run a deterministic five-event smoke build**

Build an ignored temporary corpus for:

```text
2026-05-19:123
2026-05-19:138
2026-05-20:020
2026-05-19:108
2026-05-20:137
```

Use `build-corpus --source-id` without `--allow-live-model`. Assert:

```text
selected = 5
blocked = 0
provider calls = 0
manifest = tmi-event-corpus-v3
DecisionCase facts = 0
unknown formal terms = 0
```

Verify the three reason states and that both ReRoute events use
`atm:ReRouteTMI`.

- [ ] **Step 3: Verify projection and artifact consistency**

Check:

- every fact ID in `event_facts.jsonl` exists in `facts.jsonl`;
- every event row has one admitted ATMONTO TMI subtype;
- the formal fact-ID sets represented by JSONL, RDF/Turtle, and Neo4j
  projection are equal;
- no context association appears as a formal edge;
- all observation evidence remains source-bound;
- building the same five-event corpus twice is byte-stable.

- [ ] **Step 4: Run one bounded review**

Review only:

- construct validity;
- ATMONTO TMI identity;
- Weather/BTS evidence boundaries;
- old compatibility removal;
- Query Agent always-on behavior;
- public CLI and artifact consistency.

Fix only observed supported-workflow failures. Record production-only security
or concurrency concerns as deferred; do not start another review loop.

- [ ] **Step 5: Run final repository verification once**

Run:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

Expected: all commands pass.

- [ ] **Step 6: Commit any bounded review fixes**

If the review required changes:

```bash
git add -A
git commit -m "fix(agent-system): complete TMI event semantic cutover"
```

If no changes were required, do not create an empty commit.

## Plan Self-Review

- Spec coverage: the plan removes DecisionCase from formal schema, publication,
  corpus identity, integration role, vector retrieval, Query tools, CLI,
  active documents, and figures.
- Construct validity: the plan does not create a renamed isomorphic case
  object; the ATMONTO TMI event is the formal root.
- Evidence boundaries: Weather and BTS rules are explicitly preserved and
  tested.
- Compatibility boundary: v2 corpora, old commands, old tools, and old role
  names are rejected rather than migrated.
- Type consistency: construction uses `EventEvidenceIntegration*`; storage
  uses `CorpusTMIEvent` / `CorpusEventFact`; retrieval uses
  `TMIEventRetrieval*`; query support uses event IDs.
- Scope: no new Agent, data source, causal claim, recommendation, episode, or
  live-model benchmark is included.
- Placeholder scan: no `TBD`, implementation placeholder, or unspecified test
  remains.
