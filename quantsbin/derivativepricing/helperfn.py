"""
developed by Quantsbin - Jun'18

"""

import os
import warnings
from datetime import datetime as dt
from math import e

_PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_VOLATILITY = 0.10


def require_spot(spot0):
    """Return the spot (or futures price), rejecting a missing or non-positive value."""
    if spot0 is None or spot0 <= 0:
        raise ValueError(f"spot0 (fwd0 for futures options) must be a positive number, got {spot0!r}")
    return spot0


def parse_pricing_date(pricing_date):
    """Parse a 'YYYYMMDD' pricing date, rejecting a missing one."""
    if pricing_date is None:
        raise ValueError("pricing_date is required, as a 'YYYYMMDD' string, e.g. '20180531'")
    return dt.strptime(pricing_date, "%Y%m%d")


def volatility_or_default(volatility):
    """Keep the 1.x behaviour of defaulting a missing volatility to 10%, but say so.

    This becomes an error in Quantsbin 2.0.
    """
    if not volatility:
        warnings.warn(
            f"volatility was not given; using the 1.x default of {DEFAULT_VOLATILITY:.0%}. "
            "Pass volatility explicitly: this default will be removed in Quantsbin 2.0.",
            FutureWarning,
            skip_file_prefixes=(_PACKAGE_DIR,),
        )
        return DEFAULT_VOLATILITY
    return volatility


def dividend_processor(div_list, pricing_date, expiry_date):
    div_processed = []
    if div_list:
        for date, div_amount in div_list:
            ex_date = dt.strptime(date, "%Y%m%d")
            if (ex_date > pricing_date) and (ex_date <= expiry_date):
                div_time = (ex_date - pricing_date).days / 365.0
                div_processed.append((div_time, div_amount))
    return div_processed


def pv_div(div_processed, time_point, disc_rate):
    pv_div_amount = 0
    if len(div_processed) == 0:
        return pv_div_amount
    for div_time, div_amount in div_processed:
        disc_time = div_time - time_point
        if disc_time >= 0:
            pv_div_amount += div_amount * (e ** (-1 * disc_rate * disc_time))
    return pv_div_amount
