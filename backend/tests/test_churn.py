import subprocess
from pathlib import Path

from app.services.churn import compute_file_churn


def _git(args: list[str], cwd: Path) -> None:
    env_args = ["-c", "user.name=Test", "-c", "user.email=test@example.com"]
    subprocess.run(["git", *env_args, *args], cwd=cwd, check=True, capture_output=True)


def test_compute_file_churn_counts_commits_per_file(tmp_path: Path) -> None:
    _git(["init"], tmp_path)

    (tmp_path / "a.py").write_text("v1")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "add a"], tmp_path)

    (tmp_path / "a.py").write_text("v2")
    _git(["add", "a.py"], tmp_path)
    _git(["commit", "-m", "update a"], tmp_path)

    (tmp_path / "b.py").write_text("v1")
    _git(["add", "b.py"], tmp_path)
    _git(["commit", "-m", "add b"], tmp_path)

    churn = compute_file_churn(tmp_path)

    assert churn["a.py"].commit_count == 2
    assert churn["b.py"].commit_count == 1
    assert churn["a.py"].days_since_last_commit < 0.01
    assert churn["a.py"].intensity > churn["b.py"].intensity
