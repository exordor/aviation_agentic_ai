# Project Task Board

Last updated: 2026-05-26

This file tracks concrete execution tasks. Durable project outcomes and scope boundaries live in `GOALS.md`.

A task should be small enough to finish, verify, and check off. When a task produces evidence, attach the report or artifact path.

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Done
- `[!]` Blocked or needs decision

## Active Task Queue

1. Review `reports/stages/evidence_cards.md` and use the per-question failure categories to decide which hybrid fusion dilution cases need tuning or manual gold-label refinement.
2. Add embedding/index backend comparison after retrieval ablation results are reviewed.
3. If needed, rerun Hybrid RAG answer generation on the expanded gold labels instead of only the original 10 CQ answer set.
4. Strengthen robustness abstention behavior, because the first deterministic robustness run has abstention correctness = 0.6.
5. Decide whether to expose the expanded evaluation suite and evidence cards in the web demo or keep them as report-only evidence.

Related goals: G2, G3, G4, G6, G8, G9 in `GOALS.md`.

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
- [x] Run GraphRAG review for the fixed-window baseline.
  - Command: `uv run aviation-ai report graphrag-review`
  - Evidence: `reports/stages/graphrag_review.json`, `reports/stages/graphrag_review.md`.
  - Result: GraphRAG value is framed as structured KG evidence coverage, not fixed-window page-level Recall@5 lift over vector-only retrieval.
- [x] Re-extract KG and rerun Hybrid RAG with `structure_aware` chunks.
  - Commands:
    - `uv run aviation-ai kg extract --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --ttl-output data/kg/06_phak_ch4_0.structure_aware.kg.ttl`
    - `uv run aviation-ai kg validate --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output-dir reports/stages --report-name structure_aware_kg_validation`
    - `uv run aviation-ai index build --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --collection-name phak_ch4_chunks_structure_aware`
    - `uv run aviation-ai report hybrid-rag --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --collection-name phak_ch4_chunks_structure_aware --chunking-strategy structure_aware --report-name hybrid_rag_structure_aware`
  - Evidence: `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl`, `data/kg/06_phak_ch4_0.structure_aware.kg.ttl`, `reports/stages/structure_aware_kg_validation.md`, `reports/stages/hybrid_rag_structure_aware.md`.
  - Result: structure-aware KG has 448 validated triples; structure-aware Hybrid RAG has vector Recall@5 = 1.0, graph Recall@5 = 0.9, hybrid Recall@5 = 1.0, and graph/hybrid KG evidence coverage = 0.9.
- [x] Regenerate the final project report after experiment reports exist.
  - Commands:
    - `uv run aviation-ai report project --no-ai`
  - Evidence: `reports/final/project_report.md`, `reports/final/project_report_sources.json`.
  - Current scope: deterministic evidence has been refreshed; postpone `--ai` until the chunking and Hybrid RAG outputs are reviewed.
  - Acceptance: final report replaces TBD / Not yet run sections with evidence-backed results where available.
- [x] Generate draft chunk/span gold labels and evidence-level evaluation.
  - Commands:
    - `uv run aviation-ai cqs gold-draft`
    - `uv run aviation-ai report evidence-eval`
    - `uv run aviation-ai report graphrag-review`
  - Evidence: `data/cqs/06_phak_ch4_0.gold.json`, `reports/stages/evidence_level_evaluation.md`, `reports/stages/graphrag_review.md`.
  - Result: gold labels are now marked `manual_reviewed`; structure-aware hybrid has Chunk Recall@5 = 1.0, Span hit rate = 0.7, KG triple relevance = 0.9, citation validity = 1.0, and 9 supported answers; fixed-window hybrid has 8 supported answers.
  - Acceptance: evidence-level metrics remain layered and do not create a mixed overall score.
