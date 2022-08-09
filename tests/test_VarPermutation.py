import pytest

from flopt import Variable
from flopt.constants import VariableType


@pytest.fixture(scope="function")
def a():
    return Variable("a", lowBound=0, upBound=4, cat="Permutation")


def test_VarPermutation_hash(a):
    hash(a)


# base function
def test_VarPermutation_type(a):
    assert a.type() == VariableType.Permutation


def test_VarPermutation_getVariable(a):
    assert a.getVariables() == {a}


def test_VarPermutation_colne(a):
    from flopt.variable import VarPermutation

    _a = a.clone()
    assert isinstance(_a, VarPermutation)
    assert _a.value() == a.value()
    assert _a.getLb() == a.getLb()
    assert _a.getUb() == a.getUb()
    assert _a.type() == a.type()
