# Governance Era Archive

These files were the canonical project-governance spine until the 2026-07-05 research-governance refactor (spec: `docs/superpowers/specs/2026-07-05-research-governance-refactor-design.md`, plan: `docs/superpowers/plans/2026-07-05-research-governance-refactor.md`).

## What was archived

| Archived file | Superseded by |
|---|---|
| `thread_handoff.md` | `RESEARCH_AUDIT.md` (entry-point role) |
| `master_project_scope_lock.md` | `DECISION_LOG.md` (decisions) + `RESEARCH_OVERVIEW.md` (scope/contributions/non-goals) |
| `documentation_map.md` | `ARTIFACT_INDEX.md` (artifact inventory + policy) + `RESEARCH_AUDIT.md` (start-here role) |
| `research_mainline.md` | `RESEARCH_OVERVIEW.md` (story/claims) + `RESEARCH_QUESTIONS.md` (RQs) |
| `thesis_positioning.md` | `RESEARCH_OVERVIEW.md` |
| `experiment_protocol.md` | `EXPERIMENTS.md` (protocol) + `REPRODUCIBILITY.md` (regeneration) + `HYPOTHESES.md` (H1–H4) |
| `TASKS.md` | `TODO.md` |

## Why kept

These files are preserved for provenance. They document the scope-lock decisions, document-precedence chain, and protocol evolution that the current root-level files summarize. They may also retain internal cross-links to other archived paths; those links are intentionally left stale.

## What to read instead

Start at `RESEARCH_AUDIT.md` at the repository root, then follow its navigation map. Do not link new content to the files in this directory.

## Runtime note

`src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py` previously read `docs/experiment_protocol.md` at runtime; it now reads `EXPERIMENTS.md`. The literal string `docs/experiment_protocol.md` still appears inside some archived `reports/phak_era_archive/` JSON sources and inside this directory's own files; those are not runtime paths and are left as-is.
