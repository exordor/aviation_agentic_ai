"""Representative contracts for source-bound resolution authority evidence."""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    AuthoritySourceContentFields,
    ExtractedPDFPage,
    build_authority_snapshot_set,
    build_facility_resolution_candidate,
    build_term_resolution_candidate,
    canonical_authority_source_content,
    load_authority_catalog,
    normalize_authority_text,
)
from aviation_agentic_ai.agent_system.construction_contracts import (
    ConstraintCheckStatus,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.config import load_yaml


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/agent_system_authority"
SCHEMA_PATH = ROOT / "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json"
TERM_SEED = ROOT / "data/sources/faa_atcscc_terms_v1.yaml"
DEFINITION_SEED = ROOT / "data/sources/faa_atcscc_authority_definitions_v1.yaml"
NOW = datetime(2026, 5, 19, 20, 0, tzinfo=UTC)

CONFIG_SHA256 = "3b60f312bf9592bad8e3eaf35daf2cdffb585193e4112e320b6bdd8ca683b38a"
TERM_SEED_SHA256 = "8e8941775f2e086429fb1af9751e1a191c650e737e9de5f9b10b5a4812f3bf77"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nasr_fixture_lines() -> str:
    lines: list[str] = []
    for raw in (FIXTURES / "nasr_records.txt").read_text().splitlines():
        row = json.loads(raw)
        chars = [" "] * 1220
        chars[0:3] = "APT"
        chars[27:31] = f"{row['faa']:<4}"
        chars[31:41] = row["effective"]
        chars[48:50] = row["state"]
        chars[93:133] = f"{row['city']:<40}"
        chars[133:183] = f"{row['name']:<50}"
        chars[637:641] = f"{row['artcc']:<4}"
        chars[674:678] = f"{row['artcc']:<4}"
        chars[1210:1217] = f"{row['icao']:<7}"
        lines.append("".join(chars))
    return "\n".join(lines) + "\n"


def _test_inputs(tmp_path: Path) -> tuple[dict, Path]:
    nasr_zip = tmp_path / "nasr.zip"
    with zipfile.ZipFile(nasr_zip, "w") as archive:
        archive.writestr(
            "APT.txt",
            _nasr_fixture_lines(),
        )
        archive.writestr("AFF.txt", "")
    nasr_manifest = tmp_path / "nasr-manifest.json"
    nasr_manifest.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "record_type": "nasr_28_day_subscription_zip",
                        "raw_payload_hash": _sha(nasr_zip),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    pcg = tmp_path / "pcg.pdf"
    pcg.write_bytes(b"portable-pcg-test-input")
    seed = load_yaml(DEFINITION_SEED)
    seed["authority_artifact_sha256"] = _sha(pcg)
    definition_seed = tmp_path / "definitions.yaml"
    import yaml

    definition_seed.write_text(
        yaml.safe_dump(seed, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    config = load_yaml(ROOT / "configs/cross_source_v1.yaml")
    config["sources"].update(
        {
            "nasr_zip": str(nasr_zip),
            "nasr_manifest": str(nasr_manifest),
            "pilot_controller_glossary": str(pcg),
            "term_seed": str(TERM_SEED),
            "metar": str(tmp_path / "ignored-metar.jsonl"),
            "bts_on_time_snapshot": str(tmp_path / "ignored-bts.jsonl"),
        }
    )
    return config, definition_seed


def _extract_fixture_pages(_path: Path) -> tuple[ExtractedPDFPage, ...]:
    first, second = (
        (FIXTURES / "pcg_excerpt.txt")
        .read_text(encoding="utf-8")
        .split("=== TEST PAGE BREAK ===")
    )
    return (
        ExtractedPDFPage(page_index=56, text=first),
        ExtractedPDFPage(page_index=58, text=second),
    )


def _catalog(tmp_path: Path):
    config, definition_seed = _test_inputs(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    return load_authority_catalog(
        config,
        guide=guide,
        schema_guide_path=SCHEMA_PATH,
        created_at=NOW,
        pcg_page_extractor=_extract_fixture_pages,
        definition_seed_path=definition_seed,
    )


def _term(catalog, label: str):
    return next(
        term
        for term in catalog.terminology.registry_terms
        if term.preferred_label == label
    )


def _facility(catalog, icao: str):
    return next(
        entity
        for entity in catalog.facility.entities
        if any(code.value == icao for code in entity.codes)
    )


def test_v1_inputs_keep_frozen_checksums():
    assert _sha(ROOT / "configs/cross_source_v1.yaml") == CONFIG_SHA256
    assert _sha(TERM_SEED) == TERM_SEED_SHA256


def test_snapshot_set_selects_exact_authority_inputs_and_ignores_context(tmp_path):
    config, definition_seed = _test_inputs(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    first = build_authority_snapshot_set(
        config,
        guide=guide,
        schema_guide_path=SCHEMA_PATH,
        created_at=NOW,
        definition_seed_path=definition_seed,
    )
    config["sources"]["metar"] = "different-but-ignored"
    config["sources"]["bts_on_time_snapshot"] = "also-ignored"
    second = build_authority_snapshot_set(
        config,
        guide=guide,
        schema_guide_path=SCHEMA_PATH,
        created_at=NOW,
        definition_seed_path=definition_seed,
    )

    assert first.authority_snapshot_set_id == second.authority_snapshot_set_id
    assert {row.artifact_key for row in first.artifact_results} == {
        "nasr_zip",
        "nasr_manifest",
        "pilot_controller_glossary",
        "term_seed",
        "authority_definition_seed",
        "schema_guide",
    }


def test_portable_fixture_manifest_is_explicitly_test_only():
    manifest = json.loads(
        (FIXTURES / "fixture_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["test_fixture_only"] is True
    assert manifest["upstream"]["pilot_controller_glossary"] == (
        "6bf5b614446668f4a431b6fd9a5424811b52db6f80e946cb285d00c8a2d6727b"
    )


def test_facility_catalog_and_term_catalog_fail_independently(tmp_path):
    config, definition_seed = _test_inputs(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    Path(config["sources"]["nasr_zip"]).unlink()
    catalog = load_authority_catalog(
        config,
        guide=guide,
        schema_guide_path=SCHEMA_PATH,
        created_at=NOW,
        pcg_page_extractor=_extract_fixture_pages,
        definition_seed_path=definition_seed,
    )

    assert catalog.facility.status is AuthorityBuildStatus.BLOCKED
    assert catalog.terminology.status is AuthorityBuildStatus.OK


def test_facility_candidates_bind_distinct_record_authority(tmp_path):
    catalog = _catalog(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    jfk = build_facility_resolution_candidate(
        _facility(catalog, "KJFK"),
        structural_slot="controlled_nas_element",
        expected_entity_type="airport",
        catalog=catalog.facility,
        authority_snapshots=catalog.snapshots,
        guide=guide,
    )
    ewr = build_facility_resolution_candidate(
        _facility(catalog, "KEWR"),
        structural_slot="controlled_nas_element",
        expected_entity_type="airport",
        catalog=catalog.facility,
        authority_snapshots=catalog.snapshots,
        guide=guide,
    )

    assert jfk.status is AuthorityBuildStatus.OK
    assert ewr.status is AuthorityBuildStatus.OK
    assert jfk.evidence_claim.authority_artifact_sha256 == (
        ewr.evidence_claim.authority_artifact_sha256
    )
    assert jfk.evidence_claim.authority_record_locator != (
        ewr.evidence_claim.authority_record_locator
    )
    assert jfk.source_record.source_id != ewr.source_record.source_id


def test_gdp_and_ground_stop_use_real_definitions_and_separate_checksums(tmp_path):
    catalog = _catalog(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    for label in ("Ground Delay Program", "Ground Stop"):
        result = build_term_resolution_candidate(
            _term(catalog, label),
            structural_slot="traffic_management_initiative_type",
            expected_entity_type="traffic_management_initiative",
            catalog=catalog.terminology,
            authority_snapshots=catalog.snapshots,
            guide=guide,
        )
        assert result.status is AuthorityBuildStatus.OK
        assert result.evidence_claim.definition_text != label
        assert result.evidence_claim.authority_artifact_sha256 != (
            result.evidence_claim.term_registry_artifact_sha256
        )
        assert result.evidence_claim.definition_registry_artifact_sha256 != (
            result.evidence_claim.term_registry_artifact_sha256
        )


def test_definition_excerpt_must_be_within_claimed_glossary_entry(tmp_path):
    config, definition_seed = _test_inputs(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    seed = load_yaml(definition_seed)
    ground_stop = next(
        row for row in seed["definitions"] if row["preferred_label"] == "Ground Stop"
    )
    ground_stop["source_ref"] = (
        "faa_pilot_controller_glossary:PCG_G-3:GROUND_DELAY_PROGRAM"
    )
    import yaml

    definition_seed.write_text(
        yaml.safe_dump(seed, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    catalog = load_authority_catalog(
        config,
        guide=guide,
        schema_guide_path=SCHEMA_PATH,
        created_at=NOW,
        pcg_page_extractor=_extract_fixture_pages,
        definition_seed_path=definition_seed,
    )

    assert catalog.terminology.status is AuthorityBuildStatus.BLOCKED


def test_gs_compatibility_is_candidate_specific(tmp_path):
    catalog = _catalog(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    results = {
        label: build_term_resolution_candidate(
            _term(catalog, label),
            structural_slot="traffic_management_initiative_type",
            expected_entity_type="traffic_management_initiative",
            catalog=catalog.terminology,
            authority_snapshots=catalog.snapshots,
            guide=guide,
        )
        for label in ("Ground Stop", "Glide Slope")
    }

    assert results["Ground Stop"].candidate.eligible is True
    assert results["Glide Slope"].status is AuthorityBuildStatus.OK
    assert results["Glide Slope"].candidate.eligible is False
    assert any(
        check.status is ConstraintCheckStatus.FAIL
        for check in results["Glide Slope"].candidate.constraint_checks
    )


def test_missing_definition_is_insufficient_without_label_fallback(tmp_path):
    catalog = _catalog(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    result = build_term_resolution_candidate(
        _term(catalog, "Airspace Flow Program"),
        structural_slot="traffic_management_initiative_type",
        expected_entity_type="traffic_management_initiative",
        catalog=catalog.terminology,
        authority_snapshots=catalog.snapshots,
        guide=guide,
    )

    assert result.status is AuthorityBuildStatus.INSUFFICIENT
    assert result.source_record is None
    assert result.evidence_claim is None
    assert result.candidate is not None
    assert result.candidate.authority_evidence_ids == ()
    assert result.candidate.eligible is False


def test_authority_source_content_is_stable_and_normalized():
    fields = AuthoritySourceContentFields(
        candidate_id="candidate:1",
        candidate_kind="term",
        preferred_label="Ground Stop",
        candidate_type="traffic_management_initiative",
        surface_form="GS",
        authority_text="  Ground Stop  \r\nrequires aircraft.\t\r\n",
        authority_source_ref="faa_pilot_controller_glossary:entry",
        authority_locator="page:10:entry",
        authority_artifact_key="pilot_controller_glossary",
        authority_artifact_sha256="a" * 64,
        definition_registry_artifact_sha256="b" * 64,
        term_registry_artifact_sha256="c" * 64,
    )
    first = canonical_authority_source_content(fields)
    second = canonical_authority_source_content(
        AuthoritySourceContentFields.model_validate(
            dict(reversed(list(fields.model_dump().items())))
        )
    )

    assert first == second
    assert json.loads(first)["authority_text"] == "  Ground Stop\nrequires aircraft."


def test_authority_text_rejects_nul():
    with pytest.raises(ValueError, match="NUL"):
        normalize_authority_text("bad\u0000text")


def test_schema_change_does_not_rewrite_authority_source_id(tmp_path):
    catalog = _catalog(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    term = _term(catalog, "Ground Stop")
    first = build_term_resolution_candidate(
        term,
        structural_slot="traffic_management_initiative_type",
        expected_entity_type="traffic_management_initiative",
        catalog=catalog.terminology,
        authority_snapshots=catalog.snapshots,
        guide=guide,
    )
    changed = guide.__class__(
        **{**guide.__dict__, "checksum": "f" * 64}
    )
    second = build_term_resolution_candidate(
        term,
        structural_slot="traffic_management_initiative_type",
        expected_entity_type="traffic_management_initiative",
        catalog=catalog.terminology,
        authority_snapshots=catalog.snapshots,
        guide=changed,
    )

    assert first.source_record.source_id == second.source_record.source_id
    first_schema = next(
        check
        for check in first.candidate.constraint_checks
        if check.check_kind == "schema_compatibility"
    )
    second_schema = next(
        check
        for check in second.candidate.constraint_checks
        if check.check_kind == "schema_compatibility"
    )
    assert first_schema.constraint_id != second_schema.constraint_id


def test_corrupt_authority_artifact_is_blocked(tmp_path):
    config, definition_seed = _test_inputs(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    seed = load_yaml(definition_seed)
    seed["authority_artifact_sha256"] = "0" * 64
    import yaml

    definition_seed.write_text(
        yaml.safe_dump(seed, sort_keys=False),
        encoding="utf-8",
    )
    catalog = load_authority_catalog(
        config,
        guide=guide,
        schema_guide_path=SCHEMA_PATH,
        created_at=NOW,
        pcg_page_extractor=_extract_fixture_pages,
        definition_seed_path=definition_seed,
    )

    assert catalog.terminology.status is AuthorityBuildStatus.BLOCKED
    assert catalog.facility.status is AuthorityBuildStatus.OK
