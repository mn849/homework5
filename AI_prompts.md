# AI Prompts — Homework 5

This log records the prompts I use while completing Homework 5, one problem at a time.

## Problem 1: Vibe coder prompts
- Initial prompt: "okay bb set up a folder for the hw"
- Follow-up prompt: "make sure we have the .env files and everything like that"
- Reason for follow-up: The folder setup needed environment templates and ignore rules while keeping the shared API key private.

## Problem 2: Study the Campus Customs database
- Initial prompt: "1. Inspect every table and field inside `data/campus_customs.db`. Make a duplicate named `data/campus_customs_new.db`, as later tasks will modify this working copy. 2. Examine the three open customer tickets to understand how they reference other database tables. 3. Initialize `output/harness.md`. For each database table, record its fields and add a brief, single-line explanation of why that table is important for your agents. You will continue expanding this file throughout the assignment."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the initial prompt specified the database inspection, working copy, ticket review, and harness documentation.

## Problem 3: Build the MCP server
- Initial prompt: "1. Write an MCP server inside `mcp_server/` using FastMCP that connects to `data/campus_customs_new.db`. (You do not need to run or connect it yet.) 2. Create three initial MCP tools that you know will be necessary to handle the database tickets. Use clear names and strictly rely on actual database records rather than inventing data. 3. Document your three MCP tools in `output/harness.md`. For each tool, specify which table it queries, which ticket it unlocks (101, 102, or 103), and one sentence justifying why it is the correct tool for that specific ticket (avoid vague descriptions like \"reads inventory\"). 4. Create an `mcp_server/README.md` explaining the purpose of the MCP server, the database file it uses, and its three tools."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the updated Homework 5 database was located in Downloads and used for the implementation.

## Problem 4: Add the MCP server to vibe coder and test each tool
- Initial prompt: "1. Connect your MCP server to your vibe coder (e.g., Claude Code, Cursor, or Codex) so it can execute the tools. Save the local connection settings in `.mcp.json` at the project root. 2. Test all three MCP tools through your connected vibe coder and save the evidence in `output/mcp_smoke.json`. For each tool, document: the prompt given to the vibe coder, the tool's name, and the exact tool output, ensuring it matches the values in `data/campus_customs_new.db`."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the MCP connection and smoke-test requirements were complete after fixing the rent-notice query parameter.

## Problem 5: Build the agent team and grow the MCP tools
- Initial prompt: "1. Build a PydanticAI multi-agent team consisting of a Boss, Inventory, Accounting, Facilities, and Customer Service agent. Set up prompts, models, and agent loops allowing full cross-delegation and connectivity. 2. Place agent prompts in `backend/prompts/` (one file per agent), data schemas in `backend/models.py`, and agent logic under `backend/`. Use `PORTKEY_API_KEY` and restrict every agent model strictly to `gpt-6-luna`. 3. Write comprehensive, customized prompts for each agent detailing their specific shop rules and operational scope. Detailed prompts score higher than generic ones. 4. Add any additional tools required by the agents into your MCP server. All shop facts must come directly through the MCP server querying `data/campus_customs_new.db`—do not bypass MCP with a separate tool layer. 5. Configure the agents to append execution steps and events to `output/audit_trail.json` so they can be audited later without overwriting previous runs. 6. Update `output/harness.md` to list all agents, all MCP tools (including new ones), and the tables they use. Include a safety section outlining business guardrails for handling real customers and money, as well as token-usage limits. 7. Update `mcp_server/README.md` to reflect your current, complete tool list."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the initial prompt specified the team, prompts, model restriction, MCP boundary, audit trail, harness, safety, and README requirements.

