# Final Report Directory

This directory contains final-style deliverables from multiple project phases.
It is not the canonical entry point for the current thesis story.

For the current ATCSCC thesis route, start with:

1. `docs/documentation_map.md`
2. `docs/thesis_positioning.md`
3. `docs/research_mainline.md`
4. `docs/experiment_workflow.md`
5. `reports/stages/thesis_experiment_dashboard.md`
6. `reports/stages/nasa_atmonto_reviewer_defense_audit.md`

## Current Status

The current thesis direction is:

> Schema-constrained, evidence-grounded Agentic KG-RAG over retrospective FAA
> ATCSCC advisories.

The final deliverables in this directory mostly predate that framing. They
should be treated as historical or transitional outputs unless a new ATCSCC
final-report pass explicitly regenerates or replaces them.

## File Classification

| File | Status | Notes |
| --- | --- | --- |
| `atcscc_thesis_report_outline.md` | current ATCSCC thesis outline | Use as the current final-package starting point. It maps chapters, RQs, figures, tables, and claim boundaries to current ATCSCC evidence. |
| `project_report.md` | transitional, not final thesis manuscript | Generated from the thesis dashboard and now includes ATCSCC evidence, but still opens with aviation-training / PHAK framing. Use only as a source of reusable sections after manual review. |
| `project_report_sources.json` | provenance for transitional report | Large generated source pack. Keep for provenance, not as a reading entry point. |
| `project_academic_report.md` | historical PHAK-era final draft | Focuses on FAA PHAK Chapter 4, curated ontology, and the original handbook GraphRAG prototype. Do not cite as the current ATCSCC thesis story. |
| `project_academic_report_sources.json` | provenance for historical academic report | Source pack for the PHAK-era academic report. |
| `project_defense_notes.md` | historical PHAK-era defense notes | Useful as a presentation-format reference only. The content does not match the current ATCSCC thesis route. |
| `project_defense_notes.json` | structured source for historical defense notes | Keep for reproducibility of the old defense notes. |
| `defense_deck_outline.md` | historical PHAK-era deck outline | Useful as a slide-structure reference only. It should not be used for the current ATCSCC defense without rewriting. |
| `aviation_graphrag_defense_deck.pptx` | historical PHAK-era deck | Large binary deck. Keep for provenance and design reference, not current thesis submission. |
| `aviation_graphrag_defense_deck_sources.json` | provenance for historical deck | Source pack for the old deck. |
| `assets/*` | historical visual assets | Mostly PHAK/web-demo presentation assets. Reuse only if the figure still matches the ATCSCC method story. |

## Next ATCSCC Final-Package Target

The next final package should continue as a separate ATCSCC-focused set,
instead of editing the PHAK-era deliverables in place:

| Target | Target file |
| --- | --- |
| Thesis-facing report skeleton | `reports/final/atcscc_thesis_report_outline.md` |
| Defense deck outline | `reports/final/atcscc_defense_deck_outline.md` |
| Figure asset manifest | `reports/final/atcscc_visual_assets_manifest.json` |
| Source pack | `reports/final/atcscc_thesis_report_sources.json` |

The package should cite the current stage evidence, not `reports/stages/index.md`
or the old PHAK reports as primary sources.

## Cleanup Policy

Do not delete these historical final outputs by default. They are useful for
provenance, presentation patterns, and comparison with earlier project phases.
Instead:

- keep this README as the directory-level warning;
- create new ATCSCC-named final files for the current thesis;
- move old outputs to an archive only if the user explicitly asks for a physical
  cleanup;
- do not commit new large binary assets unless they are used by a current
  ATCSCC final deliverable.
