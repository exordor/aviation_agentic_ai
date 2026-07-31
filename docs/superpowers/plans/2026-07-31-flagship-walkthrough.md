# GDP 138 Flagship Walkthrough Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Demonstrate the current ingestion-first aviation HybridRAG architecture with one reproducible, real-DeepSeek, evidence-bound GDP 138 walkthrough.

**Architecture:** Reuse the existing deterministic `ingest` and `reindex` paths, authoritative SQLite store, rebuildable Chroma indexes, bounded Query Agent, exact source reader, and live-evaluation capture. The only new runtime contract is a one-question `live_smoke` suite; the observed provider calls, tool trajectory, support bindings, and final status are then summarized in a human-readable walkthrough and an execution-trace figure.

**Tech Stack:** Python 3.12, Click CLI, SQLite evidence store, Chroma, sentence-transformers, DeepSeek `deepseek-v4-pro`, Pydantic contracts, pytest, Draw.io, Markdown.

## Global Constraints

- Use the real configured DeepSeek provider for the walkthrough; do not use fake, scripted, mock, replay, cached-response, or deterministic model substitutes.
- Keep the walkthrough classified as `live_smoke / system walkthrough`, not a benchmark or `live_experiment`.
- Use source ID `2026-05-19:138` and event ID `urn:aviation-agentic-ai:event:205dd8308f24ff4b`.
- Ask one natural-language question without embedding internal tool names or a fixed routing instruction.
- The expected evidence roles are ATCSCC source fact/source record, non-causal Weather context, and source-qualified BTS public observations.
- Do not infer that Weather caused the GDP, that the GDP caused the BTS observations, or that BTS metrics are FAA demand, capacity, AAR, EDCT, rationale, effectiveness, or recommendation evidence.
- Do not add a new Agent, public CLI, query framework, data source, persistent corpus, or production-hardening layer.
- Keep native provider responses and parsed runtime artifacts under gitignored `data/corpus/agent_system/`; commit only sanitized reports, suite contracts, documentation, and figures.
- If the real task fails, preserve and document the failure. Do not manufacture a successful walkthrough.

---

### Task 1: Freeze the Query Contract and Sequential Source Verification

**Files:**
- Create: `data/evaluation/agent_system/live_flagship_gdp138_walkthrough_v1.yaml`
- Modify: `configs/prompts/tmi_event_agents_v1.yaml`
- Modify: `tests/test_agent_system_live_evaluation.py`
- Modify: `tests/test_agent_system_prompt_catalog.py`

**Interfaces:**
- Consumes: `LiveEvaluationSuite`, the existing nine Query Agent read-only tools, and prompt catalog `aviation-tmi-event-agents-v1`.
- Produces: suite ID `flagship-gdp138-walkthrough-v1`, report stem `agent_system_live_flagship_gdp138_walkthrough_v1`, and Query prompt version `hybrid-query-agent-v5`.

- [ ] **Step 1: Write the failing suite-contract test.**

  Load `live_flagship_gdp138_walkthrough_v1.yaml` and assert that it contains exactly one query trial for `2026-05-19:138`, uses the approved natural-language question, requires `read_tmi_event_facts`, `read_source`, `read_tmi_operational_context`, and `read_public_observations`, and does not expose internal tool names in the question.

- [ ] **Step 2: Write the failing prompt-contract test.**

  Assert that the Query prompt version is `hybrid-query-agent-v5` and explicitly requires a dependent `read_source` call to occur only after a completed observation supplies its source-version and anchor identifiers.

- [ ] **Step 3: Run the two focused tests and confirm the expected failures.**

  ```bash
  uv run pytest -q \
    tests/test_agent_system_live_evaluation.py::test_flagship_walkthrough_suite_is_one_natural_cross_source_query \
    tests/test_agent_system_prompt_catalog.py::test_query_prompt_requires_sequential_exact_source_verification
  ```

  Expected: both fail because the suite and prompt-v5 contract do not yet exist.

- [ ] **Step 4: Add the minimal suite and prompt update.**

  Freeze this question:

  > What did ATCSCC publish for JFK in Advisory 138? Verify the source-declared reason from the original record, then summarize the time-aligned Weather reports and BTS public observations without inferring causality.

  Add only the sequential dependency rule; retain the existing four-provider-turn, six-tool-call, read-only, evidence-binding, and claim-boundary contracts.

