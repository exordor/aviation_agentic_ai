# Schema-Constrained Agentic KG-RAG for Evidence-Grounded Question Answering over FAA ATCSCC Advisories

> Status: master-project report. Core chapters (Introduction, Data, Schema,
> Method, Experiments, Discussion, Conclusion) are filled; remaining chapters
> are structured skeletons that map to existing evidence documents. A
> chapter-completeness table appears at the end.

## Abstract

This project studies evidence-grounded question answering over retrospective
FAA ATCSCC advisories. ATCSCC advisories are public, semi-structured operational
notices describing traffic-management initiatives, affected NAS elements, route
or airport constraints, effective time windows, and causes. The contribution is
not a complete aviation ontology. The contribution is a reproducible method that
uses a lightweight NASA ATMONTO-derived application schema to constrain advisory
event extraction, an agentic validator/refiner/critic loop to repair or reject
candidate facts before graph insertion, and a source-bounded KG-RAG evaluation
that compares graph-augmented retrieval against a matched vector-only baseline.

The headline empirical result is a same-question, same-retriever head-to-head:
on 30 ATCSCC competency questions, KG-RAG (routed, critic-gated graph + lexical
vector) reaches 0.967 answer correctness and 0.017 unsupported-claim rate,
versus 0.500 and 0.500 for the matched vector-only arm — with the gain
concentrated on relation-oriented templates where pure text retrieval cannot
recover structured predicate facts. The work is retrospective and
source-bounded; it does not claim GraphRAG universally beats vector-only
retrieval, and it is not operational ATC decision support.

## Chapter 1. Introduction

### 1.1 Motivation

Air Traffic Control System Command Center (ATCSCC) advisories are the primary
public record of national-level traffic-management initiatives in the US
National Airspace System (NAS). They are short, semi-structured texts: each
advisory carries an identifier, affected NAS elements, an effective time window,
a cause/condition, and free-text operational context. Because many facts are
visible in the source text and checkable against evidence spans, they are a
useful case study for evidence-grounded information extraction — but they are
not clean tabular data, so naive extraction over- or under-generates.

### 1.2 Problem and Contribution

The research problem is: can a lightweight application schema constrain LLM
extraction of advisory events, support agentic validation/refinement, and
provide an inspectable advisory event graph that improves source-bounded
question answering and citation quality?

The methodological contribution is the integration of four mature areas under
one bounded source family: schema-guided extraction, KG quality evaluation,
GraphRAG diagnostics, and multi-agent validation. The safe novelty claim is
**methodological integration under a bounded source family**, not a new general
GraphRAG algorithm or a complete aviation ontology.

### 1.3 Research Questions

- **RQ1** — Schema-constrained extraction: Can schema-constrained LLM extraction
  produce valid and evidence-linked event records from ATCSCC advisories?
- **RQ2** — Agentic validation-refinement: Does a validator/refiner/critic loop
  reduce schema violations and unsupported relations?
- **RQ3** — KG-RAG grounding: Does KG-RAG improve evidence grounding and
  citation quality compared with vector-only RAG?
- **RQ4** — Failure boundary: What failure types remain, and where does human
  review remain necessary?

### 1.4 Scope and Claim Boundaries

The prototype treats the ontology/profile as an engineering constraint, not as
the research object. It is evaluated with layered metrics and does not collapse
them into one overall score. Out of scope: complete aviation-domain ontology
coverage, live operational ATC decision support, operational safety
certification, universal KG-RAG superiority, and semantic correctness beyond
reviewed evidence.

**Evidence spine:** `docs/thesis_positioning.md`, `docs/research_mainline.md`,
`reports/stages/thesis_experiment_dashboard.md`.

## Chapter 2. Background and Related Work

> Skeleton — populated from existing annotated-bibliography artifacts. To be
> written as integrated prose.

The project is positioned at the intersection of four method areas rather than
as a claim that ATCSCC ontology research is itself a large SOTA field.

