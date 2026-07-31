# Architecture Storytelling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reframe the repository around a clear research story and three publication-ready figures without expanding the runtime or adding decorative Agents.

**Architecture:** The project is presented as five connected planes: heterogeneous evidence, deterministic ingestion orchestration, semantic and trust control, authoritative knowledge and rebuildable retrieval, and Agent interaction. GDP Advisory 138 is the running example because its source-declared reason, time-aligned Weather context, and BTS public observations are all present while retaining explicit non-causal boundaries.

**Tech Stack:** Draw.io XML, diagrams.net desktop export, Markdown, existing repository documentation.

## Global Constraints

- Keep the current LangGraph ingestion workflow and describe it as deterministic orchestration, not as an Agent.
- Use `ATMONTO-Grounded Agentic HybridRAG for Heterogeneous Aviation Knowledge Integration` as the flagship positioning.
- Treat GDP, GS, and ReRoute as the current reusable vertical slice, not the permanent scope of the architecture.
- Preserve SQLite as the authoritative store; FTS5, Chroma, RDF/Turtle, and Neo4j remain rebuildable views or exports.
- Preserve the distinction between a source-declared ATCSCC reason, non-causal Weather context, and source-qualified BTS public observations.
- Do not add a new Agent, framework, benchmark, model call, data source, or production-hardening layer.
- Deliver each core figure as matching editable `.drawio` and rendered `.png` files, with 26 px diagram text, an opaque light background, orthogonal connector routing, and a long side of at least 2200 px.

---

### Task 1: Freeze the Architecture Narrative

**Files:**
- Create: `docs/architecture_narrative.md`
- Modify: `README.md`
- Modify: `RESEARCH_AUDIT.md`
- Modify: `GOALS.md`

**Produces:** One shared positioning statement, five-plane terminology, a bounded definition of `Agentic`, and the GDP 138 running-example contract.

- [ ] **Step 1:** Write the narrative spine: problem, method, runtime meaning of Agentic, supported output, and research boundary.
- [ ] **Step 2:** State the safe GDP 138 example using only the ATCSCC-declared reason, non-causal Weather context, and BTS public observations.
- [ ] **Step 3:** Align the README opening, project audit snapshot, and primary goal with the same five-plane wording.
- [ ] **Step 4:** Check that top-level prose leads with capability before limitations and does not promise causal inference or TMI recommendation.
- [ ] **Step 5:** Commit as `docs(project): define the architecture narrative`.

### Task 2: Build the Three Core Figures

**Files:**
- Create: `docs/figures/cross_source_evidence_motivated_example.drawio`
- Create: `docs/figures/cross_source_evidence_motivated_example.png`
- Create: `docs/figures/aviation_hybridrag_system_architecture.drawio`
- Create: `docs/figures/aviation_hybridrag_system_architecture.png`
- Create: `docs/figures/bounded_query_agent_workflow.drawio`
- Create: `docs/figures/bounded_query_agent_workflow.png`
- Modify: `docs/figures/heterogeneous_source_formats.drawio`
- Modify: `docs/figures/heterogeneous_source_formats.png`
- Delete: `docs/figures/tmi_event_construction_architecture.drawio`
- Delete: `docs/figures/tmi_event_construction_architecture.png`
- Delete: `docs/figures/tmi_event_retrieval_architecture.drawio`
- Delete: `docs/figures/tmi_event_retrieval_architecture.png`

**Produces:** Figure 1 explains why cross-source evidence is necessary, Figure 2 provides the complete five-plane architecture, and Figure 3 makes the LLM action-observation-evidence loop visible.

- [ ] **Step 1:** Draw the GDP 138 motivated example as fragmented sources converging into an evidence-bound answer with explicit source roles.
- [ ] **Step 2:** Draw the five-plane system overview and distinguish deterministic ingestion from the model-directed Query Agent.
- [ ] **Step 3:** Draw the bounded Query Agent workflow, including candidate discovery, exact source verification, evidence assembly, and per-statement support validation.
- [ ] **Step 4:** Replace `Decision artifact` with `TMI publication record` and `Outcome Aggregator` with `Observation Aggregator` in the supporting source-format figure.
- [ ] **Step 5:** Export all four figures from their final Draw.io sources and inspect the PNGs for clipping, overlap, line crossings, and normal-page readability.
- [ ] **Step 6:** Validate Draw.io XML, PNG dimensions, and filename pairing.
- [ ] **Step 7:** Commit as `docs(figures): add the architecture story`.

### Task 3: Align the Normative Design and Artifact Routes

**Files:**
- Modify: `docs/multi_agent_kg_system_design.md`
- Modify: `ARTIFACT_INDEX.md`

**Produces:** A design document that opens with the problem, the complete architecture, and the Agent loop; an artifact index that distinguishes flagship and supporting figures.

- [ ] **Step 1:** Retitle the design document with the flagship positioning and remove the defensive capability-denial list from its opening.
- [ ] **Step 2:** Present the three core figures in narrative order with self-contained captions and editable-source links.
- [ ] **Step 3:** Explain that Agentic behavior belongs to online model-directed retrieval and selective ambiguity escalation, while ingestion remains deterministic orchestration.
- [ ] **Step 4:** Register the new figures in `ARTIFACT_INDEX.md` and classify `heterogeneous_source_formats` as a supporting implementation figure.
- [ ] **Step 5:** Scan active documentation for obsolete figure references and inconsistent top-level naming.
- [ ] **Step 6:** Run `git diff --check`, `uv run ruff check .`, and focused visual/XML checks.
- [ ] **Step 7:** Commit as `docs(project): align architecture entry points`.

## Completion Evidence

- Three new `.drawio`/`.png` pairs exist and the two superseded TMI architecture pairs are removed.
- The GDP 138 example never turns Weather or BTS association into causality, decision rationale, capacity, or effectiveness.
- README, GOALS, RESEARCH_AUDIT, the normative design, and the artifact index use the same flagship positioning and five-plane model.
- The overall system figure is shown in README; the design document presents all three figures in order.
- The Draw.io XML opens cleanly, PNG long sides are at least 2200 px, and visual inspection finds no clipping or avoidable connector crossings.
- Documentation verification passes without changing runtime code or evaluation claims.
