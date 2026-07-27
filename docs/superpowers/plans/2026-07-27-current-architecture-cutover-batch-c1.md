# Batch C.1 Current Architecture Cutover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the legacy five-role and historical-artifact compatibility surfaces so the active research prototype exposes only its current authority-resolution, Decision Case Assembly, formal publication, and bounded query pipeline.

**Architecture:** Facility and terminology handling become deterministic authority-domain services that invoke the shared Semantic Resolution Agent only for genuine ambiguity. Decision Case Assembly publishes a `GraphPatchBlock` directly to the Formal Graph Kernel without a legacy Knowledge Graph Construction `AgentResult`. New runs use one versioned, profile-owned artifact contract; old run directories are intentionally unsupported and may be regenerated from the three canonical source records.

**Tech Stack:** Python 3.12, Pydantic, LangGraph, LangChain tool models, JSONL, RDFLib, Neo4j projection, pytest, Ruff, uv.

## Global Constraints

- This is an intentional breaking cutover. Do not retain aliases, dual readers, migration scripts, deprecated wrappers, or compatibility-only tests.
- Preserve the current user-facing CLI commands `ingest`, `neo4j-export`, and `ask`; their internal Python APIs and artifact schemas may break.
- Keep all active code, contracts, prompts, CLI messages, tests, artifacts, and documentation in English.
- Make no real provider calls. The three canonical cases must remain deterministic zero-call paths.
- Do not add an Agent role, data source, ontology term, planner, critic, memory layer, recommendation, or causal claim.
- Facility and terminology candidate generation, authority evidence, exact source binding, and deterministic zero/one-candidate decisions remain separate domain capabilities.
- Preserve `source_snapshots.jsonl`, fact traces, profile gaps, Weather associations, BTS summaries, observation derivations, reconstruction traces, validation-profile ownership, and explicit `ok | insufficient | blocked` layer states.
- Weather/BTS records cannot become the declared reason or a causal fact. Ground Stop `123` remains a source-bound Profile Gap, GDP `138` retains formal `weather`, and GDP cancellation `020` retains a missing reason.
- Do not rename the shared `EvidenceCard.agent_role` audit field or modify reporting modules outside `agent_system`; current producers may retain source-domain labels there without presenting those labels as active Agent roles.
- Do not modify archived reporting pipelines, ignored run directories, visualization work, or historical experiment evidence.
- Work on `codex/decision-case-assembly-agent`; do not merge or push.

---

### Task 1: Replace Facility and Terminology Agent Compatibility with Authority Services

