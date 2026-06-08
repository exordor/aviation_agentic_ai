# Research Mainline

## One-Line Direction

**Agentic KG-RAG for evidence-grounded question answering over retrospective
FAA ATCSCC advisories.**

The project is not an ontology thesis. It studies how a lightweight
application schema can constrain advisory-event extraction, how an agentic
validation/refinement loop changes extraction behavior, and whether an
advisory event graph improves source-bounded question answering and citation
quality.

## Thesis Story

FAA ATCSCC advisories are public, semi-structured operational texts. They
describe traffic management initiatives, affected NAS elements, time windows,
causes, statuses, and route or airport constraints. They are a narrow but useful
case study for evidence-grounded information extraction because many facts are
visible in the source text and can be checked against evidence spans.

The project uses NASA ATMONTO-derived terms as a lightweight schema/profile.
That profile is a guardrail, not the research object. It defines what an
accepted advisory-event record may contain, and it makes validation, rejection,
repair, and evidence tracing explicit.

The research contribution is a bounded method:

```text
retrospective advisory text
  -> schema-constrained extraction
  -> agentic validation/refinement/critic loop
  -> advisory event graph with evidence spans
  -> vector / graph / routed KG-RAG
  -> source-grounded answers and failure analysis
```

## Research Questions

1. **RQ1: Schema-constrained extraction**
   Can schema-constrained LLM extraction produce valid and evidence-linked
   event records from ATCSCC advisories?

2. **RQ2: Agentic validation-refinement**
   Does an agentic validation-refinement loop reduce schema violations and
   unsupported relations?

3. **RQ3: KG-RAG grounding**
   Does KG-RAG improve evidence grounding and citation quality compared with
   vector-only RAG?

4. **RQ4: Failure boundary**
   What failure types remain, and where does human review remain necessary?

## Validation Matrix

The thesis should be evaluated as a set of linked gates, not as one overall
score. Each RQ must have an experiment layer, explicit metrics, tracked
artifacts, and a pass/fail interpretation.

