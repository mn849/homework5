# Database Harness Notes

## Database copies

- Source inspected: `data/campus_customs.db`
- Working copy: `data/campus_customs_new.db`
- The working copy matches the updated Downloads database before later modifications.

## Open tickets and links

| Ticket | Request | Database links |
|---:|---|---|
| 101 | Bulldog tee (customer_order) | inventory.sku, pricing.sku, invoices.id |
| 102 | Rent due (rent_notice) | leases.id |
| 103 | Bulk hoodie discount (price_override) | inventory.sku, pricing.sku |

## Tables and fields

### `cash_accounts`

Current account balances and dates used when assessing cash commitments.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `name` | `TEXT` | no | primary key | Display name for a product, account, or vendor. |
| `balance` | `REAL` | yes |  | Account balance. |
| `date` | `TEXT` | yes |  | As-of date. |

Row count: **1**.

### `desk`

Current operating date and notes used as shared desk context.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `date_today` | `TEXT` | yes |  | Current business date. |
| `notes` | `TEXT` | no |  | Free-form operational notes. |

Row count: **1**.

### `inventory`

SKU, size, quantity, and location records used to answer stock questions.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `sku` | `TEXT` | yes | primary key | Stock keeping unit linking tickets, inventory, and pricing. |
| `name` | `TEXT` | yes |  | Display name for a product, account, or vendor. |
| `size` | `TEXT` | yes | primary key | Requested inventory size. |
| `qty` | `INTEGER` | yes |  | Requested or available quantity. |
| `location` | `TEXT` | yes |  | Physical inventory location. |

Row count: **10**.

### `invoices`

Vendor bills, amounts, due dates, and statuses used to track open payables.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `id` | `INTEGER` | no | primary key | Stable record identifier. |
| `vendor_id` | `INTEGER` | yes |  | Vendor identifier linked to vendors.id. |
| `amount` | `REAL` | yes |  | Dollar amount. |
| `due_date` | `TEXT` | yes |  | Invoice due date. |
| `status` | `TEXT` | yes |  | Workflow status such as open. |
| `description` | `TEXT` | no |  | Invoice description. |

Row count: **1**.

### `leases`

Rent obligations, landlord, due date, and space information used for rent notices.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `id` | `INTEGER` | no | primary key | Stable record identifier. |
| `space_name` | `TEXT` | yes |  | Leased space. |
| `landlord` | `TEXT` | yes |  | Lease counterparty. |
| `monthly_rent` | `REAL` | yes |  | Recurring rent amount. |
| `next_due` | `TEXT` | yes |  | Next rent due date. |
| `notes` | `TEXT` | no |  | Free-form operational notes. |

Row count: **1**.

### `payments`

Recorded payment transactions and approvals used to verify whether obligations were paid.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `id` | `INTEGER` | no | primary key | Stable record identifier. |
| `kind` | `TEXT` | yes |  | Payment category. |
| `ref_id` | `INTEGER` | no |  | Related record identifier. |
| `amount` | `REAL` | yes |  | Dollar amount. |
| `account` | `TEXT` | yes |  | Account used for payment. |
| `paid_at` | `TEXT` | yes |  | Payment date. |
| `approved_by` | `TEXT` | yes |  | Approver name. |

Row count: **0**.

### `pricing`

Unit cost and list price by SKU used for pricing decisions.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `sku` | `TEXT` | no | primary key | Stock keeping unit linking tickets, inventory, and pricing. |
| `unit_cost` | `REAL` | yes |  | Recorded vendor cost per unit. |
| `list_price` | `REAL` | yes |  | Recorded customer list price. |

Row count: **4**.

### `tickets`

Open work requests and their links to inventory, leases, and invoices.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `id` | `INTEGER` | no | primary key | Stable record identifier. |
| `type` | `TEXT` | yes |  | Ticket category. |
| `requester` | `TEXT` | yes |  | Person or organization requesting action. |
| `subject` | `TEXT` | yes |  | Short request subject. |
| `sku` | `TEXT` | no |  | Stock keeping unit linking tickets, inventory, and pricing. |
| `size` | `TEXT` | no |  | Requested inventory size. |
| `qty` | `INTEGER` | no |  | Requested or available quantity. |
| `lease_id` | `INTEGER` | no |  | Lease identifier linked to leases.id. |
| `invoice_id` | `INTEGER` | no |  | Invoice identifier linked to invoices.id. |
| `status` | `TEXT` | yes |  | Workflow status such as open. |
| `notes` | `TEXT` | no |  | Free-form operational notes. |
| `created_at` | `TEXT` | yes |  | Ticket creation timestamp. |

Row count: **3**.

### `vendors`

Vendor identities, specialties, and lead times used for purchasing decisions.

| Field | Type | Required | Key | Meaning / agent use |
|---|---|---:|---|---|
| `id` | `INTEGER` | no | primary key | Stable record identifier. |
| `name` | `TEXT` | yes |  | Display name for a product, account, or vendor. |
| `specialty` | `TEXT` | yes |  | Vendor service category. |
| `lead_days` | `INTEGER` | yes |  | Vendor lead time in days. |

Row count: **3**.

## Verified relationships

- `tickets.sku` joins product-related records in `inventory.sku` and `pricing.sku`.
- `tickets.lease_id` joins `leases.id`.
- `tickets.invoice_id` joins `invoices.id`.
- `invoices.vendor_id` identifies the vendor in `vendors.id` when vendor details are needed.

## MCP tools