**Files:**
- Create: `src/aviation_agentic_ai/agent_system/authority_resolution.py`
- Modify: `src/aviation_agentic_ai/agent_system/agents.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `tests/test_agent_system_runtime_binding.py`
- Modify: `tests/test_agent_system_structural_context.py`
- Modify: `tests/test_agent_system_graph_kernel.py`
- Delete/replace: `tests/test_agent_system_architecture_compatibility.py`
- Create: `tests/test_agent_system_current_architecture.py`

**Interfaces:**
- Produces:

  ```python
  @dataclass(frozen=True)
  class AuthorityResolutionResult:
      evidence_card: EvidenceCard
      domain_outcome: ResolutionDomainOutcome
      authority_source_records: tuple[SourceRecord, ...]
      resolution_task: ResolutionTask
      resolution_proposal: ResolutionProposal
      resolution_tool_traces: tuple[ToolTraceEntry, ...] = ()
      model_calls: tuple[ModelCallRecord, ...] = ()

  def resolve_facility_authority(
      *,
      task: AgentTask,
      request: FacilityAuthorityResolutionInput,
      semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
  ) -> AuthorityResolutionResult: ...

  def resolve_terminology_authority(
      *,
      task: AgentTask,
      request: TerminologyAuthorityResolutionInput,
      semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
  ) -> AuthorityResolutionResult: ...
  ```

- The authority tool version is exactly `authority-resolution-v1`.
- `AuthorityResolutionResult` carries the source-bound evidence directly; it does not contain a legacy `AgentResult`.
- Workflow state keys become `facility_authority_result` and `terminology_authority_result`.
- Workflow node names become `facility_authority` and `terminology_authority`.
- Remove `CompatibilityResolutionResult`, `_compatibility_requested`, every `_resolve_*_compatibility` function, `run_facility_agent`, and `run_terminology_agent`.

- [ ] **Step 1: Write current-architecture authority tests**

  Add behavior tests that exercise the real workflow/services:

  ```python
  def test_unique_authority_candidates_resolve_without_semantic_model():
      factory = FailingFactory()
      facility = resolve_facility_authority(
          task=facility_task,
          request=unique_facility_request,
          semantic_resolution_tool_model_factory=factory,
      )
      terminology = resolve_terminology_authority(
          task=term_task,
          request=unique_term_request,
          semantic_resolution_tool_model_factory=factory,
      )
      assert facility.domain_outcome.decision is ResolutionDecision.ACCEPTED
      assert terminology.domain_outcome.decision is ResolutionDecision.ACCEPTED
      assert factory.calls == 0


  def test_multiple_eligible_candidates_use_only_shared_semantic_resolution():
      result = resolve_terminology_authority(
          task=term_task,
          request=ambiguous_term_request,
          semantic_resolution_tool_model_factory=scripted_factory,
      )
      assert result.resolution_proposal.decision in {
          ResolutionDecision.ACCEPTED,
          ResolutionDecision.ABSTAINED,
      }
      assert scripted_factory.calls == 1
  ```

  Convert the existing blocked, insufficient, wrong-source-family, wrong-event, and checksum tests to these new service interfaces. Add one ingest behavior test whose returned state contains the two new authority results and no legacy result envelopes.

- [ ] **Step 2: Run the focused tests and verify RED**

  Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_current_architecture.py \
    tests/test_agent_system_runtime_binding.py \
    tests/test_agent_system_structural_context.py
  ```

  Expected: collection/import failures for the new authority module and new interface names.

- [ ] **Step 3: Extract and rename the authority-domain implementation**

  Move the sealed candidate audit, source-record validation, zero/one-candidate decision, and bounded ambiguity activation from `agents.py` into `authority_resolution.py`. Change the execution-binding tool version from `resolution-compatibility-v1` to `authority-resolution-v1`.

  Build `AuthorityResolutionResult.evidence_card` from the selected proposal and exact authority evidence. Preserve these source families:

  ```python
  expected_family = (
      SourceFamily.NASR_FACILITY
      if domain == "facility"
      else SourceFamily.FAA_TERM
  )
  ```

  Unique candidates must not construct the Semantic Resolution model factory. Multiple eligible candidates may invoke only `run_semantic_resolution_agent`.

- [ ] **Step 4: Cut the workflow over to the new services**

  Rename the two workflow nodes and state keys. Keep their parallel fan-out and join. Make `_join_node` consume `AuthorityResolutionResult.domain_outcome`, and make downstream code consume each result's evidence card, source records, proposal, traces, and model calls directly.

- [ ] **Step 5: Delete compatibility wrappers and migrate tests**

  Remove the legacy Facility/Terminology public functions, dataclasses, exports, and metadata-free branches. Replace `test_agent_system_architecture_compatibility.py` with current behavior tests rather than assertions that removed names remain importable.

