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
        create_objective = func_data["co"]
        create_variables = func_data["cv"]
        minimum_value = func_data["mo"]
        func_instance = FuncInstance(
            instance_name, create_objective, create_variables, minimum_value
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

    def __init__(self, name, create_objective, create_variables, minimum_value, n=10):
        self.name = name
        self.create_objective = create_objective
        self.create_variables = create_variables
        self.minimum_value = minimum_value
        self.n = n

    def getBestBound(self):
        """return the optimal value of objective function"""
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
        problem_type = dict(
            Variable=VariableType.Number,
            Objective=ExpressionType.BlackBox,
            Constraint=None,
        )
        if solver.availableProblemType(problem_type):
            return True, self.createProblemFunc(self.n)
        else:
            logger.debug(f"{solver.name} cannot solve this instance")
            return False, None

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
        variables = self.create_variables(n=n, cat=cat)
        for var in variables:
            var.setRandom()
        func = self.create_objective(n)
        obj = CustomExpression(lambda *x: func(x), variables)
        prob = Problem(name=f"Function:{self.name}_n{n}")
        prob.setObjective(obj)
        self.n = n
        return prob

    def __str__(self):
        return f"Instance: {self.name}"
