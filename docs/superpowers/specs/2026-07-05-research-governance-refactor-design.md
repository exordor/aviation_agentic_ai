# Research-Governance Refactor Design

**Date:** 2026-07-05
**Status:** Spec — awaiting user review
**Source guide:** `pasted-text-20260705-141640-b66da09b.txt` (科研型 Vibe Coding 项目治理指南)
**Scope:** Restructure project governance into the guide's root-level file set; archive the current `docs/` canonical spine.

---

## 1. Goal

Adopt the attached guide's root-level Research-Map vocabulary as the canonical governance surface for this repo, by migrating the content of the existing `docs/` spine into the guide's named files at repository root.

The guide is treated as authoritative for **file naming and top-level organization**. The ATCSCC scope lock (`master_project_scope_lock.md`) is treated as authoritative for **content and claim boundaries**. The two are reconciled by rewriting migrated content into the guide's RQ / Hypothesis / Experiment voice while preserving every scope-lock constraint.

This is a **literal** application of the guide, not an adaptation. The old `docs/` canonical spine is archived, not kept live.

## 2. Non-Goals

- Do **not** restructure `data/experiments/nasa_atmonto/formal/` into the guide's `experiments/E001_*/` registry layout. That evidence is bounded by the scope lock and will be re-indexed (not relocated) into `EXPERIMENTS.md`.
- Do **not** change thesis claims, RQs, metrics, or scope as part of this refactor. Only their *location and voice* change.
- Do **not** delete tracked artifacts. Old canonical docs move to `docs/archive/governance_era/`.
- Do **not** migrate `docs/` files outside the canonical spine (e.g. `atcscc_agent_architecture.md`, `pipeline_authority_model.md`, `thesis_writing_spine.md`, `llm_review_protocol.md`, `nasa_atmonto_gold_annotation_guide.md`, `presentation_style_harness.md`, `atcscc_cq_answerability_matrix.md`, `research_paper_analysis_protocol.md`). They remain live under `docs/`.

## 3. Confirmed Decisions

| # | Decision | Choice |
|---|---|---|
| D1 | Refactor scope | **Literal root-level file set** |
| D2 | Old `docs/` spine fate | **Archive old spine** under `docs/archive/governance_era/` |
| D3 | Scope-lock migration | **Rewrite into guide voice** (RQ/Hypothesis/Experiment template), preserving constraints |
| D4 | Commit strategy | **Incremental commits** (one commit per logical step) |
| D5 | `experiment_protocol.md` runtime coupling | **Rewrite code + tests, full archive** of the protocol file |

## 4. Target Layout

### 4.1 New root-level canonical files

