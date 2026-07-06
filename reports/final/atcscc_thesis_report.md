# Schema-Constrained Agentic KG-RAG for Evidence-Grounded Question Answering over FAA ATCSCC Advisories

> Status: master-project report. Core chapters (Introduction, Data, Schema,
> Method, Experiments, Discussion, Conclusion) are filled; remaining chapters
> are structured skeletons that map to existing evidence documents. A
> chapter-completeness table appears at the end.

## Abstract

This project studies evidence-grounded question answering over retrospective
FAA ATCSCC advisories: public, semi-structured operational notices describing
traffic-management initiatives, affected NAS elements, effective time windows,
and causes. The contribution is a reproducible method that uses a lightweight
NASA ATMONTO-derived application schema to constrain advisory event extraction,
an agentic validator/refiner/critic loop to repair or reject candidate facts
before graph insertion, and a source-bounded KG-RAG evaluation comparing
graph-augmented retrieval against a matched vector-only baseline.

The headline result is a same-question, same-retriever head-to-head on 30 ATCSCC
questions: KG-RAG reaches 0.967 answer correctness and 0.017 unsupported-claim
rate, versus 0.500 and 0.500 for the vector-only arm. Claim boundaries are
defined once in §1.4.

## Chapter 1. Introduction

### 1.1 Motivation

ATCSCC advisories are the primary public record of national-level
traffic-management initiatives in the US National Airspace System (NAS). Because
many facts in each advisory are visible in the source text and checkable against
evidence spans, they are a useful case study for evidence-grounded extraction,
but they are not clean tabular data, so naive extraction over- or
under-generates.

### 1.2 Problem and Contribution

The research problem is: can a lightweight application schema constrain LLM
extraction of advisory events, support agentic validation/refinement, and
provide an inspectable advisory event graph that improves source-bounded
question answering and citation quality?

The methodological contribution is the integration of four mature areas under
one bounded source family: schema-guided extraction, KG quality evaluation,
GraphRAG diagnostics, and multi-agent validation.

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

**Evidence spine:** `RESEARCH_OVERVIEW.md`, `RESEARCH_OVERVIEW.md`,
`reports/stages/nasa_atmonto_s7_retrieval.md`.

## Chapter 2. Background and Related Work

> Skeleton — populated from existing annotated-bibliography artifacts. To be
> written as integrated prose. Inline citation markers `[N]` refer to
> `reports/final/references.md`.

The project is positioned at the intersection of four method areas rather than
as a claim that ATCSCC ontology research is itself a large SOTA field.

| SOTA area | What this thesis borrows | What this thesis contributes | Key references |
| --- | --- | --- | --- |
| Schema-guided / ontology-guided IE | Domain schema constrains classes, predicates, values, output contracts | A source-native ATCSCC advisory-event profile with evidence-span requirements and profile-gap handling | Text2KGBench [18]; ontology methodology [14]; ontology-grounded KG construction [19], [20], [21] |
| Knowledge-graph quality evaluation | Separate completeness, correctness, conformance, provenance, error repair | A layered metric protocol (schema validity, evidence support, extraction F1, retrieval, answer grounding, review boundaries) | KG surveys [8], [9]; auto-KG-construction survey [10]; KG quality survey [11]; KG completeness [12] |
| GraphRAG and citation-faithful QA | Compare vector, graph, hybrid, routed retrieval | A source-bounded ATCSCC KG-RAG benchmark with answer-set, citation, unsupported-claim, and abstention diagnostics | GraphRAG surveys [24], [25]; Local-to-Global GraphRAG [22]; HybridRAG [23]; GraphRAG evaluation [26]–[29]; RAG evaluation [30]–[32] |
| Multi-agent validation/refinement | Role-separated extractor, validator, refiner, critic loops | An auditable agentic loop for extraction repair/rejection under hard schema and evidence gates | Multi-agent ontology generation [19]; LLM-KG survey [13] |
| Aviation / ATM ontology and KG | Source vocabulary and schema backbone | A source-native ATCSCC advisory-event profile derived from ATMONTO | NASA ATMONTO [1]; AIRM-ATMONTO matching [2]; ATM KG [3]; flight-safety ontology [4]; ATM ontological reasoning [5]; ATM semantic interoperability [6]; CHATATC [7]; competency questions [15]–[17] |

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
data, and weather data. Unlike conversational ATC strategic-flow assistants
such as CHATATC [7], this work targets retrospective advisory-event extraction
and evidence-grounded QA, not live decision support.

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

