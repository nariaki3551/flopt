import time

import flopt
from flopt.solvers.solver_utils import (
    Log,
    start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message,
)
from flopt.constants import VariableType, ExpressionType, SolverTerminateState
import flopt.error
from flopt.env import setup_logger


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
    best_bound : float
        best lower bound value
    solution : Solution
        solution
    obj : ObjectiveFunction
        objective function
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
    build_time : float
        time to build the problem for solver
    start_time : float
        start time at calling solve()
    trial_ix : int
        number of trials
    max_k : int
        number of save solutions
    save_solution : bool
        flag for coping solution to log
    """

    name = "BaseSearch(base)"
    can_solve_problems = []

    def __init__(self):
        # base information
        self.feasible_guard = "clip"
        # core variables
        self.best_solution = None
        self.best_obj_value = float("inf")
        self.best_bound = None
        self.solution = None
        # parameters
        self.timelimit = float("inf")
        self.lowerbound = -float("inf")
        self.tol = 1e-10
        self.msg = False
        self.callbacks = []
        # for log
        self.log = Log()
        self.build_time = 0.0
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
        """reset solving log and status"""
        self.log = Log()
        self.best_obj_value = float("inf")
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
        self.start_search()

        if not self.available(prob, verbose=True):
            logger.error(f"Problem can not be solved by solver {self.name}.")
            status = SolverTerminateState.Abnormal
            raise flopt.error.SolverError

        self.log = Log()
        self.solution = solution.clone()
        self.prob = prob
        self.msg = msg
        self.best_solution = solution

        if msg:
            params = {"timelimit": self.timelimit}
            start_solver_message(self.name, params, solution)

        try:
            self.startProcess()
            status = self.search()
            self.closeProcess()
        except TimeoutError:
            status = SolverTerminateState.Timelimit
        except flopt.error.SolverError:
            status = SolverTerminateState.Error
        except flopt.error.RearchLowerbound:
            status = SolverTerminateState.Lowerbound
        except KeyboardInterrupt:
            print("Get user ctrl-cuser ctrl-c")
            status = SolverTerminateState.Interrupt

        self.recordLog()

        if msg:
            obj_value = self.prob.obj.value(self.best_solution)
            end_solver_message(
                status,
                obj_value,
                self.build_time,
                time.time() - self.start_time,
                self.trial_ix,
            )

        return status, self.log, time.time() - self.start_time

    def start_build(self):
        self.build_time = -time.time()

    def end_build(self):
        self.build_time += time.time()

    def start_search(self):
        self.start_time = time.time()

    def registerSolution(self, solution, obj_value=None, msg_tol=None):
        """update solution if the solution is better than the incumbent

        Parameters
        ----------
        solution : Solution
        obj_value : None or float
            objective value of solution, if it is None, then calculate objective value in this function
        msg_tol : None of float
            output the message when solution is updated greater than msg_tol
        """
        if obj_value is None:
            obj_value = self.getObjValue(solution)
        if obj_value < self.best_obj_value:
            if msg_tol is not None:
                diff = self.best_obj_value - obj_value
            self.updateSolution(solution, obj_value)
            self.recordLog()
            if self.msg:
                if msg_tol is None or diff > msg_tol:
                    self.during_solver_message("*")

    def updateSolution(self, solution, obj_value=None):
        """update self.best_solution

        Parameters
        ----------
        solution : Solution
        obj_value : None or float
            objective value of solution, if it is None, then calculate objective value in this function
        """
        self.best_solution.copy(solution)
        if obj_value is None:
            self.best_obj_value = self.prob.obj.value(solution)
        else:
            self.best_obj_value = obj_value
        self.save_solution = True
        if self.best_obj_value < self.lowerbound + self.tol:
            if self.msg:
                self.during_solver_message("*")
            raise flopt.error.RearchLowerbound()

    def raiseTimeoutIfNeeded(self):
        if time.time() - self.start_time > self.timelimit:
            raise TimeoutError

    def recordLog(self):
        """
        write log in `self.log`
        """
        log_dict = {
            "obj_value": self.best_obj_value,
            "best_bound": self.best_bound,
            "time": time.time() - self.start_time,
            "iteration": self.trial_ix,
        }

        if self.max_k > 1 and self.save_solution:
            self.log.appendSolution(
                self.best_solution.clone(), self.best_obj_value, self.max_k
            )
            self.save_solution = False
        self.log.append(log_dict)

    def during_solver_message(self, head):
        """
        Parameters
        ----------
        head : str
            character of header
        """
        during_solver_message(
            head,
            self.best_obj_value,
            self.best_bound,
            time.time() - self.start_time,
            self.trial_ix,
        )

    def search(self):
        raise NotImplementedError()

    def available(self, prob, verbose=False):
        assert hasattr(self, "can_solve_problems")
        assert isinstance(self.can_solve_problems, dict)
        assert {"Variable", "Objective", "Constraint"} == set(
            self.can_solve_problems.keys()
        )
        assert isinstance(self.can_solve_problems["Variable"], VariableType)
        assert isinstance(self.can_solve_problems["Objective"], ExpressionType)
        assert isinstance(self.can_solve_problems["Constraint"], ExpressionType)

        # Variables
        available_variables = self.can_solve_problems["Variable"].expand()
        for var in prob.getVariables():
            if not var.type() in available_variables:
                if verbose:
                    logger.error(
                        f"variable: \n{var}\n must be in {available_variables}, but got {var.type()}"
                    )
                return False

        # Objective
        available_objective = self.can_solve_problems["Objective"].expand()
        if not prob.obj.type() in available_objective:
            if verbose:
                logger.error(
                    f"objective function: \n{prob.obj}\n must be in {available_objective}, but got {prob.obj.type()}"
                )
            return False

        # Constraint
        if self.can_solve_problems["Constraint"] == ExpressionType.Non:
            if prob.constraints:
                if verbose:
                    logger.error(f"constraints are not available")
                return False
        else:
            available_constraint = self.can_solve_problems["Objective"].expand()
            for const in prob.constraints:
                if not const.expression.type() in available_constraint:
                    if verbose:
                        logger.error(
                            f"constraint: \n{const}\n must be in {available_constraint}, but got {const.expression.type()}"
                        )
                    return False

        return True

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
        """process of beginning of search"""
        if all(const.feasible(self.best_solution) for const in self.prob.constraints):
            self.best_obj_value = self.prob.obj.value(self.best_solution)
        else:
            self.best_obj_value = float("inf")
        self.recordLog()
        if self.best_obj_value < self.lowerbound + self.tol:
            raise flopt.error.RearchLowerbound()

        if self.msg:
            during_solver_message_header()
            self.during_solver_message("S")

    def closeProcess(self):
        """process of ending of search"""
        self.recordLog()
