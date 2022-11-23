import flopt
from flopt.variable import VarElement
from flopt.expression import Expression, CustomExpression, Const, SelfReturn
from flopt.constraint import Constraint
from flopt.solvers import Solver
from flopt.solution import Solution
from flopt.constants import (
    VariableType,
    ExpressionType,
    ConstraintType,
    OptimizationType,
    array_classes,
)
from flopt.env import setup_logger, create_variable_mode


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

    We solve

    >>> prob.solve(solver=solver_name or solver object, timelimit=10)

    After solving, we can obtain the objective value.

    >>> prob.getObjectiveValue()
    """

    def __init__(self, name=None, sense=OptimizationType.Minimize):
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

    def clone(self, variable_clone=False):
        """create clone object
        Parameters
        ----------
        variable_clone : bool
            if it is true, variables are cloned in expression

        Returns
        -------
        prob : Problem
        """
        prob = Problem(
            name=f"{self.name}" if self.name is not None else None,
            sense=self.sense,
        )
        if not variable_clone:
            prob.setObjective(self.obj.clone(), self.obj_name)
            for const in self.constraints:
                prob.addConstraint(const.clone(), const.name)
            return prob

        var_dict = {var.name: SelfReturn(var.clone()) for var in self.getVariables()}
        prob.setObjective(self.obj.value(var_dict=var_dict), self.obj_name)
        for const in self.constraints:
            const_exp = const.expression.value(var_dict=var_dict)
            if const.type == ConstraintType.Eq:
                prob.addConstraint(const_exp == 0, const.name)
            else:
                prob.addConstraint(const_exp <= 0, const.name)
        return prob

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
        self.__variables = self.obj.getVariables()
        for const in self.constraints:
            self.__variables |= const.getVariables()
        return self.__variables

    def getConstraints(self):
        """
        Returns
        -------
        list of Constraint
            list of constraints in this problem
        """
        return self.constraints

    def solve(
        self,
        solver=None,
        timelimit=None,
        lowerbound=None,
        optimized_variables=None,
        msg=False,
        **kwargs,
    ):
        """solve this problem

        Parameters
        ----------
        solver : Solver or None
        timelimit : float or None
        lowerbound : float or None
            solver terminates when it obtains the solution whose objective value is lower than this value
        optimized_variables : None or list, tuple, np.ndarray or any container of Variable
            if it is specified, solver will optimize only the variables in optimized_variables
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

        When user want to optimize a part of variables under otherwise variables are fixed,
        user specify optmized_variables in problem.solve().

        .. code-block:: python

            # optimize only a
            status, log = prob.solve(optimized_variables=[a], timelimit=1)

        """
        if solver is None:
            solver = Solver("auto")
        elif isinstance(solver, str):
            solver = Solver(solver)
        if timelimit is not None:
            solver.setParams(timelimit=timelimit)
        if lowerbound is not None:
            solver.setParams(lowerbound=lowerbound)
        solver.setParams(**kwargs)
        self.solver = solver

        if self.sense.lower() == "maximize":
            self.obj = -self.obj

        if optimized_variables is None:
            solution = Solution(self.getVariables())
        else:
            assert (
                set(optimized_variables) <= self.getVariables()
            ), "optimized_variables containes variables that are not in the problem"
            solution = Solution(optimized_variables)

        status, log, self.time = self.solver.solve(
            solution,
            self.obj,
            self.constraints,
            self,
            msg=msg,
        )

        if self.sense.lower() == "maximize":
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
        problem_type = {}

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
            ExpressionType.Polynomial,
            ExpressionType.Nonlinear,
            ExpressionType.Permutation,
            ExpressionType.BlackBox,
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

    def toEq(self):
        """Create a problem object with only equal constraints

        Returns
        -------
        prob : Problem
        """
        prob = self.clone()
        constraints = []
        for const in prob.constraints:
            if const.type() == ConstraintType.Eq:
                constraints.append(const)
            else:  # ConstraintType.Le
                with create_variable_mode():
                    s = flopt.Variable(
                        "slack", lowBound=0, cat="Continuous", ini_value=0
                    )
                constraints.append(const.expression + s == 0)
        prob.constraints = constraints
        return prob

    def toIneq(self):
        """Create a problem object with only inequal constraints

        Returns
        -------
        prob : Problem
        """
        prob = self.clone()
        constraints = []
        for const in prob.constraints:
            if const.type() == ConstraintType.Le:
                constraints.append(const)
            else:  # ConstraintType.Eq
                constraints.append(const.expression <= 0)
                constraints.append(const.expression >= 0)
        prob.constraints = constraints
        return prob

    def boundsToIneq(self):
        """Create a problem object has bounds constraints of variables as inequal constraints"""
        prob = self.clone()
        for var in prob.getVariables():
            if var.getLb() is not None:
                prob += var >= var.getLb()
            if var.getUb() is not None:
                prob += var <= var.getUb()
            var.lowBound = None
            var.upBound = None
        return prob

    def replace(self, correspondence_dict):
        """Replace variable to another variables or expression

        Parameters
        ----------
        correspondence_dict : dict
            key is Variable and value is Variable or ExpressionElement

        Examples
        --------

        .. code-block:: python

            import flopt

            # create problem
            x = flopt.Variable("x", lowBound=4, upBound=5)
            prob = flopt.Problem()
            prob += x
            prob.show()
            >>> Name: None
            >>> Type         : Problem
            >>> sense        : Minimize
            >>> objective    : x+0
            >>> #constraints : 0
            >>> #variables   : 1 (Continuous 1)
            >>>
            >>>
            >>> V 0, name x, Continuous 4 <= x <= 5

            # convert bounds of variables to constraints
            prob = prob.clone().boundsToIneq()
            prob.show()
            >>> Name: None
            >>>   Type         : Problem
            >>>   sense        : Minimize
            >>>   objective    : x+0
            >>>   #constraints : 2
            >>>   #variables   : 1 (Continuous 1)
            >>>
            >>>   C 0, name None, 4-x <= 0
            >>>   C 1, name None, x-5 <= 0
            >>>
            >>>   V 0, name x, Continuous None <= x <= None

            # replace x with x_plus + x_minus
            x_plus = flopt.Variable("x_plus", lowBound=0)
            x_minus = flopt.Variable("x_minus", lowBound=0)
            prob.replace(correspondence_dict={x: x_plus + x_minus})
            prob.show()
            >>> Name: None
            >>>   Type         : Problem
            >>>   sense        : Minimize
            >>>   objective    : x_plus+x_minus
            >>>   #constraints : 2
            >>>   #variables   : 2 (Continuous 2)
            >>>
            >>>   C 0, name None, 4-(x_plus+x_minus) <= 0
            >>>   C 1, name None, x_plus+x_minus-5 <= 0
            >>>
            >>>   V 0, name x_minus, Continuous 0 <= x_minus <= None
            >>>   V 1, name x_plus, Continuous 0 <= x_plus <= None

        """
        assert all(isinstance(key, VarElement) for key in correspondence_dict.keys())
        var_dict = {var.name: SelfReturn(var) for var in self.getVariables()}
        for var, value in correspondence_dict.items():
            var_dict[var.name] = SelfReturn(value)
        self.setObjective(self.obj.value(var_dict=var_dict), self.obj_name)
        for const in self.constraints:
            const.expression = const.expression.value(var_dict=var_dict)
        return self

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

    def __str__(self, prefix=""):
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
        obj_name = self.obj.getName() if self.obj_name is None else f"{self.obj_name}, "
        s = f"{prefix}Name: {self.name}\n"
        s += f"{prefix}  Type         : {self.type}\n"
        s += f"{prefix}  sense        : {self.sense}\n"
        s += f"{prefix}  objective    : {obj_name}\n"
        s += f"{prefix}  #constraints : {len(self.constraints)}\n"
        s += f"{prefix}  #variables   : {len(self.getVariables())} ({variables_str})"
        return s

    def show(self, to_str=False):
        s = str(self) + "\n\n"
        for ix, const in enumerate(self.constraints):
            s += f"  C {ix}, name {const.name}, {const}\n"
        s += "\n"
        for ix, var in enumerate(self.getVariables()):
            s += f"  V {ix}, name {var.name}, {var.type()} {var.getLb()} <= {var.name} <= {var.getUb()}\n"
        if to_str:
            return s
        print(s)
