import os
from logging import getLogger, StreamHandler

from colorlog import ColoredFormatter

log_name = {
    'CRITICAL': 50,
    'ERROR'   : 40,
    'WARNING' : 30,
    'INFO'    : 20,
    'DEBUG'   : 10,
}

class Environment:
    def __init__(self):
        src_dir = os.path.dirname(__file__)
        self.src_dir = src_dir
        self.datasets_dir = f'{src_dir}/../datasets'
        self.performance_dir = f'{src_dir}/../performance'
        self.root_logger = getLogger()
        self.root_logger.setLevel(0)


    def setLogLevel(self, log_level):
        if isinstance(log_level, str):
            assert log_level in log_name, \
                f'log level {log_level} is invalid.'
            log_level = log_name[log_level]
        self.root_logger.setLevel(log_level)


    def __str__(self):
        s  = f'src_dir: {self.src_dir}\n'
        s += f'datasets_dir: {self.datasets_dir}\n'
        s += f'performance_dir: {self.performance_dir}'
        return s


def setup_logger(name):
    """Return a logger with a ColoredFormatter."""
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s:%(filename)s:%(funcName)s:%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red',
        }
    )

    logger = getLogger(name)
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
