import pytest

import numpy as np

import flopt
import flopt.convert
from flopt import Variable, Problem, Solver


def test_QuadraticStructure():
    from flopt.convert import QuadraticStructure

    Q = [[1, 1], [1, 2]]
    c = [1, 1]
    C = 0
    qs = QuadraticStructure(Q, c, C)
    try:
        qs.toLinear()
    except flopt.ConversionError:
        assert True
        return True
    assert False

    Q = None
    c = [1, 1]
    C = 0
    qs = QuadraticStructure(Q, c, C)
    try:
        qs.toLinear()
    except flopt.ConversionError:
        assert False
        return True
    assert True


def test_flopt_to_qp1():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")
    c = Variable("c", lowBound=-1, upBound=2, cat="Integer")
    d = Variable("d", lowBound=-2, upBound=1, cat="Continuous")

    # Problem
    prob = Problem()
    prob += a * a + c * b  # set the objective function
    prob += a + c == 0  # set the constraint
    prob += a + b <= 1  # set the constraint
    prob += a + d >= -1  # set the constraint
    print(prob)

    from flopt.convert import QpStructure

    qp = QpStructure.fromFlopt(prob, progress=True)
    print(qp)

    qp.toEq()
    qp.toIneq()
    qp.show()


def test_flopt_to_qp2():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")

    # Problem
    prob = Problem()
    prob += a + b  # set the objective function
    print(prob)

    from flopt.convert import QpStructure

    qp = QpStructure.fromFlopt(prob)
    print(qp)

    qp.toEq()
    qp.toIneq()
    qp.toLp()
    qp.toIsing()
    qp.toQubo()


def test_flopt_to_qp3():

    # list of numbers
    A = [1, 2]

    prob = Problem()

    # create variables
    x = Variable.array("x", len(A), cat="Spin")

    # set objective function
    prob += flopt.Dot(x, A) ** 2

    # binarize from spin variables
    flopt.convert.binarize(prob)
    qp = flopt.convert.QpStructure.fromFlopt(prob)
    assert qp.Q.shape == (2, 2)
    assert (qp.Q == np.array([[0.0, 16.0], [16.0, 0.0]])).all()
    assert (qp.c == np.array([-8.0, -8.0])).all()
    assert qp.C == 9


def test_flopt_to_lp1():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")
    c = Variable("c", lowBound=-1, upBound=2, cat="Integer")
    d = Variable("d", lowBound=-2, upBound=1, cat="Continuous")

    # Problem
    prob = Problem()
    prob += c + b  # set the objective function
    prob += a + c == 0  # set the constraint
    prob += a + b <= 1  # set the constraint
    prob += a + d >= -1  # set the constraint
    print(prob)

    from flopt.convert import LpStructure

    lp = LpStructure.fromFlopt(prob)
    print(lp)

    lp.toEq()
    lp.toIneq()
    lp.toQp()
    lp.show()


def test_flopt_to_lp2():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")

    # Problem
    prob = Problem()
    prob += a + b  # set the objective function
    print(prob)

    from flopt.convert import LpStructure

    lp = LpStructure.fromFlopt(prob)
    print(lp)

    lp.toEq()
    lp.toIneq()
    lp.toQp()
    lp.toIsing()
    lp.toQubo()


def test_flopt_to_lp_ineq():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")
    c = Variable("c", lowBound=-1, upBound=2, cat="Integer")
    d = Variable("d", lowBound=-2, upBound=1, cat="Continuous")

    # Problem
    prob = Problem()
    prob += c + b  # set the objective function
    prob += a + c == 0  # set the constraint
    prob += a + b <= 1  # set the constraint
    prob += a + d >= -1  # set the constraint
    print(prob)

    from flopt.convert import LpStructure

    lp = LpStructure.fromFlopt(prob, option="ineq")


def test_flopt_to_lp_eq():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")
    c = Variable("c", lowBound=-1, upBound=2, cat="Integer")
    d = Variable("d", lowBound=-2, upBound=1, cat="Continuous")

    # Problem
    prob = Problem()
    prob += c + b  # set the objective function
    prob += a + c == 0  # set the constraint
    prob += a + b <= 1  # set the constraint
    prob += a + d >= -1  # set the constraint
    print(prob)

    from flopt.convert import LpStructure

    lp = LpStructure.fromFlopt(prob, option="eq")


def test_flopt_to_lp1():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")
    c = Variable("c", lowBound=-1, upBound=2, cat="Integer")
    d = Variable("d", lowBound=-2, upBound=1, cat="Continuous")

    # Problem
    prob = Problem()
    prob += c + b  # set the objective function
    prob += a + c == 0  # set the constraint
    prob += a + b <= 1  # set the constraint
    prob += a + d >= -1  # set the constraint
    print(prob)

    from flopt.convert import LpStructure

    lp = LpStructure.fromFlopt(prob)
    print(lp)

    lp.toEq()
    lp.toIneq()
    lp.toQp()


def test_flopt_to_lp1():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")

    # Problem
    prob = Problem()
    prob += a + b  # set the objective function
    print(prob)

    from flopt.convert import LpStructure

    lp = LpStructure.fromFlopt(prob)
    print(lp)

    lp.toEq()
    lp.toIneq()
    lp.toQp()
    lp.toIsing()
    lp.toQubo()


