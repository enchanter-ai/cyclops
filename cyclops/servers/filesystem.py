import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..config import ROOT
from ..enums import Server

HOME = Path(os.environ.get("CYCLOPS_HOME", ROOT / "sandbox" / "home"))
mcp = FastMCP(Server.FILESYSTEM)

@mcp.tool()
def read_file(path: str) -> str:
    target = (HOME / path.replace("~/", "").lstrip("/")).resolve()
    if not str(target).startswith(str(HOME.resolve())):
        return f"denied: {path} is outside the sandbox"
    return target.read_text(encoding="utf-8") if target.is_file() else f"not found: {path}"

if __name__ == "__main__":
    mcp.run()
