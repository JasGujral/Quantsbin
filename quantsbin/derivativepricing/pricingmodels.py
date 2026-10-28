"""
developed by Quantsbin - Jun'18

"""

import copy
from abc import ABCMeta, abstractmethod
from math import e, log, sqrt
from typing import NamedTuple

import numpy as np
from scipy import optimize
from scipy.stats import norm

from ..montecarlo.namesnmapper import ProcessNames, StimulationType, mc_methd_mapper
from .helperfn import dividend_processor, parse_pricing_date, pv_div, require_spot, volatility_or_default
from .namesnmapper import ExpiryType, RiskParameter, UdlType, VanillaOptionType


class MCResult(NamedTuple):
    """Monte Carlo price with its standard error (of the mean) and the number of simulated paths."""

    price: float
    standard_error: float
    n_paths: int


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
        self.spot0 = require_spot(spot0)
        self.rf_rate = rf_rate or 0
        self.cnv_yield = cnv_yield or 0
        self.cost_yield = cost_yield or 0
        self.pv_cnv = pv_cnv or 0
        self.pv_cost = pv_cost or 0
        self.volatility = volatility_or_default(volatility)
        self._pricing_date = parse_pricing_date(pricing_date)

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

    IV_LOWER, IV_UPPER = 1e-4, 5.0

    def imply_volatility(self, premium):
        """Black-Scholes-type implied volatility by Brent's method on [0.01%, 500%].

        Raises ValueError if the premium is outside the no-arbitrage bounds of the model, or if
        it needs a volatility outside the search range. The model itself is not modified.
        """
        trial = copy.copy(self)
        forward_leg = trial.adj_spot0 * trial.adj_discount_factor  # S e^{-(q-c)T}
        strike_leg = trial.instrument.strike * trial.discount_factor  # K e^{-rT}
        if trial.option_flag == 1:
            lower, upper = max(forward_leg - strike_leg, 0.0), forward_leg
        else:
            lower, upper = max(strike_leg - forward_leg, 0.0), strike_leg
        if not lower < premium < upper:
            raise ValueError(
                f"premium {premium!r} is outside the no-arbitrage bounds ({lower:.6g}, {upper:.6g}) "
                "for this option; no implied volatility exists"
            )

        def objective_func(vol_guess):
            trial.volatility = vol_guess
            return trial.valuation() - premium

        f_low, f_high = objective_func(self.IV_LOWER), objective_func(self.IV_UPPER)
        if f_low > 0 or f_high < 0:
            raise ValueError(
                f"implied volatility for premium {premium!r} is outside the search range "
                f"[{self.IV_LOWER:.2%}, {self.IV_UPPER:.0%}]"
            )
        return optimize.brentq(objective_func, self.IV_LOWER, self.IV_UPPER, xtol=1e-12, maxiter=200)


class BSM(BSMFramework):
    """
    This is the Black Scholes Merton model. This model is for EqOption(Stocks)

    Discrete dividends (div_list) use the escrowed model (Black 1975; Hull): the spot is reduced by
    the present value of dividends paid before expiry and the volatility is applied unchanged (no
    sigma* adjustment). The Monte Carlo model instead drops the spot on each ex-date, so the two
    differ slightly when there are discrete dividends.
        Args required:
            instrument = Instrument parameters mapped from instrument module
            **market_kwargs = All the parameters from BSMFramework
            help(.derivativepricing.pricingmodels.BSMFramework)

    """

    def __init__(self, instrument, **market_kwargs):
        self._rf_rate = market_kwargs["rf_rate"]
        self._div_list = market_kwargs["div_list"]
        self._pricing_date = parse_pricing_date(market_kwargs.get("pricing_date"))
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
        if self.instrument.undl == UdlType.FX.value:
            risk_parameters.update({RiskParameter.RHO_FOREIGN.value: self.phi()})
        elif self.instrument.undl == UdlType.COMMODITY.value:
            risk_parameters.update({RiskParameter.RHO_CONV.value: self.phi()})
        return risk_parameters


