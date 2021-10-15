import math
import pytest

import numpy as np

from flopt import Variable
from flopt.constants import VariableType


@pytest.fixture(scope='function')
def a():
    return Variable('a', lowBound=1, upBound=3, ini_value=2, cat='Continuous')

@pytest.fixture(scope='function')
def b():
    return Variable('b', lowBound=1, upBound=3, ini_value=2, cat='Continuous')

# add, sub, mul and div
def test_VarContinuous_add(b):
    assert (b+2).value() == 4
    assert (2+b).value() == 4
    assert (b+2.1).value() == 4.1
    assert (2.1+b).value() == 4.1
    assert (b+np.float64(2.1)).value() == 4.1
    assert (np.float64(2.1)+b).value() == 4.1

def test_VarContinuous_sub(b):
    assert (b-2).value() == 0
    assert (2-b).value() == 0
    assert math.isclose((b-2.1).value(), -0.1)
    assert math.isclose((2.1-b).value(), 0.1)
    assert math.isclose((b-np.float64(2.1)).value(), -0.1)
    assert math.isclose((np.float64(2.1)-b).value(), 0.1)

def test_VarContinuous_mul1(b):
    assert (b*2).value() == 4
    assert (2*b).value() == 4
    assert (b*2.1).value() == 4.2
    assert (2.1*b).value() == 4.2
    assert (b*np.float64(2.1)).value() == 4.2
    assert (np.float64(2.1)*b).value() == 4.2

def test_VarBinary_mul2(a, b):
    assert ((-a)*b).name == (a*(-b)).name
    assert (a*b).name == ((-a)*(-b)).name

def test_VarContinuous_div(b):
    assert (b/2).value() == 1
    assert (2/b).value() == 1
    assert (b/2.0).value() == 1
    assert (2.0/b).value() == 1
    assert (b/np.float64(2.0)).value() == 1
    assert (np.float64(2.0)/b).value() == 1

def test_VarContinuous_pow(b):
    assert (b**2).value() == 4
    assert (2**b).value() == 4
    assert (b**2.1).value() == 2**2.1
    assert (2.1**b).value() == 2.1**2
    assert (b**np.float64(2.1)).value() == 2**2.1
    assert (np.float64(2.1)**b).value() == 2.1**2

def test_VarInteger_mod(b):
    assert (b%2).value() == 0

def test_VarInteger_abs(b):
    assert abs(b) == 2
    assert abs(-b) == 2

def test_VarInteger_cast(b):
    assert isinstance(int(b), int)
    assert isinstance(float(b), float)

def test_VarInteger_hash(b):
    hash(b)

# base function
def test_VarContinuous_type(b):
    assert b.type() == VariableType.Continuous

def test_VarContinuous_getvariable(b):
    assert b.getVariables() == {b}
    assert (-b).getVariables() == {b}

def test_VarContinuous_neg(b):
    assert (-b).value() == -2

def test_VarContinuous_pos(b):
    assert (+b).value() == 2

def test_VarContinuous_colne(b):
    from flopt.variable import VarContinuous
    _b = b.clone()
    assert isinstance(_b, VarContinuous)
    assert _b.value() == b.value()
    assert _b.getLb() == b.getLb()
    assert _b.getUb() == b.getUb()
    assert _b.type() == b.type()

