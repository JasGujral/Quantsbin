"""Reference values for vanilla European options, ported from the 1.0.3 unittest suite.

Market setup shared by all cases: strike 100, spot/forward 110, vol 25%,
priced 2018-05-31 for expiry 2018-06-30 (30 days, ACT/365).
"""

import pytest

import quantsbin.derivativepricing as qbdp
from quantsbin.derivativepricing.namesnmapper import OBJECT_MODEL, UdlType

INSTRUMENT = {
    "option_type": "Call",
    "expiry_type": "European",
    "derivative_type": "Vanilla Option",
    "expiry_date": "20180630",
    "strike": 100,
}

CASES = [
    pytest.param(
        qbdp.EqOption,
        UdlType.STOCK.value,
        {
            "model": "BSM",
            "spot0": 110,
            "pricing_date": "20180531",
            "volatility": 0.25,
            "rf_rate": 0.05,
            "pv_div": 0,
            "yield_div": 0.01,
        },
        110,
        10.60964,
        # 1.0.3 returned 0.92095 here (missing the e^(-qT) dividend discount, bug 1).
        # Corrected value; matches QuantLib AnalyticEuropeanEngine to 1e-15.
        ("delta", 0.9201952109409319),
        id="equity-bsm",
    ),
    pytest.param(
        qbdp.FutOption,
        UdlType.FUTURES.value,
        {"model": "B76", "fwd0": 110, "pricing_date": "20180531", "volatility": 0.25, "rf_rate": 0.05},
        110,
        10.278649928591477,
        ("gamma", 0.019833947075722964),
        id="futures-b76",
    ),
    pytest.param(
        qbdp.FXOption,
        UdlType.FX.value,
        {
            "model": "GK",
            "spot0": 110,
            "rf_rate_local": 0.05,
            "pricing_date": "20180531",
            "volatility": 0.25,
            "rf_rate_foreign": 0.03,
        },
        110,
        10.443695049596826,
        ("theta", -0.02402706559595148),
        id="fx-gk",
    ),
    pytest.param(
        qbdp.ComOption,
        UdlType.COMMODITY.value,
        {
            "model": "GK",
            "spot0": 110,
            "rf_rate": 0.05,
            "cnv_yield": 0.03,
            "cost_yield": 0.02,
            "pricing_date": "20180531",
            "volatility": 0.25,
        },
        110,
        10.60964161458648,
        ("vega", 4.642250887645513),
        id="commodity-gk",
    ),
]


@pytest.mark.parametrize(("option_cls", "underlying", "market", "spot", "premium", "greek"), CASES)
def test_vanilla_reference(option_cls, underlying, market, spot, premium, greek):
    option = option_cls(**INSTRUMENT)
    assert market["model"] in OBJECT_MODEL[underlying][INSTRUMENT["expiry_type"]]

    engine = option.engine(**market)
    name, expected = greek

    assert option.payoff(spot) == pytest.approx(10, abs=1e-5)
    assert engine.valuation() == pytest.approx(premium, abs=1e-5)
    assert engine.risk_parameters()[name] == pytest.approx(expected, abs=1e-5)
