# Ontology Evaluation Report

- Ontology: `data/ontology/curated/06_phak_ch4_0.curated.ttl`
- CQ file: `data/cqs/06_phak_ch4_0.json`
- CQ standard: AI-generated silver CQs, not domain-expert gold annotations
- AI review enabled: no

## Overall Judgment

- RDF-valid TBox extraction prototype: yes
- Valid TBox prototype: yes
- Publication-ready ontology: no

- The ontology is an RDF-valid TBox extraction prototype.
- All high-severity ontology quality gates passed.
- No ABox individuals were detected in the ontology.

## Structural Metrics

- RDF valid: yes
- Triples: 188
- Classes: 35
- Object properties: 9
- Datatype properties: 0
- Declared named individuals: 0
- Non-schema typed resources: 0
- TBox only: yes
- Root classes: 1
- Leaf classes: 30
- Isolated classes: 0
- OWL restrictions: 0
- `owl:someValuesFrom`: 0
- Class label coverage: 1.0
- Class comment coverage: 1.0
- Property label coverage: 1.0
- Property comment coverage: 1.0
- Out-of-namespace schema terms: 0
- Properties missing domain: None
- Properties missing range: None

## Quality Gates

| Gate | Status | Severity | Evidence |
| --- | --- | --- | --- |
| RDF/Turtle parses successfully | pass | high | RDF parser completed without errors. |
| No ABox-like typed resources | pass | high | Non-schema typed resources: 0; declared named individuals: 0. |
| Ontology metadata declaration is present | pass | high | owl:Ontology declarations: 1. |
| Minimum human-readable label coverage is met | pass | high | Class labels: 1.0; property labels: 1.0. |
| Property domain/range completeness is acceptable | pass | high | Missing domain: 0; missing range: 0. |
| Schema terms stay inside the configured aviation namespace | pass | high | Out-of-namespace schema terms: 0. |
| No high-severity semantic smells are detected | pass | high | High-severity semantic smells: 0. |
| Silver-CQ unique entity lexical coverage is above threshold | fail | medium | Unique entity coverage ratio: 0.4514. |

## Semantic Smell Checks

- Total smells: 0
- High-severity smells: 0


## CQ Lexical Coverage

- CQs: 334
- Entity mentions: 754 / 1154
- Entity mention coverage ratio: 0.6534
- Unique entity coverage ratio: 0.4514
- Top missing entities: lower surface, upper surface, viscosity, acceleration, mass, friction, object, velocity, water vapor, causal relation

## Silver Answerability Heuristics

- Standard: deterministic silver heuristics from normalized CQ terms and OWL schema structure; not gold-standard answerability.
- Yes / partial / no: 10 / 290 / 34
- Heuristic support score: 0.4641
- Expected-answer term coverage ratio: 0.7587
- Property/relation coverage ratio: 0.0689
- Answer property coverage ratio: 0.0539
- Connected class/property ratio: 0.015
- Object property matches: 23
- Datatype property matches: 0

## AI Review

- AI review skipped. Run with `--ai-review` after configuring a rotated API key.