## Problem 6: Plan the three tickets
- Initial prompt: "1. Before writing the backend logic, map out your expected workflow for each open ticket. Create `output/desk_tickets.html` as a local HTML page with individual tabs for each ticket (101, 102, 103), plus empty Cash and Reflection tabs. 2. On each ticket tab, fill out an Expected section (leaving space for an Actual section to be completed later). 3. In each Expected section, describe in your own words which agent the Boss should contact first and why, the specific delegations you expect to happen (avoid generic \"Boss calls everyone\" plans), and which MCP tools you expect will be utilized during that run. 4. Plans that unnecessarily involve every specialist on every ticket will lose points. You will later compare this plan against real execution outcomes."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the initial prompt specified the tabs, expected/actual sections, focused delegations, and MCP tools.

## Problem 7: Backend routes
- Initial prompt: "Build a FastAPI backend in `backend/main.py` to support your React frontend. Implement routes that return the three tickets and their current open/resolved statuses; accept a ticket ID and execute your agent team on that ticket; return recent agent events (statements and tool usages) to allow dashboard refreshing; process human approval for payments or purchases (agents only stage transactions; this route executes the cash change); return the current checking account balance from `cash_accounts`; and reset the database back to its original state for fresh runs. Run the server from the `backend/` directory using `uvicorn main:app --reload --port 8000`. Document each API route in one line within `output/harness.md` (listing its URL and function)."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the initial prompt specified all route behaviors, the run command, and harness documentation.

## Problem 8: Agent dashboard
- Initial prompt: "1. Build a React + Vite + TypeScript frontend dashboard inside `frontend/` that interacts with your FastAPI backend. At a minimum, the dashboard should display all three tickets; allow you to select a ticket and trigger the agent team; visualize live agent dialogue and actions while a ticket is processing; automatically mark a ticket as resolved upon completion; summarize each agent's contributions for a given ticket; provide a human approval control for pending payments and purchases; and display the current checking balance, which updates after a payment is approved. 2. Design a polished, creative user interface that feels like an authentic, enjoyable workstation. 3. Configure the frontend to communicate with `http://localhost:8000` and enable CORS on the backend to accept requests from your Vite origin, typically `http://localhost:5173`. Launch the board using `npm run dev`. 4. Create `output/design.md` detailing your design decisions, layout choices, visual differentiators for agents, and creative elements that enhance the user experience."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the initial prompt specified the dashboard interactions, visual direction, backend URL, launch command, and design documentation.

## Problem 9: Resolve the tickets
- Initial prompt: "1. Reset `data/campus_customs_new.db` to a clean state and note the starting checking balance. Run all three tickets (101, 102, 103) through the dashboard until fully resolved. 2. Open `output/desk_tickets.html` and complete the Actual section for each ticket, detailing which agents worked, how they delegated tasks, and which tools were used (retaining your original Expected notes for comparison). 3. On the Cash tab of `output/desk_tickets.html`, itemize financial changes: the starting checking balance, the financial impact of each resolved ticket, specific transactions and dollar amounts, and the final checking balance matching `cash_accounts` in the working database. 4. Save `output/resolved_tickets.json` with each ticket's ID, final status, summary outcome, agent contributions, and human approvals, and save `output/resolved_board.html` with records of the React dashboard for each resolved ticket. 5. Append all live runs to `output/audit_trail.json` and finalize `output/harness.md`."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the initial prompt specified the reset, live runs, Actual notes, cash reconciliation, evidence files, audit trail, and harness completion.

## Problem 10: Reflection
- Initial prompt: "Open `output/desk_tickets.html`, navigate to the Reflection tab, and write a thorough, detailed evaluation using your own voice covering agent performance on each ticket; Expected versus Actual execution for each ticket; what could be simplified with a single agent and tools; three new problems the current team and tools could solve; and three problems it could not solve with the tools and agents needed. Ground every answer in the three tickets, ticket tabs, and Cash tab."
- Follow-up prompt: None used.
- Reason for follow-up: Not applicable; the initial prompt specified the Reflection tab, all comparison questions, capability analysis, and required ticket/cash evidence.

## Problem 11: Submit to GitHub
- Initial prompt:
- Follow-up prompt (if needed):
- What was missing after the first prompt:
