from typing import Any

import networkx as nx

from .enums import Taint
from .overlap import shares, tokens
from .records import ToolCall

class ProvenanceGraph:
    def __init__(self) -> None:
        self._g = nx.DiGraph()
        self._calls: list[ToolCall] = []

    def add_call(self, call: ToolCall) -> None:
        self._g.add_node(call.id, call=call)
        for prior in self._calls:
            if _derives_from(call.args, prior.result):
                self._g.add_edge(prior.id, call.id)
        self._calls.append(call)

    @property
    def calls(self) -> list[ToolCall]:
        return list(self._calls)

    def edges(self) -> list[tuple[str, str]]:
        return list(self._g.edges)

    def find_toxic_path(self, sink: ToolCall | None = None) -> list[ToolCall] | None:
        by_id = {c.id: c for c in self._calls}
        untrusted = [c for c in self._calls if c.taint is Taint.UNTRUSTED]
        sensitive = [c for c in self._calls if c.taint is Taint.SENSITIVE]
        egress = [sink] if sink is not None else [c for c in self._calls if c.is_egress]
        for u, s, e in ((u, s, e) for u in untrusted for s in sensitive for e in egress):
            if nx.has_path(self._g, u.id, s.id) and nx.has_path(self._g, s.id, e.id):
                chain = nx.shortest_path(self._g, u.id, s.id) + nx.shortest_path(self._g, s.id, e.id)[1:]
                return [by_id[n] for n in chain]
        return None

    def sensitive_sources(self, sink: ToolCall) -> list[ToolCall]:
        untrusted = [c.id for c in self._calls if c.taint is Taint.UNTRUSTED]
        found = []
        for s in self._calls:
            if s.taint is Taint.SENSITIVE and nx.has_path(self._g, s.id, sink.id) and any(nx.has_path(self._g, u, s.id) for u in untrusted):
                found.append(s)
        return found

def _derives_from(args: dict[str, Any], result: str) -> bool:
    produced = tokens(result)
    if not produced:
        return False
    return shares(" ".join(str(v) for v in args.values()), produced)
