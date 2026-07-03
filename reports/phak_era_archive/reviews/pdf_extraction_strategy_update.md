# PDF Extraction Strategy Update

## Decision

- PyMuPDF heuristic status: `demoted_to_legacy_baseline_only`
- Docling status: `primary_structure_extractor`
- PyMuPDF text status: `text_fidelity_reference_and_fast_fallback`
- Hybrid status: `candidate_default_for_structure_aware_pdf_chunking_after_downstream_validation`

## Evidence

- Legacy PyMuPDF false heading count: 113
- Legacy PyMuPDF heading precision: 0.0887
- Docling heading recall on gold sample: 1.0
- Hybrid repaired artifacts: 14

## Remaining Risks

- Docling word merging
- Docling runtime and model availability
- table label ambiguity
- chunk ID compatibility
- downstream retrieval must be regenerated before scientific claims change

This is internal engineering evidence. It is not human review, external aviation expert certification, or operational readiness evidence.
