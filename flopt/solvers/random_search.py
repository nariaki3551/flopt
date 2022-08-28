import time

from flopt.solvers.base import BaseSearch
from flopt.constants import SolverTerminateState

from flopt.env import setup_logger

logger = setup_logger(__name__)


class RandomSearch(BaseSearch):
    """
    Random Sampling Search

    It is a simple serach, as follows.

    .. code-block:: python

      def setNewSolution(self, *args, **kwargs):
          self.solution.setRandom()
    """

    name = "RandomSearch"
    can_solve_problems = ["blackbox", "permutation"]

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
        for self.trial_ix in range(1, int(self.n_trial) + 1):
            # check time limit
            if time.time() > self.start_time + self.timelimit:
                return SolverTerminateState.Timelimit

            # generate new solution and set it into self.solution
            self.solution.setRandom()

            # if solution is better thatn incumbent, then update best solution
            self.registerSolution(self.solution)

            # callbacks
            for callback in self.callbacks:
                callback([self.solution], self.best_solution, self.best_obj_value)

        return SolverTerminateState.Normal
