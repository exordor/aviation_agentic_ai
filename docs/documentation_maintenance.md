# Documentation Maintenance Guide

This guide defines how project documents are organized and maintained. It is a
navigation and hygiene document; the research story itself lives in
`docs/research_mainline.md`.

## Current Scale

The repository currently has three documentation layers:

| Layer | Approximate size | Purpose |
| --- | ---: | --- |
| `docs/*.md` | 21 files | Stable policies, protocols, thesis framing, and project entry points. |
| `reports/stages/*` | 200+ files | Experiment outputs, stage reports, paper-analysis notes, JSON evidence, worksheets, and generated diagnostics. |
| `reports/final/*` and `reports/reviews/*` | smaller curated sets | Final deliverables, defense material, and adversarial reviews. |

This volume is expected for the current research workflow, but only a small
subset should control the thesis narrative.

## Canonical Entry Points

Use these files first, in this order:

1. `docs/documentation_map.md` for navigation.
2. `docs/thesis_positioning.md` for claim boundaries.
3. `docs/research_mainline.md` for RQs, validation gates, and SOTA positioning.
4. `docs/experiment_workflow.md` for the end-to-end experiment sequence.
5. `docs/evaluation_protocol.md` for metric definitions and no-overall-score
   policy.
6. `reports/stages/thesis_experiment_dashboard.md` for current evidence
   synthesis.
7. `reports/stages/nasa_atmonto_reviewer_defense_audit.md` and
   `reports/stages/nasa_atmonto_sota_goal_audit.md` for claim-safety gates.
8. `reports/final/README.md` before using any final-report or defense-deck
   files.

Do not use `reports/stages/index.md` as the current thesis story. It is an
artifact inventory with legacy PHAK-era material.

## Document Tiers

| Tier | Location | Examples | Maintenance rule |
| --- | --- | --- | --- |
| T0 canonical framing | `docs/` | `thesis_positioning.md`, `research_mainline.md`, `documentation_map.md` | Update when the thesis scope, RQs, claim boundaries, or entry points change. |
| T1 protocols | `docs/` | `experiment_workflow.md`, `experiment_protocol.md`, `evaluation_protocol.md`, `research_paper_analysis_protocol.md` | Update when the reproducible workflow, scoring rules, or paper-intake process changes. |
| T2 current thesis evidence | `reports/stages/` | `nasa_atmonto_formal_experiment_scoring.md`, `nasa_atmonto_s7_retrieval.md`, `thesis_experiment_dashboard.md` | Keep as generated or reviewed evidence; cite through the dashboard and documentation map. |
| T3 source/schema explainers | `reports/stages/` | `atcscc_data_format_and_processing_flow.md`, `atcscc_ontology_profile_overview.md` | Keep thesis-facing and readable; update when data/profile boundaries change. |
| T4 method migration and paper analysis | `reports/stages/`, `data/papers/README.md` | `claim_kg_graphrag_paper_adaptation.md`, `multi_agent_pipeline_method_adaptation.md` | Use for design inspiration only after full-paper/figure inspection; do not import claims directly. |
| T5 historical artifacts | `reports/stages/`, `reports/final/` | early PHAK reports, old web-demo reports, old final report drafts | Preserve for provenance, but do not let them override current ATCSCC framing. |
| T6 generated side artifacts | `reports/stages/*.json`, `.csv`, `.html`, `.log` | report JSON, review packets, worksheets, logs | Track only if they support a current dashboard/audit/chapter claim; otherwise keep under ignored output paths. |

## Where New Documents Should Go

| New material | Destination | Required follow-up |
| --- | --- | --- |
| Change to thesis scope, RQs, or contribution claims | `docs/thesis_positioning.md` and `docs/research_mainline.md` | Update `docs/documentation_map.md`. |
| Change to experiment order or regeneration commands | `docs/experiment_workflow.md` | Verify report commands remain reproducible. |
| Change to metric definitions or claim interpretation | `docs/evaluation_protocol.md` | Regenerate `reports/stages/thesis_claims_review.*` if claims are affected. |
| New source-family explanation | `reports/stages/<source>_source_brief.md` or `<source>_data_format_and_processing_flow.md` | Decide whether it is primary, reference-only, transfer-pilot, or out of scope. |
| New schema/profile explanation | `reports/stages/<source>_ontology_profile_overview.md` | State whether it is a full ontology, application profile, mapping layer, or runtime output schema. |
| New experiment result | `reports/stages/<experiment>.md` plus JSON when generated | Link it from the dashboard or leave it as secondary evidence. |
| New paper analysis | `reports/stages/<paper>_paper_analysis.md`, `<paper>_figures_analysis.md`, or `<paper>_paper_adaptation.md` | Register the paper in `data/papers/README.md` when it influences method design. |
| Final report or defense material | `reports/final/` | Ensure it cites current docs, not legacy stage index material. |
| ATCSCC final deliverable | `reports/final/atcscc_*` | Keep separate from historical PHAK-era final files. |

## Update Rules

1. If a document changes the thesis story, update the canonical docs first.
2. If a document only records an experiment output, keep it in
   `reports/stages/` and link it only when it supports a current claim.
3. If a report is superseded, do not delete it by default; mark it historical in
   `docs/documentation_map.md` or keep it unlinked from current entry points.
4. If a generated report starts creating dirty diffs on every run, fix the
   generator before treating the report as reproducible thesis evidence.
5. Keep source families separate. ATCSCC event extraction, FAA/NASA reference
   PDFs, NASR/facility data, weather data, and NASA BGA transfer pilots should
   not share one semantic F1 table.
6. Keep claim layers separate. Schema validity, semantic correctness, evidence
   support, retrieval quality, answer quality, automated diagnostics, and human
   review are different evidence types.

## Cleanup Policy

Do not delete old reports merely because they are no longer the main story.
Delete or ignore only when a file is:

- local scratch;
- large and reproducible;
- not cited by any dashboard, audit, final report, or paper-analysis record;
- superseded by a cleaner tracked report and not needed for provenance.

When in doubt, preserve the old artifact and reduce its visibility by removing
it from canonical entry points.

## Reviewer-Facing Rule

A reviewer should be able to reconstruct the thesis path using only:

```text
docs/documentation_map.md
  -> docs/thesis_positioning.md
  -> docs/research_mainline.md
  -> docs/experiment_workflow.md
  -> docs/evaluation_protocol.md
  -> reports/stages/thesis_experiment_dashboard.md
  -> reports/stages/nasa_atmonto_reviewer_defense_audit.md
```

All other reports are supporting evidence, historical context, or method
development notes.
