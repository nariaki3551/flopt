from flopt import Problem, CustomExpression, VarContinuous
import flopt.solvers
from flopt.constants import VariableType, ExpressionType
from flopt.env import setup_logger

from .base_dataset import BaseDataset, BaseInstance
from datasets.funcLib import benchmark_func

logger = setup_logger(__name__)


class FuncDataset(BaseDataset):
    """Function Benchmark Instance Set

    Parameters
    ----------
    instance_names : list
        instance name list
    """

    name = "func"
    instance_names = list(benchmark_func)

    def createInstance(self, instance_name):
        """create FuncInstance"""
        logger.debug(f"{instance_name}")
        func_data = benchmark_func[instance_name]
        func_instance = FuncInstance(instance_name, func_data)
        return func_instance


class FuncInstance(BaseInstance):
    """Function Benchmark Instance

    Parameters
    ----------
    name : str
        instance name
    func_data : class
        create_objective : function
            function which generates the objective function using dimension n
        create_variables : function
            function which generates the variables using dimension n
        minimum_obj : function
            minimum value
    n : int
        dimension (for some instance)
    """

    def __init__(self, name, func_data, n=10):
        self.name = name
        self.func_data = func_data
        self.n = n

    def getBestBound(self):
        """return the optimal value of objective function"""
        return self.func_data.minimum_obj(self.n)

    def createProblem(self, solver):
        """Create problem according to solver

        Parameters
        ----------
        solver : Solver
            solver

        Returns
        -------
        Problem
            if solver can be solve this instance return
            (None, prob formulated according to solver)
        """
        problem_type = dict(
            Variable=VariableType.Number,
            Objective=ExpressionType.BlackBox,
            Constraint=None,
        )
        if solver.availableProblemType(problem_type):
            return self.createProblemFunc(self.n)
        else:
            logger.debug(f"{solver.name} cannot solve this instance")
            return None

    def createProblemFunc(self, n=10, cat=VarContinuous):
        """create problem from instance

        Parameters
        ----------
        n: int
            number of variables (for instance, this parameter will be ignored)
        cat: string or VariableType
            type of variables

        Returns
        -------
        Problem
            problem
        """
        x = self.func_data.create_variables(n=n, cat=cat)
        x.setRandom()
        obj = self.func_data.create_objective(n)
        prob = Problem(name=f"Function:{self.name}_n{n}")
        prob += obj(x)
        self.n = n
        return prob

    def __str__(self):
        return f"Instance: {self.name}"
