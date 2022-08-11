from scipy import optimize as scipy_optimize

from flopt.solvers.base import BaseSearch
from flopt.convert import LpStructure
from flopt.env import setup_logger
from flopt.variable import VariableArray
from flopt.expression import Const
from flopt.solution import Solution
from flopt.constants import VariableType, SolverTerminateState


logger = setup_logger(__name__)


class ScipyLpSearch(BaseSearch):
    """Scipy optimize linprog API Solver

    See Also
    --------
    scipy.optimize.linprog

    Returns
    -------
    status : int
        status of solver

    Attributes
    ----------
    method : {"highs", "highs-ds", "highs-ipm", "simplex", "revised simplex", "interior-point"}
    """

    def __init__(self):
        super().__init__()
        self.name = "ScipyLpSearch"
        self.n_trial = 1e10
        self.method = "interior-point"
        self.can_solve_problems = ["lp"]

    def available(self, prob, verbose=False):
        """
        Parameters
        ----------
        prob : Problem
        verbose : bool

        Returns
        -------
        bool
            return true if it can solve the problem else false
        """
        for var in prob.getVariables():
            if not var.type() == VariableType.Continuous:
                if verbose:
                    logger.error(
                        f"variable: \n{var}\n must be continouse, but got {var.type()}"
                    )
                return False
        if not prob.obj.isLinear():
            if verbose:
                logger.error(f"objective function: \n{prob.obj}\n must be Linear")
            return False
        for const in prob.constraints:
            if not const.expression.isLinear():
                if verbose:
                    logger.error(f"constraint: \n{const}\n must be Linear")
                return False
        return True

    def search(self):
        status = SolverTerminateState.Normal
        var_names = [var.name for var in self.solution]

        def gen_func(expression):
            def func(values):
                variables = []
                for var_name, value in zip(var_names, values):
                    variables.append(Const(value, name=var_name))
                solution = Solution("tmp", variables)
                return expression.value(solution)

            return func

        # function
        func = gen_func(self.prob.obj)

        # lp structure
        lp = LpStructure.fromFlopt(
            self.prob,
            x=VariableArray(self.solution.getVariables()),
        )

        # bounds
        bounds = [(_lb, _ub) for _lb, _ub in zip(lp.lb, lp.ub)]

        # options
        options = {
            "maxiter": self.n_trial,
            "disp": self.msg,
            "time_limit": self.timelimit,
        }

        # callback
        def callback(optimize_result):
            self.trial_ix += 1
            obj_value = func(optimize_result.x)
            for var, value in zip(self.solution, optimize_result.x):
                var.setValue(value)
            if obj_value < self.best_obj_value:
                diff = self.best_obj_value - obj_value
                self.updateSolution(self.solution, obj_value)
                self.recordLog()
                if self.msg and diff > 1e-8:
                    self.during_solver_message("*")
            for _callback in self.callbacks:
                _callback([self.solution], self.best_solution, self.best_obj_value)

        # search
        res = scipy_optimize.linprog(
            c=lp.c,
            A_ub=lp.G,
            b_ub=lp.h,
            A_eq=lp.A,
            b_eq=lp.b,
            bounds=bounds,
            options=options,
            callback=callback,
            method=self.method,
        )
        # res.status =  0: Optimal solution found.
        #               1: Iteration or time limit reached.
        #               2: Problem is infeasible.
        #               3: Problem is unbounded.
        #               4: The HiGHS solver ran into a problem.
        if res.status == 0:
            # get result of solver
            for var, value in zip(self.solution, res.x):
                var.setValue(value)
            self.updateSolution(self.solution, obj_value=None)
        elif res.status == 1:
            status = SolverTerminateState.Timelimit
        elif res.status == 2:
            status = SolverTerminateState.Infeasible
        elif res.status == 3:
            status = SolverTerminateState.Unbounded
        else:
            status = SolverTerminateState.Abnormal

        return status
