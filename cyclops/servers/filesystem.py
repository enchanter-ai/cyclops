import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..config import ROOT
from ..enums import Server

HOME = Path(os.environ.get("CYCLOPS_HOME", ROOT / "sandbox" / "home"))
mcp = FastMCP(Server.FILESYSTEM)

def _contained(path: str) -> Path | None:
    root = HOME.resolve()
    target = (HOME / path.replace("~/", "").lstrip("/")).resolve()
    return target if target.is_relative_to(root) else None

@mcp.tool()
def read_file(path: str) -> str:
    target = _contained(path)
    if target is None:
        return f"denied: {path} is outside the sandbox"
    return target.read_text(encoding="utf-8") if target.is_file() else f"not found: {path}"

if __name__ == "__main__":
    mcp.run()
