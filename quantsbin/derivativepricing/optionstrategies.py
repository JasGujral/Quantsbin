"""
developed by Quantsbin - Jun'18

"""

import platform
from collections import Counter
from datetime import timedelta
from functools import partial
from multiprocessing import Pool

from . import instruments as inst
from .namesnmapper import ExpiryType, RiskParameter, UdlType, VanillaOptionType

VANILLA_OBJECT_MAPPER = {
    UdlType.STOCK.value: inst.EqOption,
    UdlType.FUTURES.value: inst.FutOption,
    UdlType.FX.value: inst.FXOption,
    UdlType.COMMODITY.value: inst.ComOption,
}


def p_map(func, parameter):
    if platform.system() == "Windows":
        return map(func, parameter)
    else:
        with Pool() as p:
            return p.map(func, parameter)


class OptionStr1Udl:
    """
    This module is written over the .instruments and .pricingmodels modules
    Here the combined payoff, valuation and riskparameters are calculated for the portfolio
        Args required:
            option_portfolio => (List of tuples). e.g. [(eqOption1, -1), (eqOption2, -2)]
                                eqOption1 => qbdp.derivativepricing.EqOption(**Instrument parameters)
                                -1 => position and units of the option (long/short)
            spot0 => (Float). e.g. 110
            **kwargs =>  market parameters for PricingEngine (calculation of combined valuation and riskparameters)
    """

    def __init__(self, option_portfolio):
        self.option_portfolio = option_portfolio
        self.spot = None

    def weighted_payoff(self, option_detail):
        return option_detail[0].payoff(self.spot) * option_detail[1]

    def payoff(self, spot):
        self.spot = spot
        _payoffs = p_map(self.weighted_payoff, self.option_portfolio)
        return sum(_payoffs)

    def engine(self, **kwargs):
        return Engine(self, self.option_portfolio, **kwargs)


class Engine:
    def __init__(self, instrument, option_portfolio, **kwargs):
        self._other_args = kwargs
        self.option_portfolio = option_portfolio
        self.instrument = instrument

    def weighted_valuation(self, option_detail):
        return option_detail[0].engine(**self._other_args).valuation() * option_detail[1]

    def valuation(self):
        _valuations = p_map(self.weighted_valuation, self.option_portfolio)
        return sum(_valuations)

    def weighted_risk_parameters(self, option_detail):
        risk_parameters = option_detail[0].engine(**self._other_args).risk_parameters()
        risk_parameters.update((x, y * option_detail[1]) for x, y in risk_parameters.items())
        return risk_parameters

    def risk_parameter_ind(self, option_detail, risk_name):
        _risk_parameter_func = option_detail[0].engine(**self._other_args).risk_parameters_func()
        _risk_parameter = _risk_parameter_func[risk_name]()
        return _risk_parameter * option_detail[1]

    def risk_parameter(self, var):
        _risk_parameters = p_map(partial(self.risk_parameter_ind, risk_name=var), self.option_portfolio)
        return sum(_risk_parameters)

    def risk_parameters(self):
        str_risk_parameters = Counter()
        _risk_parameters = p_map(self.weighted_risk_parameters, self.option_portfolio)
        [str_risk_parameters.update(i) for i in _risk_parameters]
        return dict(str_risk_parameters)

    def risk_parameters_func(self):
        return {
            RiskParameter.DELTA.value: partial(self.risk_parameter, RiskParameter.DELTA.value),
            RiskParameter.GAMMA.value: partial(self.risk_parameter, RiskParameter.GAMMA.value),
            RiskParameter.THETA.value: partial(self.risk_parameter, RiskParameter.THETA.value),
            RiskParameter.VEGA.value: partial(self.risk_parameter, RiskParameter.VEGA.value),
            RiskParameter.RHO.value: partial(self.risk_parameter, RiskParameter.RHO.value),
        }


