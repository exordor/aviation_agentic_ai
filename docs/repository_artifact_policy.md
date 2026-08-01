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
├── reports/stages/                 # superseded live v2 reports and old literature summaries
├── reports/legacy_runtime/         # retired extraction and cross-source reports
├── src/legacy_runtime/             # retired packages and root CLI wrappers
├── tests/legacy_runtime/           # tests for retired packages
├── scripts/legacy_runtime/         # retired experiment runners
└── data/legacy_runtime/            # retired evaluation inputs
```

The 2026-08-01 archive also contains the following completed cleanup groups:

- `configs/legacy_runtime/extraction_profile.yaml` and
  `data/legacy_runtime/phak_bga/`: retired PHAK/BGA extraction inputs and
  fixtures;
- `data/legacy_runtime/nasa_atmonto/extraction/2026-05-14/`: old ATCSCC
  extraction output, together with the superseded extraction-era catalogs
  under `data/legacy_runtime/nasa_atmonto/curated/`;
- `reports/legacy_runtime/atcscc/`: old ATCSCC extraction, validation, and
  stage reports;
- `docs/legacy_runtime/atcscc_decision_record_explorer_*.md`,
  `templates/legacy_runtime/agentic_artifact_contract.md`, and the two
  archived report specifications under `reports/legacy_runtime/`: the
  retired artifact-per-role extraction and run-artifact explorer design;
- `data/legacy_runtime/agent_system/` and
  `reports/legacy_runtime/agent_system/`: retired live-agent compatibility
  contracts and sanitized reports;
- `src/legacy_runtime/agent_system/` and
  `tests/legacy_runtime/agent_system/`: the dedicated compatibility harness
  and tests moved with those reports so the active package has no broken
  historical-test dependencies.

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

The legacy-module retirement is complete for the active checkout. The old
root command wrappers, extraction/reporting packages, cross-source experiment
packages, and their dedicated tests/scripts are kept only in the dated
external archive. The archive is not on `PYTHONPATH` and is never a runtime
source of truth.

The six NASA ATMONTO OWL files pinned by the active application profile remain
in the checkout, together with the curated schema slices. Other external
ontology copies and old evaluation inputs are historical archive material.
