# Campus Customs MCP Server

This FastMCP server gives every homework agent a shared, read-only interface to
the shop database. It uses the working copy at
`data/campus_customs_new.db`; the original `data/campus_customs.db` is never
modified by this server.

## Tools

- `list_open_tickets()` reads `tickets` and returns the current work queue.
- `get_shop_date()` reads `desk` and returns the shop’s authoritative date.
- `get_cash_account(name)` reads `cash_accounts` for a read-only balance check.
- `get_product_stock_and_price(sku, size)` reads `inventory` and `pricing` for a
  requested product and size.
- `get_invoice_with_vendor(invoice_id)` reads `invoices` and its linked
  `vendors` record.
- `get_lease(lease_id)` reads the matching `leases` record.

The server is intentionally not connected or run for this problem. Additional
tools, including safe mutation tools, will be added later.
