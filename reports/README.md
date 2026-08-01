# Reports

Reports are derived reader-facing or evidence-facing artifacts. They are not
the runtime knowledge store and are never required by `ask`.

| Directory | Purpose |
| --- | --- |
| `final/` | Current thesis and defense-deck outlines, plus explicitly retained presentation assets. |
| `evidence/` | Small, sanitized live-smoke reports and other reproducibility evidence listed in `ARTIFACT_INDEX.md`. |

The authoritative data layer is the dataset-bound SQLite evidence store.
FTS5, Chroma, JSONL, RDF/Turtle, and Neo4j are rebuildable views or exports.
Raw provider responses, generated decks, logs, galleries, and other large
outputs remain ignored or are kept in the dated external archive.

Use `ARTIFACT_INDEX.md` for current ownership and historical routing. Do not
recreate the retired `reports/stages/` layout.
