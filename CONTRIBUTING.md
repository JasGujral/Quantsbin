# Contributing to Quantsbin

Thanks for helping revive Quantsbin.

## Workflow
1. Open an issue describing the bug or feature before large changes.
2. Branch from `main` (`fix/...`, `feat/...`, `chore/...`).
3. Keep pull requests focused; one topic per PR.
4. Add or update tests for every behaviour change. A bug fix starts with a test that fails on the current code.
5. Add an entry under **Unreleased** in `CHANGELOG.md`.

## Standards for numerical code
- Every new model or method cites its source (paper, book or QuantLib routine) in the docstring.
- New pricers must be checked against a published reference value or an independent implementation.
- Never use global random state; pass seeds or generators explicitly.

## Development setup
Quantsbin uses [uv](https://docs.astral.sh/uv/) and supports Python 3.12+.

```bash
git clone https://github.com/JasGujral/Quantsbin.git
cd Quantsbin
uv sync                      # creates .venv with locked dependencies
uv run python -m unittest test
uv build                     # builds sdist and wheel into dist/
```

Linting, type checking and pytest arrive in the next tooling PR.
