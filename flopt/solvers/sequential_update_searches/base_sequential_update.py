from time import time

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message
)
from flopt.env import setup_logger
import flopt.constants


logger = setup_logger(__name__)


class SequentialUpdateSearch(BaseSearch):
    """
    Sequential Update Search Base Class.
    It has a incumbent solution anytime

    1. Generate a new solution
    2. Check a new solution can be incumbent solutions
    3. If the new solution is an incumbent solution,
       then update best solution by it.
    4. Repeat 1--3

    Each child class, define `self.set_new_sol()` function which
    generates a new solution and sets it to self.variabels.
    For example, see RandomSearch class.

    Parameters
    ----------
    n_trial : str
        number of trials
    """
    def __init__(self):
        super().__init__()
        self.name = 'SequentialUpdate(base)'
        self.n_trial = 1e100


    def search(self):
        """
        search a better solution using `self.setNewSolution()` function
        `self.setNewSolution()` generate new solution and set it into self.solution
        """
        if self.constraints:
            logger.error("This Solver does not support the problem with constraints.")
            status = flopt.constants.SOLVER_ABNORMAL_TERMINATE
            return status

        self.startProcess()
        status = flopt.constants.SOLVER_NORMAL_TERMINATE

        for self.trial_ix in range(1, int(self.n_trial)+1):
            # check time limit
            if time() > self.start_time + self.timelimit:
                self.closeProcess()
                status = flopt.constants.SOLVER_TIMELIMIT_TERMINATE
                return status

            # generate new solution and set it into self.solution
            self.setNewSolution()
            obj_value = self.obj.value(self.solution)

            # check whether update or not
            if obj_value < self.best_obj_value:
                self.updateSolution(self.solution, obj_value)
                self.recordLog()
                if self.msg:
                    self.during_solver_message('*')

            # callbacks
            for callback in self.callbacks:
                callback([self.solution], self.best_solution, self.best_obj_value)

        self.closeProcess()
        return status


    def startProcess(self):
        """
        set initial value to self variables and objective value
        , and display start log
        """
        self.best_obj_value = self.obj.value(self.best_solution)
        self.recordLog()

        if self.msg:
            during_solver_message_header()
            self.during_solver_message('S')


    def closeProcess(self):
        self.recordLog()

