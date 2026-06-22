# Minerals 16 00050 Paper Analysis

## Material Passport

- Title: "Gold Deposit Ontology Guides Large Language Model to Transform Text
  into Knowledge Graphs for Gold Deposits"
- Authors: Jinhao Zhu, Yueying Wang, Wanying Tong, Shengmiao Li, Mingguo Wang,
  and Chengbin Wang
- Venue / year: Minerals 2026, 16, 50
- DOI / stable URL: https://doi.org/10.3390/min16010050
- Local PDF: `data/papers/minerals-16-00050-v2.pdf`
- Inspection artifacts: `tmp/pdfs/minerals_16_00050/`
- Figure gallery: `reports/stages/paper_figure_gallery.html`
- Project role: `primary_method_reference`, `evaluation_reference`,
  `figure_design_reference`
- Status: complete protocol pass on 2026-06-22

## Executive Takeaway

This paper is highly relevant as a cross-domain method reference. It gives a
full, thesis-friendly chain from domain ontology/schema design, to
schema-guided LLM extraction, to entity alignment, to graph construction, to
graph querying and model-size/cost evaluation. It should influence the ATCSCC
project's method presentation and experiment design, especially canonicalization,
evidence-linked extraction examples, and model/cost sweeps. It should not be
used as aviation evidence, and its broad ontology-completeness claims should not
be transferred to ATCSCC.

## What The Paper Actually Does

### Data And Scope

- Source data: 178 academic papers on gold deposits.
- Domain: geoscience, specifically gold deposit knowledge extraction.
- Corpus size: approximately 1.5 million words.
- Extracted KG scale: 3738 entities and 3900 semantic relationships are
  reported.
- Evaluation subset: 13 research articles were manually extracted and compared
  with LLM extraction.
- Non-scope: aviation, ATCSCC advisories, RAG answer generation, SHACL
  validation, and operational decision support.

### Method Pipeline

1. Collect a domain paper corpus.
2. Build a domain ontology / ER-style schema for gold deposits.
3. Translate ontology entities and relations into LLM prompt constraints.
4. Use the LLM to extract structured entity-relation triples from literature.
5. Consolidate triples into a table.
6. Align and normalize entities to reduce duplicated labels and isolated nodes.
7. Build and visualize the KG in Neo4j / Gephi.
8. Query the KG for deposit-centered and similarity-centered examples.
9. Compare extraction metrics and model-size / compute trade-offs.

### Ontology / Schema / KG Design

- Ontology source: geoscience domain knowledge, represented through an
  ER-style model.
- Classes / relations: 24 entity types and 10 relationship types.
- Provenance model: the paper visually links source text to extracted triples
  in Figure 3, but it does not define a machine-checkable evidence-span id or
  character-offset provenance contract.
- Validation method: manual extraction on a small evaluation subset and graph
  comparison; no formal SHACL-style constraint validation is reported.

### RAG / GraphRAG Design

- Retrieval unit: KG nodes and relations, not text chunks.
- Graph retrieval: Neo4j / Gephi graph querying and visualization.
- Vector retrieval: not part of the method.
- Generation setup: locally deployed DeepSeek-R1 distilled variants are used
  for extraction comparisons.
- Baselines: single-text extraction, multi-text extraction, manual extraction,
  and model-size comparisons. There is no vector-only RAG or GraphRAG QA
  baseline.

## Figure And Table Inventory

