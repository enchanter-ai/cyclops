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
from mcp.client.streamable_http import streamable_http_client
from mcp.server.lowlevel import Server as MCPServer
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import ContentBlock, TextContent
from mcp.types import Tool as MCPTool

from .config import EGRESS, OWASP, PRIVILEGED, assert_closure
from .detector import Detector
from .downstream import Downstream, load
from .enums import Mode, Transport

_SESSION = Path(os.environ.get("CYCLOPS_SESSION", "out/session.json"))

def _text(content: list[ContentBlock]) -> str:
    return "".join(c.text for c in content if isinstance(c, TextContent))

def _blocked() -> list[ContentBlock]:
    return [TextContent(type="text", text="cyclops blocked this call: toxic flow detected before the sink")]

def _claim(owner: dict[str, str], names: list[str], server: str) -> None:
    for name in names:
        if name in owner:
            raise ValueError(f"duplicate tool name across downstream servers: {name}")
        owner[name] = server

def _verify_sinks(advertised: set[tuple[str, str]]) -> None:
    missing = (EGRESS | PRIVILEGED) - advertised
    if missing:
        raise ValueError(f"declared egress/privileged sinks not advertised by any downstream server: {sorted(missing)}")

async def _open(stack: AsyncExitStack, spec: Downstream) -> tuple[Any, Any]:
    if spec.transport is Transport.STDIO:
        assert spec.command is not None
        params = StdioServerParameters(command=spec.command, args=list(spec.args), env=os.environ.copy())
        read, write = await stack.enter_async_context(stdio_client(params))
        return read, write
    assert spec.url is not None
    read, write, _ = await stack.enter_async_context(streamable_http_client(spec.url))
    return read, write

@contextlib.asynccontextmanager
async def connected(mode: Mode) -> AsyncIterator[tuple[MCPServer, Detector]]:
    detector = Detector(mode)
    sessions: dict[str, ClientSession] = {}
    owner: dict[str, str] = {}
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
        if name not in owner:
            return [TextContent(type="text", text=f"cyclops: unknown tool {name}")]
        server, tool = owner[name], name
        if (server, tool) in EGRESS or (server, tool) in PRIVILEGED:
            call = detector.feed(server, tool, arguments, "")
            if detector.blocks(call):
                return _blocked()
            return (await sessions[server].call_tool(name, arguments)).content
        result = await sessions[server].call_tool(name, arguments)
        detector.feed(server, tool, arguments, _text(result.content))
        return result.content

    async with AsyncExitStack() as stack:
        specs = load()
        assert_closure({spec.server for spec in specs})
        advertised: set[tuple[str, str]] = set()
        for spec in specs:
            read, write = await _open(stack, spec)
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            sessions[spec.server] = session
            names = [t.name for t in (await session.list_tools()).tools]
            _claim(owner, names, spec.server)
            advertised |= {(spec.server, n) for n in names}
        _verify_sinks(advertised)
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
        async with connected(mode) as (app, detector):
            manager = StreamableHTTPSessionManager(app=app, json_response=True, stateless=True)
            async with manager.run():
                state["manager"] = manager
                yield
            _dump(detector)

    async def handle(scope: Any, receive: Any, send: Any) -> None:
        await state["manager"].handle_request(scope, receive, send)

    star = Starlette(routes=[Mount("/mcp", app=handle)], lifespan=lifespan)
    uvicorn.run(star, host=host, port=port, log_level="warning")

def _dump(detector: Detector) -> None:
    flows = detector.flows()
    _SESSION.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "toxic": bool(flows),
        "flows": [
            {
                "class": flow.cls.value,
                "owasp": OWASP[flow.cls],
                "chain": [{"server": c.server, "tool": c.tool, "taint": c.taint} for c in flow.chain],
                "choke_point": {"server": flow.sink.server, "tool": flow.sink.tool},
            }
            for flow in flows
        ],
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
