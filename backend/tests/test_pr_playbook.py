from app.services.pr_playbook import build_pr_playbook, suggest_branch_name


def test_suggest_branch_name_slugifies_title() -> None:
    branch = suggest_branch_name(42, "Fix: Crash when parsing empty config!")
    assert branch == "fix/42-fix-crash-when-parsing-empty-config"


def test_suggest_branch_name_falls_back_when_title_has_no_words() -> None:
    branch = suggest_branch_name(7, "!!!")
    assert branch == "fix/7-issue"


def test_playbook_start_here_includes_direct_callers() -> None:
    reference = {
        "name": "parseConfig",
        "file": "app/config.py",
        "summary": "3 callers, no branches, no nearby tests.",
        "has_test_coverage": False,
        "direct_callers": ["loadApp", "reloadConfig"],
    }
    playbook = build_pr_playbook(12, "Fix config bug", reference, None, "tests")

    assert playbook["start_here"] == {
        "function": "parseConfig",
        "file": "app/config.py",
        "direct_callers": ["loadApp", "reloadConfig"],
    }


def test_playbook_start_here_is_none_without_a_reference() -> None:
    playbook = build_pr_playbook(12, "Fix config bug", None, None, "tests")
    assert playbook["start_here"] is None


def test_playbook_test_guidance_points_at_existing_test_directory() -> None:
    reference = {"name": "parseConfig", "file": "a.py", "has_test_coverage": False}
    playbook = build_pr_playbook(1, "x", reference, None, "tests")
    assert "`tests`" in playbook["test_guidance"]
    assert "parseConfig" in playbook["test_guidance"]


def test_playbook_test_guidance_when_already_covered() -> None:
    reference = {"name": "parseConfig", "file": "a.py", "has_test_coverage": True}
    playbook = build_pr_playbook(1, "x", reference, None, "tests")
    assert "already has a test" in playbook["test_guidance"]


def test_playbook_test_guidance_when_no_test_directory_exists() -> None:
    reference = {"name": "parseConfig", "file": "a.py", "has_test_coverage": False}
    playbook = build_pr_playbook(1, "x", reference, None, None)
    assert "no detected" in playbook["test_guidance"]


def test_playbook_pr_description_includes_closes_and_owner() -> None:
    reference = {
        "name": "parseConfig",
        "file": "app/config.py",
        "summary": "3 callers, no branches, no nearby tests.",
        "direct_callers": ["loadApp"],
    }
    owner = {"author": "octocat", "commit_count": 4}
    playbook = build_pr_playbook(99, "Fix config bug", reference, owner, "tests")

    assert "Closes #99." in playbook["pr_description"]
    assert "`parseConfig`" in playbook["pr_description"]
    assert "loadApp" in playbook["pr_description"]
    assert "@octocat" in playbook["pr_description"]


def test_playbook_pr_description_without_reference_or_owner() -> None:
    playbook = build_pr_playbook(5, "Something", None, None, None)
    assert playbook["pr_description"] == "Closes #5."
