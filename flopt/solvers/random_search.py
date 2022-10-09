from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, ExpressionType, SolverTerminateState

from flopt.env import setup_logger

logger = setup_logger(__name__)


class RandomSearch(BaseSearch):
    """Random Sampling Search"""

    name = "RandomSearch"
    can_solve_problems = {
        "Variable": VariableType.Any,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }

    def __init__(self):
        super().__init__()
        self.n_trial = 1e100

    def search(self, solution, *args):
        for _ in range(int(self.n_trial)):
            # generate new solution
            solution.setRandom()

            # update best solution if needed
            self.registerSolution(solution)

            # execute callbacks
            self.callback([solution])

            # check time limit
            self.raiseTimeoutIfNeeded()

        return SolverTerminateState.Normal
