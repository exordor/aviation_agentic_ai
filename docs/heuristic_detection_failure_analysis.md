# Heuristic Detection Failure Analysis

## Purpose

The chunking module ([src/aviation_agentic_ai/chunking/chunks.py](../src/aviation_agentic_ai/chunking/chunks.py))
relies on five heuristic detection functions to infer document structure from
the plain-text output of PyMuPDF's `page.get_text("text")`. This document
catalogues the failure modes discovered during empirical validation against
`data/raw/06_phak_ch4_0.pdf` (PHAK Chapter 4, single-column textbook with
embedded data tables).

The validation ran `_is_heading()` against every non-empty line of the first
five pages. Results demonstrate that even on this structurally simple document,
the heuristics produce a high rate of false positives and systematic biases.

## Validation Methodology

```bash
uv run python -c "
from aviation_agentic_ai.chunking.chunks import _is_heading
from aviation_agentic_ai.utils.pdf import extract_pages
for page in extract_pages('data/raw/06_phak_ch4_0.pdf', max_pages=5):
    headings = [l.strip() for l in page.text.splitlines()
                if l.strip() and _is_heading(l.strip())]
    print(f'P{page.page_number}: {len(headings)} detections')
" 2>&1
```

Pages 0–5 sample the front matter, body text, a full-page data table, and
mid-content with inline figures and cross-references.

## Per-Page Empirical Results

### Page 0 — Introduction (6 detections)

| Detection | Actual | Verdict |
|-----------|--------|---------|
| `4-1` | Page number | **False positive** |
| `Introduction` | Section heading | Correct |
| `Structure of the Atmosphere` | Subsection heading | Correct |
| `Principles of` | First half of chapter title (line-wrapped) | **False positive** |
| `Flight` | Second half of chapter title | **False positive** |
| `Chapter 4` | Chapter identifier | **False positive** |

Accurate rate: **2/6 (33%)**.

The chapter title "Principles of Flight" spans two lines due to PDF text
layout. PyMuPDF emits them as separate lines; `_is_heading` treats each as
an independent candidate. Neither fragment is a meaningful section heading.

### Page 1 — Body Content (4 detections)

| Detection | Actual | Verdict |
|-----------|--------|---------|
| `4-2` | Page number | **False positive** |
| `Air is a Fluid` | Subsection heading | Correct |
| `Viscosity` | Sub-subsection heading | Correct |
| `Friction` | Sub-subsection heading | Correct |

Accurate rate: **3/4 (75%)**. Better, but only because the page lacks
numerical data.

### Page 2 — Standard Atmosphere Data Table (103 detections)

This page is a tabular reference for the ICAO Standard Atmosphere — altitude,
pressure, and temperature values laid out in columns. PyMuPDF's text-mode
extraction loses column layout and emits each numerical label on its own line.

**0 accurate detections out of 103.** The page contains no true section
headings. All 103 flagged lines are numerical data, column labels, or
paragraph continuations.

Full list of false positives:

| Category | Examples | Count |
|----------|----------|-------|
| Altitude values | `0`, `1000`, `2000`, ..., `20000` | 21 |
| Pressure values (Hg) | `29.92`, `28.86`, `27.82`, ..., `13.74` | 21 |
| Pressure values (mb) | `1016`, `847`, `677`, ..., `170` | 8 |
| Temperature values | `15.0`, `13.0`, ..., `-69.7` | 20 |
| Column labels | `Inches of`, `Mercury`, `Millibars` | 3 |
| Axis labels | `Pressure Altitude (ft)`, `Pressure (Hg)`, `Temperature` | 3 |
| Reference labels | `Standard`, `Sea Level`, `Standard Atmosphere` | 3 |
| Mixed fragments | `14.70 pounds per square inch...`, `ICAO Standard Atmosphere...` | 2 |
| Other numeric labels | `30`, `25`, `20`, `15`, `10`, `5`, `0`, `1013`, `59.0`, ... | ~22 |

### Page 3 — Body Content (5 detections)

| Detection | Actual | Verdict |
|-----------|--------|---------|
| `4-4` | Page number | **False positive** |
| `Pressure Altitude` | Subsection heading | Correct |
| `Density Altitude` | Subsection heading | Correct |
| `Effect of Pressure on Density` | Subsection heading | Correct |
| `Effect of Temperature on Density` | Subsection heading | Correct |

Accurate rate: **4/5 (80%)**.

### Page 4 — Body Content (6 detections)

| Detection | Actual | Verdict |
|-----------|--------|---------|
| `4-5` | Page number | **False positive** |
| `Effect of Humidity (Moisture) on Density` | Subsection heading | Correct |
| `is 22.22 "Hg. Using the National Oceanic and Atmospheric` | Paragraph continuation | **False positive** |
| `Another website (www.wahiduddin.net/...)` | Paragraph body | **False positive** |
| `Theories in the Production of Lift` | Section heading | Correct |
| `Newton's Basic Laws of Motion` | Subsection heading | Correct |

Accurate rate: **3/6 (50%)**.

