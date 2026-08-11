from .config import OWASP
from .detector import Detector
from .enums import FlowClass

def render(detector: Detector) -> str:
    flows = detector.flows()
    lines = []
    if flows:
        verb = "BLOCKED" if detector.metrics.blocked else "FLAGGED"
        for flow in flows:
            lines.append(f"[RED] {flow.cls.name} {verb} (OWASP {OWASP[flow.cls]})")
            lines.append("  " + " -> ".join(f"{c.server}:{c.tool} ({c.taint})" for c in flow.chain))
            if flow.cls is FlowClass.EXFILTRATION:
                lines.append(f"  leaked: ~{detector.leak_bytes()} bytes of distinctive secret tokens reached egress")
            lines.append(f"  choke point: remove {flow.sink.server}:{flow.sink.tool} to break this flow")
    else:
        lines.append("[GREEN] no toxic flow")
    lines.append(f"  metrics: {detector.metrics.summary()}")
    lines.append("")
    lines.append(mermaid(detector))
    return "\n".join(lines)

def mermaid(detector: Detector) -> str:
    toxic = {c.id for flow in detector.flows() for c in flow.chain}
    out = ["flowchart LR"]
    for call in detector.graph.calls:
        suffix = ":::toxic" if call.id in toxic else ""
        out.append(f'  {call.id}["{call.server}:{call.tool}<br/>{call.taint}"]{suffix}')
    for src, dst in detector.graph.edges():
        out.append(f"  {src} --> {dst}")
    out.append("  classDef toxic fill:#c0392b,color:#fff;")
    return "\n".join(out)
