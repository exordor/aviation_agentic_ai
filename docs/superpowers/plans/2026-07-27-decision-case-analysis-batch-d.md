# Decision Case Analysis Batch D Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a sealed, evidence-bounded Decision Case Analysis Agent for four narrowly registered retrospective question families, while preserving zero-call deterministic answers for the existing scalar, reason, context, and combined-record questions.

**Architecture:** A deterministic router first classifies a registered analysis question and compiles a typed, immutable `QueryPlan` whose steps have a fixed scope and evidence contract. A read-only gateway executes only named plan steps, gathers typed observations, seals `CaseAnalysisTask` and `QueryEvidenceBundle` artifacts, and lets the Decision Case Analysis Agent synthesize only from those observations. The Agent can make at most two model calls and execute at most three plan steps; it cannot read files, query a graph language, add sources, write a graph, or change publication.

**Tech Stack:** Python 3.10+, Pydantic 2, LangChain tools/messages, LangGraph, Click, pytest, Ruff

## Global Constraints

- Advance the user-facing capability: answer bounded retrospective episode, operational-situation, applicability/observed-flight, and future similarity questions from existing validated run artifacts.
- Smallest end-to-end result: one current run can answer the supported operational-situation fixture through a sealed analysis task and immutable evidence bundle; unsupported evidence returns an explicit, source-qualified `insufficient` result.
- Evidence of success: focused scripted tests prove fixed query-plan scope, gateway denial, artifact checksums, exact budgets, zero provider calls on deterministic routes, and the three canonical records' preserved answers.
- Success condition: the Agent's English answer is a projection of `QueryEvidenceBundle` statements and limitations, with every non-limitation claim traceable to retrieved evidence.
- Failure condition: any route permits an unbound step, graph/source write, raw-file access, causal or recommendation language, a flight-control assertion, an invented source/fact, a model call on a deterministic route, or a similarity ranking from the three-record fixture.
- Do not add a source family, ingestion logic, raw source reader, graph/RDF write, Neo4j projection/query/change, ontology vocabulary, UI, compatibility adapter, real provider call, causal explanation, recommendation, live operational support, or flight-control claim.
- Current scalar (`measure`, `controlled facility`, `operational period`, `declared reason`, `provenance`), Weather/BTS context, and combined-record questions remain their current zero-call deterministic routes; do not migrate them into this Agent loop.
- `operational_situation` is the only initially supported Agent fixture. `episode` and `applicability_and_impact` may return `partial`/`insufficient` only with explicit limits. `historical_similarity` is deterministically `insufficient` until a separately approved corpus and profile exist.
- Use only existing current-run artifacts and existing formal/profile-gap/context/public-observation evidence. BTS observations remain public, source-qualified, non-causal observations; they are not FAA demand, AAR, capacity, EDCT, or proof of an individual-flight effect.
- No real provider call in tests or acceptance checks: use a scripted `ToolCallingModel` fixture and inspect call ledgers.
- Batch D intentionally has no old-run/runtime compatibility requirement; regenerate artifacts using current commands when acceptance tests need a run.

---

## File Structure and Dependency Order

| Area | Files | Responsibility |
| --- | --- | --- |
| Plan and gateway | `agent_system/query_plan.py`, `agent_system/case_analysis_tools.py`, `tests/test_agent_system_case_analysis_tools.py` | Immutable typed plans, typed observations, and plan-bound read-only execution. |
| Deterministic readers | `agent_system/query_context_store.py`, `agent_system/query_tools.py`, `tests/test_agent_system_case_analysis_readers.py` | D1/D2 current-run readers that expose only validated episode-timeline and operational-situation evidence. |
| Limits and corpus gate | `agent_system/case_analysis_tools.py`, `agent_system/decision_case_contracts.py`, `tests/test_agent_system_case_analysis_limits.py` | D3/D4 applicability limits, observed-flight insufficiency, and deterministic similarity refusal. |
| Agent runtime | `agent_system/case_analysis.py`, `agent_system/prompts.py`, `configs/prompts/decision_case_agents_v1.yaml`, `tests/test_agent_system_case_analysis.py`, `tests/test_agent_system_prompt_catalog.py` | Bounded tool loop, prompt, sealed task/bundle, and immutable analysis artifacts. |
| Routing and acceptance | `agent_system/query_tool_graph.py`, `agent_system/cli_agent_system.py`, `docs/multi_agent_kg_system_design.md`, `RESEARCH_AUDIT.md`, `GOALS.md`, `TODO.md`, `README.md`, `tests/test_agent_system_query_tool_graph.py`, `tests/test_cli_agent_system.py` | Select analysis only for new registered families; document capability and verify three canonical cases. |

