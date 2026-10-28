"""P&L attribution (bug 10): each market move must land on the matching input."""

import pytest

import quantsbin.derivativepricing as qbdp

FX = {
    "model": "GK",
    "spot0": 110,
    "rf_rate_local": 0.05,
    "rf_rate_foreign": 0.03,
    "pricing_date": "20180531",
    "volatility": 0.25,
}


def _fx(**overrides):
    return qbdp.FXOption(option_type="Call", strike=100, expiry_date="20180630").engine(**{**FX, **overrides})


def test_fx_foreign_rate_move_is_attributed_to_the_foreign_rate():
    pnl = _fx().pnl_attribution(delta_rf_foreign=0.10)  # foreign rate +10% relative: 3.0% -> 3.3%
    expected = _fx(rf_rate_foreign=0.033).valuation() - _fx().valuation()
    assert pnl["cnv_yield"] == pytest.approx(expected, rel=1e-9)
    assert pnl["cost_yield"] == 0


def test_moves_not_given_contribute_nothing():
    pnl = _fx().pnl_attribution(delta_spot=0.01)
    assert pnl["spot0"] != 0
    for key in ("volatility", "rf_rate", "cnv_yield", "cost_yield", "_pricing_date"):
        assert pnl[key] == 0, key
