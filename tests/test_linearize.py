import pytest

import numpy as np

import flopt
from flopt import Variable, Problem, CustomExpression, Sum, Prod
from flopt.convert import linearize, binarize


def test_convert_linearize1():
    test_name = """
    Only Objective Linearize Test
    """

    x = Variable.array("x", 3, cat="Binary")

    prob = Problem(test_name)
    prob += x[0] - 2 * x[1] - x[0] * x[1] * x[2]
    print("[ original ]\n", prob.show())

    linearize(prob)
    print("[ linearized ]\n", prob.show())


def test_convert_linearize2():
    test_name = """
    Objective + Constraints Linearize Test
    """
    x = Variable.array("x", 3, cat="Binary")

    prob = Problem(test_name)
    prob += x[0] - 2 * x[1] - x[0] * x[1] * x[2]
    prob += x[0] + x[1] <= 1
    print("[ original ]\n", prob.show())

    linearize(prob)
    print("[ linearized ]\n", prob.show())


def test_convert_linearize3():
    test_name = """
    Objective + Constraints + Mixed various type variable Linearize Test
    """
    x = Variable.array("x", 2, cat="Binary")
    y = Variable.array("y", 1, lowBound=0, upBound=2, cat="Integer")
    z = Variable.array("z", 1, lowBound=0, upBound=3, cat="Continuous")
    x = np.hstack([x, y, z])

    prob = Problem(test_name)
    prob += x[0] - 2 * x[1] - x[0] * x[1] * x[2] - x[0] * x[3]
    prob += x[0] + x[2] <= 2
    print(prob.show())

    linearize(prob)
    print(prob.show())


def test_convert_linearize4():
    test_name = """
    Objective + Constraints + Mixed various type variable Linearize Test
    """
    x = Variable.array("x", 1, cat="Binary")
    y = Variable.array("y", 1, lowBound=0, upBound=2, cat="Integer")
    z = Variable.array("z", 1, lowBound=0, upBound=3, cat="Continuous")
    x = np.hstack([x, y, z])

    prob = Problem(test_name)
    prob += x[1] * x[2]
    prob += x[0] + x[2] <= 2
    print(prob.show())

    linearize(prob)
    print(prob.show())


def test_convert_linearize5():
    test_name = """
    Objective + Constraints + Prod Linearize Test
    """
    x = Variable.array("x", 3, cat="Binary")

    prob = Problem(test_name)
    prob += Prod(x)
    print(prob.show())

    linearize(prob)
    print(prob.show())


def test_convert_linearize6():
    test_name = """
    Objective + Constraints + Sum Linearize Test
    """
    x = Variable.array("x", 3, cat="Binary")

    prob = Problem(test_name)
    prob += Sum(x) * Sum(x)
    print(prob.show())

    linearize(prob)
    print(prob.show())


def test_convert_binarize1():
    x = Variable.array("x", 1, lowBound=1, upBound=3, cat="Integer")

    prob = Problem()
    prob += x[0]
    print("[ original ]\n", prob.show())

    binarize(prob)
    print("[ binarized ]\n", prob.show())

    linearize(prob)
    print(prob.show())
    print("[ linearized ]\n", prob.show())


def test_convert_binarize2():
    x = Variable.array("x", 2, cat="Binary")
    y = Variable.array("y", 1, lowBound=1, upBound=3, cat="Integer")
    x = np.hstack([x, y])

    prob = Problem()
    prob += x[2] * x[0]
    print("[ original ]\n", prob.show())

    binarize(prob)
    print("[ binarized ]\n", prob.show())

    linearize(prob)
    print(prob.show())
    print("[ linearized ]\n", prob.show())


def test_convert_binarize3():
    x = Variable.array("x", 2, cat="Continuous")
    y = Variable.array("y", 1, lowBound=1, upBound=3, cat="Integer")
    x = np.hstack([x, y])

    prob = Problem()
    prob += x[2] * x[0] + x[1]
    print("[ original ]\n", prob.show())

    binarize(prob)
    print("[ binarized ]\n", prob.show())

    linearize(prob)
    print(prob.show())
    print("[ linearized ]\n", prob.show())


def test_convert_binarize4():
    x = Variable.array("x", 2, cat="Spin")
    y = Variable.array("y", 1, lowBound=1, upBound=3, cat="Integer")
    x = np.hstack([x, y])

    prob = Problem()
    prob += x[2] * x[0] + x[1]
    print("[ original ]\n", prob.show())

    binarize(prob)
    print("[ binarized ]\n", prob.show())

    linearize(prob)
    print(prob.show())


def test_convert_binarize5():
    x = Variable.array("x", 2, lowBound=1, upBound=2, cat="Integer")
    y = x * x

    prob = Problem()
    prob += flopt.Sum(y)
    print("[ original ]\n", prob.show())

    binarize(prob)
    print("[ binarized ]\n", prob.show())

    linearize(prob)
    print(prob.show())
    print("[ linearized ]\n", prob.show())


def test_convert_binarize6():
    x = Variable.array("x", 2, lowBound=1, upBound=2, cat="Integer")

    prob = Problem()
    prob += flopt.Prod(x)
    print("[ original ]\n", prob.show())

    binarize(prob)
    print("[ binarized ]\n", prob.show())

    linearize(prob)
    print(prob.show())
    print("[ linearized ]\n", prob.show())


def test_convert_binarize7():
    x = Variable.array("x", 2, lowBound=1, upBound=2, cat="Integer")
    prob = Problem()
    prob += x[0] >= 1
    binarize(prob)
    linearize(prob)
