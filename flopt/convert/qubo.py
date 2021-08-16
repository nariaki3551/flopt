import collections

import numpy as np

import flopt
from flopt.convert.ising import flopt_to_ising


def flopt_to_qubo(prob):
    """
    Parameters
    ----------
    prob : Problem

    Returns
    -------
    collections.namedtuple
        QuboStructure = collections.namedtuple('QuboStructure', 'Q C x')

        - object x.T.dot(Q).dot(x) + C
        - such that x[i] in {0, 1}

    Examples
    -------

    .. code-block:: python

        from flopt import Variable, Solver

        a = Variable(name='a', iniValue=1, cat='Binary')
        b = Variable(name='b', iniValue=1, cat='Binary')
        c = Variable(name='c', iniValue=1, cat='Binary')

        # Problem
        prob = Problem()

        # make model
        prob += - a * b - c

        # convert objective function to Qubo structure
        from flopt.convert import flopt_to_qubo

        qubo = flopt_to_qubo(prob)
        print('Q', qubo.Q)
        print('C', qubo.C)
        print('x', qubo.x)

        >>> Q [[-0.   0.5  0.5]
        >>>  [ 0.  -0.   0.5]
        >>>  [ 0.   0.  -0. ]]
        >>> C -0.75
        >>> x [Variable(a, cat="Binary", iniValue=1)
        >>>  Variable(b, cat="Binary", iniValue=1)
        >>>  Variable(c, cat="Binary", iniValue=1)]
    """
    assert prob.obj.toIsing()
    assert len(prob.constraints) == 0

    QuboStructure = collections.namedtuple(
        'QuboStructure',
        'Q C x'
        )

    ising = prob.obj.toIsing()
    num_x = len(ising.x)

    J = ising.J
    h = ising.h

    # create Q
    Q = np.zeros((num_x, num_x))
    for i in range(num_x):
        for j in range(i+1, num_x):
            Q[i, j] = - 4 * J[i, j]
    for i in range(num_x):
        Q[i, i] = 2 * ( sum(J[:i, i]) + sum(J[i, i+1:]) - h[i] )

    # create C
    C = ising.C
    for i in range(num_x):
        for j in range(i+1, num_x):
            C -= J[i, j]
    for i in range(num_x):
        C += h[i]

    # create x
    list( x.toBinary() for x in ising.x )
    x = np.array([x.binary for x in ising.x], dtype=object)

    return QuboStructure(Q, C, x)


def qubo_to_flopt(Q, C):
    """
    Parameters
    ----------
    Q : matrix
    C : float

    Returns
    -------
    prob : Problem

        - object x.T.dot(Q).dot(x) + C
        - such that x[i] in {0, 1}

    Examples
    --------
    .. code-block:: python

        # make Qubo model
        Q = [[1, 2, 1],
             [0, 1, 1],
             [0, 0, 3]]
        C = 10

        from flopt.convert import qubo_to_flopt
        prob = qubo_to_flopt(Q, C)
        print(prob)
        >>> Name: None
        >>>   Type         : Problem
        >>>   sense        : minimize
        >>>   objective    : (2*s0)*s1+s0*s2+s0+s1*s2+s1+3*s2+10
        >>>   #constraints : 0
        >>>   #variables   : 3 (Binary 3)

    """
    assert len(Q) == len(Q[0])
    Q = np.array(Q)

    num_x = len(Q)
    x = np.zeros((num_x, ), dtype=object)
    for i in range(num_x):
        x[i] = flopt.Variable(name=f's{i}', cat='Binary')

    prob = flopt.Problem()

    # set objective
    prob += (x.T.dot(Q).dot(x) + C).expand()

    return prob
