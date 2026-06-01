# Consensus Validation of Current Pipeline Design

## Material Passport

- Artifact: Consensus-backed validation of the current NASA ATMONTO pipeline design.
- Scope: `docs/nasa_atmonto_experiment_design.md`, `docs/experiment_workflow.md`, `docs/evaluation_protocol.md`, `docs/thesis_positioning.md`, and the data-source extraction matrix.
- Evidence source: Consensus academic-paper search and fetched paper records.
- Validation mode: literature support audit, not a proof that local pipeline outputs are already correct.
- Claim boundary: retrospective aviation data integration, ontology-constrained KG construction, and evidence-traceable QA. This validation does not support live operational aviation decisions.

## Executive Verdict

The current pipeline design is literature-supported, with one important condition: it must be presented as a constrained, evidence-gated, human-reviewable data integration and QA experiment, not as an autonomous aviation truth engine.

The strongest parts of the design are:

- using NASA ATMONTO as the primary ATM/NAS schema baseline rather than creating a new ontology from scratch;
- separating schema/reference sources from ABox/event facts;
- using deterministic translators for structured and cycle-valid sources such as AviationWeather and NASR;
- using ATMONTO constraints, domain/range checks, and SHACL-style validation before accepting triples;
- evaluating retrieval, graph evidence, answer generation, citations, and abstention as separate layers;
- keeping GraphRAG claims task-specific rather than claiming universal Recall@k improvement.

The riskiest parts are:

- LLM extraction of ATCSCC/NAS Status advisory semantics;
- causal or impact relations extracted from text;
- GraphRAG improvement claims if they are not backed by source-family-specific and CQ-specific metrics;
- treating AIRM-O alignment, ATMONTO classes, or literature claims as fact-layer ground truth.

Therefore the pipeline should keep the current C0-C7 experimental design, but label all LLM-derived advisory/event triples as `bronze_until_reviewed` until exact evidence, ontology validation, temporal checks, and manual review are complete.

## Pipeline Validation Matrix

| Pipeline stage | Consensus-backed verdict | Supporting evidence | Required project control |
| --- | --- | --- | --- |
| P0 snapshot, manifest, provenance, and checksum layer | Strongly supported. Heterogeneous KG construction depends on source traceability and reusable mappings. | ATMGRAPH integrates structured aviation sources for ATM users [2]; structured/semi-structured KG reviews emphasize source, mapping, and publication processes [5]; Docs2KG explicitly separates layout, metadata, and semantic KG layers with provenance concerns [9]. | Keep raw payload hashes, retrieval commands, source effective dates, parser versions, and local raw paths for every source record. |
| P1 NASA ATMONTO runtime profile | Strongly supported. ATMONTO directly covers NAS, flights, aircraft, airports, air routes, advisories, weather phenomena, and information-management use cases [1]. ATM semantic-integration work supports ontology-backed interoperability [3]. | NASA ATMONTO technical documentation [1]; ATMGRAPH [2]; ATM ontology integration [3]. | Treat ATMONTO as the primary TBox/schema baseline, not as ABox ground truth. |
| P2 AIRM-O/ATMONTO alignment audit | Supported with caveats. AIRM-O is valuable for interoperability auditing, but alignment work reports conceptual mismatches between AIRM-O and ATMONTO [4]. | AIRM/ATMONTO reference alignment [4]. | Keep AIRM-O as an audit and gap-analysis source. Do not replace NASA ATMONTO with AIRM-O unless the experiment is redesigned. |
| P3 deterministic translators for structured sources | Strongly supported. Structured and semi-structured KG construction literature supports explicit mappings from stable fields into semantic representations [5]. | KG construction from structured/semi-structured data review [5]. | Use deterministic translators for AviationWeather, NASR, registry, BTS, and trajectory fields where source structure exists. Do not use LLM extraction as the primary parser for official fields. |
| P4 document conversion and reference-text chunking | Strongly supported. Consensus evidence supports layout-aware document conversion and task/document-specific parser selection. | Docs2KG [9], Docling [14], comparative PDF parser study [15]. | Keep hybrid Docling + PyMuPDF. Use document structure for chunks and terminology, not direct live-event facts. |
| P5 ATMONTO-constrained LLM extraction | Supported with caveats. LLMs can support ontology/KG construction, but the literature consistently requires ontology conformance, faithfulness to source text, and review. | LLM-supported ontology/KG construction recommends human-in-the-loop evaluation [7]; Text2KGBench evaluates ontology conformance and hallucinations [8]; generative IE survey supports LLM IE as promising but evolving [11]; event-extraction survey warns about hallucinations, temporal fragility, and causal-linking fragility [12]; hallucination survey motivates mitigation controls [13]. | Constrain outputs to allowed classes/properties, require exact evidence spans, run domain/range validation, and keep event/causal triples as bronze until reviewed. |
| P6 validation, repair, and acceptance gate | Strongly supported structurally, but not semantically complete. SHACL validates RDF constraints [6]; ontology-guided KG benchmarks distinguish fact extraction, ontology conformance, and hallucination [8]; hybrid LLM + human KG validation improves precision with recall tradeoff [10]. | SHACL review [6], Text2KGBench [8], KG validation with LLM + human-in-loop [10]. | Add explicit acceptance statuses: `accepted_deterministic`, `accepted_reviewed`, `rejected_schema`, `rejected_evidence`, `rejected_temporal`, `bronze_until_reviewed`. State that SHACL/domain-range validation is structural evidence, not proof of semantic truth. |
| P7 KG construction and cross-source integration | Strongly supported for ATM/NAS integration. ATMGRAPH and ATM ontology integration papers support semantic integration across aviation data domains, including airports, weather, restrictions, flight, and surveillance data. | ATMGRAPH [2], ontology-based ATM integration [3], flight-safety message ontology [26]. | Keep KG claims to retrospective integration and query/search support. Separate data-source availability gaps from ontology gaps. |
| P8 GraphRAG / KG-RAG retrieval and QA | Supported with task-specific caveats. GraphRAG literature supports graph-structured retrieval, but also shows that RAG and GraphRAG have different strengths, limitations, and evaluation tradeoffs. | GraphRAG survey [16], RAG vs GraphRAG systematic evaluation [17], GraphRAG-Bench [18], KG-based RAG QA deployment [19]. | Keep source-only/vector-only baselines. Claim GraphRAG value only for evidence traceability, graph/path coverage, multi-source joins, or measured QA gains. Do not claim universal Recall@k improvement. |
| P9 layered evaluation and CQs | Strongly supported. RAGAS and ARES evaluate context relevance, faithfulness, answer relevance, and related RAG dimensions; RAG evaluation surveys stress multi-component evaluation; CQ literature supports scope definition and ontology evaluation. | ARES [20], RAGAS [21], RAG evaluation survey [22], eRAG [23], CQ survey [24], CQ/SPARQL analysis [25]. | Preserve layered metrics. Do not collapse retrieval, KG validity, citation quality, and safety into one score. Label CQs by required source family and unsupported/no-answer status. |
| P10 human review and gold/silver/bronze labels | Strongly supported. LLM-assisted ontology/KG construction and validation literature repeatedly recommends human review for quality-sensitive outputs. | Kommineni et al. [7], Docs2KG [9], Tsaneva et al. [10]. | Keep deterministic structured fields as silver, reviewed samples as gold, and LLM event/causal triples as bronze until reviewed. |
| P11 claim boundaries and safety framing | Strongly supported as a necessary limitation. RAG and LLM hallucination literature supports grounding and hallucination mitigation, but not unsupported operational authority. | Hallucination survey [13], RAG evaluation survey [22]. | Keep the project wording at retrospective, evidence-traceable aviation QA. Avoid live operational or certification language. |

## Research Question Fit

