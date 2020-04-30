from flopt import Variable
import math

b = Variable('b', lowBound=1, upBound=3, iniValue=2, cat='Continuous')
c = Variable('c', lowBound=1, upBound=3, iniValue=2, cat='Continuous')

# add, sub, mul and div
def test_VarContinuous_add1():
    assert (b+2).value() == 4
def test_VarContinuous_add2():
    assert (2+b).value() == 4
def test_VarContinuous_add3():
    assert (b+2.1).value() == 4.1
def test_VarContinuous_add4():
    assert (2.1+b).value() == 4.1

def test_VarContinuous_sub1():
    assert (b-2).value() == 0
def test_VarContinuous_sub2():
    assert (2-b).value() == 0
def test_VarContinuous_sub3():
    assert math.isclose((b-2.1).value(), -0.1)
def test_VarContinuous_sub4():
    assert math.isclose((2.1-b).value(), 0.1)

def test_VarContinuous_mul1():
    assert (b*2).value() == 4
def test_VarContinuous_mul2():
    assert (2*b).value() == 4
def test_VarContinuous_mul3():
    assert (b*2.1).value() == 4.2
def test_VarContinuous_mul4():
    assert (2.1*b).value() == 4.2

def test_VarContinuous_div1():
    assert (b/2).value() == 1
def test_VarContinuous_div2():
    assert (2/b).value() == 1
def test_VarContinuous_div3():
    assert (b/2.0).value() == 1
def test_VarContinuous_div4():
    assert (2.0/b).value() == 1


def test_VarContinuous_pow1():
    assert (b**2).value() == 4
def test_VarContinuous_pow2():
    assert (2**b).value() == 4
def test_VarContinuous_pow3():
    assert (b**2.1).value() == 2**2.1
def test_VarContinuous_pow4():
    assert (2.1**b).value() == 2.1**2

def test_VarInteger_mod():
    assert (b%2).value() == 0

def test_VarInteger_abs1():
    assert abs(b) == 2
def test_VarInteger_abs2():
    assert abs(-b) == 2

def test_VarInteger_cast1():
    assert isinstance(int(b), int)
def test_VarInteger_cast2():
    assert isinstance(float(b), float)

def test_VarInteger_hash():
    hash(b)

def test_VarInteger_eq():
    assert (b == c) is False

# base function
def test_VarContinuous_getType():
    assert b.getType() == 'VarContinuous'

def test_VarContinuous_getvariable1():
    assert b.getVariables() == {b}
def test_VarContinuous_getvariable2():
    assert (-b).getVariables() == {b}

def test_VarContinuous_neg():
    assert (-b).value() == -2

def test_VarContinuous_pos():
    assert (+b).value() == 2

