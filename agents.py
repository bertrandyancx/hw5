"""Shared Portkey-backed agent team. Every agent intentionally uses gpt-6-luna."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
MODEL = "gpt-6-luna"

def client():
    key = os.environ.get("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is missing from the project-root .env")
    return OpenAI(api_key=key, base_url="https://api.portkey.ai/v1")

AGENTS = {
    "boss": "You are Boss. Route shop tickets, coordinate specialists, and make final recommendations.",
    "inventory": "You are Inventory. Check SKU and size stock, identify shortages, and recommend vendors.",
    "accounting": "You are Accounting. Review cash, invoices, margins, and payment readiness; require approval.",
    "facilities": "You are Facilities. Handle leases, rent notices, due dates, and shop-space issues.",
    "customer_service": "You are Customer Service. Draft clear customer-facing messages; never send them.",
}

def ask(agent: str, prompt: str) -> str:
    if agent not in AGENTS:
        raise ValueError(f"Unknown agent: {agent}")
    response = client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": AGENTS[agent]}, {"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
