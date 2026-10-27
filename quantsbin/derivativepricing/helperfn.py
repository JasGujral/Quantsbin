"""
developed by Quantsbin - Jun'18

"""

from datetime import datetime as dt
from math import e


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
