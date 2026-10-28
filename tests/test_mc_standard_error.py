"""Monte Carlo standard error (valuation_with_error)."""

import numpy as np
import pytest

import quantsbin.derivativepricing as qbdp


def _mc(expiry_type="European", spot=36.0, **kw):
    option = qbdp.EqOption(option_type="Put", expiry_type=expiry_type, strike=40, expiry_date="20190101")
    return option.engine(model="MC_GBM", spot0=spot, pricing_date="20180101", volatility=0.2, rf_rate=0.06, **kw)


CASES = [
    pytest.param("European", {"no_of_path": 50_000}, id="european"),
    pytest.param("European", {"no_of_path": 20_000, "div_list": [("20180701", 0.5)]}, id="european-dividend"),
    pytest.param("American", {"no_of_path": 20_000, "no_of_steps": 50}, id="american"),
    pytest.param("American", {"no_of_path": 20_000, "no_of_steps": 50, "out_of_sample": True}, id="american-oos"),
    pytest.param("European", {"no_of_path": 25_000, "antithetic": True}, id="european-antithetic"),
]


@pytest.mark.parametrize(("expiry_type", "kw"), CASES)
def test_price_equals_valuation(expiry_type, kw):
    result = _mc(expiry_type, **kw).valuation_with_error()
    assert result.price == _mc(expiry_type, **kw).valuation()
    assert result.standard_error > 0


@pytest.mark.parametrize(("expiry_type", "kw"), CASES[:3])
def test_standard_error_matches_seed_to_seed_spread(expiry_type, kw):
    prices = [_mc(expiry_type, seed=s, **kw).valuation() for s in range(1, 21)]
    reported = _mc(expiry_type, seed=1, **kw).valuation_with_error().standard_error
    assert reported == pytest.approx(np.std(prices, ddof=1), rel=0.5)


def test_bsm_within_three_standard_errors():
    result = _mc(no_of_path=200_000).valuation_with_error()
    bsm = qbdp.EqOption(option_type="Put", strike=40, expiry_date="20190101").engine(
        model="BSM", spot0=36, pricing_date="20180101", volatility=0.2, rf_rate=0.06
    )
    assert abs(result.price - bsm.valuation()) < 3 * result.standard_error


def test_paths_and_antithetic_count():
    assert _mc(no_of_path=1000).valuation_with_error().n_paths == 1000
    assert _mc(no_of_path=1000, antithetic=True).valuation_with_error().n_paths == 2000


def test_exercise_today_has_zero_error():
    result = _mc("American", spot=20.0, no_of_path=5000, no_of_steps=50).valuation_with_error()
    assert result.price == 20.0 and result.standard_error == 0.0


def test_not_available_for_closed_form_models():
    engine = qbdp.EqOption(strike=40, expiry_date="20190101").engine(
        model="BSM", spot0=36, pricing_date="20180101", volatility=0.2, rf_rate=0.06
    )
    with pytest.raises(NameError):
        engine.valuation_with_error()
