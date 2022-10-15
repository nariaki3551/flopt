import pulp

from flopt.solvers.base import BaseSearch
from flopt.expression import Const
from flopt.solution import Solution
from flopt.constants import (
    VariableType,
    ExpressionType,
    ConstraintType,
    SolverTerminateState,
)
from flopt.env import setup_logger

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
    """API for PuLP, linear programming modeling tool

    Parameters
    ----------
    solver : pulp.Solver
        solver pulp use, see https://coin-or.github.io/pulp/technical/solvers.html.
        default is pulp.PULP_CBC_CMD

    Examples
    --------

    .. code-block:: python

        import flopt

        # Variables
        a = flopt.Variable("a", lowBound=0, upBound=1, cat="Integer")
        b = flopt.Variable("b", lowBound=1, upBound=2, cat="Continuous")
        c = flopt.Variable("c", lowBound=-1, upBound=3, cat="Continuous")

        # Problem
        prob = flopt.Problem()
        prob += a + b + c + 2
        prob += a + b >= 2
        prob += b - c >= 3

        solver = flopt.Solver("PulpSearch")
        prob.solve(solver, msg=True)

    When you use other solvers in pulp, for example GLPK solver, you set solver parameter in PulpSearch object.

    .. code-block:: python

        solver = flopt.Solver("PulpSearch")

        import pulp
        glpk_solver = pulp.GLPK_CMD()
        solver.setParams(solver=glpk_solver)
        prob.solve(solver, msg=True)

    """

    name = "PulpSearch"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Linear,
    }

    def __init__(self):
        super().__init__()
        self.solver = None

    def search(self, solution, *args):
        self.start_build()
        lp_prob, lp_solution = self.createLpProblem(solution, self.prob)
        self.end_build()

        if self.solver is not None:
            solver = self.solver
        else:
            solver = pulp.PULP_CBC_CMD(
                timeLimit=self.timelimit - self.build_time, msg=self.msg
            )

        lp_status = lp_prob.solve(solver)

        # get result
        for lp_var in lp_solution:
            name = lp_var.getName()
            value = lp_var.getValue()
            if lp_var.cat in {pulp.LpInteger, pulp.LpBinary}:
                value = round(value)
            solution.setValue(name, value)

        # update best solution if needed
        self.registerSolution(solution)

        # lp_status =   -1: infeasible
        #               -2: unbounded
        #               -3: undefined
        logger.info(f"PuLP LpStatus {pulp.constants.LpStatus[lp_status]}")
        if lp_status == -1:
            return SolverTerminateState.Infeasible
        elif lp_status == -2:
            return SolverTerminateState.Unbounded
        elif lp_status == -3:
            return SolverTerminateState.Abnormal
        else:
            return SolverTerminateState.Normal

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
                cat = "Continuous"
            elif var.type() == VariableType.Integer:
                cat = "Integer"
            elif var.type() == VariableType.Binary:
                cat = "Binary"
            else:
                raise ValueError(var.type())
            lp_var = LpVariable(
                var.name, lowBound=var.getLb(), upBound=var.getUb(), cat=cat
            )
            lp_variables.append(lp_var)
        lp_solution = Solution("lp_solution", lp_variables)

        # conver Problem -> pulp.LpProblem
        name = "" if self.name is None else self.name
        sense = (
            pulp.LpMinimize
            if prob.sense in {"minimize", "Minimize"}
            else pulp.LpMaximize
        )
        lp_prob = pulp.LpProblem(name=name, sense=sense)
        if not isinstance(prob.obj, Const):
            lp_prob.setObjective(prob.obj.value(lp_solution))

        for const in prob.getConstraints():
            const_exp = const.expression
            if const.type() == ConstraintType.Eq:
                lp_prob.addConstraint(const_exp.value(lp_solution) == 0, const.name)
            else:  # const.type() == ConstraintType.Le
                lp_prob.addConstraint(const_exp.value(lp_solution) <= 0, const.name)

        return lp_prob, lp_solution
