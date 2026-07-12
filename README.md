# IssueMatch AI

Find the right open-source issue for the right contributor — and know exactly why it's safe to touch, who to ask, and what to say.

IssueMatch AI matches contributors to GitHub issues while proving, through pure static analysis, exactly how risky each issue's touched code is to modify. **Zero LLM calls, zero external AI API** — every number and every generated sentence on screen is traceable to a visible formula or a real git/AST fact computed live, not a model's guess. That guarantee is enforced structurally, not just claimed: every outbound HTTP call in the backend is routed through one instrumented function, and the live Trust Panel in the UI shows exactly which hosts have been contacted this session (should always be `api.github.com` only).

📖 **[Architecture](docs/ARCHITECTURE.md)** — system design, data flow, service map, key formulas and decisions
🚀 **[Deployment](docs/DEPLOYMENT.md)** — first-time setup, environment variables, running it, honest gaps for real cloud hosting
🛠️ **[Development](docs/DEVELOPMENT.md)** — everyday workflow, tests, conventions, how to extend the engine
👋 **[Onboarding Guide](docs/ONBOARDING.md)** — comprehensive guide for onboarding new developers (concepts, decisions, architecture, schemas, models)

## Stack

- **Frontend**: React 19 + Vite + TypeScript + Tailwind CSS v4, React Query
- **Backend**: FastAPI, tree-sitter (Python/JavaScript/TypeScript/TSX), sentence-transformers (`all-MiniLM-L6-v2`, local/CPU), scikit-learn (TF-IDF), spaCy (`en_core_web_sm`)
- **Data**: PostgreSQL (users), Redis (per-repo analysis + call-graph cache, 1-hour TTL)
- **Auth**: real GitHub OAuth (Fernet-encrypted token storage, signed session cookies)

## Quick start

Requires Docker. Full walkthrough (OAuth app registration, env vars, migrations) is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — short version:

```
cp backend/.env.example backend/.env   # then fill in GitHub OAuth credentials + generated keys
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

Open <http://localhost:5173>.

## What it actually does

**Analyze a repo** (`POST /repos/{owner}/{name}/analyze`) — partial-clones the repo, parses every Python/JS/TS/TSX file with tree-sitter, and computes, per function:

- **Fan-in** — how many places call it, resolved by name across the whole repo. When a name is ambiguous (more than one function shares it), it's flagged rather than guessed.
- **Transitive fan-in** — the real caller→callee graph (not just name counts) walked outward with BFS: everything that depends on this function, directly or indirectly. Click any function name in the results table to open the **Blast Radius Map**, a radial visualization of that graph you can click through hop by hop.
- **Cyclomatic complexity** — real AST decision-node counting (branches, loops, boolean operators, `except`/`catch` clauses).
- **Test proximity** — whether a same-named test exists anywhere in the repo's test files.
- **Git churn** — commit frequency and recency for the file, from one `git log` pass (not one call per file).

These four signals combine into a weighted **Blast Radius Score** (fan-in 0.35, complexity 0.30, test proximity 0.20, churn 0.15), bucketed into **Start Here** vs. **Here Be Dragons**. The bucket boundary is a slider in the UI — the weights never change, only where the line falls on the same score. Each function also gets a plain-English summary sentence ("2 callers, no branches, has a nearby test") generated from the same numbers shown in the bars, not a separate claim.

**Rank open issues** (`GET /repos/{owner}/{name}/issues`) — local sentence-transformer embeddings compare each issue's text against the contributor's declared + GitHub-inferred skills, cosine-similarity ranked, with TF-IDF overlap terms shown as the "why." Each issue also gets:

- **A deterministic explanation** of what the issue is actually about (spaCy dependency parsing + SVO extraction), with conventional-commit-style prefixes (`feat:`, `fix:`, `Bug:`) stripped before analysis.
- **Real code cross-references** — backtick-quoted function/file names in the issue text are matched (exact match only, never fuzzy) against the cached analysis, showing the actual blast-radius bucket of the code the issue names.
- **A GitHub-label accuracy check** — whether GitHub's own "good first issue"/"help wanted" label agrees with what the engine finds in the named code, surfaced as one aggregate stat plus a list of disagreements (issues labeled beginner-friendly that quietly touch "Here Be Dragons" code).
- **An auto-drafted intro comment** — a ready-to-post "I'd like to work on this" GitHub comment, naming the specific function the issue touches, its real blast-radius summary, and (via real git commit authorship — most recent human author of that file, bot commits filtered out) who to tag for context.
- **A contributor playbook** — the step after the comment: a suggested branch name, the exact function's real direct callers as a "read these first" pointer, concrete test guidance (pointing at this repo's actual test-directory convention, not a guess), and a ready PR description with `Closes #N`. Every line composed from facts already computed above, never generated by a model.

**Readiness score** — repo-level fit: skill overlap (0.40) + inverse average blast radius (0.35) + skill-gap-size penalty (0.25), each term traceable to something already shown elsewhere on the page. Skill gap itself is a plain set-difference between skills parsed from the repo's own manifests (`requirements.txt`, `pyproject.toml`, `package.json`, `Dockerfile`) and the contributor's skills.

**Beginner-oriented views**, all derived from the same underlying signals:
- **First Merge Path** — the 3 lowest-risk "Start Here" functions, ordered as a suggested on-ramp.
- **Codebase Landmarks** — the 5 most depended-on functions by fan-in, i.e. what to touch last.
- **Risk tolerance slider** — re-buckets the existing scores live, client-side, without recomputing anything.

Full data flow and formulas: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## API surface

| Route | Purpose |
|---|---|
| `GET /api/auth/login`, `/callback`, `POST /logout` | GitHub OAuth |
| `POST /api/repos/{owner}/{name}/analyze` | Clone + parse + score a repo, cache the result |
| `GET /api/repos/{owner}/{name}/issues` | Ranked, explained, cross-referenced open issues + contributor playbook |
| `GET /api/repos/{owner}/{name}/blast-map/{function_id}` | Real transitive-dependents neighborhood for the Blast Radius Map |
| `GET /api/trust/network` | Live log of every outbound host actually contacted this session |
| `GET /api/auth/me`, `PATCH /api/users/me` | Skill profile |
| `GET /api/health` | Postgres + Redis reachability |

## Tests

```
docker compose exec backend python -m pytest -q --ignore=workspace tests/
```

95 tests, all against real computed values (no mocked business logic) — call-graph resolution including JSX component usage as a real dependency edge, transitive graph BFS, cyclomatic complexity, blast radius arithmetic, skill-gap set difference, issue explanation, readiness formula, label accuracy, security cookie rules, input path validation, real git authorship/churn against temp repos, and an end-to-end integration test that hits the actual Blast Radius Map route through a real FastAPI app and real Redis.

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) and [docs/ONBOARDING.md](docs/ONBOARDING.md) for the full test/lint/build workflow, project conventions, and detailed technical specs.

## Non-goals (for now)

Private repos, languages beyond Python/JS/TS/TSX, and cross-repo search are out of scope. Actual cloud deployment hasn't been done yet — see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#what-real-cloud-deployment-would-actually-need) for the honest list of what that would require.