| New file | Source content | Guide role |
|---|---|---|
| `RESEARCH_OVERVIEW.md` | `thesis_positioning.md` (problem, claim, contributions, evaluation philosophy, claim-safety matrix, can/must-not claim, evidence gaps) + `research_mainline.md` (one-line direction, thesis story, SOTA positioning, current usable claims, claims to avoid) + `master_project_scope_lock.md` (locked outcome, single-sentence contribution, non-goals, intake rule, stop rule) | §2.1 Research Overview |
| `RESEARCH_QUESTIONS.md` | `research_mainline.md` §Research Questions + `thesis_positioning.md` §Research Questions + `master_project_scope_lock.md` §Accepted Research Questions, rewritten as `## RQ1 … RQ4` blocks with `### Description / Motivation / Related Hypotheses / Related Experiments / Current Evidence / Status` | §2.2 Research Questions |
| `HYPOTHESES.md` | `experiment_protocol.md` §Hypotheses And Falsification Criteria (H1–H4) + `thesis_positioning.md` §Hypotheses, as a single table + per-H detail. **Falsification criteria and the literal phrase "Falsified if" must be preserved verbatim** (test depends on it). | §2.3 Hypotheses |
| `EXPERIMENTS.md` | `experiment_protocol.md` body: material passport, source families, SOTA-informed adaptation, research claims C1–C5, gold-set plan, systems under test, baselines/comparators S0–S4 + PDF reference systems, metrics, rejection error analysis, experimental procedure, reporting rules, completion gate, layered evaluation policy, navigation, regeneration commands. **All ~60 test-required string literals (see §9) must be present in this file.** | §3 Experiment index (condensed) + protocol |
| `RESULTS.md` | `master_project_scope_lock.md` §Minimum Deliverable Set table + `documentation_map.md` §Experiment Evidence layer table, rewritten as Observation / Evidence / Interpretation / Confidence rows pointing at `reports/stages/nasa_atmonto_*` evidence. **No new claims.** | §4.2 Results |
| `ARTIFACT_INDEX.md` | `documentation_map.md` §Context Inventory (Tracked File-Family Snapshot, Tracked But Non-Default Families, Current-Use Families) + §Artifact Management Policy + §Ignored Local Material | §5.1 Artifact Index |
| `DECISION_LOG.md` | `master_project_scope_lock.md` §New-Idea Intake Rule + §Stop Rule + `documentation_map.md` §Document Tiers + §Where New Documents Should Go, framed as D001-style entries (Date / Context / Decision / Reason / Alternatives / Consequences). Seed with one entry per scope-lock decision (e.g. D001 = single thesis-grade study; D002 = four locked RQs; D003 = layered metrics, no overall score; D004 = keep PHAK-era evidence historical). | §6 Decision Log |
| `REPRODUCIBILITY.md` | `experiment_protocol.md` §Recommended Regeneration Commands + `documentation_map.md` §Verification / `thread_handoff.md` §Verification Defaults + environment/install notes distilled from `README.md` §Quick Start | §7 Reproducibility |
| `RESEARCH_AUDIT.md` | New file. Project snapshot (audit date, branch, last commit, status) + a navigation map that lists each new root file with one-line purpose + the "6 questions to ask of any file" rubric from the guide. This becomes the new entry point that `AGENTS.md`, `CLAUDE.md`, `README.md`, and `thread_handoff.md` replacement all point at. | §1.3 Research Audit |
| `TODO.md` | Rename/rewrite of existing `TASKS.md` content into the guide's TODO voice. `TASKS.md` is archived. | §2 list, §11, §13 |

### 4.2 Archived under `docs/archive/governance_era/`

These move verbatim into `docs/archive/governance_era/`:

- `docs/thread_handoff.md`
- `docs/master_project_scope_lock.md`
- `docs/documentation_map.md`
- `docs/research_mainline.md`
- `docs/thesis_positioning.md`
- `docs/experiment_protocol.md`
- `docs/archive/governance_era/README.md` (new) — explains when/why these were archived and what supersedes them.
- `TASKS.md` (root → archived; content lives on in `TODO.md`)

### 4.3 Stays in place

- `AGENTS.md` (rewritten in place: retarget links, point Default Context at root files)
- `CLAUDE.md` (rewritten in place: retarget links to root files)
- `README.md` (rewritten in place: retarget links; keep project description)
- `GOALS.md` (kept; references to `thesis_positioning.md` retargeted to `RESEARCH_OVERVIEW.md`)
- All other `docs/*.md` not in §4.2
- All `reports/**`, `data/**`, `src/**`, `tests/**`, `scripts/**`

## 5. Content Migration Rules

