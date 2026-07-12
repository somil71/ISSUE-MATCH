# Development

## Prerequisites

Docker Compose is the supported way to develop this project — the backend depends on `git`, tree-sitter's compiled grammars, and two ML models baked into its image; matching that outside a container is possible but not documented here. See [DEPLOYMENT.md](DEPLOYMENT.md) for first-time setup (OAuth app, `.env`, `docker compose up`).

## Everyday loop

```
docker compose up -d --build     # once, or after a dependency change
docker compose logs -f backend   # or frontend
```

Both services bind-mount the host directory and reload on save (see "Applying code changes" in DEPLOYMENT.md). You do not need to rebuild for a plain code change.

## Running tests

```
docker compose exec backend python -m pytest -q --ignore=workspace tests/
```

`--ignore=workspace` matters: `backend/workspace/` accumulates every repo you've analyzed locally (git clones), and pytest will otherwise try to collect files from inside them — including binary/non-UTF-8 files that break collection outright.

As of this writing: **95 tests**, organized one file per service/route under `backend/tests/`. Every test asserts against a real computed value (hand-constructed source snippets, real temp git repos via `subprocess`, or a real FastAPI `TestClient` request against real Redis) — there is no mocked business logic in this suite. Notable ones:

- `test_call_graph.py` — including a regression test that JSX component usage counts as a call edge.
- `test_dependency_graph.py` — precise caller attribution, transitive BFS, ambiguous-name exclusion, recursion not counted as a self-loop.
- `test_blast_map_route.py` — an end-to-end test hitting the actual `/blast-map` route through the real app and real Redis, not just the underlying pure functions.
- `test_code_owners.py`, `test_churn.py` — git plumbing tested against real temporary repos, not fixtures.

### A gotcha if you write a test against `analysis_cache` and Redis directly

`app/services/cache.get_redis()` is `lru_cache`d for the lifetime of the real app (one event loop, under uvicorn). If a test mixes `asyncio.run(...)` (its own throwaway event loop) with a `TestClient` request (a different loop), the cached Redis client ends up bound to a closed loop and the second call raises `RuntimeError: Event loop is closed`. Call `get_redis.cache_clear()` between the two — `test_blast_map_route.py` has a working example (an autouse fixture that clears the cache before and after each test).

## Type checking, linting, and the production build (frontend)

```
docker compose exec frontend sh -lc "npx tsc --noEmit && npx oxlint src && npm run build"
```

Run all three before considering frontend work done — `tsc --noEmit` alone does **not** catch everything `vite build`'s production TypeScript pass does (e.g. `erasableSyntaxOnly` rejects constructor parameter-property shorthand, which only surfaces during the real build).

## Project conventions

- **No LLM calls, anywhere, in the request path.** Every outbound HTTP call must go through `github_client._request` (or be added to `network_trust` the same way). If you add a new external call, ask whether it belongs in this system at all before wiring it in.
- **Never guess when a signal is ambiguous.** The established pattern (see `call_graph.build_fan_in`, `dependency_graph.build_call_graph`) is: if a fact can't be determined precisely, flag it or omit it — don't pick a plausible-looking default. Follow this for any new signal.
- **Generated text (explanations, drafted comments, PR descriptions) is composed from already-computed structured data, not free-generated.** `explanation.py`, `intro_draft.py`, and `pr_playbook.py` are the reference implementations: deterministic templates over facts the code already knows, never a model call.
- **One `git log` pass per signal, not one call per file.** `churn.py` and `code_owners.py` both do a single repo-wide `git log --name-only` invocation and aggregate in Python. If you add a new git-derived signal, follow this shape rather than shelling out per file.
- **Test against real inputs.** Hand-construct a small source file or temp git repo and assert on the real computed output, matching the existing test files' style, rather than mocking the function under test.

## Adding a new language to the parsing engine

1. Add the tree-sitter grammar package to `backend/requirements.txt` and `backend/Dockerfile` if it needs a system dependency.
2. In `app/services/parsing/languages.py`:
   - Add an `iter_<lang>_functions(root, source) -> Iterator[tuple[str, Node]]` that yields `(name, definition_node)` for every function-like construct.
   - Add an `iter_<lang>_calls(root, source, function_spans) -> Iterator[tuple[str | None, str]]` that walks the tree tracking the enclosing function via `function_spans` (a `{(start_byte, end_byte): function_id}` map, built once per file from step 1's output) and yields `(enclosing_function_id_or_None, callee_name)` for every call site. This is the pattern both Python and JS/TS/TSX follow — see `_iter_python_calls`/`_iter_js_calls` for the exact shape.
   - Add an `is_decision(node, source) -> bool` for cyclomatic complexity (branches, loops, boolean operators — whatever the grammar's decision-point nodes are).
   - Register a new `LanguageSpec` in the `LANGUAGES` dict with the right file extensions.
3. Add tests mirroring `test_call_graph.py`/`test_complexity.py` for the new language — at minimum: a function is discovered, a call is attributed to the correct caller, and a decision point raises complexity by 1.

No changes are needed anywhere else — `call_graph.py`, `dependency_graph.py`, `complexity.py`, and `test_proximity.py` are all language-agnostic and operate on `ParsedFile`/`ParsedFunction`.

## Adding a new blast-radius-style signal

Follow the shape of the existing four signals (fan-in, complexity, test proximity, churn):

1. Compute it as its own pure function taking parsed files / git data in, returning a `dict[function_id, value]` or `dict[file_path, value]` out (see `churn.compute_file_churn`, `code_owners.compute_file_owners`).
2. Wire it into `analysis.py`'s `analyze_repo` alongside the existing signals.
3. If it should affect the score, add a weight constant in `blast_radius.py` — keep weights summing to 1.0 and update `docs/ARCHITECTURE.md`'s formula.
4. If it should just be *shown*, not scored, add it to the `functions` response dict and the frontend's `FunctionMetric` type — it does not need to touch the formula at all (see how `transitive_fan_in` and `direct_callers` were added as supplementary, non-scored fields).

## Directory reference

See [ARCHITECTURE.md](ARCHITECTURE.md#repository-layout) for the full annotated tree and a table of what every backend service module does.