- [ ] **Step 6: Run focused and full Agent-system tests**

  Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_current_architecture.py \
    tests/test_agent_system_runtime_binding.py \
    tests/test_agent_system_structural_context.py \
    tests/test_agent_system_graph_kernel.py \
    tests/test_agent_system_multisource_context.py
  uv run ruff check .
  ```

  Expected: all selected tests and Ruff pass; unique paths still record zero provider attempts.

- [ ] **Step 7: Commit**

  ```bash
  git add src/aviation_agentic_ai/agent_system tests
  git commit -m "refactor(agent-system): cut over authority resolution services"
  ```

---

### Task 2: Remove the Legacy Knowledge Graph Agent and Publish Assembly Directly

**Files:**
- Modify: `src/aviation_agentic_ai/agent_system/agents.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `src/aviation_agentic_ai/agent_system/prompts.py`
- Delete: `src/aviation_agentic_ai/agent_system/kg_tools.py`
- Delete: `src/aviation_agentic_ai/agent_system/kg_tool_graph.py`
- Delete: `configs/prompts/agent_system_v1.yaml`
- Create: `configs/prompts/decision_case_agents_v1.yaml`
- Delete: `scripts/smoke_agent_system_prompts.py`
- Delete: `tests/test_agent_system_kg_tool_graph.py`
- Modify: `tests/test_agent_system_prompt_catalog.py`
- Modify: `tests/test_agent_system_tool_model.py`
- Modify: `tests/test_agent_system.py`
- Modify: `tests/test_agent_system_case_assembly.py`
- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_cli_agent_system.py`

**Interfaces:**
- `DEFAULT_PROMPT_CATALOG` becomes `configs/prompts/decision_case_agents_v1.yaml`.
- The prompt catalog contains only `semantic_resolution`, `decision_case_assembly`, and `query`.
- The prompt set ID becomes `aviation-decision-case-agents-v1`.
- The workflow node is `decision_case_assembly`, implemented by `_decision_case_assembly_node`.
- The Assembly node publishes:

  ```python
  {
      "case_assembly_task": task,
      "case_assembly_proposal": proposal,
      "case_assembly_feedback": feedback,
      "case_assembly_result": result,
      "assembly_graph_patch": graph_patch_or_none,
      "assembly_failure_reason": failure_reason,
      "event_uri": event_uri,
      "event_class": event_class,
      "model_calls": list(result.model_calls),
  }
  ```

- `_materialize_node` accepts `assembly_graph_patch: GraphPatchBlock | None` directly.
- Remove `KGConstructionInput`, `run_kg_construction_agent`, `kg_tool_model_factory`, the `knowledge_graph_construction` prompt, and the fabricated `kg_result`.
- Rename deterministic `run_advisory_agent` to `build_advisory_evidence`; it remains a zero-call parser/service and has no prompt role.

- [ ] **Step 1: Write direct-Assembly and active-prompt tests**

  Add or convert tests to assert observable behavior:

  ```python
  def test_ingest_publishes_assembly_patch_without_legacy_kg_envelope():
      state = run_ingest(canonical_context)
      assert state["case_assembly_result"].proposal.assembly_status in {
          AssemblyStatus.OK,
          AssemblyStatus.PARTIAL,
      }
      assert state["assembly_graph_patch"].patch_lines
      assert state.get("kg_result") is None


  def test_prompt_catalog_contains_only_activated_model_roles():
      catalog = get_prompt_catalog()
      assert set(catalog.roles) == {
          "semantic_resolution",
          "decision_case_assembly",
          "query",
      }
  ```

  Preserve the existing Assembly preflight, out-of-task evidence, declared-reason source-family, and one-value repair tests.

- [ ] **Step 2: Run the focused tests and verify RED**

  Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_current_architecture.py \
    tests/test_agent_system_case_assembly.py \
    tests/test_agent_system_prompt_catalog.py \
    tests/test_cli_agent_system.py
  ```

  Expected: failures for the old node/result/prompt surfaces.

- [ ] **Step 3: Replace the KG bridge with direct Assembly publication**

  Rename `_kg_construction_node` and remove the legacy `AgentStatus` conversion. Return the strict Assembly proposal/result plus `assembly_graph_patch`. Update `_materialize_node` and `context_artifacts.py` to use the Assembly status and failure reason directly.

  Preserve `_proposal_to_graph_patch_block`, `preflight_validate_case_assembly_proposal`, and `validate_graph_patch`; `GraphPatchBlock` remains the bounded publication handoff.

- [ ] **Step 4: Delete the dead KG Agent runtime**

  Remove the old KG input/function from `agents.py`, delete the KG tool gateway/graph modules, and remove their tests. Remove unused model factories from `IngestContext` and CLI construction.

