from __future__ import annotations

from importlib import import_module
from typing import Any

import click


TOP_LEVEL_COMMANDS: tuple[dict[str, Any], ...] = (
    {
        "module": "aviation_agentic_ai.cli_web",
        "attribute": "web",
        "name": "web",
        "help": "Local web demo commands.",
        "subcommands": ("serve",),
    },
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
)

REPORT_REGISTRARS: tuple[dict[str, Any], ...] = (
    {
        "module": "aviation_agentic_ai.cli_report_stage",
        "attribute": "register_stage_report_commands",
        "commands": ("stages", "reviews", "generation-runs", "overnight", "hygiene"),
    },
    {
        "module": "aviation_agentic_ai.cli_report_thesis",
        "attribute": "register_thesis_report_commands",
        "commands": (
            "project",
            "thesis-claims",
            "evaluation-protocol",
            "thesis-experiment-dashboard",
            "academic-paper",
            "defense-notes",
            "defense-deck-outline",
            "visual-assets",
        ),
    },
    {
        "module": "aviation_agentic_ai.cli_report_evaluation",
        "attribute": "register_evaluation_report_commands",
        "commands": (
            "hybrid-rag",
            "graphrag-review",
            "evidence-eval",
            "evidence-cards",
            "retrieval-ablation",
            "graph-traversal-ablation",
            "kg-extraction-comparison",
            "answer-eval",
            "sufficiency-eval",
            "triple-semantic-review",
            "robustness",
            "final-evaluation",
        ),
    },
    {
        "module": "aviation_agentic_ai.cli_report_benchmark",
        "attribute": "register_benchmark_report_commands",
        "commands": (
            "benchmark-v2",
            "benchmark-review-pack",
            "benchmark-reviewed-subset",
            "answer-eval-subset",
        ),
    },
    {
        "module": "aviation_agentic_ai.cli_report_llm",
        "attribute": "register_llm_report_commands",
        "commands": (
            "benchmark-llm-review",
            "benchmark-llm-rewrite-proposals",
            "triple-semantic-llm-review",
            "graph-path-llm-review",
            "answer-generation-benchmark-subset",
            "answer-llm-judge",
            "llm-review-consistency",
        ),
    },
    {
        "module": "aviation_agentic_ai.cli_report_nasa",
        "attribute": "register_nasa_report_commands",
        "commands": (
            "nasa-source-discovery",
            "nasa-source-validation",
            "nasa-chunking-summary",
            "ontology-boundary-nasa",
            "nasa-benchmark-summary",
            "nasa-kg-validation",
            "cross-source-ontology-validation",
            "multisource-retrieval-smoke",
        ),
    },
    {
        "module": "aviation_agentic_ai.cli_report_pdf",
        "attribute": "register_pdf_report_commands",
        "commands": ("pdf-extraction-comparison", "pdf-backend-chunking-comparison"),
    },
    {
        "module": "aviation_agentic_ai.cli_report_web",
        "attribute": "register_web_report_commands",
        "commands": ("web-demo-readiness", "web-demo-smoke"),
    },
    {
        "module": "aviation_agentic_ai.cli_report_chunking",
        "attribute": "register_chunking_report_commands",
        "commands": (
            "chunking-comparison",
            "chunking-implementation-audit",
            "chunking-comparison-v2",
            "chunking-topk-sensitivity-v2",
            "chunking-category-analysis-v2",
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
