# Research Papers

This directory stores citation records and reading notes for research papers
used as project references.

Downloaded PDFs are intentionally kept local and ignored by Git. This keeps the
repository lightweight and avoids redistributing paper files when the paper
license is not part of the repository.

## Default Analysis Workflow

When a paper may affect the thesis route or experiment design, do not rely on
the abstract alone. The former local PDF-inspection and report-generation
workflow is preserved in the dated external archive. This file remains the
lightweight citation registry; it is not a report pipeline or a runtime
dependency.

## Current References

- Title: "CHATATC: Large Language Model-Driven Conversational Agents for
  Supporting Strategic Air Traffic Flow Management"
- Authors: Sinan Abdulhak, Wayne Hubbard, Karthik Gopalakrishnan, and
  Max Z. Li
- Venue / year: ICRAT 2024; arXiv preprint v2, 2024
- Stable URL: https://arxiv.org/abs/2402.14850
- arXiv PDF: https://arxiv.org/pdf/2402.14850
- Local download date: 2026-06-06
- Local ignored PDF name: `arxiv_2402.14850_chatatc.pdf`
- Use in this project: aviation-domain related work and evaluation reference
  for model-assisted historical traffic flow management question answering. It
  supports the non-safety-critical advisory analysis framing, but it is not a
  KG, ontology-constrained extraction, or GraphRAG method reference.
- Inspection artifacts: `tmp/pdfs/chatatc/`
- Curated analysis: external archive `reports/stages/chatatc_paper_analysis.md`

- Title: "Towards Automated Ontology Generation from Unstructured Text: A
  Multi-Agent LLM Approach"
- Authors: Abid Talukder, Maruf Ahmed Mridul, and Oshani Seneviratne
- arXiv: https://arxiv.org/abs/2604.23090
- arXiv PDF: https://arxiv.org/pdf/2604.23090
- Local download date: 2026-05-12
- Local ignored PDF name:
  `towards-automated-ontology-generation-multi-agent-llm.pdf`
- Use in this project: primary methodology reference for the automated ontology
  generation pipeline, especially the artifact-driven multi-agent flow from
  competency questions to SRD, TIP, Turtle generation, and quality review.
- Upstream implementation reference:
  https://github.com/brains-group/towards_automated_ontology_generation
- Inspection artifacts:
  `tmp/pdfs/automated_ontology_generation_multi_agent/`
- Curated project adaptation: external archive
  `reports/stages/multi_agent_pipeline_method_adaptation.md`

- Title: "Claim Knowledge Graph Construction and GraphRAG-Based
  Question-Answering System"
- Authors: Xinxue Wang and Jun Fang
- Venue: Buildings 2026, 16, 845
- DOI: https://doi.org/10.3390/buildings16040845
- Local ignored PDF name:
  `Claim_Knowledge_Graph_Construction_and_GraphRAG_Based_Question_Answering_System.pdf`
- Use in this project: cross-domain method and figure-design reference for
  ontology-to-KG-to-GraphRAG experiment presentation. It is not aviation
  evidence.
- Curated reports:
  - external archive `reports/stages/claim_kg_graphrag_paper_adaptation.md`
  - external archive `reports/stages/claim_kg_graphrag_figures_analysis.md`

- Title: "Gold Deposit Ontology Guides Large Language Model to Transform Text
  into Knowledge Graphs for Gold Deposits"
- Authors: Jinhao Zhu, Yueying Wang, Wanying Tong, Shengmiao Li, Mingguo Wang,
  and Chengbin Wang
- Venue / year: Minerals 2026, 16, 50
- DOI: https://doi.org/10.3390/min16010050
- Local ignored PDF name: `minerals-16-00050-v2.pdf`
- Use in this project: cross-domain method reference for ontology/schema-guided
  LLM extraction, entity alignment, KG visualization/querying, and model
  performance-cost evaluation. It is geoscience evidence, not aviation
  evidence.
- Inspection artifacts: `tmp/pdfs/minerals_16_00050/`
- Curated analysis: external archive `reports/stages/minerals_16_00050_paper_analysis.md`

## arXiv Method Candidates Downloaded for Cross-Domain Transfer

These PDFs were downloaded locally on 2026-06-02 as candidates for the
ontology-build, KG-extraction, and GraphRAG method backbone. They are not
current project evidence. Before using a paper to change the experiment plan,
reactivate the archived paper-analysis workflow explicitly and record the
result in the external archive; do not create another catch-all report stage
in this checkout.

- Title: "Accelerating Knowledge Graph and Ontology Engineering with Large
  Language Models"
- arXiv: https://arxiv.org/abs/2411.09601
- arXiv PDF: https://arxiv.org/pdf/2411.09601
- Local ignored PDF name:
  `arxiv_2411.09601_accelerating_kg_ontology_engineering_llms.pdf`
- Candidate use: model-assisted ontology/KG engineering process design.

- Title: "Ontology-grounded Automatic Knowledge Graph Construction by LLM
  under Wikidata schema"
- arXiv: https://arxiv.org/abs/2412.20942
- arXiv PDF: https://arxiv.org/pdf/2412.20942
- Local ignored PDF name:
  `arxiv_2412.20942_ontology_grounded_automatic_kg_construction_wikidata.pdf`
- Candidate use: ontology-grounded KG construction and schema-constrained
  extraction design.

- Title: "Beyond Isolation: Multi-Agent Synergy for Improving Knowledge Graph
  Construction"
- arXiv: https://arxiv.org/abs/2312.03022
- arXiv PDF: https://arxiv.org/pdf/2312.03022
- Local ignored PDF name:
  `arxiv_2312.03022_multi_agent_synergy_kg_construction.pdf`
- Candidate use: multi-agent extraction/refinement/verification architecture.

- Title: "When to use Graphs in RAG: A Comprehensive Analysis for Graph
  Retrieval-Augmented Generation"
- arXiv: https://arxiv.org/abs/2506.05690
- arXiv PDF: https://arxiv.org/pdf/2506.05690
- Local ignored PDF name:
  `arxiv_2506.05690_when_to_use_graphs_in_rag.pdf`
- Candidate use: deciding when GraphRAG is justified over vector-only RAG.

- Title: "GraphRAG-Bench: Challenging Domain-Specific Reasoning for Evaluating
  Graph Retrieval-Augmented Generation"
- arXiv: https://arxiv.org/abs/2506.02404
- arXiv PDF: https://arxiv.org/pdf/2506.02404
- Local ignored PDF name: `arxiv_2506.02404_graphrag_bench.pdf`
- Candidate use: benchmark design and domain-specific GraphRAG evaluation.

- Title: "RAG vs. GraphRAG: A Systematic Evaluation and Key Insights"
- arXiv: https://arxiv.org/abs/2502.11371
- arXiv PDF: https://arxiv.org/pdf/2502.11371
- Local ignored PDF name: `arxiv_2502.11371_rag_vs_graphrag.pdf`
- Candidate use: experimental comparison protocol for RAG versus GraphRAG.

- Title: "GRAG: Graph Retrieval-Augmented Generation"
- arXiv: https://arxiv.org/abs/2405.16506
- arXiv PDF: https://arxiv.org/pdf/2405.16506
- Local ignored PDF name:
  `arxiv_2405.16506_grag_graph_retrieval_augmented_generation.pdf`
- Candidate use: graph/subgraph retrieval and graph-context generation method
  reference.
