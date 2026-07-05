# Research-Governance Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the project's canonical governance content out of the `docs/` spine into the guide's root-level file set (`RESEARCH_OVERVIEW.md`, `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`, `RESULTS.md`, `ARTIFACT_INDEX.md`, `DECISION_LOG.md`, `REPRODUCIBILITY.md`, `RESEARCH_AUDIT.md`, `TODO.md`), archive the old `docs/` spine under `docs/archive/governance_era/`, and retarget every live link — including the runtime `read_text()` in `_audit_reports.py`.

**Architecture:** Six incremental commits on branch `refactor/research-governance-framework`. Commit 1 lands the load-bearing `EXPERIMENTS.md` migration plus the code/test rewiring (proven green before any other step). Commits 2–4 migrate the rest of the spine into the new files. Commit 5 retargets ~25 live link references across docs/reports/src. Commit 6 archives the old spine. JSON regeneration is deferred to a separate follow-up commit.

**Tech Stack:** Markdown, Python (the only code edit is `_audit_reports.py` path literals + two test files), `uv` + `ruff` + `pytest` for verification.

**Spec:** `docs/superpowers/specs/2026-07-05-research-governance-refactor-design.md`

---

## File Structure

### New files (created across the plan)

| File | Responsibility |
|---|---|
| `EXPERIMENTS.md` (root) | Material passport, source families, SOTA-informed adaptation, claims C1–C5, hypotheses H1–H4 + falsification, gold-set plan, systems S0–S4 + PDF systems, metrics, rejection analysis, procedure, reporting rules, completion gate, layered-evaluation policy, navigation, regeneration commands. Must contain every test-required literal. |
| `HYPOTHESES.md` (root) | Single H1–H4 table + per-hypothesis detail with falsification criteria and current interpretation. |
| `RESEARCH_QUESTIONS.md` (root) | RQ1–RQ4 in the guide's Description/Motivation/Related Hypotheses/Related Experiments/Current Evidence/Status template. |
| `RESEARCH_OVERVIEW.md` (root) | Problem statement, revised claim, contributions, evaluation philosophy, claim-safety matrix, can/must-not-claim, scope-lock (locked outcome, non-goals, intake rule, stop rule), one-line direction, thesis story, SOTA positioning, current usable claims, claims to avoid. |
| `RESULTS.md` (root) | Deliverables table + evidence-layer table, rewritten as Observation / Evidence / Interpretation / Confidence rows pointing at `reports/stages/nasa_atmonto_*`. |
| `ARTIFACT_INDEX.md` (root) | Tracked file-family snapshot, tracked-but-non-default families, current-use families, ignored local material, artifact management policy. |
| `DECISION_LOG.md` (root) | D001-style entries seeded from scope-lock decisions (single thesis study; four locked RQs; layered metrics, no overall score; PHAK-era evidence historical; etc.). |
| `REPRODUCIBILITY.md` (root) | Environment, install, env vars, run-prototype, run-experiments, expected outputs, known issues, regeneration commands. |
| `RESEARCH_AUDIT.md` (root) | Project snapshot, navigation map to the other nine files, the guide's 6-questions rubric. New entry point. |
| `TODO.md` (root) | Active task queue + P0–P4, migrated from `TASKS.md` into the guide's TODO voice. |
| `docs/archive/governance_era/README.md` | Documents what was archived when, why, and what supersedes each file. |

### Modified files

| File | Change |
|---|---|
| `src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py` | Lines 460, 518, 615, 642, 1082: `docs/experiment_protocol.md` → `EXPERIMENTS.md`. |
| `tests/test_nasa_atmonto_experiment_protocol.py` | Lines 58, 126, 141: `Path("docs/experiment_protocol.md")` → `Path("EXPERIMENTS.md")`. |
| `tests/test_nasa_atmonto_formal_experiment.py` | Lines 372–376: fixture source/dest → `EXPERIMENTS.md`. |
| `AGENTS.md` | Default Context paragraph rewritten to point at root files. |
| `CLAUDE.md` | Same retargeting. |
| `README.md` | Spine links retargeted (lines 45–49, 76, 182, 364, 404, 407, 456). |
| `GOALS.md` | `thesis_positioning.md` refs (lines 116, 233) → `RESEARCH_OVERVIEW.md`. |
| `docs/thesis_writing_spine.md`, `docs/research_paper_analysis_protocol.md`, `docs/atcscc_agent_architecture.md`, `docs/pipeline_authority_model.md` | Spine-link retargets. |
| `reports/stages/index.md`, `reports/final/README.md`, `reports/final/atcscc_thesis_report.md`, `reports/final/atcscc_thesis_report_outline.md`, `reports/final/atcscc_defense_deck_outline.md`, `reports/final/atcscc_agent_plan_storyboard.md`, `reports/final/figure_descriptions.md`, `reports/stages/thesis_claims_review.md` (+ `.json`), `reports/stages/nasa_atmonto_competency_questions.md`, `reports/stages/nasa_atmonto_formal_experiment_readiness.md` (+ `.json`), `reports/stages/nasa_atmonto_formal_experiment_remediation_plan.md`, `reports/stages/nasa_atmonto_formal_experiment_scoring.md` (+ `.json` + gpt-5.4-mini variants), `reports/stages/nasa_atmonto_gold_review_multiround_audit.md`, `src/aviation_agentic_ai/reporting/thesis_claims.py` | Spine-link retargets (full list in spec §7.2). |

### Archived (Commit 6 `git mv`)

`docs/thread_handoff.md`, `docs/master_project_scope_lock.md`, `docs/documentation_map.md`, `docs/research_mainline.md`, `docs/thesis_positioning.md`, `docs/experiment_protocol.md`, `TASKS.md` → into `docs/archive/governance_era/`.

---

## Task 1: Scaffold the ten root files as stubs

**Files:**
- Create: `RESEARCH_AUDIT.md`, `RESEARCH_OVERVIEW.md`, `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`, `RESULTS.md`, `ARTIFACT_INDEX.md`, `DECISION_LOG.md`, `REPRODUCIBILITY.md`, `TODO.md`

This task only creates placeholder stubs so that subsequent tasks can fill each file. It commits nothing on its own — the stubs are committed together with the content that lands first (Task 2).

- [ ] **Step 1: Confirm clean working tree and correct branch**

Run:
```bash
git status --short
git branch --show-current
```
Expected: empty status, branch `refactor/research-governance-framework`.

- [ ] **Step 2: Create the ten stub files**

