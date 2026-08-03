# Current ATCSCC Defense Deck Outline

Status: current slide spine for the ingestion-first mainline. This outline
does not describe the retired extractor/validator/refiner/critic pipeline or a
100-record Gold evaluation.

## Working title

**ATMONTO-Grounded Agentic HybridRAG for Heterogeneous Aviation Knowledge
Integration**

## Deck boundary

The thesis presents a retrospective, evidence-bounded aviation knowledge
system. It is not live ATC support, a causal model, an effectiveness scorer, or
a TMI recommendation system.

## Slide spine

| # | Slide | Main message | Current proof object |
| ---: | --- | --- | --- |
| 1 | Title and research boundary | The project integrates aviation evidence and answers bounded natural-language questions. | `RESEARCH_AUDIT.md` |
| 2 | Why heterogeneous evidence matters | ATCSCC, authority, Weather, BTS, and Flight/Airspace records have different roles and identifiers. | `docs/figures/cross_source_evidence_motivated_example.png` |
| 3 | Research positioning | ATMONTO supplies admitted vocabulary; ATMGRAPH motivates ABox construction and cross-source querying. | `docs/multi_agent_kg_system_design.md` |
| 4 | Five-plane architecture | Deterministic ingestion, semantic publication, authoritative storage, retrieval views, and Agent interaction form one pipeline. | `docs/figures/aviation_hybridrag_system_architecture.png` |
| 5 | Source and evidence contracts | Source versions, anchors, temporal scopes, and source roles are preserved before publication. | `docs/figures/heterogeneous_source_formats.png` |
| 6 | ATMONTO-grounded publication | TMI and Flight/Airspace roots use one Formal Publication Kernel and generic publication spine. | `data/ontology/curated/atmonto_application_profile_v1.json` |
| 7 | Authoritative store and views | SQLite is canonical; FTS5, Chroma, RDF/Turtle, JSONL, and Neo4j are derived or optional views. | `docs/multi_agent_kg_system_design.md` |
| 8 | Query Agent workflow | Every valid natural-language question enters an LLM-routed, bounded read-only tool loop. | `docs/figures/bounded_query_agent_workflow.png` |
| 9 | GDP 138 walkthrough | A single question can combine publication facts, declared reason, Weather context, and BTS observations without causal overclaiming. | `docs/flagship_gdp138_walkthrough.md` |
| 10 | Extensible domains | The same spine admits Flight, Airport/ARTCC, Route, TrackPoint, Sector, Weather, and reviewed associations under separate temporal scopes. | `GOALS.md` |
| 11 | Optional Web Evidence | A separately authorized sidecar can add public-document evidence with exact anchors; it is not a source of aviation facts by itself. | `docs/wigolo_web_evidence_operations.md` |
| 12 | Evaluation and limitations | Offline tests, live smoke, and future experiments are separated; current reports are compatibility evidence, not benchmarks. | `RESEARCH_AUDIT.md` |
| 13 | Conclusion | The contribution is reusable evidence integration and bounded HybridRAG interaction, not autonomous aviation decision-making. | `reports/final/atcscc_thesis_report_outline.md` |

## Speaking script

### Opening

This thesis studies an ATMONTO-grounded HybridRAG system for heterogeneous
aviation evidence. ATCSCC advisories are the mature demonstrator, while the
publication and retrieval contracts are designed for additional aviation
domains.

### Method transition

The system first preserves immutable sources, exact anchors, authority
identity, and temporal scope. Deterministic services publish only supported
facts through the Formal Publication Kernel. The Query Agent is then allowed
to choose read-only retrieval actions for a natural-language question.

### Result transition

Results must be read by layer: provider-call success is not answer acceptance;
Weather association is not causality; BTS observation is not FAA capacity or
demand; and a compatibility smoke is not a benchmark.

### Closing

The defensible claim is that a source-bounded, ATMONTO-grounded Agentic
HybridRAG can organize heterogeneous aviation evidence and produce traceable
answers under explicit support and insufficiency boundaries.

## Appendix slides

1. ATCSCC advisory source example and exact anchors.
2. ATMONTO application-profile slice and publication contract.
3. SQLite evidence store and rebuildable retrieval views.
4. Query Agent family routing and bounded tool loop.
5. GDP 138 evidence layers and claim boundaries.
6. Flight/Airspace temporal-domain separation.
7. Web Evidence sidecar boundary and license/deployment separation.
8. Evaluation-mode and limitation matrix.

## Presentation rules

- Do not use the former extractor/validator/refiner/critic architecture as a
  current system diagram.
- Do not describe the former 100-record Gold sample as current evaluation.
- Do not present historical compatibility reports as benchmark results.
- Keep Weather and BTS in their declared evidence roles.
- Keep the current architecture and report spine synchronized with
  `RESEARCH_AUDIT.md`, `GOALS.md`, and `docs/repository_artifact_policy.md`.
