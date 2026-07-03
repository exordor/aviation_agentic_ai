import importlib
import sys
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main


def test_cli_help_survives_optional_command_import_failure(monkeypatch) -> None:
    real_import_module = importlib.import_module

    def fake_import_module(name: str, *args, **kwargs):
        if name == "aviation_agentic_ai.cli_index":
            raise ImportError("chromadb unavailable")
        return real_import_module(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    sys.modules.pop("aviation_agentic_ai.cli", None)
    try:
        cli_module = real_import_module("aviation_agentic_ai.cli")
        help_result = CliRunner().invoke(cli_module.main, ["--help"])
        unavailable_result = CliRunner().invoke(cli_module.main, ["index", "build"])
    finally:
        sys.modules.pop("aviation_agentic_ai.cli", None)
        monkeypatch.setattr(importlib, "import_module", real_import_module)
        real_import_module("aviation_agentic_ai.cli")

    assert help_result.exit_code == 0
    assert unavailable_result.exit_code != 0
    assert "unavailable because an import failed" in unavailable_result.output


def test_cli_chunk_build_uses_default_command_shape(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_chunk

    def fake_build_chunk_file(*_args, **_kwargs):
        output = tmp_path / "chunks.jsonl"
        output.write_text("", encoding="utf-8")
        chunk = type("Chunk", (), {"page": 0})()
        return output, [chunk]

    monkeypatch.setattr(cli_chunk, "build_chunk_file", fake_build_chunk_file)

    result = CliRunner().invoke(
        main,
        ["chunk", "build", "--output", str(tmp_path / "chunks.jsonl")],
    )

    assert result.exit_code == 0, result.output
    assert "with 1 fixed_window chunks" in result.output


def test_cli_index_build_uses_mocked_builder(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_index

    monkeypatch.setattr(
        cli_index,
        "build_chroma_index",
        lambda *_args, **_kwargs: {
            "chunks_indexed": 2,
            "collection_name": "test_collection",
            "index_dir": "data/indexes/chroma",
        },
    )

    result = CliRunner().invoke(
        main,
        [
            "index",
            "build",
            "--chunks",
            str(tmp_path / "chunks.jsonl"),
            "--index-dir",
            str(tmp_path / "chroma"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Indexed 2 chunks" in result.output


def test_cli_query_uses_mocked_runner(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_query

    monkeypatch.setattr(
        cli_query,
        "run_query",
        lambda *_args, **_kwargs: {"answer": "Grounded answer. Citations: doc-p00-c00"},
    )

    result = CliRunner().invoke(
        main,
        [
            "query",
            "What affects lift?",
            "--chunks",
            str(tmp_path / "chunks.jsonl"),
            "--kg-file",
            str(tmp_path / "kg.jsonl"),
            "--index-dir",
            str(tmp_path / "chroma"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Grounded answer" in result.output


def test_cli_kg_extract_uses_configured_token_budget(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_kg

    calls = {}

    def fake_extract_kg_file(*_args, **kwargs):
        calls.update(kwargs)
        return tmp_path / "kg.jsonl", [object()], {"errors_total": 0}

    monkeypatch.setattr(cli_kg, "extract_kg_file", fake_extract_kg_file)

    result = CliRunner().invoke(
        main,
        [
            "kg",
            "extract",
            "--chunks",
            str(tmp_path / "chunks.jsonl"),
            "--output",
            str(tmp_path / "kg.jsonl"),
            "--profile",
            str(tmp_path / "profile.yaml"),
            "--ontology-file",
            str(tmp_path / "ontology.ttl"),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls["temperature"] == 0.0
    assert calls["max_tokens"] == 4096


def test_cli_kg_extract_max_tokens_override(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_kg

    calls = {}

    def fake_extract_kg_file(*_args, **kwargs):
        calls.update(kwargs)
        return tmp_path / "kg.jsonl", [object()], {"errors_total": 0}

    monkeypatch.setattr(cli_kg, "extract_kg_file", fake_extract_kg_file)

    result = CliRunner().invoke(
        main,
        [
            "kg",
            "extract",
            "--chunks",
            str(tmp_path / "chunks.jsonl"),
            "--output",
            str(tmp_path / "kg.jsonl"),
            "--profile",
            str(tmp_path / "profile.yaml"),
            "--ontology-file",
            str(tmp_path / "ontology.ttl"),
            "--max-tokens",
            "7000",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls["max_tokens"] == 7000


def test_cli_kg_extract_can_write_ttl_export(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_kg

    calls = {}

    def fake_extract_kg_file(*_args, **kwargs):
        calls.update(kwargs)
        return tmp_path / "kg.jsonl", [object()], {"errors_total": 0}

    def fake_write_kg_ttl(_triples, output_path):
        output_path.write_text("@prefix : <http://example.org/> .\n", encoding="utf-8")
        return output_path

    monkeypatch.setattr(cli_kg, "extract_kg_file", fake_extract_kg_file)
    monkeypatch.setattr(cli_kg, "write_kg_ttl", fake_write_kg_ttl)

    result = CliRunner().invoke(
        main,
        [
            "kg",
            "extract",
            "--chunks",
            str(tmp_path / "chunks.jsonl"),
            "--output",
            str(tmp_path / "kg.jsonl"),
            "--profile",
            str(tmp_path / "profile.yaml"),
            "--ontology-file",
            str(tmp_path / "ontology.ttl"),
            "--ttl-output",
            str(tmp_path / "kg.ttl"),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "kg.ttl" in result.output


def test_cli_kg_validate_passes_report_name(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_kg

    calls = {}

    def fake_validate_kg_file(*_args, **_kwargs):
        return {
            "valid": True,
            "kg_path": "data/kg/test.jsonl",
            "chunks_path": "data/chunks/test.jsonl",
            "profile_path": "configs/extraction_profile.yaml",
            "ontology_path": "data/ontology/curated/test.ttl",
            "triples_total": 1,
            "errors_total": 0,
            "errors": [],
        }

    def fake_write_reports(_report, output_dir, *, report_name):
        calls["report_name"] = report_name
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        json_path = output / f"{report_name}.json"
        md_path = output / f"{report_name}.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path

    monkeypatch.setattr(cli_kg, "validate_kg_file", fake_validate_kg_file)
    monkeypatch.setattr(cli_kg, "write_kg_validation_reports", fake_write_reports)

    result = CliRunner().invoke(
        main,
        [
            "kg",
            "validate",
            "--output-dir",
            str(tmp_path),
            "--report-name",
            "structure_aware_kg_validation",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls["report_name"] == "structure_aware_kg_validation"


def test_cli_cqs_gold_draft_uses_mocked_builder(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_cqs

    def fake_builder(*_args, output_path, **_kwargs):
        output_path.write_text('{"labels": []}\n', encoding="utf-8")
        return {"labels": [{}, {}]}

    monkeypatch.setattr(cli_cqs, "build_gold_draft", fake_builder)

    result = CliRunner().invoke(
        main,
        [
            "cqs",
            "gold-draft",
            "--chunks",
            str(tmp_path / "chunks.jsonl"),
            "--output",
            str(tmp_path / "gold.json"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Drafted 2 gold labels" in result.output


def test_cli_cqs_validate_benchmark_uses_mocked_validator(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_cqs

    calls = {}

    def fake_validate_benchmark(label_path, chunk_inputs, *, min_labels):
        calls["label_path"] = label_path
        calls["chunk_inputs"] = chunk_inputs
        calls["min_labels"] = min_labels
        return {
            "valid": True,
            "warnings_total": 0,
            "metadata": {
                "labels_total": 120,
                "supported_total": 100,
                "no_answer_total": 20,
            },
        }

    monkeypatch.setattr(cli_cqs, "validate_benchmark", fake_validate_benchmark)

    result = CliRunner().invoke(
        main,
        [
            "cqs",
            "validate-benchmark",
            "--gold-labels",
            str(tmp_path / "benchmark.json"),
            "--min-labels",
            "100",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls["min_labels"] == 100
    assert "validated 120 benchmark labels" in result.output


def test_cli_report_nasa_atmonto_answer_generation_uses_mocked_writer(
    tmp_path: Path, monkeypatch
) -> None:
    from aviation_agentic_ai import cli_report_nasa

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "nasa_atmonto_answer_generation.json"
        md_path = tmp_path / "nasa_atmonto_answer_generation.md"
        benchmark_path = tmp_path / "atcscc_answer_eval_benchmark.json"
        chapter_path = tmp_path / "nasa_atmonto_experiment_chapter_draft.md"
        for path in (json_path, md_path, benchmark_path, chapter_path):
            path.write_text("{}\n", encoding="utf-8")
        return (
            json_path,
            md_path,
            benchmark_path,
            chapter_path,
            {"metadata": {"benchmark_label_count": 6}, "critic_gate": {"rejected_fact_count": 1}},
        )

    monkeypatch.setattr(cli_report_nasa, "write_nasa_atmonto_answer_generation", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "nasa-atmonto-answer-generation",
            "--output-dir",
            str(tmp_path),
            "--benchmark-path",
            str(tmp_path / "benchmark.json"),
            "--chapter-path",
            str(tmp_path / "chapter.md"),
            "--max-cases-per-template",
            "1",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Generated 6 ATCSCC answer-eval labels" in result.output
    assert "critic-gate rejected 1 S4 facts" in result.output


def test_cli_report_evaluation_protocol_uses_mocked_writer(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli_report_thesis

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "evaluation_protocol_review.json"
        md_path = tmp_path / "evaluation_protocol_review.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"missing_or_pending_metrics": [{}, {}]}

    monkeypatch.setattr(cli_report_thesis, "write_evaluation_protocol_review", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "evaluation-protocol",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "pending gaps: 2" in result.output
