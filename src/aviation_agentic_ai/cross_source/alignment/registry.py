from __future__ import annotations

import io
import zipfile
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.cross_source.artifacts import read_jsonl
from aviation_agentic_ai.cross_source.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
    TermCategory,
    TermConcept,
    TermDefinition,
)
from aviation_agentic_ai.cross_source.identifiers import (
    canonical_facility_id,
    canonical_term_id,
    normalize_code,
)
from aviation_agentic_ai.config import load_yaml


def _parse_effective_date(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    return datetime.strptime(text, "%m/%d/%Y").replace(tzinfo=UTC)


def _unique_strings(values: Iterable[object]) -> list[str]:
    return sorted({str(value).strip() for value in values if str(value).strip()})


def _unique_codes(values: Iterable[CodeValue]) -> list[CodeValue]:
    by_key = {(item.scheme.upper(), normalize_code(item.value)): item for item in values}
    return [by_key[key] for key in sorted(by_key)]


def stationinfo_entities(rows: Iterable[dict[str, Any]], source_ref: str) -> list[CanonicalEntity]:
    entities: list[CanonicalEntity] = []
    for row in rows:
        raw = dict(row.get("raw") or row)
        icao = normalize_code(raw.get("icaoId") or raw.get("id"))
        if not icao:
            continue
        codes = [CodeValue(scheme="ICAO", value=icao)]
        for field, scheme in (("faaId", "FAA"), ("iataId", "IATA"), ("wmoId", "WMO")):
            value = normalize_code(raw.get(field))
            if value:
                codes.append(CodeValue(scheme=scheme, value=value))
        aliases = _unique_strings(
            [raw.get("site"), raw.get("id"), raw.get("faaId"), raw.get("iataId"), icao]
        )
        entities.append(
            CanonicalEntity(
                entity_id=canonical_facility_id(EntityType.AIRPORT, icao),
                entity_type=EntityType.AIRPORT,
                preferred_label=str(raw.get("site") or icao),
                codes=_unique_codes(codes),
                aliases=aliases,
                source_refs=[source_ref],
                metadata={
                    "latitude": raw.get("lat"),
                    "longitude": raw.get("lon"),
                    "weather_station_id": raw.get("id"),
                },
            )
        )
    return entities


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
    codes = [CodeValue(scheme="FAA", value=faa), CodeValue(scheme="ICAO", value=icao)]
    return CanonicalEntity(
        entity_id=canonical_facility_id(EntityType.AIRPORT, icao),
        entity_type=EntityType.AIRPORT,
        preferred_label=name,
        codes=codes,
        aliases=_unique_strings([faa, icao, name]),
        valid_from=effective,
        source_refs=[f"faa_nasr:{effective.date().isoformat() if effective else 'unknown'}"],
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
        source_refs=[f"faa_nasr:{effective.date().isoformat() if effective else 'unknown'}"],
        metadata={"state": line[143:173].strip() or None},
    )


def _merge_entities(entities: Iterable[CanonicalEntity]) -> list[CanonicalEntity]:
    merged: dict[str, CanonicalEntity] = {}
    for entity in entities:
        prior = merged.get(entity.entity_id)
        if prior is None:
            merged[entity.entity_id] = entity
            continue
        metadata = {**prior.metadata, **{k: v for k, v in entity.metadata.items() if v is not None}}
        merged[entity.entity_id] = prior.model_copy(
            update={
                "preferred_label": entity.preferred_label or prior.preferred_label,
                "codes": _unique_codes([*prior.codes, *entity.codes]),
                "aliases": _unique_strings([*prior.aliases, *entity.aliases]),
                "source_refs": _unique_strings([*prior.source_refs, *entity.source_refs]),
                "valid_from": entity.valid_from or prior.valid_from,
                "metadata": metadata,
            }
        )
    return [merged[key] for key in sorted(merged)]


def build_facility_registry(config: dict[str, Any]) -> list[CanonicalEntity]:
    station_path = resolve_project_path(config["sources"]["stationinfo"])
    station_entities = stationinfo_entities(
        read_jsonl(station_path),
        source_ref=f"aviationweather_stationinfo:{config['snapshot_set_id']}",
    )
    selected_codes = {normalize_code(code) for code in config["cohort"]["airport_codes"]}
    nasr_path = resolve_project_path(config["sources"]["nasr_zip"])
    nasr_entities: list[CanonicalEntity] = []
    with zipfile.ZipFile(nasr_path) as archive:
        with archive.open("APT.txt") as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="latin-1", newline="")
            for line in stream:
                faa = normalize_code(line[27:31]) if line.startswith("APT") else ""
                icao = normalize_code(line[1210:1217]) if len(line) >= 1217 else ""
                if faa not in selected_codes and icao not in selected_codes:
                    continue
                entity = parse_nasr_apt_line(line)
                if entity is not None:
                    nasr_entities.append(entity)
        with archive.open("AFF.txt") as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="latin-1", newline="")
            for line in stream:
                entity = parse_nasr_aff_line(line)
                if entity is not None:
                    nasr_entities.append(entity)
    return _merge_entities([*station_entities, *nasr_entities])


def build_term_registry(config: dict[str, Any]) -> list[TermConcept]:
    seed_path = resolve_project_path(config["sources"]["term_seed"])
    payload = load_yaml(seed_path)
    terms: list[TermConcept] = []
    for item in payload.get("terms", []):
        category = TermCategory(str(item["category"]))
        abbreviation = normalize_code(item["abbreviation"])
        terms.append(
            TermConcept(
                term_id=canonical_term_id(category, abbreviation),
                abbreviation=abbreviation,
                preferred_label=str(item["preferred_label"]),
                term_category=category,
                aliases=_unique_strings(item.get("aliases", [])),
                definitions=[
                    TermDefinition(text=str(definition["text"]), source_ref=str(definition["source_ref"]))
                    for definition in item.get("definitions", [])
                ],
                denotes_schema_term=item.get("denotes_schema_term"),
                source_refs=_unique_strings(item.get("source_refs", [])),
            )
        )
    return sorted(terms, key=lambda item: (item.abbreviation, item.term_id))
