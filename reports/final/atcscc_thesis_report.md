# Authority-Grounded Cross-Source Agentic KG-RAG for Evidence-Grounded Question Answering over FAA ATCSCC Advisories

> Status: master-project report. The report is organized around a single
> question-evidence-contribution chain: why ATCSCC advisories are the right
> source family, why schema-constrained Agentic KG-RAG is an appropriate method,
> what each experiment shows, and what the bounded take-home message is.

## Abstract

This project studies evidence-grounded question answering over retrospective
FAA ATCSCC advisories linked to versioned terminology, NASR/facility, METAR,
and TAF sources. The advisories are public, semi-structured notices describing
traffic-management initiatives, affected NAS elements, effective time windows,
and causes. The contribution is a reproducible method that uses a lightweight
NASA ATMONTO-derived application schema to constrain advisory event extraction,
an agentic validator/refiner/critic loop to repair or reject candidate facts
before graph insertion. A Source Agent pins source versions and checksums; an
Alignment Agent canonicalizes facility codes and operational abbreviations; a
Linker connects a controlled 68-record cohort to contemporaneous observations
and forecasts; and the answer contract keeps source declarations,
observation/forecast evidence, and non-causal system associations separate.

The single-source headline result is a same-question, same-retriever head-to-head on 30 ATCSCC
questions: KG-RAG reaches 0.967 answer correctness and 0.017 unsupported-claim
rate, versus 0.500 and 0.500 for the vector-only arm. In the cross-source
experiment, a 20-case `GS` challenge reaches 1.00 accepted-target accuracy and
1.00 quarantine accuracy with zero out-of-registry acceptances. On 24 matched
questions, required evidence/citation-layer coverage is 0.25 for source-only,
0.75 for linked text, and 1.00 for KG-layered answers; an independent
Evaluation Agent passes 24/24 evidence audits. These are retrospective,
source-bounded results, not causal weather attribution or operational advice.

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
provide an inspectable cross-source event graph that improves source-bounded
question answering and citation quality while autonomously quarantining
unresolved ambiguity?

The methodological contribution is the integration of four mature areas under
one bounded event corpus and explicitly profiled supporting sources:
schema-guided extraction, authority-grounded canonicalization, KG quality
evaluation, cross-source GraphRAG diagnostics, and multi-agent validation.

### 1.3 Research Questions

- **Extraction and canonicalization** — Can schema-constrained extraction
  produce valid, evidence-linked ATCSCC event records?
- **Agentic validation and ambiguity** — Can role-separated agents reduce
  unsupported facts and resolve or quarantine ambiguous aviation abbreviations
  before canonical-graph insertion?
- **Cross-source KG-RAG** — Does authority-grounded KG-RAG improve required
  evidence/citation layers and unsupported-claim control over matched
  source-only and linked-text baselines?
- **Autonomous failure boundary** — Which failures remain, and how reliably
  can the runtime reject, quarantine, or abstain without human intervention?

### 1.4 Scope and Claim Boundaries

The prototype treats the ontology/profile as an engineering constraint, not as
the research object. It is evaluated with layered metrics and does not collapse
them into one overall score. Out of scope: complete aviation-domain ontology
coverage, live operational ATC decision support, operational safety
certification, universal KG-RAG superiority, and semantic correctness beyond
reviewed evidence. Runtime autonomy does not imply external aviation-expert
certification. Facility/time association is never treated as proof that weather
caused an advisory.

**Evidence catalog:** `RESEARCH_OVERVIEW.md`, `RESEARCH_QUESTIONS.md`, and
`ARTIFACT_INDEX.md`.

## Chapter 2. Background and Related Work

This thesis is not positioned as a new general aviation ontology. Existing ATM
ontology work provides the vocabulary and interoperability context: NASA
ATMONTO [1], AIRM-ATMONTO alignment [2], ATM knowledge-graph construction [3],
flight-safety ontology generation [4], ontological reasoning for ATM decision
support [5], semantic interoperability [6], and conversational traffic-flow
support such as CHATATC [7]. Those works motivate ontology-backed aviation data
systems, but they do not by themselves define a source-bounded evaluation of
retrospective ATCSCC advisory extraction and grounded QA. The gap used here is
therefore narrower: turn one public advisory source family into a measurable
event profile, not prove that a complete aviation ontology has been built.

