import flopt
from flopt.solution import Solution
from flopt.solvers.pulp_search import PulpSearch


def flopt_to_pulp(prob):
    """
    Parameters
    ----------
    prob : flopt.Problem

    Returns
    -------
    lp_prob : pulp.LpProblem
    lp_solution : Solution of pulp.LpVariables
    """
    assert PulpSearch().available(prob)
    lp_prob, lp_solution \
        = PulpSearch().createLpProblem(prob.getSolution(), prob.obj, prob.constraints)
    return lp_prob, lp_solution


def pulp_to_flopt(prob):
    """
    Parameters
    ----------
    prob : pulp.LpProblem

    Returns
    -------
    flopt_prob : flopt.Problem
    flopt_solution : Solution of flopt.VarElement family
    """
    # conver LpVariable -> VarElement
    flopt_variables = dict()
    for var in prob.variables():
        flopt_var = flopt.Variable(
            var.getName(), lowBound=var.getLb(), upBound=var.getUb(), cat=var.cat
        )
        flopt_variables[var.getName()] = flopt_var
    flopt_solution = Solution('flopt_solution', list(flopt_variables.values()))

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
        exp = flopt_exp(const.constant, const.to_dict()['coefficients'])
        if const.sense == 0:
            flopt_prob.addConstraint( exp == 0, const.name )
        elif const.sense == -1:
            flopt_prob.addConstraint( exp <= 0, const.name )
        elif const.sense == 1:
            flopt_prob.addConstraint( exp >= 0, const.name )

    return flopt_prob, flopt_solution
