import pytest

from flopt import Variable, CustomExpression

@pytest.fixture(scope='function')
def a():
    return Variable('a', lowBound=1, upBound=3, ini_value=2, cat='Integer')

@pytest.fixture(scope='function')
def b():
    return Variable('b', lowBound=1, upBound=3, ini_value=2, cat='Continuous')

@pytest.fixture(scope='function')
def obj():
    def f(x, y):
        return 2*x + y
    return f

@pytest.fixture(scope='function')
def custom_obj(obj, a, b):
    return CustomExpression(obj, [a, b])


def test_CustomExpression(custom_obj):
    assert custom_obj.value() == 6

def test_CustomExpression_add(custom_obj):
    assert (custom_obj+1).value() == 7
    assert (1+custom_obj).value() == 7
    assert (custom_obj+1.0).value() == 7
    assert (1.0+custom_obj).value() == 7

def test_CustomExpression_add_Variable(custom_obj, a):
    assert (custom_obj+a).value() == 8  # 6+2
    assert (a+custom_obj).value() == 8

def test_CustomExpression_add_Expression1(custom_obj, a, b):
    assert (custom_obj+(a-b)).value() == 6  # 6-0
    assert ((a-b)+custom_obj).value() == 6

def test_CustomExpression_add_CustomExpression(custom_obj):
    assert (custom_obj+custom_obj).value() == 12    # 6+6

def test_CustomExpression_sub(custom_obj):
    assert (custom_obj-1).value() == 5
    assert (1-custom_obj).value() == -5
    assert (custom_obj-1.0).value() == 5
    assert (1.0-custom_obj).value() == -5

def test_CustomExpression_sub_Variable(custom_obj, a):
    assert (custom_obj-a).value() == 4  # 6-2
    assert (a-custom_obj).value() == -4

def test_CustomExpression_sub_Expression(custom_obj, a, b):
    assert (custom_obj-(a-b)).value() == 6  # 6-0
    assert ((a-b)-custom_obj).value() == -6

def test_CustomExpression_sub_CustomExpression(custom_obj):
    assert (custom_obj-custom_obj).value() == 0  # 6-6

def test_CustomExpression_mul(custom_obj):
    assert (custom_obj*2).value() == 12
    assert (2*custom_obj).value() == 12
    assert (custom_obj*2.0).value() == 12
    assert (2.0*custom_obj).value() == 12

def test_CustomExpression_mul_Variable(custom_obj, a):
    assert (custom_obj*a).value() == 12  # 6*2
    assert (a*custom_obj).value() == 12

def test_CustomExpression_mul_Expressio(custom_obj, a, b):
    assert (custom_obj*(a-b)).value() == 0  # 6*0
    assert ((a-b)*custom_obj).value() == 0

def test_CustomExpression_mul_CustomExpression(custom_obj):
    assert (custom_obj*custom_obj).value() == 36  # 6*6

def test_CustomExpression_div(custom_obj):
    assert (custom_obj/2).value() == 3
    assert (2/custom_obj).value() == 1/3
    assert (custom_obj/2.0).value() == 3
    assert (2.0/custom_obj).value() == 1/3

def test_CustomExpression_div_Variable(custom_obj, a):
    assert (custom_obj/a).value() == 3  # 6/2
    assert (a/custom_obj).value() == 1/3  # 2/6

def test_CustomExpression_div_Expression(custom_obj, a, b):
    assert (custom_obj/(a-b+1)).value() == 6  # 6/1
    assert ((a-b)/custom_obj).value() == 0

def test_CustomExpression_div_CustomExpression(custom_obj):
    assert (custom_obj/custom_obj).value() == 1  # 6/6

def test_CustomExpression_getVariable(custom_obj, a, b):
    assert custom_obj.getVariables() == {a, b}

def test_CustomExpression_getVariable_Variable(custom_obj, a, b):
    assert (custom_obj+a).getVariables() == {a, b}
    assert (custom_obj+(a+b)).getVariables() == {a,b}

def test_CustomExpression_traverse(custom_obj):
    assert len(list(custom_obj.traverse())) == 1

def test_CustomExpression_neg(custom_obj):
    assert (-custom_obj).value() == -6

def test_CustomExpression_pos(custom_obj):
    assert (+custom_obj).value() == 6

def test_CustomExpression_abs(custom_obj):
    assert abs(custom_obj) == 6
    assert abs(-custom_obj) == 6

def test_CustomExpression_hash(custom_obj):
    hash(custom_obj)

def test_CustomExpression_repr(custom_obj):
    repr(custom_obj)

def test_CustomExpression_isLinear(custom_obj, a):
    assert (custom_obj).isLinear() == False
    assert (custom_obj+a).isLinear() == False

