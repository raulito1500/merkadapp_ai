# Merkadapp AI

Python services that add AI features to the Merkadapp ecosystem: recipe suggestions backed by a semantic cache, an agent that turns e-mailed electronic invoices into bills, an MCP server that exposes Merkadapp as tools, and household-level permissions.

**Status:** early development. The layout below is the target structure; most files are still empty and get filled in phase by phase (see [Roadmap](#roadmap)).

Part of the Merkadapp ecosystem:
- [merkadapp](https://github.com/raulito1500/merkadapp) — Go + MongoDB backend (bills, products, market lists)
- [merkadapp_expenses-api](https://github.com/raulito1500/merkadapp_expenses-api) — NestJS + MongoDB backend (expenses, groups)
- [merkadapp_frontend](https://github.com/raulito1500/merkadapp_frontend) — React SPA

## How it fits together

One Python repo, several independently deployable services on Render, so each one can scale, fail and redeploy on its own like the rest of the ecosystem:

| Service | Kind | What it does |
|---|---|---|
| `services/recipes` | web service | Suggests recipes. Looks for a similar saved recipe first and only calls the LLM when nothing is close enough. |
| `services/invoices` | cron job | Reads invoice e-mails, extracts the attached XML and submits it to the Go API. |
| `services/mcp_server` | web service | Exposes Merkadapp operations (`add_bill`, `get_market_list`, ...) as MCP tools. |
| `services/households` | web service | Households, roles and permissions on top of Supabase Auth + Row Level Security. |

Code shared by the services lives in `shared/`. It authenticates against the existing backends with a Firebase ID token, the same way the frontend does.

## Stack

- **Python 3.12**, type hints everywhere, checked with `pyright`
- **httpx** for HTTP, **FastAPI** + **Pydantic** for the web services
- **Gemini** as the main LLM, Groq as a free fallback for experiments
- **sentence-transformers** for local, free embeddings
- **Supabase** (Postgres + `pgvector`) for vectors, later Supabase Auth
- **Pydantic AI**, **LangGraph** and the **MCP SDK** for the agent phases

## Layout

```
shared/                  code reused by every service
  config.py              environment variables, read in one place
  firebase_auth.py       sign in and get a Firebase ID token
  merkadapp_client.py    client for the Go and NestJS APIs
  llm.py                 Gemini / Groq client
  errors.py              common error helpers
services/
  recipes/               semantic recipe cache (FastAPI)
    main.py              app and endpoints
    models.py            Pydantic models
    embeddings.py        text -> vector
    generator.py         recipe generation with the LLM
    repository.py        Supabase / pgvector access
    service.py           search first, generate on a miss, then save
  invoices/              e-mail invoice agent
  mcp_server/            MCP server
  households/            users, roles, permissions
db/migrations/           SQL files for Supabase, applied in order
evals/                   test cases and cost/token tracking for LLM output
tests/
```

## Running locally

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then fill in the values
```

Both Merkadapp backends must be running locally. Signing in needs a real Firebase Authentication account with email and password.
