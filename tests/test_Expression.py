import pytest

from flopt import Variable
from flopt.expression import ExpressionConst

@pytest.fixture(scope='function')
def a():
    return Variable(name='a', lowBound=1, upBound=5, iniValue=2, cat='Continuous')

@pytest.fixture(scope='function')
def b():
    return Variable(name='b', lowBound=1, upBound=5, iniValue=3, cat='Continuous')

@pytest.fixture(scope='function')
def c(a, b):
    return a + b

def test_Expression(c):
    assert c.value() == 5

def test_Expression_add(c, a):
    assert (c+1).value() == 6
    assert (1+c).value() == 6
    assert (c+1.0).value() == 6
    assert (1.0+c).value() == 6
    assert (c+a).value() == 7
    assert (a+c).value() == 7

def test_Expression_sub(c, a):
    assert (c-1).value() == 4
    assert (1-c).value() == -4
    assert (c-1.0).value() == 4
    assert (1.0-c).value() == -4
    assert (c-a).value() == 3
    assert (a-c).value() == -3

def test_Expression_mul(c, a):
    assert (c*2).value() == 10
    assert (2*c).value() == 10
    assert (c*2.0).value() == 10
    assert (2.0*c).value() == 10
    assert (c*a).value() == 10
    assert (a*c).value() == 10

def test_Expression_div(c, a):
    assert (c/2).value() == 2.5
    assert (2/c).value() == 0.4
    assert (c/2.0).value() == 2.5
    assert (2.0/c).value() == 0.4
    assert (c/a).value() == 2.5
    assert (a/c).value() == 0.4

def test_Expression_pow(c, a):
    assert (c**2).value() == 25
    assert (2**c).value() == 32
    assert (c**2.0).value() == 25
    assert (2.0**c).value() == 32
    assert (c**a).value() == 25
    assert (a**c).value() == 32

def test_Expression_getVariable(a, b, c):
    assert c.getVariables() == {a, b}

def test_Expression_neg(c):
    assert (-c).value() == -5

def test_Expression_pos(c):
    assert (+c).value() == 5

def test_Expression_abs(c):
    assert abs(c) == 5
    assert abs(-c) == 5

def test_Expression_cas(c):
    assert isinstance(int(c), int)
    assert isinstance(float(c), float)

def test_Expression_hashc(c):
    hash(c)

def test_Expression_hasCustomExpression(c, a):
    assert a.hasCustomExpression() == False
    assert c.hasCustomExpression() == False

def test_Expression_isLinear(a, b, c):
    assert a.isLinear() == True
    assert c.isLinear() == True
    assert (a*b).isLinear() == False


def test_ExpressionConst_hash():
    hash(ExpressionConst(0))

def test_ExpressionConst_hasCustomExpression():
    assert ExpressionConst(0).hasCustomExpression() == False

def test_ExpressionConst_isLinear():
    assert ExpressionConst(0).isLinear() == True