| Figure / table | Type | Role in paper | Relevance to this project | Caveat |
|---|---|---|---|---|
| Figure 1 | Ontology / schema graph | Shows the ore deposit knowledge model and entity relationships. | Good reference for an ATCSCC application-schema figure. | Our figure should emphasize source-observable fields and evidence boundaries rather than full domain ontology. |
| Figure 2 | Prompt design screenshot | Shows role, entity/relation definitions, constraints, and tabular output guidance. | Strong reference for schema-guided extraction prompt structure. | Do not copy chain-of-thought phrasing; use a bounded JSON/evidence contract instead. |
| Figure 3 | Source text plus extracted triples | Shows colored source text and an extracted triple table. | Strongest visual analogue for an ATCSCC advisory span-to-facts figure. | Needs explicit source ids and span offsets for our project. |
| Figure 4 | Entity alignment before/after graph | Shows fragmentation before alignment and consolidation after alignment. | Directly motivates canonicalizing airport/facility/cause/advisory-target labels. | Their alignment includes manual Excel/Gephi steps; our version should be scripted and auditable. |
| Figure 5 | Query-centered KG example | Shows a deposit-centered query result. | Useful model for an advisory-centered or airport-centered graph demo. | Visual graph readability is not correctness evidence. |
| Figure 6 | Similarity graph | Shows deposits related by shared minerals. | Can inspire related-advisory retrieval by shared cause, target, or facility. | This is a secondary feature, not the core ATCSCC experiment. |
| Figure 7 | Manual vs LLM graph comparison | Compares manual and LLM-built graphs visually. | Useful presentation form for reviewed gold vs extracted graph. | Visual overlap should not replace precision/recall and evidence checks. |
| Figure 8 | F1 vs compute curve | Shows extraction performance and normalized compute across model sizes. | Good basis for a NewAPI model/cost sweep in this project. | Requires fixed prompts, fixed corpus, and local cost/latency measurements. |
| Tables 1-2 | Entity/relation definitions | Define the schema used by prompts. | Analogue for ATCSCC profile terms and allowed predicates. | Do not imply ATCSCC schema completeness from a geoscience schema. |
| Table 3 | Extracted triples | Demonstrates structured output format. | Useful as a report table pattern for accepted ATCSCC facts. | Must add provenance and validation columns locally. |
| Table 4 | Alignment dictionary | Shows original patterns mapped to canonical forms. | Strong analogue for facility/cause canonicalization dictionaries. | Manual replacements are brittle unless versioned and tested. |
| Table 6 | Precision / recall / F1 | Compares single-text and multi-text extraction. | Useful evaluation structure for single-advisory vs context-enriched extraction. | The evaluation unit and gold construction must be clearer locally. |

## Evaluation Design

| Metric | Unit of analysis | What it supports | What it does not prove | Local analogue |
|---|---|---|---|---|
| Precision / recall / F1 | Extracted entities and relations on 13 papers | Shows extraction quality against manual extraction. | Does not prove graph QA quality or domain transfer. | Triple/record-level precision, recall, and F1 against reviewed ATCSCC records. |
| Single-text vs multi-text comparison | Extraction over one text vs aggregated texts | Supports the idea that additional context and deduplication can improve extraction. | Does not prove that arbitrary source mixing is safe. | Compare single-advisory extraction against same-day/thread/context enrichment under source-family boundaries. |
| Manual vs LLM graph comparison | Graph structure around selected deposits | Shows missed nodes and graph-coverage gaps. | Visual comparison is not a formal correctness metric. | Reviewed gold graph vs extracted ATCSCC event graph with missing/unsupported facts counted. |
| F1 vs compute curve | Model-size comparison | Supports a cost/performance selection argument. | Does not generalize to NewAPI providers without rerunning. | Fixed-sample model sweep over schema validity, evidence support, latency, and cost. |
| EW-F1 proposal | F1 multiplied by average extracted entities | Tries to account for richer extraction coverage. | Can reward verbosity and unsupported extraction. | Only adapt with penalties for unsupported facts and no-claim false positives. |

## Transferable Ideas

