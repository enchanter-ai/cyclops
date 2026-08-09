<div align="center">
  <img src="docs/assets/social-preview.png" alt="Cyclops mascot" width="1280">
</div>

# cyclops

<p>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-3fb950?style=for-the-badge"></a>
  <a href="../../actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/enchanter-ai/cyclops/ci.yml?branch=main&style=for-the-badge"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-58a6ff?style=for-the-badge">
  <img alt="22 tests" src="https://img.shields.io/badge/Tests-22-bc8cff?style=for-the-badge">
  <img alt="Model-free detection" src="https://img.shields.io/badge/Detection-model--free-d29922?style=for-the-badge">
  <a href="https://www.repostatus.org/#active"><img alt="Project Status: Active" src="https://www.repostatus.org/badges/latest/active.svg"></a>
</p>

> **An @enchanter-ai product — deterministic, model-free, endpoint-resident.**

**Detect and prevent toxic agent flows from a rogue MCP agent on an endpoint.**

`cyclops` is a deterministic, model-free observer that sits between an autonomous
MCP agent and its tools, watches every tool call, and flags — or blocks — the
moment the agent turns untrusted content into a data exfiltration: a *toxic flow*.
It never modifies or trusts the agent; it watches from outside, the way an
endpoint-security product must. Built as an engineering artifact — a working slice
of graph-based contextual assessment for AI agents.

## The threat

A compromised or over-privileged MCP agent does harm through *sanctioned* tools,
so classic EDR / DLP / CASB miss it — nothing malicious is installed and every
egress uses an approved channel. The tell is not any single call but the *chain*:

```
untrusted source  →  sensitive read  →  external egress
 (a fetched page     (a key / creds       (a POST that carries
  with an injection)   via a real tool)     the secret out)
```

## What it does differently

The toxic-flow *concept* is not ours — Invariant Labs coined "toxic agent flows"
and the "lethal trifecta" framing is Simon Willison's (both credited in
[docs/differentiation.md](docs/differentiation.md)). cyclops's contribution is a
combination that maps directly onto Bloom Security's founders' lineage (Dig DSPM +
XM Cyber attack-graphs):

- **Argument-level provenance** — proves the *actual secret bytes* travelled from
  the sensitive read into the egress argument, not just that a "sensitive tool"
  fired. Data-value, not tool-type.
- **Encoding-unmask** — decodes base64/hex before matching, so a secret smuggled
  out as `base64(key)` is still caught. Kills the standard DLP/substring evasion.
- **Leak-volume severity** — reports *how many bytes* of sensitive data reached the
  sink, turning a boolean alert into a triage number (Dig's "how much data").
- **Choke-point** — names the single tool to remove to break the flow (XM Cyber's
  choke-point idea, ported to the tool graph).
- **Deterministic & model-free** — no LLM in the decision path, so the detector is
  not itself prompt-injectable, runs offline, and is fully replayable.
- **Detect or prevent** — in `prevent` mode the proxy denies the egress call
  *before* it leaves the machine.

## Architecture

```
attack fixture (injected web page)
        │  agent fetches it
   ┌────▼─────┐        ┌───────────────┐        ┌──────────────────┐
   │  MCP     │──MCP──▶│   MCP PROXY   │──MCP──▶│  tool servers     │
   │  agent   │◀──────│  (the detector)│◀──────│  filesystem / web │
   └──────────┘        │ taint + graph │        │  / notify (egress)│
                       │ + severity    │        └──────────────────┘
                       └───────┬───────┘
             untrusted → sensitive → egress  ⇒  FLAG (detect) / DENY (prevent)
```

## Install & run

```sh
pip install -e .
cyclops demo --scenario poisoned
cyclops demo --scenario poisoned-encoded          # base64 exfil, still caught
cyclops demo --scenario poisoned --mode prevent    # egress denied
cyclops demo --scenario benign                     # stays silent
```

The `demo` command replays a recorded trace through the detector — fully offline,
deterministic, no network, no live model. Run it from the repo root.

## Testing locally vs. deploying

- **Test it on your workstation** → use the **CLI** (`cyclops demo`, `cyclops attack`).
  This exercises the detector offline or drives the local gateway with no agent
  wiring — the dev / debug path. The CLI is not part of the MCP interface.
- **Deploy it** → wire the **MCP server** (`cyclops.proxy`) into an agent host:
  over **stdio** (Claude Desktop / Cursor launch it as a child process) or over
  **Streamable HTTP** (`python -m cyclops.proxy --http`, network-reachable). That
  is the product.

## Live run (real Claude agent)

The offline demo is the deterministic path. To capture a *real* run, install the
live extra and log in to the `claude` CLI, then let a real Claude agent fall for
the injection through the proxy:

```sh
pip install -e ".[live]"
CYCLOPS_SCENARIO=poisoned python -m cyclops.agent
```

The proxy writes `out/session.json` (verdict + leaked bytes + metrics). This path
depends on the `mcp` SDK's low-level `Server` API and the Claude Agent SDK; verify
against the installed versions on first run.

## Safety

Fully self-contained and benign by construction: a sandboxed fake home with a
**dummy** key, and an egress sink on localhost. No real credentials, no real
exfiltration, no third-party network calls.

## Layout

```
cyclops/
  enums/      Server, Tool, Taint, Mode
  records/    ToolCall, Metrics (dataclasses)
  patterns.toml   detection data (no patterns hardcoded in code)
  config.py   loads patterns.toml into typed constants
  classify.py taint classification
  overlap.py  encoding-unmask + token matching
  graph.py    provenance graph + toxic-path search
  severity.py leak-volume in bytes
  detector.py detect / prevent orchestration + metrics
  report.py   CLI verdict + Mermaid graph
  cli.py      `cyclops demo`
  proxy.py    external MCP proxy (live path)
  agent.py    Claude Agent SDK runner (live path)
  servers/    filesystem / web / notify mock MCP servers
```
