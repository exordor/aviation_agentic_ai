# ATMONTO/ATCSCC Report Families

This subpackage groups the ATMONTO-derived ATCSCC reports by experiment stage.
The old flat `reporting/nasa_atmonto_*` names have been removed; import from the
package paths below.

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

## audit/ — Claim-safety audits (RQ4)
- `reviewer_defense_audit.py` — reviewer-defense audit separating automated diagnostics from human/expert review
- `sota_goal_audit.py` — SOTA/thesis goal-claim gate audit

## core/ — Foundation building blocks
- `cq.py` — competency-question infrastructure (normalize_atmonto_predicate, DEFAULT_GOLD_PATH, CQ evaluation)
- `cq_queries.py` — CQ query templates and deterministic answer-quality scoring
- `answer_benchmark.py` — answer benchmark primitives (e.g. chunk_id, answer_value)
- `answer_scoring.py` — deterministic answer-result scoring (evaluate_result)
- `graph_retrieval.py` — graph retrieval backend
- `live_retrieval.py` — live retrieval backend
- `answer_generation.py` — deterministic GraphRAG answer generation

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

_All ATMONTO/ATCSCC report families are now migrated into subpackages._
