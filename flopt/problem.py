from flopt.variable import VarElement
from flopt.expression import Expression, CustomExpression, Const
from flopt.constraint import Constraint
from flopt.solvers import Solver
from flopt.solution import Solution
from flopt.constants import (
    VariableType,
    ExpressionType,
    OptimizationType,
    array_classes,
)
from flopt.env import setup_logger


logger = setup_logger(__name__)


class Problem:
    """
    Interface between User and Solver

    Parameters
    ----------
    name : str
        name of problem
    sense : str, optional
        minimize, maximize
        (future satisfiability is added)

    Attributes
    ----------
    name : str
        name of problem
    sense : str, optional
        minimize, maximize
        (future satisfiability is added)
    obj : Expression family
    solver : Solver or None
    time : float
        solving time

    Examples
    --------

    >>> prob = Problem(name='test')

    When we want to solve the maximize problem, then

    >>> prob = Problem(name='test', sense='maximize')

    Input solver, when we solve

    >>> solve = Solver(algo=...)
    >>> prob.solve(solver=solver, timelimit=10)

    After solving, we can obtain the objective value.

    >>> prob.getObjectiveValue()
    """

    def __init__(self, name=None, sense=OptimizationType.Minimize):
        if sense == "minimize" or sense == "maximize":
            logger.warning(
                f"'minimize' and 'maximize' is deprecated. You have to use 'Minimize', 'Maximize', flopt.Minimize or flopt.Maximize"
            )
        self.type = "Problem"
        self.name = name
        self.sense = str(sense)
        self.obj = Const(0)
        self.obj_name = None
        self.constraints = []
        self.__variables = set()
        self.solver = None
        self.time = None
        self.best_bound = None

    def setObjective(self, obj, name=None):
        """set objective function. __iadd__(), "+=" operations call this function.

        Parameters
        ----------
        obj : int, float, Variable family or Expression family
            objective function
        """
        if isinstance(obj, (int, float)):
            obj = Const(obj)
        elif isinstance(obj, VarElement):
            obj = Expression(obj, Const(0), "+")
        self.obj = obj
        self.obj_name = name
        try:
            self.__variables |= obj.getVariables()
        except RecursionError:
            import sys

            logger.warning(f"recursion reaches {sys.getrecursionlimit}")
            sys.setrecursionlimit(sys.getrecursionlimit() * 100)
            self.__variables |= obj.getVariables()
        except Exception as e:
            raise e

    def setBestBound(self, best_bound):
        """
        Parameters
        ----------
        best_bound : float
            best objective value of this problem
        """
        self.best_bound = best_bound

    def addConstraint(self, const, name=None):
        """add constraint into problem. __iadd__(), "+=" operations call this function.

        Parameters
        ----------
        const : Constraint
            constraint
        name : str or None
            constraint name

        Examples
        --------

        .. code-block:: python

            import flopt
            prob = flopt.Problem(algo=...)
            x = flopt.Variable("x")
            y = flopt.Variable("y")
            prob.addConstraint(x + y >= 2)

        """
        assert isinstance(
            const, Constraint
        ), f"assume Constraint class, but got {type(const)}"
        const.name = name
        self.constraints.append(const)
        self.__variables |= const.getVariables()

    def addConstraints(self, consts, name=None):
        for i, const in enumerate(consts):
            _name = const.name if name is None else name + f"_{i}"
            self.addConstraint(const, _name)

    def removeDuplicatedConstraints(self):
        """Remove duplicated constraints in problem

        Examples
        --------

        .. code-block:: python

            import flopt
            a = flopt.Variable("a")
            b = flopt.Variable("b")
            c = flopt.Variable("c")

            prob = flopt.Problem(name="Test")
            prob += a + b >= 0
            prob += a + b >= 0
            prob += a >= -b
            prob += 0 >= -a - b
            prob += Sum([a, b]) >= 0

            len(prob.constraints)
            >>> 5

            prob.removeDuplicatedConstraints()
            len(prob.constraints)
            >>> 1

        """
        for const in self.constraints:
            const.expression = const.expression.expand()
        self.constraints = list(set(self.constraints))

    def getObjectiveValue(self):
        """
        Returns
        -------
        float or int
            the objective value
        """
        return self.obj.value()

    def getVariables(self):
        """
        Returns
        -------
        set
            set of VarElement used in this problem
        """
        return self.__variables

    def getConstraints(self):
        """
        Returns
        -------
        list of Constraint
            list of constraints in this problem
        """
        return self.constraints

    def resetVariables(self):
        self.__variables = self.obj.getVariables()
        for const in self.constraints:
            self.__variables |= const.getVariables()

    def solve(self, solver=None, timelimit=None, lowerbound=None, msg=False, **kwargs):
        """solve this problem

        Parameters
        ----------
        solver : Solver or None
        timelimit : float or None
        lowerbound : float or None
            solver terminates when it obtains the solution whose objective value is lower than this value
        msg : bool
            if true, display the message from solver

        Returns
        -------
        Status
            return the status of solving
        Log
            return log object

        Examples
        --------

        .. code-block:: python

            import flopt
            a = flopt.Variable("a")
            b = flopt.Variable("b")
            c = flopt.Variable("c")

            prob = flopt.Problem(name="Test")
            prob += a + b
            prob += a + b >= 0

            solver = flopt.Solver("auto")
            status, logs = prob.solve(solver=solver)

        """
        if solver is None:
            solver = Solver("auto")
        if timelimit is not None:
            solver.setParams(timelimit=timelimit)
        if lowerbound is not None:
            solver.setParams(lowerbound=lowerbound)
        solver.setParams(**kwargs)
        self.solver = solver

        if self.sense == "maximize" or self.sense == "Maximize":
            self.obj = -self.obj

        solution = Solution("s", self.getVariables())

        status, log, self.time = self.solver.solve(
            solution,
            self.obj,
            self.constraints,
            self,
            msg=msg,
        )

        if self.sense == "maximize" or self.sense == "Maximize":
            self.obj = -self.obj

        return status, log

    def getSolution(self, k=1):
        """get the k-top solution

        Parameters
        ----------
        k : int
            return k-top solution
        """
        assert k >= 1
        if k == 1:
            return self.solver.best_solution
        return self.solver.log.getSolution(k=k)

    def setSolution(self, k=1):
        """set the k-top solution to variables

        Parameters
        ----------
        k : int
            set k-top solution data to variables
        """
        assert k >= 1
        solution = self.getSolution(k)
        var_dict = solution.toDict()
        for var in self.getVariables():
            var.setValue(var_dict[var.name].value())

    def toProblemType(self):
        """
        Returns
        -------
        problem_type : dict
            key is "Variable", "Objective", "Constraint"
        """
        problem_type = dict()

        variable_types = [
            VariableType.Binary,
            VariableType.Integer,
            VariableType.Continuous,
            VariableType.Permutation,
            VariableType.Number,
            VariableType.Any,
        ]

        expression_types = [
            ExpressionType.Linear,
            ExpressionType.Quadratic,
            ExpressionType.Any,
        ]

        # variables
        prob_variables_types = set(var.type() for var in self.getVariables())
        for variable_type in variable_types:
            if prob_variables_types <= variable_type.expand():
                problem_type["Variable"] = variable_type
                break

        # objective
        for expression_type in expression_types:
            for elm in self.obj.traverse():
                if isinstance(elm, CustomExpression):
                    problem_type["Objective"] = ExpressionType.BlackBox
                    break
            else:
                if self.obj.type() in expression_type.expand():
                    problem_type["Objective"] = expression_type
                    break

        # constraint
        if not self.constraints:
            problem_type["Constraint"] = ExpressionType.Non
        else:
            prob_expression_types = set(
                const.expression.type() for const in self.getConstraints()
            )
            for expression_type in expression_types:
                if prob_expression_types <= expression_type.expand():
                    problem_type["Constraint"] = expression_type
                    break

        return problem_type

    def __iadd__(self, other):
        if not isinstance(other, tuple):
            other = (other,)
        if isinstance(other[0], Constraint):
            self.addConstraint(*other)
        elif isinstance(other[0], array_classes):
            self.addConstraints(*other)
        else:
            self.setObjective(*other)
        return self

    def __str__(self):
        from collections import defaultdict

        variables_dict = defaultdict(int)
        for var in self.getVariables():
            variables_dict[var.type()] += 1
        variables_str = ", ".join(
            [
                f'{str(key).replace("VariableType.", "")} {value}'
                for key, value in sorted(variables_dict.items())
            ]
        )
        obj_name = "" if self.obj_name is None else f"{self.obj_name}, "
        s = f"Name: {self.name}\n"
        s += f"  Type         : {self.type}\n"
        s += f"  sense        : {self.sense}\n"
        s += f"  objective    : {obj_name}{self.obj.name}\n"
        s += f"  #constraints : {len(self.constraints)}\n"
        s += f"  #variables   : {len(self.getVariables())} ({variables_str})"
        return s

    def show(self):
        s = str(self) + "\n\n"
        for ix, const in enumerate(self.constraints):
            s += f"  C {ix}, name {const.name}, {str(const)}\n"
        return s
