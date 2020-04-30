from flopt import Variable

a = Variable(name='a', lowBound=1, upBound=5, iniValue=2, cat='Continuous')
b = Variable(name='b', lowBound=1, upBound=5, iniValue=3, cat='Continuous')

c = a + b

def test_Expression():
    assert c.value() == 5

def test_Expression_add1():
    assert (c+1).value() == 6
def test_Expression_add2():
    assert (1+c).value() == 6
def test_Expression_add3():
    assert (c+1.0).value() == 6
def test_Expression_add4():
    assert (1.0+c).value() == 6
def test_Expression_add5():
    assert (c+a).value() == 7
def test_Expression_add6():
    assert (a+c).value() == 7

def test_Expression_sub1():
    assert (c-1).value() == 4
def test_Expression_sub2():
    assert (1-c).value() == -4
def test_Expression_sub3():
    assert (c-1.0).value() == 4
def test_Expression_sub4():
    assert (1.0-c).value() == -4
def test_Expression_sub5():
    assert (c-a).value() == 3
def test_Expression_sub6():
    assert (a-c).value() == -3

def test_Expression_mul1():
    assert (c*2).value() == 10
def test_Expression_mul2():
    assert (2*c).value() == 10
def test_Expression_mul3():
    assert (c*2.0).value() == 10
def test_Expression_mul4():
    assert (2.0*c).value() == 10
def test_Expression_mul5():
    assert (c*a).value() == 10
def test_Expression_mul6():
    assert (a*c).value() == 10

def test_Expression_div1():
    assert (c/2).value() == 2.5
def test_Expression_div2():
    assert (2/c).value() == 0.4
def test_Expression_div3():
    assert (c/2.0).value() == 2.5
def test_Expression_div4():
    assert (2.0/c).value() == 0.4
def test_Expression_div5():
    assert (c/a).value() == 2.5
def test_Expression_div6():
    assert (a/c).value() == 0.4

def test_Expression_pow1():
    assert (c**2).value() == 25
def test_Expression_pow2():
    assert (2**c).value() == 32
def test_Expression_pow3():
    assert (c**2.0).value() == 25
def test_Expression_pow4():
    assert (2.0**c).value() == 32
def test_Expression_pow5():
    assert (c**a).value() == 25
def test_Expression_pow6():
    assert (a**c).value() == 32

def test_Expression_getVariable():
    assert c.getVariables() == {a, b}

def test_Expression_neg():
    assert (-c).value() == -5


def test_Expression_pos():
    assert (+c).value() == 5

def test_Expression_abs1():
    assert abs(c) == 5
def test_Expression_abs2():
    assert abs(-c) == 5

def test_Expression_cas1():
    assert isinstance(int(c), int)
def test_Expression_cas2():
    assert isinstance(float(c), float)

def test_Expression_hash():
    hash(c)
