from dataclasses import dataclass
from typing import Any

from ..config import EGRESS, PRIVILEGED
from ..enums import Server, Taint

@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    server: Server
    tool: str
    args: dict[str, Any]
    result: str
    taint: Taint

    @property
    def is_egress(self) -> bool:
        return (self.server, self.tool) in EGRESS

    @property
    def is_privileged(self) -> bool:
        return (self.server, self.tool) in PRIVILEGED