Schema-guided and ontology-guided information extraction provide the closest
methodological foundation. Ontology design and competency-question practice
argue that schema scope should be defined by questions the system must answer
[14]–[17], while Text2KGBench and recent ontology-grounded LLM construction
work show why class, predicate, and output contracts matter for text-to-KG
systems [18]–[21]. However, these studies are usually not about short,
semi-structured ATCSCC notices whose reliable fields are partly template-driven
and partly semantic. This thesis therefore asks whether a lightweight
ATCSCC-specific schema can constrain extraction without pretending that all
advisory semantics are covered.

Knowledge-graph quality research explains why the thesis separates validity,
correctness, completeness, provenance, and repair instead of reporting one
combined score [8]–[13]. For this project, that distinction is not only an
evaluation preference; it is the central claim-safety mechanism. A record may be
schema-valid but semantically wrong, evidence-linked but incomplete, or useful
for one competency question while still outside the current profile. The
evaluation design therefore reports schema violations, evidence support,
semantic P/R/F1, queryability, answer grounding, and independent-evaluation boundaries as
different claims.

GraphRAG research motivates graph-augmented retrieval, but it also warns against
using graph context as an unconditional substitute for vector retrieval. Local
and hybrid GraphRAG methods [22], [23], surveys [24], [25], and recent
GraphRAG-vs-RAG evaluations [26]–[29] show that graph benefit depends on
question type, graph coverage, retrieval budget, and answer-evaluation criteria.
The relevant comparison in this thesis is therefore not "GraphRAG is always
better." It is whether a routed ATCSCC event graph improves relation-oriented,
source-grounded answers over a matched vector-only baseline while preserving
abstention and citation diagnostics.

Multi-agent LLM ontology and KG-construction work motivates role separation
between extraction, validation, refinement, and critique [13], [19]. The thesis
uses that idea conservatively: the agentic loop is an auditable repair and
rejection layer under hard schema and evidence gates, not a claim of autonomous
ontology construction. The resulting contribution is a bounded pipeline that
connects these four literatures: aviation ontology vocabulary, schema-guided
event extraction, layered KG quality evaluation, and routed KG-RAG answer
generation over one reviewed ATCSCC source family.

**Evidence spine:** `reports/stages/sota_comparison_matrix.md`,
`reports/stages/agentic_ontology_graphrag_mainline_literature_search.md`,
`reports/stages/chatatc_paper_analysis.md`,
`reports/stages/top_reference_papers_for_atmonto_graphrag.md`.

## Chapter 3. Data and Task Definition

### 3.1 Source Family

The study uses a retrospective ATCSCC snapshot (advisories 2026-05-14 through
2026-05-20) plus separately versioned terminology, NASR/facility, METAR, and
TAF profiles. Each profile records source URL, effective date, local checksum,
and refresh provenance. Unlike conversational ATC strategic-flow assistants
such as CHATATC [7], this work targets retrospective advisory-event extraction
and evidence-grounded QA, not live decision support.

| Layer | Records | Artifact |
| --- | ---: | --- |
| Downloaded advisory pages | 867 | `data/raw/nasa_atmonto/2026-05-14/atcscc_advisories/` |
| Processed source records | 867 | `data/processed/nasa_atmonto/source/2026-05-14/atcscc_advisories.jsonl` |
| Temporally aligned records | 718 | aligned JSONL |
| Formal experiment sample | 100 | `data/experiments/nasa_atmonto/formal/input_records.jsonl` |
| Reviewed gold records | 100 | `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl` |
| Records aligned for facilities/terms | 718 | cross-source alignment artifacts |
| Controlled weather-linking cohort | 68 | `data/processed/cross_source/cross-source-2026-05-v1/cohort_68.jsonl` |
| Cross-source answer questions | 24 | `data/evaluation/cross_source/v1/automated_regression_v1.jsonl` |

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

The deterministic parser owns `advisoryNumber`, `issuedTime`,
`effectiveStartTime/EndTime`, and other template fields. Semantic enrichment may add but not
overwrite semantic fields. Quarantine/review conditions: conflict, unsupported
span, fuzzy-only mapping, validator-rejected fact, repair-only fact with a
semantic-change flag.

