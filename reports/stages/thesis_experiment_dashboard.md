# Master Project Dashboard

## Outcome

Evidence-grounded, schema-constrained Agentic KG-RAG over retrospective FAA ATCSCC advisories.

This dashboard is the human-readable project display surface. The full machine-readable evidence inventory remains in `reports/stages/thesis_experiment_dashboard.json`.

## Demo Path

```bash
uv run aviation-ai demo
uv run aviation-ai report thesis-experiment-dashboard
uv run aviation-ai report web-demo-smoke
```

Primary live-presentation path: `aviation-ai demo`. It runs offline over precomputed ATCSCC artifacts and traces one advisory through source text, S0 deterministic extraction, S4 evidence-linked graph facts, and S7 KG-RAG versus vector-only answers.

## Pipeline

```text
ATCSCC advisory
  -> lightweight schema/profile
  -> S0/S1/S2/S3/S4 extraction systems
  -> validator/refiner/critic diagnostics
  -> evidence-linked advisory event graph
  -> vector / graph / routed KG-RAG
  -> source-bounded answers and failure review
```

## Research Questions

| RQ | Claim strength | Evidence reports | Remaining boundary |
| --- | --- | --- | --- |
| RQ1 schema-constrained event extraction | strong | nasa_atmonto_formal_experiment_scoring, nasa_atmonto_prediction_output_validation, nasa_atmonto_cq_evaluation, atcscc_ontology_profile_overview | Semantic correctness remains reviewed-subset/profile-relative, not full ontology correctness. |
| RQ2 agentic validation-refinement | moderate | nasa_atmonto_s5_s6_agentic_loop, nasa_atmonto_s5_s6_independent_agentic_run, nasa_atmonto_s5_s6_live_agentic_pilot, nasa_atmonto_s5_s6_live_agentic_full_run, nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic | The agent loop is not autonomous ontology construction; it is a bounded diagnostic and repair loop for advisory-event extraction. |
| RQ3 KG-RAG grounding vs vector-only RAG | moderate-strong | nasa_atmonto_s7_retrieval, nasa_atmonto_s7_graph_health, nasa_atmonto_s7_llm_answer_generation, nasa_atmonto_s7_vector_only_llm_answer_generation | This is source-bounded ATCSCC evidence, not a universal claim that GraphRAG beats vector-only retrieval. |
| RQ4 failure modes and human-review boundary | moderate | nasa_atmonto_s7_llm_answer_generation, nasa_atmonto_s7_human_review_candidates, nasa_atmonto_s7_answer_review_import, nasa_atmonto_s7_answer_review_decisions, nasa_atmonto_s7_candidate_adjudication, nasa_atmonto_s7_profile_decision, nasa_atmonto_reviewer_defense_audit | Human/expert review remains separate from automated diagnostics; operational ATC use remains out of scope. |

## Key Results

| Layer | Result | Interpretation |
| --- | --- | --- |
| Extraction / KG | Provenance completeness=1; evidence-in-source rate=1; valid triples=448 | Accepted facts are source-bounded artifacts, not universal semantic truth. |
| Agentic loop | S5/S6 live full-run diagnostics are present | The loop is an auditable repair/rejection mechanism, not autonomous ontology construction. |
| KG-RAG answer generation | Best mode=routed_token_matched_live_tfidf_graphrag; correctness=0.9667; citation precision=1; citation recall=0.6084; unsupported claim rate=0.0167 | Supports a source-bounded grounding claim. |
| Matched vector-only comparison | vector-only correctness=0.5; vector-only unsupported claim rate=0.5 | Useful RQ3 contrast, but not a universal GraphRAG superiority claim. |
| Review boundary | human-review candidates=9; profile/gold-boundary failures=3; human review=false | Automated diagnostics remain separate from human or expert review. |

## Demonstration Script

1. State the boundary: retrospective ATCSCC advisories, not live ATC support.
2. Run `uv run aviation-ai demo` and show the single-advisory trace.
3. Point to the S0 deterministic facts and S4 evidence-linked graph facts.
4. Compare the KG-RAG and vector-only answer arms for the same advisory.
5. Open this dashboard and use the RQ table to connect demo behavior to thesis claims.
6. End with failure boundaries: profile gaps, unsupported facts, and human review remain explicit.

## Claim Boundary

- The project is a bounded schema-constrained Agentic KG-RAG prototype.
- The schema/profile is an engineering constraint, not a complete aviation ontology.
- The event graph is source-bounded and evidence-linked.
- KG-RAG is evaluated as a grounding and citation diagnostic, not as universal superiority.
- Automated review does not replace human or external expert review.
- The system is not live operational ATC decision support.

## Current Checks

- Every RQ has evidence report: True
- Primary metrics have report evidence: True
- Unsafe claim patterns found: False
- Automated consistency passed: True
- Claim readiness passed: True

## Next Writing Step

Write the thesis spine from this dashboard: title, abstract, method figure, experiment table, RQ-by-RQ results, and limitations. Do not add new workstreams unless they directly patch one of these rows.
