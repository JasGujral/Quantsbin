"""
    developed by Quantsbin - Jun'18

"""

from enum import Enum


class AssetClass(Enum):
    EQOPTION = 'EqOption'
    FXOPTION = 'FXOption'
    FUTOPTION = 'FutOption'
    COMOPTION = 'ComOption'


class DerivativeType(Enum):
    VANILLA_OPTION = 'Vanilla Option'


class PricingModel(Enum):
    BLACKSCHOLESMERTON = 'BSM'
    BLACK76 = 'B76'
    GK = 'GK'
    MC_GBM = "MC_GBM"
    MC_GBM_LSM = "MC_GBM_LSM"
    BINOMIAL = "Binomial"
    TRINOMIAL = "Trinomial"

class UnderlyingParameters(Enum):
    SPOT = "spot0"
    VOLATILITY = "volatility"
    PRICEDATE = "_pricing_date"
    RF_RATE = "rf_rate"
    CNV_YIELD = "cnv_yield"
    COST_YIELD = "cost_yield"
    UNEXPLAINED = "unexplained"


class RiskParameter(Enum):
    DELTA = 'delta'
    GAMMA = 'gamma'
    THETA = 'theta'
    VEGA = 'vega'
    RHO = 'rho'
    PHI = 'phi'
    RHO_FOREIGN = 'rho_foreign'
    RHO_CONV = 'rho_conv_yield'


class VanillaOptionType(Enum):
    CALL = 'Call'
    PUT = 'Put'


class ExpiryType(Enum):
    AMERICAN = 'American'
    EUROPEAN = 'European'


class UdlType(Enum):
    INDEX = 'Index'
    STOCK = 'Stock'
    FX = 'Currency'
    COMMODITY = 'Commodity'
    FUTURES = 'Futures'


class DivType(Enum):
    DISCRETE = 'Discrete'
    YIELD = 'Yield'


OBJECT_MODEL = {
    UdlType.STOCK.value: {ExpiryType.EUROPEAN.value: [PricingModel.BLACKSCHOLESMERTON.value, PricingModel.MC_GBM.value
                          , PricingModel.BINOMIAL.value, PricingModel.TRINOMIAL.value],
                          ExpiryType.AMERICAN.value: [PricingModel.MC_GBM.value, PricingModel.BINOMIAL.value, PricingModel.TRINOMIAL.value]}
    , UdlType.FUTURES.value: {ExpiryType.EUROPEAN.value: [PricingModel.BLACK76.value, PricingModel.MC_GBM.value
                              , PricingModel.BINOMIAL.value, PricingModel.TRINOMIAL.value],
                              ExpiryType.AMERICAN.value:  [PricingModel.MC_GBM.value, PricingModel.BINOMIAL.value, PricingModel.TRINOMIAL.value]}
    , UdlType.FX.value:  {ExpiryType.EUROPEAN.value: [PricingModel.GK.value, PricingModel.MC_GBM.value
                          , PricingModel.BINOMIAL.value, PricingModel.TRINOMIAL.value],
                          ExpiryType.AMERICAN.value:  [PricingModel.MC_GBM.value, PricingModel.BINOMIAL.value, PricingModel.TRINOMIAL.value]}
    , UdlType.COMMODITY.value: {ExpiryType.EUROPEAN.value: [PricingModel.GK.value, PricingModel.MC_GBM.value
                                , PricingModel.BINOMIAL.value, PricingModel.TRINOMIAL.value],
                                ExpiryType.AMERICAN.value: [PricingModel.MC_GBM.value, PricingModel.BINOMIAL.value, PricingModel.TRINOMIAL.value]}
    }

DEFAULT_MODEL = {
    UdlType.STOCK.value:
        {DerivativeType.VANILLA_OPTION.value: {ExpiryType.EUROPEAN.value: PricingModel.BLACKSCHOLESMERTON.value,
                                               ExpiryType.AMERICAN.value: PricingModel.BINOMIAL.value},
         },
    UdlType.FUTURES.value:
        {DerivativeType.VANILLA_OPTION.value: {ExpiryType.EUROPEAN.value: PricingModel.BLACK76.value,
                                               ExpiryType.AMERICAN.value: PricingModel.BINOMIAL.value},
         },
    UdlType.FX.value:
        {DerivativeType.VANILLA_OPTION.value: {ExpiryType.EUROPEAN.value: PricingModel.GK.value,
                                               ExpiryType.AMERICAN.value: PricingModel.BINOMIAL.value},
         },
    UdlType.COMMODITY.value:
        {DerivativeType.VANILLA_OPTION.value: {ExpiryType.EUROPEAN.value: PricingModel.GK.value,
                                               ExpiryType.AMERICAN.value: PricingModel.BINOMIAL.value},
         }
    }

IV_MODELS = [PricingModel.BLACKSCHOLESMERTON.value, PricingModel.BLACK76.value, PricingModel.GK.value]

ANALYTICAL_GREEKS = [PricingModel.BLACKSCHOLESMERTON.value, PricingModel.BLACK76.value, PricingModel.GK.value]

from . import pricingmodels as pm

MODEL_MAPPER = {
    PricingModel.BLACKSCHOLESMERTON.value: pm.BSM,
    PricingModel.BLACK76.value: pm.B76,
    PricingModel.GK.value: pm.GK,
    PricingModel.MC_GBM.value: pm.MonteCarloGBM,
    PricingModel.BINOMIAL.value: pm.BinomialModel,
    PricingModel.TRINOMIAL.value: pm.TrinomialModel
    }
