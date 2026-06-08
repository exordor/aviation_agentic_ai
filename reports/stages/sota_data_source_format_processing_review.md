# SOTA Data Source / Format / Processing Review

- Status: `data_methodology_review`
- Scope: near-term aviation ATMONTO / FAA ATCSCC experiment.
- Question: whether the current experiment data are methodologically defensible, and how to minimally improve them using data practices from ontology-based LLM KG extraction, schema-constrained IE, LLM-based KGC, and GraphRAG / KG-RAG evaluation.
- Non-scope: SAF, hydrogen, airport energy, and other energy-transition directions. Those remain a long-term research track.

## Executive Recommendation

Keep FAA ATCSCC advisories as the primary source family. Do not replace them with PDFs or a generic document corpus.

The stronger SOTA-aligned design is:

1. Primary source family A: FAA ATCSCC advisories.
   - Role: semi-structured aviation event / TMI extraction.
   - Output: event-instance KG facts, such as advisory identifiers, effective times, impacted NAS elements, TMI type, reroute reason, implementation status, and supporting spans.
   - Evaluation: field-level and triple-level P/R/F1, schema conformance, canonicalization accuracy, source-span support, and error taxonomy.

2. Secondary source family B: FAA / NASA PDF reference texts.
   - Role: terminology, procedure, and schema-documentation support.
   - Output: definition / alias / concept-support facts, not event-instance facts.
   - Evaluation: passage-level extraction accuracy, evidence containment, section/page provenance, term mapping accuracy, and retrieval support.

3. Reference layer C: NASA ATMONTO plus NASR / FAA reference vocabularies.
   - Role: schema profile, canonicalization and validation support.
   - Not role: ground-truth KG.

This means the corrected experiment should be an expanded two-source-family design, not a domain pivot and not a replacement of ATCSCC.

## Pattern Across Representative Papers

SOTA work rarely treats an ontology file alone as the data source. The usual pattern is layered:

1. Raw evidence source: domain short text, semi-structured records, web pages, research paragraphs, heterogeneous documents, existing KG records, or QA benchmark items.
2. Schema or ontology layer: fixed ontology, retrieved schema slice, ontology snippet, generated schema, or benchmark KG schema.
3. Processing bridge: open extraction, schema-slice retrieval, canonicalization, entity linking, deduplication, validation, and provenance tracking.
4. Evaluation layer: gold triples, field match, schema conformance, canonicalization accuracy, retrieval recall, faithfulness, human review, or ablation.

The key implication for this project: ATCSCC advisories are a plausible primary evidence source, but the experiment fails if all metrics are forced through a single "LLM creates valid ATMONTO triples directly" interface.

## Paper-by-Paper Data Matrix

