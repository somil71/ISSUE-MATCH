import httpx

from app.core.config import get_settings

AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
API_URL = "https://api.github.com"


class GitHubOAuthError(Exception):
    pass


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
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        response.raise_for_status()
    return response.json()


async def fetch_repo(full_name: str, access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/repos/{full_name}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        response.raise_for_status()
    return response.json()


async def fetch_open_issues(full_name: str, access_token: str, per_page: int = 30) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/repos/{full_name}/issues",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
            params={"state": "open", "per_page": per_page},
        )
        response.raise_for_status()
    # GitHub's issues endpoint also returns pull requests; exclude those.
    return [issue for issue in response.json() if "pull_request" not in issue]
