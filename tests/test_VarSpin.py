import pytest

import numpy as np

from flopt import Variable

@pytest.fixture(scope='function')
def a():
    return Variable('a', iniValue=1, cat='Spin')


def test_VarSpin_add(a):
    assert (a+2).value() == 3
    assert (2+a).value() == 3
    assert (a+2.1).value() == 3.1
    assert (2.1+a).value() == 3.1
    assert (a+np.float64(2.1)).value() == 3.1
    assert (np.float64(2.1)+a).value() == 3.1

def test_VarSpin_sub(a):
    assert (a-2).value() == -1
    assert (2-a).value() == 1
    assert (a-2.1).value() == -1.1
    assert (2.1-a).value() == 1.1
    assert (a-np.float64(2.1)).value() == -1.1
    assert (np.float64(2.1)-a).value() == 1.1

def test_VarSpin_mul(a):
    assert (a*2).value() == 2
    assert (2*a).value() == 2
    assert (a*2.1).value() == 2.1
    assert (2.1*a).value() == 2.1
    assert (a*np.float64(2.1)).value() == 2.1
    assert (np.float64(2.1)*a).value() == 2.1

def test_VarSpin_div(a):
    assert (a/2).value() == 0.5
    assert (1/a).value() == 1
    assert (a/2.0).value() == 0.5
    assert (1.0/a).value() == 1
    assert (a/np.float64(2.0)).value() == 0.5
    assert (np.float64(1.0)/a).value() == 1

def test_VarSpin_pow(a):
    assert (a**2).value() == 1
    assert (2**a).value() == 2
    assert (a**2.1).value() == 1
    assert (2.1**a).value() == 2.1
    assert (a**np.float64(2.1)).value() == 1
    assert (np.float64(2.1)**a).value() == 2.1

def test_VarSpin_mod(a):
    assert (a%2).value() == 1

def test_VarSpin_abs(a):
    assert abs(a) == 1
    assert abs(-a) == 1

def test_VarSpin_cast1(a):
    assert isinstance(int(a), int)
    assert isinstance(float(a), float)

def test_VarSpin_hash(a):
    hash(a)

# base function
def test_VarSpin_getType(a):
    assert a.getType() == 'VarSpin'

def test_VarSpin_getVariable(a):
    assert a.getVariables() == {a}
    assert (-a).getVariables() == {a}

def test_VarSpin_neg(a):
    assert (-a).value() == -1

def test_VarSpin_invert(a):
    assert (~a).value() == -1

def test_VarSpin_pos(a):
    assert (+a).value() == 1

def test_VarSpin_toBinary1(a):
    from flopt.variable import VarBinary
    a.toBinary()
    assert isinstance(a.binary, VarBinary)
    assert a.toBinary().value() == 1
    assert a.binary.value() == 1

def test_VarSpin_toSpin2(a):
    from flopt.variable import VarBinary
    a.toBinary()
    a.setValue(-1)
    assert isinstance(a.binary, VarBinary)
    assert a.toBinary().value() == -1
    assert a.binary.value() == 0

def test_VarSpin_colne(a):
    from flopt.variable import VarSpin
    _a = a.clone()
    assert isinstance(_a, VarSpin)
    assert _a.value() == a.value()
    assert _a.getLb() == a.getLb()
    assert _a.getUb() == a.getUb()
    assert _a.getType() == a.getType()

