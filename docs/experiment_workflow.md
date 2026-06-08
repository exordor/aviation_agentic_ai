# Thesis Experiment Workflow

This document defines the canonical experiment pipeline for the current thesis
route:

> Agentic KG-RAG for evidence-grounded question answering over retrospective
> FAA ATCSCC advisories.

The workflow is source-bounded and claim-bounded. NASA ATMONTO-derived terms are
used as a lightweight application schema/profile. They are not treated as a
complete aviation ontology or as the thesis object.

## Canonical Inputs

- Thesis framing: `docs/thesis_positioning.md`
- Research mainline: `docs/research_mainline.md`
- Documentation map: `docs/documentation_map.md`
- Metric protocol: `docs/evaluation_protocol.md`
- Paper-analysis protocol: `docs/research_paper_analysis_protocol.md`
- Formal ATCSCC protocol: `docs/experiment_protocol.md`
- Gold annotation guide: `docs/nasa_atmonto_gold_annotation_guide.md`

## Research Questions

- **RQ1**: Can schema-constrained LLM extraction produce valid and
  evidence-linked event records from ATCSCC advisories?
- **RQ2**: Does an agentic validation-refinement loop reduce schema violations
  and unsupported relations?
- **RQ3**: Does KG-RAG improve evidence grounding and citation quality compared
  with vector-only RAG?
- **RQ4**: What failure types remain, and where does human review remain
  necessary?

## Pipeline Overview

```text
FAA ATCSCC advisories
  -> source snapshot and advisory parser
  -> lightweight ATCSCC application schema/profile
  -> extraction systems and baselines
       S0 rule backbone
       S1 open LLM / canonicalized diagnostic
       S2 schema-slice LLM
       S3 validator-repair
       S4 hybrid backbone + semantic enrichment
  -> agentic validation-refinement loop
       extractor -> validator -> refiner -> critic
  -> advisory event graph / fact store
  -> vector, graph, and routed KG-RAG retrieval
  -> answer generation and citation checks
  -> failure analysis and human-review boundary
```

Every stage must emit an explicit artifact. Do not run extractor, repair,
retrieval, or report-synthesis agents directly from vague paper summaries or
unbounded prompts.

## Step 0: Lock Claim Boundary

Inputs:

- `docs/thesis_positioning.md`
- `reports/stages/thesis_claims_review.md`
- `reports/stages/nasa_atmonto_reviewer_defense_audit.md`

Rules:

- The thesis is not an ontology-construction thesis.
- The schema/profile is an engineering constraint.
- GraphRAG is evaluated as source-bounded grounding evidence, not as a universal
  Recall@k winner.
- Automated diagnostics are not human review or expert certification.
- The system is not live operational ATC decision support.

## Step 1: Define Source Corpus

Primary source family:

- FAA ATCSCC advisories from the frozen retrospective project snapshot.

Use these reports for data explanation:

- `reports/stages/atcscc_source_brief.md`
- `reports/stages/atcscc_data_format_and_processing_flow.md`
- `reports/stages/atcscc_event_centric_extraction_framing.md`

Source-family boundary:

- ATCSCC advisories are the main event-extraction and QA corpus.
- FAA/NASA PDFs, NASR, and other references can support terminology or schema
  design, but they are not mixed into the ATCSCC semantic F1 table.
- NASA BGA is only a bounded transfer pilot, not proof of domain-general
  validity.

## Step 2: Define Lightweight Application Schema

Use ATMONTO as a reference vocabulary and schema/profile backbone:

- `reports/stages/atcscc_ontology_profile_overview.md`
- `data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json`
- `data/ontology/curated/nasa_atmonto_schema_catalog.json`

The schema constrains:

- event classes such as `GroundStopTMI`, `GroundDelayProgramTMI`,
  `ReRouteTMI`, and `TrafficManagementInitiative`;
- event fields such as advisory number, affected NAS element, cause, status,
  start/end time, reroute type, and route reason;
- provenance fields such as source ID and evidence span.

Completeness and correctness are task-relative:

- **schema completeness**: covers the fields needed by the primary CQs;
- **source-observable completeness**: only facts stated in advisories count;
- **correctness**: measured against reviewed source-bounded labels, not against
  all aviation knowledge.

## Step 3: Prepare Gold And Baselines

Main artifacts:

