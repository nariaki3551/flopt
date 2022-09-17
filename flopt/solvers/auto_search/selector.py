import os
import pickle

from flopt import Solver
from flopt.constants import VariableType, ExpressionType
import flopt.env

# ---------------------------------------------
#   Optimization Class Definitions
# ---------------------------------------------

# MIP
mip = {
    "Variable": VariableType.Number,
    "Objective": ExpressionType.Linear,
    "Constraint": ExpressionType.Linear,
}

# ising
ising = {
    "Variable": VariableType.Binary,
    "Objective": ExpressionType.Quadratic,
    "Constraint": ExpressionType.Non,
}

# QP
qp = {
    "Variable": VariableType.Continuous,
    "Objective": ExpressionType.Quadratic,
    "Constraint": ExpressionType.Linear,
}

# Permutation
permutation = {
    "Variable": VariableType.Permutation,
    "Objective": ExpressionType.Any,
    "Constraint": ExpressionType.Any,
}

# nonlinear without Constraint
nonlinear = {
    "Variable": VariableType.Continuous,
    "Objective": ExpressionType.BlackBox,
    "Constraint": ExpressionType.Non,
}

# nonlinear-mip without Constraint
nonlinear_mip = {
    "Variable": VariableType.Number,
    "Objective": ExpressionType.BlackBox,
    "Constraint": ExpressionType.Non,
}


# ---------------------------------------------
#   Selectors
# ---------------------------------------------


class ModelNotFound(Exception):
    pass


class Selector:
    def __call__(self, prob, solver):
        raise NotImplementedError


class SklearnSelector(Selector):
    def __init__(self):
        if not os.path.exists(self.model_path):
            raise ModelNotFound(f"{self.model_path}: trained model file is not found")
        with open(self.model_path, "rb") as bf:
            self.model = pickle.load(bf)

    def __call__(self, prob, solver):
        feature = [solver.timelimit, len(prob.getVariables())]
        return self.model.predict([feature])[0]


class IsingSelector(SklearnSelector):
    model_path = os.path.join(flopt.env.models_dir, "ising.model.pickle")


class NonlinearSelector(SklearnSelector):
    model_path = os.path.join(flopt.env.models_dir, "func_continuous.pickle")


class NonlinearMipSelector(SklearnSelector):
    model_path = os.path.join(flopt.env.models_dir, "func_mip.pickle")


class MipSelector(Selector):
    def __call__(self, prob, solver):
        return "ScipyMilpSearch"


class QpSelector(Selector):
    def __call__(self, prob, solver):
        return "CvxoptQpSearch"


class PermutationSelector(Selector):
    def __call__(self, prob, solver):
        return "2-Opt"


class BaseSelector(Selector):
    algos = [
        "2-Opt",
        "ScipyMilpSearch",
        "PulpSearch",
        "CvxoptQpSearch",
        "ScipySearch",
        "SFLA",
        "RandomSearch",
        "HyperoptTPESearch",
        "OptunaTPESearch",
        "OptunaCmaEsSearch",
    ]

    def __call__(self, prob, solver):
        for algo in self.algos:
            if Solver(algo=algo).available(prob):
                return algo
