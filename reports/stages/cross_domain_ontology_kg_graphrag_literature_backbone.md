# Cross-Domain Literature Backbone for Ontology Build, KG Extraction, and GraphRAG

Date: 2026-06-02

Scope: cross-domain methods that can be migrated into the ATMONTO-constrained
FAA ATCSCC advisory KG experiment. This report deliberately does not limit the
search to ATM ontology papers. ATM/ATMONTO remains the target domain; the
method backbone should come from broader ontology engineering, KG construction,
KG quality, and GraphRAG literature.

## Working Thesis Frame

The project should be positioned as a cross-domain method transfer study:

> Can ontology-constrained extraction, CQ-driven validation, and graph-aware
> retrieval improve the construction and use of a retrospective advisory
> knowledge graph, compared with unconstrained extraction and vector-only RAG?

This is stronger than claiming that the ATM ontology field alone already
provides a mature, high-volume literature base.

## Method Axes

| Axis | What to borrow | Why it matters for ATCSCC advisories |
|---|---|---|
| Ontology build | CQ-driven ontology scoping, ontology learning, ontology refinement, SHACL/query validation | Prevents arbitrary LLM-created schemas and keeps ATMONTO/profile terms explicit. |
| KG extraction | Entity/relation extraction, ontology-guided triple generation, evidence-span grounding, human-in-loop quality review | Turns advisory text into auditable triples rather than unsupported LLM summaries. |
| KG quality | Completeness, correctness, conformance, provenance, error detection/correction | Lets the thesis evaluate KG quality as a downstream RAG factor. |
| GraphRAG | Graph indexing, graph-guided retrieval, hybrid vector+graph retrieval, failure-mode analysis | Tests when graph structure actually helps, rather than assuming GraphRAG is always better. |

## Foundation Surveys and Top-Journal Anchors

