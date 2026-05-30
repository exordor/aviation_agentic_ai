from __future__ import annotations

import hashlib
import html
import json
import re
import ssl
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import yaml

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.utils.io import write_json_document


NASA_SOURCE_TYPE = "nasa_web_educational_page"
NASA_SOURCE_AUTHORITY = "NASA Glenn Research Center"
NASA_ADVISORY_RISK_LEVEL = "learning"
MIN_CLEANED_TEXT_CHARS = 300
NAV_FOOTER_TERMS = (
    "enter search term",
    "rate this page",
    "did you find what you were looking for",
    "how did you find us",
    "provide feedback",
    "contact information",
    "glenn research center 21000 brookpark road",
)
STOP_TEXT_MARKERS = (
    "National Aeronautics and Space Administration",
    "Privacy Policy",
    "Provide feedback",
    "Rate this page",
)
NASA_AERODYNAMICS_LANDING_URL = (
    "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/learn-about-aerodynamics/"
)
NASA_EXPERIMENT_SECTION = "Lessons in Aerodynamics"


@dataclass(frozen=True)
class ContentBlock:
    tag: str
    text: str
    level: int = 0


class MainContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.blocks: list[ContentBlock] = []
        self._tag_stack: list[str] = []
        self._active_tag = ""
        self._active_level = 0
        self._buffer: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "nav", "header", "footer", "form", "button", "select"}:
            self._skip_depth += 1
            return
        self._tag_stack.append(tag)
        if tag == "title":
            self._active_tag = tag
            self._active_level = 0
            self._buffer = []
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li"}:
            self._active_tag = tag
            self._active_level = int(tag[1]) if tag.startswith("h") else 0
            self._buffer = []
        elif tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self.blocks.append(ContentBlock(tag="img_alt", text=_clean_text(alt)))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._skip_depth and tag in {
            "script",
            "style",
            "nav",
            "header",
            "footer",
            "form",
            "button",
            "select",
        }:
            self._skip_depth -= 1
            return
        if self._active_tag == tag:
            text = _clean_text(" ".join(self._buffer))
            if text:
                if tag == "title":
                    self.title_parts.append(text)
                else:
                    self.blocks.append(ContentBlock(tag=tag, text=text, level=self._active_level))
            self._active_tag = ""
            self._active_level = 0
            self._buffer = []
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._active_tag:
            self._buffer.append(data)


class NASAContentLinkParser(HTMLParser):
    def __init__(self, landing_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.landing_url = landing_url.rstrip("/")
        self.groups: dict[str, list[dict[str, Any]]] = {}
        self._in_main = False
        self._main_depth = 0
        self._current_heading = ""
        self._capture_tag = ""
        self._capture_href = ""
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = dict(attrs)
        if tag == "main":
            self._in_main = True
            self._main_depth = 1
        elif self._in_main:
            self._main_depth += 1
        if not self._in_main:
            return
        if tag in {"h1", "h2", "h3", "a"}:
            self._capture_tag = tag
            self._capture_href = attrs_dict.get("href") or ""
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._in_main and self._capture_tag == tag:
            text = _clean_text(" ".join(self._buffer))
            if text:
                if tag in {"h1", "h2", "h3"}:
                    self._current_heading = text
                    self.groups.setdefault(text, [])
                elif tag == "a":
                    self._record_link(text)
            self._capture_tag = ""
            self._capture_href = ""
            self._buffer = []
        if tag == "main" and self._in_main:
            self._main_depth -= 1
            if self._main_depth <= 0:
                self._in_main = False
        elif self._in_main:
            self._main_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_main and self._capture_tag:
            self._buffer.append(data)

    def _record_link(self, text: str) -> None:
        from urllib.parse import urljoin

        href = urljoin(self.landing_url + "/", self._capture_href).rstrip("/")
        lowered = text.lower()
        if lowered in {"return to top", "provide feedback", "skip to main content"}:
            return
        if "/beginners-guide-to-aeronautics/" not in href:
            return
        if href == "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics":
            return
        if href == self.landing_url:
            return
        heading = self._current_heading or "Ungrouped"
        self.groups.setdefault(heading, []).append(
            {
                "title": text,
                "url": href + "/",
                "section": heading,
                "is_interactive": bool(
                    re.search(
                        r"\b(interactive|simulator|animation|animated)\b",
                        text,
                        flags=re.IGNORECASE,
                    )
                ),
            }
        )


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "untitled"


def read_nasa_source_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"NASA source manifest must be a mapping: {project_relative_path(path)}")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"NASA source manifest must include non-empty sources list: {path}")
    document_ids: set[str] = set()
    for index, record in enumerate(sources, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"NASA manifest source {index} must be a mapping.")
        document_id = str(record.get("document_id", ""))
        if document_id in document_ids:
            raise ValueError(f"Duplicate NASA document_id: {document_id}")
        document_ids.add(document_id)
        if not re.fullmatch(r"[a-z0-9_]+", document_id):
            raise ValueError(f"Unsafe NASA document_id: {document_id}")
        if record.get("source_type") != NASA_SOURCE_TYPE:
            raise ValueError(f"{document_id}: source_type must be {NASA_SOURCE_TYPE}")
        if record.get("source_authority") != NASA_SOURCE_AUTHORITY:
            raise ValueError(f"{document_id}: source_authority must be {NASA_SOURCE_AUTHORITY}")
        if record.get("advisory_risk_level") != NASA_ADVISORY_RISK_LEVEL:
            raise ValueError(f"{document_id}: advisory_risk_level must be learning")
        if not str(record.get("url", "")).startswith("https://www1.grc.nasa.gov/"):
            raise ValueError(f"{document_id}: URL must be a NASA Glenn HTTPS page")
        if "source_section" not in record:
            raise ValueError(f"{document_id}: missing source_section")
        if "include_in_experiment" not in record:
            raise ValueError(f"{document_id}: missing include_in_experiment")
    return payload


