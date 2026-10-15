# MGT 409 Homework 5 — Campus Customs Operations

This project is a multi-agent Campus Customs operations desk. It includes a FastMCP server, a PydanticAI team using `gpt-6-luna`, a FastAPI backend, and a React/Vite/TypeScript dispatch board.

## Environment

Create the project environment and install backend dependencies:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The agents load `PORTKEY_API_KEY` from the repository root `.env`. Copy `.env.example` to `.env` and add the key locally; never commit the real `.env`. Every agent uses `gpt-6-luna` through Portkey.

## Database clean runs

The original database is `data/campus_customs.db`. Before a fresh run, restore the working copy:

```bash
cp data/campus_customs.db data/campus_customs_new.db
```

The FastAPI reset route does the same operation:

```bash
curl -X POST http://localhost:8000/reset
```

## Start the MCP server

From the project root, after installing `mcp<2`:

```bash
.venv/bin/python mcp_server/server.py
```

The local MCP connection settings are in `.mcp.json`. The agent backend connects to this server over stdio and uses it as the source of Campus Customs facts.

## Start the FastAPI backend

The assignment launch command is run from `backend/`:

```bash
cd backend
../.venv/bin/uvicorn main:app --reload --port 8000
```

The API serves tickets, agent runs, audit events, human approvals, cash balance, and database reset at `http://localhost:8000`.

## Start the React board

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`. The board polls agent events while a ticket runs, displays the checking balance, and sends human approvals to the FastAPI backend.

## Full three-ticket run

1. Restore `data/campus_customs_new.db` from the original database with the copy command above or `POST /reset`.
2. Start the MCP server, FastAPI backend, and React board.
3. Run tickets 101, 102, and 103 from the board.
4. Review `output/audit_trail.json`, `output/desk_tickets.html`, and `output/resolved_tickets.json`.
5. Confirm the ending balance in `cash_accounts` before approving any real payment or purchase.

## Project evidence

- `output/harness.md` — database, MCP, agent, API, dashboard, and safety documentation.
- `output/desk_tickets.html` — Expected, Actual, Cash, and Reflection tabs.
- `output/resolved_board.html` — static records of the three resolved runs.
- `output/mcp_smoke.json` — MCP tool smoke-test evidence.
