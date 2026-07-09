from collections import defaultdict, deque
from dataclasses import dataclass

from app.services.parsing.engine import ParsedFile, ParsedFunction


@dataclass
class CallGraph:
    all_functions: dict[str, ParsedFunction]
    edges: dict[str, set[str]]
    reverse_edges: dict[str, set[str]]


def build_call_graph(parsed_files: list[ParsedFile]) -> CallGraph:
    """Builds a real caller->callee graph, reusing the same honest name
    resolution as `call_graph.build_fan_in`: a caller is only known precisely
    (each call site is parsed with its exact enclosing function id), but a
    callee is still resolved by name, so an edge is only drawn when exactly
    one function in the repo has that name. Ambiguous or unresolved callees
    are dropped rather than guessed, same policy as fan-in.
    """
    functions_by_name: dict[str, list[ParsedFunction]] = defaultdict(list)
    all_functions: dict[str, ParsedFunction] = {}
    for parsed_file in parsed_files:
        for fn in parsed_file.functions:
            functions_by_name[fn.name].append(fn)
            all_functions[fn.id] = fn

    edges: dict[str, set[str]] = defaultdict(set)
    reverse_edges: dict[str, set[str]] = defaultdict(set)

    for parsed_file in parsed_files:
        for caller_id, callee_name in parsed_file.call_edges:
            if caller_id is None:
                continue
            candidates = functions_by_name.get(callee_name)
            if not candidates or len(candidates) != 1:
                continue
            callee_id = candidates[0].id
            if callee_id == caller_id:
                continue
            edges[caller_id].add(callee_id)
            reverse_edges[callee_id].add(caller_id)

    return CallGraph(
        all_functions=all_functions,
        edges=dict(edges),
        reverse_edges=dict(reverse_edges),
    )


def _bfs_hops(start: str, adjacency: dict[str, set[str]], max_hops: int) -> dict[str, int]:
    distances: dict[str, int] = {}
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    visited = {start}

    while queue:
        current, hops = queue.popleft()
        if hops >= max_hops:
            continue
        for neighbor in adjacency.get(current, ()):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            distances[neighbor] = hops + 1
            queue.append((neighbor, hops + 1))

    return distances


def transitive_dependents(function_id: str, graph: CallGraph, max_hops: int = 4) -> dict[str, int]:
    """Everything that depends on `function_id`, directly or indirectly,
    mapped to hop distance — the literal, traceable "blast radius": if this
    function changes, every id in this map is something that could break."""
    return _bfs_hops(function_id, graph.reverse_edges, max_hops)


def transitive_dependencies(function_id: str, graph: CallGraph, max_hops: int = 4) -> dict[str, int]:
    """Everything `function_id` (transitively) calls — the downstream half."""
    return _bfs_hops(function_id, graph.edges, max_hops)
