import pytest

import numpy as np

from flopt import Variable, Problem, CustomExpression
from flopt.convert import linearize, binarize

def test_convert_linearize1():
    x = Variable.array('x', 3, cat='Binary')

    prob = Problem()
    prob += x[0] - 2*x[1] - x[0]*x[1]*x[2]
    print('[ original ]\n', prob.show())

    linearize(prob)
    print('[ linearized ]\n', prob.show())


def test_convert_linearize2():
    x = Variable.array('x', 3, cat='Binary')

    prob = Problem()
    prob += x[0] - 2*x[1] - x[0]*x[1]*x[2]
    prob += x[0] + x[1] <= 1
    print('[ original ]\n', prob.show())

    linearize(prob)
    print('[ linearized ]\n', prob.show())


def test_convert_linearize3():
    x = Variable.array('x', 2, cat='Binary')
    y = Variable.array('y', 1, lowBound=0, upBound=2, cat='Integer')
    z = Variable.array('z', 1, lowBound=0, upBound=3, cat='Continuous')
    x = np.hstack([x, y, z])

    prob = Problem()
    prob += x[0] - 2*x[1] - x[0]*x[1]*x[2] - x[0]*x[3]
    prob += x[0] + x[2] <= 2
    print(prob.show())

    linearize(prob)
    print(prob.show())


def test_convert_binarize1():
    x = Variable.array('x', 2, cat='Binary')
    y = Variable.array('y', 1, lowBound=1, upBound=3, cat='Integer')
    x = np.hstack([x, y])

    prob = Problem()
    prob += x[2] * x[0] + x[1]
    print('[ original ]\n', prob.show())

    binarize(prob)
    print('[ binarized ]\n', prob.show())

    linearize(prob)
    print(prob.show())
    print('[ linearized ]\n', prob.show())
