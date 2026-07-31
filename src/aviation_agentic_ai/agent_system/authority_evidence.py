"""Checksum-bound authority evidence for deterministic resolution compatibility.

This module builds resolution-audit evidence only.  It does not publish event
facts, call a model, mutate the active workflow, or widen the Formal Graph
Kernel source allowlist.
"""

from __future__ import annotations

import hashlib
import io
import json
import unicodedata
import zipfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import AwareDatetime, model_validator
from pypdf import PdfReader

from aviation_agentic_ai.agent_system.contracts import SourceFamily, SourceRecord
from aviation_agentic_ai.agent_system.construction_contracts import (
    AuthorityDefinitionEvidenceClaim,
    AuthorityRecordEvidenceClaim,
    CandidateBuildStatus,
    ConstraintCheck,
    ConstraintCheckStatus,
    FrozenContractModel,
    ResolutionCandidate,
    Sha256Hex,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.schema_guide import SchemaGuide
from aviation_agentic_ai.config import load_yaml, resolve_project_path
from aviation_agentic_ai.cross_source.alignment.registry import (
    build_term_registry,
    parse_nasr_aff_line,
    parse_nasr_apt_line,
)
from aviation_agentic_ai.cross_source.contracts import (
    CanonicalEntity,
    EntityType,
    TermCategory,
    TermConcept,
)


DEFAULT_AUTHORITY_DEFINITION_SEED = (
    "data/sources/faa_atcscc_authority_definitions_v1.yaml"
)

AuthorityArtifactKey = Literal[
    "nasr_zip",
    "nasr_manifest",
    "pilot_controller_glossary",
    "term_seed",
    "authority_definition_seed",
    "schema_guide",
]

_ARTIFACT_KEYS: tuple[AuthorityArtifactKey, ...] = (
    "authority_definition_seed",
    "nasr_manifest",
    "nasr_zip",
    "pilot_controller_glossary",
    "schema_guide",
    "term_seed",
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _stable_error(scope: str, reason_code: str) -> str:
    return stable_contract_id("authority-error", scope, reason_code)


class AuthorityArtifactBinding(FrozenContractModel):
    artifact_key: AuthorityArtifactKey
    project_path: str
    sha256: Sha256Hex
    byte_count: int


class AuthorityArtifactLoadResult(FrozenContractModel):
    artifact_key: AuthorityArtifactKey
    status: Literal["ok", "insufficient", "blocked"]
    binding: AuthorityArtifactBinding | None = None
    reason_code: str | None = None
    error_id: str | None = None

    @model_validator(mode="after")
    def validate_status_shape(self) -> "AuthorityArtifactLoadResult":
        if self.status == "ok":
            if self.binding is None or self.reason_code or self.error_id:
                raise ValueError("ok authority artifact requires only a binding")
        elif self.status == "insufficient":
            if self.binding is not None or not self.reason_code or self.error_id:
                raise ValueError("insufficient authority artifact requires reason only")
        elif self.binding is not None or not self.reason_code or not self.error_id:
            raise ValueError("blocked authority artifact requires reason and error")
        return self


class AuthoritySnapshotSet(FrozenContractModel):
    authority_snapshot_set_id: str
    base_snapshot_set_id: str
    created_at: AwareDatetime
    artifact_results: tuple[AuthorityArtifactLoadResult, ...]

    def get(self, key: AuthorityArtifactKey) -> AuthorityArtifactLoadResult:
        return next(row for row in self.artifact_results if row.artifact_key == key)


def _artifact_path(
    config: Mapping[str, Any],
    key: AuthorityArtifactKey,
    *,
    schema_guide_path: str | Path,
    definition_seed_path: str | Path,
) -> Path | None:
    if key == "schema_guide":
        return resolve_project_path(schema_guide_path)
    if key == "authority_definition_seed":
        return resolve_project_path(definition_seed_path)
    sources = config.get("sources")
    if not isinstance(sources, Mapping):
        return None
    raw = sources.get(key)
    return resolve_project_path(raw) if isinstance(raw, (str, Path)) and raw else None


def _blocked_artifact(
    key: AuthorityArtifactKey,
    reason_code: str,
) -> AuthorityArtifactLoadResult:
    return AuthorityArtifactLoadResult(
        artifact_key=key,
        status="blocked",
        reason_code=reason_code,
        error_id=_stable_error(key, reason_code),
    )


def build_authority_snapshot_set(
    config: Mapping[str, Any],
    *,
    guide: SchemaGuide,
    schema_guide_path: str | Path,
    created_at: datetime,
    definition_seed_path: str | Path = DEFAULT_AUTHORITY_DEFINITION_SEED,
) -> AuthoritySnapshotSet:
    """Bind exactly the six authority artifacts used by resolution audit."""

    seed_path = resolve_project_path(definition_seed_path)
    definition_seed: dict[str, Any] = {}
    if seed_path.exists():
        try:
            definition_seed = load_yaml(seed_path)
        except (OSError, TypeError, ValueError):
            definition_seed = {}
    expected_pcg = definition_seed.get("authority_artifact_sha256")
    results: list[AuthorityArtifactLoadResult] = []
    for key in _ARTIFACT_KEYS:
        path = _artifact_path(
            config,
            key,
            schema_guide_path=schema_guide_path,
            definition_seed_path=definition_seed_path,
        )
        if path is None:
            results.append(_blocked_artifact(key, "AUTHORITY_PATH_NOT_CONFIGURED"))
            continue
        if not path.is_file():
            results.append(_blocked_artifact(key, "AUTHORITY_ARTIFACT_MISSING"))
            continue
        try:
            checksum = _sha256_path(path)
        except OSError:
            results.append(_blocked_artifact(key, "AUTHORITY_ARTIFACT_UNREADABLE"))
            continue
        if key == "schema_guide" and checksum != guide.checksum:
            results.append(_blocked_artifact(key, "SCHEMA_CHECKSUM_MISMATCH"))
            continue
        if (
            key == "pilot_controller_glossary"
            and isinstance(expected_pcg, str)
            and checksum != expected_pcg
        ):
            results.append(_blocked_artifact(key, "PCG_CHECKSUM_MISMATCH"))
            continue
        results.append(
            AuthorityArtifactLoadResult(
                artifact_key=key,
                status="ok",
                binding=AuthorityArtifactBinding(
                    artifact_key=key,
                    project_path=str(path),
                    sha256=checksum,
                    byte_count=path.stat().st_size,
                ),
            )
        )
    ordered = tuple(sorted(results, key=lambda row: row.artifact_key))
    tokens = tuple(
        f"{row.artifact_key}={row.status}:"
        f"{row.binding.sha256 if row.binding else row.error_id}"
        for row in ordered
    )
    return AuthoritySnapshotSet(
        authority_snapshot_set_id=stable_contract_id(
            "authority-snapshot-set",
            str(config.get("snapshot_set_id", "UNKNOWN")),
            *tokens,
        ),
        base_snapshot_set_id=str(config.get("snapshot_set_id", "UNKNOWN")),
        created_at=created_at,
        artifact_results=ordered,
    )


class AuthorityBuildStatus(str, Enum):
    OK = "ok"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ExtractedPDFPage:
    page_index: int
    text: str


PDFPageExtractor = Callable[[Path], tuple[ExtractedPDFPage, ...]]


def extract_pdf_pages(path: Path) -> tuple[ExtractedPDFPage, ...]:
    reader = PdfReader(path)
    return tuple(
        ExtractedPDFPage(page_index=index, text=page.extract_text() or "")
        for index, page in enumerate(reader.pages)
    )


@dataclass(frozen=True)
class NASRAuthorityRecord:
    candidate_id: str
    member_name: str
    record_locator: str
    normalized_raw_record: str
    raw_record_sha256: str
    authority_source_ref: str


@dataclass(frozen=True)
class PCGAuthorityDefinition:
    candidate_id: str
    surface_form: str
    definition_text: str
    definition_locator: str
    authority_source_ref: str


@dataclass(frozen=True)
class FacilityAuthorityCatalog:
    status: AuthorityBuildStatus
    entities: tuple[CanonicalEntity, ...]
    records: tuple[NASRAuthorityRecord, ...]
    reason_code: str | None = None
    error_id: str | None = None


@dataclass(frozen=True)
class TermAuthorityCatalog:
    status: AuthorityBuildStatus
    definitions: tuple[PCGAuthorityDefinition, ...]
    registry_terms: tuple[TermConcept, ...]
    reason_code: str | None = None
    error_id: str | None = None


@dataclass(frozen=True)
class LoadedAuthorityCatalog:
    facility: FacilityAuthorityCatalog
    terminology: TermAuthorityCatalog
    snapshots: AuthoritySnapshotSet
    schema_slice_id: str
    schema_snapshot_sha256: str


@dataclass(frozen=True)
class AuthorityCandidateBuildResult:
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    status: AuthorityBuildStatus
    candidate: ResolutionCandidate | None = None
    evidence_claim: (
        AuthorityRecordEvidenceClaim | AuthorityDefinitionEvidenceClaim | None
    ) = None
    source_record: SourceRecord | None = None
    reason_code: str | None = None
    error_id: str | None = None

    def __post_init__(self) -> None:
        if self.status is AuthorityBuildStatus.OK:
            if not self.candidate or not self.evidence_claim or not self.source_record:
                raise ValueError("ok authority candidate requires candidate and evidence")
            if self.reason_code or self.error_id:
                raise ValueError("ok authority candidate forbids failure metadata")
        elif self.status is AuthorityBuildStatus.INSUFFICIENT:
            if not self.candidate or not self.reason_code:
                raise ValueError("insufficient authority candidate requires candidate and reason")
            if self.evidence_claim or self.source_record or self.error_id:
                raise ValueError("insufficient authority candidate forbids source evidence")
        else:
            if self.candidate or self.evidence_claim or self.source_record:
                raise ValueError("blocked authority candidate forbids unvalidated content")
            if not self.reason_code or not self.error_id:
                raise ValueError("blocked authority candidate requires reason and error")


class AuthoritySourceContentFields(FrozenContractModel):
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    preferred_label: str
    candidate_type: str
    surface_form: str
    authority_text: str
    authority_source_ref: str
    authority_locator: str
    authority_record_sha256: Sha256Hex | None = None
    authority_artifact_key: Literal[
        "nasr_zip",
        "pilot_controller_glossary",
    ]
    authority_artifact_sha256: Sha256Hex
    manifest_artifact_key: Literal["nasr_manifest"] | None = None
    manifest_artifact_sha256: Sha256Hex | None = None
    definition_registry_artifact_sha256: Sha256Hex | None = None
    term_registry_artifact_sha256: Sha256Hex | None = None

    @model_validator(mode="after")
    def validate_domain_fields(self) -> "AuthoritySourceContentFields":
        if self.candidate_kind == "facility":
            if not (
                self.authority_record_sha256
                and self.manifest_artifact_key == "nasr_manifest"
                and self.manifest_artifact_sha256
                and self.authority_artifact_key == "nasr_zip"
            ):
                raise ValueError("facility authority content requires NASR bindings")
            if self.definition_registry_artifact_sha256 or self.term_registry_artifact_sha256:
                raise ValueError("facility authority content forbids term bindings")
        else:
            if not (
                self.definition_registry_artifact_sha256
                and self.term_registry_artifact_sha256
                and self.authority_artifact_key == "pilot_controller_glossary"
            ):
                raise ValueError("term authority content requires PCG and registries")
            if (
                self.authority_record_sha256
                or self.manifest_artifact_key
                or self.manifest_artifact_sha256
            ):
                raise ValueError("term authority content forbids NASR bindings")
        return self


def normalize_authority_text(value: str) -> str:
    if "\x00" in value:
        raise ValueError("authority text contains NUL")
    normalized = unicodedata.normalize("NFC", value).replace("\r\n", "\n").replace(
        "\r", "\n"
    )
    lines = [line.rstrip(" \t") for line in normalized.split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def canonical_authority_source_content(fields: AuthoritySourceContentFields) -> str:
    normalized = fields.model_copy(
        update={"authority_text": normalize_authority_text(fields.authority_text)}
    )
    return json.dumps(
        normalized.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _binding(
    snapshots: AuthoritySnapshotSet,
    key: AuthorityArtifactKey,
) -> AuthorityArtifactBinding | None:
    result = snapshots.get(key)
    return result.binding if result.status == "ok" else None


def _domain_block(
    snapshots: AuthoritySnapshotSet,
    keys: tuple[AuthorityArtifactKey, ...],
) -> tuple[str, str] | None:
    for key in keys:
        row = snapshots.get(key)
        if row.status != "ok":
            return row.reason_code or "AUTHORITY_DOMAIN_BLOCKED", row.error_id or (
                _stable_error(key, "AUTHORITY_DOMAIN_BLOCKED")
            )
    return None


def _manifest_zip_checksum(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    matches = [
        row.get("raw_payload_hash")
        for row in payload.get("files", [])
        if isinstance(row, dict)
        and row.get("record_type") == "nasr_28_day_subscription_zip"
    ]
    return matches[0] if len(matches) == 1 and isinstance(matches[0], str) else None


def _load_facility_catalog(
    config: Mapping[str, Any],
    snapshots: AuthoritySnapshotSet,
) -> FacilityAuthorityCatalog:
    blocked = _domain_block(
        snapshots,
        ("nasr_zip", "nasr_manifest", "schema_guide"),
    )
    if blocked:
        return FacilityAuthorityCatalog(
            status=AuthorityBuildStatus.BLOCKED,
            entities=(),
            records=(),
            reason_code=blocked[0],
            error_id=blocked[1],
        )
    zip_binding = _binding(snapshots, "nasr_zip")
    manifest_binding = _binding(snapshots, "nasr_manifest")
    assert zip_binding and manifest_binding
    manifest_path = Path(manifest_binding.project_path)
    if _manifest_zip_checksum(manifest_path) != zip_binding.sha256:
        reason = "NASR_MANIFEST_ZIP_CHECKSUM_MISMATCH"
        return FacilityAuthorityCatalog(
            status=AuthorityBuildStatus.BLOCKED,
            entities=(),
            records=(),
            reason_code=reason,
            error_id=_stable_error("facility", reason),
        )
    entities: list[CanonicalEntity] = []
    records: list[NASRAuthorityRecord] = []
    try:
        with zipfile.ZipFile(zip_binding.project_path) as archive:
            for member_name, parser in (
                ("APT.txt", parse_nasr_apt_line),
                ("AFF.txt", parse_nasr_aff_line),
            ):
                with archive.open(member_name) as raw:
                    stream = io.TextIOWrapper(raw, encoding="latin-1", newline="")
                    for line in stream:
                        entity = parser(line.rstrip("\r\n"))
                        if entity is None:
                            continue
                        codes = {code.value.upper() for code in entity.codes}
                        effective = (
                            entity.valid_from.date().isoformat()
                            if entity.valid_from
                            else "unknown"
                        )
                        code = next(
                            (
                                item.value
                                for item in entity.codes
                                if item.scheme == "ICAO"
                            ),
                            next(iter(sorted(codes)), entity.entity_id),
                        )
                        source_ref = (
                            f"faa_nasr:{effective}:{member_name}:{code}"
                        )
                        normalized = normalize_authority_text(line.rstrip("\r\n"))
                        entities.append(
                            entity.model_copy(update={"source_refs": [source_ref]})
                        )
                        records.append(
                            NASRAuthorityRecord(
                                candidate_id=entity.entity_id,
                                member_name=member_name,
                                record_locator=source_ref,
                                normalized_raw_record=normalized,
                                raw_record_sha256=_sha256_bytes(
                                    normalized.encode("utf-8")
                                ),
                                authority_source_ref=source_ref,
                            )
                        )
    except (OSError, KeyError, zipfile.BadZipFile):
        reason = "NASR_ARCHIVE_INVALID"
        return FacilityAuthorityCatalog(
            status=AuthorityBuildStatus.BLOCKED,
            entities=(),
            records=(),
            reason_code=reason,
            error_id=_stable_error("facility", reason),
        )
    ids = [entity.entity_id for entity in entities]
    if len(ids) != len(set(ids)):
        reason = "DUPLICATE_NASR_CANDIDATE"
        return FacilityAuthorityCatalog(
            status=AuthorityBuildStatus.BLOCKED,
            entities=(),
            records=(),
            reason_code=reason,
            error_id=_stable_error("facility", reason),
        )
    return FacilityAuthorityCatalog(
        status=AuthorityBuildStatus.OK,
        entities=tuple(sorted(entities, key=lambda row: row.entity_id)),
        records=tuple(sorted(records, key=lambda row: row.candidate_id)),
    )


def _compact_whitespace(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


_PCG_DASHES = frozenset("-−–—")


def _pcg_key(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value).upper()
    return "".join(character for character in normalized if character.isalnum())


def _pcg_source_locator(source_ref: str) -> tuple[str, str] | None:
    parts = source_ref.split(":")
    if (
        len(parts) != 3
        or parts[0] != "faa_pilot_controller_glossary"
        or not parts[1].startswith("PCG_")
        or not parts[2]
    ):
        return None
    page_marker = parts[1].replace("_", " ").replace("−", "-").upper()
    return page_marker, _pcg_key(parts[2].replace("_", " "))


def _pcg_entry_start_key(line: str) -> str | None:
    """Return the entry heading key for one extracted PCG glossary line."""

    delimiter_index: int | None = None
    for index, character in enumerate(line):
        if character not in _PCG_DASHES:
            continue
        prefix = line[:index].strip()
        if (
            any(character.isalpha() for character in prefix)
            and not any(character.islower() for character in prefix)
            and not prefix.startswith("(")
        ):
            delimiter_index = index
    if delimiter_index is None:
        return None
    heading = line[:delimiter_index].strip()
    if heading.endswith(")") and "(" in heading:
        heading = heading[: heading.rfind("(")].strip()
    return _pcg_key(heading) or None


def _pcg_page_marker_text(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    for dash in _PCG_DASHES - {"-"}:
        normalized = normalized.replace(dash, "-")
    return _compact_whitespace(normalized).upper()


def _page_binds_pcg_definition(
    page: ExtractedPDFPage,
    *,
    source_ref: str,
    excerpt: str,
) -> bool:
    locator = _pcg_source_locator(source_ref)
    if locator is None:
        return False
    page_marker, claimed_entry_key = locator
    if page_marker not in _pcg_page_marker_text(page.text):
        return False

    lines = page.text.splitlines()
    entry_starts = tuple(
        (index, key)
        for index, line in enumerate(lines)
        if (key := _pcg_entry_start_key(line)) is not None
    )
    matches = 0
    for offset, (start, entry_key) in enumerate(entry_starts):
        if entry_key != claimed_entry_key:
            continue
        end = (
            entry_starts[offset + 1][0]
            if offset + 1 < len(entry_starts)
            else len(lines)
        )
        entry_text = _compact_whitespace("\n".join(lines[start:end]))
        if _compact_whitespace(excerpt) in entry_text:
            matches += 1
    return matches == 1


def _load_term_catalog(
    config: Mapping[str, Any],
    snapshots: AuthoritySnapshotSet,
    *,
    definition_seed_path: str | Path,
    pcg_page_extractor: PDFPageExtractor,
) -> TermAuthorityCatalog:
    blocked = _domain_block(
        snapshots,
        (
            "pilot_controller_glossary",
            "term_seed",
            "authority_definition_seed",
            "schema_guide",
        ),
    )
    if blocked:
        return TermAuthorityCatalog(
            status=AuthorityBuildStatus.BLOCKED,
            definitions=(),
            registry_terms=(),
            reason_code=blocked[0],
            error_id=blocked[1],
        )
    try:
        registry_terms = tuple(build_term_registry(dict(config)))
        seed = load_yaml(definition_seed_path)
        pcg_binding = _binding(snapshots, "pilot_controller_glossary")
        assert pcg_binding
        pages = pcg_page_extractor(Path(pcg_binding.project_path))
    except (OSError, TypeError, ValueError):
        reason = "TERM_AUTHORITY_LOAD_FAILED"
        return TermAuthorityCatalog(
            status=AuthorityBuildStatus.BLOCKED,
            definitions=(),
            registry_terms=(),
            reason_code=reason,
            error_id=_stable_error("terminology", reason),
        )
    if (
        seed.get("version") != "faa-atcscc-authority-definitions-v1"
        or seed.get("authority_source") != "faa_pilot_controller_glossary"
        or seed.get("authority_artifact_key") != "pilot_controller_glossary"
    ):
        reason = "AUTHORITY_DEFINITION_SEED_INVALID"
        return TermAuthorityCatalog(
            status=AuthorityBuildStatus.BLOCKED,
            definitions=(),
            registry_terms=(),
            reason_code=reason,
            error_id=_stable_error("terminology", reason),
        )
    by_key = {
        (term.abbreviation, term.preferred_label): term for term in registry_terms
    }
    definitions: list[PCGAuthorityDefinition] = []
    seen: set[str] = set()
    for row in seed.get("definitions", []):
        if not isinstance(row, dict):
            continue
        key = (str(row.get("abbreviation", "")), str(row.get("preferred_label", "")))
        term = by_key.get(key)
        source_ref = str(row.get("source_ref", ""))
        excerpt = str(row.get("text", ""))
        if (
            term is None
            or not source_ref.startswith("faa_pilot_controller_glossary:")
            or not excerpt
            or term.term_id in seen
        ):
            reason = "AUTHORITY_DEFINITION_BINDING_INVALID"
            return TermAuthorityCatalog(
                status=AuthorityBuildStatus.BLOCKED,
                definitions=(),
                registry_terms=(),
                reason_code=reason,
                error_id=_stable_error("terminology", reason),
            )
        matching_pages = [
            page
            for page in pages
            if _page_binds_pcg_definition(
                page,
                source_ref=source_ref,
                excerpt=excerpt,
            )
        ]
        if len(matching_pages) != 1:
            reason = "PCG_DEFINITION_NOT_UNIQUE"
            return TermAuthorityCatalog(
                status=AuthorityBuildStatus.BLOCKED,
                definitions=(),
                registry_terms=(),
                reason_code=reason,
                error_id=_stable_error("terminology", reason),
            )
        page = matching_pages[0]
        definitions.append(
            PCGAuthorityDefinition(
                candidate_id=term.term_id,
                surface_form=term.abbreviation,
                definition_text=excerpt,
                definition_locator=f"page:{page.page_index}:{source_ref}",
                authority_source_ref=source_ref,
            )
        )
        seen.add(term.term_id)
    return TermAuthorityCatalog(
        status=AuthorityBuildStatus.OK,
        definitions=tuple(sorted(definitions, key=lambda row: row.candidate_id)),
        registry_terms=registry_terms,
    )


def load_authority_catalog(
    config: dict[str, Any],
    *,
    guide: SchemaGuide,
    schema_guide_path: str | Path,
    created_at: datetime,
    pcg_page_extractor: PDFPageExtractor = extract_pdf_pages,
    definition_seed_path: str | Path = DEFAULT_AUTHORITY_DEFINITION_SEED,
) -> LoadedAuthorityCatalog:
    snapshots = build_authority_snapshot_set(
        config,
        guide=guide,
        schema_guide_path=schema_guide_path,
        created_at=created_at,
        definition_seed_path=definition_seed_path,
    )
    return LoadedAuthorityCatalog(
        facility=_load_facility_catalog(config, snapshots),
        terminology=_load_term_catalog(
            config,
            snapshots,
            definition_seed_path=definition_seed_path,
            pcg_page_extractor=pcg_page_extractor,
        ),
        snapshots=snapshots,
        schema_slice_id=guide.schema_slice_id,
        schema_snapshot_sha256=guide.checksum,
    )


_FACILITY_CLASS = {
    EntityType.AIRPORT: "nas:Airport",
    EntityType.ARTCC: "nas:ARTCC",
}


def _surface_form(entity: CanonicalEntity) -> str:
    for scheme in ("FAA", "ICAO", "FAA_ARTCC", "ICAO_ARTCC"):
        for code in entity.codes:
            if code.scheme == scheme:
                return code.value
    return entity.preferred_label


def _constraint(
    *,
    candidate_id: str,
    check_kind: Literal[
        "structural_slot",
        "expected_entity_type",
        "schema_compatibility",
    ],
    passed: bool,
    structural_slot: str,
    expected_entity_type: str,
    schema_checksum: str,
    evidence_ids: tuple[str, ...],
) -> ConstraintCheck:
    return ConstraintCheck(
        constraint_id=stable_contract_id(
            "resolution-constraint",
            candidate_id,
            check_kind,
            structural_slot,
            expected_entity_type,
            schema_checksum,
        ),
        candidate_id=candidate_id,
        check_kind=check_kind,
        status=ConstraintCheckStatus.PASS if passed else ConstraintCheckStatus.FAIL,
        reason_code=f"{check_kind.upper()}_{'MATCH' if passed else 'MISMATCH'}",
        evidence_ids=evidence_ids,
        schema_snapshot_sha256=(
            schema_checksum if check_kind == "schema_compatibility" else None
        ),
    )


def _candidate(
    *,
    candidate_id: str,
    candidate_kind: Literal["facility", "term"],
    preferred_label: str,
    surface_form: str,
    candidate_type: str,
    ontology_class: str | None,
    structural_slot: str,
    expected_entity_type: str,
    expected_slot: str,
    expected_type_match: bool,
    guide: SchemaGuide,
    evidence_ids: tuple[str, ...],
) -> ResolutionCandidate:
    ontology_iri = (
        guide.classes[ontology_class].iri
        if ontology_class and guide.has_class(ontology_class)
        else None
    )
    return ResolutionCandidate(
        candidate_id=candidate_id,
        candidate_kind=candidate_kind,
        preferred_label=preferred_label,
        surface_form=surface_form,
        candidate_type=candidate_type,
        ontology_class_prefixed=ontology_class if ontology_iri else None,
        ontology_class_iri=ontology_iri,
        authority_evidence_ids=evidence_ids,
        constraint_checks=tuple(
            _constraint(
                candidate_id=candidate_id,
                check_kind=kind,
                passed=passed,
                structural_slot=structural_slot,
                expected_entity_type=expected_entity_type,
                schema_checksum=guide.checksum,
                evidence_ids=evidence_ids,
            )
            for kind, passed in (
                ("structural_slot", structural_slot == expected_slot),
                ("expected_entity_type", expected_type_match),
                (
                    "schema_compatibility",
                    bool(ontology_class and guide.has_class(ontology_class)),
                ),
            )
        ),
    )


def _blocked_candidate(
    candidate_id: str,
    candidate_kind: Literal["facility", "term"],
    reason_code: str,
    error_id: str | None,
) -> AuthorityCandidateBuildResult:
    return AuthorityCandidateBuildResult(
        candidate_id=candidate_id,
        candidate_kind=candidate_kind,
        status=AuthorityBuildStatus.BLOCKED,
        reason_code=reason_code,
        error_id=error_id or _stable_error(candidate_kind, reason_code),
    )


def build_facility_resolution_candidate(
    entity: CanonicalEntity,
    *,
    structural_slot: str,
    expected_entity_type: str,
    catalog: FacilityAuthorityCatalog,
    authority_snapshots: AuthoritySnapshotSet,
    guide: SchemaGuide,
) -> AuthorityCandidateBuildResult:
    if catalog.status is AuthorityBuildStatus.BLOCKED:
        return _blocked_candidate(
            entity.entity_id,
            "facility",
            catalog.reason_code or "FACILITY_AUTHORITY_BLOCKED",
            catalog.error_id,
        )
    record = next(
        (row for row in catalog.records if row.candidate_id == entity.entity_id),
        None,
    )
    ontology_class = _FACILITY_CLASS.get(entity.entity_type)
    candidate_type = entity.entity_type.value
    if record is None:
        candidate = _candidate(
            candidate_id=entity.entity_id,
            candidate_kind="facility",
            preferred_label=entity.preferred_label,
            surface_form=_surface_form(entity),
            candidate_type=candidate_type,
            ontology_class=ontology_class,
            structural_slot=structural_slot,
            expected_entity_type=expected_entity_type,
            expected_slot="controlled_nas_element",
            expected_type_match=candidate_type == expected_entity_type,
            guide=guide,
            evidence_ids=(),
        )
        return AuthorityCandidateBuildResult(
            candidate_id=entity.entity_id,
            candidate_kind="facility",
            status=AuthorityBuildStatus.INSUFFICIENT,
            candidate=candidate,
            reason_code="NASR_RECORD_MISSING",
        )
    zip_binding = _binding(authority_snapshots, "nasr_zip")
    manifest_binding = _binding(authority_snapshots, "nasr_manifest")
    if not zip_binding or not manifest_binding:
        return _blocked_candidate(
            entity.entity_id,
            "facility",
            "FACILITY_ARTIFACT_BINDING_MISSING",
            None,
        )
    fields = AuthoritySourceContentFields(
        candidate_id=entity.entity_id,
        candidate_kind="facility",
        preferred_label=entity.preferred_label,
        candidate_type=candidate_type,
        surface_form=_surface_form(entity),
        authority_text=record.normalized_raw_record,
        authority_source_ref=record.authority_source_ref,
        authority_locator=record.record_locator,
        authority_record_sha256=record.raw_record_sha256,
        authority_artifact_key="nasr_zip",
        authority_artifact_sha256=zip_binding.sha256,
        manifest_artifact_key="nasr_manifest",
        manifest_artifact_sha256=manifest_binding.sha256,
    )
    content = canonical_authority_source_content(fields)
    snapshot_sha = _sha256_bytes(content.encode("utf-8"))
    source_id = stable_contract_id(
        "authority-source",
        "facility",
        entity.entity_id,
        record.authority_source_ref,
        snapshot_sha,
    )
    evidence_id = stable_contract_id(
        "authority-evidence",
        entity.entity_id,
        source_id,
        snapshot_sha,
        zip_binding.sha256,
    )
    evidence = AuthorityRecordEvidenceClaim(
        evidence_id=evidence_id,
        candidate_id=entity.entity_id,
        evidence_kind="facility_record",
        authority_record_text=record.normalized_raw_record,
        authority_record_locator=record.record_locator,
        authority_record_sha256=record.raw_record_sha256,
        authority_source_ref=record.authority_source_ref,
        source_id=source_id,
        source_snapshot_sha256=snapshot_sha,
        authority_artifact_key="nasr_zip",
        authority_artifact_sha256=zip_binding.sha256,
        manifest_artifact_key="nasr_manifest",
        manifest_artifact_sha256=manifest_binding.sha256,
    )
    candidate = _candidate(
        candidate_id=entity.entity_id,
        candidate_kind="facility",
        preferred_label=entity.preferred_label,
        surface_form=_surface_form(entity),
        candidate_type=candidate_type,
        ontology_class=ontology_class,
        structural_slot=structural_slot,
        expected_entity_type=expected_entity_type,
        expected_slot="controlled_nas_element",
        expected_type_match=candidate_type == expected_entity_type,
        guide=guide,
        evidence_ids=(evidence_id,),
    )
    return AuthorityCandidateBuildResult(
        candidate_id=entity.entity_id,
        candidate_kind="facility",
        status=AuthorityBuildStatus.OK,
        candidate=candidate,
        evidence_claim=evidence,
        source_record=SourceRecord(
            source_id=source_id,
            family=SourceFamily.NASR_FACILITY,
            content=content,
            title=entity.preferred_label,
        ),
    )


def build_term_resolution_candidate(
    term: TermConcept,
    *,
    structural_slot: str,
    expected_entity_type: str,
    catalog: TermAuthorityCatalog,
    authority_snapshots: AuthoritySnapshotSet,
    guide: SchemaGuide,
) -> AuthorityCandidateBuildResult:
    if catalog.status is AuthorityBuildStatus.BLOCKED:
        return _blocked_candidate(
            term.term_id,
            "term",
            catalog.reason_code or "TERM_AUTHORITY_BLOCKED",
            catalog.error_id,
        )
    definition = next(
        (row for row in catalog.definitions if row.candidate_id == term.term_id),
        None,
    )
    expected_type_match = (
        term.term_category is TermCategory.TRAFFIC_MANAGEMENT_INITIATIVE
        and expected_entity_type == "traffic_management_initiative"
    )
    if definition is None:
        candidate = _candidate(
            candidate_id=term.term_id,
            candidate_kind="term",
            preferred_label=term.preferred_label,
            surface_form=term.abbreviation,
            candidate_type=term.term_category.value,
            ontology_class=term.denotes_schema_term,
            structural_slot=structural_slot,
            expected_entity_type=expected_entity_type,
            expected_slot="traffic_management_initiative_type",
            expected_type_match=expected_type_match,
            guide=guide,
            evidence_ids=(),
        )
        return AuthorityCandidateBuildResult(
            candidate_id=term.term_id,
            candidate_kind="term",
            status=AuthorityBuildStatus.INSUFFICIENT,
            candidate=candidate,
            reason_code="PCG_DEFINITION_MISSING",
        )
    pcg_binding = _binding(authority_snapshots, "pilot_controller_glossary")
    definition_binding = _binding(authority_snapshots, "authority_definition_seed")
    term_binding = _binding(authority_snapshots, "term_seed")
    if not pcg_binding or not definition_binding or not term_binding:
        return _blocked_candidate(
            term.term_id,
            "term",
            "TERM_ARTIFACT_BINDING_MISSING",
            None,
        )
    fields = AuthoritySourceContentFields(
        candidate_id=term.term_id,
        candidate_kind="term",
        preferred_label=term.preferred_label,
        candidate_type=term.term_category.value,
        surface_form=term.abbreviation,
        authority_text=definition.definition_text,
        authority_source_ref=definition.authority_source_ref,
        authority_locator=definition.definition_locator,
        authority_artifact_key="pilot_controller_glossary",
        authority_artifact_sha256=pcg_binding.sha256,
        definition_registry_artifact_sha256=definition_binding.sha256,
        term_registry_artifact_sha256=term_binding.sha256,
    )
    content = canonical_authority_source_content(fields)
    snapshot_sha = _sha256_bytes(content.encode("utf-8"))
    source_id = stable_contract_id(
        "authority-source",
        "term",
        term.term_id,
        definition.authority_source_ref,
        snapshot_sha,
    )
    evidence_id = stable_contract_id(
        "authority-evidence",
        term.term_id,
        source_id,
        snapshot_sha,
        pcg_binding.sha256,
    )
    evidence = AuthorityDefinitionEvidenceClaim(
        evidence_id=evidence_id,
        candidate_id=term.term_id,
        evidence_kind="term_definition",
        definition_text=definition.definition_text,
        definition_locator=definition.definition_locator,
        authority_source_ref=definition.authority_source_ref,
        source_id=source_id,
        source_snapshot_sha256=snapshot_sha,
        authority_artifact_key="pilot_controller_glossary",
        authority_artifact_sha256=pcg_binding.sha256,
        definition_registry_artifact_key="authority_definition_seed",
        definition_registry_artifact_sha256=definition_binding.sha256,
        term_registry_artifact_key="term_seed",
        term_registry_artifact_sha256=term_binding.sha256,
    )
    candidate = _candidate(
        candidate_id=term.term_id,
        candidate_kind="term",
        preferred_label=term.preferred_label,
        surface_form=term.abbreviation,
        candidate_type=term.term_category.value,
        ontology_class=term.denotes_schema_term,
        structural_slot=structural_slot,
        expected_entity_type=expected_entity_type,
        expected_slot="traffic_management_initiative_type",
        expected_type_match=expected_type_match,
        guide=guide,
        evidence_ids=(evidence_id,),
    )
    return AuthorityCandidateBuildResult(
        candidate_id=term.term_id,
        candidate_kind="term",
        status=AuthorityBuildStatus.OK,
        candidate=candidate,
        evidence_claim=evidence,
        source_record=SourceRecord(
            source_id=source_id,
            family=SourceFamily.FAA_TERM,
            content=content,
            title=term.preferred_label,
        ),
    )


def candidate_result_status(
    results: tuple[AuthorityCandidateBuildResult, ...],
) -> CandidateBuildStatus:
    """Conservatively roll up mention-matched candidate build results."""

    if any(row.status is AuthorityBuildStatus.BLOCKED for row in results):
        return CandidateBuildStatus.BLOCKED
    if any(row.status is AuthorityBuildStatus.INSUFFICIENT for row in results):
        return CandidateBuildStatus.INSUFFICIENT
    return CandidateBuildStatus.OK