The dependency order is D1 → D2 → D3 → D4 → D5. Do not start a later task until the preceding task's focused tests are green and its review gate accepts the stated scope.

## D1: Typed Bound Query Plans and Read-only Gateway

**Capability:** deterministically turn one registered analysis request into a sealed list of executable, typed steps instead of exposing generic retrieval.

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/query_plan.py`
- Create: `src/aviation_agentic_ai/agent_system/case_analysis_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/decision_case_contracts.py`
- Test: `tests/test_agent_system_case_analysis_tools.py`
- Test: `tests/test_agent_system_decision_case_contracts.py`

**Interfaces:**

```python
class AnalysisIntent(str, Enum):
    EPISODE = "episode"
    OPERATIONAL_SITUATION = "operational_situation"
    APPLICABILITY_AND_IMPACT = "applicability_and_impact"
    HISTORICAL_SIMILARITY = "historical_similarity"

class BoundQueryStep(StrictModel):
    step_id: str
    operation: Literal[
        "read_episode_timeline", "read_operational_situation",
        "read_applicability", "read_observed_flight_outcome",
        "read_similarity_corpus_gate",
    ]
    event_ids: tuple[str, ...]
    required: bool
    allowed_evidence_layers: tuple[str, ...]

class QueryPlan(ChecksummedContract):
    query_plan_id: str
    run_id: str
    question: str
    intent_family: AnalysisIntent
    event_or_case_scope: tuple[str, ...]
    steps: tuple[BoundQueryStep, ...]
    max_steps: Literal[3] = 3

class BoundQueryObservation(StrictModel):
    step_id: str
    status: Literal["ok", "partial", "insufficient", "blocked"]
    fact_ids: tuple[str, ...] = ()
    derivation_ids: tuple[str, ...] = ()
    profile_gap_ids: tuple[str, ...] = ()
    assessment_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    items: tuple[dict[str, Any], ...] = ()
    limitation: str = ""

class BoundQueryGateway:
    def __init__(self, *, plan: QueryPlan, store: QueryGraphStore) -> None: ...
    def execute_bound_query_step(self, *, step_id: str) -> BoundQueryObservation: ...

def compile_query_plan(*, run_dir: Path, question: str, store: QueryGraphStore) -> QueryPlan: ...
```

`QueryPlan` must reject duplicate step IDs, a step whose event IDs are outside `event_or_case_scope`, more than three steps, operations not registered for its intent, and a checksum/ID that does not match its canonical payload. `BoundQueryGateway` must execute each allowed step at most once, reject an absent or exhausted step with `blocked`, and return only IDs/items that came from the current `QueryGraphStore` view. Extend only the existing frozen analysis-contract support where a typed plan checksum or observation trace is required; do not loosen `CaseAnalysisTask`/`QueryEvidenceBundle` invariants.

- [ ] **Step 1: Write the failing plan and gateway tests**

```python
def test_gateway_executes_only_a_declared_step_once(store: QueryGraphStore) -> None:
    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    gateway = BoundQueryGateway(plan=plan, store=store)
    step_id = plan.steps[0].step_id
    assert gateway.execute_bound_query_step(step_id=step_id).status == "ok"
    assert gateway.execute_bound_query_step(step_id=step_id).status == "blocked"
    assert gateway.execute_bound_query_step(step_id="step:not-bound").status == "blocked"
