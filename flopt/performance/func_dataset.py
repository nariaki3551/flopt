from flopt import Variable, Problem, CustomObject
from .base_dataset import BaseDataset
from datasets.functions import benchmark_func

class FuncDataset(BaseDataset):
    """
    Function Benchmark Instance Set

    Parameters
    ----------
    instance_names : list
      instance name list
    """
    def __init__(self):
        self.name = 'func'
        self.instance_names = list(benchmark_func)

    def createInstance(self, instance_name):
        """
        create FuncInstance
        """
        func_data = benchmark_func[instance_name]
        create_objective = func_data['co']
        create_variables = func_data['cv']
        func_instance = FuncInstance(
            instance_name, create_objective, create_variables
        )
        return func_instance


class FuncInstance:
    """
    Function Benchmark Instance

    Parameters
    ----------
    name : str
      instance name
    create_objective : function
      function which generates the objective function using dimension n
    create_variables : function
      function which generates the variables using dimension n
    n : int
      dimension (for some instance)
    """
    def __init__(self, name, create_objective, create_variables, n=10):
        self.name = name
        self.create_objective = create_objective
        self.create_variables = create_variables
        self.n = n

    def createProblem(self, solver):
        """
        Create problem according to solver

        Parameters
        ----------
        solver : Solver
          solver

        Returns
        -------
        (bool, Problem)
          if solver can be solve this instance return
          (true, prob formulated according to solver)
        """
        if 'blackbox' in solver.can_solve_problems:
            return True, self.createProblemFunc()
        else:
            print('this instance can be only `blackbox` formulation')
            return False, None

    def createProblemFunc(self):
        """
        create problem from instance

        Returns
        -------
        Problem
          problem
        """
        variables = self.create_variables(self.n)
        for var in variables:
            var.setRandom()
        func = self.create_objective(self.n)
        _func = lambda *x: func(x)
        obj = CustomObject(_func, variables)
        prob = Problem(name='Function:{self.name}')
        prob.setObjective(obj)
        return prob
