# Agent Capability Drift Correction Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task by task. Use `superpowers:test-driven-development` for behavior changes.

**Goal:** Remove one model-backed role that cannot add evidence, make the existing graph query expose real cross-source evidence paths, and reset interfaces and evaluation language so the project demonstrates positive Agent/KG capability without returning to GDP-specific logic.

**Architecture:** Keep the ATMONTO-aligned TMI event corpus, deterministic source preparation, source-role separation, Formal Publication Kernel, and always-on natural-language Query Agent. Replace the impossible Event Evidence Integration Agent branch with its existing deterministic evidence-integration compiler. Extend the existing event-scoped graph view—not the corpus schema—with derived Weather and BTS evidence paths. Keep metadata-conditioned vector recall, but name it honestly. Treat current hand-selected records as development or regression fixtures, not as a frozen benchmark.

**Tech Stack:** Python 3.12, Pydantic, LangChain tool interfaces, JSONL corpus v2, RDF/Neo4j rebuildable exports, Chroma, pytest, Ruff, Draw.io.

---

## 1. Scope Decision

### Capability advanced

The user can ask a free natural-language question whose Query Agent may retrieve a structured path connecting:

```text
TMI event
  -> controlled airport
  <- weather report associated in time
```

or:

```text
TMI event
  -> controlled airport
  <- public BTS observation
```

The returned path remains evidence-bound and explicitly non-causal where the corpus only stores an association.

### Smallest end-to-end result

For one event containing admitted TMI, Weather, and BTS records:

1. `read_tmi_event_graph(view="evidence_paths")` returns stable path objects.
2. Each path retains its formal fact IDs, association/observation IDs, and source IDs.
3. The model-visible tool observation includes those paths.
4. A Query Agent statement may cite the path only through the correct source-role support record.
5. A small real-provider smoke confirms the configured model can select and use the path view.

### What remains authoritative

- ATCSCC text remains the only source of an official declared TMI reason.
- Weather context remains a time-bounded non-causal association.
- BTS remains a public operational observation, not FAA demand, capacity, rationale, or effectiveness.
- The Formal Publication Kernel remains the only final publication authority.
- Corpus v2 remains canonical; graph paths are read-time derived views.

### Explicitly deferred

- Decision episodes and advisory lifecycle reconstruction.
- New PDF/document, flight-track, sector, or trajectory data.
- Causal explanation, TMI recommendation, operational effectiveness, or optimality.
- Weather/outcome-aware similarity and community detection.
- A new Agent role, general planner, Agent-to-Agent chat, or production framework.
- A new frozen benchmark or claims of model quality.
- F1/F3S/S4/S1S competency questions until their missing flight/sector data exists.

---

## 2. Findings Selected From the Drift Assessment

### Adopt now

1. **Remove an ornamental Agent role.** The Event Evidence Integration Agent is activated only when required evidence slots are missing, but its closed bundle cannot create the missing evidence. Complete bundles bypass it. It therefore has no supported positive path.
2. **Make graph retrieval perform a graph-specific task.** The existing runtime graph tool returns flat event-scoped edges even though graph-path contracts already exist.
3. **Stop overstating metadata recall.** The current embedding encodes event type, facility, reason state, and coarse time/duration—not operational-state or outcome similarity.
4. **Separate development, regression, and future evaluation.** The five familiar records are useful fixtures but are not a representative benchmark.
5. **Remove the hidden NYC selection default.** Corpus construction must explicitly choose `cohort` or `all`.
6. **Require positive capability in mainline batches.** A validator-only batch is justified only by a reproduced supported-path failure or an explicit user request.

### Already corrected; do not rework

- Public `ask` already accepts free natural-language questions and always invokes the Query Agent.
- The canonical root is now a TMI event aligned to ATMONTO, not a synthetic DecisionCase.
- RDF and Neo4j are rebuildable exports, not competing sources of truth.
- The five records are already described as regression fixtures in the main design.

### Reject

- Do not weaken provenance, profile gaps, honest `insufficient`, or claim boundaries merely to make answers more assertive.
- Do not make every deterministic parser an Agent.
- Do not add causal edges between Weather/BTS and TMI decisions.
- Do not replace current bounded tools with an unconstrained monolithic Agent.

---

## 3. Batch G1 — Deterministic Event Evidence Integration

### Files

**Modify:**

