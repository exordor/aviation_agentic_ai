# CLAUDE.md

Development constraints for coding agents working on this repository.

## Project Intent

This repository is a standalone, GitLab-submittable research prototype for
aviation ontology generation, focused KG/ABox construction, and GraphRAG
retrieval. Keep the project clearly original, reproducible, and easy to review.

The current priority is a clean CLI-first Python project. Do not build a web API
or UI unless the project plan is explicitly changed.

## Repository Boundaries

- Treat `.` as the project root.
- Treat `../Aviation` as a read-only reference/source-of-assets repo.
- Do not vendor full external repositories into this project.
- Do not create nested git repositories, git submodules, or copied `.git`
  directories.
- If external code is needed, prefer a package dependency in `pyproject.toml`.
- If small code fragments are copied or adapted, preserve license headers where
  present and update `THIRD_PARTY.md`.

## Third-Party Integration Rules

Use these defaults unless a maintainer explicitly decides otherwise:

- `towards_automated_ontology_generation`: reference architecture and selective
  source for adapted ontology-generation modules only.
- `automatic-KG-creation-with-LLM`: methodology reference only; reimplement KG
  extraction in this project with provenance and validation.
- OntoGPT: optional dependency or reference design; wrap direct usage behind
  project-owned interfaces.

Never submit a repository that is mostly cloned external code.

## Artifact Policy

Commit:

- source code under `src/`
- tests under `tests/`
- configs under `configs/`
- curated sample inputs in `data/raw/`
- related research papers and notes in `data/papers/`
- curated baseline ontology files in `data/ontology/baseline/`
- small, intentional report artifacts under `reports/`
- `uv.lock`

Do not commit:

- `.env`
- `.venv/`
- API keys, tokens, credentials, or private endpoints
- model weights or downloaded model caches
- vector indexes and generated retrieval databases
- temporary logs, caches, or scratch outputs
- raw cloned external repositories

If a generated artifact is required for the final submission, document why in
`README.md` or the relevant report.

## Architecture Constraints

- Keep public workflows behind the `aviation-ai` CLI.
- Keep modules small and purpose-specific:
  - `ontology/`: CQ generation, ontology generation, validation, statistics
  - `kg/`: ABox extraction, RDF materialization, provenance, KG validation
  - `chunking/`: PDF text extraction and stable chunk generation
  - `retrieval/`: GraphRAG, vector RAG, hybrid retrieval
  - `evaluation/`: retrieval and answer-quality evaluation
  - `reporting/`: Markdown/JSON report generation
  - `llm/`: provider configuration and LLM wrappers
- Keep paths config-driven. Avoid hardcoded absolute paths in code,
  configuration, documentation, and generated artifacts.
- Use RDFLib for RDF/Turtle parsing and validation in the first prototype.
- Keep FastAPI or other service layers out of the first implementation.

## Ontology And KG Constraints

- The baseline PHAK ontology is
  `data/ontology/baseline/06_phak_ch4_0.ttl`.
- Generated ontologies should go under `data/ontology/generated/`.
- Do not overwrite curated baseline artifacts.
- For ABox extraction, use `configs/extraction_profile.yaml` as the source of
  truth for instantiable classes and relation properties.
- Treat unlisted ontology classes as schema-only for v1.
- Every extracted KG triple must have provenance that includes:
  - source document
  - page or section when available
  - chunk id
  - evidence text
  - extraction model
  - confidence
  - extraction timestamp
  - subject, predicate, object

## GraphRAG Constraints

- Graph retrieval must operate over validated KG artifacts.
- Vector retrieval must use stable chunk ids and metadata.
- Hybrid retrieval must normalize or rank-fuse scores. Do not add raw graph
  scores and raw vector cosine scores directly.
- Answers must cite source chunks or provenance records when possible.

## Dependency Constraints

- Manage dependencies through `pyproject.toml`.
- Keep heavy capabilities optional:
  - ontology-generation dependencies under `ontology-generation`
  - vector/GraphRAG dependencies under `graphrag`
  - OntoGPT under `ontogpt`
- Do not add dependencies only for convenience if the standard library or current
  dependencies are sufficient.

## Coding Standards

- Target Python 3.10+.
- Prefer typed functions for project-owned modules.
- Keep CLI commands deterministic and scriptable.
- Use JSON and Markdown for report outputs.
- Avoid hidden network calls in validation, reporting, and tests.
- LLM calls must be explicit and configured through environment variables or
  config files.
- Do not read `.env` values in tests unless the test explicitly mocks them.

## Testing And Verification

Before handing off changes, run:

```bash
uv run ruff check .
uv run pytest
```

For ontology-related changes, also run:

```bash
uv run aviation-ai ontology validate
uv run aviation-ai ontology report
```

Tests should not require OpenAI, DeepSeek, vLLM, OntoGPT, ChromaDB, FAISS, or
sentence-transformers unless marked as optional/manual.

## GitLab Submission Expectations

- Keep the default branch clean and reviewable.
- Keep the README setup instructions accurate.
- Keep `THIRD_PARTY.md` current whenever external code, templates, or ideas are
  materially adapted.
- Ensure `.gitignore` prevents accidental submission of credentials, virtual
  environments, indexes, caches, and model artifacts.
- Prefer small, meaningful commits grouped by subsystem.