- [x] Write final evaluation and submission-readiness review.
  - Commands:
    - `uv run aviation-ai report final-evaluation`
    - `uv run aviation-ai report web-demo-smoke`
  - Evidence: `reports/stages/final_evaluation_review.md`, `reports/stages/web_demo_final_smoke.md`.
  - Result: `structure_aware` is selected as the default demo and next-phase GraphRAG strategy; fixed-window remains the baseline. Web smoke checks passed for static HTML, status/explanation/questions/detail APIs, KG graph, live-query lockout, and favicon.
  - Acceptance: final review separates strategy decision, chunking failures, KG/evidence failures, and citation completeness without a mixed total score.

## P1 - Evaluation Quality Tasks

Related goals: G3, G4, G6, G8.

- [x] Refine gold labels from `source_page` to chunk or span level.
  - Candidate output: `data/cqs/06_phak_ch4_0.gold.json`.
  - Current evidence: `data/cqs/06_phak_ch4_0.gold.json` is marked `manual_reviewed` with span-level labels for all 10 boundary CQs.
  - Acceptance: each CQ records `gold_level`, `expected_chunk_ids` or `evidence_spans`, and `key_entities` where available.
- [x] Analyze chunking failures.
  - Evidence: `reports/stages/chunking_comparison.md`, `reports/stages/final_evaluation_review.md`.
  - Acceptance: report identifies whether misses come from page boundaries, sentence breaks, section structure, or embedding mismatch.
- [x] Analyze GraphRAG tradeoffs.
  - Current evidence: fixed-window hybrid improved graph Recall@5 by +0.1 but trailed vector-only by -0.1; structure-aware hybrid matches vector-only Recall@5 while preserving KG evidence coverage.
  - Evidence-level result: structure-aware hybrid supported 9 answers versus 8 for fixed-window hybrid.
  - Acceptance: report explains when graph retrieval improves evidence coverage, when vector retrieval is sufficient, and when KG sparsity limits hybrid gains.
- [x] Select the default chunking strategy for the next project phase.
  - Decision: `structure_aware`, because it improves vector MRR/precision, structure-aware Hybrid RAG reaches Recall@5 = 1.0 with KG evidence coverage = 0.9, and evidence-level evaluation shows more supported answers.
  - Evidence: `reports/stages/final_evaluation_review.md`.
  - Acceptance: decision is justified by retrieval metrics plus chunk cost/stability, not Recall alone.
- [x] Review KG extraction failure cases.
  - Evidence: `reports/stages/final_evaluation_review.md`.
  - Acceptance: unsupported triples, weak evidence, missing provenance, and key-entity coverage gaps are summarized.
- [x] Confirm citation completeness on LLM answers.
  - Evidence: `reports/stages/final_evaluation_review.md`.
  - Acceptance: each accepted answer cites at least one valid chunk/page/triple source or abstains when evidence is insufficient.
- [x] Add per-question evidence cards for experiment explainability.
  - Command: `uv run aviation-ai report evidence-cards --hybrid-report reports/stages/hybrid_rag_structure_aware.json --output-dir reports/stages`
  - Evidence: `reports/stages/evidence_cards.json`, `reports/stages/evidence_cards.md`.
  - Result: 10 cards summarize gold evidence, vector top-5, graph triples, hybrid fused top-5, graph helped/hurt status, citation status, and failure category; current observed categories are `success` and `hybrid fusion dilution`.
  - Acceptance: cards are generated deterministically from existing Hybrid RAG JSON without rerunning LLM work and remain available as both standalone reports and embedded Hybrid RAG report sections.

## P2 - Final Submission Tasks

Related goals: G1, G5, G6, G7, G8.

- [x] Update `README.md` after real experiment results are available.
  - Acceptance: README no longer points to archived stage filenames as if they were current files.
- [x] Complete deterministic final and academic reports.
  - Evidence: `reports/final/project_report.md`, `reports/final/project_academic_report.md`, `reports/final/project_academic_report_sources.json`.
  - Acceptance: includes motivation, architecture, ontology design, KG deliverable, GraphRAG pipeline, chunking comparison, vector/graph/hybrid analysis, limitations, advisory boundary, and reproducibility appendix.
- [x] Add project-defense notes and academic PPT outline.
  - Evidence: `reports/final/project_defense_notes.md`, `reports/final/project_defense_notes.json`, `reports/final/defense_deck_outline.md`, `reports/final/aviation_graphrag_defense_deck_sources.json`.
  - Acceptance: answers what was built, why ontology is needed, why KG is a deliverable, why GraphRAG is used, why chunking strategies are compared, and where the system can fail.
