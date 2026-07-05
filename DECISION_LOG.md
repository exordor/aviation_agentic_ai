# Decision Log

> Seeded on 2026-07-05 from the project scope lock (`docs/master_project_scope_lock.md`) and the documentation map tiering rules. Each entry records a structural decision and its consequences. Future significant choices (tool changes, abandoned experiments, model selection, refactor scope) should be appended here.

## D001 — Single thesis-grade system study

### Date

(see git history of master_project_scope_lock.md)

### Context

The repository had accumulated multiple parallel experimental tracks (PHAK ontology, web demo, chunking experiments, multi-source pilots).

### Decision

Freeze the project outcome as one bounded thesis-grade system study: Evidence-Grounded Schema-Constrained Agentic KG-RAG for FAA ATCSCC Advisories.

### Reason

- Prevents research support work from expanding into parallel subprojects.
- Keeps thesis scope defensible.

### Alternatives Considered

- Multi-thesis split (ontology + RAG + agent loop as separate studies).
- Open-ended benchmark project.

### Consequences

Pro: clear stop rule and minimum deliverable set.
Con: any new idea must fit a locked deliverable or be deferred.

## D002 — Exactly four research questions

### Date

(same as above)

### Context

Multiple candidate RQs were circulating across stage reports.

### Decision

Keep exactly four RQs: schema-constrained extraction, agentic validation-refinement, KG-RAG grounding, failure boundary. Any additional question must fold into one of these four or move to future work.

### Reason

- Keeps the evaluation layered and bounded.
- Prevents open-ended benchmark creep.

### Alternatives Considered

- Adding a fifth RQ for cross-source transfer.
- Treating ontology completeness as an RQ.

### Consequences

Pro: each RQ has an experiment layer, metrics, artifacts, pass/fail interpretation.
Con: cross-source and ontology-completeness work is future work only.

## D003 — Layered metrics, no overall score

### Date

(same as above)

### Context

A single mixed score would let one strong layer hide a weak one.

### Decision

Report layered metrics: extraction, evidence, agentic-loop, retrieval/answer, boundary. No mixed overall score.

### Reason

- Recall@5, provenance completeness, and unsupported-claim rate have different denominators and risk profiles.

### Alternatives Considered

- Weighted average score.
- Single "KG-RAG quality" number.

### Consequences

Pro: tradeoffs are visible; GraphRAG cannot be claimed to improve Recall@k without the retrieval-result support.
Con: results table is wider and harder to compress into one slide number.

## D004 — PHAK-era evidence is historical

### Date

2026-05/06 archive wave (see git log)

### Context

Early PHAK Chapter 4 ontology, chunking, and web-demo reports used different framing than the current ATCSCC line.

### Decision

Treat PHAK, web-demo, chunking-era, and old final-report docs as historical. They may be cited for method evolution or negative results, but cannot override current ATCSCC framing.

### Reason

- Prevents ontology-first framing from leaking into the schema-constrained KG-RAG thesis.

### Alternatives Considered

- Delete PHAK-era files.
- Keep PHAK-era as primary track.

### Consequences

Pro: thesis story stays coherent.
Con: some reuse requires manual rewrite into ATCSCC wording.

## D005 — Source families stay separate

### Date

(same as D001)

### Context

ATCSCC advisories, FAA/NASA reference PDFs, NASR/facility data, weather, and transfer-pilot corpora have different shapes and evaluation protocols.

### Decision

Keep source families separate. Do not merge them into one semantic-F1 table unless a source-specific profile and gold/evaluation protocol exists for each family.

### Reason

- A shared F1 table would mix different denominators and tasks.

### Alternatives Considered

- Unified cross-source extraction metric.

### Consequences

Pro: each source family gets a task-relative correctness claim.
Con: cross-source comparison is limited to structural conformance, evidence grounding, and canonicalization yield.

## D006 — Documentation tiers and tier maintenance rules

### Date

(same as documentation_map.md)

### Context

The repo mixes canonical framing, protocols, current evidence, source explainers, paper analyses, historical artifacts, and generated side artifacts.

### Decision

Use the six documentation tiers (T0–T6) from `docs/documentation_map.md` §Document Tiers. New material routes per the "Where New Documents Should Go" table.

### Reason

- Tier discipline keeps canonical framing, current evidence, source explainers, paper analyses, and historical artifacts from polluting each other.
- A documented precedence chain lets current ATCSCC framing override legacy PHAK-era framing without deleting the older evidence.

### Alternatives Considered

- Flat docs/ namespace.
- Per-date organization.

### Consequences

Pro: clear precedence chain (now anchored at RESEARCH_AUDIT.md after this refactor).
Con: tier discipline requires upkeep; stale tier assignments cause context pollution.
