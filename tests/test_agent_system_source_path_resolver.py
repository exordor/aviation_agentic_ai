"""Source-root resolution stays explicit, deterministic, and local-only."""

from __future__ import annotations

from pathlib import Path

import pytest


def _resolver_api():
    from aviation_agentic_ai.agent_system.source_path_resolver import (
        SourcePathConflictError,
        SourcePathNotFoundError,
        resolve_source_path,
    )

    return resolve_source_path, SourcePathConflictError, SourcePathNotFoundError


def _write(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_relative_path_prefers_the_external_source_root(tmp_path: Path) -> None:
    resolve_source_path, _, _ = _resolver_api()
    project_root = tmp_path / "project"
    source_root = tmp_path / "raw"
    expected = _write(source_root, "data/source.zip", "external")

    result = resolve_source_path(
        "data/source.zip",
        project_root=project_root,
        source_root=source_root,
    )

    assert result.configured_path == Path("data/source.zip")
    assert result.resolved_path == expected
    assert result.chosen_root == "source_root"
    assert result.root_path == source_root


def test_relative_path_falls_back_to_the_project_root(tmp_path: Path) -> None:
    resolve_source_path, _, _ = _resolver_api()
    project_root = tmp_path / "project"
    source_root = tmp_path / "raw"
    expected = _write(project_root, "data/source.zip", "project")

    result = resolve_source_path(
        Path("data/source.zip"),
        project_root=project_root,
        source_root=source_root,
    )

    assert result.resolved_path == expected
    assert result.chosen_root == "project_root"
    assert result.root_path == project_root


def test_distinct_existing_candidates_fail_even_when_bytes_match(
    tmp_path: Path,
) -> None:
    resolve_source_path, conflict_error, _ = _resolver_api()
    project_root = tmp_path / "project"
    source_root = tmp_path / "raw"
    project_candidate = _write(project_root, "data/source.zip", "same")
    source_candidate = _write(source_root, "data/source.zip", "same")

    with pytest.raises(conflict_error) as caught:
        resolve_source_path(
            "data/source.zip",
            project_root=project_root,
            source_root=source_root,
        )

    message = str(caught.value)
    assert str(source_candidate) in message
    assert str(project_candidate) in message


def test_two_candidates_for_the_same_physical_file_are_not_a_conflict(
    tmp_path: Path,
) -> None:
    resolve_source_path, _, _ = _resolver_api()
    project_root = tmp_path / "project"
    expected = _write(project_root, "data/source.zip", "shared")
    source_root = tmp_path / "raw-link"
    source_root.symlink_to(project_root, target_is_directory=True)

    result = resolve_source_path(
        "data/source.zip",
        project_root=project_root,
        source_root=source_root,
    )

    assert result.resolved_path == source_root / "data/source.zip"
    assert result.resolved_path.samefile(expected)
    assert result.chosen_root == "source_root"


def test_missing_relative_path_names_both_candidates(tmp_path: Path) -> None:
    resolve_source_path, _, not_found_error = _resolver_api()
    project_root = tmp_path / "project"
    source_root = tmp_path / "raw"

    with pytest.raises(not_found_error) as caught:
        resolve_source_path(
            "data/missing.zip",
            project_root=project_root,
            source_root=source_root,
        )

    message = str(caught.value)
    assert str(source_root / "data/missing.zip") in message
    assert str(project_root / "data/missing.zip") in message


def test_absolute_configured_path_is_used_exactly(tmp_path: Path) -> None:
    resolve_source_path, _, _ = _resolver_api()
    expected = _write(tmp_path, "absolute/source.zip", "absolute")

    result = resolve_source_path(
        expected,
        project_root=tmp_path / "project",
        source_root=tmp_path / "raw",
    )

    assert result.configured_path == expected
    assert result.resolved_path == expected
    assert result.chosen_root == "absolute"
    assert result.root_path is None


def test_absolute_missing_path_does_not_try_other_roots(tmp_path: Path) -> None:
    resolve_source_path, _, not_found_error = _resolver_api()
    missing = tmp_path / "absolute" / "missing.zip"
    fallback = _write(tmp_path / "project", "absolute/missing.zip", "fallback")

    with pytest.raises(not_found_error) as caught:
        resolve_source_path(
            missing,
            project_root=tmp_path / "project",
            source_root=tmp_path / "raw",
        )

    message = str(caught.value)
    assert str(missing) in message
    assert str(fallback) not in message


def test_resolution_does_not_create_a_machine_specific_sidecar(
    tmp_path: Path,
) -> None:
    resolve_source_path, _, _ = _resolver_api()
    project_root = tmp_path / "project"
    source_root = tmp_path / "raw"
    expected = _write(source_root, "data/source.zip", "external")
    paths_before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    result = resolve_source_path(
        "data/source.zip",
        project_root=project_root,
        source_root=source_root,
    )

    paths_after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert result.resolved_path == expected
    assert paths_after == paths_before