- `src/aviation_agentic_ai/agent_system/workflow.py`
- `src/aviation_agentic_ai/agent_system/event_evidence_integration_tools.py`
- `src/aviation_agentic_ai/agent_system/agent_usage.py`
- `src/aviation_agentic_ai/agent_system/corpus_batch.py`
- `src/aviation_agentic_ai/agent_system/prompts.py`
- `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- `tests/test_agent_system_current_architecture.py`
- `tests/test_agent_system_multisource_context.py`
- `tests/test_agent_system_reroute.py`
- `tests/test_agent_system_event_evidence_integration.py`
- `tests/test_agent_system_runtime_binding.py`
- `tests/test_agent_system_agent_usage.py`
- `tests/test_agent_system_corpus_batch.py`
- `tests/test_agent_system_prompt_catalog.py`

**Delete after callers are removed:**

- `src/aviation_agentic_ai/agent_system/event_evidence_integration.py`
- the `event_evidence_integration` role in `configs/agent_system_prompts_v1.yaml`
- Agent-only gateway/tool-selection tests and parser tests that no longer represent a supported workflow.

### Behavior

- Preserve the deterministic `EventEvidenceIntegrationTask`, proposal compiler, validation, and Formal Publication path.
- Retain `EventEvidenceIntegrationResult` only as a small deterministic
  workflow result contract in `event_evidence_integration.py`; remove its model,
  prompt, tool-loop, trace-construction, and retry implementation. Existing
  state and context-artifact readers may continue to consume its sealed
  proposal without fabricating Agent telemetry.
- Rename the workflow node to `integrate_event_evidence`.
- Remove the event-integration model factory, activation predicate, model calls, tool traces, prompt role, and provider configuration.
- The integration stage always compiles from the sealed admitted evidence bundle.
- Missing required evidence remains `insufficient`; malformed admitted evidence remains `blocked`.
- Agent usage contains only actual semantic-resolution roles. It does not manufacture a deterministic-bypass row for a component that is no longer an Agent.

### TDD sequence

1. Change workflow and usage tests first so they require no event-integration model factory or Agent usage row.
2. Run the focused tests and observe failure against the current model-backed branch.
3. Replace the workflow branch with the deterministic compiler.
4. Remove the dead Agent implementation, prompt, and Agent-only tests.
5. Run:

```bash
uv run pytest -q \
  tests/test_agent_system_event_evidence_integration.py \
  tests/test_agent_system_runtime_binding.py \
  tests/test_agent_system_agent_usage.py \
  tests/test_agent_system_corpus_batch.py \
  tests/test_agent_system_prompt_catalog.py
```

### Acceptance

- The five regression fixtures retain their event type, facility, time, and reason states.
- Eligible records never invoke an Event Evidence Integration provider.
- Corpus output and formal facts do not change solely because the model branch was removed.
- Semantic Resolution remains selectively model-backed only for genuine facility or terminology ambiguity.

### Commit

```text
refactor(agent-system): make event evidence integration deterministic
```

---

## 4. Batch G2 — Cross-Source Event Evidence Paths

### Files

**Modify:**

- `src/aviation_agentic_ai/agent_system/corpus_event_graph.py`
- `src/aviation_agentic_ai/agent_system/corpus_store.py`
- `src/aviation_agentic_ai/agent_system/contracts.py`
- `src/aviation_agentic_ai/agent_system/hybrid_query_tools.py`
- `src/aviation_agentic_ai/agent_system/hybrid_query_agent.py`
- `tests/test_agent_system_corpus_event_graph.py`
- `tests/test_agent_system_corpus_store.py`
- `tests/test_agent_system_hybrid_query_tools.py`
- `tests/test_agent_system_hybrid_query_agent.py`

### Public/internal interface

Extend the existing tool without adding a seventh tool:

```python
class TMIEventGraphInput:
    event_id: str
    view: Literal["edges", "evidence_paths"] = "edges"
    entity_iri: str | None
    direction: Literal["out", "in"]
    predicate_iris: tuple[str, ...]
    limit: int
