#!/usr/bin/env python3
"""Validate reviewer-facing PPTX style constraints for the ATCSCC project deck.

The harness intentionally inspects PPTX OOXML directly so it can run without a
PowerPoint installation. It is not a full visual replacement for rendered-slide
QA; it catches recurring project-level style regressions before visual review.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECK = PROJECT_ROOT / "reports/final/atcscc_agent_kg_ontology_tu_figures.pptx"
DEFAULT_TEMPLATE = (
    PROJECT_ROOT
    / "reports/final/templates/TU-Clausthal-Powerpoint16zu9-ohneStone.potx"
)

TU_TITLE_GREEN = "008C4F"
TU_SIDEBAR_GREY = "D9D9D9"
FOOTER_GREY = "5D6673"
TITLE_MIN_OOXML_SIZE = 2_000
TITLE_MAX_CHARS = 85
TITLE_MIN_WORDS = 5
MUTED_TEXT_MIN_OOXML_SIZE = 1_100
MUTED_TEXT_MAX_CHARS = 32
DECK_SHORT_TITLE = "ATCSCC Agentic KG-RAG"
FOOTER_TEXTS = {"Jiale Wang", "Informatik, TU Clausthal", DECK_SHORT_TITLE}
MUTED_COLORS = {FOOTER_GREY, "526176", "6B7280", "777777"}
INTERNAL_STAGE_PATTERN = re.compile(r"\bS[0-9]\b")
TITLE_ARTIFACT_PATTERN = re.compile(
    r"(/|\\|\.json\b|\.md\b|\.py\b|\.html\b|\.pptx\b|"
    r"\bartifact\b|\bdashboard\b|\bstage\b)",
    re.IGNORECASE,
)
TOPIC_LABEL_TITLES = {
    "architecture",
    "background",
    "conclusion",
    "conclusions",
    "data",
    "demo",
    "discussion",
    "evaluation",
    "experiment",
    "experiments",
    "introduction",
    "method",
    "methodology",
    "motivation",
    "overview",
    "pipeline",
    "results",
    "system architecture",
}
TEXT_SLIDE_BULLET_MIN = 3
TEXT_SLIDE_BULLET_MAX = 5
TEXT_SLIDE_MIN_BODY_SIZE = 1_500
TEXT_SLIDE_MAX_BULLET_CHARS = 120
TABLE_HEADER_MARKERS = {
    "Evaluation item",
    "Extraction setting",
    "Answer setting",
}

A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


@dataclass(frozen=True)
class Run:
    slide: int
    text: str
    size: int
    bold: bool
    color: str | None


@dataclass
class Finding:
    severity: str
    code: str
    message: str


def slide_number(path: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", path)
    if not match:
        raise ValueError(f"not a slide XML path: {path}")
    return int(match.group(1))


def read_slides(deck: Path) -> dict[int, str]:
    with zipfile.ZipFile(deck) as archive:
        slide_paths = sorted(
            (
                name
                for name in archive.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            ),
            key=slide_number,
        )
        return {
            slide_number(name): archive.read(name).decode("utf-8", errors="replace")
            for name in slide_paths
        }


def extract_runs(slide_no: int, xml: str) -> list[Run]:
    root = ET.fromstring(xml)
    runs: list[Run] = []
    for node in root.iter(A_NS + "r"):
        text = "".join((text_node.text or "") for text_node in node.iter(A_NS + "t")).strip()
        if not text:
            continue
        run_props = node.find(A_NS + "rPr")
        if run_props is None:
            runs.append(Run(slide_no, text, 0, False, None))
            continue
        size = int(run_props.get("sz", "0")) if run_props.get("sz") else 0
        bold = run_props.get("b") in {"1", "true"}
        color_node = run_props.find(".//" + A_NS + "srgbClr")
        color = color_node.get("val").upper() if color_node is not None else None
        runs.append(Run(slide_no, text, size, bold, color))
    return runs


def all_text(runs: list[Run]) -> str:
    return "\n".join(run.text for run in runs)


def has_picture(xml: str) -> bool:
    return "<p:pic>" in xml or "<p:pic " in xml


def count_round_rects(xml: str) -> int:
    return xml.count('prst="roundRect"')


def is_table_slide(runs: list[Run]) -> bool:
    text = all_text(runs)
    return any(marker in text for marker in TABLE_HEADER_MARKERS)


def normalized_title_label(text: str) -> str:
    normalized = re.sub(r"[\W_]+", " ", text.casefold()).strip()
    return re.sub(r"\s+", " ", normalized)


def is_all_caps_title(text: str) -> bool:
    letters = [char for char in text if char.isalpha()]
    return len(letters) >= 12 and all(not char.islower() for char in letters)


def title_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", text))


def check_template_exists(template: Path, findings: list[Finding]) -> None:
    if not template.exists():
        findings.append(
            Finding(
                "ERROR",
                "PPT_STYLE001",
                f"Missing TU Clausthal template: {template}",
            )
        )


def check_no_sidecars(deck: Path, findings: list[Finding]) -> None:
    sidecars = sorted(deck.parent.glob(f"{deck.name}.inspect.ndjson"))
    if sidecars:
        joined = ", ".join(str(path) for path in sidecars)
        findings.append(
            Finding(
                "ERROR",
                "PPT_STYLE002",
                f"Generated inspection sidecar should not be kept with final deck: {joined}",
            )
        )


def check_template_chrome(slides: dict[int, str], runs_by_slide: dict[int, list[Run]], findings: list[Finding]) -> None:
    for slide_no, xml in slides.items():
        colors = {match.upper() for match in re.findall(r'<a:srgbClr val="([0-9A-Fa-f]+)"', xml)}
        if TU_SIDEBAR_GREY not in colors:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE010",
                    f"Slide {slide_no} is missing the TU right sidebar color #{TU_SIDEBAR_GREY}.",
                )
            )

        texts = {run.text for run in runs_by_slide[slide_no]}
        missing = sorted(text for text in FOOTER_TEXTS if text not in texts)
        if missing:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE011",
                    f"Slide {slide_no} is missing footer text: {', '.join(missing)}.",
                )
            )
        if str(slide_no) not in texts:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE012",
                    f"Slide {slide_no} is missing page marker '{slide_no}'.",
                )
            )


def check_title_style(runs_by_slide: dict[int, list[Run]], findings: list[Finding]) -> None:
    for slide_no, runs in runs_by_slide.items():
        candidates = [
            run
            for run in runs
            if run.bold and run.size >= TITLE_MIN_OOXML_SIZE and run.text not in FOOTER_TEXTS
        ]
        if not candidates:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE020",
                    f"Slide {slide_no} has no large bold action/title text.",
                )
            )
            continue
        title = max(candidates, key=lambda run: run.size)
        if title.color != TU_TITLE_GREEN:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE021",
                    f"Slide {slide_no} title is #{title.color}, expected TU green #{TU_TITLE_GREEN}: {title.text!r}",
                )
            )
        if title.text.rstrip().endswith((".", "。")):
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE022",
                    f"Slide {slide_no} title must not end with a period: {title.text!r}",
                )
            )
        if len(title.text) > TITLE_MAX_CHARS:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE023",
                    f"Slide {slide_no} title is too long for reviewer-facing slides "
                    f"({len(title.text)}>{TITLE_MAX_CHARS} chars): {title.text!r}",
                )
            )
        if normalized_title_label(title.text) in TOPIC_LABEL_TITLES:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE024",
                    f"Slide {slide_no} uses a topic-label title; use an action title instead: {title.text!r}",
                )
            )
        if title_word_count(title.text) < TITLE_MIN_WORDS:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE028",
                    f"Slide {slide_no} title is too terse to carry an argument; use an action title: {title.text!r}",
                )
            )
        if TITLE_ARTIFACT_PATTERN.search(title.text):
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE025",
                    f"Slide {slide_no} title exposes file, dashboard, artifact, or stage language: {title.text!r}",
                )
            )
        if title.text.count("\n") > 1:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE026",
                    f"Slide {slide_no} title has too many line breaks; keep it to one or two lines: {title.text!r}",
                )
            )
        if is_all_caps_title(title.text):
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE027",
                    f"Slide {slide_no} title is all caps; use sentence case for readability: {title.text!r}",
                )
            )


def check_muted_generated_text(runs_by_slide: dict[int, list[Run]], findings: list[Finding]) -> None:
    allowed_texts = FOOTER_TEXTS | {str(i) for i in runs_by_slide}
    for slide_no, runs in runs_by_slide.items():
        for run in runs:
            if run.color not in MUTED_COLORS:
                continue
            if run.text in allowed_texts:
                continue
            if run.size < MUTED_TEXT_MIN_OOXML_SIZE:
                continue
            if len(run.text) <= MUTED_TEXT_MAX_CHARS:
                continue
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE030",
                    f"Slide {slide_no} has long muted generated text; move it to speaker notes or use body color: {run.text!r}",
                )
            )


def check_no_internal_stage_terms(runs_by_slide: dict[int, list[Run]], findings: list[Finding]) -> None:
    for slide_no, runs in runs_by_slide.items():
        text = all_text(runs)
        match = INTERNAL_STAGE_PATTERN.search(text)
        if match:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE040",
                    f"Slide {slide_no} exposes internal stage label {match.group(0)!r}; use reviewer-facing terminology.",
                )
            )


def check_text_slide_list_style(
    slides: dict[int, str], runs_by_slide: dict[int, list[Run]], findings: list[Finding]
) -> None:
    for slide_no, xml in slides.items():
        if slide_no == 1:
            continue
        if has_picture(xml) or is_table_slide(runs_by_slide[slide_no]):
            continue

        rounded_rects = count_round_rects(xml)
        if rounded_rects:
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE050",
                    f"Slide {slide_no} looks like a text-only slide but uses {rounded_rects} rounded card shapes; use a normal bullet list.",
                )
            )

        bullets = [run for run in runs_by_slide[slide_no] if run.text.startswith("•")]
        if not (TEXT_SLIDE_BULLET_MIN <= len(bullets) <= TEXT_SLIDE_BULLET_MAX):
            findings.append(
                Finding(
                    "ERROR",
                    "PPT_STYLE051",
                    f"Slide {slide_no} text-only layout should have {TEXT_SLIDE_BULLET_MIN}-{TEXT_SLIDE_BULLET_MAX} bullets; found {len(bullets)}.",
                )
            )
            continue

        for bullet in bullets:
            if bullet.size < TEXT_SLIDE_MIN_BODY_SIZE:
                findings.append(
                    Finding(
                        "ERROR",
                        "PPT_STYLE052",
                        f"Slide {slide_no} bullet text is too small; expected >= 20 pt equivalent: {bullet.text!r}",
                    )
                )
            if len(bullet.text) > TEXT_SLIDE_MAX_BULLET_CHARS:
                findings.append(
                    Finding(
                        "ERROR",
                        "PPT_STYLE053",
                        f"Slide {slide_no} bullet is too long; move detail to notes: {bullet.text!r}",
                    )
                )


def validate(deck: Path, template: Path) -> list[Finding]:
    findings: list[Finding] = []
    check_template_exists(template, findings)
    check_no_sidecars(deck, findings)

    if not deck.exists():
        findings.append(Finding("ERROR", "PPT_STYLE000", f"Missing deck: {deck}"))
        return findings

    try:
        slides = read_slides(deck)
    except zipfile.BadZipFile:
        findings.append(Finding("ERROR", "PPT_STYLE000", f"Not a valid PPTX ZIP file: {deck}"))
        return findings

    if not slides:
        findings.append(Finding("ERROR", "PPT_STYLE000", f"No slides found in deck: {deck}"))
        return findings

    runs_by_slide = {slide_no: extract_runs(slide_no, xml) for slide_no, xml in slides.items()}
    check_template_chrome(slides, runs_by_slide, findings)
    check_title_style(runs_by_slide, findings)
    check_muted_generated_text(runs_by_slide, findings)
    check_no_internal_stage_terms(runs_by_slide, findings)
    check_text_slide_list_style(slides, runs_by_slide, findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate TU Clausthal reviewer-facing PPT style constraints."
    )
    parser.add_argument(
        "deck",
        nargs="?",
        type=Path,
        default=DEFAULT_DECK,
        help=f"PPTX file to validate. Default: {DEFAULT_DECK}",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=f"TU Clausthal template path. Default: {DEFAULT_TEMPLATE}",
    )
    args = parser.parse_args()

    findings = validate(args.deck.resolve(), args.template.resolve())
    if findings:
        for finding in findings:
            print(f"{finding.severity} {finding.code}: {finding.message}", file=sys.stderr)
        return 1

    print(f"PPT style harness passed: {args.deck.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
