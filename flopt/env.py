import os
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


class Environment:

    variable_id = 0
    CREATE_VARIABLE_MODE = False

    def __init__(self):
        src_dir = os.path.dirname(__file__)
        self.src_dir = src_dir
        self.datasets_dir = f"{src_dir}/../datasets"
        self.performance_dir = f"{src_dir}/../performance"
        self.root_logger = getLogger()
        self.root_logger.setLevel(0)

    def setLogLevel(self, log_level):
        if isinstance(log_level, str):
            assert log_level in log_name, f"log level {log_level} is invalid."
            log_level = log_name[log_level]
        self.root_logger.setLevel(log_level)

    def __str__(self):
        s = f"src_dir: {self.src_dir}\n"
        s += f"datasets_dir: {self.datasets_dir}\n"
        s += f"performance_dir: {self.performance_dir}"
        return s


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
