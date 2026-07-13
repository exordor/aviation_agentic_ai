import pytest

from aviation_agentic_ai.cross_source.contracts import CrossSourceState
from aviation_agentic_ai.cross_source.workflow import (
    FunctionWorkflowNode,
    WorkflowNode,
    apply_node_result,
)


def test_scheduler_neutral_node_returns_validated_state_patch_and_trace() -> None:
    state = CrossSourceState(run_id="run:1", snapshot_set_id="snapshot:1")
    node = FunctionWorkflowNode(
        node_id="cohort_selector",
        handler=lambda _state: {"selected_advisory_ids": ["adv:1", "adv:2"]},
    )

    updated = apply_node_result(state, node.run(state))

    assert isinstance(node, WorkflowNode)
    assert state.selected_advisory_ids == []
    assert updated.selected_advisory_ids == ["adv:1", "adv:2"]
    assert updated.trace_events[0].node_id == "cohort_selector"


def test_workflow_node_cannot_replace_snapshot_identity() -> None:
    state = CrossSourceState(run_id="run:1", snapshot_set_id="snapshot:1")
    node = FunctionWorkflowNode(
        node_id="bad_node",
        handler=lambda _state: {"snapshot_set_id": "snapshot:other"},
    )

    with pytest.raises(ValueError, match="protected state fields"):
        apply_node_result(state, node.run(state))
