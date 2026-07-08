# IssueMatch AI

Find the right open-source issue for the right contributor — and know exactly why it's safe to touch.

IssueMatch AI matches contributors to GitHub issues while proving, through pure static analysis (tree-sitter AST parsing, call-graph fan-in, cyclomatic complexity, git churn, local sentence embeddings), exactly how risky each issue's touched code is to modify. No LLM calls, no external AI API — every number shown is traceable to a visible formula computed live.

## Stack

- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Backend**: FastAPI, tree-sitter (Python/JS/TS/TSX), sentence-transformers (`all-MiniLM-L6-v2`, local/CPU), scikit-learn (TF-IDF)
- **Data**: PostgreSQL, Redis
- **Auth**: GitHub OAuth

## Running locally

Requires Docker.

1. Copy `backend/.env.example` to `backend/.env` and fill in a GitHub OAuth App's client ID/secret (register one at https://github.com/settings/developers), plus a session secret and a Fernet token-encryption key.
2. `docker compose up -d --build`
3. Open http://localhost:5173

## Features

- **Blast Radius Engine** — fan-in, cyclomatic complexity, test proximity, and git churn combined into a single transparent, weighted score per function, bucketed into "Start Here" vs. "Here Be Dragons".
- **Skill-based issue recommendation** — local sentence embeddings rank open issues against a contributor's declared + GitHub-inferred skills, with TF-IDF overlap terms shown as the "why".

## Tests

```
cd backend
python -m pytest tests/
```
