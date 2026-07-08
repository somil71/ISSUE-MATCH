from app.services.blast_radius import FunctionBlastRadius
from app.services.blast_radius_summary import summarize


def _blast(
    fan_in=0,
    cyclomatic_complexity=1,
    has_test_coverage=False,
    normalized_churn=0.0,
) -> FunctionBlastRadius:
    return FunctionBlastRadius(
        function_id="f",
        fan_in=fan_in,
        cyclomatic_complexity=cyclomatic_complexity,
        has_test_coverage=has_test_coverage,
        churn_intensity=0.0,
        normalized_fan_in=0.0,
        normalized_complexity=0.0,
        normalized_churn=normalized_churn,
        score=0.0,
        bucket="start_here",
    )


def test_summarize_safe_function() -> None:
    blast = _blast(fan_in=2, cyclomatic_complexity=1, has_test_coverage=True)
    assert summarize(blast) == "2 callers, no branches, has a nearby test."


def test_summarize_risky_function_with_high_churn() -> None:
    blast = _blast(
        fan_in=38,
        cyclomatic_complexity=5,
        has_test_coverage=False,
        normalized_churn=0.9,
    )
    assert summarize(blast) == (
        "38 callers, complex branching (4 decision points), no nearby tests, changes often."
    )


def test_summarize_zero_callers_and_zero_branches() -> None:
    blast = _blast(fan_in=0, cyclomatic_complexity=1, has_test_coverage=False)
    assert summarize(blast) == "No other callers, no branches, no nearby tests."


def test_summarize_omits_churn_clause_when_not_notably_high() -> None:
    blast = _blast(fan_in=1, cyclomatic_complexity=2, normalized_churn=0.3)
    assert "changes often" not in summarize(blast)
