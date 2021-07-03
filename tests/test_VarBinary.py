import pytest

from flopt import Variable

@pytest.fixture(scope='function')
def a():
    return Variable('a', iniValue=1, cat='Binary')


def test_VarBinary_add(a):
    assert (a+2).value() == 3
    assert (2+a).value() == 3
    assert (a+2.1).value() == 3.1
    assert (2.1+a).value() == 3.1

def test_VarBinary_sub(a):
    assert (a-2).value() == -1
    assert (2-a).value() == 1
    assert (a-2.1).value() == -1.1
    assert (2.1-a).value() == 1.1

def test_VarBinary_mul(a):
    assert (a*2).value() == 2
    assert (2*a).value() == 2
    assert (a*2.1).value() == 2.1
    assert (2.1*a).value() == 2.1

def test_VarBinary_div(a):
    assert (a/2).value() == 0.5
    assert (1/a).value() == 1
    assert (a/2.0).value() == 0.5
    assert (1.0/a).value() == 1

def test_VarBinary_pow(a):
    assert (a**2).value() == 1
    assert (2**a).value() == 2
    assert (a**2.1).value() == 1
    assert (2.1**a).value() == 2.1

def test_VarBinary_mod(a):
    assert (a%2).value() == 1

def test_VarBinary_abs(a):
    assert abs(a) == 1
    assert abs(-a) == 1

def test_VarBinary_cast1(a):
    assert isinstance(int(a), int)
    assert isinstance(float(a), float)

def test_VarBinary_hash(a):
    hash(a)

# base function
def test_VarBinary_getType(a):
    assert a.getType() == 'VarBinary'

def test_VarBinary_getVariable(a):
    assert a.getVariables() == {a}
    assert (-a).getVariables() == {a}

def test_VarBinary_neg(a):
    assert (-a).value() == -1

def test_VarBinary_invert(a):
    assert (~a).value() == 0

def test_VarBinary_pos(a):
    assert (+a).value() == 1

