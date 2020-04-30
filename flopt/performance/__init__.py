from .log_visualizer  import LogVisualizer
from .performance import compute, performance
from .base_dataset import BaseDataset
from .custom_dataset import CustomDataset
from .tsp_dataset  import TSPDataset
from .func_dataset import FuncDataset

datasets = {
    'tsp': TSPDataset(),
    'func': FuncDataset(),
}

def Dataset_list():
	return list(datasets)
