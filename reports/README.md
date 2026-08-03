# Reports

Reports are derived reader-facing or evidence-facing artifacts. They are not
the runtime knowledge store and are never required by `ask`.

| Directory | Purpose |
| --- | --- |
| `final/` | Current thesis and defense-deck outlines, plus explicitly retained presentation assets. |
| `evidence/` | Small, sanitized live-smoke reports and other reproducibility evidence listed in `RESEARCH_AUDIT.md`. |

The authoritative data layer is the dataset-bound SQLite evidence store.
FTS5, Chroma, JSONL, RDF/Turtle, and Neo4j are rebuildable views or exports.
Raw provider responses, generated decks, logs, galleries, and other large
outputs remain ignored or are kept in the dated external archive.

Use `RESEARCH_AUDIT.md` for current evidence status and
`docs/repository_artifact_policy.md` for historical routing. Do not recreate
the retired `reports/stages/` layout.
