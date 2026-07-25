from __future__ import annotations

from importlib import import_module
from typing import Any

import click


TOP_LEVEL_COMMANDS: tuple[dict[str, Any], ...] = (
    {
        "module": "aviation_agentic_ai.cli_chunk",
        "attribute": "chunk_group",
        "name": "chunk",
        "help": "PDF chunking commands.",
        "subcommands": ("build",),
    },
    {
        "module": "aviation_agentic_ai.cli_index",
        "attribute": "index",
        "name": "index",
        "help": "Chunking and vector-index commands.",
        "subcommands": ("build",),
    },
    {
        "module": "aviation_agentic_ai.cli_query",
        "attribute": "query",
        "name": "query",
        "help": "Run a hybrid retrieval query.",
    },
    {
        "module": "aviation_agentic_ai.cli_demo",
        "attribute": "demo",
        "name": "demo",
        "help": "Trace one ATCSCC advisory through extraction -> KG -> KG-RAG answer (offline).",
    },
    {
        "module": "aviation_agentic_ai.cli_agent",
        "attribute": "agent",
        "name": "agent",
        "help": "Agent runtime demonstration commands.",
        "subcommands": ("demo",),
    },
    {
        "module": "aviation_agentic_ai.cli_kg",
        "attribute": "kg",
        "name": "kg",
        "help": "Knowledge graph commands.",
        "subcommands": ("extract", "validate"),
    },
    {
        "module": "aviation_agentic_ai.cli_cqs",
        "attribute": "cqs",
        "name": "cqs",
        "help": "Competency-question gold label utilities.",
        "subcommands": ("gold-draft", "validate-benchmark"),
    },
    {
        "module": "aviation_agentic_ai.cli_ontology",
        "attribute": "ontology",
        "name": "ontology",
        "help": "Ontology lifecycle commands.",
        "subcommands": (
            "validate",
            "report",
            "evaluate",
            "scope",
            "cqs",
            "validate-cqs",
            "generate",
        ),
    },
    {
        "module": "aviation_agentic_ai.cli_source",
        "attribute": "source_group",
        "name": "source",
        "help": "Source ingestion commands.",
        "subcommands": ("ingest-nasa",),
    },
    {
        "module": "aviation_agentic_ai.cli_cross_source",
        "attribute": "cross_source_group",
        "name": "cross-source",
        "help": "Versioned abbreviation alignment and retrospective cross-source QA.",
        "subcommands": (
            "refresh",
            "align",
            "build",
            "neo4j-export",
            "neo4j-load",
            "answer",
            "evaluate",
            "evaluate-mainline",
        ),
    },
    {
        "module": "aviation_agentic_ai.cli_agent_system",
        "attribute": "agent_system",
        "name": "agent-system",
        "help": "Multi-Agent aviation event knowledge system (ingest / neo4j-export / ask).",
        "subcommands": ("ingest", "neo4j-export", "ask"),
    },
)

REPORT_REGISTRARS: tuple[dict[str, Any], ...] = (
    {
        "module": "aviation_agentic_ai.cli_report_stage",
        "attribute": "register_stage_report_commands",
        "commands": ("hygiene",),
    },
    {
        "module": "aviation_agentic_ai.cli_report_thesis",
        "attribute": "register_thesis_report_commands",
        "commands": (
            "thesis-claims",
        ),
    },
    {
        "module": "aviation_agentic_ai.cli_report_nasa",
        "attribute": "register_nasa_report_commands",
        "commands": (
            "nasa-atmonto-cq-evaluation",
            "nasa-atmonto-cq-query-evaluation",
            "nasa-atmonto-answer-generation",
            "nasa-atmonto-agentic-loop",
            "nasa-atmonto-l1-agent-batch",
        ),
    },
)


def _unavailable_message(module: str, error: ImportError) -> str:
    return (
        f"Command module `{module}` is unavailable because an import failed: {error}. "
        "Install the relevant optional dependency group and retry."
    )


def _unavailable_command(name: str, module: str, error: ImportError, help_text: str = "") -> click.Command:
    @click.command(
        name=name,
        help=f"{help_text} Unavailable: {_unavailable_message(module, error)}".strip(),
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    )
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    def command(args: tuple[str, ...]) -> None:
        _ = args
        raise click.ClickException(_unavailable_message(module, error))

    return command


def _unavailable_group(
    name: str,
    module: str,
    error: ImportError,
    help_text: str,
    subcommands: tuple[str, ...],
) -> click.Group:
    @click.group(
        name=name,
        help=f"{help_text} Unavailable: {_unavailable_message(module, error)}",
        invoke_without_command=True,
    )
    @click.pass_context
    def group(ctx: click.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise click.ClickException(_unavailable_message(module, error))

    for subcommand in subcommands:
        group.add_command(_unavailable_command(subcommand, module, error))
    return group


def _load_attribute(module_name: str, attribute: str) -> tuple[Any | None, ImportError | None]:
    try:
        module = import_module(module_name)
    except ImportError as exc:
        return None, exc
    return getattr(module, attribute), None


def _add_unavailable_report_commands(
    report_group: click.Group,
    registrar_spec: dict[str, Any],
    import_error: ImportError,
) -> None:
    for command_name in registrar_spec["commands"]:
        name = str(command_name)
        if name in report_group.commands:
            continue
        report_group.add_command(
            _unavailable_command(
                name,
                str(registrar_spec["module"]),
                import_error,
            )
        )


@click.group()
def main() -> None:
    """Aviation Agentic AI CLI."""


for command_spec in TOP_LEVEL_COMMANDS:
    command, import_error = _load_attribute(
        str(command_spec["module"]),
        str(command_spec["attribute"]),
    )
    if import_error is None:
        main.add_command(command)
        continue
    subcommands = tuple(str(item) for item in command_spec.get("subcommands", ()))
    if subcommands:
        main.add_command(
            _unavailable_group(
                str(command_spec["name"]),
                str(command_spec["module"]),
                import_error,
                str(command_spec["help"]),
                subcommands,
            )
        )
    else:
        main.add_command(
            _unavailable_command(
                str(command_spec["name"]),
                str(command_spec["module"]),
                import_error,
                str(command_spec["help"]),
            )
        )


@main.group()
def report() -> None:
    """Research report commands."""


for registrar_spec in REPORT_REGISTRARS:
    registrar, import_error = _load_attribute(
        str(registrar_spec["module"]),
        str(registrar_spec["attribute"]),
    )
    if import_error is None:
        try:
            registrar(report)
        except ImportError as exc:
            _add_unavailable_report_commands(report, registrar_spec, exc)
        continue
    _add_unavailable_report_commands(report, registrar_spec, import_error)
