# PDF Extraction Backend Policy

## Decision

The project now treats PDF extraction as a backend choice, not as a single
PyMuPDF text step.

- `hybrid_docling_pymupdf` is the candidate default for structure-aware PDF
  chunking.
- `docling_structure` is the structural authority for section headers, tables,
  lists, hierarchy, and reading order.
- `pymupdf_text_legacy` remains a fast baseline and text-fidelity reference, but
  its heading heuristic is not a structural authority.
- `recursive_medium` and `fixed_large` remain robust non-structure fallbacks when
  Docling is unavailable.

## Why PyMuPDF Heuristics Are Demoted

PyMuPDF plain-text extraction is fast and usually preserves useful page-level
text, but PDF line breaks and tables can make title-case or short-line heading
heuristics unreliable. The latest comparison showed many false heading
candidates from table content. That path is retained for historical
comparability only.

## Why Docling Is Preferred For Structure

Docling emits document element labels such as section headers, tables, and list
items. Those labels are a better structural signal than text-line heuristics, so
structure-aware chunking should use Docling labels when they are available.

## Why Docling Is Not Used Alone

Docling can introduce merged words and OCR-like boundary artifacts. PyMuPDF is
therefore kept as the text-fidelity reference. The hybrid backend repairs only
when the PyMuPDF page text clearly contains the spaced or corrected form.

## Fallback Policy

Use this order for PDF chunking experiments:

1. `hybrid_docling_pymupdf` for structure-aware chunking when Docling conversion
   succeeds.
2. `docling_structure` only when studying Docling structure without PyMuPDF text
   correction.
3. `recursive_medium` or `fixed_large` when Docling is unavailable.
4. `pymupdf_text_legacy` only for baseline comparison or historical report
   reproducibility.

## Claim Policy

Do not claim a universal best PDF backend. Report structure quality, text
artifact repair, runtime, and downstream retrieval separately. Do not claim
human review, expert certification, or operational readiness from this backend
comparison.
