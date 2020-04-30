from .base_sequential_update import SequentialUpdateSearch

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
        self.name = 'RandomSearch'
        self.can_solve_problems = ['blackbox', 'permutation']

    def setNewSolution(self, *args, **kwargs):
        """
        generate new solution with random.
        """
        self.solution.setRandom()
