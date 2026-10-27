"""
developed by Quantsbin - Jun'18

"""

from enum import Enum


class ProcessNames(Enum):
    GEOMETRICBROWNIANMOTION = "GBM"


class StimulationType(Enum):
    FULLPATH = "Path"
    FINALVALUE = "Final"


from .stimulations import GeometricBrownianMotion

mc_methd_mapper = {ProcessNames.GEOMETRICBROWNIANMOTION.value: GeometricBrownianMotion}
