import json
import os
from http import HTTPStatus
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..config import ROOT
from ..enums import Server

SINK = Path(os.environ.get("CYCLOPS_SINK", ROOT / "out" / "egress.log"))
mcp = FastMCP(Server.NOTIFY)

@mcp.tool()
def post(url: str, body: str) -> str:
    SINK.parent.mkdir(parents=True, exist_ok=True)
    with SINK.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"url": url, "body": body}) + "\n")
    return str(HTTPStatus.ACCEPTED.value)

if __name__ == "__main__":
    mcp.run()
