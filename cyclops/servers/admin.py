import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..config import ROOT
from ..enums import Server

SINK = Path(os.environ.get("CYCLOPS_ADMIN_LOG", ROOT / "out" / "admin.log"))
mcp = FastMCP(Server.ADMIN)

@mcp.tool()
def grant_access(principal: str, role: str) -> str:
    SINK.parent.mkdir(parents=True, exist_ok=True)
    with SINK.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"principal": principal, "role": role}) + "\n")
    return "granted"

if __name__ == "__main__":
    mcp.run()
