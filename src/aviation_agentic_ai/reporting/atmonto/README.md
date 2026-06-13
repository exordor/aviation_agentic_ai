# ATMONTO/ATCSCC Report Families

This subpackage groups the ATMONTO-derived ATCSCC reports by experiment stage.
The old flat names `reporting/nasa_atmonto_*` still work via compatibility shims;
new code should import from the package paths below.

## agentic_loop/ — S5/S6 extractor/validator/refiner/critic loop (RQ2)
- `contract.py` — shared artifact-contract constants (e.g. DEFAULT_CQ_MANIFEST_PATH)
- `diagnostics.py` — agentic-loop diagnostic helpers
- `loop_render.py` — markdown rendering for the agentic loop report
- `loop.py` — top-level agentic extraction-validation loop report
- `s5_s6_loop.py` — S5/S6 agentic loop report
- `s5_s6_loop_render.py` — S5/S6 loop markdown rendering
- `independent_run.py` — independent artifact-driven S5/S6 run (from S0 candidates)
- `independent_run_agents.py` — agent roles/metrics helpers for the independent run
- `independent_run_render.py` — independent-run markdown rendering
- `live_pilot.py` — live LLM extractor/validator/critic/refiner pilot run
- `live_pilot_agents.py` — live-pilot agent helpers
- `live_pilot_render.py` — live-pilot markdown rendering

## s7/ — Retrieval, answer generation, and review boundary (RQ3/RQ4)
- `retrieval.py` — source-bounded vector/graph/hybrid retrieval
- `answer_generation.py` — deterministic GraphRAG answer generation
- `llm_answer_generation.py` — LLM answer generation over retrieved contexts
- `graph_health.py` — advisory event graph health diagnostics
- `human_review_candidates.py` — human-review candidate queue
- `candidate_adjudication.py` — profile/gold-boundary candidate adjudication
- `broad_answer_review_packet.py` — broad reviewer packet
- `partial_answer_ablation.py` — partial-answer ablation
- `profile_decision.py` — profile-decision what-if analysis
- `answer_review_decisions.py` — answer review decision records
- `answer_review_import.py` — reviewed-CSV import
- `answer_review_protocol.py` — answer review protocol
- `answer_review_worksheet.py` — answer review worksheet
- `automated_adversarial_review.py` — automated adversarial review
- `review_handoff.py` — review handoff summary

## Not yet migrated (still at reporting/nasa_atmonto_*)
- `nasa_atmonto_cq*.py` — competency-question infrastructure (planned: atmonto/core/)
- `nasa_atmonto_answer_*.py` — answer benchmark/scoring (planned: atmonto/core/)
- `nasa_atmonto_{graph,live}_retrieval.py` — retrieval backends (planned: atmonto/core/)
- `nasa_atmonto_{reviewer_defense,sota_goal}_audit.py` — claim-safety audits (planned: atmonto/audit/)
