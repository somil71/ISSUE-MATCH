from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.cache import get_redis

router = APIRouter()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    services = {"database": "error", "cache": "error"}

    try:
        await db.execute(text("SELECT 1"))
        services["database"] = "ok"
    except Exception:
        pass

    try:
        redis = get_redis()
        await redis.ping()
        services["cache"] = "ok"
    except Exception:
        pass

    status = "ok" if all(v == "ok" for v in services.values()) else "degraded"
    return {"status": status, "services": services}
