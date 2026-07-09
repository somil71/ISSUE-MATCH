from app.services.intro_draft import draft_intro_comment


def test_draft_includes_owner_reference_and_skills() -> None:
    reference = {
        "name": "parseConfig",
        "file": "app/config.py",
        "summary": "3 callers, no branches, no nearby tests.",
    }
    owner = {"author": "octocat", "commit_count": 5}

    draft = draft_intro_comment(reference, owner, ["Python", "TypeScript"])

    assert draft.startswith("Hi @octocat,")
    assert "`parseConfig`" in draft
    assert "app/config.py" in draft
    assert "3 callers, no branches, no nearby tests" in draft
    assert "Python, TypeScript" in draft


def test_draft_omits_owner_when_none_found() -> None:
    draft = draft_intro_comment(None, None, [])
    assert draft.startswith("Hi,")
    assert "@" not in draft


def test_draft_omits_skills_line_when_user_has_no_skills() -> None:
    reference = {"name": "helper", "file": "lib/helper.py", "summary": "1 caller, no branches, has a nearby test."}
    draft = draft_intro_comment(reference, None, [])
    assert "experience with" not in draft


def test_draft_omits_code_context_when_no_reference_matched() -> None:
    draft = draft_intro_comment(None, None, ["Go"])
    assert "Looking at" not in draft
    assert "Go" in draft


def test_draft_omits_code_context_when_reference_has_no_summary() -> None:
    reference = {"name": None, "file": "lib/helper.py", "summary": None}
    draft = draft_intro_comment(reference, None, [])
    assert "Looking at" not in draft


def test_draft_always_ends_with_dive_in_line() -> None:
    draft = draft_intro_comment(None, None, [])
    assert draft.endswith("Let me know if there's a preferred approach before I dive in!")
