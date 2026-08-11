# Cyclops — Agent Contract

Audience: Claude. Cyclops is a deterministic, model-free MCP proxy that detects and prevents typed toxic flows over a provenance graph — `EXFILTRATION` (`untrusted-web → sensitive-read → external-egress`) and `EXCESSIVE_AGENCY` (`untrusted → privileged action`, args derived from untrusted content, no sensitive read). Each class carries its OWASP LLM Top 10 (2025) code. It watches an autonomous MCP agent's tool calls from the outside and never trusts or modifies the agent.

## Hard invariants

1. **Model-free decision path.** No LLM, no network, no randomness decides a verdict. The detector is the thing watching an injectable agent — if it could be influenced by untrusted content, it would be the vulnerability. Never introduce a model call into `classify.py`, `overlap.py`, `graph.py`, `severity.py`, or `detector.py`.
2. **Nothing hardcoded.** Every server / tool / taint / mode name is an enum in `cyclops/enums/`. No string literal `"filesystem"`, `"web"`, `"post"` in logic.
3. **Detection data is data.** All patterns live in `cyclops/patterns.toml`, loaded by `config.py` into typed constants. Adding a pattern edits the TOML, never a `.py`.
4. **House style.** No comments in any source file. No double blank lines. Both are enforced by `tests/test_style.py`.
5. **Honest credit.** The toxic-flow concept is Invariant Labs'; the lethal-trifecta framing is Simon Willison's. The contribution is the *combination* (byte-provenance + encoding-unmask + leak-volume + choke-point + deterministic + endpoint-resident). Never present the concept as novel — see `docs/differentiation.md`.

## Layout

This is the production core — only the MCP proxy and the model-free enforcement engine. No demo CLI, harness, or mock servers ship.

```
cyclops/
  enums/      Server, Tool, Taint, Mode, FlowClass, Transport
  records/    ToolCall, Metrics, Flow (dataclasses)
  patterns.toml   detection data (untrusted / sensitive / egress / privileged / owasp)
  config.py   loads patterns.toml into typed constants
  classify.py taint classification
  overlap.py  encoding-unmask + token matching
  graph.py    provenance graph + typed find_toxic_flows (exfil + excessive-agency)
  severity.py leak-volume in bytes
  detector.py detect / prevent orchestration + per-class metrics
  downstream.py   typed loader for the downstream-server map (stdio / Streamable HTTP)
  proxy.py    external MCP proxy (stdio + Streamable HTTP) + session.json verdict
downstream.example.toml   operator template binding real MCP servers to logical roles
```

## Downstream servers

The proxy is config-driven. `downstream.toml` (path via `CYCLOPS_DOWNSTREAM`, default `downstream.toml`) declares the real MCP servers the proxy fronts. Each `[[server]]` binds one logical `Server` role (`web` / `filesystem` / `notify` / `admin`) to a `stdio` command or a Streamable-`http` URL. The role — not the endpoint — drives detection: `patterns.toml` classifies by role. No production endpoint is ever hard-coded in Python. Ship template: `downstream.example.toml`.

## Ship bar

`ruff check` clean, `mypy --strict` clean, `pytest` green. Detection behavior for both flow classes is proven by the Detector-level tests (`tests/test_detector.py`, `tests/test_flow_engine.py`). A change that breaks any of these does not ship.

## Production output

Each proxied session writes `out/session.json` (path via `CYCLOPS_SESSION`): the structured verdict — `toxic`, per-class `flows` (class + OWASP tag + chain + choke-point), `leaked_bytes`, and `metrics`. That is the product's machine-readable output; wire it to a store / SIEM.
