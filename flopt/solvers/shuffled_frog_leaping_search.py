import random

from flopt.solution import Solution
from flopt.solvers.base import BaseSearch
from flopt.env import setup_logger
from flopt.constants import VariableType, ExpressionType, SolverTerminateState

logger = setup_logger(__name__)


def bisect_left(a, x, key):
    x = key(x)
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if key(a[mid]) < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


class Frog(Solution):
    def __init__(self, solution, prob):
        super().__init__()
        self._variables = solution._variables
        self.prob = prob
        self.obj_value = None

    def setObjValue(self):
        self.obj_value = self.prob.getObjValue(self)

    def getObjValue(self):
        if self.obj_value is None:
            self.setObjValue()
        return self.obj_value

    def random(self):
        super().random()
        self.obj_value = None

    def clip(self):
        super().clip()
        self.obj_value = None


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
    max_step : float (default 1e10)
      maximum size of one step
    n_memetic_iter : int (default 100)
      number of evolution in each memeplex
    n_memeplex : int (default 5)
      number of memeplex
    n_frog_per_memeplex : int (default 10)
      number of frog per memeplex
    inc_flogsize : float
      Multiplier for increasing population size before each restart

    Examples
    --------

    .. code-block:: python

        import flopt

        x = flopt.Variable("x", lowBound=-1, upBound=1, cat="Continuous")
        y = flopt.Variable("y", lowBound=-1, upBound=1, cat="Continuous")

        prob = flopt.Problem()
        prob += 2*x*x + x*y + y*y + x + y

        solver = flopt.Solver("SFLA")
        status, log = prob.solve(solver, msg=True, timelimit=1)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
    """

    name = "SFLA"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }

    def __init__(self):
        super().__init__()
        self.has_initialized = False
        self.frogs = None
        self.memeplexes = None
        # params
        self.n_trial = int(1e10)
        self.max_step = 1e10
        self.n_memetic_iter = 100
        self.n_memeplex = 5
        self.n_frog_per_memeplex = 4
        self.inc_flogsize = 2

    def reset(self):
        super().reset()
        self.has_initialized = False
        self.n_memeplex = 5
        self.n_frog_per_memeplex = 4
        self.inc_flogsize = 2

    def search(self, solution, *args):
        for i in range(self.n_trial):
            self._memetic_evolution(solution)

            # update best solution if needed
            self.registerSolution(
                self.frogs[0], self.frogs[0].getObjValue(), msg_tol=1e-8
            )

            if self.msg and i % 100 == 0:
                self.during_solver_message(" ")

            # callbacks
            self.callback(self.frogs)

            # check time limit
            self.raiseTimeoutIfNeeded()

        return SolverTerminateState.Normal

    def _memetic_evolution(self, solution):
        """
        memetic evolution
        This function is the key to this method.
        """
        M = self.n_memeplex
        N = self.n_frog_per_memeplex
        if self.frogs[-2].getObjValue() - self.frogs[0].getObjValue() < 1e-9:
            logger.debug(f"reset frogs: #frogs {N} --> {N*2}")
            new_frogs = [Frog(solution.clone(), self) for _ in range(M * N)]
            self.frogs += new_frogs
            for frog in self.frogs[1:]:
                frog.setRandom()
            self.frogs.sort(key=lambda frog: frog.getObjValue())
            self.n_frog_per_memeplex *= 2
            N = self.n_frog_per_memeplex

        self.memeplexes = [[self.frogs[i * M + j] for i in range(N)] for j in range(M)]

        for j in range(M):
            for k in range(self.n_memetic_iter):
                # make sub-sub memeplex
                sub_mmplx_ids = random.sample(range(N), N // 2)
                first, last = min(sub_mmplx_ids), max(sub_mmplx_ids)

                best_frog = self.memeplexes[j][first]
                worst_frog = self.memeplexes[j][last]

                # move frog which has the worst objective
                step = best_frog - worst_frog
                step *= random.random()
                if (norm := step.norm()) > self.max_step:
                    step *= self.max_step / norm
                new_frog = Frog(worst_frog + step, self)
                new_frog.clip()

                # if it does not improve (1)
                if new_frog.getObjValue() > worst_frog.getObjValue():
                    step = self.best_solution - worst_frog
                    step *= random.random()
                    if (norm := step.norm()) > self.max_step:
                        step *= self.max_step / norm
                    new_frog = Frog(worst_frog + step, self)
                    new_frog.clip()

                    # if it does not improve (2)
                    if new_frog.getObjValue() > worst_frog.getObjValue():
                        new_frog.setRandom()

                # replace the worst_frog to new frog and sort memeplex
                self.memeplexes[j].pop(last)
                lo = bisect_left(
                    self.memeplexes[j], new_frog, key=lambda frog: frog.getObjValue()
                )
                self.memeplexes[j].insert(lo, new_frog)
                if lo == 0:
                    self.registerSolution(
                        new_frog, obj_value=new_frog.getObjValue(), msg_tol=1e-8
                    )

                # check time limit
                self.raiseTimeoutIfNeeded()

        # sort entire memeplexes
        self.frogs = [frog for memeplex in self.memeplexes for frog in memeplex]
        self.frogs.sort(key=lambda frog: self.getObjValue(frog))

    def startProcess(self, solution):
        super().startProcess()
        if self.has_initialized:
            return
        self.start_build()

        M = self.n_memeplex
        N = self.n_frog_per_memeplex
        self.frogs = [Frog(solution.clone(), self) for _ in range(M * N)]
        for frog in self.frogs:
            frog.setRandom()
        self.frogs.sort(key=lambda frog: frog.getObjValue())
        self.registerSolution(self.frogs[0])

        self.end_build()
        self.has_initialized = True
