# Aviation Agentic AI

Aviation Agentic AI is a research prototype for schema-constrained,
evidence-grounded Agentic KG-RAG over retrospective FAA ATCSCC advisories. It
extracts advisory-event facts from semi-structured FAA traffic-management
notices, validates them against a lightweight NASA ATMONTO-derived application
schema, and evaluates whether an advisory event graph improves source-bounded
question answering and citation quality.

The project focuses on a practical research question: can LLM extraction,
agentic validation/refinement, and KG-RAG retrieval produce valid,
evidence-linked answers over ATCSCC advisories without overclaiming ontology
completeness, human review, or operational ATC decision support?

The current thesis framing does not assume that GraphRAG universally improves
Recall@k over vector-only RAG. It evaluates a narrower claim:
schema-constrained KG-RAG can add inspectable advisory-event evidence,
source-grounded citations, and failure-boundary diagnostics, with each metric
layer reported separately.

## What This Project Demonstrates

- **Schema-constrained advisory event extraction** from retrospective FAA
  ATCSCC advisories.
- **Agentic validation/refinement diagnostics** using extractor, validator,
  refiner, and critic artifacts.
- **Evidence-linked advisory event graphs** with source IDs and evidence spans.
- **Vector, graph, hybrid, and routed KG-RAG evaluation** over source-bounded
  competency-question labels.
- **Layered evaluation and claim safety review** for schema validity, evidence
  support, retrieval quality, answer quality, and human-review boundaries.
- **Submission-friendly project hygiene** with curated assets, third-party
  attribution, and generated artifacts kept under control.

## Current Prototype

The current implementation centers on a 100-record reviewed ATCSCC advisory
experiment, S0-S4 extraction baselines, S5/S6 agentic validation diagnostics,
and S7 retrieval/answer-generation diagnostics. NASA ATMONTO is used as a
reference vocabulary and lightweight schema/profile backbone, not as a complete
aviation ontology or as the thesis object.

Primary current assets:

- Research mainline: `RESEARCH_OVERVIEW.md`
- Documentation map: `ARTIFACT_INDEX.md`
- Thesis positioning: `RESEARCH_OVERVIEW.md`
- Experiment workflow: `EXPERIMENTS.md`
- Formal ATCSCC protocol: `EXPERIMENTS.md`
- ATCSCC data processing flow:
  `reports/stages/atcscc_data_format_and_processing_flow.md`
- ATCSCC schema/profile overview:
  `reports/stages/atcscc_ontology_profile_overview.md`
- Formal extraction scoring:
  `reports/stages/nasa_atmonto_formal_experiment_scoring.md`
- Thesis dashboard: `reports/stages/nasa_atmonto_s7_retrieval.md`

Historical PHAK/PDF ontology, chunking, KG, and web-demo artifacts remain in the
repository as background evidence and legacy prototype material. They are not
the current thesis entry point.

## Current Thesis Pipeline

```text
FAA ATCSCC advisories
  -> source snapshot and advisory parser
  -> lightweight ATCSCC application schema/profile
  -> S0-S4 extraction baselines
  -> extractor / validator / refiner / critic loop
  -> advisory event graph with evidence spans
  -> vector / graph / hybrid / routed KG-RAG
  -> answer generation, citation checks, and failure review
```

The project is CLI-first so every stage can be reproduced and evaluated before a
service or user interface is added. Use `ARTIFACT_INDEX.md` to find the
current canonical reports.

## Project Layout

```text
configs/                 Reproducible project and extraction settings
data/raw/                Source snapshots, including ATCSCC advisory HTML
data/papers/             Related research papers and reading notes
data/ontology/           NASA ATMONTO references, profiles, and legacy ontology artifacts
data/kg/                 KG/ABox and evidence-graph artifacts
reports/                 Stage and final research reports
templates/               Reusable report templates for research workflows
src/aviation_agentic_ai/ Project package and CLI implementation
tests/                   Unit and integration tests
```

Report directories are intentionally separated:

- `reports/stages/`: current dashboard entrypoints such as `index.md` and
  `index.json`
- `reports/archive/`: archived stage artifacts and run evidence
- `reports/final/`: final deliverables such as `project_report.md`

## Quick Start

```bash
cd aviation_agentic_ai
uv sync --extra dev --extra graphrag
uv run aviation-ai --help
uv run aviation-ai report thesis-claims
uv run aviation-ai report nasa-atmonto-answer-generation
uv run python scripts/build_nasa_atmonto_reviewer_defense_audit.py
uv run ruff check .
uv run pytest -q
```

