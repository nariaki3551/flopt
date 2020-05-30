from flopt import Variable, CustomExpression
from flopt.expression import Expression

a = Variable('a', lowBound=1, upBound=3, iniValue=2, cat='Integer')
b = Variable('b', lowBound=1, upBound=3, iniValue=2, cat='Continuous')

def test_Constraint_type1():
    assert (a == 0).type == 'eq'

def test_Constraint_type2():
    assert (a <= 0).type == 'le'

def test_Constraint_type3():
    assert (a >= 0).type == 'ge'

def test_Constraint_type4():
    assert (a+b == 0).type == 'eq'

def test_Constraint_type5():
    assert (a+b <= 0).type == 'le'

def test_Constraint_type6():
    assert (a+b >= 0).type == 'ge'

def test_Constraint_expression1():
    assert hash((a == 0).expression) == hash(a-0)

def test_Constraint_expression2():
    assert hash((a <= 0).expression) == hash(a-0)

def test_Constraint_expression3():
    assert hash((a >= 0).expression) == hash(a-0)

def test_Constraint_expression4():
    assert hash((a+b == 0).expression) == hash(a+b-0)

def test_Constraint_expression5():
    assert hash((a+b <= 0).expression) == hash(a+b-0)

def test_Constraint_expression6():
    assert hash((a+b >= 0).expression) == hash(a+b-0)