def fetch_nasa_page(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "aviation-agentic-ai-source-ingestion/1.0"},
    )
    context = None
    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def discover_nasa_aerodynamics_links(
    html_text: str,
    *,
    landing_url: str = NASA_AERODYNAMICS_LANDING_URL,
) -> dict[str, Any]:
    parser = NASAContentLinkParser(landing_url)
    parser.feed(html_text)
    groups: dict[str, list[dict[str, Any]]] = {}
    seen_urls: set[str] = set()
    duplicates: list[dict[str, Any]] = []
    unique_links = []
    for heading, links in parser.groups.items():
        rows = []
        for link in links:
            if link["url"] in seen_urls:
                duplicates.append(link)
                continue
            seen_urls.add(link["url"])
            rows.append(link)
            unique_links.append(link)
        if rows:
            groups[heading] = rows
    return {
        "landing_url": landing_url,
        "groups": groups,
        "links_total": sum(len(links) for links in parser.groups.values()),
        "unique_urls_total": len(unique_links),
        "duplicate_url_entries": duplicates,
        "interactive_links_total": sum(1 for link in unique_links if link["is_interactive"]),
        "unique_links": unique_links,
    }


def build_nasa_source_discovery(
    manifest_path: str | Path,
    *,
    landing_html: str,
    landing_url: str = NASA_AERODYNAMICS_LANDING_URL,
) -> dict[str, Any]:
    manifest = read_nasa_source_manifest(manifest_path)
    discovery = discover_nasa_aerodynamics_links(landing_html, landing_url=landing_url)
    manifest_urls = {str(record["url"]).rstrip("/") + "/" for record in manifest["sources"]}
    discovered_urls = {link["url"] for link in discovery["unique_links"]}
    covered = [
        {**link, "manifest_status": "covered"}
        for link in discovery["unique_links"]
        if link["url"] in manifest_urls
    ]
    missing = [
        {**link, "manifest_status": "missing_from_current_manifest"}
        for link in discovery["unique_links"]
        if link["url"] not in manifest_urls
    ]
    manifest_only = sorted(manifest_urls - discovered_urls)
    by_section = {
        section: {
            "discovered_unique_urls": len(links),
            "covered_by_manifest": sum(1 for link in links if link["url"] in manifest_urls),
            "missing_from_manifest": sum(1 for link in links if link["url"] not in manifest_urls),
        }
        for section, links in discovery["groups"].items()
    }
    return {
        "metadata": {
            "landing_url": landing_url,
            "manifest_path": project_relative_path(manifest_path),
            "manifest_sources_total": len(manifest["sources"]),
            "discovered_links_total": discovery["links_total"],
            "discovered_unique_urls_total": discovery["unique_urls_total"],
            "covered_unique_urls_total": len(covered),
            "missing_unique_urls_total": len(missing),
            "manifest_only_urls_total": len(manifest_only),
            "interactive_unique_urls_total": discovery["interactive_links_total"],
            "coverage_rate": round(len(covered) / discovery["unique_urls_total"], 4)
            if discovery["unique_urls_total"]
            else 0.0,
            "experiment_subset_section": NASA_EXPERIMENT_SECTION,
            "selection_status": (
                "full_landing_page_collection_with_aerodynamics_experiment_subset"
                if len(missing) == 0
                else "partial_collection_not_complete_landing_page_crawl"
            ),
            "human_review": False,
            "external_aviation_expert_certified": False,
            "operational_readiness_claimed": False,
        },
        "by_section": by_section,
        "covered_links": covered,
        "missing_links": missing,
        "manifest_only_urls": manifest_only,
        "duplicate_url_entries": discovery["duplicate_url_entries"],
        "claim_policy": (
            "The current NASA experiment subset is smaller than the collected corpus. "
            "This report prevents overclaiming the subset as the full NASA BGA landing page."
        ),
    }