The ontology stack has three layers: external NASA ATMONTO OWL [1] → parsed
schema catalog → ATCSCC schema slice → extraction JSON schema. The ATMONTO
reference ontology [1], [2] provides the vocabulary; the AIRM-ATMONTO alignment
[2] motivates keeping the schema bounded to ATCSCC advisory events rather than
the full NAS.

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

### 5.1 Extraction stages

- **S0** rule-only deterministic backbone over advisory templates.
- **S1/S1b** LLM-only (raw open extraction, drift diagnostic) and canonicalized
  to the target schema (the comparable LLM baseline).
- **S2** schema-slice LLM extraction (gpt-5.4-mini); the schema-guided setting
  follows the ontology-driven extraction paradigm benchmarked by Text2KGBench
  [18].
- **S3** validator-repair: deterministic validator + LLM refiner.
- **S4** hybrid backbone enrichment: S0 deterministic backbone + LLM semantic
  enrichment, gated so deterministic fields cannot be overwritten.

### 5.2 Agentic loop

Role-separated extractor / validator / refiner / critic artifacts record repair
and rejection outcomes. The loop is an auditable diagnostic and repair
framework; it is not autonomous ontology construction. The role-separated agent
design is inspired by multi-agent LLM ontology-generation work [19] and the
broader LLM-empowered KG-construction literature [13], [10].

### 5.3 KG-RAG evaluation

Retrieval modes over frozen ATCSCC contexts: `source_oracle`, lexical-vector
proxies, `live_tfidf_vector` (real lexical retriever), `dense_embedding_vector`
(all-MiniLM-L6-v2), `graph_only`, `hybrid_graphrag`, and routed variants. The
routed mode uses template routing: graph context for entity/cause/status/route
templates; vector/source for time-window and abstention templates. The
graph-augmented retrieval design follows the GraphRAG survey literature
[24], [25] and the hybrid KG+vector paradigm of HybridRAG [23] and the
Local-to-Global GraphRAG [22]; recent benchmark and comparison work [26]–[29]
motivates reporting graph benefit separately from retrieval recall.

### 5.4 Failure review

Automated consistency diagnostics, a human-review candidate packet, candidate
adjudication, and a profile-decision what-if. Automated diagnostics are an
internal error-discovery layer, not human review or expert certification.

**Evidence spine:** `EXPERIMENTS.md`,
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
200 iterations, seed 1701). The answer-evaluation metric design borrows from
the RAGAs [30] and ARES [31] automated RAG-evaluation frameworks and the
broader RAG-evaluation survey [32].

**Evidence spine:** `EXPERIMENTS.md`, `RESEARCH_OVERVIEW.md`.

## Chapter 7. Experiments and Results

### 7.1 Experiment A — Schema-constrained advisory event extraction (RQ1)

