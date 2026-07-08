from app.services.blast_radius import FunctionBlastRadius

_HIGH_CHURN_THRESHOLD = 0.66


def _fan_in_clause(fan_in: int) -> str:
    if fan_in == 0:
        return "no other callers"
    if fan_in == 1:
        return "1 caller"
    return f"{fan_in} callers"


def _complexity_clause(cyclomatic_complexity: int) -> str:
    branches = cyclomatic_complexity - 1
    if branches <= 0:
        return "no branches"
    if branches <= 2:
        return f"{branches} branch{'es' if branches != 1 else ''}"
    return f"complex branching ({branches} decision points)"


def _test_clause(has_test_coverage: bool) -> str:
    return "has a nearby test" if has_test_coverage else "no nearby tests"


def summarize(blast: FunctionBlastRadius) -> str:
    """The PRD's own pitch is a plain-English verdict ("2 callers, no
    branches, has an adjacent test file") -- the bars show the same data,
    but a beginner scanning a 150-row table shouldn't have to mentally
    recompose four bars into a sentence themselves."""
    clauses = [
        _fan_in_clause(blast.fan_in),
        _complexity_clause(blast.cyclomatic_complexity),
        _test_clause(blast.has_test_coverage),
    ]
    if blast.normalized_churn >= _HIGH_CHURN_THRESHOLD:
        clauses.append("changes often")

    sentence = ", ".join(clauses) + "."
    return sentence[0].upper() + sentence[1:]
