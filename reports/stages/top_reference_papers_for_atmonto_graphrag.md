# Top Reference Papers for ATMONTO-Constrained GraphRAG Experiments

Date: 2026-06-02

Purpose: identify high-quality reference papers for the thesis direction around NASA ATMONTO-constrained extraction, competency-question-driven evaluation, knowledge-graph quality, and GraphRAG-style question answering over FAA ATCSCC advisories.

## Search Positioning

The strict "top journal" literature is strongest in the general methods layer: automatic KG construction, KG quality management, graph-based RAG, and ontology/CQ methodology. The aviation ATM ontology literature is much smaller and often appears as technical documentation, conference papers, or domain journals. For the thesis, the best evidence strategy is therefore layered:

1. Use top journals and high-citation surveys for method and evaluation framing.
2. Use NASA ATMONTO, AIRM-O alignment, ATMGRAPH, and flight-safety-message ontology papers for aviation-domain grounding.
3. Use CQ and SPARQL-OWL formalization papers to justify the experiment's test-first ontology evaluation protocol.

## Priority Reading List

| Priority | Paper | Venue / status | Citations | Role in this project | Next action |
|---|---|---:|---:|---|---|
| P0 | [Graph Retrieval-Augmented Generation: A Survey](https://consensus.app/papers/graph-retrievalaugmented-generation-a-survey-peng-zhu/1b8c5362a3d3538ba1dd90f9b40178f1/?utm_source=chatgpt) | ACM Transactions on Information Systems, 2024 | 381 | Main GraphRAG framing: graph indexing, graph-guided retrieval, graph-enhanced generation. | Download and inspect figures/tables before changing retrieval design. |
| P0 | [A Comprehensive Survey on Automatic Knowledge Graph Construction](https://consensus.app/papers/a-comprehensive-survey-on-automatic-knowledge-graph-zhong-wu/a423407f450e51228681d3b896c3fbc6/?utm_source=chatgpt) | ACM Computing Surveys, 2023 | 293 | Main KG construction taxonomy: acquisition, refinement, evolution. | Use as the thesis background anchor for extraction pipeline design. |
| P0 | [Knowledge Graph Quality Management: A Comprehensive Survey](https://consensus.app/papers/knowledge-graph-quality-management-a-comprehensive-xue-zou/2904304ba5b95b018f0f96b8ca76e39d/?utm_source=chatgpt) | IEEE TKDE, 2023 | 141 | Main KG quality framing: assessment, error detection/correction, completion. | Map thesis metrics to quality dimensions. |
| P0 | [Text2KGBench: A Benchmark for Ontology-Driven Knowledge Graph Generation from Text](https://consensus.app/papers/text2kgbench-a-benchmark-for-ontologydriven-knowledge-mihindukulasooriya-tiwari/b24be0d0ff9f52eebfa7a23833492952/?utm_source=chatgpt) | Benchmark paper, 2023 | 118 | Directly relevant to ontology-driven text-to-KG generation and hallucination/conformance evaluation. | Treat as closest methodological analogue to ATMONTO-constrained extraction. |
| P0 | [Analysis of Ontology Competency Questions and their formalizations in SPARQL-OWL](https://consensus.app/papers/analysis-of-ontology-competency-questions-and-their-wisniewski-potoniec/10971540ec3c52e488c274b84edeba70/?utm_source=chatgpt) | Journal of Web Semantics, 2019 | 75 | CQ-to-query formalization basis; useful for turning advisory CQs into executable checks. | Use to refine CQ templates and SPARQL/SHACL validation patterns. |
| P1 | [Knowledge Graph Completeness: A Systematic Literature Review](https://consensus.app/papers/knowledge-graph-completeness-a-systematic-literature-issa-adekunle/80b8706e22685cad9ca78c8bf341090f/?utm_source=chatgpt) | IEEE Access, 2021 | 64 | Completeness dimensions for KG evaluation. | Use for CQ coverage and missing-field analysis. |
| P1 | [Graph-Based Approaches and Functionalities in Retrieval-Augmented Generation: A Comprehensive Survey](https://consensus.app/papers/graphbased-approaches-and-functionalities-in-zhu-huang/6826fe71867f5352b3e6a48fa456a9b8/?utm_source=chatgpt) | ACM Computing Surveys, 2025 | 20 | Newer graph-RAG taxonomy; useful for positioning beyond vector retrieval. | Read after the TOIS GraphRAG survey. |
| P1 | [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://consensus.app/papers/ragas-automated-evaluation-of-retrieval-augmented-shahul-james/1e214d3a38e2558b8d6595f964842bca/?utm_source=chatgpt) | arXiv, 2023 | 636 | RAG evaluation metrics: context relevance, faithfulness, answer quality. | Use as evaluation inspiration, not as ontology-grounded truth. |
| P1 | [ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems](https://consensus.app/papers/ares-an-automated-evaluation-framework-for-saad-falcon-khattab/dd05712d36365561becd51b2b17be9a4/?utm_source=chatgpt) | arXiv, 2023 | 252 | RAG component evaluation with human-annotated calibration and LM judges. | Adapt cautiously for retrospective, evidence-span-grounded evaluation. |
| P1 | [Evaluation of Retrieval-Augmented Generation: A Survey](https://consensus.app/papers/evaluation-of-retrievalaugmented-generation-a-survey-yu-gan/861805cd172d534298b77a83a0d83d92/?utm_source=chatgpt) | arXiv, 2024 | 257 | Broad RAG metric landscape; helps avoid narrow or ad hoc evaluation. | Use for metric vocabulary and limitations section. |
| P1 | [RevOnt: Reverse engineering of competency questions from knowledge graphs via language models](https://consensus.app/papers/revont-reverse-engineering-of-competency-questions-from-ciroku-berardinis/ebaac0aa8457596da3c98b62a9df2b93/?utm_source=chatgpt) | Journal of Web Semantics, 2024 | 24 | Supports retrospective CQ generation from existing KGs. | Compare with our ATMONTO CQ generation/refinement workflow. |
| P1 | [Use of Competency Questions in Ontology Engineering: A Survey](https://consensus.app/papers/use-of-competency-questions-in-ontology-engineering-a-quirino-salamon/2cb3dc0807b6581ca448a183299303b7/?utm_source=chatgpt) | Survey paper, 2023 | 26 | Empirical evidence on how ontology engineers use and struggle with CQs. | Use to justify disciplined CQ management. |
| P2 | [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://consensus.app/papers/from-local-to-global-a-graph-rag-approach-to-queryfocused-edge-trinh/1cef732f6bb2558eb3b75ebc5298a26d/?utm_source=chatgpt) | arXiv, 2024 | 1390 | High-impact GraphRAG method paper. | Use for graph-community summarization ideas, not as top-journal evidence. |
| P2 | [HybridRAG: Integrating Knowledge Graphs and Vector Retrieval Augmented Generation for Efficient Information Extraction](https://consensus.app/papers/hybridrag-integrating-knowledge-graphs-and-vector-sarmah-mehta/731a8e846c0c59da9aef7951b67f7b2b/?utm_source=chatgpt) | ACM ICAIF, 2024 | 178 | Hybrid vector + KG retrieval analogue. | Use as method comparator for hybrid baselines. |
| P2 | [Methodology for the Design and Evaluation of Ontologies](https://consensus.app/papers/methodology-for-the-design-and-evaluation-of-ontologies-gruninger/11fe2efa9c315f01bab469b26b9ebf3f/?utm_source=chatgpt) | Classic ontology methodology, 1995 | 1734 | Foundational competency-question argument. | Cite for CQ-driven ontology requirements, with modern CQ papers for updates. |

## Aviation / ATM Domain References

| Priority | Paper | Venue / status | Citations | Role in this project | Evidence boundary |
|---|---|---:|---:|---|---|
| D0 | [The NASA Air Traffic Management Ontology: Technical Documentation](https://consensus.app/papers/the-nasa-air-traffic-management-ontology-technical-keller/aaa68d992d9257dc947aa197a05cffe7/?utm_source=chatgpt) | NASA / technical documentation, 2017 | 18 | Primary ATMONTO schema/profile reference. | Schema/profile reference, not empirical ground truth. |
| D0 | [Matching Ontologies for Air Traffic Management: a Comparison and Reference Alignment of the AIRM and NASA ATM Ontologies](https://consensus.app/papers/matching-ontologies-for-air-traffic-management-a-vennesland-keller/01af37df362c50a698821ec2fbba7aeb/?utm_source=chatgpt) | ATM ontology alignment paper, 2019 | 7 | ATMONTO vs AIRM-O alignments and mismatches. | Use to discuss interoperability limits. |
| D1 | [Building a Knowledge Graph for the Air Traffic Management Community](https://consensus.app/papers/building-a-knowledge-graph-for-the-air-traffic-management-keller/0bd9184f163a5d03b3a5bcc8b926c7cf/?utm_source=chatgpt) | WWW Companion, 2019 | 21 | ATMGRAPH practical KG construction reference. | Domain inspiration; not GraphRAG evaluation evidence. |
| D1 | [Ontology generation for flight safety messages in air traffic management](https://consensus.app/papers/ontology-generation-for-flight-safety-messages-in-air-aghdam-tabbakh/c53444faec215b978b77482f5c2f3523/?utm_source=chatgpt) | Journal of Big Data, 2021 | 9 | Closest message-oriented aviation ontology-generation paper. | Good domain analogue for NOTAM/safety messages, not identical to ATCSCC advisories. |
| D1 | [Situation Awareness Decision Support System for Air Traffic Management Using Ontological Reasoning](https://consensus.app/papers/situation-awareness-decision-support-system-for-air-insaurralde-blasch/631e133f7a775f13bf46090f5141e13b/?utm_source=chatgpt) | Journal of Aerospace Information Systems, 2022 | 21 | Ontology-based ATM decision-support example. | Avoid operational-readiness claims; use for background. |
| D2 | [Ontology-Based Data Integration for Semantic Interoperability in Air Traffic Management](https://consensus.app/papers/ontologybased-data-integration-for-semantic-egami-lu/d4c49acd073351f8a0c32e8f4732254e/?utm_source=chatgpt) | IEEE ICSC, 2020 | 5 | SWIM / semantic interoperability context. | Background for integration, not evaluation benchmark. |

## Recommended Reading Order

1. Read the P0 method core first: GraphRAG survey, KG construction survey, KG quality survey, Text2KGBench, and CQ formalization.
2. Then read D0/D1 aviation references to map terms, constraints, and ATCSCC advisory modeling boundaries.
3. Only then download and inspect P1/P2 papers for implementation ideas and metric refinements.
4. For any paper that changes the experiment plan, follow `docs/research_paper_analysis_protocol.md`: register it in `data/papers/README.md`, inspect PDF metadata/text/images, visually inspect figures/tables, and create a dedicated report in `reports/stages/`.

## Candidate Search Strings

Use these in Consensus, Google Scholar, Semantic Scholar, or arXiv:

- `"ontology-driven knowledge graph generation" benchmark text`
- `"knowledge graph quality management" completeness correctness survey`
- `"Graph Retrieval-Augmented Generation" survey graph-based RAG`
- `"competency questions" ontology SPARQL OWL formalization`
- `"ATMONTO" "AIRM-O" alignment`
- `"air traffic management" ontology knowledge graph`
- `"ATCSCC" advisory ontology knowledge graph`
- `"flight safety messages" ontology air traffic management`

## Thesis-Relevant Takeaway

The defensible thesis story should not claim that aviation ATM ontology literature alone is a mature top-journal field. A stronger framing is:

> This thesis applies top-journal KG construction, KG quality, GraphRAG, and CQ-based ontology evaluation methods to a narrowly scoped aviation advisory extraction task, using NASA ATMONTO as a schema/profile reference and retrospective FAA ATCSCC advisories as the evidence corpus.
