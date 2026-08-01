# Final Report Directory

This directory contains the current reader-facing thesis and defense-deck
outlines. It is a presentation layer, not the runtime knowledge store.

The current system truth is defined by `RESEARCH_AUDIT.md`, `GOALS.md`, and
`ARTIFACT_INDEX.md`. Historical PHAK, extraction-loop, and retired evaluation
materials are kept in the dated external archive and are not recreated here.

## Current package

| File | Purpose |
| --- | --- |
| `atcscc_thesis_report_outline.md` | Current thesis chapter, research-question, evidence, and claim-boundary spine. |
| `atcscc_defense_deck_outline.md` | Current defense-deck slide spine for the ATMONTO-grounded HybridRAG system. |
| `references.md` | Working bibliography for the current architecture and research framing. |

Generated decks, inspection dumps, and intermediate presentation files are
outside the active checkout. The old PPTX generation harness is preserved in
the dated external archive; current architecture figures are maintained under
`docs/figures/` as editable Draw.io sources and rendered PNGs.

## Maintenance rule

Keep new final material concise and current. Link to sanitized evidence under
`reports/evidence/` and to the authoritative project documents; do not copy
historical report text into this directory. When a deliverable is retired,
move it to the dated external archive rather than adding another compatibility
entry here.
