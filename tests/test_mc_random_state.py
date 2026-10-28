"""Monte Carlo random state (bug 7)."""

import numpy as np

import quantsbin.derivativepricing as qbdp


def _mc(**kw):
    option = qbdp.EqOption(option_type="Put", strike=40, expiry_date="20190101")
    return option.engine(
        model="MC_GBM", spot0=36, pricing_date="20180101", volatility=0.2, rf_rate=0.06, no_of_path=10_000, **kw
    )


def test_pricing_does_not_touch_numpy_global_random_state():
    np.random.seed(123)
    expected = np.random.rand(3)
    np.random.seed(123)
    _mc().valuation()
    assert np.array_equal(np.random.rand(3), expected)


def test_same_seed_same_price_and_independent_of_global_state():
    np.random.seed(1)
    first = _mc(seed=7).valuation()
    np.random.seed(999)
    second = _mc(seed=7).valuation()
    assert first == second


def test_seed_zero_is_respected():
    # 1.0.3 replaced seed=0 with the default seed 100 ('seed or 100').
    assert _mc(seed=0).valuation() != _mc(seed=100).valuation()
