from flopt import Variable
import math

a = Variable('a', lowBound=1, upBound=3, iniValue=2, cat='Integer')
b = Variable('b', lowBound=1, upBound=3, iniValue=2, cat='Continuous')
# c = Variable('c', iniValue=0, cat='Binary')
# d = Variable('d', iniValue=1, cat='Binary')
# e = Variable('e', lowBound=0, upBound=3, cat='Permutation')

# add, sub, mul, div and pow
def test_VarInteger_add1():
    assert (a+2).value() == 4
def test_VarInteger_add2():
    assert (2+a).value() == 4
def test_VarInteger_add3():
    assert (a+2.1).value() == 4.1
def test_VarInteger_add4():
    assert (2.1+a).value() == 4.1

def test_VarInteger_sub1():
    assert (a-2).value() == 0
def test_VarInteger_sub2():
    assert (2-a).value() == 0
def test_VarInteger_sub3():
    assert math.isclose((a-2.1).value(), -0.1)
def test_VarInteger_sub4():
    assert math.isclose((2.1-a).value(), 0.1)

def test_VarInteger_mul1():
    assert (a*2).value() == 4
def test_VarInteger_mul1():
    assert (2*a).value() == 4
def test_VarInteger_mul1():
    assert (a*2.1).value() == 4.2
def test_VarInteger_mul1():
    assert (2.1*a).value() == 4.2

def test_VarInteger_div1():
    assert (a/2).value() == 1
def test_VarInteger_div2():
    assert (1/a).value() == 0.5
def test_VarInteger_div3():
    assert (a/2.0).value() == 1
def test_VarInteger_div4():
    assert (1.0/a).value() == 0.5

def test_VarInteger_pow1():
    assert (a**2).value() == 4
def test_VarInteger_pow1():
    assert (2**a).value() == 4
def test_VarInteger_pow1():
    assert (a**2.1).value() == 2**2.1
def test_VarInteger_pow1():
    assert (2.1**a).value() == 2.1**2

def test_VarInteger_mod():
    assert (a%2).value() == 0

def test_VarInteger_abs1():
    assert abs(a) == 2
def test_VarInteger_abs2():
    assert abs(-a) == 2

def test_VarInteger_cast1():
    assert isinstance(int(a), int)
def test_VarInteger_cast2():
    assert isinstance(float(a), float)

def test_VarInteger_hash():
    hash(a)

def test_VarInteger_eq():
    assert (a == b) is False

# base function
def test_VarInteger_getType():
    assert a.getType() == 'VarInteger'

def test_VarInteger_getVariable1():
    assert a.getVariables() == {a}
def test_VarInteger_getVariable2():
    assert (-a).getVariables() == {a}

def test_VarInteger_neg():
    assert (-a).value() == -2

def test_VarInteger_pos():
    assert (+a).value() == 2

