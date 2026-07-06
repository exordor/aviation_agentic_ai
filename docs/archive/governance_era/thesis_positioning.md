# Thesis Positioning

## Problem Statement

The project studies evidence-grounded question answering over retrospective FAA
ATCSCC advisories. ATCSCC advisories are semi-structured operational notices:
they contain identifiers, affected NAS elements, route or airport constraints,
effective time windows, causes, and free-text operational context. The research
problem is not to build a complete aviation ontology. The research problem is to
extract advisory-event knowledge with explicit schema constraints and evidence
spans, then evaluate whether that structured graph improves grounded question
answering.

The prototype therefore treats the ontology/profile as an engineering
constraint. The main method is schema-constrained, evidence-grounded Agentic
KG-RAG.

## Revised Thesis Claim

This thesis investigates a retrospective and source-bounded claim: for FAA
ATCSCC advisories, a lightweight NASA ATMONTO-derived application schema can
constrain LLM extraction of advisory events, support agentic
validation/refinement, and provide an inspectable advisory event graph for
KG-RAG question answering. The system is evaluated with layered metrics:
schema-valid extraction, evidence-linked relation correctness on reviewed
subsets, repair/critic behavior, retrieval and answer quality, citation quality,
and failure/human-review boundaries are reported separately.

The thesis does not claim that the ATCSCC schema is a complete aviation
ontology, that GraphRAG universally improves retrieval, or that the system is
usable for live ATC decision support.

## Research Questions

- **RQ1**: Can schema-constrained LLM extraction produce valid and
  evidence-linked event records from ATCSCC advisories?
- **RQ2**: Does an agentic validation-refinement loop reduce schema violations
  and unsupported relations?
- **RQ3**: Does KG-RAG improve evidence grounding and citation quality compared
  with vector-only RAG?
- **RQ4**: What failure types remain, and where does human review remain
  necessary?

## Hypotheses

- **H1**: Schema constraints increase valid, evidence-linked advisory event
  records compared with unconstrained or weakly constrained extraction.
- **H2**: A validator/refiner/critic loop reduces schema violations,
  unsupported relations, and parser artifacts before graph insertion.
- **H3**: KG-RAG improves source-bounded grounding, answer-set quality, and
  citation behavior on relation-oriented ATCSCC questions, while vector-only
  retrieval can remain sufficient for simple source-local questions.
- **H4**: Failure analysis can separate extraction errors, profile/gold-boundary
  gaps, retrieval context errors, answer overreach, and cases requiring human
  review.

## Contributions

- A lightweight ATCSCC application schema/profile derived from NASA ATMONTO
  terms and restricted to the advisory-event extraction task.
- An advisory event graph with source IDs and evidence spans for extracted
  facts.
- An agentic extraction loop with extractor, validator, refiner, and critic
  roles that records repair and rejection outcomes.
- A reproducible vector, graph, and hybrid KG-RAG evaluation pipeline over
  retrospective ATCSCC advisories.
- A layered evaluation and claim-boundary protocol that separates schema
  validity, evidence support, answer quality, and human-review requirements.

## Evaluation Philosophy

The thesis should report mixed or negative retrieval results directly. KG-RAG
does not need to win every Recall@k comparison to be useful. The defensible
claim is narrower: graph evidence is useful when it improves source-bounded
answer sets, evidence traceability, citation behavior, and failure diagnosis.

| Layer | Metrics | Purpose |
| --- | --- | --- |
| Schema-constrained extraction | schema validity, structural acceptance rate, rejected fact count, repaired fact count | Measure whether generated event records obey the application schema before graph insertion. |
| Evidence support | evidence-span coverage, unsupported relation rate, provenance completeness, reviewed-subset precision/recall/F1 | Measure whether accepted facts can be traced to advisory text. |
| Agentic loop behavior | violation reduction, repair success, critic rejection count, post-loop extraction F1 | Measure whether validation/refinement improves extraction quality. |
| Retrieval and KG-RAG answer quality | answer-set F1, target-source hit rate, citation precision/recall, evidence faithfulness | Measure whether vector, graph, and hybrid modes support grounded answers. |
| Failure and human-review boundary | failure category counts, abstention correctness, profile/gold-boundary cases, human-review completion status | Measure what remains unresolved and which claims require review. |

