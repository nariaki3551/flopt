from time import time
from copy import deepcopy
import pulp
from pulp import LpMinimize, LpMaximize
from flopt import Problem, Solution
from flopt.problem import ObjectiveFunction

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


class LpProblem(Problem):
    def __init__(self, name=None, sense='minimize'):
        super().__init__(name, sense=sense)

    def solve(self, solver=None, timelimit=None, msg=False):
        """
        solve this problem
        objective function is self.obj
        variables is self.variables

        Parameters
        ----------
        solver : solver of pulp
          pulp solver
        timelimit : float
          timelimit
        msg : bool
          if true, display the message from solver

        Returns
        -------
        int
          return the status of solving
        Log
          return log object
        """

        # convert for pulp
        obj = ObjectiveFunction(deepcopy(self.obj))
        solution = Solution('s', self.variables)

        # conver VarElement -> LpVariable
        lp_variables = []
        for var in solution:
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
        lp_solution = solution.clone()
        lp_solution._variables = lp_variables

        # conver Problem -> pulp.LpProblem
        sense = LpMinimize if self.sense == 'minimize' else LpMaximize
        lpProb = pulp.LpProblem(name=self.name, sense=sense)
        lpProb.setObjective(obj.value(lp_solution))

        # solver
        if solver is None:
            solver = pulp.PULP_CBC_CMD(maxSeconds=timelimit, msg=True)
        status = lpProb.solve(solver)
        
        # get result of solver
        for lp_var, var in zip(lp_solution, solution):
            var.setValue(lp_var.getValue())

        return status, None, lpProb.solutionTime
