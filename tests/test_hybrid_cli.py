from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main


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


def test_cli_report_chunking_comparison_v2_uses_mocked_writer(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli

    calls = {}

    def fake_writer(*_args, **kwargs):
        calls["max_labels"] = kwargs["max_labels"]
        calls["semantic_download"] = kwargs["semantic_download"]
        calls["evaluation_mode"] = kwargs["evaluation_mode"]
        calls["context_budget_chars"] = kwargs["context_budget_chars"]
        json_path = tmp_path / "chunking_comparison_benchmark_v2.json"
        md_path = tmp_path / "chunking_comparison_benchmark_v2.md"
        failure_json = tmp_path / "chunking_failure_cards_benchmark_v2.json"
        failure_md = tmp_path / "chunking_failure_cards_benchmark_v2.md"
        for path in (json_path, md_path, failure_json, failure_md):
            path.write_text("{}\n", encoding="utf-8")
        return (
            json_path,
            md_path,
            failure_json,
            failure_md,
            {"ranking": [{"strategy": "fixed_small"}], "strategies": {"fixed_small": {}}},
            {"strategies": {}},
        )

    monkeypatch.setattr(cli, "write_chunking_comparison_v2", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "chunking-comparison-v2",
            "--output-dir",
            str(tmp_path),
            "--max-labels",
            "3",
            "--no-semantic-download",
            "--evaluation-mode",
            "fixed_context_budget",
            "--context-budget-chars",
            "1234",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls == {
        "max_labels": 3,
        "semantic_download": False,
        "evaluation_mode": "fixed_context_budget",
        "context_budget_chars": 1234,
    }
    assert "benchmark-v2 chunking strategies" in result.output


def test_cli_report_chunking_implementation_audit_uses_mocked_writer(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "chunking_implementation_audit.json"
        md_path = tmp_path / "chunking_implementation_audit.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"strategies_total": 3}}

    monkeypatch.setattr(cli, "write_chunking_implementation_audit", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "chunking-implementation-audit",
            "--output-dir",
            str(tmp_path),
            "--reuse-chunks",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Audited 3 chunking strategies" in result.output


def test_cli_report_chunking_topk_and_category_use_mocked_writers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli

    def fake_topk(*_args, **_kwargs):
        json_path = tmp_path / "chunking_topk_sensitivity_benchmark_v2.json"
        md_path = tmp_path / "chunking_topk_sensitivity_benchmark_v2.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"top_k_values": [3, 5, 10, 20]}}

    def fake_category(*_args, **_kwargs):
        json_path = tmp_path / "chunking_category_analysis_benchmark_v2.json"
        md_path = tmp_path / "chunking_category_analysis_benchmark_v2.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"categories": ["relation_causal"]}}

    monkeypatch.setattr(cli, "write_chunking_topk_sensitivity_v2", fake_topk)
    monkeypatch.setattr(cli, "write_chunking_category_analysis_v2", fake_category)

    topk = CliRunner().invoke(
        main,
        ["report", "chunking-topk-sensitivity-v2", "--output-dir", str(tmp_path)],
    )
    category = CliRunner().invoke(
        main,
        ["report", "chunking-category-analysis-v2", "--output-dir", str(tmp_path)],
    )

    assert topk.exit_code == 0, topk.output
    assert category.exit_code == 0, category.output
    assert "top-k sensitivity" in topk.output
    assert "category analysis" in category.output


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


def test_cli_report_benchmark_reviewed_subset_uses_mocked_writer(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "benchmark_reviewed_subset_summary.json"
        md_path = tmp_path / "benchmark_reviewed_subset_summary.md"
        subset_path = tmp_path / "reviewed_subset.json"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        subset_path.write_text("{}\n", encoding="utf-8")
        return json_path, md_path, subset_path, {"metadata": {"labels_total": 60}}

    monkeypatch.setattr(cli, "write_benchmark_reviewed_subset", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "benchmark-reviewed-subset",
            "--output-dir",
            str(tmp_path),
            "--subset-output",
            str(tmp_path / "reviewed_subset.json"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Prepared reviewed subset scaffold with 60 labels" in result.output


def test_cli_report_answer_eval_subset_uses_mocked_writer(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        subset_path = tmp_path / "answer_eval_subset.json"
        subset_path.write_text("{}\n", encoding="utf-8")
        return subset_path, {"labels": [{} for _ in range(45)]}

    monkeypatch.setattr(cli, "write_answer_eval_subset", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "answer-eval-subset",
            "--subset-output",
            str(tmp_path / "answer_eval_subset.json"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Prepared answer-eval subset with 45 labels" in result.output


def test_cli_report_evaluation_protocol_uses_mocked_writer(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "evaluation_protocol_review.json"
        md_path = tmp_path / "evaluation_protocol_review.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"missing_or_pending_metrics": [{}, {}]}

    monkeypatch.setattr(cli, "write_evaluation_protocol_review", fake_writer)

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


def test_cli_report_thesis_dashboard_uses_mocked_writer(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(*_args, **_kwargs):
        json_path = tmp_path / "thesis_experiment_dashboard.json"
        md_path = tmp_path / "thesis_experiment_dashboard.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"consistency_checks": {"all_passed": True}}

    monkeypatch.setattr(cli, "write_thesis_experiment_dashboard", fake_writer)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "thesis-experiment-dashboard",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "consistency checks passed=True" in result.output


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


def test_cli_llm_review_commands_use_mocked_writers(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_benchmark(*_args, **_kwargs):
        json_path = tmp_path / "benchmark_llm_review.json"
        md_path = tmp_path / "benchmark_llm_review.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"summary": {"items_total": 2, "llm_reviewed_total": 2}}

    def fake_rewrite(*_args, **_kwargs):
        json_path = tmp_path / "benchmark_llm_rewrite_proposals.json"
        md_path = tmp_path / "benchmark_llm_rewrite_proposals.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, None, {"metadata": {"proposals_total": 1}}

    def fake_review(*_args, **_kwargs):
        json_path = tmp_path / "review.json"
        md_path = tmp_path / "review.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"summary": {"items_total": 2, "llm_reviewed_total": 2}}

    def fake_answer_gen(*_args, **_kwargs):
        json_path = tmp_path / "answer_generation_benchmark_subset.json"
        md_path = tmp_path / "answer_generation_benchmark_subset.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"metadata": {"answers_total": 3}}

    def fake_consistency(*_args, **_kwargs):
        json_path = tmp_path / "llm_review_consistency.json"
        md_path = tmp_path / "llm_review_consistency.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return json_path, md_path, {"summary": {"consistency_not_measured": False}}

    monkeypatch.setattr(cli, "write_benchmark_llm_review", fake_benchmark)
    monkeypatch.setattr(cli, "write_benchmark_llm_rewrite_proposals", fake_rewrite)
    monkeypatch.setattr(cli, "write_triple_semantic_llm_review", fake_review)
    monkeypatch.setattr(cli, "write_graph_path_llm_review", fake_review)
    monkeypatch.setattr(cli, "write_answer_llm_judge", fake_review)
    monkeypatch.setattr(cli, "write_answer_generation_benchmark_subset", fake_answer_gen)
    monkeypatch.setattr(cli, "write_llm_review_consistency", fake_consistency)

    commands = [
        ("benchmark-llm-review", "Benchmark LLM review records=2"),
        ("benchmark-llm-rewrite-proposals", "Prepared 1 rewrite proposals"),
        ("triple-semantic-llm-review", "Triple LLM review records=2"),
        ("graph-path-llm-review", "Graph path LLM review records=2"),
        ("answer-generation-benchmark-subset", "Generated 3 benchmark-subset answers"),
        ("answer-llm-judge", "Answer LLM judge records=2"),
        ("llm-review-consistency", "LLM review consistency measured=True"),
    ]
    for command, expected in commands:
        result = CliRunner().invoke(
            main,
            ["report", command, "--output-dir", str(tmp_path)],
        )
        assert result.exit_code == 0, result.output
        assert expected in result.output
