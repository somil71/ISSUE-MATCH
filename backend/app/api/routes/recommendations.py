import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.auth import get_current_user
from app.core.security import decrypt_token
from app.db.models import User
from app.services import analysis_cache, github_client
from app.services.beginner_labels import has_beginner_friendly_label
from app.services.explanation import explain_issue
from app.services.intro_draft import draft_intro_comment
from app.services.issue_code_refs import extract_backtick_references, match_code_references
from app.services.label_accuracy import compute_label_accuracy
from app.services.recommendation import rank_issues


router = APIRouter()


def _pick_primary_reference(code_references: list[dict]) -> dict | None:
    """Prefers the riskiest reference an issue names -- that's the one most
    worth flagging in a drafted intro comment -- falling back to whichever
    was matched first."""
    for ref in code_references:
        if ref.get("bucket") == "here_be_dragons":
            return ref
    return code_references[0] if code_references else None


@router.get("/repos/{owner}/{name}/issues")
async def ranked_issues(owner: str, name: str, user: User = Depends(get_current_user)) -> dict:
    full_name = f"{owner}/{name}"
    access_token = decrypt_token(user.encrypted_access_token)

    try:
        issues = await github_client.fetch_open_issues(full_name, access_token)
        inferred_languages = await github_client.fetch_user_repo_languages(
            user.username, access_token
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail="Could not fetch issues from GitHub"
        ) from exc

    skill_terms = [*user.skills, *inferred_languages]
    user_skill_text = ", ".join(skill_terms) if skill_terms else user.username

    issue_texts = [f"{issue['title']}\n\n{issue.get('body') or ''}" for issue in issues]
    matches = rank_issues(user_skill_text, issue_texts)

    # Only present if the repo has already been analyzed (cache keyed by
    # repo, populated by /analyze) -- when absent, we simply omit code
    # references rather than fabricate a signal we haven't computed.
    cached = await analysis_cache.load_analysis(full_name)

    ranked = []
    for m in matches:
        issue = issues[m.issue_index]
        label_names = [label["name"] for label in issue.get("labels", [])]

        code_references = []
        code_owner = None
        if cached is not None:
            refs = extract_backtick_references(f"{issue['title']}\n{issue.get('body') or ''}")
            code_references = match_code_references(refs, cached["functions"], cached["files"])
            primary_reference = _pick_primary_reference(code_references)
            if primary_reference is not None:
                code_owner = cached.get("owners", {}).get(primary_reference["file"])
        else:
            primary_reference = None

        ranked.append(
            {
                "number": issue["number"],
                "title": issue["title"],
                "url": issue["html_url"],
                "labels": [
                    {"name": label["name"], "color": label.get("color", "888888")}
                    for label in issue.get("labels", [])
                ],
                "similarity": round(m.similarity, 4),
                "overlapping_terms": m.overlapping_terms,
                "explanation": explain_issue(issue["title"]),
                "beginner_friendly_label": has_beginner_friendly_label(label_names),
                "code_references": code_references,
                "draft_comment": draft_intro_comment(primary_reference, code_owner, skill_terms),
            }
        )

    return {
        "repo": full_name,
        "user_skills": user.skills,
        "inferred_skills": inferred_languages,
        "analyzed": cached is not None,
        "issues": ranked,
        "label_accuracy": compute_label_accuracy(ranked),
    }