| Paper / source | Data source | Data format | Processing pattern | Gold / evaluation | Lesson for this experiment | Caveat |
| --- | --- | --- | --- | --- | --- | --- |
| [1] [Extract, Define, Canonicalize: An LLM-based Framework for Knowledge Graph Construction](https://consensus.app/papers/extract-define-canonicalize-an-llmbased-framework-for-zhang-soh/711b33c15bfc562d9137b07050be7666/), Zhang & Soh, 2024, ArXiv, citations: 110 | Input text over three KGC benchmarks | Text to triples, with larger schemas | Open extraction, schema definition/retrieval, post-hoc canonicalization | KGC benchmark triplet quality | Supports splitting S1 into raw open extraction and S1b canonicalized extraction. It directly argues against putting a large schema into one prompt and expecting valid triples. | Do not copy its self-generated-schema setting wholesale; this project has an ATMONTO-derived schema profile. |
| [2] [Ontology-guided Knowledge Graph Construction from Maintenance Short Texts](https://consensus.app/papers/ontologyguided-knowledge-graph-construction-from-cauter-yakovets/28494e5fc0905fc598416a17f098c8c0/), Cauter & Yakovets, 2024, KaLLM, citations: 15 | Domain-specific maintenance short texts | Short, domain-specific text records | Ontology-guided triplet extraction plus in-context learning with 20 semantically similar examples | Comparable performance to fine-tuned IE baselines in the reported setting | Strongest support for keeping ATCSCC advisories: they are also short, domain-specific, semi-structured operational-style records. Add 10-20 reviewed dev examples. | Maintenance domain is not aviation; transfer the data pattern, not its labels or scores. |
| [3] [ODKE+: Ontology-Guided Open-Domain Knowledge Extraction with LLMs](https://consensus.app/papers/odke-ontologyguided-opendomain-knowledge-extraction-khorshidi-nikfarjam/bf5f40fe4528547882c7ebbfbbd21113/), Khorshidi et al., 2025, ArXiv, citations: 1 | Web sources, including Wikipedia-scale pages | Open-domain web text | Evidence retrieval, hybrid rule-based and ontology-guided LLM extractors, grounding, corroboration, normalization | High-precision production ingestion metrics | Supports S4: deterministic backbone + ontology snippets + LLM extraction + grounding/corroboration before KG ingestion. | Open-domain production setting; too broad to use as direct benchmark. |
| [4] [Docs2KG](https://consensus.app/papers/docs2kg-a-humanllm-collaborative-approach-to-unified-sun-luo/d2c7ec831d695f5fb3a02d3cd10ae6b0/), Sun et al., 2025, ACM Web Conference Companion, citations: 6 | Heterogeneous enterprise documents | Unstructured documents with text, tables, figures, metadata, and layout | Document processing, Layout KG, Metadata KG, Semantic KG, LLM / ontology / NLP extraction modes, human verification | Human-in-the-loop quality assessment | Supports adding FAA PCG / JO 7110.65BB / NASA ATMONTO PDFs as a separate source family with layout/page/section provenance. | It is a broad framework, not a narrow aviation benchmark. |
| [5] [Structured information extraction from scientific text with large language models](https://consensus.app/papers/structured-information-extraction-from-scientific-text-dagdelen-dunn/075e3f5a3be0575d99f30dc34440d323/), Dagdelen et al., 2024, Nature Communications, citations: 555 | Scientific papers in materials chemistry | Single sentences or full paragraphs; outputs as sentences or JSON-like records | Task-specific NER/RE style extraction with structured records | Task-level extraction evaluation over representative scientific IE tasks | Supports PDF passage extraction as a distinct task, especially JSON records with exact passage evidence. | Materials chemistry data; use the methodological pattern, not the domain ontology. |
| [6] [Building Semantic Knowledge Graphs from (Semi-)Structured Data: A Review](https://consensus.app/papers/building-semantic-knowledge-graphs-from-semistructured-ryen-soylu/1320b5afd1ab58d6a3e24c91a499425e/), Ryen et al., 2022, Future Internet, citations: 63 | Structured and semi-structured data sources | Tables, records, and semi-structured source formats | Semantic Web mapping, ontology use, publication and integration practices | Literature review of tools, methods, source types, ontologies, and challenges | Supports treating ATCSCC as a semi-structured source with deterministic parsing plus semantic mapping. | Review paper; use it for framing, not for performance claims. |
| [7] [LLMs for knowledge graph construction and reasoning](https://consensus.app/papers/llms-for-knowledge-graph-construction-and-reasoning-zhu-wang/bc301ddc6b135419a9743367f3b5545c/), Zhu et al., 2023, World Wide Web, citations: 259 | Eight datasets across entity/relation extraction, event extraction, link prediction, and QA | Existing benchmark datasets | Compare LLMs across construction and reasoning tasks; propose LLM-assisted KG workflows | Task-level quantitative and qualitative evaluation | Supports not relying on one unconstrained LLM extractor. LLMs are better used as support modules, canonicalizers, and reasoning modules around controlled data and schema. | Broad survey/evaluation; does not decide the aviation data source by itself. |
| [8] [Graph Retrieval-Augmented Generation: A Survey](https://consensus.app/papers/graph-retrievalaugmented-generation-a-survey-peng-zhu/1b8c5362a3d3538ba1dd90f9b40178f1/), Peng et al., 2024, ACM TOIS, citations: 381 | Graph-enhanced RAG systems across downstream settings | Text plus graph structures | Graph-based indexing, graph-guided retrieval, graph-enhanced generation | Survey of application domains and evaluation methods | Supports evaluating KG construction separately from graph retrieval and answer generation. | Survey; not an extraction dataset. |
| [9] [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://consensus.app/papers/ragas-automated-evaluation-of-retrieval-augmented-shahul-james/1e214d3a38e2558b8d6595f964842bca/), Shahul et al., 2023, ArXiv, citations: 636 | RAG over reference textual databases | Retrieved context passages plus generated answers | Reference-free metrics for retrieval context, faithfulness, and generation quality | RAG pipeline evaluation dimensions | Supports reporting GraphRAG answer grounding and faithfulness separately from KG triple F1. | Reference-free evaluation should not replace gold-based evaluation for the 100 reviewed ATCSCC records. |
| [10] [STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases](https://consensus.app/papers/stark-benchmarking-llm-retrieval-on-textual-and-wu-zhao/383dfb6b2662532495cb8d747952f4cc/), Wu et al., 2024, ArXiv, citations: 56 | Product search, academic paper search, precision medicine | Semi-structured textual plus relational knowledge bases | Synthetic realistic queries integrating relational and textual constraints; human evaluation; human-generated query reference | Retrieval benchmark for LLM-driven systems | Supports the idea that GraphRAG evaluation should test both textual evidence and graph relations, e.g. entity/triple/path recall. | It is retrieval-focused and non-aviation; do not borrow scores. |

## Data-Methodology Assimilation

The follow-up methodology review reached the same decision as the literature
matrix: keep FAA ATCSCC advisories as the primary source family and add only a
small reference-grounding source family. It should not be read as a new
independent benchmark. Its value is that it sharpens the data boundaries and
adds concrete rerun design constraints.

### Methodology additions adopted here

- ATCSCC remains the main event-extraction corpus. The thesis claim should be
  limited to "FAA ATCSCC advisory event-KG extraction under an ATMONTO-derived
  validator profile".
- FAA PCG, FAA JO 7110.65BB, and NASA ATMONTO PDF are added only as
  reference / terminology / schema-grounding sources. They are not competitors
  for ATCSCC event-instance triple F1.
- NASR is added only as an entity-canonicalization reference layer for
  airports, fixes, facilities, runways, and related identifiers. It does not
  validate advisory reason, status, type, or event truth.
- GraphRAG is evaluated as a separate retrieval and answer-grounding task:
  `retrieval_recall@k`, `citation_support_rate`, `answer_faithfulness`,
  `unsupported_claim_rate`, and answer correctness should not replace KG
  construction F1.
- S1 must remain a raw drift diagnostic. S1b is the first fair baseline because
  it canonicalizes raw open facts into the ATMONTO profile before scoring.

### Additional paper/source leads

These leads are useful for related work and future verification, but they should
not be promoted to formal evidence in the thesis until fetched directly or
validated through direct paper checks or official sources:

| Lead | Reported data pattern | Current status in this report | How to use |
| --- | --- | --- | --- |
| ChatSchema | 100 medical reports and 2,945 key-value pairs for schema-based extraction | Search lead only | Supports the acceptability of small, manually reviewed, schema-constrained gold sets after direct verification. |
| Schema-driven IE from heterogeneous tables | Human-authored schemas over tables from ML, chemistry, materials, and web sources | Search lead only | Supports the field-level evaluation analogy for semi-structured sources. |
| Microsoft GraphRAG / local-to-global | Podcast transcripts and news articles chunked into graph-indexed long corpora | Search lead only | Use for GraphRAG background and global/sensemaking evaluation, not ATCSCC extraction F1. |
| RAKG | Document-level retrieval-augmented KGC from text to standard KGs | Search lead only | Possible reference for long-PDF/reference-doc processing after source verification. |
| Graphusion | Retrieval-augmented KGC with global fusion, entity merging, and conflict resolution | Search lead only | Possible reference for S4 merge/fusion design after source verification. |
| ODKE+ | Web/Wikipedia-scale evidence retrieval, ontology snippets, grounding, and corroboration | Literature record available as [3]; details still need direct paper check before exact numeric claims | Use for the architecture pattern, not as an aviation benchmark. |
| Ontology-guided KGC from Maintenance Short Texts | Short domain-specific records with ontology-guided triplet extraction and 20 similar examples | Literature record available as [2] | Use as the strongest short-text analogy for ATCSCC, while keeping domain-transfer limits explicit. |

### Refined data boundary

The corrected source policy is:

- Event truth comes only from frozen ATCSCC advisory text plus human-reviewed
  gold annotations.
- Schema legality comes from the ATMONTO slice / validator profile.
- Term and procedure support comes from FAA PCG, JO 7110.65BB, and ATMONTO
  technical documentation.
- Entity identity comes from the frozen NASR / FAA reference cycle, with cycle
  date recorded.
- GraphRAG answer support may cite both accepted event facts and reference
  passages, but must report which source family supported each claim.

This resolves the apparent "Should we replace ATCSCC with PDFs?" question:
PDFs should be added, but as a second task family. Mixing PDF definition
extraction and ATCSCC event extraction into one F1 table would be a methodology
error.

## What Data Shapes Are SOTA-Compatible?

The reviewed papers support these data shapes:

- Short domain texts: valid for ontology-guided KG construction when examples and schema slices are controlled.
- Semi-structured records/logs/tables: valid when deterministic parsing and semantic mapping are separated.
- Scientific paragraphs / long-form passages: valid for structured IE, but require passage-level provenance and task-specific labels.
- Heterogeneous documents / PDFs: valid when layout, metadata, and semantic extraction are modeled separately.
- Web pages: valid at scale when evidence retrieval, grounding, corroboration, and confidence thresholds are explicit.
- Existing KGs / benchmarks: useful for retrieval or reasoning evaluation, but not automatically available for domain-specific aviation event truth.
- QA benchmark items: useful for GraphRAG evaluation, but should be generated or reviewed separately from KG construction gold.

Therefore, FAA ATCSCC advisories are not a weak data choice just because they are narrow. Their narrowness is actually useful for a master-thesis experiment, provided the claim is narrowed to ATCSCC / TMI extraction.

## ATCSCC As Primary Source Family

### Why It Is Defensible

- It matches the short domain text pattern from ontology-guided maintenance short text extraction.
- It matches the semi-structured data pattern from Semantic Web KG construction reviews.
- It naturally supports a deterministic backbone for identifiers, dates, times, and template fields.
- It gives a realistic setting where ontology/schema constraints matter: TMI type, affected NAS element, reroute reason, implementation status, and event-specific evidence.
- It is close enough to ATMONTO's ATM advisory vocabulary to justify ATMONTO as an external schema/profile layer.

### Risks

- It is not representative of all aviation text.
- It may reward template parsing more than semantic LLM reasoning.
- It may be too narrow to support broad GraphRAG claims.
- ATCSCC pages are time-sensitive, so the source snapshot and retrieval date must be frozen.
- NASA ATMONTO is not the gold KG for these advisories; human-reviewed source-grounded facts remain required.
- Entity canonicalization can be brittle if NASR cycle dates and advisory dates are mixed.

### Mitigation

- Keep the primary claim narrow: ATCSCC advisory KG extraction under an ATMONTO-derived schema profile.
- Report structured-field metrics separately from semantic predicate metrics.
- Add S1b canonicalization and S4 hybrid merge/gate instead of continuing to treat S1 all-zero as a semantic baseline.
- Freeze source manifests, source hashes where feasible, NASR cycle, advisory date range, and profile version.
- Use 10-20 reviewed dev examples and 100 held-out reviewed gold items.

## PDF Source Family

Adding PDFs is recommended, but only as a separate source family.

### Recommended PDF Inputs

- FAA Pilot/Controller Glossary:
  `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/PCG_Bsc_w_Chg_1_and_2_dtd_1-22-26.pdf`
- FAA JO 7110.65BB Air Traffic Control:
  `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/7110.65BB_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf`
- NASA ATMONTO technical documentation:
  `data/papers/ntrs_ontology_selection/20170006095_nasa_air_traffic_management_ontology.pdf`

### PDF Extraction Tasks

Do not ask PDFs to produce the same event-instance facts as ATCSCC advisories. Use separate tasks:

- `term_has_definition(term, definition_text)`
- `term_has_alias(term, alias)`
- `procedure_mentions_concept(section_id, atmonto_class_or_property)`
- `document_defines_or_constrains(term, atmonto_class_or_property)`
- `source_supports_mapping(source_span, atmonto_class_or_property)`

### PDF Evaluation

Report PDF metrics separately:

- passage-level exact / normalized match;
- page and section provenance accuracy;
- evidence-span containment;
- term-to-ATMONTO mapping precision;
- retrieval recall over relevant passages;
- human-reviewed accept / reject decisions.

Do not compare PDF definition extraction F1 directly against ATCSCC event extraction F1. They are different tasks.

## Minimum Executable Data Plan

### Split A: ATCSCC Event Extraction

- Source: `data/processed/nasa_atmonto/aligned/2026-05-14/atcscc_advisories.jsonl`
- Gold: `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- Dev: 10-20 reviewed records copied out of training / prompt tuning only.
- Test: existing 100 reviewed gold records, kept held out.
- Systems:
  - `S0_rule_only`
  - `S1_raw_open_llm_drift_diagnostic`
  - `S1b_open_llm_plus_canonicalization`
  - `S2_schema_slice`
  - `S3_schema_slice_validator_repair`
  - `S4_deterministic_backbone_semantic_enrichment_validator_gate`
- Metrics:
  - structured-field F1;
  - semantic-predicate macro-F1;
  - schema violation rate;
  - accepted ratio;
  - predicate/entity/enum/time canonicalization accuracy;
  - unsupported-by-span rate;
  - reject taxonomy.

### Split B: PDF Terminology / Procedure / Schema Support

- Source: 20-40 passages from PCG and JO 7110.65BB; optional 5-10 passages from NASA ATMONTO technical documentation.
- Backend comparison:
  - `pymupdf_text_legacy`
  - `hybrid_docling_pymupdf`
- Gold:
  - term definition;
  - alias;
  - source span;
  - page;
  - section;
  - ATMONTO concept/property support label.
- Metrics:
  - definition / alias extraction P/R/F1;
  - section/page correctness;
  - evidence containment;
  - mapping precision;
  - retrieval recall@k for source-support queries.

### Split C: GraphRAG / KG-RAG Evaluation

- Source graph: accepted S4 ATCSCC facts plus optional PDF support facts.
- Query types:
  - event lookup: "Which advisories affected X during interval Y?"
  - semantic filter: "Which reroutes were caused by WEATHER?"
  - evidence query: "Which source span supports this TMI status?"
  - cross-source support: "Which glossary/procedure passage supports this term mapping?"
- Metrics:
  - entity recall@k;
  - triple recall@k;
  - path recall;
  - answer faithfulness;
  - citation support;
  - answer completeness.

## Decision

The data should be expanded, not replaced.

The corrected thesis experiment should say:

> We evaluate ontology-constrained KG construction and GraphRAG on a frozen FAA ATCSCC advisory corpus, using NASA ATMONTO as an external schema/profile and validation reference. We further add a small PDF reference-text slice from FAA/NASA documents to test whether the same ontology-constrained pipeline behaves differently on semi-structured event advisories versus long-form reference prose.

This is defensible because it aligns with current SOTA data practice: short domain text / semi-structured source records are legitimate primary data, while PDFs should be a second source family with separate tasks and separate metrics.

## Sources

[1] Zhang, B. and Soh, H. (2024). [Extract, Define, Canonicalize: An LLM-based Framework for Knowledge Graph Construction](https://consensus.app/papers/extract-define-canonicalize-an-llmbased-framework-for-zhang-soh/711b33c15bfc562d9137b07050be7666/). ArXiv. Citations: 110.

[2] Cauter, Z. and Yakovets, N. (2024). [Ontology-guided Knowledge Graph Construction from Maintenance Short Texts](https://consensus.app/papers/ontologyguided-knowledge-graph-construction-from-cauter-yakovets/28494e5fc0905fc598416a17f098c8c0/). KaLLM 2024. Citations: 15.

[3] Khorshidi, S. et al. (2025). [ODKE+: Ontology-Guided Open-Domain Knowledge Extraction with LLMs](https://consensus.app/papers/odke-ontologyguided-opendomain-knowledge-extraction-khorshidi-nikfarjam/bf5f40fe4528547882c7ebbfbbd21113/). ArXiv. Citations: 1.

[4] Sun, Q. et al. (2025). [Docs2KG: A Human-LLM Collaborative Approach to Unified Knowledge Graph Construction from Heterogeneous Documents](https://consensus.app/papers/docs2kg-a-humanllm-collaborative-approach-to-unified-sun-luo/d2c7ec831d695f5fb3a02d3cd10ae6b0/). ACM Web Conference Companion. Citations: 6.

[5] Dagdelen, J. et al. (2024). [Structured information extraction from scientific text with large language models](https://consensus.app/papers/structured-information-extraction-from-scientific-text-dagdelen-dunn/075e3f5a3be0575d99f30dc34440d323/). Nature Communications. Citations: 555.

[6] Ryen, V., Soylu, A., and Roman, D. (2022). [Building Semantic Knowledge Graphs from (Semi-)Structured Data: A Review](https://consensus.app/papers/building-semantic-knowledge-graphs-from-semistructured-ryen-soylu/1320b5afd1ab58d6a3e24c91a499425e/). Future Internet. Citations: 63.

[7] Zhu, Y. et al. (2023). [LLMs for knowledge graph construction and reasoning: recent capabilities and future opportunities](https://consensus.app/papers/llms-for-knowledge-graph-construction-and-reasoning-zhu-wang/bc301ddc6b135419a9743367f3b5545c/). World Wide Web. Citations: 259.

[8] Peng, B. et al. (2024). [Graph Retrieval-Augmented Generation: A Survey](https://consensus.app/papers/graph-retrievalaugmented-generation-a-survey-peng-zhu/1b8c5362a3d3538ba1dd90f9b40178f1/). ACM Transactions on Information Systems. Citations: 381.

[9] Shahul, E. S. et al. (2023). [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://consensus.app/papers/ragas-automated-evaluation-of-retrieval-augmented-shahul-james/1e214d3a38e2558b8d6595f964842bca/). ArXiv. Citations: 636.

[10] Wu, S. et al. (2024). [STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases](https://consensus.app/papers/stark-benchmarking-llm-retrieval-on-textual-and-wu-zhao/383dfb6b2662532495cb8d747952f4cc/). ArXiv. Citations: 56.
