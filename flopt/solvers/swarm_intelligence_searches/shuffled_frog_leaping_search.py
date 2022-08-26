import time
import random

from flopt.solvers.base import BaseSearch
from flopt.env import setup_logger
from flopt.constants import VariableType, SolverTerminateState


logger = setup_logger(__name__)


class ShuffledFrogLeapingSearch(BaseSearch):
    """
    SFLA (Shuffled Frog Leaping Search)
    It has a incumbent solution anytime.

    1. Generate new solutions as frogs at random.
    2. Divide frog set into some memeplexes.
    3. Improve each memeplex a certain number of times respectively.
    4. Update best solution.
    5. Redistribute memeplexes.
    6. Repeat step3 to step5

    Parameters
    ----------
    n_trial : int (default 1e10)
      number of memetic evolution

    n_memetic_iter : int (default 100)
      number of evolution in each memeplex

    n_memeplex : int (default 5)
      number of memeplex

    n_frog_per_memeplex : int (default 10)
      number of frog per memeplex

    max_step : float (default 0.01)
      max size of step when frog move in memetic evolution.
    """

    name = "ShuffledFrogLeapingSearch"
    can_solve_problems = ["blackbox"]

    def __init__(self):
        super().__init__()
        self.frogs = None
        self.memeplexes = None
        # params
        self.n_memeplex = 5
        self.n_frog_per_memeplex = 10
        self.n_memetic_iter = 100
        self.n_trial = int(1e10)
        self.max_step = int(1e10)

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
                    logger.error(
                        f"variable: \n{var}\n must be not permutation, but got {var.type()}"
                    )
                return False
        if prob.constraints:
            if verbose:
                logger.error(f"this solver can not handle constraints")
            return False
        return True

    def search(self):
        for i in range(self.n_trial):
            self.trial_ix += 1

            # check time limit
            if time.time() > self.start_time + self.timelimit:
                return SolverTerminateState.Timelimit

            self._memetic_evolution()

            # if solution is better thatn incumbent, then update best solution
            self.registerSolution(self.frogs[0])

            if self.msg and i % 100 == 0:
                self.during_solver_message(" ")

            # callbacks
            for callback in self.callbacks:
                callback(self.frogs, self.best_solution, self.best_obj_value)

        return SolverTerminateState.Normal

    def _memetic_evolution(self):
        """
        memetic evolution
        This function is the key to this method.
        """
        M = self.n_memeplex
        N = self.n_frog_per_memeplex
        for j, memeplex in enumerate(self.memeplexes):
            for k in range(self.n_memetic_iter):
                # make sub memeplex
                sub_mmplx_ids = random.sample(range(N), N // 2)
                sub_mmplx = [memeplex[i] for i in sorted(sub_mmplx_ids)]

                # move frog which has the worst objective
                best_frog = sub_mmplx[0]
                worst_frog = sub_mmplx[-1]
                step = random.random() * (best_frog - worst_frog)
                if step.norm() > self.max_step:
                    step = step * self.max_step / step.norm()
                new_frog = worst_frog + step

                # feasible guard
                if self.feasible_guard == "clip":
                    new_frog.clip()

                # evaluate solutions
                fitness_best = self.getObjValue(best_frog)
                fitness_worst = self.getObjValue(worst_frog)
                fitness_new = self.getObjValue(new_frog)

                # if it does not improve (1)
                if fitness_new > fitness_worst:
                    step = random.random() * (self.best_solution - worst_frog)
                    if step.norm() > self.max_step:
                        step = step * self.max_step / step.norm()
                    new_frog = worst_frog + step

                    # feasible guard
                    if self.feasible_guard == "clip":
                        new_frog.clip()

                    fitness_new = self.getObjValue(new_frog)
                    # if it does not improve (2)
                    if fitness_new > fitness_worst:
                        new_frog.setRandom()

                # the worst_frog is replaced to the new_frog
                self.memeplexes[j] = (
                    sub_mmplx[:-1]
                    + [new_frog]
                    + [memeplex[i] for i in range(N) if i not in sub_mmplx_ids]
                )

                # evaluate and sort memeplex
                for flog in self.memeplexes[j]:
                    if not hasattr(flog, "__flog_obj"):
                        setattr(flog, "__flog_obj", self.getObjValue(flog))
                self.memeplexes[j].sort(key=lambda frog: getattr(flog, "__flog_obj"))

        # sort entire memeplexes
        self.frogs = [frog for memeplex in self.memeplexes for frog in memeplex]
        self.frogs.sort(key=lambda frog: self.getObjValue(frog))
        self.memeplexes = [[self.frogs[i * M + j] for i in range(N)] for j in range(M)]

    def startProcess(self):
        super().startProcess()
        M = self.n_memeplex
        N = self.n_frog_per_memeplex
        self.frogs = [self.solution.clone() for _ in range(M * N)]
        for frog in self.frogs:
            frog.setRandom()
        self.frogs.sort(key=lambda frog: self.getObjValue(frog))
        self.memeplexes = [[self.frogs[i * M + j] for i in range(N)] for j in range(M)]
        self.updateSolution(self.frogs[0])
