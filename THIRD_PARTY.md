# Third-Party Sources and Integration Policy

This project is designed as an original GitLab-submittable research prototype.
External repositories are not vendored into the source tree.

## Reference Projects

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

## Artifact Policy

Commit source code, configs, curated sample data, tests, and final reports.
Do not commit virtual environments, API keys, vector indexes, downloaded models,
external repositories, temporary logs, or generated caches.