```

Add one corpus read method:

```python
CorpusQueryStore.get_event_evidence_paths(
    event_id: str,
) -> tuple[CorpusEventEvidencePath, ...]
```

Each derived row contains:

```text
QueryGraphPath
support kind
formal fact IDs
context association IDs
observation IDs
source IDs
```

Define a small `CorpusEventEvidencePath` wrapper in the read-side query layer:

```text
path: QueryGraphPath
support_kind: non_causal_context | public_observation
fact_ids
context_association_ids
observation_ids
source_ids
```

`QueryGraphPath` remains the model-facing path shape. The wrapper carries the
extra corpus bindings needed to build one `HybridQuerySupportRecord` that binds
the path ID and its association/observation, fact, and source IDs together.

Implementation note: the wrapper remains local to `hybrid_query_tools.py`
because it is a read-time binding and is not part of the canonical corpus or
formal graph schema.

### Path construction

Weather path:

```text
TMI --atm:controlledNASelement--> Airport
WeatherReport --data:forecastingAirport--> Airport
```

Admit the path only when a matching `CorpusContextAssociation` binds the same event, report, and facility. Its support kind is `non_causal_context`.

BTS path:

```text
TMI --atm:controlledNASelement--> Airport
Observation --sosa:hasFeatureOfInterest--> Airport
```

Admit the path only when the observation edge is among the formal fact IDs bound to the same `CorpusObservation`. Its support kind is `public_observation`.

### TDD sequence

1. Add failing store tests for stable, event-scoped Weather and BTS paths.
2. Add negative tests: no association means no Weather path; a foreign event or unbound observation never joins.
3. Add failing tool tests for `view="evidence_paths"`, exact IDs, stable ordering, and support records.
4. Add a failing Query Agent test proving `graph_paths` appears in the model-visible observation and in the final `QueryEvidenceBundle`.
5. Implement the store join and tool view.
6. Run:

```bash
uv run pytest -q \
  tests/test_agent_system_corpus_event_graph.py \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_hybrid_query_tools.py \
  tests/test_agent_system_hybrid_query_agent.py
```

### Acceptance

- Paths are derived at read time; corpus identity and manifest do not change.
- Path IDs and ordering are byte-stable for the same corpus.
- Weather paths preserve `causal_claim=false`.
- Every path is event-scoped and source-bound.
- The Query Agent can see and cite graph paths; unrelated sources are rejected by existing support validation.

### Commit

```text
feat(agent-system): expose cross-source event evidence paths
```

---

## 5. Batch G3 — Honest Interfaces and Evaluation Reset

### Files

**Modify:**

- `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_search.py`
- `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_evaluation.py`
- `src/aviation_agentic_ai/agent_system/hybrid_query_tools.py`
- `src/aviation_agentic_ai/agent_system/corpus_batch.py`
- `src/aviation_agentic_ai/agent_system/live_agent_evaluation.py`
- `src/aviation_agentic_ai/agent_system/live_agent_experiment.py`
- `src/aviation_agentic_ai/cli_agent_system.py`
- relevant retrieval, CLI, live-evaluation, and live-experiment tests
- `data/evaluation/agent_system/live_agent_smoke_v4.yaml`
- `data/evaluation/agent_system/live_agent_experiment_v4.yaml`

### Breaking interface corrections

- Rename `find_similar_tmi_events` to `rank_tmi_events_by_metadata`.
- Keep exactly six Query Agent tools; do not retain the old tool alias.
- Require `--selection cohort|all` for `build-corpus`; remove the default.
- Remove the internal `build_corpus_batch(selection="cohort")` default as well;
  every caller and test must choose explicitly.
- Update error/help text from “similar cases” to “metadata-conditioned event ranking.”
- Keep the internal mathematical/support kind name `similarity` in the typed
  result contract. This batch corrects the public tool/API wording; it does not
  rename the established score/support primitive.

### Evaluation partitions

```text
development
  synthetic contract cases
  2026-05-20:025, :030, :070, :072
  GDP 138

regression
  five TMI semantic fixtures
  graph-path and retrieval smoke fixtures

future_frozen_evaluation
  NOT CONSTRUCTED
```

- Retire the four Event Evidence Integration trials from the active v4 live suite.
- Create a small query-only `live_smoke` covering exact facts and cross-source graph paths with non-regression eligible records.
- Keep the repeated real-provider runner available, but make its v4 suite query-only and label repeated cycles as repeated measurements.
- Do not claim model quality, representative coverage, or frozen benchmark performance.

### Tests

```bash
uv run pytest -q \
  tests/test_agent_system_tmi_event_retrieval_search.py \
  tests/test_agent_system_hybrid_query_tools.py \
  tests/test_agent_system_live_evaluation.py \
  tests/test_agent_system_live_experiment.py \
  tests/test_cli_agent_system.py
