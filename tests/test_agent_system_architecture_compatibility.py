"""Characterization coverage for the frozen Batch A legacy compatibility surface."""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.agent_system.agents import (
    FacilityCandidates,
    TermCandidates,
    run_advisory_agent,
    run_facility_agent,
    run_kg_construction_agent,
    run_query_agent,
    run_terminology_agent,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentResult,
    AgentStatus,
    AgentTask,
    EvidenceCard,
    GraphValidationResult,
    GraphPatchBlock,
    QueryToolOutcome,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.formal_graph import (
    write_fact_trace,
    write_profile_gaps,
)
from aviation_agentic_ai.agent_system.materialize import materialize_graph_patch
from aviation_agentic_ai.agent_system.prompts import load_prompt_catalog
from aviation_agentic_ai.agent_system.runtime import write_run_manifest
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot_registry,
    write_source_snapshot_registry,
)
from aviation_agentic_ai.agent_system.workflow import IngestState, build_ingest_graph
from aviation_agentic_ai.cli_agent_system import agent_system
from aviation_agentic_ai.cross_source.identifiers import stable_id


LEGACY_AGENT_STATUS_VALUES = {
    "resolved",
    "abstain",
    "profile_gap",
    "blocked",
}

LEGACY_INGEST_NODES = {
    "advisory",
    "facility",
    "terminology",
    "join",
    "kg_construction",
    "materialize",
    "decision_context",
}

LEGACY_CLI_COMMANDS = {
    "ingest",
    "neo4j-export",
    "ask",
}

FUTURE_THREE_AGENT_ROLE_MARKERS = {
    "three-agent",
    "three_agent",
    "semantic resolution agent",
    "semantic-resolution-agent",
    "semantic_resolution",
    "semantic_resolution_agent",
    "decision case assembly agent",
    "decision-case-assembly-agent",
    "decision_case_assembly",
    "decision_case_assembly_agent",
    "decision case analysis agent",
    "decision-case-analysis-agent",
    "decision_case_analysis",
    "decision_case_analysis_agent",
}


def test_core_run_artifact_writers_preserve_filenames(tmp_path) -> None:
    """Catches a rename in a run-artifact writer, not merely manifest metadata."""

    source = SourceRecord(
        source_id="source",
        family=SourceFamily.ATCSCC_ADVISORY,
        content="GROUND DELAY PROGRAM",
    )
    guide = load_schema_guide()
    event_class = "atm:GroundDelayProgramTMI"
    event_uri = stable_id("evt", source.source_id, event_class)
    materialization = materialize_graph_patch(
        graph_patch_raw=(
            f"GRAPH_PATCH\n{event_uri} | rdf:type | {event_class} | {source.source_id}\n"
        ),
        advisory_source_id=source.source_id,
        event_class=event_class,
        guide=guide,
        known_source_ids={source.source_id},
        output_dir=tmp_path,
    )
    snapshots = build_source_snapshot_registry([source])
    source_snapshots_path = write_source_snapshot_registry(snapshots, tmp_path)
    fact_trace_path = write_fact_trace(
        result=GraphValidationResult(),
        block=GraphPatchBlock(),
        evidence_cards=[],
        source_snapshot=snapshots,
        output_dir=tmp_path,
    )
    profile_gaps_path = write_profile_gaps(
        result=GraphValidationResult(),
        event_id=event_uri,
        source_snapshot=snapshots,
        output_dir=tmp_path,
    )
    manifest_path = write_run_manifest(
        run_dir=tmp_path,
        source_id=source.source_id,
        model_calls=[],
        materialization=materialization,
        schema_slice_id=guide.schema_slice_id,
        schema_checksum=guide.checksum,
        evidence_cards=[],
        graph_patch_raw=None,
        prompt_set_id="prompts",
        profile_gap_count=0,
    )

    assert {
        Path(path).name
        for path in (
            materialization.jsonl_path,
            materialization.ttl_path,
            materialization.nodes_path,
            materialization.relationships_path,
            source_snapshots_path,
            fact_trace_path,
            profile_gaps_path,
            manifest_path,
        )
    } == {
        "fact_trace.jsonl",
        "kg.jsonl",
        "kg.ttl",
        "neo4j_nodes.jsonl",
        "neo4j_relationships.jsonl",
        "profile_gaps.jsonl",
        "run_manifest.json",
        "source_snapshots.jsonl",
    }


