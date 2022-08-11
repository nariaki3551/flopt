from .log_visualizer import LogVisualizer
from .performance import compute, performance
from .base_dataset import BaseDataset
from .custom_dataset import CustomDataset
from .tsp_dataset import TSPDataset
from .func_dataset import FuncDataset
from .mip_dataset import MipDataset

datasets = {
    "tsp": TSPDataset(),
    "func": FuncDataset(),
    "mip": MipDataset(),
}


def Dataset_list():
    return list(datasets)
