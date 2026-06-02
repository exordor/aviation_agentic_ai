#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/inspect_paper_pdf.sh <paper.pdf> [slug]

Extracts a local paper PDF into ignored tmp artifacts for evidence-first review:
metadata, layout text, figure/table mentions, rendered page PNGs, and embedded
images.

Examples:
  scripts/inspect_paper_pdf.sh data/papers/example.pdf
  scripts/inspect_paper_pdf.sh data/papers/example.pdf example_paper
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage >&2
  exit 2
fi

pdf_path="$1"
if [[ ! -f "$pdf_path" ]]; then
  echo "PDF not found: $pdf_path" >&2
  exit 1
fi

for tool in pdfinfo pdftotext pdftoppm pdfimages; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing required Poppler tool: $tool" >&2
    echo "Install on macOS with: brew install poppler" >&2
    exit 1
  fi
done

slug="${2:-}"
if [[ -z "$slug" ]]; then
  base="$(basename "$pdf_path")"
  slug="${base%.*}"
  slug="$(printf '%s' "$slug" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/_/g; s/^_+|_+$//g')"
fi

out_dir="tmp/pdfs/$slug"
pages_dir="$out_dir/pages"
images_dir="$out_dir/images"
mkdir -p "$pages_dir" "$images_dir"

pdfinfo "$pdf_path" > "$out_dir/metadata.txt"
pdftotext -layout "$pdf_path" "$out_dir/extracted.txt"
pdfimages -list "$pdf_path" > "$out_dir/image_inventory.txt"
pdfimages -png "$pdf_path" "$images_dir/image" >/dev/null 2>&1 || true
pdftoppm -png -r 110 "$pdf_path" "$pages_dir/page" >/dev/null

if command -v rg >/dev/null 2>&1; then
  rg -n "Figure|Fig\\.|Table|Supplementary|BLEU|ROUGE|BERT|precision|recall|F1|metric|p-value|significance" \
    "$out_dir/extracted.txt" > "$out_dir/figure_table_metric_mentions.txt" || true
else
  grep -En "Figure|Fig\\.|Table|Supplementary|BLEU|ROUGE|BERT|precision|recall|F1|metric|p-value|significance" \
    "$out_dir/extracted.txt" > "$out_dir/figure_table_metric_mentions.txt" || true
fi

page_count="$(find "$pages_dir" -type f -name 'page-*.png' | wc -l | tr -d ' ')"
image_count="$(find "$images_dir" -type f -name '*.png' | wc -l | tr -d ' ')"

cat > "$out_dir/README.md" <<EOF
# PDF Inspection Artifacts

- Source PDF: \`$pdf_path\`
- Slug: \`$slug\`
- Rendered pages: $page_count
- Extracted embedded images: $image_count

Key files:

- \`metadata.txt\`: PDF metadata from \`pdfinfo\`
- \`extracted.txt\`: layout-preserving text from \`pdftotext -layout\`
- \`figure_table_metric_mentions.txt\`: quick anchors for figure/table/metric review
- \`image_inventory.txt\`: embedded image inventory from \`pdfimages -list\`
- \`pages/\`: page renderings for visual inspection
- \`images/\`: extracted embedded images when available

These artifacts are intentionally under \`tmp/\` and should not be committed.
Curated analysis belongs in \`reports/stages/\`.
EOF

echo "PDF inspection artifacts written to $out_dir"
echo "Rendered pages: $page_count"
echo "Extracted images: $image_count"
