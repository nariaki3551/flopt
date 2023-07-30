import gurobipy

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


class GpVar:
    def __init__(self, gp_var):
        self.gp_var = gp_var

    def value(self):
        return self.gp_var

    def getValue(self):
        return self.gp_var.X

    @property
    def name(self):
        return self.gp_var.VarName

    def getName(self):
        return self.name

    @property
    def Vtype(self):
        return self.gp_var.Vtype


class GurobiSearch(BaseSearch):
    """API for Gurobi

    Parameters
    ----------
    gurobi_params : dict
        key is name, value is parameter value

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
        prob += a + b + c * c + 2
        prob += a + b >= 2
        prob += b - c >= 3

        prob.solve(solver="gurobi", msg=True)

    To set parameter for Gurobi, you use gurobi_params argument.

    .. code-block:: python

        solver = flopt.Solver("gurobi")
        solver.setParams(gurobi_params={"LogToConsole": 0}) # set LogToConsole to 0
        prob.solve(solver=solver)

    """

    name = "Gurobi"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Quadratic,
    }

    def __init__(self):
        super().__init__()
        self.gurobi_params = None

    def search(self, solution, *args):
        self.start_build()
        gp_model, gp_solution = self.createGpProblem(solution, self.prob)
        self.end_build()

        # set parameters
        gp_model.setParam("TimeLimit", self.timelimit - self.build_time)
        if self.gurobi_params is not None:
            for key, value in self.gurobi_params.items():
                gp_model.setParam(key, value)

        # solve
        gp_model.optimize()

        # Status code	    Value	Description
        # LOADED	        1	Model is loaded, but no solution information is available.
        # OPTIMAL           2   Model was solved to optimality (subject to tolerances), and an optimal solution is available.
        # INFEASIBLE	    3	Model was proven to be infeasible.
        # INF_OR_UNBD   	4	Model was proven to be either infeasible or unbounded. To obtain a more definitive conclusion, set the DualReductions parameter to 0 and reoptimize.
        # UNBOUNDED         5	Model was proven to be unbounded. Important note: an unbounded status indicates the presence of an unbounded ray that allows the objective to improve without limit. It says nothing about whether the model has a feasible solution. If you require information on feasibility, you should set the objective to zero and reoptimize.
        # CUTOFF	        6	Optimal objective for model was proven to be worse than the value specified in the Cutoff parameter. No solution information is available.
        # ITERATION_LIMIT	7	Optimization terminated because the total number of simplex iterations performed exceeded the value specified in the IterationLimit parameter, or because the total number of barrier iterations exceeded the value specified in the BarIterLimit parameter.
        # NODE_LIMIT	    8	Optimization terminated because the total number of branch-and-cut nodes explored exceeded the value specified in the NodeLimit parameter.
        # TIME_LIMIT	    9	Optimization terminated because the time expended exceeded the value specified in the TimeLimit parameter.
        # SOLUTION_LIMIT	10	Optimization terminated because the number of solutions found reached the value specified in the SolutionLimit parameter.
        # INTERRUPTED	    11	Optimization was terminated by the user.
        # NUMERIC	        12	Optimization was terminated due to unrecoverable numerical difficulties.
        # SUBOPTIMAL	    13	Unable to satisfy optimality tolerances; a sub-optimal solution is available.
        # INPROGRESS	    14	An asynchronous optimization call was made, but the associated optimization run is not yet complete.
        # USER_OBJ_LIMIT	15	User specified an objective limit (a bound on either the best objective or the best bound), and that limit has been reached.
        # WORK_LIMIT	    16	Optimization terminated because the work expended exceeded the value specified in the WorkLimit parameter.
        # MEM_LIMIT	        17	Optimization terminated because the total amount of allocated memory exceeded the value specified in the SoftMemLimit parameter.
        logger.debug(f"Gurobi Status {gp_model.status}")
        if gp_model.status == 3:
            status = SolverTerminateState.Infeasible
            return status
        elif gp_model.status == 5:
            status = SolverTerminateState.Unbounded
            return status
        elif gp_model.status == 9:
            status = SolverTerminateState.Timelimit
        elif gp_model.status == 11:
            status = SolverTerminateState.Interrupted
        elif gp_model.status == 2:
            status = SolverTerminateState.Normal
        else:
            status = SolverTerminateState.Abnormal

        # get result
        for gp_var in gp_solution:
            name = gp_var.getName()
            value = gp_var.getValue()
            if gp_var.Vtype in {gurobipy.GRB.BINARY, gurobipy.GRB.INTEGER}:
                value = round(value)
            solution.setValue(name, value)

        # update best solution if needed
        self.registerSolution(solution)

        return status

    def createGpProblem(self, solution, prob):
        """Convert Problem into gurobi.Model

        Parameters
        ----------
        solution : Solution
        prob : Problem

        Returns
        -------
        gurobi.Model, Solution
        """
        name = "" if self.name is None else self.name
        gp_model = gurobipy.Model(name=name)

        gp_variables = list()
        for var in solution:
            var_name = var.getName()
            if var.type() == VariableType.Binary:
                vtype = gurobipy.GRB.BINARY
            elif var.type() == VariableType.Integer:
                vtype = gurobipy.GRB.INTEGER
            elif var.type() == VariableType.Continuous:
                vtype = gurobipy.GRB.CONTINUOUS
            else:
                raise ValueError(var.type())
            var_lb = var.getLb() if var.getLb() is not None else -float("inf")
            var_ub = var.getUb() if var.getUb() is not None else float("inf")
            gp_var = gp_model.addVar(name=var_name, vtype=vtype, lb=var_lb, ub=var_ub)
            gp_var = GpVar(gp_var)
            gp_variables.append(gp_var)
        gp_model.update()
        gp_solution = Solution(gp_variables)

        # conver Problem -> pulp.LpProblem
        gp_obj = prob.obj.value(gp_solution)
        gp_sense = (
            gurobipy.GRB.MINIMIZE
            if prob.sense in {"minimize", "Minimize"}
            else gurobipy.GRB.MAXIMIZE
        )
        gp_model.setObjective(gp_obj, gp_sense)

        for const in prob.getConstraints():
            const_exp = const.expression.value(gp_solution)
            const_name = const.name if const.name is not None else ""
            if not isinstance(const_exp, (int, float)):
                if const.type() == ConstraintType.Eq:
                    gp_model.addConstr(const_exp == 0, name=const_name)
                else:  # const.type() == ConstraintType.Le
                    gp_model.addConstr(const_exp <= 0, name=const_name)

        gp_model.update()

        return gp_model, gp_solution
