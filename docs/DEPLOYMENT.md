# Deployment

**Current state, honestly: this runs locally via Docker Compose. It has not been deployed to any cloud host.** This document covers the deployment path that actually exists today, plus what's genuinely required (not assumed) to take it further.

## Prerequisites

- Docker and Docker Compose
- A GitHub account (to register an OAuth App)

## 1. Register a GitHub OAuth App

Go to <https://github.com/settings/developers> → **New OAuth App**.

- **Homepage URL**: `http://localhost:5173`
- **Authorization callback URL**: `http://localhost:8010/api/auth/callback`

Note the Client ID, and generate a Client Secret. Both are required in step 2.

## 2. Configure environment

```
cp backend/.env.example backend/.env
```

Fill in `backend/.env`:

| Variable | Purpose | How to get it |
|---|---|---|
| `GITHUB_CLIENT_ID` | OAuth App client ID | From step 1 |
| `GITHUB_CLIENT_SECRET` | OAuth App client secret | From step 1 |
| `GITHUB_OAUTH_REDIRECT_URI` | Must exactly match the OAuth App's callback URL | `http://localhost:8010/api/auth/callback` |
| `SESSION_SECRET_KEY` | Signs session cookies (itsdangerous) | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `TOKEN_ENCRYPTION_KEY` | Encrypts stored GitHub access tokens at rest (Fernet) | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `FRONTEND_URL` | CORS allow-origin + post-login redirect target | `http://localhost:5173` |
| `DATABASE_URL`, `REDIS_URL` | Already correct for Compose; only change for a non-Compose setup | — |

`backend/.env` is gitignored. Never commit real secrets here.

## 3. Build and start

```
docker compose up -d --build
```

This starts four containers:

| Service | Image | Port (host → container) | Notes |
|---|---|---|---|
| `postgres` | `postgres:16-alpine` | 5432 → 5432 | Stores `users` only |
| `redis` | `redis:7-alpine` | 6379 → 6379 | Per-repo analysis + graph cache, 1-hour TTL |
| `backend` | built from `backend/Dockerfile` | 8010 → 8000 | FastAPI + uvicorn, `--reload` on |
| `frontend` | built from `frontend/Dockerfile` | 5173 → 5173 | Vite dev server, `--host` |

The backend image bakes in the sentence-transformer model and the spaCy pipeline at **build time** (`RUN python -c "...SentenceTransformer('all-MiniLM-L6-v2')"` and `RUN python -m spacy download en_core_web_sm` in `backend/Dockerfile`), so a fresh container never fetches a model over the network at request time. Rebuilding after a dependency change (`docker compose up -d --build backend`) re-runs those layers only if `requirements.txt` changed.

## 4. Run the database migration

The `users` table is managed by Alembic (`backend/migrations/`), and **migrations do not run automatically** — there is no entrypoint script invoking `alembic upgrade head`. Run it once after the first `up`:

```
docker compose exec backend alembic upgrade head
```

Re-run this any time a new migration is added.

## 5. Open the app

<http://localhost:5173>

## Applying code changes

Both `backend/` and `frontend/` are bind-mounted into their containers, so edits on the host take effect without a rebuild:

- **Backend**: uvicorn's `--reload` picks up `.py` changes automatically.
- **Frontend**: Vite's dev server watches for changes. On Windows, Docker bind mounts don't support inotify, so `vite.config.ts` sets `watch: { usePolling: true, interval: 300 }` — HMR works, just polling-based rather than event-based.

If a container's environment variables change (e.g. you edit `backend/.env`), the container must be recreated, not just left running:

```
docker compose up -d --force-recreate backend
```

## Rebuilding after a dependency change

```
docker compose up -d --build backend    # after editing backend/requirements.txt
docker compose up -d --build frontend   # after editing frontend/package.json
```

## Known local-dev friction

- **Port 8000 vs 8010**: the backend listens on `8000` *inside* its container but is published on host port `8010` (see `docker-compose.yml`). This was chosen to dodge a port conflict with an unrelated project on this machine — `GITHUB_OAUTH_REDIRECT_URI` and `docker-compose.yml`'s port mapping must stay in sync if you change it.
- **A stray `workspace/` directory under `backend/`** holds every repo you've analyzed (git clones). It's gitignored and can be deleted freely — a re-analyze will re-clone.
- **pytest picks up `backend/workspace/` if run without a path.** Always run `pytest tests/ --ignore=workspace` (see [DEVELOPMENT.md](DEVELOPMENT.md)), or a stray non-UTF-8 file left over from a previous clone can break collection.

## What real cloud deployment would actually need

Nothing below has been done — this is the honest list of what's left, not a claim about what exists.

1. **Split hosting is the likely shape**: the backend does long-running, stateful work (git clone, tree-sitter parse, in-process ML models) that doesn't fit a stateless serverless function well — a container host (e.g. Railway, Fly.io, a small VM) is the natural fit. The frontend is a static Vite build and fits any static host (e.g. Vercel, Netlify, Cloudflare Pages) with a reverse proxy or rewrite rule for `/api/*` to the backend.
2. **Managed Postgres and Redis** — Compose's `postgres`/`redis` services would be swapped for a hosted equivalent; only `DATABASE_URL`/`REDIS_URL` need to change.
3. **A persistent volume (or size cap + eviction policy) for `backend/workspace/`** — currently unbounded local disk, fine for a demo, not fine unattended in production.
4. **Real secrets management** for `TOKEN_ENCRYPTION_KEY`/`SESSION_SECRET_KEY`/GitHub OAuth credentials, instead of a local `.env` file.
5. **A production ASGI run command** — drop `--reload`, consider multiple uvicorn workers or a process manager, since the current `CMD` in `backend/Dockerfile` is dev-oriented.
6. **A production frontend build**, served statically (`npm run build` → `dist/`) rather than the Vite dev server currently run in the container.
7. **An automated migration step** in the deploy pipeline (`alembic upgrade head`), replacing the manual step above.
8. **Rate-limit and timeout handling** for the GitHub API and for very large repo clones/parses, if this is ever exposed beyond a controlled demo audience.
