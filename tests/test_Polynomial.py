import pytest

from flopt import Variable
from flopt.polynomial import Monomial, Polynomial


@pytest.fixture(scope='function')
def x():
    return Variable('x', cat='Integer')

@pytest.fixture(scope='function')
def y():
    return Variable('y', cat='Integer')

@pytest.fixture(scope='function')
def a(x):
    return x.toPolynomial()

@pytest.fixture(scope='function')
def b(y):
    return y.toPolynomial()


def test_Monomial_constructer(x, y):
    print(Monomial({x: 1}))
    print(Monomial({x: 2}))
    print(Monomial({x: 2, y: 2}))
    print(Monomial({x: 2, y: 2}, 3))


def test_Monomial_mul(x, y):
    a = Monomial({x: 1})  # x
    b = Monomial({y: 2})  # y^2
    assert a * b == Monomial({x: 1, y: 2})
    assert 2 * a == Monomial({x: 1}, coeff=2)
    assert a * 2 == Monomial({x: 1}, coeff=2)


def test_Monomial_pow(x, y):
    a = Monomial({x: 1})  # x
    b = Monomial({y: 2})  # y^2
    assert (2*a*b*b) ** 3 == Monomial({x: 3, y: 12}, coeff=8)


def test_Monomial_toPolynomial(x, y):
    a = Monomial({x: 1})  # x
    b = Monomial({y: 2})  # y^2
    assert (a*b).toPolynomial() == Polynomial({Monomial({x: 1, y: 2}): 1})
    assert (2*a*b).toPolynomial() == Polynomial({Monomial({x: 1, y: 2}): 2})


def test_Monomial_maxDegree(x, y):
    assert Monomial({x: 1}).maxDegree() == 1
    assert Monomial({x: 2}).maxDegree() == 2
    assert Monomial({x: 2, y: 2}).maxDegree() == 2
    assert Monomial({x: 2, y: 3}).maxDegree() == 3


def test_Monomial_isLinear(x, y):
    assert Monomial({x: 1}).isLinear() == True
    assert Monomial({x: 1}, coeff=3).isLinear() == True
    assert Monomial({x: 2}).isLinear() == False
    assert Monomial({x: 2, y: 2}).isLinear() == False


def test_Monomial_isQuadratic(x, y):
    assert Monomial({x: 1}).isQuadratic() == True
    assert Monomial({x: 2}).isQuadratic() == True
    assert Monomial({x: 3}).isQuadratic() == False
    assert Monomial({x: 1, y: 1}).isQuadratic() == True
    assert Monomial({x: 1, y: 2}).isQuadratic() == False


def test_Monomial_diff(x, y):
    assert Monomial({x: 2, y: 2}).diff(x) == Monomial({x: 1, y: 2}, coeff=2)
    assert Monomial({x: 2, y: 2}).diff(x).diff(x) == Monomial({y: 2}, coeff=2)
    assert Monomial({x: 2, y: 2}).diff(x).diff(x).diff(x) == Monomial(coeff=0)
    assert Monomial({x: 2, y: 2}).diff(x).diff(x).diff(x).diff(x) == Monomial(coeff=0)


def test_Polynomial_constructor(x, y, a, b):
    assert a + 3 == Polynomial({Monomial({x: 1}): 1}, constant=3)
    assert a + b + 2 == Polynomial({Monomial({x: 1}): 1, Monomial({y: 1}): 1}, constant=2)


def test_Polynomial_mul(x, y, a, b):
    assert a * 3 == Polynomial({Monomial({x: 1}): 3})
    assert a * b == Polynomial({Monomial({x: 1, y: 1}): 1})
    assert a * b * 2 == Polynomial({Monomial({x: 1, y: 1}): 2})


def test_Polynomial_pow(x, y, a, b):
    assert a ** 3 == Polynomial({Monomial({x: 3}): 1})
    assert (a * b ** 2) ** 2 == Polynomial({Monomial({x: 2, y: 4}): 1})


def test_Polynomial_pow(x, y, a, b):
    assert (a * 3).maxDegree() == 1
    assert (a * b*b).maxDegree() == 2
    assert (b ** 4).maxDegree() == 4


def test_Polynomial_isLinear(x, y, a, b):
    assert (a * 3).isLinear() == True
    assert (a + 3 * b).isLinear() == True
    assert (a * b).isLinear() == False
    assert (a * b * 2).isLinear() == False



def test_Polynomial_diff(x, y, a, b):
    p = a**2 + b**4
    assert p.diff(x) == 2 * a
    assert p.diff(x).diff(x) == Polynomial(constant=2)
    assert p.diff(x).diff(x).diff(x) == Polynomial(constant=0)


def test_Polynomial_coeff(x, y, a, b):
    mx = Monomial({x: 1})  # x
    my = Monomial({y: 1})  # y
    p = Polynomial({mx*my: 2, mx*mx: 1, mx: -1, my: 3})  # 2xy + xx - x + 3y
    assert p.coeff(x) == -1
    assert p.coeff(y) == 3
    assert p.coeff(x, y) == 2
    assert p.coeff(x, x) == 1
    assert p.coeff(x, x, x) == 0


def test_Polynomial_isConstant(x, y, a, b):
    assert Polynomial(constant=2).isConstant() == True
    assert Polynomial(constant=2).constant() == 2
    assert a.isConstant() == False
