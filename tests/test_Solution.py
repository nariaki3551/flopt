import pytest
from math import sqrt

from flopt import Variable, Solution

@pytest.fixture(scope='function')
def b():
    _b = [Variable(f'b{i}', lowBound=0, upBound=10, ini_value=i+1, cat='Continuous') for i in range(5)]
    return Solution('b', _b )

@pytest.fixture(scope='function')
def c():
    _c = [Variable(f'c{i}', lowBound=0, upBound=10, ini_value=2*i, cat='Continuous') for i in range(5)]
    return Solution('c', _c )

@pytest.fixture(scope='function')
def d():
    return [1, 1, 1, 1, 1]

@pytest.fixture(scope='function')
def f():
    _f = [Variable(f'f{i}', lowBound=0, upBound=10, ini_value=2*i, cat='Integer') for i in range(5)]
    return Solution('f', _f )

@pytest.fixture(scope='function')
def g():
    return [0.1, 0.2, 0.3, 0.4, 0.5]

def test_Solution_value_1(b, c):
    assert b.value() == [1, 2, 3, 4, 5]
    assert c.value() == [0, 2, 4, 6, 8]

def test_Solution_clone(b):
    assert (b.clone()).value() == [1, 2, 3, 4, 5]

def test_Solution_pos(b):
    assert (+b).value() == [1, 2, 3, 4, 5]

def test_Solution_neg(b):
    assert (-b).value() == [-1, -2, -3, -4, -5]

def test_Solution_add(b, c, d, f, g):
    assert (b+c).value() == [1, 4, 7, 10, 13]
    assert (b+d).value() == [2, 3, 4, 5, 6]
    assert (f+g).value() == list(map(int, [0.1, 2.2, 4.3, 6.4, 8.5]))
    assert (d+b).value() == [2, 3, 4, 5, 6]
    assert (b+1).value() == [2, 3, 4, 5, 6]
    assert (1+b).value() == [2, 3, 4, 5, 6]

def test_Solution_sub(b, c, d):
    assert (b-c).value() == [1, 0, -1, -2, -3]
    assert (b-d).value() == [0, 1, 2, 3, 4]
    assert (c-b).value() == [-1, 0, 1, 2, 3]
    assert (d-b).value() == [0, -1, -2, -3, -4]

def test_Solution_mul_s(b, c):
    assert (b*c).value() == [0, 4, 12, 24, 40]  # [1, 2, 3, 4, 5] * [0, 2, 4 ,6, 8]

def test_Solution_doc(b, c):
    assert b.dot(c) == 0 + 4 + 12 + 24 + 40 # [1, 2, 3, 4, 5] dot [0, 2, 4 ,6, 8]

def test_Solution_mul(b):
    assert (b*2).value() == [2, 4, 6, 8, 10]
    assert (2*b).value() == [2, 4, 6, 8, 10]

def test_Solution_div(b, d):
    assert (b/d).value() == [1, 2, 3, 4, 5]
    assert (b/2).value() == [0.5, 1, 1.5, 2, 2.5]

def test_Solution_squaredNorm(b):
    assert b.squaredNorm() == sum((1+i)*(1+i) for i in range(5))

def test_Solution_norm(b):
    assert b.norm() == sqrt(sum((1+i)*(1+i) for i in range(5)))

def test_Solution_len(b):
    assert len(b) == 5

def test_Solution_hash(b):
    hash(b)

def test_Solution_repr(b):
    repr(b)

def test_Solution_feasible(b):
    assert b.feasible()
    assert not (3*b).feasible()

def test_Solution_clip(b):
    e = 3*b
    e.clip()
    assert e.value() == [3, 6, 9, 10, 10]
