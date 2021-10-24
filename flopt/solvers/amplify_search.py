import numpy as np

from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, SolverTerminateState


class AmplifySearch(BaseSearch):
    """API of Amplify Solver (https://amplify.fixstars.com/en/docs/index.html)

    Parameters
    ----------
    timelimit : float or int
        time limit
    token : str
        user token

    Examples
    --------

    AmplifySearch can solve the problem whose variables are Spin

    .. code-block:: python

        from flopt import Variable, Problem

        x = Variable('x', cat='Spin')
        y = Variable('y', cat='Spin')

        prob = Problem()
        prob += 1 - x * y - x
        prob += x + y >= 0

        print(prob.show())
        >>> Name: None
        >>>   Type         : Problem
        >>>   sense        : minimize
        >>>   objective    : 1-(x*y)-x
        >>>   #constraints : 1
        >>>   #variables   : 2 (Spin 2)
        >>>
        >>>   C 0, name None, x+y >= 0

    .. code-block:: python

        from flopt import Solver

        solver = Solver('AmplifySearch')
        solver.setParams(token="xxx")  # your token
        prob.solve(solver, msg=True)

        print()
        print('obj =', Value(prob.obj))
        print('x =', Value(x))
        print('y =', Value(y))
        >>> obj = -1
        >>> x = 1
        >>> y = 1

    In the case, the problem includes the binary variables,
    you should convert them to spin variables.

    .. code-block:: python

        from flopt import Variable, Problem

        x = Variable('x', cat='Binary')
        y = Variable('y', cat='Binary')

        prob = Problem()
        prob += (1 - x * y - x).toSpin()
        prob += (x + y >= 0).toSpin()

        print(prob.show())
        >>> Name: None
        >>>   Type         : Problem
        >>>   sense        : minimize
        >>>   objective    : -0.25*(x_s*y_s)-(0.75*x_s)-(0.25*y_s)+0.25
        >>>   #constraints : 1
        >>>   #variables   : 2 (Spin 2)
        >>>
        >>>   C 0, name None, 0.5*x_s+(0.5*y_s)+1.0 >= 0
    """
    def __init__(self):
        super().__init__()
        self.name = 'AmplifySearch'
        self.timelimit = 1
        self.token = None
        self.can_solve_problems = ['ising']


    def available(self, prob):
        """
        Parameters
        ----------
        prob : Problem

        Returns
        -------
        bool
            return true if it can solve the problem else false
        """
        all_spin = all( var.type() == VariableType.Spin for var in prob.getVariables() )
        ising_obj = prob.obj.isIsing()
        ising_consts = all( const.expression.isIsing() for const in prob.constraints )
        return all_spin and ising_obj and ising_consts


    def search(self):
        from amplify import IsingPoly, gen_symbols, Solver, decode_solution
        from amplify.constraint import equal_to, greater_equal, less_equal
        from amplify.client import FixstarsClient

        assert self.token is not None, f'token is None, set token as .solve(..., token="xxx")'

        x = self.prob.getVariables()
        s = np.array(gen_symbols(IsingPoly, len(x)), dtype=object)

        # objective function
        ising = self.prob.obj.toIsing()
        f = - s.T.dot(ising.J).dot(s) - ising.h.T.dot(s) + ising.C

        # constraints
        for const in self.prob.constraints:
            ising = const.expression.toIsing()
            g = s.T.dot(ising.J).dot(s) - ising.h.T.dot(s) + ising.C
            if const.type == 'le':
                f += less_equal(g, 0)
            elif const.type == 'ge':
                f += greater_equal(g, 0)
            else:
                f += equal_to(g, 0)

        # solve
        client = FixstarsClient()  # Fixstars Optigan
        client.parameters.timeout = int(1000.0 * self.timelimit)
        client.token = self.token

        result = Solver(client).solve(f)

        var_dict = {var.name: var for var in self.solution}
        for amplify_solution in list(result)[::-1]:
            values = decode_solution(s, amplify_solution.values)
            for var, value in zip(x, values):
                self.solution.setValue(var.name, value.constant())

            # check whether update or not
            obj_value = self.getObjValue(self.solution)
            if obj_value < self.best_obj_value:
                self.updateSolution(self.solution, obj_value)
                self.recordLog()
                if self.msg:
                    self.during_solver_message('*')

        return SolverTerminateState.Normal


