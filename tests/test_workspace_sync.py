from __future__ import annotations

import subprocess
from pathlib import Path

from aviation_agentic_ai.workspace_sync import collect_sync_paths


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True)


def test_collect_sync_paths_keeps_non_git_artifacts_and_useful_ignored_data(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")

    (repo / ".gitignore").write_text(
        "\n".join(
            [
                ".venv/",
                "data/chunks/",
                "data/papers/*.pdf",
                "tmp/",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", ".gitignore", "tracked.txt")

    (repo / "notes.txt").write_text("untracked\n", encoding="utf-8")
    (repo / "reports/stages").mkdir(parents=True)
    (repo / "reports/stages/run.json").write_text("{}\n", encoding="utf-8")
    (repo / "data/chunks").mkdir(parents=True)
    (repo / "data/chunks/chunk.jsonl").write_text("{}\n", encoding="utf-8")
    (repo / "data/papers").mkdir(parents=True)
    (repo / "data/papers/paper.pdf").write_bytes(b"%PDF\n")
    (repo / ".venv").mkdir()
    (repo / ".venv/local.py").write_text("pass\n", encoding="utf-8")
    (repo / "tmp").mkdir()
    (repo / "tmp/scratch.txt").write_text("scratch\n", encoding="utf-8")

    paths = collect_sync_paths(
        repo,
        extra_ignored_roots=("data/chunks", "data/papers"),
    )

    assert paths == [
        "data/chunks/chunk.jsonl",
        "data/papers/paper.pdf",
        "notes.txt",
        "reports/stages/run.json",
    ]


def test_collect_sync_paths_excludes_untracked_code_by_default(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")

    for path in [
        repo / "src/aviation_agentic_ai/new_module.py",
        repo / "scripts/new_script.py",
        repo / "tests/test_new_module.py",
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("pass\n", encoding="utf-8")

    (repo / "reports/stages/run.json").parent.mkdir(parents=True)
    (repo / "reports/stages/run.json").write_text("{}\n", encoding="utf-8")

    assert collect_sync_paths(repo) == ["reports/stages/run.json"]
