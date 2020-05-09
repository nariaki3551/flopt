from time import time
import pulp

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message
)
from flopt.env import setup_logger
import flopt.constants


logger = setup_logger(__name__)


class LpVariable(pulp.LpVariable):
    def __init__(self, name, lowBound, upBound, cat):
        super().__init__(name, lowBound=lowBound, upBound=upBound, cat=cat)

    def value(self):
        """
        for Creating the objective function fo pulp
        """
        return self

    def getValue(self):
        return self.varValue


class PulpSearch(BaseSearch):
    """LP Solver
    """

    def __init__(self):
        super().__init__()
        self.name = "PulpSearch"
        self.solver = None
        self.can_solve_problems = ['lp']

    def search(self):
        status = flopt.constants.SOLVER_NORMAL_TERMINATE

        lp_prob, lp_solution = self.createLpProblem()

        if self.solver is not None:
            solver = self.solver
        else:
            solver = pulp.PULP_CBC_CMD(maxSeconds=self.timelimit, msg=self.msg)
        lp_status = lp_prob.solve(solver)

        # get result of solver
        for lp_var, var in zip(lp_solution, self.solution):
            var.setValue(lp_var.getValue())
        self.updateSolution(self.solution, obj_value=None)

        return status


    def createLpProblem(self):
        # conver VarElement -> LpVariable
        lp_variables = []
        for var in self.solution:
            if var.getType() == 'VarContinuous':
                cat = 'Continuous'
            elif var.getType() == 'VarInteger':
                cat = 'Integer'
            elif var.getType() == 'VarBinary':
                car = 'Binary'
            else:
                raise ValueError
            lp_var = LpVariable(
                var.name, lowBound=var.lowBound, upBound=var.upBound, cat=cat
            )
            lp_variables.append(lp_var)
        lp_solution = self.solution.clone()
        lp_solution._variables = lp_variables

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