from __future__ import annotations

from typing import Any

import click

from aviation_agentic_ai.agents.demo import (
    DEFAULT_AGENT_DEMO_QUESTION,
    DEFAULT_AGENT_DEMO_SOURCE_ID,
    run_atcscc_agent_demo,
)


@click.group(name="agent")
def agent() -> None:
    """Agent runtime demonstration commands."""


@agent.command(name="demo")
@click.option(
    "--source-id",
    default=DEFAULT_AGENT_DEMO_SOURCE_ID,
    show_default=True,
    help="ATCSCC advisory source_id to run through the L2 Agent.",
)
@click.option(
    "--question",
    default=DEFAULT_AGENT_DEMO_QUESTION,
    show_default=True,
    help="Retrospective ATCSCC question to answer from extracted facts.",
)
@click.option(
    "--max-iterations",
    default=2,
    show_default=True,
    type=click.IntRange(min=1),
    help="Maximum L1 extractor-validator-repair iterations.",
)
def demo(source_id: str, question: str, max_iterations: int) -> None:
    """Run advisory -> L1 Agent extraction -> L2 routing/retrieval -> cited answer."""
    try:
        result = run_atcscc_agent_demo(
            source_id=source_id,
            question=question,
            max_iterations=max_iterations,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    answer = result.answer
    click.echo("=" * 78)
    click.echo("ATCSCC L2 Agent demo")
    click.echo("=" * 78)
    click.echo(f"source_id: {source_id}")
    click.echo(f"sample_id: {result.advisory.get('sample_id')}")
    click.echo(f"question: {question}")
    click.echo(f"abstain: {str(answer.abstain).lower()}")
    if _is_boundary_abstention(answer.trace.l2_steps):
        click.echo(f"rationale: {answer.rationale}")
        _print_boundary()
        return

    click.echo(f"template_id: {answer.metadata.get('template_id')}")
    click.echo(f"mode: {answer.metadata.get('mode')}")
    click.echo(f"route_confidence: {answer.metadata.get('route_confidence')}")
    click.echo(f"baseline_artifact_facts: {result.baseline_fact_count}")
    click.echo(f"repair_artifact_facts: {result.repair_fact_count}")
    _print_l1_trace(answer.trace.extraction)
    _print_values("answer_values", answer.answer_values)
    _print_citations(answer.citations)
    roles = " -> ".join(str(step.get("role")) for step in answer.trace.l2_steps)
    click.echo(f"l2_steps: {roles}")
    click.echo(f"rationale: {answer.rationale}")
    _print_boundary()


def _print_l1_trace(trace: Any | None) -> None:
    if trace is None:
        click.echo("l1_iterations: 0")
        click.echo("l1_accepted_facts: 0")
        click.echo("l1_blocked_facts: 0")
        return
    click.echo(f"l1_iterations: {trace.iterations_used}")
    click.echo(f"l1_budget_exhausted: {str(trace.budget_exhausted).lower()}")
    click.echo(f"l1_accepted_facts: {len(trace.accepted_identity_keys)}")
    click.echo(f"l1_blocked_facts: {len(trace.blocked_identity_keys)}")


def _is_boundary_abstention(steps: list[dict[str, Any]]) -> bool:
    return [str(step.get("role")) for step in steps] == ["boundary_gate"]


def _print_values(label: str, values: list[str]) -> None:
    click.echo(f"{label}:")
    if not values:
        click.echo("  - (none)")
        return
    for value in values:
        click.echo(f"  - {value}")


def _print_citations(citations: list[dict[str, Any]]) -> None:
    click.echo("citations:")
    if not citations:
        click.echo("  - (none)")
        return
    for citation in citations:
        evidence = _truncate(str(citation.get("evidence_text") or ""), 140)
        click.echo(f"  - {citation.get('fact_id')}: {evidence}")


def _print_boundary() -> None:
    click.echo("Boundary: retrospective, source-bounded diagnostics; not operational ATC support.")
    click.echo("=" * 78)


def _truncate(text: str, limit: int) -> str:
    normalized = " ".join(text.split())
    return normalized if len(normalized) <= limit else normalized[:limit].rstrip() + " ..."
