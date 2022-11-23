import pytest
import numpy as np

import flopt
from flopt import Variable
from flopt.polynomial import Monomial, Polynomial
from flopt.expression import Expression, Const
from flopt.env import get_variable_lower_bound, get_variable_upper_bound


@pytest.fixture(scope="function")
def a():
    return Variable(name="a", lowBound=1, upBound=5, ini_value=2, cat="Continuous")


@pytest.fixture(scope="function")
def b():
    return Variable(name="b", lowBound=1, upBound=5, ini_value=3, cat="Continuous")


@pytest.fixture(scope="function")
def c(a, b):
    return a + b


def test_Expression(c):
    assert c.value() == 5


def test_Expression_add(c, a):
    assert (c + 1).value() == 6
    assert (1 + c).value() == 6
    assert (c + 1.0).value() == 6
    assert (1.0 + c).value() == 6
    assert (c + a).value() == 7
    assert (a + c).value() == 7
    assert ((a + c) + (a + c)).value() == 14


def test_Expression_sub(c, a):
    assert (c - 1).value() == 4
    assert (c - -1).value() == 6
    assert (1 - c).value() == -4
    assert (c - 1.0).value() == 4
    assert (1.0 - c).value() == -4
    assert (c - a).value() == 3
    assert (a - c).value() == -3
    assert ((a + c) - (a + c)).value() == 0


def test_Expression_mul(c, a):
    assert (c * 2).value() == 10
    assert (2 * c).value() == 10
    assert (c * 2.0).value() == 10
    assert (2.0 * c).value() == 10
    assert (c * a).value() == 10
    assert (a * c).value() == 10
    assert (c * 0) == Const(0)
    assert (c * 1) == c
    assert (c * -1) == -c
    assert (0 * c) == Const(0)
    assert (1 * c) == c
    assert (-1 * c) == -c
    assert (2 * a) * (3 * c) == 6 * (a * c)
    assert (2 * a) * c == 2 * (a * c)
    assert (2 + a) * (2 * a) == 2 * ((2 + a) * a)
    assert (2 + a) * (2 + a)


def test_Expression_div(c, a):
    assert (c / 2).value() == 2.5
    assert (2 / c).value() == 0.4
    assert (c / 2.0).value() == 2.5
    assert (2.0 / c).value() == 0.4
    assert (c / a).value() == 2.5
    assert (a / c).value() == 0.4
    assert (c / 1) == c
    assert (0 / c) == Const(0)


def test_Expression_pow(c, a):
    assert (c**2).value() == 25
    assert (2**c).value() == 32
    assert (c**2.0).value() == 25
    assert (2.0**c).value() == 32
    assert (c**a).value() == 25
    assert (a**c).value() == 32
    assert (c**1) == c
    assert (c**c).value() == 5**5
    assert (1**c) == Const(1)


def test_Expression_and():
    a = Variable(name="a", ini_value=2, cat="Integer")
    b = Variable(name="b", ini_value=1, cat="Integer")
    c = a + b
    assert (c & 1).value() == c.value() & 1
    assert (1 & c).value() == 1 & c.value()


def test_Expression_or():
    a = Variable(name="a", ini_value=2, cat="Integer")
    b = Variable(name="b", ini_value=1, cat="Integer")
    c = a + b
    assert (c | 1).value() == c.value() | 1
    assert (1 | c).value() == 1 | c.value()


def test_Expression_setPolynomial(a, b, c):
    assert (a + b).setPolynomial() == Polynomial(
        {Monomial({a: 1}): 1, Monomial({b: 1}): 1}
    )
    assert (a + b + c).setPolynomial() == Polynomial(
        {Monomial({a: 1}): 2, Monomial({b: 1}): 2}
    )
    assert (3 * a).setPolynomial() == Polynomial({Monomial({a: 1}): 3})
    assert (a * 3).setPolynomial() == Polynomial({Monomial({a: 1}): 3})
    assert (a / 3).setPolynomial() == Polynomial({Monomial({a: 1}): 1.0 / 3})
    assert (2 * a**3).setPolynomial() == Polynomial({Monomial({a: 3}): 2})
    assert (a - b).setPolynomial() == Polynomial(
        {Monomial({a: 1}): 1, Monomial({b: 1}): -1}
    )


def test_Expression_getVariable(a, b, c):
    assert c.getVariables() == {a, b}