def write_nasa_source_discovery_report(
    manifest_path: str | Path,
    output_dir: str | Path,
    *,
    landing_url: str = NASA_AERODYNAMICS_LANDING_URL,
    landing_html: str | None = None,
    report_name: str = "nasa_source_discovery",
) -> tuple[Path, Path, dict[str, Any]]:
    html_text = landing_html if landing_html is not None else fetch_nasa_page(landing_url)
    result = build_nasa_source_discovery(
        manifest_path,
        landing_html=html_text,
        landing_url=landing_url,
    )
    output = Path(output_dir)
    json_path = output / f"{report_name}.json"
    md_path = output / f"{report_name}.md"
    write_json_document(result, json_path)
    metadata = result["metadata"]
    lines = [
        "# NASA Source Discovery",
        "",
        f"- Landing URL: {landing_url}",
        f"- Manifest sources: {metadata['manifest_sources_total']}",
        f"- Discovered unique content URLs: {metadata['discovered_unique_urls_total']}",
        f"- Covered by current manifest: {metadata['covered_unique_urls_total']}",
        f"- Missing from current manifest: {metadata['missing_unique_urls_total']}",
        f"- Coverage rate: {metadata['coverage_rate']}",
        f"- Selection status: `{metadata['selection_status']}`",
        "- Claim policy: collection coverage and experiment subset are reported separately.",
        "",
        "| Section | Discovered | Covered | Missing |",
        "| --- | ---: | ---: | ---: |",
    ]
    for section, values in result["by_section"].items():
        lines.append(
            f"| {section} | {values['discovered_unique_urls']} | "
            f"{values['covered_by_manifest']} | {values['missing_from_manifest']} |"
        )
    if result["missing_links"]:
        lines.extend(["", "## Missing From Current Manifest", ""])
        for link in result["missing_links"]:
            suffix = " (interactive)" if link.get("is_interactive") else ""
            lines.append(f"- {link['section']}: [{link['title']}]({link['url']}){suffix}")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path, result


def _parse_blocks(html_text: str) -> tuple[str, list[ContentBlock]]:
    parser = MainContentParser()
    parser.feed(html_text)
    title = parser.title_parts[0] if parser.title_parts else ""
    return title, parser.blocks


def _filter_content_blocks(blocks: list[ContentBlock]) -> list[ContentBlock]:
    filtered: list[ContentBlock] = []
    for block in blocks:
        text = block.text
        if any(marker in text for marker in STOP_TEXT_MARKERS):
            break
        lowered = text.lower()
        if any(term in lowered for term in NAV_FOOTER_TERMS):
            continue
        if block.tag == "img_alt" and len(text.split()) < 3:
            continue
        filtered.append(block)
    return filtered


def extract_main_content(html_text: str) -> str:
    _title, blocks = _parse_blocks(html_text)
    filtered = _filter_content_blocks(blocks)
    return "\n\n".join(block.text for block in filtered if block.text)


