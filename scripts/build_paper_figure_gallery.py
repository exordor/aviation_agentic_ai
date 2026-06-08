from __future__ import annotations

import html
import json
import os
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "tmp" / "pdfs"
DEFAULT_OUTPUT_HTML = ROOT / "reports" / "stages" / "paper_figure_gallery.html"
DEFAULT_OUTPUT_MANIFEST = ROOT / "reports" / "stages" / "paper_figure_gallery_manifest.json"
DEFAULT_CROP_SPECS = ROOT / "reports" / "stages" / "paper_figure_crop_specs.json"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
ASSET_KIND_PRIORITY = {
    "evaluation_image": 0,
    "curated_crop": 1,
    "mineru_extract": 2,
    "page_render": 3,
    "embedded_image": 4,
    "image": 5,
}


@dataclass(frozen=True)
class GalleryAsset:
    paper_slug: str
    paper_title: str
    asset_kind: str
    path: str
    relative_to_html: str
    filename: str
    page_number: int | None
    asset_index: int | None
    width: int | None
    height: int | None
    source_pdf: str | None
    caption: str | None
    visual_score: float
    thumbnail_color_count: int
    is_figure_candidate: bool
    candidate_reason: str | None


def _natural_key(text: str) -> list[int | str]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", text)]


def _project_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _html_relative(path: Path, output_html: Path) -> str:
    return Path(os.path.relpath(path.resolve(), output_html.parent.resolve())).as_posix()


def _read_readme_source_pdf(paper_dir: Path) -> str | None:
    readme = paper_dir / "README.md"
    if not readme.exists():
        return None
    for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("- Source PDF:"):
            return line.split("`", 2)[1] if "`" in line else line.split(":", 1)[1].strip()
    return None


def _title_from_source_pdf(source_pdf: str | None, slug: str) -> str:
    if not source_pdf:
        return slug.replace("_", " ").title()
    stem = Path(source_pdf).stem
    return re.sub(r"[_\\-]+", " ", stem).strip().title() or slug.replace("_", " ").title()


def _read_mineru_asset_metadata(paper_dir: Path) -> dict[str, dict[str, Any]]:
    manifest = paper_dir / "mineru_assets" / "mineru_assets_manifest.json"
    if not manifest.exists():
        return {}
    try:
        items = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {str(item.get("filename")): item for item in items if isinstance(item, dict) and item.get("filename")}


def _safe_crop_filename(spec: dict[str, Any]) -> str:
    label = str(spec.get("label") or spec.get("id") or "crop")
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", label).strip("_").lower()
    return f"{safe or 'crop'}.png"