| SOTA area | What this thesis borrows | What this thesis contributes |
| --- | --- | --- |
| Schema-guided / ontology-guided IE | Domain schema constrains classes, predicates, values, output contracts | A source-native ATCSCC advisory-event profile with evidence-span requirements and profile-gap handling |
| Knowledge-graph quality evaluation | Separate completeness, correctness, conformance, provenance, error repair | A layered metric protocol (schema validity, evidence support, extraction F1, retrieval, answer grounding, review boundaries) |
| GraphRAG and citation-faithful QA | Compare vector, graph, hybrid, routed retrieval | A source-bounded ATCSCC KG-RAG benchmark with answer-set, citation, unsupported-claim, and abstention diagnostics |
| Multi-agent validation/refinement | Role-separated extractor, validator, refiner, critic loops | An auditable agentic loop for extraction repair/rejection under hard schema and evidence gates |

**Source material (annotated bibliography, ready to integrate):**
`reports/stages/agentic_ontology_graphrag_mainline_literature_search.md`
(8-query search log; core papers: Text2KGBench, OntoLogX, Document GraphRAG,
AIRM/ATM ontology matching),
`reports/stages/sota_comparison_matrix.md` (14-criterion criteria matrix),
`reports/stages/chatatc_paper_analysis.md` (aviation LLM related-work framing),
`reports/stages/top_reference_papers_for_atmonto_graphrag.md`.

## Chapter 3. Data and Task Definition

### 3.1 Source Family

The study uses a retrospective ATCSCC snapshot (advisories 2026-05-14 through
2026-05-20). Source family is kept separate from FAA/NASA reference PDFs, NASR
data, and weather data.

| Layer | Records | Artifact |
| --- | ---: | --- |
| Downloaded advisory pages | 867 | `data/raw/nasa_atmonto/2026-05-14/atcscc_advisories/` |
| Processed source records | 867 | `data/processed/nasa_atmonto/source/2026-05-14/atcscc_advisories.jsonl` |
| Temporally aligned records | 718 | aligned JSONL |
| Formal experiment sample | 100 | `data/experiments/nasa_atmonto/formal/input_records.jsonl` |
| Reviewed gold records | 100 | `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl` |

Candidate classes in the reviewed gold set: `GroundDelayProgramTMI` (16),
`GroundStopTMI` (21), `ReRouteTMI` (23), `TrafficManagementInitiative` (40).

### 3.2 Raw Format and Task

Each advisory is an HTML page whose payload is a short table: a header row
(e.g. `ATCSCC ADVZY 007 ... CDM GROUND STOP`), a `MESSAGE:` `<PRE>` block, an
`EFFECTIVE TIME:` row, and a `SIGNATURE:` row. The task is advisory-event ABox
extraction: produce schema-valid facts (TMI type, affected NAS elements,
effective start/end time, cause/condition, implementation status, route
constraints) each tied to an evidence span.

**Evidence spine:** `reports/stages/atcscc_data_format_and_processing_flow.md`,
`reports/stages/atcscc_source_brief.md`.

## Chapter 4. Application Schema / Profile

The ontology stack has three layers: external NASA ATMONTO OWL → parsed schema
catalog → ATCSCC schema slice → extraction JSON schema.

| Component | Count |
| --- | ---: |
| Classes | 18 |
| Object properties | 11 |
| Datatype properties | 11 |
| Class hierarchy axioms | 33 |

The profile boundary is:

```text
NASA ATMONTO full ontology
  -> parsed schema catalog
  -> ATCSCC traffic-management schema slice
  -> extraction JSON schema
  -> candidate facts with evidence
  -> validator / reviewer decisions
```

S0 owns deterministic fields (`advisoryNumber`, `issuedTime`,
`effectiveStartTime/EndTime`, header/template fields). S3/S4 may add but not
overwrite semantic fields. Quarantine/review conditions: conflict, unsupported
span, fuzzy-only mapping, validator-rejected fact, repair-only fact with a
semantic-change flag.

**Evidence spine:** `reports/stages/atcscc_ontology_profile_overview.md`,
`reports/stages/atcscc_semantic_requirements.md`.

## Chapter 5. Method

The method is a five-block pipeline, executable end-to-end and reproduced by
the `aviation-ai demo` command on precomputed artifacts:

```text
FAA ATCSCC advisories
  -> lightweight ATCSCC application schema/profile
  -> S0-S4 extraction baselines + extractor/validator/refiner/critic loop
  -> advisory event graph with evidence spans
  -> vector / graph / hybrid / routed KG-RAG + answer generation, citation checks, failure review
```

### 5.1 Extraction stages (RQ1)

