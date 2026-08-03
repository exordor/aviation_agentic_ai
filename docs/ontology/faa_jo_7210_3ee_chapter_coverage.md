# FAA JO 7210.3EE chapter coverage matrix

This matrix defines the semantic boundary for grounding FAA Order JO 7210.3EE
(`2025-02-20`) with ATMONTO. It covers all seven parts, 21 chapters, and six
appendices. The machine-readable source is
`data/ontology/curated/faa_jo_7210_3ee_chapter_coverage_v1.json`.

## What the matrix means

The matrix is a coverage contract, not a claim that the PDF has already been
fully converted into an ABox. A chapter may contain concepts that are useful
for retrieval but have no publishable semantic facts yet.

| Status | Meaning |
| --- | --- |
| `active` | The current profile or adapter has a class/property path that can reach the publication boundary. |
| `planned` | The concept is aligned to ATMONTO or a FAA extension, but is not yet in the active publication path. |
| `unsupported` | Keep the material as PDF chunks and retrieval evidence; do not publish it as a semantic KG object. |

`active` is intentionally conservative. Chapter 18 is the only active chapter
in this first matrix. Its 26 sections and 159 numbered paragraphs are now in
the configured extraction scope; the other chapters remain planned or
unsupported rather than being implied by the document-level adapter.

## Coverage summary

| Scope | Count | Current status |
| --- | ---: | --- |
| Parts | 7 | registered |
| Chapters | 21 | 1 active, 20 planned |
| Appendices | 6 | 3 planned, 1 unsupported, 2 reserved/unsupported |
| ATMONTO domains represented | 8 | used as the semantic alignment vocabulary |

## Mapping rule

Each row follows the same pattern:

```text
chapter / section range
  -> concepts in the FAA text
  -> ATMONTO classes
  -> FAA Order-specific extension classes
  -> property signatures with domain and range
  -> active | planned | unsupported
```

ATMONTO classes and properties are taken from the local semantic catalog. FAA
Order-specific classes and relations are defined in
`faa_jo_7210_3ee_ontology_profile_v2.json`. A proposed relationship that is not
in either authority remains `planned`; it is not silently invented in the KG.

## Current focal path

```text
PolicyDocument
  -> PolicySection
  -> PolicyParagraph
  -> PolicyRule
  -> ATMONTO TMI / facility / route / weather terms
  -> deterministic validation and publication
```

For Chapter 18, `WeatherCondition` and `MeteorologicalReport` are contextual
or evidentiary roots. Their presence does not establish that weather caused a
TMI, and a missing reason remains missing.

## Source integrity

- Source: `data/raw/faa_orders/JO_7210.3EE_2025-02-20.pdf`
- Effective date: `2025-02-20`
- Pages: `590`
- SHA-256: `16893ed16ab2c9432ec981a4cefa2cc11ba264e45ebd33cfc63d680f53ca6a5d`

This artifact deliberately separates normative-document coverage from runtime
event evidence. It can guide chunking, retrieval, candidate-fact tasks, and
future profile expansion without implying that the order itself contains
historical flight, weather, or TMI instances.
