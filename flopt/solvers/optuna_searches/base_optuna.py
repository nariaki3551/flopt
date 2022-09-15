import timeout_decorator

import flopt
from flopt.solvers.base import BaseSearch
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

    name = "OptunaSearch(base)"

    def __init__(self):
        super().__init__()
        self.n_trial = 1e100

    def createStudy(self):
        raise NotImplementedError()

    def available(self, prob, verbose=False):
        """
        Parameters
        ----------
        prob : Problem
        verbose : bool

        Returns
        -------
        bool
            return true if it can solve the problem else false
        """
        for var in prob.getVariables():
            if var.type() == VariableType.Permutation:
                if verbose:
                    logger.error(f"variable: \n{var}\n must not be permutation")
                return False
        if prob.constraints:
            if verbose:
                logger.error(f"this solver can not handle constraints")
            return False
        return True

    def search(self):
        self.start_build()

        self.createStudy()

        self.end_build()

        search_timelimit = self.timelimit - self.build_time

        @timeout_decorator.timeout(search_timelimit, timeout_exception=TimeoutError)
        def optimize():
            self.study.optimize(self.objective, self.n_trial, timeout=search_timelimit)

        optimize()

        return SolverTerminateState.Normal

    def objective(self, trial):
        # set value into self.solution
        self.trial_ix += 1
        for var in self.solution:
            if var.type() == VariableType.Binary:
                var.setValue(trial.suggest_int(var.name, 0, 1))
            elif var.type() == VariableType.Spin:
                var.toBinary()
                var.binary.setValue(trial.suggest_int(var.name, 0, 1))
            lb = var.getLb(must_number=True)
            ub = var.getUb(must_number=True)
            if var.type() == VariableType.Integer:
                var.setValue(trial.suggest_int(var.name, lb, ub))
            elif var.type() == VariableType.Continuous:
                var.setValue(trial.suggest_uniform(var.name, lb, ub))

        # get objective value by self.solution
        obj_value = self.getObjValue(self.solution)

        # if solution is better thatn incumbent, then update best solution
        self.registerSolution(self.solution, obj_value)

        # callback
        for callback in self.callbacks:
            callback([self.solution], self.best_solution, self.best_obj_value)

        return obj_value