- `resolve_customer_order_ticket` queries `tickets`, `inventory`, and `invoices` for ticket 101 because the Bulldog tee request needs stock by SKU and size plus its linked invoice.
- `resolve_rent_notice_ticket` queries `tickets`, `leases`, and `cash_accounts` for ticket 102 because the rent notice needs the linked lease obligation and current checking balance.
- `resolve_bulk_price_override_ticket` queries `tickets`, `pricing`, and `inventory` for ticket 103 because the bulk hoodie request needs recorded prices and size-specific quantity before any discount decision.

## Agent team (Problem 5)

| Agent | Prompt file | Operational scope | MCP-backed facts used |
|---|---|---|---|
| Boss | `backend/prompts/boss.md` | Routes tickets, coordinates specialists, synthesizes evidence, and escalates decisions. | `tickets`, `desk`, plus specialist tool results. |
| Inventory | `backend/prompts/inventory.md` | Checks exact SKU, size, quantity, and location for orders and bulk requests. | `tickets`, `inventory`. |
| Accounting | `backend/prompts/accounting.md` | Reviews invoice status, due dates, payments, and cash evidence without approving money movement. | `tickets`, `invoices`, `payments`, `cash_accounts`, `desk`. |
| Facilities | `backend/prompts/facilities.md` | Reviews leases, rent timing, cash evidence, and landlord notices. | `tickets`, `leases`, `cash_accounts`, `payments`, `desk`. |
| Customer Service | `backend/prompts/customer_service.md` | Converts verified operational evidence into safe customer/vendor/landlord messages. | `tickets` and the specialist tool results. |

Every agent uses the exact model `gpt-6-luna` through Portkey and loads `PORTKEY_API_KEY` from the repository root `.env` without hard-coding it.

## Complete MCP tool list

| MCP tool | Tables queried | Agent/ticket use |
|---|---|---|
| `get_ticket_statuses` | `tickets` | The dashboard refreshes ticket IDs, requesters, subjects, and open/resolved statuses. |
| `get_cash_balance` | `cash_accounts` | The dashboard displays the current checking balance without a backend SQLite read. |
| `get_business_context` | `desk` | Every role can compare due dates with the recorded business date. |
| `list_open_tickets` | `tickets` | Boss discovers the current open workload and routes tickets 101–103. |
| `resolve_customer_order_ticket` | `tickets`, `inventory`, `invoices` | Inventory and Accounting resolve ticket 101’s requested Bulldog tee, stock, and linked invoice. |
| `resolve_rent_notice_ticket` | `tickets`, `leases`, `cash_accounts` | Facilities and Accounting resolve ticket 102’s rent obligation and checking balance. |
| `resolve_bulk_price_override_ticket` | `tickets`, `pricing`, `inventory` | Inventory and Accounting resolve ticket 103’s bulk hoodie quantity and recorded pricing. |

Agent code calls these tools through the stdio MCP gateway in `backend/mcp_gateway.py`; it does not open SQLite or create a parallel shop-data layer.

## Safety and token guardrails

- MCP is the source of truth; missing records produce an explicit uncertainty or escalation rather than an invented answer.
- Agents cannot approve payments, refunds, price overrides, shipments, lease changes, or other irreversible actions; a human must approve real-money actions.
- Do not release or promise shipment when a linked invoice is unpaid or overdue; compare dates against the recorded `desk.date_today`.
- Keep customer, vendor, and financial information limited to the people who need it; never expose credentials or password data.
- Each run has a maximum of 12 agent/MCP steps and delegation depth of 4. Exceeding either limit stops the loop and escalates to a human.
- Every team start, delegation, MCP call, completion, and error appends an event to `output/audit_trail.json`; prior events are retained.

## FastAPI routes (Problem 7)

- `GET /health` — confirms that the backend process is available.
- `GET /tickets` — returns all three ticket IDs, requesters, subjects, types, and current open/resolved statuses through MCP.
- `POST /tickets/{ticket_id}/run` — runs the Boss-led PydanticAI team for ticket 101, 102, or 103 and returns the typed result.
- `GET /events?limit=100` — returns recent append-only agent statements, delegations, MCP tool calls, completions, errors, and human actions for dashboard refreshes.
- `POST /approve-pay` — executes a staged payment or purchase only after a named human approval, updates `payments` and `cash_accounts`, and marks a linked invoice paid when appropriate.
- `GET /cash/balance` — returns the current checking account record through the MCP `get_cash_balance` tool.
- `POST /reset` — restores `data/campus_customs_new.db` from the untouched original `data/campus_customs.db` copy.


## Problem 9 live resolution record

- The working database was reset from `data/campus_customs.db` before the three live dashboard runs. Starting checking balance: **$3,400.00**.
- Ticket 101 resolved with no cash change: inventory showed 0 size-S tees and invoice 501 remained open/overdue; no payment was approved.
- Ticket 102 resolved with no cash change: rent of $2,400 is due 2026-09-02 and no payment record was found; no payment was approved.
- Ticket 103 resolved with no cash change: 8 size-M hoodies were available against a request for 20; no purchase or discount was approved.
- Final checking balance: **$3,400.00**, matching `cash_accounts.balance`; `payments` contains no rows.
- Detailed outcomes are saved in `output/resolved_tickets.json`; static dashboard records are in `output/resolved_board.html`; live traces remain in `output/audit_trail.json`.

## Dashboard (Problems 8–9)

The React/Vite/TypeScript board in `frontend/` uses `http://localhost:8000`, lists all three tickets, polls `/events` during a run, shows color-coded agent dialogue and per-agent contribution summaries, marks a completed run resolved, and refreshes the checking balance after `/approve-pay`. The right rail keeps the human approval form visible, while `output/design.md` records the dispatch-console visual system and interaction choices.

For the live Problem 9 run, all three tickets are marked `resolved` in the working database. This status means the agent workflow completed; each summary separately records any pending human action. The starting and ending checking balance was $3,400.00, with no payments posted.
