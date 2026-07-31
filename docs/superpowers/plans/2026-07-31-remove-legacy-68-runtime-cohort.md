# Remove Legacy 68-Record Runtime Cohort Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the historical 68-record NYC mention cohort from the active ingestion runtime while preserving the old cross-source experiment as an explicitly historical, reproducible path.

**Architecture:** The active `agent-system` will use a dedicated configuration without a `cohort` section, ingest all configured advisory records unless bounded by `--source-id`, and build facility authority from the complete configured NASR snapshot. The old `cross-source` subsystem retains `configs/cross_source_v1.yaml` and its deterministic JFK/EWR/LGA text-mention selector solely for historical evaluation reproduction.

**Tech Stack:** Python 3.11+, Click, PyYAML, pytest, SQLite evidence-store runtime, FAA NASR parsers.

## Global Constraints

- Do not change ATMONTO TMI publication semantics or the five regression fixtures.
- Do not add a new Agent, model call, data source, compatibility alias, or migration layer.
- Do not describe the 68 records as manually reviewed, representative, or the active runtime scope.
- Preserve the historical selector result of exactly 68 NYC-code-mention records.
- Active ingestion must not read `config.cohort` or call `select_cross_source_cohort`.
- Run focused tests during implementation and one final repository verification.

---

### Task 1: Separate Active And Historical Configuration

**Files:**
- Create: `configs/aviation_knowledge_v1.yaml`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_evaluation.py`
- Modify: `tests/test_cli_agent_system.py`
- Modify: `tests/test_agent_system_evidence_store.py`
- Test: `tests/test_cross_source_contracts.py`
- Test: `tests/test_cross_source_cohort.py`

**Interfaces:**
- Consumes: existing source paths and evidence-role metadata from `configs/cross_source_v1.yaml`.
- Produces: `configs/aviation_knowledge_v1.yaml`, the default active configuration with its own `aviation-knowledge-2026-05-v1` identity and no `cohort` section; the old configuration remains the historical cross-source contract.

- [x] **Step 1: Write failing active-config tests**

  Update the active configuration assertions to require:

  ```python
  config = load_yaml("configs/aviation_knowledge_v1.yaml")
  assert "cohort" not in config
  assert config["sources"]["atcscc_advisories"].endswith("atcscc_advisories.jsonl")
  ```

  Add a CLI help assertion that the default `--config` is `configs/aviation_knowledge_v1.yaml`.

- [x] **Step 2: Run the focused tests and verify RED**

  Run:

  ```bash
  uv run pytest -q tests/test_cli_agent_system.py tests/test_agent_system_evidence_store.py
  ```

  Expected: failure because the active configuration does not exist and the CLI still defaults to the historical configuration.

- [x] **Step 3: Add the active configuration and switch active defaults**

  Copy the active source, metadata, URL, and evidence settings into `configs/aviation_knowledge_v1.yaml`, omitting `cohort` and retired cross-source-only settings. Give the active dataset and store their own `aviation-knowledge-2026-05-v1` identity. Change only `agent-system` and current retrieval-evaluation defaults. Keep `cli_cross_source.py`, `cross_source/supervisor.py`, and their tests on `configs/cross_source_v1.yaml`.

- [x] **Step 4: Run focused tests and verify GREEN**

  Run:

  ```bash
  uv run pytest -q tests/test_cli_agent_system.py tests/test_agent_system_evidence_store.py tests/test_cross_source_contracts.py tests/test_cross_source_cohort.py
  ```

  Expected: active config assertions and historical 68-record selection both pass.

### Task 2: Remove NYC Cohort Filtering From Runtime Authority

**Files:**
- Modify: `src/aviation_agentic_ai/agent_system/authority_evidence.py`
- Modify: `src/aviation_agentic_ai/agent_system/sources.py`
- Modify: `tests/fixtures/agent_system_authority/nasr_records.txt`
- Modify: `tests/test_agent_system_authority_evidence.py`

**Interfaces:**
- Consumes: the configured NASR ZIP and manifest.
- Produces: a source-wide `FacilityAuthorityCatalog` whose airport contents are not filtered through legacy NYC codes; event tasks still receive only mention-matched candidates.

- [x] **Step 1: Add a non-NYC NASR fixture and failing test**

  Add a DCA/KDCA airport row to the test fixture and assert that a configuration with no `cohort` section loads KJFK, KEWR, and KDCA into the authority catalog.

- [x] **Step 2: Run the authority test and verify RED**

  Run:

  ```bash
  uv run pytest -q tests/test_agent_system_authority_evidence.py -k facility
  ```

  Expected: failure because `_load_facility_catalog` currently reads `config.cohort.airport_codes` and filters out KDCA.

- [x] **Step 3: Remove the runtime filter and obsolete bridge helpers**

  Delete the `configured_codes` filter from `_load_facility_catalog`. Remove `_cross_source_config`, `load_facility_source`, `load_term_source`, `facility_candidates`, and `term_candidates` from `agent_system/sources.py` after confirming they have no callers. Keep advisory, Weather, BTS, and source-asset loaders unchanged.

- [x] **Step 4: Run focused authority and ingestion tests**

  Run:

  ```bash
  uv run pytest -q tests/test_agent_system_authority_evidence.py tests/test_agent_system_ingestion_pipeline.py
  ```

  Expected: the no-cohort active configuration loads non-NYC authority records and ingestion behavior remains unchanged.

### Task 3: Correct Current Claims And Preserve Historical Provenance

**Files:**
- Modify: `AGENTS.md`
- Modify: `RESEARCH_AUDIT.md`
- Modify: `README.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `ARTIFACT_INDEX.md`
- Modify: `TODO.md`
- Modify: `tests/test_agent_system_tmi_profiles.py`

