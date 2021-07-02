from time import time
import pulp

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message
)
from flopt.solution import Solution
from flopt.env import setup_logger
import flopt.constants


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
        prob : flopt.Problem

        Returns
        -------
        bool
            return true if objective and constraint functions are linear else false
        """
        return all( expr.isLinear() for expr in [prob.obj] + prob.constraints )\
                and all(not var.getType() == 'VarPermutation' for var in prob.getVariables())


    def search(self):
        status = flopt.constants.SOLVER_NORMAL_TERMINATE

        lp_prob, lp_solution = self.createLpProblem()

        if self.solver is not None:
            solver = self.solver
        else:
            solver = pulp.PULP_CBC_CMD(maxSeconds=self.timelimit, msg=self.msg)
        lp_status = lp_prob.solve(solver)

        # get result
        for lp_var, var in zip(lp_solution, self.solution):
            value = lp_var.getValue()
            if var.getType() in {'VarInteger', 'VarBinary'}:
                value = round(value)
            var.setValue(value)
            logger.debug(f'{var.name}: {value}')
        self.updateSolution(self.solution)

        if lp_status in {-1, -2, -3}:
            # -1: infeasible
            # -2: unbounded
            # -3: undefined
            status = flopt.constants.SOLVER_ABNORMAL_TERMINATE
            logger.info(f'PuLP LpStatus {pulp.constants.LpStatus[lp_status]}')

        return status


    def createLpProblem(self):
        """Convert Problem into pulp.LpProblem

        Returns
        -------
        pulp.LpProblem, Solution
        """
        # conver VarElement -> LpVariable
        lp_variables = []
        for var in self.solution:
            if var.getType() == 'VarContinuous':
                cat = 'Continuous'
            elif var.getType() == 'VarInteger':
                cat = 'Integer'
            elif var.getType() == 'VarBinary':
                cat = 'Binary'
            else:
                raise ValueError
            lp_var = LpVariable(
                var.name, lowBound=var.lowBound, upBound=var.upBound, cat=cat
            )
            lp_variables.append(lp_var)
        lp_solution = Solution('lp_solution', lp_variables)

        # conver Problem -> pulp.LpProblem
        name = '' if self.name is None else self.name
        lp_prob = pulp.LpProblem(name=name)
        lp_prob.setObjective(self.obj.value(lp_solution))

        for const in self.constraints:
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
