from app.services.explanation import explain_issue


def test_explain_issue_handles_imperative_titles() -> None:
    assert explain_issue("Add dark mode toggle to settings page") == (
        "This issue is about adding the dark mode toggle to settings page."
    )
    assert explain_issue("Refactor authentication middleware") == (
        "This issue is about refactoring the logging in a step that runs before your request is handled."
    )
    assert explain_issue("Remove deprecated API endpoints") == (
        "This issue is about removing the deprecated API endpoints."
    )


def test_explain_issue_applies_glossary_substitution() -> None:
    result = explain_issue("Improve error handling for OAuth token refresh")
    assert "keeping you logged in without re-entering your password" in result


def test_explain_issue_falls_back_honestly_when_no_clear_verb() -> None:
    result = explain_issue("TypeError in utils.py when parsing empty response")
    assert result.startswith("This issue describes a problem involving")


def test_explain_issue_handles_empty_title() -> None:
    assert explain_issue("") == "No description available."