def test_legacy_agent_statuses_and_public_agent_signatures_are_frozen() -> None:
    """Catches a migration that renames a legacy status or public parameter."""

    assert {status.value for status in AgentStatus} == LEGACY_AGENT_STATUS_VALUES

    signatures = {
        "run_advisory_agent": inspect.signature(run_advisory_agent),
        "run_facility_agent": inspect.signature(run_facility_agent),
        "run_terminology_agent": inspect.signature(run_terminology_agent),
        "run_kg_construction_agent": inspect.signature(run_kg_construction_agent),
        "run_query_agent": inspect.signature(run_query_agent),
    }
    expected = {
        "run_advisory_agent": (
            ("task", "advisory", "event_classes", "mentions", "model_invoker"),
            {"model_invoker": None},
        ),
        "run_facility_agent": (
            ("task", "candidates", "model_invoker"),
            {"model_invoker": None},
        ),
        "run_terminology_agent": (
            ("task", "candidates", "model_invoker"),
            {"model_invoker": None},
        ),
        "run_kg_construction_agent": (
            ("task", "inputs", "tool_model_factory"),
            {"tool_model_factory": None},
        ),
        "run_query_agent": (
            (
                "task",
                "question",
                "evidence",
                "ontology_labels",
                "model_invoker",
                "insufficient_answer",
            ),
            {"insufficient_answer": "Insufficient graph evidence."},
        ),
    }

    for name, signature in signatures.items():
        expected_names, expected_defaults = expected[name]
        parameters = list(signature.parameters.values())
        assert tuple(parameter.name for parameter in parameters) == expected_names
        assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters)
        assert {
            parameter.name: parameter.default
            for parameter in parameters
            if parameter.default is not inspect.Parameter.empty
        } == expected_defaults


def test_legacy_contract_json_keys_are_frozen() -> None:
    """Catches removal or renaming of fields persisted across legacy envelopes."""

    card = EvidenceCard(agent_role="advisory", status=AgentStatus.RESOLVED)
    task = AgentTask(run_id="run", source_id="source", objective="characterize")
    result = AgentResult(status=AgentStatus.RESOLVED, evidence_card=card)
    patch = GraphPatchBlock()
    query_outcome = QueryToolOutcome(status="insufficient")

    assert set(card.model_dump(mode="json")) == {
        "agent_role",
        "status",
        "claims",
        "canonical_refs",
        "source_ids",
        "uncertainties",
        "tool_trace",
        "decision_basis",
    }
    assert set(task.model_dump(mode="json")) == {
        "run_id",
        "source_id",
        "objective",
        "context_refs",
        "allowed_tools",
        "schema_slice_id",
    }
    assert set(result.model_dump(mode="json")) == {
        "status",
        "artifact_ref",
        "evidence_card",
        "failure_reason",
        "model_calls",
        "graph_patch",
    }
    assert set(patch.model_dump(mode="json")) == {"patch_lines", "profile_gaps", "raw"}
    assert set(query_outcome.model_dump(mode="json")) == {
        "status",
        "answer",
        "source_ids",
        "retrieved_fact_ids",
        "retrieved_profile_gap_ids",
        "retrieved_context_association_ids",
        "retrieved_outcome_summary_ids",
        "retrieved_observation_ids",
        "retrieved_derivation_ids",
        "model_calls",
        "tool_calls",
        "failure_reason",
    }


