from flopt import Variable, Problem, CustomExpression
from .base_dataset import BaseDataset, BaseInstance
from datasets.funcLib import benchmark_func

import logging
logger = logging.getLogger(__name__)


class FuncDataset(BaseDataset):
    """Function Benchmark Instance Set

    Parameters
    ----------
    instance_names : list
        instance name list
    """
    def __init__(self):
        self.name = 'func'
        self.instance_names = list(benchmark_func)


    def createInstance(self, instance_name):
        """create FuncInstance
        """
        logger.debug(f'{instance_name}')
        func_data = benchmark_func[instance_name]
        create_objective = func_data['co']
        create_variables = func_data['cv']
        minimum_value    = func_data['mo']
        func_instance = FuncInstance(
            instance_name, create_objective,
            create_variables, minimum_value
        )
        return func_instance



class FuncInstance(BaseInstance):
    """Function Benchmark Instance

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
    def __init__(self, name, create_objective, create_variables,
            minimum_value, n=10):
        self.name = name
        self.create_objective = create_objective
        self.create_variables = create_variables
        self.minimum_value    = minimum_value
        self.n = n


    def getBestValue(self):
        """return the optimal value of objective function
        """
        return self.minimum_value(self.n)


    def createProblem(self, solver):
        """Create problem according to solver

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
            logger.info('this instance can be only `blackbox` formulation')
            return False, None


    def createProblemFunc(self):
        """create problem from instance

        Returns
        -------
        Problem
            problem
        """
        variables = self.create_variables(self.n)
        for var in variables:
            var.setRandom()
        func = self.create_objective(self.n)
        obj = CustomExpression(lambda *x: func(x), variables)
        prob = Problem(name='Function:{self.name}')
        prob.setObjective(obj)
        return prob


    def __str__(self):
        return f'Instance: {self.name}'
