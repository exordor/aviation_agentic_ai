#!/usr/bin/env python3
"""Collect the phase-1 NASA ATMONTO-aligned source snapshot.

The collector uses resumable raw-file caching, bounded concurrency, retries, and
visible progress logs so the multi-source capture is repeatable enough for the
experiment evidence trail.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import re
import shutil
import sys
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from typing import AsyncIterator, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

import httpx
import scrapy
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from scrapy.crawler import CrawlerProcess
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential


DEFAULT_AIRPORTS = ("KJFK", "KEWR", "KLGA")
AVIATIONWEATHER_BASE = "https://aviationweather.gov/api/data"
AVIATIONWEATHER_OPENAPI = "https://aviationweather.gov/data/schema/openapi.yaml"
NASR_INDEX_URL = (
    "https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/"
    "NASR_Subscription/"
)
ATCSCC_FORM_URL = "https://www.fly.faa.gov/adv/advAdvisoryForm"
ATCSCC_LIST_URL = "https://www.fly.faa.gov/adv/adv_list"
USER_AGENT = "aviation-agentic-ai-research/0.1"
LOGGER = logging.getLogger("nasa_atmonto.collect")


@dataclass(frozen=True)
class FetchResult:
    url: str
    final_url: str
    status: int
    content_type: str
    body: bytes


@dataclass(frozen=True)
class FetchTask:
    record_type: str
    url: str
    raw_path: Path
    source_effective_date: str
    file_format: str
    timeout: int = 120
    metadata: dict[str, object] | None = None


@dataclass(frozen=True)
class FetchArtifact:
    task: FetchTask
    final_url: str
    status: int
    content_type: str
    body: bytes
    raw_payload_hash: str
    cached: bool


class CollectionRunner:
    def __init__(
        self,
        *,
        repo_root: Path,
        workers: int,
        retries: int,
        resume: bool,
    ) -> None:
        self.repo_root = repo_root
        self.workers = max(1, workers)
        self.retries = max(1, retries)
        self.resume = resume
        self.console = Console(stderr=True)
        self.client = httpx.Client(
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
            timeout=httpx.Timeout(120.0),
            limits=httpx.Limits(
                max_connections=max(4, self.workers * 2),
                max_keepalive_connections=max(2, self.workers),
            ),
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "CollectionRunner":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def _request(self, task: FetchTask) -> httpx.Response:
        response = self.client.get(task.url, timeout=task.timeout)
        if response.status_code in {408, 429} or response.status_code >= 500:
            raise httpx.HTTPStatusError(
                f"HTTP {response.status_code} for {task.url}",
                request=response.request,
                response=response,
            )
        response.raise_for_status()
        return response

    def fetch(self, task: FetchTask) -> FetchArtifact:
        if self.resume and task.raw_path.exists() and task.raw_path.stat().st_size > 0:
            body = task.raw_path.read_bytes()
            LOGGER.debug("cache hit %s -> %s", task.record_type, task.raw_path)
            return FetchArtifact(
                task=task,
                final_url=task.url,
                status=200,
                content_type="",
                body=body,
                raw_payload_hash=digest_bytes(body),
                cached=True,
            )

        for attempt in Retrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=1, min=1, max=30),
            retry=retry_if_exception_type((httpx.HTTPError, OSError)),
            reraise=True,
        ):
            with attempt:
                response = self._request(task)
        body = response.content
        checksum = write_bytes(task.raw_path, body)
        return FetchArtifact(
            task=task,
            final_url=str(response.url),
            status=response.status_code,
            content_type=response.headers.get("content-type", ""),
            body=body,
            raw_payload_hash=checksum,
            cached=False,
        )

    def fetch_many(self, tasks: list[FetchTask], label: str) -> list[FetchArtifact]:
        if not tasks:
            return []
        started = time.monotonic()
        LOGGER.info(
            "fetch %s: %d tasks, workers=%d, resume=%s",
            label,
            len(tasks),
            min(self.workers, len(tasks)),
            self.resume,
        )
        results: list[FetchArtifact | None] = [None] * len(tasks)
        completed = 0
        cached = 0
        log_every = max(1, min(25, len(tasks) // 10 or 1))
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            progress_task = progress.add_task(label, total=len(tasks))
            with ThreadPoolExecutor(max_workers=min(self.workers, len(tasks))) as executor:
                future_to_index = {
                    executor.submit(self.fetch, task): index for index, task in enumerate(tasks)
                }
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    artifact = future.result()
                    results[index] = artifact
                    completed += 1
                    cached += int(artifact.cached)
                    progress.update(progress_task, advance=1)
                    if completed == len(tasks) or completed % log_every == 0:
                        LOGGER.info(
                            "fetch %s progress: %d/%d done (%d cached)",
                            label,
                            completed,
                            len(tasks),
                            cached,
                        )
        elapsed = time.monotonic() - started
        LOGGER.info(
            "fetch %s complete: %d tasks in %.1fs (%d cached)",
            label,
            len(tasks),
            elapsed,
            cached,
        )
        return [artifact for artifact in results if artifact is not None]


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attrs_dict = {name.lower(): value for name, value in attrs}
        href = attrs_dict.get("href")
        if href:
            self._current_href = href
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._current_href:
            text = " ".join("".join(self._current_text).split())
            self.links.append((self._current_href, text))
            self._current_href = None
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href:
            self._current_text.append(data)


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            clean = " ".join(data.split())
            if clean:
                self.parts.append(clean)

    def text(self) -> str:
        return "\n".join(self.parts)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def window_label(window_start: datetime, window_end: datetime) -> str:
    return f"{window_start:%Y%m%dT%H%MZ}_{window_end:%Y%m%dT%H%MZ}"


def metar_hours_back(window_start: datetime, window_end: datetime) -> int:
    seconds = (window_end - window_start).total_seconds()
    # AviationWeather's METAR `hours` search is exclusive of the lower boundary,
    # so request one extra hour and let the alignment step filter exactly.
    return int((seconds + 3599) // 3600) + 1


def window_query_times(
    window_start: datetime, window_end: datetime, step_hours: int
) -> list[datetime]:
    times: list[datetime] = []
    current = window_start
    while current <= window_end:
        times.append(current)
        current += timedelta(hours=step_hours)
    if times[-1] != window_end:
        times.append(window_end)
    return times


def window_dates(window_start: datetime, window_end: datetime) -> list[str]:
    last_inclusive = window_end - timedelta(microseconds=1)
    current = window_start.date()
    last = last_inclusive.date()
    dates: list[str] = []
    while current <= last:
        dates.append(current.isoformat())
        current += timedelta(days=1)
    return dates


def parse_airports(value: str) -> tuple[str, ...]:
    airports = tuple(
        airport.strip().upper()
        for airport in value.replace(";", ",").split(",")
        if airport.strip()
    )
    if not airports:
        raise ValueError("At least one airport must be provided")
    for airport in airports:
        if not re.fullmatch(r"K[A-Z0-9]{3}", airport):
            raise ValueError(f"Expected four-character ICAO airport ID, got {airport!r}")
    return airports


def digest_bytes(body: bytes) -> str:
    return sha256(body).hexdigest()


def write_bytes(path: Path, body: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_bytes(body)
    tmp_path.replace(path)
    return digest_bytes(body)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def configure_logging(log_level: str) -> None:
    log_console = Console(stderr=True)
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=log_console, rich_tracebacks=True, markup=True)],
        force=True,
    )
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    silence_scrapy_loggers()


def silence_scrapy_loggers() -> None:
    """Keep Scrapy internals quiet while preserving collector progress logs."""
    logger_names = [
        name
        for name in logging.root.manager.loggerDict
        if name == "scrapy" or name.startswith("scrapy.")
    ]
    logger_names.extend(["scrapy", "twisted"])
    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = False
        logger.setLevel(logging.ERROR)


def fetch_url(url: str, timeout: int = 120) -> FetchResult:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            return FetchResult(
                url=url,
                final_url=response.geturl(),
                status=response.status,
                content_type=response.headers.get("Content-Type", ""),
                body=body,
            )
    except HTTPError as exc:
        body = exc.read()
        return FetchResult(
            url=url,
            final_url=exc.geturl(),
            status=exc.code,
            content_type=exc.headers.get("Content-Type", ""),
            body=body,
        )
    except URLError as exc:
        raise RuntimeError(f"Could not fetch {url}: {exc}") from exc


def decode_text(body: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return body.decode(encoding)
        except UnicodeDecodeError:
            continue
    return body.decode("utf-8", errors="replace")


def relative_to_repo(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def parse_links(html_text: str) -> list[tuple[str, str]]:
    parser = LinkExtractor()
    parser.feed(html_text)
    return parser.links


def html_to_text(html_text: str) -> str:
    parser = TextExtractor()
    parser.feed(html_text)
    return parser.text()


def artifact_manifest_entry(
    artifact: FetchArtifact,
    repo_root: Path,
    *,
    record_count: int | None = None,
    processed_file: Path | None = None,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "record_type": artifact.task.record_type,
        "source_url": artifact.final_url,
        "retrieval_command": f"curl -L '{artifact.task.url}'",
        "retrieved_at": artifact.task.metadata.get("retrieved_at")
        if artifact.task.metadata
        else None,
        "source_effective_date": artifact.task.source_effective_date,
        "raw_file": relative_to_repo(artifact.task.raw_path, repo_root),
        "raw_payload_hash": artifact.raw_payload_hash,
        "format": artifact.task.file_format,
        "content_type": artifact.content_type,
        "status": artifact.status,
        "cached": artifact.cached,
        "record_count": record_count,
    }
    if processed_file:
        entry["processed_file"] = relative_to_repo(processed_file, repo_root)
    return entry


def collect_aviationweather(
    raw_root: Path,
    processed_root: Path,
    reports_root: Path,
    repo_root: Path,
    runner: CollectionRunner,
    airports: tuple[str, ...],
    snapshot_date: str,
    window_start: datetime,
    window_end: datetime,
    retrieved_at: str,
) -> dict[str, object]:
    source_dir = raw_root / "aviationweather"
    processed_root.mkdir(parents=True, exist_ok=True)
    label = window_label(window_start, window_end)
    metar_hours = metar_hours_back(window_start, window_end)
    window_start_iso = iso_utc(window_start)
    window_end_iso = iso_utc(window_end)
    raw_entries: list[dict[str, object]] = []
    inventories: list[dict[str, object]] = []

    def parse_json_artifact(artifact: FetchArtifact) -> list[dict[str, object]]:
        data = json.loads(decode_text(artifact.body))
        if not isinstance(data, list):
            raise RuntimeError(f"Expected list payload for {artifact.task.url}")
        raw_entries.append(
            artifact_manifest_entry(artifact, repo_root, record_count=len(data))
        )
        return data

    metar_rows: list[dict[str, object]] = []
    metar_raw_files: list[str] = []
    metar_seen: set[tuple[object, object, object]] = set()
    metar_tasks: list[FetchTask] = []
    for airport in airports:
        url = (
            f"{AVIATIONWEATHER_BASE}/metar?"
            + urlencode(
                {
                    "ids": airport,
                    "format": "json",
                    "date": window_end_iso,
                    "hours": str(metar_hours),
                }
            )
        )
        metar_tasks.append(
            FetchTask(
                record_type="metar",
                url=url,
                raw_path=source_dir / f"metar_{airport}_{label}.json",
                source_effective_date=snapshot_date,
                file_format="json",
                metadata={"airport": airport, "retrieved_at": retrieved_at},
            )
        )
    for artifact in runner.fetch_many(metar_tasks, "AviationWeather METAR"):
        airport = str(artifact.task.metadata["airport"]) if artifact.task.metadata else ""
        records = parse_json_artifact(artifact)
        raw_path = artifact.task.raw_path
        metar_raw_files.append(relative_to_repo(raw_path, repo_root))
        for index, record in enumerate(records):
            key = (record.get("icaoId"), record.get("reportTime"), record.get("rawOb"))
            if key in metar_seen:
                continue
            metar_seen.add(key)
            metar_rows.append(
                {
                    "source_family": "aviationweather",
                    "source_record_type": "metar",
                    "source_id": record.get("rawOb") or f"metar:{airport}:{index}",
                    "source_url": artifact.final_url,
                    "retrieved_at": retrieved_at,
                    "snapshot_date": snapshot_date,
                    "raw_file": relative_to_repo(raw_path, repo_root),
                    "raw": record,
                }
            )
    metar_path = processed_root / "aviationweather_metar.jsonl"
    metar_count = write_jsonl(metar_path, metar_rows)
    inventories.append(
        {
            "source_family": "aviationweather",
            "record_type": "metar",
            "record_count": metar_count,
            "raw_files": metar_raw_files,
            "processed_file": relative_to_repo(metar_path, repo_root),
        }
    )

    taf_rows: list[dict[str, object]] = []
    taf_raw_files: list[str] = []
    taf_seen: set[tuple[object, object, object]] = set()
    ids = ",".join(airports)
    taf_tasks: list[FetchTask] = []
    for query_time in window_query_times(window_start, window_end, step_hours=6):
        query_time_iso = iso_utc(query_time)
        url = (
            f"{AVIATIONWEATHER_BASE}/taf?"
            + urlencode(
                {
                    "ids": ids,
                    "format": "json",
                    "date": query_time_iso,
                    "time": "valid",
                }
            )
        )
        taf_tasks.append(
            FetchTask(
                record_type="taf",
                url=url,
                raw_path=source_dir
                / f"taf_{'_'.join(airports)}_valid_{query_time:%Y%m%dT%H%MZ}.json",
                source_effective_date=snapshot_date,
                file_format="json",
                metadata={"query_time": query_time_iso, "retrieved_at": retrieved_at},
            )
        )
    for artifact in runner.fetch_many(taf_tasks, "AviationWeather TAF"):
        query_time_iso = (
            str(artifact.task.metadata["query_time"]) if artifact.task.metadata else ""
        )
        records = parse_json_artifact(artifact)
        raw_path = artifact.task.raw_path
        taf_raw_files.append(relative_to_repo(raw_path, repo_root))
        for index, record in enumerate(records):
            key = (record.get("icaoId"), record.get("issueTime"), record.get("rawTAF"))
            if key in taf_seen:
                continue
            taf_seen.add(key)
            taf_rows.append(
                {
                    "source_family": "aviationweather",
                    "source_record_type": "taf",
                    "source_id": record.get("rawTAF") or f"taf:{query_time_iso}:{index}",
                    "source_url": artifact.final_url,
                    "retrieved_at": retrieved_at,
                    "snapshot_date": snapshot_date,
                    "raw_file": relative_to_repo(raw_path, repo_root),
                    "raw": record,
                }
            )
    taf_path = processed_root / "aviationweather_taf.jsonl"
    taf_count = write_jsonl(taf_path, taf_rows)
    inventories.append(
        {
            "source_family": "aviationweather",
            "record_type": "taf",
            "record_count": taf_count,
            "raw_files": taf_raw_files,
            "processed_file": relative_to_repo(taf_path, repo_root),
        }
    )

    station_url = (
        f"{AVIATIONWEATHER_BASE}/stationinfo?"
        + urlencode({"ids": ids, "format": "json"})
    )
    station_artifact = runner.fetch(
        FetchTask(
            record_type="stationinfo",
            url=station_url,
            raw_path=source_dir / f"stationinfo_{'_'.join(airports)}.json",
            source_effective_date=snapshot_date,
            file_format="json",
            metadata={"retrieved_at": retrieved_at},
        )
    )
    station_records = parse_json_artifact(station_artifact)
    raw_path = station_artifact.task.raw_path
    station_rows = (
        {
            "source_family": "aviationweather",
            "source_record_type": "stationinfo",
            "source_id": record.get("icaoId") or record.get("id") or f"stationinfo:{index}",
            "source_url": station_artifact.final_url,
            "retrieved_at": retrieved_at,
            "snapshot_date": snapshot_date,
            "raw_file": relative_to_repo(raw_path, repo_root),
            "raw": record,
        }
        for index, record in enumerate(station_records)
    )
    station_path = processed_root / "aviationweather_stationinfo.jsonl"
    station_count = write_jsonl(station_path, station_rows)
    inventories.append(
        {
            "source_family": "aviationweather",
            "record_type": "stationinfo",
            "record_count": station_count,
            "raw_file": relative_to_repo(raw_path, repo_root),
            "processed_file": relative_to_repo(station_path, repo_root),
        }
    )

    schema_artifact = runner.fetch(
        FetchTask(
            record_type="openapi_schema",
            url=AVIATIONWEATHER_OPENAPI,
            raw_path=source_dir / "openapi.yaml",
            source_effective_date=snapshot_date,
            file_format="yaml",
            metadata={"retrieved_at": retrieved_at},
        )
    )
    raw_entries.append(artifact_manifest_entry(schema_artifact, repo_root))

    manifest = {
        "source_family": "aviationweather",
        "retrieved_at": retrieved_at,
        "snapshot_date": snapshot_date,
        "scope": {
            "airports": list(airports),
            "alignment_window_start": window_start_iso,
            "alignment_window_end": window_end_iso,
            "metar_hours": metar_hours,
            "taf_date_basis": "valid",
            "taf_query_step_hours": 6,
        },
        "license_or_access_note": "Public NOAA/NWS AviationWeather Data API endpoint.",
        "parser_version": "scripts/collect_nasa_atmonto_phase1.py",
        "known_limitations": [
            "METAR/TAF endpoints provide current rolling observations/forecasts, not a permanent historical archive.",
            "Station metadata is limited to sampled airport IDs for the phase-1 scope.",
        ],
        "files": raw_entries,
    }
    write_json(source_dir / "manifest.json", manifest)
    inventory = {
        "source_family": "aviationweather",
        "retrieved_at": retrieved_at,
        "snapshot_date": snapshot_date,
        "records": inventories,
        "manifest": relative_to_repo(source_dir / "manifest.json", repo_root),
    }
    write_json(reports_root / "nasa_atmonto_aviationweather_source_inventory.json", inventory)
    return inventory


def current_nasr_subscription(index_html: str) -> tuple[str, str]:
    current_section_match = re.search(
        r"<h2>\s*Current\s*</h2>(.*?)(?:<h2>|$)",
        index_html,
        flags=re.I | re.S,
    )
    current_section = current_section_match.group(1) if current_section_match else index_html
    links = parse_links(current_section)
    for href, text in links:
        if "Subscription effective" in text and re.search(r"\d{4}-\d{2}-\d{2}", href):
            return href, text
    raise RuntimeError("Could not find current NASR subscription link")


def nasr_subscription_for_date(index_html: str, anchor: datetime) -> tuple[str, str, str]:
    links = parse_links(index_html)
    candidates: list[tuple[datetime, str, str]] = []
    for href, text in links:
        match = re.search(r"(\d{4}-\d{2}-\d{2})", href)
        if not match:
            match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if not match:
            continue
        effective = parse_utc(f"{match.group(1)}T00:00:00Z")
        if effective <= anchor:
            candidates.append((effective, href, text))
    if not candidates:
        raise RuntimeError(f"Could not find a NASR subscription covering {iso_utc(anchor)}")
    effective, href, text = max(candidates, key=lambda item: item[0])
    return href, text, effective.date().isoformat()


def nasr_zip_url(current_url: str, current_html: str, effective_date: str) -> str:
    links = parse_links(current_html)
    for href, text in links:
        if href.lower().endswith(".zip") or ".zip" in href.lower():
            return urljoin(current_url, href)
        if "28 day subscription" in text.lower() and "zip" in text.lower():
            return urljoin(current_url, href)
    return (
        "https://nfdc.faa.gov/webContent/28DaySub/"
        f"28DaySubscription_Effective_{effective_date}.zip"
    )


def collect_faa_nasr(
    raw_root: Path,
    processed_root: Path,
    reports_root: Path,
    repo_root: Path,
    runner: CollectionRunner,
    airports: tuple[str, ...],
    snapshot_date: str,
    window_start: datetime,
    window_end: datetime,
    retrieved_at: str,
) -> dict[str, object]:
    source_dir = raw_root / "faa_nasr"
    source_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []

    index_artifact = runner.fetch(
        FetchTask(
            record_type="nasr_subscription_index",
            url=NASR_INDEX_URL,
            raw_path=source_dir / "nasr_subscription_index.html",
            source_effective_date=snapshot_date,
            file_format="html",
            metadata={"retrieved_at": retrieved_at},
        )
    )
    index_text = decode_text(index_artifact.body)
    current_href, _current_text, effective_date = nasr_subscription_for_date(index_text, window_start)
    current_url = urljoin(NASR_INDEX_URL, current_href)
    cycle_start = datetime.strptime(effective_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    cycle_end_exclusive = cycle_start + timedelta(days=28)
    entries.append(
        artifact_manifest_entry(
            FetchArtifact(
                task=FetchTask(
                    record_type=index_artifact.task.record_type,
                    url=index_artifact.task.url,
                    raw_path=index_artifact.task.raw_path,
                    source_effective_date=effective_date,
                    file_format=index_artifact.task.file_format,
                    metadata=index_artifact.task.metadata,
                ),
                final_url=index_artifact.final_url,
                status=index_artifact.status,
                content_type=index_artifact.content_type,
                body=index_artifact.body,
                raw_payload_hash=index_artifact.raw_payload_hash,
                cached=index_artifact.cached,
            ),
            repo_root,
        )
    )

    current_artifact = runner.fetch(
        FetchTask(
            record_type="nasr_subscription_page",
            url=current_url,
            raw_path=source_dir / f"nasr_subscription_{effective_date}.html",
            source_effective_date=effective_date,
            file_format="html",
            metadata={"retrieved_at": retrieved_at},
        )
    )
    current_text_body = decode_text(current_artifact.body)
    entries.append(artifact_manifest_entry(current_artifact, repo_root))

    zip_download_url = nasr_zip_url(current_artifact.final_url, current_text_body, effective_date)
    zip_name = f"28DaySubscription_Effective_{effective_date}.zip"
    zip_path = source_dir / zip_name
    if runner.resume and not zip_path.exists():
        for candidate in sorted(
            (repo_root / "data/raw/nasa_atmonto").glob(f"*/faa_nasr/{zip_name}")
        ):
            if candidate.resolve() == zip_path.resolve() or candidate.stat().st_size <= 0:
                continue
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, zip_path)
            LOGGER.info(
                "reuse existing NASR zip %s -> %s",
                relative_to_repo(candidate, repo_root),
                relative_to_repo(zip_path, repo_root),
            )
            break
    zip_artifact = runner.fetch(
        FetchTask(
            record_type="nasr_28_day_subscription_zip",
            url=zip_download_url,
            raw_path=zip_path,
            source_effective_date=effective_date,
            file_format="zip",
            timeout=240,
            metadata={"retrieved_at": retrieved_at},
        )
    )
    zip_path = zip_artifact.task.raw_path
    zip_members: list[dict[str, object]] = []
    if zip_artifact.status == 200:
        with zipfile.ZipFile(zip_path) as archive:
            for item in archive.infolist():
                if item.is_dir():
                    continue
                zip_members.append(
                    {
                        "source_family": "faa_nasr",
                        "source_effective_date": effective_date,
                        "snapshot_date": snapshot_date,
                        "zip_file": relative_to_repo(zip_path, repo_root),
                        "member_name": item.filename,
                        "file_size": item.file_size,
                        "compressed_size": item.compress_size,
                    }
                )
    members_path = processed_root / "faa_nasr_zip_inventory.jsonl"
    member_count = write_jsonl(members_path, zip_members)
    entries.append(
        artifact_manifest_entry(
            zip_artifact,
            repo_root,
            record_count=member_count,
            processed_file=members_path,
        )
    )

    manifest = {
        "source_family": "faa_nasr",
        "retrieved_at": retrieved_at,
        "snapshot_date": snapshot_date,
        "scope": {
            "subscription": "FAA NASR 28-Day Subscription",
            "effective_date": effective_date,
            "cycle_start": iso_utc(cycle_start),
            "cycle_end_exclusive": iso_utc(cycle_end_exclusive),
            "experiment_window_start": iso_utc(window_start),
            "experiment_window_end": iso_utc(window_end),
            "selected_airports": list(airports),
        },
        "license_or_access_note": "FAA public aeronautical data download page.",
        "parser_version": "scripts/collect_nasa_atmonto_phase1.py",
        "known_limitations": [
            "The phase-1 inventory records zip members; semantic field parsing is a later normalization step.",
            "NASR is cycle-valid reference data. The experiment window is a subset of the cycle, not the NASR source time window.",
            "Some enroute resources in the package may update on a 56-day charting basis even though the subscriber files are issued on a 28-day cycle.",
        ],
        "files": entries,
    }
    write_json(source_dir / "manifest.json", manifest)
    inventory = {
        "source_family": "faa_nasr",
        "retrieved_at": retrieved_at,
        "snapshot_date": snapshot_date,
        "source_effective_date": effective_date,
        "cycle_start": iso_utc(cycle_start),
        "cycle_end_exclusive": iso_utc(cycle_end_exclusive),
        "experiment_window_start": iso_utc(window_start),
        "experiment_window_end": iso_utc(window_end),
        "zip_member_count": member_count,
        "zip_file": relative_to_repo(zip_path, repo_root),
        "processed_file": relative_to_repo(members_path, repo_root),
        "manifest": relative_to_repo(source_dir / "manifest.json", repo_root),
    }
    write_json(reports_root / "nasa_atmonto_faa_nasr_source_inventory.json", inventory)
    return inventory


def atcscc_query_url(snapshot_date: str) -> str:
    params = {
        "whichAdvisories": "ATCSCC",
        "advisoryCategory": "All",
        "date": snapshot_date,
        "airflow": "true",
        "_airflow": "on",
        "ctop": "true",
        "_ctop": "on",
        "gStop": "true",
        "_gStop": "on",
        "gDelay": "true",
        "_gDelay": "on",
        "route": "true",
        "_route": "on",
        "other": "true",
        "_other": "on",
    }
    return f"{ATCSCC_LIST_URL}?{urlencode(params)}"


def atcscc_detail_links(html_text: str) -> list[tuple[str, str]]:
    return sorted(
        set(
            re.findall(
                r'href="(/adv/adv_otherdis\?adv_date=\d+&advn=(\d+))"',
                html_text,
            )
        ),
        key=lambda item: int(item[1]),
    )


class AtcsccAdvisorySpider(scrapy.Spider):
    name = "atcscc_advisories"

    def __init__(
        self,
        *,
        source_dir: Path,
        repo_root: Path,
        snapshot_date: str,
        advisory_dates: list[str],
        retrieved_at: str,
        resume: bool,
        entries: list[dict[str, object]],
        processed_rows: list[dict[str, object]],
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self.source_dir = source_dir
        self.repo_root = repo_root
        self.snapshot_date = snapshot_date
        self.advisory_dates = advisory_dates
        self.retrieved_at = retrieved_at
        self.resume = resume
        self.entries = entries
        self.processed_rows = processed_rows
        self.downloaded_advisory_links = 0

    async def start(self) -> AsyncIterator[scrapy.Request]:
        for request in self._start_requests():
            yield request

    def start_requests(self) -> Iterable[scrapy.Request]:
        yield from self._start_requests()

    def _start_requests(self) -> Iterable[scrapy.Request]:
        form_path = self.source_dir / "advAdvisoryForm.html"
        if self.resume and form_path.exists():
            self._append_entry(
                record_type="atcscc_form",
                source_url=ATCSCC_FORM_URL,
                source_effective_date=self.snapshot_date,
                raw_path=form_path,
                body=form_path.read_bytes(),
                file_format="html",
                cached=True,
            )
        else:
            yield scrapy.Request(
                ATCSCC_FORM_URL,
                callback=self.parse_form,
                cb_kwargs={"raw_path": form_path},
                dont_filter=True,
            )

        for advisory_date in self.advisory_dates:
            list_url = atcscc_query_url(advisory_date)
            list_path = self.source_dir / f"adv_list_{advisory_date}.html"
            if self.resume and list_path.exists():
                body = list_path.read_bytes()
                html_text = decode_text(body)
                day_links = atcscc_detail_links(html_text)
                self._append_entry(
                    record_type="atcscc_list",
                    source_url=list_url,
                    source_effective_date=advisory_date,
                    raw_path=list_path,
                    body=body,
                    file_format="html",
                    cached=True,
                    record_count=len(day_links),
                )
                yield from self._detail_requests(day_links, advisory_date)
            else:
                yield scrapy.Request(
                    list_url,
                    callback=self.parse_list,
                    cb_kwargs={"advisory_date": advisory_date, "raw_path": list_path},
                    dont_filter=True,
                )

    def parse_form(self, response: scrapy.http.Response, raw_path: Path) -> None:
        body = bytes(response.body)
        write_bytes(raw_path, body)
        self._append_entry(
            record_type="atcscc_form",
            source_url=response.url,
            source_effective_date=self.snapshot_date,
            raw_path=raw_path,
            body=body,
            file_format="html",
            content_type=response.headers.get("Content-Type", b"").decode("latin-1"),
            status=response.status,
        )

    def parse_list(
        self, response: scrapy.http.Response, advisory_date: str, raw_path: Path
    ) -> Iterable[scrapy.Request]:
        body = bytes(response.body)
        write_bytes(raw_path, body)
        html_text = decode_text(body)
        day_links = atcscc_detail_links(html_text)
        self._append_entry(
            record_type="atcscc_list",
            source_url=response.url,
            source_effective_date=advisory_date,
            raw_path=raw_path,
            body=body,
            file_format="html",
            content_type=response.headers.get("Content-Type", b"").decode("latin-1"),
            status=response.status,
            record_count=len(day_links),
        )
        yield from self._detail_requests(day_links, advisory_date)

    def _detail_requests(
        self, day_links: list[tuple[str, str]], advisory_date: str
    ) -> Iterable[scrapy.Request]:
        self.downloaded_advisory_links += len(day_links)
        for href, advisory_number in day_links:
            url = urljoin(ATCSCC_LIST_URL, href)
            raw_path = self.source_dir / f"advisory_{advisory_date}_{int(advisory_number):03d}.html"
            if self.resume and raw_path.exists():
                self._parse_detail_body(
                    url=url,
                    advisory_date=advisory_date,
                    advisory_number=advisory_number,
                    raw_path=raw_path,
                    body=raw_path.read_bytes(),
                    cached=True,
                )
                continue
            yield scrapy.Request(
                url,
                callback=self.parse_detail,
                cb_kwargs={
                    "advisory_date": advisory_date,
                    "advisory_number": advisory_number,
                    "raw_path": raw_path,
                },
                dont_filter=True,
            )

    def parse_detail(
        self,
        response: scrapy.http.Response,
        advisory_date: str,
        advisory_number: str,
        raw_path: Path,
    ) -> None:
        body = bytes(response.body)
        write_bytes(raw_path, body)
        self._parse_detail_body(
            url=response.url,
            advisory_date=advisory_date,
            advisory_number=advisory_number,
            raw_path=raw_path,
            body=body,
            content_type=response.headers.get("Content-Type", b"").decode("latin-1"),
            status=response.status,
        )

    def _parse_detail_body(
        self,
        *,
        url: str,
        advisory_date: str,
        advisory_number: str,
        raw_path: Path,
        body: bytes,
        content_type: str = "",
        status: int = 200,
        cached: bool = False,
    ) -> None:
        html_text = decode_text(body)
        title_match = re.search(r"<title>(.*?)</title>", html_text, flags=re.I | re.S)
        title = " ".join(title_match.group(1).split()) if title_match else ""
        text = html_to_text(html_text)
        self.processed_rows.append(
            {
                "source_family": "atcscc_advisories",
                "source_record_type": "advisory",
                "source_id": f"{advisory_date}:{int(advisory_number):03d}",
                "advisory_number": int(advisory_number),
                "source_url": url,
                "retrieved_at": self.retrieved_at,
                "snapshot_date": self.snapshot_date,
                "advisory_date": advisory_date,
                "raw_file": relative_to_repo(raw_path, self.repo_root),
                "title": title,
                "text": text,
            }
        )
        if len(self.processed_rows) % 100 == 0:
            LOGGER.info("ATCSCC advisory records processed: %d", len(self.processed_rows))
        self._append_entry(
            record_type="atcscc_advisory",
            source_url=url,
            source_effective_date=advisory_date,
            raw_path=raw_path,
            body=body,
            file_format="html",
            content_type=content_type,
            status=status,
            cached=cached,
            record_count=1,
        )

    def _append_entry(
        self,
        *,
        record_type: str,
        source_url: str,
        source_effective_date: str,
        raw_path: Path,
        body: bytes,
        file_format: str,
        content_type: str = "",
        status: int = 200,
        cached: bool = False,
        record_count: int | None = None,
    ) -> None:
        self.entries.append(
            {
                "record_type": record_type,
                "source_url": source_url,
                "retrieval_command": f"curl -L '{source_url}'",
                "retrieved_at": self.retrieved_at,
                "source_effective_date": source_effective_date,
                "raw_file": relative_to_repo(raw_path, self.repo_root),
                "raw_payload_hash": digest_bytes(body),
                "format": file_format,
                "content_type": content_type,
                "status": status,
                "cached": cached,
                "record_count": record_count,
            }
        )


def collect_atcscc(
    raw_root: Path,
    processed_root: Path,
    reports_root: Path,
    repo_root: Path,
    snapshot_date: str,
    window_start: datetime,
    window_end: datetime,
    retrieved_at: str,
    *,
    workers: int,
    retries: int,
    resume: bool,
    log_level: str,
) -> dict[str, object]:
    source_dir = raw_root / "atcscc_advisories"
    source_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    processed_rows: list[dict[str, object]] = []
    advisory_dates = window_dates(window_start, window_end)
    LOGGER.info(
        "crawl ATCSCC: %d dates, workers=%d, retries=%d, resume=%s",
        len(advisory_dates),
        workers,
        retries,
        resume,
    )
    started = time.monotonic()
    process = CrawlerProcess(
        settings={
            "USER_AGENT": USER_AGENT,
            "LOG_ENABLED": False,
            "LOG_LEVEL": "ERROR",
            "CONCURRENT_REQUESTS": max(1, workers),
            "CONCURRENT_REQUESTS_PER_DOMAIN": max(1, workers),
            "DOWNLOAD_DELAY": 0.05,
            "RETRY_ENABLED": True,
            "RETRY_TIMES": max(1, retries) - 1,
            "RETRY_HTTP_CODES": [408, 429, 500, 502, 503, 504],
            "HTTPCACHE_ENABLED": True,
            "HTTPCACHE_DIR": str(source_dir / ".scrapy_httpcache"),
            "TELNETCONSOLE_ENABLED": False,
            "ROBOTSTXT_OBEY": False,
        },
        install_root_handler=False,
    )
    silence_scrapy_loggers()
    process.crawl(
        AtcsccAdvisorySpider,
        source_dir=source_dir,
        repo_root=repo_root,
        snapshot_date=snapshot_date,
        advisory_dates=advisory_dates,
        retrieved_at=retrieved_at,
        resume=resume,
        entries=entries,
        processed_rows=processed_rows,
    )
    process.start()
    processed_rows.sort(key=lambda row: str(row["source_id"]))
    total_detail_links = sum(
        int(entry.get("record_count") or 0)
        for entry in entries
        if entry.get("record_type") == "atcscc_list"
    )
    LOGGER.info(
        "crawl ATCSCC complete: %d advisory links, %d processed records in %.1fs",
        total_detail_links,
        len(processed_rows),
        time.monotonic() - started,
    )

    processed_path = processed_root / "atcscc_advisories.jsonl"
    advisory_count = write_jsonl(processed_path, processed_rows)
    manifest = {
        "source_family": "atcscc_advisories",
        "retrieved_at": retrieved_at,
        "snapshot_date": snapshot_date,
        "scope": {
            "whichAdvisories": "ATCSCC",
            "advisoryCategory": "All",
            "alignment_window_start": iso_utc(window_start),
            "alignment_window_end": iso_utc(window_end),
            "advisory_dates": window_dates(window_start, window_end),
            "categories": ["airflow", "ctop", "ground_stop", "ground_delay", "route", "other"],
        },
        "license_or_access_note": "FAA public ATCSCC advisory database pages.",
        "parser_version": "scripts/collect_nasa_atmonto_phase1.py",
        "known_limitations": [
            "Advisory text is captured as HTML plus plain text; airport/ARTCC entity extraction is a later step.",
            "The advisory database is collected one UTC date at a time and then filtered to the fixed alignment window.",
        ],
        "files": entries,
        "processed_file": relative_to_repo(processed_path, repo_root),
    }
    write_json(source_dir / "manifest.json", manifest)
    inventory = {
        "source_family": "atcscc_advisories",
        "retrieved_at": retrieved_at,
        "snapshot_date": snapshot_date,
        "advisory_count": advisory_count,
        "downloaded_advisory_links": total_detail_links,
        "alignment_window_start": iso_utc(window_start),
        "alignment_window_end": iso_utc(window_end),
        "processed_file": relative_to_repo(processed_path, repo_root),
        "manifest": relative_to_repo(source_dir / "manifest.json", repo_root),
    }
    write_json(reports_root / "nasa_atmonto_atcscc_advisories_source_inventory.json", inventory)
    return inventory


def write_combined_report(
    reports_root: Path,
    repo_root: Path,
    retrieved_at: str,
    snapshot_date: str,
    window_start: datetime,
    window_end: datetime,
    inventories: list[dict[str, object]],
) -> None:
    combined = {
        "collection": "nasa_atmonto_phase1_core_sources",
        "retrieved_at": retrieved_at,
        "snapshot_date": snapshot_date,
        "alignment_window": {
            "start": iso_utc(window_start),
            "end": iso_utc(window_end),
            "policy": "fixed historical UTC window selected before retrieval",
        },
        "sources": inventories,
    }
    json_path = reports_root / "nasa_atmonto_phase1_collection.json"
    write_json(json_path, combined)

    lines = [
        "# NASA ATMONTO Phase 1 Source Collection",
        "",
        f"- Snapshot date: {snapshot_date}",
        f"- Alignment window: {iso_utc(window_start)} to {iso_utc(window_end)}",
        f"- Retrieved at: {retrieved_at}",
        "",
        "## Collected Sources",
        "",
    ]
    for item in inventories:
        source_family = item["source_family"]
        lines.append(f"### {source_family}")
        for key, value in item.items():
            if key in {"source_family", "records"}:
                continue
            lines.append(f"- {key}: {value}")
        records = item.get("records")
        if isinstance(records, list):
            for record in records:
                lines.append(
                    "- "
                    + ", ".join(f"{key}: {value}" for key, value in record.items())
                )
        lines.append("")
    lines.append(f"Combined JSON: `{relative_to_repo(json_path, repo_root)}`")
    (reports_root / "nasa_atmonto_phase1_collection.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot-date",
        required=True,
        help="Source snapshot date / cycle anchor, YYYY-MM-DD. Pass this explicitly to avoid accidental current-date snapshots.",
    )
    parser.add_argument(
        "--window-start",
        help="Fixed historical alignment window start, ISO UTC. Defaults to snapshot-date T00:00Z.",
    )
    parser.add_argument(
        "--window-end",
        help="Fixed historical alignment window end, ISO UTC. Defaults to window-start + 7 days.",
    )
    parser.add_argument(
        "--airports",
        default=",".join(DEFAULT_AIRPORTS),
        help=(
            "Comma-separated ICAO airport IDs. Defaults to the New York-area "
            "airport set used by the NASA ATM Ontology sample: KJFK,KEWR,KLGA."
        ),
    )
    parser.add_argument(
        "--workers",
        default=12,
        type=int,
        help="Maximum concurrent download workers.",
    )
    parser.add_argument(
        "--retries",
        default=3,
        type=int,
        help="Total HTTP attempts per request, including the initial attempt.",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore existing raw files and fetch everything again.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Console log verbosity.",
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)
    repo_root = args.repo_root.resolve()
    snapshot_date = args.snapshot_date
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", snapshot_date):
        raise SystemExit("--snapshot-date must use YYYY-MM-DD")
    try:
        airports = parse_airports(args.airports)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    window_start = parse_utc(args.window_start or f"{snapshot_date}T00:00:00Z")
    window_end = parse_utc(args.window_end) if args.window_end else window_start + timedelta(days=7)
    if window_end <= window_start:
        raise SystemExit("--window-end must be later than --window-start")
    retrieved_at = utc_now()
    raw_root = repo_root / "data/raw/nasa_atmonto" / snapshot_date
    processed_root = repo_root / "data/processed/nasa_atmonto/source" / snapshot_date
    reports_root = repo_root / "reports/stages"
    reports_root.mkdir(parents=True, exist_ok=True)

    LOGGER.info(
        "collect NASA ATMONTO sources: snapshot=%s window=%s..%s airports=%s workers=%d retries=%d resume=%s",
        snapshot_date,
        iso_utc(window_start),
        iso_utc(window_end),
        ",".join(airports),
        args.workers,
        args.retries,
        not args.no_resume,
    )
    with CollectionRunner(
        repo_root=repo_root,
        workers=args.workers,
        retries=args.retries,
        resume=not args.no_resume,
    ) as runner:
        inventories = [
            collect_aviationweather(
                raw_root,
                processed_root,
                reports_root,
                repo_root,
                runner,
                airports,
                snapshot_date,
                window_start,
                window_end,
                retrieved_at,
            ),
            collect_faa_nasr(
                raw_root,
                processed_root,
                reports_root,
                repo_root,
                runner,
                airports,
                snapshot_date,
                window_start,
                window_end,
                retrieved_at,
            ),
            collect_atcscc(
                raw_root,
                processed_root,
                reports_root,
                repo_root,
                snapshot_date,
                window_start,
                window_end,
                retrieved_at,
                workers=args.workers,
                retries=args.retries,
                resume=not args.no_resume,
                log_level=args.log_level,
            ),
        ]
    write_combined_report(
        reports_root, repo_root, retrieved_at, snapshot_date, window_start, window_end, inventories
    )
    print(
        json.dumps(
            {
                "snapshot_date": snapshot_date,
                "alignment_window": {"start": iso_utc(window_start), "end": iso_utc(window_end)},
                "airports": list(airports),
                "sources": inventories,
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
