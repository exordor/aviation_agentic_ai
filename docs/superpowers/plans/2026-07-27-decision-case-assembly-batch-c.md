# Decision Case Assembly Agent Batch C Implementation Plan

> **Status:** Planning complete. Implementation in progress. Do not merge or push.

**Goal:** Implement the offline Decision Case Assembly Agent pipeline while preserving all existing ATCSCC, Weather, BTS, provenance, and query semantics. Three real records pass through sealed case-assembly contracts; deterministic cases use zero Assembly provider calls; controlled agent fixtures demonstrate bounded evidence selection and one allowed validation-guided revision; Formal Graph Kernel remains final publication authority.

**Architecture:** The pipeline is:
```text
ATCSCC parsing and authority resolution
  -> validated core-event candidate facts
  -> deterministic Weather/BTS context preparation
  -> deterministic assembly-complexity gate
       -> complete fixed mapping:
          deterministic case compiler
       -> genuine evidence or schema choice:
          Decision Case Assembly Agent
  -> deterministic proposal preflight
       -> valid:
          Formal Graph Kernel
       -> repairable:
          one constrained Assembly revision
       -> hard violation:
          blocked
  -> final validated JSONL/RDF/Neo4j materialization
  -> existing bounded Query Agent
```

**Tech Stack:** Python 3.10+, Pydantic 2, LangChain tools/messages, LangGraph, PyYAML, pytest

---

## Global Constraints

- Work on branch `codex/decision-case-assembly-agent`.
- Do not merge or push.
- No new Agent roles, no new data sources, no new ontology vocabulary, no causal or recommendation claims.
- No real provider calls in tests (scripted stubs / replay only).
- Keep existing contracts in `decision_case_contracts.py` intact unless a test proves a contract defect.
- Formal Graph Kernel remains the final publication gate.

---

## Task Graph & Execution Schedule

### C0: Preflight and Record Plan
- [x] Create branch `codex/decision-case-assembly-agent`.
- [x] Run baseline checks (`uv run ruff check .` and `uv run pytest -q`).
- [x] Write `docs/superpowers/plans/2026-07-27-decision-case-assembly-batch-c.md`.
- [ ] Commit: `docs(agent-system): plan Batch C decision case assembly`.

### C1: Bounded Assembly Tools and Task Builder
- Create `src/aviation_agentic_ai/agent_system/case_assembly_tools.py`.
- Expose candidate/task-bounded read-only tools:
  - `get_case_requirements`
  - `get_schema_context`
  - `get_source_evidence`
  - `get_resolution_result`
  - `get_context_associations`
  - `get_public_observations`
- Add focused tests in `tests/test_agent_system_case_assembly.py`.
- Run RED-GREEN-REFACTOR, review, then commit:
  `feat(agent-system): add bounded case assembly tools`.

### C2: Deterministic Compiler and Preflight Validator
- Implement in `case_assembly_tools.py` or `case_assembly.py`:
  - `build_case_assembly_task(...)`
  - `compile_case_assembly_proposal(...)`
  - `preflight_validate_case_assembly_proposal(...)`
- Test deterministic compilation, repairable validation feedback, hard violations, fail-closed binding checks, and ID stability.
- Run RED-GREEN-REFACTOR, review, then commit:
  `feat(agent-system): add deterministic case assembly preflight`.

### C3: Bounded Decision Case Assembly Agent Loop
- Create `src/aviation_agentic_ai/agent_system/case_assembly.py`.
- Add prompt role `decision_case_assembly` in catalog / YAML.
- Implement model-mediated loop: max 3 provider turns, max 6 read-only tool calls across activation, max 1 tool-selection batch, max 1 validation-guided revision.
- Test scripted scenarios: source-grounded evidence/schema choice success, insufficient/partial status, 1 allowed revision success, hard violation block, out-of-task evidence block, replay stability.
- Run RED-GREEN-REFACTOR, review, then commit:
  `feat(agent-system): implement decision case assembly agent`.

### C4: Workflow Integration & Three-Case Regressions
- Integrate into `src/aviation_agentic_ai/agent_system/workflow.py`, `agents.py`, `kg_tool_graph.py`, `cli_agent_system.py`.
- Preserve existing CLI commands, validated run artifact readers, Query Agent behavior, RDF/Neo4j identities.
- Ensure three approved records (GS 123, GDP 138, GDP 020) compile deterministically with 0 Assembly provider calls.
- Verify semantic preservation: GS123 profile gap reason, GDP138 weather reason & cross-midnight period, GDP020 missing reason.
- Run RED-GREEN-REFACTOR, review, then commit:
  `feat(agent-system): integrate decision case assembly workflow`.

### C5: Documentation Review and Final Verification
- Update `docs/multi_agent_kg_system_design.md` and architecture spec status.
- Update `RESEARCH_AUDIT.md`, `GOALS.md`, `TODO.md`, `README.md`, `AGENTS.md` as needed.
- Run full test suite and validation (`ruff check`, `pytest`, `uv build`, `git diff --check`).
- Review and commit:
  `docs(agent-system): record Batch C assembly gate`.
