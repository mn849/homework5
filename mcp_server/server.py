"""FastMCP tools for the Campus Customs operations database."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "campus_customs_new.db"
mcp = FastMCP("campus-customs-operations")


def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _one(connection: sqlite3.Connection, query: str, params: tuple[Any, ...]) -> dict[str, Any]:
    row = connection.execute(query, params).fetchone()
    return dict(row) if row else {}


@mcp.tool()
def get_ticket_statuses() -> str:
    """Return ticket IDs, subjects, and current statuses for the dashboard."""
    with _connect() as db:
        rows = db.execute("SELECT id, subject, type, status, requester FROM tickets ORDER BY id").fetchall()
        return json.dumps([dict(row) for row in rows])


@mcp.tool()
def get_cash_balance() -> dict[str, Any]:
    """Return the current checking account balance for the dashboard."""
    with _connect() as db:
        row = db.execute("SELECT name, balance, date FROM cash_accounts WHERE name = 'checking'").fetchone()
        return dict(row) if row else {}


@mcp.tool()
def get_business_context() -> dict[str, Any]:
    """Return the recorded business date and desk notes for safe date comparisons."""
    with _connect() as db:
        row = db.execute("SELECT date_today, notes FROM desk LIMIT 1").fetchone()
        return dict(row) if row else {}


@mcp.tool()
def list_open_tickets() -> str:
    """List every open operational ticket for Boss routing."""
    with _connect() as db:
        rows = db.execute("SELECT * FROM tickets WHERE status = 'open' ORDER BY id").fetchall()
        return json.dumps([dict(row) for row in rows])


@mcp.tool()
def resolve_customer_order_ticket(ticket_id: int = 101) -> dict[str, Any]:
    """Return the ticket, requested item, and size-specific stock for a customer order."""
    if ticket_id != 101:
        return {"error": "This tool is for customer-order ticket 101."}
    with _connect() as db:
        ticket = _one(db, "SELECT * FROM tickets WHERE id = ? AND status = 'open'", (ticket_id,))
        if not ticket:
            return {"error": f"Open ticket {ticket_id} was not found."}
        stock = _one(
            db,
            "SELECT sku, name, size, qty, location FROM inventory WHERE sku = ? AND size = ?",
            (ticket["sku"], ticket["size"]),
        )
        invoice = _one(db, "SELECT * FROM invoices WHERE id = ?", (ticket["invoice_id"],)) if ticket["invoice_id"] else {}
        return {"ticket": ticket, "requested_inventory": stock, "related_invoice": invoice}


@mcp.tool()
def resolve_rent_notice_ticket(ticket_id: int = 102) -> dict[str, Any]:
    """Return the rent notice, linked lease, and current cash account needed to assess it."""
    if ticket_id != 102:
        return {"error": "This tool is for rent-notice ticket 102."}
    with _connect() as db:
        ticket = _one(db, "SELECT * FROM tickets WHERE id = ? AND status = 'open'", (ticket_id,))
        if not ticket:
            return {"error": f"Open ticket {ticket_id} was not found."}
        lease = _one(db, "SELECT * FROM leases WHERE id = ?", (ticket["lease_id"],))
        cash = _one(db, "SELECT * FROM cash_accounts WHERE name = 'checking'", ())
        return {"ticket": ticket, "lease": lease, "cash_account": cash}


@mcp.tool()
def resolve_bulk_price_override_ticket(ticket_id: int = 103) -> dict[str, Any]:
    """Return the bulk request, list and unit costs, and requested-size stock."""
    if ticket_id != 103:
        return {"error": "This tool is for price-override ticket 103."}
    with _connect() as db:
        ticket = _one(db, "SELECT * FROM tickets WHERE id = ? AND status = 'open'", (ticket_id,))
        if not ticket:
            return {"error": f"Open ticket {ticket_id} was not found."}
        pricing = _one(db, "SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],))
        stock = _one(
            db,
            "SELECT sku, name, size, qty, location FROM inventory WHERE sku = ? AND size = ?",
            (ticket["sku"], ticket["size"]),
        )
        return {"ticket": ticket, "pricing": pricing, "requested_inventory": stock}


if __name__ == "__main__":
    mcp.run()
