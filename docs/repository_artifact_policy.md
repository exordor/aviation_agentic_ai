# Repository Artifact Policy

Last updated: 2026-08-01

The repository contains the runnable system and the small set of tracked
artifacts needed to reproduce its current claims. Historical plans, review
trails, and retired evaluation material are not runtime dependencies and do
not belong in the default checkout.

## Current checkout

Keep these categories in Git:

- source code, tests, configuration, and semantic profiles;
- current architecture and reproducibility documentation;
- the current sanitized evaluation contracts and reports listed in
  `ARTIFACT_INDEX.md`;
- small source metadata needed by the supported ingestion commands.

SQLite stores, Chroma indexes, provider traces, raw model responses, and
generated export packages stay outside Git under the paths documented in
`AGENTS.md` and `ARTIFACT_INDEX.md`.

## External historical archive

The 2026-08-01 cleanup moved the following material to the sibling workspace
directory:

```text
../aviation_agentic_ai-research-archive-2026-08-01/
├── reports/phak_era_archive/
├── docs/archive/
├── docs/superpowers/
├── reports/stages/                 # superseded live v2 reports
└── data/evaluation/agent_system/   # superseded v2/v3 contracts
```

The archive is a local research-history backup, not an import path and not a
runtime source of truth. Its files are preserved byte-for-byte and remain
recoverable from Git history as well. Historical code that still names an
archived path is not part of the supported root CLI; restore the relevant
archive subtree only when deliberately running that legacy experiment.

## Retention rule

When a new report or plan is produced, first decide whether it is:

1. current reproducibility evidence;
2. a small reader-facing design reference;
3. ignored generated output; or
4. historical material for the external archive.

Only the first two categories should be committed by default. A report must
not become part of the runtime simply because a historical script writes to
the same directory. The canonical data layer remains the SQLite evidence
store; indexes and exports are rebuildable views.

## Scope of this cleanup

This phase removes non-runtime history without retiring the legacy ontology
and reporting modules that still have direct test fixtures. A later, explicit
legacy-module retirement can remove their source/data dependencies together;
that is a separate change and must not be inferred from this archive move.
