from flopt.solvers.base import BaseSearch
from flopt.convert import QpStructure
from flopt.constants import VariableType, SolverTerminateState


class CvxoptQpSearch(BaseSearch):
    """API of CVXOPT.qp Solver

    Parameters
    ----------
    n_trial : int
        max iteration

    Examples
    --------

    .. code-block:: python

        from flopt import Variable, Problem

        x = Variable('x', lowBound=-1, upBound=1, cat='Continuous')
        y = Variable('y', lowBound=-1, upBound=1, cat='Continuous')

        prob = Problem()
        prob += 2*x*x + x*y + y*y + x + y
        prob += x >= 0
        prob += y >= 0
        prob += x + y == 1

        print(prob.show())
        >>> Name: None
        >>>   Type         : Problem
        >>>   sense        : minimize
        >>>   objective    : 2*(x*x)+(x*y)+(y*y)+x+y
        >>>   #constraints : 3
        >>>   #variables   : 2 (Continuous 2)
        >>>
        >>>   C 0, name None, x >= 0
        >>>   C 1, name None, y >= 0
        >>>   C 2, name None, x+y-1 == 0


    .. code-block:: python

        from flopt import Solver, Value

        solver = Solver('CvxoptQpSearch')
        status, log = prob.solve(solver, msg=True)
        print()
        print('obj =', Value(prob.obj))
        print('x =', Value(x))
        print('y =', Value(y))
        >>> obj = 1.8750000000000002
        >>> x = 0.2500000152449024
        >>> y = 0.7499999847550975

    See Also
    --------
    `https://cvxopt.org/userguide/coneprog.html#quadratic-programming`
    """
    def __init__(self):
        super().__init__()
        self.name = 'CvxoptQpSearch'
        self.n_trial = None
        self.can_solve_problems = ['lp', 'qp']


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
        obj_is_quadratic    = prob.obj.isQuadratic()
        consts_are_lp       = all( const.expression.isLinear() for const in prob.constraints )
        var_are_continuous  = all( var.type() == VariableType.Continuous for var in prob.getVariables() )
        return obj_is_quadratic and consts_are_lp and var_are_continuous


    def search(self):
        qp = QpStructure.fromFlopt(self.prob).boundsToNeq()
        if qp.isLp():
            sol = self.search_lp(qp.toLp())
        else:
            sol = self.search_qp(qp)

        for var, value in zip(qp.x, sol['x']):
            self.solution.setValue(var.name, value)

        # check whether update or not
        obj_value = self.getObjValue(self.solution)
        if obj_value < self.best_obj_value:
            self.updateSolution(self.solution, obj_value)
            self.recordLog()

        return SolverTerminateState.Normal



    def search_qp(self, qp):
        from cvxopt import matrix, solvers

        qp = qp.boundsToNeq()
        Q = matrix(qp.Q)
        c = matrix(qp.c)
        G = matrix(qp.G) if qp.G is not None else None
        h = matrix(qp.h) if qp.h is not None else None
        A = matrix(qp.A) if qp.A is not None else None
        b = matrix(qp.b) if qp.b is not None else None

        # solve
        solvers.options['show_progress'] = self.msg
        if self.n_trial is not None:
            solvers.options['maxiters'] = self.n_trial
        elif 'maxiters' in solvers.options:
            del solvers.options['maxiters']
        sol = solvers.qp(Q, c, G, h, A, b)
        return sol


    def search_lp(self, lp):
        from cvxopt import matrix, solvers

        c = matrix(lp.c)
        G = matrix(lp.G) if lp.G is not None else None
        h = matrix(lp.h) if lp.h is not None else None
        A = matrix(lp.A) if lp.A is not None else None
        b = matrix(lp.b) if lp.b is not None else None

        # solve
        solvers.options['show_progress'] = self.msg
        if self.n_trial is not None:
            solvers.options['maxiters'] = self.n_trial
        elif 'maxiters' in solvers.options:
            del solvers.options['maxiters']
        sol = solvers.lp(c, G, h, A, b)
        return sol


    def startProcess(self):
        """process of beginning of search
        """
        if all(const.feasible(self.best_solution) for const in self.prob.constraints):
            self.best_obj_value = self.getObjValue(self.best_solution)
        else:
            self.best_obj_value = float('inf')
        self.recordLog()

    def closeProcess(self):
        """process of ending of search
        """
        self.recordLog()
