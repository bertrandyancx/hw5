# AI Prompt Log

## Problem 1 — Campus Customs Multi-Agent Operations

### Prompt 1

User asked me to work in the `hw5` folder, then provided the Campus Customs assignment screenshots describing the MCP server, FastAPI multi-agent backend, React dashboard, SQLite working copy, shop rules, approvals, and required `gpt-6-luna` Portkey usage.

I implemented the initial backend, dashboard, database copy, and agent scaffolding in `hw5`.

### Follow-up prompt

The user clarified that all agent calls must use only `gpt-6-luna` through Portkey and requested that the implementation be updated accordingly.

What was lacking after the first prompt: the initial implementation did not yet include the required Portkey-backed agent calls or connectivity test.

## Problem 2 — Database Inspection and Harness

### Prompt 1

User asked me to inspect `data/campus_customs.db`, review every table and field, copy the original to `data/campus_customs_new.db` for future mutations, study the three open tickets and their table relationships, and start `output/harness.md` with each table’s fields and why it matters to the agents.

I copied the database, documented all nine tables, and traced the ticket links to inventory, pricing, invoices, vendors, and leases.

### Follow-up prompt

No follow-up was needed. The first prompt specified the database paths, required inspection scope, ticket study, and harness format completely.

What was lacking after the first prompt: nothing material; the task was sufficiently specified to complete directly.

## Problem 9 — Clean Full-Ticket Agent Run

### Prompt 1

User asked me to reset `data/campus_customs_new.db`, note the starting checking balance, run tickets 101, 102, and 103 to resolution, open the Problem 6 desk page, and fill each Actual section with observed agents, delegations, and MCP tools while preserving Expected sections.

I reset the working database and verified the starting checking balance was `$3,400.00` on `2026-08-31`. I installed the declared dependencies, verified Portkey connectivity for `gpt-6-luna`, and attempted the three real runs.

### Follow-up prompt

No follow-up was needed. The first prompt specified the clean-run order, required starting state, comparison page, and Actual-section evidence.

What was lacking after the first prompt: the runtime MCP stdio bridge failed with a broken pipe/closed stream, so no successful agent results were available to record. The Actual sections explicitly document that limitation rather than inventing agent behavior.

## Problem 10 — Ticket Run Reflection

### Prompt 1

User asked me to open the Problem 6 desk page and fill its Reflection tab with a detailed, app-specific evaluation of all three tickets, Expected-versus-Actual comparisons, single-agent tradeoffs, three solvable future problems, and three problems outside the current tools. They required the analysis to use the ticket tabs and Cash tab as evidence.

I filled the Reflection tab with the clean `$3,400.00` Cash evidence, the actual MCP transport failure, ticket-specific comparisons, and concrete future capabilities tied to Campus Customs.

### Follow-up prompt

No follow-up was needed. The first prompt specified the reflection questions, evidence source, and level of detail.

What was lacking after the first prompt: a successful agent run was still unavailable, so the reflection distinguishes planned behavior from the observed failed run instead of claiming resolutions that did not occur.

## Problem 8 — React Operations Dashboard

### Prompt 1

User asked me to build a creative React + Vite + TypeScript frontend that talks to the FastAPI backend on port 8000, lists and runs all three tickets, streams agent activity and summaries, shows resolution state, supports human payment approval, reflects checking-balance changes, and documents the design choices.

I created the Vite project, live polling dashboard, ticket command center, agent transcript, approval interaction, responsive styling, and design rationale.

### Follow-up prompt

No follow-up was needed. The first prompt specified the stack, backend URL, required interactions, startup command, and design-document requirement.

What was lacking after the first prompt: nothing material; the task was sufficiently specified to complete directly.

## Problem 7 — FastAPI Dashboard Backend Routes

### Prompt 1

User asked me to add `backend/main.py` with FastAPI routes for ticket status, running the team on a ticket, recent agent events, human-approved payments, checking balance, and database reset. They also specified the uvicorn command and asked for one-line route documentation in the harness.

I added the FastAPI application, working-database access, append-only event polling, guarded payment mutation, reset route, and harness route list.

### Follow-up prompt

No follow-up was needed. The first prompt specified every required route and the intended server command.

What was lacking after the first prompt: nothing material; the task was sufficiently specified to complete directly.

## Problem 6 — Pre-Wiring Ticket Desk Plan

### Prompt 1

User asked me to plan the expected team behavior for open tickets 101, 102, and 103 before backend wiring, create a double-clickable tabbed `output/desk_tickets.html`, include separate Cash and Reflection tabs marked for later, and document the first Boss call, all targeted delegations, and expected MCP tools for each ticket while leaving room for Actual results.

I created a focused plan with ticket-specific delegation chains rather than sending every specialist to every ticket.

### Follow-up prompt

No follow-up was needed. The first prompt specified the page format, tabs, expected-only content, required planning details, and the later comparison purpose.

What was lacking after the first prompt: nothing material; the task was sufficiently specified to complete directly.

## Problem 5 — PydanticAI Agent Team

### Prompt 1

User asked me to build Boss, Inventory, Accounting, Facilities, and Customer Service with PydanticAI, detailed role prompts, Portkey `gpt-6-luna` models, full delegation connectivity, MCP-backed shop facts, append-only audit logging, additional MCP tools, harness documentation, safety guardrails, and synchronized MCP README documentation.

I added the five prompt files, typed models, shared MCP client bridge, PydanticAI team runner, delegation and MCP tool hooks, audit records, three additional MCP read tools, and the requested documentation.

### Follow-up prompt

No follow-up was needed. The first prompt specified the roles, framework, model, data boundary, audit behavior, documentation locations, and safety requirements.

What was lacking after the first prompt: nothing material; the task was sufficiently specified to complete directly.

## Problem 4 — MCP Registration and Smoke Evidence

### Prompt 1

User asked me to register the MCP server for the vibe coder in a project-root `.mcp.json`, test all three MCP tools while connected, and save JSON evidence containing each prompt, tool name, and database-backed output in `output/mcp_smoke.json`.

I added the local MCP server configuration, declared the `mcp` dependency, and recorded exact outputs for the product, invoice/vendor, and lease tools using the working database.

### Follow-up prompt

No follow-up was needed. The first prompt specified the connection file, required tool coverage, evidence fields, and database consistency requirement.

What was lacking after the first prompt: nothing material; the task was sufficiently specified to complete directly.

## Problem 3 — Initial FastMCP Server Tools

### Prompt 1

User asked me to write a FastMCP server in `mcp_server/` using the working database `data/campus_customs_new.db`, without running it yet. They requested three clear read-only tools needed for the existing tickets, documentation for each tool in the harness with exact table and ticket relationships, and a short MCP README.

I added three database-backed tools: product stock and price lookup, invoice-with-vendor lookup, and lease lookup. I documented the ticket-specific reason for each and left the server unconnected.

### Follow-up prompt

No follow-up was needed. The first prompt specified the implementation location, framework, database, tool count, read-only data constraint, documentation requirements, and no-run requirement.

What was lacking after the first prompt: nothing material; the task was sufficiently specified to complete directly.