| Current ATMONTO RQ | Consensus validation |
| --- | --- |
| RQ1: Can NASA ATMONTO be transformed into a usable project ontology profile? | Supported. ATMONTO is explicitly documented as a conceptual model for NAS/ATM information management [1], and SHACL/ontology validation literature supports profile-based constraint checking [6]. |
| RQ2: Does ATMONTO-constrained extraction reduce unsupported classes/properties and domain/range violations? | Supported as an experimental question. Text2KGBench directly treats ontology conformance, source faithfulness, and hallucination as separate metrics for ontology-guided KG generation [8]. |
| RQ3: Does a mapping-rule layer improve cross-source entity linking and provenance? | Supported. Semantic KG construction from structured data and ATMGRAPH both rely on mappings across heterogeneous sources [2, 5]. |
| RQ4: Does the resulting KG improve evidence-traceable CQ answering over source-only retrieval? | Supported with caveats. GraphRAG/KG-RAG literature supports structured retrieval, but systematic comparisons show task-specific tradeoffs [16, 17, 18, 19]. This must remain an empirical question. |
| RQ5: Which ATMONTO areas are covered by open reproducible data? | Supported as a source-coverage/gap-analysis question. ATM ontology alignment literature reports conceptual mismatches [4], while ATMGRAPH highlights practical challenges in applied aviation KG construction [2]. |

## Required Design Strengthening

1. Add a pipeline-level quality label to every produced candidate triple:
   `deterministic_silver`, `llm_bronze_until_reviewed`, `manual_gold`,
   `rejected_schema`, `rejected_evidence`, `rejected_temporal`, or
   `rejected_unmapped_source`.
2. Add SHACL or equivalent domain/range validation between extraction and KG
   acceptance. Keep the wording precise: this proves structural conformance, not
   semantic truth.
3. Keep C7 deterministic translator as an upper-bound condition for structured
   records. If the LLM beats or loses to C7, interpret that per source family,
   not as a global LLM result.
4. Require exact evidence containment for all LLM-produced triples. The evidence
   string must occur in the captured source record or normalized source text.
5. Make ATCSCC advisory time windows and impacting-condition fields review
   targets before they can be gold evidence.
6. Evaluate CQs by source-family requirement:
   weather-only, NAS-reference-only, advisory/TMI-only, cross-source
   weather-advisory, cross-source NAS-advisory, and unsupported/no-answer.
7. Keep GraphRAG evaluation layered: retrieval metrics, graph evidence/path
   metrics, answer faithfulness/citation metrics, and abstention metrics should
   stay separate.
8. Make AIRM-O an alignment audit source only. Its existence improves
   interoperability analysis but does not validate extracted ATMONTO ABox facts.

## Pass/Fail Gates Before Claiming Pipeline Validity

| Gate | Pass condition |
| --- | --- |
| G0 source snapshot gate | Every source family has a manifest with URL, command, retrieved time, source effective date, raw hash, parser version, and known limitations. |
| G1 ontology profile gate | NASA ATMONTO profile parses successfully and exposes selected classes/properties/domains/ranges used by the experiment. |
| G2 deterministic translator gate | Structured sources produce normalized JSONL with record counts, source IDs, and stable entity keys. |
| G3 LLM evidence gate | Every LLM candidate triple has exact source evidence and source record provenance. |
| G4 schema validation gate | Accepted triples have allowed classes/properties and pass domain/range or SHACL-equivalent checks. |
| G5 review gate | LLM-derived event, causal, and ambiguous temporal triples remain bronze until manual review. |
| G6 retrieval/QA gate | Source-only, vector-only, and KG-enabled variants are compared on the same CQs with separate retrieval, graph, answer, citation, and abstention metrics. |
| G7 claim gate | Final claims are mapped to evidence artifacts and negative results remain visible. |

## Bottom Line

Consensus supports the current pipeline design as a defensible research pipeline
for ontology-constrained, retrospective ATM/NAS data integration and
evidence-traceable QA. It does not support treating LLM extraction as
self-validating, treating ATMONTO/AIRM-O as fact-layer ground truth, or claiming
GraphRAG universally improves retrieval.