- **S0** rule-only deterministic backbone over advisory templates.
- **S1/S1b** LLM-only (raw open extraction, drift diagnostic) and canonicalized
  to the target schema (the comparable LLM baseline).
- **S2** schema-slice LLM extraction (gpt-5.4-mini).
- **S3** validator-repair: deterministic validator + LLM refiner.
- **S4** hybrid backbone enrichment: S0 deterministic backbone + LLM semantic
  enrichment, gated so deterministic fields cannot be overwritten.

### 5.2 Agentic loop (RQ2)

Role-separated extractor / validator / refiner / critic artifacts record repair
and rejection outcomes. The loop is an auditable diagnostic and repair
framework; it is not autonomous ontology construction.

### 5.3 KG-RAG evaluation (RQ3)

Retrieval modes over frozen ATCSCC contexts: `source_oracle`, lexical-vector
proxies, `live_tfidf_vector` (real lexical retriever), `dense_embedding_vector`
(all-MiniLM-L6-v2), `graph_only`, `hybrid_graphrag`, and routed variants. The
routed mode uses template routing: graph context for entity/cause/status/route
templates; vector/source for time-window and abstention templates.

### 5.4 Failure review (RQ4)

Automated consistency diagnostics, a human-review candidate packet, candidate
adjudication, and a profile-decision what-if. Automated diagnostics are an
internal error-discovery layer, not human review or expert certification.

**Evidence spine:** `docs/experiment_workflow.md`,
`reports/stages/atcscc_agentic_artifact_contract.md`,
`reports/stages/nasa_atmonto_formal_experiment_scoring.md`.

## Chapter 6. Evaluation Design

Layered metrics, no mixed overall score. Each RQ has an experiment layer,
explicit metrics, tracked artifacts, and a pass/fail interpretation.

| Layer | Metrics |
| --- | --- |
| Schema-constrained extraction | schema validity, structural acceptance rate, rejected/repaired fact count |
| Evidence support | evidence-span coverage, unsupported relation rate, provenance completeness, reviewed-subset P/R/F1 |
| Agentic loop | violation reduction, repair success, critic rejection count, post-loop F1 |
| Retrieval and KG-RAG | answer-set F1, target-source hit rate, citation P/R, evidence faithfulness |
| Failure and review boundary | failure category counts, abstention correctness, profile/gold-boundary cases |

Bootstrap 95% CIs are reported for extraction F1 (record-bootstrap by source_id,
200 iterations, seed 1701).

**Evidence spine:** `docs/evaluation_protocol.md`, `docs/research_mainline.md`.

## Chapter 7. Experiments and Results

### 7.1 Experiment A — Schema-constrained advisory event extraction (RQ1)

Scored against the frozen 100-record reviewed gold set, strict semantic F1.
Provenance completeness = 1.0, evidence-in-source rate = 1.0, valid triples =
448.

| System | Precision | Recall | F1 | Schema violation rate | Structural acceptance |
| --- | ---: | ---: | ---: | ---: | ---: |
| S0 rule-only | 0.8163 | 0.7097 | **0.7592** | 0.0780 | 0.9220 |
| S1 LLM-only (open) | — (diagnostic; P=R=F1=0.0 against target schema) | 1.0 | 0.0 |
| S1b LLM canonicalized | 0.4974 | 0.1444 | 0.2238 | 0.5837 | 0.4163 |
| S2 schema-slice LLM | 0.2062 | 0.1843 | 0.1946 | 0.1751 | 0.8249 |
| S3 validator-repair | 0.2423 | 0.1321 | 0.1710 | 0.1035 | 0.8965 |
| S4 hybrid backbone enrichment | 0.6857 | 0.7742 | **0.7273** | 0.0000 | 1.0000 |

Bootstrap 95% CIs (F1): S0 0.708–0.804, S2 0.144–0.240, S4 0.681–0.763.

**Reading (RQ1):** The deterministic S0 backbone is the strongest single
extractor for these semi-structured advisories (F1 0.759), and S4 hybrid
enrichment (0.727) preserves deterministic correctness while adding semantic
fields with zero schema violations. The pure-LLM arms (S1b/S2/S3) are markedly
weaker — a negative result consistent with semi-structured short-text
extraction being hard for unconstrained LLMs. The schema constraint is
effective: S1b's structural acceptance is only 0.42 versus S2/S3/S4 ≥ 0.82, and
unconstrained open LLM output (S1) scores zero against the target schema,
confirming that raw open LLM extraction must not be scored with target-schema
P/R/F1.