| RQ | Experiment layer | Baselines / systems | Primary metrics | Evidence artifacts | Pass criterion | Fail or limit criterion |
| --- | --- | --- | --- | --- | --- | --- |
| RQ1: schema-constrained extraction | Reviewed ATCSCC event-fact extraction over the frozen 100-record sample. | S0 rule-only, S1 LLM-only, S1b canonicalized LLM, S2 schema-slice LLM, S3 validator/repair, S4 hybrid merge. | JSON validity, schema violation rate, structural acceptance rate, triple precision/recall/F1, evidence containment, provenance completeness. | `reports/stages/nasa_atmonto_formal_experiment_scoring.md`, `reports/stages/nasa_atmonto_prediction_output_validation.md`, `reports/stages/nasa_atmonto_cq_evaluation.md`. | The schema-constrained or validator-gated system improves valid evidence-linked facts over weakly constrained LLM output, while deterministic fields remain protected. | If schema validity improves only by dropping useful source-supported facts, report it as a profile-gap or recall tradeoff rather than semantic correctness. |
| RQ2: agentic validation-refinement | Extractor / validator / refiner / critic loop over ATCSCC candidate facts. | Pre-loop candidate extraction, deterministic validator, critic-filtered output, refiner output, independent and live S5/S6 runs. | Violation reduction, unsupported-relation reduction, repair success, quarantine/rejection count, critic acceptance/rejection reasons, post-loop extraction F1. | `reports/stages/atcscc_agentic_artifact_contract.md`, `reports/stages/nasa_atmonto_agentic_loop.md`, `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`, `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md`. | The loop produces auditable repair/rejection decisions and reduces specific schema or support failures without silently overwriting protected deterministic facts. | If live LLM extraction underperforms deterministic extraction, state this as a negative method result: agentic orchestration is useful for audit and repair, not autonomous ontology construction. |
| RQ3: KG-RAG grounding | Source-bounded ATCSCC retrieval and answer generation. | Source-only, vector RAG, graph-only retrieval, token-matched GraphRAG, routed/hybrid KG-RAG. | Answer-set F1, target-source hit rate, citation precision, citation recall, evidence faithfulness, unsupported claim rate, abstention correctness. | `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_graph_health.md`, `reports/stages/nasa_atmonto_answer_generation.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`. | KG/hybrid modes improve at least some relation-oriented grounding or citation diagnostics while vector-only remains a fair baseline for source-local questions. | If graph retrieval does not improve Recall@k or answer accuracy broadly, keep the claim to source-bounded grounding diagnostics and failure analysis. |
| RQ4: failure boundary | Reviewer-defense, answer-review, profile-decision, and claim-safety audits. | Automated consistency diagnostic, human-review packet, candidate adjudication, profile/gold-boundary what-if analysis. | Failure category counts, unsupported-claim rate, profile-gap count, abstention correctness, human-review completion status, expert-certification status. | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md`, `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.md`, `reports/stages/nasa_atmonto_s7_answer_review_decisions.md`, `reports/stages/nasa_atmonto_s7_profile_decision.md`. | The thesis explicitly separates automated diagnostics from human or expert review and lists remaining failure types with claim impact. | If human answer review or expert certification is incomplete, do not claim human-reviewed answer quality, external certification, or operational readiness. |

## Acceptance Gates

The research mainline is thesis-ready only if the following gates hold in the
current repository state:

| Gate | Required evidence |
| --- | --- |
| Scope gate | `docs/thesis_positioning.md` and this document state that the work is schema-constrained Agentic KG-RAG, not ontology engineering or live ATC decision support. |
| Data gate | `reports/stages/atcscc_data_format_and_processing_flow.md` documents the ATCSCC source format, frozen snapshot, processed JSONL shape, and reviewed 100-record gold set. |
| Schema/profile gate | `reports/stages/atcscc_ontology_profile_overview.md` documents the NASA ATMONTO-derived ATCSCC profile, slice size, properties, constraints, and profile-gap policy. |
| CQ gate | `reports/stages/nasa_atmonto_competency_questions.md` keeps exactly 12 primary CQs with fields, metrics, failure modes, and deferred cross-source questions. |
| Experiment gate | Extraction, agentic loop, retrieval, answer-generation, and reviewer-defense reports are present and linked from `docs/documentation_map.md`. |
| Claim-safety gate | `reports/stages/nasa_atmonto_sota_goal_audit.md` and `reports/stages/nasa_atmonto_reviewer_defense_audit.md` pass for internal diagnostic and retrospective case-study claims, while keeping human review, expert certification, operational use, and domain-general proof false unless separately completed. |
| Reproducibility gate | Report regeneration commands do not create unintended dirty diffs; `uv run ruff check .` and `uv run pytest -q` pass before merging. |
| Git hygiene gate | Large/local/generated artifacts remain ignored unless they are referenced by the thesis dashboard or a claim-safety audit. |

## Method Components

| Component | Role | Primary artifacts |
| --- | --- | --- |
| ATCSCC source snapshot | Retrospective advisory corpus | `atcscc_source_brief.md`, `atcscc_data_format_and_processing_flow.md` |
| Application schema/profile | Constraint for accepted event records | `atcscc_ontology_profile_overview.md`, `nasa_atmonto_atcscc_extraction_schema.json` |
| Extraction baselines | Compare rules, LLM, schema-slice, repair, and hybrid extraction | `nasa_atmonto_formal_experiment_scoring.md` |
| Agentic loop | Extractor, validator, refiner, critic diagnostics | `nasa_atmonto_s5_s6_*` reports |
| Advisory event graph | Evidence-linked fact store for retrieval | S4/S5/S6 fact artifacts and S7 graph reports |
| KG-RAG evaluation | Vector, graph, hybrid, routed comparisons | `nasa_atmonto_s7_retrieval.md`, `nasa_atmonto_s7_graph_health.md` |
| Answer generation | Source-bounded generated answers and citations | `nasa_atmonto_s7_llm_answer_generation.md` |
| Review boundary | Automated diagnostics vs human/expert review | `nasa_atmonto_reviewer_defense_audit.md`, `nasa_atmonto_sota_goal_audit.md` |

## Current Thesis-Usable Claims

- The ATCSCC application schema constrains which advisory event fields and
  relations can enter the graph.
- Accepted facts preserve source IDs and evidence spans at the artifact level.
- The agentic loop is useful as an auditable diagnostic and repair framework,
  even when deterministic extraction remains stronger for semi-structured
  advisories.
- KG-RAG adds structured evidence and citation diagnostics for source-bounded
  ATCSCC QA.
- Remaining failures can be categorized into extraction, retrieval, profile/gold
  boundary, answer-overreach, and human-review cases.

## Claims To Avoid

- The project builds a complete aviation ontology.
- NASA ATMONTO is complete ground truth for ATCSCC advisories.
- GraphRAG universally outperforms vector-only RAG.
- Automated review replaces human or expert review.
- The system is safe for live ATC or flight decisions.
- The method is proven domain-general.

## Evidence Spine

Use this order when writing the thesis or preparing slides:

1. Data shape and source boundary: `atcscc_data_format_and_processing_flow.md`
2. Schema/profile boundary: `atcscc_ontology_profile_overview.md`
3. Formal extraction scoring: `nasa_atmonto_formal_experiment_scoring.md`
4. Agentic loop diagnostics: `nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md`
5. Retrieval and graph health: `nasa_atmonto_s7_retrieval.md`,
   `nasa_atmonto_s7_graph_health.md`
6. Answer-generation diagnostics: `nasa_atmonto_s7_llm_answer_generation.md`
7. Failure and review boundary: `nasa_atmonto_reviewer_defense_audit.md`
8. Thesis synthesis: `thesis_experiment_dashboard.md`,
   `nasa_atmonto_experiment_chapter_draft.md`

## How Literature Fits

Literature is used for method migration, not for importing claims. The current
paper-analysis workflow requires full-text and figure/table inspection before a
paper can change experiment design.

Primary literature roles:

- GraphRAG/RAG comparison papers define fair baselines and failure modes.
- Ontology/KG construction papers provide schema-guided extraction and
  validation patterns.
- Multi-agent ontology-generation papers provide role-separated artifact
  handoff patterns.
- Aviation LLM papers such as CHATATC support related-work framing for
  non-safety-critical analysis of historical traffic-flow records.

## SOTA Positioning

The project should be positioned as a thesis-scale system study at the
intersection of four mature method areas rather than as a claim that ATCSCC
ontology research is itself a large SOTA field.

| SOTA area | What the thesis borrows | What the thesis contributes in this project |
| --- | --- | --- |
| Schema-guided / ontology-guided information extraction | Use a domain schema to constrain classes, predicates, values, and output contracts. | A source-native ATCSCC advisory-event profile with evidence-span requirements and profile-gap handling. |
| Knowledge-graph quality evaluation | Separate completeness, correctness, conformance, provenance, and error repair. | A layered metric protocol that reports schema validity, evidence support, extraction F1, retrieval quality, answer grounding, and review boundaries separately. |
| GraphRAG and citation-faithful QA | Compare vector, graph, hybrid, and routed retrieval instead of assuming graph retrieval is always better. | A source-bounded ATCSCC KG-RAG benchmark with answer-set, citation, unsupported-claim, and abstention diagnostics. |
| Multi-agent validation/refinement | Use role-separated extractor, validator, refiner, and critic loops. | An auditable agentic loop for extraction repair and rejection under hard schema and evidence gates. |

The safe novelty claim is therefore methodological integration under a bounded
source family: the thesis adapts schema-guided extraction, KG quality
evaluation, GraphRAG diagnostics, and multi-agent validation to retrospective
FAA ATCSCC advisories. It does not claim to invent a new general GraphRAG
algorithm, construct a complete aviation ontology, or prove domain-general
autonomy.

## Next Writing Deliverables

- A concise method figure with five blocks: source, schema, agentic extraction,
  event graph/KG-RAG, evaluation.
- A thesis chapter outline using the four RQs above.
- A results table grouped by extraction, agentic loop, retrieval, answers, and
  failure review.
- A related-work matrix that separates aviation LLM systems, schema-guided KG
  extraction, GraphRAG evaluation, and multi-agent workflows.