Each stub has the same shape: top-level title matching the guide, a one-line "Status: stub — populated in Tasks N–M" note, and a "Source: spec §X" pointer. Use this exact body for each (substitute the file's own title and source-section pointer):

For `RESEARCH_OVERVIEW.md`:
```markdown
# Research Overview

> Status: stub — populated in Task 3.
> Source: spec §4.1. Guide §2.1. Replaces `docs/thesis_positioning.md` + `docs/research_mainline.md` + scope-lock framing from `docs/master_project_scope_lock.md`.
```

For `RESEARCH_QUESTIONS.md`:
```markdown
# Research Questions

> Status: stub — populated in Task 3.
> Source: spec §4.1, §5. Guide §2.2. Replaces the Research-Questions sections of `docs/research_mainline.md`, `docs/thesis_positioning.md`, and `docs/master_project_scope_lock.md`.
```

For `HYPOTHESES.md`:
```markdown
# Hypotheses

> Status: stub — populated in Task 3.
> Source: spec §4.1, §5, §6.3. Guide §2.3. Replaces the Hypotheses sections of `docs/experiment_protocol.md` and `docs/thesis_positioning.md`.
```

For `EXPERIMENTS.md`:
```markdown
# Experiments

> Status: stub — populated in Task 2.
> Source: spec §4.1, §6.3. Guide §3.3. Replaces `docs/experiment_protocol.md`.
```

For `RESULTS.md`:
```markdown
# Results

> Status: stub — populated in Task 4.
> Source: spec §4.1. Guide §4.2. Replaces deliverables/evidence-layer tables from `docs/master_project_scope_lock.md` and `docs/documentation_map.md`.
```

For `ARTIFACT_INDEX.md`:
```markdown
# Artifact Index

> Status: stub — populated in Task 4.
> Source: spec §4.1. Guide §5.1. Replaces the Context Inventory and Artifact Management Policy of `docs/documentation_map.md`.
```

For `DECISION_LOG.md`:
```markdown
# Decision Log

> Status: stub — populated in Task 4.
> Source: spec §4.1. Guide §6. Replaces scope-lock decisions from `docs/master_project_scope_lock.md` and tiering rules from `docs/documentation_map.md`.
```

For `REPRODUCIBILITY.md`:
```markdown
# Reproducibility

> Status: stub — populated in Task 4.
> Source: spec §4.1. Guide §7. Replaces regeneration commands from `docs/experiment_protocol.md` and verification defaults from `docs/thread_handoff.md`.
```

For `RESEARCH_AUDIT.md`:
```markdown
# Research Audit

> Status: stub — populated in Task 5.
> Source: spec §4.1, §4.3 #6. Guide §1.3. Becomes the new thread entry point; replaces `docs/thread_handoff.md` + `docs/documentation_map.md` start-here role.
```

For `TODO.md`:
```markdown
# TODO

> Status: stub — populated in Task 5.
> Source: spec §4.1. Guide §2, §11, §13. Replaces `TASKS.md`.
```

- [ ] **Step 3: Verify the stubs exist and are non-empty**

Run:
```bash
ls -la RESEARCH_AUDIT.md RESEARCH_OVERVIEW.md RESEARCH_QUESTIONS.md HYPOTHESES.md EXPERIMENTS.md RESULTS.md ARTIFACT_INDEX.md DECISION_LOG.md REPRODUCIBILITY.md TODO.md
```
Expected: ten files, each non-zero bytes.

Do not commit yet — Task 2 commits `EXPERIMENTS.md` content (and the stub is overwritten in the same commit).

---

## Task 2: Populate EXPERIMENTS.md and rewire code + tests (Commit 1)

This is the load-bearing task. It must be green before anything else.

**Files:**
- Modify: `EXPERIMENTS.md` (root) — replace stub with full migrated content.
- Modify: `src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py:460,518,615,642,1082`
- Modify: `tests/test_nasa_atmonto_experiment_protocol.py:58,126,141`
- Modify: `tests/test_nasa_atmonto_formal_experiment.py:372-376`

- [ ] **Step 1: Build EXPERIMENTS.md by copying docs/experiment_protocol.md verbatim, then retitling**

The protocol content migrates essentially verbatim because the test asserts ~60 specific string literals. Do not paraphrase. Steps:

```bash
cp docs/experiment_protocol.md EXPERIMENTS.md
```

Then edit `EXPERIMENTS.md` in place:

1. Change the H1 title line from `# NASA ATMONTO ATCSCC Formal Experiment Protocol` to `# Experiments`.
2. Immediately under the new H1, add a provenance note:
   ```markdown
   > Migrated from `docs/experiment_protocol.md` on 2026-07-05 as part of the research-governance refactor (spec `docs/superpowers/specs/2026-07-05-research-governance-refactor-design.md`). The original is preserved under `docs/archive/governance_era/experiment_protocol.md`. This file is the live protocol referenced by `_audit_reports.py` and the formal-experiment tests.
   ```
3. Leave every other line unchanged.

- [ ] **Step 2: Verify the test-required literals are all present in EXPERIMENTS.md**

Run:
```bash
uv run python -c "
from pathlib import Path
text = Path('EXPERIMENTS.md').read_text(encoding='utf-8')
required = [
    'pilot / feasibility study','Source Families','faa_atcscc_advisories',
    'faa_nasa_pdf_reference_documents','hybrid_docling_pymupdf','pymupdf_text_legacy',
    'term_has_definition','procedure_mentions_concept',
    'SOTA-Informed Adaptation For The Rerun','Extract-Define-Canonicalize',
    'reviewed_dev_examples','held-out 100 scoring records','canonicalizers',
    'evidence checkers','profile-gap explainers','nine-stage pipeline',
    'ATCSCC parsing','schema/atcscc_tmi_profile.yaml','predicate_uri',
    'repair-induced false positive','format error','predicate drift',
    'entity canonicalization error','fuzzy-only mappings','repair-only facts',
    'log/review/quarantine','GraphRAG evaluation remains layered',
    'end-to-end GraphRAG answer improvement','requiring verification',
    'JSON-Schema-guided information extraction','S0: Rule-Only','S1: LLM-Only',
    'S2: LLM + Schema Slice','S3: LLM + Schema Slice + Validator/Repair',
    'S4: Hybrid Backbone + Semantic Enrichment','Baselines And Comparators',
    'S0 rule-only','S1 LLM-only','S1_raw_open_llm','S1b_llm_canonicalized',
    'S4_hybrid_backbone_enrichment','invalid_direct_schema_scoring',
    'JSON Adherence','Schema Violation Rate','Triple Precision, Recall, And F1',
    'Canonicalization Yield','Repair Success Rate','Manual Semantic Correctness',
    'Falsified if',
    'reports/stages/nasa_atmonto_gold_review_session_plan.md',
    'reports/stages/nasa_atmonto_gold_review_multiround_audit.md',
    'prepare_nasa_atmonto_gold_review_session_plan.py',
    '100 sampled advisories have reviewed gold annotations',
    'Assisted Gold Adjudication Workflow','Adversarial ontology/profile review',
    'Gold truth is not created by model agreement alone',
    'multi-round and multi-perspective','extensionProbability:MODERATE->MEDIUM',
    'raw_value','value_normalization',
    'supported on the corrected stage',
    'S1b/S4 corrected-stage derived outputs',
    'supported on the reviewed 100-record sample','Semantic Stratification',
    'data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl',
    'all 288 pilot rejections','13 \`extractor_bug\` facts','275 \`profile_gap\`',
    'enter the S3 validator/repair loop as initially invalid',
    'must not be fabricated or manually filled','100 usable records before scoring',
    '\`session_01\` covers 4 records','review queue only',
]
missing = [r for r in required if r not in text]
print('MISSING:', missing)
assert not missing
print('all', len(required), 'literals present')
"
```
Expected: `all 70 literals present`, `MISSING: []`. If any missing, the `cp` in Step 1 missed content — re-check the title edit didn't drop lines.

- [ ] **Step 3: Rewire _audit_reports.py to read EXPERIMENTS.md**

Edit `src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py`. There are five `docs/experiment_protocol.md` references; replace each with `EXPERIMENTS.md`:

- Line ~460 (R0 evidence string): `"evidence": "docs/experiment_protocol.md contains pilot/feasibility boundary and bronze-until-reviewed language."` → `"evidence": "EXPERIMENTS.md contains pilot/feasibility boundary and bronze-until-reviewed language."`
- Line ~518 (R5 evidence string): `"evidence": "docs/experiment_protocol.md and reports/stages/nasa_atmonto_formal_experiment_scoring.json"` → `"evidence": "EXPERIMENTS.md and reports/stages/nasa_atmonto_formal_experiment_scoring.json"`
- Line 615 (the live `read_text`): `protocol_text = (repo_root / "docs/experiment_protocol.md").read_text(encoding="utf-8")` → `protocol_text = (repo_root / "EXPERIMENTS.md").read_text(encoding="utf-8")`
- Line 642 (returned dict field): `"protocol": "docs/experiment_protocol.md",` → `"protocol": "EXPERIMENTS.md",`
- Line 1082 (returned dict field): `"protocol": "docs/experiment_protocol.md",` → `"protocol": "EXPERIMENTS.md",`

Verify no other references remain in that file:
```bash
git grep -n "docs/experiment_protocol.md" src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py
```
Expected: empty.

- [ ] **Step 4: Rewire the protocol test to read EXPERIMENTS.md**

Edit `tests/test_nasa_atmonto_experiment_protocol.py`. Three identical reads to change:

- Line 58: `protocol = Path("docs/experiment_protocol.md").read_text(encoding="utf-8")` → `protocol = Path("EXPERIMENTS.md").read_text(encoding="utf-8")`
- Line 126: same replacement.
- Line 141: same replacement.

Verify:
```bash
git grep -n "docs/experiment_protocol.md" tests/test_nasa_atmonto_experiment_protocol.py
```
Expected: empty.

- [ ] **Step 5: Rewire the formal-experiment test fixture**

Edit `tests/test_nasa_atmonto_formal_experiment.py` lines 372–376. The current block is:
```python
        protocol_src = repo / "docs/experiment_protocol.md"
        if protocol_src.exists():
            protocol_dst = tmp_path / "docs/experiment_protocol.md"
            protocol_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(protocol_src, protocol_dst)
```
Replace with:
```python
        protocol_src = repo / "EXPERIMENTS.md"
        if protocol_src.exists():
            protocol_dst = tmp_path / "EXPERIMENTS.md"
            protocol_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(protocol_src, protocol_dst)
```

Verify:
```bash
git grep -n "docs/experiment_protocol.md" tests/test_nasa_atmonto_formal_experiment.py
```
Expected: empty.

- [ ] **Step 6: Run the two affected test files and confirm green**

Run:
```bash
uv run pytest -q tests/test_nasa_atmonto_experiment_protocol.py tests/test_nasa_atmonto_formal_experiment.py
```
Expected: all pass (baseline was 50 passed).

- [ ] **Step 7: Run ruff on the changed Python files**

Run:
```bash
uv run ruff check src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py tests/test_nasa_atmonto_experiment_protocol.py tests/test_nasa_atmonto_formal_experiment.py
```
Expected: no findings.

- [ ] **Step 8: Commit**

```bash
git add EXPERIMENTS.md src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py tests/test_nasa_atmonto_experiment_protocol.py tests/test_nasa_atmonto_formal_experiment.py
git commit -m "refactor: migrate experiment_protocol.md content to EXPERIMENTS.md and update runtime+test readers

- EXPERIMENTS.md is the new live protocol file (content migrated verbatim from docs/experiment_protocol.md so all ~70 test-required string literals survive).
- _audit_reports.py reads repo_root/EXPERIMENTS.md and emits protocol: EXPERIMENTS.md in generated report JSON.
- test_nasa_atmonto_experiment_protocol.py reads EXPERIMENTS.md at three call sites.
- test_nasa_atmonto_formal_experiment.py fixture copies EXPERIMENTS.md into tmp_path.
- docs/experiment_protocol.md is left in place for now; it is archived in a later commit.
- Generated JSON files (nasa_atmonto_formal_experiment_scoring.json, _readiness.json) still embed the old protocol path; regenerating them is deferred to a separate follow-up commit per spec Q3."
```

---

## Task 3: Populate RESEARCH_OVERVIEW, RESEARCH_QUESTIONS, HYPOTHESES (Commit 2)

**Files:**
- Modify: `RESEARCH_OVERVIEW.md` (replace stub)
- Modify: `RESEARCH_QUESTIONS.md` (replace stub)
- Modify: `HYPOTHESES.md` (replace stub)

- [ ] **Step 1: Write RESEARCH_OVERVIEW.md**

Replace the stub with content migrated from `docs/thesis_positioning.md` + `docs/research_mainline.md` + scope-lock framing from `docs/master_project_scope_lock.md`. Use this exact structure (each section's prose is taken verbatim from the named source file — do not paraphrase scope-lock constraints):

```markdown
# Research Overview

> Migrated on 2026-07-05 from `docs/thesis_positioning.md`, `docs/research_mainline.md`, and `docs/master_project_scope_lock.md` as part of the research-governance refactor (spec `docs/superpowers/specs/2026-07-05-research-governance-refactor-design.md`). Sources preserved under `docs/archive/governance_era/`.

## Research Area

- Schema-constrained, evidence-grounded information extraction.
- Agentic validation/refinement loops for KG construction.
- Source-bounded KG-RAG question answering.
- Retrospective FAA ATCSCC advisory analysis.

## Problem Statement

[Copy verbatim the "## Problem Statement" section body from docs/thesis_positioning.md, lines 5–17.]

## Locked Project Outcome

[Copy verbatim the "## Locked Project Outcome" section body from docs/master_project_scope_lock.md, lines 8–18 — including the paragraph "The ontology/profile is an engineering constraint. It is not the research object."]

## Single-Sentence Contribution

[Copy verbatim the "## Single-Sentence Contribution" section body from docs/master_project_scope_lock.md, lines 22–26.]

## Revised Thesis Claim

[Copy verbatim the "## Revised Thesis Claim" section body from docs/thesis_positioning.md, lines 20–31.]

## Thesis Story

[Copy verbatim the "## Thesis Story" section body from docs/research_mainline.md, lines 16–36, including the code block.]

## Research Scope

### In scope

[Copy verbatim the "## Minimum Deliverable Set" table from docs/master_project_scope_lock.md, lines 31–41.]

### Not in scope (Non-Goals)

[Copy verbatim the "## Non-Goals" bullet list from docs/master_project_scope_lock.md, lines 46–63, plus the closing sentence "These topics can appear in related work, limitations, or future work..."]

## Contributions

[Copy verbatim the "## Contributions" section body from docs/thesis_positioning.md, lines 59–68.]

## Evaluation Philosophy

[Copy verbatim the "## Evaluation Philosophy" section body from docs/thesis_positioning.md, lines 71–88. In the last paragraph, replace the two occurrences of `docs/experiment_protocol.md` with `EXPERIMENTS.md`. Keep `uv run aviation-ai report evaluation-protocol` unchanged.]

## Claim Safety Matrix

[Copy verbatim the "## Claim Safety Matrix" table from docs/thesis_positioning.md, lines 92–99.]

## What The Thesis Can Claim

[Copy verbatim the "## What The Thesis Can Claim" list from docs/thesis_positioning.md, lines 103–112.]

## What The Thesis Must Not Claim

[Copy verbatim the "## What The Thesis Must Not Claim" list from docs/thesis_positioning.md, lines 116–121.]

## Current Thesis-Usable Claims

[Copy verbatim the "## Current Thesis-Usable Claims" list from docs/research_mainline.md, lines 99–108.]

## Claims To Avoid

[Copy verbatim the "## Claims To Avoid" list from docs/research_mainline.md, lines 112–117.]

## SOTA Positioning

[Copy verbatim the "## SOTA Positioning" section body from docs/research_mainline.md, lines 151–167, including the table.]

## New-Idea Intake Rule

[Copy verbatim the "## New-Idea Intake Rule" section body from docs/master_project_scope_lock.md, lines 129–139, including the table and "Default decision: defer."]

## Stop Rule

[Copy verbatim the "## Stop Rule" section body from docs/master_project_scope_lock.md, lines 165–176.]

## Evidence Gaps Before Thesis Submission

[Copy verbatim the "## Evidence Gaps Before Thesis Submission" list from docs/thesis_positioning.md, lines 140–146.]
```

After writing, verify scope-lock constraints survived intact:
```bash
uv run python -c "
from pathlib import Path
text = Path('RESEARCH_OVERVIEW.md').read_text()
for s in ['Evidence-Grounded Schema-Constrained Agentic KG-RAG','The ontology/profile is an engineering constraint','Non-Goals','A full aviation ontology thesis','Default decision: defer','Stop Rule','GraphRAG universally improves Recall@k']:
    assert s in text, s
print('scope-lock constraints present')
"
```
Expected: `scope-lock constraints present`.

- [ ] **Step 2: Write RESEARCH_QUESTIONS.md with RQ1–RQ4 blocks**

Replace the stub. The RQ statements, motivation, evidence, and pass/fail criteria come from `docs/research_mainline.md` (Validation Matrix row for each RQ) and `docs/thesis_positioning.md` (RQ list). Use the guide's template:

```markdown
# Research Questions

> Migrated on 2026-07-05 from `docs/research_mainline.md`, `docs/thesis_positioning.md`, and `docs/master_project_scope_lock.md`. Sources preserved under `docs/archive/governance_era/`.

The project keeps exactly four research questions. Any additional question should be folded into one of these four, or moved to future work.

## RQ1: Schema-constrained extraction

### Description

Can schema-constrained LLM extraction produce valid and evidence-linked event records from ATCSCC advisories?

### Motivation

[From research_mainline.md thesis-story lines 16–25: advisories are "narrow but useful ... because many facts are visible in the source text and can be checked against evidence spans." Summarize in one sentence — do not invent new motivation.]

### Related Hypotheses

- H1 (schema guidance reduces structural drift after canonicalization)
- H3 (hybrid backbone + enrichment improves selected semantic predicates)

### Related Experiments

- Extraction layer: S0/S1/S1b/S2/S3/S4 over the frozen 100-record reviewed gold sample.
- Evidence: `reports/stages/nasa_atmonto_formal_experiment_scoring.md`, `reports/stages/nasa_atmonto_prediction_output_validation.md`, `reports/stages/nasa_atmonto_cq_evaluation.md`.

### Current Evidence

[From the Validation Matrix RQ1 row of research_mainline.md, the Pass criterion sentence, verbatim.]

### Status

active

## RQ2: Agentic validation-refinement

### Description

Does an agentic validation-refinement loop reduce schema violations and unsupported relations?

### Motivation

[One sentence from research_mainline.md / experiment_protocol.md: validator/refiner/critic loops make repair and rejection auditable before graph insertion. Do not invent.]

### Related Hypotheses

- H2 (validator/repair improves valid yield)

### Related Experiments

- Agentic loop: extractor / validator / refiner / critic over ATCSCC candidate facts; independent and live S5/S6 runs.
- Evidence: `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`, `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md`, `reports/stages/nasa_atmonto_agentic_loop.md`.

### Current Evidence

[Validation Matrix RQ2 row Pass criterion sentence, verbatim.]

### Status

active

## RQ3: KG-RAG grounding

### Description

Does KG-RAG improve evidence grounding and citation quality compared with vector-only RAG?

### Motivation

[One sentence from research_mainline.md / thesis_positioning.md: graph evidence is useful when it improves source-bounded answer sets, evidence traceability, citation behavior. Do not invent.]

### Related Hypotheses

- H3 (KG-RAG improves source-bounded grounding, answer-set quality, citation behavior on relation-oriented questions; vector-only can remain sufficient for simple source-local questions)

### Related Experiments

- Retrieval and answer generation: source-only, vector RAG, graph-only, token-matched GraphRAG, routed/hybrid KG-RAG.
- Evidence: `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_graph_health.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`.

### Current Evidence

[Validation Matrix RQ3 row Pass criterion sentence, verbatim.]

### Status

active

## RQ4: Failure boundary

### Description

What failure types remain, and where does human review remain necessary?

### Motivation

[One sentence: the thesis must separate automated diagnostics from human/expert review and list remaining failure types with claim impact. Do not invent.]

### Related Hypotheses

- H4 (rejection triage produces actionable engineering decisions; failure analysis separates extractor errors, profile/gold-boundary gaps, retrieval context errors, answer overreach, human-review cases)

### Related Experiments

- Reviewer-defense, answer-review, profile-decision, claim-safety audits.
- Evidence: `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md`, `reports/stages/nasa_atmonto_s7_profile_decision.md`.

### Current Evidence

[Validation Matrix RQ4 row Pass criterion sentence, verbatim.]

### Status

active
```

- [ ] **Step 3: Write HYPOTHESES.md**

Replace the stub. The falsification criteria and "Falsified if" phrase come from `docs/experiment_protocol.md` §Hypotheses And Falsification Criteria (lines 273–323). The "Falsified if" literal must be preserved (test indirectly relies on it via `experiment_protocol.md`; once that file is archived in Commit 6, the test reads EXPERIMENTS.md which already contains it — but HYPOTHESES.md should also keep it for human readability).

```markdown
# Hypotheses

> Migrated on 2026-07-05 from `docs/experiment_protocol.md` §Hypotheses And Falsification Criteria and `docs/thesis_positioning.md` §Hypotheses. Sources preserved under `docs/archive/governance_era/`.

## Hypothesis Table

| ID | Hypothesis | Related RQ | Primary comparison | Status |
|---|---|---|---|---|
| H1 | Schema guidance reduces structural drift after canonicalization. | RQ1 | S2 vs S1b | supported on the corrected stage |
| H2 | Validator/repair improves valid yield. | RQ2 | S3 vs S2 | supported on the reviewed 100-record sample |
| H3 | Hybrid backbone + enrichment improves selected semantic predicates. | RQ1 / RQ3 | S4 vs S0 for selected semantic predicates | supported on the corrected stage for the selected semantic predicate family |
| H4 | Rejection triage produces actionable engineering decisions. | RQ4 | rejection-error analysis coverage | supported at property level |

Status vocabulary: `pending`, `supported`, `rejected`, `partially_supported`, `inconclusive`, `abandoned`, `needs_replication`.

## H1: Schema Guidance Reduces Structural Drift After Canonicalization

Compared with `S1b_llm_canonicalized`, `LLM + schema slice` will reduce unsupported target-schema terms and schema violation rate.

- Primary comparison: S2 vs S1b.
- Falsified if S2 schema violation rate is not lower than S1b by at least 10 percentage points, or if bootstrap confidence intervals show no practical separation.
- Secondary failure mode: S2 achieves lower violations only by suppressing more than 25 percent of gold-supported facts relative to S1b.
- Current interpretation: supported on the corrected stage. S1 direct schema scoring remains an interface-failure diagnostic, while `S1b_llm_canonicalized` provides the comparable canonicalized baseline.

## H2: Validator/Repair Improves Valid Yield

Compared with `LLM + schema slice`, `LLM + schema slice + validator/repair` will increase structurally accepted facts while preserving manual semantic correctness.

- Primary comparison: S3 vs S2.
- Falsified if S3 structural repair success rate is below 15 percent of facts that enter the S3 validator/repair loop as initially invalid, or if S3 manual semantic correctness is more than 5 percentage points lower than S2.

## H3: Hybrid Backbone Plus Enrichment Improves Selected Semantic Predicates

The next candidate system should combine the deterministic ATCSCC parser with schema-constrained LLM enrichment.

- Primary comparison: S4 vs S0 for selected semantic predicates where S0 is weak, especially `reRouteReason`, `reRouteType`, and `implementationStatus`.
- Preservation criterion: S4 must preserve S0 F1 for deterministic fields such as `advisoryNumber`, `issuedTime`, `effectiveStartTime`, and `effectiveEndTime` within a pre-registered tolerance.
- Falsified if S4 does not improve the selected semantic predicate family or if it materially harms deterministic-field F1.
- Current interpretation: supported on the corrected stage for the selected semantic predicate family. This is not an aggregate end-to-end GraphRAG or general aviation KG claim.

## H4: Rejection Triage Produces Actionable Engineering Decisions

Most rejected facts should be classifiable into a small set of actionable property-level causes.

- Primary evidence: `reports/stages/nasa_atmonto_rejection_error_analysis.md`.
- Falsified if more than 20 percent of rejected facts remain `manual_review_required` after review, or if a proposed profile extension cannot be tied to source evidence and a NASA ATMONTO term.
```

- [ ] **Step 4: Sanity-check the three files**

Run:
```bash
wc -l RESEARCH_OVERVIEW.md RESEARCH_QUESTIONS.md HYPOTHESES.md
grep -c "Falsified if" HYPOTHESES.md
grep -c "### " RESEARCH_QUESTIONS.md
```
Expected: three non-trivial line counts; `Falsified if` appears 4 times in HYPOTHESES.md; RESEARCH_QUESTIONS.md has 6 `### ` subheads per RQ × 4 RQs = 24.

- [ ] **Step 5: Commit**

```bash
git add RESEARCH_OVERVIEW.md RESEARCH_QUESTIONS.md HYPOTHESES.md
git commit -m "refactor: migrate thesis/research_mainline into RESEARCH_OVERVIEW/QUESTIONS/HYPOTHESES

- RESEARCH_OVERVIEW.md: problem statement, locked outcome, single-sentence contribution, revised claim, thesis story, scope/non-goals, contributions, evaluation philosophy, claim-safety matrix, can/must-not-claim, SOTA positioning, intake/stop rules. Content migrated verbatim from thesis_positioning.md + research_mainline.md + master_project_scope_lock.md; the only edit is retargeting docs/experiment_protocol.md -> EXPERIMENTS.md inside the Evaluation Philosophy paragraph.
- RESEARCH_QUESTIONS.md: RQ1-RQ4 in the guide's Description/Motivation/Related Hypotheses/Related Experiments/Current Evidence/Status template.
- HYPOTHESES.md: H1-H4 table + per-hypothesis detail with falsification criteria preserved verbatim (Falsified if literals survive)."
```

---

## Task 4: Populate RESULTS, ARTIFACT_INDEX, DECISION_LOG, REPRODUCIBILITY (Commit 3)

**Files:**
- Modify: `RESULTS.md`, `ARTIFACT_INDEX.md`, `DECISION_LOG.md`, `REPRODUCIBILITY.md` (replace stubs)

- [ ] **Step 1: Write RESULTS.md**

Replace the stub. Content comes from `docs/master_project_scope_lock.md` §Minimum Deliverable Set (table at lines 31–41) and `docs/documentation_map.md` §Experiment Evidence (table at lines 53–61). Use Observation / Evidence / Interpretation / Confidence columns as the guide §4.2 specifies:

```markdown
# Results

> Migrated on 2026-07-05 from `docs/master_project_scope_lock.md` §Minimum Deliverable Set and `docs/documentation_map.md` §Experiment Evidence. Sources preserved under `docs/archive/governance_era/`. No new claims — every row points at an existing evidence artifact.

## Deliverables And Evidence

| Deliverable | Observation | Evidence (artifact) | Interpretation | Confidence |
|---|---|---|---|---|
| Frozen ATCSCC data profile | Source family and format are documented and frozen. | `reports/stages/atcscc_data_format_and_processing_flow.md` | Defines the retrospective corpus and source-record shape. | high |
| Lightweight ATCSCC schema/profile | Application schema constrains accepted event fields and predicates; profile gaps documented. | `reports/stages/atcscc_ontology_profile_overview.md` | Engineering constraint, not full ontology. | high |
| Schema-constrained extraction experiment | Rule / LLM / schema / repair / hybrid extraction scored on the reviewed 100-record sample. | `reports/stages/nasa_atmonto_formal_experiment_scoring.md` | Layered metrics; structural acceptance is not semantic correctness. | medium (semantic layer requires reviewed gold) |
| Agentic validation/refinement loop | Validator/refiner/critic reduces specific schema and support failures. | `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` | Auditable repair/rejection; not autonomous ontology construction. | medium |
| KG-RAG answer-generation comparison | Vector / graph / hybrid / routed retrieval compared for source-grounded answers. | `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md` | KG-RAG improves some source-bounded grounding diagnostics; vector-only remains a fair baseline for source-local questions. | medium |
| Failure and claim-safety audit | Remaining failures categorized; human-review boundary explicit. | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md` | Automated diagnostics separated from human/expert review. | high (process claim) |
| Thesis synthesis | Evidence turned into the research story. | `reports/stages/nasa_atmonto_experiment_chapter_draft.md` | Draft; final acceptance pending submission gates. | low (draft) |

## Confidence Levels

| Level | Meaning |
|---|---|
| `low` | single observation or draft state |
| `medium` | repeated observation or partial evidence layer |
| `high` | baseline- or repetition-supported, or process/protocol claim |

## Evidence Layer Map

[Copy verbatim the "## Experiment Evidence" table from docs/documentation_map.md lines 53–61 — Extraction scoring / CQ-query evaluation / Agentic loop / Retrieval and graph health / Answer generation / Failure review / SOTA-readiness audit rows. This is the canonical layer→report map.]
```

- [ ] **Step 2: Write ARTIFACT_INDEX.md**

Replace the stub. Content migrates from `docs/documentation_map.md` §Context Inventory (Tracked File-Family Snapshot, Tracked But Non-Default Families, Current-Use Families at lines 161–187), §Ignored Local Material (lines 121–126), and §Artifact Management Policy (lines 273–293):

```markdown
# Artifact Index

> Migrated on 2026-07-05 from `docs/documentation_map.md` Context Inventory, Ignored Local Material, and Artifact Management Policy sections. Source preserved under `docs/archive/governance_era/documentation_map.md`.

## Artifact Type Vocabulary

`code`, `dataset`, `model`, `notebook`, `figure`, `screenshot`, `prompt`, `generated_asset`, `log`, `report`, `configuration`.

## Tracked File-Family Snapshot

[Copy verbatim the "### Tracked File-Family Snapshot" table from docs/documentation_map.md lines 161–168.]

## Tracked But Non-Default Families

[Copy verbatim the "### Tracked But Non-Default Families" table from docs/documentation_map.md lines 171–178.]

## Current-Use Families

[Copy verbatim the "### Current-Use Families" table from docs/documentation_map.md lines 181–187.]

## Ignored Local Material

[Copy verbatim the "### Ignored Local Material" table from docs/documentation_map.md lines 121–126 — reports/archive/, outputs/, paper_figure_gallery.html rows.]

## Artifact Management Policy

[Copy verbatim the "## Artifact Management Policy" section body from docs/documentation_map.md lines 273–293.]

## Audit Commands

[Copy verbatim the "### Audit Commands" bash block from docs/documentation_map.md lines 149–158.]
```

- [ ] **Step 3: Write DECISION_LOG.md**

Replace the stub. Seed with the scope-lock decisions, each as a D00N entry. The decisions are derived from `docs/master_project_scope_lock.md`:

```markdown
# Decision Log

> Seeded on 2026-07-05 from the project scope lock (`docs/master_project_scope_lock.md`) and the documentation map tiering rules. Each entry records a structural decision and its consequences. Future significant choices (tool changes, abandoned experiments, model selection, refactor scope) should be appended here.

## D001 — Single thesis-grade system study

### Date

(see git history of master_project_scope_lock.md)

### Context

The repository had accumulated multiple parallel experimental tracks (PHAK ontology, web demo, chunking experiments, multi-source pilots).

### Decision

Freeze the project outcome as one bounded thesis-grade system study: Evidence-Grounded Schema-Constrained Agentic KG-RAG for FAA ATCSCC Advisories.

### Reason

- Prevents research support work from expanding into parallel subprojects.
- Keeps thesis scope defensible.

### Alternatives Considered

- Multi-thesis split (ontology + RAG + agent loop as separate studies).
- Open-ended benchmark project.

### Consequences

Pro: clear stop rule and minimum deliverable set.
Con: any new idea must fit a locked deliverable or be deferred.

## D002 — Exactly four research questions

### Date

(same as above)

### Context

Multiple candidate RQs were circulating across stage reports.

### Decision

Keep exactly four RQs: schema-constrained extraction, agentic validation-refinement, KG-RAG grounding, failure boundary. Any additional question must fold into one of these four or move to future work.

### Reason

- Keeps the evaluation layered and bounded.
- Prevents open-ended benchmark creep.

### Alternatives Considered

- Adding a fifth RQ for cross-source transfer.
- Treating ontology completeness as an RQ.

### Consequences

Pro: each RQ has an experiment layer, metrics, artifacts, pass/fail interpretation.
Con: cross-source and ontology-completeness work is future work only.

## D003 — Layered metrics, no overall score

### Date

(same as above)

### Context

A single mixed score would let one strong layer hide a weak one.

### Decision

Report layered metrics: extraction, evidence, agentic-loop, retrieval/answer, boundary. No mixed overall score.

### Reason

- Recall@5, provenance completeness, and unsupported-claim rate have different denominators and risk profiles.

### Alternatives Considered

- Weighted average score.
- Single "KG-RAG quality" number.

### Consequences

Pro: tradeoffs are visible; GraphRAG cannot be claimed to improve Recall@k without the retrieval-result support.
Con: results table is wider and harder to compress into one slide number.

## D004 — PHAK-era evidence is historical

### Date

2026-05/06 archive wave (see git log)

### Context

Early PHAK Chapter 4 ontology, chunking, and web-demo reports used different framing than the current ATCSCC line.

### Decision

Treat PHAK, web-demo, chunking-era, and old final-report docs as historical. They may be cited for method evolution or negative results, but cannot override current ATCSCC framing.

### Reason

- Prevents ontology-first framing from leaking into the schema-constrained KG-RAG thesis.

### Alternatives Considered

- Delete PHAK-era files.
- Keep PHAK-era as primary track.

### Consequences

Pro: thesis story stays coherent.
Con: some reuse requires manual rewrite into ATCSCC wording.

## D005 — Source families stay separate

### Date

(same as D001)

### Context

ATCSCC advisories, FAA/NASA reference PDFs, NASR/facility data, weather, and transfer-pilot corpora have different shapes and evaluation protocols.

### Decision

Keep source families separate. Do not merge them into one semantic-F1 table unless a source-specific profile and gold/evaluation protocol exists for each family.

### Reason

- A shared F1 table would mix different denominators and tasks.

### Alternatives Considered

- Unified cross-source extraction metric.

### Consequences

Pro: each source family gets a task-relative correctness claim.
Con: cross-source comparison is limited to structural conformance, evidence grounding, and canonicalization yield.

## D006 — Documentation tiers and tier maintenance rules

### Date

(same as documentation_map.md)

### Context

The repo mixes canonical framing, protocols, current evidence, source explainers, paper analyses, historical artifacts, and generated side artifacts.

### Decision

Use the six documentation tiers (T0–T6) from `docs/documentation_map.md` §Document Tiers. New material routes per the "Where New Documents Should Go" table.

### Alternatives Considered

- Flat docs/ namespace.
- Per-date organization.

### Consequences

Pro: clear precedence chain (now anchored at RESEARCH_AUDIT.md after this refactor).
Con: tier discipline requires upkeep; stale tier assignments cause context pollution.
```

- [ ] **Step 4: Write REPRODUCIBILITY.md**

Replace the stub. Content comes from `docs/experiment_protocol.md` §Recommended Regeneration Commands (lines 1086–1099), `docs/thread_handoff.md` §Verification Defaults (lines 90–93), and `README.md` §Quick Start:

```markdown
# Reproducibility

> Migrated on 2026-07-05 from `docs/experiment_protocol.md` §Recommended Regeneration Commands, `docs/thread_handoff.md` §Verification Defaults, and `README.md` §Quick Start. Sources preserved under `docs/archive/governance_era/`.

## Environment

- OS: macOS / Linux (project developed on darwin arm64).
- Python: see `pyproject.toml` `requires-python`.
- Package manager: `uv`.
- Optional extras: `dev`, `graphrag`, `web`.

## Installation

```bash
uv sync --extra dev --extra graphrag
```

## Run Main Prototype

[If README.md Quick Start lists a prototype/dashboard command, copy it here verbatim. Otherwise omit this subsection.]

## Run Experiments

The full formal-experiment procedure lives in `EXPERIMENTS.md` §Experimental Procedure. The regeneration commands below refresh the thesis-evidence reports:

```bash
uv sync --extra dev --extra graphrag
uv run aviation-ai report thesis-claims
uv run aviation-ai report nasa-atmonto-answer-generation
uv run python scripts/build_nasa_atmonto_sota_goal_audit.py
uv run python scripts/build_nasa_atmonto_reviewer_defense_audit.py
uv run ruff check .
uv run pytest -q
```

## Expected Outputs

After regeneration, the following tracked artifacts refresh:

- `reports/stages/thesis_claims_review.md` (+ `.json`)
- `reports/stages/nasa_atmonto_answer_generation.md` (+ `.json`)
- `reports/stages/nasa_atmonto_sota_goal_audit.md`
- `reports/stages/nasa_atmonto_reviewer_defense_audit.md`

The formal-scoring JSON (`reports/stages/nasa_atmonto_formal_experiment_scoring.json`) and readiness JSON embed a `protocol` field that now reads `EXPERIMENTS.md`; regenerating those JSONs is a separate follow-up step (spec §8 follow-up commit).

## Verification Defaults

- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Report-generation changes: run the relevant command above and inspect the generated diff before committing.

## Known Issues

- PDF source-family B (FAA/NASA reference PDFs) is a planned second pilot; its extraction pipeline is not in the regeneration commands above.
- LLM-dependent steps (S1/S2/S3 prediction runs) require API access; the regeneration commands above cover only deterministic report builders.
```

- [ ] **Step 5: Sanity-check the four files**

Run:
```bash
wc -l RESULTS.md ARTIFACT_INDEX.md DECISION_LOG.md REPRODUCIBILITY.md
grep -c "^## D00" DECISION_LOG.md
grep -c "uv run" REPRODUCIBILITY.md
```
Expected: four non-trivial counts; six `## D00N` entries in DECISION_LOG.md; at least six `uv run` lines in REPRODUCIBILITY.md.

- [ ] **Step 6: Commit**

```bash
git add RESULTS.md ARTIFACT_INDEX.md DECISION_LOG.md REPRODUCIBILITY.md
git commit -m "refactor: migrate documentation_map/scope-lock into RESULTS/ARTIFACT_INDEX/DECISION_LOG/REPRODUCIBILITY

- RESULTS.md: deliverables table rewritten as Observation/Evidence/Interpretation/Confidence rows + evidence-layer map from documentation_map.md. No new claims.
- ARTIFACT_INDEX.md: tracked/non-default/current-use families, ignored local material, artifact management policy, audit commands.
- DECISION_LOG.md: D001-D006 seeded from scope-lock decisions (single study; four RQs; layered metrics; PHAK-era historical; source families separate; doc tiers).
- REPRODUCIBILITY.md: environment, install, regeneration commands (from experiment_protocol.md), verification defaults (from thread_handoff.md)."
```

---

## Task 5: Populate RESEARCH_AUDIT and TODO (Commit 4)

**Files:**
- Modify: `RESEARCH_AUDIT.md`, `TODO.md` (replace stubs)

- [ ] **Step 1: Write RESEARCH_AUDIT.md as the new entry point**

Replace the stub. Capture the project snapshot dynamically:

```bash
LAST_COMMIT=$(git rev-parse HEAD)
BRANCH=$(git branch --show-current)
DATE=$(date +%Y-%m-%d)
```

Then write the file body:
```markdown
# Research Audit

> This is the new thread entry point. It replaces the start-here role of `docs/thread_handoff.md` and `docs/documentation_map.md` (both preserved under `docs/archive/governance_era/`). For a new thread, read this file first, then follow the navigation map below.

## 1. Project Snapshot

- Audit date: <DATE>
- Current branch: <BRANCH>
- Last commit: <LAST_COMMIT>
- Main language: Python (`uv` workspace).
- Main framework: custom CLI (`aviation-ai`) over `pyproject.toml`.
- Current thesis line: Agentic KG-RAG for evidence-grounded question answering over retrospective FAA ATCSCC advisories.
- Current status: writing-up phase. Schema, extraction, agentic loop, KG-RAG, and failure-audit evidence collected; thesis chapter draft in progress.

## 2. Navigation Map

Read in this order when entering the project:

| Order | File | Purpose |
|---|---|---|
| 1 | `RESEARCH_AUDIT.md` (this file) | Project snapshot and navigation. |
| 2 | `RESEARCH_OVERVIEW.md` | Problem, claim, scope, contributions, claim-safety matrix, SOTA positioning. |
| 3 | `RESEARCH_QUESTIONS.md` | RQ1–RQ4 in Description/Motivation/Related Hypotheses/Related Experiments/Current Evidence/Status form. |
| 4 | `HYPOTHESES.md` | H1–H4 table + falsification criteria. |
| 5 | `EXPERIMENTS.md` | Full formal-experiment protocol: systems, gold, metrics, procedure, completion gate, layered evaluation. |
| 6 | `RESULTS.md` | Deliverables and evidence rows with Observation/Evidence/Interpretation/Confidence. |
| 7 | `ARTIFACT_INDEX.md` | Tracked, non-default, and ignored artifact families; artifact management policy. |
| 8 | `DECISION_LOG.md` | Structural decisions D001+ with context/reason/alternatives/consequences. |
| 9 | `REPRODUCIBILITY.md` | Environment, install, regeneration commands, verification defaults. |
| 10 | `TODO.md` | Active task queue and P0–P4 backlog. |

## 3. Six-Question File Rubric

When looking at any file in this repo, ask:

1. Which research question does this file serve?
2. Which hypothesis does it support?
3. Which experiment is it part of?
4. What are its inputs and outputs?
5. What evidence does it produce?
6. Should it be kept, archived, or deleted?

If a file cannot answer these, treat it as an `unknown artifact` — do not delete it; move it under `archive/unknown/` and note it in `ARTIFACT_INDEX.md`.

## 4. Default Context For New Threads

- Read this file, then `RESEARCH_OVERVIEW.md`, then `ARTIFACT_INDEX.md`. Load additional files only when the task needs their layer.
- Keep the active plugin/skill surface minimal. Use task-specific skills only when their trigger matches the current action.
- PHAK, web-demo, chunking-era, and old final-report docs are historical unless explicitly requested.
- Avoid unsupported claims: full aviation ontology completeness, live ATC decision support, external expert certification, or universal GraphRAG superiority.

## 5. Source Boundaries

Keep source families separate unless a source-specific profile and evaluation protocol exists: ATCSCC advisories; FAA/NASA reference PDFs; NASR/facility data; weather data; transfer pilots or non-ATCSCC corpora.

## 6. Verification Defaults

- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Report-generation changes: run the relevant command in `REPRODUCIBILITY.md` and inspect the generated diff before committing.

## 7. Git And Publishing

- Publishing remotes: `origin` is GitLab; `github` is GitHub.
- When a branch should be shared, push both remotes unless the user requests one remote only.
- After merging into `main`, push `main` to both remotes and verify local `main`, `origin/main`, and `github/main` resolve to the intended commit.
```

(Substitute `<DATE>`, `<BRANCH>`, `<LAST_COMMIT>` with the captured values.)

- [ ] **Step 2: Write TODO.md by migrating TASKS.md**

Replace the stub. Migrate the structure of `TASKS.md` but retitle to the guide's TODO voice. Keep every task entry verbatim (do not silently drop the open `[ ]` items):

```markdown
# TODO

> Migrated on 2026-07-05 from `TASKS.md` (preserved under `docs/archive/governance_era/TASKS.md`). Concrete execution tasks live here. Durable project outcomes and scope boundaries live in `GOALS.md`. A task should be small enough to finish, verify, and check off. When a task produces evidence, attach the report or artifact path.

Last updated: 2026-05-30.

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Done
- `[!]` Blocked or needs decision

## Active Task Queue

[Copy verbatim the "## Active Task Queue" numbered list and the "Related goals" line from TASKS.md lines 18–24.]

## P0 - Immediate Reproducibility Tasks

[Copy verbatim lines 28–94 of TASKS.md — the entire P0 section including Related goals line, all [x] items, and their evidence/acceptance sub-bullets. The only edit: do not change any task text.]

## P1 - Evaluation Quality Tasks

[Copy verbatim lines 96–125 of TASKS.md.]

## P2 - Final Submission Tasks

[Copy verbatim lines 127–164 of TASKS.md.]

## P3 - Experimental Expansion Tasks

[Copy verbatim lines 166–245 of TASKS.md.]

## P4 - Automation And GitLab Tasks

[Copy verbatim lines 247–258 of TASKS.md.]

## Maintenance Rules

[Copy verbatim lines 260–266 of TASKS.md.]
```

- [ ] **Step 3: Sanity-check**

Run:
```bash
wc -l RESEARCH_AUDIT.md TODO.md
grep -c "^## " RESEARCH_AUDIT.md
grep -c "^## " TODO.md
test -s RESEARCH_AUDIT.md && test -s TODO.md && echo OK
```
Expected: both files non-trivial; RESEARCH_AUDIT.md has ≥7 `## ` sections; TODO.md has the Status Legend + Active + P0–P4 + Maintenance sections (≥7).

- [ ] **Step 4: Commit**

```bash
git add RESEARCH_AUDIT.md TODO.md
git commit -m "refactor: add RESEARCH_AUDIT entry point; migrate TASKS to TODO

- RESEARCH_AUDIT.md: new thread entry point. Project snapshot (date/branch/last-commit captured dynamically), navigation map to the other nine root files, six-question file rubric, default context, source boundaries, verification defaults, git/publishing rules. Replaces the start-here role of thread_handoff.md and documentation_map.md.
- TODO.md: TASKS.md content migrated verbatim into the guide's TODO voice; Status Legend, Active Task Queue, P0-P4, Maintenance Rules preserved. TASKS.md itself is archived in a later commit."
```

---

## Task 6: Retarget canonical-doc links across the repo (Commit 5)

**Files (modify in place — link retargets only):**
- `AGENTS.md`, `CLAUDE.md`, `README.md`, `GOALS.md`
- `RESEARCH_OVERVIEW.md` — retarget spine-path references inside verbatim-migrated sections (Minimum Deliverable Set "Thesis synthesis" row; Stop Rule items 1–2) per spec §7.1 retarget table. These were carried verbatim from source during Task 3 and would dangle after Commit 6 archives the spine.
- `docs/thesis_writing_spine.md`, `docs/research_paper_analysis_protocol.md`, `docs/atcscc_agent_architecture.md`, `docs/pipeline_authority_model.md`
- `reports/stages/index.md`, `reports/final/README.md`, `reports/final/atcscc_thesis_report.md`, `reports/final/atcscc_thesis_report_outline.md`, `reports/final/atcscc_defense_deck_outline.md`, `reports/final/atcscc_agent_plan_storyboard.md`, `reports/final/figure_descriptions.md`
- `reports/stages/thesis_claims_review.md`, `reports/stages/thesis_claims_review.json`
- `reports/stages/nasa_atmonto_competency_questions.md`
- `reports/stages/nasa_atmonto_formal_experiment_readiness.md`, `reports/stages/nasa_atmonto_formal_experiment_readiness.json`
- `reports/stages/nasa_atmonto_formal_experiment_remediation_plan.md`
- `reports/stages/nasa_atmonto_formal_experiment_scoring.md`, `reports/stages/nasa_atmonto_formal_experiment_scoring.json`, `reports/stages/nasa_atmonto_formal_experiment_scoring_gpt-5.4-mini_baseline.md`, `reports/stages/nasa_atmonto_formal_experiment_scoring_gpt-5.4-mini_baseline.json`
- `reports/stages/nasa_atmonto_gold_review_multiround_audit.md`
- `src/aviation_agentic_ai/reporting/thesis_claims.py`

The retarget table (from spec §7.1):

| Old path | New target |
|---|---|
| `docs/thread_handoff.md` | `RESEARCH_AUDIT.md` |
| `docs/master_project_scope_lock.md` | `DECISION_LOG.md` (primary) and `RESEARCH_OVERVIEW.md` |
| `docs/documentation_map.md` | `ARTIFACT_INDEX.md` (primary) and `RESEARCH_AUDIT.md` |
| `docs/research_mainline.md` | `RESEARCH_OVERVIEW.md` and `RESEARCH_QUESTIONS.md` |
| `docs/thesis_positioning.md` | `RESEARCH_OVERVIEW.md` |
| `docs/experiment_protocol.md` | `EXPERIMENTS.md` |
| `TASKS.md` | `TODO.md` |

Because most references should go to a single primary target, the rule for each replacement is: replace the old path string with the primary target listed first in the table. Where context clearly calls for a specific secondary target (e.g. a sentence about RQs), use the secondary. When unsure, use the primary.

- [ ] **Step 1: Rewrite AGENTS.md Default Context paragraph**

Edit `AGENTS.md` lines 7–17. Replace the existing Default Context bullet block:

Old:
```
- For a new thread, start from `docs/thread_handoff.md`, then
  `docs/master_project_scope_lock.md` and `docs/documentation_map.md`
  (which absorbs the former context-hygiene audit, maintenance guide, and
  tracked-context inventory).
```

New:
```
- For a new thread, start from `RESEARCH_AUDIT.md` (project snapshot and
  navigation map), then `RESEARCH_OVERVIEW.md` and `ARTIFACT_INDEX.md`
  (which absorbs the former context-hygiene audit, maintenance guide, and
  tracked-context inventory).
```

Leave the rest of `AGENTS.md` unchanged in this step except for any other spine path references — verify with the grep in Step 8.

- [ ] **Step 2: Rewrite CLAUDE.md to mirror AGENTS.md**

Edit `CLAUDE.md` lines 7–10 (the Current Scope pointers). Apply the same path replacements as Step 1.

- [ ] **Step 3: Retarget README.md spine links**

Use `Edit` (or `replace_all`) to replace each spine path in `README.md`. Lines known to contain spine refs: 45–49, 76, 182, 364, 404, 407, 456. For each:

- `docs/thesis_positioning.md` → `RESEARCH_OVERVIEW.md`
- `docs/research_mainline.md` → `RESEARCH_OVERVIEW.md` (or `RESEARCH_QUESTIONS.md` if the surrounding sentence is specifically about RQs)
- `docs/experiment_protocol.md` → `EXPERIMENTS.md`
- `docs/documentation_map.md` → `ARTIFACT_INDEX.md`
- `docs/master_project_scope_lock.md` → `DECISION_LOG.md`
- `docs/thread_handoff.md` → `RESEARCH_AUDIT.md`

Verify:
```bash
git grep -nE "docs/(thread_handoff|master_project_scope_lock|documentation_map|research_mainline|thesis_positioning|experiment_protocol)\.md" README.md
```
Expected: empty.

- [ ] **Step 4: Retarget GOALS.md**

Edit `GOALS.md` lines 116 and 233: `docs/thesis_positioning.md` → `RESEARCH_OVERVIEW.md`. Verify:
```bash
git grep -nE "docs/(thread_handoff|master_project_scope_lock|documentation_map|research_mainline|thesis_positioning|experiment_protocol)\.md" GOALS.md
```
Expected: empty.

- [ ] **Step 5: Retarget the remaining docs/ files**

Edit each:
- `docs/thesis_writing_spine.md` lines 4–5: replace spine refs per the table.
- `docs/research_paper_analysis_protocol.md` lines 153–154: `docs/experiment_protocol.md` → `EXPERIMENTS.md`.
- `docs/atcscc_agent_architecture.md` lines 30, 687: `docs/thesis_positioning.md` → `RESEARCH_OVERVIEW.md`.
- `docs/pipeline_authority_model.md` line 49: spine ref → primary target.

Verify:
```bash
git grep -nE "docs/(thread_handoff|master_project_scope_lock|documentation_map|research_mainline|thesis_positioning|experiment_protocol)\.md" docs/thesis_writing_spine.md docs/research_paper_analysis_protocol.md docs/atcscc_agent_architecture.md docs/pipeline_authority_model.md
```
Expected: empty.

- [ ] **Step 6: Retarget reports/final/ and reports/stages/ files**

Apply the retarget table to each file listed in the task header. Work file by file. For the JSON files (`thesis_claims_review.json`, `nasa_atmonto_formal_experiment_readiness.json`, `nasa_atmonto_formal_experiment_scoring.json`, gpt-5.4-mini variant), the references are typically inside `source` / `evidence` / `protocol` string fields — replace the path string in place.

Special note for `reports/stages/nasa_atmonto_formal_experiment_scoring.json` and the gpt-5.4-mini variant: these JSONs may also contain a top-level `"protocol": "docs/experiment_protocol.md"` field. Per spec Q3 (deferred JSON regeneration), do **not** regenerate the JSON. But because we are editing the JSON in this commit to retarget *link references*, also update the `"protocol"` field to `"EXPERIMENTS.md"` for consistency — this is a hand-edit, not a regeneration, and the diff will be auditable. (The follow-up regen commit later will confirm the generator produces the same value.)

If, on inspection, a JSON's `"protocol"` field is the *only* `docs/experiment_protocol.md` reference in that file, this hand-edit is the whole change for that file.

- [ ] **Step 7: Retarget src/aviation_agentic_ai/reporting/thesis_claims.py**

Edit line 475: replace the spine path reference with its primary target. Verify:
```bash
git grep -nE "docs/(thread_handoff|master_project_scope_lock|documentation_map|research_mainline|thesis_positioning|experiment_protocol)\.md" src/aviation_agentic_ai/reporting/thesis_claims.py
```
Expected: empty.

- [ ] **Step 8: Confirm no live spine refs remain outside archives**

Run:
```bash
git grep -nE "docs/(thread_handoff|master_project_scope_lock|documentation_map|research_mainline|thesis_positioning|experiment_protocol)\.md" \
  | grep -vE "^docs/archive/|^reports/phak_era_archive/"
```
Expected: empty. (Any remaining hits must be inside `docs/archive/` or `reports/phak_era_archive/`, which are intentionally left stale for provenance.)

Also confirm `TASKS.md` has no remaining live inbound references that should now point at `TODO.md`:
```bash
git grep -nE "(^|[^/])TASKS\.md" -- AGENTS.md CLAUDE.md README.md GOALS.md docs reports src tests 2>/dev/null | grep -vE "^docs/archive/|^reports/phak_era_archive/|^TASKS.md:"
```
Expected: empty (or only the `TASKS.md:` self-line).

- [ ] **Step 9: Run full test suite + ruff**

Run:
```bash
uv run ruff check .
uv run pytest -q
```
Expected: ruff clean, all tests pass (baseline 50 in the two protocol tests + the rest of the suite).

- [ ] **Step 10: Commit**

```bash
git add AGENTS.md CLAUDE.md README.md GOALS.md \
  docs/thesis_writing_spine.md docs/research_paper_analysis_protocol.md docs/atcscc_agent_architecture.md docs/pipeline_authority_model.md \
  reports/stages/index.md reports/final/README.md reports/final/atcscc_thesis_report.md reports/final/atcscc_thesis_report_outline.md reports/final/atcscc_defense_deck_outline.md reports/final/atcscc_agent_plan_storyboard.md reports/final/figure_descriptions.md \
  reports/stages/thesis_claims_review.md reports/stages/thesis_claims_review.json \
  reports/stages/nasa_atmonto_competency_questions.md \
  reports/stages/nasa_atmonto_formal_experiment_readiness.md reports/stages/nasa_atmonto_formal_experiment_readiness.json \
  reports/stages/nasa_atmonto_formal_experiment_remediation_plan.md \
  reports/stages/nasa_atmonto_formal_experiment_scoring.md reports/stages/nasa_atmonto_formal_experiment_scoring.json reports/stages/nasa_atmonto_formal_experiment_scoring_gpt-5.4-mini_baseline.md reports/stages/nasa_atmonto_formal_experiment_scoring_gpt-5.4-mini_baseline.json \
  reports/stages/nasa_atmonto_gold_review_multiround_audit.md \
  src/aviation_agentic_ai/reporting/thesis_claims.py
git commit -m "refactor: retarget canonical-doc links to new root-level research files

- AGENTS.md/CLAUDE.md Default Context now points at RESEARCH_AUDIT.md -> RESEARCH_OVERVIEW.md -> ARTIFACT_INDEX.md.
- README.md, GOALS.md, docs/thesis_writing_spine.md, docs/research_paper_analysis_protocol.md, docs/atcscc_agent_architecture.md, docs/pipeline_authority_model.md: spine paths retargeted.
- reports/stages/index.md, reports/final/*, reports/stages/thesis_claims_review.*, reports/stages/nasa_atmonto_*formal_experiment_*, reports/stages/nasa_atmonto_competency_questions.md, reports/stages/nasa_atmonto_gold_review_multiround_audit.md: spine paths retargeted.
- src/aviation_agentic_ai/reporting/thesis_claims.py: spine path retargeted.
- nasa_atmonto_formal_experiment_scoring.json (+ gpt-5.4-mini variant) and _readiness.json: hand-edited the protocol field to EXPERIMENTS.md for consistency with the link retarget; full JSON regeneration is still deferred to a separate follow-up commit per spec Q3.
- Archived paths under docs/archive/ and reports/phak_era_archive/ are intentionally left with stale links for provenance."
```

---

## Task 7: Archive the old docs/ spine (Commit 6)

**Files:**
- Move: six docs/ spine files + `TASKS.md` into `docs/archive/governance_era/`
- Create: `docs/archive/governance_era/README.md`

- [ ] **Step 1: Create the archive directory and move the spine files**

Run:
```bash
mkdir -p docs/archive/governance_era
git mv docs/thread_handoff.md            docs/archive/governance_era/thread_handoff.md
git mv docs/master_project_scope_lock.md docs/archive/governance_era/master_project_scope_lock.md
git mv docs/documentation_map.md         docs/archive/governance_era/documentation_map.md
git mv docs/research_mainline.md         docs/archive/governance_era/research_mainline.md
git mv docs/thesis_positioning.md        docs/archive/governance_era/thesis_positioning.md
git mv docs/experiment_protocol.md       docs/archive/governance_era/experiment_protocol.md
git mv TASKS.md                          docs/archive/governance_era/TASKS.md
```

- [ ] **Step 2: Write docs/archive/governance_era/README.md**

```markdown
# Governance Era Archive

These files were the canonical project-governance spine until the 2026-07-05 research-governance refactor (spec: `docs/superpowers/specs/2026-07-05-research-governance-refactor-design.md`, plan: `docs/superpowers/plans/2026-07-05-research-governance-refactor.md`).

## What was archived

| Archived file | Superseded by |
|---|---|
| `thread_handoff.md` | `RESEARCH_AUDIT.md` (entry-point role) |
| `master_project_scope_lock.md` | `DECISION_LOG.md` (decisions) + `RESEARCH_OVERVIEW.md` (scope/contributions/non-goals) |
| `documentation_map.md` | `ARTIFACT_INDEX.md` (artifact inventory + policy) + `RESEARCH_AUDIT.md` (start-here role) |
| `research_mainline.md` | `RESEARCH_OVERVIEW.md` (story/claims) + `RESEARCH_QUESTIONS.md` (RQs) |
| `thesis_positioning.md` | `RESEARCH_OVERVIEW.md` |
| `experiment_protocol.md` | `EXPERIMENTS.md` (protocol) + `REPRODUCIBILITY.md` (regeneration) + `HYPOTHESES.md` (H1–H4) |
| `TASKS.md` | `TODO.md` |

## Why kept

These files are preserved for provenance. They document the scope-lock decisions, document-precedence chain, and protocol evolution that the current root-level files summarize. They may also retain internal cross-links to other archived paths; those links are intentionally left stale.

## What to read instead

Start at `RESEARCH_AUDIT.md` at the repository root, then follow its navigation map. Do not link new content to the files in this directory.

## Runtime note

`src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py` previously read `docs/experiment_protocol.md` at runtime; it now reads `EXPERIMENTS.md`. The literal string `docs/experiment_protocol.md` still appears inside some archived `reports/phak_era_archive/` JSON sources and inside this directory's own files; those are not runtime paths and are left as-is.
```

- [ ] **Step 3: Verify the runtime read still resolves**

The code reads `repo_root / "EXPERIMENTS.md"`. Confirm the file is at the root and the archived copy is not in the way:
```bash
test -f EXPERIMENTS.md && echo "root EXPERIMENTS.md OK"
test -f docs/archive/governance_era/experiment_protocol.md && echo "archived copy OK"
test ! -f docs/experiment_protocol.md && echo "old path removed OK"
```
Expected: all three print OK.

- [ ] **Step 4: Run full verification**

Run:
```bash
uv run ruff check .
uv run pytest -q
git diff --check
```
Expected: ruff clean, all tests pass, `git diff --check` clean.

- [ ] **Step 5: Confirm archive-only stale links are the remaining spine refs**

Run:
```bash
git grep -nE "docs/(thread_handoff|master_project_scope_lock|documentation_map|research_mainline|thesis_positioning|experiment_protocol)\.md" \
  | grep -vE "^docs/archive/|^reports/phak_era_archive/"
```
Expected: empty.

- [ ] **Step 6: Commit**

```bash
git add docs/archive/governance_era/
git commit -m "refactor: archive docs/ governance spine into docs/archive/governance_era/

- Moves thread_handoff.md, master_project_scope_lock.md, documentation_map.md, research_mainline.md, thesis_positioning.md, experiment_protocol.md, and TASKS.md into docs/archive/governance_era/.
- Adds docs/archive/governance_era/README.md documenting supersession, why kept, and the runtime-path note (the live read now targets EXPERIMENTS.md at the repo root).
- No JSON regeneration in this commit (deferred to a follow-up per spec Q3); the protocol field hand-edit landed in the previous commit.
- Verification: uv run ruff check . clean; uv run pytest -q green; git diff --check clean."
```

---

## Task 8: Final verification and stop-rule check

No commits in this task — it is the verification gate before handing the branch to the user for GPT review.

- [ ] **Step 1: Confirm branch commit count and log**

Run:
```bash
git log --oneline main..HEAD
```
Expected: eight commits — the two spec commits already on the branch (`0d4692a` design, `da5eb48` Q1–Q3 resolution) plus the six refactor commits from Tasks 2–7. (The spec commits live on this branch by design; they are part of the same PR.)

- [ ] **Step 2: Confirm the new root file set is complete and non-stub**

Run:
```bash
for f in RESEARCH_AUDIT.md RESEARCH_OVERVIEW.md RESEARCH_QUESTIONS.md HYPOTHESES.md EXPERIMENTS.md RESULTS.md ARTIFACT_INDEX.md DECISION_LOG.md REPRODUCIBILITY.md TODO.md; do
  if grep -q "^> Status: stub" "$f"; then echo "STUB: $f"; else echo "OK: $f"; fi
done
```
Expected: ten `OK:` lines, zero `STUB:`.

- [ ] **Step 3: Re-run scope-lock stop rule (master_project_scope_lock.md §Stop Rule)**

The five stop-rule conditions, restated for this refactor:

1. The frozen ATCSCC data, schema/profile, extraction results, agentic loop, KG-RAG results, and failure audit are all linked from `RESEARCH_AUDIT.md` (via the navigation map → `RESULTS.md` and `ARTIFACT_INDEX.md`).
2. `RESEARCH_OVERVIEW.md` and `RESEARCH_QUESTIONS.md` tell the same story (cross-check: both name the same four RQs and the same thesis line).
3. Every major claim in the thesis draft maps to one tracked evidence artifact — `RESULTS.md` rows each carry an evidence path.
4. Remaining gaps are listed as limitations or future work, not new experiments — `RESEARCH_OVERVIEW.md` §Evidence Gaps Before Thesis Submission covers this.
5. Verification commands pass: `uv run ruff check .` and `uv run pytest -q` (already green from Task 7 Step 4).

Confirm each by inspection; if any fails, fix before declaring done.

- [ ] **Step 4: Confirm deferred follow-up is tracked**

The JSON regeneration follow-up (spec §8) is intentionally out of this refactor. Confirm it is documented in:
- `REPRODUCIBILITY.md` §Expected Outputs / Known Issues
- `docs/archive/governance_era/README.md` §Runtime note
- The Commit 1 and Commit 6 messages

If any of those mentions are missing, add a one-line note.

- [ ] **Step 5: Do not push**

Per user decision Q2, do not run `git push`. The user will run a GPT review on the local branch and merge themselves. State this in the final handoff message.

---

## Self-Review Notes

**Spec coverage check (every spec section → task):**
- Spec §4.1 new root files → Tasks 2–5 populate all ten.
- Spec §4.2 archived spine → Task 7.
- Spec §4.3 stays-in-place files → Tasks 6 (link retargets only, no restructuring).
- Spec §5 migration rules (verbatim scope-lock, RQ template, H statuses, evidence pointers, no invention) → encoded in Task 3 steps.
- Spec §6 runtime coupling → Task 2 (the load-bearing rewiring).
- Spec §6.3 literals → Task 2 Step 2 verifies all 70.
- Spec §7 link rewiring → Task 6.
- Spec §8 six commits → Tasks 2, 3, 4, 5, 6, 7 each produce one commit.
- Spec §9 verification → Task 7 Step 4 + Task 8.
- Spec §11 resolved questions → reflected in Task 7 (no JSON regen) and Task 8 Step 5 (no push).

**Placeholder scan:** the "[Copy verbatim …]" instructions in Task 3/4 are not placeholders — they are explicit instructions to migrate specific named sections verbatim, with line ranges given. The plan does not contain "TBD", "implement later", "add appropriate error handling", or unstated types/functions.

**Type consistency:** the only code identifiers touched are the `protocol_text` local and the `"protocol"` dict key in `_audit_reports.py`; both keep their types. Test call sites keep `Path(...)`. No function was renamed.

**Risks carried forward from spec §10:** test-failure risk mitigated by Task 2 Step 2 + Step 6 running before any other task; JSON drift handled by deferral; stale archive links intentional.
