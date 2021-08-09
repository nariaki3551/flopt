import pytest

import numpy as np

import flopt

def test_flopt_to_lp():
    # Variables
    a = flopt.Variable('a', cat='Binary')
    b = flopt.Variable('b', cat='Binary')
    c = flopt.Variable('c', lowBound=-1, upBound=2, cat='Integer')
    d = flopt.Variable('d', lowBound=-2, upBound=1, cat='Continuous')

    # Problem
    prob = flopt.Problem()
    prob += c + b       # set the objective function
    prob += a + c == 0  # set the constraint
    prob += a + b <= 1  # set the constraint
    prob += a + d >= -1 # set the constraint
    print(prob)

    from flopt.convert import flopt_to_lp
    lp = flopt_to_lp(prob)
    print('x', lp.x)
    print('A', lp.A)
    print('b', lp.b.T)
    print('c', lp.c.T)
    print('lb', lp.lb.T)
    print('ub', lp.ub.T)

    lp = flopt_to_lp(prob, eq=True)
    print('x', lp.x)
    print('A', lp.A)
    print('b', lp.b.T)
    print('c', lp.c.T)
    print('lb', lp.lb.T)
    print('ub', lp.ub.T)


def test_flopt_to_ising1():
    a = flopt.Variable(name='a', iniValue=1, cat='Spin')
    b = flopt.Variable(name='b', iniValue=1, cat='Spin')
    c = flopt.Variable(name='c', iniValue=1, cat='Spin')

    # Problem
    prob = flopt.Problem()

    # make Ising model
    import numpy as np
    x = np.array([a, b, c])
    J = np.array([
        [1, 2, 1],
        [0, 1, 1],
        [0, 0, 3]
    ])
    h = np.array([1, 2, 0])
    prob += - (x.T).dot(J).dot(x) - (h.T).dot(x)  # objective function

    print(prob)

    # convert objective function to Ising structure
    from flopt.convert import flopt_to_ising
    ising = flopt_to_ising(prob)
    print('J', ising.J)
    print('h', ising.h)
    print('x', ising.x)


def test_flopt_to_ising2():
    a = flopt.Variable(name='a', iniValue=1, cat='Binary')
    b = flopt.Variable(name='b', iniValue=1, cat='Binary')
    c = flopt.Variable(name='c', iniValue=1, cat='Binary')

    # Problem
    prob = flopt.Problem()

    # make model
    prob += - a * b - c

    print(prob)

    # convert objective function to Ising structure
    from flopt.convert import flopt_to_ising
    ising = flopt_to_ising(prob)
    print('J', ising.J)
    print('h', ising.h)
    print('x', ising.x)


def test_flopt_to_qubo():
    a = flopt.Variable(name='a', iniValue=1, cat='Binary')
    b = flopt.Variable(name='b', iniValue=1, cat='Binary')
    c = flopt.Variable(name='c', iniValue=1, cat='Binary')

    # Problem
    prob = flopt.Problem()

    # make model
    prob += - a * b - c

    print(prob)

    # convert objective function to Qubo structure
    from flopt.convert import flopt_to_qubo
    qubo = flopt_to_qubo(prob)
    print('Q', qubo.Q)
    print('C', qubo.C)
    print('x', qubo.x)



def test_flopt_to_pulp():
    # Variables
    a = flopt.Variable('a', cat='Binary')
    b = flopt.Variable('b', cat='Binary')
    c = flopt.Variable('c', lowBound=-1, upBound=2, cat='Integer')
    d = flopt.Variable('d', lowBound=-2, upBound=1, cat='Continuous')

    # Problem
    prob = flopt.Problem()
    prob += c + b       # set the objective function
    prob += a + c == 0  # set the constraint
    prob += a + b <= 1  # set the constraint
    prob += a + d >= -1 # set the constraint

    print(prob)

    # check wheter prob can be converted into pulp modeling
    assert flopt.Solver(algo='PulpSearch').available(prob)

    # convert flopt to pulp
    from flopt.convert import flopt_to_pulp
    lp_prob, lp_solution = flopt_to_pulp(prob)
    print(lp_prob)
    print(lp_solution)


def test_lp_to_flopt():
    # make Lp model
    c = [0, 1, 2]
    A = [[0, 1, 2],
         [1, 2, 3],
         [0, 1, 2]]
    b = [0, 1, 1]
    lb = [0, 0, 0]
    ub = [1, 1, 1]
    var_types=['Binary', 'Binary', 'Continuous']

    from flopt.convert import lp_to_flopt
    prob = lp_to_flopt(A, b, c, lb, ub, var_types)
    print(prob)
    print(prob.constraints)


def test_ising_to_flopt():
    # make Ising model
    J = [[1, 2, 1],
         [0, 1, 1],
         [0, 0, 3]]
    h = [1, 2, 0]

    from flopt.convert import ising_to_flopt
    prob = ising_to_flopt(J, h)
    print(prob)


def test_qubo_tto_flopt():
    # make Qubo model
    Q = [[1, 2, 1],
         [0, 1, 1],
         [0, 0, 3]]
    C = 10

    from flopt.convert import qubo_to_flopt
    prob = qubo_to_flopt(Q, C)
    print(prob)


def test_pulp_to_flopt():
    import pulp

    # Variables
    a = pulp.LpVariable('a', lowBound=0, upBound=1, cat='Integer')
    b = pulp.LpVariable('b', lowBound=1, upBound=2, cat='Continuous')
    c = pulp.LpVariable('c', upBound=3, cat='Continuous')

    # Problem
    prob = pulp.LpProblem()
    prob += - a - b - c  # set the objective function
    prob += a      <= 0  # set the constraint
    prob += a + b  == c  # set the constraint
    prob += c      >= 0  # set the constraint

    print(prob)
