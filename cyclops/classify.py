from typing import Any

from .config import SECRET_MARKERS, SENSITIVE_PATHS, SENSITIVE_SERVERS, UNTRUSTED_SERVERS
from .enums import Server, Taint, Tool

def classify(server: Server, tool: Tool, args: dict[str, Any], result: str) -> Taint:
    if server in UNTRUSTED_SERVERS:
        return Taint.UNTRUSTED
    if server in SENSITIVE_SERVERS and _is_secret(str(args.get("path", "")), result):
        return Taint.SENSITIVE
    return Taint.NORMAL

def _is_secret(path: str, result: str) -> bool:
    return any(p in path for p in SENSITIVE_PATHS) or any(m in result for m in SECRET_MARKERS)
