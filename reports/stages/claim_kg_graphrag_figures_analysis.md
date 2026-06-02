# Figure Analysis: Claim KG Construction and GraphRAG QA Paper

Source paper: Xinxue Wang and Jun Fang, "Claim Knowledge Graph Construction and GraphRAG-Based Question-Answering System", Buildings 2026, 16, 845, https://doi.org/10.3390/buildings16040845.

Local PDF: `data/papers/Claim_Knowledge_Graph_Construction_and_GraphRAG_Based_Question_Answering_System.pdf`

## Figure Inventory

The paper uses 11 main figures and no regular in-body data table. Detailed per-answer scores are deferred to Supplementary Table S1.

| Figure | Role in paper | What it shows | Relevance for ATCSCC/ATMONTO work |
|---|---|---|---|
| Figure 1 | Method overview | End-to-end flow from documents, preprocessing, ontology, KG, retrieval, and LLM QA | Useful as a narrative skeleton, but it is high-level and not reproducible by itself |
| Figure 2 | Ontology engineering method | A reduced five-step ontology development workflow | Strong template for our method figure if extended with CQs, SHACL validation, evidence spans, and gold review |
| Figure 3 | Ontology taxonomy | Claim event class hierarchy | Useful visual idiom for domain taxonomy excerpts |
| Figure 4 | Ontology taxonomy | Contract, law, and regulation class hierarchy | Useful visual idiom, but needs coverage/source annotations in our version |
| Figure 5 | Ontology taxonomy | Party class hierarchy | Useful, but mostly descriptive rather than evaluative |
| Figure 6 | Ontology taxonomy | Evidence material class hierarchy | Highly relevant: our thesis should also model evidence/provenance, not only operational entities |
| Figure 7 | Ontology taxonomy | Claim class hierarchy | Useful as a compact domain-scope figure |
| Figure 8 | Ontology schema | Classes, object properties, datatype properties, and relation legend | Most useful ontology figure pattern for our ATCSCC profile |
| Figure 9 | KG instance visualization | Dense case graph plus selected node property panel | Useful for interpretability, but too dense; our version should show a smaller advisory-centered subgraph |
| Figure 10 | Evaluation result | BLEU-4 comparison for Base LLM, Vector RAG, GraphRAG | Useful comparison pattern, but BLEU-4 is weak evidence for factual correctness |
| Figure 11 | Evaluation result | BERT-Cosine and ROUGE precision/recall/F1 comparison | Better than Figure 10, but still evaluates text similarity more than KG factual validity |

## Visual and Methodological Assessment

### Strengths

1. The paper has a clear visual progression: method pipeline, ontology construction, KG instance, then QA evaluation.
2. Figures 3-8 make the ontology visible instead of treating it as an invisible implementation detail.
3. Figure 8 is especially strong because it combines class structure, object properties, datatype properties, and relation legend in one schema view.
4. Figure 9 connects graph structure to node-level properties, which helps explain why KG-based QA can be more interpretable than pure vector retrieval.
5. Figures 10-11 compare Base LLM, Vector RAG, and GraphRAG directly, which is a useful baseline structure for our later aviation QA experiment.

### Limitations

1. The taxonomy figures are mostly illustrative excerpts. They do not report class coverage, source coverage, annotation support, or validation status.
2. Figure 9 is visually overloaded. It demonstrates graph richness but is hard to read in print and lacks a clear legend for edge semantics.
3. The evaluation figures rely on text-similarity metrics: BLEU-4, BERT-Cosine, ROUGE-1, and ROUGE-L. These do not directly measure whether generated answers are evidence-grounded or whether KG triples are correct.
4. Figure 10 shows GraphRAG with the highest BLEU-4 mean, but the standard deviation is large. The visible significance annotation is only for Vector RAG versus GraphRAG.
5. Figure 11 shows stronger GraphRAG gains mainly in recall and F1-oriented metrics. It does not show uniform dominance across all precision metrics.
6. Main numeric evidence is split between figures and supplementary material. The paper would be easier to audit with an in-body metric table showing means, standard deviations, p-values, sample count, and per-question failure cases.

## Lessons for Our Thesis Figures

The most reusable contribution is not the exact chart design, but the figure sequence:

1. Show the pipeline first.
2. Show the ontology/profile design.
3. Show one interpretable KG instance.
4. Show downstream QA/evaluation results.

For the ATCSCC/ATMONTO thesis, this should become a more evidence-first figure set:

| Proposed figure | Purpose | Difference from the source paper |
|---|---|---|
| Experiment pipeline | ATCSCC advisories -> ATMONTO profile/CQs -> S0-S4 extraction -> SHACL/gold/scoring -> GraphRAG QA | Add validator, gold review, evidence spans, and abstention gates |
| ATCSCC profile schema | Advisory, controlled element, restriction, time interval, cause, condition, evidence span, validation result | Use Figure 8 style but include provenance and profile-gap concepts |
| Advisory subgraph case study | One advisory-centered graph with source span IDs and validation status | Keep much smaller than Figure 9 and include a legend |
| CQ evaluation matrix | 12 CQs versus answerability, ontology terms, gold fields, validation pattern, metric | New figure/table absent from the source paper |
| Predicate-level extraction results | Precision/recall/F1 by predicate and system variant | More diagnostic than aggregate text metrics |
| Evidence coverage chart | Supported triples, unsupported triples, citation precision/recall, span coverage | Directly tests evidence-grounded extraction |
| SHACL/profile-gap breakdown | Constraint violations grouped into extractor error versus schema/profile gap | Makes ATMONTO-as-profile explicit |
| QA comparison chart | Base LLM, Vector RAG, KG-only retrieval, Hybrid GraphRAG | Similar to Figures 10-11 but use aviation-specific factual/evidence metrics |

## Recommended Metric Framing

BLEU, ROUGE, and BERT-Cosine can be reported as secondary text-similarity measures, but they should not be the main thesis evidence. For aviation advisory KG/GraphRAG, the primary metrics should be:

- Triple-level precision, recall, and F1 against reviewed gold.
- Predicate-level precision, recall, and F1 for affected airport/airspace, restriction type, time interval, cause, and condition.
- Evidence-span coverage and citation correctness.
- Unsupported triple rate.
- SHACL violation rate and violation type.
- CQ answer accuracy.
- Abstention correctness when the advisory text does not support an answer.
- Downstream QA answer-set precision/recall for the 12 competency questions.

## Bottom Line

This paper is a useful figure-design reference for presenting an ontology-to-KG-to-GraphRAG pipeline. Its strongest figures for our purposes are Figure 2, Figure 8, Figure 9, and Figure 11. However, the paper's evaluation visuals are not sufficient as a model for an evidence-first aviation thesis, because they emphasize generated-answer similarity rather than provenance, constraint satisfaction, unsupported facts, and CQ-level answerability.

Our thesis should borrow the visual sequence but upgrade the evaluation layer: from "GraphRAG answers look more similar to references" to "ATMONTO-constrained extraction produces queryable, evidence-grounded, validator-aware advisory knowledge with measurable failure modes."
