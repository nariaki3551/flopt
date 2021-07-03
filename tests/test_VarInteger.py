import pytest

from flopt import Variable
import math

@pytest.fixture(scope='function')
def a():
    return Variable('a', lowBound=1, upBound=3, iniValue=2, cat='Integer')

# add, sub, mul, div and pow
def test_VarInteger_add(a):
    assert (a+2).value() == 4
    assert (2+a).value() == 4
    assert (a+2.1).value() == 4.1
    assert (2.1+a).value() == 4.1

def test_VarInteger_sub(a):
    assert (a-2).value() == 0
    assert (2-a).value() == 0
    assert math.isclose((a-2.1).value(), -0.1)
    assert math.isclose((2.1-a).value(), 0.1)

def test_VarInteger_mul(a):
    assert (a*2).value() == 4
    assert (2*a).value() == 4
    assert (a*2.1).value() == 4.2
    assert (2.1*a).value() == 4.2

def test_VarInteger_div(a):
    assert (a/2).value() == 1
    assert (1/a).value() == 0.5
    assert (a/2.0).value() == 1
    assert (1.0/a).value() == 0.5

def test_VarInteger_pow(a):
    assert (a**2).value() == 4
    assert (2**a).value() == 4
    assert (a**2.1).value() == 2**2.1
    assert (2.1**a).value() == 2.1**2

def test_VarInteger_mod(a):
    assert (a%2).value() == 0

def test_VarInteger_abs(a):
    assert abs(a) == 2
    assert abs(-a) == 2

def test_VarInteger_cast(a):
    assert isinstance(int(a), int)
    assert isinstance(float(a), float)

def test_VarInteger_hash(a):
    hash(a)

# base function
def test_VarInteger_getType(a):
    assert a.getType() == 'VarInteger'

def test_VarInteger_getVariable(a):
    assert a.getVariables() == {a}
    assert (-a).getVariables() == {a}

def test_VarInteger_neg(a):
    assert (-a).value() == -2

def test_VarInteger_pos(a):
    assert (+a).value() == 2

