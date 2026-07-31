from __future__ import annotations

import io
import zipfile
from collections.abc import Iterable
from typing import Any

from aviation_agentic_ai.authority.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
    TermConcept,
)
from aviation_agentic_ai.authority.identifiers import (
    canonical_facility_id,
    normalize_code,
)
from aviation_agentic_ai.authority.nasr import (
    parse_nasr_aff_line,
    parse_nasr_apt_line,
)
from aviation_agentic_ai.authority.terminology import load_term_registry
from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.cross_source.artifacts import read_jsonl


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
    return load_term_registry(seed_path)
