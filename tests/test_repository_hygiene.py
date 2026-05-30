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
        "data/chunks/",
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
        "data/chunks/",
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
