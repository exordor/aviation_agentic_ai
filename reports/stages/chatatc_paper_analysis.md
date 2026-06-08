# CHATATC Paper Analysis

## Material Passport

- Title: "CHATATC: Large Language Model-Driven Conversational Agents for
  Supporting Strategic Air Traffic Flow Management"
- Authors: Sinan Abdulhak, Wayne Hubbard, Karthik Gopalakrishnan, and
  Max Z. Li
- Venue / year: ICRAT 2024; arXiv v2, 2024
- DOI / stable URL: https://arxiv.org/abs/2402.14850
- Local PDF: `data/papers/arxiv_2402.14850_chatatc.pdf`
- Inspection artifacts: `tmp/pdfs/chatatc/`
- Figure gallery: `reports/stages/paper_figure_gallery.html`
- Project role: `background_citation`, `evaluation_reference`,
  `figure_design_reference`
- Status: complete protocol pass on 2026-06-06

## Executive Takeaway

CHATATC is the closest aviation-domain related work found so far for a
non-safety-critical LLM assistant over historical traffic flow management
records. It supports this project's practical framing: the target use case is
not passenger flight search, flight-delay prediction, or FAA decision
replacement, but evidence-backed retrieval and analysis of official operational
records. It should shape our related-work positioning and evaluation question
taxonomy, especially GDP parameter questions and failure cases such as
superlatives. It should not be treated as a KG, ontology, schema-constrained
extraction, RAG, or GraphRAG method reference.

## What The Paper Actually Does

### Data And Scope

- Source data: historical Ground Delay Program (GDP) issuances from the FAA
  Operational Information System (OIS) website.
- Data format: OIS XML entries containing raw GDP text plus parsed parameters
  such as duration and associated Airport Arrival Rates (AARs).
- Domain: strategic air traffic flow management in the US National Airspace
  System.
- Sample size: 86,842 GDP issuances spanning 146 airports from February 2000 to
  November 2023.
- Training subsets: airport-specific CHATATC instances were created for SFO and
  EWR; each instance used 500 historical GDP observations selected by largest
  amount of text.
- User scope: Traffic Managers, traffic management trainees, and adjacent FAA
  Air Traffic Organization quality-control staff.
- Non-scope: safety-critical decision making, prediction, optimization, and
  replacing Traffic Manager authority.

### Method Pipeline

1. Collect historical GDP issuances from FAA OIS and retain both raw GDP text
   and selected parsed parameters.
2. Summarize and visualize the historical GDP collection to understand duration,
   airport share, and program-rate patterns.
3. Test two LLM use modes:
   - in-prompt learning using U-M GPT / GPT-4 with a small prompt subset;
   - fine-tuning GPT-4 through Maizey using collected GDP text.
4. Create airport-specific conversational agents for SFO and EWR.
5. Query the agents with GDP-focused questions and manually inspect selected
   response correctness.
6. Add system-prompt instructions for more structured output, including key GDP
   fields such as date, start time, end time, program rate, runway
   configuration, and impacting condition.
7. Design GUI wireframes for a Traffic Manager-facing assistant.

### Ontology / Schema / KG Design

- Ontology source: none.
- Classes / relations: none formalized as an ontology, KG schema, or extraction
  schema.
- Provenance model: the examples cite raw GDP text snippets, but the paper does
  not define fact-level provenance, evidence-span links, or source-backed answer
  verification.
- Validation method: manual checking is reported for the 13 GDP entries used in
  the in-prompt experiment; no schema validation, ontology validation, or
  triple-level validation is used.

### RAG / GraphRAG Design

- Retrieval unit: not a RAG index design. The paper uses in-prompt context and
  fine-tuned custom LLM instances over raw GDP text.
- Graph retrieval: none.
- Vector retrieval: none described as a baseline.
- Generation setup: U-M GPT and Maizey-based custom LLMs, including GPT-4-based
  settings; temperature 0.2 is used in test cases, with informal comparison
  against 1.2.
- Baselines: no vector RAG, GraphRAG, hybrid RAG, rule-only extraction, or
  ontology-constrained extraction baseline.