- [ ] **Step 5: Make advisory interpretation deterministic-only**

  Rename the existing deterministic parser wrapper to:

  ```python
  def build_advisory_evidence(
      *,
      task: AgentTask,
      advisory: SourceRecord,
      event_classes: list[str],
      mentions: AdvisoryMentions,
  ) -> EvidenceCard: ...
  ```

  Store it as `advisory_evidence` in workflow state. It produces exact source-contained claims and no `ModelCallRecord`.

- [ ] **Step 6: Replace the prompt catalog**

  Create the three-role catalog by retaining only the current Semantic Resolution, Decision Case Assembly, and Query prompt contracts. Update prompt loading/tests and remove the obsolete five-role smoke script. Do not make live calls.

- [ ] **Step 7: Run focused tests and repository lint**

  Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_current_architecture.py \
    tests/test_agent_system_case_assembly.py \
    tests/test_agent_system_prompt_catalog.py \
    tests/test_agent_system_tool_model.py \
    tests/test_agent_system_multisource_context.py \
    tests/test_cli_agent_system.py
  uv run ruff check .
  ```

- [ ] **Step 8: Commit**

  ```bash
  git add -A
  git commit -m "refactor(agent-system): remove legacy graph agent runtime"
  ```

---

### Task 3: Require the Current Profile-Owned Run Artifact Format

**Files:**
- Modify: `src/aviation_agentic_ai/agent_system/sources.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `src/aviation_agentic_ai/agent_system/materialize.py`
- Modify: `src/aviation_agentic_ai/agent_system/validation_profiles.py`
- Modify: `src/aviation_agentic_ai/agent_system/runtime.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_context_store.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `tests/test_agent_system_current_architecture.py`
- Modify: `tests/test_agent_system_graph_kernel.py`
- Modify: `tests/test_agent_system_public_observations.py`
- Modify: `tests/test_agent_system_query_tools.py`
- Modify: `tests/test_agent_system_query_tool_graph.py`
- Modify: `tests/test_agent_system_multisource_contracts.py`
- Modify: `tests/test_agent_system_runtime_binding.py`

**Interfaces:**
- Add:

  ```python
  RUN_MANIFEST_VERSION = "decision-case-run-v1"
  ```

- `write_run_manifest` accepts `FactMaterialization | None` only and writes `"manifest_version": RUN_MANIFEST_VERSION`.
- Canonical call accounting consists of `provider_attempts` and `provider_successes`; remove `provider_calls`.
- `QueryGraphStore` and `QueryContextStore` require the current manifest version before reading any graph or context artifact.
- `SourceSnapshotRegistry` and `source_snapshots.jsonl` are the only accepted snapshot contract.
- `ValidatedFact` with an exact `ValidationProfileRef`, `evidence_mode`, `evidence_ref`, source IDs, and snapshot checksums is the only formal fact contract.
- Explicit current-format optional-layer `insufficient` and `blocked` states remain valid.

- [ ] **Step 1: Write current-format rejection and acceptance tests**

  Add tests whose expected values are hand-authored:

  ```python
  def test_query_store_rejects_a_run_without_current_manifest(tmp_path):
      write_profile_owned_graph(tmp_path)
      with pytest.raises(QueryToolError, match="current run manifest"):
          QueryGraphStore(tmp_path)


  def test_profile_gap_requires_registered_jsonl_snapshot(tmp_path):
      write_current_manifest(tmp_path)
      write_profile_gap(tmp_path)
      write_legacy_single_snapshot(tmp_path)
      with pytest.raises(QueryToolError, match="source_snapshots.jsonl"):
          QueryGraphStore(tmp_path)


  def test_manifest_records_attempts_without_legacy_provider_calls(tmp_path):
      path = write_run_manifest(..., model_calls=[failed_call])
      payload = json.loads(path.read_text())
      assert payload["manifest_version"] == "decision-case-run-v1"
      assert payload["provider_attempts"] == 1
      assert payload["provider_successes"] == 0
      assert "provider_calls" not in payload
  ```

  Add a positive test proving a current manifest, registered snapshots, and profile-owned facts remain queryable. Preserve explicit current `insufficient`/`blocked` optional-layer tests.

- [ ] **Step 2: Run the focused tests and verify RED**

  Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_current_architecture.py \
    tests/test_agent_system_query_tools.py \
    tests/test_agent_system_multisource_contracts.py \
    tests/test_agent_system_runtime_binding.py
  ```

  Expected: old no-manifest/single-snapshot fixtures are still accepted or the version key is absent.

