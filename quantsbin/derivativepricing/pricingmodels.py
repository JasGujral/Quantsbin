"""
developed by Quantsbin - Jun'18

"""

from abc import ABCMeta, abstractmethod
from datetime import datetime as dt
from math import e, log, sqrt

import numpy as np
from scipy import optimize
from scipy.stats import norm

from ..montecarlo.namesnmapper import ProcessNames, StimulationType, mc_methd_mapper
from .helperfn import dividend_processor, pv_div
from .namesnmapper import ExpiryType, RiskParameter, UdlType, VanillaOptionType


class Model(metaclass=ABCMeta):
    """
    Basic model class defined with properties required for all the pricing models for any type of Asset class

    """

    @abstractmethod
    def valuation(self):
        pass

    @abstractmethod
    def risk_parameters(self):
        pass

    @property
    def _cnv_yield(self):
        if self.instrument.undl == UdlType.FUTURES.value:
            return self.rf_rate
        else:
            return self.cnv_yield

    @property
    def pricing_date(self):
        if self._pricing_date < self.instrument.expiry_date:
            return self._pricing_date
        else:
            raise Exception("Pricing date should be less than expiry of instrument")

    @property
    def maturity(self):
        return (self.instrument.expiry_date - self.pricing_date).days / 365.0

    @property
    def option_flag(self):
        if self.instrument.option_type == VanillaOptionType.CALL.value:
            return 1
        elif self.instrument.option_type == VanillaOptionType.PUT.value:
            return -1


class BSMFramework(Model):
    """
    This is the base class for the Black Scholes Merton, Black76 and GK models
        Args required:
        instrument = Instrument parameters mapped from instrument module
        spot0 = (Float) e.g. 110.0
        rf_rate = (Float < 1) e.g. 0.2
        _cnv_yield = (Float < 1) e.g. 0.3
        cost_yield = (Float < 1) e.g. 0.2
        pv_cnv = (Float) e.g. 1.2
        pv_cost = (Float) e.g. 3.2
        volatility = (Float < 1) e.g. 0.25
        pricing_date = (Date in string format "YYYYMMDD") e.g. 10 Dec 2018 as "20181210"
    """

    def __init__(
        self,
        instrument,
        spot0=None,
        rf_rate=0,
        cnv_yield=0,
        cost_yield=0,
        pv_cnv=0,
        pv_cost=0,
        volatility=None,
        pricing_date=None,
        **kwargs,
    ):
        self.instrument = instrument
        self.spot0 = spot0 or 0.00001
        self.rf_rate = rf_rate or 0
        self.cnv_yield = cnv_yield or 0
        self.cost_yield = cost_yield or 0
        self.pv_cnv = pv_cnv or 0
        self.pv_cost = pv_cost or 0
        self.volatility = volatility or 0.10
        self._pricing_date = dt.strptime(pricing_date, "%Y%m%d")

    @property
    def adj_spot0(self):
        return self.spot0 + self.pv_cost - self.pv_cnv

    @property
    def d1(self):
        return (
            log(self.adj_spot0 / self.instrument.strike)
            + (self.rf_rate - self._cnv_yield + self.cost_yield + 0.5 * (self.volatility**2)) * self.maturity
        ) / (self.volatility * sqrt(self.maturity))

    @property
    def d2(self):
        return self.d1 - self.volatility * sqrt(self.maturity)

    @property
    def discount_factor(self):
        return e ** (-1 * self.rf_rate * self.maturity)

    @property
    def adj_discount_factor(self):
        return e ** (-1 * (self._cnv_yield - self.cost_yield) * self.maturity)

    @property
    def option_flag(self):
        if self.instrument.option_type == VanillaOptionType.CALL.value:
            return 1
        elif self.instrument.option_type == VanillaOptionType.PUT.value:
            return -1

    def valuation(self):
        return self.option_flag * (
            self.adj_spot0 * self.adj_discount_factor * norm.cdf(self.option_flag * self.d1)
        ) - self.option_flag * (self.instrument.strike * self.discount_factor * norm.cdf(self.option_flag * self.d2))

    #   greeks defined
    def delta(self):
        """dV/dS = flag * exp(-(q - c) T) * N(flag * d1)."""
        return self.option_flag * self.adj_discount_factor * norm.cdf(self.option_flag * self.d1)

    def gamma(self):
        return (norm.pdf(self.d1) * self.adj_discount_factor) / (self.adj_spot0 * self.volatility * sqrt(self.maturity))

    def vega(self):
        return (self.adj_spot0 * self.adj_discount_factor * sqrt(self.maturity)) * norm.pdf(self.d1)

    def rho(self):
        return self.option_flag * (
            self.instrument.strike * self.maturity * self.discount_factor * norm.cdf(self.option_flag * self.d2)
        )

    def phi(self):
        """dV/dq = -flag * S * T * exp(-(q - c) T) * N(flag * d1)."""
        return (
            -1
            * self.option_flag
            * self.adj_spot0
            * self.maturity
            * self.adj_discount_factor
            * norm.cdf(self.option_flag * self.d1)
        )

    def rho_fut(self):
        return -1 * self.maturity * self.valuation()

    def theta(self):
        return (
            (
                -1
                * norm.pdf(self.d1)
                * self.volatility
                * self.adj_discount_factor
                * self.adj_spot0
                / (2 * sqrt(self.maturity))
            )
            + (
                self.option_flag
                * (self._cnv_yield - self.cost_yield)
                * self.adj_spot0
                * norm.cdf(self.option_flag * self.d1)
                * self.adj_discount_factor
            )
            - (
                self.option_flag
                * self.rf_rate
                * self.instrument.strike
                * self.discount_factor
                * norm.cdf(self.option_flag * self.d2)
            )
        ) / 365

    @abstractmethod
    def risk_parameters(self):
        pass

    def risk_parameters_func(self):
        return {
            RiskParameter.DELTA.value: self.delta,
            RiskParameter.GAMMA.value: self.gamma,
            RiskParameter.THETA.value: self.theta,
            RiskParameter.VEGA.value: self.vega,
            RiskParameter.RHO.value: self.rho,
        }

    def imply_volatility(self, premium):
        def objective_func(vol_guess):
            self.volatility = vol_guess
            val = self.valuation()
            return val - premium

        try:
            return optimize.bisect(objective_func, a=0.001, b=0.999, xtol=0.00005)
        except ValueError:
            raise ValueError("Unable to converge to implied volatility")


