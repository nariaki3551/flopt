from time import time
import optuna
optuna.logging.disable_default_handler()

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message
)

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
        """
        set study by each solver
        """
        pass

    def search(self):
        status = 0
        self.startProcess()
        self.createStudy()
        self.study.optimize(self.objective, self.n_trial, timeout=self.timelimit)
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
                during_solver_message('*', obj_value, time()-self.start_time, self.trial_ix)

        # callback
        for callback in self.callbacks:
            callback([self.solution], self.best_solution, self.best_obj_value)

        return obj_value

    def startProcess(self):
        self.best_obj_value = self.obj.value(self.best_solution)
        self.recordLog()

        if self.msg:
            during_solver_message_header()
            during_solver_message('S', self.best_obj_value,
                time()-self.start_time, self.trial_ix)

    def closeProcess(self):
        self.recordLog()

