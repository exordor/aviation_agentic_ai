# SubAgent Ontology Pipeline Review

- Review ID: `2026-05-18-subagent-ontology-review`
- Date: 2026-05-18
- Method: four read-only subAgent reviews covering CQs, baseline ontology, prompts, and pipeline.
- Status: CQ validation, ontology quality gates, structured SRD/TIP artifacts, checkpoints, manifests, and deterministic evaluation workflow completed; ontology model refactor remains planned.

## Summary

The project has a working ontology-generation prototype and baseline evaluation
report, but the current evidence is still too weak to claim robust ontology
engineering quality. The immediate improvement path is to harden CQ validation,
normalize ODPs, make ontology verdicts more conservative, enforce structured
SRD/TIP artifacts, and add reproducible run manifests/checkpoints.

## Findings

| ID | Area | Severity | Finding | Status |
| --- | --- | --- | --- | --- |
| F-CQ-001 | cqs | high | CQ artifacts are not strictly validated before generation or evaluation | closed |
| F-CQ-002 | cqs | high | CQ IDs are positional and not stable | closed |
| F-CQ-003 | cqs | high | ODP labels are too fragmented for defensible stratification | closed |
| F-CQ-004 | cqs | medium | Lexical CQ coverage can overstate ontology support | closed |
| F-ONT-001 | baseline_ontology | high | Baseline verdict is too generous for ontology engineering quality | closed |
| F-ONT-002 | baseline_ontology | high | Baseline ontology conflates quantity kinds, units, assertions, states, and processes | open |
| F-ONT-003 | baseline_ontology | high | Several axioms appear semantically incoherent or likely false | closed |
| F-ONT-004 | baseline_ontology | medium | Core property semantics are weakened by broad owl:Thing domains and ranges | open |
| F-PROMPT-001 | prompts | high | SRD and TIP outputs have no enforceable schema | closed |
| F-PROMPT-002 | prompts | high | Turtle validation only checks syntax, not ontology intent | closed |
| F-PROMPT-003 | prompts | medium | Complete-TTL rewrite is fragile as ontology size grows | open |
| F-PIPE-001 | pipeline | high | Generated ontology is not evaluated by default | closed |
| F-PIPE-002 | pipeline | high | Generation has no durable per-page artifacts or checkpoints | closed |
| F-PIPE-003 | pipeline | high | LLM and run settings are not captured in outputs | closed |
| F-PIPE-004 | pipeline | medium | AI review is enabled by default and fails all-or-nothing | closed |

## Actions

| ID | Priority | Action | Target | Status |
| --- | --- | --- | --- | --- |
| A-P0-001 | P0 | Add strict CQ validation and stable CQ identity | CQs | done |
| A-P0-002 | P0 | Reframe ontology verdict and add semantic quality gates | Ontology evaluation | done |
| A-P1-001 | P1 | Introduce structured SRD/TIP schemas tied to CQ evidence | Prompt artifacts | done |
| A-P1-002 | P1 | Write generation run manifests and per-page checkpoints | Pipeline reproducibility | done |
| A-P1-003 | P1 | Make evaluation deterministic by default and align generated artifact evaluation | CLI workflow | done |
| A-P2-001 | P2 | Refactor ontology upper patterns for quantities, units, states, and processes | Ontology model | planned |

## Notes

- Current CQs are AI-generated silver CQs, not expert gold annotations.
- Current lexical CQ coverage should be treated as a smoke metric only.
- The baseline ontology is RDF-valid, but not yet publication-ready.
- Future reviews should add new JSON/Markdown files under `reports/reviews/`
  and update action statuses instead of deleting historical findings.
