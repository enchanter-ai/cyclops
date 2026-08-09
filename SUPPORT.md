# Support

Short version: **pick the right channel, and you'll get an answer faster.**

## Where to go

| You have a… | Go to |
|-------------|-------|
| Security vulnerability | [Private security advisory](https://github.com/enchanter-ai/cyclops/security/advisories/new) — **never** a public issue. See [SECURITY.md](SECURITY.md). |
| Reproducible bug | [Bug report issue](https://github.com/enchanter-ai/cyclops/issues/new?template=bug_report.md). Include repro steps, transport, mode, and exact output. |
| Concrete feature proposal | [Feature request issue](https://github.com/enchanter-ai/cyclops/issues/new?template=feature_request.md). |
| Usage question | [Discussions → Q&A](https://github.com/enchanter-ai/cyclops/discussions) |

## Before filing

1. **Search first.** Existing issues and Discussions. Duplicates get closed without comment.
2. **Read the docs.** Most questions are answered in one of these:
   - [README.md](README.md) — overview, install, what cyclops does, testing vs. deploying
   - [docs/architecture.md](docs/architecture.md) — dependency graph, file-by-file, runtime flows
   - [docs/differentiation.md](docs/differentiation.md) — what cyclops does differently, and honest credit
3. **Reproduce it offline.** The `cyclops demo` command replays recorded traces deterministically with no network — the fastest way to isolate a detection issue.
4. **Narrow the case.** "It sometimes misses" is not reproducible. Minimize the failing trace.

## Response expectations

This is a community-maintained project. We answer when we can, usually within a few days.

- **Security reports**: acknowledged within 72 hours (see [SECURITY.md](SECURITY.md)).
- **Bug reports**: triaged roughly weekly. High-signal reports (clear repro, exact versions) move fastest.
- **Feature requests**: considered at roadmap review time, not on demand.

## What we can't help with

- Questions about the Model Context Protocol itself → the [MCP project](https://modelcontextprotocol.io).
- Questions about Claude Code or the Claude Agent SDK → [anthropics/claude-code](https://github.com/anthropics/claude-code).

Thanks for using an @enchanter-ai product.
