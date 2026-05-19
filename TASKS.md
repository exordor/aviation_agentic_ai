# Project Task Board

Last updated: 2026-05-19

This file tracks concrete execution tasks. Durable project outcomes and scope boundaries live in `GOALS.md`.

A task should be small enough to finish, verify, and check off. When a task produces evidence, attach the report or artifact path.

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Done
- `[!]` Blocked or needs decision

## Active Task Queue

1. Use the chunking and Hybrid RAG results to explain why GraphRAG helps or does not help compared with vector-only retrieval.
2. Decide whether to re-extract the KG with `structure_aware` chunks after reviewing the chunking comparison.
3. Refine gold labels from page-level to chunk/span-level evidence.
4. Implement a minimal web interface once the core pipeline has stable outputs.
5. Regenerate the AI-polished final project report after the experiment outputs are reviewed.

Related goals: G2, G3, G4, G5, G7, G8 in `GOALS.md`.

## P0 - Immediate Reproducibility Tasks

Related goals: G2, G3, G4, G5.

- [x] Create initial commit and push `main` to GitLab.
  - Evidence: GitLab remote `origin`, commit `5ccd437`.
- [x] Clean report clutter by archiving old stage reports.
  - Evidence: `reports/stages/index.md`, `reports/archive/stages/2026-05-18/`.
- [x] Generate the first AI-assisted project report draft.
  - Evidence: `reports/final/project_report.md`, `reports/final/project_report_sources.json`.
- [x] Verify local runtime and test environment.
  - Evidence: `uv run ruff check .`, `uv run pytest`.
- [x] Create an explainable curated ontology as the active KG schema.
  - Evidence: `data/ontology/curated/06_phak_ch4_0.curated.ttl`, `docs/ontology_design.md`.
  - Acceptance: curated ontology is TBox-only, has 35 classes, 9 object properties, complete label/comment coverage, and passes ontology evaluation.
- [x] Run full chunking comparison for all strategies.
  - Command: `uv run aviation-ai report chunking-comparison`
  - Evidence: `reports/stages/chunking_comparison.json`, `reports/stages/chunking_comparison.md`.
  - Result: `structure_aware` ranked first; `fixed_window` remained competitive on Recall@5 and remains the current KG-aligned strategy.
  - Acceptance: each strategy has Recall@5, MRR@5, Context Precision@5, chunk stats, and an explanation paragraph.
- [x] Run the focused KG extraction and validation workflow.
  - Commands:
    - `uv run aviation-ai chunk build`
    - `uv run aviation-ai kg extract`
    - `uv run aviation-ai kg validate`
  - Evidence: `data/kg/06_phak_ch4_0.kg.jsonl`, `data/kg/06_phak_ch4_0.kg.ttl`, `reports/stages/kg_validation.md`.
  - Acceptance: KG triples are constrained by the ontology/extraction profile, and unsupported classes/properties or missing provenance are rejected deterministically.
- [x] Build or refresh the Chroma vector index for the selected chunking strategy.
  - Command: `uv run aviation-ai index build`
  - Evidence: local ignored collection under `data/indexes/chroma`, collection `phak_ch4_chunks`.
  - Acceptance: collection name, index path, chunk path, and strategy are recorded in run manifests.
- [x] Run Hybrid RAG evaluation on the 10 boundary CQs.
  - Command: `uv run aviation-ai report hybrid-rag`
  - Evidence: `reports/stages/hybrid_rag_experiment.json`, `reports/stages/hybrid_rag_experiment.md`.
  - Result: vector Recall@5 = 1.0, graph Recall@5 = 0.8, hybrid Recall@5 = 0.9; graph/hybrid KG evidence coverage = 0.9; LLM citation completeness = 1.0 across modes.
  - Acceptance: report compares vector, graph, and hybrid/GraphRAG modes, and separates retrieval metrics, KG evidence metrics, and LLM answer metrics without a mixed total score.
- [x] Regenerate the final project report after experiment reports exist.
  - Commands:
    - `uv run aviation-ai report project --no-ai`
  - Evidence: `reports/final/project_report.md`, `reports/final/project_report_sources.json`.
  - Current scope: deterministic evidence has been refreshed; postpone `--ai` until the chunking and Hybrid RAG outputs are reviewed.
  - Acceptance: final report replaces TBD / Not yet run sections with evidence-backed results where available.

