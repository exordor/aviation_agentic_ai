# Final Report Directory

This directory contains the current ATCSCC report and defense-deck spines,
plus explicitly historical presentation material. The current system truth is
defined by `RESEARCH_AUDIT.md`, `GOALS.md`, and the normative design.

Start with the repository-root `RESEARCH_AUDIT.md`, `GOALS.md`, and
`ARTIFACT_INDEX.md`. Files below retain their recorded wording and bytes for
provenance; none is current merely because it is stored under `reports/final/`.

## File Classification

| File | Status | Notes |
| --- | --- | --- |
| `atcscc_thesis_report_outline.md` | current ATCSCC thesis report spine | Current chapter, research-question, evidence, and claim-boundary outline for the ingestion-first system. |
| `atcscc_defense_deck_outline.md` | current ATCSCC defense deck spine | Current slide outline for the five-plane architecture, Query Agent, evidence boundaries, and observed evaluation status. |
| `project_report.md` | historical/transitional report | Retained for provenance; it is not the current thesis narrative. |
| `project_report_sources.json` | provenance for transitional report | Large generated source pack. Keep for provenance, not as a reading entry point. Do not load it as current narrative context. |
| `project_academic_report.md` | historical PHAK-era final draft | Focuses on FAA PHAK Chapter 4, curated ontology, and the original handbook GraphRAG prototype. Do not cite as the current ATCSCC thesis story. |
| `project_academic_report_sources.json` | provenance for historical academic report | Source pack for the PHAK-era academic report. Do not load it as current narrative context. |
| `project_defense_notes.md` | historical PHAK-era defense notes | Presentation-format reference only. |
| `project_defense_notes.json` | structured source for historical defense notes | Keep for reproducibility of the old defense notes. |
| `defense_deck_outline.md` | historical PHAK-era deck outline | Slide-structure reference only; not current content. |
| external archive `reports/legacy_runtime/atcscc_agent_plan_storyboard.md` | historical extraction-loop storyboard | Superseded by the current Query Agent and ingestion-first architecture. |
| external archive `reports/legacy_runtime/figure_descriptions.md` | historical figure specifications | Contains superseded extractor/validator/refiner/critic and Gold-sample wording. |
| `aviation_graphrag_defense_deck.pptx` | historical PHAK-era deck | Large binary deck. Keep for provenance and design reference, not current thesis submission. |
| `aviation_graphrag_defense_deck_sources.json` | provenance for historical deck | Source pack for the old deck. Do not load it as current narrative context. |
| `assets/*` | historical figures | Mostly PHAK/web-demo presentation assets. Some legacy filenames preserve earlier asset labels; reuse only if the figure still matches the ATCSCC method story. |

## Current ATCSCC Final Package

The current package is intentionally separate from the PHAK-era deliverables:

| Target | Target file |
| --- | --- |
| Thesis-facing report spine | `reports/final/atcscc_thesis_report_outline.md` |
| Defense deck outline | `reports/final/atcscc_defense_deck_outline.md` |
| Current evidence router | `RESEARCH_AUDIT.md`, `GOALS.md`, `ARTIFACT_INDEX.md` |

The package cites the current implementation and sanitized stage evidence. It
does not treat historical PHAK reports, old extraction-loop plans, or the
retired competency runner as current system evidence.

## Cleanup Policy

Historical final outputs remain available in the dated external archive when
they describe a retired pipeline. They are useful for provenance and
comparison with earlier project phases. For the remaining files:

- keep this README as the directory-level warning;
- create new ATCSCC-named final files for the current thesis;
- do not commit new large binary assets unless they are used by a current
  ATCSCC final deliverable.
