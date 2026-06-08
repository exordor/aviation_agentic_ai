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

## Next Writing Deliverables

- A concise method figure with five blocks: source, schema, agentic extraction,
  event graph/KG-RAG, evaluation.
- A thesis chapter outline using the four RQs above.
- A results table grouped by extraction, agentic loop, retrieval, answers, and
  failure review.
- A related-work matrix that separates aviation LLM systems, schema-guided KG
  extraction, GraphRAG evaluation, and multi-agent workflows.
