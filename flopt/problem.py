from flopt.variable import VarElement, VarConst
from flopt.expression import Expression, ExpressionConst, CustomExpression
from flopt.constraint import Constraint
from flopt.solution import Solution
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
    variables : set of VarElement family
    solver : Solver or None
    time : float
        solving time
    prob_type : list of str
        type of problems

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
    def __init__(self, name=None, sense='minimize'):
        self.type = 'Problem'
        self.name = name
        self.sense = sense
        self.obj = ExpressionConst(0)
        self.constraints = []
        self.variables = set()
        self.solver = None
        self.time = None
        self.prob_type = ['blackbox']


    def setObjective(self, obj):
        """set objective function

        Parameters
        ----------
        obj : int, float, Variable family or Expression family
            objective function
        """
        if isinstance(obj, (int, float)):
            obj = ExpressionConst(obj)
        elif isinstance(obj, VarElement):
            obj = Expression(obj, VarConst(0), '+')
        self.obj = obj
        self.variables |= obj.getVariables()


    def setSolver(self, solver):
        """
        Parameters
        ----------
        solver : Solver
        """
        self.solver = solver


    def addConstraint(self, const, name=None):
        """add constraint

        Parameters
        ----------
        const : Constraint
            constraint
        name : str
            constraint name
        """
        assert isinstance(const, Constraint), \
            f"assume Constraint class, but got {type(const)}"
        const.name = name
        self.constraints.append(const)
        self.variables |= const.getVariables()


    def getObjectiveValue(self):
        """
        Returns
        -------
        float or int
            return the objective value
        """
        return self.obj.value()


    def getVariables(self):
        """
        Returns
        -------
        set of VarElement family
        """
        return self.variables


    def solve(self, solver=None, timelimit=None, msg=False):
        """solve this problem

        Parameters
        ----------
        solver : Solver
        timelimit : float
        msg : bool
            if true, display the message from solver

        Returns
        -------
        int
            return the status of solving
        Log
            return log object
        """
        assert solver is not None or self.solver is not None, f'solver is not specified'
        if solver is not None:
            self.solver = solver
        if timelimit is not None:
            solver.setParams(timelimit=timelimit)

        if self.sense == 'minimize':
            obj = self.obj
        elif self.sense == 'maximize':
            obj = -self.obj

        solution = Solution('s', self.getVariables())

        status, log, self.time = self.solver.solve(
            solution, obj, self.constraints, self, msg=msg,
        )

        return status, log


    def getSolution(self, k=0):
        """get the k-top solution
        """
        assert k < len(self.solver.log)
        solution = self.solver.log.getSolution(k=k)
        return solution


    def setSolution(self, k=0):
        """set the k-top solution to variables
        """
        assert k < len(self.solver.log)
        solution = self.getSolution(k)
        var_dict = solution.toDict()
        for var in self.getVariables():
            var.setValue(var_dict[var.name].value())


    def __iadd__(self, other):
        if isinstance(other, Constraint):
            self.addConstraint(other)
        else:
            self.setObjective(other)
        return self


    def __str__(self):
        from collections import defaultdict
        variables_dict = defaultdict(int)
        for var in self.getVariables():
            variables_dict[var.getType()] += 1
        variables_str = ', '.join(
            [f'{key.replace("Var", "")} {value}'
                for key, value in sorted(variables_dict.items())]
            )
        s  = f'Name: {self.name}\n'
        s += f'  Type         : {self.type}\n'
        s += f'  sense        : {self.sense}\n'
        s += f'  objective    : {self.obj.name}\n'
        s += f'  #constraints : {len(self.constraints)}\n'
        s += f'  #variables   : {len(self.variables)} ({variables_str})'
        return s
