# ATCSCC Agent Plan Presentation Storyboard

This storyboard is a concise English slide spine for presenting the Agent plan
without overstating what has been experimentally validated. It separates the
implemented ATCSCC KG-RAG baseline, the implemented L1 repair-loop MVP, and the
planned L2 end-to-end Agent.

## Claim Boundary

- Retrospective FAA ATCSCC advisories only.
- Schema/profile is an engineering constraint, not a complete aviation ontology.
- No live ATC decision support.
- No quantitative Agent uplift claim until L1/L2 is separately scored.
- Existing quantitative evidence supports source-bounded KG-RAG grounding, not
  universal GraphRAG superiority.

## Ghost Deck

1. The current project already demonstrates source-bounded ATCSCC KG-RAG; the Agent plan adds auditable repair.
2. The existing S5/S6 agentic path is single-pass, so diagnostics do not yet trigger targeted re-extraction.
3. L1 turns extractor, validator, critic, repair planner, and refiner into a bounded feedback loop.
4. L1 keeps authority in sources and validators; repair targets are instructions, never accepted facts.
5. The L1 MVP is behavioral: repair missing fields, preserve accepted facts, block repeats, and record budget exhaustion.
6. L2 composes L1 with graph build, retrieval, answer generation, citation, and abstention.
7. Path B is the preferred L2 route because it reuses the existing ATCSCC S7 retrieval contracts.
8. Existing results support KG-RAG grounding on ATCSCC, but they do not yet prove Agent-loop uplift.
9. The deliverable is a bounded, testable Agentic KG-RAG pipeline rather than autonomous ontology construction.
10. The next experiment scores L1 repair-loop outputs against the same evidence and grounding metrics.

## Slide Plan

| # | Status | Action title | Exhibit type | Evidence / artifact |
|---:|---|---|---|---|
| 1 | Implemented baseline + L1 MVP | The current project already demonstrates source-bounded ATCSCC KG-RAG; the Agent plan adds auditable repair. | Title slide with boundary ribbon | `docs/thesis_writing_spine.md`; `docs/atcscc_agent_architecture.md`; `reports/stages/nasa_atmonto_s7_retrieval.md` |
| 2 | Implemented baseline gap | The existing S5/S6 agentic path is single-pass, so diagnostics do not yet trigger targeted re-extraction. | Before-state sequence diagram | `reporting/atmonto/agentic_loop/live_pilot_agents.py`; `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` |
| 3 | Implemented L1 MVP | L1 turns extractor, validator, critic, repair planner, and refiner into a bounded feedback loop. | Agent loop diagram | `src/aviation_agentic_ai/agents/extraction_agent.py`; `src/aviation_agentic_ai/agents/repair_planner.py` |
| 4 | Implemented L1 MVP | L1 keeps authority in sources and validators; repair targets are instructions, never accepted facts. | Evidence/fact lifecycle card | `src/aviation_agentic_ai/agents/types.py`; `docs/atcscc_agent_architecture.md` |
| 5 | Implemented L1 MVP | The L1 MVP is behavioral: repair missing fields, preserve accepted facts, block repeats, and record budget exhaustion. | Acceptance-test matrix | `tests/test_agents_extraction_agent.py` |
| 6 | Planned L2 | L2 composes L1 with graph build, retrieval, answer generation, citation, and abstention. | Layered architecture diagram | `docs/atcscc_agent_architecture.md`; `reports/final/assets/architecture/atcscc_architecture_01_layered_system.png` |
| 7 | Planned L2 | Path B is the preferred L2 route because it reuses the existing ATCSCC S7 retrieval contracts. | Path A vs Path B trade-off table | `docs/atcscc_agent_architecture.md`; `reporting/atmonto/core/live_retrieval.py` |
| 8 | Existing evidence | Existing results support KG-RAG grounding on ATCSCC, but they do not yet prove Agent-loop uplift. | KPI bars plus claim-boundary callout | `reports/stages/nasa_atmonto_s7_retrieval.md`; `reports/final/assets/architecture/atcscc_architecture_04_evaluation.png` |
| 9 | Boundary | The deliverable is a bounded, testable Agentic KG-RAG pipeline rather than autonomous ontology construction. | Boundary table | `docs/thesis_positioning.md`; `docs/master_project_scope_lock.md` |
| 10 | Next experiment | The next experiment scores L1 repair-loop outputs against the same evidence and grounding metrics. | Roadmap / conclusion slide | `docs/atcscc_agent_architecture.md`; `tests/test_agents_extraction_agent.py` |

## Demo And Verification Paths

- Existing project trace: `uv run aviation-ai demo`
- L1 repair-loop behavior: `uv run pytest -q tests/test_agents_extraction_agent.py`
- Relevant regression slice:
  `uv run pytest -q tests/test_nasa_atmonto_s5_s6_live_agentic_pilot.py tests/test_nasa_atmonto_agentic_loop.py tests/test_nasa_atmonto_s5_s6_agentic_loop.py tests/test_nasa_atmonto_s5_s6_independent_agentic_run.py tests/test_hybrid_cli.py`
