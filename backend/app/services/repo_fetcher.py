import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent / "workspace"


class RepoFetchError(Exception):
    pass


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
