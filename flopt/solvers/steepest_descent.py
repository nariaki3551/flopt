from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, ExpressionType, SolverTerminateState


class SteepestDescentSearch(BaseSearch):
    """Steepest Descent Search

    Update search points as x_{n+1} = x_n - alpha d,
    where d = -grad(x_n) and alpha is a step size calculated by Armijo's method.

    Examples
    --------

    .. code-block:: python

        import flopt

        x = flopt.Variable("x", lowBound=-1, upBound=1, cat="Continuous")
        y = flopt.Variable("y", lowBound=-1, upBound=1, cat="Continuous")

        prob = flopt.Problem()
        prob += 2*x*x + x*y + y*y + x + y

        solver = flopt.Solver("SteepestDescentSearch")
        status, log = prob.solve(solver, msg=True, timelimit=1)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
    """

    name = "SteepestDescentSearch"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Polynomial,
        "Constraint": ExpressionType.Non,
    }

    def __init__(self):
        super().__init__()
        self.n_trial = 1e100
        self.xi = 0.9
        self.tau = 0.9

    def search(self, solution, obj, *args):
        assert 0 < self.xi < 1 and 0 < self.tau < 1

        # get variable array
        x = solution.getVariables()

        # get jacobian (gradient) function
        jac = obj.jac(x)

        for _ in range(int(self.n_trial)):
            # 1. obtain gradient
            # 2. define search direction
            # 3. linear search for step size
            # 4. update solution
            grad = jac.value(solution)
            d = -grad
            alpha = self.search_step_size(solution, obj, grad, d)
            solution += alpha * d

            # register solution
            self.registerSolution(solution, msg_tol=1e-6)

            # execute callbacks
            self.callback([solution])

            # check time limit
            self.raiseTimeoutIfNeeded()

        return SolverTerminateState.Normal

    def search_step_size(self, solution, obj, grad, d):
        """Armijo"""
        alpha = 1.0
        dot = grad.dot(d)

        obj_value = obj(solution)
        while obj.value(solution + alpha * d) > obj_value + self.xi * alpha * dot:
            alpha *= self.tau
        return alpha
