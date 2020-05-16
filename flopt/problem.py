from flopt.expression import Expression, ExpressionConst
from flopt.constraint import Constraint
from flopt.custom_object import CustomObject
from flopt.solution import Solution
from flopt.solvers import Solver
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
        self.type = 'Problem'
        self.name = name
        self.sense = sense
        self.obj = ExpressionConst(0)
        self.constraints = []
        self.variables = set()
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
        self.variables |= obj.getVariables()
    
    def addConstraint(self, const, name=None):
        """
        add constraint

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
        if solver is None:
            solver = Solver(algo='RandomSearch')
        if timelimit is not None:
            solver.setParams(timelimit=timelimit)

        # convert for solver
        solution = Solution('s', self.variables)

        if self.sense == 'minimize':
            obj = ObjectiveFunction(self.obj)
        elif self.sense == 'maximize':
            obj = ObjectiveFunction(-self.obj)

        constraints = [
            Constraint(ObjectiveFunction(const.expression), const.type)
            for const in self.constraints
        ]

        status, log, self.time = solver.solve(
            solution, obj, constraints, msg=msg
        )

        return status, log

    def __iadd__(self, other):
        if isinstance(other, Constraint):
            self.addConstraint(other)
        else:
            self.setObjective(other)
        return self

    def __str__(self):
        obj_str = ",".join(self.obj.__str__().split("\n"))
        s  = f'Name: {self.name}\n'
        s += f'  Type         : {self.type}\n'
        s += f'  sense        : {self.sense}\n'
        s += f'  objective    : {obj_str}\n'
        s += f'  #constraints : {len(self.constraints)}\n'
        s += f'  #variables   : {len(self.variables)}'
        return s


class ObjectiveFunction:
    """
    TODO: rename class name
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
        if isinstance(obj, Constraint):
            obj = obj.expression
        if isinstance(obj, Expression):
            self.type = 'Expression'
            self.obj = obj
        elif isinstance(obj, CustomObject):
            self.type = 'CustomObject'
            self.obj = obj

    def value(self, solution):
        """
        Parameters
        ----------
        solution : Solution
            solution used for calculation of expressions

        Returns
        -------
        float
            the objective value with respect to the solution
        """
        if self.type == 'Expression':
            var_dict = {var.name : var for var in solution}
            self.obj.setVarDict(var_dict)
            return self.obj.value()
        elif self.type == 'CustomObject':
            var_list = solution.getVariables()
            self.obj.setVarList(var_list)
            return self.obj.value()
