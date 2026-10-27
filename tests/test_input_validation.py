"""Missing market inputs must not be silently replaced (bug 4).

1.0.3 replaced a missing spot with 1e-5 and a missing vol with 10% without telling the user,
and failed on a missing pricing date with an unhelpful TypeError from strptime.
"""

import pytest

import quantsbin.derivativepricing as qbdp

EXPIRY, PRICING = "20180630", "20180531"

CASES = [
    pytest.param(qbdp.EqOption, "European", "BSM", "spot0", {"rf_rate": 0.05}, id="equity-bsm"),
    pytest.param(qbdp.FutOption, "European", "B76", "fwd0", {"rf_rate": 0.05}, id="futures-b76"),
    pytest.param(qbdp.FXOption, "European", "GK", "spot0", {"rf_rate_local": 0.05}, id="fx-gk"),
    pytest.param(qbdp.EqOption, "American", "Binomial", "spot0", {"rf_rate": 0.05}, id="equity-binomial"),
    pytest.param(qbdp.EqOption, "European", "MC_GBM", "spot0", {"rf_rate": 0.05, "no_of_path": 1000}, id="equity-mc"),
]


def _engine(cls, expiry_type, model, **market):
    option = cls(option_type="Put", expiry_type=expiry_type, strike=100, expiry_date=EXPIRY)
    return option.engine(model=model, **market)


@pytest.mark.parametrize(("cls", "expiry_type", "model", "spot_kw", "extra"), CASES)
@pytest.mark.parametrize("bad_spot", [None, 0])
def test_missing_spot_raises(cls, expiry_type, model, spot_kw, extra, bad_spot):
    with pytest.raises(ValueError, match="spot"):
        _engine(
            cls, expiry_type, model, **{spot_kw: bad_spot}, pricing_date=PRICING, volatility=0.25, **extra
        ).valuation()


@pytest.mark.parametrize(("cls", "expiry_type", "model", "spot_kw", "extra"), CASES)
def test_missing_pricing_date_raises(cls, expiry_type, model, spot_kw, extra):
    with pytest.raises(ValueError, match="pricing_date"):
        _engine(cls, expiry_type, model, **{spot_kw: 110}, volatility=0.25, **extra).valuation()


@pytest.mark.parametrize(("cls", "expiry_type", "model", "spot_kw", "extra"), CASES)
def test_missing_volatility_warns_and_keeps_1x_default(cls, expiry_type, model, spot_kw, extra):
    market = {spot_kw: 110, "pricing_date": PRICING, **extra}
    with pytest.warns(FutureWarning, match="volatility"):
        defaulted = _engine(cls, expiry_type, model, **market).valuation()
    explicit = _engine(cls, expiry_type, model, **market, volatility=0.10).valuation()
    assert defaulted == pytest.approx(explicit, rel=1e-12)