```

### Acceptance

- No active user-facing tool name, help text, or prompt description calls
  metadata-only retrieval “similar TMI events.” Internal score/support fields
  may continue to use the established `similarity` primitive.
- `build-corpus` without `--selection` fails with a clear CLI usage error.
- Active live suites contain only behaviors that exist in the current architecture.
- Historical v1–v3 reports remain immutable historical evidence and are not relabeled.

### Commit

```text
refactor(agent-system): reset retrieval and evaluation interfaces
```

---

## 6. Batch G4 — Documentation and Architecture Figures

### Files

**Modify:**

- `AGENTS.md`
- `README.md`
- `GOALS.md`
- `TODO.md`
- `RESEARCH_AUDIT.md`
- `REPRODUCIBILITY.md`
- `ARTIFACT_INDEX.md`
- `docs/multi_agent_kg_system_design.md`
- `docs/figures/tmi_event_construction_architecture.drawio`
- `docs/figures/tmi_event_construction_architecture.png`
- `docs/figures/tmi_event_retrieval_architecture.drawio`
- `docs/figures/tmi_event_retrieval_architecture.png`

### Documentation corrections

- Describe active model-backed roles as:
  - Query Agent: always activated for valid public questions.
  - Semantic Resolution Agent: selectively activated only for genuine authority ambiguity.
- Describe event evidence integration as a deterministic service, not an Agent.
- Show `TMI Event Corpus -> event-scoped graph view -> cross-source evidence paths -> Query Agent`.
- Label Chroma as a metadata-conditioned event index.
- Label the five fixtures as regression/development artifacts only.
- State that no frozen evaluation set currently exists.
- Add the project rule:

```text
Every mainline implementation batch must add or simplify a user-visible
capability. A validator-only batch requires a reproduced failure through a
supported workflow or an explicit user request.
```

### Figure constraints

- Preserve the existing two-figure split.
- Use one main direction and no crossing connectors.
- Keep each box to a title and at most two short subtitle lines.
- Minimum 26 px type.
- Update both editable `.drawio` and PNG previews.
- Visually inspect both PNG files for clipping, overlap, and connector crossings.

### Commit

```text
docs(agent-system): document capability-centered architecture
```

---

## 7. Verification

### Offline software verification

Run focused tests during each batch. At the end, run once:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

### Real-provider compatibility smoke

After all offline checks pass, run one query-only `live_smoke` using the configured DeepSeek provider, `temperature=0`, current prompt version, no fake fallback, and no cached response substitute.

The smoke is accepted only if:

- every trial records a real provider call;
- at least one trial invokes `read_tmi_event_graph` with `view="evidence_paths"`;
- the final answer cites the returned path/source bindings;
- Weather remains non-causal and BTS remains a public observation;
- provider-call success and task acceptance are reported separately;
- raw and parsed artifact locations and checksums are reported.

If credentials, input data, or provider compatibility prevent the calls, report the smoke as `NOT EXECUTED`; do not substitute an offline result.

### Final review

Use one bounded review pass only:

1. Inspect the final diff for accidental loss of evidence boundaries or public commands.
2. Fix only concrete issues reproduced by supported tests or workflows.
3. Re-run affected focused tests and the final verification once.
4. Stop; record production-only residual risks as deferred.

---

## 8. Overall Success and Failure Conditions

### Success

- The active runtime has no Event Evidence Integration Agent or associated provider call.
- Event evidence integration and final publication continue deterministically.
- The Query Agent can retrieve and cite real cross-source graph paths.
- Metadata ranking and corpus selection interfaces are explicit and honest.
- Development/regression artifacts are not presented as a frozen benchmark.
- The two architecture figures match the implementation.
- Focused tests, full tests, Ruff, package build, diff check, and the real query smoke pass.

### Failure

- Removing the Agent changes the five regression fixtures' formal facts or reason states.
- Cross-source paths are created without matching corpus bindings.
- Weather/BTS is used to fill an official reason or imply causality/effectiveness.
- A legacy fixed-question registry or deterministic public answer path is reintroduced.
- A live result is reported from a fake, replayed, or cached substitute.
- The batch expands into new sources, new Agents, production hardening, or an invented benchmark.
