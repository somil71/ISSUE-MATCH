# Architecture

This document describes how IssueMatch AI is actually built: the components, the data flow through them, the key design decisions, and the guarantees the system enforces structurally rather than by convention.

## System overview

```
┌─────────────┐      cookies (session, OAuth state)      ┌──────────────────┐
│   Browser    │ ───────────────────────────────────────▶ │  FastAPI backend  │
│ (React/Vite) │ ◀─────────────────────────────────────── │   (port 8000)     │
└─────────────┘         JSON over /api/*                  └──────┬───────────┘
                                                                   │
                                    ┌──────────────────────────────┼───────────────────────────┐
                                    │                               │                            │
                              ┌─────▼─────┐                 ┌───────▼───────┐           ┌────────▼────────┐
                              │ PostgreSQL │                 │     Redis      │           │  api.github.com  │
                              │  (users)   │                 │ (analysis /   │           │  (the only other  │
                              └───────────┘                 │  graph cache) │           │  network peer)    │
                                                              └───────────────┘           └───────────────────┘
```

The backend also shells out to `git` (partial clone into a local `workspace/` directory) and loads two models entirely in-process: a sentence-transformer for embeddings and a spaCy pipeline for dependency parsing. Neither model ever makes a network call at request time — both are baked into the Docker image at build time (see [DEPLOYMENT.md](DEPLOYMENT.md)).

**The zero-external-AI-API guarantee is structural, not a comment.** Every outbound HTTP call in the entire backend goes through one function, `_request` in `app/services/github_client.py`, which logs the destination host via `app/services/network_trust.py` before making the call. `GET /api/trust/network` exposes that log live, and the frontend's Trust Panel polls it every 4 seconds and turns red if any host other than `api.github.com` is ever contacted. This means the claim is falsifiable by inspection — a `grep` for `httpx.AsyncClient` should turn up exactly one call site outside that function (`exchange_code_for_token`, which needs custom error handling and records its own call the same way).

## Repository layout

```
backend/
  app/
    core/           # settings (pydantic-settings), token encryption + session signing
    db/              # SQLAlchemy models, async session factory
    api/routes/       # one file per resource: auth, analysis, recommendations, blast_map, trust, users, health
    services/          # all business logic — see "Service map" below
    main.py             # FastAPI app assembly, CORS, router registration
  migrations/            # Alembic (one migration so far: users table)
  tests/                  # pytest, one file per service/route, real computed assertions
  workspace/               # git clone destination at runtime (gitignored)

frontend/
  src/
    components/       # RepoWorkspace.tsx is the main view; the rest are focused pieces
    lib/                # api.ts (typed fetch wrappers), session.ts (current-user query)
```

## Service map (backend/app/services)

| Module | Responsibility |
|---|---|
| `parsing/languages.py`, `parsing/engine.py` | tree-sitter grammars for Python/JS/TS/TSX; walks each file's AST once to extract function definitions **and** scope-aware call/JSX edges in the same pass |
| `call_graph.py` | Aggregate fan-in: resolves call sites to function definitions by name, repo-wide. Ambiguous names (shared by >1 function) are flagged, never guessed |
| `dependency_graph.py` | The *real* graph: precise caller→callee edges (using the exact enclosing-function id from the parser, not just a name), plus BFS for transitive dependents/dependencies |
| `complexity.py` | McCabe cyclomatic complexity via AST decision-node counting |
| `test_proximity.py` | Recognizes test files by convention; records which names are referenced from them; detects the repo's actual test-directory convention |
| `churn.py` | Git commit frequency/recency per file, from one `git log --name-only` pass |
| `code_owners.py` | Most recent human commit author per file (bot commits filtered), from one `git log` pass |
| `blast_radius.py` | The weighted formula combining fan-in, complexity, test proximity, and churn into one score + bucket |
| `blast_radius_summary.py` | Turns the same numbers into one plain-English sentence per function |
| `analysis_cache.py` | Redis-backed cache of the last `/analyze` result per repo (functions, graph edges, code owners, test directory) so `/issues` never needs to re-clone |
| `embeddings.py`, `recommendation.py` | Local sentence-transformer embeddings + cosine similarity ranking; TF-IDF overlap terms as the "why" |
| `skill_gap.py` | Parses the repo's own manifests into a required-skills set; plain set difference against the user's skills |
| `explanation.py` | spaCy dependency parse → deterministic template sentence explaining what an issue is about |
| `beginner_labels.py`, `label_accuracy.py` | Recognizes GitHub's beginner-friendly labels; checks them against the engine's own bucket for the code the issue names |
| `issue_code_refs.py` | Extracts backtick-quoted function/file names from issue text; resolves them against the cache (exact match only) |
| `intro_draft.py`, `pr_playbook.py` | Compose the auto-drafted GitHub comment and the PR playbook (branch name, start-here pointer, test guidance, PR description) from already-computed facts |
| `readiness.py` | Final weighted formula combining skill overlap, average blast radius, and gap size |
| `network_trust.py`, `github_client.py` | The instrumented network boundary described above |
| `repo_fetcher.py` | Partial git clone (`--filter=blob:none`) and source file enumeration |
| `cache.py` | `lru_cache`d Redis client factory |

## Data flow: analyzing a repo