Without `uv`:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
aviation-ai --help
```

## CLI

```bash
aviation-ai --help
aviation-ai report thesis-claims
aviation-ai report nasa-atmonto-answer-generation
aviation-ai report stages
aviation-ai ontology validate
aviation-ai ontology report
aviation-ai ontology scope
aviation-ai ontology evaluate
aviation-ai ontology evaluate --generated --report-name generated_ontology_evaluation
aviation-ai ontology validate-cqs
aviation-ai ontology cqs --dry-run --max-pages 1
aviation-ai ontology generate --dry-run --artifact-dir reports/stages/generation_runs/dry-run-seed
aviation-ai cqs validate-benchmark
aviation-ai chunk build
aviation-ai source ingest-nasa
aviation-ai kg extract --dry-run
aviation-ai kg validate
aviation-ai index build
aviation-ai query "How does angle of attack affect lift?"
aviation-ai report hybrid-rag --max-questions 1
aviation-ai report chunking-comparison --max-questions 1
aviation-ai report benchmark-v2
aviation-ai report benchmark-reviewed-subset
aviation-ai report graph-traversal-ablation
aviation-ai report sufficiency-eval
aviation-ai report triple-semantic-review
aviation-ai report answer-eval-subset
aviation-ai report web-demo-readiness
aviation-ai report web-demo-smoke
aviation-ai report final-evaluation
aviation-ai report thesis-claims
aviation-ai report evaluation-protocol
aviation-ai report nasa-source-discovery
aviation-ai report nasa-source-validation
aviation-ai report nasa-chunking-summary
aviation-ai report ontology-boundary-nasa
aviation-ai report nasa-kg-validation
aviation-ai report nasa-benchmark-summary
aviation-ai report cross-source-ontology-validation
aviation-ai report multisource-retrieval-smoke
aviation-ai report pdf-extraction-comparison
aviation-ai report pdf-backend-chunking-comparison
aviation-ai report retrieval-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name retrieval_ablation_benchmark_v2
aviation-ai report graph-traversal-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name graph_traversal_ablation_benchmark_v2
aviation-ai web serve
aviation-ai report hygiene --dry-run
aviation-ai report project --no-ai
```

Additional stage-report aggregation is available with:

```bash
aviation-ai report stages
```

## Current Research Direction

The current research direction is defined in `RESEARCH_OVERVIEW.md`:

> Agentic KG-RAG for evidence-grounded question answering over retrospective
> FAA ATCSCC advisories.

The project now treats ontology/schema material as a lightweight engineering
constraint. The thesis contribution is the end-to-end method: source-bounded
advisory parsing, schema-constrained extraction, agentic validation/refinement,
evidence-linked event graph construction, KG-RAG retrieval, answer generation,
and failure-boundary evaluation.

The paper-analysis workflow remains important, but it is used to transfer
methods, evaluation designs, and figure/report conventions into this ATCSCC
pipeline. It does not turn external paper datasets into direct evidence for
ATCSCC extraction correctness.

## Legacy PHAK And PDF Prototype Notes

The older PHAK/PDF ontology and GraphRAG pipeline remains useful as engineering
background. It should be cited as a prior prototype, not as the current thesis
mainline.

The ontology-generation code was adapted from the open-source implementation
associated with the paper in
`data/papers/towards-automated-ontology-generation-multi-agent-llm.pdf`. The
upstream implementation is
`https://github.com/brains-group/towards_automated_ontology_generation`. Source
PDF text was converted into ontology-focused Competency Questions, then a
model-assisted pipeline turned those CQs into validated Semantic Requirements
Document and Technical Implementation Plan JSON artifacts, then Turtle ontology
output. Per-run manifests and page checkpoints are written when an artifact
directory is supplied. The baseline ontology is not treated as final.

The legacy focused ABox extraction design used `configs/extraction_profile.yaml`
to define a small set of high-value aviation classes and relations. Each
extracted triple carries source provenance so GraphRAG answers can cite the text
that supports them.

## Legacy Chunking Comparison

The chunking comparison experiment evaluates how document splitting affects
vector retrieval quality in the earlier PHAK/PDF prototype. The original report
is a 10-CQ pilot over PHAK Chapter 4 boundary CQs. It compares:

- `fixed_window`: character window baseline with overlap
- `sentence_recursive`: paragraph/sentence-aware merging
- `structure_aware`: page and section/list boundary-aware chunks
- `semantic_meta_like`: lightweight Meta-Chunking-style semantic boundary approximation

Run after installing the optional GraphRAG dependencies:

```bash
uv sync --extra dev --extra graphrag
uv run aviation-ai report chunking-comparison
```

The command writes `reports/stages/chunking_comparison.json` and `.md` with a
run manifest, rebuild policy, collection names, chunking strategy metadata,
page/chunk/span gold-label level, Recall@5, MRR@5, Context Precision@5,
chunk-size statistics, boundary preservation rates, and per-strategy
explanations.

The thesis-scale chunking comparison is intentionally separate so it does not
overwrite the pilot report or slow the default thesis workflow:

```bash
uv run aviation-ai report chunking-comparison-v2
uv run aviation-ai report chunking-comparison-v2 --evaluation-mode fixed_context_budget
uv run aviation-ai report chunking-implementation-audit
uv run aviation-ai report chunking-topk-sensitivity-v2
uv run aviation-ai report chunking-category-analysis-v2
uv run aviation-ai report pdf-extraction-comparison
uv run aviation-ai report pdf-backend-chunking-comparison
```

This legacy command evaluates mainstream chunking families on benchmark v2 and writes
`reports/stages/chunking_comparison_benchmark_v2.json`, `.md`,
`reports/stages/chunking_failure_cards_benchmark_v2.json`, and `.md`. It reports
supported-only retrieval metrics, insufficient-evidence diagnostics, chunk-size
sensitivity, category-level results, confidence intervals, and qualitative
failure cards. The fixed-budget mode writes
`reports/stages/chunking_comparison_benchmark_v2_budget.json` and `.md`; the
independent hardening commands write implementation-audit, top-k sensitivity, and
category-analysis reports. These commands are not included in `thesis-all` or
the default thesis report generation targets by design. The protocol is
documented in `docs/archive/phak_era/chunking_experiment_protocol.md`.

PDF extraction is evaluated separately from chunking. The recommended candidate
backend for structure-aware PDF chunking is `hybrid_docling_pymupdf`: Docling
supplies section/table/list structure while PyMuPDF supplies fast text-fidelity
comparison and conservative text repair. The legacy PyMuPDF heading heuristic
remains available only as a baseline. This policy is documented in
`docs/archive/phak_era/pdf_extraction_backend_policy.md`; the commands above write
`reports/stages/pdf_extraction_comparison.*`,
`reports/stages/pdf_hybrid_repair_report.*`, and
`reports/stages/pdf_backend_chunking_comparison.*`.

## Legacy PHAK Hybrid RAG Experiment

The older PHAK Chapter 4 Hybrid RAG experiment builds a reproducible retrieval
and grounded-answering loop:

```text
PDF -> chunks -> focused KG triples -> ChromaDB chunk index
    -> graph/vector/hybrid retrieval -> LLM answer with citations
```

Run the full experiment after installing the optional GraphRAG and LLM
dependencies and configuring a local `.env` provider:

```bash
uv sync --extra dev --extra graphrag --extra ontology-generation
uv run aviation-ai chunk build
uv run aviation-ai kg extract
uv run aviation-ai kg validate
uv run aviation-ai index build
uv run aviation-ai query "How does angle of attack affect lift?" --mode hybrid
uv run aviation-ai report hybrid-rag
```

For the local NewAPI relay, keep secrets in the ignored `.env` file:

```dotenv
LLM_PROVIDER=newapi
MODEL_NAME=glm-5.2
NEWAPI_BASE_URL=http://localhost:3000
NEWAPI_API_KEY=<your-newapi-key>
```

`NEWAPI_BASE_URL` may be either the service host or the OpenAI-compatible `/v1`
base URL; the provider normalizes `http://localhost:3000` to
`http://localhost:3000/v1`.

For the sub2api relay (Codex-subscription-backed GPT-5 models), use the
`sub2api` provider:

```dotenv
LLM_PROVIDER=sub2api
MODEL_NAME=gpt-5.5
SUB2API_BASE_URL=http://127.0.0.1:8080
SUB2API_API_KEY=<your-sub2api-key>
```