## P1 - Evaluation Quality Tasks

Related goals: G3, G4, G6, G8.

- [ ] Refine gold labels from `source_page` to chunk or span level.
  - Candidate output: `data/cqs/06_phak_ch4_0.gold.json`.
  - Acceptance: each CQ records `gold_level`, `expected_chunk_ids` or `evidence_spans`, and `key_entities` where available.
- [ ] Analyze chunking failures.
  - Acceptance: report identifies whether misses come from page boundaries, sentence breaks, section structure, or embedding mismatch.
- [ ] Analyze GraphRAG tradeoffs.
  - Current evidence: hybrid improved graph Recall@5 by +0.1 but trailed vector-only Recall@5 by -0.1; graph/hybrid modes added KG evidence coverage that vector-only did not provide.
  - Acceptance: report explains when graph retrieval improves evidence coverage, when vector retrieval is sufficient, and when KG sparsity limits hybrid gains.
- [ ] Select the default chunking strategy for the next project phase.
  - Current candidate: `structure_aware` for future KG re-extraction; keep `fixed_window` for the current Hybrid RAG report because KG triples reference fixed-window chunk ids.
  - Acceptance: decision is justified by retrieval metrics plus chunk cost/stability, not Recall alone.
- [ ] Review KG extraction failure cases.
  - Acceptance: unsupported triples, weak evidence, missing provenance, and key-entity coverage gaps are summarized.
- [ ] Confirm citation completeness on LLM answers.
  - Acceptance: each accepted answer cites at least one valid chunk/page/triple source or abstains when evidence is insufficient.

## P2 - Final Submission Tasks

Related goals: G1, G5, G6, G7, G8.

- [ ] Update `README.md` after real experiment results are available.
  - Acceptance: README no longer points to archived stage filenames as if they were current files.
- [ ] Complete `reports/final/project_report.md`.
  - Acceptance: includes motivation, architecture, ontology design, KG deliverable, GraphRAG pipeline, chunking comparison, vector/graph/hybrid analysis, limitations, advisory boundary, and reproducibility appendix.
- [ ] Add a project-defense section or note.
  - Candidate output: `reports/final/project_defense_notes.md`.
  - Acceptance: answers what was built, why ontology is needed, why KG is a deliverable, why GraphRAG is used, why chunking strategies are compared, and where the system can fail.
- [ ] Implement a minimal web interface demonstrator.
  - Candidate scope: ask-question page, retrieval mode selector, answer panel, citation/evidence panel, KG triple evidence panel, advisory boundary notice.
  - Acceptance: reviewer can run it locally and see the pipeline output without reading raw JSON reports.
- [ ] Add web interface run instructions and screenshots or smoke-test evidence.
  - Acceptance: README or final report explains how to start the interface and what each UI section demonstrates.
- [ ] Review `THIRD_PARTY.md` and license attribution.
  - Acceptance: all copied/adapted external assets and papers are attributed; generated local artifacts are clearly identified.
- [ ] Run final quality gate before submission.
  - Commands:
    - `uv run ruff check .`
    - `uv run pytest`
    - `git status --short`
  - Acceptance: checks pass and only intentional files are changed.

## P3 - Automation And GitLab Tasks

Related goals: G5.

- [ ] Add GitLab CI for `ruff` and `pytest`.
  - Candidate output: `.gitlab-ci.yml`.
  - Acceptance: pipeline runs on `main` and merge requests without requiring local secrets.
- [ ] Add optional GitLab API helper commands.
  - Candidate scope: auth check, project check, issue creation, pipeline status, report publishing.
  - Acceptance: uses `.env` token locally, never prints token, and tests mock HTTP calls.
- [ ] Use GitLab issues or milestones to mirror this task board if stronger tracking is needed.
  - Acceptance: repo-local `TASKS.md` remains the source of truth, or a clear sync policy is documented.

## Maintenance Rules

- Do not commit `.env`, local Chroma indexes, model caches, or generated temporary files.
- Keep `reports/stages/` as a dashboard entrypoint; archive detailed stage artifacts with `aviation-ai report hygiene --apply`.
- Every completed experiment should leave a JSON report, Markdown report, and run manifest.
- Do not claim advisory assistant capability beyond aviation learning and decision support.
