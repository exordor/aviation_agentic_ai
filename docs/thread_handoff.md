# Thread Handoff

Use this file when starting a new Codex thread for this repository. It is a
compact context pack, not a project report.

## Current Research Line

The active thesis line is:

> Agentic KG-RAG for evidence-grounded question answering over retrospective
> FAA ATCSCC advisories.

Frame the project as schema-constrained advisory-event extraction plus
evidence-grounded KG-RAG evaluation. Do not frame it as full aviation ontology
construction or live ATC decision support.

## Minimal Startup Pack

For a new thread, read only these files first:

1. `docs/master_project_scope_lock.md`
2. `docs/documentation_map.md` (absorbs the former context-hygiene audit,
   maintenance guide, and tracked-context inventory)

This keeps startup context small. Load additional files only when the task needs
their layer:

- thesis framing: `docs/thesis_positioning.md`, `docs/research_mainline.md`;
- experiment execution and metrics: `docs/experiment_protocol.md`;
- current evidence synthesis: `reports/stages/thesis_experiment_dashboard.md`;
- reviewer/SOTA defense:
  `reports/stages/nasa_atmonto_reviewer_defense_audit.md`,
  `reports/stages/nasa_atmonto_sota_goal_audit.md`.

Before opening a long-running new thread, also use the recommended Codex client
state in `docs/documentation_map.md#codex-skill-and-plugin-hygiene`:
keep only the needed plugins and load task-specific skills on demand.

## Startup Validation

After reading the startup pack, verify these before making broad edits:

1. The thesis is ATCSCC schema-constrained KG-RAG, not ontology construction.
2. Historical PHAK/web-demo/final-report files are excluded by default.
3. New source families need separate profiles and metrics.
4. Tooling is limited to the plugins and skills needed for the current task.
5. Claims stay evidence-backed and avoid operational readiness language.

## Claim Boundaries

Allowed claims:

- schema/profile validity on the evaluated source family;
- evidence-linked event extraction over bounded ATCSCC advisories;
- task-relative CQ and source-field coverage;
- reviewed-subset correctness;
- retrieval and answer-grounding metrics under the documented protocol.

Avoid claims that imply:

- complete aviation-domain ontology coverage;
- production ATC decision support;
- operational safety certification;
- universal KG-RAG superiority;
- semantic correctness beyond reviewed evidence.

## Source Boundaries

Keep source families separate unless a source-specific profile and evaluation
protocol exists:

- ATCSCC advisories;
- FAA/NASA reference PDFs;
- NASR/facility data;
- weather data;
- transfer pilots or non-ATCSCC corpora.

## Historical Context To Avoid By Default

Do not use these as thesis entry points unless the task explicitly asks for
history or comparison:

- PHAK Chapter 4 ontology and benchmark documents;
- old web-demo/chunking/retrieval reports;
- historical `reports/final/project_*` drafts;
- ignored `reports/archive/` and `outputs/` material;
- paper figure galleries and temporary PDF extraction assets.

## Verification Defaults

- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Report-generation changes: run the relevant report command and inspect the
  generated diff before committing.
