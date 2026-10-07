from typing import Any, Literal
from pydantic import BaseModel, Field

AgentRole = Literal["boss", "inventory", "accounting", "facilities", "customer_service"]

class Ticket(BaseModel):
    id: int
    type: str
    requester: str
    subject: str
    sku: str | None = None
    size: str | None = None
    qty: int | None = None
    lease_id: int | None = None
    invoice_id: int | None = None
    status: str
    notes: str | None = None
    created_at: str

class Delegation(BaseModel):
    from_agent: AgentRole
    to_agent: AgentRole
    task: str
    ticket_id: int | None = None

class AgentStep(BaseModel):
    run_id: str
    step: int
    agent: AgentRole
    action: Literal["start", "mcp_tool", "delegate", "response", "error"]
    detail: str
    ticket_id: int | None = None
    tool_name: str | None = None
    result: Any = None
