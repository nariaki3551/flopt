import pytest

from flopt import Variable, Problem, CustomExpression, Solver
import numpy as np


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


def test_Problem_getSolution(a, b):
    # Variables
    a = Variable('a', lowBound=0, upBound=1, cat='Integer')
    b = Variable('b', lowBound=1, upBound=2, cat='Continuous')
    c = Variable('c', lowBound=1, upBound=3, cat='Continuous')

    # Problem
    prob = Problem(name='Test')
    x = np.array([a, b, c], dtype=object)
    J = np.array([
        [1, 2, 1],
        [0, 1, 1],
        [0, 0, 3]
    ])
    h = np.array([1, 2, 0])
    prob += - (x.T).dot(J).dot(x) - (h.T).dot(x)

    # Solver
    solver = Solver('RandomSearch')
    solver.setParams(max_k=2, timelimit=1)  # set max_k > 1

    # solve
    prob.solve(solver, msg=True)

    from itertools import count
    # get k-top solutions
    for k in count(0):
        try:
            solution = prob.getSolution(k=k)
            prob.setSolution(k=k)
        except KeyError:
            break
        var_dict = solution.toDict()
        print(f'{k:2d}-th obj = {prob.obj.value():.4f}',
              {name: f'{var.value():.4f}' for name, var in var_dict.items()})