def test_legacy_workflow_catalog_and_cli_surface_remain_loadable(tmp_path) -> None:
    """Catches a topology, prompt-role catalog, or CLI command migration."""

    graph = build_ingest_graph()
    assert set(graph.get_graph().nodes) - {"__start__", "__end__"} == LEGACY_INGEST_NODES
    assert {
        "advisory",
        "facility",
        "terminology",
        "knowledge_graph_construction",
        "query",
    }.issubset(load_prompt_catalog().roles)

    runner = CliRunner()
    root_help = runner.invoke(agent_system, ["--help"])
    assert root_help.exit_code == 0
    assert set(agent_system.commands) == LEGACY_CLI_COMMANDS
    for command in sorted(LEGACY_CLI_COMMANDS):
        result = runner.invoke(agent_system, [command, "--help"])
        assert result.exit_code == 0

    manifest_path = write_run_manifest(
        run_dir=tmp_path,
        source_id="source",
        model_calls=[],
        materialization=None,
        schema_slice_id="slice",
        schema_checksum="0" * 64,
        evidence_cards=[EvidenceCard(agent_role="advisory", status=AgentStatus.RESOLVED)],
        graph_patch_raw=None,
        prompt_set_id="prompts",
        profile_gap_count=0,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert set(manifest) == {
        "run_id",
        "source_id",
        "created_at",
        "prompt_set_id",
        "prompt_catalog",
        "frozen_model",
        "schema_slice_id",
        "schema_checksum",
        "provider_calls",
        "provider_attempts",
        "provider_successes",
        "input_tokens",
        "output_tokens",
        "model_calls",
        "materialization",
        "profile_gaps",
        "context_artifacts",
        "formal_layers",
        "public_observation_publication",
        "evidence_cards",
        "graph_patch_raw",
    }
    assert manifest_path.name == "run_manifest.json"
    assert manifest["profile_gaps"]["path"] == "profile_gaps.jsonl"
    cli_surface = "\n".join(
        [
            root_help.output,
            *[
                runner.invoke(agent_system, [command, "--help"]).output
                for command in sorted(LEGACY_CLI_COMMANDS)
            ],
        ]
    ).lower()
    persisted_surface = json.dumps(manifest).lower()
    workflow_state_surface = "\n".join(IngestState.__annotations__).lower()
    for marker in FUTURE_THREE_AGENT_ROLE_MARKERS:
        assert marker not in cli_surface
        assert marker not in persisted_surface
        assert marker not in workflow_state_surface


def test_unique_authority_paths_make_zero_provider_calls() -> None:
    """Catches a migration that sends uniquely resolved authority records to a provider."""

    class FacilityType(Enum):
        AIRPORT = "airport"

    @dataclass
    class Facility:
        entity_id: str
        preferred_label: str
        entity_type: FacilityType

    class TermCategory(Enum):
        TRAFFIC_MANAGEMENT_INITIATIVE = "traffic_management_initiative"

    @dataclass
    class Term:
        term_id: str
        preferred_label: str
        abbreviation: str
        term_category: TermCategory

    calls: list[str] = []

    def unexpected_provider(role: str, variables: dict[str, object]):
        calls.append(role)
        raise AssertionError(f"unique {role} resolution called the provider")

    facility_task = AgentTask(
        run_id="run",
        source_id="source",
        objective="resolve facility",
        allowed_tools=["lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias"],
    )
    facility_result = run_facility_agent(
        task=facility_task,
        candidates=FacilityCandidates(
            mention="JFK",
            candidates=[
                Facility(
                    entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
                    preferred_label="John F. Kennedy International Airport",
                    entity_type=FacilityType.AIRPORT,
                )
            ],
            source_id="source",
            advisory_evidence="CTL ELEMENT: JFK",
        ),
        model_invoker=unexpected_provider,
    )
    terminology_task = AgentTask(
        run_id="run",
        source_id="source",
        objective="resolve terminology",
        allowed_tools=[
            "lookup_faa_glossary",
            "lookup_pcg_term",
            "resolve_term_registry",
            "resolve_schema_event_class",
        ],
    )
    terminology_result = run_terminology_agent(
        task=terminology_task,
        candidates=TermCandidates(
            mention="GDP",
            candidates=[
                Term(
                    term_id="urn:aviation-agentic-ai:term:ground_delay_program",
                    preferred_label="Ground Delay Program",
                    abbreviation="GDP",
                    term_category=TermCategory.TRAFFIC_MANAGEMENT_INITIATIVE,
                )
            ],
            source_id="source",
            guide=load_schema_guide(),
            advisory_evidence="GDP",
        ),
        model_invoker=unexpected_provider,
    )

    assert facility_result.status is AgentStatus.RESOLVED
    assert terminology_result.status is AgentStatus.RESOLVED
    assert facility_result.model_calls == []
    assert terminology_result.model_calls == []
    assert calls == []
