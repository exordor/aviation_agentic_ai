# ATCSCC Defense Deck Outline

Status: outline for the current ATCSCC thesis route, not a generated PPTX.

Deck profile: `engineering-platform`

Working title:

> Schema-Constrained Agentic KG-RAG for Evidence-Grounded FAA ATCSCC Advisory QA

## Deck Intent

The defense deck should explain a bounded research system, not sell a product.
Its purpose is to make the thesis claim auditable:

> A lightweight ATCSCC application schema can constrain advisory-event
> extraction, an agentic validator/refiner/critic loop can expose repair and
> rejection behavior, and KG-RAG can improve source-bounded grounding and
> citation diagnostics without claiming live operational decision support.

## Design System

| Element | Direction |
| --- | --- |
| Visual style | SOTA-paper figure style: clean white background, technical diagrams, compact metric tables, restrained blue/gray accents. |
| Slide rhythm | Alternate system diagrams, source examples, metric tables, and claim-boundary slides. Avoid repeated card grids. |
| Proof objects | ATCSCC advisory excerpt, schema/profile slice, agentic loop artifact contract, research-question validation matrix, extraction-to-answer result tables, failure taxonomy. |
| Typography | Academic technical deck: large claim headline, one proof object per slide, source footnote. |
| Claim boundary | Every result slide must state whether evidence is deterministic, LLM diagnostic, automated review, or human/expert review. |

## Slide Spine

