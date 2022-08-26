import time
import random

from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, SolverTerminateState

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
    can_solve_problems = ["permutation"]

    def __init__(self):
        super().__init__()
        self.n_trial = 1e100

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
            if not var.type() == VariableType.Permutation:
                if verbose:
                    logger.error(
                        f"variable: \n{var}\n must be permutation, but got {var.type()}"
                    )
                return False
        if prob.constraints:
            if verbose:
                logger.error(f"this solver can not handle constraints")
            return False
        return True

    def search(self):
        """
        search a better solution using `self.setNewSolution()` function
        `self.setNewSolution()` generate new solution and set it into self.solution
        """
        best_obj_value = self.best_obj_value

        for self.trial_ix in range(1, int(self.n_trial) + 1):
            # check time limit
            if time.time() > self.start_time + self.timelimit:
                return SolverTerminateState.Timelimit

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

        return SolverTerminateState.Normal
