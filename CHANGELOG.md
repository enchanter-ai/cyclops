# Changelog

All notable changes to `cyclops` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Tier-1 governance docs: `LICENSE`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `CITATION.cff`, `CLAUDE.md`.
- `.github/` scaffold: CI workflow (ruff + mypy + pytest on 3.11/3.12), issue templates, PR template, `CODEOWNERS`, dependabot config.
- Package metadata in `pyproject.toml`: license, authors, keywords, classifiers, project URLs.

### Fixed
- **Sticky toxic path**: `feed()` / `blocks()` now target the specific egress call that closes a toxic path, so a later unrelated egress is no longer flagged/blocked because an older toxic path exists.
- **Demo `prevent`**: the offline demo now invokes `blocks()` on egress like the live proxy, so `metrics.blocked` is real and the verdict verb reflects an actual block rather than the selected mode.
- **Hex + bounded nested decoding**: `overlap.py` now unmasks hex (as advertised) and normalizes bounded nested encodings (base64/hex, depth-limited, deduplicated).
- **Tool-name collisions**: the proxy fails fast on duplicate downstream tool names instead of silently overwriting the owner mapping.
- **Sandbox containment**: the mock filesystem server uses `Path.is_relative_to` instead of a string-prefix check (rejects sibling paths that share the prefix).
- **HTTP `session.json`**: the Streamable-HTTP path now writes `session.json` at server shutdown.

### Changed
- **Leak-volume** now aggregates distinctive secret-token bytes across every sensitive source with a path to the sink, and is documented as bytes reaching the egress *attempt* (choke point), not confirmed remote delivery.

### Known limitations (roadmap)
- HTTP transport is single-tenant (one detector per process); per-client session isolation is deferred — prefer stdio for multi-tenant isolation.
- Downstream servers are enum-driven; a generic external-server configuration surface is deferred.
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
