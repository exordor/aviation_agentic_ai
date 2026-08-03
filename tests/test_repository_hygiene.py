from pathlib import Path
from subprocess import PIPE, run


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RETIRED_DOCUMENT_REFERENCES = {
    "ARTIFACT_INDEX.md",
    "docs/architecture_narrative.md",
    "docs/multi_agent_kg_system_design.md",
    "reports/final/",
    "atcscc_defense_deck_outline.md",
    "src/aviation_agentic_ai/web/static/vendor/cytoscape.min.js",
}


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


def _tracked_markdown_files() -> list[Path]:
    return [
        PROJECT_ROOT / path
        for path in _tracked_files()
        if path.endswith(".md")
    ]


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


def test_tracked_markdown_uses_only_current_document_authorities() -> None:
    offenders = []
    for path in _tracked_markdown_files():
        text = path.read_text(encoding="utf-8")
        for retired_reference in RETIRED_DOCUMENT_REFERENCES:
            if retired_reference in text:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {retired_reference}")

    assert offenders == []


def test_redundant_research_overview_is_not_tracked() -> None:
    assert "RESEARCH_OVERVIEW.md" not in _tracked_files()


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
