import pytest

import numpy as np

from flopt import Variable, CustomExpression
from flopt.expression import Expression, Const

@pytest.fixture(scope='function')
def a():
    return Variable('a', lowBound=1, upBound=3, ini_value=2, cat='Integer')

@pytest.fixture(scope='function')
def b():
    return Variable('b', lowBound=1, upBound=3, ini_value=2, cat='Continuous')

def test_Constraint_type(a, b):
    assert (a == 0).type == 'eq'
    assert (a <= 0).type == 'le'
    assert (a >= 0).type == 'ge'
    assert (a+b == 0).type == 'eq'
    assert (a+b <= 0).type == 'le'
    assert (a+b >= 0).type == 'ge'
    assert (0 == a+b).type == 'eq'
    assert (0 <= a+b).type == 'ge'
    assert (0 >= a+b).type == 'le'

    assert (a+b == np.float64(0)).type == 'eq'
    assert (a+b <= np.float64(0)).type == 'le'
    assert (a+b >= np.float64(0)).type == 'ge'
    # assert (np.float64(0) == a+b).type == 'eq'
    # assert (np.float64(0) <= a+b).type == 'ge'
    # assert (np.float64(0) >= a+b).type == 'le'


def test_Constraint_expression(a, b):
    assert hash((a == 0).expression) == hash(Expression(a, Const(0), '+'))
    assert hash((a <= 0).expression) == hash(Expression(a, Const(0), '+'))
    assert hash((a >= 0).expression) == hash(Expression(a, Const(0), '+'))
    assert hash((a+b == 0).expression) == hash(a+b-0)
    assert hash((a+b <= 0).expression) == hash(a+b-0)
    assert hash((a+b >= 0).expression) == hash(a+b-0)
    assert hash((a+b == np.float64(0)).expression) == hash(a+b-np.float64(0))
    assert hash((a+b <= np.float64(0)).expression) == hash(a+b-np.float64(0))
    assert hash((a+b >= np.float64(0)).expression) == hash(a+b-np.float64(0))


def test_Constraint_feasible(a, b):
    a.setValue(1)
    b.setValue(1)
    assert (a + b <= 2).feasible() == True
    assert (a + b >= 3).feasible() == False
    assert (a + b == 2).feasible() == True
    assert (a + b == 3).feasible() == False


def test_Constraint_repr(a, b):
    repr(a+b <= 0)
