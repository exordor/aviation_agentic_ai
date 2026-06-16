# Pipeline Authority Model

Status: design note for thesis writing, architecture figures, and reviewer
defense. This document records a peer-slide-inspired framing pattern. It is
not external evidence for experiment results.

Source note: the framing pattern was inspired by PPT material shared by Emre
Cem Elevis, especially the build/verification/schema-boundary pipeline slide.
The adaptation below is project-specific and should be cited as design
inspiration, not as empirical evidence for this repository.

## Purpose

The current thesis needs a clear authority model: which components may propose
facts, which components may accept facts, which components only audit facts,
and which artifacts must be rebuildable. This matters because the project uses
LLMs and agentic roles, but the thesis cannot imply that an LLM is the source of
truth or that the graph is manually curated after generation.

The design principle is:

> LLM agents may propose, critique, or rewrite candidate event records, but no
> LLM output is authoritative until it passes source, schema, evidence, and
> provenance gates.

## Architecture Principles

| Principle | Meaning for this project | Claim-safety benefit |
| --- | --- | --- |
| Build and verification are separate | Extraction and graph materialization build candidate artifacts; validation, audits, and reviewer-defense reports inspect or reject them. | Prevents the thesis from claiming that an audit magically improves the graph unless a documented repair stage is run. |
| LLMs are non-authoritative | Extractor, refiner, critic, and answer generator roles can use LLMs, but accepted facts require schema validity and evidence support. | Reduces reviewer risk around hallucinated triples and ungrounded claims. |
| Schema spine is cross-cutting | The ATCSCC profile, controlled values, CQs, SHACL/JSON-schema checks, and artifact contracts constrain all stages. | Keeps ontology as an engineering constraint, not the thesis object. |
| Graph is rebuildable | The advisory event graph must be reproducible from raw advisories, parser outputs, schema/profile versions, prompts, configs, and run manifests. | Supports reproducibility and avoids hand-edited KG claims. |
| Retrieval atom is source-bounded | Retrieval should prefer advisory event fields, source records, facts, evidence spans, and graph paths over whole-page authority. | Makes KG-RAG evaluation about inspectable evidence units, not opaque document retrieval. |
| Human review is an explicit boundary | Human or expert review is represented as a separate sign-off or review packet, not silently folded into automated metrics. | Protects against overclaiming expert certification. |

## Mapping To The ATCSCC Project

| Generic pipeline idea | ATCSCC project equivalent | Existing or target artifact |
| --- | --- | --- |
| Source documents | FAA ATCSCC advisory HTML/text snapshots | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| Source intake | Advisory parser, source IDs, evidence spans, provenance fields | `data/experiments/nasa_atmonto/formal/input_records.jsonl` |
| Claim extractor | Event/slot/fact proposer for advisory number, TMI type, target, cause, time window, status, route information | S1/S2/S3/S4 prediction artifacts |
| Graph builder | Advisory event graph / fact store built from accepted facts | S4/S5/S6 graph and S7 graph-health reports |
| Schema gate | ATCSCC profile, controlled vocabulary, schema validation, SHACL/JSON-schema checks | `reports/stages/atcscc_ontology_profile_overview.md`, prediction-output validation reports |
| Graph health | Entity/fact/path availability, graph-use diagnostics, CQ coverage | `reports/stages/nasa_atmonto_s7_graph_health.md`, `reports/stages/nasa_atmonto_cq_query_evaluation.md` |
| Correctness auditor | Evidence containment, unsupported relation checks, reviewed-subset precision/recall/F1, citation faithfulness | extraction scoring, answer review, reviewer-defense audit |
| Completeness auditor | CQ coverage, source-observable field coverage, profile-gap register, recall diagnostics | CQ evaluation, profile decision, rejection adjudication |
| Schema spine | NASA ATMONTO-derived ATCSCC application schema/profile plus CQs and constraints | `docs/thesis_positioning.md`, schema/profile reports |
| External boundary | NewAPI LLM provider, vector index, graph store, local runtime dependencies | provider metadata and run manifests |
| Sign-off dossier | Thesis dashboard, claim review, reviewer-defense audit, optional human-review packet | `reports/stages/thesis_experiment_dashboard.md`, `reports/stages/nasa_atmonto_reviewer_defense_audit.md` |
| Product layer | Web demo, defense deck, report renderer | Must remain retrospective and non-operational |

## Support Assessment

This framing strongly supports the project, but as a method narrative and
architecture discipline rather than as a new experimental result.

It supports the project in five concrete ways:

1. **Method figure design**: The thesis method figure should show three layers:
   build pipeline, independent verification layer, and cross-cutting schema /
   runtime boundary. This is clearer than a single long left-to-right pipeline.
2. **Reviewer defense**: It gives a concise answer to a likely criticism:
   "How do you prevent the LLM from inventing KG facts?" The answer is that the
   LLM proposes candidates, while schema and evidence gates decide acceptance.
3. **Experiment interpretation**: Negative or mixed LLM results remain useful
   because the verifier, critic, rejection register, and failure taxonomy are
   first-class outputs.
4. **Engineering discipline**: It gives a rule for future code changes: no
   verifier should silently mutate the graph. Repair must be an explicit stage
   with before/after artifacts.
5. **Thesis scope control**: It reinforces that the project is not proving
   ontology completeness or operational ATC authority. It evaluates a bounded,
   rebuildable, evidence-grounded advisory-event graph pipeline.

## What Not To Copy Directly

The peer slide states that the LLM appears in exactly one place. That is too
strict for this project because the thesis explicitly studies agentic roles
such as extractor, validator, refiner, critic, and answer generator.

Use this adapted rule instead:

> LLMs may appear in multiple bounded agent roles, but authority is assigned to
> source evidence, schema constraints, validation reports, and review packets,
> not to model output alone.

The slide also uses a product layer with an advisory engine. For this thesis,
that layer must remain parked or retrospective. The project should not imply
live operational decision support.

## Project Support Actions

| Action | Priority | Rationale |
| --- | --- | --- |
| Redraw the architecture figure around build, verification, and cross-cutting schema/runtime layers. | High | This will make the method section and defense deck easier to understand. |
| Add an "authority model" paragraph to the Method chapter and defense speaker notes. | High | This directly addresses LLM hallucination and ontology-overclaim risk. |
| Audit validation/refinement code and reports for silent graph mutation. | Medium | Verifiers should emit diagnostics; repair stages should be explicit and reproducible. |
| Ensure run manifests record source snapshot, schema/profile version, prompt version, model/provider, and config hash where available. | Medium | Strengthens rebuildability and experiment provenance. |
| Treat the thesis dashboard and reviewer-defense audit as the sign-off dossier. | Medium | Avoids creating a parallel reporting path unless a final package requires it. |
| Use this authority model when designing future transfer-domain pilots. | Low | The same discipline can transfer, but ATCSCC remains the primary evaluated source family. |

## Thesis-Ready Wording

The system is best described as:

> A rebuildable schema-constrained pipeline in which LLM agents propose and
> refine source-bounded advisory-event candidates, while deterministic schema,
> evidence, provenance, and review gates decide what can enter the graph and
> how KG-RAG answers may cite it.

Avoid wording such as:

- "The LLM constructs the knowledge graph."
- "The ontology guarantees semantic correctness."
- "The graph is complete."
- "The advisory engine supports operational ATC decisions."
