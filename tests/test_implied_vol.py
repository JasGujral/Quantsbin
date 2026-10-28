"""Implied volatility (bug 6): accuracy, range, and no-arbitrage bounds."""

import pytest

import quantsbin.derivativepricing as qbdp

CASES = {
    "equity-bsm": (qbdp.EqOption, {"model": "BSM", "spot0": 100, "rf_rate": 0.05, "yield_div": 0.01}),
    "futures-b76": (qbdp.FutOption, {"model": "B76", "fwd0": 100, "rf_rate": 0.05}),
    "fx-gk": (qbdp.FXOption, {"model": "GK", "spot0": 100, "rf_rate_local": 0.05, "rf_rate_foreign": 0.03}),
}


def _engine(underlying, option_type, vol, strike=100):
    cls, market = CASES[underlying]
    option = cls(option_type=option_type, strike=strike, expiry_date="20180630")
    return option.engine(pricing_date="20180531", volatility=vol, **market)


@pytest.mark.parametrize("underlying", CASES)
@pytest.mark.parametrize("option_type", ["Call", "Put"])
@pytest.mark.parametrize("vol", [0.05, 0.25, 0.9, 1.5, 3.0])
def test_round_trip(underlying, option_type, vol):
    engine = _engine(underlying, option_type, vol)
    assert engine.imply_volatility(engine.valuation()) == pytest.approx(vol, abs=1e-8)


@pytest.mark.parametrize("strike", [60, 140])
def test_round_trip_away_from_the_money(strike):
    """Deep ITM/OTM short-dated options have almost no vega (1.5e-7 at K=60), so the implied vol is
    only determined up to price round-off; check that it reproduces the premium instead."""
    engine = _engine("equity-bsm", "Call", 0.3, strike=strike)
    premium = engine.valuation()
    implied = engine.imply_volatility(premium)
    assert _engine("equity-bsm", "Call", implied, strike=strike).valuation() == pytest.approx(premium, abs=1e-10)


@pytest.mark.parametrize(("option_type", "premium"), [("Call", 0.0), ("Call", 150.0), ("Put", -1.0), ("Put", 150.0)])
def test_premium_outside_no_arbitrage_bounds_raises(option_type, premium):
    with pytest.raises(ValueError, match="no-arbitrage"):
        _engine("equity-bsm", option_type, 0.25).imply_volatility(premium)


def test_model_volatility_is_not_modified():
    model = _engine("equity-bsm", "Call", 0.25)._model_class
    model.imply_volatility(5.0)
    assert model.volatility == 0.25
