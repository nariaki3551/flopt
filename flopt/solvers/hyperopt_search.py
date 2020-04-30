from time import time
import hyperopt
from hyperopt import hp

from .base import BaseSearch
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message
)

class HyperoptTPESearch(BaseSearch):
    """
    TPE Search using Hyperopt (https://hyperopt.github.io/hyperopt/)

    Parameters
    ----------
    n_trial : int
      number of trials
    show_progressbar : bool
      whether display a progress bar of search
    """
    def __init__(self):
        super().__init__()
        self.name = 'HyperoptTPESearch'
        self.n_trial = 1e100
        self.show_progressbar = False
        self.can_solve_problems = ['blackbox']

    def search(self):
        self.startProcess()
        status = 0

        # make the search space
        space = self.gen_space()
        self.var_dict = {var.name: var for var in self.solution}

        # search
        try:
            hyperopt.fmin(
                self.objective, space=space,
                algo=hyperopt.tpe.suggest,
                max_evals=self.n_trial,
                show_progressbar=self.show_progressbar,
            )
        except TimeoutError:
            status = 1  # timelimit termination

        self.closeProcess()
        return status


    def gen_space(self):
        """
        generate search space
        """
        space = dict()
        for var in self.solution:
            name = var.name
            if var.getType() in {name, 'VarInteger' , 'VarBinary'}:
                var_space = hp.quniform(name, var.lowBound, var.upBound, 1)
            elif var.getType() == 'VarContinuous':
                var_space = hp.uniform(name, var.lowBound, var.upBound)
            space[var.name] = var_space
        return space


    def objective(self, var_value_dict):
        # check timelimit
        if time() > self.start_time + self.timelimit:
            raise TimeoutError

        # set value into self.solution
        self.trial_ix += 1
        for name, value in var_value_dict.items():
            self.var_dict[name].setValue(value)
        obj_value = self.obj.value(self.solution)

        # check whether update or not
        if obj_value < self.best_obj_value:
            self.updateSolution(self.solution, obj_value)
            self.recordLog()
            if self.msg:
                during_solver_message('*', obj_value, time()-self.start_time, self.trial_ix)
        
        # callbacks
        for callback in self.callbacks:
            callback([self.solution], self.best_solution, self.best_obj_value)

        return {'loss': obj_value, 'status': hyperopt.STATUS_OK}


    def startProcess(self):
        self.best_obj_value = self.obj.value(self.best_solution)
        self.recordLog()

        if self.msg:
            during_solver_message_header()
            during_solver_message('S', self.best_obj_value,
                time()-self.start_time, self.trial_ix)


    def closeProcess(self):
        self.recordLog()
