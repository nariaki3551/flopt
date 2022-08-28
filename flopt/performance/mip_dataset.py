import re

import pulp

import flopt
import flopt.convert
from flopt import env as flopt_env
from .base_dataset import BaseDataset, BaseInstance
from flopt.env import setup_logger


logger = setup_logger(__name__)

# instance problems
mip_storage = f"{flopt_env.datasets_dir}/mipLib"


class MipDataset(BaseDataset):
    """MIP Benchmark Instance Set

    Parameters
    ----------
    instance_names : list
      instance name list
    """

    def __init__(self):
        self.name = "mip"
        self.instance_names = [
            "50v-10",
            "enlight_hard",
            "gen-ip054",
            "neos-3046615-murg",
            "gen-ip002",
            "neos-3754480-nidda",
        ]

        self.sol_data = dict()
        sol_file = "miplib2017-v23.solu"
        pattern = re.compile("=(?P<status>.*)=\s+(?P<name>.*)\s+(?P<value>.*)")
        for line in open(f"{mip_storage}/{sol_file}", "r"):
            line = line.strip()
            m = pattern.match(line)
            if m is not None:
                d = m.groupdict()
                if d["status"] in {"unkn", "inf", "unbd"}:
                    continue
                name = d["name"].strip()
                value = float(d["value"].strip())
                status = d["status"].strip()
                self.sol_data[name] = {"value": value, "status": status}

    def createInstance(self, instance_name):
        """
        Returns
        -------
        MipInstance
        """
        mps_file = f"{mip_storage}/{instance_name}.mps"
        pulp_var, pulp_prob = pulp.LpProblem.fromMPS(mps_file)
        value = self.sol_data[instance_name]["value"]
        prob = flopt.convert.pulp_to_flopt(pulp_prob)
        return MipInstance(instance_name, prob, value)


class MipInstance(BaseInstance):
    """MIP Instance

    Parameters
    ----------
    name : str
      problem name
    prob : Problem
    value : optimal or best value of problem
    """

    def __init__(self, name, prob, value):
        self.name = name
        self.prob = prob
        self.value = value

    def getBestValue(self):
        """return the optimal value of objective function"""
        return self.value

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
        if solver.name == "PulpSearch":
            return solver.available(self.prob), self.prob
        elif solver.name == "ScipyLpSearch":
            return solver.available(self.prob), self.prob
        elif solver.name == "ScipyMilpSearch":
            return solver.available(self.prob), self.prob
        else:
            logger.info("this instance only can be MIP formulation")
            return False, None

    def __str__(self):
        s = f"NAME: {self.name}"
        return s
