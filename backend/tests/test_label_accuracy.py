from app.services.label_accuracy import compute_label_accuracy


def _issue(number, beginner_friendly_label, code_references, title="Some issue", url="https://x"):
    return {
        "number": number,
        "title": title,
        "url": url,
        "beginner_friendly_label": beginner_friendly_label,
        "code_references": code_references,
    }


def test_counts_only_beginner_labeled_issues() -> None:
    issues = [
        _issue(1, True, []),
        _issue(2, False, []),
    ]
    result = compute_label_accuracy(issues)
    assert result["github_labeled_count"] == 1


def test_counts_verified_only_when_code_references_exist() -> None:
    issues = [
        _issue(1, True, []),
        _issue(2, True, [{"name": "foo", "file": "a.py", "bucket": "start_here"}]),
    ]
    result = compute_label_accuracy(issues)
    assert result["github_labeled_count"] == 2
    assert result["verified_count"] == 1


def test_flags_disagreement_when_verified_issue_touches_risky_code() -> None:
    issues = [
        _issue(
            1,
            True,
            [{"name": "risky", "file": "a.py", "bucket": "here_be_dragons"}],
            title="Fix typo",
            url="https://x/1",
        ),
        _issue(2, True, [{"name": "safe", "file": "b.py", "bucket": "start_here"}]),
    ]
    result = compute_label_accuracy(issues)
    assert result["disagreement_count"] == 1
    assert result["disagreements"] == [
        {
            "number": 1,
            "title": "Fix typo",
            "url": "https://x/1",
            "risky_reference": {"name": "risky", "file": "a.py", "bucket": "here_be_dragons"},
        }
    ]


def test_no_disagreement_when_all_verified_references_are_safe() -> None:
    issues = [
        _issue(1, True, [{"name": "safe", "file": "a.py", "bucket": "start_here"}]),
    ]
    result = compute_label_accuracy(issues)
    assert result["disagreement_count"] == 0
    assert result["disagreements"] == []
