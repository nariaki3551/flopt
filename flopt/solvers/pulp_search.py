import copy

import pulp

from flopt.solvers.base import BaseSearch
from flopt.expression import Const
from flopt.solution import Solution
from flopt.env import setup_logger
from flopt.constants import VariableType, SolverTerminateState


logger = setup_logger(__name__)


class LpVariable(pulp.LpVariable):
    def __init__(self, name, lowBound, upBound, cat):
        super().__init__(name, lowBound=lowBound, upBound=upBound, cat=cat)

    def value(self):
        """for creating the objective and constraints of pulp"""
        return self

    def getValue(self):
        return self.varValue


class PulpSearch(BaseSearch):
    """PuLP API LP Solver

    Parameters
    ----------
    solver : pulp.Solver
        solver pulp use, see https://coin-or.github.io/pulp/technical/solvers.html.
        default is pulp.PULP_CBC_CMD

    Returns
    -------
    status : int
        status of solver
    """
    def __init__(self):
        super().__init__()
        self.name = "PulpSearch"
        self.solver = None
        self.can_solve_problems = ['lp']


    def available(self, prob):
        """
        Parameters
        ----------
        prob : Problem

        Returns
        -------
        bool
            return true if objective and constraint functions are linear else false
        """
        var_types = {VariableType.Binary, VariableType.Integer, VariableType.Continuous}
        var_match = all( var.type() in var_types for var in prob.getVariables() )
        obj_linear = prob.obj.isLinear()
        const_linear = all( const.isLinear() for const in prob.constraints )
        return var_match and obj_linear and const_linear


    def search(self):

        lp_prob, lp_solution = self.createLpProblem(self.solution, self.prob)

        if self.solver is not None:
            solver = self.solver
        else:
            solver = pulp.PULP_CBC_CMD(timeLimit=self.timelimit, msg=self.msg)
        lp_status = lp_prob.solve(solver)

        # get result
        for lp_var, var in zip(lp_solution, self.solution):
            value = lp_var.getValue()
            if var.type() in {VariableType.Integer, VariableType.Binary}:
                value = round(value)
            var.setValue(value)
        self.updateSolution(self.solution)

        if lp_status in {-1, -2, -3}:
            # -1: infeasible
            # -2: unbounded
            # -3: undefined
            status = SolverTerminateState.Abnormal
            logger.info(f'PuLP LpStatus {pulp.constants.LpStatus[lp_status]}')
        else:
            status = SolverTerminateState.Normal

        return status


    def createLpProblem(self, solution, prob):
        """Convert Problem into pulp.LpProblem

        Parameters
        ----------
        solution : Solution
        prob : Problem

        Returns
        -------
        pulp.LpProblem, Solution
        """
        # conver VarElement -> LpVariable
        lp_variables = []
        for var in solution:
            if var.type() == VariableType.Continuous:
                cat = 'Continuous'
            elif var.type() == VariableType.Integer:
                cat = 'Integer'
            elif var.type() == VariableType.Binary:
                cat = 'Binary'
            else:
                raise ValueError(var.type())
            lp_var = LpVariable(
                var.name, lowBound=var.lowBound, upBound=var.upBound, cat=cat
            )
            lp_variables.append(lp_var)
        lp_solution = Solution('lp_solution', lp_variables)

        # conver Problem -> pulp.LpProblem
        name = '' if self.name is None else self.name
        lp_prob = pulp.LpProblem(name=name)
        if not isinstance(prob.obj, Const):
            lp_prob.setObjective(prob.obj.value(lp_solution))

        for const in prob.constraints:
            const_exp = const.expression
            if const.type == 'eq':
                lp_prob.addConstraint(
                    const_exp.value(lp_solution) == 0,
                    const.name
                )
            elif const.type == 'le':
                lp_prob.addConstraint(
                    const_exp.value(lp_solution) <= 0,
                    const.name
                )
            elif const.type == 'ge':
                lp_prob.addConstraint(
                    const_exp.value(lp_solution) >= 0,
                    const.name
                )

        return lp_prob, lp_solution

