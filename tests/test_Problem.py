import pytest
import numpy as np

from flopt import Variable, Problem, CustomExpression, Solver, Sum


def test_Problem_obj():
    a = Variable("a", ini_value=1, cat="Integer")
    b = Variable("b", ini_value=1, cat="Continuous")

    prob = Problem()
    prob.setObjective(a + b)
    assert prob.getObjectiveValue() == 2


def test_Problem_obj2():
    a = Variable("a", ini_value=1, cat="Integer")
    b = Variable("b", ini_value=1, cat="Continuous")

    prob = Problem()
    prob += a + 2 * b
    assert prob.getObjectiveValue() == 3


def test_Problem_obj3():
    prob = Problem()
    prob += 1
    assert prob.getObjectiveValue() == 1


def test_Problem_getSolution():
    # Variables
    a = Variable("a", lowBound=0, upBound=1, cat="Integer")
    b = Variable("b", lowBound=1, upBound=2, cat="Continuous")
    c = Variable("c", lowBound=1, upBound=3, cat="Continuous")

    # Problem
    prob = Problem(name="Test")
    x = np.array([a, b, c], dtype=object)
    J = np.array([[1, 2, 1], [0, 1, 1], [0, 0, 3]])
    h = np.array([1, 2, 0])
    prob += -(x.T).dot(J).dot(x) - (h.T).dot(x)

    # Solver
    solver = Solver("RandomSearch")
    solver.setParams(max_k=2, timelimit=1)  # set max_k > 1

    # solve
    prob.solve(solver, msg=True)

    from itertools import count

    # get k-top solutions
    for k in count(1):
        try:
            solution = prob.getSolution(k=k)
            prob.setSolution(k=k)
        except IndexError:
            break
        var_dict = solution.toDict()
        print(
            f"{k:2d}-th obj = {prob.obj.value():.4f}",
            {name: f"{var.value():.4f}" for name, var in var_dict.items()},
        )


def test_Problem_duplicate_constraint():
    # Variables
    a = Variable("a", lowBound=0, upBound=1, cat="Integer")
    b = Variable("b", lowBound=1, upBound=2, cat="Continuous")
    c = Variable("c", lowBound=1, upBound=3, cat="Continuous")

    # Problem
    prob = Problem(name="Test")
    prob += a + b >= 0
    prob += a + b >= 0
    prob += a >= -b
    prob += 0 >= -a - b
    prob += Sum([a, b]) >= 0

    prob.removeDuplicatedConstraints()

    assert len(prob.constraints) == 1
