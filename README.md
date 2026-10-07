# Campus Customs Multi-Agent Operations

Campus Customs is a FastAPI + PydanticAI + FastMCP operations desk with a Vite React dashboard. The original and working SQLite databases are included under `data/`.

## Run the backend

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend:app --reload
```

Put `PORTKEY_API_KEY` in the project-root `.env`, then validate the required model connection with:

```bash
python test_luna.py
```

Then open `frontend/index.html` in a browser. The dashboard reads from the working copy `campus_customs_new.db`; `campus_customs.db` remains untouched.

The API exposes ticket, inventory, finance, approval, and MCP-tool endpoints under `/api`. Payments require an approver name, reject insufficient cash, and update both `payments` and `cash_accounts` atomically.

All five agents call Portkey with `gpt-6-luna` through the shared implementation in `agents.py`.

## Clean-run order

1. Reset the working database with `cp data/campus_customs.db data/campus_customs_new.db`.
2. Start the MCP server with `.venv/bin/python mcp_server/server.py` when using a compatible MCP client.
3. Start the backend from `backend/` with `uvicorn main:app --reload --port 8000`.
4. Start the React board from `frontend/` with `npm install && npm run dev`.
5. Before a full three-ticket run, reset the working database again. Payments remain human-approved through the dashboard route.

Never commit `.env`; copy `.env.example` to `.env` and add the Portkey key locally.
