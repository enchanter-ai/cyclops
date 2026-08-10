from .detector import Detector

def render(detector: Detector) -> str:
    path = detector.toxic_path()
    lines = []
    if path:
        verb = "BLOCKED" if detector.metrics.blocked else "FLAGGED"
        lines.append(f"[RED] TOXIC FLOW {verb}")
        lines.append("  " + " -> ".join(f"{c.server}:{c.tool} ({c.taint})" for c in path))
        lines.append(f"  leaked: ~{detector.leak_bytes()} bytes of distinctive secret tokens reached egress")
        lines.append(f"  choke point: remove {path[-1].server}:{path[-1].tool} to break this flow")
    else:
        lines.append("[GREEN] no toxic flow")
    lines.append(f"  metrics: {detector.metrics.summary()}")
    lines.append("")
    lines.append(mermaid(detector))
    return "\n".join(lines)

def mermaid(detector: Detector) -> str:
    toxic = {c.id for c in (detector.toxic_path() or [])}
    out = ["flowchart LR"]
    for call in detector.graph.calls:
        suffix = ":::toxic" if call.id in toxic else ""
        out.append(f'  {call.id}["{call.server}:{call.tool}<br/>{call.taint}"]{suffix}')
    for src, dst in detector.graph.edges():
        out.append(f"  {src} --> {dst}")
    out.append("  classDef toxic fill:#c0392b,color:#fff;")
    return "\n".join(out)
