import re

import pulp

import flopt.solvers
import flopt.convert
from flopt.constants import VariableType, ExpressionType
import flopt.env
from flopt.env import setup_logger

from .base_dataset import BaseDataset, BaseInstance

logger = setup_logger(__name__)

# instance problems
mip_storage = f"{flopt.env.DATASETS_DIR}/mipLib"


class MipDataset(BaseDataset):
    """MIP Benchmark Instance Set

    Parameters
    ----------
    instance_names : list
      instance name list
    """

    name = "mip"
    instance_names = [
        "markshare2",
        "50v-10",
        "enlight_hard",
        "gen-ip054",
        "neos-3046615-murg",
        "gen-ip002",
        "neos-3754480-nidda",
    ]

    def __init__(self):
        self.sol_data = dict()
        sol_file = "miplib2017-v23.solu"
        pattern = re.compile("=(?P<status>.*)=\s+(?P<name>.*)\s+(?P<best_value>.*)")
        for line in open(f"{mip_storage}/{sol_file}", "r"):
            line = line.strip()
            m = pattern.match(line)
            if m is not None:
                d = m.groupdict()
                if d["status"] in {"unkn", "inf", "unbd"}:
                    continue
                name = d["name"].strip()
                best_value = float(d["best_value"].strip())
                status = d["status"].strip()
                self.sol_data[name] = {"best_value": best_value, "status": status}

    def createInstance(self, instance_name):
        """
        Returns
        -------
        MipInstance
        """
        mps_file = f"{mip_storage}/{instance_name}.mps"
        pulp_var, pulp_prob = pulp.LpProblem.fromMPS(mps_file)
        best_value = self.sol_data[instance_name]["best_value"]
        prob = flopt.convert.pulp_to_flopt(pulp_prob)
        return MipInstance(instance_name, prob, best_value)


class MipInstance(BaseInstance):
    """MIP Instance

    Parameters
    ----------
    name : str
      problem name
    prob : Problem
    best_value : optimal or best value of problem
    """

    def __init__(self, name, prob, best_value):
        self.name = name
        self.prob = prob
        self.best_value = best_value

    def getBestBound(self):
        """return the optimal or best value of objective function"""
        return self.best_value

    def createProblem(self, solver):
        """
        Create problem according to solver

        Parameters
        ----------
        solver : Solver
          solver

        Returns
        -------
        (bool, Problem)
          if solver can be solve this instance return
          (true, prob formulated according to solver)
        """
        problem_type = dict(
            Variable=VariableType.Number,
            Objective=ExpressionType.Linear,
            Constraint=ExpressionType.Linear,
        )
        available_solvers = flopt.solvers.allAvailableSolversProblemType(problem_type)
        if solver.name in available_solvers:
            return solver.available(self.prob), self.prob
        else:
            logger.info(f"{solver.name} cannot solve this instance")
            return False, None

    def __str__(self):
        s = f"NAME: {self.name}"
        return s