- [ ] **Step 5: Run the focused tests and the full prompt/live-evaluator test modules.**

  ```bash
  uv run pytest -q \
    tests/test_agent_system_prompt_catalog.py \
    tests/test_agent_system_live_evaluation.py
  ```

  Expected: pass.

- [ ] **Step 6: Commit.**

  ```bash
  git add \
    data/evaluation/agent_system/live_flagship_gdp138_walkthrough_v1.yaml \
    configs/prompts/tmi_event_agents_v1.yaml \
    tests/test_agent_system_live_evaluation.py \
    tests/test_agent_system_prompt_catalog.py
  git commit -m "test(agent-system): define flagship live walkthrough"
  ```

### Task 2: Build the Evidence Slice and Run the Real Walkthrough

**Files:**
- Create, gitignored: `data/stores/aviation/flagship-gdp138-walkthrough-v1/`
- Create, gitignored: `data/corpus/agent_system/flagship-gdp138-walkthrough-v1/`
- Create through the existing evaluator: `reports/stages/agent_system_live_flagship_gdp138_walkthrough_v1.json`
- Create through the existing evaluator: `reports/stages/agent_system_live_flagship_gdp138_walkthrough_v1.md`

**Interfaces:**
- Consumes: `agent-system ingest`, `agent-system reindex`, `run_live_agent_evaluation`, `.env` DeepSeek credentials, and the Task 1 suite.
- Produces: an authoritative one-event store, current vector indexes, native provider-call capture, parsed trial output, a sanitized `HybridQueryRunArtifact`, and tracked sanitized summaries.

- [ ] **Step 1: Check only credential and input presence.**

  Confirm that `.env` exposes the configured DeepSeek credential and that the configured ATCSCC, NASR, Weather, and BTS snapshots exist. Do not print secrets.

- [ ] **Step 2: Ingest GDP 138 through the supported deterministic pipeline.**

  ```bash
  uv run --extra agent-system aviation-ai agent-system ingest \
    --config configs/aviation_knowledge_v1.yaml \
    --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
    --source-id 2026-05-19:138
  ```

  Expected: one accepted TMI event, zero provider calls, and retained ATCSCC, NASR, Weather, and BTS bindings.

- [ ] **Step 3: Build both rebuildable vector indexes.**

  ```bash
  uv run --extra agent-system aviation-ai agent-system reindex \
    --config configs/aviation_knowledge_v1.yaml \
    --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
    --model-name sentence-transformers/all-MiniLM-L6-v2 \
    --allow-model-download
  ```

  Expected: source and event indexes bind to the current store revision.

- [ ] **Step 4: Run exactly one real-provider walkthrough.**

  ```bash
  uv run python -m aviation_agentic_ai.agent_system.live_agent_evaluation \
    --config configs/aviation_knowledge_v1.yaml \
    --suite data/evaluation/agent_system/live_flagship_gdp138_walkthrough_v1.yaml \
    --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
    --output-dir data/corpus/agent_system/flagship-gdp138-walkthrough-v1 \
    --report-dir reports/stages \
    --allow-live-model \
    --repetitions 1
  ```

  Expected provider configuration: `deepseek/deepseek-v4-pro`, temperature `0`, thinking disabled, retries `0`.

- [ ] **Step 5: Verify runtime integrity before interpreting the answer.**

  Record attempted, returned, successful, failed, and provider-error calls; input/output tokens; latency; observed tool names; runner status; task-acceptance status; and the raw, parsed, and query-run paths and checksums. Confirm that every parsed trial binds to its real provider calls.

- [ ] **Step 6: Verify semantic acceptance without silently repairing the output.**

  Confirm the event type and KJFK identity, the exact source-declared `WEATHER / THUNDERSTORMS` reason, Weather-only non-causal context, BTS-only public observations, statement-level support bindings, registered read-only tools, and absence of causal, effectiveness, demand/capacity, or recommendation claims. If any check fails, retain the observed failed report and diagnose it separately.

### Task 3: Publish the Human-Readable Walkthrough and Observed Trace

