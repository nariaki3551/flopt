from copy import deepcopy
from .base_dataset import BaseDataset, BaseInstance

class CustomDataset(BaseDataset):
    """
    Creaet Dataset

    Parameters
    ----------
    name : str
      dataset name
    probs : list of Problem
      problems 

    Examples
    --------

    We have a problem with the compatibility of the solvers.

    .. code-block:: python

      import flopt
      from flopt import Variable, Problem, Solver
      from flopt.performance import CustomDataset

      a = Variable('a', lowBound=2, upBound=4, cat='Continuous')
      b = Variable('b', lowBound=2, upBound=4, cat='Continuous')

      prob = Problem()
      prob += a + b


    We calculates the performance of (solver, problem) by using `CusomDataset`


    .. code-block:: python

      cd = CustomDataset(name='user')
      cd += prob  # add problem

    Then, we run to calculate the performance.

    .. code-block:: python

      flopt.performance.compute(cd, timelimit=2, msg=True)

    After that, we can see the performace each solver.

    .. code-block:: python

      flopt.performance.performance(cd)


    We can select the solvers to calculate the performance.

    .. code-block:: python

      rs_solver = Solver('RandomSearch')
      tpe_solver = Solver('OptunaTPESearch')
      cma_solver = Solver('OptunaCmaEsSearch')
      htpe_solver = Solver('HyperoptTPESearch')

      logs = flopt.performance.compute(
          cd,  # dataset or dataset list 
          [rs_solver, tpe_solver, cma_solver, htpe_solver],  # solver list
          timelimit=2,
          msg=True
      )

      # visualize he performance
      log_visualizer = flopt.performance.LogVisualizer(logs)
      lov_visualizer.plot()
    """
    def __init__(self, name='CustomDataset', probs=[]):
        if not isinstance(probs, list):
            probs = [probs]
        self.name = name
        self.instance_names = [prob.name for prob in probs]
        self.instance_dict = {prob.name: prob for prob in probs}

    def createInstance(self, instance_name):
        prob = self.instance_dict[instance_name]
        return CustomInstance(deepcopy(prob))

    def addProblem(self, prob):
        self.instance_names.append(prob.name)
        self.instance_dict[prob.name] = prob

    def __iadd__(self, prob):
        self.addProblem(prob)
        return self


class CustomInstance(BaseInstance):
    """
    Custom Instance

    Parameters
    ----------
    name : str
      problem name
    prob : Problem
      problem
    prob_type : list of str
      type oof problem
    """
    def __init__(self, prob):
        self.name = prob.name
        self.prob = prob
        self.prob_type = prob.prob_type

    def createProblem(self, solver):
        if set(self.prob_type) & set(solver.can_solve_problems):
            return True, deepcopy(self.prob)
        else:
            return False, None
