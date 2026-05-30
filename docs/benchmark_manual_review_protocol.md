# Benchmark Model-Based Review Protocol

## Purpose

Benchmark v2 expands the project from 35 labels to 120 labels, but the current
file is machine-seeded and must not be described as externally aviation-expert
certified. This project uses model-based review rather than human review, so
strong human-verified or expert-certified aviation-domain correctness claims
remain unsupported.

## Inputs

- Source labels: `data/cqs/06_phak_ch4_0.benchmark_v2.gold.json`
- Review pack command: `uv run aviation-ai report benchmark-review-pack`
- LLM review command: `uv run aviation-ai report benchmark-llm-review`
- Review pack outputs:
  - `reports/stages/benchmark_review_pack.json`
  - `reports/stages/benchmark_review_pack.md`
- Working review copy:
  - `data/cqs/06_phak_ch4_0.benchmark_v2.reviewed.gold.json`

## Review Checks

For each label, model-based review checks:

- Question wording: mark unnatural machine-generated wording, especially generic
  prompts such as "source-backed fact connects" or "evidence mentioning".
- Evidence spans: mark duplicate spans and spans that are too broad, too short,
  or not sufficient for the answer key.
- Question strength: mark weak or generic questions that do not test a meaningful
  aviation relation or concept.
- Cross-page synthesis: mark cross-page labels where the answer key merely
  repeats one span and does not synthesize across pages.
- Insufficient-evidence safety: check no-answer labels for live weather,
  current NOTAMs, ATC clearances, aircraft-specific V-speeds, POH/checklist
  replacement, emergency procedures, weight and balance, and go/no-go decisions.

## Annotation Policy

The reviewed working copy starts with
`review.status = needs_llm_review`. Schema-valid LLM review may create
`llm_reviewed_not_human_certified` results. Acceptable recommended actions:

- `accepted_for_internal_thesis_eval`
- `revise_question_wording`
- `revise_evidence`
- `remove_from_eval`
- `needs_human_expert`

The file remains internal thesis evidence. Do not claim human review, expert
gold status, or external certification.

## Safety Boundary

The benchmark supports aviation learning and decision support only. It must not
be used to claim that the system replaces the aircraft POH/AFM, approved
checklists, ATC instructions, instructor guidance, or pilot judgment.