class StdStrategies(OptionStr1Udl):
    """
    The combined payoff, valuation and riskparameters are calculated for the Standard Strategies.
    This class inherits OptionStr1Udl class. so for valuation and riskparameters the market parameters are passed
    to the engine in similar fashion
        Args required:
            name = (String). Name of the std strategy e.g. "bull_call"
            asset = (String). Name of the asset class  e.g. "Stock"
            expiry_date = (Date in string format "YYYYMMDD") e.g. 10 Dec 2018 as "20181210"
            expiry_type = 'European' or 'American' (default is set to 'European')
            low_strike = (Float) Strike for option with lowest strike e.g. 110
            strike_spread = (Float). This is added or subtracted to strike based on the strategy e.g. 10
            time_spread = time added to expiry in to find expiry of long term maturity option in calendar spread.

    List of Std. Strategies [bull_call, bear_call, bull_put, bear_put, box_spread, butterfly_call, butterfly_put,
                            calendar_call, calendar_put, rev_calendar_call, rev_calendar_put, bottom_straddle,
                            top_straddle, bottom_strangle, top_strangle, strip, strap]
    """

    def __init__(
        self,
        name="bull_call",
        asset=None,
        expiry_date=None,
        expiry_type=None,
        low_strike=100,
        strike_spread=10,
        time_spread=30,
    ):
        self.name = name
        self.asset = asset or UdlType.STOCK.value
        self.expiry_date = expiry_date or None
        self.expiry_type = expiry_type or ExpiryType.EUROPEAN.value
        self.strike = low_strike or 100
        self.spread = strike_spread or (low_strike * 0.1)
        self.time_spread = time_spread or 30
        super().__init__(self.std_option_portfolio)

    @property
    def std_option_portfolio(self):
        _option_portfolio = getattr(self, self.name)()
        return _option_portfolio

    def low_option(self, option_type):
        return VANILLA_OBJECT_MAPPER[self.asset](
            option_type=option_type,
            strike=self.strike - self.spread,
            expiry_date=self.expiry_date,
            expiry_type=self.expiry_type,
        )

    def mid_option(self, option_type):
        return VANILLA_OBJECT_MAPPER[self.asset](
            option_type=option_type, strike=self.strike, expiry_date=self.expiry_date, expiry_type=self.expiry_type
        )

    def high_option(self, option_type):
        return VANILLA_OBJECT_MAPPER[self.asset](
            option_type=option_type,
            strike=self.strike + self.spread,
            expiry_date=self.expiry_date,
            expiry_type=self.expiry_type,
        )

    def before_option(self, option_type):
        return VANILLA_OBJECT_MAPPER[self.asset](
            option_type=option_type,
            strike=self.strike,
            expiry_date=self.expiry_date - timedelta(days=self.time_spread),
            expiry_type=self.expiry_type,
        )

    def after_option(self, option_type):
        return VANILLA_OBJECT_MAPPER[self.asset](
            option_type=option_type,
            strike=self.strike,
            expiry_date=self.expiry_date + timedelta(days=self.time_spread),
            expiry_type=self.expiry_type,
        )

    def bull_call(self):
        return [
            (self.mid_option(VanillaOptionType.CALL.value), 1),
            (self.high_option(VanillaOptionType.CALL.value), -1),
        ]

    def bear_call(self):
        return [
            (self.mid_option(VanillaOptionType.CALL.value), -1),
            (self.high_option(VanillaOptionType.CALL.value), 1),
        ]

    def bull_put(self):
        return [(self.mid_option(VanillaOptionType.PUT.value), 1), (self.high_option(VanillaOptionType.PUT.value), -1)]

    def bear_put(self):
        return [(self.mid_option(VanillaOptionType.PUT.value), -1), (self.high_option(VanillaOptionType.PUT.value), 1)]

    def box_spread(self):
        return [
            (self.mid_option(VanillaOptionType.CALL.value), 1),
            (self.high_option(VanillaOptionType.CALL.value), -1),
            (self.mid_option(VanillaOptionType.PUT.value), -1),
            (self.high_option(VanillaOptionType.PUT.value), 1),
        ]

    def butterfly_call(self):
        return [
            (self.low_option(VanillaOptionType.CALL.value), 1),
            (self.mid_option(VanillaOptionType.CALL.value), -1),
            (self.mid_option(VanillaOptionType.CALL.value), -1),
            (self.high_option(VanillaOptionType.CALL.value), 1),
        ]

    def butterfly_put(self):
        return [
            (self.low_option(VanillaOptionType.PUT.value), -1),
            (self.mid_option(VanillaOptionType.PUT.value), 1),
            (self.mid_option(VanillaOptionType.PUT.value), 1),
            (self.high_option(VanillaOptionType.PUT.value), -1),
        ]

    def calendar_call(self):
        return [(self.mid_option(VanillaOptionType.CALL.value), -1), self.after_option(VanillaOptionType.CALL.value), 1]

    def calendar_put(self):
        return [(self.mid_option(VanillaOptionType.PUT.value), -1), self.after_option(VanillaOptionType.PUT.value), 1]

    def rev_calendar_call(self):
        return [(self.mid_option(VanillaOptionType.CALL.value), 1), self.after_option(VanillaOptionType.CALL.value), -1]

    def rev_calendar_put(self):
        return [(self.mid_option(VanillaOptionType.PUT.value), 1), self.after_option(VanillaOptionType.PUT.value), -1]

    def bottom_straddle(self):
        return [(self.mid_option(VanillaOptionType.CALL.value), 1), (self.mid_option(VanillaOptionType.PUT.value), 1)]

    def top_straddle(self):
        return [(self.mid_option(VanillaOptionType.CALL.value), -1), (self.mid_option(VanillaOptionType.PUT.value), -1)]

    def bottom_strangle(self):
        return [(self.mid_option(VanillaOptionType.CALL.value), 1), (self.high_option(VanillaOptionType.PUT.value), 1)]

    def top_strangle(self):
        return [
            (self.mid_option(VanillaOptionType.CALL.value), -1),
            (self.high_option(VanillaOptionType.PUT.value), -1),
        ]

    def strip(self):
        return [
            (self.mid_option(VanillaOptionType.CALL.value), 1),
            (self.mid_option(VanillaOptionType.PUT.value), 1),
            (self.mid_option(VanillaOptionType.PUT.value), 1),
        ]

    def strap(self):
        return [
            (self.mid_option(VanillaOptionType.CALL.value), 1),
            (self.mid_option(VanillaOptionType.CALL.value), 1),
            (self.mid_option(VanillaOptionType.PUT.value), 1),
        ]
