# CLAUDE.md

Compatibility instructions for tools that read this file.

This file does not define a separate project scope. Use `AGENTS.md` as the
authoritative repository instruction file, then start new work from:

1. `docs/thread_handoff.md`
2. `docs/documentation_map.md`
3. `docs/context_hygiene_audit.md`
4. `docs/tracked_context_inventory.md`

## Current Scope

The current thesis line is schema-constrained, evidence-grounded Agentic KG-RAG
over retrospective FAA ATCSCC advisories.

Do not use older PHAK, web-demo, chunking-era, or historical final-report
documents as the thesis entry point unless the task explicitly asks for
historical comparison.

## Repository Rules

- Keep workflows CLI-first and reproducible.
- Keep source families separate: ATCSCC advisories, FAA/NASA references,
  NASR/facility data, weather data, and transfer pilots need separate profiles
  and metrics unless a current document says otherwise.
- Treat completeness and correctness as task-relative: CQ coverage,
  source-observable field coverage, schema/profile validity, evidence support,
  and reviewed-subset correctness are different claims.
- Do not vendor external repositories, nested Git repositories, or copied
  `.git` directories.
- Keep generated indexes, model caches, credentials, scratch outputs, raw local
  snapshots, and local paper PDFs out of Git unless a tracked document explains
  why they are submission evidence.

## Verification

- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Context-hygiene scans should use `git grep` over tracked files.
