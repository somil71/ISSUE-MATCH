import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


class ChurnError(Exception):
    pass


@dataclass
class FileChurn:
    commit_count: int
    days_since_last_commit: float

    @property
    def intensity(self) -> float:
        """Frequent AND recent changes both raise risk; either one fading
        (old last-touch, or few total commits) lowers it."""
        return self.commit_count / (self.days_since_last_commit + 1)


def compute_file_churn(repo_path: Path) -> dict[str, FileChurn]:
    """One `git log` pass over the whole repo (not one call per file, which
    would not scale) mapping each path touched in history to how often and
    how recently it changed. Renamed files are not stitched to their
    pre-rename history — that would need a --follow pass per file — so
    churn for heavily-renamed files is a known undercount.
    """
    result = subprocess.run(
        ["git", "log", "--name-only", "--format=__COMMIT__%at"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ChurnError(result.stderr.strip())

    now = time.time()
    commit_counts: dict[str, int] = {}
    last_commit_at: dict[str, int] = {}

    current_ts: int | None = None
    for line in result.stdout.splitlines():
        if line.startswith("__COMMIT__"):
            current_ts = int(line.removeprefix("__COMMIT__"))
            continue
        path = line.strip()
        if not path or current_ts is None:
            continue
        commit_counts[path] = commit_counts.get(path, 0) + 1
        if path not in last_commit_at:
            last_commit_at[path] = current_ts  # git log is newest-first

    return {
        path: FileChurn(
            commit_count=commit_counts[path],
            days_since_last_commit=(now - last_commit_at[path]) / 86400,
        )
        for path in commit_counts
    }
