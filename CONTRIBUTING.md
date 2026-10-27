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
uv sync                          # .venv with locked runtime + dev dependencies
uv run pre-commit install        # ruff lint/format on every commit
uv run pytest --cov              # tests with coverage
uv run ruff check . && uv run ruff format --check .
uv run pyright                   # type check (advisory until the typing clean-up lands)
uv build                         # sdist + wheel into dist/
```

CI runs the same checks on Linux, macOS and Windows for Python 3.12, 3.13 and 3.14.

To skip the bulk reformat commit in `git blame`:

```bash
git config blame.ignoreRevsFile .git-blame-ignore-revs
```