```

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `uv run pytest tests/test_agent_system_case_analysis_tools.py tests/test_agent_system_decision_case_contracts.py -q`

Expected: failure because `QueryPlan`, `BoundQueryGateway`, and plan-bound execution do not yet exist.

- [ ] **Step 3: Implement the minimal immutable plan and gateway**

```python
def execute_bound_query_step(self, *, step_id: str) -> BoundQueryObservation:
    if step_id in self._executed:
        return BoundQueryObservation(step_id=step_id, status="blocked", limitation="bound step already executed")
    step = self._steps_by_id.get(step_id)
    if step is None:
        return BoundQueryObservation(step_id=step_id, status="blocked", limitation="step is not bound by query plan")
    self._executed.add(step_id)
    return _execute_registered_step(step=step, store=self._store)
```

Implement `_execute_registered_step` as a closed dispatch over the five literal operations. It must contain no callback, path, Cypher, SPARQL, URL, or user-provided operation name. Record a sanitized deterministic `QueryToolTrace`/analysis trace only after an observation has been validated.

- [ ] **Step 4: Make the contract proof pass**

Add tests for canonical `query_plan_id`, checksum stability, foreign event scope rejection, duplicate step rejection, one-execution limit, and a gateway result whose cited source IDs are a subset of the store result. Run the focused command again.

Expected: PASS with no model/provider construction.

- [ ] **Step 5: Review and commit the independently usable gateway**

Run: `uv run ruff check src/aviation_agentic_ai/agent_system/query_plan.py src/aviation_agentic_ai/agent_system/case_analysis_tools.py tests/test_agent_system_case_analysis_tools.py && git diff --check`

Commit:

```bash
git add src/aviation_agentic_ai/agent_system/query_plan.py src/aviation_agentic_ai/agent_system/case_analysis_tools.py src/aviation_agentic_ai/agent_system/decision_case_contracts.py tests/test_agent_system_case_analysis_tools.py tests/test_agent_system_decision_case_contracts.py
git commit -m "feat(agent-system): add bound analysis query plans"
```

## D2: D1 Episode Timeline and D2 Operational-Situation Readers

**Capability:** expose narrow current-run evidence projections for one-record episode information and source-qualified operational situation, without inferring lifecycle identity or operational causation.

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/query_context_store.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/case_analysis_tools.py`
- Test: `tests/test_agent_system_case_analysis_readers.py`

**Interfaces:**

```python
def read_episode_timeline(self, *, event_id: str) -> BoundQueryObservation: ...
def read_operational_situation(self, *, event_id: str) -> BoundQueryObservation: ...
```

The episode reader may return the single record's advisory issue, effective start/end, and source-bound event identity only. It must label the result `partial` and say `single-record timeline; no advisory lifecycle grouping evidence` unless explicit source-named episode links already exist in the current run. It must never turn matching facility/time into an episode.

The operational-situation reader is the supported fixture. It may return validated formal event facts, TAF/METAR associations labeled non-causal, and BTS baseline/active/recovery observations labeled public/source-qualified. It must require enough active observations to produce `ok`; otherwise return `insufficient` with the exact missing evidence layer. It must not call a model or use raw advisory/source text.

- [ ] **Step 1: Write reader tests from a current validated three-case fixture**

```python
def test_episode_reader_returns_single_record_partial_without_grouping(store):
    result = read_episode_timeline(store, event_id="event:2026-05-19:138")
    assert result.status == "partial"
    assert "no advisory lifecycle grouping" in result.limitation

def test_operational_situation_preserves_bts_and_weather_roles(store):
    result = read_operational_situation(store, event_id="event:2026-05-19:138")
    assert result.status == "ok"
    assert {item["evidence_role"] for item in result.items} >= {"non_causal_weather_context", "bts_reported_public_observation"}
```

- [ ] **Step 2: Run RED**

Run: `uv run pytest tests/test_agent_system_case_analysis_readers.py -q`

Expected: failure because neither reader nor its evidence-role projection exists.

- [ ] **Step 3: Implement deterministic readers through existing validated store accessors**

Use existing `QueryContextStore` fact, context-association, public-observation, source-snapshot, and fact-trace accessors. Add focused methods rather than a general artifact scan. Every returned item must carry an `evidence_role`, stable IDs, and source IDs. Produce no new formal fact, derivation, source snapshot, or persisted artifact.

