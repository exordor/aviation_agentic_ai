from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF_ARTIFACT_ROOT = ROOT / "tmp" / "pdfs"


def _caption_text(item: dict[str, Any]) -> str | None:
    captions = item.get("table_caption") or item.get("image_caption") or []
    if isinstance(captions, str):
        return captions
    if isinstance(captions, list):
        parts = []
        for caption in captions:
            if isinstance(caption, str):
                parts.append(caption)
            elif isinstance(caption, dict) and isinstance(caption.get("content"), str):
                parts.append(caption["content"])
        return " ".join(part.strip() for part in parts if part.strip()) or None
    return None


def _safe_name(index: int, item: dict[str, Any], source_path: Path) -> str:
    item_type = str(item.get("type") or "asset").lower()
    caption = _caption_text(item) or source_path.stem
    stem = "".join(char.lower() if char.isalnum() else "_" for char in caption)
    stem = "_".join(part for part in stem.split("_") if part)[:80]
    return f"{index:03d}_{item_type}_{stem or source_path.stem}{source_path.suffix.lower()}"


def import_mineru_assets(
    *,
    mineru_content_list: Path,
    paper_slug: str,
    pdf_artifact_root: Path = DEFAULT_PDF_ARTIFACT_ROOT,
) -> Path:
    content = json.loads(mineru_content_list.read_text(encoding="utf-8"))
    source_root = mineru_content_list.parent
    out_dir = pdf_artifact_root / paper_slug / "mineru_assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for index, item in enumerate(content):
        if item.get("type") not in {"table", "image"}:
            continue
        img_path = item.get("img_path")
        if not isinstance(img_path, str):
            continue
        source_path = source_root / img_path
        if not source_path.exists():
            continue
        filename = _safe_name(index, item, source_path)
        target_path = out_dir / filename
        shutil.copy2(source_path, target_path)
        manifest.append(
            {
                "filename": filename,
                "source_path": source_path.as_posix(),
                "type": item.get("type"),
                "caption": _caption_text(item),
                "bbox": item.get("bbox"),
                "page_idx": item.get("page_idx"),
            }
        )
    manifest_path = out_dir / "mineru_assets_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Import MinerU-extracted table/figure assets into the paper gallery.")
    parser.add_argument("content_list", type=Path, help="Path to MinerU *_content_list.json output.")
    parser.add_argument("paper_slug", help="Existing tmp/pdfs/<paper_slug> directory.")
    args = parser.parse_args()
    manifest_path = import_mineru_assets(mineru_content_list=args.content_list, paper_slug=args.paper_slug)
    print(f"Wrote {manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