| # | Slide | Role | Main claim | Proof object | Visual plan | Primary sources |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | Title and research boundary | title | The project studies retrospective ATCSCC advisory analysis, not live ATC decision support. | One-line thesis title plus boundary footer. | Clean title over a minimal pipeline strip. | `RESEARCH_OVERVIEW.md`, `RESEARCH_OVERVIEW.md` |
| 2 | Problem: advisory facts are useful but hard to trust | motivation | FAA ATCSCC advisories contain operational facts, but free-form LLM answers need schema and evidence controls. | Ground Stop / GDP advisory excerpt. | Left: raw advisory excerpt; right: extracted fields needed for QA. | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| 3 | Thesis reframing | positioning | The thesis is schema-guided event extraction plus KG-RAG evaluation, not ontology engineering. | Pressure-lowering framing table: ontology thesis vs schema-constrained KG-RAG. | Two-column contrast table. | `RESEARCH_OVERVIEW.md`, `RESEARCH_OVERVIEW.md` |
| 4 | Data source and task | data | ATCSCC is a semi-structured retrospective source family with a frozen 100-record reviewed sample. | Dataset table: 867 raw, 718 aligned, 100 formal sample, 100 reviewed gold. | Funnel from raw HTML to reviewed gold. | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| 5 | Schema/profile boundary | method | NASA ATMONTO is used as a lightweight ATCSCC application profile and validation guardrail. | Profile-size table: 18 classes, 11 object properties, 11 datatype properties, 17 constraints. | Layer diagram: full ATMONTO -> schema catalog -> ATCSCC slice -> extraction schema. | `reports/stages/atcscc_ontology_profile_overview.md` |
| 6 | Competency questions define measurable scope | method | The 12 CQs turn vague extraction into task-relative fields, metrics, and failure modes. | CQ matrix excerpt grouped by domain, event, ontology, provenance, queryability, abstention. | Compact CQ heatmap or grouped matrix. | `reports/stages/nasa_atmonto_competency_questions.md` |
| 7 | End-to-end pipeline | method | The system connects source parsing, schema-constrained extraction, agentic validation, event graph construction, retrieval, answering, and review. | Pipeline sequence from `RESEARCH_OVERVIEW.md`. | SOTA-style 5-block architecture diagram. | `RESEARCH_OVERVIEW.md`, `EXPERIMENTS.md` |
| 8 | Baselines and systems | experiment design | The evaluation compares rule, LLM, schema-constrained, repair, hybrid, and agentic systems rather than one model. | Descriptively named system table. | Horizontal system ladder with what each stage adds. | `EXPERIMENTS.md`, retrieval report listed in `ARTIFACT_INDEX.md` |
| 9 | Research-question validation matrix | evaluation design | Each question has explicit baselines, metrics, artifacts, and pass/fail criteria. | Four-row validation matrix. | Extraction, agentic validation, cross-source KG-RAG, and autonomous failure boundary. | `RESEARCH_QUESTIONS.md` |
| 10 | Extraction results and boundary | result | Schema-constrained extraction is evaluated through validity, evidence, precision/recall/F1, and profile gaps, not ontology completeness. | Formal scoring summary and rejection/profile-gap counts. | Layered metric table with claim-safe interpretation. | `reports/stages/nasa_atmonto_formal_experiment_scoring.md`, `reports/stages/nasa_atmonto_rejection_adjudication.md` |
| 11 | Agentic loop result | result | The agentic loop is auditable and diagnostic; it should not be overclaimed as autonomous ontology construction. | Live full-run diagnostic summary. | Agent roles around a fact artifact; side panel with repairs, rejections, failure categories. | Agentic evidence listed in `ARTIFACT_INDEX.md` |
| 12 | KG-RAG answer-generation result | result | KG/hybrid retrieval supports source-bounded grounding and citation diagnostics, while vector-only remains a fair baseline. | Correctness, citation precision/recall, and unsupported-claim rate. | Retrieval-mode comparison table with citation metrics. | Retrieval evidence listed in `ARTIFACT_INDEX.md` |
| 13 | Failure analysis and review boundary | result / limitation | Remaining failures are categorized, and automated diagnostics are not human or expert certification. | Failure categories plus human-review and expert-certification status. | Failure taxonomy diagram with red boundary labels. | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md` |
| 14 | SOTA positioning | related work | The contribution is methodological integration under a bounded source family. | Four-area SOTA table: schema-guided IE, KG quality, GraphRAG, multi-agent validation. | 2x2 method-positioning matrix. | `RESEARCH_OVERVIEW.md`, `reports/stages/sota_comparison_matrix.md` |
| 15 | Conclusion and defense claim | closing | The thesis is defensible as a retrospective, schema-constrained Agentic KG-RAG case study with explicit claim boundaries. | Claims preserved / claims avoided. | Two-column final claim safety slide. | `RESEARCH_OVERVIEW.md`, `reports/stages/nasa_atmonto_reviewer_defense_audit.md` |

## Appendix Slides

| # | Slide | Purpose | Source |
| ---: | --- | --- | --- |
| A1 | Detailed ATCSCC source example | Show raw advisory structure and extracted fields. | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| A2 | ATCSCC profile term list | Show classes, object properties, datatype properties, and constraints. | `reports/stages/atcscc_ontology_profile_overview.md` |
| A3 | Full CQ matrix | Preserve the 12 CQ framework for examiner questions. | `reports/stages/nasa_atmonto_competency_questions.md` |
| Full result dashboard snapshot | Provide evidence inventory and consistency checks. | Retrieval evidence listed in `ARTIFACT_INDEX.md` |
| A5 | Claim safety matrix | Give safe wording versus unsafe wording. | `RESEARCH_OVERVIEW.md` |
| A6 | Historical project boundary | Explain why old PHAK final outputs are not the current thesis narrative. | `reports/final/README.md` |

## Core Speaking Script

### Opening

This thesis studies how to build a source-bounded, evidence-grounded QA system
over FAA ATCSCC advisories. The system is not an operational ATC tool and does
not claim to build a complete aviation ontology. The research question is
whether a lightweight application schema, an agentic validation loop, and an
advisory event graph can make LLM-based advisory QA more constrained,
traceable, and auditable.

### Method Transition

ATCSCC advisories are useful because they are neither clean tables nor generic
prose. They contain typed fields, time windows, causes, route or airport
constraints, and comments. This makes them suitable for a schema-constrained
event extraction task where every accepted fact must carry source evidence.

### Result Transition

The results should be read layer by layer. Schema validity is not semantic
truth. Evidence containment is not full support. Graph retrieval is not
automatically better than vector retrieval. Automated adversarial review is not
human review. The thesis contribution is the disciplined separation of these
layers and the evidence that this separation makes the system easier to audit.

### Closing

The defensible conclusion is that schema-constrained Agentic KG-RAG is a useful
method for retrospective ATCSCC advisory analysis when claims remain
source-bounded, profile-relative, and evidence-aware. The next step would be
human answer review, external aviation expert review, or a separate
source-family transfer study, not operational deployment.

## Figures To Build Next

| Figure | Build priority | Notes |
| --- | --- | --- |
| SOTA-style 5-block pipeline | high | Should become the main defense deck architecture figure. |
| Raw advisory to event record | high | Use an actual ATCSCC advisory excerpt and annotate fields. |
| ATMONTO to ATCSCC profile slice | high | Must show why the full ontology is not used wholesale. |
| Agentic validation loop | medium | Use role labels: extractor, validator, refiner, critic. |
| Layered evaluation stack | medium | Show extraction, agentic, retrieval, answer, and review layers separately. |

## Build Rules For Future PPTX

- Do not reuse the old PHAK `aviation_graphrag_defense_deck.pptx` content
  without rewriting the claims.
- Reuse its slide-rhythm lessons only: title, motivation, pipeline, method,
  results, limitations, appendix.
- Use current ATCSCC source documents and stage reports as primary evidence.
- Keep every result slide paired with a claim-boundary note.
- Do not introduce operational aviation images that imply live ATC deployment.
