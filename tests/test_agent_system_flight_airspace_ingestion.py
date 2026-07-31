"""Incremental Flight/Airspace ingestion into the authoritative store."""

from __future__ import annotations

import hashlib
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.flight_airspace_contracts import (
    AirCarrierRecord,
    FlightAirspaceMaterialization,
    FlightPublicationRecord,
    FlightRecord,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    KnowledgePublicationPackage,
    KnowledgePublicationRecord,
    KnowledgeRootRecord,
    PublicationEvidenceLink,
    PublicationSourceMembership,
    stable_knowledge_publication_id,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    KnowledgeIngestionResult,
    SourceVersionRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


DOMAIN = "bts-2026-05"


def _version(label: str) -> SourceVersionRecord:
    content = f"source row {label}"
    checksum = hashlib.sha256(content.encode()).hexdigest()
    source_id = f"source:{label}"
    return SourceVersionRecord(
        source_version_id=stable_id("source-version", source_id, checksum),
        source_id=source_id,
        family=SourceFamily.BTS_FLIGHT_OPERATION,
        asset_id=None,
        content=content,
        content_sha256=checksum,
        source_url=None,
        logical_time="2026-05-20",
        metadata={"row": label},
    )


def test_source_versions_are_registered_in_reusable_chunks(tmp_path: Path) -> None:
    """A scalable adapter must not require one transaction per logical row."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-flight-ingestion",
        create=True,
    )
    try:
        versions = (_version("1"), _version("2"))

        assert store.register_source_versions(versions) == {
            versions[0].source_version_id: "inserted",
            versions[1].source_version_id: "inserted",
        }
        assert store.register_source_versions(versions) == {
            versions[0].source_version_id: "existing",
            versions[1].source_version_id: "existing",
        }
        assert len(store.list_source_versions()) == 2
    finally:
        store.close()


def test_knowledge_ingestion_results_are_recorded_in_reusable_chunks(
    tmp_path: Path,
) -> None:
    """Adapter outcomes should share one transaction per ingestion chunk."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-flight-ingestion",
        create=True,
    )
    try:
        versions = (_version("1"), _version("2"))
        store.register_source_versions(versions)
        recorded_at = datetime(2026, 5, 1, tzinfo=UTC)
        results = tuple(
            KnowledgeIngestionResult(
                source_version_id=version.source_version_id,
                adapter_id="test-adapter",
                adapter_version="v1",
                status="insufficient",
                reason="source retained without a semantic root",
                recorded_at=recorded_at,
            )
            for version in versions
        )

        store.record_knowledge_ingestion_results(results)

        assert tuple(
            store.get_knowledge_ingestion_result(
                source_version_id=version.source_version_id,
                adapter_id="test-adapter",
                adapter_version="v1",
            )
            for version in versions
        ) == results
    finally:
        store.close()


