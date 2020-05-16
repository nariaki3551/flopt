from flopt import Variable, CustomObject

a = Variable('a', lowBound=1, upBound=3, iniValue=2, cat='Integer')
b = Variable('b', lowBound=1, upBound=3, iniValue=2, cat='Continuous')
c = Variable('c', lowBound=1, upBound=3, iniValue=1, cat='Continuous')

def obj(a, b):
    return 2*a + b

def obj2(b, c):
    return b + c

custom_obj = CustomObject(obj, [a, b])
custom_obj2 = CustomObject(obj2, [b, c])


def test_CustomObject():
    assert custom_obj.value() == 6

def test_CustomObject_add1():
    assert (custom_obj+1).value() == 7
def test_CustomObject_add2():
    assert (1+custom_obj).value() == 7
def test_CustomObject_add3():
    assert (custom_obj+1.0).value() == 7
def test_CustomObject_add4():
    assert (1.0+custom_obj).value() == 7

def test_CustomObject_add_Variable1():
    assert (custom_obj+a).value() == 8  # 6+2
def test_CustomObject_add_Variable2():
    assert (a+custom_obj).value() == 8

def test_CustomObject_add_Expression1():
    assert (custom_obj+(a-b)).value() == 6  # 6-0
def test_CustomObject_add_Expression2():
    assert ((a-b)+custom_obj).value() == 6

def test_CustomObject_add_CustomObject1():
    assert (custom_obj+custom_obj2).value() == 9  # 6+3

def test_CustomObject_sub1():
    assert (custom_obj-1).value() == 5
def test_CustomObject_sub2():
    assert (1-custom_obj).value() == -5
def test_CustomObject_sub3():
    assert (custom_obj-1.0).value() == 5
def test_CustomObject_sub4():
    assert (1.0-custom_obj).value() == -5

def test_CustomObject_sub_Variable1():
    assert (custom_obj-a).value() == 4  # 6-2
def test_CustomObject_sub_Variable2():
    assert (a-custom_obj).value() == -4

def test_CustomObject_sub_Expression1():
    assert (custom_obj-(a-b)).value() == 6  # 6-0
def test_CustomObject_sub_Expression2():
    assert ((a-b)-custom_obj).value() == -6

def test_CustomObject_sub_CustomObject():
    assert (custom_obj-custom_obj2).value() == 3  # 6-3

def test_CustomObject_mul1():
    assert (custom_obj*2).value() == 12
def test_CustomObject_mul2():
    assert (2*custom_obj).value() == 12
def test_CustomObject_mul3():
    assert (custom_obj*2.0).value() == 12
def test_CustomObject_mul4():
    assert (2.0*custom_obj).value() == 12

def test_CustomObject_mul_Variable1():
    assert (custom_obj*a).value() == 12  # 6*2
def test_CustomObject_mul_Variable2():
    assert (a*custom_obj).value() == 12

def test_CustomObject_mul_Expressio1():
    assert (custom_obj*(a-b)).value() == 0  # 6*0
def test_CustomObject_mul_Expressio2():
    assert ((a-b)*custom_obj).value() == 0

def test_CustomObject_mul_CustomObject():
    assert (custom_obj*custom_obj2).value() == 18  # 6*3

def test_CustomObject_div1():
    assert (custom_obj/2).value() == 3
def test_CustomObject_div2():
    assert (2/custom_obj).value() == 1/3
def test_CustomObject_div3():
    assert (custom_obj/2.0).value() == 3
def test_CustomObject_div4():
    assert (2.0/custom_obj).value() == 1/3

def test_CustomObject_div_Variable1():
    assert (custom_obj/a).value() == 3  # 6/2
def test_CustomObject_div_Variable2():
    assert (a/custom_obj).value() == 1/3  # 2/6

def test_CustomObject_div_Expression1():
    assert (custom_obj/(a-b+1)).value() == 6  # 6/1
def test_CustomObject_div_Expression2():
    assert ((a-b)/custom_obj).value() == 0

def test_CustomObject_div_CustomObject():
    assert (custom_obj/custom_obj2).value() == 2  # 6/3

def test_CustomObject_getVariable():
    assert custom_obj.getVariables() == {a, b}

def test_CustomObject_getVariable_Variable():
    assert (custom_obj+a).getVariables() == {a, b, a}

def test_CustomObject_getVariable_Expression1():
    assert len((custom_obj+(a+c)).getVariables()) == 3
def test_CustomObject_getVariable_Expression2():
    assert (custom_obj+(a+c)).getVariables() == {a,b,c}

def test_CustomObject_neg():
    assert (-custom_obj).value() == -6

def test_CustomObject_pos():
    assert (+custom_obj).value() == 6

def test_CustomObject_abs():
    assert abs(custom_obj) == 6
    assert abs(-custom_obj) == 6

def test_CustomObject_hash():
    hash(custom_obj)
