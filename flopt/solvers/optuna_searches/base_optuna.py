from time import time

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    during_solver_message,
)
from flopt.env import setup_logger
from flopt.constants import VariableType, SolverTerminateState


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
        raise NotImplementedError()


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
        return all(
                var.type() in {VariableType.Continuous, VariableType.Integer, VariableType.Binary}
                for var in prob.getVariables()
                ) and ( not prob.constraints )


    def search(self):
        status = SolverTerminateState.Normal
        self.createStudy()
        try:
            self.study.optimize(self.objective, self.n_trial, timeout=self.timelimit)
        except Exception as e:
            logger.info(f'Exception {e}')
            status = flopt.constants.SolverTerminateState.Abnormal
        return status


    def objective(self, trial):
        # set value into self.solution
        self.trial_ix += 1
        for var in self.solution:
            if var.type() == VariableType.Integer:
                var._value = trial.suggest_int(
                    var.name, var.getLb(), var.getUb()
                )
            elif var.type() == VariableType.Continuous:
                var._value = trial.suggest_uniform(
                    var.name, var.getLb(), var.getUb()
                )

        # get objective value by self.solution
        obj_value = self.getObjValue(self.solution)

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


