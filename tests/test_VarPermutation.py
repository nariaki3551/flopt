import pytest

from flopt import Variable

@pytest.fixture(scope='function')
def a():
    return Variable('a', lowBound=0, upBound=4, cat='Permutation')

def test_VarPermutation_hash(a):
    hash(a)

# base function
def test_VarPermutation_getType(a):
    assert a.getType() == 'VarPermutation'

def test_VarPermutation_getVariable(a):
    assert a.getVariables() == {a}
