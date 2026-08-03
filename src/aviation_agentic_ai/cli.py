from __future__ import annotations

from importlib import import_module
from typing import Any

import click


TOP_LEVEL_COMMANDS: tuple[dict[str, Any], ...] = (
    {
        "module": "aviation_agentic_ai.cli_agent_system",
        "attribute": "agent_system",
        "name": "agent-system",
        "help": (
            "Ingestion-first aviation HybridRAG knowledge system "
            "(ingest / reindex / ask / build-kg / neo4j-export / "
            "export-event)."
        ),
        "subcommands": (
            "ingest",
            "reindex",
            "ask",
            "build-kg",
            "neo4j-export",
            "export-event",
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


@click.group()
def main() -> None:
    """Supported Aviation Agentic AI runtime CLI."""


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
