# Consensus Validation of Extraction Methods

## Material Passport

- Artifact: Consensus-backed validation of the data-source extraction method matrix.
- Scope: extraction methods M1-M8 in `reports/stages/data_source_extraction_method_matrix.md`.
- Evidence source: Consensus academic-paper search and fetched paper records.
- Validation mode: literature support audit, not an experimental proof that the local implementation is already correct.
- Claim boundary: this report validates method choice and risk controls. It does not validate local extraction outputs or aviation operational correctness.

## Executive Verdict

The matrix is well supported at the method-selection level. The strongest support is for ontology/SHACL validation, structured and semi-structured data to KG mapping, ATM ontology-based integration, and layout-aware PDF/document extraction. The riskiest method remains LLM extraction for ATCSCC-style events: Consensus supports LLM-based information/event extraction as a promising method, but the literature also warns about hallucination, weak constraints, temporal/causal fragility, and provenance problems. Therefore the matrix's rule is correct: deterministic translators first; LLM extraction only behind evidence containment, schema validation, and human review.

## Method Validation Matrix

| Method | Consensus-backed verdict | Supporting evidence | Required project control |
| --- | --- | --- | --- |
| M1 ontology/schema inventory | Strongly supported. Ontologies, SHACL, and ontology-derived constraints are established ways to validate RDF/KG structure. | SHACL is reviewed as a W3C RDF validation language [1]; Astrea supports automatic SHACL-shape generation from ontologies [2]; SHACL over endpoints and ontology-aware validation are active methods [3]. | Generate a NASA ATMONTO profile and SHACL/domain-range checks before accepting triples. |
| M2 structured API translator | Strongly supported by KG construction literature: structured/semi-structured sources should be mapped deterministically to semantic representations when fields are stable. | Systematic review of semantic KG construction from structured/semi-structured data [4]; ontology-driven relational mapping to triples [5]. | Keep source fields, raw strings, checksums, parser version, and deterministic mapping rules. |
| M3 archive/reference-data parser | Strongly supported as an extension of structured-source KG mapping. Fixed-cycle reference data should be parsed as authoritative entity backbone, not LLM text. | Semi-structured KG review [4]; virtual KG/OBDA mapping literature [6, 7]. | Parse NASR members with file-specific parsers and attach effective-cycle metadata to each record. |
| M4 semi-structured HTML event extraction | Supported with caveats. Event extraction with LLMs is plausible, but weak constraints cause hallucinations and fragile temporal/causal linking. | LLM event extraction survey emphasizes event schemas and slot constraints for grounding/verification [8]; LLM information extraction survey supports generative IE but treats it as an active research area [9]; hallucination survey motivates strict mitigation [10]; ODKE+ supports hybrid rule-plus-ontology-guided extraction with verification [11]. | Require exact quote evidence, ATMONTO allowed terms, domain/range validation, timestamp review, and human review before gold use. |
| M5 reference document chunking | Strongly supported. Layout-aware extraction is necessary for PDFs; tool choice should depend on document type and task. | Docling provides richly structured document conversion [12]; comparative PDF parser study shows PyMuPDF is strong for text extraction while task/document type matters [13]; VILA shows visual layout groups improve structured PDF extraction [14]. | Keep hybrid Docling + PyMuPDF: Docling for structure, PyMuPDF for text-fidelity fallback. Do not claim a universal best parser. |
| M6 structured tabular translator | Strongly supported. Relational/table data should use declarative or deterministic mapping into ontology/KG form. | Ontology-driven relational data mapping [5]; R2RML-style and conceptual mapping patterns for VKGs [7]; structured/semi-structured KG review [4]. | Use schema dictionaries, type conversion, key normalization, and explicit mapping files. |
| M7 time-series/trajectory translator | Supported, but only as a separate extension. Aviation and ATM literature supports semantic integration of spatiotemporal/trajectory data, but this raises scale and query-performance issues. | ATMGRAPH integrates multiple structured aviation sources [15]; semantic representation and scale-up of integrated ATM data discusses one-day airport prototype and scaling challenges [16]; ATM ontology interoperability studies include weather, airports, flight, surveillance, and restrictions [17]. | Keep OpenSky/trajectory work optional and separate from the primary ATMONTO claims. Validate time/coordinate sanity and provenance. |
| M8 literature/source-selection extraction | Supported as related-work/source-justification workflow, not as ABox extraction. | NTRS/ATM ontology literature supports source selection and ontology alignment context [15-18], while document extraction literature supports PDF processing [12-14]. | Use papers for citations, source links, and design rationale only. Do not convert literature claims into event facts. |

