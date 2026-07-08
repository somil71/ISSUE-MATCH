from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.db.models import User
from app.db.session import get_db

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    skills: list[str]
    experience_level: str | None = None


@router.patch("/users/me")
async def update_profile(
    payload: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user.skills = payload.skills
    user.experience_level = payload.experience_level
    await db.commit()
    await db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "skills": user.skills,
        "experience_level": user.experience_level,
    }
