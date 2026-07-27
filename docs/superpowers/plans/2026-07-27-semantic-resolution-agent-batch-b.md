# Semantic Resolution Agent Batch B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to implement this plan task by task.
> Every production change follows RED-GREEN-REFACTOR and each task ends in one
> reviewed commit.

**Status:** Offline implementation and repository verification complete. The
bounded live semantic smoke remains pending. Do not merge or push.

**Goal:** Replace the Batch A “ambiguous resolution deferred” outcome with one
shared, bounded Semantic Resolution Agent that can inspect source-bound
facility or terminology evidence, select only a registered eligible candidate,
or abstain. Preserve deterministic zero-model paths for pre-activation blocked,
missing, zero-candidate, and unique-candidate cases.

**Architecture:** Keep the current ingest graph, CLI, Formal Graph Kernel,
artifact readers, and compatibility entrypoints. Add one internal
`semantic_resolution` capability behind the existing facility and terminology
branches. Source-specific authority lookup stays deterministic and separate;
the Agent receives a sealed `ResolutionTask`, selects at most three
candidate-bounded read-only tools in one batch, observes their typed results,
and emits one strict four-field JSON decision. The runtime constructs and
validates the full `ResolutionProposal`. No Agent writes graph facts.

**Tech Stack:** Python 3.10+, Pydantic 2, LangChain tools/messages, LangGraph,
PyYAML, pytest

## Global Constraints

- Work only on `codex/decision-case-semantic-expansion-design`.
- Use English for code, prompts, tests, traces, CLI messages, and active docs.
- Optimize for the architecture and complete pipeline, not production-grade
  polish or exhaustive micro-edge-case coverage.
- Keep public `run_facility_agent` and `run_terminology_agent` signatures
  compatible; compatibility wrappers may delegate to the new Agent.
- Keep the current workflow node topology and all existing CLI commands.
- Do not activate Decision Case Assembly or Decision Case Analysis.
- Do not add ontology terms, graph-write tools, source families, memory,
  planner, critic, retries, or an unrestricted loop.
- Preserve separate NASR facility and FAA terminology authority families.
- Preserve the three Decision Record regressions and all Weather/BTS semantics.
- The Agent may select only an eligible candidate in its sealed task.
- Zero eligible candidates return `insufficient`; one eligible candidate is
  accepted deterministically; only multiple eligible candidates activate the
  model path.
- Enforce at most two provider turns, one batch of at most three read-only
  tools, a 4,096-token rendered-input budget, and a 256-token output cap.
- A failed provider call consumes its budget. Malformed or extra output blocks
  immediately; no parse-repair retry.
- Automated tests use scripted tool-model stubs or replay only. Make no real
  provider call in this batch. The separate bounded live smoke gate remains
  explicitly pending unless the user later authorizes it.
- Commit each task separately. Do not merge or push.

---

## Task 1: Add the Candidate-Bounded Resolution Tool Surface

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/resolution_tools.py`
- Create: `tests/test_agent_system_semantic_resolution.py`
- Modify only if needed:
  `src/aviation_agentic_ai/agent_system/decision_case_contracts.py`

### Required interface

```python
class ResolutionToolGateway:
    def __init__(self, *, task: ResolutionTask) -> None: ...

    def get_resolution_candidates(self) -> ResolutionToolResult: ...
    def get_authority_record(
        self, *, candidate_id: str
    ) -> ResolutionToolResult: ...
    def get_ontology_context(
        self, *, candidate_ids: list[str]
    ) -> ResolutionToolResult: ...
    def check_candidate_constraints(
        self, *, candidate_ids: list[str]
    ) -> ResolutionToolResult: ...
    def compare_candidate_evidence(
        self, *, candidate_ids: list[str]
    ) -> ResolutionToolResult: ...


