import pytest

from math import sqrt
import numpy as np

from flopt import Variable, Solution


@pytest.fixture(scope="function")
def b():
    _b = [
        Variable(f"b{i}", lowBound=0, upBound=10, ini_value=i + 1, cat="Continuous")
        for i in range(2)
    ]
    return Solution(_b)


@pytest.fixture(scope="function")
def c():
    _c = [
        Variable(f"c{i}", lowBound=0, upBound=10, ini_value=2 * i, cat="Continuous")
        for i in range(2)
    ]
    return Solution(_c)


@pytest.fixture(scope="function")
def d():
    return [1, 1]


@pytest.fixture(scope="function")
def f():
    _f = [
        Variable(f"f{i}", lowBound=0, upBound=10, ini_value=2 * i, cat="Integer")
        for i in range(2)
    ]
    return Solution(_f)


@pytest.fixture(scope="function")
def g():
    return [0.1, 0.2]


def test_Solution_value_1(b, c):
    assert np.all(b.value() == [1, 2])
    assert np.all(c.value() == [0, 2])


def test_Solution_value_2(b, c):
    assert np.all(b.value(c) == [0, 2])


def test_Solution_clone(b):
    assert np.all((b.clone()).value() == [1, 2])


def test_Solution_pos(b):
    assert np.all((+b).value() == [1, 2])


def test_Solution_neg(b):
    assert np.all((-b).value() == [-1, -2])


def test_Solution_add(b, c, d, f, g):
    assert np.all((b + c).value() == [1, 4])
    assert np.all((b + d).value() == [2, 3])
    assert np.all((b + np.array(d)).value() == [2, 3])
    assert np.all((f + g).value() == list(map(int, [0.1, 2.2])))
    assert np.all((d + b).value() == [2, 3])
    assert np.all((b + 1).value() == [2, 3])
    assert np.all((1 + b).value() == [2, 3])
    assert np.all((b + 1.0).value() == [2, 3])
    assert np.all((1.0 + b).value() == [2, 3])
    assert np.all((b + np.float64(1.0)).value() == [2, 3])


def test_Solution_sub(b, c, d):
    assert np.all((b - c).value() == [1, 0])
    assert np.all((b - d).value() == [0, 1])
    assert np.all((c - b).value() == [-1, 0])
    assert np.all((d - b).value() == [0, -1])
    assert np.all((b - 1).value() == [0, 1])
    assert np.all((b - 2.0).value() == [-1, 0])
    assert np.all((b - np.float64(2.0)).value() == [-1, 0])


def test_Solution_mul_s(b, c):
    assert np.all((b * c).value() == [0, 4])  # [1, 2] * [0, 2]


def test_Solution_doc(b, c):
    assert np.all(b.dot(c) == 0 + 4)  # [1, 2] dot [0, 2]


def test_Solution_mul(b):
    assert np.all((b * 2).value() == [2, 4])
    assert np.all((2 * b).value() == [2, 4])
    assert np.all((b * 2.0).value() == [2, 4])
    assert np.all((2.0 * b).value() == [2, 4])
    assert np.all((b * np.float64(2.0)).value() == [2, 4])


def test_Solution_div(b, d):
    assert np.all((b / d).value() == [1, 2])
    assert np.all((b / 2).value() == [0.5, 1])
    assert np.all((b / 2.0).value() == [0.5, 1])
    assert np.all((b / np.float64(2.0)).value() == [0.5, 1])


def test_Solution_squaredNorm(b):
    assert b.squaredNorm() == sum((1 + i) * (1 + i) for i in range(2))


def test_Solution_norm(b):
    assert b.norm() == sqrt(sum((1 + i) * (1 + i) for i in range(2)))


def test_Solution_len(b):
    assert len(b) == 2


def test_Solution_abs():
    a = [Variable(f"b{i}", ini_value=i - 2) for i in range(2)]
    sol_a = Solution(a)
    assert np.all(abs(sol_a).value() == [2, 1])


def test_Solution_getitem(b):
    b[0].value() == 1
    b[1].value() == 2


def test_Solution_hash(b):
    hash(b)


def test_Solution_repr(b):
    repr(b)


def test_Solution_feasible(b):
    assert b.feasible()
    assert not (11 * b).feasible()


def test_Solution_clip(b):
    e = 3 * b
    e.clip()
    assert np.all(e.value() == [3, 6])