The safest thesis framing is:

> This pipeline tests whether a NASA ATMONTO-constrained KG construction and
> GraphRAG workflow can improve schema validity, provenance completeness,
> cross-source evidence traceability, and CQ-level answer grounding over
> source-only baselines, while explicitly measuring recall tradeoffs and
> unsupported-question abstention.

## References

[1] [The NASA Air Traffic Management Ontology: Technical Documentation](https://consensus.app/papers/the-nasa-air-traffic-management-ontology-technical-keller/aaa68d992d9257dc947aa197a05cffe7/?utm_source=chatgpt). R. Keller. 2017. Citation count: 18.

[2] [Building a Knowledge Graph for the Air Traffic Management Community](https://consensus.app/papers/building-a-knowledge-graph-for-the-air-traffic-management-keller/0bd9184f163a5d03b3a5bcc8b926c7cf/?utm_source=chatgpt). R. Keller. 2019. Companion Proceedings of The 2019 World Wide Web Conference. Citation count: 21.

[3] [Ontology-Based Data Integration for Semantic Interoperability in Air Traffic Management](https://consensus.app/papers/ontologybased-data-integration-for-semantic-egami-lu/d4c49acd073351f8a0c32e8f4732254e/?utm_source=chatgpt). S. Egami, Xiaodong Lu, T. Koga, Y. Sumiya. 2020. 2020 IEEE 14th International Conference on Semantic Computing (ICSC). Citation count: 5.

[4] [Matching Ontologies for Air Traffic Management: a Comparison and Reference Alignment of the AIRM and NASA ATM Ontologies](https://consensus.app/papers/matching-ontologies-for-air-traffic-management-a-vennesland-keller/01af37df362c50a698821ec2fbba7aeb/?utm_source=chatgpt). A. Vennesland, R. Keller, C. Schuetz, E. Gringinger, B. Neumayr. 2019. Citation count: 7.

[5] [Building Semantic Knowledge Graphs from (Semi-)Structured Data: A Review](https://consensus.app/papers/building-semantic-knowledge-graphs-from-semistructured-ryen-soylu/1320b5afd1ab58d6a3e24c91a499425e/?utm_source=chatgpt). Vetle Ryen, A. Soylu, D. Roman. 2022. Future Internet. Citation count: 63.

[6] [A Review of SHACL: From Data Validation to Schema Reasoning for RDF Graphs](https://consensus.app/papers/a-review-of-shacl-from-data-validation-to-schema-reasoning-pareti-konstantinidis/10995bdbe3cc54f397f5505ae787cc9b/?utm_source=chatgpt). Paolo Pareti, G. Konstantinidis. 2021. Citation count: 42.

[7] [From human experts to machines: An LLM supported approach to ontology and knowledge graph construction](https://consensus.app/papers/from-human-experts-to-machines-an-llm-supported-approach-to-kommineni-knig-ries/57f213fdb33c53609cd26604814de6b3/?utm_source=chatgpt). Vamsi Krishna Kommineni, B. Koenig-Ries, Sheeba Samuel. 2024. ArXiv. Citation count: 99.

[8] [Text2KGBench: A Benchmark for Ontology-Driven Knowledge Graph Generation from Text](https://consensus.app/papers/text2kgbench-a-benchmark-for-ontologydriven-knowledge-mihindukulasooriya-tiwari/b24be0d0ff9f52eebfa7a23833492952/?utm_source=chatgpt). Nandana Mihindukulasooriya, S. Tiwari, Carlos F. Enguix, K. Lata. 2023. Citation count: 118.

[9] [Docs2KG: A Human-LLM Collaborative Approach to Unified Knowledge Graph Construction from Heterogeneous Documents](https://consensus.app/papers/docs2kg-a-humanllm-collaborative-approach-to-unified-sun-luo/d2c7ec831d695f5fb3a02d3cd10ae6b0/?utm_source=chatgpt). Qiang Sun, Yuanyi Luo, Wenxiao Zhang, Sirui Li, Jichunyang Li, Kai Niu, Xiangrui Kong, Wei Liu. 2025. Companion Proceedings of the ACM on Web Conference 2025. Citation count: 6.

[10] [Knowledge graph validation by integrating LLMs and human-in-the-loop](https://consensus.app/papers/knowledge-graph-validation-by-integrating-llms-and-tsaneva-dess/ef224a0a19d05ba4a3667ac7df16c122/?utm_source=chatgpt). Stefani Tsaneva, D. Dessi, Francesco Osborne, Marta Sabou. 2025. Information Processing & Management. Citation count: 37.

[11] [Large language models for generative information extraction: a survey](https://consensus.app/papers/large-language-models-for-generative-information-xu-chen/4c63099c001557d0847c860d1f98e213/?utm_source=chatgpt). Derong Xu, Wei Chen, Wenjun Peng, Chao Zhang, Tong Xu, Xiangyu Zhao, Xian Wu, Yefeng Zheng, Enhong Chen. 2023. Frontiers of Computer Science. Citation count: 379.

[12] [Event Extraction in Large Language Model](https://consensus.app/papers/event-extraction-in-large-language-model-li-han/3eee89eb691d5bab933b78db77888d77/?utm_source=chatgpt). Bobo Li, Xudong Han, Jiang Liu, Yuzhe Ding, Liqiang Jing, Zhaoqi Zhang, Jinheng Li, Xinya Du, Fei Li, Meishan Zhang, Min Zhang, Aixin Sun, P. Yu, Hao Fei. 2025. ArXiv. Citation count: 4.

[13] [A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions](https://consensus.app/papers/a-survey-on-hallucination-in-large-language-models-huang-yu/2ed4ee36843c59e58e5b66fb210b0d54/?utm_source=chatgpt). Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng, Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing Qin, Ting Liu. 2023. ACM Transactions on Information Systems. Citation count: 2734.

[14] [Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion](https://consensus.app/papers/docling-an-efficient-opensource-toolkit-for-aidriven-livathinos-auer/ec62522c3373520680261d2ec660d533/?utm_source=chatgpt). Nikolaos Livathinos, Christoph Auer, Maksym Lysak, A. Nassar, Michele Dolfi, Panos Vagenas, Cesar Berrospi Ramis, Matteo Omenetti, K. Dinkla, Yusik Kim, Shubham Gupta, Rafael Teixeira de Lima, Valery Weber, Lucas Morin, Ingmar Meijer, Viktor Kuropiatnyk, P. Staar. 2025. ArXiv. Citation count: 49.

[15] [A Comparative Study of PDF Parsing Tools Across Diverse Document Categories](https://consensus.app/papers/a-comparative-study-of-pdf-parsing-tools-across-diverse-adhikari-agarwal/356c29104c7f53a8a9695d4dc3bd8a49/?utm_source=chatgpt). Narayan Adhikari, S. Agarwal. 2024. ArXiv. Citation count: 33.

[16] [Graph Retrieval-Augmented Generation: A Survey](https://consensus.app/papers/graph-retrievalaugmented-generation-a-survey-peng-zhu/1b8c5362a3d3538ba1dd90f9b40178f1/?utm_source=chatgpt). Boci Peng, Yun Zhu, Yongchao Liu, Xiaohe Bo, Haizhou Shi, Chuntao Hong, Yan Zhang, Siliang Tang. 2024. ACM Transactions on Information Systems. Citation count: 381.

[17] [RAG vs. GraphRAG: A Systematic Evaluation and Key Insights](https://consensus.app/papers/rag-vs-graphrag-a-systematic-evaluation-and-key-insights-han-shomer/79a87d60d85a5596b0c6f1077a0b4725/?utm_source=chatgpt). Haoyu Han, Harry Shomer, Yu Wang, Yongjia Lei, Kai Guo, Zhigang Hua, Bo Long, Hui Liu, Jiliang Tang. 2025. ArXiv. Citation count: 60.

[18] [GraphRAG-Bench: Challenging Domain-Specific Reasoning for Evaluating Graph Retrieval-Augmented Generation](https://consensus.app/papers/graphragbench-challenging-domainspecific-reasoning-for-xiao-dong/622e8b388c575636b2d8f4b7463068c0/?utm_source=chatgpt). Yilin Xiao, Junnan Dong, Chuang Zhou, Su Dong, Qianwen Zhang, Di Yin, Xing Sun, Xiao Huang. 2025. ArXiv. Citation count: 15.

[19] [Retrieval-Augmented Generation with Knowledge Graphs for Customer Service Question Answering](https://consensus.app/papers/retrievalaugmented-generation-with-knowledge-graphs-for-xu-cruz/34effc648b565bf4be1a759f098455cf/?utm_source=chatgpt). Zhentao Xu, Mark Jerome Cruz, M. Guevara, Tie-xin Wang, Manasi Deshpande, Xiaofeng Wang, Zheng Li. 2024. Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. Citation count: 219.

[20] [ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems](https://consensus.app/papers/ares-an-automated-evaluation-framework-for-saad-falcon-khattab/dd05712d36365561becd51b2b17be9a4/?utm_source=chatgpt). Jon Saad-Falcon, O. Khattab, Christopher Potts, Matei Zaharia. 2023. ArXiv. Citation count: 252.

[21] [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://consensus.app/papers/ragas-automated-evaluation-of-retrieval-augmented-shahul-james/1e214d3a38e2558b8d6595f964842bca/?utm_source=chatgpt). ES Shahul, J. James, Luis Espinosa Anke, S. Schockaert. 2023. ArXiv. Citation count: 636.

[22] [Evaluation of Retrieval-Augmented Generation: A Survey](https://consensus.app/papers/evaluation-of-retrievalaugmented-generation-a-survey-yu-gan/861805cd172d534298b77a83a0d83d92/?utm_source=chatgpt). Hao Yu, Aoran Gan, Kai Zhang, Shiwei Tong, Qi Liu, Zhaofeng Liu. 2024. ArXiv. Citation count: 257.

[23] [Evaluating Retrieval Quality in Retrieval-Augmented Generation](https://consensus.app/papers/evaluating-retrieval-quality-in-retrievalaugmented-salemi-zamani/a0505157c8a35c0082d67273dc6c6818/?utm_source=chatgpt). Alireza Salemi, Hamed Zamani. 2024. Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. Citation count: 181.

[24] [Use of Competency Questions in Ontology Engineering: A Survey](https://consensus.app/papers/use-of-competency-questions-in-ontology-engineering-a-quirino-salamon/2cb3dc0807b6581ca448a183299303b7/?utm_source=chatgpt). Glaice K. S. Quirino, J. S. Salamon, M. Barcellos. 2023. Citation count: 26.

[25] [Analysis of Ontology Competency Questions and their formalizations in SPARQL-OWL](https://consensus.app/papers/analysis-of-ontology-competency-questions-and-their-wisniewski-potoniec/10971540ec3c52e488c274b84edeba70/?utm_source=chatgpt). Dawid Wisniewski, Jedrzej Potoniec, Agnieszka Lawrynowicz, C. Keet. 2019. Journal of Web Semantics. Citation count: 75.

[26] [Ontology generation for flight safety messages in air traffic management](https://consensus.app/papers/ontology-generation-for-flight-safety-messages-in-air-aghdam-tabbakh/c53444faec215b978b77482f5c2f3523/?utm_source=chatgpt). Mahdi Yousefzadeh Aghdam, Seyed Reza Kamel Tabbakh, Seyed Javad Mahdavi Chabok, M. Kheyrabadi. 2021. Journal of Big Data. Citation count: 9.
