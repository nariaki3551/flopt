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


class OptunaSearch(BaseSearch):
    """
    Optuna Update
      It has a incumbent solution anytime
      1. Generate a new solution using Optuna sampler
      2. Check a new solution can be incumbent solutions
      3. Update incumbent solution

    Parameters
    ----------
    n_trial : int
        number of trials
    """
    def __init__(self):
        super().__init__()
        self.name = 'OptunaSearch(base)'
        self.n_trial = 1e100


    def createStudy(self):
        raise NotImplementedError


    def available(self, prob):
        """
        Parameters
        ----------
        obj : Expression or VarElement family
            objective function
        constraints : list of Constraint
            constraints

        Returns
        -------
        bool
            return true if it can solve the problem else false
        """
        return all(not var.getType() == 'VarPermutation' for var in prob.getVariables())\
                and (not prob.constraints)


    def search(self):
        if self.constraints:
            logger.error("This Solver does not support the problem with constraints.")
            status = flopt.constants.SOLVER_ABNORMAL_TERMINATE
            return status

        status = flopt.constants.SOLVER_NORMAL_TERMINATE
        self.startProcess()
        self.createStudy()
        try:
            self.study.optimize(self.objective, self.n_trial, timeout=self.timelimit)
        except Exception as e:
            logger.info(f'Exception {e}')
            status = flopt.constants.SOLVER_ABNORMAL_TERMINATE
        self.closeProcess()
        return status

    def objective(self, trial):
        # set value into self.solution
        self.trial_ix += 1
        for var in self.solution:
            if var.getType() == 'VarInteger':
                var._value = trial.suggest_int(
                    var.name, var.lowBound, var.upBound
                )
            elif var.getType() == 'VarContinuous':
                var._value = trial.suggest_uniform(
                    var.name, var.lowBound, var.upBound
                )

        # get objective value by self.solution
        obj_value = self.obj.value(self.solution)

        # check whether update or not
        if obj_value < self.best_obj_value:
            self.updateSolution(self.solution, obj_value)
            self.recordLog()
            if self.msg:
                self.during_solver_message('*')

        # callback
        for callback in self.callbacks:
            callback([self.solution], self.best_solution, self.best_obj_value)

        return obj_value


    def startProcess(self):
        self.best_obj_value = self.obj.value(self.best_solution)
        self.recordLog()

        if self.msg:
            during_solver_message_header()
            self.during_solver_message('S')


    def closeProcess(self):
        self.recordLog()

