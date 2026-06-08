# Tracked Context Inventory

Last audited: 2026-06-08.

This inventory classifies tracked Markdown and report-source files by their
default context value. It complements `docs/context_hygiene_audit.md`: the audit
explains why old framing is risky, while this file explains which tracked file
families should be loaded by default.

## Audit Commands

Use tracked-file scans for context hygiene:

```bash
git ls-files '*.md' 'reports/**/*.json'
git grep -n -E '<pattern>' -- AGENTS.md README.md docs reports src scripts tests data/papers
```

Do not use broad multi-root `rg` scans as proof that repository context is
clean. They can include ignored local archives when explicit paths are supplied.

## Current Snapshot

| Family | Current tracked count | Default context status |
| --- | ---: | --- |
| Root project docs | 6 | mixed; start with `AGENTS.md`, `README.md`, `GOALS.md`, and use `TASKS.md` only for execution backlog. |
| `docs/*.md` | 23 | mixed; canonical docs plus historical PHAK-era protocols. |
| `reports/stages/*` Markdown/JSON | 241 | mixed; current ATCSCC evidence, method literature, and legacy experiment reports live together. |
| `reports/final/*` Markdown/JSON | 12 | mostly historical/transitional; current ATCSCC entry files are explicitly named. |
| `reports/reviews/*` Markdown/JSON | 16 | historical review evidence; useful for audit trail, not thesis entry context. |
| Other `reports/*.md` | 6 | historical code/security review evidence; do not load by default. |
| `data/evaluation/nasa_atmonto/*.md` | 21 | current evaluation evidence; load only for gold/review tasks. |
| `data/raw/nasa_bga_aerodynamics/*.md` | 90 | tracked transfer-pilot corpus; not current ATCSCC mainline. |
| `data/papers/*` tracked notes | 3 | literature/source notes; load only for paper or source-background tasks. |
| `data/ontology/*/README.md` | 3 | ontology-source notes; load only for schema/source questions. |
| `data/cqs/README.md` | 1 | CQ data note; load only for CQ tasks. |

## Default Load Set

For a new thread or thesis-writing task, load only:

1. `docs/thread_handoff.md`
2. `docs/documentation_map.md`
3. `docs/context_hygiene_audit.md`
4. `docs/thesis_positioning.md`
5. `docs/research_mainline.md`
6. `docs/experiment_workflow.md`
7. `docs/evaluation_protocol.md`
8. `reports/stages/thesis_experiment_dashboard.md`
9. `reports/stages/nasa_atmonto_reviewer_defense_audit.md`
10. `reports/stages/nasa_atmonto_sota_goal_audit.md`

Load additional files only when the task needs their layer.

## Tracked But Non-Default Families

| Family | Why it can pollute context | Safe use |
| --- | --- | --- |
| `docs/benchmark_design.md`, `docs/chunking_experiment_protocol.md`, `docs/ontology_design.md`, and related PHAK-era protocols | They describe the earlier aviation-training prototype and can make the thesis look ontology-first. | Historical method evolution only. |
| Early `reports/stages/benchmark_*`, `chunking_*`, `hybrid_rag_*`, `retrieval_ablation*`, `graphrag_review.*`, `kg_validation.*`, `web_demo_*` | They mix PHAK/web-demo evidence with current ATCSCC terminology. | Negative results, method evolution, or explicit comparison. |
| `reports/final/project_*`, `reports/final/defense_deck_outline.md`, old deck source JSON | Final-style but mostly pre-ATCSCC. | Presentation format reference or manually reviewed reusable fragments. |
| `reports/reviews/*` and root `reports/*review*.md` | Review trails from earlier branches may include stale issue lists or resolved risks. | Audit history only after checking current dashboard and reviewer-defense audit. |
| `data/raw/nasa_bga_aerodynamics/*.md` | Transfer-pilot source family, not ATCSCC. | Transfer/source-expansion tasks only. |
| `data/papers/ntrs_ontology_selection/*.pdf` | Tracked source PDFs are useful provenance but large and not thread context. | Open specific PDFs only for source-background analysis. |

## Current-Use Families

| Family | Use |
| --- | --- |
| `reports/stages/atcscc_*` | ATCSCC source, schema, validation, repair, and graph-use explainers. |
| `reports/stages/nasa_atmonto_*` | Current formal experiment scoring, agentic loop, retrieval, answer generation, and reviewer-defense evidence. |
| `data/evaluation/nasa_atmonto/*` | Gold review, CQ query templates, candidate review, and review packets. |
| `reports/stages/*sota*`, `*method*`, `*paper_analysis*`, `*paper_adaptation*` | Related work and method migration, not direct experiment evidence unless linked by the dashboard. |

## Maintenance Rule

When adding a new tracked report or document, decide one of:

- current default context;
- current evidence but task-specific;
- method/literature support;
- transfer/source-expansion support;
- historical/provenance only.

Then link it from `docs/documentation_map.md` only if it should be discoverable
from the current thesis path.