sub2api speaks the OpenAI Responses API and converts `/v1/chat/completions`
calls to `/v1/responses` internally, so the existing chat-completions code path
(including tool calling) works without a custom adapter. `SUB2API_BASE_URL` is
normalized the same way as `NEWAPI_BASE_URL`.

Hybrid reports keep retrieval, KG evidence, and LLM answer metrics separate.
They also record the LLM provider/model name, Chroma collection, chunking
strategy, graph/vector top-k settings, and whether chunks/indexes/KG were
rebuilt for that report run. Reviewed gold labels live at
`data/cqs/06_phak_ch4_0.gold.json`; they use chunk/span evidence for all 10
boundary CQs while remaining course-project labels rather than external aviation
examiner certification. The final evaluation command summarizes strategy
selection, failure cases, and citation completeness without producing a mixed
overall score:

```bash
uv run aviation-ai report evidence-eval
uv run aviation-ai report graphrag-review
uv run aviation-ai report final-evaluation
uv run aviation-ai report thesis-claims
uv run aviation-ai report evaluation-protocol
uv run aviation-ai report benchmark-v2
uv run aviation-ai report benchmark-review-pack --no-write-reviewed
uv run aviation-ai report benchmark-reviewed-subset
uv run aviation-ai report answer-eval-subset
uv run aviation-ai report benchmark-llm-review --max-items 60
uv run aviation-ai report benchmark-llm-rewrite-proposals
uv run aviation-ai report triple-semantic-llm-review --max-items 50
uv run aviation-ai report graph-path-llm-review --max-items 50
uv run aviation-ai report answer-generation-benchmark-subset --max-questions 45
uv run aviation-ai report answer-llm-judge --max-items 60
uv run aviation-ai report llm-review-consistency
uv run aviation-ai report retrieval-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name retrieval_ablation_benchmark_v2
uv run aviation-ai report graph-traversal-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name graph_traversal_ablation_benchmark_v2
uv run aviation-ai report sufficiency-eval --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json
uv run aviation-ai report triple-semantic-review --sample-size 100
uv run aviation-ai report answer-eval --gold-labels data/cqs/06_phak_ch4_0.answer_eval_subset.gold.json --report-name answer_evaluation_benchmark_subset
```

The evaluation protocol is documented in `EXPERIMENTS.md`. It maps
mainstream RAGAS-style, ARES-style, IR, GraphRAG, ontology/KG, and aviation
safety metrics to this project. The project reports layered metrics and does not
claim or compute a single mixed overall score.

Model-based review is documented in `docs/llm_review_protocol.md`. LLM review
uses the configured `MODEL_NAME` as `reviewer_model`; it is not human review,
not expert gold, and not external aviation certification. If LLM dependencies or
credentials are unavailable, the review commands write explicit `not_run`
statuses instead of fabricating review results.

## NASA Source Expansion

NASA Glenn Beginners Guide to Aeronautics is supported as a second authoritative
educational source corpus. The landing-page catalog is collected broadly, while
the current experiment uses only the `Lessons in Aerodynamics` subset for
ontology boundary, chunking, KG, seed benchmark, and FAA/NASA source-routing
diagnostics. This is source-diversity evidence only; it does not add operational
flight readiness or external aviation certification.

```bash
uv run aviation-ai report nasa-source-discovery
uv run aviation-ai source ingest-nasa
uv run aviation-ai report nasa-source-validation
uv run aviation-ai report nasa-chunking-summary --no-semantic-download
uv run aviation-ai report ontology-boundary-nasa
uv run aviation-ai kg extract --chunks data/chunks/nasa_bga_aerodynamics.structure_aware_large.jsonl --output data/kg/nasa_bga_aerodynamics.structure_aware_large.kg.jsonl --ttl-output data/kg/nasa_bga_aerodynamics.structure_aware_large.kg.ttl --dry-run
uv run aviation-ai report nasa-kg-validation
uv run aviation-ai report nasa-benchmark-summary
uv run aviation-ai report cross-source-ontology-validation
uv run aviation-ai report multisource-retrieval-smoke
```

The tracked manifest is
`data/sources/nasa_bga_aerodynamics_sources.yaml`. Discovery and validation
reports keep full-corpus collection separate from the experiment subset so the
reports do not overclaim a small subset as the full NASA landing-page corpus.

## Thesis Experiment Workflow

