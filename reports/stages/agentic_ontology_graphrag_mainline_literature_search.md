# Agentic Ontology-Guided KG + RAG Quality Mainline Literature Search

- Date: 2026-06-01
- Search surface: academic search web pages
- Search policy: searches were run sequentially; a new query was not submitted
  until the previous search page had loaded or clearly returned no analyzable
  papers.
- Library action: six core papers were saved to the local literature review
  collection.

## Mainline

Working title:

> Agentic ontology-guided knowledge graph construction and RAG-oriented quality
> evaluation for aviation knowledge systems.

The mainline combines two research claims:

1. Ontology-guided KG construction should be implemented as an iterative,
   role-separated process rather than as one-pass LLM extraction.
2. KG quality should be evaluated through downstream RAG usefulness:
   provenance, graph evidence coverage, answer support, and abstention behavior,
   not only through isolated ontology/KG purity metrics.

This matches the current project because `aviation_agentic_ai` already has:

- NASA ATMONTO / ATCSCC schema-slice work;
- reviewed ATCSCC gold records;
- S0/S1/S1b/S2/S3/S4 extraction system comparisons;
- validator-gated fact acceptance and rejection analysis;
- GraphRAG-style retrieval and layered evaluation reports.

## Search Log

| # | Query purpose | Search page | Result |
| ---: | --- | --- | --- |
| 1 | Agentic ontology-guided KG construction | [Agentic Ontology Knowledge Graph](https://consensus.app/search/agentic-ontology-knowledge-graph/5AaPumUUS7qw2QPOcik3ew/) | 7 paper links |
| 2 | Ontology-guided information extraction and validation | [Ontology Guided Information Extraction](https://consensus.app/search/ontology-guided-information-extraction/oab-Z6WSRyuMuS1v2G1m1Q/) | 9 paper links |
| 3 | KG quality with faithfulness/completeness/provenance wording | [Knowledge Graph Quality Evaluation](https://consensus.app/search/knowledge-graph-quality-evaluation/QfguZmlRRQOXepKxwfIN5g/) | Too narrow; no papers found |
| 4 | KG-RAG evaluation benchmark wording | [Knowledge Graph Retrieval Evaluation](https://consensus.app/search/knowledge-graph-retrieval-evaluation/rwwnhOiJT3GC2EhwcfTWSg/) | Too narrow; no papers found |
| 5 | GraphRAG QA wording | [Graph Enhanced Retrieval Generation](https://consensus.app/search/graph-enhanced-retrieval-generation/UCillFJZQDmgBiRu1AHBnQ/) | Too narrow; no papers found |
| 6 | Document GraphRAG and KG-enhanced RAG | [Knowledge Graph Enhanced Retrieval](https://consensus.app/search/knowledge-graph-enhanced-retrieval/1nRbryntTFuI9BuUwrWPpg/) | 16 paper links |
| 7 | Aviation ontology/KG/RAG | [Aviation Ontology Knowledge Graph](https://consensus.app/search/aviation-ontology-knowledge-graph/GAw3Gn1ESfyvChjh4pxzYQ/) | 9 paper links; aviation-specific evidence still emerging |
| 8 | ATMONTO, AIRM-O, and aviation ontology baselines | [Aviation Ontology Knowledge Graph](https://consensus.app/search/aviation-ontology-knowledge-graph/KtxCf1GASjq8g0jhlL1alw/) | 16 paper links |

## Papers Saved To The Literature Collection

These papers were saved to `My Library` and added to the `Literature Review`
collection. The final UI evidence showed the collection at `6 items`.

| # | Paper | Why it matters |
| ---: | --- | --- |
| 1 | [LLM-empowered knowledge graph construction: A survey](https://consensus.app/papers/llmempowered-knowledge-graph-construction-a-survey-bian/dfbcfc9b12ba50659e7f8a8fabdfa034/) | Current survey framing for ontology engineering, extraction, fusion, and dynamic memory in LLM-based KG construction. |
| 2 | [Text2KGBench: A Benchmark for Ontology-Driven Knowledge Graph Generation from Text](https://consensus.app/papers/text2kgbench-a-benchmark-for-ontologydriven-knowledge-mihindukulasooriya-tiwari/b24be0d0ff9f52eebfa7a23833492952/) | Direct benchmark precedent for ontology-driven KG generation from text. |
| 3 | [OntoLogX: Ontology-Guided Knowledge Graph Extraction from Cybersecurity Logs with Large Language Models](https://consensus.app/papers/ontologx-ontologyguided-knowledge-graph-extraction-from-cotti-drago/62e38f951eba5102986a31c198d42f62/) | Strong analog for ontology-guided extraction from domain-specific semi-structured text. |
| 4 | [Graph Retrieval-Augmented Generation: A Survey](https://consensus.app/papers/graph-retrievalaugmented-generation-a-survey-peng-zhu/1b8c5362a3d3538ba1dd90f9b40178f1/) | Baseline survey for GraphRAG mechanisms and evaluation language. |
| 5 | [Document GraphRAG: Knowledge Graph Enhanced Retrieval Augmented Generation for Document Question Answering Within the Manufacturing Domain](https://consensus.app/papers/document-graphrag-knowledge-graph-enhanced-retrieval-knollmeyer-caymazer/78d009e01f925a00811cd33cbc74f60d/) | Closest document-QA analog: KG-enhanced RAG over technical documents. |
| 6 | [Matching Ontologies for Air Traffic Management: a Comparison and Reference Alignment of the AIRM and NASA ATM Ontologies](https://consensus.app/papers/matching-ontologies-for-air-traffic-management-a-vennesland-keller/01af37df362c50a698821ec2fbba7aeb/) | Direct aviation ontology baseline connecting AIRM and NASA ATM ontology alignment. |

## Additional High-Value Papers From The Searches

### Agentic and ontology-guided KG construction

- [Clinical Knowledge Graph Construction and Evaluation](https://consensus.app/papers/clinical-knowledge-graph-construction-and-evaluation-das-atmakuri/61cff97314005507b472d425f81012b2/)
  surfaced as a role-separated, schema-guided, adversarial-validation analog.
- [Ontology-grounded automatic knowledge graph construction](https://consensus.app/papers/ontologygrounded-automatic-knowledge-graph-feng-wu/c9777514924d5ff581b025bc2d54f1da/)
  supports the "ontology as extraction constraint" argument.
- [From Human Experts to Machines](https://consensus.app/papers/from-human-experts-to-machines-an-llm-supported-approach-to-kommineni-knig-ries/57f213fdb33c53609cd26604814de6b3/)
  supports competency-question and expert-knowledge transfer framing.
- [Ontology-grounded Knowledge Graphs for Mitigating Hallucinations](https://consensus.app/papers/ontologygrounded-knowledge-graphs-for-mitigating-ali-taha/d7c871f2bb3857439c1bfa563bebf37a/)
  is relevant for hallucination control and evidence grounding.

### RAG-oriented KG quality and GraphRAG

- [K-RAG: Knowledge-enhanced Retrieval-Augmented Generation](https://consensus.app/papers/kerag-knowledgeenhanced-retrievalaugmented-generation-sun-sun/0b98b2d23b9352db8370d39aa40a1363/)
  supports KG-enhanced RAG mechanism comparison.
- [LightRAG](https://consensus.app/papers/lightrag-simple-and-fast-retrievalaugmented-generation-guo-xia/a183192658da576aa0258cc463efda26/)
  is relevant as an efficiency-oriented GraphRAG baseline.
- [StructuGraphRAG](https://consensus.app/papers/structugraphrag-structured-documentinformed-knowledge-zhu-guo/6887cecc8ea85a26a080ce77d24905eb/)
  supports structured-document-informed KG/RAG design.
- [HybridRAG](https://consensus.app/papers/hybridrag-integrating-knowledge-graphs-and-vector-sarmah-mehta/731a8e846c0c59da9aef7951b67f7b2b/)
  is directly relevant to the current vector + graph hybrid evaluation pattern.
- [Knowledge graph-guided retrieval augmented generation](https://consensus.app/papers/knowledge-graphguided-retrieval-augmented-generation-zhu-xie/ec4b4f57474d5fb59e2e7bcff8eb0862/)
  supports graph-guided retrieval and grounding language.

### Aviation-specific leads

- [A Retrieval-Augmented Generation Method for Question Answering](https://consensus.app/papers/a-retrievalaugmented-generation-method-for-question-zheng-shen/edb1f1a3d02a50d78d7599ba634b83c2/)
  and related civil/aviation RAG papers support domain QA positioning.
- [OG-RAG: Ontology-grounded Retrieval-Augmented Generation](https://consensus.app/papers/ograg-ontologygrounded-retrievalaugmented-generation-sharma-kumar/8ca054be10465990aa43e529002fd029/)
  is important for the exact "ontology-grounded RAG" phrase.
- [Creating an ATC Knowledge Graph in Support of the SESAR Digital Academy](https://consensus.app/papers/creating-an-atc-knowledge-graph-in-support-of-the-schrefl-neumayr/6fdf942ccc745db2a46c4490e2ddadc8/)
  is a strong aviation/ATC KG lead.
- [Ontology-driven Digital Twin Framework for Aviation Infrastructure](https://consensus.app/papers/ontologydriven-digital-twin-framework-for-aviation-kabashkin/cae797fca2f350d88a4bae83fda3a268/)
  is useful only if the thesis discussion needs a bridge to digital twin topics.

## Search Lessons

The main useful terminology is:

- `ontology-guided knowledge graph construction`
- `ontology-driven knowledge graph generation from text`
- `GraphRAG`
- `knowledge graph enhanced retrieval augmented generation`
- `ontology-grounded RAG`
- `aviation ontology knowledge graph`
- `AIRM NASA ATM ontology alignment`

The overly narrow phrasing
`faithfulness completeness correctness provenance` returned no papers in the
search run. Those are still useful evaluation dimensions, but they should be
introduced in the thesis as evaluation metrics rather than as the primary search
query phrase.

## Literature Positioning

### What the literature supports

The literature supports an architecture where LLMs are KG construction support
modules, not final authorities. Ontologies define admissible types and
relations; LLMs extract, canonicalize, or enrich candidate facts; validators
gate the output; and downstream RAG evaluation checks whether the resulting KG
actually helps retrieval, evidence support, or answer grounding.

### What is still open

There is room for a thesis contribution because the exact combination remains
underexplored:

- aviation-specific ontology-guided KG construction;
- iterative agentic extraction/validation/repair;
- ATMONTO/AIRM-style ontology boundary management;
- RAG-oriented KG quality metrics;
- evidence sufficiency and abstention for aviation learning questions.

### Claim boundary

The thesis should not claim that GraphRAG universally improves Recall@k or that
the system is operationally safe for aviation decisions. The defensible claim is
narrower: ontology-guided KG construction can improve traceable structured
evidence, validation quality, and evaluation transparency for scoped aviation
knowledge tasks.

## Proposed Thesis Framing

### Research question

How can an agentic, ontology-guided construction loop improve aviation knowledge
graph quality, and how should that quality be evaluated for RAG-oriented
question answering?

### Subquestions

1. How should extractor, canonicalizer, validator, repairer, and critic roles be
   separated in an ontology-guided KG construction loop?
2. Which ontology/KG quality dimensions best predict RAG usefulness: schema
   conformance, provenance completeness, semantic correctness, relation
   completeness, graph-path support, or answer citation support?
3. Does a hybrid deterministic backbone plus LLM semantic enrichment outperform
   pure LLM extraction for aviation event/advisory KG construction?
4. How well do aviation ontology baselines such as ATMONTO and AIRM-O support
   the schema boundaries needed for KG construction and evaluation?
5. Which failure modes are specific to aviation knowledge systems: source
   insufficiency, ontology gaps, unsupported facts, or retrieval dilution?

### Primary experiment spine

1. Use the existing ATCSCC reviewed gold set as the KG-construction benchmark.
2. Compare S0, S1b, S2, S3, and S4 as construction systems.
3. Report structural acceptance, schema violations, accepted facts, rejected
   facts, semantic precision/recall/F1, repair success, and bootstrap
   confidence intervals.
4. Map rejected facts into extractor bug, ontology/profile gap, source
   ambiguity, and manual-review-only categories.
5. Connect KG quality to RAG-oriented metrics using current retrieval, graph
   path, citation, and sufficiency reports.

### Secondary extension

Use PDF/reference documents as a second source family only after the primary
ATCSCC event-extraction story is stable. Keep source families in separate metric
tables.

## Meeting Pitch

> I propose combining the professor's agentic ontology-construction topic with
> the KG-quality-for-RAG topic. I already have a working aviation KG/RAG system
> with ATMONTO/ATCSCC schema constraints, reviewed gold records, validator-gated
> facts, and layered RAG metrics. The thesis can contribute an agentic
> ontology-guided construction loop and an evaluation protocol that measures KG
> quality by downstream evidence usefulness rather than by ontology purity alone.

## Immediate Follow-Up

1. Read the six saved Library papers first.
2. Decide whether the thesis title should emphasize `agentic ontology
   construction`, `KG quality evaluation`, or `aviation GraphRAG`.
3. Prepare a one-page proposal with the research question, hypotheses, current
   artifacts, and missing experiments.
4. Add 2-3 more aviation-specific papers after manually inspecting the ATC and
   civil aviation RAG leads.
