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
    QuboStructure
        object x.T.dot(Q).dot(x) + C
        such that x[i] in {0, 1}
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
            Q[i, j] = 2 * ( sum(J[i+1:, i]) + sum(J[i, i-1:]) + h[i] )
    for i in range(num_x):
        Q[i, i] = - 4 * J[i, i]

    # create C
    C = 0
    for i in range(num_x):
        for j in range(i+1, num_x):
            C -= J[i, j]
    for i in range(num_x):
        C -= h[i]

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
    prob : flopt.Problem
        object x.T.dot(Q).dot(x) + C
        such that x[i] in {0, 1}
    """
    assert len(Q) == len(Q[0])
    import numpy as np
    Q = np.array(Q)

    num_x = len(Q)
    x = np.zeros((num_x, ), dtype=object)
    for i in range(num_x):
        x[i] = flopt.Variable(name=f's{i}', cat='Binary')

    prob = flopt.Problem()

    # set objective
    prob += x.T.dot(Q).dot(x) + C

    return prob