## Source-Specific Implications

- NASA ATMONTO and AIRM-O should be treated as schema/reference layers, not fact layers. Consensus found ATM ontology alignment work that explicitly notes conceptual mismatches and provides manual reference alignment between AIRM-O and NASA ATMONTO [18]. This supports our decision to keep AIRM-O as an audit/alignment reference rather than replacing NASA ATMONTO.
- AviationWeather and NASR should be deterministic-translator sources. Their records are structured or cycle-valid, so LLM extraction would add risk without adding much value. This is consistent with structured/semi-structured KG construction and ontology-driven relational mapping literature [4, 5].
- ATCSCC advisories are the correct primary LLM target, but only as bronze candidates before validation. The event-extraction and hallucination literature supports schema/slot constraints, evidence grounding, and review rather than free-form extraction [8-11].
- FAA reference PDFs and manuals should use hybrid document parsing. Consensus supports layout-aware PDF extraction and task-specific parser choice, which matches the current Docling + PyMuPDF policy [12-14].
- Aviation-specific semantic-integration papers support the broader thesis pivot: ATM data integration needs ontology-backed semantic interoperability across weather, airports, restrictions, flight, surveillance, and other heterogeneous sources [15-17].

## Adjustments to the Matrix

No reversal is needed. The Consensus check supports the existing hierarchy:

1. Deterministic parsers for official structured/cycle-valid data.
2. Ontology/SHACL/domain-range gates for KG validity.
3. Hybrid PDF extraction for reference documents.
4. Constrained LLM extraction only for text-rich event/advisory sources.
5. Human-in-the-loop review before gold labels or thesis claims.

The only strengthening I recommend is to label M4 and any causal/event relation extraction as `bronze_until_reviewed` in future KG artifacts. The literature repeatedly treats LLM extraction as useful but not self-validating.

## References

