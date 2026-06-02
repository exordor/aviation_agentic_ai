# Claim KG GraphRAG Paper Adaptation Note

- Date: 2026-06-02
- Source PDF:
  `data/papers/Claim_Knowledge_Graph_Construction_and_GraphRAG_Based_Question_Answering_System.pdf`
- Source paper: Xinxue Wang and Jun Fang, "Claim Knowledge Graph
  Construction and GraphRAG-Based Question-Answering System", Buildings 2026,
  16, 845. DOI: `10.3390/buildings16040845`.
- Purpose: identify what can be reused for the NASA ATMONTO / FAA ATCSCC
  experiment design and thesis writing.

## Paper Summary

The paper builds a construction-claim domain ontology, populates a knowledge
graph from legal, case, project, and research text, stores the graph in Neo4j,
and evaluates a GraphRAG question-answering system against a base LLM and a
Vector RAG baseline.

Its pipeline is:

1. Collect domain texts.
2. Build a domain ontology using a reduced five-step version of the Stanford
   seven-step ontology process.
3. Populate a KG with LLM-assisted extraction plus manual verification.
4. Retrieve graph nodes/relations for GraphRAG question answering.
5. Compare Base LLM, Vector RAG, and GraphRAG using automatic answer metrics
   and non-parametric significance tests.

## Transferable Ideas

| Paper element | How to adapt for the current project |
| --- | --- |
| Domain ontology as retrieval schema | Use NASA ATMONTO / ATCSCC schema slice as the primary ontology profile, not as semantic ground truth. |
| Expert-reviewed KG population | Use the 100 reviewed ATCSCC gold records and rejected-fact adjudication as the manual verification layer. |
| Three-system QA comparison | Keep Base LLM, Vector RAG, and GraphRAG as an answer-generation comparison, but separate it from KG-construction scoring. |
| Graph path interpretability | Expose retrieved triples, evidence text, and source advisory IDs rather than only final generated answers. |
| Statistical comparison | Use bootstrap confidence intervals or paired tests over enough records/CQs; avoid overclaiming from tiny question sets. |
| Limitations section | Explicitly state domain, temporal, and operational boundaries: retrospective FAA ATCSCC advisories only. |

## Weaknesses Not To Copy

- The experimental QA set is small: four domain questions with repeated
  generations. That is useful as a demonstration, but weak as a thesis-level
  benchmark by itself.
- BLEU, ROUGE, and BERT-Cosine are text-similarity metrics; they do not verify
  evidence faithfulness, source support, ontology conformance, or citation
  correctness.
- The paper treats GraphRAG gains mostly through answer similarity to reference
  answers. For this project, KG construction quality and evidence grounding are
  the stronger contributions.
- The paper reports statistical tests, but the small number of unique questions
  makes broad statistical claims fragile.
- The paper's data are domain- and jurisdiction-specific. The analogous
  limitation here is that the current gold set is a frozen retrospective ATCSCC
  snapshot, not a general live aviation decision system.

## Adapted Experiment Design

### Experiment A: KG Construction Quality

Use this as the primary thesis experiment because current artifacts already
support it.

Systems:

- `S0_rule_only`
- `S1_llm_only`
- `S1b_llm_canonicalized`
- `S2_llm_schema_slice`
- `S3_llm_schema_slice_validator_repair`
- `S4_hybrid_backbone_enrichment`

Gold and evaluation basis:

- `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- `reports/stages/nasa_atmonto_formal_experiment_scoring.json`
- `reports/stages/nasa_atmonto_rejection_adjudication.json`
- `reports/stages/nasa_atmonto_cq_evaluation.json`

Metrics:

- JSON adherence and output completeness.
- Schema violation rate and repair success rate.
- Predicate-level precision, recall, and F1.
- Evidence containment and evidence support.
- Unsupported triple rate and rejected-fact adjudication counts.
- Profile-gap count, especially ARTCC controlled-element gaps.
- CQ coverage status: directly measurable, partially measurable, or deferred.

### Experiment B: Source-Bounded GraphRAG QA

Use this as a follow-up experiment after KG construction quality is established.

Candidate systems:

- Base LLM with no retrieval.
- Vector RAG over ATCSCC advisory text.
- KG-only graph retrieval over accepted facts.
- Hybrid GraphRAG using vector retrieval plus KG evidence.

Question set:

- Start from the 12 primary CQs.
- Convert each CQ into one or more answerable source-bounded query templates.
- Do not include live operations questions.
- Do not use ATMONTO as truth; use source text and reviewed gold as evidence.

Recommended QA metrics:

- Answer-set precision and recall against frozen reviewed records.
- Citation/evidence support rate.
- Unsupported answer rate.
- Abstention correctness for missing or out-of-profile fields.
- ROUGE/BERT-Cosine only as supplementary readability or reference-similarity
  metrics, not as the main correctness measure.

## Thesis Writing Structure To Borrow

1. Introduction:
   - Manual aviation advisory interpretation and KG extraction are difficult
     because facts are terse, semi-structured, time-sensitive, and ontology
     constrained.
   - State the retrospective research boundary clearly.

2. Related Work:
   - Ontology engineering and competency questions.
   - Ontology-guided information extraction.
   - Knowledge graph quality evaluation.
   - GraphRAG and KG-enhanced question answering.
   - Aviation/ATM ontology baselines: NASA ATMONTO, AIRM-O, ATMGRAPH.

3. Methodology:
   - Source collection and snapshot boundary.
   - NASA ATMONTO / ATCSCC profile construction.
   - CQ-driven gold review.
   - Multi-system extraction pipeline.
   - Validation, rejection adjudication, and evidence checks.

4. Experiments:
   - KG construction quality as the main experiment.
   - Optional GraphRAG QA as a second experiment.
   - Compare systems with layered metrics, not a single aggregate score.

5. Discussion:
   - Explain why Graph/KG helps where vector retrieval misses structured facts.
   - Separate profile gaps from extractor errors.
   - Discuss why SHACL/profile validation is not semantic truth.

6. Limitations:
   - Frozen retrospective ATCSCC snapshot.
   - Profile coverage gaps.
   - No live operational decision support.
   - Queryability and GraphRAG answer evaluation are follow-up layers unless
     implemented and scored.

## Immediate Project Actions

1. Keep the current CQ evaluation report as the bridge between ontology
   engineering and experiment scoring.
2. Add a small "paper-inspired experiment design" subsection to the thesis
   methodology notes.
3. Implement the follow-up source-bounded QA benchmark only after defining
   answer-set gold labels from the 12 CQs.
4. Cite this paper as a cross-domain methodological analogue, not as aviation
   evidence.
5. Use the paper's Base LLM / Vector RAG / GraphRAG comparison structure, but
   replace its automatic text-similarity core with evidence-grounded and
   ontology-aware metrics.