def build_resolution_tools(
    gateway: ResolutionToolGateway,
) -> list[BaseTool]: ...
```

Tool results must be typed, stably serialized, read-only, and contain only
task-owned candidate, authority-evidence, source, constraint, schema, and
result IDs. Unknown, duplicate, ineligible, cross-task, or source-mismatched
candidate requests fail closed.

### Steps

- [x] Add red tests for the five tool names, closed candidate scope, exact
  authority/source projection, typed constraint/schema observations, and
  stable serialization.
- [x] Observe the focused tests fail before production code is added.
- [x] Implement the minimal gateway and LangChain tool wrappers.
- [x] Re-run the focused suite and Ruff.
- [x] Commit:

```bash
git add src/aviation_agentic_ai/agent_system/resolution_tools.py \
  src/aviation_agentic_ai/agent_system/decision_case_contracts.py \
  tests/test_agent_system_semantic_resolution.py
git commit -m "feat(agent-system): add bounded resolution tools"
```

---

## Task 2: Implement the Bounded Semantic Resolution Loop

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/semantic_resolution.py`
- Modify: `src/aviation_agentic_ai/agent_system/prompts.py`
- Modify: `src/aviation_agentic_ai/agent_system/tool_model.py`
- Modify: `configs/prompts/agent_system_v1.yaml`
- Modify: `tests/test_agent_system_semantic_resolution.py`
- Modify as needed: `tests/test_agent_system_prompt_catalog.py`
- Modify as needed: `tests/test_agent_system_tool_model.py`

### Required interface

```python
@dataclass(frozen=True)
class SemanticResolutionResult:
    proposal: ResolutionProposal
    model_calls: tuple[ModelCallRecord, ...]
    tool_traces: tuple[ToolTraceEntry, ...]
    failure_reason: str | None = None


def run_semantic_resolution_agent(
    *,
    task: ResolutionTask,
    binding: ContractExecutionBinding,
    tool_model_factory: Callable[[list[BaseTool]], ToolCallingModel] | None,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> SemanticResolutionResult: ...
```

Provider-facing final output contains exactly:

```json
{
  "decision": "accepted|abstained",
  "selected_candidate_id": "candidate-id-or-null",
  "rejected_candidate_ids": ["..."],
  "limitation": "string-or-null"
}
```

The first model turn may select one batch of one to three registered tools.
The second and final turn must contain only the strict JSON decision and no
additional tool call. Runtime code derives support claims, source IDs,
proposal ID/checksum, and ordered trace IDs from task-owned observations.

### Steps

- [x] Add red tests for resolvable ambiguity, honest abstention, candidate
  containment, required observed support, strict JSON parsing, no repair retry,
  provider failure, two-provider/three-tool budgets, input budget, 256 output
  cap, and byte-stable scripted replay.
- [x] Observe representative failures.
- [x] Add the frozen `semantic_resolution` prompt with two fictional,
  source-disjoint examples; retain legacy prompt roles during migration.
- [x] Implement the model-tool-model loop and local sealing.
- [x] Re-run focused prompt, tool-model, and semantic-resolution tests.
- [x] Commit:

```bash
git add configs/prompts/agent_system_v1.yaml \
  src/aviation_agentic_ai/agent_system/prompts.py \
  src/aviation_agentic_ai/agent_system/tool_model.py \
  src/aviation_agentic_ai/agent_system/semantic_resolution.py \
  tests/test_agent_system_prompt_catalog.py \
  tests/test_agent_system_tool_model.py \
  tests/test_agent_system_semantic_resolution.py
git commit -m "feat(agent-system): implement semantic resolution agent"
```

---

## Task 3: Route Facility and Terminology Ambiguity Through One Agent

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/agents.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `tests/test_agent_system_runtime_binding.py`
- Modify: `tests/test_agent_system_architecture_compatibility.py`
- Modify: `tests/test_cli_agent_system.py`

### Integration rules

- Extract or reuse the Batch A deterministic task/audit construction.
- Preserve pre-activation `blocked`, `insufficient`, and unique `accepted`
  results without constructing the Semantic Resolution model factory.
- For multiple eligible candidates, call the shared Agent and translate its
  sealed proposal into the existing legacy `AgentResult`,
  `ResolutionDomainOutcome`, authority source registry, and additive model-call
  ledger.
- Add one lazy `semantic_resolution_tool_model_factory` to `IngestContext` and
  CLI ingest wiring. The factory is never touched by deterministic paths.