The thesis must not collapse these layers into a single mixed overall score.
The full metric protocol is documented in `docs/experiment_protocol.md` and can
be audited with `uv run aviation-ai report evaluation-protocol`. The full thesis
experiment sequence is documented in `docs/experiment_protocol.md` and

## Claim Safety Matrix

| Claim | Current evidence | Supported strength | Safe wording | Unsafe wording to avoid |
| --- | --- | --- | --- | --- |
| Lightweight schema constrains advisory event extraction. | ATCSCC profile terms, schema validation, and prediction-output validation reports constrain accepted event fields. | strong | The application schema constrains which advisory event fields and relations can enter the graph. | The ontology fully models aviation knowledge. |
| Accepted facts preserve provenance. | KG and prediction validation reports check source IDs and evidence spans. | strong | Accepted facts carry source-bounded provenance checked by deterministic validation. | Every KG triple is semantically correct. |
| Agentic validation improves extraction quality. | S5/S6 reports record validator, refiner, critic, repair, and rejection behavior. | moderate | The agentic loop reduces specific schema and support failures in the current ATCSCC pipeline. | Autonomous agents construct a correct ontology. |
| KG-RAG improves grounded ATCSCC QA. | S7 retrieval, graph-health, and LLM answer-generation diagnostics report answer-set, citation, and target-source metrics. | moderate | KG-RAG improves some source-bounded grounding diagnostics on this benchmark. | GraphRAG is always more accurate than vector retrieval. |
| The system can answer operational ATC questions. | The advisory boundary limits the system to retrospective research diagnostics. | not supported | The system analyzes retrospective advisories and must not be used for live operational decisions. | The system can support operational flight or ATC decisions. |
| The benchmark is externally expert certified. | Current labels and diagnostics are project/thesis evidence with documented review gaps. | not supported | The benchmark is thesis-oriented and source-bounded, with explicit review limitations. | The benchmark is externally aviation-expert certified. |

## What The Thesis Can Claim

- The project implements a reproducible schema-constrained Agentic KG-RAG
  prototype over retrospective FAA ATCSCC advisories.
- The application schema constrains focused advisory-event extraction and
  supports deterministic validation.
- Accepted facts preserve source IDs and evidence spans at the artifact level.
- Agentic validation/refinement provides inspectable repair and rejection
  signals.
- KG-RAG adds structured evidence and citation diagnostics in the current
  source-bounded benchmark.
- Remaining failures and human-review requirements are explicitly categorized.

## What The Thesis Must Not Claim

- The ATCSCC application schema is a complete aviation ontology.
- NASA ATMONTO is treated as complete ground truth for ATCSCC advisories.
- GraphRAG universally improves Recall@k or answer accuracy.
- Automated diagnostics replace human or expert review.
- The benchmark is externally aviation-expert certified.
- The system is operationally safe for live ATC or flight decisions.

## Relationship Between Schema, Event Graph, Agent Loop, KG-RAG, And Review

The schema is the boundary. It defines the focused advisory-event fields and
relations that the extractor is allowed to emit. The event graph is the
structured evidence layer built under that boundary; each accepted fact must
preserve source provenance and an evidence span. The agent loop uses validation
results to repair or reject candidate facts before they enter the graph. KG-RAG
combines graph evidence with vector retrieval so answers can cite both text and
structured event facts where available. Review artifacts then classify remaining
failures and mark which conclusions require human adjudication.

This relationship keeps the thesis defensible: the project evaluates a bounded
method for evidence-grounded advisory QA, not a certified aviation ontology or a
live operational decision-support system.

## Evidence Gaps Before Thesis Submission

- Need final reviewed subset for triple-level and answer-level correctness.
- Need explicit comparison against a naive/unconstrained extraction baseline.
- Need clearer reporting of repair success and rejection reasons across the
  agentic loop.
- Need final failure taxonomy with examples and claim impact.
- Need an optional second-domain pilot only as transfer evidence, not as proof
  of domain-general validity.
