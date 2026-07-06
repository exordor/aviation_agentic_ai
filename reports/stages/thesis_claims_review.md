# Thesis Claims Review

## Revised Thesis Claim

This thesis investigates a retrospective and source-bounded claim: for FAA ATCSCC advisories, a lightweight NASA ATMONTO-derived application schema can constrain LLM extraction of advisory events, support agentic validation/refinement, and provide an inspectable advisory event graph for KG-RAG question answering. The system is evaluated with layered metrics: schema-valid extraction, evidence-linked relation correctness on reviewed subsets, repair/critic behavior, retrieval and answer quality, citation quality, and failure/human-review boundaries are reported separately.

## Research Questions

- **RQ1**: Can schema-constrained LLM extraction produce valid and evidence-linked event records from ATCSCC advisories?
- **RQ2**: Does an agentic validation-refinement loop reduce schema violations and unsupported relations?
- **RQ3**: Does KG-RAG improve evidence grounding and citation quality compared with vector-only RAG?
- **RQ4**: What failure types remain, and where does human review remain necessary?

## Hypotheses

- **H1**: Schema constraints increase valid, evidence-linked advisory event records compared with unconstrained or weakly constrained extraction.
- **H2**: A validator/refiner/critic loop reduces schema violations, unsupported relations, and parser artifacts before graph insertion.
- **H3**: KG-RAG improves source-bounded grounding, answer-set quality, and citation behavior on relation-oriented ATCSCC questions, while vector-only retrieval can remain sufficient for simple source-local questions.
- **H4**: Failure analysis can separate extraction errors, profile/gold-boundary gaps, retrieval context errors, answer overreach, and cases requiring human review.

## Evaluation Framing

Negative or mixed Recall@k results are not hidden. They motivate layered evaluation and identify when vector retrieval is sufficient.

| Layer | Metrics | Purpose |
| --- | --- | --- |
| Schema-constrained extraction | schema validity, structural acceptance rate, rejected fact count, repaired fact count | Measure whether generated event records obey the application schema before graph insertion. |
| Evidence support | evidence-span coverage, unsupported relation rate, provenance completeness, reviewed-subset precision/recall/F1 | Measure whether accepted facts can be traced to advisory text. |
| Agentic loop behavior | violation reduction, repair success, critic rejection count, post-loop extraction F1 | Measure whether validation/refinement improves extraction quality. |
| Retrieval and KG-RAG answer quality | answer-set F1, target-source hit rate, citation precision/recall, evidence faithfulness | Measure whether vector, graph, and hybrid modes support grounded answers. |
| Failure and human-review boundary | failure category counts, abstention correctness, profile/gold-boundary cases, human-review completion status | Measure what remains unresolved and which claims require review. |

The report must not create or recommend a single mixed overall score.

## Claim Safety Matrix

| Claim | Current evidence | Supported strength | Safe wording | Unsafe wording to avoid |
| --- | --- | --- | --- | --- |
| Lightweight schema constrains advisory event extraction. | ATCSCC profile terms, schema validation, and prediction-output validation reports constrain accepted event fields. | strong | The application schema constrains which advisory event fields and relations can enter the graph. | The ontology fully models aviation knowledge. |
| Accepted facts preserve provenance. | KG and prediction validation reports check source IDs and evidence spans. | strong | Accepted facts carry source-bounded provenance checked by deterministic validation. | Every KG triple is semantically correct. |
| Agentic validation improves extraction quality. | S5/S6 reports record validator, refiner, critic, repair, and rejection behavior. | moderate | The agentic loop reduces specific schema and support failures in the current ATCSCC pipeline. | Autonomous agents construct a correct ontology. |
| KG-RAG improves grounded ATCSCC QA diagnostics. | S7 retrieval, graph-health, and LLM answer-generation diagnostics report answer-set, citation, and target-source metrics. | moderate | KG-RAG improves some source-bounded grounding diagnostics on this benchmark. | GraphRAG is always more accurate than vector retrieval. |
| GraphRAG universally improves retrieval. | S7 reports vector, graph, and routed modes separately; graph use is template-dependent. | not supported | KG-RAG should be reported as a source-bounded grounding and evidence diagnostic, not a universal Recall@k improvement. | GraphRAG always improves Recall@k. |
| The system can answer operational ATC questions. | The advisory boundary limits the system to retrospective research diagnostics. | not supported | The system analyzes retrospective advisories and must not be used for live operational decisions. | The system can support operational flight or ATC decisions. |
| Automated diagnostics replace human review. | Reviewer-defense and SOTA audits keep automated diagnostics separate from human review. | not supported | Automated diagnostics are internal error-discovery tools and do not replace human or expert review. | The benchmark is human reviewed or expert certified. |
| The benchmark is externally aviation-expert certified. | Current labels and diagnostics are project/thesis evidence with documented review gaps. | not supported | The benchmark is thesis-oriented and source-bounded, with explicit review limitations. | The benchmark is externally aviation-expert certified. |
| The method is domain-general. | A bounded second-source-family pilot exists, but it is not a full cross-domain benchmark. | weak | The method is designed to be domain-adaptable, with only pilot-level transfer evidence so far. | The method is proven domain-general. |

## Unsafe Claims Scan

No unsupported unsafe claims were found in the scanned files outside explicit limitation or advisory-boundary contexts.

## Evidence Gaps Before Thesis Submission

- Need final reviewed subset for triple-level and answer-level correctness
- Need explicit comparison against a naive/unconstrained extraction baseline
- Need clearer reporting of repair success and rejection reasons across the agentic loop
- Need final failure taxonomy with examples and claim impact
- Need optional second-domain pilot evidence only as transfer evidence, not as proof of domain-general validity

## Evidence Files

- `data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json`: present
- `RESEARCH_OVERVIEW.md`: present
- `reports/stages/atcscc_ontology_profile_overview.md`: present
- `reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md`: present
- `reports/stages/nasa_atmonto_cq_evaluation.json`: present
- `reports/stages/nasa_atmonto_formal_experiment_scoring.json`: present
- `reports/stages/nasa_atmonto_prediction_output_validation.json`: present
- `reports/stages/nasa_atmonto_reviewer_defense_audit.json`: present
- `reports/stages/nasa_atmonto_s5_s6_agentic_loop.json`: present
- `reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.json`: present
- `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.json`: present
- `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.json`: present
- `reports/stages/nasa_atmonto_s7_answer_review_decisions.json`: present
- `reports/stages/nasa_atmonto_s7_automated_adversarial_review.json`: present
- `reports/stages/nasa_atmonto_s7_graph_health.json`: present
- `reports/stages/nasa_atmonto_s7_llm_answer_generation.json`: present
- `reports/stages/nasa_atmonto_s7_retrieval.json`: present
- `reports/stages/nasa_atmonto_sota_goal_audit.json`: present
- `reports/stages/nasa_bga_domain_transfer_pilot.json`: present
- `src/aviation_agentic_ai/advisory.py`: present