- [x] Generate academic defense PPT and AI-enhanced visual assets.
  - Commands:
    - `uv run aviation-ai report visual-assets`
    - `uv run aviation-ai report defense-deck-outline`
    - `node scripts/build_defense_deck.mjs`
  - Evidence: `reports/final/aviation_graphrag_defense_deck.pptx`, `reports/final/assets/*_ai.png`, `reports/final/assets/*.svg`, `reports/final/assets/visual_assets_manifest.json`.
  - Acceptance: PPT uses evidence-backed action titles, AI presentation visuals with local SVG fallbacks, source citations, an artifact-index appendix, and zero layout-check errors/warnings.
- [x] Implement a minimal web interface demonstrator.
  - Command: `uv run aviation-ai web serve`
  - Evidence: `reports/stages/web_demo_readiness.md`
  - Scope: offline-first FastAPI page with macOS-style sidebar question list, deterministic demo narrative, pipeline explanation, fixed-window/structure-aware comparison, vector/graph/hybrid toolbar controls, Why This Result panel, answer panel, citation/evidence chunks, KG triple evidence, question-scoped KG relationship graph, metrics, and advisory boundary notice.
  - Acceptance: reviewer can run it locally, inspect retrieved KG relationships for each CQ, understand why each retrieval mode behaves differently, and see the pipeline output without reading raw JSON reports.
- [x] Add web interface run instructions and screenshots or smoke-test evidence.
  - Current evidence: README includes `uv sync --extra dev --extra graphrag --extra web` and `uv run aviation-ai web serve`.
  - Current smoke evidence: `reports/stages/web_demo_final_smoke.md` confirms the default structure-aware hybrid view API/static checks, KG graph, and live-query lockout.
  - Acceptance: final report explains how to start the interface and what each UI section demonstrates.
- [x] Review `THIRD_PARTY.md` and license attribution.
  - Acceptance: all copied/adapted external assets and papers are attributed; generated local artifacts are clearly identified.
- [x] Run final quality gate before submission.
  - Commands:
    - `uv run ruff check .`
    - `uv run pytest`
    - `git status --short`
    - PPT layout and archive checks.
    - Secret scan excluding ignored `.env` and empty `.env.example` placeholders.
  - Evidence: Ruff passed; Pytest passed with 116 tests; PPT layout check reported 0 errors/0 warnings; `unzip -t` reported no PPTX archive errors; refined secret scan found no committed secrets.
  - Acceptance: checks pass and only intentional files are changed.

## P3 - Experimental Expansion Tasks

Related goals: G2, G3, G4, G6, G8, G9.

- [x] Expand the gold label set to 30-50 evaluation questions.
  - Candidate output: `data/cqs/06_phak_ch4_0.expanded.gold.json`.
  - Scope: include topic coverage for atmosphere, air density, pressure/temperature, viscosity, boundary layer, Newton laws, Bernoulli, airfoil geometry, lift, angle of attack, wingtip vortices, and induced drag.
  - Required fields: `gold_level`, `source_page`, `expected_chunk_ids`, `evidence_spans`, `key_entities`, `answer_key`, `question_type`.
  - Include at least 5 no-answer or insufficient-evidence questions to test abstention.
  - Evidence: `data/cqs/06_phak_ch4_0.expanded.gold.json`.
  - Result: 35 total labels, including 5 no-answer / insufficient-evidence labels.
  - Acceptance: loader and metrics can evaluate page/chunk/span/no-answer labels without API keys.