class BSM(BSMFramework):
    """
    This is the Black Scholes Merton model. This model is for EqOption(Stocks)
        Args required:
            instrument = Instrument parameters mapped from instrument module
            **market_kwargs = All the parameters from BSMFramework
            help(.derivativepricing.pricingmodels.BSMFramework)

    """

    def __init__(self, instrument, **market_kwargs):
        self._rf_rate = market_kwargs["rf_rate"]
        self._div_list = market_kwargs["div_list"]
        self._pricing_date = dt.strptime(market_kwargs["pricing_date"], "%Y%m%d")
        self._instrument = instrument
        market_kwargs["pv_cnv"] = self.pv_div()
        super().__init__(instrument, **market_kwargs)

    def pv_div(self):
        if self._div_list:
            _div_processed = dividend_processor(self._div_list, self._pricing_date, self._instrument.expiry_date)
            return pv_div(_div_processed, 0, self._rf_rate)
        else:
            return 0

    def risk_parameters(self):
        return {
            RiskParameter.DELTA.value: self.delta(),
            RiskParameter.GAMMA.value: self.gamma(),
            RiskParameter.THETA.value: self.theta(),
            RiskParameter.VEGA.value: self.vega(),
            RiskParameter.RHO.value: self.rho(),
            RiskParameter.PHI.value: self.phi(),
        }


class B76(BSMFramework):
    """
    This is the Black76. This model is for FutOption(Futures)
        Args required:
            instrument = Instrument parameters mapped from instrument module
            **market_kwargs = All the parameters from BSMFramework
            help(.derivativepricing.pricingmodels.BSMFramework)

    """

    def __init__(self, instrument, **market_kwargs):
        super().__init__(instrument, **market_kwargs)

    def risk_parameters(self):
        risk_parameters = {
            RiskParameter.DELTA.value: self.delta(),
            RiskParameter.GAMMA.value: self.gamma(),
            RiskParameter.THETA.value: self.theta(),
            RiskParameter.VEGA.value: self.vega(),
            RiskParameter.RHO.value: self.rho_fut(),
        }
        return risk_parameters


class GK(BSMFramework):
    """
    This is the Garman Kohlhagen model. This model is for FxOption and ComOption(Fx Rates and Commodities)
        Args required:
            instrument = Instrument parameters mapped from instrument module
            **market_kwargs = All the parameters from BSMFramework
            help(.derivativepricing.pricingmodels.BSMFramework)

    """

    def __init__(self, instrument, **market_kwargs):
        self.instrument = instrument
        super().__init__(instrument, **market_kwargs)

    def risk_parameters(self):
        risk_parameters = {
            RiskParameter.DELTA.value: self.delta(),
            RiskParameter.GAMMA.value: self.gamma(),
            RiskParameter.THETA.value: self.theta(),
            RiskParameter.VEGA.value: self.vega(),
            RiskParameter.RHO.value: self.rho(),
        }
        if self.instrument.undl == UdlType.FX:
            risk_parameters.update({RiskParameter.RHO_FOREIGN.value: self.phi()})
        elif self.instrument.undl == UdlType.COMMODITY:
            risk_parameters.update({RiskParameter.RHO_CONV.value: self.phi()})
        return risk_parameters