**Evidence spine:** `reports/stages/atcscc_ontology_profile_overview.md`,
`reports/stages/atcscc_semantic_requirements.md`.

## Chapter 5. Method

The method combines the original extraction study with a versioned cross-source
path:

```text
FAA ATCSCC advisories + terminology/NASR/METAR/TAF snapshots
  -> lightweight ATCSCC application schema/profile
  -> extraction baselines + extractor/validator/refiner/critic loop
  -> facility and operational-term alignment with autonomous confidence gates
  -> 68-record facility/time linking cohort
  -> cross-source event graph with evidence spans and typed provenance
  -> source-only / linked-text / KG-layered answering + independent Evaluation Agent
```

### 5.1 Extraction stages

- **Deterministic rule baseline:** parsing over advisory templates.
- **Schema-free LLM conditions:** raw open extraction as a drift diagnostic,
  followed by a canonicalized form as the comparable LLM baseline.
- **Schema-guided LLM extraction:** `gpt-5.4-mini` receives the application
  schema; this setting
  follows the ontology-driven extraction paradigm benchmarked by Text2KGBench
  [18].
- **Validator and repair:** deterministic validator plus LLM refiner.
- **Hybrid backbone enrichment:** deterministic parsing plus LLM semantic
  enrichment, gated so deterministic fields cannot be overwritten.

### 5.2 Agentic loop

Role-separated extractor / validator / refiner / critic artifacts record repair
and rejection outcomes. The loop is an auditable diagnostic and repair
framework; it is not autonomous ontology construction. The role-separated agent
design is inspired by multi-agent LLM ontology-generation work [19] and the
broader LLM-empowered KG-construction literature [13], [10].

### 5.3 Versioned cross-source agents and gates

The Source Agent activates only checksum-verified local snapshots. Unique
authority mappings, including `JFK`/`KJFK` aliases that resolve to one canonical
airport entity, are accepted automatically. Ambiguous terms are passed to a
Context Alignment Agent that may rank only registry-supplied candidates and
must record candidates, authority sources, evidence, confidence, and margin.
Neutral, conflicting, low-confidence, or out-of-registry cases are quarantined
and excluded from the formal graph. The Linker uses accepted facility identity
and configured temporal windows to attach METAR observations and overlapping
TAF forecasts; links explicitly carry `causal_claim=false`.

The Answer Agent emits four typed layers: source assertion, observation,
forecast, and system association. Every statement requires a same-layer
citation. The Evidence Critic rejects missing evidence, unresolved requested
abbreviations, or causal wording. Neo4j is a projection for visual inspection;
the versioned RDF and JSONL artifacts remain canonical.

### 5.4 KG-RAG evaluation

Retrieval modes over frozen ATCSCC contexts: `source_oracle`, lexical-vector
proxies, `live_tfidf_vector` (real lexical retriever), `dense_embedding_vector`
(all-MiniLM-L6-v2), `graph_only`, `hybrid_graphrag`, and routed variants. The
routed mode uses template routing: graph context for entity/cause/status/route
templates; vector/source for time-window and abstention templates. The
graph-augmented retrieval design follows the GraphRAG survey literature
[24], [25] and the hybrid KG+vector paradigm of HybridRAG [23] and the
Local-to-Global GraphRAG [22]; recent benchmark and comparison work [26]–[29]
motivates reporting graph benefit separately from retrieval recall.

### 5.5 Failure review

The runtime uses deterministic and agentic critics to accept, reject,
quarantine, or abstain without a human queue. The independent Evaluation Agent
then checks exact evidence, citations, registered links, layer separation,
alignment expectations, and abstention through a path separate from answer
generation. This is reproducible internal evaluation, not external expert
certification.

**Evidence spine:** `EXPERIMENTS.md`,
`reports/stages/atcscc_agentic_artifact_contract.md`,
`reports/stages/nasa_atmonto_formal_experiment_scoring.md`.

## Chapter 6. Evaluation Design

Layered metrics, no mixed overall score. Each research question has an experiment layer,
explicit metrics, tracked artifacts, and a pass/fail interpretation.

