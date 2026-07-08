import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    SESSION_MAX_AGE_SECONDS,
    create_session_token,
    encrypt_token,
    read_session_token,
)
from app.db.models import User
from app.db.session import get_db
from app.services import github_client

router = APIRouter()

STATE_COOKIE = "oauth_state"
SESSION_COOKIE = "session"


@router.get("/auth/login")
async def login() -> RedirectResponse:
    state = secrets.token_urlsafe(24)
    redirect = RedirectResponse(github_client.build_authorize_url(state))
    redirect.set_cookie(
        STATE_COOKIE, state, httponly=True, samesite="lax", max_age=600
    )
    return redirect


@router.get("/auth/callback")
async def callback(
    request: Request,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    settings = get_settings()
    expected_state = request.cookies.get(STATE_COOKIE)
    if not expected_state or expected_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    try:
        access_token = await github_client.exchange_code_for_token(code, state)
        profile = await github_client.fetch_authenticated_user(access_token)
    except github_client.GitHubOAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = await db.execute(select(User).where(User.github_id == profile["id"]))
    user = result.scalar_one_or_none()
    encrypted = encrypt_token(access_token)

    if user is None:
        user = User(
            github_id=profile["id"],
            username=profile["login"],
            avatar_url=profile.get("avatar_url", ""),
            encrypted_access_token=encrypted,
        )
        db.add(user)
    else:
        user.username = profile["login"]
        user.avatar_url = profile.get("avatar_url", "")
        user.encrypted_access_token = encrypted

    await db.commit()
    await db.refresh(user)

    redirect = RedirectResponse(settings.frontend_url)
    redirect.delete_cookie(STATE_COOKIE)
    redirect.set_cookie(
        SESSION_COOKIE,
        create_session_token(user.id),
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE_SECONDS,
    )
    return redirect


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    user_id = read_session_token(token) if token else None
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/auth/me")
async def me(user: User = Depends(get_current_user)) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "skills": user.skills,
        "experience_level": user.experience_level,
    }


@router.post("/auth/logout")
async def logout() -> Response:
    response = Response(status_code=204)
    response.delete_cookie(SESSION_COOKIE)
    return response
