import os

import dill
import pooch

from flopt import Solver
from flopt.constants import VariableType, ExpressionType
import flopt.env
from flopt.env import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------
#   File Paths for Trained models
# ---------------------------------------------
MODELS_CONFIG = flopt.env.TRAINED_MODELS_CONFIG
if MODELS_CONFIG.getboolean("LOCAL"):
    # trained models are used from local
    MODELS_DIR = flopt.env.MODELS_DIR
    nonlinear_model_path = os.path.join(MODELS_DIR, MODELS_CONFIG["NONLINEAR_FILE"])
    nonlinear_mip_model_path = os.path.join(
        MODELS_DIR, MODELS_CONFIG["NONLINEAR_MIP_FILE"]
    )
    ising_model_path = os.path.join(MODELS_DIR, MODELS_CONFIG["ISING_FILE"])
else:
    # trained models are downloaded
    models_pooch = pooch.create(
        path=pooch.os_cache(MODELS_CONFIG["CACHE"]),
        base_url=MODELS_CONFIG["URL"],
        registry={
            MODELS_CONFIG["NONLINEAR_FILE"]: MODELS_CONFIG["NONLINEAR_SHA256"],
            MODELS_CONFIG["NONLINEAR_MIP_FILE"]: MODELS_CONFIG["NONLINEAR_MIP_SHA256"],
            MODELS_CONFIG["ISING_FILE"]: MODELS_CONFIG["ISING_SHA256"],
        },
    )

    nonlinear_model_path = models_pooch.fetch(
        MODELS_CONFIG["NONLINEAR_FILE"], processor=pooch.Untar()
    )[0]
    logger.info(f"download trained model into {nonlinear_model_path}")
    nonlinear_mip_model_path = models_pooch.fetch(
        MODELS_CONFIG["NONLINEAR_MIP_FILE"], processor=pooch.Untar()
    )[0]
    logger.info(f"download trained model into {nonlinear_mip_model_path}")
    ising_model_path = models_pooch.fetch(
        MODELS_CONFIG["ISING_FILE"], processor=pooch.Untar()
    )[0]
    logger.info(f"download trained model into {ising_model_path}")


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

# blackbox
blackbox = {
    "Variable": VariableType.Continuous,
    "Objective": ExpressionType.BlackBox,
    "Constraint": ExpressionType.Non,
}

# blackbox-mip with integer variables
blackbox_mip = {
    "Variable": VariableType.Number,
    "Objective": ExpressionType.BlackBox,
    "Constraint": ExpressionType.Non,
}

# nonlinear
nonlinear = {
    "Variable": VariableType.Continuous,
    "Objective": ExpressionType.Any,
    "Constraint": ExpressionType.Non,
}

# nonlinear with integer variables
nonlinear_mip = {
    "Variable": VariableType.Continuous,
    "Objective": ExpressionType.Any,
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
            self.model = dill.load(bf)
        logger.debug(f"load selector model from {self.model_path}")

    def __call__(self, prob, solver):
        feature = self.model.features(prob, solver)
        return self.model.output([feature])[0]


class IsingSelector(SklearnSelector):
    model_path = ising_model_path


class BlackBoxSelector(SklearnSelector):
    model_path = nonlinear_model_path


class BlackBoxMipSelector(SklearnSelector):
    model_path = nonlinear_mip_model_path


class NonlinearSelector(SklearnSelector):
    model_path = nonlinear_model_path


class NonlinearMipSelector(SklearnSelector):
    model_path = nonlinear_mip_model_path


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