| Layer | Metrics |
| --- | --- |
| Schema-constrained extraction | schema validity, structural acceptance rate, rejected/repaired fact count |
| Evidence support | evidence-span coverage, unsupported relation rate, provenance completeness, reviewed-subset P/R/F1 |
| Agentic loop | violation reduction, repair success, critic rejection count, post-loop F1 |
| Retrieval and KG-RAG | answer-set F1, target-source hit rate, citation P/R, evidence faithfulness |
| Authority/ambiguity alignment | accepted-target accuracy, quarantine accuracy, out-of-registry acceptance count |
| Cross-source answers | required evidence-layer coverage, required citation-layer coverage, alignment explanation, causal overstatement |
| Autonomous failure boundary | failure category counts, abstention correctness, quarantine/rejection behavior, independent audit status |

The research-question-to-evidence map is deliberately explicit so that each result section has
a "so what" target rather than merely reporting another artifact.

| Research question | Experiment section | Evidence test | Required interpretation |
| --- | --- | --- | --- |
| Extraction and canonicalization | §7.1 | Six extraction conditions over the 100-record reviewed gold set | Does schema constraint improve valid, evidence-linked advisory-event records, and where does deterministic parsing remain stronger? |
| Agentic validation and ambiguity | §7.2 and §7.4 | Validator/refiner/critic behavior plus the `GS` challenge | Does agentic orchestration improve auditability and resolve or quarantine ambiguity safely? |
| Cross-source KG-RAG | §7.3 | Single-source diagnostics plus cross-source matched baselines | Does graph context add attributable evidence and unsupported-claim control? |
| Autonomous failure boundary | §7.4 | Quarantine, abstention, Evidence Critic, and independent Evaluation Agent | Which residual failures are automatically contained, and which claims remain scientifically unverified? |

Bootstrap 95% CIs are reported for extraction F1 (record-bootstrap by source_id,
200 iterations, seed 1701). The answer-evaluation metric design borrows from
the RAGAs [30] and ARES [31] automated RAG-evaluation frameworks and the
broader RAG-evaluation survey [32].

**Evidence spine:** `EXPERIMENTS.md`, `RESEARCH_OVERVIEW.md`.

## Chapter 7. Experiments and Results

### 7.1 Experiment A — Schema-constrained advisory event extraction

**Experimental framing.** This experiment asks whether schema-constrained LLM extraction
can produce *valid* and evidence-linked records — a feasibility question, not a
SOTA-competitiveness question. Six conditions form a controlled component
ablation: deterministic rules, raw schema-free LLM extraction, canonicalized
LLM extraction, schema-guided extraction, validator/repair, and hybrid
enrichment. This mirrors the schema-guided
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
| Deterministic rule baseline | 0.8163 | 0.7097 | **0.7592** | 0.0780 | 0.9220 |
| Raw schema-free LLM diagnostic | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| Canonicalized schema-free LLM | 0.4974 | 0.1444 | 0.2238 | 0.5837 | 0.4163 |
| Schema-guided LLM | 0.2062 | 0.1843 | 0.1946 | 0.1751 | 0.8249 |
| Schema-guided LLM with validator/repair | 0.2423 | 0.1321 | 0.1710 | 0.1035 | 0.8965 |
| Deterministic backbone with semantic enrichment | 0.6857 | 0.7742 | **0.7273** | 0.0000 | 1.0000 |

Bootstrap 95% confidence intervals for F1 are 0.708–0.804 for deterministic
rules, 0.144–0.240 for schema-guided LLM extraction, and 0.681–0.763 for the
hybrid backbone.

**Interpretation.** Two findings carry over to the broader schema-guided IE
literature [18], [13]. First, schema presence sharply raises structural
acceptance: canonicalized schema-free extraction reaches 0.42, whereas the
schema-guided and hybrid conditions reach at least 0.82, reproducing the
schema-as-constraint benefit. Second, on semi-structured short text a
deterministic backbone (F1 0.759) can outperform the LLM-only conditions
(F1 at most 0.22), a negative result consistent with the
observation in the KG-construction surveys [10], [13] that LLMs struggle on
short, template-driven text where surface patterns are reliable. The hybrid
The hybrid condition (F1 0.727, zero schema violations) shows deterministic backbones and LLM
semantic enrichment can be combined without corrupting structural correctness.
Raw open-LLM output scores zero against the target schema, confirming
that schema-free extraction must not be evaluated with target-schema P/R/F1.
These are component-level feasibility findings on one ATCSCC sample; they are
not claims that the local baselines beat published systems.

