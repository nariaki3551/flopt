from flopt.solvers.base import BaseSearch
from flopt.convert import QpStructure
from flopt.constants import VariableType, SolverTerminateState


class CvxoptQpSearch(BaseSearch):
    """API of CVXOPT.qp Solver

    """
    def __init__(self):
        super().__init__()
        self.name = 'CvxoptQpSearch'
        self.n_trial = None


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
        obj_value = self.obj.value(self.solution)
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
        if all(const.feasible(self.best_solution) for const in self.constraints):
            self.best_obj_value = self.obj.value(self.best_solution)
        else:
            self.best_obj_value = float('inf')
        self.recordLog()

    def closeProcess(self):
        """process of ending of search
        """
        self.recordLog()
