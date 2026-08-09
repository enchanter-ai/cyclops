# Changelog

All notable changes to `cyclops` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Tier-1 governance docs: `LICENSE`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `CITATION.cff`, `CLAUDE.md`.
- `.github/` scaffold: CI workflow (ruff + mypy + pytest on 3.11/3.12), issue templates, PR template, `CODEOWNERS`, dependabot config.
- Package metadata in `pyproject.toml`: license, authors, keywords, classifiers, project URLs.

## [0.1.0] — deterministic, model-free toxic-flow detection

The initial release. See [README.md](README.md) for the complete surface.

### Highlights
- External MCP proxy (stdio + Streamable HTTP) that watches every tool call and flags — or blocks — the toxic flow `untrusted-web → sensitive-read → external-egress`.
- **Argument-level provenance** — proves the actual secret bytes travelled into the egress argument, not just that a sensitive tool fired.
- **Encoding-unmask** — decodes base64/hex before matching, catching `base64(key)` exfiltration.
- **Leak-volume severity** — reports how many bytes of sensitive data reached the sink.
- **Choke-point** — names the single tool to remove to break the flow.
- **Deterministic & model-free** — no LLM in the decision path; not itself prompt-injectable, runs offline, fully replayable.
- **Detect or prevent** modes; per-session metrics.
- Offline `cyclops demo` (recorded-trace replay) and `cyclops attack` (malicious-client self-test).
- 22 tests green, including a style guard (no comments, no double blank lines).

[Unreleased]: https://github.com/enchanter-ai/cyclops/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/enchanter-ai/cyclops/releases/tag/v0.1.0
