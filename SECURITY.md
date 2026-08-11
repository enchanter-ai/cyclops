# Security Policy

## Reporting a vulnerability

**Do not open a public issue for security reports.** Use GitHub's private vulnerability reporting instead:

- **Primary channel:** [Open a private security advisory](https://github.com/enchanter-ai/cyclops/security/advisories/new) on this repository.
- **Maintainers:** the Enchanter Labs maintainers.

We treat reports confidentially. We will acknowledge receipt within 72 hours and share a remediation timeline within 7 days. Coordinated disclosure is strongly preferred — please do not disclose publicly until a fix has shipped or we have agreed on a disclosure date together.

## What to include

A good report has:

- A clear, reproducible proof-of-concept (ideally a minimal `Detector` tool-call sequence, as in `tests/`, or a captured MCP trace).
- The exact module, transport (stdio / Streamable HTTP), and mode (`detect` / `prevent`) involved.
- The version you observed the issue in (`pip show cyclops`).
- Impact assessment: what can an attacker do, and under what preconditions.
- Suggested remediation, if you have one.

Minimal reports ("there's a bug") get triaged last. Be specific.

## Supported versions

The security fix window tracks the latest minor release. Older minors receive fixes for critical issues only, at maintainer discretion.

| Version | Supported |
|---------|-----------|
| latest minor | ✅ full support |
| older | ❌ not supported |

## Scope

Cyclops is itself a security tool, so its threat model is central. In scope:

- **Detection bypass** — a toxic flow (untrusted → sensitive → egress) that reaches the sink without being flagged in `detect` mode or denied in `prevent` mode.
- **Encoding evasion** — a secret exfiltrated through an encoding the unmask layer fails to decode.
- **Provenance evasion** — moving secret bytes to a sink in a way the argument-level provenance graph does not link.
- **Injectability of the detector itself** — any path where untrusted content influences the detector's own decision (the detector must stay deterministic and model-free by construction).
- **Credential or secret exposure** in `out/session.json`, logs, or metrics output.

Out of scope:

- Vulnerabilities in the Model Context Protocol SDK or `networkx` — report to those projects.
- Vulnerabilities in Claude Code or the Claude Agent SDK — report at [anthropics/claude-code](https://github.com/anthropics/claude-code/issues).
- The bundled fixtures are benign by construction: a sandboxed fake home with a **dummy** key and a localhost-only egress sink. Reports that rely on the dummy key being "leaked" to localhost are not vulnerabilities.

## Safe harbor

Good-faith security research that adheres to this policy is welcomed. We will not pursue legal action against researchers who make a reasonable effort to avoid privacy violations, data destruction, or service degradation; report through the private channel above; and give us a reasonable window to remediate before public disclosure.

## Related documents

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — community behavior
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution workflow
- [SUPPORT.md](SUPPORT.md) — where to ask non-security questions
