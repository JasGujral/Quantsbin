"""Analytic greeks checked against central finite differences of the model's own price.

The prices themselves match QuantLib to 1e-6, so a finite difference of the price is an
independent reference for the analytic formulas (Hull, Options, Futures and Other Derivatives,
ch. 19, generalised Black-Scholes-Merton with carry).
"""

import math

import pytest

import quantsbin.derivativepricing as qbdp

K, SPOT, VOL = 100.0, 110.0, 0.25
PRICING, EXPIRY = "20180531", "20180630"
T = 30 / 365

UNDERLYINGS = {
    # id: (instrument class, spot keyword, market kwargs, carry yield q, yield keyword)
    "equity-bsm": (qbdp.EqOption, "spot0", {"model": "BSM", "rf_rate": 0.05, "yield_div": 0.01}, 0.01, "yield_div"),
    "futures-b76": (qbdp.FutOption, "fwd0", {"model": "B76", "rf_rate": 0.05}, 0.05, None),
    "fx-gk": (qbdp.FXOption, "spot0", {"model": "GK", "rf_rate_local": 0.05, "rf_rate_foreign": 0.03}, 0.03, None),
}


def _engine(cls, spot_kw, market, option_type, spot=SPOT, **overrides):
    option = cls(option_type=option_type, strike=K, expiry_date=EXPIRY)
    return option.engine(pricing_date=PRICING, volatility=VOL, **{spot_kw: spot}, **{**market, **overrides})


@pytest.mark.parametrize("underlying", UNDERLYINGS)
@pytest.mark.parametrize("option_type", ["Call", "Put"])
def test_delta_matches_finite_difference(underlying, option_type):
    cls, spot_kw, market, _, _ = UNDERLYINGS[underlying]
    h = 1e-4
    up = _engine(cls, spot_kw, market, option_type, spot=SPOT + h).valuation()
    dn = _engine(cls, spot_kw, market, option_type, spot=SPOT - h).valuation()
    expected = (up - dn) / (2 * h)

    delta = _engine(cls, spot_kw, market, option_type).risk_parameters()["delta"]

    assert delta == pytest.approx(expected, abs=1e-6)


@pytest.mark.parametrize("underlying", UNDERLYINGS)
def test_put_delta_is_negative(underlying):
    cls, spot_kw, market, _, _ = UNDERLYINGS[underlying]
    assert _engine(cls, spot_kw, market, "Put").risk_parameters()["delta"] < 0


@pytest.mark.parametrize("underlying", UNDERLYINGS)
def test_delta_put_call_parity(underlying):
    """delta_call - delta_put = exp(-q T) for European options."""
    cls, spot_kw, market, q, _ = UNDERLYINGS[underlying]
    call = _engine(cls, spot_kw, market, "Call").risk_parameters()["delta"]
    put = _engine(cls, spot_kw, market, "Put").risk_parameters()["delta"]
    assert call - put == pytest.approx(math.exp(-q * T), abs=1e-9)


@pytest.mark.parametrize("option_type", ["Call", "Put"])
def test_bsm_phi_matches_finite_difference(option_type):
    """phi = dV/dq, the sensitivity to the continuous dividend yield."""
    cls, spot_kw, market, q, yield_kw = UNDERLYINGS["equity-bsm"]
    h = 1e-6
    up = _engine(cls, spot_kw, market, option_type, **{yield_kw: q + h}).valuation()
    dn = _engine(cls, spot_kw, market, option_type, **{yield_kw: q - h}).valuation()
    expected = (up - dn) / (2 * h)

    phi = _engine(cls, spot_kw, market, option_type).risk_parameters()["phi"]

    assert phi == pytest.approx(expected, rel=1e-6)
