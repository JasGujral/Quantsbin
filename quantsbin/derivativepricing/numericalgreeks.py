"""
developed by Quantsbin - Jun'18

"""

import copy

import pandas as pd

from .namesnmapper import RiskParameter, UnderlyingParameters


class NumericalGreeks:
    """
    Numerical greeks are calculated. It is mapped with engineconfig module for calculation of valuation
    and riskparameters
        Args required:
        Bumps are relative to the current value (0.02 = 2%); a zero base value is bumped by the
        absolute amount instead. Defaults apply to any bump that is not given.
        delta_spot = (Float < 1). Relative change in spot, default 0.02
        delta_vol = (Float < 1). Relative change in volatility, default 0.02
        delta_rf_rate = (Float < 1). Relative change in risk free rate, default 0.02
        delta_time = (Integer). Number of days to change in pricing date e.g. 2
        delta_conv_yield = (Float < 1). Change in conv_yield e.g. 0.2
        delta_cost_yield = (Float < 1). Change in cost yield e.g. 0.2
    """

    def __init__(
        self,
        model_class,
        delta_spot=0.02,
        delta_vol=0.02,
        delta_rf_rate=0.02,
        delta_time=1,
        delta_conv_yield=0,
        delta_cost_yield=0,
        **kwargs,
    ):
        self.model = model_class
        self._model = copy.deepcopy(self.model)
        self.delta_spot = delta_spot or 0
        self.delta_vol = delta_vol or 0
        self.delta_rf_rate = delta_rf_rate or 0
        self.delta_time = delta_time or 0
        self.delta_conv_yield = delta_conv_yield or 0
        self.delta_cost_yield = delta_cost_yield or 0

    @staticmethod
    def _bump_size(base, change):
        """Absolute bump for a relative ``change``.

        Bumps are relative (base * change). When the base value is 0 (e.g. a zero interest rate)
        a relative bump never moves it, so ``change`` is applied as an absolute amount instead.
        """
        return abs(base) * change if base != 0 else change

    def _bumped_pair(self, var, change):
        base = getattr(self._model, var)
        h = self._bump_size(base, change)
        up_model = copy.deepcopy(self._model)
        setattr(up_model, var, base + h)
        down_model = copy.deepcopy(self._model)
        setattr(down_model, var, base - h)
        return up_model, down_model, h

    def degree_one(self, var, change):
        if var == UnderlyingParameters.PRICEDATE.value:
            up_model = copy.deepcopy(self._model)
            setattr(up_model, var, getattr(self._model, var) + pd.Timedelta(change, unit="D"))
            return (up_model.valuation() - self.model.valuation()) / change
        up_model, down_model, h = self._bumped_pair(var, change)
        return (up_model.valuation() - down_model.valuation()) / (2 * h)

    def degree_two(self, var, change):
        up_model, down_model, h = self._bumped_pair(var, change)
        return (up_model.valuation() - 2 * self.model.valuation() + down_model.valuation()) / h**2

    def delta(self):
        return self.degree_one(UnderlyingParameters.SPOT.value, self.delta_spot)

    def gamma(self):
        return self.degree_two(UnderlyingParameters.SPOT.value, self.delta_spot)

    def theta(self):
        return self.degree_one(UnderlyingParameters.PRICEDATE.value, self.delta_time)

    def vega(self):
        return self.degree_one(UnderlyingParameters.VOLATILITY.value, self.delta_vol)

    def rho(self):
        return self.degree_one(UnderlyingParameters.RF_RATE.value, self.delta_rf_rate)

    def risk_parameters_num(self):
        return {
            RiskParameter.DELTA.value: self.delta(),
            RiskParameter.GAMMA.value: self.gamma(),
            RiskParameter.THETA.value: self.theta(),
            RiskParameter.VEGA.value: self.vega(),
            RiskParameter.RHO.value: self.rho(),
        }

    def risk_parameters_num_func(self):
        return {
            RiskParameter.DELTA.value: self.delta,
            RiskParameter.GAMMA.value: self.gamma,
            RiskParameter.THETA.value: self.theta,
            RiskParameter.VEGA.value: self.vega,
            RiskParameter.RHO.value: self.rho,
        }

    def pnl(self, var, change):
        if change == 0:
            return 0
        up_model = copy.copy(self.model)
        if var == UnderlyingParameters.PRICEDATE.value:
            setattr(up_model, var, getattr(self.model, var) + pd.Timedelta(change, unit="D"))
        else:
            setattr(up_model, var, getattr(self.model, var) * (1 + change))
        return up_model.valuation() - self.model.valuation()

    def pnl_attribution(self):
        return {
            UnderlyingParameters.SPOT.value: self.pnl(UnderlyingParameters.SPOT.value, self.delta_spot),
            UnderlyingParameters.PRICEDATE.value: self.pnl(UnderlyingParameters.PRICEDATE.value, self.delta_time),
            UnderlyingParameters.VOLATILITY.value: self.pnl(UnderlyingParameters.VOLATILITY.value, self.delta_vol),
            UnderlyingParameters.RF_RATE.value: self.pnl(UnderlyingParameters.RF_RATE.value, self.delta_rf_rate),
            UnderlyingParameters.CNV_YIELD.value: self.pnl(UnderlyingParameters.CNV_YIELD.value, self.delta_conv_yield),
            UnderlyingParameters.COST_YIELD.value: self.pnl(
                UnderlyingParameters.COST_YIELD.value, self.delta_cost_yield
            ),
        }
