# Reproducibility

> Migrated on 2026-07-05 from `docs/experiment_protocol.md` §Recommended Regeneration Commands, `docs/thread_handoff.md` §Verification Defaults, and `README.md` §Quick Start. Until the archive commit lands, those source files remain in place under `docs/`; afterward they will be preserved under `docs/archive/governance_era/`.

## Environment

- OS: macOS / Linux (project developed on darwin arm64).
- Python: see `pyproject.toml` `requires-python`.
- Package manager: `uv`.
- Optional extras: `dev`, `graphrag`, `web`.

## Installation

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

## Run Main Prototype

The CLI entry point is `aviation-ai`. Quick-start commands from README.md §Quick Start:

```bash
uv run aviation-ai report thesis-claims
uv run aviation-ai report nasa-atmonto-answer-generation
uv run python scripts/build_nasa_atmonto_reviewer_defense_audit.py
uv run ruff check .
uv run pytest -q
```

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

Use `reports/stages/nasa_atmonto_s7_retrieval.md` as the current state table,
not as a substitute for reading the underlying reports.

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
- Report-generation changes: run the relevant report command and inspect the
  generated diff before committing.

## Known Issues

- PDF source-family B (FAA/NASA reference PDFs) is a planned second pilot; its extraction pipeline is not in the regeneration commands above.
- LLM-dependent steps (S1/S2/S3 prediction runs) require API access; the regeneration commands above cover only deterministic report builders.
