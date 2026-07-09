import subprocess
from dataclasses import dataclass
from pathlib import Path


class CodeOwnersError(Exception):
    pass


@dataclass
class FileOwner:
    author: str
    commit_count: int


_BOT_AUTHOR_SUFFIXES = ("[bot]",)
_BOT_AUTHOR_NAMES = frozenset({"github-actions", "dependabot"})


def _is_bot_author(name: str) -> bool:
    lowered = name.lower()
    return lowered in _BOT_AUTHOR_NAMES or any(
        lowered.endswith(suffix) for suffix in _BOT_AUTHOR_SUFFIXES
    )


def compute_file_owners(repo_path: Path) -> dict[str, FileOwner]:
    """One `git log` pass (same shape as churn.compute_file_churn) mapping
    each file to the human author of its most recent commit, plus how many
    times that person has touched it. This is who actually wrote/maintains
    the code -- real git attribution, not a guess -- used to suggest who a
    contributor might tag for context. Bot commits (dependabot, CI, etc.)
    are skipped when picking "most recent", since tagging a bot isn't
    useful; a file touched only by bots simply gets no suggested owner.
    """
    result = subprocess.run(
        ["git", "log", "--name-only", "--format=__COMMIT__%an"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CodeOwnersError(result.stderr.strip())

    most_recent_author: dict[str, str] = {}
    commit_counts: dict[tuple[str, str], int] = {}

    current_author: str | None = None
    for line in result.stdout.splitlines():
        if line.startswith("__COMMIT__"):
            author = line.removeprefix("__COMMIT__").strip()
            current_author = None if _is_bot_author(author) else author
            continue
        path = line.strip()
        if not path or current_author is None:
            continue
        if path not in most_recent_author:
            most_recent_author[path] = current_author  # git log is newest-first
        key = (path, current_author)
        commit_counts[key] = commit_counts.get(key, 0) + 1

    return {
        path: FileOwner(author=author, commit_count=commit_counts.get((path, author), 0))
        for path, author in most_recent_author.items()
    }
