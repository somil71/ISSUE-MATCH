from fastapi import APIRouter

from app.services import network_trust

router = APIRouter()


@router.get("/trust/network")
async def network_trust_summary() -> dict:
    return network_trust.summary()
