from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_EXTRA_IGNORED_ROOTS = ("data/chunks", "data/papers")
DEFAULT_EXCLUDED_UNTRACKED_ROOTS = ("scripts", "src", "tests")
DEFAULT_REMOTE = "wjl@desktop-g9260uj"
DEFAULT_REMOTE_PATH = "/mnt/c/Users/wjl/code/aviation_agentic_ai/"
DEFAULT_RSYNC_PATH = "wsl -d Ubuntu-22.04 -- rsync"


def _git_output(repo: Path, args: Sequence[str]) -> bytes:
    return subprocess.check_output(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=repo,
    )


def _split_nul_paths(output: bytes) -> set[str]:
    return {
        item.decode("utf-8")
        for item in output.split(b"\0")
        if item
    }


def collect_sync_paths(
    repo: Path,
    *,
    extra_ignored_roots: Iterable[str] = DEFAULT_EXTRA_IGNORED_ROOTS,
    excluded_untracked_roots: Iterable[str] = DEFAULT_EXCLUDED_UNTRACKED_ROOTS,
) -> list[str]:
    """Return non-Git files that should be copied to the paired workstation."""
    repo = repo.resolve()
    excluded_roots = tuple(root.rstrip("/") for root in excluded_untracked_roots)
    paths = _split_nul_paths(
        _git_output(repo, ["ls-files", "-z", "-o", "--exclude-standard"])
    )

    for root in extra_ignored_roots:
        paths.update(
            _split_nul_paths(
                _git_output(
                    repo,
                    ["ls-files", "-z", "-o", "-i", "--exclude-standard", "--", root],
                )
            )
        )

    return sorted(
        path for path in paths
        if not any(path == root or path.startswith(f"{root}/") for root in excluded_roots)
    )


def find_repo_root(start: Path) -> Path:
    root = _git_output(start, ["rev-parse", "--show-toplevel"]).decode("utf-8").strip()
    return Path(root)


def build_rsync_command(
    *,
    files_from: Path,
    remote: str,
    remote_path: str,
    rsync_path: str,
    dry_run: bool,
) -> list[str]:
    command = [
        "rsync",
        "-rt",
        "--stats",
        f"--files-from={files_from}",
        f"--rsync-path={rsync_path}",
        "-e",
        "ssh",
    ]
    if dry_run:
        command.append("--dry-run")
    command.extend(["./", f"{remote}:{remote_path}"])
    return command


def sync_workspace(
    *,
    repo: Path,
    remote: str,
    remote_path: str,
    rsync_path: str,
    extra_ignored_roots: Iterable[str],
    dry_run: bool,
    list_only: bool,
) -> int:
    paths = collect_sync_paths(repo, extra_ignored_roots=extra_ignored_roots)
    if list_only:
        for path in paths:
            print(path)
        return 0

    if not paths:
        print("No non-Git workspace files to sync.")
        return 0

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as file_list:
        file_list.write("\n".join(paths))
        file_list.write("\n")
        file_list_path = Path(file_list.name)

    try:
        mode = "Dry run" if dry_run else "Sync"
        print(f"{mode}: {len(paths)} non-Git files -> {remote}:{remote_path}")
        command = build_rsync_command(
            files_from=file_list_path,
            remote=remote,
            remote_path=remote_path,
            rsync_path=rsync_path,
            dry_run=dry_run,
        )
        return subprocess.run(command, cwd=repo).returncode
    finally:
        file_list_path.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync non-Git aviation_agentic_ai workspace artifacts to Windows."
    )
    parser.add_argument("--repo", type=Path, default=None, help="Repository root. Defaults to cwd.")
    parser.add_argument(
        "--remote",
        default=os.environ.get("AVIATION_SYNC_REMOTE", DEFAULT_REMOTE),
        help="SSH remote, for example wjl@desktop-g9260uj.",
    )
    parser.add_argument(
        "--remote-path",
        default=os.environ.get("AVIATION_SYNC_REMOTE_PATH", DEFAULT_REMOTE_PATH),
        help="Remote rsync destination path.",
    )
    parser.add_argument(
        "--rsync-path",
        default=os.environ.get("AVIATION_SYNC_RSYNC_PATH", DEFAULT_RSYNC_PATH),
        help="Remote rsync command. The default uses WSL on Windows.",
    )
    parser.add_argument(
        "--extra-ignored-root",
        action="append",
        default=None,
        help="Ignored root to include anyway. Can be passed more than once.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what rsync would copy.")
    parser.add_argument("--list-only", action="store_true", help="Print the sync file list only.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repo = args.repo.resolve() if args.repo else find_repo_root(Path.cwd())
    extra_ignored_roots = args.extra_ignored_root or list(DEFAULT_EXTRA_IGNORED_ROOTS)

    return sync_workspace(
        repo=repo,
        remote=args.remote,
        remote_path=args.remote_path,
        rsync_path=args.rsync_path,
        extra_ignored_roots=extra_ignored_roots,
        dry_run=args.dry_run,
        list_only=args.list_only,
    )


if __name__ == "__main__":
    raise SystemExit(main())