## Figure And Table Inventory

| Figure / table | Type | Role in paper | Relevance to this project | Caveat |
|---|---|---|---|---|
| Figure 1 | Time-series line chart | Shows average GDP duration by month/year from 2010 to 2023. | Useful as an example of historical TMI parameter visualization. | It is descriptive data exploration, not LLM or RAG evaluation. |
| Figure 2 | Stacked bar chart | Shows percentage of GDPs by airport from 2010 to 2023. | Useful for motivating airport-frequency and event-distribution summaries. | It uses GDP-only data, not full ATCSCC advisory events. |
| Figure 3 | Box plots | Shows GDP rates for EWR, JFK, and LGA from 2010 to 2023. | Useful for showing parameter distributions that matter to Traffic Managers. | The paper assumes rates are nominally aircraft per hour; this is a domain-specific convention, not an extraction metric. |
| Figure 4 | GUI wireframe | Shows CHATATC home page with an explicit non-predictive-tool framing and links to weather/OIS resources. | Useful as a figure-design reference for responsible demo positioning. | It is a wireframe, not validated user-interface evidence. |
| Figure 5 | GUI wireframe / example answer | Shows a GDP answer surface with rate, delay, and scope. | Useful for demo ideas: show structured operational fields and evidence-facing context. | It is not a KG/RAG architecture and does not show provenance scoring. |
| Tables | None observed | The paper has no formal result table. | Reinforces that this is mainly a prototype and related-work anchor. | Do not infer quantitative performance from narrative examples. |

Visual inspection notes:

- `tmp/pdfs/chatatc/pages/page-4.png` contains Figures 1-3.
- `tmp/pdfs/chatatc/pages/page-7.png` contains Figures 4-5.
- `tmp/pdfs/chatatc/pages/page-5.png` and `page-6.png` contain the main query
  and response examples, including the incorrect superlative response.

## Evaluation Design

| Metric / check | Unit of analysis | What it supports | What it does not prove | Local analogue |
|---|---|---|---|---|
| Manual correctness check for 13 in-prompt GDP entries | GDP response examples | Shows GPT-4 can parse some GDP structure under narrow examples. | Does not establish general extraction precision/recall or schema reliability. | Small manually reviewed seed set for extraction debugging only, not final evaluation. |
| Narrative response inspection for fine-tuned SFO/EWR models | Individual question-answer pairs | Shows model can retrieve examples by airport, date, reason, and rate in some cases. | Does not compare against Vector RAG, GraphRAG, Hybrid RAG, or a gold answer set. | RAG evaluation questions over airport, reason, time, TMI type, and evidence source. |
| Superlative failure example | Aggregate question over many GDP records | Demonstrates difficulty with max-delay questions even when raw data contains the answer. | Does not quantify aggregate-question failure rate. | Mark aggregate/superlative questions as difficult cases requiring graph/fact-store support and explicit evaluation. |
| Temperature comparison 0.2 vs 1.2 | Model configuration | Suggests query specificity may matter more than temperature in their examples. | No statistical result is shown; do not generalize. | Keep model settings fixed in our experiments and report configuration, not broad LLM behavior claims. |
| GUI design examples | Human-facing answer surface | Shows useful operational fields and warning language. | Does not evaluate user performance or trust calibration. | Demo UI / report examples should show TMI type, location, reason, time, evidence, and non-operational warning. |

## Transferable Ideas

| Paper element | Local adaptation | Required local artifact |
|---|---|---|
| Non-safety-critical strategic TFM assistant framing | Position this project as advisory search, situational understanding, and retrospective analysis. | Boundary document and thesis related-work section. |
| GDP-focused factual questions | Include questions about airport, GDP/Ground Stop/TMI type, reason, start/end time, and rate/delay only when observable. | `reports/stages/master_project_boundary_discussion.md` and RAG evaluation question set. |
| Superlative failure case | Include aggregate and extreme-value questions as explicit hard/failure cases, not as easy headline claims. | RAG evaluation taxonomy and failure-analysis report. |
| GUI field hierarchy | Structure demo answers around event type, airport/location, reason, valid time, status/action, and source advisory. | Demo examples or report figures. |
| Explicit non-predictive warning | Keep project claims outside safety-critical, prediction, optimization, and decision authority. | Claim-safety boundary in thesis/report. |