[1] [A Review of SHACL: From Data Validation to Schema Reasoning for RDF Graphs](https://consensus.app/papers/a-review-of-shacl-from-data-validation-to-schema-reasoning-pareti-konstantinidis/10995bdbe3cc54f397f5505ae787cc9b/?utm_source=chatgpt). Paolo Pareti, G. Konstantinidis. 2021. Citation count: 42.

[2] [Astrea: Automatic Generation of SHACL Shapes from Ontologies](https://consensus.app/papers/astrea-automatic-generation-of-shacl-shapes-from-cimmino-fernndez-izquierdo/b787f41aac2a5122883c2e3cdf0e3836/?utm_source=chatgpt). Andrea Cimmino, Alba Fernandez-Izquierdo, R. Garcia-Castro. 2020. The Semantic Web. Citation count: 50.

[3] [Validating Shacl Constraints over a Sparql Endpoint](https://consensus.app/papers/validating-shacl-constraints-over-a-sparql-endpoint-corman-florenzano/7220c4725a2c5164bbc84ac492e662c3/?utm_source=chatgpt). Julien Corman, F. Florenzano, Juan L. Reutter, Ognjen Savkovic. 2019. Citation count: 46.

[4] [Building Semantic Knowledge Graphs from (Semi-)Structured Data: A Review](https://consensus.app/papers/building-semantic-knowledge-graphs-from-semistructured-ryen-soylu/1320b5afd1ab58d6a3e24c91a499425e/?utm_source=chatgpt). Vetle Ryen, A. Soylu, D. Roman. 2022. Future Internet. Citation count: 63.

[5] [Ontology-driven relational data mapping for constructing a knowledge graph of porphyry copper deposits](https://consensus.app/papers/ontologydriven-relational-data-mapping-for-constructing-wang-tan/92f69dcca8885e8f8b5c6a79c13dd36e/?utm_source=chatgpt). Chengbin Wang, L. Tan, Yuanjun Li, Mingguo Wang, Xiaogang Ma, Jianguo Chen. 2024. Earth Science Informatics. Citation count: 10.

[6] [Virtual Knowledge Graphs: An Overview of Systems and Use Cases](https://consensus.app/papers/virtual-knowledge-graphs-an-overview-of-systems-and-use-xiao-ding/c86d8dcbca775063821fe2628c5255aa/?utm_source=chatgpt). Guohui Xiao, L. Ding, Benjamin Cogrel, Diego Calvanese. 2019. Data Intelligence. Citation count: 153.

[7] [Conceptually-grounded Mapping Patterns for Virtual Knowledge Graphs](https://consensus.app/papers/conceptuallygrounded-mapping-patterns-for-virtual-calvanese-gal/411eb26e482d5231b13d02cb6ff7a02c/?utm_source=chatgpt). Diego Calvanese, A. Gal, Davide Lanti, Marco Montali, A. Mosca, Roee Shraga. 2023. Data & Knowledge Engineering. Citation count: 13.

[8] [Event Extraction in Large Language Model](https://consensus.app/papers/event-extraction-in-large-language-model-li-han/3eee89eb691d5bab933b78db77888d77/?utm_source=chatgpt). Bobo Li, Xudong Han, Jiang Liu, Yuzhe Ding, Liqiang Jing, Zhaoqi Zhang, Jinheng Li, Xinya Du, Fei Li, Meishan Zhang, Min Zhang, Aixin Sun, P. Yu, Hao Fei. 2025. ArXiv. Citation count: 4.

[9] [Large language models for generative information extraction: a survey](https://consensus.app/papers/large-language-models-for-generative-information-xu-chen/4c63099c001557d0847c860d1f98e213/?utm_source=chatgpt). Derong Xu, Wei Chen, Wenjun Peng, Chao Zhang, Tong Xu, Xiangyu Zhao, Xian Wu, Yefeng Zheng, Enhong Chen. 2023. Frontiers of Computer Science. Citation count: 379.

[10] [A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions](https://consensus.app/papers/a-survey-on-hallucination-in-large-language-models-huang-yu/2ed4ee36843c59e58e5b66fb210b0d54/?utm_source=chatgpt). Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng, Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing Qin, Ting Liu. 2023. ACM Transactions on Information Systems. Citation count: 2734.

[11] [ODKE+: Ontology-Guided Open-Domain Knowledge Extraction with LLMs](https://consensus.app/papers/odke-ontologyguided-opendomain-knowledge-extraction-khorshidi-nikfarjam/bf5f40fe4528547882c7ebbfbbd21113/?utm_source=chatgpt). Samira Khorshidi, Azadeh Nikfarjam, S. Shankar, Yisi Sang, Yash Govind, Hyunseok Jang, Ali Kasgari, Alexis McClimans, Mohamed Soliman, V. Konda, Ahmed Fakhry, Xiaoguang Qi. 2025. ArXiv. Citation count: 1.

[12] [Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion](https://consensus.app/papers/docling-an-efficient-opensource-toolkit-for-aidriven-livathinos-auer/ec62522c3373520680261d2ec660d533/?utm_source=chatgpt). Nikolaos Livathinos, Christoph Auer, Maksym Lysak, A. Nassar, Michele Dolfi, Panos Vagenas, Cesar Berrospi Ramis, Matteo Omenetti, K. Dinkla, Yusik Kim, Shubham Gupta, Rafael Teixeira de Lima, Valery Weber, Lucas Morin, Ingmar Meijer, Viktor Kuropiatnyk, P. Staar. 2025. ArXiv. Citation count: 49.

[13] [A Comparative Study of PDF Parsing Tools Across Diverse Document Categories](https://consensus.app/papers/a-comparative-study-of-pdf-parsing-tools-across-diverse-adhikari-agarwal/356c29104c7f53a8a9695d4dc3bd8a49/?utm_source=chatgpt). Narayan Adhikari, S. Agarwal. 2024. ArXiv. Citation count: 33.

[14] [VILA: Improving Structured Content Extraction from Scientific PDFs Using Visual Layout Groups](https://consensus.app/papers/vila-improving-structured-content-extraction-from-shen-lo/2d54806e0f055a269233f5048300f9dc/?utm_source=chatgpt). Shannon Zejiang Shen, Kyle Lo, Lucy Lu Wang, Bailey Kuehl, Daniel S. Weld, Doug Downey. 2021. Transactions of the Association for Computational Linguistics. Citation count: 46.

[15] [Building a Knowledge Graph for the Air Traffic Management Community](https://consensus.app/papers/building-a-knowledge-graph-for-the-air-traffic-management-keller/0bd9184f163a5d03b3a5bcc8b926c7cf/?utm_source=chatgpt). R. Keller. 2019. Companion Proceedings of The 2019 World Wide Web Conference. Citation count: 21.

[16] [Semantic representation and scale-up of integrated air traffic management data](https://consensus.app/papers/semantic-representation-and-scaleup-of-integrated-air-keller-ranjan/7e5a0c6eb8e35e539cdb74b0e8f1f8d1/?utm_source=chatgpt). R. Keller, Shubha Ranjan, M. Wei, Michelle M. Eshow. 2016. Citation count: 21.

[17] [Ontology-Based Data Integration for Semantic Interoperability in Air Traffic Management](https://consensus.app/papers/ontologybased-data-integration-for-semantic-egami-lu/d4c49acd073351f8a0c32e8f4732254e/?utm_source=chatgpt). S. Egami, Xiaodong Lu, T. Koga, Y. Sumiya. 2020. 2020 IEEE 14th International Conference on Semantic Computing (ICSC). Citation count: 5.

[18] [Matching Ontologies for Air Traffic Management: a Comparison and Reference Alignment of the AIRM and NASA ATM Ontologies](https://consensus.app/papers/matching-ontologies-for-air-traffic-management-a-vennesland-keller/01af37df362c50a698821ec2fbba7aeb/?utm_source=chatgpt). A. Vennesland, R. Keller, C. Schuetz, E. Gringinger, B. Neumayr. 2019. Citation count: 7.

[19] [From human experts to machines: An LLM supported approach to ontology and knowledge graph construction](https://consensus.app/papers/from-human-experts-to-machines-an-llm-supported-approach-to-kommineni-knig-ries/57f213fdb33c53609cd26604814de6b3/?utm_source=chatgpt). Vamsi Krishna Kommineni, B. Konig-Ries, Sheeba Samuel. 2024. ArXiv. Citation count: 99.

[20] [Docs2KG: A Human-LLM Collaborative Approach to Unified Knowledge Graph Construction from Heterogeneous Documents](https://consensus.app/papers/docs2kg-a-humanllm-collaborative-approach-to-unified-sun-luo/d2c7ec831d695f5fb3a02d3cd10ae6b0/?utm_source=chatgpt). Qiang Sun, Yuanyi Luo, Wenxiao Zhang, Sirui Li, Jichunyang Li, Kai Niu, Xiangrui Kong, Wei Liu. 2025. Companion Proceedings of the ACM on Web Conference 2025. Citation count: 6.

[21] [Ontology generation for flight safety messages in air traffic management](https://consensus.app/papers/ontology-generation-for-flight-safety-messages-in-air-aghdam-tabbakh/c53444faec215b978b77482f5c2f3523/?utm_source=chatgpt). Mahdi Yousefzadeh Aghdam, Seyed Reza Kamel Tabbakh, Seyed Javad Mahdavi Chabok, M. Kheyrabadi. 2021. Journal of Big Data. Citation count: 9.
