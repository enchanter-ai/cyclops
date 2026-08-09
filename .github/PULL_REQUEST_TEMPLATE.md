## What

<!-- One sentence: what this PR changes. -->

## Why

<!-- The motivation. Link the issue if there is one. -->

## Checklist

- [ ] `ruff check cyclops tests` clean
- [ ] `mypy cyclops` clean
- [ ] `pytest` green
- [ ] No comments and no double blank lines in changed source (`test_style.py` proves it)
- [ ] Every new name is an enum; no hardcoded strings in logic
- [ ] New detection data is in `patterns.toml`, not in code
- [ ] The detector still makes zero model / network calls in the decision path
- [ ] Any new README claim is credited in `docs/differentiation.md`
