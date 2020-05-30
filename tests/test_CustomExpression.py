from flopt import Variable, CustomExpression

a = Variable('a', lowBound=1, upBound=3, iniValue=2, cat='Integer')
b = Variable('b', lowBound=1, upBound=3, iniValue=2, cat='Continuous')
c = Variable('c', lowBound=1, upBound=3, iniValue=1, cat='Continuous')

def obj(a, b):
    return 2*a + b

def obj2(b, c):
    return b + c

custom_obj = CustomExpression(obj, [a, b])
custom_obj2 = CustomExpression(obj2, [b, c])


def test_CustomExpression():
    assert custom_obj.value() == 6

def test_CustomExpression_add1():
    assert (custom_obj+1).value() == 7
def test_CustomExpression_add2():
    assert (1+custom_obj).value() == 7
def test_CustomExpression_add3():
    assert (custom_obj+1.0).value() == 7
def test_CustomExpression_add4():
    assert (1.0+custom_obj).value() == 7

def test_CustomExpression_add_Variable1():
    assert (custom_obj+a).value() == 8  # 6+2
def test_CustomExpression_add_Variable2():
    assert (a+custom_obj).value() == 8

def test_CustomExpression_add_Expression1():
    assert (custom_obj+(a-b)).value() == 6  # 6-0
def test_CustomExpression_add_Expression2():
    assert ((a-b)+custom_obj).value() == 6

def test_CustomExpression_add_CustomExpression1():
    assert (custom_obj+custom_obj2).value() == 9  # 6+3

def test_CustomExpression_sub1():
    assert (custom_obj-1).value() == 5
def test_CustomExpression_sub2():
    assert (1-custom_obj).value() == -5
def test_CustomExpression_sub3():
    assert (custom_obj-1.0).value() == 5
def test_CustomExpression_sub4():
    assert (1.0-custom_obj).value() == -5

def test_CustomExpression_sub_Variable1():
    assert (custom_obj-a).value() == 4  # 6-2
def test_CustomExpression_sub_Variable2():
    assert (a-custom_obj).value() == -4

def test_CustomExpression_sub_Expression1():
    assert (custom_obj-(a-b)).value() == 6  # 6-0
def test_CustomExpression_sub_Expression2():
    assert ((a-b)-custom_obj).value() == -6

def test_CustomExpression_sub_CustomExpression():
    assert (custom_obj-custom_obj2).value() == 3  # 6-3

def test_CustomExpression_mul1():
    assert (custom_obj*2).value() == 12
def test_CustomExpression_mul2():
    assert (2*custom_obj).value() == 12
def test_CustomExpression_mul3():
    assert (custom_obj*2.0).value() == 12
def test_CustomExpression_mul4():
    assert (2.0*custom_obj).value() == 12

def test_CustomExpression_mul_Variable1():
    assert (custom_obj*a).value() == 12  # 6*2
def test_CustomExpression_mul_Variable2():
    assert (a*custom_obj).value() == 12

def test_CustomExpression_mul_Expressio1():
    assert (custom_obj*(a-b)).value() == 0  # 6*0
def test_CustomExpression_mul_Expressio2():
    assert ((a-b)*custom_obj).value() == 0

def test_CustomExpression_mul_CustomExpression():
    assert (custom_obj*custom_obj2).value() == 18  # 6*3

def test_CustomExpression_div1():
    assert (custom_obj/2).value() == 3
def test_CustomExpression_div2():
    assert (2/custom_obj).value() == 1/3
def test_CustomExpression_div3():
    assert (custom_obj/2.0).value() == 3
def test_CustomExpression_div4():
    assert (2.0/custom_obj).value() == 1/3

def test_CustomExpression_div_Variable1():
    assert (custom_obj/a).value() == 3  # 6/2
def test_CustomExpression_div_Variable2():
    assert (a/custom_obj).value() == 1/3  # 2/6

def test_CustomExpression_div_Expression1():
    assert (custom_obj/(a-b+1)).value() == 6  # 6/1
def test_CustomExpression_div_Expression2():
    assert ((a-b)/custom_obj).value() == 0

def test_CustomExpression_div_CustomExpression():
    assert (custom_obj/custom_obj2).value() == 2  # 6/3

def test_CustomExpression_getVariable():
    assert custom_obj.getVariables() == {a, b}

def test_CustomExpression_getVariable_Variable():
    assert (custom_obj+a).getVariables() == {a, b, a}

def test_CustomExpression_getVariable_Expression1():
    assert len((custom_obj+(a+c)).getVariables()) == 3
def test_CustomExpression_getVariable_Expression2():
    assert (custom_obj+(a+c)).getVariables() == {a,b,c}

def test_CustomExpression_neg():
    assert (-custom_obj).value() == -6

def test_CustomExpression_pos():
    assert (+custom_obj).value() == 6

def test_CustomExpression_abs():
    assert abs(custom_obj) == 6
    assert abs(-custom_obj) == 6

def test_CustomExpression_hash():
    hash(custom_obj)
