import inspect
from time import time
import flopt
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message,
)
from flopt.env import setup_logger
import flopt.constants


logger = setup_logger(__name__)


class BaseSearch:
    """
    Base Search Class

    For developer;

    - `self.best_solution` has references to variables defined by the user
    - `self.obj.value(solution)` returns the objective value by the solution
    - `self.recordLog()` records the log (objective value, time, iteratino)
      for each time incumbent solution (`self.bset_solution`) is updated.

    Parameters
    ----------
    name : str
        name of solver
    feasible_guard : str
        type of guarder to keep feasibility of solution
    can_solve_problems : list of str
        problem names can be solved by this solver
    best_solution : Solution
        best solution
    best_obj_value : float
        incumbent objective value
    best_bd : float
        best lower bound value
    solution : Solution
        solution
    obj : ObjectiveFunction
        objective function
    feasible_guard : str
        type of guarder to keep feasibility of solution
    timelimit : float
        timelimit, unit is second
    msg : bool
        if true, then display logs
    callbacks : list of function
       List of callback functions that are invoked at the end of each trial.
       Each function must accept three parameters with the following types
       in this order: list of solution object, best_solution, best_obj_value
    log : Log
        Solver Log class
    start_time : time()
        start_time of solver
    trial_ix : int
        number of trials
    """
    def __init__(self):
        # base information
        self.name = 'BaseSearch(base)'
        self.feasible_guard = 'clip'
        # each solver
        self.can_solve_problems = []
        # core variables
        self.best_solution = None
        self.best_obj_value = float('inf')
        self.best_bd = None
        self.solution = None
        self.obj = None
        # parameters
        self.timelimit = float('inf')
        self.msg = False
        self.callbacks = []
        # for log
        self.log = Log()
        self.start_time = None
        self.trial_ix = 0


    def setParams(self, params=None, feasible_guard=None, **kwargs):
        """
        set some parameters

        Parameters
        ----------
        params : dict
            {paramname: paramvalue}
        feasible_guard : str
            'clip' is noly selectable
        """
        if params is not None:
            for param, value in params.items():
                setattr(self, param, value)
        if feasible_guard is not None:
            self.feasible_guard = feasible_guard
        for param, value in kwargs.items():
            setattr(self, param, value)


    def reset(self):
        """
        reset log, best_obj_value, start_time, trial_ix
        """
        self.log = Log()
        self.best_obj_value = float('inf')
        self.start_time = None
        self.trial_ix = 0


    def solve(self, solution, obj, constraints, prob=None, msg=False):
        """
        solve the problem of (solution, obj)

        Parameters
        ----------
        solution : Solution
            solution object
        obj : expression or VarElement family
            objective function
        constraints : list of Constraint
            constraints
        prob : Problem
            problem
        msg : bool
            if true, then display logs

        Returns
        -------
        status, Log
        """
        if prob is not None and not self.available(prob):
            status = flopt.constants.SOLVER_ABNORMAL_TERMINATE
            raise flopt.constants.SolverError

        self.best_solution = solution
        self.solution = solution.clone()
        self.obj = obj
        self.constraints = constraints
        self.start_time = time()
        self.msg = msg

        if msg:
            params = {'timelimit': self.timelimit}
            start_solver_message(self.name, params, solution)

        try:
            status = self.search()
        except KeyboardInterrupt:
            print('Get user ctrl-cuser ctrl-c')
            status = flopt.constants.SOLVER_INTERRUPT_TERMINATE

        if msg:
            obj_value = self.obj.value(self.best_solution)
            end_solver_message(status, obj_value, time()-self.start_time)

        return status, self.log, time()-self.start_time


    def updateSolution(self, solution, obj_value=None):
        """
        update self.best_solution
        """
        self.best_solution.copy(solution)
        if obj_value is None:
            self.best_obj_value = self.obj.value(solution)
        else:
            self.best_obj_value = obj_value


    def recordLog(self):
        """
        write log in `self.log`
        """
        self.log.append({
            'obj_value': self.best_obj_value,
            'best_bd': self.best_bd,
            'time': time()-self.start_time,
            'iteration': self.trial_ix
        })


    def during_solver_message(self, head):
        during_solver_message(head, self.best_obj_value,
            self.best_bd, time()-self.start_time, self.trial_ix)


    def search(self):
        raise NotImplementedError


    def available(self, prob):
        raise NotImplementedError


    def __str__(self):
        s  = f'Name: Solver\n'
        s += f'  Type : {self.name}\n'
        attrobjs = [
            (attr, obj) for (attr, obj) in inspect.getmembers(self)
            if not callable(obj) and attr[:2] != "__" and attr[-2:] != "__" and attr != 'name'
        ]
        for attr, obj in attrobjs:
            s += f'  {attr} : {obj}\n'
        s += '\n'
        return s