**Interfaces:**
- Consumes: verified source-selection behavior and current ingestion behavior.
- Produces: one consistent description of the active 718-record source and a clearly historical 68-record deterministic NYC mention selection.

- [x] **Step 1: Rename historical regression tests**

  Rename tests so they state `legacy_nyc_mention_selection` rather than `frozen cohort` or current coverage. Preserve the assertions that the historical selector returns 68 and the automated family/preflight classifications remain reproducible.

- [x] **Step 2: Replace active configuration references**

  Change current `agent-system` commands in README, REPRODUCIBILITY, and ARTIFACT_INDEX to `configs/aviation_knowledge_v1.yaml`. Keep historical `cross-source` commands and records on `configs/cross_source_v1.yaml`.

- [x] **Step 3: Correct the 68-record wording**

  Remove the 68-record table from `Current Intake`. State that the active source contains 718 configured records and that ingestion processes all records or an explicit source-ID subset. In historical context, use:

  ```text
  The legacy cross-source experiment deterministically selected 68 records
  whose full text mentioned JFK, EWR, LGA, KJFK, KEWR, or KLGA. The 46/3/18/1
  split is automated registry/preflight output, not manual review or a
  representative sample.
  ```

- [x] **Step 4: Run context-hygiene and focused tests**

  Run:

  ```bash
  git grep -n -E 'reviewed 68|reviewed 68-record|manual.*68' -- '*.md' '*.yaml' '*.py'
  uv run pytest -q tests/test_agent_system_tmi_profiles.py tests/test_cross_source_cohort.py
  ```

  Expected: no false manual-review claim; historical selection remains exactly 68.

### Task 4: Final Verification

**Files:**
- Verify all modified files.

**Interfaces:**
- Consumes: Tasks 1-3.
- Produces: a clean, tested feature branch ready for review.

- [x] **Step 1: Verify active/historical separation**

  Run:

  ```bash
  git grep -n -I 'cohort' -- 'src/aviation_agentic_ai/agent_system/**/*.py' 'configs/aviation_knowledge_v1.yaml'
  uv run pytest -q tests/test_cross_source_cohort.py
  ```

  Expected: no active runtime cohort dependency; historical selector still passes.

- [x] **Step 2: Run final repository checks once**

  Run:

  ```bash
  uv run ruff check .
  uv run pytest -q
  uv build
  git diff --check
  ```

  Expected: all commands succeed.
