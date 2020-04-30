from flopt import Variable

a = Variable('a', iniValue=1, cat='Binary')
b = Variable('b', iniValue=0, cat='Binary')


def test_VarBinary_add1():
    assert (a+2).value() == 3
def test_VarBinary_add2():
    assert (2+a).value() == 3
def test_VarBinary_add3():
    assert (a+2.1).value() == 3.1
def test_VarBinary_add4():
    assert (2.1+a).value() == 3.1

def test_VarBinary_sub1():
    assert (a-2).value() == -1
def test_VarBinary_sub2():
    assert (2-a).value() == 1
def test_VarBinary_sub3():
    assert (a-2.1).value() == -1.1
def test_VarBinary_sub4():
    assert (2.1-a).value() == 1.1

def test_VarBinary_mul1():
    assert (a*2).value() == 2
def test_VarBinary_mul2():
    assert (2*a).value() == 2
def test_VarBinary_mul3():
    assert (a*2.1).value() == 2.1
def test_VarBinary_mul4():
    assert (2.1*a).value() == 2.1

def test_VarBinary_div1():
    assert (a/2).value() == 0.5
def test_VarBinary_div2():
    assert (1/a).value() == 1
def test_VarBinary_div3():
    assert (a/2.0).value() == 0.5
def test_VarBinary_div4():
    assert (1.0/a).value() == 1

def test_VarBinary_pow1():
    assert (a**2).value() == 1
def test_VarBinary_pow2():
    assert (2**a).value() == 2
def test_VarBinary_pow3():
    assert (a**2.1).value() == 1
def test_VarBinary_pow4():
    assert (2.1**a).value() == 2.1

def test_VarBinary_mod():
    assert (a%2).value() == 1

def test_VarBinary_abs():
    assert abs(a) == 1
    assert abs(-a) == 1

def test_VarBinary_cast1():
    assert isinstance(int(a), int)
def test_VarBinary_cast2():
    assert isinstance(float(a), float)

def test_VarBinary_hash():
    hash(a)

def test_VarBinary_eq():
    assert (a == b) is False

# base function
def test_VarBinary_getType():
    assert a.getType() == 'VarBinary'

def test_VarBinary_getVariable1():
    assert a.getVariables() == {a}
def test_VarBinary_getVariable2():
    assert (-a).getVariables() == {a}

def test_VarBinary_neg():
    assert (-a).value() == -1
    
def test_VarBinary_invert():
    assert (~a).value() == 0

def test_VarBinary_pos():
    assert (+a).value() == 1

