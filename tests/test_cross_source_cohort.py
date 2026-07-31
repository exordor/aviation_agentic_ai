from aviation_agentic_ai.agent_system.contracts import SourceFamily, SourceRecord
from aviation_agentic_ai.agent_system.ingestion_pipeline import preflight_advisory
from aviation_agentic_ai.agent_system.tmi_profiles import detected_family_counts
from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.cross_source.artifacts import read_jsonl
from aviation_agentic_ai.cross_source.config import load_cross_source_config
from aviation_agentic_ai.cross_source.evaluation.cohort import select_cross_source_cohort


def test_legacy_nyc_mention_selection_has_68_records() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    records = read_jsonl(resolve_project_path(config["cohort"]["advisory_input"]))

    cohort = select_cross_source_cohort(
        records,
        airport_codes=config["cohort"]["airport_codes"],
        expected_count=config["cohort"]["expected_record_count"],
    )

    assert len(cohort.records) == 68
    assert len(set(cohort.source_ids)) == 68


def test_legacy_nyc_mention_selection_uses_token_boundaries() -> None:
    records = [
        {"source_id": "yes", "text": "CONSTRAINED FACILITIES: JFK"},
        {"source_id": "no", "text": "NOTJFKTOKEN"},
    ]

    cohort = select_cross_source_cohort(records, airport_codes=["JFK"])

    assert cohort.source_ids == ["yes"]


def test_registry_classifies_the_legacy_nyc_mention_selection() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    records = read_jsonl(resolve_project_path(config["cohort"]["advisory_input"]))
    selection = select_cross_source_cohort(
        records,
        airport_codes=config["cohort"]["airport_codes"],
        expected_count=config["cohort"]["expected_record_count"],
    )

    assert detected_family_counts(selection.records) == {
        "ARRIVAL_DELAY": 7,
        "GDP": 21,
        "GS": 24,
        "HOTLINE": 3,
        "NATOTS": 7,
        "REROUTE": 4,
        "REROUTE_CANCELLATION": 1,
        "SWAP": 1,
    }


def test_legacy_nyc_mention_selection_reproduces_preflight_split() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    records = read_jsonl(resolve_project_path(config["cohort"]["advisory_input"]))
    selection = select_cross_source_cohort(
        records,
        airport_codes=config["cohort"]["airport_codes"],
        expected_count=config["cohort"]["expected_record_count"],
    )
    results = [
        preflight_advisory(
            SourceRecord(
                source_id=str(row["source_id"]),
                family=SourceFamily.ATCSCC_ADVISORY,
                content=str(row["text"]),
            )
        )
        for row in selection.records
    ]

    assert sum(result is None for result in results) == 46
    assert sum(
        result is not None
        and result.reason == "incomplete core advisory fields"
        for result in results
    ) == 3
    assert sum(
        result is not None
        and result.reason
        == "recognized advisory family outside active publication profile"
        for result in results
    ) == 18
    assert sum(
        result is not None
        and result.reason == "deferred traffic-management lifecycle event"
        for result in results
    ) == 1
