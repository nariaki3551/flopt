import os
import configparser
from logging import getLogger, StreamHandler

import colorlog

log_name = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
}


class create_variable_mode:
    def __enter__(self):
        Environment.CREATE_VARIABLE_MODE = True

    def __exit__(self, exc_type, exc_value, traceback):
        Environment.CREATE_VARIABLE_MODE = False


def is_create_variable_mode():
    return Environment.CREATE_VARIABLE_MODE


def get_variable_id():
    var_id = Environment.variable_id
    Environment.variable_id += 1
    return var_id


def get_variable_lower_bound(to_int=False):
    if to_int:
        return int(Environment.VARIABLE_LOWER_BOUND)
    else:
        return Environment.VARIABLE_LOWER_BOUND


def get_variable_upper_bound(to_int=False):
    if to_int:
        return int(Environment.VARIABLE_UPPER_BOUND)
    else:
        return Environment.VARIABLE_UPPER_BOUND


class Environment:

    variable_id = 0
    CREATE_VARIABLE_MODE = False
    VARIABLE_LOWER_BOUND = None
    VARIABLE_UPPER_BOUND = None
    TRAINED_MODELS_CONFIG = None

    SOURCE_DIR = os.path.dirname(__file__)
    DATASETS_DIR = os.path.join(SOURCE_DIR, "..", "datasets")
    PERFORMANCE_DIR = os.path.join(SOURCE_DIR, "..", "performance")
    MODELS_DIR = os.path.join(SOURCE_DIR, "tuning")

    root_logger = getLogger()

    def __init__(self):
        # logger
        self.root_logger.setLevel(0)

        # config
        config = configparser.ConfigParser()
        config.read(os.path.join(self.SOURCE_DIR, "flopt.config"))

        Environment.VARIABLE_LOWER_BOUND = float(
            config["DEFAULT"]["VARIABLE_LOWER_BOUND"]
        )
        Environment.VARIABLE_UPPER_BOUND = float(
            config["DEFAULT"]["VARIABLE_UPPER_BOUND"]
        )

        # download trained model
        Environment.TRAINED_MODELS_CONFIG = config["TRAINED_MODELS"]

    def setLogLevel(self, log_level):
        if isinstance(log_level, str):
            assert log_level in log_name, f"log level {log_level} is invalid."
            log_level = log_name[log_level]
        self.root_logger.setLevel(log_level)

    def getConfig(self, name, section="DEFAULT"):
        return self.config[section][name]


def setup_logger(name):
    """Return a logger with a ColoredFormatter."""
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(filename)s:%(funcName)s:%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red",
        },
    )

    logger = getLogger(name)
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