`POST /api/repos/{owner}/{name}/analyze`

1. Fetch repo metadata from GitHub (default branch, etc.) using the user's own OAuth token.
2. `repo_fetcher.clone_repo` — partial clone (full commit history, no historical blobs) into `backend/workspace/{owner}__{name}`. Re-runs `fetch --all` + `reset --hard` if already cloned, so repeat analyses reflect the latest commit.
3. Enumerate every `.py`/`.js`/`.jsx`/`.mjs`/`.cjs`/`.ts`/`.tsx` file and parse each with `parsing/engine.parse_file`:
   - Walks the AST once to collect every function definition (name, id, byte span).
   - Builds a `function_spans` map (byte span → function id) from step above.
   - Walks the AST **again** for calls/JSX usages, using `function_spans` to attribute each call site to its exact enclosing function id (or `None` for module-level code) — this is what makes the dependency graph precise rather than name-only.
4. `call_graph.build_fan_in` — aggregate fan-in by name, across all parsed files, flagging ambiguous names.
5. `complexity.cyclomatic_complexity` per function.
6. `test_proximity.build_tested_names` + `find_test_directory_convention` — one pass over files recognized as tests.
7. `churn.compute_file_churn` and `code_owners.compute_file_owners` — two more single-pass `git log` invocations (churn needs commit dates, owners needs authors; kept separate since they serve different consumers, but neither is O(files)).
8. `blast_radius.compute_blast_radius` — combines steps 4-7 into one score + bucket per function (weights below).
9. `dependency_graph.build_call_graph` — the precise graph, then BFS (`transitive_dependents`) for a `transitive_fan_in` per function, capped at 6 hops.
10. Results are cached in Redis two ways: `analysis_cache.store_analysis` (function metadata by name, keyed for issue cross-referencing) and `analysis_cache.store_graph` (the graph itself, keyed by function id, for the Blast Radius Map).
11. `skill_gap.extract_required_skills` + `compute_gap`, and `readiness.compute_readiness`, close out the response.

## Data flow: ranking issues

`GET /api/repos/{owner}/{name}/issues`

1. Fetch open issues (excluding PRs) and the user's own repo languages from GitHub.
2. `recommendation.rank_issues` — embed the user's skill text and every issue's title+body locally, cosine-similarity rank, and compute TF-IDF overlap terms.
3. `explanation.explain_issue` — deterministic per-title explanation.
4. If the repo was analyzed already (cache present): `issue_code_refs` extracts backtick-quoted names from the issue text and resolves them exactly against the cache; `label_accuracy` aggregates GitHub-label-vs-engine disagreements; `intro_draft`/`pr_playbook` compose the drafted comment and the next-steps playbook from the matched reference, the cached code owner, and the cached test-directory convention.
5. If the repo was **not** analyzed yet, all of the above degrade to empty/omitted rather than fabricated — `analyzed: false` in the response tells the frontend to prompt for analysis.

## Data flow: the Blast Radius Map

`GET /api/repos/{owner}/{name}/blast-map/{function_id}`

Reads the cached graph (not a re-parse), does a BFS over the reverse edges from the requested function up to `hops` (default 3, max 5), and returns only the nodes/edges within that neighborhood — not the whole graph — keeping the payload bounded regardless of repo size. The frontend lays this out as concentric rings by hop distance (a deterministic radial layout, not a physics simulation) and lets you click any node to re-center the map on it.

## Key formulas

**Blast Radius Score** (`blast_radius.py`), each term min-max normalized across the repo's functions:

```
score = 0.35 × normalized(fan_in)
      + 0.30 × normalized(cyclomatic_complexity)
      + 0.20 × (0 if has_test_coverage else 1)
      + 0.15 × normalized(churn_intensity)

bucket = "start_here" if score < threshold else "here_be_dragons"
```

The threshold defaults to `0.5` server-side but is client-adjustable (the risk tolerance slider re-buckets already-computed scores; it never recomputes the formula).

**Readiness Score** (`readiness.py`):

```
readiness = 0.40 × skill_overlap_ratio
          + 0.35 × (1 − avg_blast_radius_score)
          + 0.25 × 1/(1 + gap_size)
```

**Churn intensity** (`churn.py`): `commit_count / (days_since_last_commit + 1)` — frequent *and* recent changes raise it; either fading lowers it.

## Design decisions worth knowing

- **Name-based call resolution, honestly bounded.** Fan-in and the dependency graph's callee side both resolve calls by name across the repo. When a name is ambiguous, the affected functions are flagged (`name_is_ambiguous`) rather than the tool silently picking one candidate. The caller side of a graph edge is *not* name-based — it's the exact function id determined during parsing — so only the callee resolution carries this caveat.
- **JSX usage counts as a call edge.** `<FitCard />` is a real dependency on `FitCard`, not a `call_expression` node in the grammar — it's matched separately so React/Next.js components don't show a false zero fan-in.
- **Two-pass single-file parse, not two full repo walks.** Function discovery happens once per file; the call/JSX walk reuses that file's own `function_spans`, so scope-tracking doesn't require a second repo-wide pass.
- **Everything shown is either a direct git/AST fact or a value from one of the two formulas above.** There is no step anywhere in the request path that calls an LLM, and the Trust Panel makes that runtime-checkable rather than just documented.
