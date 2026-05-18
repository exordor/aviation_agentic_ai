from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.project_report import (
    build_project_evidence_pack,
    build_project_report_draft,
    build_project_report_prompt,
    write_project_report,
)


def _write_project_fixture(root: Path) -> Path:
    (root / "configs").mkdir()
    (root / "reports" / "stages").mkdir(parents=True)
    (root / "reports" / "final").mkdir(parents=True)
    (root / "tmp").mkdir()
    (root / "README.md").write_text(
        "# Aviation Agentic AI\n\nArchitecture evidence.\n",
        encoding="utf-8",
    )
    (root / "tmp" / "goal.md").write_text(
        "# Course Goal\n\nBuild an aviation RAG prototype.\n",
        encoding="utf-8",
    )
    (root / "configs" / "default.yaml").write_text(
        "retrieval:\n  vector_top_k: 5\n  graph_hops: 2\n  hybrid_top_k: 8\n",
        encoding="utf-8",
    )
    (root / "configs" / "ontology_generation.yaml").write_text(
        "input_pdf: data/raw/doc.pdf\n",
        encoding="utf-8",
    )
    (root / "configs" / "extraction_profile.yaml").write_text(
        "name: test-profile\n",
        encoding="utf-8",
    )
    index_path = root / "reports" / "stages" / "index.json"
    index_path.write_text(
        json.dumps(
            {
                "categories": {
                    "ontology_evaluation": [{"path": "reports/archive/ontology.json"}],
                    "rag_experiments": [{"path": "reports/archive/chunking.json"}],
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return index_path


def test_project_evidence_pack_reads_index_configs_and_goal(tmp_path: Path) -> None:
    index_path = _write_project_fixture(tmp_path)

    evidence = build_project_evidence_pack(
        project_root=tmp_path,
        stage_index_path=index_path,
    )

    assert evidence["stage_index"]["present"]
    assert evidence["readme"]["present"]
    assert evidence["course_goal"]["present"]
    assert evidence["configs"]["default"]["data"]["retrieval"]["vector_top_k"] == 5
    assert not evidence["source_policy"]["env_files_read"]


def test_deterministic_project_report_needs_no_ai(tmp_path: Path) -> None:
    index_path = _write_project_fixture(tmp_path)

    md_path, sources_path, result = write_project_report(
        tmp_path / "reports" / "final",
        project_root=tmp_path,
        stage_index_path=index_path,
    )

    assert not result["used_ai"]
    assert md_path.exists()
    assert sources_path.exists()
    markdown = md_path.read_text(encoding="utf-8")
    assert "Aviation Agentic AI Project Report" in markdown
    assert "Hybrid RAG protocol and layered metrics" in markdown


def test_ai_project_report_uses_mock_llm_and_prompt_constraints(tmp_path: Path) -> None:
    index_path = _write_project_fixture(tmp_path)
    captured = {}

    def fake_llm(prompt: str, temperature: float, max_tokens: int) -> str:
        captured["prompt"] = prompt
        captured["temperature"] = temperature
        captured["max_tokens"] = max_tokens
        return "# AI Project Report\n\nCited from `README.md`."

    md_path, _sources_path, result = write_project_report(
        tmp_path / "reports" / "final",
        project_root=tmp_path,
        stage_index_path=index_path,
        use_ai=True,
        llm_runner=fake_llm,
        max_tokens=1000,
    )

    assert result["used_ai"]
    assert "Use only the evidence pack" in captured["prompt"]
    assert "TBD or Not yet run" in captured["prompt"]
    assert "Do not invent completed experiments" in captured["prompt"]
    assert md_path.read_text(encoding="utf-8").startswith("# AI Project Report")


def test_project_report_prompt_includes_required_sections(tmp_path: Path) -> None:
    index_path = _write_project_fixture(tmp_path)
    evidence = build_project_evidence_pack(project_root=tmp_path, stage_index_path=index_path)
    draft = build_project_report_draft(evidence)
    prompt = build_project_report_prompt(evidence, draft)

    assert "Project motivation and course objective alignment" in prompt
    assert "Reproducibility appendix" in prompt
    assert "Cite source file paths" in prompt


def test_cli_report_project_no_ai_writes_outputs(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(output_dir, **kwargs):
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        md_path = output / "project_report.md"
        sources_path = output / "project_report_sources.json"
        md_path.write_text("# report\n", encoding="utf-8")
        sources_path.write_text("{}\n", encoding="utf-8")
        return md_path, sources_path, {"used_ai": kwargs.get("use_ai", False)}

    monkeypatch.setattr(cli, "write_project_report", fake_writer)
    result = CliRunner().invoke(
        main,
        [
            "report",
            "project",
            "--no-ai",
            "--output-dir",
            str(tmp_path / "final"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Generated deterministic project report" in result.output
    assert (tmp_path / "final" / "project_report.md").exists()


def test_cli_report_project_ai_uses_writer_flag(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    calls = {}

    def fake_writer(output_dir, **kwargs):
        calls["use_ai"] = kwargs.get("use_ai")
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        md_path = output / "project_report.md"
        sources_path = output / "project_report_sources.json"
        md_path.write_text("# report\n", encoding="utf-8")
        sources_path.write_text("{}\n", encoding="utf-8")
        return md_path, sources_path, {"used_ai": kwargs.get("use_ai", False)}

    monkeypatch.setattr(cli, "write_project_report", fake_writer)
    result = CliRunner().invoke(
        main,
        [
            "report",
            "project",
            "--ai",
            "--output-dir",
            str(tmp_path / "final"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls["use_ai"] is True
    assert "Generated AI-polished project report" in result.output