- `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- `data/experiments/nasa_atmonto/formal/input_records.jsonl`
- `data/experiments/nasa_atmonto/formal/system_specs.json`
- `reports/stages/nasa_atmonto_gold_annotation_validation.md`
- `reports/stages/nasa_atmonto_prediction_output_validation.md`

Extraction systems:

- **S0**: rule-only deterministic backbone.
- **S1**: open LLM / diagnostic baseline.
- **S1b**: canonicalized open extraction diagnostic where applicable.
- **S2**: schema-slice LLM extraction.
- **S3**: schema-slice LLM plus validator/repair.
- **S4**: hybrid deterministic backbone plus semantic enrichment.
- **S5/S6**: agentic validation, evidence checking, refinement, and critic
  diagnostics.

Report structural validity, evidence support, and semantic precision/recall/F1
separately.

## Step 4: Score Extraction And Profile Behavior

Primary reports:

- `reports/stages/nasa_atmonto_formal_experiment_scoring.md`
- `reports/stages/nasa_atmonto_rejection_error_analysis.md`
- `reports/stages/nasa_atmonto_rejection_adjudication.md`
- `reports/stages/nasa_atmonto_cq_evaluation.md`

Primary metrics:

- accepted fact count;
- rejected fact count;
- structural acceptance rate;
- schema violation count;
- precision, recall, and F1 against reviewed facts;
- provenance completeness;
- unsupported relation rate.

Claim boundary:

- schema validity is not semantic correctness;
- a profile gap is not automatically an ontology gap;
- deterministic extraction can outperform live agents on semi-structured
  advisory text and should not be hidden.

## Step 5: Run Agentic Validation-Refinement Diagnostics

Primary reports:

- `reports/stages/atcscc_agentic_artifact_contract.md`
- `reports/stages/nasa_atmonto_s5_s6_agentic_loop.md`
- `reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.md`
- `reports/stages/nasa_atmonto_s5_s6_live_agentic_pilot.md`
- `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`
- `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md`

Required interpretation:

- the agent loop is an auditable extraction/validation workflow;
- it is not evidence that autonomous agents build a correct ontology;
- negative diagnostic results are useful if they identify failure types and
  repair boundaries.

## Step 6: Materialize Graph And Evaluate Retrieval

Primary reports:

- `reports/stages/atcscc_graph_use_plan.md`
- `reports/stages/nasa_atmonto_s7_retrieval.md`
- `reports/stages/nasa_atmonto_s7_graph_health.md`

Retrieval modes:

- source-only / lexical source retrieval;
- token-matched vector proxy;
- dense/vector retrieval where available;
- graph-only retrieval;
- hybrid KG-RAG;
- routed KG-RAG.

Primary metrics:

- answer-set F1;
- target-source hit rate;
- graph-context availability;
- graph-use rate;
- path support diagnostics;
- context token budget.

Claim boundary:

- graph evidence can improve source-bounded grounding diagnostics;
- do not claim universal GraphRAG superiority.

## Step 7: Evaluate Answer Generation

Primary reports:

- `reports/stages/nasa_atmonto_answer_generation.md`
- `reports/stages/nasa_atmonto_s7_answer_generation.md`
- `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`
- `reports/stages/nasa_atmonto_s7_llm_failure_review.md`
- `reports/stages/nasa_atmonto_s7_partial_answer_ablation.md`

Primary metrics:

- answer correctness;
- answer-set F1;
- citation precision;
- citation recall;
- evidence faithfulness;
- unsupported claim rate;
- abstention correctness.

Interpret deterministic, LLM-judge, and human-review scores separately.

## Step 8: Review Failures And Human-Review Boundary

Primary reports:

- `reports/stages/nasa_atmonto_s7_human_review_candidates.md`
- `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.md`
- `reports/stages/nasa_atmonto_s7_answer_review_protocol.md`
- `reports/stages/nasa_atmonto_s7_answer_review_import.md`
- `reports/stages/nasa_atmonto_s7_answer_review_decisions.md`
- `reports/stages/nasa_atmonto_s7_candidate_adjudication.md`
- `reports/stages/nasa_atmonto_s7_profile_decision.md`
- `reports/stages/nasa_atmonto_s7_automated_adversarial_review.md`

Failure categories:

- extraction error;
- unsupported relation;
- evidence-span miss;
- profile/gold-boundary gap;
- retrieval source miss;
- answer overreach;
- abstention error;
- case requiring human review.

Automated adversarial review is an internal consistency diagnostic. It does not
replace human or expert review.

## Step 9: Synthesize Thesis-Ready Claims

Primary reports:

- `reports/stages/thesis_claims_review.md`
- `reports/stages/thesis_experiment_dashboard.md`
- `reports/stages/nasa_atmonto_sota_goal_audit.md`
- `reports/stages/nasa_atmonto_reviewer_defense_audit.md`
- `reports/stages/nasa_atmonto_experiment_chapter_draft.md`

For each RQ, record:

- evidence reports;
- primary metrics;
- result summary;
- supported claim strength;
- remaining gap;
- forbidden overclaim.

## Recommended Regeneration Commands

```bash
uv sync --extra dev --extra graphrag
uv run aviation-ai report thesis-claims
uv run aviation-ai report nasa-atmonto-answer-generation
uv run python scripts/build_nasa_atmonto_sota_goal_audit.py
uv run python scripts/build_nasa_atmonto_reviewer_defense_audit.py
uv run aviation-ai report thesis-experiment-dashboard
uv run ruff check .
uv run pytest -q
```

Use `reports/stages/thesis_experiment_dashboard.md` as the current state table,
not as a substitute for reading the underlying reports.
