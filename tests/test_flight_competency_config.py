from __future__ import annotations

from aviation_agentic_ai.config import load_yaml


def test_flight_competency_config_declares_the_public_atmontoplus_slice() -> None:
    config = load_yaml("configs/flight_competency_v1.yaml")

    sample = config["canonical_public_sample"]
    nasa_source = config["sources"]["nasa_atmonto_plus"]

    assert nasa_source["path"].endswith("/allFilesTTL.zip")
    assert nasa_source["source_role"] == "canonical_public_sample_bundle"
    assert sample["primary_source_id"] == "nasa_atmonto_plus"
    assert sample["source_role"] == "canonical_public_cross_source_sample"
    assert sample["geographic_scope"] == {
        "flight_weather_aspm_airports": ["KJFK", "KEWR", "KLGA"],
        "tmi": "all_nas_issued_on_sample_date",
    }
    assert sample["temporal_selection"] == {
        "taf": "issued_on_sample_date",
        "tmi": "issued_on_sample_date",
    }
    assert sample["overlap_reference_inventory"] == {
        "taf_reports": 66,
        "traffic_management_initiatives": 114,
    }
    assert sample["temporal_scope"] == {
        "primary_date": "2014-07-15",
        "flight_departure_start_utc": "2014-07-15T00:01:00Z",
        "flight_departure_end_utc": "2014-07-15T23:59:00Z",
        "arrival_spillover_end_utc": "2014-07-16T04:54:00Z",
    }


def test_flight_competency_config_marks_2026_bts_as_optional_supplement() -> None:
    config = load_yaml("configs/flight_competency_v1.yaml")

    canonical = config["canonical_public_sample"]
    bts_source = config["sources"]["bts_on_time_2026_05"]

    assert canonical["primary_source_id"] != "bts_on_time_2026_05"
    assert bts_source["source_role"] == "optional_raw_source_supplement"
    assert bts_source["cross_temporal_join_allowed"] is False