### 7.2 Experiment B — Agentic validation and queryability

**Experimental framing.** This experiment asks whether role-separated validation and
refinement changes extraction governance, not whether an agentic system can
replace deterministic parsing. The tested loop therefore keeps protected
template fields under deterministic ownership and uses extractor, validator,
refiner, and critic roles to record repair or rejection decisions before graph
insertion.

The validator/refiner/critic loop records auditable repair and rejection
decisions. Validator/repair succeeds on 0.8965 of eligible cases; the hybrid
condition reaches 1.0 repair success with zero quarantines. The live agentic
run over 100 reviewed samples is a bounded
extraction-layer method artifact.

**Interpretation.** The loop's value is strongest as an accountability mechanism:
it makes schema failures, unsupported relations, repair attempts, and rejected
facts inspectable before they reach the graph. It does not show that live LLM
agents should own all extraction decisions. Deterministic parsing remains
stronger on these semi-structured advisories, so the agentic contribution is
quality governance around candidate facts rather than autonomous ontology or KG
construction.

**Evidence catalog:** agentic full-run diagnostics and competency-question
evaluation listed in `ARTIFACT_INDEX.md`.

### 7.3 Experiment C — KG-RAG grounding and answer generation

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

**Interpretation:** On this source-bounded ATCSCC benchmark, KG-RAG
approximately doubles answer correctness and cuts the unsupported-claim rate by
~30x versus the matched vector-only arm, with the gain concentrated on
relation-oriented templates. The Retrieval-only Answer-F1 gap is narrower than
the LLM-answer gap, indicating the graph's value is larger at the
answer-correctness layer than at the retrieval-F1 proxy. This is retrospective,
source-bounded evidence on 30 questions, not a universal GraphRAG claim.

**Evidence catalog:** the matched retrieval and answer-generation reports listed
in `ARTIFACT_INDEX.md`.

#### 7.3.3 Cross-source matched component evaluation (24 questions)

The cross-source experiment freezes one snapshot and uses the same 24
questions and accepted record links in all arms. `B0_source_only` exposes only
the advisory statement. `B1_linked_text` adds the same accepted METAR/TAF text
without typed graph associations. `S_cross_source_kg` adds canonical alignment,
typed association statements, and per-layer citations. Because linked text
shares the Linker's output, this is a component ablation of the typed graph
answer contract, not a comparison of independent entity-linking algorithms.

| Mode | Required evidence-layer coverage | Required citation-layer coverage | Abstention accuracy | Alignment explanation | Critic failures | Causal overstatement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Source only | 0.25 | 0.25 | 1.00 | 0.00 | 24 | 0 |
| Linked text | 0.75 | 0.75 | 1.00 | 0.00 | 0 | 0 |
| Cross-source KG | **1.00** | **1.00** | 1.00 | **1.00** | 0 | 0 |

**Interpretation.** The full system improves the predeclared evidence and
citation-layer obligations over both matched baselines, supporting the
hypothesis that KG-layered answers improve evidence coverage for
this component evaluation. The measured improvement is attributable to typed
source separation and graph-association evidence; it is not a claim that
facility/time links prove why an advisory was issued. The zero
causal-overstatement count confirms the critic boundary on this fixed set.

**Evidence spine:** `reports/stages/cross_source_mainline_evaluation.md`,
`data/evaluation/cross_source/v1/automated_regression_v1.jsonl`.

### 7.4 Experiment D — Autonomous ambiguity, failure, and audit boundary

The hard ambiguity challenge contains 20 authored `GS` cases: eight Ground Stop
contexts, six Glide Slope contexts, three neutral contexts, and three contexts
with conflicting traffic-management and instrument-approach cues. All 14
discriminating cases select the expected registry target; all six
neutral/conflicting cases are quarantined; no out-of-registry target is
accepted.

| Hard-challenge metric | Result |
| --- | ---: |
| Accepted-target accuracy | 1.00 (14/14) |
| Neutral/conflict quarantine accuracy | 1.00 (6/6) |
| Out-of-registry acceptances | 0 |

The authority-grounded ambiguity hypothesis is therefore supported on this
documented abbreviation family. It does not
establish universal acronym disambiguation. In the observed 718-advisory corpus
run, the system extracts and accepts 8,403 mentions, including 68 contextual
`GS` mappings to Ground Stop; the formal graph receives only accepted mappings.

