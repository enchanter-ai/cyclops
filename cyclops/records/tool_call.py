from dataclasses import dataclass
from typing import Any

from ..config import EGRESS
from ..enums import Server, Taint, Tool

@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    server: Server
    tool: Tool
    args: dict[str, Any]
    result: str
    taint: Taint

    @property
    def is_egress(self) -> bool:
        return (self.server, self.tool) in EGRESS
