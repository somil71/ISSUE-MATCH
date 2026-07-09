import json

from app.services.cache import get_redis

_TTL_SECONDS = 3600
_KEY_PREFIX = "blast_radius_cache"
_GRAPH_KEY_PREFIX = "blast_radius_graph"


async def store_analysis(
    full_name: str,
    commit_sha: str,
    functions: list[dict],
    owners: dict[str, dict] | None = None,
    test_directory: str | None = None,
) -> None:
    """Caches a compact view of an /analyze result so /issues can cross-
    reference issue text against real function-level blast radius data
    without re-cloning and re-parsing the repo. `owners` (file -> real git
    commit authorship) and `test_directory` (this repo's actual test-folder
    convention) ride along in the same cache so the auto-drafted intro
    comment and PR playbook can use them, also without a re-clone."""
    by_name: dict[str, list[dict]] = {}
    for fn in functions:
        by_name.setdefault(fn["name"], []).append(
            {
                "file": fn["file"],
                "bucket": fn["bucket"],
                "score": fn["blast_radius_score"],
                "summary": fn["summary"],
                "has_test_coverage": fn["has_test_coverage"],
                "direct_callers": fn.get("direct_callers", []),
            }
        )
    files = sorted({fn["file"] for fn in functions})

    payload = json.dumps(
        {
            "commit_sha": commit_sha,
            "functions": by_name,
            "files": files,
            "owners": owners or {},
            "test_directory": test_directory,
        }
    )
    redis = get_redis()
    await redis.set(f"{_KEY_PREFIX}:{full_name}", payload, ex=_TTL_SECONDS)


async def load_analysis(full_name: str) -> dict | None:
    redis = get_redis()
    payload = await redis.get(f"{_KEY_PREFIX}:{full_name}")
    if payload is None:
        return None
    return json.loads(payload)


async def store_graph(
    full_name: str,
    commit_sha: str,
    functions: list[dict],
    edges: dict[str, list[str]],
) -> None:
    """Caches the real caller->callee graph (by function id) plus enough
    per-node metadata to render a Blast Radius Map without re-cloning and
    re-parsing the repo on every click."""
    nodes = {
        fn["id"]: {
            "name": fn["name"],
            "file": fn["file"],
            "start_line": fn["start_line"],
            "bucket": fn["bucket"],
            "score": fn["blast_radius_score"],
        }
        for fn in functions
    }
    payload = json.dumps({"commit_sha": commit_sha, "nodes": nodes, "edges": edges})
    redis = get_redis()
    await redis.set(f"{_GRAPH_KEY_PREFIX}:{full_name}", payload, ex=_TTL_SECONDS)


async def load_graph(full_name: str) -> dict | None:
    redis = get_redis()
    payload = await redis.get(f"{_GRAPH_KEY_PREFIX}:{full_name}")
    if payload is None:
        return None
    return json.loads(payload)
