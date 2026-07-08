from app.services.recommendation import rank_issues


def test_rank_issues_orders_by_relevance_and_surfaces_overlap_terms() -> None:
    user_skill_text = "Python, FastAPI, PostgreSQL"
    issues = [
        "Fix bug in FastAPI authentication middleware for PostgreSQL sessions",
        "Update Rust WASM bindings for the graphics renderer",
        "Improve Python type hints in the FastAPI routing layer",
    ]

    matches = rank_issues(user_skill_text, issues)

    assert [m.issue_index for m in matches][0] in (0, 2)
    assert matches[-1].issue_index == 1
    assert matches[-1].overlapping_terms == []

    top_match = next(m for m in matches if m.issue_index == 0)
    assert "fastapi" in top_match.overlapping_terms
    assert "postgresql" in top_match.overlapping_terms


def test_rank_issues_handles_empty_issue_list() -> None:
    assert rank_issues("Python", []) == []
