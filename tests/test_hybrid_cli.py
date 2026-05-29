from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main


def test_cli_chunk_build_uses_default_command_shape(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_build_chunk_file(*_args, **_kwargs):
        output = tmp_path / "chunks.jsonl"
        output.write_text("", encoding="utf-8")
        chunk = type("Chunk", (), {"page": 0})()
        return output, [chunk]

    monkeypatch.setattr(cli, "build_chunk_file", fake_build_chunk_file)

    result = CliRunner().invoke(
        main,
        ["chunk", "build", "--output", str(tmp_path / "chunks.jsonl")],
    )

    assert result.exit_code == 0, result.output
    assert "with 1 fixed_window chunks" in result.output


def test_cli_index_build_uses_mocked_builder(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    monkeypatch.setattr(
        cli,
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
    from aviation_agentic_ai import cli

    monkeypatch.setattr(
        cli,
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
    from aviation_agentic_ai import cli

    calls = {}

    def fake_extract_kg_file(*_args, **kwargs):
        calls.update(kwargs)
        return tmp_path / "kg.jsonl", [object()], {"errors_total": 0}

    monkeypatch.setattr(cli, "extract_kg_file", fake_extract_kg_file)

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
    from aviation_agentic_ai import cli

    calls = {}

    def fake_extract_kg_file(*_args, **kwargs):
        calls.update(kwargs)
        return tmp_path / "kg.jsonl", [object()], {"errors_total": 0}

    monkeypatch.setattr(cli, "extract_kg_file", fake_extract_kg_file)

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
    from aviation_agentic_ai import cli

    calls = {}

    def fake_extract_kg_file(*_args, **kwargs):
        calls.update(kwargs)
        return tmp_path / "kg.jsonl", [object()], {"errors_total": 0}

    def fake_write_kg_ttl(_triples, output_path):
        output_path.write_text("@prefix : <http://example.org/> .\n", encoding="utf-8")
        return output_path

    monkeypatch.setattr(cli, "extract_kg_file", fake_extract_kg_file)
    monkeypatch.setattr(cli, "write_kg_ttl", fake_write_kg_ttl)

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
    from aviation_agentic_ai import cli

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

    monkeypatch.setattr(cli, "validate_kg_file", fake_validate_kg_file)
    monkeypatch.setattr(cli, "write_kg_validation_reports", fake_write_reports)

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


def test_cli_report_chunking_comparison_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "chunking_comparison.json"
        md_path = tmp_path / "chunking_comparison.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return (
            json_path,
            md_path,
            {"ranking": [{"strategy": "fixed_window"}], "strategies": {"fixed_window": {}}},
        )

    monkeypatch.setattr(cli, "write_chunking_comparison", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "chunking-comparison",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Compared 1 chunking strategies" in result.output


def test_cli_report_hybrid_rag_passes_report_name(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    calls = {}

    def fake_writer(*_args, **kwargs):
        calls["report_name"] = kwargs["report_name"]
        json_path = tmp_path / f"{kwargs['report_name']}.json"
        md_path = tmp_path / f"{kwargs['report_name']}.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"questions_total": 2}}

    monkeypatch.setattr(cli, "write_hybrid_rag_experiment", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "hybrid-rag",
            "--output-dir",
            str(tmp_path),
            "--report-name",
            "hybrid_rag_structure_aware",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls["report_name"] == "hybrid_rag_structure_aware"
    assert "Evaluated 2 boundary CQs" in result.output


def test_cli_report_graphrag_review_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **kwargs):
        json_path = tmp_path / f"{kwargs['report_name']}.json"
        md_path = tmp_path / f"{kwargs['report_name']}.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return (
            json_path,
            md_path,
            {"metadata": {"structure_aware_present": False, "evidence_eval_present": False}},
        )

    monkeypatch.setattr(cli, "write_graphrag_review", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "graphrag-review",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Reviewed GraphRAG reports" in result.output


def test_cli_cqs_gold_draft_uses_mocked_builder(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_builder(*_args, output_path, **_kwargs):
        output_path.write_text('{"labels": []}\n', encoding="utf-8")
        return {"labels": [{}, {}]}

    monkeypatch.setattr(cli, "build_gold_draft", fake_builder)

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
    from aviation_agentic_ai import cli

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

    monkeypatch.setattr(cli, "validate_benchmark", fake_validate_benchmark)

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


def test_cli_report_evidence_eval_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "evidence_level_evaluation.json"
        md_path = tmp_path / "evidence_level_evaluation.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"labels_total": 10}}

    monkeypatch.setattr(cli, "write_evidence_level_evaluation", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "evidence-eval",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Evaluated evidence-level metrics for 10 CQs" in result.output


def test_cli_report_retrieval_ablation_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "retrieval_ablation.json"
        md_path = tmp_path / "retrieval_ablation.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"scenarios_total": 3, "questions_total": 2}}

    monkeypatch.setattr(cli, "write_retrieval_ablation", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "retrieval-ablation",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Evaluated 3 retrieval ablation scenarios" in result.output


def test_cli_report_benchmark_v2_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "benchmark_v2_summary.json"
        md_path = tmp_path / "benchmark_v2_summary.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return (
            json_path,
            md_path,
            {
                "metadata": {"labels_total": 120},
                "validation": {"valid": True},
            },
        )

    monkeypatch.setattr(cli, "write_benchmark_v2_summary", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "benchmark-v2",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Summarized 120 benchmark labels" in result.output


def test_cli_report_kg_extraction_comparison_uses_mocked_writer(
    tmp_path: Path, monkeypatch
) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "kg_extraction_comparison.json"
        md_path = tmp_path / "kg_extraction_comparison.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"experiments": {"fixed_window": {}, "structure_aware": {}}}

    monkeypatch.setattr(cli, "write_kg_extraction_comparison", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "kg-extraction-comparison",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Compared 2 KG extraction artifacts" in result.output


def test_cli_report_answer_eval_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "answer_evaluation.json"
        md_path = tmp_path / "answer_evaluation.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"answers_total": 4}}

    monkeypatch.setattr(cli, "write_answer_evaluation", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "answer-eval",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Evaluated 4 answers" in result.output


def test_cli_report_robustness_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "robustness_evaluation.json"
        md_path = tmp_path / "robustness_evaluation.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"cases_total": 5}}

    monkeypatch.setattr(cli, "write_robustness_evaluation", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "robustness",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Evaluated 5 robustness cases" in result.output