def _write_curated_crops(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    crop_specs: Path = DEFAULT_CROP_SPECS,
) -> None:
    if not crop_specs.exists():
        return
    specs = json.loads(crop_specs.read_text(encoding="utf-8"))
    for spec in specs.get("crops", []):
        paper_slug = spec["paper_slug"]
        page_number = int(spec["page"])
        box = tuple(int(value) for value in spec["box"])
        if len(box) != 4:
            raise ValueError(f"Invalid crop box for {paper_slug}: {box!r}")
        page_path = input_dir / paper_slug / "pages" / f"page-{page_number:02d}.png"
        if not page_path.exists():
            page_path = input_dir / paper_slug / "pages" / f"page-{page_number}.png"
        if not page_path.exists():
            continue
        out_dir = input_dir / paper_slug / "curated_crops"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / _safe_crop_filename(spec)
        try:
            from PIL import Image

            with Image.open(page_path) as page_image:
                page_image.crop(box).save(out_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to crop {page_path} with {box!r}") from exc


def _read_manual_exclusions(crop_specs: Path = DEFAULT_CROP_SPECS) -> set[tuple[str, str]]:
    if not crop_specs.exists():
        return set()
    specs = json.loads(crop_specs.read_text(encoding="utf-8"))
    exclusions: set[tuple[str, str]] = set()
    for item in specs.get("exclusions", []):
        if not isinstance(item, dict):
            continue
        paper_slug = item.get("paper_slug")
        filename = item.get("filename")
        if isinstance(paper_slug, str) and isinstance(filename, str):
            exclusions.add((paper_slug, filename))
    return exclusions


def _page_number(path: Path) -> int | None:
    match = re.search(r"page[-_]?0*(\d+)", path.stem, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _asset_index(path: Path) -> int | None:
    match = re.search(r"(?:image|fig|eval)[-_]?0*(\d+)", path.stem, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _image_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        from PIL import Image

        with Image.open(path) as image:
            return image.size
    except Exception:
        return None, None


def _image_visual_score(path: Path) -> float:
    try:
        from PIL import Image, ImageStat

        with Image.open(path) as image:
            rgb = image.convert("RGB")
            rgb.thumbnail((128, 128))
            stat = ImageStat.Stat(rgb)
            r_mean, g_mean, b_mean = stat.mean
            r_std, g_std, b_std = stat.stddev
            color_delta = abs(r_mean - g_mean) + abs(g_mean - b_mean) + abs(r_mean - b_mean)
            return round(color_delta + r_std + g_std + b_std, 3)
    except Exception:
        return 0.0


def _thumbnail_color_count(path: Path) -> int:
    try:
        from PIL import Image

        with Image.open(path) as image:
            rgb = image.convert("RGB").resize((64, 64))
            colors = rgb.getcolors(maxcolors=4096)
            return len(colors) if colors is not None else 4097
    except Exception:
        return 0


def _asset_kind(path: Path, paper_dir: Path) -> str:
    parts = set(path.relative_to(paper_dir).parts[:-1])
    if "mineru_assets" in parts:
        return "mineru_extract"
    if "curated_crops" in parts:
        return "curated_crop"
    if "pages" in parts or path.name.lower().startswith("page-"):
        return "page_render"
    if "images" in parts or "extracted_images" in parts:
        return "embedded_image"
    if "eval_images" in parts:
        return "evaluation_image"
    return "image"


def _is_legacy_embedded_image(path: Path, paper_dir: Path) -> bool:
    parts = set(path.relative_to(paper_dir).parts[:-1])
    return bool({"images", "extracted_images"} & parts)


def _candidate_reason(asset: GalleryAsset) -> str | None:
    width = asset.width or 0
    height = asset.height or 0
    area = width * height
    max_side = max(width, height)
    min_side = max(1, min(width, height))
    aspect = max_side / min_side
    if asset.asset_kind == "evaluation_image":
        if asset.visual_score <= 5:
            return None
        return "evaluation_figure"
    if asset.asset_kind == "curated_crop":
        return "curated_page_crop"
    if asset.asset_kind == "mineru_extract":
        if area < 30_000 or max_side < 180:
            return None
        if asset.thumbnail_color_count < 40 and asset.visual_score <= 20:
            return None
        if aspect > 16:
            return None
        return "mineru_layout_extract"
    if asset.asset_kind != "embedded_image":
        return None
    if area < 100_000 or max_side < 450:
        return None
    if max_side <= 512 and area <= 120_000:
        return None
    if asset.thumbnail_color_count < 80:
        return None
    if aspect > 12:
        return None
    return "extracted_figure_or_table"


def _mark_figure_candidates(assets: list[GalleryAsset], exclusions: set[tuple[str, str]]) -> list[GalleryAsset]:
    marked = [
        replace(
            asset,
            is_figure_candidate=(asset.paper_slug, asset.filename) not in exclusions and bool(_candidate_reason(asset)),
            candidate_reason=_candidate_reason(asset) if (asset.paper_slug, asset.filename) not in exclusions else None,
        )
        for asset in assets
    ]
    preferred_papers = {
        asset.paper_slug
        for asset in marked
        if asset.is_figure_candidate and asset.asset_kind in {"curated_crop", "evaluation_image", "mineru_extract"}
    }
    marked = [
        replace(asset, is_figure_candidate=False, candidate_reason=None)
        if asset.asset_kind == "embedded_image" and asset.paper_slug in preferred_papers
        else asset
        for asset in marked
    ]
    grouped: dict[tuple[str, int | None, int | None], list[int]] = {}
    for index, asset in enumerate(marked):
        if asset.is_figure_candidate and asset.asset_kind == "embedded_image":
            grouped.setdefault((asset.paper_slug, asset.width, asset.height), []).append(index)
    keep_indices: set[int] = {index for index, asset in enumerate(marked) if asset.is_figure_candidate}
    for indices in grouped.values():
        if len(indices) < 2:
            continue
        top_score = max(marked[index].visual_score for index in indices)
        if top_score <= 5:
            continue
        for index in indices:
            if marked[index].visual_score < top_score * 0.25:
                keep_indices.discard(index)
    return [
        replace(asset, is_figure_candidate=index in keep_indices, candidate_reason=asset.candidate_reason if index in keep_indices else None)
        for index, asset in enumerate(marked)
    ]


def _asset_sort_key(asset: GalleryAsset) -> tuple[str, int, int, int, int, list[int | str]]:
    return (
        asset.paper_slug,
        0 if asset.is_figure_candidate else 1,
        ASSET_KIND_PRIORITY.get(asset.asset_kind, 99),
        asset.page_number if asset.page_number is not None else 999_999,
        asset.asset_index if asset.asset_index is not None else 999_999,
        _natural_key(asset.filename),
    )


def build_manifest(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_html: Path = DEFAULT_OUTPUT_HTML,
) -> dict[str, Any]:
    assets: list[GalleryAsset] = []
    exclusions = _read_manual_exclusions()
    if not input_dir.exists():
        return {
            "source_root": _project_relative(input_dir),
            "papers": [],
            "assets": [],
            "asset_count": 0,
        }
    for paper_dir in sorted((item for item in input_dir.iterdir() if item.is_dir()), key=lambda p: p.name):
        if paper_dir.name.endswith("_default_check"):
            continue
        source_pdf = _read_readme_source_pdf(paper_dir)
        paper_title = _title_from_source_pdf(source_pdf, paper_dir.name)
        mineru_metadata = _read_mineru_asset_metadata(paper_dir)
        image_paths = sorted(
            (
                path
                for path in paper_dir.rglob("*")
                if path.is_file()
                and path.suffix.lower() in IMAGE_SUFFIXES
                and "curated_crops_probe" not in path.parts
                and not _is_legacy_embedded_image(path, paper_dir)
                and (paper_dir.name, path.name) not in exclusions
            ),
            key=lambda p: _natural_key(p.as_posix()),
        )
        for path in image_paths:
            width, height = _image_dimensions(path)
            metadata = mineru_metadata.get(path.name, {})
            assets.append(
                GalleryAsset(
                    paper_slug=paper_dir.name,
                    paper_title=paper_title,
                    asset_kind=_asset_kind(path, paper_dir),
                    path=_project_relative(path),
                    relative_to_html=_html_relative(path, output_html),
                    filename=path.name,
                    page_number=_page_number(path),
                    asset_index=_asset_index(path),
                    width=width,
                    height=height,
                    source_pdf=source_pdf,
                    caption=metadata.get("caption") if isinstance(metadata.get("caption"), str) else None,
                    visual_score=_image_visual_score(path),
                    thumbnail_color_count=_thumbnail_color_count(path),
                    is_figure_candidate=False,
                    candidate_reason=None,
                )
            )
    assets = _mark_figure_candidates(assets, exclusions)
    assets.sort(key=_asset_sort_key)
    paper_counts: dict[str, dict[str, Any]] = {}
    for asset in assets:
        entry = paper_counts.setdefault(
            asset.paper_slug,
            {
                "paper_slug": asset.paper_slug,
                "paper_title": asset.paper_title,
                "source_pdf": asset.source_pdf,
                "asset_count": 0,
                "figure_candidate_count": 0,
                "asset_kinds": {},
            },
        )
        entry["asset_count"] += 1
        if asset.is_figure_candidate:
            entry["figure_candidate_count"] += 1
        entry["asset_kinds"][asset.asset_kind] = entry["asset_kinds"].get(asset.asset_kind, 0) + 1
    figure_candidate_count = sum(1 for asset in assets if asset.is_figure_candidate)
    return {
        "source_root": _project_relative(input_dir),
        "asset_count": len(assets),
        "figure_candidate_count": figure_candidate_count,
        "hidden_artifact_count": len(assets) - figure_candidate_count,
        "papers": sorted(paper_counts.values(), key=lambda item: item["paper_slug"]),
        "assets": [asdict(asset) for asset in assets],
        "workflow": {
            "refresh_command": "uv run python scripts/build_paper_figure_gallery.py",
            "paper_intake_command": "scripts/inspect_paper_pdf.sh <paper.pdf> [slug]",
        },
    }


def _json_for_script(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def render_html(manifest: dict[str, Any]) -> str:
    paper_options = "\n".join(
        f'<option value="{html.escape(paper["paper_slug"])}">{html.escape(paper["paper_title"])} ({paper["asset_count"]})</option>'
        for paper in manifest["papers"]
    )
    manifest_json = _json_for_script(manifest)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Paper Figure Comparison</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --surface: #ffffff;
      --ink: #1d2430;
      --muted: #657184;
      --line: #d8dee8;
      --blue: #2f6fed;
      --teal: #168a7a;
      --amber: #b7791f;
      --red: #c2413b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
      line-height: 1.45;
    }}
    header {{
      position: sticky;
      top: 0;
      z-index: 10;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(12px);
    }}
    .topbar {{
      display: grid;
      grid-template-columns: minmax(260px, 1fr) auto;
      gap: 18px;
      align-items: center;
      padding: 16px 22px;
    }}
    h1 {{
      margin: 0;
      font-size: 20px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin-top: 4px;
      color: var(--muted);
      font-size: 13px;
    }}
    .stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }}
    .stat {{
      border: 1px solid var(--line);
      background: #f9fafc;
      padding: 6px 10px;
      border-radius: 7px;
      color: var(--muted);
      white-space: nowrap;
    }}
    .stat strong {{ color: var(--ink); }}
    .controls {{
      display: grid;
      grid-template-columns: minmax(260px, 1.4fr) minmax(180px, 0.8fr) minmax(170px, 0.7fr) auto auto;
      gap: 10px;
      padding: 0 22px 16px;
    }}
    input, select, button {{
      width: 100%;
      height: 38px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #fff;
      color: var(--ink);
      padding: 0 10px;
      font: inherit;
    }}
    button {{
      cursor: pointer;
      background: #eef4ff;
      border-color: #c5d7ff;
      color: #174ea6;
      font-weight: 600;
      white-space: nowrap;
    }}
    main {{ padding: 18px 22px 40px; }}
    .mode-note {{
      margin: 0 0 16px;
      color: var(--muted);
      font-size: 13px;
    }}
    .paper-summary {{
      margin-bottom: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
    }}
    .paper-summary summary {{
      cursor: pointer;
      padding: 10px 12px;
      color: var(--muted);
      font-weight: 650;
    }}
    .paper-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 12px;
      padding: 0 12px 12px;
    }}
    .paper-card {{
      border: 1px solid var(--line);
      border-left: 6px solid var(--teal);
      background: var(--surface);
      border-radius: 8px;
      padding: 12px;
    }}
    .paper-card h2 {{
      margin: 0 0 6px;
      font-size: 14px;
      line-height: 1.25;
    }}
    .paper-meta {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      color: var(--muted);
      font-size: 12px;
    }}
    .gallery {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 18px;
    }}
    .asset {{
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      min-height: 260px;
      display: flex;
      flex-direction: column;
    }}
    .asset img {{
      width: 100%;
      height: auto;
      max-height: 420px;
      object-fit: contain;
      border-bottom: 1px solid var(--line);
      background: #fff;
      cursor: zoom-in;
    }}
    .asset-body {{ padding: 10px; }}
    .asset-title {{
      font-weight: 650;
      font-size: 13px;
      margin-bottom: 4px;
    }}
    .asset-detail {{
      color: var(--muted);
      font-size: 12px;
      word-break: break-word;
    }}
    .kind {{
      display: inline-block;
      margin-top: 8px;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 650;
      background: #edf8f6;
      color: #106f62;
    }}
    .kind.page_render {{ background: #eef4ff; color: #2457b8; }}
    .kind.evaluation_image {{ background: #fff7ed; color: #a65f00; }}
    .kind.curated_crop {{ background: #f4ecff; color: #6b35b8; }}
    .kind.mineru_extract {{ background: #eef7ff; color: #1d5d8f; }}
    .kind.embedded_image {{ background: #edf8f6; color: #106f62; }}
    .candidate {{
      display: inline-block;
      margin-top: 8px;
      margin-left: 6px;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 650;
      background: #f0f7ff;
      color: #225aa8;
    }}
    dialog {{
      width: min(92vw, 1200px);
      border: none;
      border-radius: 10px;
      padding: 0;
      box-shadow: 0 20px 80px rgba(0,0,0,0.35);
    }}
    dialog::backdrop {{ background: rgba(14, 20, 31, 0.62); }}
    .modal-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
    }}
    .modal-head h3 {{ margin: 0; font-size: 15px; }}
    .modal-head button {{ width: auto; }}
    .modal-body {{ padding: 14px; background: #f7f8fb; }}
    .modal-body img {{
      display: block;
      max-width: 100%;
      max-height: 78vh;
      margin: 0 auto;
      background: white;
      border: 1px solid var(--line);
    }}
    @media (max-width: 860px) {{
      .topbar {{ grid-template-columns: 1fr; }}
      .stats {{ justify-content: flex-start; }}
      .controls {{ grid-template-columns: 1fr; }}
      main {{ padding: 14px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <div>
        <h1>Paper Figure Comparison</h1>
        <div class="subtitle">Default view shows only extracted figure/table candidates from inspected papers.</div>
      </div>
      <div class="stats">
        <div class="stat"><strong id="paperCount">0</strong> papers</div>
        <div class="stat"><strong id="candidateCount">0</strong> figures</div>
        <div class="stat"><strong id="rawCount">0</strong> raw assets</div>
        <div class="stat"><strong id="visibleCount">0</strong> visible</div>
      </div>
    </div>
    <div class="controls">
      <input id="search" placeholder="Search paper, filename, figure type..." />
      <select id="paperFilter">
        <option value="">All papers</option>
        {paper_options}
      </select>
      <select id="kindFilter">
        <option value="">All figure candidates</option>
        <option value="curated_crop">Curated crops</option>
        <option value="mineru_extract">MinerU extracts</option>
        <option value="embedded_image">Extracted figures/tables</option>
        <option value="evaluation_image">Evaluation figures</option>
        <option value="page_render">Raw page renders</option>
      </select>
      <button id="candidatesOnly">Figures</button>
      <button id="allAssets">All raw</button>
    </div>
  </header>
  <main>
    <p class="mode-note" id="modeNote"></p>
    <details class="paper-summary">
      <summary>Paper coverage and extracted asset counts</summary>
      <section id="papers" class="paper-strip"></section>
    </details>
    <section id="gallery" class="gallery"></section>
  </main>
  <dialog id="preview">
    <div class="modal-head">
      <h3 id="previewTitle"></h3>
      <button id="closePreview">Close</button>
    </div>
    <div class="modal-body">
      <img id="previewImage" alt="" />
    </div>
  </dialog>
  <script>
    const manifest = {manifest_json};
    const state = {{ search: "", paper: "", kind: "", onlyFigures: true }};
    const gallery = document.getElementById("gallery");
    const papers = document.getElementById("papers");
    const preview = document.getElementById("preview");
    const previewImage = document.getElementById("previewImage");
    const previewTitle = document.getElementById("previewTitle");

    function textFor(asset) {{
      return [
        asset.paper_slug,
        asset.paper_title,
        asset.asset_kind,
        asset.candidate_reason || "",
        asset.caption || "",
        asset.filename,
        asset.page_number === null ? "" : `page ${{asset.page_number}}`,
        asset.path
      ].join(" ").toLowerCase();
    }}

    function filteredAssets() {{
      const needle = state.search.trim().toLowerCase();
      return manifest.assets.filter(asset => {{
        if (state.paper && asset.paper_slug !== state.paper) return false;
        if (state.onlyFigures && !asset.is_figure_candidate) return false;
        if (state.kind && asset.asset_kind !== state.kind) return false;
        if (needle && !textFor(asset).includes(needle)) return false;
        return true;
      }});
    }}

    function renderPapers() {{
      papers.innerHTML = manifest.papers.map(paper => {{
        const kinds = Object.entries(paper.asset_kinds)
          .map(([kind, count]) => `${{kind}}: ${{count}}`)
          .join(" · ");
        return `<article class="paper-card">
          <h2>${{escapeHtml(paper.paper_title)}}</h2>
          <div class="paper-meta">
            <span>${{escapeHtml(paper.paper_slug)}}</span>
            <span>${{paper.figure_candidate_count}} figures</span>
            <span>${{paper.asset_count}} raw assets</span>
            <span>${{escapeHtml(kinds)}}</span>
          </div>
        </article>`;
      }}).join("");
    }}

    function renderGallery() {{
      const assets = filteredAssets();
      document.getElementById("paperCount").textContent = manifest.papers.length;
      document.getElementById("candidateCount").textContent = manifest.figure_candidate_count;
      document.getElementById("rawCount").textContent = manifest.asset_count;
      document.getElementById("visibleCount").textContent = assets.length;
      document.getElementById("modeNote").textContent = state.onlyFigures
        ? "Showing figure/table candidates only. Small PDF icons, masks, and full page renders are hidden."
        : "Showing all extracted raw assets, including page renders and likely PDF artifacts.";
      gallery.innerHTML = assets.map((asset, index) => {{
        const page = asset.page_number === null ? "" : ` · page ${{asset.page_number}}`;
        const size = asset.width && asset.height ? ` · ${{asset.width}}×${{asset.height}}` : "";
        const candidate = asset.is_figure_candidate ? `<span class="candidate">${{escapeHtml(asset.candidate_reason)}}</span>` : "";
        const caption = asset.caption ? `<div class="asset-detail">${{escapeHtml(asset.caption)}}</div>` : "";
        return `<article class="asset">
          <img loading="lazy" src="${{escapeAttr(asset.relative_to_html)}}" alt="${{escapeAttr(asset.filename)}}" data-index="${{index}}" />
          <div class="asset-body">
            <div class="asset-title">${{escapeHtml(asset.paper_title)}}</div>
            <div class="asset-detail">${{escapeHtml(asset.filename)}}${{page}}${{size}}</div>
            ${{caption}}
            <div class="asset-detail">${{escapeHtml(asset.path)}}</div>
            <span class="kind ${{escapeAttr(asset.asset_kind)}}">${{escapeHtml(asset.asset_kind)}}</span>${{candidate}}
          </div>
        </article>`;
      }}).join("");
      gallery.querySelectorAll("img").forEach((img, index) => {{
        img.addEventListener("click", () => openPreview(assets[index]));
      }});
    }}

    function openPreview(asset) {{
      previewTitle.textContent = `${{asset.paper_title}} · ${{asset.filename}}`;
      previewImage.src = asset.relative_to_html;
      previewImage.alt = asset.filename;
      preview.showModal();
    }}

    function escapeHtml(value) {{
      return String(value ?? "").replace(/[&<>"']/g, ch => ({{ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\\"": "&quot;", "'": "&#39;" }}[ch]));
    }}
    function escapeAttr(value) {{ return escapeHtml(value); }}

    document.getElementById("search").addEventListener("input", event => {{
      state.search = event.target.value;
      renderGallery();
    }});
    document.getElementById("paperFilter").addEventListener("change", event => {{
      state.paper = event.target.value;
      renderGallery();
    }});
    document.getElementById("kindFilter").addEventListener("change", event => {{
      state.kind = event.target.value;
      if (state.kind === "page_render") state.onlyFigures = false;
      renderGallery();
    }});
    document.getElementById("candidatesOnly").addEventListener("click", () => {{
      state.onlyFigures = true;
      state.kind = "";
      document.getElementById("kindFilter").value = "";
      renderGallery();
    }});
    document.getElementById("allAssets").addEventListener("click", () => {{
      state.onlyFigures = false;
      state.kind = "";
      document.getElementById("kindFilter").value = "";
      renderGallery();
    }});
    document.getElementById("closePreview").addEventListener("click", () => preview.close());

    renderPapers();
    renderGallery();
  </script>
</body>
</html>
"""


def write_gallery(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_html: Path = DEFAULT_OUTPUT_HTML,
    output_manifest: Path = DEFAULT_OUTPUT_MANIFEST,
) -> tuple[Path, Path, dict[str, Any]]:
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    _write_curated_crops(input_dir=input_dir)
    manifest = build_manifest(input_dir=input_dir, output_html=output_html)
    output_manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    output_html.write_text(render_html(manifest), encoding="utf-8")
    return output_html, output_manifest, manifest


def main() -> int:
    html_path, manifest_path, manifest = write_gallery()
    print(f"Wrote {html_path.relative_to(ROOT)}")
    print(f"Wrote {manifest_path.relative_to(ROOT)}")
    print(f"Papers: {len(manifest['papers'])}")
    print(f"Assets: {manifest['asset_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
