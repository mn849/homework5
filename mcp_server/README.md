# Campus Customs MCP server

This FastMCP server exposes read-only, database-backed tools for the Campus Customs operations agents. It uses `../data/campus_customs_new.db`, the working copy that later homework problems may modify. The tools return only records found in SQLite and report missing records instead of inventing values.

## Tools

- `get_ticket_statuses` — reads `tickets` for dashboard status refreshes.
- `get_cash_balance` — reads `cash_accounts` for the current checking balance.
- `get_business_context` — reads `desk` and supplies the recorded business date and notes.
- `list_open_tickets` — reads `tickets` and gives Boss the open-ticket queue.
- `resolve_customer_order_ticket` — ticket 101; reads `tickets`, `inventory`, and the linked `invoices` row to determine whether the requested Bulldog tee size is available and what invoice is attached.
- `resolve_rent_notice_ticket` — ticket 102; reads `tickets`, the linked `leases` row, and the `checking` row in `cash_accounts` to support the rent notice with the actual due date, rent, and balance.
- `resolve_bulk_price_override_ticket` — ticket 103; reads `tickets`, `pricing`, and size-specific `inventory` to evaluate the requested 20-hoodie bulk request using recorded costs, list price, and stock.

The server is configured for local stdio use through the project `.mcp.json`.

The Problem 5 agent team uses these tools through `backend/mcp_gateway.py`; no backend agent reads the SQLite file directly.
