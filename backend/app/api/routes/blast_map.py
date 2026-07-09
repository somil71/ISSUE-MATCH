from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.routes.auth import get_current_user
from app.db.models import User
from app.services import analysis_cache

router = APIRouter()

_DEFAULT_HOPS = 3
_MAX_HOPS = 5


@router.get("/repos/{owner}/{name}/blast-map/{function_id:path}")
async def get_blast_map(
    owner: str,
    name: str,
    function_id: str,
    hops: int = Query(_DEFAULT_HOPS, ge=1, le=_MAX_HOPS),
    user: User = Depends(get_current_user),
) -> dict:
    """Returns the real transitive-dependents neighborhood of one function --
    everything that calls it, directly or indirectly, up to `hops` away --
    for rendering the Blast Radius Map. Reads the graph cached by /analyze,
    so it never re-clones or re-parses the repo."""
    full_name = f"{owner}/{name}"
    graph_data = await analysis_cache.load_graph(full_name)
    if graph_data is None:
        raise HTTPException(status_code=404, detail="Repo not analyzed yet")

    nodes: dict[str, dict] = graph_data["nodes"]
    edges: dict[str, list[str]] = graph_data["edges"]
    if function_id not in nodes:
        raise HTTPException(status_code=404, detail="Function not found in cached analysis")

    reverse_edges: dict[str, list[str]] = defaultdict(list)
    for caller_id, callee_ids in edges.items():
        for callee_id in callee_ids:
            reverse_edges[callee_id].append(caller_id)

    hop_distance: dict[str, int] = {function_id: 0}
    queue: deque[tuple[str, int]] = deque([(function_id, 0)])
    while queue:
        current, current_hop = queue.popleft()
        if current_hop >= hops:
            continue
        for caller_id in reverse_edges.get(current, ()):
            if caller_id in hop_distance:
                continue
            hop_distance[caller_id] = current_hop + 1
            queue.append((caller_id, current_hop + 1))

    result_nodes = [
        {"id": fid, "hops": hop, **nodes[fid]}
        for fid, hop in hop_distance.items()
        if fid in nodes
    ]
    included_ids = {n["id"] for n in result_nodes}
    result_edges = [
        {"source": caller_id, "target": callee_id}
        for caller_id, callee_ids in edges.items()
        if caller_id in included_ids
        for callee_id in callee_ids
        if callee_id in included_ids
    ]

    return {
        "function_id": function_id,
        "max_hops": hops,
        "total_transitive_dependents": len(hop_distance) - 1,
        "nodes": result_nodes,
        "edges": result_edges,
    }
