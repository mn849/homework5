"""FastAPI dashboard backend for the Campus Customs agent team."""
from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .audit import AUDIT_PATH, append_event
    from .mcp_gateway import CampusCustomsMCP
    from .models import AuditEvent
    from .team import run_team
except ImportError:
    from audit import AUDIT_PATH, append_event
    from mcp_gateway import CampusCustomsMCP
    from models import AuditEvent
    from team import run_team

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKING_DB = PROJECT_ROOT / "data" / "campus_customs_new.db"
ORIGINAL_DB = PROJECT_ROOT / "data" / "campus_customs.db"
app = FastAPI(title="Campus Customs Operations API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
mcp = CampusCustomsMCP()


class ApprovalRequest(BaseModel):
    ticket_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    approved_by: str = Field(min_length=2)
    kind: Literal["payment", "purchase"] = "payment"
    ref_id: int | None = None
    account: str = "checking"


class ResetResponse(BaseModel):
    reset: bool
    database: str


def _json_value(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tickets")
async def tickets() -> list[dict]:
    """Return all three tickets and their current statuses through MCP."""
    return _json_value(await mcp.ticket_statuses())


@app.post("/tickets/{ticket_id}/run")
async def run_ticket(ticket_id: int) -> dict:
    """Run the Boss-led agent team for one ticket."""
    if ticket_id not in {101, 102, 103}:
        raise HTTPException(status_code=404, detail="Ticket must be 101, 102, or 103")
    try:
        result = await run_team(ticket_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent run failed: {exc}") from exc
    # A completed team run resolves the ticket for dashboard and future refreshes.
    with sqlite3.connect(WORKING_DB) as db:
        db.execute("UPDATE tickets SET status = 'resolved' WHERE id = ?", (ticket_id,))
        db.commit()
    return result.model_dump(mode="json")


@app.get("/events")
def events(limit: int = 100) -> list[dict]:
    """Return recent append-only agent statements, delegations, and MCP calls."""
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    if not AUDIT_PATH.exists():
        return []
    try:
        rows = json.loads(AUDIT_PATH.read_text())
    except json.JSONDecodeError:
        return []
    return rows[-limit:]


@app.post("/approve-pay")
def approve_pay(request: ApprovalRequest) -> dict:
    """Execute a staged payment or purchase only after a named human approval."""
    if not request.approved_by.strip():
        raise HTTPException(status_code=400, detail="A human approver is required")
    if not WORKING_DB.exists():
        raise HTTPException(status_code=500, detail="Working database is missing")
    with sqlite3.connect(WORKING_DB) as db:
        db.row_factory = sqlite3.Row
        ticket = db.execute("SELECT * FROM tickets WHERE id = ?", (request.ticket_id,)).fetchone()
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        account = db.execute("SELECT * FROM cash_accounts WHERE name = ?", (request.account,)).fetchone()
        if account is None:
            raise HTTPException(status_code=400, detail="Cash account not found")
        if account["balance"] < request.amount:
            raise HTTPException(status_code=409, detail="Insufficient checking balance")
        next_id = db.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM payments").fetchone()[0]
        db.execute("INSERT INTO payments (id, kind, ref_id, amount, account, paid_at, approved_by) VALUES (?, ?, ?, ?, ?, date('now'), ?)", (next_id, request.kind, request.ref_id or request.ticket_id, request.amount, request.account, request.approved_by.strip()))
        db.execute("UPDATE cash_accounts SET balance = balance - ? WHERE name = ?", (request.amount, request.account))
        if ticket["invoice_id"] and request.kind == "payment":
            db.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (ticket["invoice_id"],))
        db.commit()
        new_balance = db.execute("SELECT balance FROM cash_accounts WHERE name = ?", (request.account,)).fetchone()[0]
    append_event(AuditEvent(trace_id=f"approval-{request.ticket_id}-{next_id}", step=0, event="human_approval", agent="human", detail=f"{request.approved_by.strip()} approved {request.kind} for ticket {request.ticket_id}", data={"amount": request.amount, "payment_id": next_id, "new_balance": new_balance}))
    return {"approved": True, "payment_id": next_id, "ticket_id": request.ticket_id, "amount": request.amount, "approved_by": request.approved_by.strip(), "new_balance": new_balance}


@app.get("/cash/balance")
async def cash_balance() -> dict:
    """Return the current checking balance through MCP."""
    return _json_value(await mcp.cash_balance())


@app.post("/reset", response_model=ResetResponse)
def reset_database() -> ResetResponse:
    """Restore the working database from the untouched original copy."""
    if not ORIGINAL_DB.exists():
        raise HTTPException(status_code=500, detail="Original database is missing")
    shutil.copy2(ORIGINAL_DB, WORKING_DB)
    append_event(AuditEvent(trace_id="database-reset", step=0, event="database_reset", agent="human", detail="Working database restored from original copy"))
    return ResetResponse(reset=True, database=str(WORKING_DB))
