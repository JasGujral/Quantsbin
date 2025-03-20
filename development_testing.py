"""
    developed by Quantsbin - Jun'18

"""

import quantsbin.derivativepricing as qbdp

import quantsbin.derivativepricing.plotting as pt


"""Defining options"""
eqOption1 = qbdp.EqOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='European')
eqOption2 = qbdp.EqOption(option_type='Call', strike=110, expiry_date='20180630', expiry_type='European')

fxOption1 = qbdp.FXOption(option_type='Call', strike=98, expiry_date='20190630', expiry_type='European')
fxOption2 = qbdp.FXOption(option_type='Put', strike=95, expiry_date='20180630', expiry_type='American')

futOption1 = qbdp.FutOption(option_type='Put', strike=102, expiry_date='20190630', expiry_type='American')
futOption2 = qbdp.FutOption(option_type='Call', strike=95, expiry_date='20180630', expiry_type='European')

comOption1 = qbdp.ComOption(option_type='Put', strike=95, expiry_date='20190630', expiry_type='European')
comOption2 = qbdp.ComOption(option_type='Call', strike=105, expiry_date='20190630', expiry_type='American')

"""Creating list of all defined option for consolidate testing"""

# option_list = [eqOption1, eqOption2, fxOption1, fxOption2, futOption1, futOption2, comOption1, comOption2]
#
# # print(eqOption2.payoff(0))
#
# """Payoff plot testing"""
# for option in option_list:
#     payoff_plt = qbdp.Plotting(option, "payoff", x_axis_range=[0, 200]).line_plot()
#     payoff_plt.show()


"""Testing payoff"""
# for option in option_list:
#     print("Payoff for option {} with strike {} at {} is {}".format(option.option_type,
#                                                                    option.strike, 110, option.payoff(110)))
#     print("Payoff for option {} with strike {} at {} is {}".format(option.option_type,
#                                                                    option.strike, 95, option.payoff(95)))
# """Testing model list generation"""
# for option in option_list:
#     print("Models available for pricing {} option are {}".format(option.undl, option.list_models()))

print(eqOption1.engine.__doc__)


eqOption1_pricer = eqOption1.engine(model="BSM", spot0=100, pricing_date='20180531', volatility=.25,
                                    rf_rate=.05, pv_div=0.0,
                                    yield_div=0.0, seed=12)

print(eqOption1_pricer.risk_parameters_num())

# payoff_plt = qbdp.Plotting(eqOption1, "payoff", x_axis_range=[0, 200]).line_plot()

# delta_plt = qbdp.Plotting(eqOption1_pricer, "Gamma", x_axis_range=[0, 200]).line_plot()
#
# delta_plt.show()

OPTION1 = qbdp.OptionStr1Udl([(eqOption1, 1), (eqOption2, -1)])
OPTION1_Pricer = OPTION1.engine(model="BSM", spot0=100, pricing_date='20180531', volatility=.25,
                                rf_rate=.05, pv_div=0.0, yield_div=0.0, seed=12)

test_plot = qbdp.Plotting(eqOption1_pricer,'pnl', x_axis_range=[50, 150]).line_plot()
test_plot.show()
# option_payoff = qbdp.Plotting(OPTION1, "payoff", x_axis_range=[0, 200]).line_plot()
#
# option_payoff.show()

# option_val = qbdp.Plotting(OPTION1_Pricer, "valuation", x_axis_range=[0, 200]).line_plot()
# option_val.show()

abc = qbdp.StdStrategies(name="bull_call", expiry_date="20180630", expiry_type=None, low_strike=100, spread=10)
abc_engine = abc.engine(model="BSM", spot0=100, pricing_date='20180531', volatility=.25,
                                 rf_rate=.05, pv_div=0.0, yield_div=0.0, seed=12)


# stg_payoff = qbdp.Plotting(abc, "payoff", x_axis_range=[75, 125]).line_plot()

stg_gamma = qbdp.Plotting(OPTION1_Pricer, "valuation", x_axis_range=[75, 125]).line_plot()
stg_gamma.show()


"""Testing for incorrect model - should raise assertion error"""
# eqOption2_pricer = eqOption2.engine(model="BSM", spot0=100, pricing_date='20180531', volatility=.1,
#                                     rf_rate=.05, pv_div=0.0,
#                                     yield_div=0.0, seed=12)

"""BS Framework Testing"""

# div_list = [("20180610", 2), ("20180624", 4)]
#
# """Equity Options BSM Testing"""
# eqOption_BSM_test = qbdp.EqOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='European')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="BSM", spot0=110, pricing_date='20180531', volatility=.25,
#                                             rf_rate=.05, div_list=None, yield_div=0.01, seed=12)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())
# print(eqOption_BSM_test_pricer.risk_parameters())

