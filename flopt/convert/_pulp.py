import flopt
from flopt.solution import Solution
from flopt.solvers.pulp_search import PulpSearch


def flopt_to_pulp(prob):
    """
    Parameters
    ----------
    prob : Problem

    Returns
    -------
    lp_prob : pulp.LpProblem
    lp_solution : Solution of pulp.LpVariables

    Examples
    --------
    .. code-block:: python

        from flopt import Variable, Solver

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

        # check wheter prob can be converted into pulp modeling
        flopt.Solver(algo='PulpSearch').available(prob)

        # convert flopt to pulp
        from flopt.solvers.convert import flopt_to_pulp
        lp_prob, lp_solution = flopt_to_pulp(prob)
    """
    assert PulpSearch().available(prob)
    solution = Solution('s', prob.getVariables())
    lp_prob, lp_solution = PulpSearch().createLpProblem(solution, prob)
    return lp_prob, lp_solution


def pulp_to_flopt(prob):
    """
    Parameters
    ----------
    prob : pulp.LpProblem

    Returns
    -------
    flopt_prob : Problem

    Examples
    --------
    .. code-block:: python

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

        # convert pulp to flopt
        from flopt.solvers.convert import pulp_to_flopt
        flopt_prob = pulp_to_flopt(prob)

    """
    # conver LpVariable -> VarElement
    flopt_variables = dict()
    for var in prob.variables():
        flopt_var = flopt.Variable(
            var.getName(), lowBound=var.getLb(), upBound=var.getUb(), cat=var.cat
        )
        flopt_variables[var.getName()] = flopt_var

    # convert Problem -> pulp.LpProblem
    name = '' if prob.name is None else prob.name
    flopt_prob = flopt.Problem(name=name)

    def flopt_exp(const, var_dicts):
        exp = const
        for var_dict in var_dicts:
            name, value = var_dict['name'], var_dict['value']
            exp += value * flopt_variables[name]
        return exp

    # convert objective function
    obj = flopt_exp(prob.objective.constant, prob.objective.to_dict())
    flopt_prob.setObjective(obj)

    for const in prob.constraints.values():
        if 'coefficients' in const.to_dict():
            exp = flopt_exp(const.constant, const.to_dict()['coefficients'])
        else:
            exp = flopt_exp(const.constant, const.to_dict())
        if const.sense == 0:
            flopt_prob.addConstraint( exp == 0, const.name )
        elif const.sense == -1:
            flopt_prob.addConstraint( exp <= 0, const.name )
        elif const.sense == 1:
            flopt_prob.addConstraint( exp >= 0, const.name )

    return flopt_prob
