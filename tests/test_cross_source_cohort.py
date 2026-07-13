from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.cross_source.artifacts import read_jsonl
from aviation_agentic_ai.cross_source.config import load_cross_source_config
from aviation_agentic_ai.cross_source.evaluation.cohort import select_cross_source_cohort


def test_frozen_cross_source_cohort_has_68_records() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    records = read_jsonl(resolve_project_path(config["cohort"]["advisory_input"]))

    cohort = select_cross_source_cohort(
        records,
        airport_codes=config["cohort"]["airport_codes"],
        expected_count=config["cohort"]["expected_record_count"],
    )

    assert len(cohort.records) == 68
    assert len(set(cohort.source_ids)) == 68


def test_cohort_uses_token_boundaries() -> None:
    records = [
        {"source_id": "yes", "text": "CONSTRAINED FACILITIES: JFK"},
        {"source_id": "no", "text": "NOTJFKTOKEN"},
    ]

    cohort = select_cross_source_cohort(records, airport_codes=["JFK"])

    assert cohort.source_ids == ["yes"]
