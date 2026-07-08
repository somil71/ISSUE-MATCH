import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.auth import get_current_user
from app.core.security import decrypt_token
from app.db.models import User
from app.services import github_client
from app.services.explanation import explain_issue
from app.services.recommendation import rank_issues

router = APIRouter()


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

    ranked = [
        {
            "number": issues[m.issue_index]["number"],
            "title": issues[m.issue_index]["title"],
            "url": issues[m.issue_index]["html_url"],
            "labels": [
                {"name": label["name"], "color": label.get("color", "888888")}
                for label in issues[m.issue_index].get("labels", [])
            ],
            "similarity": round(m.similarity, 4),
            "overlapping_terms": m.overlapping_terms,
            "explanation": explain_issue(issues[m.issue_index]["title"]),
        }
        for m in matches
    ]

    return {
        "repo": full_name,
        "user_skills": user.skills,
        "inferred_skills": inferred_languages,
        "issues": ranked,
    }
