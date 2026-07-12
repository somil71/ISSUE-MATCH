import re
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent / "workspace"

# GitHub owner/repo names are always alphanumeric plus ._- ; this is
# deliberately an allowlist (reject anything else) rather than trying to
# blocklist "/", "..", backslashes, etc. one by one. Today the only caller
# happens to check with GitHub's API first (which would itself reject a
# malformed identifier before this runs), but that's an implicit ordering
# dependency, not validation -- this makes clone_repo safe on its own for
# any caller, present or future.
_SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9._-]+$")


class RepoFetchError(Exception):
    pass


def _is_safe_segment(segment: str) -> bool:
    # "." and ".." are the only dot-sequences with special filesystem
    # meaning; every other character in the allowlist is otherwise inert.
    return bool(segment) and segment not in (".", "..") and bool(_SAFE_SEGMENT.match(segment))


def _run_git(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RepoFetchError(result.stderr.strip())
    return result.stdout.strip()


def clone_repo(full_name: str) -> Path:
    """Partial clone (blob:none): full commit history for churn analysis,
    without downloading every historical blob up front."""
    owner, sep, name = full_name.partition("/")
    if not (sep and _is_safe_segment(owner) and _is_safe_segment(name)):
        raise RepoFetchError(f"Not a valid owner/repo identifier: {full_name!r}")

    dest = WORKSPACE_ROOT / full_name.replace("/", "__")
    if dest.exists():
        _run_git(["fetch", "--all"], cwd=dest)
        _run_git(["reset", "--hard", "origin/HEAD"], cwd=dest)
        return dest

    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{full_name}.git"
    _run_git(["clone", "--filter=blob:none", url, str(dest)])
    return dest


def current_commit_sha(repo_path: Path) -> str:
    return _run_git(["rev-parse", "HEAD"], cwd=repo_path)


def list_source_files(repo_path: Path, extensions: set[str]) -> list[Path]:
    return [
        path
        for path in repo_path.rglob("*")
        if path.is_file() and path.suffix in extensions and ".git" not in path.parts
    ]
