from datetime import date
from pathlib import Path
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import ask, AGENTS

DB = Path(__file__).with_name("campus_customs_new.db")
app = FastAPI(title="Campus Customs Operations")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def rows(query, args=()):
    with db() as conn:
        return [dict(r) for r in conn.execute(query, args).fetchall()]

@app.get("/api/health")
def health(): return {"ok": True, "database": str(DB.name)}

@app.get("/api/desk")
def desk(): return rows("select * from desk limit 1")[0]

@app.get("/api/tickets")
def tickets():
    return rows("""select t.*, v.name vendor_name from tickets t left join invoices i on i.id=t.invoice_id
                  left join vendors v on v.id=i.vendor_id order by t.id""")

@app.get("/api/overview")
def overview():
    d = desk(); ts = tickets()
    return {"date": d["date_today"], "tickets": ts, "open_count": sum(t["status"] == "open" for t in ts),
            "cash": rows("select * from cash_accounts")[0],
            "overdue_invoices": rows("select i.*, v.name vendor_name from invoices i join vendors v on v.id=i.vendor_id where status='open' and due_date < ?", (d["date_today"],)),
            "inventory": rows("select * from inventory"), "leases": rows("select * from leases")}

class Approval(BaseModel):
    approved_by: str

@app.post("/api/tickets/{ticket_id}/resolve")
def resolve(ticket_id: int, approval: Approval):
    if not approval.approved_by.strip(): raise HTTPException(400, "Human approval is required")
    with db() as conn:
        ticket = conn.execute("select * from tickets where id=?", (ticket_id,)).fetchone()
        if not ticket: raise HTTPException(404, "Ticket not found")
        conn.execute("update tickets set status='resolved', notes=coalesce(notes,'') || ? where id=?", (f" Resolved by {approval.approved_by}.", ticket_id))
        conn.commit()
    return {"ok": True, "ticket_id": ticket_id, "status": "resolved"}

@app.get("/api/mcp/tools")
def mcp_tools():
    return {"tools": ["list_tickets", "check_inventory", "find_vendor", "list_overdue_invoices", "prepare_payment", "resolve_ticket"]}

@app.get("/api/agents")
def agents():
    return {"model": "gpt-6-luna", "agents": list(AGENTS)}

class AgentPrompt(BaseModel):
    agent: str
    prompt: str

@app.post("/api/agents/chat")
def agent_chat(request: AgentPrompt):
    try:
        return {"agent": request.agent, "model": "gpt-6-luna", "reply": ask(request.agent, request.prompt)}
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(400, str(exc))

@app.post("/api/mcp/prepare-payment")
def prepare_payment(ticket_id: int, approved_by: str = ""):
    if not approved_by.strip(): raise HTTPException(400, "Payment requires human approval")
    with db() as conn:
        t = conn.execute("select * from tickets where id=?", (ticket_id,)).fetchone()
        if not t or not t["invoice_id"]: raise HTTPException(400, "Ticket has no invoice")
        inv = conn.execute("select * from invoices where id=?", (t["invoice_id"],)).fetchone()
        cash = conn.execute("select balance from cash_accounts where name='checking'").fetchone()[0]
        if inv["status"] != "open": raise HTTPException(400, "Invoice is already closed")
        if inv["amount"] > cash: raise HTTPException(400, "Payment refused: insufficient cash")
        conn.execute("insert into payments(kind,ref_id,amount,account,paid_at,approved_by) values(?,?,?,?,?,?)", ("invoice", inv["id"], inv["amount"], "checking", date.today().isoformat(), approved_by))
        conn.execute("update invoices set status='paid' where id=?", (inv["id"],))
        conn.execute("update cash_accounts set balance=balance-? where name='checking'", (inv["amount"],))
        conn.commit()
    return {"ok": True, "paid": inv["amount"], "approved_by": approved_by}
