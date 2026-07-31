"""Golden contracts for the neutral FAA authority layer."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[1]


def _fixed_line(length: int, fields: list[tuple[int, str]]) -> str:
    chars = [" "] * length
    for start, value in fields:
        chars[start : start + len(value)] = value
    return "".join(chars)


def test_neutral_authority_contract_preserves_shape_and_strictness() -> None:
    from aviation_agentic_ai.authority.contracts import (
        CanonicalEntity,
        CodeValue,
        EntityType,
    )

    entity = CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
        entity_type=EntityType.AIRPORT,
        preferred_label="JOHN F KENNEDY INTL",
        codes=[CodeValue(scheme="ICAO", value="KJFK")],
        aliases=["JFK"],
        source_refs=["faa_nasr:2026-05-14"],
    )

    assert entity.model_dump(mode="json") == {
        "entity_id": "urn:aviation-agentic-ai:facility:airport:KJFK",
        "entity_type": "airport",
        "preferred_label": "JOHN F KENNEDY INTL",
        "codes": [{"scheme": "ICAO", "value": "KJFK"}],
        "aliases": ["JFK"],
        "valid_from": None,
        "valid_to": None,
        "source_refs": ["faa_nasr:2026-05-14"],
        "metadata": {},
    }
    with pytest.raises(ValidationError):
        CanonicalEntity(
            entity_id=entity.entity_id,
            entity_type=EntityType.AIRPORT,
            preferred_label=entity.preferred_label,
            codes=entity.codes,
            unexpected="not allowed",
        )


def test_neutral_nasr_parsers_preserve_airport_and_artcc_ids() -> None:
    from aviation_agentic_ai.authority.contracts import EntityType
    from aviation_agentic_ai.authority.nasr import (
        parse_nasr_aff_line,
        parse_nasr_apt_line,
    )

    airport = parse_nasr_apt_line(
        _fixed_line(
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
    )
    artcc = parse_nasr_aff_line(
        _fixed_line(
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
    )

    assert airport is not None
    assert airport.entity_id == "urn:aviation-agentic-ai:facility:airport:KJFK"
    assert {code.value for code in airport.codes} == {"JFK", "KJFK"}
    assert airport.metadata["boundary_artcc"] == "ZNY"
    assert artcc is not None
    assert artcc.entity_type is EntityType.ARTCC
    assert artcc.entity_id == "urn:aviation-agentic-ai:facility:artcc:ZNY"


def test_neutral_term_loader_preserves_ids_mappings_and_order() -> None:
    from aviation_agentic_ai.authority.terminology import load_term_registry

    terms = load_term_registry(ROOT / "data/sources/faa_atcscc_terms_v1.yaml")
    pairs = [(term.abbreviation, term.preferred_label) for term in terms]
    gdp = next(term for term in terms if term.abbreviation == "GDP")

    assert pairs == sorted(pairs)
    assert {
        term.preferred_label for term in terms if term.abbreviation == "GS"
    } == {"Glide Slope", "Ground Stop"}
    assert gdp.term_id == (
        "urn:aviation-agentic-ai:term:traffic_management_initiative:GDP"
    )
    assert gdp.denotes_schema_term == "atm:GroundDelayProgramTMI"
    assert gdp.source_refs == [
        "faa_pilot_controller_glossary",
        "faa_tmi_glossary",
    ]
