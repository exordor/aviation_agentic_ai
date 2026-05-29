# Benchmark Manual Review Protocol

## Purpose

Benchmark v2 expands the project from 35 labels to 120 labels, but the current
file is machine-seeded and must not be described as externally aviation-expert
certified. Manual review is required before using it for strong thesis claims
about aviation-domain correctness.

## Inputs

- Source labels: `data/cqs/06_phak_ch4_0.benchmark_v2.gold.json`
- Review pack command: `uv run aviation-ai report benchmark-review-pack`
- Review pack outputs:
  - `reports/stages/benchmark_review_pack.json`
  - `reports/stages/benchmark_review_pack.md`
- Working review copy:
  - `data/cqs/06_phak_ch4_0.benchmark_v2.reviewed.gold.json`

## Review Checks

For each label, review:

- Question wording: mark unnatural machine-generated wording, especially generic
  prompts such as "source-backed fact connects" or "evidence mentioning".
- Evidence spans: mark duplicate spans and spans that are too broad, too short,
  or not sufficient for the answer key.
- Question strength: mark weak or generic questions that do not test a meaningful
  aviation relation or concept.
- Cross-page synthesis: mark cross-page labels where the answer key merely
  repeats one span and does not synthesize across pages.
- Insufficient-evidence safety: review no-answer labels for live weather,
  current NOTAMs, ATC clearances, aircraft-specific V-speeds, POH/checklist
  replacement, emergency procedures, weight and balance, and go/no-go decisions.

## Annotation Policy

The reviewed working copy starts with `review.status = needs_manual_review`.
Reviewers may change this only after checking source text and evidence spans.
Acceptable review statuses:

- `accepted_for_internal_thesis_eval`
- `revise_question_wording`
- `revise_evidence`
- `remove_from_eval`
- `needs_aviation_safety_review`

The file remains course-project / thesis-oriented gold unless there is explicit
external expert review evidence. Do not claim external certification.

## Safety Boundary

The benchmark supports aviation learning and decision support only. It must not
be used to claim that the system replaces the aircraft POH/AFM, approved
checklists, ATC instructions, instructor guidance, or pilot judgment.
