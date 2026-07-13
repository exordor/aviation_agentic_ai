from __future__ import annotations

from aviation_agentic_ai.cross_source.alignment.registry import (
    build_facility_registry,
    build_term_registry,
    parse_nasr_aff_line,
    parse_nasr_apt_line,
)
from aviation_agentic_ai.cross_source.config import load_cross_source_config
from aviation_agentic_ai.cross_source.contracts import EntityType


def _fixed_line(length: int, fields: list[tuple[int, str]]) -> str:
    chars = [" "] * length
    for start, value in fields:
        chars[start : start + len(value)] = value
    return "".join(chars)


def test_parse_nasr_airport_line_uses_faa_icao_and_artcc_fields() -> None:
    line = _fixed_line(
        1532,
        [
            (0, "APT"),
            (27, "JFK "),
            (31, "05/14/2026"),
            (48, "NY"),
            (93, "NEW YORK"),
            (133, "JOHN F KENNEDY INTL"),
            (637, "ZNY "),
            (674, "ZNY "),
            (1210, "KJFK   "),
        ],
    )

    entity = parse_nasr_apt_line(line)

    assert entity is not None
    assert entity.entity_id.endswith(":airport:KJFK")
    assert {code.value for code in entity.codes} == {"JFK", "KJFK"}
    assert entity.metadata["boundary_artcc"] == "ZNY"


def test_parse_nasr_artcc_line_keeps_center_distinct_from_airports() -> None:
    line = _fixed_line(
        254,
        [
            (0, "AFF1"),
            (4, "ZNY "),
            (8, "NEW YORK"),
            (128, "ARTCC"),
            (133, "05/14/2026"),
            (143, "NEW YORK"),
            (225, "KZNY"),
        ],
    )

    entity = parse_nasr_aff_line(line)

    assert entity is not None
    assert entity.entity_type is EntityType.ARTCC
    assert entity.entity_id.endswith(":artcc:ZNY")


def test_real_snapshot_builds_three_airports_and_new_york_artcc() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")

    entities = build_facility_registry(config)
    by_id = {item.entity_id: item for item in entities}

    assert "urn:aviation-agentic-ai:facility:airport:KJFK" in by_id
    assert "urn:aviation-agentic-ai:facility:airport:KEWR" in by_id
    assert "urn:aviation-agentic-ai:facility:airport:KLGA" in by_id
    assert "urn:aviation-agentic-ai:facility:artcc:ZNY" in by_id
    assert len([item for item in entities if item.entity_type is EntityType.ARTCC]) >= 20


def test_term_registry_preserves_ambiguous_gs_candidates() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")

    terms = build_term_registry(config)
    gs_labels = {item.preferred_label for item in terms if item.abbreviation == "GS"}

    assert gs_labels == {"Glide Slope", "Ground Stop"}
    assert any(item.abbreviation == "GDP" for item in terms)
