"""American options by Monte Carlo (Longstaff-Schwartz least squares), bug 2.

Reference: Longstaff & Schwartz (2001), "Valuing American Options by Simulation: A Simple
Least-Squares Approach", Review of Financial Studies 14(1), Table 1. American put, S=36, K=40,
r=6%, sigma=20%, T=1 year: finite-difference value 4.478.
"""

import pytest

import quantsbin.derivativepricing as qbdp

LS_REF = 4.478


def _put(expiry_type, model, spot=36.0, **kw):
    option = qbdp.EqOption(option_type="Put", expiry_type=expiry_type, strike=40, expiry_date="20190101")
    return option.engine(model=model, spot0=spot, pricing_date="20180101", volatility=0.20, rf_rate=0.06, **kw)


def test_lsm_american_put_matches_longstaff_schwartz_table_1():
    price = _put("American", "MC_GBM", no_of_path=100_000, no_of_steps=50, seed=7).valuation()
    assert price == pytest.approx(LS_REF, abs=0.03)


def test_lsm_american_put_at_least_european():
    american = _put("American", "MC_GBM", no_of_path=50_000, no_of_steps=50, seed=7).valuation()
    european = _put("European", "BSM").valuation()
    assert american > european


def test_lsm_deep_in_the_money_put_is_worth_at_least_intrinsic():
    # S=20, K=40: exercising today (20) beats holding; 1.0.3 returned 19.95.
    price = _put("American", "MC_GBM", spot=20.0, no_of_path=20_000, no_of_steps=50, seed=7).valuation()
    assert price >= 20.0 - 1e-12


def test_lsm_out_of_the_money_put_is_positive():
    # The 1.0.3 bug: no path in the money at early steps -> value collapsed to 0.
    price = _put("American", "MC_GBM", spot=55.0, no_of_path=50_000, no_of_steps=50, seed=7).valuation()
    european = _put("European", "BSM", spot=55.0).valuation()
    assert price == pytest.approx(european, rel=0.15)
    assert price > 0
