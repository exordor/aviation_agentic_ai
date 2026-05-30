from __future__ import annotations

import click

from aviation_agentic_ai.cli_chunk import chunk_group
from aviation_agentic_ai.cli_cqs import cqs
from aviation_agentic_ai.cli_index import index
from aviation_agentic_ai.cli_kg import kg
from aviation_agentic_ai.cli_ontology import ontology
from aviation_agentic_ai.cli_query import query
from aviation_agentic_ai.cli_report_benchmark import register_benchmark_report_commands
from aviation_agentic_ai.cli_report_chunking import register_chunking_report_commands
from aviation_agentic_ai.cli_report_evaluation import register_evaluation_report_commands
from aviation_agentic_ai.cli_report_llm import register_llm_report_commands
from aviation_agentic_ai.cli_report_stage import register_stage_report_commands
from aviation_agentic_ai.cli_report_thesis import register_thesis_report_commands
from aviation_agentic_ai.cli_report_web import register_web_report_commands
from aviation_agentic_ai.cli_web import web


@click.group()
def main() -> None:
    """Aviation Agentic AI CLI."""


main.add_command(web)
main.add_command(chunk_group)
main.add_command(index)
main.add_command(query)
main.add_command(kg)
main.add_command(cqs)
main.add_command(ontology)


@main.group()
def report() -> None:
    """Research report commands."""


register_stage_report_commands(report)
register_thesis_report_commands(report)
register_evaluation_report_commands(report)
register_benchmark_report_commands(report)
register_llm_report_commands(report)


register_web_report_commands(report)
register_chunking_report_commands(report)
