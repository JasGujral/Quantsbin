"""Numerical (bump-and-reprice) greeks: bugs 8 and 11.

Reference: the analytic BSM greeks, which match QuantLib (see test_greeks_analytic.py).
"""

import math

import pytest

import quantsbin.derivativepricing as qbdp

MARKET = {"spot0": 110, "pricing_date": "20180531", "volatility": 0.25, "yield_div": 0.01}


def _engine(model, option_type="Put", rf_rate=0.05, **kw):
    option = qbdp.EqOption(option_type=option_type, strike=100, expiry_date="20180630")
    return option.engine(model=model, rf_rate=rf_rate, **MARKET, **kw)


@pytest.mark.parametrize("option_type", ["Call", "Put"])
def test_numerical_greeks_with_default_bumps_match_analytic(option_type):
    analytic = _engine("BSM", option_type).risk_parameters()
    numerical = _engine("BSM", option_type).risk_parameters_num()  # no bump sizes given: documented defaults
    for name in ("delta", "gamma", "vega", "rho", "theta"):
        assert math.isfinite(numerical[name]), name
    # Tolerances reflect the documented default bumps (spot +/-2%, vol +/-2%, rate +/-2%, 1 day):
    # a 2% spot bump has a central-difference error of about 0.003 in delta and 1% in gamma here.
    assert numerical["delta"] == pytest.approx(analytic["delta"], abs=5e-3)
    assert numerical["gamma"] == pytest.approx(analytic["gamma"], rel=0.02)
    assert numerical["vega"] == pytest.approx(analytic["vega"], rel=1e-3)
    assert numerical["rho"] == pytest.approx(analytic["rho"], rel=1e-3)
    # theta: one-day forward difference vs the analytic per-day theta
    assert numerical["theta"] == pytest.approx(analytic["theta"], rel=0.05)


def test_binomial_risk_parameters_are_finite_and_close_to_bsm():
    """risk_parameters() on a non-analytic model goes through the numerical path."""
    bsm = _engine("BSM").risk_parameters()
    tree = _engine("Binomial", no_of_steps=500).risk_parameters()
    for name in ("delta", "vega", "rho"):
        assert math.isfinite(tree[name]), name
        assert tree[name] == pytest.approx(bsm[name], rel=0.02, abs=5e-3), name  # 2% default spot bump


def test_numerical_rho_with_zero_rate():
    """Relative bumps never move a zero rate; bug 11 returned NaN here."""
    analytic = _engine("BSM", rf_rate=0.0).risk_parameters()["rho"]
    numerical = _engine("BSM", rf_rate=0.0).risk_parameters_num(delta_rf_rate=0.0001)["rho"]
    assert math.isfinite(numerical)
    assert numerical == pytest.approx(analytic, rel=1e-4)


def test_explicit_bump_sizes_still_respected():
    small = _engine("BSM").risk_parameters_num(delta_spot=0.001)["delta"]
    large = _engine("BSM").risk_parameters_num(delta_spot=0.2)["delta"]
    assert small != large
