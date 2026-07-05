# Artifact Index

> Migrated on 2026-07-05 from `docs/documentation_map.md` Context Inventory, Ignored Local Material, and Artifact Management Policy sections. Until the archive commit lands, `docs/documentation_map.md` remains in place under `docs/`; afterward it will be preserved under `docs/archive/governance_era/documentation_map.md`.

## Artifact Type Vocabulary

`code`, `dataset`, `model`, `notebook`, `figure`, `screenshot`, `prompt`, `generated_asset`, `log`, `report`, `configuration`.

## Tracked File-Family Snapshot

| Family | Default context status |
| --- | --- |
| Root project docs | mixed; `AGENTS.md` is authoritative, `CLAUDE.md` is a compatibility shim, `README.md` and `GOALS.md` are project references, `TASKS.md` is execution backlog only. |
| `docs/*.md` | canonical docs; PHAK-era protocols archived under `docs/archive/phak_era/`. |
| `reports/stages/*` | mixed; current ATCSCC evidence, method literature, and legacy experiment reports live together. |
| `reports/final/*` | mostly historical/transitional; current ATCSCC entry files are explicitly named `atcscc_*`. |
| `data/evaluation/nasa_atmonto/*` | current evaluation evidence; load only for gold/review tasks. |
| `data/raw/nasa_bga_aerodynamics/*` | tracked transfer-pilot corpus; not current ATCSCC mainline. |

## Tracked But Non-Default Families

| Family | Why it can pollute context | Safe use |
| --- | --- | --- |
| `docs/archive/phak_era/*` | Describe the earlier aviation-training prototype; can make the thesis look ontology-first. | Historical method evolution only. |
| Early `reports/stages/benchmark_*`, `chunking_*`, `hybrid_rag_*`, `retrieval_ablation*`, `graphrag_review.*`, `kg_validation.*`, `web_demo_*` | Mix PHAK/web-demo evidence with current ATCSCC terminology. | Negative results, method evolution, or explicit comparison. |
| `reports/final/project_*`, `reports/final/defense_deck_outline.md`, old deck source JSON | Final-style but mostly pre-ATCSCC. | Presentation format reference or manually reviewed reusable fragments. |
| `reports/phak_era_archive/reviews/*` and root `reports/*review*.md` | Archived 2026-05/06 adversarial/implementation review trails; the thesis has incorporated their findings. | Audit history only. |
| `data/cqs/06_phak_*.json` | Historical PHAK benchmark and gold data. | Load only for explicit PHAK benchmark or historical comparison tasks. |

## Current-Use Families

| Family | Use |
| --- | --- |
| `reports/stages/atcscc_*` | ATCSCC source, schema, validation, repair, and graph-use explainers. |
| `reports/stages/nasa_atmonto_*` | Current formal experiment scoring, agentic loop, retrieval, answer generation, and reviewer-defense evidence. |
| `data/evaluation/nasa_atmonto/*` | Gold review, CQ query templates, candidate review, and review packets. |
| `reports/stages/*sota*`, `*method*`, `*paper_analysis*`, `*paper_adaptation*` | Related work and method migration, not direct experiment evidence unless linked by the dashboard. |

## Ignored Local Material

| Path | Why it is risky |
| --- | --- |
| `reports/archive/` | Local archive of obsolete stage reports; keep out of thesis-writing context. |
| `outputs/` | Runtime outputs and scratch material that may combine multiple branches or stale experiments. |
| `reports/stages/paper_figure_gallery.html` and gallery manifests | Local visual-comparison pages generated during paper review; useful for inspection, not thesis evidence. |

## Artifact Management Policy

The repository intentionally tracks bounded thesis-evidence artifacts needed to
reproduce the current ATCSCC claims:

- reviewed gold and review-decision artifacts under `data/evaluation/nasa_atmonto/`;
- formal S0-S7 prediction and run-metadata artifacts under
  `data/experiments/nasa_atmonto/formal/`;
- stage-report JSON/Markdown files that feed the thesis dashboard, SOTA audit,
  reviewer-defense audit, and chapter draft.

The repository intentionally ignores raw/local/generated material that is either
large, environment-specific, or easy to rebuild: raw NASA ATMONTO snapshots under
`data/raw/nasa_atmonto/`; smoke outputs under
`data/experiments/nasa_atmonto/formal/smoke/`; vector indexes, chunks, local
paper PDFs, temporary PDF extraction assets, gallery HTML/manifest files,
historical local archives under `reports/archive/`, and `outputs/`.

Future large experiment outputs should enter Git only when they are referenced
by the thesis dashboard or a claim-safety audit. Otherwise place them under an
ignored runtime/output location and summarize them in a small tracked report.

## Audit Commands

Use tracked-file scans for context hygiene:

```bash
git ls-files '*.md' 'reports/**/*.json'
git grep -n -E '<pattern>' -- AGENTS.md README.md docs reports src scripts tests data/papers
```

Do not use broad multi-root `rg` scans as proof that repository context is
clean; they can include ignored local archives when explicit paths are supplied.
