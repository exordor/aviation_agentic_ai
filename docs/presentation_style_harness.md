# Presentation Style Harness

This project uses the TU Clausthal 16:9 template for reviewer-facing decks.
Generated PPT files must preserve the template chrome and avoid presentation
anti-patterns that repeatedly appeared during deck iteration.

## Command

```bash
python3 scripts/validate_ppt_style.py
```

By default, the harness checks:

```text
reports/final/atcscc_agent_kg_ontology_tu_figures.pptx
```

To check another deck:

```bash
python3 scripts/validate_ppt_style.py path/to/deck.pptx
```

## Current Rules

The harness inspects PPTX OOXML directly and checks:

- the project-local TU Clausthal template exists;
- no `.pptx.inspect.ndjson` sidecar remains next to the final deck;
- each slide keeps the right grey sidebar;
- each slide keeps footer text and page marker;
- each slide's largest action/title text uses TU green `#008C4F`;
- slide titles follow reviewer-facing academic title rules:
  - use action titles, not topic labels such as `Results`, `Method`, or
    `Architecture`;
  - use sentence case, not all caps;
  - stay within 85 characters;
  - contain at least five words, so the title carries a claim rather than a
    bare topic label;
  - do not end with a period;
  - do not expose file paths, artifact names, dashboard/stage wording, or
    implementation-oriented filenames;
- long grey generated text is rejected, because detailed explanation belongs in
  speaker notes, not visible slide captions;
- internal stage labels such as `S7` do not appear in reviewer-facing slide text.
- text-only slides use the school-style list pattern: no rounded-card layout,
  3-5 bullets, body text at least 20 pt equivalent, and no overlong bullet
  sentences.

The harness is a style gate, not a replacement for rendered visual QA. After it
passes, still inspect rendered slide previews for overflow, weak diagrams, and
readability at presentation scale.

## Template Source

The template reference is kept at:

```text
reports/final/templates/TU-Clausthal-Powerpoint16zu9-ohneStone.potx
```

Do not approximate this template by memory. Use the project-local template when
generating or revising reviewer-facing PPT files.