- [ ] **Step 4: Add negative boundary tests and run GREEN**

Cover: no lifecycle link ⇒ `partial`; an invalid/no active BTS observation ⇒ `insufficient`; Weather has `causal_claim=false`; BTS cannot be rendered as FAA capacity/demand/EDCT; an unknown event ⇒ `blocked`; and reader execution has no model calls. Run `uv run pytest tests/test_agent_system_case_analysis_readers.py tests/test_agent_system_query_tools.py -q`.

Expected: PASS.

- [ ] **Step 5: Review and commit D1/D2 readers**

Run: `uv run ruff check src/aviation_agentic_ai/agent_system/query_context_store.py src/aviation_agentic_ai/agent_system/query_tools.py src/aviation_agentic_ai/agent_system/case_analysis_tools.py tests/test_agent_system_case_analysis_readers.py && git diff --check`

Commit:

```bash
git add src/aviation_agentic_ai/agent_system/query_context_store.py src/aviation_agentic_ai/agent_system/query_tools.py src/aviation_agentic_ai/agent_system/case_analysis_tools.py tests/test_agent_system_case_analysis_readers.py
git commit -m "feat(agent-system): add bounded case analysis readers"
```

## D3: D3 Applicability/Observed-Flight Limits and D4 Similarity Corpus Gate

**Capability:** make absent applicability and flight-outcome evidence honest, and make similarity impossible to overclaim from the three canonical records.

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/case_analysis_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/decision_case_contracts.py`
- Test: `tests/test_agent_system_case_analysis_limits.py`

**Interfaces:**

```python
def read_applicability(self, *, event_id: str) -> BoundQueryObservation: ...
def read_observed_flight_outcome(self, *, event_id: str) -> BoundQueryObservation: ...
def read_similarity_corpus_gate(self, *, event_ids: tuple[str, ...]) -> BoundQueryObservation: ...
```

`read_applicability` may state only facility and effective-time applicability directly represented by formal event facts. It must return `partial` if no explicit applicability scope beyond those facts exists. `read_observed_flight_outcome` must always return `insufficient` unless a separately admitted current profile provides a source-bound observed-flight fact; BTS aggregate observations must not satisfy it. `read_similarity_corpus_gate` must always return `insufficient` in Batch D with the limitation `historical similarity requires an approved corpus and comparison profile`; it must return no candidate IDs, score, ordering, nearest-neighbor label, or recommendation.

- [ ] **Step 1: Write failing limit and gate tests**

```python
def test_observed_flight_outcome_rejects_aggregate_bts_as_flight_evidence(store):
    result = read_observed_flight_outcome(store, event_id="event:2026-05-19:138")
    assert result.status == "insufficient"
    assert "BTS aggregate observations do not establish an individual-flight outcome" in result.limitation

def test_similarity_gate_never_ranks_three_case_fixture(store):
    result = read_similarity_corpus_gate(store, event_ids=tuple(store.event_ids))
    assert result.status == "insufficient"
    assert result.items == ()
    assert "approved corpus and comparison profile" in result.limitation
