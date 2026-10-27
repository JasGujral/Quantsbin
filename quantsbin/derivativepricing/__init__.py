"""
    developed by Quantsbin - Jun'18

"""

from .instruments import ComOption, EqOption, FutOption, FXOption
from .optionstrategies import OptionStr1Udl, StdStrategies
from .plotting import Plotting

__all__ = ["ComOption", "EqOption", "FXOption", "FutOption", "OptionStr1Udl", "Plotting", "StdStrategies"]
