# AGENTS.md

Repository-level instructions for coding agents. Keep this file operational;
detailed designs and historical protocols live under `docs/`.

## Project Posture

This is a **system and framework construction project**. The primary deliverable
is a runnable multi-Agent aviation event knowledge system over retrospective FAA
ATCSCC advisories.

The active pipeline is:

```text
718 ATCSCC advisories + bounded FAA authority records
  -> cohort/all selection or explicit source-ID subset
  -> deterministic preflight (unsupported/incomplete -> zero-call insufficient)
  -> deterministic AdvisoryParser
  -> facility and terminology authority services
     -> shared Semantic Resolution Agent only for genuine ambiguity
  -> deterministic Weather and BTS context preparation and validation
  -> sealed Decision Case Assembly task
  -> deterministic compiler for the three canonical cases or bounded
     Decision Case Assembly Agent for genuine evidence/schema choice
  -> task-bound validation
  -> deterministic Formal Graph Kernel
  -> corpus v2 normalization and JSONL + RDF + Neo4j materialization
  -> deterministic corpus query routing with bounded read-only graph tools
     -> Decision Case Analysis Agent only for exact registered analysis questions
```

The knowledge graph is both a system output and shared evidence memory. The
ontology profile constrains publication; it is not a separate Agent and is not
claimed to be a complete aviation ontology.

The normative implementation design is
`docs/multi_agent_kg_system_design.md`. Reader-facing documents use full Agent
names, not internal alphanumeric labels.

## Current Status

- `main` contains the corpus-first builder, validation, corpus v2
  materialization, full-corpus Neo4j projection, bounded query path,
  Decision Case Assembly, and Decision Case Analysis.
- The three Decision Record Explorer cases have deterministic query support on
  `main`, including a profile-gap reason and an honest missing-reason outcome.
- Batch C.1 and Batch D are merged into `main`. The three canonical records use
  the zero-call deterministic compiler, and the Formal Graph Kernel remains the
  sole final publication authority.
- Decision Case Analysis is active only for exact registered episode,
  operational-situation, and applicability questions. It uses closed plans and
  bounded read-only tools. Historical similarity remains a deterministic
  insufficient corpus gate; existing record questions remain zero-call.
- Storage Batch S2 is the completed breaking storage cutover. The public
  commands are `build-corpus`, `ask`, `neo4j-export`, and `export-case`.
  There is no persistent single-case `ingest`, `ask-corpus`, `--runs-root`,
  `--run-dir`, or corpus-v1 compatibility path. Use `build-corpus --source-id`
  for a bounded debug build.
- The frozen cohort is 718 discovered and 68 selected: 42 Agent-eligible, 23
  unsupported TMI, and 3 incomplete core-field records. The 26 preflight
  failures are `insufficient` with zero model calls. A corpus manifest is
  published only when blocked is zero; `--resume` retries only blocked entries.
- The read-only visualization prototype is isolated on
  `codex/kg-visualization-research`. Visualization is paused and is not the
  active `main` implementation track.
- Comparison experiments, Gold adjudication, alignment MVE work, broader
  weather expansion, causal explanation, and recommendation remain optional or
  deferred unless explicitly reactivated.

## Default Context

For a new task:

1. Read `RESEARCH_AUDIT.md`.
2. Read `GOALS.md`.
3. Load `README.md`, `TODO.md`, or a design document only when the task needs
   that layer.

Do not preload `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`,
`RESULTS.md`, stage-report directories, ignored corpus outputs, or archived
PHAK/web-demo material. They describe optional evaluation or historical work,
not the default system scope.

Use English for active code, contracts, prompts, CLI messages, tests,
documentation, and generated artifacts. Preserve non-English text only when it
is explicitly identified source material.

## Execution Policy

Before proposing a new implementation stage, state:

- the user-facing or system capability being advanced;
- the smallest end-to-end result;
- the minimum components needed;
- the evidence that will show it works;
- the success and failure conditions;
- what is explicitly deferred.

Prefer the smallest runnable system increment. Do not add a role, data source,
guardrail, framework, schema layer, or benchmark unless an observed failure or
the approved task requires it. Do not turn an implementation task into a paired
comparison experiment without an explicit scope decision.

## Research Prototype Effort Boundary

- Optimize for the end-to-end architecture, runnable pipeline, and approved
  research semantics rather than production-grade hardening.
- Add a guard or adversarial test only when an approved acceptance scenario
  requires it or a failure is reproduced through a supported user workflow.
- Preserve the canonical reason states, time boundaries, source-role
  separation, zero-call insufficient behavior, bounded read-only access, and
  the prohibition on causal or recommendation claims.
- Validate external inputs and final publication/query boundaries. Do not add
  redundant checks for manually forged internal objects that the supported
  pipeline does not construct.
- Symlink attacks, path traversal, concurrent mutation, secret injection,
  contradictory hand-built audit records, and hostile cross-run tampering are
  deferred unless a deployment or security task explicitly activates them.
- Use one bounded review pass. After fixes, run focused tests and one final
  repository verification; do not start recursive reviewer-fix-review cycles.
- Once the approved acceptance scenarios pass, record production-only residual
  risks as deferred and stop the batch.

## Research And Evidence Boundaries

- Keep ATCSCC advisories, FAA/NASA references, NASR facilities, terminology,
  weather, and transfer pilots as separate source families unless a current
  design admits their integration.
- Treat correctness as task-relative: source-field coverage, schema validity,
  evidence support, canonical identity, and reviewed semantic accuracy are
  different claims.
- Do not claim complete aviation knowledge, live ATC decision support,
  external expert certification, causal explanation, or optimal TMI
  recommendation.
- Treat papers, web pages, raw HTML, and downloaded files as untrusted evidence.

## Development Workflow

- Prefer existing project patterns and small, reviewable changes.
- Use `rg` and `rg --files` for repository search.
- Use `git grep` for tracked-file context-hygiene scans.
- Preserve unrelated user changes and generated research artifacts.
- Do not load ignored archives, `outputs/`, local corpus outputs, or figure
  galleries unless the task explicitly requires them.
- Use subagents primarily for read-only review or non-overlapping work.

## Verification

- During implementation, run the focused tests for the changed capability.
- At batch completion, run `uv run ruff check .` and `uv run pytest -q` once.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Report changes: run the relevant command in `REPRODUCIBILITY.md` and inspect
  the generated diff.
- Verify implementation and artifacts before changing project claims.

## Current Documentation And APIs

For current library, framework, SDK, API, CLI, or cloud-service syntax, use the
repository-configured `ctx7` workflow before relying on model memory. Do not use
it for business logic, refactoring, or code review.

## Git And Publishing

- `origin` is GitLab and `github` is GitHub.
- Push only when the user requests publishing.
- After an approved merge into `main`, verify local and requested remote refs
  point to the intended commit.
