import collections

import flopt


def flopt_to_lp(prob, x=None, eq=False):
    """
    Parameters
    ----------
    prob : Problem
    x : vector
    eq : bool
        If it is true, then return norml equation formulation, such that Ax = b
        else inequality formulation such that Ax <= b

    Returns
    -------
    LpStructure
        object     c.T.dot(x)
        subject to A.dot(x) == b or A.dot(x) <= b
                   lb <= x <= ub
    """
    if eq:
        return flopt_to_lp_eq(prob, x)
    else:
        return flopt_to_lp_ineq(prob, x)


def flopt_to_lp_eq(prob, x=None):
    """
    Parameters
    ----------
    prob : Problem
    x : vector

    Returns
    -------
    LpStructure
        object     c.T.dot(x)
        subject to A.dot(x) == b
                   lb <= x <= ub
    """
    import numpy as np

    LpStructure = collections.namedtuple(
        'LpStructure',
        'A b c x lb ub type'
        )

    # prepare slack variables
    n_slacks = sum(const.type != 'eq' for const in prob.constraints)
    slack_list = np.zeros(n_slacks, dtype=object)
    for i in range(n_slacks):
        slack_list[i] = flopt.Variable(f'slack{i}', lowBound=0, cat='Continuous')

    n_variables = len(prob.variables) + n_slacks
    if x is None:
        x = np.array(list(prob.variables), dtype=object)
    x = np.hstack([x, slack_list])

    # create A, b
    A = np.zeros((len(prob.constraints), n_variables))
    b = np.zeros((len(prob.constraints), ))
    slack_ix = 0
    for i, const in enumerate(prob.constraints):
        if const.type == 'eq':
            linear = const.expression.toLinear(x)
            A[i, :] = linear.c.T
            b[i] = - linear.constant
        elif const.type == 'le':
            # a_i^T x <= b_i --> a_i^T x + s_i = b_i
            linear = (const.expression + slack_list[slack_ix]).toLinear(x)
            A[i, :] = linear.c.T
            b[i] = - linear.constant
            slack_ix += 1
        else:
            # a_i^T x >= b_i --> -a_i^T x + s_i = -b_i
            linear = (const.expression - slack_list[slack_ix]).toLinear(x)
            A[i, :] = - linear.c.T
            b[i] = linear.constant
            slack_ix += 1
    assert slack_ix == n_slacks

    # create c
    c = prob.obj.toLinear(x).c

    # create lb, ub
    lb = np.array([var.lowBound for var in x])
    ub = np.array([var.upBound  for var in x])

    return LpStructure(A, b, c, x, lb, ub, 'eq')


def flopt_to_lp_ineq(prob, x=None):
    """
    Parameters
    ----------
    prob : Problem
    x : vector

    Returns
    -------
    LpStructure
        object     c.T.dot(x)
        subject to A.dot(x) <= b
                   lb <= x <= ub
    """
    import numpy as np

    LpStructure = collections.namedtuple(
        'LpStructure',
        'A b c x lb ub type'
        )

    n_eqs = sum(const.type == 'eq' for const in prob.constraints)
    if x is None:
        x = np.array(list(prob.variables), dtype=object)

    # create A, b
    A = np.zeros((len(prob.constraints) + n_eqs, len(x)))
    b = np.zeros((len(prob.constraints) + n_eqs, ))
    i = 0
    for const in prob.constraints:
        linear = const.expression.toLinear(x)
        if const.type == 'eq':
            # a_i^T x <= b_i && -a_i^T x <= -b_i
            A[i, :] = linear.c.T
            b[i] = - linear.constant
            i += 1
            A[i, :] = - linear.c.T
            b[i] = linear.constant
            i += 1
        elif const.type == 'le':
            # a_i^T x <= b_i
            A[i, :] = linear.c.T
            b[i] = - linear.constant
            i += 1
        else:
            # a_i^T x >= b_i --> -a_i^T x <= -b_i
            A[i, :] = - linear.c.T
            b[i] = linear.constant
            i += 1

    # create c
    c = prob.obj.toLinear(x).c

    # create lb, ub
    lb = np.array([var.lowBound for var in x])
    ub = np.array([var.upBound  for var in x])

    return LpStructure(A, b, c, x, lb, ub, 'ineq')



def lp_to_flopt(A, b, c, lb, ub, var_types):
    """
    Parameters
    ----------
    A : matrix
    b : vector
    c : vector
    lb : vector
    ub : vector
    var_types : list of {'Binary', 'Continuous', 'Integer'}

    Returns
    -------
    prob : flopt.Problem
        object     c.T.dot(x)
        subject to A.dot(x) <= b
                   lb <= x <= ub
    """
    assert len(A) == len(b)
    assert len(A[0]) == len(c) == len(lb) == len(ub) == len(var_types)
    assert all( var_type in {'Binary', 'Continuous', 'Integer'} for var_type in var_types )
    import numpy as np
    A, b, c = np.array(A), np.array(b), np.array(c)

    num_x = len(A)
    x = np.zeros((num_x, ), dtype=object)
    for i in range(num_x):
        x[i] = flopt.Variable(f'x{i}', lb[i], ub[i], cat=var_types[i])

    prob = flopt.Problem()

    # set objective
    prob += c.T.dot(x)

    # add constraints
    for i in range(len(A)):
        prob += A[i, :].T.dot(x) <= b[i]

    return prob