```

- [ ] **Step 2: Run RED**

Run: `uv run pytest tests/test_agent_system_case_analysis_limits.py -q`

Expected: failure because applicability/flight/similarity operations are not yet enforced as explicit limits.

- [ ] **Step 3: Implement fixed insufficiency and partial contracts**

Return `BoundQueryObservation` from a closed deterministic implementation. For applicability, retrieve only `atm:controlledNASelement`, `atm:effectiveStartTime`, and `atm:effectiveEndTime`; add a limitation rather than inferring flight/population eligibility. For observed flight and similarity, return no data-bearing items and no model request. Preserve `retrieved_*` ID sets as empty when no support exists.

- [ ] **Step 4: Verify fail-closed behavior**

Add tests for: unknown event blocks; a profile gap cannot become flight evidence; a request containing `recommend`, `best`, or `similar` cannot bypass the corpus gate; no source or graph mutation occurs; and no `QueryEvidenceBundle` can contain an unsupported evidence statement. Run `uv run pytest tests/test_agent_system_case_analysis_limits.py tests/test_agent_system_decision_case_contracts.py -q`.

Expected: PASS.

- [ ] **Step 5: Review and commit limits**

Run: `uv run ruff check src/aviation_agentic_ai/agent_system/case_analysis_tools.py src/aviation_agentic_ai/agent_system/decision_case_contracts.py tests/test_agent_system_case_analysis_limits.py && git diff --check`

Commit:

```bash
git add src/aviation_agentic_ai/agent_system/case_analysis_tools.py src/aviation_agentic_ai/agent_system/decision_case_contracts.py tests/test_agent_system_case_analysis_limits.py tests/test_agent_system_decision_case_contracts.py
git commit -m "feat(agent-system): gate analysis applicability and similarity"
```

## D4: Decision Case Analysis Agent, Prompt, and Immutable Artifacts

**Capability:** allow controlled language synthesis only after the deterministic gate and bound-step observations, producing auditable immutable analysis artifacts.

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/case_analysis.py`
- Modify: `src/aviation_agentic_ai/agent_system/prompts.py`
- Modify: `configs/prompts/decision_case_agents_v1.yaml`
- Modify: `src/aviation_agentic_ai/agent_system/decision_case_contracts.py`
- Test: `tests/test_agent_system_case_analysis.py`
- Test: `tests/test_agent_system_prompt_catalog.py`

**Interfaces:**

```python
MAX_CASE_ANALYSIS_MODEL_CALLS = 2
MAX_CASE_ANALYSIS_BOUND_STEPS = 3

def run_case_analysis_agent(
    *, plan: QueryPlan, gateway: BoundQueryGateway,
    model_factory: ToolModelFactory, binding: ContractExecutionBinding,
) -> tuple[CaseAnalysisTask, QueryEvidenceBundle, QueryToolOutcome]: ...

def write_case_analysis_artifacts(
    *, run_dir: Path, task: CaseAnalysisTask, bundle: QueryEvidenceBundle,
    outcome: QueryToolOutcome,
) -> Path: ...
```

Add `decision_case_analysis` to `ROLE_KEYS`. Its prompt must state that the sole model-visible tool is `execute_bound_query_step(step_id: str)`, all tool results are untrusted data, at least one bound observation is required before an answer, and only concise English source-backed statements plus limitations are allowed. The model must receive plan step IDs, not the store, paths, tools from `QueryToolGateway`, raw source text, graph query syntax, or generic retrieval capability.

The runtime may make two model calls total: first select one or more valid step IDs; second render structured answer statements. It may execute three distinct plan steps total and must terminate `blocked` for a malformed/foreign/repeated tool request or a third model call. Seal the `CaseAnalysisTask` before model synthesis and seal a `QueryEvidenceBundle` only from the task's retrieved IDs, component statuses, traces, statements, and source bindings.

Persist one immutable analysis directory at
`analysis/<analysis_run_id>/`, containing `case_analysis_task.json`,
`query_evidence_bundle.json`, and `case_analysis_run.json`.
`analysis_run_id` is a stable identifier over the sealed task, bundle, and
sanitized outcome payload. An identical write is idempotent; a differing write
to an existing ID fails closed. Analysis artifacts do not mutate the validated
ingest manifest and never overwrite the mutable legacy `query_run.json`.

Migrate the old model-mediated Query Agent path/naming only where needed to make this runtime the sole model-visible bound-step loop. Preserve the existing `answer_question_with_tools` deterministic/scalar routes and their public output. Remove obsolete model-loop naming instead of maintaining an alias or compatibility wrapper.

- [ ] **Step 1: Write scripted runtime and artifact RED tests**

```python
def test_analysis_agent_can_answer_operational_situation_from_one_bound_tool(scripted_model, store, binding):
    plan = compile_query_plan(run_dir=store.run_dir, question="What public operational situation is recorded?", store=store)
    task, bundle, outcome = run_case_analysis_agent(
        plan=plan, gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=scripted_model, binding=binding,
    )
    assert outcome.status == "ok"
    assert len(outcome.model_calls) <= 2
    assert len(bundle.executed_step_ids) <= 3
    assert bundle.task_id == task.task_id
```

