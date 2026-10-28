"""Binomial tree (bug 5: recursive implementation; bug 12: shared node cache).

The iterative implementation must reproduce 1.0.3 exactly on the same CRR tree with escrowed
discrete dividends (Hull; Schroder 1988). Reference values below were generated with 1.0.3.
"""

import ast

import pytest

import quantsbin.derivativepricing as qbdp

REFERENCE_1_0_3 = [
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "European", "Call", 25, "2.171591155108106"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "European", "Call", 100, "2.1778142505387"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "European", "Call", 400, "2.1742125260905634"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "European", "Put", 25, "3.8421724984780985"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "European", "Put", 100, "3.8483955939088053"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "European", "Put", 400, "3.8447938694593384"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "American", "Call", 25, "2.171591155108106"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "American", "Call", 100, "2.1778142505387"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "American", "Call", 400, "2.1742125260905634"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "American", "Put", 25, "4.484532174343904"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "American", "Put", 100, "4.488049779865594"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06}", "American", "Put", 400, "4.486940981396445"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "European", "Call", 25, "1.8678399344442984"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "European", "Call", 100, "1.8717984586276677"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "European", "Call", 400, "1.867864566015306"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "European", "Put", 25, "4.251269038771103"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "European", "Put", 100, "4.255227562954166"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "European", "Put", 400, "4.25129367034108"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "American", "Call", 25, "1.8678399344442984"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "American", "Call", 100, "1.8717984586285406"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "American", "Call", 400, "1.8678645660184927"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "American", "Put", 25, "4.685950784490976"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "American", "Put", 100, "4.690041039992381"),
    ("EqOption", "{'spot0': 36, 'rf_rate': 0.06, 'yield_div': 0.02}", "American", "Put", 400, "4.688025020763206"),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "European",
        "Call",
        25,
        "1.754080386855197",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "European",
        "Call",
        100,
        "1.7656229507559011",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "European",
        "Call",
        400,
        "1.7641095928515684",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "European",
        "Put",
        25,
        "4.395376596457585",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "European",
        "Put",
        100,
        "4.406919160358405",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "European",
        "Put",
        400,
        "4.405405802452767",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "American",
        "Call",
        25,
        "1.754080386855197",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "American",
        "Call",
        100,
        "1.7656229507559011",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "American",
        "Call",
        400,
        "1.7641095928515684",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "American",
        "Put",
        25,
        "4.819986892375566",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "American",
        "Put",
        100,
        "4.835411772842787",
    ),
    (
        "EqOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'div_list': [('20180401', 0.5), ('20181001', 0.5)]}",
        "American",
        "Put",
        400,
        "4.834035580565511",
    ),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "European", "Call", 25, "1.355829206781731"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "European", "Call", 100, "1.3568486451955217"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "European", "Call", 400, "1.3527495765584474"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "European", "Put", 25, "5.122887341118714"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "European", "Put", 100, "5.123906779532578"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "European", "Put", 400, "5.119807710895055"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "American", "Call", 25, "1.3706120386495129"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "American", "Call", 100, "1.3700939819297302"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "American", "Call", 400, "1.3658004914096618"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "American", "Put", 25, "5.230883122528078"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "American", "Put", 100, "5.231165070802421"),
    ("FutOption", "{'fwd0': 36, 'rf_rate': 0.06}", "American", "Put", 400, "5.227179294309042"),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "European",
        "Call",
        25,
        "1.7282515260144529",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "European",
        "Call",
        100,
        "1.7312793201146621",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "European",
        "Call",
        400,
        "1.7272437279587334",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "European",
        "Put",
        25,
        "4.462793661638127",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "European",
        "Put",
        100,
        "4.465821455738453",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "European",
        "Put",
        400,
        "4.46178586358327",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "American",
        "Call",
        25,
        "1.7282515634663265",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "American",
        "Call",
        100,
        "1.7312795396804832",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "American",
        "Call",
        400,
        "1.7272440207000275",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "American",
        "Put",
        25,
        "4.804753912900607",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "American",
        "Put",
        100,
        "4.807011730190131",
    ),
    (
        "FXOption",
        "{'spot0': 36, 'rf_rate_local': 0.06, 'rf_rate_foreign': 0.03}",
        "American",
        "Put",
        400,
        "4.804410131698576",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "European",
        "Call",
        25,
        "1.8678399344442984",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "European",
        "Call",
        100,
        "1.8717984586276677",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "European",
        "Call",
        400,
        "1.867864566015306",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "European",
        "Put",
        25,
        "4.251269038771103",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "European",
        "Put",
        100,
        "4.255227562954166",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "European",
        "Put",
        400,
        "4.25129367034108",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "American",
        "Call",
        25,
        "1.8678399344442984",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "American",
        "Call",
        100,
        "1.8717984586285406",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "American",
        "Call",
        400,
        "1.8678645660184927",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "American",
        "Put",
        25,
        "4.685950784490976",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "American",
        "Put",
        100,
        "4.690041039992381",
    ),
    (
        "ComOption",
        "{'spot0': 36, 'rf_rate': 0.06, 'cnv_yield': 0.03, 'cost_yield': 0.01}",
        "American",
        "Put",
        400,
        "4.688025020763206",
    ),
]


@pytest.mark.parametrize(("cls_name", "market", "expiry_type", "option_type", "steps", "expected"), REFERENCE_1_0_3)
def test_matches_1_0_3(cls_name, market, expiry_type, option_type, steps, expected):
    cls = getattr(qbdp, cls_name)
    option = cls(option_type=option_type, expiry_type=expiry_type, strike=40, expiry_date="20190101")
    engine = option.engine(
        model="Binomial", pricing_date="20180101", volatility=0.2, no_of_steps=steps, **ast.literal_eval(market)
    )
    assert engine.valuation() == pytest.approx(float(expected), abs=1e-12)


def _american_put(steps, spot=36.0):
    option = qbdp.EqOption(option_type="Put", expiry_type="American", strike=40, expiry_date="20190101")
    return option.engine(
        model="Binomial", spot0=spot, pricing_date="20180101", volatility=0.2, rf_rate=0.06, no_of_steps=steps
    )


def test_many_steps_run_and_converge():
    # 1.0.3 hit RecursionError above ~1000 steps.
    v2000, v5000 = _american_put(2000).valuation(), _american_put(5000).valuation()
    assert v2000 == pytest.approx(v5000, abs=1e-3)
    assert v5000 == pytest.approx(4.4867, abs=1e-3)  # continuous-exercise American value


def test_european_converges_to_bsm():
    option = qbdp.EqOption(option_type="Put", strike=40, expiry_date="20190101")
    market = {"spot0": 36, "pricing_date": "20180101", "volatility": 0.2, "rf_rate": 0.06}
    tree = option.engine(model="Binomial", no_of_steps=4000, **market).valuation()
    assert tree == pytest.approx(option.engine(model="BSM", **market).valuation(), abs=1e-3)


def test_pnl_attribution_spot_move():
    """1.0.3 returned 0: the bumped and base trees shared one node cache through a shallow copy."""
    base = _american_put(100)
    pnl = base.pnl_attribution(delta_spot=0.05)["spot0"]
    expected = _american_put(100, spot=36 * 1.05).valuation() - base.valuation()
    assert pnl == pytest.approx(expected, abs=1e-12)
