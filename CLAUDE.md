# Cyclops — Agent Contract

Audience: Claude. Cyclops is a deterministic, model-free MCP proxy that detects and prevents the toxic flow `untrusted-web → sensitive-read → external-egress`. It watches an autonomous MCP agent's tool calls from the outside and never trusts or modifies the agent.

## Hard invariants

1. **Model-free decision path.** No LLM, no network, no randomness decides a verdict. The detector is the thing watching an injectable agent — if it could be influenced by untrusted content, it would be the vulnerability. Never introduce a model call into `classify.py`, `overlap.py`, `graph.py`, `severity.py`, or `detector.py`.
2. **Nothing hardcoded.** Every server / tool / taint / mode name is an enum in `cyclops/enums/`. No string literal `"filesystem"`, `"web"`, `"post"` in logic.
3. **Detection data is data.** All patterns live in `cyclops/patterns.toml`, loaded by `config.py` into typed constants. Adding a pattern edits the TOML, never a `.py`.
4. **House style.** No comments in any source file. No double blank lines. Both are enforced by `tests/test_style.py`.
5. **Honest credit.** The toxic-flow concept is Invariant Labs'; the lethal-trifecta framing is Simon Willison's. The contribution is the *combination* (byte-provenance + encoding-unmask + leak-volume + choke-point + deterministic + endpoint-resident). Never present the concept as novel — see `docs/differentiation.md`.

## Layout

```
cyclops/
  enums/      Server, Tool, Taint, Mode
  records/    ToolCall, Metrics (dataclasses)
  patterns.toml   detection data
  config.py   loads patterns.toml into typed constants
  classify.py taint classification
  overlap.py  encoding-unmask + token matching
  graph.py    provenance graph + toxic-path search
  severity.py leak-volume in bytes
  detector.py detect / prevent orchestration + metrics
  report.py   CLI verdict + Mermaid graph
  cli.py      cyclops demo / cyclops attack
  proxy.py    external MCP proxy (stdio + Streamable HTTP)
  agent.py    Claude Agent SDK runner (live path)
  redteam.py  malicious MCP client self-test
  servers/    filesystem / web / notify mock MCP servers
```

## Ship bar

`ruff check` clean, `mypy --strict` clean, `pytest` green (22 tests), and the deterministic `cyclops demo` still BLOCKs the exfil in `prevent` mode and stays silent on `benign`. A change that breaks any of these does not ship.

## Testing vs. deploying

- **Test on a workstation** → the CLI (`cyclops demo`, `cyclops attack`) — offline, deterministic, no agent wiring.
- **Deploy** → wire the MCP proxy (`cyclops.proxy`) into an agent host over stdio or Streamable HTTP. That is the product.
