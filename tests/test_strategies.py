"""Option strategies (bug 9: per-call multiprocessing Pool)."""

import subprocess
import sys
import textwrap

import pytest

import quantsbin.derivativepricing as qbdp

MARKET = {"model": "BSM", "spot0": 105, "pricing_date": "20180531", "volatility": 0.25, "rf_rate": 0.05}


def _bull_call_spread():
    return qbdp.OptionStr1Udl(
        [
            (qbdp.EqOption(option_type="Call", strike=100, expiry_date="20180630"), 1),
            (qbdp.EqOption(option_type="Call", strike=110, expiry_date="20180630"), -1),
        ]
    )


def test_strategy_value_is_sum_of_legs():
    legs = [
        qbdp.EqOption(option_type="Call", strike=k, expiry_date="20180630").engine(**MARKET).valuation()
        for k in (100, 110)
    ]
    assert _bull_call_spread().engine(**MARKET).valuation() == pytest.approx(legs[0] - legs[1], abs=1e-12)


def test_strategy_payoff_and_greeks():
    strategy = _bull_call_spread()
    assert strategy.payoff(120) == pytest.approx(10.0)
    assert set(strategy.engine(**MARKET).risk_parameters()) >= {"delta", "gamma", "vega"}


SCRIPT_WITHOUT_MAIN_GUARD = textwrap.dedent(
    """
    import multiprocessing
    multiprocessing.set_start_method("spawn", force=True)   # macOS default; Linux uses forkserver from 3.14
    import quantsbin.derivativepricing as qbdp
    legs = [(qbdp.EqOption(option_type="Call", strike=k, expiry_date="20180630"), w) for k, w in [(100, 1), (110, -1)]]
    engine = qbdp.OptionStr1Udl(legs).engine(model="BSM", spot0=105, pricing_date="20180531",
                                             volatility=0.25, rf_rate=0.05)
    print(round(engine.valuation(), 6))
    """
)


def test_strategy_runs_in_a_script_without_main_guard(tmp_path):
    script = tmp_path / "user_script.py"
    script.write_text(SCRIPT_WITHOUT_MAIN_GUARD)
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr[-2000:]
    assert result.stdout.strip() == "5.07741"
