# ATCSCC Agent Plan Presentation Storyboard

This storyboard is a concise English slide spine for presenting the Agent plan
without overstating what has been experimentally validated. It separates the
implemented ATCSCC KG-RAG baseline, the implemented extraction loop repair-loop MVP, and the
planned retrieval layer end-to-end Agent.

## Claim Boundary

- Retrospective FAA ATCSCC advisories only.
- Schema/profile is an engineering constraint, not a complete aviation ontology.
- No live ATC decision support.
- No quantitative Agent uplift claim until extraction loop/retrieval layer is separately scored.
- Existing quantitative evidence supports source-bounded KG-RAG grounding, not
  universal GraphRAG superiority.

## Ghost Deck

1. The current project already demonstrates source-bounded ATCSCC KG-RAG; the Agent plan adds auditable repair.
2. The existing agentic validation stage/agentic refinement stage agentic path is single-pass, so diagnostics do not yet trigger targeted re-extraction.
3. extraction loop turns extractor, validator, critic, repair planner, and refiner into a bounded feedback loop.
4. extraction loop keeps authority in sources and validators; repair targets are instructions, never accepted facts.
5. The extraction loop MVP is behavioral: repair missing fields, preserve accepted facts, block repeats, and record budget exhaustion.
6. retrieval layer composes extraction loop with graph build, retrieval, answer generation, citation, and abstention.
7. thesis-aligned retrieval path is the preferred retrieval layer route because it reuses the existing ATCSCC retrieval-and-answer stage retrieval contracts.
8. Existing results support KG-RAG grounding on ATCSCC, but they do not yet prove Agent-loop uplift.
9. The deliverable is a bounded, testable Agentic KG-RAG pipeline rather than autonomous ontology construction.
10. The next experiment scores extraction loop repair-loop outputs against the same evidence and grounding metrics.

## Slide Plan

| # | Status | Action title | Exhibit type | Evidence / artifact |
|---:|---|---|---|---|
| 1 | Implemented baseline and minimum viable system | The current project already demonstrates source-bounded ATCSCC KG-RAG; the Agent plan adds auditable repair. | Title slide with boundary ribbon | Thesis writing spine, architecture, and retrieval evidence catalog |
| 2 | Implemented baseline gap | The existing agentic path is single-pass, so diagnostics do not yet trigger targeted re-extraction. | Before-state sequence diagram | Agentic runtime and diagnostic evidence catalog |
| 3 | Implemented extraction loop MVP | extraction loop turns extractor, validator, critic, repair planner, and refiner into a bounded feedback loop. | Agent loop diagram | `src/aviation_agentic_ai/agents/extraction_agent.py`; `src/aviation_agentic_ai/agents/repair_planner.py` |
| 4 | Implemented extraction loop MVP | extraction loop keeps authority in sources and validators; repair targets are instructions, never accepted facts. | Evidence/fact lifecycle card | `src/aviation_agentic_ai/agents/types.py`; `docs/atcscc_agent_architecture.md` |
| 5 | Implemented extraction loop MVP | The extraction loop MVP is behavioral: repair missing fields, preserve accepted facts, block repeats, and record budget exhaustion. | Acceptance-test matrix | `tests/test_agents_extraction_agent.py` |
| 6 | Planned retrieval layer | retrieval layer composes extraction loop with graph build, retrieval, answer generation, citation, and abstention. | Layered architecture diagram | `docs/atcscc_agent_architecture.md`; `reports/final/assets/architecture/atcscc_architecture_01_layered_system.png` |
| 7 | Planned retrieval layer | thesis-aligned retrieval path is the preferred retrieval layer route because it reuses the existing ATCSCC retrieval-and-answer stage retrieval contracts. | legacy Chroma path vs thesis-aligned retrieval path trade-off table | `docs/atcscc_agent_architecture.md`; `reporting/atmonto/core/live_retrieval.py` |
| 8 | Existing evidence | Existing results support KG-RAG grounding on ATCSCC, but they do not yet prove Agent-loop uplift. | KPI bars plus claim-boundary callout | Retrieval evidence catalog and evaluation architecture figure |
| 9 | Boundary | The deliverable is a bounded, testable Agentic KG-RAG pipeline rather than autonomous ontology construction. | Boundary table | `RESEARCH_OVERVIEW.md`; `DECISION_LOG.md` |
| 10 | Next experiment | The next experiment scores extraction loop repair-loop outputs against the same evidence and grounding metrics. | Roadmap / conclusion slide | `docs/atcscc_agent_architecture.md`; `tests/test_agents_extraction_agent.py` |

## Demo And Verification Paths

- Existing project trace: `uv run aviation-ai demo`
- extraction loop repair-loop behavior: `uv run pytest -q tests/test_agents_extraction_agent.py`
- Relevant regression slice:
  `uv run pytest -q`