Start with `RESEARCH_AUDIT.md` and `RESEARCH_OVERVIEW.md`. The
current thesis route is **schema-constrained Agentic KG-RAG over retrospective
FAA ATCSCC advisories**, not a general aviation ontology thesis. The canonical
experiment workflow is documented in `EXPERIMENTS.md`; it connects
the four research questions, source scope, extraction baselines, agentic
validation/refinement, KG-RAG retrieval, answer-generation diagnostics, failure
analysis, and claim boundaries.

Use the Makefile targets for deterministic legacy workflow pieces where they
still apply. The current ATCSCC thesis reports are generated through the
ATMONTO/ATCSCC report commands and scripts below.

```bash
uv sync --extra dev --extra graphrag
make validate
uv run aviation-ai cqs validate-benchmark --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json
make reports-core
make reports-main-experiments
make reports-review
uv run aviation-ai report thesis-claims
uv run aviation-ai report nasa-atmonto-answer-generation
uv run python scripts/build_nasa_atmonto_sota_goal_audit.py
uv run python scripts/build_nasa_atmonto_reviewer_defense_audit.py
uv run aviation-ai report project --no-ai
uv run aviation-ai report academic-paper --no-ai
```

The dashboard command writes `reports/stages/nasa_atmonto_s7_retrieval.json`
and `.md`. It aggregates existing reports into an experiment inventory,
RQ-to-evidence matrix, dataset usage matrix, primary results table,
failure-mode summary, and thesis-ready claim summary. It does not recompute
experiments, fabricate human review results, or produce a mixed overall score.
`all_passed=false` can be expected while model-based benchmark, triple, answer,
or path review remains pending; automated consistency is reported separately.

## Research Paper Analysis Protocol

External papers should not shape the thesis route from abstracts alone. The
default workflow is documented in `docs/research_paper_analysis_protocol.md`:

```bash
scripts/inspect_paper_pdf.sh data/papers/example.pdf example_paper
```

This creates ignored PDF evidence artifacts under `tmp/pdfs/example_paper/`.
Curated paper analysis should then be written under `reports/stages/` using
`templates/research_paper_analysis_report.md`. A paper is project-usable only
after the report covers full-text methods, figure/table design, metrics,
limitations, transferable ideas, and claim-safety boundaries.

## Thesis Positioning And Claim Safety

The thesis positioning document is `RESEARCH_OVERVIEW.md`. It records the
revised claim, research questions, hypotheses, claim safety matrix, and evidence
gaps before thesis submission. Generate the deterministic claim review with:

```bash
uv run aviation-ai report thesis-claims
```

The command writes `reports/stages/thesis_claims_review.json` and `.md`. It
summarizes which claims are currently strong, moderate, weak, or not supported;
lists evidence files for each claim; scans final report files for unsafe
overclaims; and keeps the course-project / thesis-oriented benchmark boundary
explicit.

For local smoke tests without an LLM call, use deterministic seed triples:

```bash
uv run aviation-ai chunk build --max-pages 1 --output tmp/smoke-chunks.jsonl
uv run aviation-ai kg extract --chunks tmp/smoke-chunks.jsonl --output tmp/smoke-kg.jsonl --dry-run
uv run aviation-ai kg validate --chunks tmp/smoke-chunks.jsonl --kg-file tmp/smoke-kg.jsonl
```

## Web Demo

The local web demo is an offline-first FastAPI dashboard for reviewing the
GraphRAG pipeline evidence. The UI follows a macOS-style utility layout with a
sidebar question list, compact toolbar controls, an answer workspace, and
separate chunk/KG evidence inspectors. It also includes a question-scoped KG
relationship graph that visualizes the retrieved triples for the selected CQ,
strategy, and retrieval mode. The top explanation panels summarize the pipeline,
compare vector/graph/hybrid modes, and explain why the current result is
supported. By default it reads committed reports, KG artifacts, gold labels, and
Hybrid RAG outputs instead of calling the LLM. This keeps the review demo
reproducible and lets a reviewer inspect answers, retrieved chunks, KG triples,
citations, evidence-level metrics, structured relationships, and the advisory
boundary from a browser.

Install the optional web dependencies and run the readiness check:

```bash
uv sync --extra dev --extra graphrag --extra web
uv run aviation-ai report web-demo-readiness
uv run aviation-ai report web-demo-smoke
uv run aviation-ai web serve
```

