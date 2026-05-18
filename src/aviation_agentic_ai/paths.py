import os
from pathlib import Path


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
