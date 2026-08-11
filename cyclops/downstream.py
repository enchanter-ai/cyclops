import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .enums import Server, Transport

_PATH = Path(os.environ.get("CYCLOPS_DOWNSTREAM", "downstream.toml"))

@dataclass(frozen=True, slots=True)
class Downstream:
    server: Server
    transport: Transport
    command: str | None
    args: tuple[str, ...]
    url: str | None

def load(path: str | Path | None = None) -> list[Downstream]:
    source = Path(path) if path is not None else _PATH
    data = tomllib.loads(source.read_text(encoding="utf-8"))
    seen: set[Server] = set()
    out: list[Downstream] = []
    for entry in data.get("server", []):
        server = Server(entry["name"])
        if server in seen:
            raise ValueError(f"duplicate downstream server: {server}")
        seen.add(server)
        out.append(_build(server, Transport(entry["transport"]), entry))
    if not out:
        raise ValueError(f"no downstream servers declared in {source}")
    return out

def _build(server: Server, transport: Transport, entry: dict[str, Any]) -> Downstream:
    if transport is Transport.STDIO:
        command = entry.get("command")
        if not command:
            raise ValueError(f"stdio server {server} requires a command")
        return Downstream(server, transport, str(command), tuple(str(a) for a in entry.get("args", [])), None)
    url = entry.get("url")
    if not url:
        raise ValueError(f"http server {server} requires a url")
    return Downstream(server, transport, None, (), str(url))
