import pytest

import numpy as np

from flopt import Variable, CustomExpression
from flopt.expression import Expression, Const
from flopt.constants import ConstraintType


@pytest.fixture(scope="function")
def a():
    return Variable("a", lowBound=1, upBound=3, ini_value=2, cat="Integer")


@pytest.fixture(scope="function")
def b():
    return Variable("b", lowBound=1, upBound=3, ini_value=2, cat="Continuous")


def test_Constraint_type(a, b):
    assert (a == 0).type() == ConstraintType.Eq
    assert (a <= 0).type() == ConstraintType.Le
    assert (a >= 0).type() == ConstraintType.Le
    assert (a + b == 0).type() == ConstraintType.Eq
    assert (a + b <= 0).type() == ConstraintType.Le
    assert (a + b >= 0).type() == ConstraintType.Le
    assert (0 == a + b).type() == ConstraintType.Eq
    assert (0 <= a + b).type() == ConstraintType.Le
    assert (0 >= a + b).type() == ConstraintType.Le

    assert (a + b == np.float64(0)).type() == ConstraintType.Eq
    assert (a + b <= np.float64(0)).type() == ConstraintType.Le
    assert (a + b >= np.float64(0)).type() == ConstraintType.Le
    # assert (np.float64(0) == a+b).type() == ConstraintType.Eq
    # assert (np.float64(0) <= a+b).type() == ConstraintType.Le
    # assert (np.float64(0) >= a+b).type() == ConstraintType.Le


def test_Constraint_expression(a, b):
    assert hash((a == 0).expression) == hash(Expression(a, Const(0), "+"))
    assert hash((a <= 0).expression) == hash(Expression(a, Const(0), "+"))
    assert hash((a >= 0).expression) == hash(Expression(Const(-1), a, "*"))
    assert hash((a + b == 0).expression) == hash(a + b - 0)
    assert hash((a + b <= 0).expression) == hash(a + b - 0)
    assert hash((a + b >= 0).expression) == hash(-(a + b - 0))
    assert hash((a + b == np.float64(0)).expression) == hash(a + b - np.float64(0))
    assert hash((a + b <= np.float64(0)).expression) == hash(a + b - np.float64(0))
    assert hash((a + b >= np.float64(0)).expression) == hash(-(a + b - np.float64(0)))


def test_Constraint_feasible(a, b):
    a.setValue(1)
    b.setValue(1)
    assert (a + b <= 2).feasible() == True
    assert (a + b >= 3).feasible() == False
    assert (a + b == 2).feasible() == True
    assert (a + b == 3).feasible() == False


def test_Constraint_rshift(a, b):
    assert len((a + b <= 2) >> (b >= 0)) == 2
    assert len((a + b <= 2) >> (b == 0)) == 3
    assert len((a + b == 2) >> (b >= 0)) == 4
    assert len((a + b == 2) >> (b == 0)) == 5


def test_Constraint_hash(a, b):
    assert hash(a == 1) == hash(a - 1 == 0)
    assert hash(a >= 0) == hash(-a <= 0)
    assert hash(a - b <= 0) == hash(a <= b)
    assert hash(a + b <= 0) == hash(a <= -b)
    assert hash(a + b <= 0) == hash(a <= -b)


def test_Constraint_repr(a, b):
    repr(a + b <= 0)
