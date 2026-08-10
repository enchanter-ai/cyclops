from typing import Any

from .classify import classify
from .enums import Mode, Server, Tool
from .graph import ProvenanceGraph
from .records import Metrics, ToolCall
from .severity import leaked_bytes

class Detector:
    def __init__(self, mode: Mode = Mode.DETECT) -> None:
        self.mode = mode
        self.graph = ProvenanceGraph()
        self.metrics = Metrics()
        self._seq = 0

    def feed(self, server: Server, tool: Tool, args: dict[str, Any], result: str) -> ToolCall:
        self._seq += 1
        call = ToolCall(f"c{self._seq}", server, tool, args, result, classify(server, tool, args, result))
        self.graph.add_call(call)
        self.metrics.observe(call.taint)
        if call.is_egress and self.graph.find_toxic_path(call):
            self.metrics.flag()
        return call

    def toxic_path(self) -> list[ToolCall] | None:
        return self.graph.find_toxic_path()

    def leak_bytes(self) -> int:
        path = self.graph.find_toxic_path()
        if not path:
            return 0
        sink = path[-1]
        return sum(leaked_bytes(s.result, sink.args) for s in self.graph.sensitive_sources(sink))

    def blocks(self, call: ToolCall) -> bool:
        if self.mode is Mode.PREVENT and call.is_egress and self.graph.find_toxic_path(call):
            self.metrics.block()
            return True
        return False
