from dataclasses import dataclass

from ..enums import FlowClass
from .tool_call import ToolCall

@dataclass(frozen=True, slots=True)
class Flow:
    cls: FlowClass
    chain: list[ToolCall]

    @property
    def sink(self) -> ToolCall:
        return self.chain[-1]
