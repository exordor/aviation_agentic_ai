import os
import warnings
from pathlib import Path

_ENV_ROOT = os.getenv("AVIATION_AI_PROJECT_ROOT")
if _ENV_ROOT:
    PROJECT_ROOT = Path(_ENV_ROOT).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]


def project_relative_path(path: str | Path, base: str | Path = PROJECT_ROOT) -> str:
    """Return a stable relative path string for reports and manifests."""
    candidate = Path(path)
    if not candidate.is_absolute():
        return candidate.as_posix()

    base_path = Path(base)
    try:
        relative = candidate.resolve(strict=False).relative_to(base_path.resolve(strict=False))
    except ValueError:
        relative = Path(
            os.path.relpath(
                candidate.resolve(strict=False),
                base_path.resolve(strict=False),
            )
        )
    return relative.as_posix()


def resolve_output_path(path: str | Path) -> Path:
    """Resolve an output path, warning when it falls outside the project root."""
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    try:
        candidate.resolve(strict=False).relative_to(PROJECT_ROOT.resolve(strict=False))
    except ValueError:
        warnings.warn(
            f"Output path {candidate} is outside the project root ({PROJECT_ROOT}). "
            "This may be a path traversal risk.",
            stacklevel=2,
        )
    return candidate
