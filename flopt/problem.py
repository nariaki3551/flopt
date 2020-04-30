from .expression import Expression, ExpressionConst
from .custom_object import CustomObject
from .solution import Solution
from .solvers import Solver

class Problem:
    """
    Interface between User and Solver

    Parameters
    ----------
    name : str
        name of problem
    sense : str, optional
        minimize or maximize
    obj : Expression or CustomObject
        objective function
    variables : set of VarElement family
        variables
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
        self.name = name
        self.sense = sense
        self.obj = ExpressionConst(0)
        self.variables = []
        self.time = None
        self.prob_type = ['blackbox']
    
    def setObjective(self, obj):
        """
        set objective function

        Parameters
        ----------
        obj : VarElement family, Expression or CustomObject
            objective functioon
        """
        if isinstance(obj, (int, float)):
            obj = ExpressionConst(obj)
        self.obj = obj
        self.variables = obj.getVariables()
    
    def getObjectiveValue(self):
        """
        Returns
        -------
        float or int
            return the objective value
        """
        return self.obj.value()

    def solve(self, solver=None, timelimit=None, msg=False):
        """
        solve this problem;
        objective function is self.obj;
        variables is self.variables

        Parameters
        ----------
        solver : Solver
            solver
        timelimit : float
            timelimit
        msg : bool
            if true, display the message from solver

        Returns
        -------
        int
            return the status of solving
        Log
            return log object
        """
        if self.sense == 'minimize':
            obj = ObjectiveFunction(self.obj)
        elif self.sense == 'maximize':
            obj = ObjectiveFunction(-self.obj)
        
        if solver is None:
          solver = Solver(algo='RandomSearch')
        if timelimit is not None:
          solver.setParams(timelimit=timelimit)

        # convert for soluver
        solution = Solution('s', self.variables)

        status, log, self.time = solver.solve(
            solution, obj, msg=msg
        )

        return status, log

    def __iadd__(self, other):
        self.setObjective(other)
        return self

    def __str__(self):
        obj_str = ",".join(self.obj.__str__().split("\n"))
        s  = f'Name: {self.name}\n'
        s += f'  Type       : Problem\n'
        s += f'  sense      : {self.sense}\n'
        s += f'  objective  : {obj_str}\n'
        s += f'  #variables : {len(self.variables)}'
        return s


class ObjectiveFunction:
    """
    Objective Function for Solver

    ObjectiveFunction is an overwrap class for expression and customObjects.
    In this class, by specifying the value argument as a solution,
    we can compute the objective value of the solution.

    Parameters
    ----------
    obj : Expression or CustomObject
        objective function
    type : str
        'Expression' or 'CustomObject'
    """
    def __init__(self, obj):
        self.obj = obj
        if isinstance(self.obj, Expression):
            self.type = 'Expression'
        elif isinstance(self.obj, CustomObject):
            self.type = 'CustomObject'

    def value(self, solution):
        """
        Parameters
        ----------
        solution : Solution
            solution

        Returns
        -------
        float
            the objective value with respect to the solution
        """
        if self.type == 'Expression':
            var_dict = {var.name : var for var in solution}
            self.obj.setVarDict(var_dict)
            return self.obj.value()
        if self.type == 'CustomObject':
            var_list = solution.getVariables()
            self.obj.setVarList(var_list)
            return self.obj.value()
