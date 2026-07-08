import httpx

from app.core.config import get_settings
from app.services import network_trust

AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
API_URL = "https://api.github.com"


class GitHubOAuthError(Exception):
    pass


async def _request(method: str, url: str, **kwargs) -> httpx.Response:
    """The only place an HTTP request leaves this backend. Every call is
    routed through here so the trust panel's list of contacted hosts is
    generated from what actually happened, not a claim that could drift
    out of sync with the code."""
    network_trust.record_call(httpx.URL(url).host)
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response


def build_authorize_url(state: str) -> str:
    settings = get_settings()
    url = httpx.URL(
        AUTHORIZE_URL,
        params={
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_oauth_redirect_uri,
            "scope": "read:user public_repo",
            "state": state,
        },
    )
    return str(url)


async def exchange_code_for_token(code: str, state: str) -> str:
    settings = get_settings()
    network_trust.record_call(httpx.URL(TOKEN_URL).host)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_oauth_redirect_uri,
                "state": state,
            },
        )
        response.raise_for_status()
        payload = response.json()

    if "error" in payload:
        raise GitHubOAuthError(payload.get("error_description", payload["error"]))
    return payload["access_token"]


async def fetch_authenticated_user(access_token: str) -> dict:
    response = await _request(
        "GET",
        f"{API_URL}/user",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
    )
    return response.json()


async def fetch_repo(full_name: str, access_token: str) -> dict:
    response = await _request(
        "GET",
        f"{API_URL}/repos/{full_name}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
    )
    return response.json()


async def fetch_user_repo_languages(
    username: str, access_token: str, per_page: int = 100
) -> list[str]:
    """Primary languages of the user's own non-fork public repos, ranked by
    frequency — a lightweight, non-AI stand-in for "skills inferred from
    GitHub activity" (Feature 2)."""
    response = await _request(
        "GET",
        f"{API_URL}/users/{username}/repos",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
        params={"per_page": per_page, "sort": "pushed", "type": "owner"},
    )

    counts: dict[str, int] = {}
    for repo in response.json():
        if repo.get("fork"):
            continue
        language = repo.get("language")
        if language:
            counts[language] = counts.get(language, 0) + 1

    return [lang for lang, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)]


async def fetch_open_issues(full_name: str, access_token: str, per_page: int = 30) -> list[dict]:
    response = await _request(
        "GET",
        f"{API_URL}/repos/{full_name}/issues",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
        params={"state": "open", "per_page": per_page},
    )
    # GitHub's issues endpoint also returns pull requests; exclude those.
    return [issue for issue in response.json() if "pull_request" not in issue]
