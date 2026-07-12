import pytest

from app.services.repo_fetcher import RepoFetchError, clone_repo


@pytest.mark.parametrize(
    "full_name",
    [
        "../../etc/passwd",
        "owner/../../../etc",
        "owner/..",
        "../owner/name",
        "owner name/repo",
        "owner/repo name",
        "owner/",
        "/repo",
        "owner//repo",
        "just-a-name-no-slash",
        "",
    ],
)
def test_clone_repo_rejects_unsafe_or_malformed_identifiers(full_name: str) -> None:
    """Defense in depth: clone_repo must reject anything that isn't a safe
    owner/repo identifier on its own, without depending on the caller having
    already validated it (e.g. via a prior GitHub API existence check)."""
    with pytest.raises(RepoFetchError, match="valid owner/repo identifier"):
        clone_repo(full_name)


def test_clone_repo_rejection_happens_before_any_git_invocation(tmp_path, monkeypatch) -> None:
    """The safety check must short-circuit before subprocess is ever
    touched -- otherwise a malicious identifier could still reach `git`."""
    import app.services.repo_fetcher as repo_fetcher

    called = False

    def _fail_if_called(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("subprocess.run should not be reached for invalid input")

    monkeypatch.setattr(repo_fetcher.subprocess, "run", _fail_if_called)

    with pytest.raises(RepoFetchError):
        clone_repo("../escape")

    assert called is False
