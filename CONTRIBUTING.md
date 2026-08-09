# Contributing to Cyclops

## Stack

Python ≥ 3.11. Runtime dependencies are exactly two: `mcp` and `networkx`. The live path adds `claude-agent-sdk` + `anyio` (optional extra). No other runtime deps — keep it that way.

## House style — enforced by tests

`tests/test_style.py` is not decoration. It fails the build on:

1. **No comments in any source file.** Not one. The code is written to read without them.
2. **No double blank lines.** `\n\n\n` anywhere under `cyclops/` fails.

Beyond what the test enforces, the project holds these rules:

3. **Nothing hardcoded.** Every server / tool / taint / mode name is an enum (`cyclops/enums/`). No string literal `"filesystem"`, `"web"`, `"post"` in logic — wire it to the enum.
4. **All detection data lives in `patterns.toml`.** Untrusted/sensitive server lists, secret markers, sensitive paths, egress pairs, token regex — data, not code. `config.py` loads it into typed constants. Adding a pattern means editing `patterns.toml`, never a `.py`.
5. **Dataclasses live in `cyclops/records/`.** Not "models" (this project has no ORM and no LLM), not "entities" (no database).
6. **The detector is deterministic and model-free.** No LLM, no network, no randomness in the decision path. This is a hard invariant — a change that makes detection depend on a model is rejected on sight.

## Code quality gates

```sh
pip install -e ".[dev]"
ruff check cyclops tests
mypy cyclops
pytest
```

All four must pass. `mypy` runs in `strict` mode.

## Adding a detection pattern

1. Edit `cyclops/patterns.toml` — add to the relevant list (`untrusted_servers`, `sensitive_servers`, `sensitive_paths`, `secret_markers`, `egress`, `token_regex`).
2. If the pattern references a new server or tool, add it to the matching enum in `cyclops/enums/` first, then reference the enum value from `patterns.toml`.
3. Add a test that exercises the new pattern through the detector, plus a benign negative case that must stay silent.

## Adding a differentiator

Detection logic changes go through `classify.py`, `overlap.py`, `graph.py`, `severity.py`, or `detector.py`. Keep each file single-purpose. If the change adds a claim to the README's "What it does differently" list, it must also be credited honestly in `docs/differentiation.md` — the toxic-flow concept is Invariant Labs' and the lethal-trifecta framing is Simon Willison's; do not present borrowed ideas as novel.

## Submitting

Before opening a PR, verify:

1. `ruff check` clean, `mypy` clean, `pytest` green.
2. No comments and no double blank lines in any changed source file (`test_style.py` proves it).
3. Every new name is an enum; no hardcoded strings in logic.
4. New detection data is in `patterns.toml`, not in code.
5. The detector still makes zero model / network calls in the decision path.
6. Any new README claim is credited in `docs/differentiation.md`.