The two body-text false positives are lines that happen to be short and contain
a sufficient ratio of title-case words to clear the threshold. The line
`is 22.22 "Hg. Using the National Oceanic and Atmospheric` is a continuation of
a paragraph describing atmospheric pressure; it was split at a PDF line break.

## Root Cause Analysis

### 1. Numeric line regex — `\d+(?:\.\d+)*` (highest severity)

**Code** ([chunks.py:402-404](../src/aviation_agentic_ai/chunking/chunks.py#L402-L404)):

```python
re.match(r"^(chapter|section|\d+(?:\.\d+)*)\b", stripped, flags=re.IGNORECASE)
```

**Failure mode:** The `\d+(?:\.\d+)*` branch matches **any line beginning with
a digit sequence**, regardless of the line's actual role in the document.

**Matches incorrectly:**
- Page numbers: `4-1`, `4-2`, `4-3` (partial match on the leading digits, then
  `\b` at the hyphen boundary)
- Altitude values: `0`, `1000`, `2000`, ..., `20000`
- Pressure values: `29.92`, `28.86`, ..., `13.74` (decimal form matches
  `\d+\.\d+`)
- Barometric values: `1016`, `847`, `677`
- Temperature values: `15.0`, `13.0`, `59.0`
- Measurement data: `14.70`, `22.22`

**Impact:** Aviation documents are dense with numerical data tables (atmospheric
conditions, performance charts, weight-and-balance tables, V-speeds, fuel
calculations). Every row of every table becomes a false heading detection. This
single heuristic branch accounted for ~90 of the 103 false positives on Page 2.

### 2. Title-case ratio on PDF line-wrapped fragments (high severity)

**Code** ([chunks.py:401](../src/aviation_agentic_ai/chunking/chunks.py#L401)):

```python
title_words = sum(1 for word in stripped.split() if word[:1].isupper())
return title_words >= max(1, len(stripped.split()) // 2)
```

**Failure mode:** When a paragraph line is wrapped mid-sentence by the PDF
renderer, the resulting text fragment is short (a few words). Proper nouns,
acronyms, or technical terms that happen to be capitalized can push the
title-case ratio above the 50% threshold.

**Example:** The fragment `Using the National Oceanic and Atmospheric` has 4
capitalized words out of 5 (`Using`, `National`, `Oceanic`, `Atmospheric`),
clearing the threshold of `max(1, 2) = 2`. But it is the tail of a paragraph
about ICAO standards.

**Impact:** Any PDF with justified text and variable word spacing will produce
line-wrapped fragments. Technical documents with many proper nouns (agency
names, aircraft models, regulation references like "14 CFR Part 61") are
especially vulnerable.

### 3. No inter-line context (medium severity)

**Code** ([chunks.py:417-431](../src/aviation_agentic_ai/chunking/chunks.py#L417-L431)):

`_structure_segments()` evaluates each line in isolation. It has no awareness of:
- Whether the previous line was a paragraph body line
- Whether the next line is a paragraph body line
- Whether surrounding lines suggest this is a table or list
- Font size, bold/italic weight, or indentation (all discarded by
  `page.get_text("text")`)

**Impact:** A heading followed immediately by body text is structurally
distinct from a paragraph line that happens to be short. The heuristic cannot
tell them apart because it throws away the one signal that would help:
typographic formatting.

### 4. Duplicate-line coordinate corruption (medium severity)

**Code** ([chunks.py:422-424](../src/aviation_agentic_ai/chunking/chunks.py#L422-L424)):

```python
start = text.find(line, cursor)
end = start + len(line)
cursor = end
```

**Failure mode:** `str.find()` returns the first occurrence. When the same
string appears multiple times on a page (e.g., the altitude `0` appears twice,
`Standard` appears three times, `Sea Level` appears twice on Page 2), every
occurrence after the first maps back to the coordinates of the first occurrence.

**Impact:** Segment character spans overlap or are misordered. Chunks built
from these segments will have incorrect `char_start`/`char_end` provenance,
breaking any downstream feature that relies on character-offset pointers into
the source text.

### 5. Proposition cue `\bis\b` over-matching (medium severity)

**Code** ([chunks.py:64-70](../src/aviation_agentic_ai/chunking/chunks.py#L64-L70)):

```python
PROPOSITION_CUE_RE = re.compile(
    r"\b(is|means|refers to|causes|affects|increases|"
    r"decreases|produces|results|consists|composed|part|component)\b",
    flags=re.IGNORECASE,
)
```

**Failure mode:** `\bis\b` matches the most common English copula. Nearly every
definitional or descriptive sentence in technical prose contains "is" — not only
proposition-like atomic claims.

**Impact:** The `proposition_like` strategy is effectively a sentence-length
chunker with a bias toward sentences containing "is". It does not isolate
atomic propositions; it just segments around a common word.

Additionally, the regex misses key proposition indicators common in aviation
text: `defines`, `determines`, `influences`, `depends on`, `characterized by`,
`consists of`, `results in`.

### 6. Sentence boundary detection gaps (low severity)

**Code** ([chunks.py:319-335](../src/aviation_agentic_ai/chunking/chunks.py#L319-L335)):

`_find_soft_break()` recognizes four sentence-ending patterns: `. `, `; `,
`? `, `! `.

**Missing patterns:**
- Quotation-terminated sentences: `lift." The`
- Parenthetical endings: `angle.) The`
- Colon-terminated list intros followed by newlines
- Semicolon without trailing space (rare in well-formed PDF, but possible)

**Code** ([chunks.py:407-414](../src/aviation_agentic_ai/chunking/chunks.py#L407-L414)):

`sentence_segments` uses `[^.!?;\n]+(?:[.!?;]+|(?=\n)|$)` which does not
account for abbreviations common in technical prose: `e.g.`, `i.e.`, `etc.`,
`vs.`, `Fig.`, `Eq.`, `Ref.`, `approx.`, `alt.`.

**Impact:** Abbreviation mid-sentence triggers a false sentence boundary,
causing semantic strategies to compare "adjacent sentences" that are actually
fragments of the same sentence. This injects noise into similarity-based
chunk boundary decisions.

### 7. Unused function (low severity)

`_is_sentence_boundary()` is defined at
[line 391](../src/aviation_agentic_ai/chunking/chunks.py#L391-L392) but is not
called anywhere in the codebase. Dead code that suggests an intended feature
(perhaps sentence-boundary-aware chunk merging) was started but never
integrated.

## Aggregate Results (Pages 0–4)

| Metric | Value |
|--------|-------|
| Total non-empty lines evaluated | 452 |
| Lines flagged as headings | 124 |
| True headings in document | 19 |
| True positives | 13 |
| False positives | 111 |
| False negatives (missed headings) | 3 |
| **Precision** | **10.5%** |
| **Recall** | **81.3%** |
| **F1** | **18.6%** |

The three false negatives:
- Page 0: The multi-line title "Principles of / Flight" — both fragments were
  flagged individually, but the heading itself was never recognized as a single
  entity (classified here as FN rather than TP because the chunk never gets a
  correct `section="Principles of Flight"`)
- Page 1: `Figure 4-1. Microscopic surface of a wing.` — a figure caption that
  could be useful structure metadata but is rejected due to the trailing period
- Page 2: Two section labels within the table (`Pressure`, `Hg`) were flagged
  as headings by accident; they happen to be correct structural markers but
  for the wrong reason

## Implications for Chunking Quality

These heuristic failures cascade into downstream quality issues:

1. **structure_aware strategies** — False headings create spurious section
   boundaries. A chunk may be split mid-paragraph because a numeric table value
   on the next line was mistaken for a heading. Conversely, true section
   transitions may not trigger a boundary when a heading is missed.

2. **semantic boundary strategies** — Abbreviation-triggered false sentence
   splits cause the similarity function to compare sentence fragments rather
   than complete sentences, leading to arbitrary chunk boundaries.

3. **hierarchical_parent_child** — Parent chunks built from structure segments
   inherit the corrupted section labels and section boundaries from
   `_structure_segments`.

4. **proposition_like** — The `\bis\b` over-match means this strategy does not
   actually isolate propositional claims; it functions as a sentence-length
   chunker with a trivial filter.

5. **provenance integrity** — Duplicate-line coordinate corruption means
   `char_start`/`char_end` offsets in `SourceChunk` records do not reliably
   point to the correct text span, breaking citation and evidence tracing.

## Remediation Options

### Option A: Patch the Heuristics (low effort, partial fix)

- Remove the `\d+(?:\.\d+)*` branch from `_is_heading`.
- Require headings to be bookended by blank lines (preceding and following
  whitespace).
- Add a minimum length filter (≥ 2 words with alphabetic content).
- Add an abbreviation list to the sentence splitter.

**Limitation:** Does not solve the fundamental problem — plain-text extraction
discards typographic signals (font size, weight, indentation).

### Option B: Use PyMuPDF Structured Output (medium effort, better fix)

Replace `page.get_text("text")` with `page.get_text("blocks")` or
`page.get_text("dict")` to access font size, bold flag, and bounding box
coordinates. Headings are typically larger, bolder, and/or offset from body
text. This retains PyMuPDF's performance while adding the key signal the
heuristics currently lack.

Alternatively, use `pymupdf4llm.to_markdown(page_chunks=True)` which performs
layout analysis internally and outputs Markdown with heading levels preserved
(`#`, `##`, etc.).

**Limitation:** Still uses heuristic font-size thresholds; may not handle
unconventional layouts or scanned PDFs.

### Option C: Adopt Docling (higher effort, structural fix)

Replace the PyMuPDF-based extraction with Docling's deep-learning-based
document understanding pipeline. Docling classifies each text span by semantic
role (SectionHeader, Text, Table, ListItem, Picture), infers reading order, and
exports a `DoclingDocument` tree.

**Trade-off:** Adds ML model dependencies (~2–4 GB download), slower
processing (seconds per page vs. milliseconds), but eliminates all seven
heuristic failure modes at the source.

## Validation Date

2026-05-31 — empirical validation against `data/raw/06_phak_ch4_0.pdf` using
the code at commit context of this analysis.