def test_Expression_constant1(a):
    assert (a + 1).constant() == 1


def test_Expression_constant2(a, b):
    assert (a / b + 1).constant() == 1


def test_Expression_isMonomial1(a, b):
    assert (2 * a).isMonomial() == True
    assert (2 * a * b).isMonomial() == True
    assert (a + 1).isMonomial() == False
    assert (a / b).isMonomial() == False


def test_Expression_isMonomial2(a, b):
    assert (2 * a).toMonomial() == Monomial({a: 1}, coeff=2)
    assert (2 * a * b).toMonomial() == Monomial({a: 1, b: 1}, coeff=2)


def test_Expression_toLinear1(a, b):
    lp = (a + b + 1).toLinear([a, b])
    assert lp.C == 1
    assert np.all(lp.c == [1, 1])


def test_Expression_toLinear2(a, b):
    lp = (a + b + 1).toLinear([a])
    # assert (lp.C).value() == (b + 1).value()
    assert lp.C == (b + 1).value()
    assert np.all(lp.c == [1])


def test_Expression_toQuadratic1(a, b):
    qp = (a * a + a * b + b + 1).toQuadratic([a, b])
    assert np.all(qp.Q == [[2, 1], [1, 0]])
    assert np.all(qp.c == [0, 1])
    assert qp.C == 1


def test_Expression_toQuadratic2(a, b):
    qp = (a * a + a * b + b + 1).toQuadratic([a])
    assert np.all(qp.Q == [[2]])
    assert np.all(qp.c == [b])
    # assert (qp.C).value() == (b + 1).value()
    assert qp.C == (b + 1).value()


def test_Expression_simplify(a, b):
    (a + 1 - a).simplify()
    (a * a + a * b + a).simplify()


def test_Expression_expand(a, b):
    (a + 1 - a).expand()
    (a * a + a * b + a).expand()


def test_Expression_toBinary():
    b = Variable("bb", cat="Binary")
    s = Variable("ss", cat="Spin")
    i = Variable("ii", lowBound=-1, upBound=1, cat="Integer")
    print((b + 1).toBinary())
    print((s + 1).toBinary())
    print((i + 1).toBinary())


def test_Expression_toSpin():
    b = Variable("bb", cat="Binary")
    s = Variable("ss", cat="Spin")
    i = Variable("ii", lowBound=-1, upBound=1, cat="Integer")
    print((b + 1).toSpin())
    print((s + 1).toSpin())
    print((i + 1).toSpin())


def test_Expression_max():
    a = Variable(name="a", lowBound=1, upBound=5)
    b = Variable(name="b", lowBound=1, upBound=5)
    c = a + b
    assert np.isclose((a + b + c).max(), 20)

    assert np.isclose((a * a).max(), 25)

    # not linear or quadratic
    assert np.isclose((a * a * a).max(), get_variable_upper_bound())

    # unbounded
    z = Variable("z")
    assert np.isclose(z.max(), get_variable_upper_bound())
    assert np.isclose((z + 1.0).max(), get_variable_upper_bound())


def test_Expression_min():
    a = Variable(name="a", lowBound=1, upBound=5)
    b = Variable(name="b", lowBound=1, upBound=5)
    c = a + b
    assert np.isclose((a + b + c).min(), 4)

    assert np.isclose((a * a).min(), 1)

    # not linear or quadratic
    assert np.isclose((a * a * a).min(), get_variable_lower_bound())

    # unbounded
    z = Variable("z")
    assert np.isclose(z.min(), get_variable_lower_bound())
    assert np.isclose((z + 1.0).min(), get_variable_lower_bound())


def test_Expression_neg(c):
    assert (-c).value() == -5


def test_Expression_pos(c):
    assert (+c).value() == 5


def test_Expression_abs(c):
    assert abs(c) == 5
    assert abs(-c) == 5


def test_Expression_cas(c):
    assert isinstance(int(c), int)
    assert isinstance(float(c), float)


def test_Expression_hash(c):
    hash(c)


def test_Expression_isLinear(a, b, c):
    assert a.isLinear() == True
    assert c.isLinear() == True
    assert (a * b).isLinear() == False


