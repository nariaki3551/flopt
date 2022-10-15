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
      log_visualizer.plot()
    """

    def __init__(self, name="CustomDataset", probs=[]):
        if not isinstance(probs, list):
            probs = [probs]
        assert all(prob.name is not None for prob in probs), "problem must be named"
        self.name = name
        self.instance_names = [prob.name for prob in probs]
        self.instance_dict = {prob.name: prob for prob in probs}

    def createInstance(self, instance_name):
        prob = self.instance_dict[instance_name]
        if isinstance(prob, CustomInstance):
            return prob
        else:
            return CustomInstance(prob)

    def addProblem(self, prob):
        self.instance_names.append(prob.name)
        self.instance_dict[prob.name] = prob

    def __iadd__(self, prob):
        assert prob.name is not None, "problem must be named"
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
        assert prob.sense in {"Minimize", "minimize"}
        self.name = prob.name
        self.prob = prob
        self.var_values = {var.name: var.value() for var in prob.getVariables()}
        self.best_bound = None

    def createProblem(self, solver):
        if solver.available(self.prob):
            for variable in self.prob.getVariables():
                variable.setValue(self.var_values[variable.name])
            return True, self.prob
        else:
            return False, None

    def getBestBound(self):
        """return the optimal value of objective function"""
        return self.prob.best_bound

    def setBestBound(self, best_bound):
        self.prob.setBestBound(best_bound)
