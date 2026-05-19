# Document Expansion Protocol

This project must not expand beyond PHAK Chapter 4 until each new source has a
stable metadata record, section map, and evaluation plan. The goal is to avoid
mixing document-scope uncertainty with GraphRAG retrieval or KG extraction
claims.

## Required Document Metadata

Each source document must define:

- `document_id`: stable lowercase identifier used in chunks, KG triples, and reports.
- `title`: human-readable source title.
- `source_type`: for example `faa_handbook_chapter`, `poh`, `procedure_manual`, or `training_note`.
- `source_path`: repository-relative path to the raw source.
- `chapter`: chapter or section label when applicable.
- `revision_date`: source revision or publication date when available.
- `page_start` and `page_end`: page range included in the experiment.
- `advisory_risk_level`: `learning`, `procedure_reference`, or `operationally_sensitive`.

## Required Section Schema

Each document must also provide section records:

- `section_id`: stable identifier, unique within the document.
- `title`: section heading from the source.
- `level`: hierarchy level, starting at 1 for top-level sections.
- `page_start` and `page_end`: source page coverage.
- `parent_id`: parent section id, or `null` for top-level sections.

## Readiness Checklist

Before adding a new document:

- Metadata and section records are validated.
- Chunk IDs include `document_id`, strategy, page, and chunk index.
- Gold labels identify page/chunk/span evidence or expected abstention.
- KG extraction profile terms are checked against the curated ontology.
- Advisory boundary language is reviewed if the source is procedure-like or operationally sensitive.
- Reports keep retrieval, KG evidence, answer quality, and cost/latency metrics separate.

## Expansion Rule

Emergency, procedure, POH, or live operational sources are out of scope until
this schema is enforced and no-answer/abstention evaluation is working for the
existing PHAK Chapter 4 benchmark.
