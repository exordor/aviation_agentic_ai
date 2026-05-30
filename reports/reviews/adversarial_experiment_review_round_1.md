# Adversarial Experiment Review Round 1

- Round: 1
- Method: seven read-only subagent reviews.
- Scope: thesis method, RAG/GraphRAG evaluation, ontology/KG evidence, benchmark quality, aviation safety, statistics/reproducibility, and skeptical external examination.
- Policy: no manual review, external aviation expert certification, or operational readiness is claimed by this review.

## Consolidated Must Fix

- Split automated consistency from thesis claim readiness; manual-review-dependent metrics remain pending.
- Reconcile RQ4 safety interpretation with robustness results and live-query/robustness safety gating.
- Treat benchmark v2 as the main internal thesis benchmark pending manual review, not as external validation.
- Keep KG claims limited to schema/provenance validity unless semantic review annotations are complete.
- Keep graph path metrics as diagnostic heuristics unless path relevance is manually reviewed.
- Make answer and sufficiency metrics visibly heuristic/gold-aware where appropriate.

## Subagent Findings

### A - Thesis Methodologist

- RQ4 underplays robustness failures while surfacing favorable sufficiency metrics.
- RQ2 does not yet prove an improvement over vector-only citation metrics; safer wording is that graph evidence adds inspectable KG/path evidence.
- Benchmark v2 support remains provisional because wording and safety review are pending.
- RQ1 should avoid claiming reduced unsupported triples without an unconstrained baseline.

### B - RAG / GraphRAG Evaluation Reviewer

- Retrieval aggregates mix supported and no-answer labels, distorting Recall/MRR and Context Recall.
- Vector/hybrid budget differences make some `@k` comparisons unfair.
- Path support is a useful diagnostic heuristic, not semantic path correctness.
- Answer table labels should state deterministic heuristic scoring.

### C - Ontology / KG Reviewer

- Schema validity, provenance validity, and semantic correctness must stay separate.
- `valid_triples=448` and provenance completeness do not imply every triple is correct.
- The triple review sample still has no completed manual semantic annotations.
- High-risk KG patterns need review before stronger KG quality claims.

### D - Benchmark Curator

- Benchmark v2 is explicitly machine-seeded and has systemic template wording.
- All insufficient-evidence labels need safety review.
- Cross-page labels need synthesis review and should not pass just because spans exist.
- The implemented subset should preserve the user's requested 60-label contract while documenting the curator's alternate recommendation.

### E - Aviation Safety Reviewer

- Live query needs an advisory-boundary gate before generation.
- Robustness previously answered unsupported operational prompts and must either be fixed or surfaced as unresolved.
- Risk-category accuracy is not independent when expected categories are derived by the same detector.
- Boundary-violation phrase checks should cover operational recommendations such as safe departure, continuing flight, legal clearance, and takeoff advice.

### F - Statistics / Reproducibility Reviewer

- `make thesis-all` needs documented local artifact prerequisites for ignored chunks/indexes.
- CI metadata should include `n`, confidence level, sample count, and seed.
- Report Markdown/dashboard should expose CI values visibly.
- Review report targets should not rewrite data artifacts by default.

### G - Skeptical External Examiner

- A strict examiner could reject the methodology if machine-seeded or manual-pending artifacts are treated as validated.
- Safety, KG semantic correctness, path relevance, and answer quality claims need stronger evidence or narrower wording.
- Final report, academic report, defense notes, and deck must keep limitations synchronized.

## Manual Review Dependencies

- Benchmark label wording, evidence sufficiency, answer-key correctness, risk category, and keep/revise/remove status.
- All 20 insufficient-evidence labels require safety review.
- 100-triple semantic review sample.
- Graph path relevance labels.
- Answer faithfulness, answer correctness, and answer relevance if used as thesis evidence.

## Acceptance Criteria

- Dashboard reports automated consistency separately from claim readiness.
- Reviewed subset artifacts are scaffolds and do not claim completed review.
- Triple semantic rates appear only when at least one item is actually reviewed.
- Path and answer metrics are labelled heuristic.
- Robustness and sufficiency results are both visible in RQ4.
- No thesis-facing report claims external certification, operational readiness, or replacement of POH/AFM, approved checklists, ATC, instructor guidance, regulations, or pilot judgment.
