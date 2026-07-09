import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.auth import get_current_user
from app.main import app
from app.services import analysis_cache, call_graph, dependency_graph
from app.services.blast_radius import compute_blast_radius
from app.services.cache import get_redis
from app.services.complexity import cyclomatic_complexity
from app.services.parsing.engine import parse_file


class _FakeUser:
    id = 1
    username = "tester"


def _override_user() -> _FakeUser:
    return _FakeUser()


@pytest.fixture(autouse=True)
def _fresh_redis_client_per_test():
    """Each TestClient(app) call here runs its own event loop; get_redis()
    is lru_cached for the app's real lifetime (one loop under uvicorn), so
    without this the client cached by one test's loop would be reused -
    and fail - against the next test's different loop."""
    get_redis.cache_clear()
    yield
    get_redis.cache_clear()


def test_blast_map_route_returns_real_transitive_neighborhood(tmp_path: Path) -> None:
    """End-to-end check of the actual FastAPI route (not just the pure
    functions): builds a real call graph from source, caches it exactly how
    /analyze does, then hits GET /blast-map/{id} through the real app and
    real Redis to confirm the whole wire-up (route, cache schema, BFS)
    works together, not just in isolation."""
    source = """
def leaf():
    return 1

def middle():
    return leaf()

def top():
    return middle()
"""
    path = tmp_path / "sample.py"
    path.write_text(source)
    parsed = parse_file(path, "sample.py")
    assert parsed is not None

    fan_in_metrics = call_graph.build_fan_in([parsed])
    complexity_by_id = {
        fid: cyclomatic_complexity(fm.function.node, fm.function.source, fm.function.language)
        for fid, fm in fan_in_metrics.items()
    }
    blast_radius = compute_blast_radius(fan_in_metrics, complexity_by_id, set(), {})
    graph = dependency_graph.build_call_graph([parsed])

    functions = [
        {
            "id": fid,
            "name": fm.function.name,
            "file": fm.function.relative_path,
            "start_line": fm.function.start_line,
            "blast_radius_score": round(blast_radius[fid].score, 4),
            "bucket": blast_radius[fid].bucket,
        }
        for fid, fm in fan_in_metrics.items()
    ]
    edges = {caller_id: sorted(callee_ids) for caller_id, callee_ids in graph.edges.items()}

    asyncio.run(analysis_cache.store_graph("integration-test/repo", "deadbeef", functions, edges))
    # get_redis() is lru_cached for the lifetime of the real app (one event
    # loop under uvicorn); the setup call above ran its own throwaway loop
    # via asyncio.run, so the cached client's connection is now bound to a
    # closed loop. Clear it so the request below gets a fresh client on
    # TestClient's own loop, same as any two real requests would share one.
    get_redis.cache_clear()

    by_name = {fn.name: fn.id for fn in graph.all_functions.values()}
    leaf_id = by_name["leaf"]

    app.dependency_overrides[get_current_user] = _override_user
    try:
        client = TestClient(app)
        response = client.get(
            f"/api/repos/integration-test/repo/blast-map/{leaf_id}", params={"hops": 3}
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    body = response.json()
    assert body["total_transitive_dependents"] == 2
    assert {n["name"] for n in body["nodes"]} == {"leaf", "middle", "top"}
    edge_pairs = {(e["source"], e["target"]) for e in body["edges"]}
    assert (by_name["middle"], by_name["leaf"]) in edge_pairs
    assert (by_name["top"], by_name["middle"]) in edge_pairs


def test_blast_map_route_404s_for_unanalyzed_repo() -> None:
    app.dependency_overrides[get_current_user] = _override_user
    try:
        client = TestClient(app)
        response = client.get(
            "/api/repos/nobody/never-analyzed/blast-map/some.py::fn:1"
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404
