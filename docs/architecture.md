# Architecture & flow

Derived from the real import graph. Everything funnels up into one hub —
`detector.py`. Enums are the shared leaf, which is why no server/tool name is
hardcoded anywhere.

## Module dependency graph

```mermaid
flowchart TD
  subgraph L0["foundation"]
    enums["enums/ — Server·Tool·Taint·Mode"]
    toml["patterns.toml — detection data"]
  end
  subgraph L1["config"]
    config["config.py"]
  end
  subgraph L2["primitives"]
    overlap["overlap.py — encoding-unmask + tokens"]
    records["records/ — ToolCall · Metrics"]
    classify["classify.py — taint rules"]
  end
  subgraph L3["detection core"]
    severity["severity.py — bytes leaked"]
    graph["graph.py — provenance + toxic path"]
  end
  subgraph L4["hub"]
    detector["detector.py — feed / toxic_path / blocks / metrics"]
  end
  subgraph L5["surfaces"]
    report["report.py"]
    cli["cli.py — cyclops demo"]
    proxy["proxy.py — live MCP tap"]
    agent["agent.py — live Claude runner"]
    servers["servers/ — filesystem·web·notify"]
  end
  config --> enums
  overlap --> config
  records --> config
  records --> enums
  classify --> config
  classify --> enums
  severity --> overlap
  graph --> overlap
  graph --> records
  graph --> enums
  detector --> classify
  detector --> graph
  detector --> severity
  detector --> records
  report --> detector
  cli --> detector
  cli --> report
  proxy --> detector
  proxy --> config
  agent --> enums
  servers --> enums
```

## File by file

| File | Role | Depends on |
|------|------|-----------|
| `enums/` | `Server`, `Tool`, `Taint`, `Mode` — the only place names live | — |
| `patterns.toml` | untrusted/sensitive servers, secret markers, egress pairs, token regex | — |
| `config.py` | loads `patterns.toml` into typed, enum-keyed constants | enums |
| `overlap.py` | tokenizes text and matches across **decoded** forms (base64) — the encoding-unmask | config |
| `records/tool_call.py` | `ToolCall` dataclass (+ `is_egress`) | config, enums |
| `records/metrics.py` | `Metrics` dataclass — calls / flagged / blocked / taint | enums |
| `classify.py` | assigns `Taint` to a call from server + path + content | config, enums |
| `severity.py` | distinctive secret-token bytes reaching the sink (aggregated per sink) | overlap |
| `graph.py` | provenance DiGraph; `find_toxic_path()` = untrusted→sensitive→egress | overlap, records, enums |
| `detector.py` | **hub** — `feed` / `toxic_path` / `leak_bytes` / `blocks`, holds graph + metrics | classify, graph, severity, records |
| `report.py` | renders verdict + leak + choke-point + Mermaid | detector |
| `cli.py` | `cyclops demo` — replays a recording through the detector | detector, report |
| `proxy.py` | external MCP proxy: taps real tool calls, detect or prevent | detector, config |
| `agent.py` | drives a real Claude agent through the proxy (live capture) | claude-agent-sdk |
| `servers/` | 3 mock MCP tool servers | enums |

## Runtime flow — offline demo (`cyclops demo`)

```
cli → reads recordings/<scenario>.jsonl
    → detector.feed(each call)
         → classify()          taint: web=untrusted, key-read=sensitive
         → graph.add_call()    overlap decides "derives-from" edges (base64-aware)
    → detector.toxic_path()    graph search: untrusted → sensitive → egress
    → detector.leak_bytes()    severity
    → report.render()          RED/GREEN + Mermaid
```

## Runtime flow — live (`python -m cyclops.agent`)

```
Claude agent → proxy.py (MCP) → servers/ (real tool calls)
                   │ taps every call → detector (same hub)
                   └ detect: flag   |   prevent: deny the egress before it leaves
              → out/session.json (verdict + leaked bytes + metrics)
```

Same `detector` brain in both paths; only the source of calls differs — a recorded
file vs a live agent through the proxy.

## Detection in four steps

1. **Tag** each tool result: untrusted (web) / sensitive (secret read) / normal.
2. **Link** calls with a provenance edge when a later call's arguments share a
   distinctive token with an earlier result — checked across base64-decoded forms.
3. **Search** for a path untrusted → sensitive → egress.
4. **Score** the bytes of the secret that reached the sink; in prevent mode, deny.
