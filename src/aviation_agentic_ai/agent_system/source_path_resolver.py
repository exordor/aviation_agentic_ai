"""Resolve configured source artifacts without persisting local machine paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


class SourcePathConflictError(ValueError):
    """Raised when two distinct configured source candidates both exist."""


class SourcePathNotFoundError(FileNotFoundError):
    """Raised when no permitted candidate contains the configured source."""


@dataclass(frozen=True, slots=True)
class ResolvedSourcePath:
    """In-memory source-path choice for one ingestion execution."""

    configured_path: Path
    resolved_path: Path
    chosen_root: Literal["absolute", "source_root", "project_root"]
    root_path: Path | None


def resolve_source_path(
    configured_path: str | Path,
    *,
    project_root: str | Path,
    source_root: str | Path | None = None,
) -> ResolvedSourcePath:
    """Resolve one configured source path within the permitted local roots."""

    configured = Path(configured_path)
    project = Path(project_root)
    external = Path(source_root) if source_root is not None else None

    if configured.is_absolute():
        if not configured.exists():
            raise SourcePathNotFoundError(
                f"configured absolute source path does not exist: {configured}"
            )
        return ResolvedSourcePath(
            configured_path=configured,
            resolved_path=configured,
            chosen_root="absolute",
            root_path=None,
        )

    project_candidate = project / configured
    external_candidate = external / configured if external is not None else None
    project_exists = project_candidate.exists()
    external_exists = (
        external_candidate is not None and external_candidate.exists()
    )

    if external_exists and project_exists:
        assert external_candidate is not None
        if not external_candidate.samefile(project_candidate):
            raise SourcePathConflictError(
                "configured relative source path exists at two distinct locations: "
                f"source_root={external_candidate}; project_root={project_candidate}"
            )

    if external_exists:
        assert external_candidate is not None
        return ResolvedSourcePath(
            configured_path=configured,
            resolved_path=external_candidate,
            chosen_root="source_root",
            root_path=external,
        )
    if project_exists:
        return ResolvedSourcePath(
            configured_path=configured,
            resolved_path=project_candidate,
            chosen_root="project_root",
            root_path=project,
        )

    checked_external = (
        str(external_candidate)
        if external_candidate is not None
        else "<source_root not configured>"
    )
    raise SourcePathNotFoundError(
        "configured relative source path was not found; "
        f"source_root candidate={checked_external}; "
        f"project_root candidate={project_candidate}"
    )


__all__ = [
    "ResolvedSourcePath",
    "SourcePathConflictError",
    "SourcePathNotFoundError",
    "resolve_source_path",
]