An independent deterministic Evaluation Agent audits all 24 cross-source
answers through a path separate from answer generation. It verifies exact
advisory evidence, statement citations, registered weather records and graph
links, layer separation, expected alignment, abstention, and Evidence Critic
status. The result is 24/24 pass. This removes a manual queue from runtime and
provides a reproducible internal correctness check for those properties; it is
not external aviation-expert certification or unrestricted semantic gold.

9 generated-answer cases were packaged for review (including the 3 current
failures). Deterministic adjudication classifies the 3 failures as
profile/gold-boundary cases and leaves the original strict metrics unchanged. The
profile-decision what-if shows a predicate whitelist would correct those 3
selected records, but it does not replace strict metrics or change gold/profile
artifacts. Remaining failure categories: extraction error, retrieval context
error, profile/gold-boundary gap, answer overreach, and evaluation-boundary cases.

**Interpretation.** The remaining errors are not a single undifferentiated
"model hallucination" bucket. Some are extraction or retrieval errors that can
be engineered against, but the selected cause-condition failures are
profile/gold-boundary cases: they expose a policy choice about which predicates
belong in the ATCSCC profile. The practical implication is that the system's
final boundary is not only model accuracy; it is also explicit profile
governance. Runtime decisions are autonomous and fail closed, while claims not
covered by the internal evaluator remain limitations rather than waiting in a
mandatory human queue.

**Evidence catalog:** failure candidates, deterministic adjudication, profile
decision, reviewer-defense audit, and cross-source evaluation listed in
`ARTIFACT_INDEX.md`.

## Chapter 8. Discussion

### 8.1 What the evidence supports

- The application schema constrains which advisory event fields and relations
  enter the graph (structural acceptance 0.42 for canonicalized schema-free
  extraction versus at least 0.82 for schema-guided and hybrid conditions).
- Accepted facts preserve source IDs and evidence spans at the artifact level.
- KG-RAG's gain over vector-only is concentrated on relation-oriented templates
  and operates at the answer-correctness layer, not retrieval recall.
- The agentic loop is a useful auditable repair/rejection framework even though
  deterministic extraction remains stronger on semi-structured advisories.
- Authority-grounded context alignment resolves discriminating `GS` cases and
  quarantines neutral/conflicting cases under the registered challenge.
- Cross-source KG answers satisfy all four required evidence/citation layers,
  compared with three for linked text and one for source-only answers.
- The runtime completes acceptance, quarantine, rejection, abstention, and
  evidence audit without mandatory human intervention.

### 8.2 Negative results reported directly

- LLM-only extraction underperforms deterministic parsing; agentic
  orchestration is useful for audit and repair, not autonomous ontology
  construction.
- Forcing graph context everywhere hurts abstention handling; the router, not
  unconditional graph use, is what helps.
- Recall@5 is non-discriminating on ATCSCC; KG-RAG's win is at the
  answer-correctness layer, not retrieval recall.
- The cross-source evaluation is a matched component ablation over accepted
  links; it does not independently benchmark link discovery.

### 8.3 What the evidence does not support

See §1.4 for the full claim boundary. In short: the results support a bounded
source-bounded method, not complete ontology coverage, operational use,
universal GraphRAG superiority, or correctness beyond reviewed evidence.
The autonomous evaluator is not external aviation-expert certification, and
weather co-occurrence is not causal attribution.

## Chapter 9. Threats to Validity

The main construct-validity risk is that "correct extraction" can mean several
different things: valid schema shape, correct relation semantics, complete
field coverage, evidence-span support, or downstream queryability. The thesis
handles this by reporting those constructs separately. Strict semantic F1
penalizes evidence-span mismatch; an evidence-tolerant variant is implemented
by dropping the `evidence_text` key and raises LLM-system F1, so strict numbers
should be read as conservative lower bounds rather than as the only possible
measure of usefulness.

The main internal-validity risk is unfair comparison between vector and graph
retrieval. The head-to-head comparison mitigates this by using the same questions, same
LLM, and frozen retrieved contexts, with retrieval mode as the intended varying
factor. This does not remove every possible confound: routing policy, graph
coverage, prompt design, and the available schema still shape which questions
benefit from graph context. For that reason, the conclusion is phrased as
template- and source-bounded answer improvement rather than universal GraphRAG
superiority.

