# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- Repository moved to https://github.com/JasGujral/Quantsbin.
- README badges and links fixed; dead quantsbin.com documentation links removed.
- `development_testing.py` moved to `examples/quickstart.py`; fixed its `StdStrategies` call (`spread` -> `strike_spread`).
- Removed the dead Twitter badge.

### Removed
- Committed IDE settings (`.idea/`) and the distutils-generated `MANIFEST`.

## [1.0.3] - 2021-05-15
- Use `interp1d` instead of the deprecated spline in `line_plot`.
- Fixed unit tests and updated README.

## [1.0.2] - 2018-07-08
- First stable release on PyPI.
