import flopt

def flopt_to_ising(prob):
    """
    Parameters
    ----------
    prob : Problem

    Returns
    -------
    IsingStructure
        object - x.T.dot(J).dot(x) - h.T.dot(x)
        such that x[i] in {-1, 1}
    """
    assert prob.obj.toIsing()
    assert len(prob.constraints) == 0

    return prob.obj.toIsing()


def ising_to_flopt(J, h):
    """
    Parameters
    ----------
    J : matrix
    h : vector

    Returns
    -------
    prob : flopt.Problem
        object - x.T.dot(J).dot(x) - h.T.dot(x)
        such that x[i] in {-1, 1}
    """
    assert len(J) == len(J[0]) == len(h)
    import numpy as np
    J, h = np.array(J), np.array(h)

    num_x = len(J)
    x = np.zeros((num_x, ), dtype=object)
    for i in range(num_x):
        x[i] = flopt.Variable(name=f's{i}', cat='Spin')

    prob = flopt.Problem()

    # set objective
    prob += - x.T.dot(J).dot(x) - h.T.dot(x)

    return prob
