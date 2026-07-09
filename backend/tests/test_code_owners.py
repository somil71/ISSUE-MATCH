import subprocess
from pathlib import Path

from app.services.code_owners import compute_file_owners


def _git(args: list[str], cwd: Path, author: str = "Test") -> None:
    env_args = ["-c", f"user.name={author}", "-c", f"user.email={author}@example.com"]
    subprocess.run(["git", *env_args, *args], cwd=cwd, check=True, capture_output=True)


def test_compute_file_owners_picks_most_recent_human_author(tmp_path: Path) -> None:
    _git(["init"], tmp_path)

    (tmp_path / "a.py").write_text("v1")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "add a"], tmp_path, author="Alice")

    (tmp_path / "a.py").write_text("v2")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "update a"], tmp_path, author="Bob")

    owners = compute_file_owners(tmp_path)

    assert owners["a.py"].author == "Bob"
    assert owners["a.py"].commit_count == 1


def test_compute_file_owners_counts_commits_by_that_author(tmp_path: Path) -> None:
    _git(["init"], tmp_path)

    (tmp_path / "a.py").write_text("v1")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "add a"], tmp_path, author="Alice")

    (tmp_path / "a.py").write_text("v2")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "update a"], tmp_path, author="Alice")

    owners = compute_file_owners(tmp_path)

    assert owners["a.py"].author == "Alice"
    assert owners["a.py"].commit_count == 2


def test_compute_file_owners_skips_bot_commits(tmp_path: Path) -> None:
    _git(["init"], tmp_path)

    (tmp_path / "a.py").write_text("v1")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "add a"], tmp_path, author="Alice")

    (tmp_path / "a.py").write_text("v2")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "bump deps"], tmp_path, author="dependabot[bot]")

    owners = compute_file_owners(tmp_path)

    assert owners["a.py"].author == "Alice"


def test_compute_file_owners_omits_files_touched_only_by_bots(tmp_path: Path) -> None:
    _git(["init"], tmp_path)

    (tmp_path / "a.py").write_text("v1")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "automated commit"], tmp_path, author="github-actions")

    owners = compute_file_owners(tmp_path)

    assert "a.py" not in owners
