from flopt import Variable

a = Variable('a', lowBound=0, upBound=4, cat='Permutation')
b = Variable('b', lowBound=0, upBound=4, cat='Permutation')

# 四則演算
def test_VarPermutation_hash():
    hash(a)

def test_VarPermutation_eq():
    assert (a == b) is False

# base function
def test_VarPermutation_getType():
    assert a.getType() == 'VarPermutation'

def test_VarPermutation_getVariable():
    assert a.getVariables() == {a}