class MonteCarloGBM(Model):
    """
    This is the Montecarlo Simulation(for Geometric Brownian motion) method for both European and
    American type of Options for all Asset classes. For American Type LSM method is used defined under this class
        Args required:
        instrument = Instrument parameters mapped from instrument module
        spot0 = (Float) e.g. 110.0
        rf_rate = (Float < 1) e.g. 0.2
        cnv_yield = (Float < 1) e.g. 0.3
        cost_yield = (Float < 1) e.g. 0.2
        volatility = (Float < 1) e.g. 0.25
        pricing_date = (Date in string format "YYYYMMDD") e.g. 10 Dec 2018 as "20181210"
        no_of_path = (Integer). Number of paths to be generated for simulation e.g. 10000
        no_of_steps = (Integer). Number of steps (nodes) for the premium calculation e.g. 100
        seed = (Integer). Used for seeding
        antithetic = (Boolean). A process in Montecarlo Simulation. Default False
        method = (String). Type of Simulation e.g. GBM
        div_list = (List). list of tuples with Ex-Dates and Dividend amounts. e.g. [('20180625',0.2),('20180727',0.6)]

    """

    def __init__(
        self,
        instrument,
        spot0=None,
        rf_rate=0,
        cnv_yield=0,
        cost_yield=0,
        volatility=None,
        pricing_date=None,
        no_of_path=None,
        no_of_steps=None,
        mc_method=None,
        seed=None,
        antithetic=False,
        div_list=None,
        **kwargs,
    ):
        self.instrument = instrument
        self.spot0 = spot0 or 0.0001
        self.rf_rate = rf_rate or 0
        self.cnv_yield = cnv_yield or 0
        self.cost_yield = cost_yield or 0
        self.volatility = volatility or 0.10
        self._pricing_date = dt.strptime(pricing_date, "%Y%m%d")
        self._no_of_path = no_of_path
        self.no_of_steps = no_of_steps or 100
        self.seed = seed or 100
        self.antithetic = antithetic
        self.method = mc_method or ProcessNames.GEOMETRICBROWNIANMOTION.value
        self.div_list = div_list

    @property
    def div_processed(self):
        return dividend_processor(self.div_list, self._pricing_date, self.instrument.expiry_date)

    @property
    def drift(self):
        return self.rf_rate + self.cost_yield - self._cnv_yield

    @property
    def no_of_path(self):
        if self._no_of_path:
            return self._no_of_path
        else:
            if self.instrument.expiry_type == ExpiryType.EUROPEAN.value:
                if self.div_list:
                    return 10000
                return 1000000
            elif self.instrument.expiry_type == ExpiryType.AMERICAN.value:
                return 10000

    @property
    def stimulation_type(self):
        if self.instrument.expiry_type == ExpiryType.EUROPEAN.value:
            if self.div_list:
                return StimulationType.FULLPATH.value
            else:
                return StimulationType.FINALVALUE.value
        elif self.instrument.expiry_type == ExpiryType.AMERICAN.value:
            return StimulationType.FULLPATH.value

    @property
    def delta_t(self):
        return self.maturity / self.no_of_steps

    @property
    def step_disc_fact(self):
        return e ** (-self.rf_rate * self.maturity / self.no_of_steps)

    def stimulation_method(self):
        obj_stimulation = mc_methd_mapper[self.method](
            self.spot0,
            self.maturity,
            drift=self.drift,
            volatility=self.volatility,
            div_list_processed=self.div_processed,
            stimulation_type=self.stimulation_type,
            no_of_path=self.no_of_path,
            no_of_steps=self.no_of_steps,
            seed=self.seed,
            antithetic=self.antithetic,
        )
        return obj_stimulation.stimulation()

    def option_payoff(self, stimulated_price):
        temp_zeros = np.zeros_like(stimulated_price)
        return np.maximum(self.option_flag * (stimulated_price - self.instrument.strike), temp_zeros)

    def LSM_model(self):
        _s_stimulated = self.stimulation_method()
        _intrinsic_val = self.option_payoff(_s_stimulated)
        _option_value = np.zeros_like(_intrinsic_val)
        _option_value[:, -1] = _intrinsic_val[:, -1]

        for t in range(self.no_of_steps - 1, 0, -1):
            if len(_s_stimulated[_intrinsic_val[:, t] > 0, t]) == 0:
                continue
            else:
                _ITM_check = _intrinsic_val[:, t] > 0
                _x_axis = _s_stimulated[_ITM_check, t]
                _y_axis = _option_value[_ITM_check, t + 1] * self.step_disc_fact
                _option_value[:, t] = _option_value[:, t + 1] * self.step_disc_fact
                laguerre_poly_degree = 4
                laguerre_poly_4 = np.polynomial.laguerre.lagfit(_x_axis, _y_axis, laguerre_poly_degree)
                _cond_pv = np.polynomial.laguerre.lagval(_x_axis, laguerre_poly_4)

                _option_value[_ITM_check, t] = np.where(
                    _intrinsic_val[_ITM_check, t] > _cond_pv.transpose(), _intrinsic_val[_ITM_check, t], _y_axis
                )

        _option_value[:, 0] = _option_value[:, 1] * self.step_disc_fact
        return np.mean(_option_value[:, 0])

    def valuation(self):
        if self.instrument.expiry_type == ExpiryType.EUROPEAN.value:
            if self.div_list:
                return np.average(
                    self.option_payoff(self.stimulation_method()[:, -1]) * (e ** (-1 * self.rf_rate * self.maturity))
                )
            return np.average(self.option_payoff(self.stimulation_method()) * e ** (-1 * self.rf_rate * self.maturity))
        elif self.instrument.expiry_type == ExpiryType.AMERICAN.value:
            return self.LSM_model()

    def risk_parameters(self):
        return None


