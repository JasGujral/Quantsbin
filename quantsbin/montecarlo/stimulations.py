"""
developed by Quantsbin - Jun'18

"""

import numpy as np

from .namesnmapper import StimulationType


class GeometricBrownianMotion:
    def __init__(
        self,
        spot0,
        maturity,
        drift=0.0,
        volatility=0.1,
        stimulation_type=StimulationType.FINALVALUE,
        no_of_path=10000,
        no_of_steps=100,
        seed=None,
        antithetic=False,
        random_array=None,
        div_list_processed=None,
        **kwargs,
    ):
        self.spot0 = spot0
        self.maturity = maturity
        self.drift = drift
        self.volatility = volatility
        self.stimulation_type = stimulation_type
        self.no_of_path = no_of_path
        self.no_of_steps = no_of_steps
        self.seed = seed
        self.antithetic = antithetic
        self.random_array = random_array
        self.div_list_processed = div_list_processed

    @property
    def delta_maturity(self):
        return self.maturity / self.no_of_steps

    @property
    def norm_random(self):
        if self.random_array:
            if self.stimulation_type == StimulationType.FINALVALUE.value:
                assert self.random_array.shape == (self.no_of_path, 1), "Incorrect dimension of random array"
            if self.stimulation_type == StimulationType.FULLPATH.value:
                assert self.random_array.shape == (self.no_of_path, self.no_of_steps), "Incorrect dimension of array"
            __norm_random = self.random_array
        else:
            # A local generator: same stream as np.random.seed(seed) + np.random.normal in 1.0.3,
            # without resetting numpy's global random state for the caller.
            rng = np.random.RandomState(self.seed)
            if self.stimulation_type == StimulationType.FINALVALUE.value:
                __norm_random = rng.normal(size=(self.no_of_path, 1))
            else:
                __norm_random = rng.normal(size=(self.no_of_path, self.no_of_steps))

        if self.antithetic:
            __norm_random = np.vstack((__norm_random, __norm_random * -1))

        return __norm_random

    def _stimulate_final(self):
        return self.spot0 * np.exp(
            (self.drift - (self.volatility**2) / 2) * self.maturity
            + self.volatility * np.sqrt(self.maturity) * self.norm_random
        )

    def _stimulate_path(self):
        __exp_term = ((self.drift - (self.volatility**2) / 2) * self.delta_maturity) + (
            self.volatility * np.sqrt(self.delta_maturity) * self.norm_random
        )
        __cum_exp_term = np.exp(np.cumsum(__exp_term, axis=1))
        if self.antithetic:
            __paths = self.no_of_path * 2
        else:
            __paths = self.no_of_path
        __final_term = np.hstack((np.ones((__paths, 1)), __cum_exp_term))
        _stimulated_spot = self.spot0 * __final_term
        for div in self.div_list_processed:
            _temp_n = int(div[0] / self.delta_maturity)
            _temp_cum_exp_term = div[1] * np.exp(np.cumsum(__exp_term[:, _temp_n:], axis=1))
            _stimulated_spot[:, _temp_n + 1 :] = _stimulated_spot[:, _temp_n + 1 :] - _temp_cum_exp_term
        return _stimulated_spot

    def stimulation(self):
        if self.stimulation_type == StimulationType.FINALVALUE.value:
            return self._stimulate_final()
        elif self.stimulation_type == StimulationType.FULLPATH.value:
            return self._stimulate_path()