- Keep the facility and terminology nodes and join unchanged.
- Retain the sealed task/proposal and safe tool trace in the compatibility
  result/state sufficiently for replay and tests; do not create a new graph
  write or public run artifact solely for this batch.

### Steps

- [x] Add red tests proving both domains use the same runtime, unique and
  missing paths make zero model calls, ambiguous resolution and abstention
  propagate correctly, and factory/provider failures become `blocked`.
- [x] Observe focused failures.
- [x] Implement the minimal compatibility wiring.
- [x] Run focused runtime/CLI/architecture tests.
- [x] Commit:

```bash
git add src/aviation_agentic_ai/agent_system/agents.py \
  src/aviation_agentic_ai/agent_system/workflow.py \
  src/aviation_agentic_ai/cli_agent_system.py \
  tests/test_agent_system_runtime_binding.py \
  tests/test_agent_system_architecture_compatibility.py \
  tests/test_cli_agent_system.py
git commit -m "feat(agent-system): route ambiguity through semantic resolver"
```

---

## Task 4: Close the Offline Batch B Gate and Update Active Design

**Files:**

- Modify: `docs/multi_agent_kg_system_design.md`
- Modify: `docs/superpowers/specs/2026-07-27-three-agent-decision-case-architecture-design.md`
- Modify: `docs/superpowers/plans/2026-07-27-semantic-resolution-agent-batch-b.md`
- Modify as needed: `README.md`, `TODO.md`
- Modify tests only for concrete acceptance gaps found during review.

### Acceptance

- The source-grounded resolvable fixture selects the frozen candidate only
  after observing distinguishing source-bound authority content; ontology or
  constraint observations may be supplementary.
- The indistinguishable fixture returns `abstained`.
- Unique, zero-candidate, pre-activation blocked, and pre-activation corrupt
  paths construct no provider. A factory construction failure returns a sealed
  blocked limitation without a provider-attempt record; an invocation failure
  records and consumes the failed provider attempt.
- Facility and terminology authority source families remain separate.
- The sealed task owns registered candidates, authority evidence and sources,
  and the schema checksum. The sealed proposal owns the selected/rejected
  candidate IDs, supporting evidence/source IDs, and content-bound tool-trace
  IDs. Full safe traces remain in compatibility workflow state and validate
  against those proposal-bound IDs.
- Stub/replay output is deterministic.
- Existing three-case semantics, workflow topology, CLI, artifacts, Formal
  Graph Kernel, Weather, and BTS behavior remain unchanged.
- Documentation says Batch B is implemented offline and the bounded live smoke
  is pending; it does not claim that all three new Agents are active.

### Steps

- [x] Run focused Batch B tests:

```bash
uv run pytest -q \
  tests/test_agent_system_semantic_resolution.py \
  tests/test_agent_system_runtime_binding.py \
  tests/test_agent_system_architecture_compatibility.py \
  tests/test_agent_system_prompt_catalog.py \
  tests/test_agent_system_tool_model.py \
  tests/test_cli_agent_system.py
```

- [x] Run repository checks:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

- [x] Request independent specification and code-quality reviews. Fix only
  Critical or Important findings that affect Batch B correctness or pipeline
  integrity.
- [x] Update active documentation to record the completed offline
  implementation and the still-pending live-smoke gate.
- [x] Close the offline verification gate after the required independent review
  and repository checks are confirmed.
- [x] Commit:

```bash
git add docs/multi_agent_kg_system_design.md \
  docs/superpowers/specs/2026-07-27-three-agent-decision-case-architecture-design.md \
  docs/superpowers/plans/2026-07-27-semantic-resolution-agent-batch-b.md
git commit -m "docs(agent-system): record Batch B semantic resolution gate"
```

## Handoff

Return one checkpoint with:

- four task batches plus their focused review-fix commits;
- changed public/internal interfaces;
- deterministic and ambiguous-path model/tool call counts;
- resolvable and abstention fixture outcomes;
- three-case semantic regression status;
- focused/full/Ruff/build/diff results;
- exact remaining blocker: the separately authorized bounded live semantic
  smoke;
- confirmation that no merge or push occurred.