- [ ] **Step 2: Run RED**

Run: `uv run pytest tests/test_agent_system_case_analysis.py tests/test_agent_system_prompt_catalog.py -q`

Expected: failure because there is no active analysis role, runtime, artifact writer, or bound-only model tool.

- [ ] **Step 3: Implement the closed two-turn runtime and frozen prompt**

Implement a small explicit state machine: `plan -> select_steps -> execute_steps -> synthesize -> seal -> persist`. Do not use a planner, memory, retry loop, validation-guided revision, or general LangGraph tool node. Decode only `ModelToolCall(name="execute_bound_query_step")`; validate arguments against `plan.steps`; carry the deterministic observation results into synthesis; then parse a strict statement format into `AnswerStatement` values. An `AGENT_SYNTHESIS` statement must cite earlier supported statements exactly as required by the existing contract.

- [ ] **Step 4: Prove budgets, immutability, and boundaries**

Add tests for: successful scripted operational situation; one model turn then insufficient evidence; foreign/malformed/repeated tool call blocks; third tool step blocks; third model call blocks; model cannot see any other tool name; artifact checksum round-trip; differing rewrite rejection; explicit episode partial; observed-flight insufficiency; similarity insufficiency; and no raw response stores hidden reasoning. Run the focused test command again.

Expected: PASS with scripted providers only.

- [ ] **Step 5: Review and commit the Agent runtime**

Run: `uv run ruff check src/aviation_agentic_ai/agent_system/case_analysis.py src/aviation_agentic_ai/agent_system/prompts.py src/aviation_agentic_ai/agent_system/decision_case_contracts.py tests/test_agent_system_case_analysis.py tests/test_agent_system_prompt_catalog.py && git diff --check`

Commit:

```bash
git add src/aviation_agentic_ai/agent_system/case_analysis.py src/aviation_agentic_ai/agent_system/prompts.py configs/prompts/decision_case_agents_v1.yaml src/aviation_agentic_ai/agent_system/decision_case_contracts.py tests/test_agent_system_case_analysis.py tests/test_agent_system_prompt_catalog.py
git commit -m "feat(agent-system): add bounded decision case analysis agent"
```

## D5: Router, CLI, Three-Case Acceptance, and Current Documentation

**Capability:** make the new analysis family reachable through the existing `ask` command while preserving the established user-facing routes and accurately documenting the narrow capability.

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/query_tool_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_tools.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `docs/multi_agent_kg_system_design.md`
- Modify: `RESEARCH_AUDIT.md`
- Modify: `GOALS.md`
- Modify: `TODO.md`
- Modify: `README.md`
- Test: `tests/test_agent_system_query_tool_graph.py`
- Test: `tests/test_cli_agent_system.py`

**Interfaces:**

```python
def classify_registered_question(question: str) -> QueryIntent | AnalysisIntent | None: ...
def answer_question_with_tools(*, run_dir: Path, question: str, model_factory: ToolModelFactory) -> QueryToolOutcome: ...
```

Route exact registered analysis phrasings to `compile_query_plan` and `run_case_analysis_agent`. The capability gate must reject non-English, non-registered, recommendation, causal, live-operational, generic similarity, and flight-control questions before a model factory is invoked. Keep all existing scalar/context/combined intents on their deterministic paths with `model_calls == []`; do not rename their CLI question behavior or persist analysis artifacts for them. The CLI's current `--allow-live-model` authorization applies only to an actual analysis Agent route; tests must use injected scripted models and no command may make a real provider call.

- [ ] **Step 1: Write router and CLI acceptance tests**

