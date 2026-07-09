from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, auth, blast_map, health, recommendations, trust, users
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="IssueMatch AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(trust.router, prefix="/api")
app.include_router(blast_map.router, prefix="/api")
