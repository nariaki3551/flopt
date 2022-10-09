import random

from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, ExpressionType, SolverTerminateState

from flopt.env import setup_logger

logger = setup_logger(__name__)


class TwoOpt(BaseSearch):
    """2-Opt: local search for permutation

    2-Opt search explores neighborhood of current solution.
    In 2-Opt, the neighborhood of a perm = [0, 1, 2, ..., n-1] are
    [0, 1, .., i-1, j, j-1, ..., i+1, i, j+1, ..., n],
    where i and j are in {0..n}, and i is less than j.

    """

    name = "2-Opt"
    can_solve_problems = {
        "Variable": VariableType.Permutation,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }

    def __init__(self):
        super().__init__()
        self.n_trial = 1e100

    def search(self, solution, *args):
        best_obj_value = self.best_obj_value

        for _ in range(int(self.n_trial)):
            # generate new solution
            for var in solution:
                perm = var.value()
                n_perm = len(perm)
                i, j = sorted(random.sample(range(n_perm), 2))
                new_perm = perm[:i] + perm[i:j][::-1] + perm[j:]  # 2-opt
                var.setValue(new_perm)
                obj_value = self.getObjValue(solution)
                if obj_value >= self.best_obj_value:
                    var.setValue(perm)
                else:
                    best_obj_value = obj_value

            # update best solution if needed
            self.registerSolution(solution, best_obj_value)

            # callbacks
            self.callback([solution])

            # check time limit
            self.raiseTimeoutIfNeeded()

        return SolverTerminateState.Normal
