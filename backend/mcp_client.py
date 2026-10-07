"""Small stdio MCP client used by agents; shop facts remain behind MCP."""
import json
import os
import subprocess
from pathlib import Path
from typing import Any

SERVER = Path(__file__).resolve().parent.parent / "mcp_server" / "server.py"

class MCPClient:
    def __init__(self) -> None:
        self.proc = None
        self.request_id = 0

    def start(self) -> None:
        self.proc = subprocess.Popen(
            [str(Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"), str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )

    def call(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Invoke an MCP tool over stdio. The protocol handshake is kept here, not in agents."""
        if self.proc is None:
            self.start()
        self.request_id += 1
        def send(method: str, params: dict, expect_response: bool = True) -> dict:
            request = {"jsonrpc": "2.0", "method": method, "params": params}
            if expect_response:
                self.request_id += 1
                request["id"] = self.request_id
            self.proc.stdin.write(json.dumps(request) + "\n"); self.proc.stdin.flush()
            if not expect_response:
                return {}
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("MCP server closed its stdio stream")
            return json.loads(line)
        send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "campus-agents", "version": "1.0"}})
        send("notifications/initialized", {}, expect_response=False)
        result = send("tools/call", {"name": tool_name, "arguments": arguments})
        return result.get("result", result.get("error"))