def extract_page_metadata(html_text: str, url: str) -> dict[str, Any]:
    parsed_title, blocks = _parse_blocks(html_text)
    title = ""
    for block in blocks:
        if block.tag == "h1":
            title = block.text
            break
    text = _clean_text(re.sub(r"<[^>]+>", " ", html_text))
    match = re.search(r"Page Last Updated:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
    return {
        "title": title or parsed_title.removesuffix(" | Glenn Research Center | NASA"),
        "url": url,
        "page_last_updated": match.group(1) if match else "",
    }


def _sections_from_blocks(blocks: list[ContentBlock], cleaned_text: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    heading_blocks = [block for block in blocks if block.tag.startswith("h")]
    if not heading_blocks:
        return [
            {
                "section_id": "section_00_body",
                "title": "Body",
                "level": 1,
                "order": 0,
                "parent_id": None,
                "text_start": 0,
                "text_end": len(cleaned_text),
            }
        ]
    for order, block in enumerate(heading_blocks):
        start = cleaned_text.find(block.text)
        if start < 0:
            start = 0
        next_start = len(cleaned_text)
        if order + 1 < len(heading_blocks):
            candidate = cleaned_text.find(heading_blocks[order + 1].text, start + len(block.text))
            if candidate >= 0:
                next_start = candidate
        sections.append(
            {
                "section_id": f"section_{order:02d}_{_safe_slug(block.text)}",
                "title": block.text,
                "level": block.level or 1,
                "order": order,
                "parent_id": None,
                "text_start": start,
                "text_end": next_start,
            }
        )
    return sections


def _equations_from_text(cleaned_text: str) -> list[str]:
    equations = []
    for line in cleaned_text.splitlines():
        stripped = line.strip()
        if "\\(" in stripped or "\\LARGE" in stripped or re.search(r"\b[A-Za-z]\s*=", stripped):
            equations.append(stripped)
    return equations[:20]


def normalize_nasa_page(record: dict[str, Any], html_text: str) -> dict[str, Any]:
    metadata = extract_page_metadata(html_text, str(record["url"]))
    _title, blocks = _parse_blocks(html_text)
    filtered = _filter_content_blocks(blocks)
    cleaned_text = "\n\n".join(block.text for block in filtered if block.text)
    headings = [block.text for block in filtered if block.tag.startswith("h")]
    page = {
        "document_id": record["document_id"],
        "title": metadata["title"] or record["title"],
        "url": record["url"],
        "source_type": record["source_type"],
        "source_authority": record["source_authority"],
        "advisory_risk_level": record["advisory_risk_level"],
        "source_section": record.get("source_section", ""),
        "is_interactive": bool(record.get("is_interactive", False)),
        "include_in_corpus": bool(record.get("include_in_corpus", True)),
        "include_in_experiment": bool(record.get("include_in_experiment", False)),
        "experiment_scope": record.get("experiment_scope", ""),
        "page_last_updated": metadata.get("page_last_updated", ""),
        "crawl_timestamp": datetime.now(UTC).isoformat(),
        "content_hash": hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest(),
        "headings": headings,
        "cleaned_text": cleaned_text,
        "sections": _sections_from_blocks(filtered, cleaned_text),
        "equations": _equations_from_text(cleaned_text),
        "expected_topics": list(record.get("expected_topics", [])),
        "expected_ontology_concepts": list(record.get("expected_ontology_concepts", [])),
        "expected_relations": list(record.get("expected_relations", [])),
        "warnings": [],
        "validation_status": "unchecked",
    }
    validation = validate_nasa_source_page(page, raise_on_error=False)
    page["warnings"] = validation["warnings"]
    page["validation_status"] = "valid" if validation["valid"] else "invalid"
    return page


def validate_nasa_source_page(
    page: dict[str, Any],
    *,
    raise_on_error: bool = True,
) -> dict[str, Any]:
    warnings: list[str] = []
    errors: list[str] = []
    required = [
        "document_id",
        "title",
        "url",
        "source_type",
        "source_authority",
        "advisory_risk_level",
        "content_hash",
        "cleaned_text",
        "sections",
    ]
    for field in required:
        if not page.get(field):
            errors.append(f"missing {field}")
    if page.get("source_type") != NASA_SOURCE_TYPE:
        errors.append("source_type is not nasa_web_educational_page")
    if page.get("source_authority") != NASA_SOURCE_AUTHORITY:
        errors.append("source_authority is not NASA Glenn Research Center")
    if page.get("advisory_risk_level") != NASA_ADVISORY_RISK_LEVEL:
        errors.append("advisory_risk_level is not learning")
    text = str(page.get("cleaned_text", ""))
    if len(text) < MIN_CLEANED_TEXT_CHARS:
        errors.append("cleaned_text below minimum length")
    if not page.get("headings") and not page.get("sections"):
        errors.append("no headings or sections")
    lowered = text.lower()
    nav_hits = [term for term in NAV_FOOTER_TERMS if term in lowered]
    if nav_hits:
        warnings.append(f"possible nav/footer terms present: {', '.join(nav_hits)}")
    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    if errors and raise_on_error:
        raise ValueError(f"Invalid NASA source page {page.get('document_id')}: {errors}")
    return result


def load_normalized_nasa_pages(
    raw_dir: str | Path,
    *,
    experiment_only: bool = False,
) -> list[dict[str, Any]]:
    """Load normalized NASA page JSON files from an ingestion directory."""
    pages: list[dict[str, Any]] = []
    for path in sorted(Path(raw_dir).glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("document_id"):
            if experiment_only and not bool(payload.get("include_in_experiment", False)):
                continue
            pages.append(payload)
    return pages


def build_nasa_source_metadata(pages: list[dict[str, Any]]) -> dict[str, Any]:
    documents = []
    for page in sorted(pages, key=lambda item: str(item.get("document_id", ""))):
        sections = page.get("sections", [])
        documents.append(
            {
                "document_id": page.get("document_id", ""),
                "title": page.get("title", ""),
                "url": page.get("url", ""),
                "source_type": page.get("source_type", ""),
                "source_section": page.get("source_section", ""),
                "include_in_corpus": bool(page.get("include_in_corpus", True)),
                "include_in_experiment": bool(page.get("include_in_experiment", False)),
                "experiment_scope": page.get("experiment_scope", ""),
                "page_last_updated": page.get("page_last_updated", ""),
                "advisory_risk_level": page.get("advisory_risk_level", ""),
                "section_count": len(sections) if isinstance(sections, list) else 0,
                "section_ids": [
                    str(section.get("section_id", ""))
                    for section in sections
                    if isinstance(section, dict)
                ],
                "content_hash": page.get("content_hash", ""),
                "ingestion_status": page.get("validation_status", "unchecked"),
            }
        )
    return {
        "corpus_id": "nasa_bga_aerodynamics",
        "source_type": NASA_SOURCE_TYPE,
        "source_authority": NASA_SOURCE_AUTHORITY,
        "advisory_risk_level": NASA_ADVISORY_RISK_LEVEL,
        "documents_total": len(documents),
        "experiment_documents_total": sum(
            1 for document in documents if document["include_in_experiment"]
        ),
        "documents": documents,
    }


def build_nasa_section_records(pages: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for page in sorted(pages, key=lambda item: str(item.get("document_id", ""))):
        for section in page.get("sections", []):
            if not isinstance(section, dict):
                continue
            records.append(
                {
                    "document_id": page.get("document_id", ""),
                    "section_id": section.get("section_id", ""),
                    "title": section.get("title", ""),
                    "level": section.get("level", 1),
                    "order": section.get("order", 0),
                    "parent_id": section.get("parent_id"),
                    "text_start": section.get("text_start", 0),
                    "text_end": section.get("text_end", 0),
                    "source_url": page.get("url", ""),
                    "source_section": page.get("source_section", ""),
                    "include_in_experiment": bool(page.get("include_in_experiment", False)),
                }
            )
    return {
        "corpus_id": "nasa_bga_aerodynamics",
        "source_type": NASA_SOURCE_TYPE,
        "sections_total": len(records),
        "sections": records,
    }


def build_nasa_source_validation(pages: list[dict[str, Any]]) -> dict[str, Any]:
    document_ids = [str(page.get("document_id", "")) for page in pages]
    duplicate_ids = sorted(
        document_id for document_id, count in Counter(document_ids).items() if count > 1
    )
    page_results = []
    errors: list[str] = []
    warnings: list[str] = []
    for page in pages:
        validation = validate_nasa_source_page(page, raise_on_error=False)
        document_id = str(page.get("document_id", ""))
        page_errors = list(validation["errors"])
        page_warnings = list(validation["warnings"])
        if document_id in duplicate_ids:
            page_errors.append("duplicate document_id")
        if not page.get("url"):
            page_errors.append("missing URL")
        if not page.get("content_hash"):
            page_errors.append("missing content_hash")
        page_results.append(
            {
                "document_id": document_id,
                "title": page.get("title", ""),
                "url": page.get("url", ""),
                "source_section": page.get("source_section", ""),
                "include_in_experiment": bool(page.get("include_in_experiment", False)),
                "valid": not page_errors,
                "errors": page_errors,
                "warnings": page_warnings,
                "ingestion_error": page.get("ingestion_error", ""),
                "cleaned_text_chars": len(str(page.get("cleaned_text", ""))),
                "sections_total": len(page.get("sections", []))
                if isinstance(page.get("sections"), list)
                else 0,
            }
        )
        errors.extend(f"{document_id}: {error}" for error in page_errors)
        warnings.extend(f"{document_id}: {warning}" for warning in page_warnings)
    valid_pages = sum(1 for page in page_results if page["valid"])
    experiment_pages = [page for page in page_results if page["include_in_experiment"]]
    experiment_valid_pages = sum(1 for page in experiment_pages if page["valid"])
    return {
        "valid": not errors and bool(pages),
        "experiment_valid": bool(experiment_pages) and experiment_valid_pages == len(experiment_pages),
        "metadata": {
            "corpus_id": "nasa_bga_aerodynamics",
            "source_type": NASA_SOURCE_TYPE,
            "source_authority": NASA_SOURCE_AUTHORITY,
            "advisory_risk_level": NASA_ADVISORY_RISK_LEVEL,
            "pages_total": len(pages),
            "experiment_pages_total": sum(
                1 for page in pages if bool(page.get("include_in_experiment", False))
            ),
            "experiment_valid_pages": experiment_valid_pages,
            "experiment_invalid_pages": len(experiment_pages) - experiment_valid_pages,
            "valid_pages": valid_pages,
            "invalid_pages": len(pages) - valid_pages,
            "minimum_cleaned_text_chars": MIN_CLEANED_TEXT_CHARS,
            "human_review": False,
            "external_aviation_expert_certified": False,
            "operational_readiness_claimed": False,
        },
        "checks": {
            "document_ids_unique": not duplicate_ids,
            "urls_present": all(bool(page.get("url")) for page in pages),
            "cleaned_text_present": all(bool(page.get("cleaned_text")) for page in pages),
            "content_hash_present": all(bool(page.get("content_hash")) for page in pages),
            "advisory_risk_level_learning": all(
                page.get("advisory_risk_level") == NASA_ADVISORY_RISK_LEVEL
                for page in pages
            ),
            "source_type_expected": all(page.get("source_type") == NASA_SOURCE_TYPE for page in pages),
        },
        "pages": page_results,
        "errors": errors,
        "warnings": warnings,
        "claim_policy": (
            "NASA source validation is source-scoped educational evidence. It is not "
            "external certification, operational readiness, or proof of a complete aviation ontology."
        ),
    }


def write_nasa_source_metadata_and_sections(
    pages: list[dict[str, Any]],
    *,
    metadata_path: str | Path,
    sections_path: str | Path,
) -> tuple[Path, Path, dict[str, Any], dict[str, Any]]:
    metadata = build_nasa_source_metadata(pages)
    sections = build_nasa_section_records(pages)
    metadata_output = write_json_document(metadata, metadata_path)
    sections_output = write_json_document(sections, sections_path)
    return metadata_output, sections_output, metadata, sections


def write_nasa_source_validation_report(
    raw_dir: str | Path,
    output_dir: str | Path,
    *,
    metadata_path: str | Path,
    sections_path: str | Path,
    report_name: str = "nasa_source_validation",
) -> tuple[Path, Path, dict[str, Any]]:
    pages = load_normalized_nasa_pages(raw_dir)
    metadata_output, sections_output, _metadata, _sections = (
        write_nasa_source_metadata_and_sections(
            pages,
            metadata_path=metadata_path,
            sections_path=sections_path,
        )
    )
    result = build_nasa_source_validation(pages)
    result["metadata"]["metadata_path"] = project_relative_path(metadata_output)
    result["metadata"]["sections_path"] = project_relative_path(sections_output)
    output = Path(output_dir)
    json_path = output / f"{report_name}.json"
    md_path = output / f"{report_name}.md"
    write_json_document(result, json_path)
    lines = [
        "# NASA Source Validation",
        "",
        f"- Pages: {result['metadata']['pages_total']}",
        f"- Valid pages: {result['metadata']['valid_pages']}",
        f"- Experiment pages: {result['metadata']['experiment_pages_total']}",
        f"- Experiment valid pages: {result['metadata']['experiment_valid_pages']}",
        f"- Source type: `{NASA_SOURCE_TYPE}`",
        f"- Advisory risk level: `{NASA_ADVISORY_RISK_LEVEL}`",
        "- Human review: false",
        "- External aviation expert certified: false",
        "- Claim policy: source-scoped educational validation only.",
        "",
        "| Document | Valid | Chars | Sections | Errors |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for page in result["pages"]:
        errors_text = "; ".join(page["errors"]) if page["errors"] else ""
        lines.append(
            f"| `{page['document_id']}` | {page['valid']} | "
            f"{page['cleaned_text_chars']} | {page['sections_total']} | {errors_text} |"
        )
    if result["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path, result


def write_nasa_raw_json(page: dict[str, Any], output_dir: str | Path) -> Path:
    path = Path(output_dir) / f"{page['document_id']}.json"
    write_json_document(page, path)
    return path


def write_nasa_markdown(page: dict[str, Any], output_dir: str | Path) -> Path:
    path = Path(output_dir) / f"{page['document_id']}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {page['title']}",
        "",
        f"- Document ID: `{page['document_id']}`",
        f"- Source URL: {page['url']}",
        f"- Source type: `{page['source_type']}`",
        f"- Authority: {page['source_authority']}",
        f"- Advisory risk level: `{page['advisory_risk_level']}`",
        f"- Page last updated: {page.get('page_last_updated') or 'not found'}",
        f"- Content hash: `{page['content_hash']}`",
    ]
    if page.get("ingestion_error"):
        lines.append(f"- Ingestion error: {page['ingestion_error']}")
    lines.extend(["", "## Cleaned Content", "", page["cleaned_text"]])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def _write_ingestion_report(
    pages: list[dict[str, Any]],
    output_dir: str | Path,
    *,
    report_name: str = "nasa_source_ingestion",
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    valid_total = sum(1 for page in pages if page.get("validation_status") == "valid")
    report = {
        "metadata": {
            "source_type": NASA_SOURCE_TYPE,
            "source_authority": NASA_SOURCE_AUTHORITY,
            "advisory_risk_level": NASA_ADVISORY_RISK_LEVEL,
            "pages_total": len(pages),
            "valid_pages": valid_total,
            "invalid_pages": len(pages) - valid_total,
            "human_review": False,
            "external_aviation_expert_certified": False,
            "operational_readiness_claimed": False,
        },
        "pages": [
            {
                "document_id": page["document_id"],
                "title": page["title"],
                "url": page["url"],
                "source_section": page.get("source_section", ""),
                "include_in_experiment": bool(page.get("include_in_experiment", False)),
                "validation_status": page["validation_status"],
                "content_hash": page["content_hash"],
                "cleaned_text_chars": len(page.get("cleaned_text", "")),
                "sections_total": len(page.get("sections", [])),
                "warnings": page.get("warnings", []),
                "ingestion_error": page.get("ingestion_error", ""),
            }
            for page in pages
        ],
        "claim_policy": (
            "NASA Glenn pages are educational source-diversity evidence only; they do "
            "not provide operational readiness or external certification."
        ),
    }
    json_path = output / f"{report_name}.json"
    md_path = output / f"{report_name}.md"
    write_json_document(report, json_path)
    lines = [
        "# NASA Source Ingestion",
        "",
        f"- Pages: {len(pages)}",
        f"- Valid pages: {valid_total}",
        f"- Experiment pages: {sum(1 for page in pages if page.get('include_in_experiment'))}",
        f"- Source type: `{NASA_SOURCE_TYPE}`",
        f"- Authority: {NASA_SOURCE_AUTHORITY}",
        "- Claim policy: educational source-diversity evidence only; no operational readiness.",
        "",
        "| Document | Source section | Experiment | Status | Chars | Sections |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for page in report["pages"]:
        lines.append(
            f"| `{page['document_id']}` | {page['source_section']} | "
            f"{page['include_in_experiment']} | {page['validation_status']} | "
            f"{page['cleaned_text_chars']} | {page['sections_total']} |"
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path, report


def _failed_nasa_page(record: dict[str, Any], error: Exception) -> dict[str, Any]:
    cleaned_text = ""
    return {
        "document_id": record["document_id"],
        "title": record.get("title", record["document_id"]),
        "url": record["url"],
        "source_type": record["source_type"],
        "source_authority": record["source_authority"],
        "advisory_risk_level": record["advisory_risk_level"],
        "source_section": record.get("source_section", ""),
        "is_interactive": bool(record.get("is_interactive", False)),
        "include_in_corpus": bool(record.get("include_in_corpus", True)),
        "include_in_experiment": bool(record.get("include_in_experiment", False)),
        "experiment_scope": record.get("experiment_scope", ""),
        "page_last_updated": "",
        "crawl_timestamp": datetime.now(UTC).isoformat(),
        "content_hash": hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest(),
        "headings": [],
        "cleaned_text": cleaned_text,
        "sections": [],
        "equations": [],
        "expected_topics": list(record.get("expected_topics", [])),
        "expected_ontology_concepts": list(record.get("expected_ontology_concepts", [])),
        "expected_relations": list(record.get("expected_relations", [])),
        "warnings": ["source fetch failed"],
        "validation_status": "invalid",
        "ingestion_error": f"{type(error).__name__}: {error}",
    }


def _ingest_nasa_record(
    record: dict[str, Any],
    *,
    fixture_dir: str | Path | None,
    fetcher: Any,
) -> dict[str, Any]:
    try:
        if fixture_dir is not None:
            html_path = Path(fixture_dir) / f"{record['document_id']}.html"
            html_text = html_path.read_text(encoding="utf-8")
        else:
            html_text = fetcher(str(record["url"]))
        return normalize_nasa_page(record, html_text)
    except Exception as error:  # pragma: no cover - depends on external source availability.
        return _failed_nasa_page(record, error)


def _prune_stale_nasa_outputs(raw_dir: Path, document_ids: set[str]) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("*.json", "*.md"):
        for path in raw_dir.glob(suffix):
            if path.stem not in document_ids:
                path.unlink()


def ingest_nasa_sources(
    manifest_path: str | Path,
    *,
    raw_output_dir: str | Path,
    report_output_dir: str | Path,
    fixture_dir: str | Path | None = None,
    fetcher: Any = fetch_nasa_page,
    workers: int = 4,
    prune_stale: bool = True,
) -> tuple[Path, Path, dict[str, Any]]:
    manifest = read_nasa_source_manifest(manifest_path)
    raw_dir = Path(raw_output_dir)
    records = [
        record
        for record in manifest["sources"]
        if bool(record.get("include_in_corpus", True))
    ]
    if prune_stale:
        _prune_stale_nasa_outputs(
            raw_dir,
            {str(record["document_id"]) for record in records},
        )
    if workers <= 1 or len(records) <= 1:
        pages = [
            _ingest_nasa_record(record, fixture_dir=fixture_dir, fetcher=fetcher)
            for record in records
        ]
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            pages = list(
                executor.map(
                    lambda record: _ingest_nasa_record(
                        record,
                        fixture_dir=fixture_dir,
                        fetcher=fetcher,
                    ),
                    records,
                )
            )
    for page in pages:
        write_nasa_raw_json(page, raw_dir)
        write_nasa_markdown(page, raw_dir)
    return _write_ingestion_report(pages, report_output_dir)
