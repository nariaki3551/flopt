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

    def __init__(self):
        super().__init__()
        self.name = "OptunaSearch(base)"
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
            if not var.type() in {
                VariableType.Continuous,
                VariableType.Integer,
                VariableType.Binary,
            }:
                if verbose:
                    logger.error(
                        f"variable: \n{var}\n must be continuous, integer, or binary, but got {var.type()}"
                    )
                return False
        if prob.constraints:
            if verbose:
                logger.error(f"this solver can not handle constraints")
            return False
        return True

    def search(self):
        self.createStudy()
        try:
            self.study.optimize(self.objective, self.n_trial, timeout=self.timelimit)
        except Exception as e:
            logger.info(f"Exception {e}")
            return SolverTerminateState.Abnormal
        return SolverTerminateState.Normal

    def objective(self, trial):
        # set value into self.solution
        self.trial_ix += 1
        for var in self.solution:
            if var.type() == VariableType.Integer:
                var._value = trial.suggest_int(var.name, var.getLb(), var.getUb())
            elif var.type() == VariableType.Continuous:
                var._value = trial.suggest_uniform(var.name, var.getLb(), var.getUb())

        # get objective value by self.solution
        obj_value = self.getObjValue(self.solution)

        # if solution is better thatn incumbent, then update best solution
        self.registerSolution(self.solution, obj_value)

        # callback
        for callback in self.callbacks:
            callback([self.solution], self.best_solution, self.best_obj_value)

        return obj_value
