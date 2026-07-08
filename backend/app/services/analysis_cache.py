import json

from app.services.cache import get_redis

_TTL_SECONDS = 3600
_KEY_PREFIX = "blast_radius_cache"


async def store_analysis(full_name: str, commit_sha: str, functions: list[dict]) -> None:
    """Caches a compact view of an /analyze result so /issues can cross-
    reference issue text against real function-level blast radius data
    without re-cloning and re-parsing the repo."""
    by_name: dict[str, list[dict]] = {}
    for fn in functions:
        by_name.setdefault(fn["name"], []).append(
            {"file": fn["file"], "bucket": fn["bucket"], "score": fn["blast_radius_score"]}
        )
    files = sorted({fn["file"] for fn in functions})

    payload = json.dumps({"commit_sha": commit_sha, "functions": by_name, "files": files})
    redis = get_redis()
    await redis.set(f"{_KEY_PREFIX}:{full_name}", payload, ex=_TTL_SECONDS)


async def load_analysis(full_name: str) -> dict | None:
    redis = get_redis()
    payload = await redis.get(f"{_KEY_PREFIX}:{full_name}")
    if payload is None:
        return None
    return json.loads(payload)
