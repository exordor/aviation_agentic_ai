# Research Audit

> This is the new thread entry point. It replaces the start-here role of `docs/thread_handoff.md` and `docs/documentation_map.md`. Until the archive commit lands, both remain in place under `docs/`; afterward they will be preserved under `docs/archive/governance_era/`. For a new thread, read this file first, then follow the navigation map below.

## 1. Project Snapshot

- Audit date: 2026-07-06
- Current branch: refactor/research-governance-framework
- Last commit: 0bf437e70f74dd199c08759b7d473a6fc2e18a5d
- Main language: Python (`uv` workspace).
- Main framework: custom CLI (`aviation-ai`) over `pyproject.toml`.
- Current thesis line: Agentic KG-RAG for evidence-grounded question answering over retrospective FAA ATCSCC advisories.
- Current status: writing-up phase. Schema, extraction, agentic loop, KG-RAG, and failure-audit evidence collected; thesis chapter draft in progress.

## 2. Navigation Map

Read in this order when entering the project:

| Order | File | Purpose |
|---|---|---|
| 1 | `RESEARCH_AUDIT.md` (this file) | Project snapshot and navigation. |
| 2 | `RESEARCH_OVERVIEW.md` | Problem, claim, scope, contributions, claim-safety matrix, SOTA positioning. |
| 3 | `RESEARCH_QUESTIONS.md` | RQ1–RQ4 in Description/Motivation/Related Hypotheses/Related Experiments/Current Evidence/Status form. |
| 4 | `HYPOTHESES.md` | H1–H6 table + falsification criteria. |
| 5 | `EXPERIMENTS.md` | Full formal-experiment protocol: systems, gold, metrics, procedure, completion gate, layered evaluation. |
| 6 | `RESULTS.md` | Deliverables and evidence rows with Observation/Evidence/Interpretation/Confidence. |
| 7 | `ARTIFACT_INDEX.md` | Tracked, non-default, and ignored artifact families; artifact management policy. |
| 8 | `DECISION_LOG.md` | Structural decisions D001+ with context/reason/alternatives/consequences. |
| 9 | `REPRODUCIBILITY.md` | Environment, install, regeneration commands, verification defaults. |
| 10 | `TODO.md` | Active task queue and P0–P4 backlog. |

## 3. Six-Question File Rubric

When looking at any file in this repo, ask:

1. Which research question does this file serve?
2. Which hypothesis does it support?
3. Which experiment is it part of?
4. What are its inputs and outputs?
5. What evidence does it produce?
6. Should it be kept, archived, or deleted?

If a file cannot answer these, treat it as an `unknown artifact` — do not delete it; move it under `archive/unknown/` and note it in `ARTIFACT_INDEX.md`.

## 4. Default Context For New Threads

- Read this file, then `RESEARCH_OVERVIEW.md`, then `ARTIFACT_INDEX.md`. Load additional files only when the task needs their layer.
- Keep the active plugin/skill surface minimal. Use task-specific skills only when their trigger matches the current action.
- PHAK, web-demo, chunking-era, and old final-report docs are historical unless explicitly requested.
- Avoid unsupported claims: full aviation ontology completeness, live ATC decision support, external expert certification, or universal GraphRAG superiority.

## 5. Source Boundaries

Keep source families separate unless a source-specific profile and evaluation protocol exists: ATCSCC advisories; FAA/NASA reference PDFs; NASR/facility data; weather data; transfer pilots or non-ATCSCC corpora.

## 6. Verification Defaults

- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Report-generation changes: run the relevant command in `REPRODUCIBILITY.md` and inspect the generated diff before committing.

## 7. Git And Publishing

- Publishing remotes: `origin` is GitLab; `github` is GitHub.
- When a branch should be shared, push both remotes unless the user requests one remote only.
- After merging into `main`, push `main` to both remotes and verify local `main`, `origin/main`, and `github/main` resolve to the intended commit.