**Files:**
- Create: `docs/flagship_gdp138_walkthrough.md`
- Create: `docs/figures/flagship_gdp138_live_trace.drawio`
- Create: `docs/figures/flagship_gdp138_live_trace.png`
- Modify: `README.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `ARTIFACT_INDEX.md`
- Modify: `reports/stages/agent_system_live_flagship_gdp138_walkthrough_v1.{json,md}` only through the existing evaluator, never by hand.

**Interfaces:**
- Consumes: the observed Task 2 report and sanitized `HybridQueryRunArtifact`.
- Produces: a reader-facing end-to-end narrative and one trace figure derived from the actual run rather than a predesigned ideal path.

- [ ] **Step 1: Write the walkthrough around observed evidence.**

  Include scope/status, the natural-language question, ingested evidence slice, real-model configuration, actual tool trajectory, validated answer, statement-to-evidence mapping, claim boundaries, reproduction commands, and artifact checksums. Do not expose prompts, raw responses, model reasoning, secrets, or sensitive tool payloads.

- [ ] **Step 2: Draw the observed execution trace.**

  Use one top-to-bottom path: question → Query Agent → observed tools → evidence roles → statement support validation → observed terminal answer/status. Include only tools actually present in the sanitized trace and show ATCSCC, Weather, and BTS as distinct evidence roles.

- [ ] **Step 3: Export and visually inspect the figure.**

  Confirm matching editable/rendered files, minimum 26 px text, no clipping, no overlapping nodes, no crossed connectors, and a readable long side of at least 2200 px.

- [ ] **Step 4: Add reader and reproduction routes.**

  Link the walkthrough from README, register the suite/report/document/figure in `ARTIFACT_INDEX.md`, and add exact ingest, reindex, and real-evaluator commands to `REPRODUCIBILITY.md`.

- [ ] **Step 5: Commit.**

  ```bash
  git add \
    docs/flagship_gdp138_walkthrough.md \
    docs/figures/flagship_gdp138_live_trace.drawio \
    docs/figures/flagship_gdp138_live_trace.png \
    data/evaluation/agent_system/live_flagship_gdp138_walkthrough_v1.yaml \
    reports/stages/agent_system_live_flagship_gdp138_walkthrough_v1.json \
    reports/stages/agent_system_live_flagship_gdp138_walkthrough_v1.md \
    README.md REPRODUCIBILITY.md ARTIFACT_INDEX.md
  git commit -m "docs(agent-system): add real flagship walkthrough"
  ```

### Task 4: Final Verification

**Files:**
- Verify only; no planned source changes.

- [ ] **Step 1: Run focused software verification.**

  ```bash
  uv run pytest -q \
    tests/test_agent_system_prompt_catalog.py \
    tests/test_agent_system_live_evaluation.py
  uv run ruff check .
  git diff --check
  ```

- [ ] **Step 2: Verify tracked and ignored boundaries.**

  Confirm no `.env`, credential, native provider response, parsed runtime row, local SQLite/Chroma file, or model-download artifact is staged.

- [ ] **Step 3: Report observed outcome.**

  Report the branch, commits, real provider/model, call counts, token usage, task acceptance, artifact paths/checksums, focused-test status, and deferred items. Do not merge or push unless the user explicitly requests it.

## Completion Evidence

- A one-question versioned suite exists and every evaluation sample in it invokes the real configured provider.
- GDP 138 is ingested by the normal persistent pipeline and queried by the normal bounded Query Agent.
- The raw-response, parsed-output, and query-run artifacts are checksum-bound and remain gitignored.
- The tracked report distinguishes provider success from task acceptance.
- The walkthrough and trace show the actual tool sequence and statement support, not a hypothetical route.
- ATCSCC reason, Weather context, and BTS observations remain separate evidence roles.
- No causal explanation, FAA demand/capacity inference, effectiveness claim, or TMI recommendation is introduced.
- Focused tests, Ruff, and diff checks pass.

## Explicitly Deferred

- A 100-call `live_experiment`, repeated measurements, model comparison, and statistical benchmark.
- Prompt optimization after observing the flagship result.
- A new web UI or revival of the retired Query Explorer.
- National Playbook PDF grounding, decision-episode linking, flight/sector integration, or additional data sources.
- Production deployment, security hardening, concurrency, and generalized walkthrough rendering.
