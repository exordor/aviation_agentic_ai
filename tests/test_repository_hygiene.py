from pathlib import Path
from subprocess import PIPE, run


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _tracked_files() -> list[str]:
    result = run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
    )
    return result.stdout.splitlines()


def test_gitignore_covers_secret_runtime_and_model_artifacts() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    required_patterns = {
        ".env",
        ".venv/",
        "data/indexes/",
        "data/stores/",
        "models/",
        "*.faiss",
        "*.index",
        "*.sqlite3",
        "*.duckdb",
        "*.parquet",
    }

    assert required_patterns <= set(gitignore)


def test_tracked_files_exclude_secrets_indexes_chunks_and_model_weights() -> None:
    forbidden_exact = {".env"}
    forbidden_prefixes = (
        "data/indexes/",
        "data/stores/",
        "data/runs/agent_system/",
        "models/",
    )
    forbidden_suffixes = (
        ".faiss",
        ".index",
        ".sqlite3",
        ".duckdb",
        ".parquet",
        ".safetensors",
        ".gguf",
        ".onnx",
        ".ckpt",
        ".pt",
        ".pth",
    )

    offenders = [
        path
        for path in _tracked_files()
        if path in forbidden_exact
        or path.startswith(forbidden_prefixes)
        or path.endswith(forbidden_suffixes)
    ]

    assert offenders == []


def test_tracked_markdown_does_not_reference_retired_repository_documents() -> None:
    retired_references = {
        "ARTIFACT_INDEX.md",
        "docs/architecture_narrative.md",
    }
    offenders = []
    for path in PROJECT_ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for retired_reference in retired_references:
            if retired_reference in text:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {retired_reference}")

    assert offenders == []


def test_authoritative_command_lists_include_all_public_commands() -> None:
    expected = {
        "ingest",
        "reindex",
        "ask",
        "build-kg",
        "neo4j-export",
        "export-event",
    }
    documents = (
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "RESEARCH_AUDIT.md",
        PROJECT_ROOT / "AGENTS.md",
    )

    for document in documents:
        text = document.read_text(encoding="utf-8")
        missing = sorted(command for command in expected if command not in text)
        assert missing == [], f"{document}: missing public commands {missing}"
