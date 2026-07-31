# Legacy Surface and Module Decoupling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove retired public command surfaces and make the active ingestion-first `agent_system` independent of the historical `cross_source` package without changing IDs, stored semantics, or current Query-Agent behavior.

**Architecture:** The active public runtime remains `agent-system`, with research utilities kept only when they still support the ATMONTO-aligned project. Shared identifiers, JSONL reading, authority entities, NASR parsing, and FAA terminology loading move into neutral utility and authority modules. The historical `cross_source` implementation remains available for explicit reproduction but no longer owns code required by the current runtime.

**Tech Stack:** Python 3.12, Click, Pydantic v2, pytest, Ruff, uv.

## Global Constraints

- Do not modify the fixed LangGraph ingestion topology or `_CTX_HOLDER` in this batch.
- Do not add source-coverage metadata, new data sources, Agents, prompts, or model calls.
- Preserve every existing stable ID, canonical authority ID, Pydantic serialization shape, NASR parse result, and term-registry ordering.
- Preserve the historical 68-record experiment and its configuration as explicitly historical reproduction material.
- Remove historical commands only from the supported top-level CLI; do not delete their implementation or rewrite recorded historical outputs.
- Active `agent_system` production modules and active-named tests must not import `aviation_agentic_ai.cross_source` after L2.
- Use one focused review after each batch and one final repository verification.

---

### Task 1: Retire Historical Public Surfaces

**Files:**
- Modify: `tests/test_cli_agent_system.py`
- Modify: `tests/test_cli_cross_source.py`
- Modify: `src/aviation_agentic_ai/cli.py`
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `reports/stages/index.md`
- Modify: `reports/final/README.md`
- Modify: `docs/atcscc_decision_record_explorer_cases.md`
- Modify: current `agent_system` tests that explicitly pass `configs/cross_source_v1.yaml`

**Interfaces:**
- Consumes: the current top-level Click registry in `TOP_LEVEL_COMMANDS`.
- Produces: a supported root surface containing `agent-system` and still-relevant research utilities, while the retired `cross-source`, PHAK chunk/index/query/demo/agent/KG groups are no longer registered at the root.

- [ ] **Step 1: Write failing public-surface and packaging tests**

  Add assertions that the root CLI does not register `cross-source`, `chunk`, `index`, `query`, `demo`, `agent`, or `kg`; assert that `agent-system`, `ontology`, `source`, and `cqs` remain. Assert that `pyproject.toml` defines an `agent-system` extra and no empty `web` deployment extra.

- [ ] **Step 2: Run focused tests and verify RED**

  Run:

  ```bash
  uv run pytest -q tests/test_cli_agent_system.py tests/test_cli_cross_source.py
  ```

  Expected: failure because retired groups are still registered and the active dependency extra is still named only `ontology-generation`.

- [ ] **Step 3: Apply the minimal public-surface change**

  Remove the retired groups from `TOP_LEVEL_COMMANDS`. Keep the historical command modules untouched. Add an `agent-system` optional dependency group for the active LangChain model/tool runtime, retain `ontology-generation` for historical ontology workflows, and remove the unused FastAPI/Uvicorn `web` extra.

- [ ] **Step 4: Remove active references to the historical configuration**

  Replace explicit `configs/cross_source_v1.yaml` arguments in current `agent_system` tests with `configs/aviation_knowledge_v1.yaml`. Keep checksum/reproduction assertions that intentionally verify the historical configuration in clearly historical tests.

- [ ] **Step 5: Correct current-looking documentation**

  Update installation instructions to use `--extra agent-system`; reduce `reports/stages/index.md` to a routing tombstone; mark the Decision Record Explorer case set and final-report directory as historical; do not alter historical report result bodies.

- [ ] **Step 6: Run focused tests and verify GREEN**

  Run:

  ```bash
  uv run pytest -q tests/test_cli_agent_system.py tests/test_cli_cross_source.py tests/test_agent_system_live_evaluation.py tests/test_agent_system_graph_kernel.py tests/test_agent_system_multisource_context.py
  uv run ruff check src/aviation_agentic_ai/cli.py tests/test_cli_agent_system.py tests/test_cli_cross_source.py
  ```