def test_Expression_fromPolynominal():
    x = Variable("x", cat="Integer")
    y = Variable("y", cat="Integer")
    polynomial = Polynomial({Monomial({x: 3}): 1, Monomial({y: 2}): 2})  # x^3 + 2*y^2
    print(Expression.fromPolynomial(polynomial))


def test_Expression_jac1():
    x = Variable.array("x", 2, cat="Integer")
    exp = x[0] ** 3 + 2 * x[1] ** 2 + x[0] * x[1]
    jac = exp.jac(x)
    assert jac[0] == 3 * x[0] ** 2 + x[1]
    assert jac[1] == 4 * x[1] + x[0]


def test_Expression_jac2():
    x = Variable.array("x", 2, cat="Integer")
    exp1 = flopt.Sum(x * x)
    exp2 = x[0] * x[0] + x[1] * x[1]
    assert np.all(exp1.jac(x) == exp2.jac(x))


def test_Const_constant():
    assert Const(1).constant() == 1


def test_Const_setPolynominal():
    Const(0).setPolynomial()


def test_Const_constant():
    assert Const(1).constant() == 1


def test_Const_isMonomial():
    assert Const(0).isMonomial() == True


def test_Const_toMonomial():
    assert Const(0).toMonomial()


def test_Const_isLinear():
    assert Const(0).isLinear() == True


def test_Const_toLinear():
    assert Const(0).toLinear()


def test_Const_toQuadratic():
    assert Const(0).toQuadratic()


def test_Const_simplify():
    assert Const(1).simplify() == Const(1)


def test_Const_add():
    assert Const(1) + 3 == Const(4)
    assert 3 + Const(1) == Const(4)


def test_Const_sub(a):
    assert Const(1) - 3 == Const(-2)
    assert 3 - Const(1) == Const(2)
    assert a - Const(-1) == a + 1


def test_Const_div(a):
    assert Const(1) / 3 == Const(1 / 3)
    assert Const(1) / a == 1 / a
    assert a / Const(1) == a


def test_Const_pow(a):
    assert Const(2) ** 2 == Const(4)
    assert 2 ** Const(2) == Const(4)


def test_Const_hash():
    hash(Const(0))


def test_Expression_isIsing(a, b):

    x = np.array([Variable("a", cat="Spin"), Variable("b", cat="Spin")])
    J = np.array(
        [
            [1, 2],
            [0, 1],
        ]
    )
    h = np.array([1, 2])
    obj = -(x.T).dot(J).dot(x) - (h.T).dot(x)
    assert obj.isIsing()


def test_Expression_toIsing(a, b):
    x = np.array([Variable("a", cat="Spin"), Variable("b", cat="Spin")])
    J = np.array(
        [
            [1, 2],
            [0, 1],
        ]
    )
    h = np.array([1, 2])
    obj = -(x.T).dot(J).dot(x) - (h.T).dot(x)
    obj.toIsing()


def test_Expression_Exp1(a):
    exp = flopt.exp(a)
    assert exp.value() == np.exp(a.value())
    assert exp.getName() == "Exp(a)"
    assert list(exp.getChildren()) == [a]
    assert exp.isPolynomial() == False
    assert exp.getVariables() == {a}
    assert exp.isNeg() == False
    assert exp.__repr__()


def test_Expression_Exp2():
    x = flopt.Variable.array("x", 2)
    exp = flopt.exp(x)
    assert exp[0] == flopt.exp(x[0])
    assert exp[1] == flopt.exp(x[1])


def test_Expression_Cos(a):
    exp = flopt.cos(a)
    assert exp.value() == np.cos(a.value())
    assert exp.getName() == "Cos(a)"


def test_Expression_Sin(a):
    exp = flopt.sin(a)
    assert exp.value() == np.sin(a.value())
    assert exp.getName() == "Sin(a)"


def test_Expression_Log(a):
    exp = flopt.log(a)
    assert exp.value() == np.log(a.value())
    assert exp.getName() == "Log(a)"


def test_Expression_Abs(a):
    exp = flopt.abs(a)
    assert exp.value() == np.abs(a.value())
    assert exp.getName() == "Abs(a)"


def test_Expression_Floor(a):
    exp = flopt.floor(a)
    assert exp.value() == np.floor(a.value())
    assert exp.getName() == "Floor(a)"


def test_Expression_Ceil(a):
    exp = flopt.ceil(a)
    assert exp.getName() == "Ceil(a)"
