import numpy as np

import flopt

def flopt_to_ising(prob):
    """
    Parameters
    ----------
    prob : Problem

    Returns
    -------
    collections.namedtuple
        IsingStructure('IsingStructure', 'J h C x')

        - object is - x.T.dot(J).dot(x) - h.T.dot(x)
        - such that x[i] in {-1, 1}

    Examples
    --------
    .. code-block:: python

        from flopt import Variable, Solver
        import numpy as np

        # Spin Variables
        a = Variable(name='a', iniValue=1, cat='Spin')
        b = Variable(name='b', iniValue=1, cat='Spin')
        c = Variable(name='c', iniValue=1, cat='Spin')

        # Problem
        prob = Problem()

        # make Ising model
        x = np.array([a, b, c])
        J = np.array([
            [1, 2, 1],
            [0, 1, 1],
            [0, 0, 3]
        ])
        h = np.array([1, 2, 0])
        prob += - (x.T).dot(J).dot(x) - (h.T).dot(x)  # objective function

        # convert objective function to Ising structure
        from flopt.convert import flopt_to_ising

        ising = flopt_to_ising(prob)
        print('J', ising.J)
        print('h', ising.h)
        print('C', ising.C)
        print('x', ising.x)

        >>> J [[1. 2. 1.]
        >>>  [0. 1. 1.]
        >>>  [0. 0. 3.]]
        >>> h [1. 2. 0.]
        >>> C 0
        >>> x [Variable(a, cat="Spin", iniValue=1) Variable(b, cat="Spin", iniValue=1)
        >>>  Variable(c, cat="Spin", iniValue=1)]
    """
    assert prob.obj.toIsing()
    assert len(prob.constraints) == 0

    return prob.obj.toIsing()


def ising_to_flopt(J, h, C=0):
    """
    Parameters
    ----------
    J : matrix
    h : vector
    C : float or int
        constant

    Returns
    -------
    prob : Problem

        - object - x.T.dot(J).dot(x) - h.T.dot(x) + C
        - such that x[i] in {-1, 1}

    Examples
    --------
    .. code-block:: python

        # make Ising model
        J = [[1, 2, 1],
             [0, 1, 1],
             [0, 0, 3]]
        h = [1, 2, 0]

        from flopt.convert import ising_to_flopt

        prob = ising_to_flopt(J, h)
        print(prob)

        >>> Name: None
        >>>   Type         : Problem
        >>>   sense        : minimize
        >>>   objective    : (((2*s0)*s1+s0*s2)-s0+s1*s2)-(2*s1)+3
        >>>   #constraints : 0
        >>>   #variables   : 3 (Spin 3)
    """
    assert len(J) == len(J[0]) == len(h)
    J, h = np.array(J), np.array(h)

    num_x = len(J)
    x = np.zeros((num_x, ), dtype=object)
    for i in range(num_x):
        x[i] = flopt.Variable(name=f's{i}', cat='Spin')

    prob = flopt.Problem()

    # set objective
    prob += - x.T.dot(J).dot(x) - h.T.dot(x) + C

    return prob
