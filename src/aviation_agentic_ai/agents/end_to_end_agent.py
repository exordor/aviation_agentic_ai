from __future__ import annotations

from typing import Any

from aviation_agentic_ai.agents.extraction_agent import AgentInvoker, ExtractionAgent
from aviation_agentic_ai.agents.types import EndToEndAnswer, EndToEndTrace
from aviation_agentic_ai.ontology.atmonto_experiment import term_name
from aviation_agentic_ai.reporting.atmonto.core.answer_scoring import (
    ROUTED_TEMPLATE_MODES,
)
from aviation_agentic_ai.reporting.io import normalize_report_text


QUESTION_TEMPLATE_PREDICATES: dict[str, tuple[str, ...]] = {
    "QT-Q01-AFFECTED-NAS-ELEMENTS": ("controlledNASelement",),
    "QT-Q01-CAUSE-CONDITION": ("impactingCondition",),
    "QT-Q01-TIME-WINDOW": ("effectiveStartTime", "effectiveEndTime", "issuedTime"),
    "QT-Q01-STATUS-ACTION": ("implementationStatus", "extensionProbability", "initiativeComments"),
    "QT-Q01-ROUTE-SEMANTICS": ("reRouteType", "allowedRoute", "reRouteReason"),
}


class ATCSCCEndToEndAgent:
    """Minimal L2 runtime over one retrospective ATCSCC advisory.

    The MVP intentionally stays extractive and source-bounded: it composes the
    L1 extraction loop with deterministic routing/retrieval and does not create
    new scored experiment claims.
    """

    def __init__(
        self,
        *,
        schema_slice: dict[str, Any],
        route_map: dict[str, dict[str, set[str]]] | None = None,
        max_iterations: int = 2,
    ) -> None:
        self.schema_slice = schema_slice
        self.route_map = route_map or {}
        self.extraction = ExtractionAgent(
            schema_slice=schema_slice,
            route_map=route_map,
            max_iterations=max_iterations,
        )

    def process(
        self,
        advisory: dict[str, Any],
        *,
        question: str,
        invoker: AgentInvoker | None = None,
        invoker_label: str = "default",
        progress: bool = False,
    ) -> EndToEndAnswer:
        trace = EndToEndTrace()
        boundary = self._boundary_gate(question)
        trace.l2_steps.append(
            {
                "role": "boundary_gate",
                "input_summary": {"question": question},
                "output_summary": boundary,
                "raw_response_len": 0,
            }
        )
        if boundary["abstain"]:
            return EndToEndAnswer(
                question=question,
                answer="",
                answer_values=[],
                citations=[],
                abstain=True,
                rationale=boundary["reason"],
                trace=trace,
                metadata={
                    "system_id": "L2_atcscc_agentic_kg_rag",
                    "source_id": advisory.get("source_id"),
                    "live_llm_run": invoker is None,
                    "invoker_label": invoker_label,
                },
            )

        extraction_result = self.extraction.run(
            advisory,
            invoker=invoker,
            invoker_label=invoker_label,
            progress=progress,
        )
        trace.extraction = extraction_result.trace

        route = self._route_question(question)
        trace.l2_steps.append(
            {
                "role": "router",
                "input_summary": {"question": question},
                "output_summary": route,
                "raw_response_len": 0,
            }
        )
        retrieval = self._retrieve(
            facts=extraction_result.facts,
            template_id=route["template_id"],
            question=question,
        )
        trace.l2_steps.append(
            {
                "role": "retriever",
                "input_summary": {
                    "fact_count": len(extraction_result.facts),
                    "template_id": route["template_id"],
                },
                "output_summary": {
                    "retrieved_fact_count": len(retrieval),
                    "predicates": sorted({item["predicate"] for item in retrieval}),
                },
                "raw_response_len": 0,
            }
        )
        answer_values = [_fact_answer_value(item["fact"]) for item in retrieval]
        citations = [
            {
                "source_id": str(advisory.get("source_id") or ""),
                "fact_id": item["fact"].get("fact_id"),
                "evidence_text": item["fact"].get("evidence_text", ""),
            }
            for item in retrieval
        ]
        answer = ", ".join(answer_values)
        trace.l2_steps.append(
            {
                "role": "answerer",
                "input_summary": {"retrieved_fact_count": len(retrieval)},
                "output_summary": {"answer_values": answer_values},
                "raw_response_len": 0,
            }
        )
        abstain = not answer_values
        rationale = (
            "No source-bounded facts matched the routed ATCSCC question."
            if abstain
            else "Answered from L1 accepted facts with copied evidence spans."
        )
        trace.l2_steps.append(
            {
                "role": "self_eval",
                "input_summary": {"answer_values": answer_values, "citation_count": len(citations)},
                "output_summary": {"abstain": abstain, "rationale": rationale},
                "raw_response_len": 0,
            }
        )
        return EndToEndAnswer(
            question=question,
            answer=answer,
            answer_values=answer_values,
            citations=citations,
            abstain=abstain,
            rationale=rationale,
            trace=trace,
            metadata={
                "system_id": "L2_atcscc_agentic_kg_rag",
                "source_id": advisory.get("source_id"),
                "template_id": route["template_id"],
                "mode": route["mode"],
                "route_confidence": route["route_confidence"],
                "live_llm_run": invoker is None,
                "invoker_label": invoker_label,
            },
        )

    def _boundary_gate(self, question: str) -> dict[str, Any]:
        normalized = normalize_report_text(question).lower()
        live_markers = ("right now", "currently", "live", "should i", "should we", "real time")
        if any(marker in normalized for marker in live_markers):
            return {
                "abstain": True,
                "reason": "Question requests live operational decision support outside retrospective ATCSCC scope.",
            }
        return {"abstain": False, "reason": "retrospective_atcscc_scope"}

    def _route_question(self, question: str) -> dict[str, Any]:
        normalized = normalize_report_text(question).lower()
        if any(token in normalized for token in ("cause", "condition", "weather", "why")):
            template_id = "QT-Q01-CAUSE-CONDITION"
            confidence = "high"
        elif any(token in normalized for token in ("affected", "airport", "airspace", "element", "nas")):
            template_id = "QT-Q01-AFFECTED-NAS-ELEMENTS"
            confidence = "high"
        elif any(token in normalized for token in ("time", "start", "end", "effective")):
            template_id = "QT-Q01-TIME-WINDOW"
            confidence = "medium"
        else:
            template_id = "unknown_template"
            confidence = "low"
        return {
            "template_id": template_id,
            "mode": ROUTED_TEMPLATE_MODES.get(template_id, "hybrid_graphrag"),
            "route_confidence": confidence,
        }

    def _retrieve(
        self,
        *,
        facts: list[dict[str, Any]],
        template_id: str,
        question: str,
    ) -> list[dict[str, Any]]:
        predicates = QUESTION_TEMPLATE_PREDICATES.get(template_id)
        if predicates is None:
            question_tokens = set(normalize_report_text(question).lower().split())
            predicates = tuple(
                term_name(fact.get("predicate"))
                for fact in facts
                if question_tokens & set(normalize_report_text(_fact_answer_value(fact)).lower().split())
            )
        wanted = set(predicates)
        retrieved: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for fact in facts:
            predicate = term_name(fact.get("predicate"))
            if predicate not in wanted:
                continue
            key = (predicate, _fact_answer_value(fact))
            if key in seen:
                continue
            seen.add(key)
            retrieved.append({"predicate": predicate, "fact": fact})
        return retrieved


def _fact_answer_value(fact: dict[str, Any]) -> str:
    if fact.get("object_label") not in (None, ""):
        return str(fact["object_label"])
    if fact.get("value") not in (None, ""):
        return str(fact["value"])
    if fact.get("object") not in (None, ""):
        return str(fact["object"])
    return ""