| Paper element | Local adaptation | Required local artifact |
|---|---|---|
| Ontology/schema-driven prompt mapping | Convert the ATCSCC application schema into explicit extraction contracts. | Prompt version file plus schema/profile version reference. |
| Source text to triple table figure | Build an ATCSCC example showing advisory text spans mapped to event facts. | `reports/stages/*_figures_analysis.md` or thesis figure source. |
| Entity alignment dictionary | Canonicalize airport, ARTCC, route/fix, cause, and initiative labels. | Versioned canonicalization table and tests. |
| Alignment before/after graph | Show reduced duplication and isolated-node count after canonicalization. | Graph-health report with before/after counts. |
| Single vs multi-text evaluation | Test whether bounded context enrichment improves extraction. | Frozen sample, prompt variants, and reviewed gold scoring. |
| F1/compute trade-off | Compare NewAPI-backed models under identical extraction conditions. | Model sweep manifest with cost, latency, schema validity, and evidence metrics. |

## Weaknesses Not To Copy

- Do not claim that a compact schema covers nearly all critical information in
  ATCSCC or aviation.
- Do not treat ontology/schema validity as semantic truth.
- Do not use graph screenshots as correctness evidence.
- Do not rely on manual Excel/Gephi cleanup without a reproducible script or
  versioned mapping file.
- Do not copy prompt instructions that ask the model to expose private
  reasoning; use concise JSON output with evidence ids instead.
- Do not use EW-F1 without penalizing over-extraction, unsupported relations,
  and false positives on no-claim fields.
- Do not hide provenance gaps. The paper itself notes that tracing and
  verifying LLM-extracted triples can be challenging; this project should make
  evidence spans a first-class artifact.

## Adaptation Plan

### Immediate

- Cite this paper as a cross-domain method reference for schema-guided KG
  extraction, not as aviation evidence.
- Add an ATCSCC "source span to structured event facts" figure to the thesis
  figure plan.
- Review whether current ATCSCC extraction outputs include enough provenance
  fields to support Figure-3-style span-to-fact reporting.
- Add or strengthen canonicalization artifacts for airport/facility/cause
  labels.
- Add a small model/cost sweep plan using NewAPI models under a fixed prompt and
  fixed reviewed sample.

### Deferred

- Implement a context-enrichment experiment: single advisory vs same-day
  advisory thread vs bounded reference enrichment.
- Add an alignment before/after graph-health panel to the dashboard.
- Compare a scripted canonicalization pass against an agentic
  validator/refiner loop.
- Explore related-advisory retrieval through shared cause, facility, route, or
  time window after the core event graph is stable.

## Claim-Safety Boundaries

- What can be cited:
  - The paper is evidence that another domain used a domain ontology/schema to
    guide LLM extraction into a KG.
  - It provides useful figure patterns for schema, prompt, source-to-triple,
    alignment, query, and cost/performance presentation.
  - It motivates entity alignment and model-size/cost evaluation as important
    components of LLM-based KG construction.
- What cannot be claimed:
  - It does not show that NASA ATMONTO or an ATCSCC schema is complete.
  - It does not validate FAA ATCSCC extraction or aviation RAG.
  - It does not prove GraphRAG superiority over vector RAG.
  - It does not prove operational suitability.
- Domain-transfer warning:
  - Gold-deposit literature is not ATCSCC advisory data. Transfer only the
    method pattern, not the domain conclusions.
- Evidence boundary:
  - Any local claim must be grounded in frozen ATCSCC artifacts, reviewed gold,
    schema validation, evidence-span checks, and local experiments.

## Follow-Up Actions

| Action | Owner / tool | Output artifact | Status |
|---|---|---|---|
| Register paper in local paper index | Codex | `data/papers/README.md` | done |
| Create PDF evidence pack | `scripts/inspect_paper_pdf.sh` | `tmp/pdfs/minerals_16_00050/` | done |
| Refresh figure gallery | `scripts/build_paper_figure_gallery.py` | ignored gallery HTML/manifest | done |
| Add curated analysis | Codex | `reports/stages/minerals_16_00050_paper_analysis.md` | done |
| Decide whether to update experiment workflow | Research planning | `docs/experiment_workflow.md` or focused stage note | pending |
| Design model/cost sweep | Experiment planning | model sweep manifest and report | pending |