**Experimental framing.** RQ1 asks whether schema-constrained LLM extraction
can produce *valid* and evidence-linked records — a feasibility question, not a
SOTA-competitiveness question. The six systems S0–S4 form a controlled
component-ablation ladder (rule baseline → schema-free LLM → schema-slice LLM
→ +validator/repair → +hybrid enrichment), mirroring the schema-guided
ablation design of Text2KGBench [18] and the LLM-KG-construction evaluation
methodology of [13], [10]. Each step isolates one design choice (schema
presence, validator, hybridization). The study deliberately uses a single LLM
(gpt-5.4-mini) to hold the model constant while varying the extraction
contract; cross-LLM generalization is discussed as a threat to external
validity (§9). No external SOTA baseline (e.g., a fine-tuned RE model or a
published system's reported F1) is included, because the ATCSCC advisory-event
task has no prior benchmark to benchmark against; this is itself part of the
contribution (a first profile and gold set for this source family).

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

**Reading (RQ1).** Two findings carry over to the broader schema-guided IE
literature [18], [13]. First, schema presence sharply raises structural
acceptance: S1b's 0.42 versus S2/S3/S4 ≥ 0.82 reproduces the well-documented
schema-as-constraint benefit. Second, on semi-structured short text a
deterministic backbone (S0, F1 0.759) can outperform unconstrained LLM
extraction (S1b/S2/S3 ≤ 0.22), a negative result consistent with the
observation in the KG-construction surveys [10], [13] that LLMs struggle on
short, template-driven text where surface patterns are reliable. The hybrid
S4 (F1 0.727, zero schema violations) shows deterministic backbones and LLM
semantic enrichment can be combined without corrupting structural correctness.
Raw open-LLM output (S1) scores zero against the target schema, confirming
that schema-free extraction must not be evaluated with target-schema P/R/F1.
These are component-level feasibility findings on one ATCSCC sample; they are
not claims that S0/S4 beats published systems.

### 7.2 Experiment B — Agentic validation and CQ queryability (RQ2)

The validator/refiner/critic loop records auditable repair and rejection
decisions (S3 repair success 0.8965; S4 repair success 1.0, quarantine 0). The
S5/S6 live agentic full run over 100 reviewed samples is a bounded
extraction-layer method artifact. Per the claim boundary, the loop is a
diagnostic and repair framework; it is not autonomous ontology construction,
and deterministic parsing remains stronger than live LLM extraction on these
advisories, a negative method result reported directly.

**Evidence spine:** `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`,
`..._diagnostic.md`, `reports/stages/nasa_atmonto_cq_evaluation.md`.

### 7.3 Experiment C — KG-RAG grounding and answer generation (RQ3)

#### 7.3.1 Retrieval-only diagnostics (317 cases)

Recall@5 is non-discriminating on ATCSCC (0.6845 for most modes including the
real `live_tfidf_vector` baseline); the signal is in Answer F1 and abstention.
Forcing graph context everywhere (`graph_only`, `hybrid_graphrag`) collapses on
abstention (F1 0.5205, abstention-correct 0.01); the router suppresses graph
use on abstention/time-window templates.

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
`QT-Q01-STATUS-ACTION` (0.0, unsupported=1.0): the templates where pure text
retrieval cannot recover structured predicate facts and where the router
selects graph context.

**Reading (RQ3):** On this source-bounded ATCSCC benchmark, KG-RAG
approximately doubles answer correctness and cuts the unsupported-claim rate by
~30x versus the matched vector-only arm, with the gain concentrated on
relation-oriented templates. The Retrieval-only Answer-F1 gap is narrower than
the LLM-answer gap, indicating the graph's value is larger at the
answer-correctness layer than at the retrieval-F1 proxy. This is retrospective,
source-bounded evidence on 30 questions, not a universal GraphRAG claim.

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
  enter the graph (S1b structural acceptance 0.42 vs S2/S4 ≥ 0.82).
- Accepted facts preserve source IDs and evidence spans at the artifact level.
- KG-RAG's gain over vector-only is concentrated on relation-oriented templates
  and operates at the answer-correctness layer, not retrieval recall.
- The agentic loop is a useful auditable repair/rejection framework even though
  deterministic extraction remains stronger on semi-structured advisories.

### 8.2 Negative results reported directly

- Pure-LLM extraction (S1b/S2/S3) underperforms deterministic S0; agentic
  orchestration is useful for audit and repair, not autonomous ontology
  construction.
- Forcing graph context everywhere hurts abstention handling; the router, not
  unconditional graph use, is what helps.
- Recall@5 is non-discriminating on ATCSCC; KG-RAG's win is at the
  answer-correctness layer, not retrieval recall.

### 8.3 What the evidence does not support

See §1.4 for the full claim boundary. In short: the results support a bounded
source-bounded method, not complete ontology coverage, operational use,
universal GraphRAG superiority, or correctness beyond reviewed evidence.
Human/expert review remains separate from automated diagnostics.

## Chapter 9. Threats to Validity

> Skeleton — to be expanded.

- **Construct validity:** strict semantic F1 penalizes evidence-span mismatch;
  an evidence-tolerant variant is implemented (drops the evidence_text key) and
  raises LLM-system F1, so strict numbers are conservative lower bounds.
- **Internal validity:** RQ3 comparison uses the same questions, retriever, and
  LLM; the only varying factor is retrieval mode (graph presence + routing).
- **External validity:** 30 matched questions on one source family over one
  advisory week; not domain-general proof.
- **External validity (extraction):** S0–S4 use a single LLM (gpt-5.4-mini)
  with one prompt per arm and no external SOTA baseline; the absolute F1
  values are therefore not directly comparable to published IE systems, and
  cross-model replication is needed before generalizing the component-level
  findings. The ablation structure (schema presence, validator, hybridization)
  follows the standard design of [18], [13], but the effect sizes are
  specific to ATCSCC advisory text.
- **Conclusion validity:** bootstrap CIs reported for extraction F1; RQ3 is a
  fixed-budget LLM run, not human review.

**Evidence spine:** `RESEARCH_OVERVIEW.md`,
`reports/stages/nasa_atmonto_reviewer_defense_audit.md`,
`reports/stages/nasa_atmonto_sota_goal_audit.md`.

## Chapter 10. Conclusion

This project implements a reproducible schema-constrained Agentic KG-RAG
prototype over retrospective FAA ATCSCC advisories. The schema constrains
extraction and supports deterministic validation; accepted facts carry source
provenance and evidence spans; the agentic loop provides inspectable repair and
rejection signals; and a matched head-to-head shows KG-RAG improves answer
correctness and reduces unsupported claims on relation-oriented questions
relative to a vector-only baseline. Remaining failures and human-review
requirements are explicitly categorized (§7.4). Claim boundaries are stated in
§1.4.

### Reproducibility

- CLI end-to-end demo (offline): `uv run aviation-ai demo`
- RQ3 vector-only arm: `uv run python scripts/build_nasa_atmonto_s7_llm_answer_generation.py --run-llm --modes vector-only --report-name nasa_atmonto_s7_vector_only_llm_answer_generation`
- Quality gates: `uv run ruff check .` and `uv run pytest -q`

## Chapter 11. References

The full numbered reference list is maintained in
`reports/final/references.md` (32 entries, grouped by topic). Citation markers
`[N]` below refer to that list. Entries are grouped as: (A) Aviation/ATM
ontology and KG [1]–[7]; (B) KG surveys and quality [8]–[13]; (C) ontology
engineering and competency questions [14]–[17]; (D) schema-guided and LLM-based
KG construction [18]–[21]; (E) RAG methods [22]–[23]; (F) GraphRAG surveys
[24]–[29]; (G) RAG and GraphRAG evaluation [30]–[32].

---

## Chapter Completeness Table

| Chapter | Status | Notes |
| --- | --- | --- |
| 1 Introduction | filled | |
| 2 Background / Related Work | skeleton | annotated bibliography + SOTA matrix ready to integrate into prose; inline citations [1]–[32] added |
| 3 Data and Task Definition | filled | |
| 4 Application Schema / Profile | filled | |
| 5 Method | filled | |
| 6 Evaluation Design | filled | |
| 7 Experiments and Results | filled | includes new RQ3 head-to-head (7.3.2) |
| 8 Discussion | filled | |
| 9 Threats to Validity | skeleton | |
| 10 Conclusion | filled | |
