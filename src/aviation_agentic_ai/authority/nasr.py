"""Deterministic parsers for the NASR airport and facility records in use."""

from __future__ import annotations

from datetime import UTC, datetime

from aviation_agentic_ai.authority.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
)
from aviation_agentic_ai.authority.identifiers import (
    canonical_facility_id,
    normalize_code,
)


def _parse_effective_date(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    return datetime.strptime(text, "%m/%d/%Y").replace(tzinfo=UTC)


def _unique_strings(values: list[object]) -> list[str]:
    return sorted({str(value).strip() for value in values if str(value).strip()})


def parse_nasr_apt_line(line: str) -> CanonicalEntity | None:
    if not line.startswith("APT") or len(line) < 1217:
        return None
    faa = normalize_code(line[27:31])
    icao = normalize_code(line[1210:1217])
    if not faa or not icao:
        return None
    name = line[133:183].strip() or icao
    boundary_artcc = normalize_code(line[637:641])
    responsible_artcc = normalize_code(line[674:678])
    effective = _parse_effective_date(line[31:41])
    codes = [
        CodeValue(scheme="FAA", value=faa),
        CodeValue(scheme="ICAO", value=icao),
    ]
    return CanonicalEntity(
        entity_id=canonical_facility_id(EntityType.AIRPORT, icao),
        entity_type=EntityType.AIRPORT,
        preferred_label=name,
        codes=codes,
        aliases=_unique_strings([faa, icao, name]),
        valid_from=effective,
        source_refs=[
            f"faa_nasr:{effective.date().isoformat() if effective else 'unknown'}"
        ],
        metadata={
            "boundary_artcc": boundary_artcc or None,
            "responsible_artcc": responsible_artcc or None,
            "city": line[93:133].strip() or None,
            "state": line[48:50].strip() or None,
        },
    )


def parse_nasr_aff_line(line: str) -> CanonicalEntity | None:
    if not line.startswith("AFF1") or len(line) < 229:
        return None
    facility_type = line[128:133].strip()
    if facility_type != "ARTCC":
        return None
    center_id = normalize_code(line[4:8])
    if not center_id:
        return None
    name = line[8:48].strip() or center_id
    icao = normalize_code(line[225:229])
    effective = _parse_effective_date(line[133:143])
    codes = [CodeValue(scheme="FAA_ARTCC", value=center_id)]
    if icao:
        codes.append(CodeValue(scheme="ICAO_ARTCC", value=icao))
    return CanonicalEntity(
        entity_id=canonical_facility_id(EntityType.ARTCC, center_id),
        entity_type=EntityType.ARTCC,
        preferred_label=f"{name} ARTCC",
        codes=codes,
        aliases=_unique_strings([center_id, icao, name, f"{name} Center"]),
        valid_from=effective,
        source_refs=[
            f"faa_nasr:{effective.date().isoformat() if effective else 'unknown'}"
        ],
        metadata={"state": line[143:173].strip() or None},
    )
