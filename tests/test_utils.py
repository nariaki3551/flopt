import pytest

import numpy as np

from flopt import Variable, Problem, CustomExpression
from flopt import Sum, Prod, Dot, Value


def test_Sum1():
    x = [Variable('x'), Variable('y')]
    assert Sum(x).name == (x[0] + x[1]).name

def test_Sum2():
    x = Variable.array('x', 2)
    assert Sum(x).name == (x[0] + x[1]).name

def test_Prod1():
    x = [Variable('x'), Variable('y')]
    assert Prod(x).name == (x[0] * x[1]).name

def test_Prod2():
    x = Variable.array('x', 2)
    assert Prod(x).name == (x[0] * x[1]).name

def test_Dot1():
    x = [Variable('x'), Variable('y')]
    w = [1, 2]
    assert Dot(x, w).name == (x[0] + 2 * x[1]).name

def test_Value1():
    x = Variable('x', ini_value=1)
    assert Value(x) == 1

def test_Value2():
    x = [Variable('x', ini_value=1), Variable('y', ini_value=2)]
    assert Value(x) == [1, 2]

def test_Value3():
    x = (Variable('x', ini_value=1), Variable('y', ini_value=2))
    assert Value(x) == (1, 2)

def test_Value4():
    x = Variable.array('x', 2, ini_value=2)
    assert np.all(Value(x) == 2)
