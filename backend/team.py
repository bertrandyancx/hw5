import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
try:
    from .mcp_client import MCPClient
    from .models import AgentRole, AgentStep
except ImportError:  # Supports importing when uvicorn is launched from backend/
    from mcp_client import MCPClient
    from models import AgentRole, AgentStep

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "output" / "audit_trail.json"
PROMPTS = ROOT / "backend" / "prompts"
MODEL_NAME = "gpt-6-luna"

def make_model() -> OpenAIModel:
    key = os.environ["PORTKEY_API_KEY"]
    portkey = AsyncOpenAI(api_key=key, base_url="https://api.portkey.ai/v1")
    return OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=portkey))

class Deps:
    def __init__(self, run_id: str, agent: AgentRole, client: MCPClient, step: int = 0):
        self.run_id, self.agent, self.client, self.step = run_id, agent, client, step

    def audit(self, action: str, detail: str, **kwargs: Any) -> None:
        self.step += 1
        record = AgentStep(run_id=self.run_id, step=self.step, agent=self.agent, action=action, detail=detail, **kwargs).model_dump()
        AUDIT.parent.mkdir(exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, default=str) + "\n")

def build_agents() -> dict[AgentRole, Agent]:
    agents = {}
    for role in ("boss", "inventory", "accounting", "facilities", "customer_service"):
        agents[role] = Agent(make_model(), system_prompt=(PROMPTS / f"{role}.txt").read_text(), deps_type=Deps,
                             model_settings={"openai_reasoning_effort": "none"})
    def register(agent: Agent, current_role: AgentRole) -> None:
        """Expose named MCP calls so the model can choose the right shop lookup."""
        async def mcp_call(ctx: RunContext[Deps], tool: str, args: dict[str, Any]) -> dict:
            result = ctx.deps.client.call(tool, args)
            ctx.deps.audit("mcp_tool", f"{current_role} read shop facts through MCP.", tool_name=tool, result=result)
            return result
        @agent.tool
        async def list_open_tickets(ctx: RunContext[Deps]) -> dict: return await mcp_call(ctx, "list_open_tickets", {})
        @agent.tool
        async def get_shop_date(ctx: RunContext[Deps]) -> dict: return await mcp_call(ctx, "get_shop_date", {})
        @agent.tool
        async def get_cash_account(ctx: RunContext[Deps], name: str = "checking") -> dict: return await mcp_call(ctx, "get_cash_account", {"name": name})
        @agent.tool
        async def get_product_stock_and_price(ctx: RunContext[Deps], sku: str, size: str) -> dict: return await mcp_call(ctx, "get_product_stock_and_price", {"sku": sku, "size": size})
        @agent.tool
        async def get_invoice_with_vendor(ctx: RunContext[Deps], invoice_id: int) -> dict: return await mcp_call(ctx, "get_invoice_with_vendor", {"invoice_id": invoice_id})
        @agent.tool
        async def get_lease(ctx: RunContext[Deps], lease_id: int) -> dict: return await mcp_call(ctx, "get_lease", {"lease_id": lease_id})
        @agent.tool
        async def delegate(ctx: RunContext[Deps], to_agent: AgentRole, task: str, ticket_id: int | None = None) -> str:
            if to_agent == current_role: raise ValueError("An agent cannot delegate to itself")
            ctx.deps.audit("delegate", f"{current_role} delegated work to {to_agent}: {task}", ticket_id=ticket_id)
            child = Deps(ctx.deps.run_id, to_agent, ctx.deps.client, ctx.deps.step)
            answer = await agents[to_agent].run(task, deps=child)
            ctx.deps.step = child.step
            return answer.output
    for role, agent in agents.items(): register(agent, role)
    return agents

async def run_team(prompt: str, ticket_id: int | None = None) -> str:
    run_id, client = str(uuid.uuid4()), MCPClient()
    agents = build_agents()
    deps = Deps(run_id, "boss", client)
    deps.audit("start", prompt, ticket_id=ticket_id)
    result = await agents["boss"].run(prompt, deps=deps)
    deps.audit("response", "Boss completed the team loop.", ticket_id=ticket_id, result=str(result.output))
    return result.output