| Paper | Venue | Why it is a backbone source |
|---|---|---|
| [Knowledge Graphs](https://consensus.app/papers/knowledge-graphs-hogan-blomqvist/e0263bd4f91255f889c5fa6141525ab1/) | ACM Computing Surveys, 2020 | Broad KG foundation: graph data models, query/validation languages, deductive and inductive extraction. |
| [A Survey on Knowledge Graphs: Representation, Acquisition, and Applications](https://consensus.app/papers/a-survey-on-knowledge-graphs-representation-acquisition-ji-pan/31cd4a8403f95a22b2622970d2121370/) | IEEE TNNLS, 2020 | High-citation survey for representation, acquisition, completion, temporal KGs, and knowledge-aware applications. |
| [A Comprehensive Survey on Automatic Knowledge Graph Construction](https://consensus.app/papers/a-comprehensive-survey-on-automatic-knowledge-graph-zhong-wu/a423407f450e51228681d3b896c3fbc6/) | ACM Computing Surveys, 2023 | KG construction taxonomy: acquisition, refinement, evolution. |
| [Knowledge Graph Quality Management: A Comprehensive Survey](https://consensus.app/papers/knowledge-graph-quality-management-a-comprehensive-xue-zou/2904304ba5b95b018f0f96b8ca76e39d/) | IEEE TKDE, 2023 | Quality dimensions and management lifecycle. |
| [Graph Retrieval-Augmented Generation: A Survey](https://consensus.app/papers/graph-retrievalaugmented-generation-a-survey-peng-zhu/1b8c5362a3d3538ba1dd90f9b40178f1/) | ACM TOIS, 2024 | GraphRAG workflow: graph-based indexing, graph-guided retrieval, graph-enhanced generation. |

## Ontology Build and Ontology Learning Sources

| Paper | Venue | Transfer value |
|---|---|---|
| [Automatic ontology construction from text: a review from shallow to deep learning trend](https://consensus.app/papers/automatic-ontology-construction-from-text-a-review-from-al-aswadi-chan/b0d53a91a10857afad67726896bcbaca/) | Artificial Intelligence Review, 2019 | Good survey for ontology construction from text and transition from shallow to deep learning. |
| [A survey of ontology learning techniques and applications](https://consensus.app/papers/a-survey-of-ontology-learning-techniques-and-applications-asim-wasim/6e0a2fb999f15893acb4bf15f87f068b/) | Database, 2018 | Classifies linguistic/statistical/logical ontology learning and evaluation techniques. |
| [Ontology learning: Grand tour and challenges](https://consensus.app/papers/ontology-learning-grand-tour-and-challenges-khadir-aliane/be376261d3925c2fa98da2dc0c559658/) | Computer Science Review, 2021 | Useful for scoping automation limits and reliability/evaluation challenges. |
| [Analysis of Ontology Competency Questions and their formalizations in SPARQL-OWL](https://consensus.app/papers/analysis-of-ontology-competency-questions-and-their-wisniewski-potoniec/10971540ec3c52e488c274b84edeba70/) | Journal of Web Semantics, 2019 | Direct basis for converting natural-language CQs into executable validation/query patterns. |
| [RevOnt: Reverse engineering of competency questions from knowledge graphs via language models](https://consensus.app/papers/revont-reverse-engineering-of-competency-questions-from-ciroku-berardinis/ebaac0aa8457596da3c98b62a9df2b93/) | Journal of Web Semantics, 2024 | Useful for retrospective CQ generation from an existing KG. |

## KG Extraction and Domain-KG Case Studies

| Paper | Venue | Transfer value |
|---|---|---|
| [Text2KGBench: A Benchmark for Ontology-Driven Knowledge Graph Generation from Text](https://consensus.app/papers/text2kgbench-a-benchmark-for-ontologydriven-knowledge-mihindukulasooriya-tiwari/b24be0d0ff9f52eebfa7a23833492952/) | Benchmark paper, 2023 | Closest benchmark analogue: ontology conformance, fact extraction, hallucination metrics. |
| [Domain Ontology-Driven Knowledge Graph Generation from Text](https://consensus.app/papers/domain-ontologydriven-knowledge-graph-generation-from-meng-zhan/c444147707505d06962f6f38b65982f1/) | ACM TOPML, 2024 | End-to-end domain ontology-driven node/relation extraction using pretrained language models. |
| [Generating Knowledge Graphs by Employing Natural Language Processing and Machine Learning Techniques within the Scholarly Domain](https://consensus.app/papers/generating-knowledge-graphs-by-employing-natural-dess-osborne/0eb51722f4885f1db753f8304b32cd30/) | Future Generation Computer Systems, 2020 | Strong cross-domain pipeline example for extracting entities/relations from scientific text into a KG. |
| [Healthcare knowledge graph construction: A systematic review of the state-of-the-art, open issues, and opportunities](https://consensus.app/papers/healthcare-knowledge-graph-construction-a-systematic-abu-salih-al-qurishi/4d7b27b516c651558bb7728f55d6d39c/) | Journal of Big Data, 2023 | Domain KG construction taxonomy and evaluation protocols from a high-stakes text domain. |
| [KGen: a knowledge graph generator from biomedical scientific literature](https://consensus.app/papers/kgen-a-knowledge-graph-generator-from-biomedical-rossanez-reis/074a591e31445155ad37f71285ef0b89/) | BMC Medical Informatics and Decision Making, 2020 | Semi-automatic ontology-linked KG generation with expert comparison; good human-in-loop analogue. |

## arXiv Method Papers Downloaded Locally

These are method candidates, not yet curated evidence. They must go through the
PDF inspection and figure/table analysis workflow before being used to change
the experiment.

| Paper | Local PDF | Why it was downloaded |
|---|---|---|
| [Accelerating Knowledge Graph and Ontology Engineering with Large Language Models](https://arxiv.org/abs/2411.09601) | `data/papers/arxiv_2411.09601_accelerating_kg_ontology_engineering_llms.pdf` | LLM-assisted ontology/KG engineering workflow. |
| [Ontology-grounded Automatic Knowledge Graph Construction by LLM under Wikidata schema](https://arxiv.org/abs/2412.20942) | `data/papers/arxiv_2412.20942_ontology_grounded_automatic_kg_construction_wikidata.pdf` | Ontology-grounded generation and schema-constrained extraction. |
| [Beyond Isolation: Multi-Agent Synergy for Improving Knowledge Graph Construction](https://arxiv.org/abs/2312.03022) | `data/papers/arxiv_2312.03022_multi_agent_synergy_kg_construction.pdf` | Multi-agent extractor/refiner/critic architecture analogue. |
| [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://arxiv.org/abs/2506.05690) | `data/papers/arxiv_2506.05690_when_to_use_graphs_in_rag.pdf` | Deciding when graph structure is warranted. |
| [GraphRAG-Bench: Challenging Domain-Specific Reasoning for Evaluating Graph Retrieval-Augmented Generation](https://arxiv.org/abs/2506.02404) | `data/papers/arxiv_2506.02404_graphrag_bench.pdf` | Domain-specific GraphRAG benchmark design. |
| [RAG vs. GraphRAG: A Systematic Evaluation and Key Insights](https://arxiv.org/abs/2502.11371) | `data/papers/arxiv_2502.11371_rag_vs_graphrag.pdf` | Comparison protocol and failure-mode framing. |
| [GRAG: Graph Retrieval-Augmented Generation](https://arxiv.org/abs/2405.16506) | `data/papers/arxiv_2405.16506_grag_graph_retrieval_augmented_generation.pdf` | Textual subgraph retrieval and graph-context generation. |

## Recommended Migration Plan

1. Keep ATMONTO as the target schema/profile, but borrow method design from
   cross-domain ontology/KG papers.
2. Define three experimental layers:
   - ontology/CQ layer: ATMONTO profile, CQ matrix, SHACL/query validation;
   - extraction layer: constrained LLM triples, evidence spans, repair loop;
   - retrieval layer: vector RAG, graph RAG, hybrid vector+graph RAG.
3. Evaluate by both intrinsic and downstream measures:
   - intrinsic: triple precision/recall, ontology conformance, evidence-span
     coverage, unsupported triple rate;
   - downstream: CQ answerability, answer faithfulness, abstention correctness,
     query-specific retrieval quality.
4. Before using any newly downloaded arXiv paper as evidence, inspect:
   - architecture diagrams;
   - evaluation tables;
   - dataset construction;
   - ablations/failure modes;
   - reproducibility artifacts.

## Immediate Reading Queue

1. `arxiv_2506.05690_when_to_use_graphs_in_rag.pdf`
2. `arxiv_2502.11371_rag_vs_graphrag.pdf`
3. `arxiv_2506.02404_graphrag_bench.pdf`
4. `arxiv_2411.09601_accelerating_kg_ontology_engineering_llms.pdf`
5. `arxiv_2412.20942_ontology_grounded_automatic_kg_construction_wikidata.pdf`
