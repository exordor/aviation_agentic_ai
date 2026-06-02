# NASA ATMONTO Agentic Extraction-Validation Loop

## Scope

- Boundary: Retrospective FAA ATCSCC advisory extraction only; no live operational use.
- CQ manifest: `data/evaluation/nasa_atmonto/atcscc_cq_query_manifest.json`
- Scoring report: `reports/stages/nasa_atmonto_formal_experiment_scoring.json`
- Prediction validation: `reports/stages/nasa_atmonto_prediction_output_validation.json`
- Status: `agentic_loop_ready_with_code_review_triggers`

## Multi-Paper Method Transfer

- **Claim KG and GraphRAG**: Treat extracted claims/triples as testable artifacts, then evaluate them against downstream retrieval and question-answering behavior.
- **Multi-agent ontology generation**: Separate extractor, validator, critic, and refiner roles so validation failures drive a bounded repair loop instead of a one-shot extraction.
- **Ontology engineering and competency questions**: Use CQs as an executable requirements contract rather than as informal examples of expected questions.
- **KG quality and evidence provenance**: Score semantic correctness, structural conformance, and evidence support as separate dimensions.
- **GraphRAG evaluation**: Keep graph quality tied to answerability, citation support, and abstention behavior instead of ontological completeness alone.

## Domain-Independent Pipeline

| Stage | Name | Role |
| --- | --- | --- |
| `P01` | `method_synthesis` | Research method abstraction from multiple reference papers. |
| `P02` | `semantic_requirements` | Source Requirement Document (SRD): domain entities, predicates, constraints, and CQs. |
| `P03` | `technical_implementation_plan` | TIP: ontology reuse decisions, profile gaps, schema slices, and extraction routes. |
| `P04` | `candidate_extraction` | Extractor agent produces schema-bound candidate triples with evidence text. |
| `P05` | `validation` | Validator agent checks JSON schema, ontology/profile constraints, and evidence presence. |
| `P06` | `critic_review` | Critic agent flags unsupported, over-broad, or source-unbounded facts. |
| `P07` | `repair_or_abstain` | Refiner repairs facts only when evidence and schema constraints permit it. |
| `P08` | `graph_and_graphrag_evaluation` | Materialize graph queries and later GraphRAG answer-set/citation evaluations. |
| `P09` | `code_review_gate` | Abnormal experiment diagnostics trigger code review before another extraction pass. |

## Generated Artifacts

| Artifact | Status | Path | Purpose |
| --- | --- | --- | --- |
| `SRD` | `generated` | `reports/stages/atcscc_semantic_requirements.md` | Semantic requirements contract from CQs, gold fields, predicates, and evidence rules. |
| `TIP` | `generated` | `reports/stages/atcscc_technical_implementation_plan.md` | Implementation plan for deterministic, LLM, validation, repair, and review stages. |
| `ExtractionValidationPlan` | `generated` | `reports/stages/atcscc_extraction_validation_plan.md` | Runnable loop policy with anomaly-to-review routing. |
| `CQManifest` | `ready` | `data/evaluation/nasa_atmonto/atcscc_cq_query_manifest.json` | Executable CQs and route labels for ATCSCC/ATMONTO extraction. |
| `PredictionValidation` | `ready_for_scoring` | `reports/stages/nasa_atmonto_prediction_output_validation.json` | Saved S0-S4 prediction readiness before scoring and repair decisions. |

## Agentic Loop Diagnostics

| System | F1 | Schema violation | Structural acceptance | JSON adherence | Action | Flags |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `S0_rule_only` | 0.7643 | 0.078 | 0.922 | 1.0 | `accept_for_current_baseline` | `none` |
| `S1_llm_only` | 0.0 | 1.0 | 0.0 | 1.0 | `quarantine_before_rerun` | `invalid_target_schema_scoring, schema_rejection_collapse, structural_acceptance_low, semantic_f1_below_minimum` |
| `S1b_llm_canonicalized` | 0.2271 | 0.5925 | 0.4075 | 1.0 | `review_code_before_rerun` | `structural_acceptance_low, semantic_f1_below_minimum` |
| `S2_llm_schema_slice` | 0.1677 | 0.4901 | 0.5099 | 1.0 | `review_code_before_rerun` | `structural_acceptance_low, semantic_f1_below_minimum` |
| `S3_llm_schema_slice_validator_repair` | 0.1615 | 0.2778 | 0.7222 | 1.0 | `review_code_before_rerun` | `semantic_f1_below_minimum, repair_did_not_improve_semantic_f1, structural_repair_without_semantic_gain` |
| `S4_hybrid_backbone_enrichment` | 0.7395 | 0.0 | 1.0 | 1.0 | `accept_for_current_baseline` | `none` |

## Code Review Triggers

- `S1b_llm_canonicalized`: flags=`structural_acceptance_low, semantic_f1_below_minimum`; focus=false-positive and false-negative examples by predicate
- `S2_llm_schema_slice`: flags=`structural_acceptance_low, semantic_f1_below_minimum`; focus=schema-slice prompt contract; predicate routing and enum canonicalization; evidence-span preservation before validation; false-positive and false-negative examples by predicate
- `S3_llm_schema_slice_validator_repair`: flags=`semantic_f1_below_minimum, repair_did_not_improve_semantic_f1, structural_repair_without_semantic_gain`; focus=validator repair rules in atmonto_experiment.py; repair acceptance criteria that may privilege structural validity over semantic support; post-repair evidence support checks; false-positive and false-negative examples by predicate

## SRD Seed

- Competency questions: 12
- Route counts: `{"abstain": 1, "deterministic": 2, "graph": 2, "hybrid": 4, "validator": 3}`
- Required predicates: `{"advisoryNumber": 2, "controlledNASelement": 4, "effectiveEndTime": 3, "effectiveStartTime": 2, "evidence_text": 3, "extensionProbability": 2, "impactingCondition": 3, "impactingConditionMessage": 2, "implementationStatus": 2, "initiativeComments": 3, "issuedTime": 2, "rdf:type": 1, "reRouteReason": 4, "reRouteType": 2, "source_id": 2}`
- Subject classes: `{"GroundDelayProgramTMI": 16, "GroundStopTMI": 21, "ReRouteTMI": 23, "TrafficManagementInitiative": 40}`

## TIP Seed

- Accepted baselines: `S0_rule_only, S4_hybrid_backbone_enrichment`
- Systems requiring review: `S1b_llm_canonicalized, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair`

## Next Actions

- Review code paths listed in code_review_triggers before rerunning S2/S3 extraction.
- Use the generated SRD and TIP as the contract before another live LLM run.
- Materialize template graph queries for CQ-Q01 before making GraphRAG answer-quality claims.
- Add explicit absent-field labels for CQ-A01 if abstention becomes a primary claim.
