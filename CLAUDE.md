# CLAUDE.md

Compatibility instructions for tools that read this file.

`AGENTS.md` is authoritative. For current project context, read:

1. `RESEARCH_AUDIT.md`
2. `GOALS.md`
3. the task-specific design or interface document

Do not preload archived experiments, historical stage reports, ignored batch
snapshots/provider outputs, or the paused browser prototype.

## Authority Boundary

This file is only a compatibility pointer. Do not duplicate changing project
status, dataset counts, provider results, or architecture details here.
Use `RESEARCH_AUDIT.md` for current implementation truth, `GOALS.md` for
durable goals and non-goals, `README.md` for the public entry point, and
`docs/multi_agent_kg_system_design.md` for normative architecture.

## Repository Rules

- Keep workflows CLI-first and reproducible.
- Keep source families and evidence roles distinct.
- Treat schema validity, evidence support, canonical identity, and reviewed
  semantic correctness as different claims.
- Preserve unrelated user changes and generated artifacts.
- Keep credentials, model caches, local corpora, and provider output out of Git.
- Use tracked-file scans for current-context hygiene.

## Verification

- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
