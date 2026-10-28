# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- **Binomial tree** is now iterative: same CRR tree and escrowed dividends, identical prices (72 reference cases within 1.3e-15), but no recursion limit (1.0.3 failed above about 1,000 steps) and about 100x faster (900 steps: 2.0 s -> 0.02 s).
- **Binomial P&L attribution** returned 0: the bumped and base trees shared one node cache through a shallow copy. Fixed by the iterative tree, which keeps no cache.
- **Implied volatility** uses Brent's method on [0.01%, 500%] to machine precision (1.0.3: bisection on [0.1%, 99.9%] with tolerance 5e-5, so it failed above 99.9% vol and was accurate only to about 2e-5). A premium outside the no-arbitrage bounds now raises a clear `ValueError`. ATM call, vol 25%: 0.249982 -> 0.250000; vol 150%: error -> 1.5.
- **Monte Carlo no longer resets numpy's global random state** (`np.random.seed`). It uses a local `RandomState(seed)`, which produces exactly the same paths, so Monte Carlo prices are unchanged. `seed=0` is now respected (1.0.3 silently replaced it with 100).
- **Garman-Kohlhagen greeks** now include `rho_foreign` (FX options) and `rho_conv_yield` (commodity options). They were never returned because the underlying type was compared with an Enum member instead of its value.
- **P&L attribution for FX options**: `delta_rf_foreign` was passed to the cost-yield slot, so a foreign-rate move produced no P&L. It now moves the foreign rate. `pnl_attribution` also accepts `delta_cost_yield`.
- **Numerical greeks** no longer return NaN when no bump sizes are given. This affected `risk_parameters()` for every Binomial and Monte Carlo engine and `risk_parameters_num()` without arguments. The documented default bumps (2% spot/vol/rate, 1 day) now apply.
- **Numerical rho / vega with a zero base value** (e.g. `rf_rate=0`): a relative bump never moved it, giving NaN; a zero base is now bumped by the absolute amount.
- **Option strategies** no longer start a multiprocessing pool on every call. This crashed scripts without an `if __name__ == "__main__":` guard on macOS and on Python 3.14+, and was about 25x slower on 3.12 (1,000x on 3.14). Values unchanged.
- **American Monte Carlo** now compares against exercising today, so it never prices below intrinsic value. Deep in-the-money put S=20, K=40: 19.9524 -> 20.0000. Other prices unchanged.
- **American Monte Carlo (Longstaff-Schwartz)** no longer returns 0 when no simulated path is in the money at early exercise dates. The backward induction now carries every path's cashflow back at each step; the regression runs only when there are enough in-the-money paths. Example: American put S=55, K=40, vol 20%, r 6%, 1y, 50 steps: 0.0000 -> 0.1057 (European 0.1023). Prices that were already correct are unchanged.
- **Missing market inputs are no longer silently replaced** (BSM, Black-76, GK, Binomial, Monte Carlo):
  - a missing or non-positive `spot0` / `fwd0` now raises `ValueError` (1.0.3 priced with a spot of 0.00001);
  - a missing `pricing_date` now raises `ValueError` with the expected format (1.0.3 raised an unclear `TypeError`);
  - a missing (or zero) `volatility` still defaults to 10% but now emits a `FutureWarning` pointing at the calling line; this becomes an error in 2.0.
- **Analytic delta** for BSM, Black-76 and Garman-Kohlhagen now includes the carry discount `exp(-(q - c) T)`, and put delta has the correct (negative) sign. In 1.0.3 put delta was returned as `+N(-d1)`. Equity call example (S=110, K=100, q=1%, 30d): 0.92095 -> 0.92020; put: +0.07905 -> -0.07898. Matches QuantLib.
- **Phi** (dividend / carry-yield sensitivity) now includes the same `exp(-(q - c) T)` factor: -8.32641 -> -8.31957 in the same example. Matches QuantLib.

### Added
- `out_of_sample` switch for American Monte Carlo (`engine(model="MC_GBM", ..., out_of_sample=True)`): fits the Longstaff-Schwartz exercise rule on one set of paths and prices on an independent set, removing the in-sample upward bias (about +0.01 on the LS 2001 benchmark). Default `False` keeps 1.x results.
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