### 7.2 Experiment B — Agentic validation and CQ queryability (RQ2)

The validator/refiner/critic loop records auditable repair and rejection
decisions (S3 repair success 0.8965; S4 repair success 1.0, quarantine 0). The
S5/S6 live agentic full run over 100 reviewed samples is a bounded
extraction-layer method artifact. Per the claim boundary, the loop is a
diagnostic and repair framework; it is not autonomous ontology construction,
and deterministic parsing remains stronger than live LLM extraction on these
advisories — a negative method result reported directly.

**Evidence spine:** `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`,
`..._diagnostic.md`, `reports/stages/nasa_atmonto_cq_evaluation.md`.

### 7.3 Experiment C — KG-RAG grounding and answer generation (RQ3)

#### 7.3.1 Retrieval-only diagnostics (317 cases)

Recall@5 is non-discriminating on ATCSCC (0.6845 for most modes including the
real `live_tfidf_vector` baseline); the signal is in Answer F1 and abstention.
Forcing graph context everywhere (`graph_only`, `hybrid_graphrag`) collapses on
abstention (F1 0.5205, abstention-correct 0.01) — the router exists precisely
to suppress graph use on abstention/time-window templates.

| Mode | Recall@5 | Answer F1 | Abstention correct |
| --- | ---: | ---: | ---: |
| live_tfidf_vector (real lexical) | 0.6845 | 0.8235 | 1.0 |
| graph_only | 0.6845 | 0.5205 | 0.01 |
| hybrid_graphrag | 0.6845 | 0.5205 | 0.01 |
| routed_graphrag | 0.6845 | 0.9833 | 1.0 |

#### 7.3.2 Head-to-head LLM answers: KG-RAG vs vector-only (same 30 questions)

Same LLM (`gpt-5.4-mini`), same frozen retrieved contexts, same questions. The
two arms differ only in retrieval mode.

| Mode | Questions | Correctness | Unsupported claim rate | Citation recall |
| --- | ---: | ---: | ---: | ---: |
| KG-RAG (routed, graph+critic) | 30 | **0.9667** | **0.0167** | 0.6084 |
| Vector-only (live tfidf, no graph) | 30 | 0.5000 | 0.5000 | 0.3722 |

Per-template mechanism (vector-only arm): it ties or wins on
`QT-A01-ABSTENTION-FIELDS` (1.0), `QT-Q01-TIME-WINDOW` (1.0), and
`QT-Q01-ROUTE-SEMANTICS` (1.0), but collapses on
`QT-Q01-AFFECTED-NAS-ELEMENTS` (0.0, unsupported=1.0),
`QT-Q01-CAUSE-CONDITION` (0.0, unsupported=1.0), and
`QT-Q01-STATUS-ACTION` (0.0, unsupported=1.0) — exactly the templates where
pure text retrieval cannot recover structured predicate facts and where the
router selects graph context.

**Reading (RQ3):** On this source-bounded ATCSCC benchmark, KG-RAG
approximately doubles answer correctness and cuts the unsupported-claim rate by
~30x versus the matched vector-only arm, with the gain concentrated on
relation-oriented templates. The Retrieval-only Answer-F1 gap is narrower than
the LLM-answer gap, indicating the graph's value is larger at the
answer-correctness layer than at the retrieval-F1 proxy. This is retrospective,
source-bounded evidence on 30 questions — not a universal GraphRAG claim.

**Evidence spine:** `reports/stages/nasa_atmonto_s7_retrieval.md` (head-to-head
section), `reports/stages/nasa_atmonto_s7_llm_answer_generation.json` (KG-RAG),
`reports/stages/nasa_atmonto_s7_vector_only_llm_answer_generation.json`
(vector-only).

### 7.4 Experiment D — Failure analysis and human-review boundary (RQ4)

9 generated-answer cases were packaged for review (including the 3 current
failures). Deterministic adjudication classifies the 3 failures as
profile/gold-boundary cases and leaves strict S7 metrics unchanged. The
profile-decision what-if shows a predicate whitelist would correct those 3
selected records, but it does not replace strict metrics or change gold/profile
artifacts. Remaining failure categories: extraction error, retrieval context
error, profile/gold-boundary gap, answer overreach, and human-review cases.

