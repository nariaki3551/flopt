import pytest

import numpy as np

from flopt import Variable, Problem, CustomExpression
from flopt import Sum, Prod, Dot, Value, get_dot_graph


def test_Sum1():
    x = [Variable("x"), Variable("y")]
    assert Sum(x).name == (x[0] + x[1]).name


def test_Sum2():
    x = Variable.array("x", 2)
    assert Sum(x).name == (x[0] + x[1]).name


def test_Prod1():
    x = [Variable("x"), Variable("y")]
    assert Prod(x).name == (x[0] * x[1]).name


def test_Prod2():
    x = Variable.array("x", 2)
    assert Prod(x).name == (x[0] * x[1]).name


def test_Dot1():
    x = [Variable("x"), Variable("y")]
    w = [1, 2]
    assert Dot(x, w).name == (x[0] + 2 * x[1]).name


def test_Value1():
    x = Variable("x", ini_value=1)
    assert Value(x) == 1


def test_Value2():
    x = [Variable("x", ini_value=1), Variable("y", ini_value=2)]
    assert Value(x) == [1, 2]


def test_Value3():
    x = (Variable("x", ini_value=1), Variable("y", ini_value=2))
    assert Value(x) == (1, 2)


def test_Value4():
    x = Variable.array("x", 2, ini_value=2)
    assert np.all(Value(x) == 2)


def test_dot_graph_Expression(tmpdir):
    a = Variable("a", lowBound=0, upBound=1, cat="Continuous")
    b = Variable("b", lowBound=1, upBound=2, cat="Continuous")
    c = Variable("c", upBound=3, cat="Continuous")

    z = 2 * (3 * a + b) * c**2 + 3

    path = tmpdir.mkdir("save").join("tmp1.txt")
    get_dot_graph(z, path)


def test_dot_graph_CustomExpression(tmpdir):
    a = Variable("a", lowBound=0, upBound=1, cat="Continuous")
    b = Variable("b", lowBound=1, upBound=2, cat="Continuous")
    c = Variable("c", upBound=3, cat="Continuous")

    def custom(a, b, c):
        return a + b * c

    z = CustomExpression(func=custom, arg=[a, b, c])

    path = tmpdir.mkdir("save").join("tmp2.txt")
    get_dot_graph(z, path)


def test_dot_graph_Sum(tmpdir):
    x = Variable.array("x", 6)

    z = Sum(x)

    path = tmpdir.mkdir("save").join("tmp3.txt")
    get_dot_graph(z, path)


def test_dot_graph_Prod(tmpdir):
    x = Variable.array("x", 6)

    z = Prod(x)

    path = tmpdir.mkdir("save").join("tmp4.txt")
    get_dot_graph(z, path)
