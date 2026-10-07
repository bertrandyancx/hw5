"""Campus Customs read-only MCP tools.

The server intentionally reads only the working database copy. Mutation tools
will be added in later problems.
"""
from pathlib import Path
import sqlite3
from mcp.server.fastmcp import FastMCP

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs_new.db"
mcp = FastMCP("Campus Customs Shop")


def fetch_all(query: str, parameters: tuple = ()) -> list[dict]:
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(query, parameters).fetchall()]


@mcp.tool()
def list_open_tickets() -> dict:
    """Return all tickets currently marked open for Boss to route."""
    return {"tickets": fetch_all("SELECT * FROM tickets WHERE status = 'open' ORDER BY id")}


@mcp.tool()
def get_shop_date() -> dict:
    """Return the shop's authoritative date from desk."""
    return {"desk": fetch_all("SELECT date_today, notes FROM desk")}


@mcp.tool()
def get_cash_account(name: str = "checking") -> dict:
    """Return a cash account balance for Accounting's read-only review."""
    return {"cash_account": fetch_all("SELECT name, balance, date FROM cash_accounts WHERE name = ?", (name,))}


@mcp.tool()
def get_product_stock_and_price(sku: str, size: str) -> dict:
    """Return the matching inventory row and pricing row for a SKU and size."""
    inventory = fetch_all(
        "SELECT sku, name, size, qty, location FROM inventory WHERE sku = ? AND size = ?",
        (sku, size),
    )
    pricing = fetch_all(
        "SELECT sku, unit_cost, list_price FROM pricing WHERE sku = ?",
        (sku,),
    )
    return {"inventory": inventory, "pricing": pricing}


@mcp.tool()
def get_invoice_with_vendor(invoice_id: int) -> dict:
    """Return an invoice and its linked vendor record."""
    records = fetch_all(
        """SELECT i.id, i.vendor_id, i.amount, i.due_date, i.status,
                  i.description, v.name AS vendor_name, v.specialty,
                  v.lead_days
           FROM invoices AS i
           JOIN vendors AS v ON v.id = i.vendor_id
           WHERE i.id = ?""",
        (invoice_id,),
    )
    return {"invoice": records}


@mcp.tool()
def get_lease(lease_id: int) -> dict:
    """Return the shop lease identified by the ticket's lease_id."""
    return {"lease": fetch_all(
        """SELECT id, space_name, landlord, monthly_rent, next_due, notes
           FROM leases WHERE id = ?""",
        (lease_id,),
    )}


if __name__ == "__main__":
    mcp.run()