- [ ] **Step 7: Commit L1**

  ```bash
  git add pyproject.toml src/aviation_agentic_ai/cli.py tests README.md REPRODUCIBILITY.md reports/stages/index.md reports/final/README.md docs/atcscc_decision_record_explorer_cases.md
  git commit -m "refactor(project): retire historical public surfaces"
  ```

---

### Task 2: Extract Neutral Identifier and JSONL Utilities

**Files:**
- Create: `src/aviation_agentic_ai/utils/identifiers.py`
- Modify: `src/aviation_agentic_ai/utils/io.py`
- Create: `tests/test_agent_system_import_boundaries.py`
- Modify: active `src/aviation_agentic_ai/agent_system/*.py` imports
- Modify: active `tests/test_agent_system_*.py` imports

**Interfaces:**
- Produces: `stable_id(prefix: str, *parts: object) -> str` in `utils.identifiers`.
- Produces: `read_jsonl_objects(path: str | Path) -> list[dict[str, Any]]` in `utils.io`.
- Preserves: the exact existing SHA-256/16-character `stable_id` algorithm and JSONL blank-line/object/error behavior.

- [ ] **Step 1: Write failing golden and import-boundary tests**

  Test representative stable IDs against fixed expected strings. Test JSONL blank-line skipping, object-only validation, and path/line error messages. Add an AST-based boundary assertion that current `agent_system` modules do not import `aviation_agentic_ai.cross_source`.

- [ ] **Step 2: Run focused tests and verify RED**

  Run:

  ```bash
  uv run pytest -q tests/test_agent_system_import_boundaries.py
  ```

  Expected: failure because the neutral functions do not exist and active imports still target `cross_source`.

- [ ] **Step 3: Implement neutral utilities**

  Move the stable-ID algorithm unchanged into `utils.identifiers`. Add the JSONL object reader to `utils.io` without changing existing JSON-document helpers.

- [ ] **Step 4: Migrate active utility imports**

  Update active runtime modules and active-named tests to import from the neutral modules. Do not yet change authority contract or registry imports; the boundary test may temporarily allow those exact authority symbols until Task 3.

- [ ] **Step 5: Run focused regression tests and verify GREEN**

  Run:

  ```bash
  uv run pytest -q tests/test_agent_system_import_boundaries.py tests/test_agent_system_evidence_store.py tests/test_agent_system_ingestion_pipeline.py tests/test_agent_system_hybrid_query_tools.py tests/test_agent_system_source_retrieval.py
  ```

- [ ] **Step 6: Commit L2A**

  ```bash
  git add src/aviation_agentic_ai/utils src/aviation_agentic_ai/agent_system tests/test_agent_system_import_boundaries.py tests/test_agent_system_*.py
  git commit -m "refactor(agent-system): extract neutral storage utilities"
  ```

---

### Task 3: Extract Neutral Aviation Authority Modules

**Files:**
- Create: `src/aviation_agentic_ai/authority/__init__.py`
- Create: `src/aviation_agentic_ai/authority/contracts.py`
- Create: `src/aviation_agentic_ai/authority/identifiers.py`
- Create: `src/aviation_agentic_ai/authority/nasr.py`
- Create: `src/aviation_agentic_ai/authority/terminology.py`
- Modify: `src/aviation_agentic_ai/agent_system/authority_evidence.py`
- Modify: active Weather/BTS/context modules importing `CanonicalEntity` or `EntityType`
- Modify: `src/aviation_agentic_ai/cross_source/contracts.py`
- Modify: `src/aviation_agentic_ai/cross_source/alignment/registry.py`
- Modify: authority and cross-source regression tests

**Interfaces:**
- Produces: neutral `EntityType`, `TermCategory`, `CodeValue`, `CanonicalEntity`, `TermDefinition`, and `TermConcept` classes.
- Produces: `normalize_code`, `canonical_facility_id`, and `canonical_term_id`.
- Produces: `parse_nasr_apt_line`, `parse_nasr_aff_line`, and `load_term_registry(seed_path)`.
- Preserves: one shared class/Enum identity across current and historical modules; no duplicate authority type definitions.

