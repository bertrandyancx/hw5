# Campus Customs Agent Harness

This harness documents the SQLite data contract used by the agents. The immutable source is `data/campus_customs.db`; agent tools must use the working copy `data/campus_customs_new.db`.

## Tables

| Table | Fields | Why it matters |
|---|---|---|
| `cash_accounts` | `name` (TEXT, PK); `balance` (REAL); `date` (TEXT) | Accounting uses the current balance to refuse payments that would create a negative account. |
| `desk` | `date_today` (TEXT); `notes` (TEXT) | Provides the shop’s authoritative “today” date for overdue and due-date decisions. |
| `inventory` | `sku` (TEXT, PK part); `name` (TEXT); `size` (TEXT, PK part); `qty` (INTEGER); `location` (TEXT) | Inventory checks stock by SKU and size, finds shortages, and reports where items are stored. |
| `invoices` | `id` (INTEGER, PK); `vendor_id` (INTEGER, FK); `amount` (REAL); `due_date` (TEXT); `status` (TEXT); `description` (TEXT) | Accounting tracks unpaid vendor bills and blocks new vendor shipments while an invoice remains open. |
| `leases` | `id` (INTEGER, PK); `space_name` (TEXT); `landlord` (TEXT); `monthly_rent` (REAL); `next_due` (TEXT); `notes` (TEXT) | Facilities handles rent notices and shop-space obligations from this table. |
| `payments` | `id` (INTEGER, PK); `kind` (TEXT); `ref_id` (INTEGER); `amount` (REAL); `account` (TEXT); `paid_at` (TEXT); `approved_by` (TEXT) | Records approved outgoing money and provides an audit trail for accounting actions. |
| `pricing` | `sku` (TEXT, PK); `unit_cost` (REAL); `list_price` (REAL) | Boss and Accounting use cost and list price to evaluate discounts and margins. |
| `tickets` | `id` (INTEGER, PK); `type` (TEXT); `requester` (TEXT); `subject` (TEXT); `sku` (TEXT); `size` (TEXT); `qty` (INTEGER); `lease_id` (INTEGER, FK); `invoice_id` (INTEGER, FK); `status` (TEXT); `notes` (TEXT); `created_at` (TEXT) | The shared work queue; each ticket routes work to one or more specialist agents and links to relevant records. |
| `vendors` | `id` (INTEGER, PK); `name` (TEXT); `specialty` (TEXT); `lead_days` (INTEGER) | Inventory uses vendor specialty and lead time when recommending a restock. |

## Open-ticket relationship study

- **Ticket 101 — Bulldog tee:** `sku=CC-TEE-WHITE`, `size=S`, `qty=1`, and `invoice_id=501`. The matching inventory row has quantity `0`; pricing is unit cost `$8` and list price `$28`. Invoice `501` belongs to vendor `1`, Bulldog Print Co, is `$840`, and is overdue/open. This ticket needs Inventory, Accounting, and Customer Service coordination.
- **Ticket 102 — Rent due:** `lease_id=1`. Lease `1` is the Chapel Street shop, landlord Elm City Properties, monthly rent `$2,400`, due `2026-09-02`. This ticket routes to Facilities and Accounting.
- **Ticket 103 — Bulk hoodie discount:** `sku=CC-HOOD-NAVY`, `size=M`, `qty=20`. Matching inventory is `8`; pricing is unit cost `$22` and list price `$58`. The request therefore needs a shortage/restock check plus margin-aware discount review before Customer Service drafts a response.

## Database reset rule

Before a full run, copy `data/campus_customs.db` over `data/campus_customs_new.db` to restore the original values. Never mutate the source file.

## MCP tools

The read-only FastMCP server is implemented in `mcp_server/server.py` and uses `data/campus_customs_new.db`.

| MCP tool | Tables read | Ticket unlocked | Why this tool is right |
|---|---|---|---|
| `get_product_stock_and_price(sku, size)` | `inventory`, `pricing` | 101 and 103 | Ticket 101 needs to confirm that `CC-TEE-WHITE` size `S` is unavailable and Ticket 103 needs the `CC-HOOD-NAVY` size `M` quantity and price before restocking or evaluating a discount. |
| `get_invoice_with_vendor(invoice_id)` | `invoices`, `vendors` | 101 | Ticket 101 carries `invoice_id=501`, so this tool exposes the linked overdue invoice and Bulldog Print Co details needed before recommending a restock. |
| `get_lease(lease_id)` | `leases` | 102 | Ticket 102 carries `lease_id=1`, so this tool retrieves the Chapel Street rent obligation and due date Facilities and Accounting must act on. |
| `list_open_tickets()` | `tickets` | 101, 102, 103 | Boss uses the live open queue to route exactly the three unresolved tickets without inventing work. |
| `get_shop_date()` | `desk` | 101, 102, 103 | Every agent uses the shop-controlled date to determine whether invoice 501 is overdue or lease 1 is approaching due. |
| `get_cash_account(name)` | `cash_accounts` | 101 and 102 | Accounting uses the checking balance before recommending either the ticket-101 vendor payment or ticket-102 rent payment. |

## Agent team

| Agent | Prompt file | Primary responsibility |
|---|---|---|
| Boss | `backend/prompts/boss.txt` | Routes tickets, delegates to any specialist, reconciles findings, and makes final calls. |
| Inventory | `backend/prompts/inventory.txt` | Checks SKU/size stock, shortages, pricing, and vendor replenishment constraints. |
| Accounting | `backend/prompts/accounting.txt` | Reviews invoices, cash, margins, and approval requirements. |
| Facilities | `backend/prompts/facilities.txt` | Handles lease, rent, landlord, and shop-space obligations. |
| Customer Service | `backend/prompts/customer_service.txt` | Drafts customer-facing messages without sending them. |

## Safety and token guardrails

- Keep all customer and vendor communication as drafts; require explicit human approval before sending anything.
- Require explicit human approval for every payment, verify the current cash balance, and reject any transaction that would make cash negative.
- Use the working database only; preserve the original database for reset and audit every database mutation.
- Never invent stock, dates, prices, vendor lead times, lease terms, or customer commitments; cite MCP results and surface unknowns.
- Bound each run to one ticket, limit delegation depth and total steps, and summarize tool results before passing them onward to control token use.
- Use only `gpt-6-luna` through Portkey, and append audit records rather than overwriting `output/audit_trail.json`.

## FastAPI dashboard routes

- `GET /api/tickets` — returns the three tickets with their current status.
- `POST /api/tickets/{ticket_id}/run` — runs the agent team for one ticket.
- `GET /api/agent-events?limit=100` — returns recent agent statements, tool events, delegations, and errors for board refreshes.
- `POST /api/approve-payment` — human approval route that validates cash and records the approved invoice or purchase payment.
- `GET /api/cash` — returns the current checking balance and date.
- `POST /api/reset` — restores `data/campus_customs_new.db` from the untouched original database.
