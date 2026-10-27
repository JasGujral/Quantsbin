"""Import and packaging smoke tests."""

import re

import quantsbin
import quantsbin.derivativepricing as qbdp


def test_version_is_pep440():
    assert re.fullmatch(r"\d+\.\d+\.\d+((a|b|rc)\d+)?(\.dev\d+)?", quantsbin.__version__)


def test_public_api_exports():
    for name in qbdp.__all__:
        assert hasattr(qbdp, name), name


def test_list_models():
    option = qbdp.EqOption(strike=100, expiry_date="20180630")
    assert "BSM" in option.list_models()
