from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from aviation_agentic_ai.cross_source.contracts import (
    CrossSourceState,
    NodeResult,
    TraceEvent,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


@runtime_checkable
class WorkflowNode(Protocol):
    """Small interface shared by the V1 supervisor and a future graph scheduler."""

    node_id: str

    def run(self, state: CrossSourceState) -> NodeResult: ...


NodeHandler = Callable[[CrossSourceState], dict]


@dataclass(frozen=True)
class FunctionWorkflowNode:
    """Adapter for deterministic V1 stage functions."""

    node_id: str
    handler: NodeHandler

    def run(self, state: CrossSourceState) -> NodeResult:
        trace_id = stable_id("node-trace", state.run_id, self.node_id)
        try:
            patch = self.handler(state)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            return NodeResult(
                node_id=self.node_id,
                status="error",
                trace_event=TraceEvent(
                    trace_id=trace_id,
                    node_id=self.node_id,
                    status="error",
                    errors=[message],
                ),
                errors=[message],
            )
        return NodeResult(
            node_id=self.node_id,
            status="success",
            state_patch=patch,
            trace_event=TraceEvent(
                trace_id=trace_id,
                node_id=self.node_id,
                status="success",
                output_summary={"updated_fields": sorted(patch)},
            ),
        )


def apply_node_result(state: CrossSourceState, result: NodeResult) -> CrossSourceState:
    """Validate a node patch and append its trace without mutating input state."""
    if result.node_id != result.trace_event.node_id:
        raise ValueError("NodeResult and TraceEvent node_id values must match")
    protected = {"run_id", "snapshot_set_id"}
    attempted = protected.intersection(result.state_patch)
    if attempted:
        raise ValueError(f"Workflow nodes cannot replace protected state fields: {sorted(attempted)}")

    payload = state.model_dump(mode="python")
    payload.update(result.state_patch)
    payload["trace_events"] = [*state.trace_events, result.trace_event]
    payload["errors"] = [*state.errors, *result.errors]
    return CrossSourceState.model_validate(payload)
