import pytest
from core.driver import Driver

# One day, I will make sure everything works...


@pytest.fixture
def valid_formula() -> str:
    return "{p_r(m)^{1\\over\\alpha}}\\over{\\sum_{n=1}^{m}{p_r(n)^{1\\over\\alpha}}}}"


@pytest.mark.Driver
@pytest.mark.tryfirst
def test_driver_functionality(valid_formula):
    dr = Driver()
    results = dr.drive(formula=valid_formula)
