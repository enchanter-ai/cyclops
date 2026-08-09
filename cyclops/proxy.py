import asyncio
import contextlib
import json
import os
import sys
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.lowlevel import Server as MCPServer
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import ContentBlock, TextContent
from mcp.types import Tool as MCPTool

from .config import EGRESS
from .detector import Detector
from .enums import Mode, Server, Tool

_SESSION = Path(os.environ.get("CYCLOPS_SESSION", "out/session.json"))

def _text(content: list[ContentBlock]) -> str:
    return "".join(c.text for c in content if isinstance(c, TextContent))

def _blocked() -> list[ContentBlock]:
    return [TextContent(type="text", text="cyclops blocked this call: toxic flow untrusted -> sensitive -> egress")]

@contextlib.asynccontextmanager
async def connected(mode: Mode) -> AsyncIterator[tuple[MCPServer, Detector]]:
    detector = Detector(mode)
    sessions: dict[Server, ClientSession] = {}
    owner: dict[str, Server] = {}
    app = MCPServer("cyclops-proxy")

    @app.list_tools()
    async def list_tools() -> list[MCPTool]:
        tools: list[MCPTool] = []
        for session in sessions.values():
            for tool in (await session.list_tools()).tools:
                tools.append(tool.model_copy(update={"outputSchema": None}))
        return tools

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[ContentBlock]:
        server, tool = owner[name], Tool(name)
        if (server, tool) in EGRESS:
            call = detector.feed(server, tool, arguments, "")
            if detector.blocks(call):
                return _blocked()
            return (await sessions[server].call_tool(name, arguments)).content
        result = await sessions[server].call_tool(name, arguments)
        detector.feed(server, tool, arguments, _text(result.content))
        return result.content

    async with AsyncExitStack() as stack:
        for server in Server:
            params = StdioServerParameters(
                command=sys.executable,
                args=["-m", f"cyclops.servers.{server.value}"],
                env=os.environ.copy(),
            )
            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            sessions[server] = session
            for mcp_tool in (await session.list_tools()).tools:
                owner[mcp_tool.name] = server
        yield app, detector

async def serve_stdio(mode: Mode = Mode.DETECT) -> None:
    async with connected(mode) as (app, detector):
        async with stdio_server() as (read, write):
            await app.run(read, write, app.create_initialization_options())
        _dump(detector)

def serve_http(mode: Mode, host: str, port: int) -> None:
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Mount
    state: dict[str, Any] = {}

    @contextlib.asynccontextmanager
    async def lifespan(_app: Any) -> AsyncIterator[None]:
        async with connected(mode) as (app, _detector):
            manager = StreamableHTTPSessionManager(app=app, json_response=True, stateless=True)
            async with manager.run():
                state["manager"] = manager
                yield

    async def handle(scope: Any, receive: Any, send: Any) -> None:
        await state["manager"].handle_request(scope, receive, send)

    star = Starlette(routes=[Mount("/mcp", app=handle)], lifespan=lifespan)
    uvicorn.run(star, host=host, port=port, log_level="warning")

def _dump(detector: Detector) -> None:
    path = detector.toxic_path()
    _SESSION.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "toxic": bool(path),
        "chain": [{"server": c.server, "tool": c.tool, "taint": c.taint} for c in (path or [])],
        "leaked_bytes": detector.leak_bytes(),
        "metrics": detector.metrics.summary(),
    }
    _SESSION.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def main() -> None:
    mode = Mode(os.environ.get("CYCLOPS_MODE", Mode.DETECT))
    if "--http" in sys.argv:
        serve_http(mode, "127.0.0.1", int(os.environ.get("CYCLOPS_PORT", "8000")))
    else:
        asyncio.run(serve_stdio(mode))

if __name__ == "__main__":
    main()
