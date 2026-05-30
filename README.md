# Aviation Agentic AI

Aviation Agentic AI is a research prototype for turning aviation training text
into machine-queryable knowledge. It uses FAA Pilot's Handbook of Aeronautical
Knowledge material as a source document, represents domain concepts as an
ontology, and prepares the foundation for provenance-aware Knowledge Graph and
GraphRAG retrieval workflows.

The project focuses on a practical question: can aviation concepts such as lift,
drag, angle of attack, airflow, pressure, density, and altitude be extracted from
technical prose into structured knowledge that can support traceable question
answering?

The current thesis framing does not assume that GraphRAG universally improves
Recall@k over vector-only RAG. It evaluates a narrower claim:
ontology-constrained GraphRAG can add inspectable evidence-traceability signals,
KG evidence coverage, and safety-aware abstention checks for aviation training
QA, with each metric layer reported separately.

## What This Project Demonstrates

- **Ontology-first modeling** of aviation concepts from PHAK Chapter 4.
- **RDF/OWL validation and reporting** over the generated aviation ontology.
- **A focused ABox extraction design** for future entity and relation extraction.
- **GraphRAG-ready structure** with separate modules for ontology, KG, chunking,
  retrieval, evaluation, and reporting.
- **Layered evaluation and claim safety review** for retrieval quality, KG
  evidence quality, answer quality, and safety-aware abstention.
- **Submission-friendly project hygiene** with curated assets, third-party
  attribution, and generated artifacts kept under control.

## Current Prototype

The current implementation includes project-owned ontology generation code plus
an explainable curated ontology for PHAK Chapter 4. The older baseline ontology
is kept as a historical reference because it is useful for comparison but too
large to explain clearly as the primary project schema. The curated ontology is
the active task ontology for focused KG extraction and GraphRAG experiments.

Baseline assets:

- Source PDF: `data/raw/06_phak_ch4_0.pdf`
- Primary ontology-generation reference paper:
  `data/papers/towards-automated-ontology-generation-multi-agent-llm.pdf`
- Generated CQs copied from the reference pipeline:
  `data/cqs/06_phak_ch4_0.json`
- Active curated ontology: `data/ontology/curated/06_phak_ch4_0.curated.ttl`
- Ontology design explanation: `docs/ontology_design.md`
- Historical baseline ontology: `data/ontology/baseline/06_phak_ch4_0.ttl`
- Reference generated ontology/KG artifact:
  `data/ontology/generated/reference/06_phak_ch4_0_kg_backup_20260512_042920.ttl`
- Ontology report: `reports/stages/ontology_report.md`
- Ontology statistics: `reports/stages/ontology_stats.json`

The historical baseline ontology currently contains:

- 2,773 RDF triples
- 245 OWL classes
- 173 object properties
- 2 datatype properties
- 0 named individuals in the historical baseline TBox

The active curated ontology is intentionally smaller. It is designed to be
explainable in a project review and to constrain KG extraction with a focused
set of aviation classes and relations.

## Planned Pipeline

```text
PHAK PDF
  -> CQ generation
  -> SRD/TIP/TTL ontology generation
  -> RDF validation and reporting
  -> focused ABox/KG extraction with provenance
  -> section-aware semantic chunking
  -> graph retrieval + vector retrieval
  -> hybrid GraphRAG answer generation with citations
```

The project is CLI-first so every stage can be reproduced and evaluated before a
service or user interface is added.

## Project Layout

```text
configs/                 Reproducible project and extraction settings
data/raw/                Curated source PDF
data/papers/             Related research papers and reading notes
data/ontology/           Baseline and generated ontology artifacts
data/kg/                 Future KG/ABox artifacts
reports/                 Stage and final research reports
src/aviation_agentic_ai/ Project package and CLI implementation
tests/                   Unit and integration tests
```

Report directories are intentionally separated:

- `reports/stages/`: current dashboard entrypoints such as `index.md` and
  `index.json`
- `reports/archive/`: archived stage artifacts and run evidence
- `reports/reviews/`: review inputs that are indexed but not archived by
  hygiene commands
- `reports/final/`: final deliverables such as `project_report.md`

## Quick Start

```bash
cd aviation_agentic_ai
uv sync --extra dev
uv run aviation-ai ontology validate
uv run aviation-ai ontology report
uv run aviation-ai ontology validate-cqs
```

Without `uv`:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
aviation-ai ontology validate
```

## CLI

```bash
aviation-ai --help
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
aviation-ai report retrieval-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name retrieval_ablation_benchmark_v2
aviation-ai report graph-traversal-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name graph_traversal_ablation_benchmark_v2
aviation-ai report thesis-experiment-dashboard
aviation-ai web serve
aviation-ai report hygiene --dry-run
aviation-ai report project --no-ai
```

Additional stage-report aggregation is available with:

```bash
aviation-ai report stages
```

## Research Direction

The ontology-generation code is adapted from the open-source implementation
associated with the paper in
`data/papers/towards-automated-ontology-generation-multi-agent-llm.pdf`, with
the method reworked for aviation training text. The upstream implementation is
`https://github.com/brains-group/towards_automated_ontology_generation`. Source
PDF text is converted into ontology-focused Competency Questions, then an
LLM-assisted pipeline turns those CQs into validated Semantic Requirements
Document and Technical Implementation Plan JSON artifacts, then Turtle ontology
output. Per-run manifests and page checkpoints are written when an artifact
directory is supplied. The current baseline ontology is not treated as final.