def test_source_asset_discovery_supports_external_raw_root_without_read_bytes(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Large ZIP discovery must hash incrementally and retain a logical path."""

    from aviation_agentic_ai.agent_system.sources import discover_source_assets

    project_root = tmp_path / "worktree"
    source_root = tmp_path / "source-checkout"
    configured = Path("data/raw/bts/month.zip")
    source_path = source_root / configured
    source_path.parent.mkdir(parents=True)
    source_path.write_bytes(b"large-source-fixture")

    def reject_read_bytes(_path: Path) -> bytes:
        raise AssertionError("source discovery must not read the whole file")

    monkeypatch.setattr(Path, "read_bytes", reject_read_bytes)

    assets = discover_source_assets(
        {"sources": {"bts_flight_operations": configured.as_posix()}},
        source_root=source_root,
        project_root=project_root,
    )

    assert len(assets) == 1
    assert assets[0].asset_key == "bts_flight_operations"
    assert assets[0].local_path == configured.as_posix()
    assert assets[0].byte_count == len(b"large-source-fixture")
    assert assets[0].content_sha256 == hashlib.sha256(
        b"large-source-fixture"
    ).hexdigest()


def test_source_asset_discovery_rejects_a_pinned_checksum_mismatch(
    tmp_path: Path,
) -> None:
    from aviation_agentic_ai.agent_system.sources import discover_source_assets

    path = tmp_path / "month.zip"
    path.write_bytes(b"actual source bytes")

    with pytest.raises(ValueError, match="checksum mismatch.*bts_flight_operations"):
        discover_source_assets(
            {
                "sources": {"bts_flight_operations": str(path)},
                "source_checksums": {"bts_flight_operations": "0" * 64},
            }
        )


def test_canonical_config_registers_all_flight_airspace_raw_sources() -> None:
    from aviation_agentic_ai.config import load_yaml

    config = load_yaml("configs/aviation_knowledge_v1.yaml")
    expected_keys = {
        "bts_flight_operations",
        "faa_aircraft_registry",
        "historical_metar_speci",
        "nasa_atmonto_instances",
        "nasr_airspace_zip",
    }

    assert expected_keys <= set(config["sources"])
    assert expected_keys <= set(config["source_checksums"])
    assert config["source_metadata"]["bts_flight_operations"][
        "temporal_domain_id"
    ] == "proxy-2026-05"
    assert config["source_metadata"]["bts_flight_operations"][
        "ingestion_scope"
    ] == {
        "mode": "bounded",
        "service_date_from": date(2026, 5, 20),
        "service_date_to": date(2026, 5, 20),
        "routes": [
            ["ATL", "JFK"],
            ["JFK", "ATL"],
            ["ATL", "EWR"],
            ["EWR", "ATL"],
            ["ATL", "LGA"],
            ["LGA", "ATL"],
        ],
        "selection_basis": (
            "single-day overlap across configured advisory, weather, flight, "
            "registry, and NASR sources"
        ),
    }
    assert config["source_metadata"]["nasa_atmonto_instances"][
        "temporal_domain_id"
    ] == "nasa-atmonto-2014"


def _materialization(
    store: AviationEvidenceStore,
    *,
    flight_number: str,
    carrier_name: str = "Delta Air Lines",
) -> FlightAirspaceMaterialization:
    content = f"DL,{flight_number},ATL,JFK"
    source_id = f"bts-row:test:{flight_number}"
    checksum = hashlib.sha256(content.encode()).hexdigest()
    version = SourceVersionRecord(
        source_version_id=stable_id("source-version", source_id, checksum),
        source_id=source_id,
        family=SourceFamily.BTS_FLIGHT_OPERATION,
        asset_id=None,
        content=content,
        content_sha256=checksum,
        source_url=None,
        logical_time="2026-05-20",
        metadata={"row_number": int(flight_number)},
    )
    store.register_source_version(version)
    anchor = store.register_source_anchor(
        version.source_version_id,
        char_start=0,
        char_end=len(content),
    )
    flight_id = stable_id(
        "flight",
        SourceFamily.BTS_FLIGHT_OPERATION.value,
        "2026-05-20",
        "DL",
        flight_number,
        "ATL",
        "JFK",
        f"2026-05-20|{flight_number}",
    )
    digest = hashlib.sha256(
        f"{flight_id}|{version.source_version_id}".encode()
    ).hexdigest()
    publication_id = stable_knowledge_publication_id(
        flight_id,
        version.source_version_id,
        digest,
    )
    package = KnowledgePublicationPackage(
        root=KnowledgeRootRecord(
            root_id=flight_id,
            root_kind="flight",
            temporal_domain_id=DOMAIN,
            active_publication_id=publication_id,
        ),
        publication=KnowledgePublicationRecord(
            publication_id=publication_id,
            root_id=flight_id,
            temporal_domain_id=DOMAIN,
            primary_source_version_id=version.source_version_id,
            formal_publication_digest=digest,
        ),
        publication_sources=(
            PublicationSourceMembership(
                membership_id=stable_id(
                    "publication-source",
                    publication_id,
                    version.source_version_id,
                    "primary",
                ),
                publication_id=publication_id,
                source_version_id=version.source_version_id,
                source_role="primary",
            ),
        ),
        source_anchors=(anchor,),
        facts=(),
        fact_memberships=(),
        evidence_links=(
            PublicationEvidenceLink(
                evidence_link_id=stable_id(
                    "publication-evidence",
                    publication_id,
                    "structured_record",
                    flight_id,
                    version.source_version_id,
                    anchor.source_anchor_id,
                    "full_record",
                ),
                publication_id=publication_id,
                owner_kind="structured_record",
                owner_id=flight_id,
                source_version_id=version.source_version_id,
                source_anchor_id=anchor.source_anchor_id,
                evidence_text=content,
                evidence_ref="full_record",
            ),
        ),
    )
    carrier_id = stable_id(
        "air-carrier",
        SourceFamily.BTS_FLIGHT_OPERATION.value,
        "DL",
    )
    return FlightAirspaceMaterialization(
        publication=package,
        flight=FlightRecord(
            flight_id=flight_id,
            temporal_domain_id=DOMAIN,
            source_family=SourceFamily.BTS_FLIGHT_OPERATION,
            service_date=date(2026, 5, 20),
            reporting_carrier="DL",
            flight_number=flight_number,
            origin_airport_id="ATL",
            destination_airport_id="JFK",
            scheduled_departure_key=f"2026-05-20|{flight_number}",
            tail_number=None,
            scheduled_departure=None,
            actual_wheels_off=None,
            time_basis="unknown",
            cancelled=False,
            diverted=False,
        ),
        flight_publication=FlightPublicationRecord(
            publication_id=publication_id,
            flight_id=flight_id,
            temporal_domain_id=DOMAIN,
            primary_source_version_id=version.source_version_id,
        ),
        air_carriers=(
            AirCarrierRecord(
                carrier_id=carrier_id,
                temporal_domain_id=DOMAIN,
                source_family=SourceFamily.BTS_FLIGHT_OPERATION,
                carrier_code="DL",
                display_name=carrier_name,
            ),
        ),
    )


def test_chunk_publication_reuses_stable_references_and_advances_one_revision(
    tmp_path: Path,
) -> None:
    """Per-record commits would make full BTS ingestion needlessly expensive."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-flight-ingestion",
        create=True,
    )
    try:
        first = _materialization(store, flight_number="101")
        second = _materialization(store, flight_number="102")
        before = store.get_knowledge_revision()

        outcomes = store.apply_flight_airspace_publication_batch((first, second))

        assert outcomes == {
            first.publication.publication.publication_id: "inserted",
            second.publication.publication.publication_id: "inserted",
        }
        assert store.get_knowledge_revision() == before + 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM air_carriers"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM flight_publications"
        ).fetchone()[0] == 2
    finally:
        store.close()


def test_chunk_publication_rolls_back_only_the_conflicting_root(
    tmp_path: Path,
) -> None:
    """One conflicting semantic root must not hide unrelated accepted records."""

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-flight-ingestion",
        create=True,
    )
    try:
        accepted = _materialization(store, flight_number="101")
        conflicting = _materialization(
            store,
            flight_number="102",
            carrier_name="Conflicting Carrier Name",
        )
        later = _materialization(store, flight_number="103")

        outcomes = store.apply_flight_airspace_publication_batch(
            (accepted, conflicting, later)
        )

        assert outcomes == {
            accepted.publication.publication.publication_id: "inserted",
            conflicting.publication.publication.publication_id: "blocked",
            later.publication.publication.publication_id: "inserted",
        }
        assert store._connection.execute(
            "SELECT COUNT(*) FROM flight_publications"
        ).fetchone()[0] == 2
        assert store._connection.execute(
            "SELECT COUNT(*) FROM knowledge_publications WHERE publication_id = ?",
            (conflicting.publication.publication.publication_id,),
        ).fetchone()[0] == 0
    finally:
        store.close()
