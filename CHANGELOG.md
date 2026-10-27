# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
