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

def test_CustomObject_add():
    assert (custom_obj+1).value() == 7
    assert (1+custom_obj).value() == 7
    assert (custom_obj+1.0).value() == 7
    assert (1.0+custom_obj).value() == 7

def test_CustomObject_add_Variable():
    assert (custom_obj+a).value() == 8  # 6+2
    assert (a+custom_obj).value() == 8

def test_CustomObject_add_Expression():
    assert (custom_obj+(a-b)).value() == 6  # 6-0
    assert ((a-b)+custom_obj).value() == 6

def test_CustomObject_add_CustomObject():
    assert (custom_obj+custom_obj2).value() == 9  # 6+3

def test_CustomObject_sub():
    assert (custom_obj-1).value() == 5
    assert (1-custom_obj).value() == -5
    assert (custom_obj-1.0).value() == 5
    assert (1.0-custom_obj).value() == -5

def test_CustomObject_sub_Variable():
    assert (custom_obj-a).value() == 4  # 6-2
    assert (a-custom_obj).value() == -4

def test_CustomObject_sub_Expression():
    assert (custom_obj-(a-b)).value() == 6  # 6-0
    assert ((a-b)-custom_obj).value() == -6

def test_CustomObject_sub_CustomObject():
    assert (custom_obj-custom_obj2).value() == 3  # 6-3

def test_CustomObject_mul():
    assert (custom_obj*2).value() == 12
    assert (2*custom_obj).value() == 12
    assert (custom_obj*2.0).value() == 12
    assert (2.0*custom_obj).value() == 12

def test_CustomObject_mul_Variable():
    assert (custom_obj*a).value() == 12  # 6*2
    assert (a*custom_obj).value() == 12

def test_CustomObject_mul_Expression():
    assert (custom_obj*(a-b)).value() == 0  # 6*0
    assert ((a-b)*custom_obj).value() == 0

def test_CustomObject_mul_CustomObject():
    assert (custom_obj*custom_obj2).value() == 18  # 6*3

def test_CustomObject_div():
    assert (custom_obj/2).value() == 3
    assert (2/custom_obj).value() == 1/3
    assert (custom_obj/2.0).value() == 3
    assert (2.0/custom_obj).value() == 1/3

def test_CustomObject_div_Variable():
    assert (custom_obj/a).value() == 3  # 6/2
    assert (a/custom_obj).value() == 1/3  # 2/6

def test_CustomObject_div_Expression():
    assert (custom_obj/(a-b+1)).value() == 6  # 6/1
    assert ((a-b)/custom_obj).value() == 0

def test_CustomObject_div_CustomObject():
    assert (custom_obj/custom_obj2).value() == 2  # 6/3

def test_CustomObject_getVariable():
    assert custom_obj.getVariables() == [a, b]

def test_CustomObject_getVariable():
    assert custom_obj.getVariables() == [a, b]

def test_CustomObject_getVariable_Variable():
    assert (custom_obj+a).getVariables() == [a, b, a]

def test_CustomObject_getVariable_Expression():
    assert len((custom_obj+(a+c)).getVariables()) == 4
    assert set((custom_obj+(a+c)).getVariables()) == {a,b,c}

def test_CustomObject_neg():
    assert (-custom_obj).value() == -6

def test_CustomObject_pos():
    assert (+custom_obj).value() == 6

def test_CustomObject_abs():
    assert abs(custom_obj) == 6
    assert abs(-custom_obj) == 6

def test_CustomObject_hash():
    hash(custom_obj)
