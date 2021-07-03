import pytest

from flopt import Variable, CustomExpression
from flopt.expression import Expression

@pytest.fixture(scope='function')
def a():
    return Variable('a', lowBound=1, upBound=3, iniValue=2, cat='Integer')

@pytest.fixture(scope='function')
def b():
    return Variable('b', lowBound=1, upBound=3, iniValue=2, cat='Continuous')

def test_Constraint_type(a, b):
    assert (a == 0).type == 'eq'
    assert (a <= 0).type == 'le'
    assert (a >= 0).type == 'ge'
    assert (a+b == 0).type == 'eq'
    assert (a+b <= 0).type == 'le'
    assert (a+b >= 0).type == 'ge'

def test_Constraint_expression(a, b):
    assert hash((a == 0).expression) == hash(a-0)
    assert hash((a <= 0).expression) == hash(a-0)
    assert hash((a >= 0).expression) == hash(a-0)
    assert hash((a+b == 0).expression) == hash(a+b-0)
    assert hash((a+b <= 0).expression) == hash(a+b-0)
    assert hash((a+b >= 0).expression) == hash(a+b-0)
