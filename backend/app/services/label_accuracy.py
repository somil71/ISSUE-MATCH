def compute_label_accuracy(ranked_issues: list[dict]) -> dict:
    """The core thesis made into one quotable number: how often does
    GitHub's manually-applied "good first issue"/"help wanted" label
    disagree with what the engine actually finds in the code the issue
    names? Only counts issues where we have a real, exact code reference
    (see issue_code_refs) -- never a guess dressed up as a disagreement.
    """
    labeled = [issue for issue in ranked_issues if issue["beginner_friendly_label"]]
    verified = [issue for issue in labeled if issue["code_references"]]

    disagreements = []
    for issue in verified:
        risky_ref = next(
            (ref for ref in issue["code_references"] if ref["bucket"] == "here_be_dragons"),
            None,
        )
        if risky_ref is not None:
            disagreements.append(
                {
                    "number": issue["number"],
                    "title": issue["title"],
                    "url": issue["url"],
                    "risky_reference": risky_ref,
                }
            )

    return {
        "github_labeled_count": len(labeled),
        "verified_count": len(verified),
        "disagreement_count": len(disagreements),
        "disagreements": disagreements,
    }
