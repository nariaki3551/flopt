from optuna.study import create_study
from optuna.samplers import CmaEsSampler, TPESampler
from optuna.logging import disable_default_handler
import timeout_decorator

import flopt
from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, ExpressionType, SolverTerminateState
from flopt.env import setup_logger


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

    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }

    def __init__(self):
        super().__init__()
        self.n_trial = 1e100

    def createStudy(self):
        raise NotImplementedError()

    def search(self, solution, *args):
        self.start_build()
        self.createStudy(solution)

        def objective_func(trial):
            # set value into solution
            for var in solution:
                if var.type() == VariableType.Binary:
                    var.setValue(trial.suggest_int(var.name, 0, 1))
                elif var.type() == VariableType.Spin:
                    var.toBinary()
                    var.binary.setValue(trial.suggest_int(var.name, 0, 1))
                elif var.type() == VariableType.Integer:
                    lb = var.getLb(must_number=True)
                    ub = var.getUb(must_number=True)
                    var.setValue(trial.suggest_int(var.name, lb, ub))
                elif var.type() == VariableType.Continuous:
                    lb = var.getLb(must_number=True)
                    ub = var.getUb(must_number=True)
                    var.setValue(trial.suggest_uniform(var.name, lb, ub))
            obj_value = self.getObjValue(solution)

            # update best solution if needed
            self.registerSolution(solution, obj_value)

            # callback
            self.callback([solution])

            return obj_value

        self.end_build()
        search_timelimit = self.timelimit - self.build_time

        @timeout_decorator.timeout(search_timelimit, timeout_exception=TimeoutError)
        def optimize():
            self.study.optimize(objective_func, self.n_trial, timeout=search_timelimit)

        optimize()

        return SolverTerminateState.Normal


class OptunaTPESearch(OptunaSearch):
    """
    Tree-structured Parzen Estimator (TPE) Sampling Search of Optuna.
    https://optuna.readthedocs.io/en/latest/reference/samplers/generated/optuna.samplers.TPESampler.html

    Parameters
    ----------
    name : str
        name
    consider_prior : bool
    consider_magic_clip : bool
    consider_endpoints : bool
    n_startup_trials : int
    n_ei_candidates : int
    seed : float
        seed of random generater

    Examples
    --------

    .. code-block:: python

        import flopt

        x = flopt.Variable("x", lowBound=-1, upBound=1, cat="Continuous")
        y = flopt.Variable("y", lowBound=-1, upBound=1, cat="Continuous")

        prob = flopt.Problem()
        prob += 2*x*x + x*y + y*y + x + y

        solver = flopt.Solver("OptunaTPESearch")
        status, log = prob.solve(solver, msg=True, timelimit=1)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
    """

    name = "OptunaTPESearch"

    def __init__(self):
        super().__init__()
        self.consider_prior = True
        self.prior_weight = 1.0
        self.consider_magic_clip = True
        self.consider_endpoints = False
        self.n_startup_trials = 10
        self.n_ei_candidates = 24
        self.seed = None

    def createStudy(self, *args):
        """
        create sampler and create Study object
        """

        disable_default_handler()
        sampler = TPESampler(
            consider_prior=self.consider_prior,
            prior_weight=self.prior_weight,
            consider_magic_clip=self.consider_magic_clip,
            consider_endpoints=self.consider_endpoints,
            n_startup_trials=self.n_startup_trials,
            n_ei_candidates=self.n_ei_candidates,
            seed=self.seed,
        )
        self.study = create_study(sampler=sampler)


class OptunaCmaEsSearch(OptunaSearch):
    """
    Covariance Matrix Adaptation Evolution Strategy (CMA-ES) search of Optuna.
    https://optuna.readthedocs.io/en/latest/reference/samplers/generated/optuna.samplers.CmaEsSampler.html

    Parameters
    ----------
    x0
    sigma0
    n_startup_trials
    independent_sampler
    warn_independe_sampling
    seed

    Examples
    --------

    .. code-block:: python

        import flopt

        x = flopt.Variable("x", lowBound=-1, upBound=1, cat="Continuous")
        y = flopt.Variable("y", lowBound=-1, upBound=1, cat="Continuous")

        prob = flopt.Problem()
        prob += 2*x*x + x*y + y*y + x + y

        solver = flopt.Solver("OptunaCmaEsSearch")
        status, log = prob.solve(solver, msg=True, timelimit=1)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
        >>> obj = -0.2857142857142857
        >>> x = -0.14285714185152507
        >>> y = -0.4285714299429902
    """

    name = "OptunaCmaEsSearch"

    def __init__(self):
        super().__init__()
        self.x0 = None
        self.sigma0 = None
        self.n_startup_trials = 1
        self.independent_sampler = None
        self.warn_independent_sampling = False
        self.seed = None

    def createStudy(self, solution):
        disable_default_handler()
        if self.x0 is None:
            x0 = {var.name: var.value() for var in solution}
        sampler = CmaEsSampler(
            x0=x0,
            sigma0=self.sigma0,
            n_startup_trials=self.n_startup_trials,
            independent_sampler=self.independent_sampler,
            warn_independent_sampling=self.warn_independent_sampling,
            seed=self.seed,
        )
        self.study = create_study(sampler=sampler)
