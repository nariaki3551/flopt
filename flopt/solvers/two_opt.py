import random

from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, ExpressionType, SolverTerminateState

from flopt.env import setup_logger

logger = setup_logger(__name__)


class TwoOpt(BaseSearch):
    """2-Opt: a kind of local search for permutation.

    2-Opt applies neighborhood of swapping a edge.
    Example, we have perm = [0, 1, 2, ..., n-1],
    [0, 1, .., i-1, j, j-1, ..., i+1, i, j+1, ..., n] is in
    neighborhood of perm for all i, j in {0..n} and i is neq j.

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

    def search(self):
        """
        search a better solution using `self.setNewSolution()` function
        `self.setNewSolution()` generate new solution and set it into self.solution
        """
        best_obj_value = self.best_obj_value

        for self.trial_ix in range(1, int(self.n_trial) + 1):
            # generate new solution and set it into self.solution
            for var in self.solution:
                perm = var.value()
                n_perm = len(perm)
                i, j = sorted(random.sample(range(n_perm), 2))
                new_perm = perm[:i] + perm[i:j][::-1] + perm[j:]  # 2-opt
                var.setValue(new_perm)
                obj_value = self.getObjValue(self.solution)
                if obj_value >= self.best_obj_value:
                    var.setValue(perm)
                else:
                    best_obj_value = obj_value

            # if solution is better thatn incumbent, then update best solution
            self.registerSolution(self.solution, best_obj_value)

            # callbacks
            for callback in self.callbacks:
                callback([self.solution], self.best_solution, self.best_obj_value)

            # check time limit
            self.raiseTimeoutIfNeeded()

        return SolverTerminateState.Normal
