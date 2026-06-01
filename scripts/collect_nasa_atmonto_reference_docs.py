#!/usr/bin/env python3
"""Collect stable FAA reference documents for the NASA ATMONTO phase-1 corpus."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, date, datetime
from email.utils import parsedate_to_datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USER_AGENT = "aviation-agentic-ai-research/0.1"


@dataclass(frozen=True)
class ReferenceSource:
    source_id: str
    title: str
    url: str
    file_name: str
    document_group: str
    role: str
    format: str
    atmonto_modules: tuple[str, ...]
    atmonto_targets: tuple[str, ...]
    use_scope: str
    limitations: tuple[str, ...]


REFERENCE_SOURCES: tuple[ReferenceSource, ...] = (
    ReferenceSource(
        source_id="faa_air_traffic_publications_catalog",
        title="FAA Air Traffic Plans and Publications catalog",
        url="https://www.faa.gov/air_traffic/publications/",
        file_name="faa_air_traffic_publications_catalog.html",
        document_group="air_traffic_publications",
        role="catalog",
        format="html",
        atmonto_modules=("atm", "nas", "gen"),
        atmonto_targets=(
            "Air traffic publication inventory",
            "ATM/NAS reference-document provenance",
        ),
        use_scope="Catalog page used to anchor the official FAA publication set.",
        limitations=("Catalog page is an entrypoint, not a complete content source.",),
    ),
    ReferenceSource(
        source_id="aim_html_entrypoint",
        title="Aeronautical Information Manual HTML entrypoint",
        url="https://www.faa.gov/air_traffic/publications/atpubs/aim_html/index.html",
        file_name="aim_html_index.html",
        document_group="aim",
        role="structured_html_entrypoint",
        format="html",
        atmonto_modules=("atm", "nas", "gen", "data"),
        atmonto_targets=("Flight", "NavigationFix", "Airport", "FederalAirway", "Location"),
        use_scope="Structured HTML entrypoint for ATM/NAS concept explanations.",
        limitations=("Only the HTML entrypoint is captured; recursive HTML capture is a later step.",),
    ),
    ReferenceSource(
        source_id="aim_pdf",
        title="Aeronautical Information Manual Basic with Change 1 and 2",
        url="https://www.faa.gov/air_traffic/publications/media/AIM_Basic_w_Chg_1_and_2_dtd_1-22-26.pdf",
        file_name="AIM_Basic_w_Chg_1_and_2_dtd_1-22-26.pdf",
        document_group="aim",
        role="reference_document",
        format="pdf",
        atmonto_modules=("atm", "nas", "gen", "data"),
        atmonto_targets=("Flight", "NavigationFix", "Airport", "FederalAirway", "Location"),
        use_scope="Official FAA ATM/NAS reference text for concept extraction and QA evidence.",
        limitations=("Reference text is not live operational guidance for flight decisions.",),
    ),
    ReferenceSource(
        source_id="pilot_controller_glossary_html_entrypoint",
        title="Pilot/Controller Glossary HTML entrypoint",
        url="https://www.faa.gov/air_traffic/publications/atpubs/pcg_html/index.html",
        file_name="pilot_controller_glossary_html_index.html",
        document_group="pilot_controller_glossary",
        role="structured_html_entrypoint",
        format="html",
        atmonto_modules=("atm", "nas", "data", "gen"),
        atmonto_targets=("Terminology alignment", "Entity aliases", "Controlled labels"),
        use_scope="Terminology source for labels, aliases, and extraction vocabulary.",
        limitations=("Glossary definitions help normalization but do not by themselves create event facts.",),
    ),
    ReferenceSource(
        source_id="pilot_controller_glossary_pdf",
        title="Pilot/Controller Glossary Basic with Change 1 and 2",
        url="https://www.faa.gov/air_traffic/publications/media/PCG_Bsc_w_Chg_1_and_2_dtd_1-22-26.pdf",
        file_name="PCG_Bsc_w_Chg_1_and_2_dtd_1-22-26.pdf",
        document_group="pilot_controller_glossary",
        role="terminology_reference",
        format="pdf",
        atmonto_modules=("atm", "nas", "data", "gen"),
        atmonto_targets=("Terminology alignment", "Entity aliases", "Controlled labels"),
        use_scope="Official glossary for controlled vocabulary and synonym mapping.",
        limitations=("Glossary definitions require mapping rules before KG use.",),
    ),
    ReferenceSource(
        source_id="aip_html_entrypoint",
        title="Aeronautical Information Publication HTML entrypoint",
        url="https://www.faa.gov/air_traffic/publications/atpubs/aip_html/index.html",
        file_name="aip_html_index.html",
        document_group="aip",
        role="structured_html_entrypoint",
        format="html",
        atmonto_modules=("atm", "nas", "gen"),
        atmonto_targets=("Airport", "Airspace", "NavigationFix", "FederalAirway", "Location"),
        use_scope="Structured entrypoint for NAS/airspace/procedure reference text.",
        limitations=("Only the HTML entrypoint is captured; recursive HTML capture is a later step.",),
    ),
    ReferenceSource(
        source_id="aip_pdf",
        title="Aeronautical Information Publication Basic",
        url="https://www.faa.gov/air_traffic/publications/media/AIP_Basic_dtd_1-22-26.pdf",
        file_name="AIP_Basic_dtd_1-22-26.pdf",
        document_group="aip",
        role="reference_document",
        format="pdf",
        atmonto_modules=("atm", "nas", "gen"),
        atmonto_targets=("Airport", "Airspace", "NavigationFix", "FederalAirway", "Location"),
        use_scope="Official NAS/airspace/procedure explanatory reference.",
        limitations=("Reference text should not be treated as current operational clearance data.",),
    ),
    ReferenceSource(
        source_id="jo_7110_65_html_entrypoint",
        title="FAA Order JO 7110.65 Air Traffic Control HTML entrypoint",
        url="https://www.faa.gov/air_traffic/publications/atpubs/atc_html/",
        file_name="jo_7110_65_atc_html_index.html",
        document_group="jo_7110_65",
        role="structured_html_entrypoint",
        format="html",
        atmonto_modules=("atm", "nas"),
        atmonto_targets=("Flight", "NavigationFix", "TrafficManagementInitiative"),
        use_scope="Structured entrypoint for ATC procedure and ATM concept extraction.",
        limitations=("Procedure text must not be converted into operational advice.",),
    ),
    ReferenceSource(
        source_id="jo_7110_65_pdf",
        title="FAA Order JO 7110.65BB Air Traffic Control",
        url="https://www.faa.gov/documentLibrary/media/Order/7110.65BB_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf",
        file_name="7110.65BB_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf",
        document_group="jo_7110_65",
        role="procedure_reference",
        format="pdf",
        atmonto_modules=("atm", "nas"),
        atmonto_targets=("Flight", "NavigationFix", "TrafficManagementInitiative"),
        use_scope="Official ATC procedure reference for ATM/NAS concept coverage.",
        limitations=("Use for retrospective text QA only, not live operational decision support.",),
    ),
    ReferenceSource(
        source_id="jo_7210_3_html_entrypoint",
        title="FAA Order JO 7210.3 Facility Operation and Administration HTML entrypoint",
        url="https://www.faa.gov/air_traffic/publications/atpubs/foa_html/",
        file_name="jo_7210_3_foa_html_index.html",
        document_group="jo_7210_3",
        role="structured_html_entrypoint",
        format="html",
        atmonto_modules=("atm", "nas", "gen"),
        atmonto_targets=("Airport", "ARTCC", "TRACON", "Sector", "Location"),
        use_scope="Structured entrypoint for facility-operation and NAS administration concepts.",
        limitations=("Procedure text must be interpreted as source evidence, not operational instruction.",),
    ),
    ReferenceSource(
        source_id="jo_7210_3_pdf",
        title="FAA Order JO 7210.3EE Facility Operation and Administration",
        url="https://www.faa.gov/documentLibrary/media/Order/7210.3EE_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf",
        file_name="7210.3EE_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf",
        document_group="jo_7210_3",
        role="facility_reference",
        format="pdf",
        atmonto_modules=("atm", "nas", "gen"),
        atmonto_targets=("Airport", "ARTCC", "TRACON", "Sector", "Location"),
        use_scope="Official facility-operation reference for NAS entity and relation coverage.",
        limitations=("Use for retrospective evidence and schema coverage only.",),
    ),
    ReferenceSource(
        source_id="aviation_weather_handbook_page",
        title="Aviation Weather Handbook FAA detail page",
        url="https://www.faa.gov/regulationspolicies/handbooksmanuals/aviation/faa-h-8083-28b-aviation-weather-handbook",
        file_name="aviation_weather_handbook_detail.html",
        document_group="aviation_weather_handbook",
        role="catalog",
        format="html",
        atmonto_modules=("data", "nas"),
        atmonto_targets=("MeteorologicalReport", "WeatherCondition", "forecastingAirport"),
        use_scope="Detail page anchoring the official Aviation Weather Handbook PDF.",
        limitations=("Detail page is provenance metadata, not the main content artifact.",),
    ),
    ReferenceSource(
        source_id="aviation_weather_handbook_pdf",
        title="FAA-H-8083-28B Aviation Weather Handbook",
        url="https://www.faa.gov/sites/faa.gov/files/FAA-H-8083-28B.pdf",
        file_name="FAA-H-8083-28B_Aviation_Weather_Handbook.pdf",
        document_group="aviation_weather_handbook",
        role="weather_reference",
        format="pdf",
        atmonto_modules=("data", "nas"),
        atmonto_targets=(
            "MeteorologicalReport",
            "WeatherCondition",
            "SurfaceWindCondition",
            "VisibilityCondition",
            "SkyCondition",
            "CloudLayer",
        ),
        use_scope="Weather concept reference paired with AviationWeather METAR/TAF records.",
        limitations=("Concept handbook does not provide live weather observations.",),
    ),
    ReferenceSource(
        source_id="chart_users_guide_page",
        title="Aeronautical Chart Users' Guide FAA page",
        url="https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/aero_guide/",
        file_name="aeronautical_chart_users_guide_page.html",
        document_group="chart_users_guide",
        role="catalog",
        format="html",
        atmonto_modules=("nas", "gen", "atm"),
        atmonto_targets=("Airport", "NavigationFix", "FederalAirway", "Location"),
        use_scope="Guide page anchoring chart-symbol and NAS interpretation artifacts.",
        limitations=("Chart interpretation source is not a substitute for NASR records.",),
    ),
    ReferenceSource(
        source_id="chart_users_guide_pdf",
        title="Aeronautical Chart Users' Guide complete PDF",
        url="https://aeronav.faa.gov/user_guide/cug-complete_20260122.pdf",
        file_name="cug-complete_20260122.pdf",
        document_group="chart_users_guide",
        role="chart_reference",
        format="pdf",
        atmonto_modules=("nas", "gen", "atm"),
        atmonto_targets=("Airport", "NavigationFix", "FederalAirway", "Location"),
        use_scope="Chart-symbol and NAS interpretation reference paired with NASR records.",
        limitations=("Chart guide supports interpretation, not current chart-cycle completeness.",),
    ),
)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def digest_bytes(body: bytes) -> str:
    return sha256(body).hexdigest()


def repo_rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(path: Path, manifest: dict[str, object], repo_root: Path) -> None:
    files = manifest["files"]
    assert isinstance(files, list)
    lines = [
        "# NASA ATMONTO FAA Reference Documents",
        "",
        f"- Snapshot date: {manifest['snapshot_date']}",
        f"- Retrieved at: {manifest['retrieved_at']}",
        f"- Source family: `{manifest['source_family']}`",
        f"- Manifest: `{repo_rel(Path(manifest['manifest_path']), repo_root)}`",
        "",
        "## Downloaded Sources",
        "",
        "| Source | Group | Role | Format | ATMONTO modules | Local file |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in files:
        assert isinstance(item, dict)
        modules = ", ".join(item["atmonto_modules"])
        lines.append(
            "| {title} | `{group}` | `{role}` | `{fmt}` | {modules} | `{path}` |".format(
                title=item["title"],
                group=item["document_group"],
                role=item["role"],
                fmt=item["format"],
                modules=modules,
                path=item["raw_file"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- These documents are reference and terminology sources for ATMONTO alignment.",
            "- ABox event data should still come from AviationWeather, NASR, and ATCSCC snapshots.",
            "- Procedure documents are for retrospective evidence-traceable QA, not operational use.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def source_effective_date(headers: object) -> str | None:
    last_modified = getattr(headers, "get", lambda _name: None)("Last-Modified")
    if not last_modified:
        return None
    try:
        return parsedate_to_datetime(last_modified).astimezone(UTC).date().isoformat()
    except (TypeError, ValueError):
        return None


def fetch_source(
    source: ReferenceSource,
    output_dir: Path,
    *,
    timeout: int,
    resume: bool,
) -> dict[str, object]:
    raw_path = output_dir / source.file_name
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    cached = resume and raw_path.exists() and raw_path.stat().st_size > 0
    if cached:
        body = raw_path.read_bytes()
        return {
            "source_id": source.source_id,
            "title": source.title,
            "source_url": source.url,
            "final_url": source.url,
            "http_status": 200,
            "content_type": "",
            "source_effective_date": None,
            "raw_file": raw_path,
            "raw_payload_hash": digest_bytes(body),
            "bytes": len(body),
            "cached": True,
        }

    request = Request(source.url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            final_url = response.geturl()
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            effective_date = source_effective_date(response.headers)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Failed to fetch {source.source_id} from {source.url}: {exc}") from exc
    tmp_path = raw_path.with_name(f".{raw_path.name}.tmp")
    tmp_path.write_bytes(body)
    tmp_path.replace(raw_path)
    return {
        "source_id": source.source_id,
        "title": source.title,
        "source_url": source.url,
        "final_url": final_url,
        "http_status": status,
        "content_type": content_type,
        "source_effective_date": effective_date,
        "raw_file": raw_path,
        "raw_payload_hash": digest_bytes(body),
        "bytes": len(body),
        "cached": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot-date",
        default=date.today().isoformat(),
        help="Snapshot date, YYYY-MM-DD. Defaults to today's local date.",
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root.",
    )
    parser.add_argument("--timeout", default=180, type=int, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Fetch every file again even when a non-empty local file already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    source_family = "faa_reference_documents"
    raw_root = repo_root / "data/raw/nasa_atmonto" / args.snapshot_date / source_family
    reports_root = repo_root / "reports/stages"
    retrieved_at = utc_now()

    files: list[dict[str, object]] = []
    for source in REFERENCE_SOURCES:
        result = fetch_source(
            source,
            raw_root,
            timeout=args.timeout,
            resume=not args.no_resume,
        )
        raw_file = result["raw_file"]
        assert isinstance(raw_file, Path)
        files.append(
            {
                **{key: value for key, value in result.items() if key != "raw_file"},
                "raw_file": repo_rel(raw_file, repo_root),
                "format": source.format,
                "document_group": source.document_group,
                "role": source.role,
                "atmonto_modules": list(source.atmonto_modules),
                "atmonto_targets": list(source.atmonto_targets),
                "use_scope": source.use_scope,
                "known_limitations": list(source.limitations),
                "retrieval_command": f"python scripts/collect_nasa_atmonto_reference_docs.py --snapshot-date {args.snapshot_date}",
            }
        )

    manifest_path = raw_root / "manifest.json"
    manifest: dict[str, object] = {
        "source_family": source_family,
        "retrieved_at": retrieved_at,
        "snapshot_date": args.snapshot_date,
        "scope": {
            "phase": "phase_1_reference_documents",
            "selection_policy": (
                "FAA sources selected for NASA ATMONTO atm/nas/data/gen alignment: "
                "AIM, Pilot/Controller Glossary, AIP, JO 7110.65, JO 7210.3, "
                "Aviation Weather Handbook, and Aeronautical Chart Users' Guide."
            ),
            "core_abox_sources": (
                "Pair with AviationWeather, FAA NASR, and ATCSCC snapshots; these "
                "reference documents are not replacements for event/record sources."
            ),
        },
        "license_or_access_note": "FAA public web documents downloaded for research snapshotting.",
        "parser_version": "scripts/collect_nasa_atmonto_reference_docs.py",
        "record_count": len(files),
        "known_limitations": [
            "HTML entrypoints are captured as entrypoints only; recursive HTML page capture is deferred.",
            "PDFs preserve official source documents but require downstream PDF extraction/chunking.",
            "Procedure documents support retrospective evidence-traceable QA, not operational decisions.",
        ],
        "files": files,
    }
    manifest["manifest_path"] = str(manifest_path)
    write_json(manifest_path, manifest)
    manifest["manifest_path"] = repo_rel(manifest_path, repo_root)
    write_json(manifest_path, manifest)

    inventory_path = reports_root / "nasa_atmonto_faa_reference_documents_inventory.json"
    report_path = reports_root / "nasa_atmonto_faa_reference_documents_inventory.md"
    inventory = {
        "source_family": source_family,
        "snapshot_date": args.snapshot_date,
        "retrieved_at": retrieved_at,
        "manifest": repo_rel(manifest_path, repo_root),
        "record_count": len(files),
        "total_bytes": sum(int(item["bytes"]) for item in files),
        "document_groups": sorted({str(item["document_group"]) for item in files}),
        "files": files,
    }
    write_json(inventory_path, inventory)
    write_markdown(report_path, {**manifest, "manifest_path": str(manifest_path)}, repo_root)

    print(
        json.dumps(
            {
                "snapshot_date": args.snapshot_date,
                "source_family": source_family,
                "manifest": repo_rel(manifest_path, repo_root),
                "inventory": repo_rel(inventory_path, repo_root),
                "report": repo_rel(report_path, repo_root),
                "record_count": len(files),
                "total_bytes": inventory["total_bytes"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"collection failed: {exc}", file=sys.stderr)
        raise