The main external-validity risk is source scope. The formal extraction sample
comes from one retrospective ATCSCC week, the single-source LLM head-to-head
contains 30 questions, and the cross-source experiment uses a 68-record
JFK/EWR/LGA cohort with 24 answer questions. Terminology, NASR/facility, METAR,
and TAF are separate profiles, but this remains one bounded aviation case
study—not a general aviation QA system or live ATC decision support.

The cross-source experiment has two additional construct boundaries. First,
the 20 `GS` challenge cases are deliberately authored stress cases, not an
external expert sample, and cover only one ambiguity family. Second, the
linked-text baseline shares accepted Linker outputs with the KG arm. It cleanly
tests the typed evidence contract but does not establish that the graph discovers
better links than an independent text-fusion linker. Both boundaries are
reported rather than folded into the positive coverage result.

The extraction comparison has an additional external-validity boundary. All
LLM conditions use `gpt-5.4-mini` with one prompt per arm and no published
ATCSCC IE benchmark exists for direct SOTA comparison. The ablation ladder
still answers the local research question because it isolates schema presence,
validator/repair, and hybridization under the same reviewed gold set. The
absolute effect sizes should not be compared to published IE systems without a
shared benchmark or cross-model replication.

The conclusion-validity risk is over-reading automated evaluation as external
certification. Bootstrap confidence intervals are reported for extraction F1,
the matched LLM answer run is fixed-budget, and the independent Evaluation Agent
checks exact evidence and policy properties rather than unrestricted aviation
semantics. Its 24/24 pass supports reproducible evidence conformance, not a
claim of external expert certification. Likewise, facility/time association
between weather and an advisory supports contextual linkage only, never causal
attribution.

**Evidence spine:** `RESEARCH_OVERVIEW.md`,
`reports/stages/nasa_atmonto_reviewer_defense_audit.md`,
`reports/stages/nasa_atmonto_sota_goal_audit.md`.

## Chapter 10. Conclusion

This project shows that retrospective FAA ATCSCC advisories can be turned into
a bounded, authority-grounded cross-source QA setting when schema validity,
canonical identity, evidence spans, graph links, answer layers, and failure
boundaries are evaluated as separate claims. Routed KG-RAG improves
single-source answer correctness and unsupported-claim control for
relation-oriented questions, while source/vector retrieval remains appropriate
for simpler source-local and abstention cases.

The cross-source mainline adds a second result. Authority-grounded alignment
reaches 1.00 accepted-target and quarantine accuracy on the 20-case `GS`
challenge with no out-of-registry acceptance. On the 24 matched questions,
KG-layered evidence and citation coverage reaches 1.00, versus 0.75 for linked
text and 0.25 for source-only answers, with 24/24 independent Evaluation Agent
passes and no causal overstatement. These results support the ambiguity and
cross-source evidence-coverage hypotheses within the declared component
evaluation boundary.

The take-home message is therefore: for semi-structured operational advisories,
multi-agent KG-RAG is useful as a routed, schema-constrained, authority-grounded
evidence layer. The runtime can accept, quarantine, reject, and abstain without
a mandatory human queue, but autonomous conformance is not external expertise,
and cross-source association is not causation. The next research step is
replication across more facilities, dates, abbreviation families, and an
independent linker baseline under the same versioned evidence contract.

### Reproducibility

- CLI end-to-end demo (offline): `uv run aviation-ai demo`
- Cross-source mainline evaluation: `uv run aviation-ai cross-source evaluate-mainline`
- Matched vector-only answer arm: use the regeneration command documented in
  `REPRODUCIBILITY.md`.
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
| 2 Background / Related Work | filled | integrated prose organized by aviation ontology, schema-guided IE, KG quality, GraphRAG, and agentic validation |
| 3 Data and Task Definition | filled | |
| 4 Application Schema / Profile | filled | |
| 5 Method | filled | |
| 6 Evaluation Design | filled | |
| 7 Experiments and Results | filled | includes the single-source head-to-head and cross-source mainline evaluation |
| 8 Discussion | filled | |
| 9 Threats to Validity | filled | construct, internal, external, extraction-comparison, and conclusion-validity boundaries |
| 10 Conclusion | filled | |
