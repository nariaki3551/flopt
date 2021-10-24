import time

import flopt
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message,
)
from flopt.env import setup_logger
from flopt.constants import SolverTerminateState
import flopt.error


logger = setup_logger(__name__)


class BaseSearch:
    """Base Search Class

    For developer;

    - `self.best_solution` has references to variables defined by the user
    - `self.getObjValue(solution)` returns the objective value by the solution
    - `self.recordLog()` records the log (objective value, time, iteratino)
      for each time incumbent solution (`self.bset_solution`) is updated.

    Attributes
    ----------
    name : str
        name of solver
    feasible_guard : str
        type of guarder to keep feasibility of solution
    can_solve_problems : list of {'blackbox', 'lp', 'qp', 'permutation'}
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
    lowerbound : float
        solver terminates when it obtains the solution whose objective value is lower than this
    msg : bool
        if true, then display logs
    callbacks : list of function
       List of callback functions that are invoked at the end of each trial.
       Each function must accept three parameters with the following types
       in this order: list of solution object, best_solution, best_obj_value
    log : Log
        Solver Log class
    start_time : float
        start_time of solver
    trial_ix : int
        number of trials
    max_k : int
        number of save solutions
    save_solution : bool
        flag for coping solution to log
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
        # parameters
        self.timelimit = float('inf')
        self.lowerbound = -float('inf')
        self.tol = 1e-10
        self.msg = False
        self.callbacks = []
        # for log
        self.log = Log()
        self.start_time = None
        self.trial_ix = 0
        self.max_k = 1
        self.save_solution = False


    def setParams(self, params=None, feasible_guard=None, **kwargs):
        """set some parameters

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
        """reset solving log and status
        """
        self.log = Log()
        self.best_obj_value = float('inf')
        self.start_time = None
        self.trial_ix = 0
        self.max_k = 1
        self.save_solution = False


    def solve(self, solution, prob, msg=False):
        """solve the problem of (solution, obj)

        Parameters
        ----------
        solution : Solution
            solution object
        prob : Problem
            problem
        msg : bool
            if true, then display logs

        Returns
        -------
        status, Log
        """
        if not self.available(prob):
            logger.error(f'Problem can not be solved by solver {self.name}.')
            status = SolverTerminateState.Abnormal
            raise flopt.error.SolverError

        self.solution = solution.clone()
        self.prob = prob
        self.msg = msg
        self.best_solution = solution

        self.start_time = time.time()
        if msg:
            params = {'timelimit': self.timelimit}
            start_solver_message(self.name, params, solution)

        try:
            self.startProcess()
            status = self.search()
            self.closeProcess()
        except flopt.error.RearchLowerbound:
            status = SolverTerminateState.Lowerbound
        except KeyboardInterrupt:
            print('Get user ctrl-cuser ctrl-c')
            status = SolverTerminateState.Interrupt

        if msg:
            obj_value = self.prob.obj.value(self.best_solution)
            end_solver_message(status, obj_value, time.time()-self.start_time)

        return status, self.log, time.time()-self.start_time


    def updateSolution(self, solution, obj_value=None):
        """update self.best_solution
        """
        self.best_solution.copy(solution)
        if obj_value is None:
            self.best_obj_value = self.prob.obj.value(solution)
        else:
            self.best_obj_value = obj_value
            self.save_solution = True


    def recordLog(self):
        """write log in `self.log`
        """
        log_dict = {
            'obj_value': self.best_obj_value,
            'best_bd': self.best_bd,
            'time': time.time()-self.start_time,
            'iteration': self.trial_ix
        }
        if self.max_k > 1 and self.save_solution:
            log_dict['solution'] = self.best_solution.clone()
            self.save_solution = False
        self.log.append(log_dict)
        if self.best_obj_value < self.lowerbound + self.tol:
            if self.msg:
                self.during_solver_message('*')
            raise flopt.error.RearchLowerbound()


    def during_solver_message(self, head):
        during_solver_message(head, self.best_obj_value,
            self.best_bd, time.time()-self.start_time, self.trial_ix)


    def search(self):
        raise NotImplementedError()


    def available(self, prob):
        raise NotImplementedError()


    def getObjValue(self, solution):
        """calculate objective value

        Parameters
        ----------
        solution : Solution

        Returns
        -------
        int or float
        """
        return self.prob.obj.value(solution)


    def startProcess(self):
        """process of beginning of search
        """
        if all(const.feasible(self.best_solution) for const in self.prob.constraints):
            self.best_obj_value = self.prob.obj.value(self.best_solution)
        else:
            self.best_obj_value = float('inf')
        self.recordLog()
        if self.best_obj_value < self.lowerbound + self.tol:
            raise flopt.error.RearchLowerbound()

        if self.msg:
            during_solver_message_header()
            self.during_solver_message('S')


    def closeProcess(self):
        """process of ending of search
        """
        self.recordLog()