1. **Scope-lock constraints are preserved exactly.** The four RQs, the metric boundary, the figure boundary, the non-goals list, the claim boundary, the stop rule, and the new-idea intake rule all migrate without weakening. They are *reorganized* into the guide's templates, not relaxed.
2. **RQ blocks use the guide's full template.** Each of RQ1–RQ4 gets `### Description / Motivation / Related Hypotheses / Related Experiments / Current Evidence / Status` subfields. Status values: `active`, `partially answered`, `inconclusive` — chosen to match `research_mainline.md`'s current per-RQ state.
3. **Hypothesis table uses the guide's status vocabulary** (`pending`, `supported`, `rejected`, `partially_supported`, `inconclusive`, `abandoned`, `needs_replication`), mapped from the current H1–H4 falsification status in `experiment_protocol.md`.
4. **Every migrated claim keeps its evidence pointer.** A sentence that today cites `reports/stages/nasa_atmonto_s7_retrieval.md` must still cite that path after migration. The evidence artifacts do not move.
5. **No invented content.** Where the guide template asks for a field that no current doc fills (e.g. some RQ's "Related Experiments"), write `unknown / not yet structured` rather than fabricating.
6. **`RESEARCH_AUDIT.md` is the new entry point.** It is the only file a new thread must read first; it then routes to `RESEARCH_OVERVIEW.md` → `RESEARCH_QUESTIONS.md` → `HYPOTHESES.md` → `EXPERIMENTS.md` → `RESULTS.md` → `ARTIFACT_INDEX.md` → `DECISION_LOG.md` → `REPRODUCIBILITY.md` → `TODO.md`.

## 6. Runtime / Test Coupling (D5)

`experiment_protocol.md` is read at runtime and its path is asserted by tests. Decision D5 = rewrite code + tests + fully archive.

### 6.1 Source changes

`src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py`:

- **Line 615:** `protocol_text = (repo_root / "docs/experiment_protocol.md").read_text(...)` → read from `repo_root / "EXPERIMENTS.md"`.
- **Line 642:** `"protocol": "docs/experiment_protocol.md"` → `"protocol": "EXPERIMENTS.md"`.
- **Line 1082:** `"protocol": "docs/experiment_protocol.md"` → `"protocol": "EXPERIMENTS.md"`.
- **Lines 460, 518:** docstring/evidence strings mentioning `docs/experiment_protocol.md` → `EXPERIMENTS.md`.

Generated report JSON that currently embeds `"protocol": "docs/experiment_protocol.md"` will, after regeneration, embed `"protocol": "EXPERIMENTS.md"`. **This is an expected, documented dirty diff** in regenerated `reports/stages/nasa_atmonto_formal_experiment_scoring.json` and `nasa_atmonto_formal_experiment_readiness.json`. The commit message for that step will call this out.

### 6.2 Test changes

`tests/test_nasa_atmonto_experiment_protocol.py`:

- **Line 58, 126, 141:** `Path("docs/experiment_protocol.md")` → `Path("EXPERIMENTS.md")`.
- The ~60 required-string assertions at lines 60–122, 128–137, 143–149 must still pass against `EXPERIMENTS.md`. The migration must carry every required literal across.

`tests/test_nasa_atmonto_formal_experiment.py`:

- **Lines 372–376:** fixture copies `repo / "docs/experiment_protocol.md"` into `tmp_path / "docs/experiment_protocol.md"`. Change both source and destination to `EXPERIMENTS.md` so the fixture copies the new root file into `tmp_path / "EXPERIMENTS.md"`, matching what `_audit_reports.py` now reads. Single resolution; no alternative branch.

### 6.3 Test-Required Literals (must survive into EXPERIMENTS.md)

`tests/test_nasa_atmonto_experiment_protocol.py:60-122` requires these substrings present verbatim in the protocol text. The migration must preserve every one in `EXPERIMENTS.md`:

`pilot / feasibility study`, `Source Families`, `faa_atcscc_advisories`, `faa_nasa_pdf_reference_documents`, `hybrid_docling_pymupdf`, `pymupdf_text_legacy`, `term_has_definition`, `procedure_mentions_concept`, `SOTA-Informed Adaptation For The Rerun`, `Extract-Define-Canonicalize`, `reviewed_dev_examples`, `held-out 100 scoring records`, `canonicalizers`, `evidence checkers`, `profile-gap explainers`, `nine-stage pipeline`, `ATCSCC parsing`, `schema/atcscc_tmi_profile.yaml`, `predicate_uri`, `repair-induced false positive`, `format error`, `predicate drift`, `entity canonicalization error`, `fuzzy-only mappings`, `repair-only facts`, `log/review/quarantine`, `GraphRAG evaluation remains layered`, `end-to-end GraphRAG answer improvement`, `requiring verification`, `JSON-Schema-guided information extraction`, `S0: Rule-Only`, `S1: LLM-Only`, `S2: LLM + Schema Slice`, `S3: LLM + Schema Slice + Validator/Repair`, `S4: Hybrid Backbone + Semantic Enrichment`, `Baselines And Comparators`, `S0 rule-only`, `S1 LLM-only`, `S1_raw_open_llm`, `S1b_llm_canonicalized`, `S4_hybrid_backbone_enrichment`, `invalid_direct_schema_scoring`, `JSON Adherence`, `Schema Violation Rate`, `Triple Precision, Recall, And F1`, `Canonicalization Yield`, `Repair Success Rate`, `Manual Semantic Correctness`, `Falsified if`, `reports/stages/nasa_atmonto_gold_review_session_plan.md`, `reports/stages/nasa_atmonto_gold_review_multiround_audit.md`, `prepare_nasa_atmonto_gold_review_session_plan.py`, `100 sampled advisories have reviewed gold annotations`, `Assisted Gold Adjudication Workflow`, `Adversarial ontology/profile review`, `Gold truth is not created by model agreement alone`, `multi-round and multi-perspective`, `extensionProbability:MODERATE->MEDIUM`, `raw_value`, `value_normalization`.

Plus, from lines 128–148: `supported on the corrected stage`, `S1b/S4 corrected-stage derived outputs`, `supported on the reviewed 100-record sample`, `Semantic Stratification`, `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`, `all 288 pilot rejections`, `13 \`extractor_bug\` facts`, `275 \`profile_gap\``, `enter the S3 validator/repair loop as initially invalid`, `must not be fabricated or manually filled`, `100 usable records before scoring`, `\`session_01\` covers 4 records`, `review queue only`.

Migration approach: keep the relevant protocol sections intact in `EXPERIMENTS.md` rather than paraphrasing them. Where the guide template is sparser than the protocol, the protocol wins.

## 7. Link Rewiring

### 7.1 Live link rewrites (every occurrence retargeted)

| Old path | New target |
|---|---|
| `docs/thread_handoff.md` | `RESEARCH_AUDIT.md` |
| `docs/master_project_scope_lock.md` | `DECISION_LOG.md` + `RESEARCH_OVERVIEW.md` |
| `docs/documentation_map.md` | `ARTIFACT_INDEX.md` (primary); `RESEARCH_AUDIT.md` (entry-point role) |
| `docs/research_mainline.md` | `RESEARCH_OVERVIEW.md` (story/claims) + `RESEARCH_QUESTIONS.md` (RQs) |
| `docs/thesis_positioning.md` | `RESEARCH_OVERVIEW.md` |
| `docs/experiment_protocol.md` | `EXPERIMENTS.md` (procedure/claims/metrics) + `REPRODUCIBILITY.md` (commands/env) + `HYPOTHESES.md` (H1–H4 + falsification) |
| `TASKS.md` | `TODO.md` |

### 7.2 Files requiring in-place edits (link retargeting only)

| File | Action |
|---|---|
| `AGENTS.md` | Rewrite Default Context paragraph (lines 7–17): startup pack becomes `RESEARCH_AUDIT.md` → `RESEARCH_OVERVIEW.md` → `ARTIFACT_INDEX.md`. Retarget any other spine link. |
| `CLAUDE.md` | Same retargeting as `AGENTS.md`. |
| `README.md` | Retarget spine links at lines 45–49, 76, 182, 364, 404, 407, 456. |
| `GOALS.md` | Retarget `thesis_positioning.md` at lines 116, 233 → `RESEARCH_OVERVIEW.md`. |
| `docs/thesis_writing_spine.md` | Retarget lines 4–5. |
| `docs/research_paper_analysis_protocol.md` | Retarget `experiment_protocol.md` refs at lines 153–154. |
| `docs/atcscc_agent_architecture.md` | Retarget `thesis_positioning.md` at lines 30, 687. |
| `docs/pipeline_authority_model.md` | Retarget line 49. |
| `docs/experiment_protocol.md` (now archived) | n/a — moves as-is. |
| `reports/stages/index.md` | Retarget header nav at lines 5–6. |
| `reports/final/README.md` | Retarget lines 8–13. |
| `reports/final/atcscc_thesis_report.md` | Retarget lines 66, 213, 235, 413. |
| `reports/final/atcscc_thesis_report_outline.md` | Retarget lines 14–17, 38, 42–43, 46–47, 62, 66, 72, 75. |
| `reports/final/atcscc_defense_deck_outline.md` | Retarget lines 35, 37, 41–43, 48–49, 59. |
| `reports/final/atcscc_agent_plan_storyboard.md` | Retarget line 42. |
| `reports/final/figure_descriptions.md` | Retarget line 4. |
| `reports/stages/thesis_claims_review.md` + `.json` | Retarget line 64 / 177. |
| `reports/stages/nasa_atmonto_competency_questions.md` | Retarget line 57. |
| `reports/stages/nasa_atmonto_formal_experiment_readiness.md` + `.json` | Retarget line 4. |
| `reports/stages/nasa_atmonto_formal_experiment_remediation_plan.md` | Retarget lines 18, 536. |
| `reports/stages/nasa_atmonto_formal_experiment_scoring.md` + `.json` + gpt-5.4-mini variants | Retarget lines 4, 170, 175, 180 / JSON lines 4, 4685, 4715, 4745. |
| `reports/stages/nasa_atmonto_gold_review_multiround_audit.md` | Retarget line 22. |
| `src/aviation_agentic_ai/reporting/thesis_claims.py` | Retarget line 475. |
| `src/aviation_agentic_ai/ontology/atmonto_experiment/_audit_reports.py` | Per §6.1. |

### 7.3 Stale links intentionally left (provenance-only)

References inside `docs/archive/phak_era/`, `reports/phak_era_archive/`, and any other file already under an archive path are **not** retargeted. They are historical provenance; updating them would rewrite audit history. The `docs/archive/governance_era/README.md` notes that links from archive → old spine are intentionally preserved.

## 8. Execution Plan (incremental commits)

Each step is one commit. Branch off `main` first (`refactor/research-governance-framework`).

**Commit 1 — scaffold + EXPERIMENTS.md (the load-bearing file).**
- Create the 10 root files as stubs.
- Migrate `experiment_protocol.md` content into `EXPERIMENTS.md`, preserving all §6.3 literals.
- Update `_audit_reports.py` (§6.1) and the two test files (§6.2).
- Run `uv run pytest -q tests/test_nasa_atmonto_experiment_protocol.py tests/test_nasa_atmonto_formal_experiment.py` and `uv run ruff check .`.
- Commit: `refactor: migrate experiment_protocol.md content to EXPERIMENTS.md and update runtime+test readers`.

**Commit 2 — RESEARCH_OVERVIEW + RESEARCH_QUESTIONS + HYPOTHESES.**
- Migrate `thesis_positioning.md` + `research_mainline.md` + scope-lock framing into `RESEARCH_OVERVIEW.md`.
- Build RQ1–RQ4 blocks in `RESEARCH_QUESTIONS.md`.
- Build H1–H4 table + falsification detail in `HYPOTHESES.md`.
- Commit: `refactor: migrate thesis/research_mainline into RESEARCH_OVERVIEW/QUESTIONS/HYPOTHESES`.

**Commit 3 — RESULTS + ARTIFACT_INDEX + DECISION_LOG + REPRODUCIBILITY.**
- Build `RESULTS.md` from deliverables + evidence-layer table.
- Build `ARTIFACT_INDEX.md` from `documentation_map.md` inventory + artifact policy.
- Build `DECISION_LOG.md` seeded from scope-lock decisions.
- Build `REPRODUCIBILITY.md` from regen commands + verification defaults.
- Commit: `refactor: migrate documentation_map/scope-lock into RESULTS/ARTIFACT_INDEX/DECISION_LOG/REPRODUCIBILITY`.

**Commit 4 — RESEARCH_AUDIT + TODO.**
- Build `RESEARCH_AUDIT.md` as new entry point with navigation map.
- Migrate `TASKS.md` → `TODO.md`.
- Commit: `refactor: add RESEARCH_AUDIT entry point; migrate TASKS to TODO`.

**Commit 5 — link rewiring.**
- Apply every §7.2 retargeting in place across `AGENTS.md`, `CLAUDE.md`, `README.md`, `GOALS.md`, `docs/*.md`, `reports/**`, `src/**`.
- Run `git grep -n "docs/experiment_protocol.md\|docs/thesis_positioning.md\|docs/research_mainline.md\|docs/documentation_map.md\|docs/master_project_scope_lock.md\|docs/thread_handoff.md"` outside archive paths to confirm only archive/internal refs remain.
- Commit: `refactor: retarget canonical-doc links to new root-level research files`.

**Commit 6 — archive old spine.**
- `git mv` the six spine docs + `TASKS.md` into `docs/archive/governance_era/`.
- Add `docs/archive/governance_era/README.md` documenting the supersession.
- Run full `uv run ruff check .` and `uv run pytest -q`.
- Regenerate `reports/stages/nasa_atmonto_formal_experiment_scoring.json` + readiness JSON (if a regen command exists in `REPRODUCIBILITY.md`) to capture the `protocol: EXPERIMENTS.md` change; commit message notes the expected diff.
- Commit: `refactor: archive docs/ governance spine into docs/archive/governance_era/`.

## 9. Verification

- `uv run ruff check .` passes after every commit.
- `uv run pytest -q` passes after Commits 1 and 6.
- `git diff --check` clean for documentation-only commits.
- After Commit 6: `git grep -nE "docs/(thread_handoff|master_project_scope_lock|documentation_map|research_mainline|thesis_positioning|experiment_protocol)\.md"` returns hits only inside `docs/archive/` and `reports/phak_era_archive/`.
- The §9 stop-rule checklist from `master_project_scope_lock.md` (all deliverables linked from the new entry point; mainline + positioning tell the same story; every major claim maps to one evidence artifact; remaining gaps are limitations; verification commands pass) is re-confirmed against the new file layout in `RESEARCH_AUDIT.md`.

## 10. Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Generated report JSON drift after `_audit_reports.py` path change | Document expected diff in Commit 6 message; regenerate via the command listed in `REPRODUCIBILITY.md`. |
| Missed string literal causes test failure | Commit 1 runs the two protocol tests before any other step; literals catalogued in §6.3. |
| Stale link in a `reports/final/` source-JSON breaks a deck rebuild | §7.2 retargets `reports/final/**` files; deck sources under `reports/phak_era_archive/` are explicitly left stale (archived provenance). |
| Scope-lock constraint accidentally weakened during rewrite | §5 rule 1; `DECISION_LOG.md` entries map 1:1 to original scope-lock sections so any drift is auditable. |
| `documentation_map.md` Document-Precedence chain becomes orphaned | Replaced by `RESEARCH_AUDIT.md` navigation map; old chain preserved in archive for provenance. |
| Large single PR is hard to review | Six incremental commits, each independently buildable. |

## 11. Open Questions For Spec Review

- **Q1.** Branch name `refactor/research-governance-framework` — acceptable, or do you want a different name?
- **Q2.** Push policy: the workspace says push both `origin` (GitLab) and `github` after merging to `main`. For this refactor branch, push both remotes too, or GitLab only until merged?
- **Q3.** Should the regenerated `nasa_atmonto_formal_experiment_scoring.json` / readiness JSON be regenerated in Commit 6, or left for a follow-up so the refactor PR stays text-only? (Regen may pull in unrelated dirty diffs from other changed inputs.)