- [x] Implement retrieval ablation experiment reporting.
  - Candidate command: `uv run aviation-ai report retrieval-ablation`.
  - Modes/settings: vector-only, graph-only, hybrid RRF, hybrid with graph disabled, `graph_hops` variants, `vector_top_k` variants, `hybrid_top_k` variants.
  - Metrics: Recall@5, MRR@5, Context Precision@5, first relevant rank, source-page hits, chunk/span hits, and KG evidence coverage.
  - Evidence: `reports/stages/retrieval_ablation.md`.
  - Result: 12 deterministic scenarios over 35 expanded questions; default vector Recall@5 = 0.6857, explicit graph-disabled hybrid Recall@5 = 0.6857, and default hybrid Recall@5 = 0.6286.
  - Acceptance: report explains where graph evidence helps, where vector is sufficient, and where hybrid fusion hurts page-level recall.
- [x] Implement KG extraction quality comparison.
  - Candidate command: `uv run aviation-ai report kg-extraction-comparison`.
  - Variables: `fixed_window` vs `structure_aware`, model name, max token setting, prompt strictness, dry-run seed triples versus live extraction.
  - Metrics: valid triples, unsupported class/property count, provenance completeness, evidence-in-chunk rate, duplicate/near-duplicate triples, key-entity coverage, cost/time.
  - Evidence: `reports/stages/kg_extraction_comparison.md`.
  - Result: structure-aware KG has 448 valid triples and 0.8571 key-entity coverage; fixed-window KG has 172 valid triples and 0.8286 key-entity coverage.
  - Acceptance: report identifies whether extra structure-aware triples improve useful evidence or mainly add noise/cost.
- [x] Implement answer-level evaluation report.
  - Candidate command: `uv run aviation-ai report answer-eval`.
  - Metrics: citation correctness, citation completeness, answer faithfulness, answer relevance, abstention correctness, advisory-boundary violation count.
  - Inputs: Hybrid RAG reports plus expanded gold labels.
  - Evidence: `reports/stages/answer_evaluation.md`.
  - Result: existing 10-CQ structure-aware hybrid answers have citation completeness = 1.0, citation correctness = 0.9, answer faithfulness = 0.9, and zero advisory-boundary violations.
  - Note: expanded-gold answer generation is not yet rerun; current answer evaluation uses the existing 10-CQ Hybrid RAG report.
  - Acceptance: answer quality remains a separate layer and is not merged with retrieval or KG metrics into one score.
- [x] Add paraphrase and robustness benchmark.
  - Candidate output: `data/cqs/06_phak_ch4_0.robustness.json`.
  - Cases: paraphrased CQs, terminology substitution, ambiguous questions, cross-page questions, and unsupported questions.
  - Metrics: retrieval stability, answer stability, citation stability, KG evidence stability, abstention correctness.
  - Evidence: `data/cqs/06_phak_ch4_0.robustness.json`, `reports/stages/robustness_evaluation.md`.
  - Result: 10 cases; retrieval stability = 0.8, citation stability = 0.7, abstention correctness = 0.6.
  - Acceptance: report identifies whether the current system overfits the original boundary CQ wording.
- [ ] Compare embedding/index options.
  - Candidate command: `uv run aviation-ai report embedding-comparison`.
  - Variables: current Chroma default embedding versus at least one configured external/local embedding backend if available.
  - Metrics: retrieval quality, index build time, query latency, index size, and reproducibility notes.
  - Acceptance: default embedding choice is justified by quality/cost/stability, not assumed.
- [x] Add cost and latency tracking to experiment manifests.
  - Candidate output: extend run manifest schema and reports.
  - Track: chunk build time, KG extraction elapsed time, LLM token usage where available, Chroma index build time, query latency, report runtime, collection size.
  - Evidence: `cost_latency` blocks in `reports/stages/retrieval_ablation.json`, `reports/stages/kg_extraction_comparison.json`, `reports/stages/answer_evaluation.json`, and `reports/stages/robustness_evaluation.json`.
  - Acceptance: structure-aware quality gains can be discussed alongside cost and runtime overhead.
- [x] Define the next-document expansion protocol.
  - Candidate output: `docs/document_expansion_protocol.md`.
  - Scope: document metadata, section schema, source type, revision/date, page range, section hierarchy, and advisory risk level.
  - Evidence: `docs/document_expansion_protocol.md`.
  - Acceptance: no emergency/procedure manual is added until its metadata and section schema can be validated.

## P4 - Automation And GitLab Tasks

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