## Weaknesses Not To Copy

- Do not rely on narrative examples as the main evaluation result.
- Do not treat fine-tuning on raw operational text as equivalent to verifiable
  retrieval or evidence-backed QA.
- Do not omit a baseline; our project needs Vector RAG, GraphRAG, and Hybrid
  RAG comparison, even if small.
- Do not blur raw answer fluency with factual correctness.
- Do not use broad historical records without provenance links from answer to
  source advisory.
- Do not use aggregate/superlative answers without a structured fact store or
  deterministic computation path.
- Do not frame the system as predictive, prescriptive, or operationally
  authoritative.

## Adaptation Plan

### Immediate

- Use CHATATC as related work showing that historical FAA traffic management
  records are a legitimate data source for LLM-assisted strategic TFM support.
- Use its user framing to justify analysts, Traffic Managers, trainees, and
  quality-control staff as plausible users, while keeping the project
  non-safety-critical.
- Add CHATATC-style factual questions to the evaluation taxonomy:
  - identify a GDP or Ground Stop by airport;
  - identify reason or impacting condition;
  - identify start/end/valid time;
  - identify program rate or delay only when present in the source text;
  - cite the source advisory.
- Add hard questions inspired by the paper's superlative failure:
  - maximum delay;
  - longest duration;
  - most frequent affected airport;
  - repeated weather-related initiatives over a period.
- Use the GUI figures only as presentation inspiration, not method evidence.

### Deferred

- Compare the project's event-fact store against GDP-specific historical data
  only if a separate GDP/OIS data pipeline is introduced later.
- Add user testing only after the extraction/RAG prototype is stable.
- Consider similar-day retrieval only as future work; it would expand the
  project beyond the current Master prototype.

## Claim-Safety Boundaries

- What can be cited:
  - CHATATC demonstrates an aviation-domain prototype for LLM-assisted
    historical GDP question answering in a non-safety-critical strategic TFM
    setting.
  - It provides useful examples of GDP questions, user groups, GUI warning
    language, and failure cases.
  - It reinforces that historical operational records can support training,
    search, summarization, and retrospective analysis.
- What cannot be claimed:
  - It does not prove that GraphRAG outperforms Vector RAG.
  - It does not evaluate ontology-constrained extraction.
  - It does not build or validate a KG.
  - It does not provide a reusable ATCSCC advisory data model.
  - It does not prove operational readiness for real-time FAA decision support.
- Domain-transfer warning:
  - The data is GDP-focused OIS XML, while this project targets broader ATCSCC
    advisory text. GDP field expectations can inspire question design, but they
    cannot define the full ATCSCC extraction schema.
- Evidence boundary:
  - Use CHATATC as a related-work and evaluation-design anchor. Use this
    project's own gold data, extraction metrics, provenance checks, and RAG
    comparisons for thesis claims.

## Follow-Up Actions

| Action | Owner / tool | Output artifact | Status |
|---|---|---|---|
| Register paper in citation inventory | Codex / `data/papers/README.md` | CHATATC entry | Done |
| Download PDF locally | Codex / `curl` | `data/papers/arxiv_2402.14850_chatatc.pdf` | Done |
| Generate evidence pack | Codex / `scripts/inspect_paper_pdf.sh` | `tmp/pdfs/chatatc/` | Done |
| Refresh figure gallery | Codex / `uv run python scripts/build_paper_figure_gallery.py` | `reports/stages/paper_figure_gallery.html` and manifest | Done |
| Visually inspect figures and method pages | Codex / page renders | Notes in this report | Done |
| Add related-work paragraph to thesis/report | Future writing pass | Report or thesis section | Pending |
| Translate evaluation inspirations into concrete question set | Future design pass | RAG evaluation questions | Pending |
