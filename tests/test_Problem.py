import pytest

from flopt import Variable, Problem, CustomExpression

@pytest.fixture(scope='function')
def a():
    return Variable('a', ini_value=0, cat='Binary')

@pytest.fixture(scope='function')
def b():
    return Variable('b', ini_value=2, cat='Continuous')

def test_Problem_obj(a, b):
    prob = Problem()
    prob.setObjective(a+b)
    assert prob.getObjectiveValue() == 2

def test_Problem_obj2(a, b):
    prob = Problem()
    prob += a + 2*b
    assert prob.getObjectiveValue() == 4

def test_Problem_obj3(a, b):
    prob = Problem()
    prob += 1
    assert prob.getObjectiveValue() == 1
