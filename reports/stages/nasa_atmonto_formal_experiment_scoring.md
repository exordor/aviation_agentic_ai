# NASA ATMONTO Formal Experiment Scoring

- Status: `scored`
- Protocol: `docs/experiment_protocol.md`

## Gold Source

- Source: `frozen_reviewed_gold`
- Path: `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- Exists: `True`
- Ready for scoring: `True`
- SHA-256: `f668488624a43cbb7d74fd3f33731a0bf9adfa11093d185a236d86d9cfb1ac0d`

## Gold Status

- Records: 100
- Reviewed records: 100
- Pending records: 0
- Complete: `True`

## Methodology Remediation

- Status: `methodology_remediation`
- Scope: The current scored run is a narrow FAA ATCSCC advisory / NASA ATMONTO ATCSCC schema-slice experiment. PDF reference documents are added only as a second source-family design for the next rerun; PDF definition/procedure metrics must not be mixed into the ATCSCC event F1 table.
- Cross-source metric policy: Compare structural conformance, evidence grounding, and canonicalization yield across source families. Report semantic F1 within each task family only.

| Source family | Data shape | Task | Boundary |
| --- | --- | --- | --- |
| `faa_atcscc_advisories` | `semi_structured_short_advisories` | TMI/event ABox extraction | Current scored ATCSCC event extraction. |
| `faa_nasa_pdf_reference_documents` | `unstructured_or_long_form_reference_text` | definition, terminology, procedure, and source-mapping evidence extraction | Next-rerun PDF reference extraction; do not mix definition/procedure F1 with ATCSCC event F1. |

- PDF backend policy: `hybrid_docling_pymupdf` is the candidate default; `pymupdf_text_legacy` is a baseline only.
- PDF target predicates: `term_has_definition, term_has_alias, procedure_mentions_concept, document_defines_or_constrains, source_supports_mapping`.
- PDF provenance fields: `document_id, page, section, span, evidence_text`.

## Consensus SOTA Constraints

- Status: `rerun_design_constraint`
- Boundary: These constraints refine the narrow ATCSCC / ATMONTO rerun. They are not a pivot to a general aviation KG or an end-to-end GraphRAG claim.
- S1 interpretation: `S1_raw_open_llm` is a drift diagnostic; `S1b_llm_canonicalized` is the comparable target-schema baseline.
- Nine-stage pipeline: `ATCSCC parsing -> S0 deterministic backbone -> schema-slice retrieval -> LLM semantic extraction -> canonicalization -> validator gate -> repair with trace -> graph materialization -> layered evaluation`.
- Reviewed dev examples artifact: `reviewed_dev_examples`; use 10-20 examples outside the held-out 100 scoring records.

| SOTA constraint | Implementation | Claim guardrail |
| --- | --- | --- |
| `Extract-Define-Canonicalize` | Split open extraction from target-schema canonicalization. | Do not score raw open LLM output with ATMONTO P/R/F1. |
| `ontology_guided_domain_short_text_kgc` | Use 10-20 reviewed dev examples for S2/S3 by advisory type and predicate family. | Do not draw examples from the held-out 100 scoring records. |
| `llm_as_kg_support_module` | Use LLMs as canonicalizer, semantic enrichment module, evidence checker, and profile-gap explainer. | Do not make pure LLM extraction the primary thesis system. |
| `production_ontology_guided_pipeline` | Combine pattern/rule extraction, ontology-guided prompting, grounding, corroboration, and validator gating. | Quarantine conflicts, unsupported spans, and rejected repairs. |
| `source_family_separation` | Keep ATCSCC event extraction and PDF reference extraction in separate metric tables. | Do not compare PDF definition F1 with ATCSCC event F1. |
| `graph_rag_layered_evaluation` | Report KG construction, graph retrieval, and answer generation metrics as separate layers. | Current remediation supports KG construction metrics only; no end-to-end GraphRAG answer improvement claim. |

- S4 primary candidate: `S4_hybrid_backbone_enrichment`.
- S0 owns deterministic fields: `advisoryNumber, issuedTime, effectiveStartTime, effectiveEndTime, header/template fields`.
- S3/S4 may add but not overwrite semantic fields: `controlledNASelement, departureScope, extensionProbability, impactingCondition, impactingConditionMessage, implementationStatus, initiativeComments, reRouteReason, reRouteType`.
- Quarantine/review conditions: `conflict, unsupported span, fuzzy-only mapping, validator rejected fact, repair-only fact with semantic-change flag`.
- Planned artifacts/TODO: `schema/atcscc_tmi_profile.yaml, predicate canonicalizer, enum canonicalizer, entity canonicalizer, time normalizer, repair trace, error taxonomy`.
- Unverified search leads remain `requiring verification`: `OntoLogX, JSON-Schema-guided information extraction, Graphusion, RAKG, RAGAS, STaRK, Microsoft GraphRAG`.
- GraphRAG boundary: report `KG construction`, `graph retrieval`, and `answer faithfulness/completeness/citation support` separately; current remediation makes no end-to-end GraphRAG answer improvement claim.

## Corrected Stage Results

- `S1b_llm_canonicalized`: accepted 189 / 454 mapped facts; target-schema F1=0.2238095238095238.
- `S4_hybrid_backbone_enrichment`: selected semantic macro-F1 0.14285714285714285 -> 0.5486727026361172; deterministic macro-F1 0.8779591836734694 -> 0.8779591836734694.

## System Metrics

| System | Output | JSON adherence | Candidate facts | Accepted | Rejected | Structural acceptance | Schema violation rate | Repair success | Semantic metrics |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | `True` | 1.0 | 615 | 567 | 48 | 0.9219512195121952 | 0.07804878048780488 | n/a | P=0.8162544169611308, R=0.7096774193548387, F1=0.7592440427280197 |
| `S1_llm_only` | `True` | 1.0 | 1211 | 0 | 1211 | 0.0 | 1.0 | n/a | `invalid_direct_schema_scoring`; diagnostic P=0.0, R=0.0, F1=0.0 |
| `S1b_llm_canonicalized` | `True` | 1.0 | 454 | 189 | 265 | 0.41629955947136565 | 0.5837004405286343 | n/a | P=0.4973544973544973, R=0.1443932411674347, F1=0.2238095238095238 |
| `S2_llm_schema_slice` | `True` | 1.0 | 708 | 584 | 124 | 0.8248587570621468 | 0.1751412429378531 | n/a | P=0.20618556701030927, R=0.18433179723502305, F1=0.19464720194647203 |
| `S3_llm_schema_slice_validator_repair` | `True` | 1.0 | 396 | 355 | 41 | 0.8964646464646465 | 0.10353535353535354 | 0.8964646464646465 | P=0.24225352112676057, R=0.13210445468509985, F1=0.17097415506958252 |
| `S4_hybrid_backbone_enrichment` | `True` | 1.0 | 731 | 731 | 0 | 1.0 | 0.0 | 1.0 | P=0.6794520547945205, R=0.7619047619047619, F1=0.718320057929037 |

## Semantic Confidence Intervals

| System | Method | Precision 95% CI | Recall 95% CI | F1 95% CI |
| --- | --- | ---: | ---: | ---: |
| `S0_rule_only` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.7534246575342466 - 0.8619329388560157 | 0.6601208459214502 - 0.7639751552795031 | 0.7082658022690438 - 0.8042939719240298 |
| `S1b_llm_canonicalized` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.41624365482233505 - 0.5963855421686747 | 0.12037037037037036 - 0.1679160419790105 | 0.18457943925233644 - 0.25389221556886227 |
| `S2_llm_schema_slice` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.15081967213114755 - 0.25244618395303325 | 0.13582089552238805 - 0.23076923076923078 | 0.1437403400309119 - 0.23986486486486486 |
| `S3_llm_schema_slice_validator_repair` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.17064846416382254 - 0.29941860465116277 | 0.08507223113964688 - 0.16593245227606462 | 0.11324786324786325 - 0.2121504339440694 |
| `S4_hybrid_backbone_enrichment` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.6340819022457067 - 0.7178477690288714 | 0.7105666156202144 - 0.8051750380517504 | 0.6757369614512472 - 0.7531556802244038 |

## Semantic Group Metrics

- Semantic groups are stratified reporting slices, not train/dev/test splits.

| System | Group | Records | Gold facts | Predicted facts | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `S0_rule_only` | `ground_stop_lifecycle` | 26 | 186 | 190 | 0.8736842105263158 | 0.8924731182795699 | 0.8829787234042553 |
| `S0_rule_only` | `reroute_or_route_constraint` | 25 | 183 | 113 | 0.8938053097345132 | 0.5519125683060109 | 0.6824324324324325 |
| `S0_rule_only` | `volcanic_activity_bulletin` | 19 | 95 | 76 | 0.75 | 0.6 | 0.6666666666666665 |
| `S0_rule_only` | `ground_delay_program_lifecycle` | 12 | 91 | 87 | 0.9885057471264368 | 0.945054945054945 | 0.9662921348314606 |
| `S0_rule_only` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 63 | 0.6349206349206349 | 0.7272727272727273 | 0.6779661016949152 |
| `S0_rule_only` | `hotline_or_webpage_status` | 3 | 15 | 12 | 0.3333333333333333 | 0.26666666666666666 | 0.2962962962962963 |
| `S0_rule_only` | `airport_diversion_recovery` | 2 | 12 | 8 | 0.0 | 0.0 | 0.0 |
| `S0_rule_only` | `special_or_flow_constraint_fyi` | 2 | 10 | 9 | 0.4444444444444444 | 0.4 | 0.4210526315789474 |
| `S0_rule_only` | `flight_plan_drop_time_status` | 1 | 4 | 8 | 0.5 | 1.0 | 0.6666666666666666 |
| `S1b_llm_canonicalized` | `ground_stop_lifecycle` | 26 | 186 | 78 | 0.5641025641025641 | 0.23655913978494625 | 0.33333333333333337 |
| `S1b_llm_canonicalized` | `reroute_or_route_constraint` | 25 | 183 | 24 | 0.375 | 0.04918032786885246 | 0.08695652173913043 |
| `S1b_llm_canonicalized` | `volcanic_activity_bulletin` | 19 | 95 | 26 | 0.6538461538461539 | 0.17894736842105263 | 0.2809917355371901 |
| `S1b_llm_canonicalized` | `ground_delay_program_lifecycle` | 12 | 91 | 37 | 0.35135135135135137 | 0.14285714285714285 | 0.20312499999999997 |
| `S1b_llm_canonicalized` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 20 | 0.5 | 0.18181818181818182 | 0.26666666666666666 |
| `S1b_llm_canonicalized` | `hotline_or_webpage_status` | 3 | 15 | 1 | 0.0 | 0.0 | 0.0 |
| `S1b_llm_canonicalized` | `airport_diversion_recovery` | 2 | 12 | 2 | 0.0 | 0.0 | 0.0 |
| `S1b_llm_canonicalized` | `special_or_flow_constraint_fyi` | 2 | 10 | 0 | 0.0 | 0.0 | 0.0 |
| `S1b_llm_canonicalized` | `flight_plan_drop_time_status` | 1 | 4 | 1 | 1.0 | 0.25 | 0.4 |
| `S2_llm_schema_slice` | `ground_stop_lifecycle` | 26 | 186 | 167 | 0.2275449101796407 | 0.20430107526881722 | 0.21529745042492918 |
| `S2_llm_schema_slice` | `reroute_or_route_constraint` | 25 | 183 | 187 | 0.1711229946524064 | 0.17486338797814208 | 0.17297297297297298 |
| `S2_llm_schema_slice` | `volcanic_activity_bulletin` | 19 | 95 | 71 | 0.4788732394366197 | 0.35789473684210527 | 0.40963855421686746 |
| `S2_llm_schema_slice` | `ground_delay_program_lifecycle` | 12 | 91 | 66 | 0.045454545454545456 | 0.03296703296703297 | 0.03821656050955414 |
| `S2_llm_schema_slice` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 35 | 0.08571428571428572 | 0.05454545454545454 | 0.06666666666666667 |
| `S2_llm_schema_slice` | `hotline_or_webpage_status` | 3 | 15 | 17 | 0.29411764705882354 | 0.3333333333333333 | 0.3125 |
| `S2_llm_schema_slice` | `airport_diversion_recovery` | 2 | 12 | 11 | 0.2727272727272727 | 0.25 | 0.2608695652173913 |
| `S2_llm_schema_slice` | `special_or_flow_constraint_fyi` | 2 | 10 | 22 | 0.09090909090909091 | 0.2 | 0.12500000000000003 |
| `S2_llm_schema_slice` | `flight_plan_drop_time_status` | 1 | 4 | 6 | 0.0 | 0.0 | 0.0 |
| `S3_llm_schema_slice_validator_repair` | `ground_stop_lifecycle` | 26 | 186 | 91 | 0.1978021978021978 | 0.0967741935483871 | 0.1299638989169675 |
| `S3_llm_schema_slice_validator_repair` | `reroute_or_route_constraint` | 25 | 183 | 136 | 0.33088235294117646 | 0.2459016393442623 | 0.28213166144200624 |
| `S3_llm_schema_slice_validator_repair` | `volcanic_activity_bulletin` | 19 | 95 | 17 | 0.47058823529411764 | 0.08421052631578947 | 0.14285714285714282 |
| `S3_llm_schema_slice_validator_repair` | `ground_delay_program_lifecycle` | 12 | 91 | 50 | 0.14 | 0.07692307692307693 | 0.09929078014184398 |
| `S3_llm_schema_slice_validator_repair` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 31 | 0.12903225806451613 | 0.07272727272727272 | 0.09302325581395349 |
| `S3_llm_schema_slice_validator_repair` | `hotline_or_webpage_status` | 3 | 15 | 11 | 0.0 | 0.0 | 0.0 |
| `S3_llm_schema_slice_validator_repair` | `airport_diversion_recovery` | 2 | 12 | 11 | 0.36363636363636365 | 0.3333333333333333 | 0.34782608695652173 |
| `S3_llm_schema_slice_validator_repair` | `special_or_flow_constraint_fyi` | 2 | 10 | 5 | 0.0 | 0.0 | 0.0 |
| `S3_llm_schema_slice_validator_repair` | `flight_plan_drop_time_status` | 1 | 4 | 3 | 0.0 | 0.0 | 0.0 |
| `S4_hybrid_backbone_enrichment` | `ground_stop_lifecycle` | 26 | 186 | 238 | 0.7142857142857143 | 0.9139784946236559 | 0.8018867924528302 |
| `S4_hybrid_backbone_enrichment` | `reroute_or_route_constraint` | 25 | 183 | 185 | 0.7027027027027027 | 0.7103825136612022 | 0.7065217391304348 |
| `S4_hybrid_backbone_enrichment` | `volcanic_activity_bulletin` | 19 | 95 | 81 | 0.7037037037037037 | 0.6 | 0.6477272727272727 |
| `S4_hybrid_backbone_enrichment` | `ground_delay_program_lifecycle` | 12 | 91 | 106 | 0.8113207547169812 | 0.945054945054945 | 0.8730964467005076 |
| `S4_hybrid_backbone_enrichment` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 77 | 0.5324675324675324 | 0.7454545454545455 | 0.6212121212121212 |
| `S4_hybrid_backbone_enrichment` | `hotline_or_webpage_status` | 3 | 15 | 15 | 0.26666666666666666 | 0.26666666666666666 | 0.26666666666666666 |
| `S4_hybrid_backbone_enrichment` | `airport_diversion_recovery` | 2 | 12 | 10 | 0.0 | 0.0 | 0.0 |
| `S4_hybrid_backbone_enrichment` | `special_or_flow_constraint_fyi` | 2 | 10 | 9 | 0.4444444444444444 | 0.4 | 0.4210526315789474 |
| `S4_hybrid_backbone_enrichment` | `flight_plan_drop_time_status` | 1 | 4 | 9 | 0.4444444444444444 | 1.0 | 0.6153846153846153 |

## Rejection Adjudication

- Property-level complete: `True`
- Decision counts: `{"extractor_bug": 13, "profile_gap": 275}`
- Pending facts: 0

## Claim Status

| Claim | Status | Rationale |
| --- | --- | --- |
| `C1` Runtime NASA ATMONTO profile feasibility | `supported_by_pilot` | The pilot generated the schema catalog, ATCSCC schema slice, and validated candidate-fact artifact. This remains a schema-engineering claim. |
| `C2` Schema-slice constraint benefit | `supported` | S2 schema guidance reduces target-schema violation rate versus the canonicalized S1b baseline by at least 10 percentage points. |
| `C3` Validator/repair benefit | `supported` | S3 meets the repair-success threshold and preserves semantic correctness. |
| `C4` Rejection analysis utility | `supported` | All 288 rejections have final property-level action labels: {"extractor_bug": 13, "profile_gap": 275}. |

## Hypothesis Status

| Hypothesis | Status | Falsification criterion |
| --- | --- | --- |
| `H1` Schema guidance reduces structural drift | `supported` | Falsified if schema guidance does not reduce unsupported target-schema terms after a canonicalized S1b baseline exists, or if the reduction only comes from suppressing more than 25 percent of gold-supported facts. |
| `H2` Validator/repair improves valid yield | `supported` | Falsified if S3 repair success is below 15 percent of initially invalid facts, or if S3 manual semantic correctness is more than 5 percentage points lower than S2. |
| `H3` Hybrid backbone plus enrichment improves selected semantic predicates | `supported` | Falsified if S4 hybrid does not improve selected semantic predicate F1 over S0 while preserving deterministic-field F1 within the pre-registered tolerance. |
| `H4` Rejection triage produces actionable engineering decisions | `supported` | Falsified if more than 20 percent of rejected facts remain manual-review-only after review, or if profile extensions cannot be tied to source evidence and NASA ATMONTO terms. |

## Completion Audit

- Overall status: `formal_experiment_complete`
- Blocking requirements: `[]`

| Requirement | Status | Evidence |
| --- | --- | --- |
| `R0` Position the current NASA ATMONTO loop as pilot / feasibility evidence, not a completed formal experiment. | `satisfied` | docs/experiment_protocol.md contains pilot/feasibility boundary and bronze-until-reviewed language. |
| `R1` Sample 80-120 ATCSCC advisories for the formal gold set. | `satisfied` | sample_size=100; manifest=data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json |
| `R2` Freeze reviewed gold annotations before semantic scoring. | `satisfied` | gold_source=frozen_reviewed_gold; template_reviewed=100; template_pending=0 |
| `R3` Define the corrected system suite: S0, diagnostic S1, S1b, S2, S3, and S4. | `satisfied` | systems=S0_rule_only,S1_llm_only,S1b_llm_canonicalized,S2_llm_schema_slice,S3_llm_schema_slice_validator_repair,S4_hybrid_backbone_enrichment |
| `R4` Run all corrected-stage systems on the identical sampled records. | `satisfied` | {"S0_rule_only": true, "S1_llm_only": true, "S1b_llm_canonicalized": true, "S2_llm_schema_slice": true, "S3_llm_schema_slice_validator_repair": true, "S4_hybrid_backbone_enrichment": true} |
| `R5` Define JSON, schema, semantic, repair, and manual-correctness metrics. | `satisfied` | docs/experiment_protocol.md and reports/stages/nasa_atmonto_formal_experiment_scoring.json |
| `R6` Report JSON adherence, schema violation rate, precision/recall/F1, repair success, and manual semantic correctness. | `satisfied` | all_system_outputs=True; all_semantic_metrics_available=True |
| `R7` Account for all pilot rejections in property-level error analysis. | `satisfied` | rejected_fact_count=288; grouped_fact_count=288 |
| `R8` Finalize whether each rejection group is extractor bug, NASA ATMONTO profile gap, source ambiguity, or manual-review-only. | `satisfied` | {"extractor_bug": 13, "profile_gap": 275} |
| `R9` Assign supported, falsified, or inconclusive status to claims C1-C4 and hypotheses H1-H4. | `satisfied` | {"C1": "supported_by_pilot", "C2": "supported", "C3": "supported", "C4": "supported", "H1": "supported", "H2": "supported", "H3": "supported", "H4": "supported"} |
| `R10` Fix the protocol artifact with claims, hypotheses, baselines, metrics, and falsification criteria. | `satisfied` | docs/experiment_protocol.md |

## Missing Required Inputs


## Boundary

- Formal metrics are descriptive until all four systems have predictions and the frozen reviewed gold set is available.
