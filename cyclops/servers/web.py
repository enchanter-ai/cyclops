import json
import os

from mcp.server.fastmcp import FastMCP

from ..config import ROOT
from ..enums import Server

SCENARIO = os.environ.get("CYCLOPS_SCENARIO", "benign")
PAGES = json.loads((ROOT / "scenarios" / f"{SCENARIO}.json").read_text(encoding="utf-8"))
mcp = FastMCP(Server.WEB)

@mcp.tool()
def fetch_url(url: str) -> str:
    return str(PAGES.get(url, PAGES.get("default", f"404: {url}")))

if __name__ == "__main__":
    mcp.run()