class BinomialModel(Model):
    """
    This is the generalised Binomial model used for valuation calculation for both European and American type
        Args required:
        instrument = Instrument parameters mapped from instrument module
        spot0 = (Float) e.g. 110.0
        rf_rate = (Float < 1) e.g. 0.2
        cnv_yield = (Float < 1) e.g. 0.3
        cost_yield = (Float < 1) e.g. 0.2
        volatility = (Float < 1) e.g. 0.25
        pricing_date = (Date in string format "YYYYMMDD") e.g. 10 Dec 2018 as "20181210"
            no_of_steps = (Integer). Number of steps (nodes) for the premium calculation e.g. 100
        div_list = (List). list of tuples with Ex-Dates and Dividend amounts. e.g. [('20180625',0.2),('20180727',0.6)]

    """

    def __init__(
        self,
        instrument,
        spot0=None,
        rf_rate=0,
        cnv_yield=0,
        cost_yield=0,
        volatility=None,
        pricing_date=None,
        no_of_steps=None,
        div_list=None,
        **kwargs,
    ):
        self.instrument = instrument
        self.spot0 = spot0 or 0.0001
        self.rf_rate = rf_rate or 0
        self.cnv_yield = cnv_yield or 0
        self.cost_yield = cost_yield or 0
        self.volatility = volatility or 0.10
        self._pricing_date = dt.strptime(pricing_date, "%Y%m%d")
        self.no_of_steps = no_of_steps or 100
        self.div_list = div_list
        self.cache_node = {}

    @property
    def drift(self):
        return self.rf_rate + self.cost_yield - self._cnv_yield

    @property
    def div_processed(self):
        return dividend_processor(self.div_list, self._pricing_date, self.instrument.expiry_date)

    @property
    def spot_update(self):
        return self.spot0 - pv_div(self.div_processed, 0, self.rf_rate)

    @property
    def t_delta(self):
        return self.maturity / self.no_of_steps

    @property
    def up_mult(self):
        return e ** (self.volatility * (self.t_delta**0.5))

    @property
    def up_prob(self):
        return (e ** (self.drift * self.t_delta) - (1 / self.up_mult)) / (self.up_mult - (1 / self.up_mult))

    @property
    def step_discount_fact(self):
        return e ** (-1 * self.rf_rate * self.t_delta)

    def node_value_store(self, pv, intrinsic_value):
        if self.instrument.expiry_type == ExpiryType.AMERICAN.value:
            return max(pv, intrinsic_value)
        else:
            return pv

    def intrinsic_value(self, _spot):
        return max(self.option_flag * (_spot - self.instrument.strike), 0.0)

    def calc_spot(self, step_no, no_up):
        return self.spot_update * (self.up_mult ** (2 * no_up - step_no)) + pv_div(
            self.div_processed, self.t_delta * step_no, self.rf_rate
        )

    def node_value(self, step_no, no_up):
        cache_node_key = (step_no, no_up)
        if cache_node_key in self.cache_node:
            return self.cache_node[cache_node_key]
        else:
            _spot = self.calc_spot(step_no, no_up)
            _intrinsic_value = self.intrinsic_value(_spot)

            if step_no >= self.no_of_steps:
                return _intrinsic_value
            else:
                _pv = (
                    (self.up_prob * self.node_value(step_no + 1, no_up + 1))
                    + ((1 - self.up_prob) * self.node_value(step_no + 1, no_up))
                ) * self.step_discount_fact
                _node_value = self.node_value_store(_pv, _intrinsic_value)
                self.cache_node[cache_node_key] = _node_value
                return self.cache_node[cache_node_key]

    def valuation(self):
        return self.node_value(0, 0)

    def risk_parameters(self):
        pass
