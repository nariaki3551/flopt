from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, ExpressionType, SolverTerminateState

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
    can_solve_problems = {
        "Variable": VariableType.Any,
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
        for self.trial_ix in range(1, int(self.n_trial) + 1):
            # generate new solution and set it into self.solution
            self.solution.setRandom()

            # if solution is better thatn incumbent, then update best solution
            self.registerSolution(self.solution)

            # callbacks
            for callback in self.callbacks:
                callback([self.solution], self.best_solution, self.best_obj_value)

            # check time limit
            self.raiseTimeoutIfNeeded()

        return SolverTerminateState.Normal
