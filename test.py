"""
developed by Quantsbin - Jun'18

"""

import unittest
import quantsbin.derivativepricing as qbdp

from quantsbin.derivativepricing.namesnmapper import (
    VanillaOptionType,
    ExpiryType,
    UdlType,
    OBJECT_MODEL,
    DerivativeType,
)


Input = {
    "equityInst": {
        "option_type": "Call",
        "expiry_type": "European",
        "derivative_type": "Vanilla Option",
        "expiry_date": "20180630",
        "strike": 100,
    },
    "equityEng": {
        "model": "BSM",
        "spot0": 110,
        "pricing_date": "20180531",
        "volatility": 0.25,
        "rf_rate": 0.05,
        "pv_div": 0,
        "yield_div": 0.01,
    },
    "futuresInst": {
        "option_type": "Call",
        "expiry_type": "European",
        "derivative_type": "Vanilla Option",
        "expiry_date": "20180630",
        "strike": 100,
    },
    "futuresEng": {"model": "B76", "fwd0": 110, "pricing_date": "20180531", "volatility": 0.25, "rf_rate": 0.05},
    "fxInst": {
        "option_type": "Call",
        "expiry_type": "European",
        "derivative_type": "Vanilla Option",
        "expiry_date": "20180630",
        "strike": 100,
    },
    "fxEng": {
        "model": "GK",
        "spot0": 110,
        "rf_rate_local": 0.05,
        "pricing_date": "20180531",
        "volatility": 0.25,
        "rf_rate_foreign": 0.03,
    },
    "comInst": {
        "option_type": "Call",
        "expiry_type": "European",
        "derivative_type": "Vanilla Option",
        "expiry_date": "20180630",
        "strike": 100,
    },
    "comEng": {
        "model": "GK",
        "spot0": 110,
        "rf_rate": 0.05,
        "cnv_yield": 0.03,
        "cost_yield": 0.02,
        "pricing_date": "20180531",
        "volatility": 0.25,
    },
}

Output = {
    "equity": {
        "payOff": 10,
        "premium": 10.60964,
        "riskParameters": {
            "Delta": 0.9209518466754392,
            "Gamma": 0.01867131211008939,
            "Phi": -8.326413956243696,
            "Rho": 0.07447547801828713,
            "Theta": -0.028982100654899527,
            "Vega": 0.04642250887645513,
        },
    },
    "futures": {
        "payOff": 10,
        "premium": 10.278649928591477,
        "riskParameters": {
            "Delta": 0.9139728421226333,
            "Gamma": 0.019833947075722964,
            "Rho": -0.8448205420760118,
            "Theta": -0.0191391198399402,
            "Vega": 0.04931316978416053,
        },
    },
    "fx": {
        "payOff": 10,
        "premium": 10.443695049596826,
        "riskParameters": {
            "Delta": 0.9175179027112913,
            "Gamma": 0.019248913449738413,
            "Rho": 0.07416552311621331,
            "Theta": -0.02402706559595148,
            "Vega": 0.04785859987845919,
        },
    },
    "commodity": {
        "payOff": 10,
        "premium": 10.60964161458648,
        "riskParameters": {
            "Delta": 0.5234330145822786,
            "Gamma": 0.05542873261965293,
            "Rho": 0.040506072164629855,
            "Theta": -0.04991552463127051,
            "Vega": 4.642250887645513,
        },
    },
}


class Test_eqOption(unittest.TestCase):
    def setUp(self):
        self.eq_option = qbdp.EqOption(**Input["equityInst"])
        self.eq_option_engine = self.eq_option.engine(**Input["equityEng"])

    def test(self):
        if Input["equityEng"]["model"] in OBJECT_MODEL[UdlType.STOCK.value][Input["equityInst"]["expiry_type"]]:
            self.assertAlmostEqual(
                self.eq_option.payoff(Input["equityEng"]["spot0"]), Output["equity"]["payOff"], places=5
            )
            self.assertAlmostEqual(self.eq_option_engine.valuation(), Output["equity"]["premium"], places=5)
            self.assertAlmostEqual(
                self.eq_option_engine.risk_parameters()["delta"], Output["equity"]["riskParameters"]["Delta"], places=5
            )
        else:
            self.fail("Invalid Model")


class Test_futOption(unittest.TestCase):
    def setUp(self):
        self.fut_option = qbdp.FutOption(**Input["futuresInst"])
        self.fut_option_engine = self.fut_option.engine(**Input["futuresEng"])

    def test(self):
        if Input["futuresEng"]["model"] in OBJECT_MODEL[UdlType.FUTURES.value][Input["futuresInst"]["expiry_type"]]:
            self.assertAlmostEqual(
                self.fut_option.payoff(Input["futuresEng"]["fwd0"]), Output["futures"]["payOff"], places=5
            )
            self.assertAlmostEqual(self.fut_option_engine.valuation(), Output["futures"]["premium"], places=5)
            self.assertAlmostEqual(
                self.fut_option_engine.risk_parameters()["gamma"],
                Output["futures"]["riskParameters"]["Gamma"],
                places=5,
            )
        else:
            self.fail("Invalid Model")


class Test_fxtOption(unittest.TestCase):
    def setUp(self):
        self.fx_option = qbdp.FXOption(**Input["fxInst"])
        self.fx_option_engine = self.fx_option.engine(**Input["fxEng"])

    def test(self):
        if Input["fxEng"]["model"] in OBJECT_MODEL[UdlType.FX.value][Input["fxInst"]["expiry_type"]]:
            self.assertAlmostEqual(self.fx_option.payoff(Input["fxEng"]["spot0"]), Output["fx"]["payOff"], places=5)
            self.assertAlmostEqual(self.fx_option_engine.valuation(), Output["fx"]["premium"], places=5)
            self.assertAlmostEqual(
                self.fx_option_engine.risk_parameters()["theta"], Output["fx"]["riskParameters"]["Theta"], places=5
            )
        else:
            self.fail("Invalid Model")


class Test_comOption(unittest.TestCase):
    def setUp(self):
        self.com_option = qbdp.ComOption(**Input["comInst"])
        self.com_option_engine = self.com_option.engine(**Input["comEng"])

    def test(self):
        if Input["comEng"]["model"] in OBJECT_MODEL[UdlType.COMMODITY.value][Input["comInst"]["expiry_type"]]:
            self.assertAlmostEqual(
                self.com_option.payoff(Input["comEng"]["spot0"]), Output["commodity"]["payOff"], places=5
            )
            self.assertAlmostEqual(self.com_option_engine.valuation(), Output["commodity"]["premium"], places=5)
            self.assertAlmostEqual(
                self.com_option_engine.risk_parameters()["vega"],
                Output["commodity"]["riskParameters"]["Vega"],
                places=5,
            )
        else:
            self.fail("Invalid Model")


# eqOption1 = qbdp.EqOption(option_type='Call', strike=100, expiry_date='20180630')
# models = eqOption1.list_models()
# eqOption1_pricer = eqOption1.engine(model='BSM', spot0=100, pricing_date='20180531', volatility=.25,
#                                     rf_rate=.05, pv_div=0,
#                                     yield_div=.01)
# premium = eqOption1_pricer.valuation()
# risk_parameters = eqOption1_pricer.risk_parameters()


if __name__ == "__main__":
    test_classes_to_run = [Test_eqOption, Test_futOption]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)
