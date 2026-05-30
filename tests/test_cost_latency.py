from pathlib import Path

from aviation_agentic_ai.evaluation.cost_latency import (
    artifact_size_bytes,
    cost_latency_block,
)


def test_artifact_size_bytes_handles_none_and_missing(tmp_path: Path) -> None:
    assert artifact_size_bytes(None) is None
    assert artifact_size_bytes(tmp_path / "missing.txt") is None


def test_artifact_size_bytes_counts_files_and_directories(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("abc", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "a.txt").write_text("12345", encoding="utf-8")
    (nested / "b.txt").write_text("xy", encoding="utf-8")

    assert artifact_size_bytes(file_path) == 3
    assert artifact_size_bytes(nested) == 7


def test_cost_latency_block_records_relative_paths_and_rounding(tmp_path: Path) -> None:
    chunks_path = tmp_path / "chunks.jsonl"
    kg_path = tmp_path / "kg.jsonl"
    index_dir = tmp_path / "index"
    chunks_path.write_text("chunk", encoding="utf-8")
    kg_path.write_text("kg", encoding="utf-8")
    index_dir.mkdir()
    (index_dir / "index.bin").write_text("1234", encoding="utf-8")

    block = cost_latency_block(
        elapsed_seconds=1.23456,
        questions_total=3,
        cases_total=4,
        chunks_path=chunks_path,
        kg_path=kg_path,
        index_dir=index_dir,
        token_usage={"prompt": 10},
    )

    assert block["elapsed_seconds"] == 1.2346
    assert block["questions_total"] == 3
    assert block["cases_total"] == 4
    assert block["chunks_path"].endswith("chunks.jsonl")
    assert block["chunks_size_bytes"] == 5
    assert block["kg_size_bytes"] == 2
    assert block["index_size_bytes"] == 4
    assert block["llm_token_usage"] == {"prompt": 10}