- [ ] **Step 3: Remove old writers and materialization**

  Delete `write_source_snapshot`, `LegacyValidatedFact`, `decode_legacy_validated_fact`, `GraphPatchMaterialization`, `materialize_graph_patch`, and the guide-only materialization/projection branch. Keep `FactMaterialization`, `materialize_validated_facts`, and the profile-owned Neo4j projection.

  In `_materialize_node`, keep the provisional registry in memory for Kernel/trace validation; do not write it. `integrate_decision_context` remains the sole writer of the final multi-source registry.

- [ ] **Step 4: Version the manifest and simplify CLI output**

  Write the exact current version, accept only `FactMaterialization | None`, remove the old summary branch and duplicate provider key, and simplify the CLI materialization output accordingly.

- [ ] **Step 5: Make all query paths require the current run**

  Validate `run_manifest.json`, its exact version, current materialization, `formal_layers`, and registered snapshots before `QueryGraphStore` accepts `kg.jsonl`. Require current fact ownership/evidence fields. Remove the `source_snapshot.json` fallback and no-manifest/summary-only branches.

  Keep these current optional outcomes:

  ```python
  if layer_status == "insufficient":
      return OutcomeSummaryRead(status="insufficient", event_id=event_id)
  if layer_status == "blocked":
      return OutcomeSummaryRead(
          status="blocked",
          event_id=event_id,
          failure_reason=recorded_failure_reason,
      )
  ```

- [ ] **Step 6: Migrate shared query fixtures**

  Update the fixture writers in `test_agent_system_query_tools.py`, `test_agent_system_query_tool_graph.py`, and `test_agent_system_multisource_contracts.py` so every query fixture writes the current manifest, profile-owned fact shape, and source registry. Delete tests whose sole purpose was reading an old run.

- [ ] **Step 7: Run artifact, query, and full Agent-system tests**

  Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_current_architecture.py \
    tests/test_agent_system_graph_kernel.py \
    tests/test_agent_system_public_observations.py \
    tests/test_agent_system_query_tools.py \
    tests/test_agent_system_query_tool_graph.py \
    tests/test_agent_system_multisource_contracts.py \
    tests/test_agent_system_runtime_binding.py \
    tests/test_cli_agent_system.py
  uv run ruff check .
  ```

- [ ] **Step 8: Commit**

  ```bash
  git add -A
  git commit -m "refactor(agent-system): require current run artifacts"
  ```

---

### Task 4: Update the Normative Architecture and Verify the Three Cases

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `GOALS.md`
- Modify: `TODO.md`
- Modify: `RESEARCH_AUDIT.md`
- Modify: `RESEARCH_OVERVIEW.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `src/aviation_agentic_ai/agent_system/__init__.py`
- Modify: `docs/multi_agent_kg_system_design.md`
- Modify: `docs/superpowers/specs/2026-07-27-three-agent-decision-case-architecture-design.md`
- Modify only if still current-facing: `docs/atcscc_decision_record_explorer_design.md`
- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_agent_system_query_tool_graph.py`
- Modify: `tests/test_cli_agent_system.py`

**Interfaces:**
- Reader-facing architecture:

  ```text
  deterministic AdvisoryParser
    -> deterministic facility / terminology authority services
       -> shared Semantic Resolution Agent only for genuine ambiguity
    -> deterministic Weather / BTS adapters
    -> Decision Case Assembly Agent or canonical zero-call compiler
    -> Formal Graph Kernel
    -> profile-owned current run artifacts
    -> bounded Query Agent
  ```

- Supersede the deferred Batch E compatibility gate. Batch C.1 is the completed breaking cutover; Decision Case Analysis remains inactive.
- Historical Batch A/B/C plan documents remain historical and are not rewritten as current runtime documentation.

- [ ] **Step 1: Confirm the three-case acceptance tests state all required outcomes**

  Preserve or add parameterized tests with literal expected values:

  ```python
  @pytest.mark.parametrize(
      ("source_id", "facility", "reason_state", "active_counts"),
      [
          ("2026-05-19:123", "KJFK", "profile_gap", (20, 18, 2, 0)),
          ("2026-05-19:138", "KJFK", "formal_weather", (77, 68, 4, 5)),
          ("2026-05-20:020", "KEWR", "missing", (50, 49, 1, 0)),
      ],
  )
  def test_current_pipeline_preserves_the_three_decision_cases(...):
      ...
  ```

  The GDP `138` source evidence must end at `THUNDERSTORMS`. Ground Stop `123` must have no formal `atm:impactingCondition`. Cancellation `020` reason queries must be `insufficient`. All three must make zero unnecessary provider calls.

- [ ] **Step 2: Run the three-case tests**

  Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_multisource_context.py::test_three_cases_integrate_weather_and_bts_without_widening_core_semantics \
    tests/test_agent_system_query_tool_graph.py::test_weather_context_never_changes_the_three_reason_states \
    tests/test_agent_system_query_tool_graph.py::test_ground_stop_reason_uses_profile_gap_without_model_call \
    tests/test_agent_system_query_tool_graph.py::test_gdp_reason_uses_formal_fact_and_exact_source_wording \
    tests/test_agent_system_query_tool_graph.py::test_missing_reason_is_insufficient_before_model_construction \
    tests/test_agent_system_query_tool_graph.py::test_public_outcome_response_preserves_three_case_active_counts
  ```

