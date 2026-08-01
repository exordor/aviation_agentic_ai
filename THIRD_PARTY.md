# Third-Party Sources and Integration Policy

This project is designed as an original GitLab-submittable research prototype.
External repositories are not vendored into the source tree. Small browser
runtime libraries may be vendored as static distribution files when needed for
offline demo behavior and must be attributed below.

## Reference Projects

### Retired coursework and ontology-generation inputs

The former PHAK chunking/KG pipeline, ontology-generation experiments, and
their local PDFs/derived files are preserved in the dated external archive at
`../aviation_agentic_ai-research-archive-2026-08-01/`. They are historical
research material, not dependencies of the active ingestion-first runtime.

The active system uses a curated ATMONTO application profile and six pinned
NASA OWL authority files. It does not depend on OntoGPT, the former
ontology-generation extra, or a PHAK bounded corpus.

## Runtime And Tooling Dependencies

- ChromaDB is used as a local vector index backend; generated collections under
  `data/indexes/chroma` are ignored and not committed.
- FastAPI and Uvicorn are optional web-demo dependencies; the offline smoke
  report uses FastAPI TestClient and does not call the LLM.
- Cytoscape.js 3.33.4 is vendored as
  `src/aviation_agentic_ai/web/static/vendor/cytoscape.min.js` with its MIT
  license at `src/aviation_agentic_ai/web/static/vendor/cytoscape.LICENSE.txt`.
  It powers the offline KG relationship graph's node dragging, pan/zoom, and
  edge-selection interactions without requiring a CDN.
- The Presentations runtime is used to build the editable PPTX under
  `reports/final/`; scratch render/check files are kept under ignored
  `outputs/`.

## Artifact Policy

Commit source code, configs, curated sample data, tests, and final reports.
Do not commit virtual environments, API keys, vector indexes, downloaded models,
external repositories, temporary logs, or generated caches.

### ICARUS Ontology / NASA ATMONTO

- Source:
  https://github.com/UCY-LINC-LAB/icarus-ontology (MIT License)
- Local:
  `data/ontology/external/icarus_ontology/NASA/`
- Use in this project:
  - Six NASA OWL modules are checksum-pinned by the active application profile
    and provide ATMONTO TBox authority for publication and retrieval labels.
  - They are reference inputs, not an imported ATMGRAPH dataset or a complete
    aviation ontology.

### Additional Research Papers

- Local reference papers in `data/papers/`:
  - `2404.16130v2.pdf` — LLM-based ontology construction survey.
  - `stefanidis_2020_icarus_ontology.pdf` — ICARUS ontology methodology.
  - `Building a Knowledge Graph for the Air Traffic Management Community.pdf` —
    ATM KG reference.
  - `Paper_17-An_Improvement_for_Spatial_Temporal_Queries_of_ATMGRAPH.pdf` —
    ATMGRAPH spatial-temporal query reference.

## Presentation Generation

### PPTX Generation Script

- Local script:
  `scripts/build_defense_deck.mjs`
- Use in this project:
  - Generates the thesis defense deck as an editable PPTX under `reports/final/`.
  - Uses the Presentations runtime for PPTX construction.
