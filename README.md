[![PyPI version](https://img.shields.io/pypi/v/quantsbin.svg?maxAge=60)](https://pypi.org/project/quantsbin/) [![PyPi Status](https://img.shields.io/pypi/status/quantsbin.svg?maxAge=60)](https://pypi.org/project/quantsbin/) [![Github Stars](https://img.shields.io/github/stars/JasGujral/Quantsbin.svg?style=social&label=Star&maxAge=60)](https://github.com/JasGujral/Quantsbin)

# Quantsbin

Open source library for finance.

> **Revival in progress (2026).** Quantsbin is being modernised: a 1.1 release with bug fixes and modern packaging comes first, followed by Quantsbin 2.0 (typed, differentiable pricing with Monte Carlo, volatility and fixed income modules). Follow progress in [issues](https://github.com/JasGujral/Quantsbin/issues) and [pull requests](https://github.com/JasGujral/Quantsbin/pulls).

Quantsbin 1.0.3, which started as a weekend project is currently in its initial phase and
incorporates tools for pricing and plotting of vanilla option prices, greeks and various other analysis around them.
We are working on optimising calculations and expanding the scope of library in multiple directions for future releases.

## Quantsbin 1.0.3 includes
   1. Option payoff, premium and greeks calculation for vanilla options on Equity, FX, Commodity and Futures.
   2. Capability to calculate greeks numerically for all models and also analytically for Black Scholes Model.
   3. Price vanilla options with European expiry using BSM, Binomial tree and MonteCarlo with option to 
      incorporate continuous compounded dividend yield for Equity options,
      cost and convenience yield for Commodity options and
      local and foreign risk-free rate in case of FX options.
      It also allows option to give discrete dividends in cased of Equity options.
   4. Price vanilla options with American expiry using Binomial tree and MonteCarlo(Longstaff Schwartz) method.
      There is option to provide discrete dividends for Equity options for both the models.
   5. Implied volatility calculation under BSM framework model.
   6. Option to create user defined or standard strategies using multiple single underlying options and
      directly generate and plot valuation and greeks for these strategies.

## License
[MIT License](LICENSE)

## Dependencies and Installation details
      scipy==1.6.3
      pandas==1.2.4
      matplotlib==3.4.2
      numpy==1.18.0     
    
Install using setup.py:
```
>>> python setup.py install
```
Install using pip:
```
>>> pip install quantsbin
```

## Examples
See [examples/quickstart.py](examples/quickstart.py) for pricing, greeks, strategies and plotting.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Changes are tracked in [CHANGELOG.md](CHANGELOG.md).

## Note
Full documentation is being rebuilt as part of the 2.0 work.
