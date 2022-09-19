from .log_visualizer import LogVisualizer
from .performance import compute, performance
from .base_dataset import BaseDataset
from .custom_dataset import CustomDataset, CustomInstance

dataset_list = [
    "tsp",
    "func",
    "mip",
]


def get_dataset(name):
    if name == "tsp":
        from .tsp_dataset import TSPDataset

        return TSPDataset()
    elif name == "func":
        from .func_dataset import FuncDataset

        return FuncDataset()
    elif name == "mip":
        from .mip_dataset import MipDataset

        return MipDataset()
    else:
        assert f"{name} is not available, choices from {Dataset_list()}"


def Dataset_list():
    return dataset_list