- [ ] **Step 3: Rewrite current-facing documentation**

  Remove claims that Facility, Terminology, Advisory parsing, or legacy KG construction are active Agent roles. Document the authority services, the two conditionally activated semantic Agents, current Query Agent, exact artifact format, and deliberate lack of backward compatibility.

  In the three-agent architecture specification, replace the old Batch E waiting condition with the completed Batch C.1 cutover and state that old commands' useful names were retained as current UX, not as a compatibility guarantee.

- [ ] **Step 4: Run a tracked-file legacy-surface scan**

  Run:

  ```bash
  git grep -nE \
    'CompatibilityResolutionResult|_resolve_.*compatibility|run_facility_agent|run_terminology_agent|run_kg_construction_agent|KGConstructionInput|kg_tool_model_factory|resolution-compatibility-v1|source_snapshot\.json|decode_legacy_validated_fact|provider_calls' \
    -- \
    src/aviation_agentic_ai/agent_system \
    src/aviation_agentic_ai/cli_agent_system.py \
    configs/prompts \
    tests \
    README.md AGENTS.md GOALS.md TODO.md RESEARCH_AUDIT.md \
    docs/multi_agent_kg_system_design.md
  ```

  Expected: no matches. Historical plan/spec files are outside this active-surface scan.

- [ ] **Step 5: Run full verification**

  Run:

  ```bash
  uv run ruff check .
  uv run pytest -q
  uv build
  git diff --check
  ```

  Expected: all commands exit zero. No real provider call occurs.

- [ ] **Step 6: Commit**

  ```bash
  git add AGENTS.md README.md GOALS.md TODO.md RESEARCH_AUDIT.md \
    RESEARCH_OVERVIEW.md REPRODUCIBILITY.md \
    src/aviation_agentic_ai/agent_system/__init__.py \
    docs/multi_agent_kg_system_design.md \
    docs/superpowers/specs/2026-07-27-three-agent-decision-case-architecture-design.md \
    tests
  git commit -m "docs(agent-system): record current architecture cutover"
  ```

---

## Final Review Gate

- Review the complete branch diff against this plan.
- Confirm no compatibility-only alias, wrapper, reader, writer, prompt, or test remains in the active Agent-system surface.
- Confirm useful current CLI commands still work with current runs.
- Confirm all three canonical cases retain exact reason states, facilities, operational periods, BTS-reported observations, non-causal Weather boundaries, and source provenance.
- Confirm no Decision Case Analysis Agent, new source, causal relation, or recommendation was introduced.
- Run the full verification commands again after any review fix.
