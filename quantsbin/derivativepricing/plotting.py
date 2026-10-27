"""
developed by Quantsbin - Jun'18

"""

import copy

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

from .namesnmapper import UnderlyingParameters

plt.style.use("ggplot")


class Plotting:
    """
    Here the graphs for payoff, valuation and riskparameters are plotted
        Args required:
            object = (Object). e.g, EqOption for payoff graph/engine for valuation and riskparameters
            func = (String). e.g, "payoff" (graph of which needs to be plotted)
            x_axis = (String). e.g, "spot0" (the x-axis of the graph)
            x_axis_range = (List). List with start and end points of the x-axis.
    :return: Graph of the func
    """

    def __init__(
        self, instrument_object, func, x_axis=UnderlyingParameters.SPOT.value, x_axis_range=None, no_of_points=50
    ):
        self.object = instrument_object
        self.func = func
        self.x_axis = x_axis
        self.x_axis_range = x_axis_range
        self.no_of_points = no_of_points

    def _x(self):
        _temp_x = np.linspace(self.x_axis_range[0], self.x_axis_range[1], self.no_of_points)
        if not _temp_x[0]:
            _temp_x[0] += 0.001
        return np.linspace(self.x_axis_range[0], self.x_axis_range[1], self.no_of_points)

    def _get_set(self, _x_var):
        temp_object = copy.copy(self.object)
        temp_object._other_args[self.x_axis] = _x_var
        if self.func == "valuation":
            _fucntion_return = getattr(temp_object, self.func)()
        else:
            _fucntion_return = temp_object.risk_parameters_func()[self.func]()
        return _fucntion_return

    def _y(self):
        if self.func == "payoff":
            return list(map(getattr(self.object, self.func), list(self._x())))
        elif self.func == "pnl":
            return (
                np.array(list(map(getattr(self.object.instrument, "payoff"), list(self._x()))))
                - self.object.valuation()
            )
        else:
            return list(map(self._get_set, list(self._x())))

    def line_plot(self):
        """
            The plot uses matplotlib library and for smoothing purposes interp1d is used
            (spline is retired since scipy 1.0.0)
        :return: matplotlib plot object
        """
        _x_axis = self._x()
        _x_new = np.linspace(_x_axis[0], _x_axis[-1], self.no_of_points * 10)
        # _y_smooth = spline(_x_axis, self._y(), _x_new)
        f = interp1d(_x_axis, self._y(), kind="cubic")
        _y_smooth = f(_x_new)
        plt.plot(_x_new, _y_smooth)
        plt.grid(True)
        plt.xlabel(str(self.x_axis).capitalize())
        plt.ylabel(str(self.func).capitalize())
        plt.title(str(self.func).capitalize() + " vs " + str(self.x_axis).capitalize())
        return plt