class MonteCarloGBM(Model):
    """
    This is the Montecarlo Simulation(for Geometric Brownian motion) method for both European and
    American type of Options for all Asset classes. For American Type LSM method is used defined under this class

    Discrete dividends (div_list) use the spot-drop model: each path falls by the dividend amount at
    the first time step after the ex-date (step int(t_ex / dt) + 1, so up to one step late) and is
    lognormal in between. BSM and Binomial use the escrowed model instead.

    Greeks are bump-and-reprice with the same seed. For American options the gamma is noisy and
    biased, because the bumped runs fit slightly different exercise rules; use the Binomial model for
    American gamma. Use valuation_with_error() to see the Monte Carlo standard error.
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
        out_of_sample=False,
        **kwargs,
    ):
        self.instrument = instrument
        self.spot0 = require_spot(spot0)
        self.rf_rate = rf_rate or 0
        self.cnv_yield = cnv_yield or 0
        self.cost_yield = cost_yield or 0
        self.volatility = volatility_or_default(volatility)
        self._pricing_date = parse_pricing_date(pricing_date)
        self._no_of_path = no_of_path
        self.no_of_steps = no_of_steps or 100
        self.seed = 100 if seed is None else seed
        self.antithetic = antithetic
        self.method = mc_method or ProcessNames.GEOMETRICBROWNIANMOTION.value
        self.div_list = div_list
        self.out_of_sample = bool(out_of_sample)

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

    def stimulation_method(self, seed=None):
        obj_stimulation = mc_methd_mapper[self.method](
            self.spot0,
            self.maturity,
            drift=self.drift,
            volatility=self.volatility,
            div_list_processed=self.div_processed,
            stimulation_type=self.stimulation_type,
            no_of_path=self.no_of_path,
            no_of_steps=self.no_of_steps,
            seed=self.seed if seed is None else seed,
            antithetic=self.antithetic,
        )
        return obj_stimulation.stimulation()

    def option_payoff(self, stimulated_price):
        temp_zeros = np.zeros_like(stimulated_price)
        return np.maximum(self.option_flag * (stimulated_price - self.instrument.strike), temp_zeros)

    LSM_POLY_DEGREE = 4

    @property
    def out_of_sample_seed(self):
        """Seed for the independent pricing paths used when ``out_of_sample=True``."""
        return (int(self.seed) * 1_000_003 + 7) % 2**32

    def _lsm_backward_induction(self, s_stimulated):
        """Longstaff-Schwartz backward induction.

        Returns the per-date regression coefficients of the exercise rule and each path's
        cashflow discounted to the first exercise date (in-sample).
        """
        intrinsic = self.option_payoff(s_stimulated)
        option_value = np.zeros_like(intrinsic)
        option_value[:, -1] = intrinsic[:, -1]
        coefficients = {}

        for t in range(self.no_of_steps - 1, 0, -1):
            # Carry every path's cashflow back one step, whether or not any path is in the money.
            # (1.0.3 skipped this when no path was ITM, which zeroed the value at all earlier dates.)
            option_value[:, t] = option_value[:, t + 1] * self.step_disc_fact
            itm = intrinsic[:, t] > 0
            # The exercise decision needs enough ITM paths for a meaningful regression.
            if np.count_nonzero(itm) > self.LSM_POLY_DEGREE + 1:
                x_axis = s_stimulated[itm, t]
                y_axis = option_value[itm, t]
                coef = np.polynomial.laguerre.lagfit(x_axis, y_axis, self.LSM_POLY_DEGREE)
                continuation = np.polynomial.laguerre.lagval(x_axis, coef)
                coefficients[t] = coef
                option_value[itm, t] = np.where(intrinsic[itm, t] > continuation, intrinsic[itm, t], y_axis)

        return coefficients, intrinsic, option_value[:, 1]

    def _lsm_apply_rule(self, s_stimulated, coefficients):
        """Value fresh paths with a fixed exercise rule: exercise at the first date where the
        intrinsic value beats the fitted continuation value. Returns cashflows discounted to t0."""
        intrinsic = self.option_payoff(s_stimulated)
        df = self.step_disc_fact
        cashflow = intrinsic[:, -1] * df**self.no_of_steps
        alive = np.ones(intrinsic.shape[0], dtype=bool)
        for t in range(1, self.no_of_steps):
            coef = coefficients.get(t)
            if coef is None:
                continue
            itm = alive & (intrinsic[:, t] > 0)
            exercise = np.zeros_like(alive)
            exercise[itm] = intrinsic[itm, t] > np.polynomial.laguerre.lagval(s_stimulated[itm, t], coef)
            cashflow[exercise] = intrinsic[exercise, t] * df**t
            alive &= ~exercise
        return cashflow

    def LSM_model(self):
        """American option value by Longstaff-Schwartz least-squares Monte Carlo.

        Longstaff, F. and Schwartz, E. (2001), "Valuing American Options by Simulation:
        A Simple Least-Squares Approach", Review of Financial Studies 14(1), 113-147.

        With ``out_of_sample=False`` (default, 1.x behaviour) the exercise rule is fitted and
        the option priced on the same paths; this estimator is biased slightly high. With
        ``out_of_sample=True`` the rule is fitted on one set of paths and applied to an
        independent set (seed ``out_of_sample_seed``); this gives a low-biased estimate.
        """
        path_values, exercise_now = self._lsm_path_values()
        # An American option can also be exercised today: never price below intrinsic value.
        return max(np.mean(path_values), exercise_now)

    def _lsm_path_values(self):
        """Per-path discounted cashflows of the hold strategy, and the value of exercising today."""
        s_fit = self.stimulation_method()
        coefficients, intrinsic, cashflow_t1 = self._lsm_backward_induction(s_fit)
        if self.out_of_sample:
            path_values = self._lsm_apply_rule(self.stimulation_method(self.out_of_sample_seed), coefficients)
        else:
            path_values = cashflow_t1 * self.step_disc_fact
        return path_values, intrinsic[0, 0]

    def valuation(self):
        if self.instrument.expiry_type == ExpiryType.EUROPEAN.value:
            if self.div_list:
                return np.average(
                    self.option_payoff(self.stimulation_method()[:, -1]) * (e ** (-1 * self.rf_rate * self.maturity))
                )
            return np.average(self.option_payoff(self.stimulation_method()) * e ** (-1 * self.rf_rate * self.maturity))
        elif self.instrument.expiry_type == ExpiryType.AMERICAN.value:
            return self.LSM_model()

    def valuation_with_error(self):
        """Price, its Monte Carlo standard error, and the number of simulated paths.

        The price equals ``valuation()``. With antithetic sampling the error is computed from the
        averages of each antithetic pair. For American options, when exercising today beats the
        simulated hold value, the price is the intrinsic value and the reported error is 0.
        """
        if self.instrument.expiry_type == ExpiryType.AMERICAN.value:
            path_values, exercise_now = self._lsm_path_values()
        else:
            simulated = self.stimulation_method()
            final = simulated[:, -1] if self.div_list else simulated
            path_values = (self.option_payoff(final) * e ** (-1 * self.rf_rate * self.maturity)).ravel()
            exercise_now = None

        n_paths = len(path_values)
        samples = path_values
        if self.antithetic:
            half = n_paths // 2
            samples = 0.5 * (path_values[:half] + path_values[half:])
        price = float(np.mean(path_values))
        standard_error = float(np.std(samples, ddof=1) / np.sqrt(len(samples)))
        if exercise_now is not None and exercise_now > price:
            return MCResult(float(exercise_now), 0.0, n_paths)
        return MCResult(price, standard_error, n_paths)

    def risk_parameters(self):
        return None


class BinomialModel(Model):
    """
    This is the generalised Binomial model used for valuation calculation for both European and American type

    Cox-Ross-Rubinstein tree. Discrete dividends (div_list) use the escrowed approach of Hull and
    Schroder (1988): the tree is built on S - PV(dividends) and the PV of the remaining dividends is
    added back at each node; the volatility is applied unchanged (no sigma* adjustment).
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
        self.spot0 = require_spot(spot0)
        self.rf_rate = rf_rate or 0
        self.cnv_yield = cnv_yield or 0
        self.cost_yield = cost_yield or 0
        self.volatility = volatility_or_default(volatility)
        self._pricing_date = parse_pricing_date(pricing_date)
        self.no_of_steps = no_of_steps or 100
        self.div_list = div_list

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

    def _spots_at_step(self, step_no):
        """Stock prices at every node of a step: the CRR tree on S - PV(dividends) plus the PV of the
        dividends still to be paid (escrowed dividends; Hull, Schroder 1988)."""
        no_up = np.arange(step_no + 1)
        return self.spot_update * (self.up_mult ** (2 * no_up - step_no)) + pv_div(
            self.div_processed, self.t_delta * step_no, self.rf_rate
        )

    def _intrinsic_at_step(self, step_no):
        return np.maximum(self.option_flag * (self._spots_at_step(step_no) - self.instrument.strike), 0.0)

    def valuation(self):
        """Backward induction over the recombining tree.

        Iterative replacement of the 1.0.3 recursive version (same tree, same results), which hit
        Python's recursion limit above about 1,000 steps and kept a node cache that was shared by
        shallow copies of the model.
        """
        american = self.instrument.expiry_type == ExpiryType.AMERICAN.value
        p, df = self.up_prob, self.step_discount_fact
        values = self._intrinsic_at_step(self.no_of_steps)  # index = number of up moves
        for step_no in range(self.no_of_steps - 1, -1, -1):
            values = (p * values[1:] + (1 - p) * values[:-1]) * df
            if american:
                values = np.maximum(values, self._intrinsic_at_step(step_no))
        return float(values[0])

    def risk_parameters(self):
        pass