The next stage after selecting the curated ontology is focused ABox extraction.
Instead of extracting every possible concept from the historical baseline, the
project uses `configs/extraction_profile.yaml` to define a small set of
high-value aviation classes and relations for v1. Each extracted triple carries
source provenance so GraphRAG answers can cite the text that supports them.

The retrieval layer will combine:

- graph lookup and neighborhood traversal over validated RDF
- vector retrieval over stable source chunks
- normalized rank fusion for hybrid retrieval

## Chunking Comparison

The chunking comparison experiment evaluates how document splitting affects
vector retrieval quality. The original report is a 10-CQ pilot over PHAK
Chapter 4 boundary CQs. It compares:

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
```

This command evaluates mainstream chunking families on benchmark v2 and writes
`reports/stages/chunking_comparison_benchmark_v2.json`, `.md`,
`reports/stages/chunking_failure_cards_benchmark_v2.json`, and `.md`. It reports
supported-only retrieval metrics, insufficient-evidence diagnostics, chunk-size
sensitivity, category-level results, confidence intervals, and qualitative
failure cards. The fixed-budget mode writes
`reports/stages/chunking_comparison_benchmark_v2_budget.json` and `.md`; the
independent hardening commands write implementation-audit, top-k sensitivity, and
category-analysis reports. These commands are not included in `thesis-all` or
the default thesis report generation targets by design. The protocol is
documented in `docs/chunking_experiment_protocol.md`.

## Hybrid RAG Experiment

The PHAK Chapter 4 Hybrid RAG experiment builds a reproducible retrieval and
grounded-answering loop:

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

The evaluation protocol is documented in `docs/evaluation_protocol.md`. It maps
mainstream RAGAS-style, ARES-style, IR, GraphRAG, ontology/KG, and aviation
safety metrics to this project. The project reports layered metrics and does not
claim or compute a single mixed overall score.

Model-based review is documented in `docs/llm_review_protocol.md`. LLM review
uses the configured `MODEL_NAME` as `reviewer_model`; it is not human review,
not expert gold, and not external aviation certification. If LLM dependencies or
credentials are unavailable, the review commands write explicit `not_run`
statuses instead of fabricating review results.

## Thesis Experiment Workflow

The canonical thesis workflow is documented in `docs/experiment_workflow.md`.
It connects research questions, datasets, baselines, metrics, reports,
limitations, and final thesis claims. Use the Makefile targets for the
deterministic workflow; they do not require API keys. The main experiment
targets do require a prepared local GraphRAG workspace with the ignored
`data/chunks/` and `data/indexes/chroma/` artifacts present.

```bash
uv sync --extra dev --extra graphrag
make validate
uv run aviation-ai cqs validate-benchmark --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json
make reports-core
make reports-main-experiments
make reports-review
make thesis-dashboard
uv run aviation-ai report project --no-ai
uv run aviation-ai report academic-paper --no-ai
```

The dashboard command writes `reports/stages/thesis_experiment_dashboard.json`
and `.md`. It aggregates existing reports into an experiment inventory,
RQ-to-evidence matrix, dataset usage matrix, primary results table,
failure-mode summary, and thesis-ready claim summary. It does not recompute
experiments, fabricate human review results, or produce a mixed overall score.
`all_passed=false` can be expected while model-based benchmark, triple, answer,
or path review remains pending; automated consistency is reported separately.

## Thesis Positioning And Claim Safety

The thesis positioning document is `docs/thesis_positioning.md`. It records the
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
completeness, namespace policy, and high-severity semantic smell checks. AI
review is opt-in; run with `--ai-review` only after configuring a rotated local
API key in an ignored `.env` file.

The source PDF boundary can be summarized into deterministic scope reports and
boundary CQs:

```bash
uv run aviation-ai ontology scope
```

The evaluation treats generated CQs and boundary CQs as AI-generated silver CQs,
not expert gold annotations.

## Review Reports

Important agent, code, and research reviews are recorded under `reports/reviews/`
as Markdown plus JSON. Each review finding includes severity, evidence,
recommendation, and status; each action includes priority, target, and status.
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

After configuring the existing local LLM provider, generate the AI-polished
Markdown report:

```bash
uv run aviation-ai report project --ai
```

The project report command writes `reports/final/project_report.md` and
`reports/final/project_report_sources.json`. The AI prompt is constrained to the
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

These commands write `reports/final/project_academic_report.md`,
`reports/final/project_defense_notes.md`, AI-enhanced PNG visuals with local
deterministic SVG fallbacks under
`reports/final/assets/`, and
`reports/final/aviation_graphrag_defense_deck.pptx`. The PNG visuals are
presentation-only explanatory assets; the metrics and technical labels remain
editable PPT objects backed by local reports. The manifest records whether AI
PNG assets are present without storing API keys, tokens, or gateway URLs. The
PPT builder uses the installed Presentations runtime and keeps preview/contact-
sheet scratch files under ignored `outputs/`.