**Evidence spine:** `reports/stages/nasa_atmonto_s7_human_review_candidates.md`,
`reports/stages/nasa_atmonto_s7_candidate_adjudication.md`,
`reports/stages/nasa_atmonto_s7_profile_decision.md`,
`reports/stages/nasa_atmonto_reviewer_defense_audit.md`.

## Chapter 8. Discussion

### 8.1 What the evidence supports

- The application schema constrains which advisory event fields and relations
  enter the graph (schema validity, structural acceptance, profile-gap
  handling).
- Accepted facts preserve source IDs and evidence spans at the artifact level
  (provenance completeness 1.0).
- KG-RAG adds inspectable structured evidence and improves answer correctness
  on relation-oriented ATCSCC questions on this benchmark.
- The agentic loop is a useful auditable repair/rejection framework even though
  deterministic extraction remains stronger on semi-structured advisories.

### 8.2 Negative results reported directly

- Pure-LLM extraction (S1b/S2/S3) underperforms deterministic S0 — agentic
  orchestration is useful for audit and repair, not autonomous ontology
  construction.
- Forcing graph context everywhere hurts abstention handling (F1 0.52); the
  router, not unconditional graph use, is what helps.
- Recall@5 is non-discriminating on ATCSCC; KG-RAG's win is at the
  answer-correctness layer, not retrieval recall.

### 8.3 What the evidence does not support

Complete aviation-domain ontology coverage, operational ATC decision support,
operational safety certification, universal KG-RAG superiority, and semantic
correctness beyond reviewed evidence. Human/expert review remains separate from
automated diagnostics.

## Chapter 9. Threats to Validity

> Skeleton — to be expanded.

- **Construct validity:** strict semantic F1 penalizes evidence-span mismatch;
  an evidence-tolerant variant is implemented (drops the evidence_text key) and
  raises LLM-system F1, so strict numbers are conservative lower bounds.
- **Internal validity:** RQ3 comparison uses the same questions, retriever, and
  LLM; the only varying factor is retrieval mode (graph presence + routing).
- **External validity:** 30 matched questions on one source family over one
  advisory week; not domain-general proof.
- **Conclusion validity:** bootstrap CIs reported for extraction F1; RQ3 is a
  fixed-budget LLM run, not human review.

**Evidence spine:** `docs/thesis_positioning.md`,
`reports/stages/nasa_atmonto_reviewer_defense_audit.md`,
`reports/stages/nasa_atmonto_sota_goal_audit.md`.

## Chapter 10. Conclusion

This project implements a reproducible schema-constrained Agentic KG-RAG
prototype over retrospective FAA ATCSCC advisories. The application schema
constrains focused advisory-event extraction and supports deterministic
validation; accepted facts carry source provenance and evidence spans; the
agentic loop provides inspectable repair and rejection signals; and a matched
head-to-head shows KG-RAG improves answer correctness and reduces unsupported
claims on relation-oriented ATCSCC questions relative to a vector-only
baseline. Remaining failures and human-review requirements are explicitly
categorized. The thesis claims a bounded method for evidence-grounded advisory
QA, not a certified aviation ontology or a live operational decision-support
system.

### Reproducibility

- CLI end-to-end demo (offline): `uv run aviation-ai demo`
- RQ3 vector-only arm: `uv run python scripts/build_nasa_atmonto_s7_llm_answer_generation.py --run-llm --modes vector-only --report-name nasa_atmonto_s7_vector_only_llm_answer_generation`
- Quality gates: `uv run ruff check .` and `uv run pytest -q`

---

## Chapter Completeness Table

| Chapter | Status | Notes |
| --- | --- | --- |
| 1 Introduction | filled | |
| 2 Background / Related Work | skeleton | annotated bibliography + SOTA matrix ready to integrate into prose |
| 3 Data and Task Definition | filled | |
| 4 Application Schema / Profile | filled | |
| 5 Method | filled | |
| 6 Evaluation Design | filled | |
| 7 Experiments and Results | filled | includes new RQ3 head-to-head (7.3.2) |
| 8 Discussion | filled | |
| 9 Threats to Validity | skeleton | |
| 10 Conclusion | filled | |
