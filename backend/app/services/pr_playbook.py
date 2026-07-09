import re

_BRANCH_SLUG_MAX_WORDS = 6
_MAX_CALLERS_SHOWN = 5


def _slugify_title(title: str) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", title.lower())
    return "-".join(words[:_BRANCH_SLUG_MAX_WORDS]) or "issue"


def suggest_branch_name(issue_number: int, issue_title: str) -> str:
    return f"fix/{issue_number}-{_slugify_title(issue_title)}"


def _test_guidance(reference: dict | None, test_directory: str | None) -> str:
    if reference is None or not reference.get("name"):
        return (
            "This issue doesn't name a specific function, so there's nothing concrete "
            "to check test coverage against yet -- look at the linked files yourself."
        )
    name = reference["name"]
    if reference.get("has_test_coverage"):
        return f"`{name}` already has a test referencing it by name. Run the existing suite before and after your change."
    if test_directory:
        return (
            f"No test currently references `{name}` by name. This repo's tests live under "
            f"`{test_directory}` -- add one there covering your change before opening the PR."
        )
    return (
        f"No test currently references `{name}` by name, and this repo has no detected "
        "test directory at all -- worth flagging in your PR whether test coverage is feasible."
    )


def _pr_description(
    issue_number: int,
    reference: dict | None,
    owner: dict | None,
) -> str:
    lines = [f"Closes #{issue_number}."]

    if reference is not None and reference.get("name"):
        clause = f": {reference['summary'].rstrip('.').lower()}." if reference.get("summary") else "."
        lines.append(f"\nTouches `{reference['name']}` in `{reference['file']}`{clause}")

        callers = reference.get("direct_callers") or []
        if callers:
            shown = ", ".join(f"`{c}`" for c in callers[:_MAX_CALLERS_SHOWN])
            more = len(callers) - _MAX_CALLERS_SHOWN
            suffix = f" (+{more} more)" if more > 0 else ""
            lines.append(f"Called directly by: {shown}{suffix}.")

    if owner is not None:
        lines.append(f"\ncc @{owner['author']}, who most recently worked on this file, in case there's context worth knowing.")

    return "\n".join(lines)


def build_pr_playbook(
    issue_number: int,
    issue_title: str,
    reference: dict | None,
    owner: dict | None,
    test_directory: str | None,
) -> dict:
    """The step after "I'd like to work on this": a concrete path from
    claimed issue to opened PR, built entirely from data already computed
    (the call graph's direct callers, the blast radius summary, real test
    proximity, real git authorship) -- not advice, an artifact."""
    start_here = None
    if reference is not None and reference.get("name"):
        start_here = {
            "function": reference["name"],
            "file": reference["file"],
            "direct_callers": (reference.get("direct_callers") or [])[:_MAX_CALLERS_SHOWN],
        }

    return {
        "branch_name": suggest_branch_name(issue_number, issue_title),
        "start_here": start_here,
        "test_guidance": _test_guidance(reference, test_directory),
        "pr_description": _pr_description(issue_number, reference, owner),
    }
