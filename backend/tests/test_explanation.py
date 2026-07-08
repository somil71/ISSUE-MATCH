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
    # No "bug:"/"fix:" prefix and no clear verb -- neutral framing, since
    # asserting "problem" without either signal would be an unsupported guess.
    result = explain_issue("TypeError in utils.py when parsing empty response")
    assert result.startswith("This issue is about")


def test_explain_issue_handles_empty_title() -> None:
    assert explain_issue("") == "No description available."


def test_explain_issue_strips_conventional_commit_prefixes() -> None:
    """Real GitHub issues overwhelmingly use "feat:"/"Feature Request:"/
    "bug:" style prefixes rather than bare imperative sentences. Without
    stripping the prefix first, these titles never hit the imperative-verb
    check and all fall through to a low-value fallback that just echoes the
    whole title (prefix included) back with no simplification."""
    assert explain_issue(
        "Feature Request: Add popular developer themes (Catppuccin Mocha)"
    ) == "This issue is about adding the popular developer themes (Catppuccin Mocha)."

    assert explain_issue("feat: Add LeetCode Stats Card") == (
        "This issue is about adding the LeetCode Stats Card."
    )

    assert explain_issue("feat: Custom Color Palette Picker for SVGs") == (
        "This issue is about the Custom Color Palette Picker for SVGs."
    )


def test_explain_issue_uses_problem_framing_only_for_bug_prefixes() -> None:
    bug_result = explain_issue("bug: Duplicate Skill Badges in Generator Output")
    assert bug_result.startswith("This issue describes a problem involving")

    feature_result = explain_issue("feat: GitHub Actions Workflow Generator")
    assert feature_result.startswith("This issue is about")
    assert "describes a problem" not in feature_result
