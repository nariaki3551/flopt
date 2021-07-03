import pytest

from flopt import Variable
import math

@pytest.fixture(scope='function')
def b():
    return Variable('b', lowBound=1, upBound=3, iniValue=2, cat='Continuous')

# add, sub, mul and div
def test_VarContinuous_add(b):
    assert (b+2).value() == 4
    assert (2+b).value() == 4
    assert (b+2.1).value() == 4.1
    assert (2.1+b).value() == 4.1

def test_VarContinuous_sub(b):
    assert (b-2).value() == 0
    assert (2-b).value() == 0
    assert math.isclose((b-2.1).value(), -0.1)
    assert math.isclose((2.1-b).value(), 0.1)

def test_VarContinuous_mul(b):
    assert (b*2).value() == 4
    assert (2*b).value() == 4
    assert (b*2.1).value() == 4.2
    assert (2.1*b).value() == 4.2

def test_VarContinuous_div(b):
    assert (b/2).value() == 1
    assert (2/b).value() == 1
    assert (b/2.0).value() == 1
    assert (2.0/b).value() == 1

def test_VarContinuous_pow(b):
    assert (b**2).value() == 4
    assert (2**b).value() == 4
    assert (b**2.1).value() == 2**2.1
    assert (2.1**b).value() == 2.1**2

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
def test_VarContinuous_getType(b):
    assert b.getType() == 'VarContinuous'

def test_VarContinuous_getvariable(b):
    assert b.getVariables() == {b}
    assert (-b).getVariables() == {b}

def test_VarContinuous_neg(b):
    assert (-b).value() == -2

def test_VarContinuous_pos(b):
    assert (+b).value() == 2

