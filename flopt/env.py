import os
class Environment:
    def __init__(self):
        src_dir = os.path.dirname(__file__)
        self.src_dir = src_dir
        self.datasets_dir = f'{src_dir}/../datasets'
        self.performance_dir = f'{src_dir}/../performance'

    def __str__(self):
        s  = f'src_dir: {self.src_dir}\n'
        s += f'datasets_dir: {self.datasets_dir}\n'
        s += f'performance_dir: {self.performance_dir}'
        return s
