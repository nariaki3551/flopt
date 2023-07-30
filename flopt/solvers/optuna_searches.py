from optuna.study import create_study
from optuna.samplers import TPESampler, CmaEsSampler, NSGAIISampler  # , BoTorchSampler
from optuna.logging import disable_default_handler
import timeout_decorator

import flopt
from flopt.solvers.base import BaseSearch
from flopt.constants import (
    VariableType,
    ExpressionType,
    ConstraintType,
    SolverTerminateState,
)
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
                    lb = var.getLb(number=True)
                    ub = var.getUb(number=True)
                    var.setValue(trial.suggest_int(var.name, lb, ub))
                elif var.type() == VariableType.Continuous:
                    lb = var.getLb(number=True)
                    ub = var.getUb(number=True)
                    var.setValue(trial.suggest_float(var.name, lb, ub))
            obj_value = self.getObjValue(solution)

            # Constraints which are considered feasible if less than or equal to zero.
            optuna_const_values = list()
            for const in self.prob.getConstraints():
                if const.type() == ConstraintType.Le:
                    optuna_const_values.append(const.value(solution))
                elif const.type() == ConstraintType.Eq:
                    optuna_const_values.append(const.value(solution))
                    optuna_const_values.append(-const.value(solution))
                else:
                    raise Exception()

            # Store the constraints as user attributes so that they can be restored after optimization.
            trial.set_user_attr("constraint", optuna_const_values)

            # update best solution if needed
            if self.prob.getConstraints():
                if all(
                    const.feasible(solution) for const in self.prob.getConstraints()
                ):
                    self.registerSolution(solution, obj_value)
            else:
                self.registerSolution(solution, obj_value)

            # callback
            self.callback([solution])

            return obj_value

        self.end_build()
        search_timelimit = max(0, self.timelimit - self.build_time)

        @timeout_decorator.timeout(search_timelimit, timeout_exception=TimeoutError)
        def optimize():
            self.study.optimize(objective_func, self.n_trial, timeout=search_timelimit)

        def set_best_value():
            if self.best_obj_value < float("inf"):
                for var in self.best_solution:
                    solution.toDict()[var.name].setValue(var.value())

        try:
            optimize()
        except TimeoutError as e:
            set_best_value()
            raise e
        except ValueError as e:
            logger.warning(e)
            set_best_value()
            raise flopt.error.SolverError()

        set_best_value()

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
        prob += x + y >= 0

        status, log = prob.solve(solver="OptunaTPE", msg=True, timelimit=1)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
    """

    name = "OptunaTPE"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Any,
    }

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
        create sampler and Study object
        """

        disable_default_handler()
        constraints = lambda trial: trial.user_attrs["constraint"]
        sampler = TPESampler(
            consider_prior=self.consider_prior,
            prior_weight=self.prior_weight,
            consider_magic_clip=self.consider_magic_clip,
            consider_endpoints=self.consider_endpoints,
            n_startup_trials=self.n_startup_trials,
            n_ei_candidates=self.n_ei_candidates,
            seed=self.seed,
            constraints_func=constraints,
        )
        self.study = create_study(sampler=sampler)


class OptunaCmaEsSearch(OptunaSearch):
    """
    Covariance Matrix Adaptation Evolution Strategy (CMA-ES) search of Optuna.
    https://optuna.readthedocs.io/en/latest/reference/samplers/generated/optuna.samplers.CmaEsSampler.html

    Parameters
    ----------
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

        status, log = prob.solve(solver="OptunaCmaEs", msg=True, timelimit=1)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
        >>> obj = -0.2857142857142857
        >>> x = -0.14285714185152507
        >>> y = -0.4285714299429902
    """

    name = "OptunaCmaEs"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }

    def __init__(self):
        super().__init__()
        self.sigma0 = None
        self.n_startup_trials = 1
        self.independent_sampler = None
        self.warn_independent_sampling = False
        self.seed = None

    def createStudy(self, solution):
        disable_default_handler()
        x0 = dict()
        for var in solution:
            if var.type() == VariableType.Spin:
                x0[var.name] = (var.value() + 1) / 2
            else:
                x0[var.name] = var.value()
        sampler = CmaEsSampler(
            x0=x0,
            sigma0=self.sigma0,
            n_startup_trials=self.n_startup_trials,
            independent_sampler=self.independent_sampler,
            warn_independent_sampling=self.warn_independent_sampling,
            seed=self.seed,
        )
        self.study = create_study(sampler=sampler)


class OptunaNSGAIISearch(OptunaSearch):
    """
    Multi-objective sampler using the NSGA-II algorithm of Optuna.

    Parameters
    ----------
    name : str
        name
    population_size : int
    mutation_prob : float
    crossover : ---
    crossover_prob : float
    swapping_prob : float
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
        prob += x + y >= 0

        status, log = prob.solve(solver="OptunaNSGAII", msg=True, timelimit=1)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
    """

    name = "OptunaNSGAII"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Any,
    }

    def __init__(self):
        super().__init__()
        self.population_size = 50
        self.mutation_prob = None
        self.crossover = None
        self.crossover_prob = 0.9
        self.swapping_prob = 0.5
        self.seed = None

    def createStudy(self, *args):
        """
        create sampler and Study object
        """

        disable_default_handler()
        constraints = lambda trial: trial.user_attrs["constraint"]
        sampler = NSGAIISampler(
            population_size=self.population_size,
            mutation_prob=self.mutation_prob,
            crossover=self.crossover,
            crossover_prob=self.crossover_prob,
            swapping_prob=self.swapping_prob,
            seed=self.seed,
            constraints_func=constraints,
        )
        self.study = create_study(sampler=sampler)
