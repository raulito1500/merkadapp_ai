# Merkadapp AI

Python services that add AI features to the Merkadapp ecosystem: recipe suggestions backed by a semantic cache, an agent that turns e-mailed electronic invoices into bills, an MCP server that exposes Merkadapp as tools, and household-level permissions.

**Status:** in active development, built phase by phase. Recipes and the invoice agent work end to end, the MCP server has its first tool, and households and evals are still empty.

Part of the Merkadapp ecosystem:
- [merkadapp](https://github.com/raulito1500/merkadapp) — Go + MongoDB backend (bills, products, market lists)
- [merkadapp_expenses-api](https://github.com/raulito1500/merkadapp_expenses-api) — NestJS + MongoDB backend (expenses, groups)
- [merkadapp_frontend](https://github.com/raulito1500/merkadapp_frontend) — React SPA

## How it fits together

One Python repo, several independently deployable services on Render, so each one can scale, fail and redeploy on its own like the rest of the ecosystem:

| Service | Kind | What it does |
|---|---|---|
| `services/recipes` | web service | `GET /recipes/options` proposes 3 recipes from recently bought ingredients; `POST /recipes/detail` looks for a similar saved recipe (pgvector) and only calls Gemini when nothing is close enough. |
| `services/invoices` | cron job | Reads invoice e-mails from Gmail, lets Gemini decide via tool calling whether it's a supermarket invoice, and submits the attached XML to the Go API. Orchestrated as a LangGraph `StateGraph` (decide → execute → respond). |
| `services/mcp_server` | local stdio server | Exposes Merkadapp operations as MCP tools; `get_bill` works from Claude Desktop. |
| `services/households` | web service | *Not started.* Households, roles and permissions on top of Supabase Auth + Row Level Security. |

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
  merkadapp_client.py    client for the Go API (ingredients, bills, invoice upload, market lists)
  expenses_client.py     client for the NestJS expenses API
  llm.py                 Gemini client
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
    mail_reader.py       Gmail OAuth, MIME traversal, ZIP/XML extraction
    tools.py             `submit_invoice` tool declaration
    agent.py             tool-calling loop
    graph.py             same flow as a LangGraph state graph
  mcp_server/            MCP server (server.py)
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

Both Merkadapp backends must be running locally. Signing in needs a real Firebase Authentication account with email and password. The invoice agent also needs Gmail OAuth files (`credentials.json`, generated `token.json`; both gitignored).

To try the MCP server from Claude Desktop, register `services/mcp_server/server.py` by absolute path in its config (Claude Desktop ignores `cwd`).