- [ ] **Step 1: Write failing authority golden tests**

  Assert model serialization and `extra="forbid"`; assert canonical IDs; parse the existing APT/AFF fixture into exact expected entity data; load the tracked term seed and assert stable IDs, schema mappings, source refs, and ordering.

- [ ] **Step 2: Run focused tests and verify RED**

  Run:

  ```bash
  uv run pytest -q tests/test_agent_system_import_boundaries.py tests/test_agent_system_authority_evidence.py
  ```

  Expected: failure because neutral authority modules do not exist and active imports still target `cross_source`.

- [ ] **Step 3: Implement authority contracts and identifiers**

  Move only the shared authority types into `authority/contracts.py`. Import those same objects into historical `cross_source/contracts.py` so historical contracts continue to use identical Enum and model classes.

- [ ] **Step 4: Implement NASR and terminology loaders**

  Move APT/AFF fixed-width parsing unchanged into `authority/nasr.py`. Implement `load_term_registry(seed_path)` in `authority/terminology.py`, accepting a resolved seed path instead of an entire historical configuration.

- [ ] **Step 5: Migrate the current authority runtime**

  Update `authority_evidence.py` to resolve `sources.term_seed` itself and call `load_term_registry`. Update all current Weather, BTS, observation, and context modules to use the neutral authority contracts.

- [ ] **Step 6: Keep historical reproduction isolated**

  Make `cross_source/alignment/registry.py` import neutral authority types and parsers. Keep its cohort-specific `build_facility_registry(config)` and thin historical `build_term_registry(config)` adapter inside the historical package.

- [ ] **Step 7: Enforce the final import boundary**

  Remove every `aviation_agentic_ai.cross_source` import from `src/aviation_agentic_ai/agent_system/` and current `agent_system` tests. Move the two 68-selection assertions out of `test_agent_system_tmi_profiles.py` into the historical cohort test.

- [ ] **Step 8: Run focused regressions and verify GREEN**

  Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_import_boundaries.py \
    tests/test_agent_system_authority_evidence.py \
    tests/test_agent_system_weather_context.py \
    tests/test_agent_system_public_observations.py \
    tests/test_agent_system_multisource_context.py \
    tests/test_agent_system_ingestion_pipeline.py \
    tests/test_cross_source_contracts.py \
    tests/test_cross_source_cohort.py \
    tests/test_cross_source_registries.py \
    tests/test_cross_source_alignment.py
  ```

- [ ] **Step 9: Commit L2B**

  ```bash
  git add src/aviation_agentic_ai/authority src/aviation_agentic_ai/agent_system src/aviation_agentic_ai/cross_source tests
  git commit -m "refactor(agent-system): decouple historical cross-source modules"
  ```

---

### Task 4: Final Verification and Focused Documentation Alignment

**Files:**
- Modify only if needed: `RESEARCH_AUDIT.md`, `GOALS.md`, `ARTIFACT_INDEX.md`, `docs/multi_agent_kg_system_design.md`

**Interfaces:**
- Consumes: completed L1/L2 implementation.
- Produces: documentation that states the public/runtime boundary accurately without claiming removal of historical reproduction code.

- [ ] **Step 1: Scan active boundaries**

  Run:

  ```bash
  rg -n "aviation_agentic_ai\.cross_source" src/aviation_agentic_ai/agent_system tests/test_agent_system_*.py
  uv run aviation-ai --help
  ```

  Expected: no active cross-source imports and no retired root commands.

- [ ] **Step 2: Run the final repository checks once**

  ```bash
  uv run ruff check .
  uv run pytest -q
  uv build
  git diff --check
  ```

- [ ] **Step 3: Perform one bounded diff review**

  Confirm no LangGraph orchestration, storage schema, stable ID, source data, prompt, model, or evaluation result changed.

- [ ] **Step 4: Commit any final documentation-only correction**

  ```bash
  git add RESEARCH_AUDIT.md GOALS.md ARTIFACT_INDEX.md docs/multi_agent_kg_system_design.md
  git commit -m "docs(project): clarify active and historical boundaries"
  ```
