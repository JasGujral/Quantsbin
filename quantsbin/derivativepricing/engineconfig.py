"""
    developed by Quantsbin - Jun'18

"""

from .namesnmapper import ANALYTICAL_GREEKS, IV_MODELS, MODEL_MAPPER, OBJECT_MODEL
from .numericalgreeks import NumericalGreeks


class PricingEngine:
    """
        Maps engine from instrument to model class.
    """

    def __init__(self, instrument, model, **kwargs):
        self.instrument = instrument
        self._model = model
        self._other_args = kwargs
        self.check_model = self.model_check()

    @property
    def _model_class(self):
        """
        Maps pricing model class according to the type of Instrument
            Args required:
                model: pricing model given as argument or the default value(default value set to BSM for European expiry)
                **kwargs: Dictionary of parameters and their corresponding value required for valuation
        """
        return MODEL_MAPPER[self._model](self.instrument, **self._other_args)

    def model_check(self):
        """
        Asserts pricing model mapped to the Instrument in the "namesmapper" and raises assertion error if not
            Args required:
                self.model: property defined in engineconfig module under Pricing Engine class
        """
        assert self._model in OBJECT_MODEL[self.instrument.undl][self.instrument.expiry_type], \
            "Model not valid please check available models using option.list_models()"
        return True

    def valuation(self):
        """
        Maps to the valuation method defined under required pricing model class
            Args required:
                **kwargs: Dictionary of parameters and their corresponding value required for valuation.
                For arguments required and method available for each model check\
                help(.derivativepricing.pricingmodels.<model name>)
        """
        return self._model_class.valuation()

    def risk_parameters(self, delta_spot=None, delta_vol=None, delta_rf_rate=None,
                            delta_time=None, delta_rf_conv=None, delta_cost_yield=None, **kwargs):
        """
        Maps to the riskparameters method defined under required pricing model class
        For American type of options only numerical greeks are calculated
            Args required:
                **kwargs: Dictionary of parameters and their corresponding value required for risk_parameters.
                For arguments required and method available for each model check\
                help(.derivativepricing.pricingmodels.<model name>)
        """
        if self._model in ANALYTICAL_GREEKS:
            return self._model_class.risk_parameters()
        else:
            return self.risk_parameters_num(delta_spot=delta_spot, delta_vol=delta_vol
                                            , delta_rf_rate=delta_rf_rate, delta_time=delta_time
                                            , delta_rf_conv=delta_rf_conv, delta_cost_yield=delta_cost_yield, **kwargs)

    def risk_parameters_num(self, delta_spot=None, delta_vol=None, delta_rf_rate=None,
                            delta_time=None, delta_rf_conv=None, delta_cost_yield=None, **kwargs):
        """
        Maps to the risk_parameters_num method defined in numericalgreeks module.
            Args required:
                **kwargs: Dictionary of parameters and their corresponding value required for risk_parameters_num.
                For arguments required and method available for each model check\
                help(.numericalgreeks.NumericalGreeks)
        """
        ng = NumericalGreeks(self._model_class, delta_spot, delta_vol, delta_rf_rate,
                             delta_time, delta_rf_conv, delta_cost_yield, **kwargs)
        return ng.risk_parameters_num()

    def risk_parameters_num_func(self):
        ng = NumericalGreeks(self._model_class)
        return ng.risk_parameters_num_func()

    def pnl_attribution(self, delta_spot=None, delta_vol=None, delta_rf_rate=None,
                        delta_time=None, delta_rf_conv=None, delta_rf_foreign=None,**kwargs):
        """
        Maps to the pnl_attribution method defined in numericalgreeks module.
            Args required:
                **kwargs: Dictionary of parameters and their corresponding value required for pnl_attribution.
                For arguments required and method available for each model check\
                help(.numericalgreeks.NumericalGreeks)
        """
        ng = NumericalGreeks(self._model_class, delta_spot, delta_vol, delta_rf_rate,
                             delta_time, delta_rf_conv, delta_rf_foreign,**kwargs)
        return ng.pnl_attribution()

    def risk_parameters_func(self):
        if self._model in ANALYTICAL_GREEKS:
            return self._model_class.risk_parameters_func()
        else:
            return self.risk_parameters_num_func()

    def imply_volatility(self, premium):
        """
        Maps to the imply_volatility method defined in pricingmodels module under required model class.
            Args required:
                **kwargs: Dictionary of parameters and their corresponding value required for valuation.
                For the implied volatility calculation in addition to the **kwargs premium is also taken as input
                For arguments required and method available for each model check\
                help(.derivativepricing.pricingmodels.<model name>)
        """
        if self._model in IV_MODELS:
            return self._model_class.imply_volatility(premium)
        else:
            raise NameError("implied volatility method not defined for " + self._model + " model")
