from __future__ import annotations

import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

try:
    from .models import Ticket
    from .team import run_team
except ImportError:  # Supports: cd backend && uvicorn main:app --reload --port 8000
    from models import Ticket
    from team import run_team

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DB = ROOT / "data" / "campus_customs.db"
WORKING_DB = ROOT / "data" / "campus_customs_new.db"
AUDIT_FILE = ROOT / "output" / "audit_trail.json"

app = FastAPI(title="Campus Customs Operations API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])


def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(WORKING_DB)
    conn.row_factory = sqlite3.Row
    return conn


def rows(query: str, params: tuple = ()) -> list[dict]:
    with connection() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def audit_event(agent: str, action: str, detail: str, **extra: object) -> None:
    """Append a dashboard-visible event without deleting previous run history."""
    AUDIT_FILE.parent.mkdir(exist_ok=True)
    event = {"run_id": "human-action", "step": 0, "agent": agent, "action": action,
             "detail": detail, "timestamp": datetime.now(timezone.utc).isoformat(), **extra}
    with AUDIT_FILE.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, default=str) + "\n")


class RunRequest(BaseModel):
    requested_by: str = "dashboard"


class ApprovalRequest(BaseModel):
    approved_by: str
    ticket_id: int | None = None
    invoice_id: int | None = None
    kind: str = "invoice"


@app.get("/api/tickets", response_model=list[Ticket])
def get_tickets() -> list[dict]:
    """Return the three assignment tickets and their current open/resolved state."""
    return rows("SELECT * FROM tickets ORDER BY id")


@app.post("/api/tickets/{ticket_id}/run")
async def run_ticket(ticket_id: int, request: RunRequest) -> dict:
    ticket = rows("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    prompt = f"Resolve ticket {ticket_id}. Ticket record: {json.dumps(ticket[0], default=str)}. Use the planned specialist delegations and return an evidence-based recommendation."
    audit_event("boss", "start", f"Team run requested by {request.requested_by}.", ticket_id=ticket_id)
    try:
        result = await run_team(prompt, ticket_id=ticket_id)
    except Exception as exc:
        audit_event("boss", "error", str(exc), ticket_id=ticket_id)
        raise HTTPException(500, f"Agent team failed: {exc}") from exc
    return {"ticket_id": ticket_id, "status": "agent_run_complete", "recommendation": result}


@app.get("/api/agent-events")
def get_agent_events(limit: int = Query(100, ge=1, le=500)) -> list[dict]:
    """Return recent JSONL audit events for dashboard polling."""
    if not AUDIT_FILE.exists():
        return []
    events = []
    for line in AUDIT_FILE.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events[-limit:]


@app.post("/api/approve-payment")
def approve_payment(request: ApprovalRequest) -> dict:
    """Human-only mutation route: pay an invoice after checking cash and approval."""
    if not request.approved_by.strip():
        raise HTTPException(400, "approved_by is required")
    with connection() as conn:
        invoice_id = request.invoice_id
        if invoice_id is None and request.ticket_id is not None:
            linked = conn.execute("SELECT invoice_id FROM tickets WHERE id = ?", (request.ticket_id,)).fetchone()
            invoice_id = linked[0] if linked and linked[0] else None
        if invoice_id is None:
            raise HTTPException(400, "Provide invoice_id or a ticket linked to an invoice")
        invoice = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        cash = conn.execute("SELECT * FROM cash_accounts WHERE name = 'checking'").fetchone()
        if invoice is None or cash is None:
            raise HTTPException(404, "Invoice or checking account not found")
        if invoice["status"] != "open":
            raise HTTPException(409, "Invoice is not open")
        if invoice["amount"] > cash["balance"]:
            raise HTTPException(409, "Payment refused: insufficient checking balance")
        paid_at = date.today().isoformat()
        conn.execute("INSERT INTO payments(kind, ref_id, amount, account, paid_at, approved_by) VALUES (?, ?, ?, ?, ?, ?)",
                     (request.kind, invoice_id, invoice["amount"], "checking", paid_at, request.approved_by.strip()))
        conn.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (invoice_id,))
        conn.execute("UPDATE cash_accounts SET balance = balance - ?, date = ? WHERE name = 'checking'",
                     (invoice["amount"], paid_at))
        conn.commit()
    audit_event("human", "payment_approved", f"Approved {request.kind} payment for invoice {invoice_id}.",
                invoice_id=invoice_id, amount=invoice["amount"], approved_by=request.approved_by)
    return {"ok": True, "invoice_id": invoice_id, "amount": invoice["amount"], "approved_by": request.approved_by}


@app.get("/api/cash")
def get_cash() -> dict:
    account = rows("SELECT name, balance, date FROM cash_accounts WHERE name = 'checking'")
    if not account:
        raise HTTPException(404, "Checking account not found")
    return account[0]


@app.post("/api/reset")
def reset_database() -> dict:
    """Restore the mutable working copy while preserving the original database."""
    if not SOURCE_DB.exists():
        raise HTTPException(500, "Original database not found")
    shutil.copyfile(SOURCE_DB, WORKING_DB)
    audit_event("human", "database_reset", "Working database reset from the original source.")
    return {"ok": True, "database": str(WORKING_DB.relative_to(ROOT))}
