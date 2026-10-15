# Campus Customs Dispatch Board

## Design direction

The dashboard is a dark “dispatch console” for a small operations team. Navy and ink surfaces make long event streams easy to scan, while warm amber marks decisions and cash, mint marks safe completion, and violet identifies the Boss. The visual language is intentionally closer to a calm control room than a generic starter dashboard.

## Layout

The page uses three working columns. The left rail is the open-ticket queue with ticket number, requester, type, status, SKU, size, and quantity. The center is the selected-ticket workspace: a clear header, a compact fact strip, a live event stream, and a completion banner. The right rail keeps the checking balance, the five-agent roster, and the human approval gate visible while an operator watches a run.

## Agent differentiation

Each agent has a distinct badge color and symbol in the roster and event stream: Boss uses violet, Inventory cyan, Accounting amber, Facilities green, and Customer Service rose. The roster counts events attributed to each agent, while the stream labels the event type, timestamp, detail, and MCP tool where available. This makes delegation and tool use readable without requiring the operator to parse raw JSON.

## Interaction choices

The operator selects one ticket, starts the team, and sees the event stream refresh while the request is processing. A successful run refreshes the ticket list and marks that ticket resolved. The approval card keeps cash movement explicit: an operator must enter a name and amount before the frontend calls `POST /approve-pay`; the balance then refreshes from the backend. The refresh control reloads tickets, events, and balance for a second operator taking over the desk.

## Creative elements

The small “MCP LINKED” indicator and live queue note make the board feel connected to a working system. The warm balance card treats cash as a high-attention object, while the “human gate” copy explains why the final click belongs to a person. The event stream uses short operational labels and a scrollable trace so the interface feels active without becoming noisy.

## Frontend-to-backend wiring

The Vite app uses `http://localhost:8000` directly, polls `/events` while a run is active, refreshes `/tickets` and `/cash/balance` after actions, and sends approvals to `/approve-pay`. The FastAPI CORS middleware permits the Vite development origin and the board launches with `npm run dev` from `frontend/`.
