from typing import Any

from .classify import classify
from .enums import Mode, Server
from .graph import ProvenanceGraph
from .records import Flow, Metrics, ToolCall
from .severity import leaked_bytes

class Detector:
    def __init__(self, mode: Mode = Mode.DETECT) -> None:
        self.mode = mode
        self.graph = ProvenanceGraph()
        self.metrics = Metrics()
        self._seq = 0

    def feed(self, server: Server, tool: str, args: dict[str, Any], result: str) -> ToolCall:
        self._seq += 1
        call = ToolCall(f"c{self._seq}", server, tool, args, result, classify(server, tool, args, result))
        self.graph.add_call(call)
        self.metrics.observe(call.taint)
        for flow in self.graph.find_toxic_flows(call):
            self.metrics.flag(flow.cls)
        return call

    def flows(self) -> list[Flow]:
        return self.graph.find_toxic_flows()

    def toxic_path(self) -> list[ToolCall] | None:
        return self.graph.find_toxic_path()

    def leak_bytes(self) -> int:
        path = self.graph.find_toxic_path()
        if not path:
            return 0
        sink = path[-1]
        return sum(leaked_bytes(s.result, sink.args) for s in self.graph.sensitive_sources(sink))

    def blocks(self, call: ToolCall) -> bool:
        if self.mode is not Mode.PREVENT:
            return False
        blocked = False
        for flow in self.graph.find_toxic_flows(call):
            self.metrics.block(flow.cls)
            blocked = True
        return blocked
