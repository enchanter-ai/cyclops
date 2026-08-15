# Changelog

All notable changes to `cyclops` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Fully operator-defined roles and sinks (breaking startup behavior).** The `Server` and `Tool` enums are removed; server names and tool names are plain `str` end-to-end (`ToolCall.server`, `Detector.feed`, `classify`, `downstream.py`, `proxy.py`). `patterns.toml` + `downstream.toml` now define *all* roles and every `(server, tool)` egress / privileged sink by the operator's real names — onboarding a real system (e.g. `slack.send`, `iam.attach_policy`) is a two-TOML edit with **zero Python changes**, honouring the "no endpoint hard-coded in Python" contract that the tool-name half started. Removing the enums also lifts the four-role / one-server-per-role cap: any number of untrusted sources or egress channels can be declared. The `StrEnum`-equality sink match (`(server, tool) in EGRESS`) is byte-identical as `(str, str)` membership; detection for both flow classes is unchanged (proven by the Detector-level suite). The remaining enums — `Taint`, `FlowClass`, `Mode`, `Transport` — stay, as genuine closed vocabularies of the engine.
- **Closure validation replaces the enum vocabulary guard (stricter startup).** The old enums only failed fast against four demo names; two real checks now run when the proxy connects: (1) every server referenced in `patterns.toml` must be declared in `downstream.toml` (`config.assert_closure`), and (2) every declared egress / privileged sink must be a tool its bound server actually advertises (`proxy._verify_sinks`). A prevent-mode gate whose sink table matches nothing now **refuses to boot** instead of silently detecting nothing — a config that "worked" by passing everything is now a startup error. `patterns.toml` gains a `CYCLOPS_PATTERNS` env override (packaged file is the default), and the proxy returns a clean MCP error for an unknown tool name instead of a `KeyError`.

### Added
- **Config-driven downstream server map.** The proxy no longer hard-codes downstream servers. `downstream.py` loads a typed `downstream.toml` (path via `CYCLOPS_DOWNSTREAM`) that binds each real MCP server to a logical `Server` role over `stdio` (command + args) or Streamable `http` (url); a new `Transport` enum types the transport. Classification stays role-driven via `patterns.toml` — no production endpoint is hard-coded in Python. Ships `downstream.example.toml` as an operator template.
- **Arbitrary real tool names.** The proxy no longer assumed downstream tools were one of four enum values (`Tool(name)` would have raised on a real server). `ToolCall.tool` / `Detector.feed` / `classify` now carry the raw tool name; the `Tool` enum stays as the declared egress / privileged **sink** vocabulary, matched by name via `StrEnum` equality. Non-sink tools pass through, still tapped for provenance. Detection behavior for both flow classes is unchanged (proven by the existing Detector-level tests, plus two new arbitrary-tool-name regressions).
- **Structured `session.json` verdict** now emits one entry per toxic flow **class** — each with its OWASP tag, ordered chain, and named `choke_point` — plus `leaked_bytes` and per-class `metrics`. This replaces the human-rendered report as the product's machine-readable output.

### Removed
- **Harness, demo, and mock servers.** The production core drops `cli.py` (`cyclops demo` / `cyclops attack`), `report.py`, `agent.py`, `redteam.py`, the `servers/` mock MCP servers, and the `scenarios/` · `recordings/` · `sandbox/` fixtures — along with their harness-only tests. The `cyclops` console script now launches the proxy (`cyclops.proxy:main`); the `live` extra is replaced by an `http` extra (uvicorn + starlette). Detection behavior for both flow classes is unchanged and proven by the Detector-level tests.

### Added (flow engine)
- **Multi-class flow rule engine.** The single hard-coded trifecta is generalized into a typed engine. `FlowClass` enum (`EXFILTRATION`, `EXCESSIVE_AGENCY`); `graph.find_toxic_flows()` returns typed `Flow` records (class + ordered chain) with a targeted per-sink variant; the `session.json` verdict carries the class and its OWASP tag; `Metrics` counts flags per class.
- **`EXCESSIVE_AGENCY` flow class** (`untrusted → privileged action`, no sensitive read) — an untrusted source reaching a privileged `(server, tool)` sink whose arguments derive from the untrusted content. `EXFILTRATION` remains an untouched subset of the same graph. OWASP LLM Top 10 (2025) tags carried as data in `patterns.toml` (`LLM06:2025` / `LLM02:2025`).
- **Privileged action model.** A `privileged` `(server, tool)` table in `patterns.toml` (mirroring `egress`), loaded by `config.py`; an `is_privileged` property on `ToolCall` (mirroring `is_egress`); and Detector-level regression tests (detection, targeted blocking, benign-not-flagged, agency-without-exfil, OWASP tag).
- Tier-1 governance docs: `LICENSE`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `CITATION.cff`, `CLAUDE.md`.
- `.github/` scaffold: CI workflow (ruff + mypy + pytest on 3.11/3.12), issue templates, PR template, `CODEOWNERS`, dependabot config.
- Package metadata in `pyproject.toml`: license, authors, keywords, classifiers, project URLs.

### Fixed
- **Sticky toxic path**: `feed()` / `blocks()` now target the specific egress call that closes a toxic path, so a later unrelated egress is no longer flagged/blocked because an older toxic path exists.
- **Hex + bounded nested decoding**: `overlap.py` now unmasks hex (as advertised) and normalizes bounded nested encodings (base64/hex, depth-limited, deduplicated).
- **Tool-name collisions**: the proxy fails fast on duplicate downstream tool names instead of silently overwriting the owner mapping.
- **HTTP `session.json`**: the Streamable-HTTP path now writes `session.json` at server shutdown.

### Changed
- **Leak-volume** now aggregates distinctive secret-token bytes across every sensitive source with a path to the sink, and is documented as bytes reaching the egress *attempt* (choke point), not confirmed remote delivery.

### Known limitations (roadmap)
- HTTP transport is single-tenant (one detector per process); per-client session isolation is deferred — prefer stdio for multi-tenant isolation.
- Downstream roles are the fixed `Server` enum vocabulary (`web` / `filesystem` / `notify` / `admin`); real servers bind to a role in `downstream.toml`. A dynamic, arbitrary-role vocabulary is deferred.
- Non-text MCP content types are not fed to provenance (documented; the model-free constraint forbids semantic interpretation).
- `find_toxic_path` returns the first toxic path (each segment shortest), not a globally-ranked choke-point.

## [0.1.0] — deterministic, model-free toxic-flow detection

The initial release. See [README.md](README.md) for the complete surface.

### Highlights
- External MCP proxy (stdio + Streamable HTTP) that watches every tool call and flags — or blocks — the toxic flow `untrusted-web → sensitive-read → external-egress`.
- **Argument-level provenance** — proves the actual secret bytes travelled into the egress argument, not just that a sensitive tool fired.
- **Encoding-unmask** — decodes base64/hex before matching, catching `base64(key)` exfiltration.
- **Leak-volume severity** — reports the distinctive secret-token byte count that reached the egress attempt.
- **Choke-point** — names the single tool to remove to break the flow.
- **Deterministic & model-free** — no LLM in the decision path; not itself prompt-injectable, runs offline, fully replayable.
- **Detect or prevent** modes; per-session metrics.
- Offline `cyclops demo` (recorded-trace replay) and `cyclops attack` (malicious-client self-test).
- 22 tests green, including a style guard (no comments, no double blank lines).

[Unreleased]: https://github.com/enchanter-ai/cyclops/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/enchanter-ai/cyclops/releases/tag/v0.1.0