```python
def test_existing_combined_and_scalar_questions_remain_zero_call(run_dir, forbidden_model):
    for question in (
        REGISTERED_COMPETENCY_QUESTION, MEASURE_QUESTION,
        DECLARED_REASON_QUESTION, PUBLIC_OUTCOME_QUESTION,
    ):
        outcome = answer_question_with_tools(run_dir=run_dir, question=question, model_factory=forbidden_model)
        assert outcome.model_calls == []

def test_similarity_question_is_insufficient_without_provider(run_dir, forbidden_model):
    outcome = answer_question_with_tools(run_dir=run_dir, question="Which historical case is most similar?", model_factory=forbidden_model)
    assert outcome.status == "insufficient"
    assert outcome.model_calls == []
```

- [ ] **Step 2: Run RED**

Run: `uv run pytest tests/test_agent_system_query_tool_graph.py tests/test_cli_agent_system.py -q`

Expected: failure because analysis family routing, explicit similarity refusal, and preserved zero-call regressions are not fully specified in the current router.

- [ ] **Step 3: Implement routing and narrow CLI reporting**

Add only the new registered question constants/intents needed for the four analysis families. Have `ask` print existing outcome fields plus analysis artifact paths only when an analysis route wrote them. Do not add CLI commands, options, input formats, provider configuration, Neo4j changes, compatibility shims, or UI output. Ensure a deterministic insufficient route returns normally with its explicit limitation rather than prompting a provider.

- [ ] **Step 4: Run three-case and documentation acceptance checks**

Regenerate/test current fixtures for GS `123`, GDP `138`, and cancellation `020`. Assert: GS `123` retains its reason profile gap; GDP `138` retains `weather`, its cross-midnight operational period, non-causal Weather context, and BTS source roles; GDP `020` retains missing/insufficient reason. Add a `git grep` scope test or documented review that finds no claims of cause, recommendation, flight control, full-corpus similarity, Neo4j work, or compatibility guarantee in the new current documentation.

Run:

```bash
uv run pytest tests/test_agent_system_case_analysis.py tests/test_agent_system_case_analysis_tools.py tests/test_agent_system_case_analysis_readers.py tests/test_agent_system_case_analysis_limits.py tests/test_agent_system_query_tool_graph.py tests/test_cli_agent_system.py -q
uv run ruff check .
uv run pytest -q
git diff --check
```

Expected: all checks pass; no real provider is called; existing deterministic questions show zero model calls.

- [ ] **Step 5: Review documentation and commit the complete increment**

Update current docs to call the Agent active only for the registered bounded analysis families, name operational situation as the supported fixture, and preserve episode/applicability/similarity limitations. Do not rewrite historical plans.

Commit:

```bash
git add src/aviation_agentic_ai/agent_system/query_tool_graph.py src/aviation_agentic_ai/agent_system/query_tools.py src/aviation_agentic_ai/cli_agent_system.py docs/multi_agent_kg_system_design.md RESEARCH_AUDIT.md GOALS.md TODO.md README.md tests/test_agent_system_query_tool_graph.py tests/test_cli_agent_system.py
git commit -m "feat(agent-system): route bounded decision case analysis"
```

## Final Review Checklist

- [ ] Each of D1-D5 has focused RED → GREEN evidence, Ruff, `git diff --check`, and a reviewable commit.
- [ ] `QueryPlan` and every executed observation are typed, checksummed/bound where persisted, and current-run scoped.
- [ ] Only `execute_bound_query_step` is model-visible; it accepts a plan step ID and has no path/query/source/write parameter.
- [ ] The Agent makes at most two model calls and executes at most three distinct steps; malformed and out-of-plan calls fail closed.
- [ ] Existing scalar/context/combined paths require no provider construction and retain their current answer semantics.
- [ ] Episode output never groups lifecycle records from time/facility similarity; applicability never becomes flight impact; BTS aggregates never become individual-flight evidence.
- [ ] Similarity produces no ranking, neighbor, score, or recommendation until an approved corpus and comparison profile exist.
- [ ] No source, ingestion, RDF, graph, Neo4j, causal, recommendation, flight-control, UI, compatibility, or real-provider scope leaked into the change.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-27-decision-case-analysis-batch-d.md`. Two execution options:

1. Subagent-Driven (recommended) - dispatch a fresh subagent per task and review between tasks.

2. Inline Execution - execute the tasks in this session with checkpoints for review.