# """Futures Option B76 Testing"""
# eqOption_BSM_test = qbdp.FutOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='European')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="B76", fwd0=110, pricing_date='20180531', volatility=.25,
#                                                     rf_rate=.05, seed=12)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())
# print(eqOption_BSM_test_pricer.risk_parameters())

# """COM Option GK Testing"""
# eqOption_BSM_test = qbdp.ComOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='European')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="GK", spot0=110, pricing_date='20180531', volatility=.25,
#                                                     rf_rate=.05, cost_yield=0.03, cnv_yield=0.01, seed=12)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())
# print(eqOption_BSM_test_pricer.risk_parameters())

# #
# """EqOption using Binomial"""
# eqOption_BSM_test = qbdp.EqOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='American')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="Binomial", spot0=110, pricing_date='20180531', volatility=.25,
#                                             rf_rate=.05, div_list=div_list, yield_div=0.01, seed=12)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())
# print(eqOption_BSM_test_pricer.risk_parameters())

# #
# """EqOption using Trinomial"""
# eqOption_BSM_test = qbdp.EqOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='American')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="Trinomial", spot0=110, pricing_date='20180531', volatility=.25,
#                                             rf_rate=.05, div_list=div_list, yield_div=0.01, seed=12)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())
# print(eqOption_BSM_test_pricer.risk_parameters())

# """FutOption using Binomial"""
# eqOption_BSM_test = qbdp.FutOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='American')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="Binomial", fwd0=110, pricing_date='20180531', volatility=.25,
#                                                     rf_rate=.05, seed=12)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())

# """Comm using Binomial"""
# eqOption_BSM_test = qbdp.ComOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='European')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="Binomial", spot0=110, pricing_date='20180531', volatility=.25,
#                                                     rf_rate=.05, cost_yield=0.03, cnv_yield=0.01)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())


# """Comm using MC"""
# eqOption_BSM_test = qbdp.ComOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='European')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="MC_GBM", spot0=110, pricing_date='20180531', volatility=.25,
#                                                     rf_rate=.05, cost_yield=0.03, cnv_yield=0.01)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())

# """Fut using MC"""
# eqOption_BSM_test = qbdp.FutOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='American')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="MC_GBM", fwd0=110, pricing_date='20180531', volatility=.25,
#                                                     rf_rate=.05, seed=153)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())

#
# """Equity using MC"""
# eqOption_BSM_test = qbdp.EqOption(option_type='Call', strike=100, expiry_date='20180630', expiry_type='American')
# eqOption_BSM_test_pricer = eqOption_BSM_test.engine(model="MC_GBM", spot0=110, pricing_date='20180531', volatility=.25,
#                                             rf_rate=.05, div_list=div_list, yield_div=0.01, seed=153)
#
# print(eqOption_BSM_test_pricer.valuation())
# print(eqOption_BSM_test_pricer.risk_parameters_num())




"""strategy1_constituents = [(eqOption1, 1), (eqOption2, -1)]

option_strategy1 = qbdp.OptionStr1Udl(strategy1_constituents)

# print(option_strategy1.payoff(105))

# print(qbdp.StdStrategies(name="strip", asset="Stock", expiry_date='20180630', expiry_type="European", low_strike=100
#                          , spread=10).payoff(0))

# payoff = eqOption1.payoff(110)
#
# # print(payoff)
#
eqOption1_pricer = eqOption1.engine(model="Binomial", spot0=100, pricing_date='20180531', volatility=.1,
                                    rf_rate=.05, pv_div=0.0,
                                    yield_div=0.0, seed=12)

premium = eqOption1_pricer.valuation()

print(premium)

Plotting

# eqOption1.plot("payoff", x_axis="spot", range=[50, 150])
#
# eqOption1_pricer.plot("valuation", spot_range=[50, 150])
#
# eqOption1_pricer.plot("delta", spot_range=[50, 150])

Plotting code structure

# Construct spot range
#  range 50 to 150
#
# map (func, range )
#
# func set attr x_axis, first variable

# print(premium)

# print(eqOption1_pricer.risk_parameters())

# payoff = pt.Plotting(eqOption1, "payoff", x_axis_range=[0, 150]).line_plot()
# payoff.show()
#
# premium = pt.Plotting(eqOption1_pricer, "valuation", x_axis_range=[50, 150]).line_plot()
# premium.show()

delta = pt.Plotting(eqOption1_pricer, "delta", x_axis_range=[50, 200]).line_plot()
print(delta)
delta.show()

"""