Then open `http://127.0.0.1:8000`. The default displayed strategy is
`structure_aware`; `fixed_window` remains visible as the baseline comparison.
The smoke report writes `reports/stages/web_demo_final_smoke.md` and verifies
the static page, status/explanation/question APIs, detail endpoint, KG graph,
live-query readiness lockout, and favicon through FastAPI TestClient.

Live LLM querying is auto-detected. The query box is enabled only when the
Chroma collection, optional GraphRAG/LLM dependencies, and LLM provider
environment are configured. To force the live GraphRAG path after setup, start
the server with:

```bash
uv run aviation-ai web serve --enable-live-query
```

To force the review demo to remain offline, use `--disable-live-query`.

The web demo is for aviation learning and decision support only. It does not
replace the aircraft POH, approved checklists, ATC instructions, instructor
guidance, or pilot judgment.

## Development Notes

External projects are used as references or optional dependencies, not vendored
repositories. See `THIRD_PARTY.md` for attribution and integration policy.

Before submitting or handing off changes:

```bash
uv run ruff check .
uv run pytest
```

## Ontology Evaluation

CQ artifacts are strict normalized JSON inputs. Each CQ must include a stable
`id`, source document/page metadata, normalized `canonical_entities`, controlled
`odp_id`, `cq_type`, and `status`.

```bash
uv run aviation-ai ontology validate-cqs
```

The baseline and generated ontologies can be evaluated with deterministic
structural checks plus silver-CQ lexical and answerability heuristics:

```bash
uv run aviation-ai ontology evaluate
uv run aviation-ai ontology evaluate --generated --report-name generated_ontology_evaluation
```

The deterministic report distinguishes an RDF-valid TBox extraction prototype
from a valid TBox prototype. A valid prototype must pass conservative quality
gates for TBox-only output, ontology metadata, label coverage, domain/range
completeness, namespace policy, and high-severity semantic smell checks. Model
review is opt-in; run with `--ai-review` only after configuring a rotated local
API key in an ignored `.env` file.

The source PDF boundary can be summarized into deterministic scope reports and
boundary CQs:

```bash
uv run aviation-ai ontology scope
```

The evaluation treats generated CQs and boundary CQs as machine-generated silver
CQs, not expert gold annotations.

## Review Reports

Historical adversarial and implementation reviews (2026-05/06) were archived
under `reports/phak_era_archive/reviews/`; the thesis has incorporated their
findings.
Aggregate review progress with:

```bash
uv run aviation-ai report reviews
uv run aviation-ai report generation-runs
uv run aviation-ai report overnight
```

These commands write review progress, generation run summaries, and the
overnight optimization summary under `reports/stages/`.

## Report Hygiene and Final Project Report

Use report hygiene when `reports/stages/` becomes crowded with stage artifacts.
The dry run previews what will be archived without moving files:

```bash
uv run aviation-ai report hygiene --dry-run
```

Apply mode moves existing stage artifacts into
`reports/archive/stages/<YYYY-MM-DD>/` and leaves `reports/stages/` as a
readable dashboard with `index.md` and `index.json`:

```bash
uv run aviation-ai report hygiene --apply
```

Generate the final project report from curated evidence without requiring an API
key:

```bash
uv run aviation-ai report project --no-ai
```

After configuring the existing local LLM provider, generate the model-polished
Markdown report:

```bash
uv run aviation-ai report project --ai
```

The project report command writes `reports/phak_era_archive/project_report.md` and
`reports/phak_era_archive/project_report_sources.json`. The model prompt is constrained to the
evidence pack, must cite source file paths, and must mark missing results as
`TBD` or `Not yet run`.

Generate academic-style defense deliverables from the same evidence pack:

```bash
uv run aviation-ai report visual-assets
uv run aviation-ai report academic-paper --no-ai
uv run aviation-ai report defense-notes
uv run aviation-ai report defense-deck-outline
node scripts/build_defense_deck.mjs
```

These commands write `reports/phak_era_archive/project_academic_report.md`,
`reports/phak_era_archive/project_defense_notes.md`, illustrative PNG visuals with local
deterministic SVG fallbacks under
`reports/final/assets/`, and
`reports/final/aviation_graphrag_defense_deck.pptx`. The PNG visuals are
presentation-only explanatory assets; the metrics and technical labels remain
editable PPT objects backed by local reports. The manifest records whether
illustrative PNG assets are present without storing API keys, tokens, or gateway URLs. The
PPT builder uses the installed Presentations runtime and keeps preview/contact-
sheet scratch files under ignored `outputs/`.
