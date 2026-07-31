from __future__ import annotations

from aviation_agentic_ai.config import (
    configured_dataset_id,
    configured_store_root,
    load_yaml,
    resolve_project_path,
)


CONFIG_PATH = "configs/atmonto_public_sample_v1.yaml"


def test_public_sample_config_is_a_standalone_2014_runtime() -> None:
    """Adding a modern source would silently turn the sample into a proxy join."""

    config = load_yaml(CONFIG_PATH)

    assert config["snapshot_set_id"] == "atmonto-public-sample-2014-v1"
    assert configured_dataset_id(config) == "atmonto-public-sample-2014-v1"
    assert configured_store_root(config) == resolve_project_path(
        "data/stores/aviation/atmonto-public-sample-2014-v1"
    )
    assert config["sources"] == {
        "nasa_atmonto_instances": (
            "data/raw/nasa_atmonto_prototype/allFilesTTL.zip"
        )
    }
    assert set(config["source_checksums"]) == {"nasa_atmonto_instances"}
    assert set(config["source_urls"]) == {"nasa_atmonto_instances"}


def test_public_sample_config_activates_all_atmonto_sample_layers() -> None:
    """Omitting a layer or widening time would break the canonical sample."""

    config = load_yaml(CONFIG_PATH)
    metadata = config["source_metadata"]["nasa_atmonto_instances"]

    assert metadata["temporal_domain_id"] == "nasa-atmonto-2014-07-15"
    assert metadata["sample_date"].isoformat() == "2014-07-15"
    assert metadata["weather_aspm_airport_codes"] == [
        "KJFK",
        "KEWR",
        "KLGA",
    ]
    assert metadata["tmi_scope"] == "all_nas_issued_on_sample_date"
    assert metadata["temporal_selection"] == {
        "weather_observation": "observed_on_sample_date",
        "weather_forecast": "issued_on_sample_date",
        "airport_operations": "interval_starts_on_sample_date",
        "traffic_management_initiative": "issued_on_sample_date",
    }
    assert metadata["inventory_interval_overlap_reference"] == {
        "taf_reports": 66,
        "traffic_management_initiatives": 114,
    }


def test_general_knowledge_config_keeps_the_sample_in_its_own_time_domain() -> None:
    config = load_yaml("configs/aviation_knowledge_v1.yaml")
    metadata = config["source_metadata"]["nasa_atmonto_instances"]

    assert metadata["include_public_sample_layers"] is True
    assert metadata["sample_date"].isoformat() == "2014-07-15"
    assert metadata["weather_aspm_airport_codes"] == [
        "KJFK",
        "KEWR",
        "KLGA",
    ]
    assert metadata["tmi_scope"] == "all_nas_issued_on_sample_date"
    assert metadata["cross_temporal_join_allowed"] is False
    assert metadata["include_public_sample_layers"] is True
    assert metadata["cross_temporal_join_allowed"] is False
    assert metadata["role"] == "canonical_public_cross_source_sample"
