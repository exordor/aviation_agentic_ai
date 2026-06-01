# Third-Party Sources and Integration Policy

This project is designed as an original GitLab-submittable research prototype.
External repositories are not vendored into the source tree. Small browser
runtime libraries may be vendored as static distribution files when needed for
offline demo behavior and must be attributed below.

## Reference Projects

### FAA Pilot's Handbook of Aeronautical Knowledge

- Local source excerpt:
  `data/raw/06_phak_ch4_0.pdf`
- Source type:
  FAA handbook chapter excerpt used as the bounded corpus for coursework
  experiments.
- Use in this project:
  - Input document for chunking, ontology-grounded KG extraction, vector
    indexing, GraphRAG retrieval, and evaluation.
  - The project stores derived chunks, KG triples, and reports with provenance
    back to source pages/chunks.
- Integration rule:
  - Keep the source scope explicit in reports.
  - Do not claim coverage beyond the included PHAK Chapter 4 excerpt.

### Towards Automated Ontology Generation from Unstructured Text

- Local reference paper:
  `data/papers/towards-automated-ontology-generation-multi-agent-llm.pdf`
- Title:
  "Towards Automated Ontology Generation from Unstructured Text: A Multi-Agent
  LLM Approach"
- Authors:
  Abid Talukder, Maruf Ahmed Mridul, and Oshani Seneviratne
- Associated GitHub repository:
  https://github.com/brains-group/towards_automated_ontology_generation
- Use in this project:
  - Primary methodology reference for automated ontology generation.
  - Inspires the CQ-driven, artifact-oriented generation flow used by this
    project.
  - The associated open-source GitHub implementation is used as the basis for
    the project-owned ontology generation code, adapted for aviation training
    text.
  - The project adapts the general method to aviation training text rather than
    insurance contracts.

### `towards_automated_ontology_generation`

- Upstream repository:
  https://github.com/brains-group/towards_automated_ontology_generation
- Local reference path during development:
  `../Aviation/towards_automated_ontology_generation`
- Use in this project:
  - Source implementation basis for CQ generation and multi-agent ontology
    generation, modified and simplified into project-owned modules under
    `src/aviation_agentic_ai/ontology/`.
  - Source of the curated baseline PHAK ontology copied to
    `data/ontology/baseline/06_phak_ch4_0.ttl`.
  - Source of the PHAK Chapter 4 PDF if needed.
- Integration rule:
  - Adapt small modules only when needed and keep the adapted implementation
    clearly project-owned.
  - Do not vendor the full repository.
  - Preserve license/copyright headers if any source code is copied.

### `automatic-KG-creation-with-LLM`

- Local reference path during development:
  `../Aviation/automatic-KG-creation-with-LLM`
- License: Apache License 2.0, as declared by the source project.
- Use in this project:
  - Methodology reference for CQ-driven KG construction.
  - No full-repository vendoring.

### OntoGPT

- Upstream project: https://github.com/monarch-initiative/ontogpt
- License: BSD-3-Clause, as declared by the upstream project.
- Use in this project:
  - Optional dependency and reference design for ontology-grounded extraction.
  - If used directly, wrap it behind project-owned interfaces.
  - If source/templates are copied or adapted, document the copied files and preserve attribution.

## Generated Presentation Assets

### AI-Generated Explanatory Images

- Local generated assets:
  `reports/final/assets/*_ai.png`
- Local deterministic fallbacks:
  `reports/final/assets/*.svg`
- Manifest:
  `reports/final/assets/visual_assets_manifest.json`
- Use in this project:
  - Presentation-only visuals for the final academic defense deck.
  - They illustrate the project pipeline, KG evidence, and web demo narrative.
- Integration rule:
  - Metrics, labels, source citations, and artifact paths remain editable PPT
    objects backed by local reports.
  - The manifest records whether AI PNG assets are present but never records
    API keys, tokens, gateway credentials, or private endpoint URLs.

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
  `data/ontology/external/icarus_ontology/`
- Use in this project:
  - ATM ontology reference used in ATMONTO experiment and minimal-loop scripts.
  - Referenced by `atmonto_minimal_loop.py` and `atmonto_experiment.py`.

### AIRM-O Ontology

- Source:
  https://github.com/airm-o/airm-o (CC-BY-4.0)
- Local:
  `data/ontology/external/airm_o/`
- Use in this project:
  - ATM Information Reference Model ontology used as external reference.
  - Referenced by `airm_o.py`.

### NASA Beginner's Guide to Aeronautics (BGA)

- Source:
  https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/
- Source type:
  NASA educational web resource covering aerodynamics principles.
- Use in this project:
  - Web source material for aerodynamics ontology extraction.

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