def test_flopt_to_ising1():
    a = Variable(name="a", ini_value=1, cat="Spin")
    b = Variable(name="b", ini_value=1, cat="Spin")
    c = Variable(name="c", ini_value=1, cat="Spin")

    # Problem
    prob = Problem()

    # make Ising model
    x = np.array([a, b, c])
    J = np.array([[1, 2, 1], [0, 1, 1], [0, 0, 3]])
    h = np.array([1, 2, 0])
    prob += -(x.T).dot(J).dot(x) - (h.T).dot(x)  # objective function

    print(prob)

    # convert objective function to Ising structure
    from flopt.convert import IsingStructure

    ising = IsingStructure.fromFlopt(prob)
    print(ising)

    ising.toQp()
    ising.toQubo()


def test_flopt_to_ising2():
    a = Variable(name="a", ini_value=1, cat="Binary")
    b = Variable(name="b", ini_value=1, cat="Binary")
    c = Variable(name="c", ini_value=1, cat="Binary")

    # Problem
    prob = Problem()

    # make model
    prob += -a - b - c

    print(prob)

    # convert objective function to Ising structure
    from flopt.convert import IsingStructure

    ising = IsingStructure.fromFlopt(prob)

    ising.toQp()
    ising.toLp()
    ising.toQubo()


def test_flopt_to_qubo1():
    a = Variable(name="a", ini_value=1, cat="Binary")
    b = Variable(name="b", ini_value=1, cat="Binary")
    c = Variable(name="c", ini_value=1, cat="Binary")

    # Problem
    prob = Problem()

    # make model
    prob += -a * b - c

    print(prob)

    # convert objective function to Qubo structure
    from flopt.convert import QuboStructure

    qubo = QuboStructure.fromFlopt(prob)
    print(qubo)

    qubo.toQp()
    qubo.toIsing()


def test_flopt_to_qubo2():
    a = Variable(name="a", ini_value=1, cat="Binary")
    b = Variable(name="b", ini_value=1, cat="Binary")
    c = Variable(name="c", ini_value=1, cat="Binary")

    # Problem
    prob = Problem()

    # make model
    prob += -a - b - c

    print(prob)

    # convert objective function to Qubo structure
    from flopt.convert import QuboStructure

    qubo = QuboStructure.fromFlopt(prob)
    print(qubo)

    qubo.toQp()
    qubo.toLp()
    qubo.toIsing()


def test_flopt_to_pulp():
    # Variables
    a = Variable("a", cat="Binary")
    b = Variable("b", cat="Binary")
    c = Variable("c", lowBound=-1, upBound=2, cat="Integer")
    d = Variable("d", lowBound=-2, upBound=1, cat="Continuous")

    # Problem
    prob = Problem()
    prob += c + b  # set the objective function
    prob += a + c == 0  # set the constraint
    prob += a + b <= 1  # set the constraint
    prob += a + d >= -1  # set the constraint

    print(prob)

    # check wheter prob can be converted into pulp modeling
    assert Solver(algo="Pulp").available(prob)

    # convert flopt to pulp
    from flopt.convert import flopt_to_pulp

    lp_prob, lp_solution = flopt_to_pulp(prob)
    print(lp_prob)
    print(lp_solution)


def test_lp_to_flopt():
    # make Lp model
    c = [0, 1, 2]
    C = 0
    A = [[0, 1, 2], [1, 2, 3], [0, 1, 2]]
    b = [0, 1, 1]
    lb = [0, 0, 0]
    ub = [1, 1, 1]
    var_types = ["Binary", "Binary", "Continuous"]

    from flopt.convert import LpStructure

    prob = LpStructure(c, C, A=A, b=b, lb=lb, ub=ub, types=var_types).toFlopt()
    prob.show()


def test_ising_to_flopt():
    # make Ising model
    J = [[1, 2, 1], [0, 1, 1], [0, 0, 3]]
    h = [1, 2, 0]
    C = 0

    from flopt.convert import IsingStructure

    prob = IsingStructure(J, h, C).toFlopt()
    prob.show()


def test_qubo_to_flopt():
    # make Qubo model
    Q = [[1, 2, 1], [0, 1, 1], [0, 0, 3]]
    C = 10

    from flopt.convert import QuboStructure

    prob = QuboStructure(Q, C).toFlopt()
    print(prob)


def test_pulp_to_flopt1():
    import pulp

    # Variables
    a = pulp.LpVariable("a", lowBound=0, upBound=1, cat="Integer")
    b = pulp.LpVariable("b", lowBound=1, upBound=2, cat="Continuous")
    c = pulp.LpVariable("c", upBound=3, cat="Continuous")

    # Problem
    prob = pulp.LpProblem()
    prob += -a - b - c  # set the objective function
    prob += a <= 0  # set the constraint
    prob += a + b == c  # set the constraint
    prob += c >= 0  # set the constraint

    print(prob)

    from flopt.convert import pulp_to_flopt

    flopt_prob = pulp_to_flopt(prob)
    flopt_prob.show()


def test_pulp_to_flopt2():
    import pulp

    # Variables
    a = pulp.LpVariable("a", lowBound=0, upBound=1, cat="Integer")
    b = pulp.LpVariable("b", lowBound=1, upBound=2, cat="Continuous")
    c = pulp.LpVariable("c", upBound=3, cat="Continuous")

    # Problem
    prob = pulp.LpProblem()
    prob += -2 * a - b - c + 4  # set the objective function
    prob += 10 * a <= 0  # set the constraint

    from flopt.convert import pulp_to_flopt

    flopt_prob = pulp_to_flopt(prob)
