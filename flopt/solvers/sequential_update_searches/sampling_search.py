from .base_sequential_update import SequentialUpdateSearch
from flopt.env import setup_logger


logger = setup_logger(__name__)


class RandomSearch(SequentialUpdateSearch):
    """
    Random Sampling Search

    It is a simple serach, as follows.

    .. code-block:: python

      def setNewSolution(self, *args, **kwargs):
          self.solution.setRandom()
    """

    def __init__(self):
        super().__init__()
        self.name = "RandomSearch"
        self.can_solve_problems = ["blackbox", "permutation"]

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

    def setNewSolution(self, *args, **kwargs):
        """generate new solution with random."""
        self.solution.setRandom()
