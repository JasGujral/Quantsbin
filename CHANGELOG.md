# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- **American Monte Carlo (Longstaff-Schwartz)** no longer returns 0 when no simulated path is in the money at early exercise dates. The backward induction now carries every path's cashflow back at each step; the regression runs only when there are enough in-the-money paths. Example: American put S=55, K=40, vol 20%, r 6%, 1y, 50 steps: 0.0000 -> 0.1057 (European 0.1023). Prices that were already correct are unchanged.
- **Missing market inputs are no longer silently replaced** (BSM, Black-76, GK, Binomial, Monte Carlo):
  - a missing or non-positive `spot0` / `fwd0` now raises `ValueError` (1.0.3 priced with a spot of 0.00001);
  - a missing `pricing_date` now raises `ValueError` with the expected format (1.0.3 raised an unclear `TypeError`);
  - a missing (or zero) `volatility` still defaults to 10% but now emits a `FutureWarning` pointing at the calling line; this becomes an error in 2.0.
- **Analytic delta** for BSM, Black-76 and Garman-Kohlhagen now includes the carry discount `exp(-(q - c) T)`, and put delta has the correct (negative) sign. In 1.0.3 put delta was returned as `+N(-d1)`. Equity call example (S=110, K=100, q=1%, 30d): 0.92095 -> 0.92020; put: +0.07905 -> -0.07898. Matches QuantLib.
- **Phi** (dividend / carry-yield sensitivity) now includes the same `exp(-(q - c) T)` factor: -8.32641 -> -8.31957 in the same example. Matches QuantLib.

### Added
- GitHub Actions CI: ruff, pyright (advisory) and pytest with coverage on Linux, macOS and Windows for Python 3.12-3.14; wheel build check.
- pre-commit hooks (ruff lint and format), Dependabot for Actions and uv dependencies.

### Changed
- Tests moved from `test.py` (unittest) to `tests/` (pytest).
- Code base formatted with ruff; wildcard import in `pricingmodels` replaced with explicit imports.
- Packaging moved to `pyproject.toml` (hatchling) with a `uv.lock`; requires Python 3.12+.
- Dependencies now use minimum versions (numpy >= 1.26, scipy >= 1.11.2, pandas >= 2.1.1, matplotlib >= 3.8) instead of 2021 pins; this clears the Dependabot alerts on the old pins.
- Version is defined once, in `quantsbin.__version__`.
- Repository moved to https://github.com/JasGujral/Quantsbin.
- README badges and links fixed; dead quantsbin.com documentation links removed.
- `development_testing.py` moved to `examples/quickstart.py`; fixed its `StdStrategies` call (`spread` -> `strike_spread`).
- Removed the dead Twitter badge.

### Removed
- `setup.py` (distutils, removed `pypandoc.convert`) and `REQUIREMENTS.txt`.
- Committed IDE settings (`.idea/`) and the distutils-generated `MANIFEST`.

## [1.0.3] - 2021-05-15
- Use `interp1d` instead of the deprecated spline in `line_plot`.
- Fixed unit tests and updated README.

## [1.0.2] - 2018-07-08
- First stable release on PyPI.
