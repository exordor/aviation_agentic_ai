# Master Project Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one demonstrable master-project package for the ATCSCC
schema-constrained Agentic KG-RAG thesis line.

**Architecture:** Reuse existing ATCSCC artifacts and CLI/report commands. The
demo package consists of a concise dashboard, an offline single-advisory CLI
trace, and a thesis writing spine. No new database, platform, broad literature
review, or separate dashboard is introduced.

**Tech Stack:** Python, Click CLI, existing JSON/Markdown reports, pytest,
ruff, tracked ATCSCC experiment artifacts.

---

### Task 1: Keep The Dashboard Concise

**Files:**
- Modify: `src/aviation_agentic_ai/reporting/thesis_dashboard.py`
- Modify: `tests/test_thesis_dashboard.py`
- Regenerate: `reports/stages/thesis_experiment_dashboard.md`

- [x] **Step 1: Add vector-only S7 answer report to the dashboard inventory**

Expected source:

```python
"nasa_atmonto_s7_vector_only_llm_answer_generation": (
    "reports/stages/nasa_atmonto_s7_vector_only_llm_answer_generation.json"
)
```

- [x] **Step 2: Render concise Markdown**

The Markdown dashboard must contain:

```text
Outcome
Demo Path
Pipeline
Research Questions
Key Results
Demonstration Script
Claim Boundary
Current Checks
Next Writing Step
```

It must not render the full experiment inventory table in Markdown.

- [x] **Step 3: Add regression coverage**

Run:

```bash
uv run pytest tests/test_thesis_dashboard.py -q
```

Expected:

```text
2 passed
```

- [x] **Step 4: Regenerate dashboard**

Run:

```bash
uv run aviation-ai report thesis-experiment-dashboard
```

Expected:

```text
Built thesis experiment dashboard; consistency checks passed=True.
```

### Task 2: Preserve The Offline Demo Path

**Files:**
- Existing: `src/aviation_agentic_ai/cli_demo.py`
- Existing test: `tests/test_cli_demo.py`

- [x] **Step 1: Verify the CLI demo**

Run:

```bash
uv run aviation-ai demo
```

Expected content:

```text
ATCSCC advisory end-to-end demo
Pipeline: advisory -> S0 backbone -> S4 event graph -> KG-RAG answer.
Boundary: retrospective, source-bounded diagnostics; not operational ATC support.
```

- [x] **Step 2: Verify demo regression tests**

Run:

```bash
uv run pytest tests/test_cli_demo.py -q
```

Expected:

```text
2 passed
```

### Task 3: Create The Thesis Writing Spine

**Files:**
- Create: `docs/thesis_writing_spine.md`
- Modify: `docs/documentation_map.md`

- [x] **Step 1: Create the writing spine**

The document must include:

```text
Title
One-paragraph abstract draft
Contribution list
Method figure plan
Experiment table plan
RQ-to-evidence map
Claim boundary
Limitations and future work
```

- [x] **Step 2: Link it from the documentation map**

Add it to the `Start Here` section so future threads use it after the scope
lock and research mainline.

### Task 4: Final Verification

**Files:** all changed files.

- [x] **Step 1: Run focused tests**

```bash
uv run pytest tests/test_thesis_dashboard.py tests/test_cli_demo.py -q
```

- [x] **Step 2: Run documentation/code checks**

```bash
git diff --check
uv run ruff check .
```

- [x] **Step 3: Check Git status**

```bash
git status --short
```

Only scoped dashboard, writing-spine, and report artifacts should be dirty.

## Out Of Scope

- No new systematic review.
- No new database.
- No new dashboard app.
- No new data-source integration.
- No large multi-domain transfer experiment.
- No claim of live ATC decision support.
