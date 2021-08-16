import collections

import numpy as np

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
    collections.namedtuple
        LpStructure = collections.namedtuple('LpStructure', 'A b c C x lb ub type')

        - object is c.T.dot(x) + C
        - constraints are A.dot(x) == b or A.dot(x) <= l and b <= x <= ub

    Examples
    --------

    .. code-block:: python

        from flopt import Variable Problem

        # Variables
        a = Variable('a', cat='Binary')
        b = Variable('b', cat='Binary')
        c = Variable('c', lowBound=-1, upBound=2, cat='Integer')
        d = Variable('d', lowBound=-2, upBound=1, cat='Continuous')

        # Problem
        prob = Problem()
        prob += c + b       # set the objective function
        prob += a + c == 0  # set the constraint
        prob += a + b <= 1  # set the constraint
        prob += a + d >= -1 # set the constraint

    We can obtain normal equal-formulation, Ax <= b

    .. code-block:: python

        from flopt.convert import flopt_to_lp
        lp = flopt_to_lp(prob)
        print('x', lp.x)
        print('A', lp.A)
        print('b', lp.b.T)
        print('c', lp.c.T)
        print('C', lp.C)
        print('lb', lp.lb.T)
        print('ub', lp.ub.T)

        >>> x [Variable(b, cat="Binary", iniValue=0) VarElement("c", -1, 2, 0)
        >>>  Variable(a, cat="Binary", iniValue=0) VarElement("d", -2, 1, -0.5)]
        >>> A [[ 0.  1.  1.  0.]
        >>>  [-0. -1. -1. -0.]
        >>>  [ 1.  0.  1.  0.]
        >>>  [-0. -0. -1. -1.]]
        >>> b [0. 0. 1. 1.]
        >>> c [1. 1. 0. 0.]
        >>> C 0
        >>> lb [ 0 -1  0 -2]
        >>> ub [1 2 1 1]

    and, we can obtain normal equal-formulation, Ax = b

    .. code-block:: python

        lp = flopt_to_lp(prob, eq=True)
        print('x', lp.x)
        print('A', lp.A)
        print('b', lp.b.T)
        print('c', lp.c.T)
        print('C', lp.C)
        print('lb', lp.lb.T)
        print('ub', lp.ub.T)

        >>> x [Variable(b, cat="Binary", iniValue=0) VarElement("c", -1, 2, 0)
        >>>  Variable(a, cat="Binary", iniValue=0) VarElement("d", -2, 1, -0.5)
        >>>  VarElement("slack0", 0, None, 5000000000.0)
        >>>  VarElement("slack1", 0, None, 5000000000.0)]
        >>> A [[ 0.  1.  1.  0.  0.  0.]
        >>>  [ 1.  0.  1.  0.  1.  0.]
        >>>  [-0. -0. -1. -1. -0.  1.]]
        >>> b [0. 1. 1.]
        >>> c [1. 1. 0. 0. 0. 0.]
        >>> C 0
        >>> lb [ 0 -1  0 -2  0  0]
        >>> ub [1 2 1 1 None None]

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
        object     c.T.dot(x) + C
        subject to A.dot(x) == b
                   lb <= x <= ub
    """

    LpStructure = collections.namedtuple(
        'LpStructure',
        'A b c C x lb ub type'
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
            b[i] = - linear.C
        elif const.type == 'le':
            # a_i^T x <= b_i --> a_i^T x + s_i = b_i
            linear = (const.expression + slack_list[slack_ix]).toLinear(x)
            A[i, :] = linear.c.T
            b[i] = - linear.C
            slack_ix += 1
        else:
            # a_i^T x >= b_i --> -a_i^T x + s_i = -b_i
            linear = (const.expression - slack_list[slack_ix]).toLinear(x)
            A[i, :] = - linear.c.T
            b[i] = linear.C
            slack_ix += 1
    assert slack_ix == n_slacks

    # create c
    c = prob.obj.toLinear(x).c

    # create C
    C = prob.obj.constant()

    # create lb, ub
    lb = np.array([var.lowBound for var in x])
    ub = np.array([var.upBound  for var in x])

    return LpStructure(A, b, c, C, x, lb, ub, 'eq')


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
    LpStructure = collections.namedtuple(
        'LpStructure',
        'A b c C x lb ub type'
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
            b[i] = - linear.C
            i += 1
            A[i, :] = - linear.c.T
            b[i] = linear.C
            i += 1
        elif const.type == 'le':
            # a_i^T x <= b_i
            A[i, :] = linear.c.T
            b[i] = - linear.C
            i += 1
        else:
            # a_i^T x >= b_i --> -a_i^T x <= -b_i
            A[i, :] = - linear.c.T
            b[i] = linear.C
            i += 1

    # create c
    c = prob.obj.toLinear(x).c

    # create C
    C = prob.obj.constant()

    # create lb, ub
    lb = np.array([var.lowBound for var in x])
    ub = np.array([var.upBound  for var in x])

    return LpStructure(A, b, c, C, x, lb, ub, 'ineq')



def lp_to_flopt(A, b, c, C, lb, ub, var_types):
    """
    Parameters
    ----------
    A : matrix
    b : vector
    c : vector
    C : float or int
    lb : vector
    ub : vector
    var_types : list of {'Binary', 'Continuous', 'Integer'}

    Returns
    -------
    prob : Problem

        - object is c.T.dot(x)
        - constraints are A.dot(x) <= b, lb <= x <= ub

    Examples
    --------

    .. code-block:: python

        # make Lp model
        c = [0, 1, 2]
        C = 0
        A = [[0, 1, 2],
             [1, 2, 3],
             [0, 1, 2]]
        b = [0, 1, 1]
        lb = [0, 0, 0]
        ub = [1, 1, 1]
        var_types=['Binary', 'Binary', 'Continuous']

        from flopt.convert import lp_to_flopt
        prob = lp_to_flopt(A, b, c, C, lb, ub, var_types)
        print(prob)
        print(prob.constraints)

    """
    assert len(A) == len(b)
    assert len(A[0]) == len(c) == len(lb) == len(ub) == len(var_types)
    assert all( var_type in {'Binary', 'Continuous', 'Integer'} for var_type in var_types )
    A, b, c = np.array(A), np.array(b), np.array(c)

    num_x = len(A[0])
    x = np.zeros((num_x, ), dtype=object)
    for i in range(num_x):
        x[i] = flopt.Variable(f'x{i}', lb[i], ub[i], cat=var_types[i])

    prob = flopt.Problem()

    # set objective
    prob += c.T.dot(x) + C

    # add constraints
    for i in range(len(A)):
        prob += A[i, :].T.dot(x) <= b[i]

    return prob

