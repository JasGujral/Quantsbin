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
Modern tooling (uv, ruff, pyright, pytest) is being introduced in the upcoming
packaging and CI pull requests; this section will be filled in then.
Until then:

```bash
python -m pip install numpy scipy pandas matplotlib
python -m unittest test
```
