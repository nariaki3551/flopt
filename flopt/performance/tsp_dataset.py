import math
from itertools import combinations, product

import numpy as np
from tqdm import tqdm

from flopt import Variable, Const, CustomExpression, Problem, Sum
from flopt import env as flopt_env
from .base_dataset import BaseDataset, BaseInstance
from flopt.env import setup_logger


logger = setup_logger(__name__)

# instance problems
tsp_storage = f'{flopt_env.datasets_dir}/tspLib/tsp'


class TSPDataset(BaseDataset):
    """TSP Benchmark Instance Set

    Parameters
    ----------
    instance_names : list
      instance name list
    """
    def __init__(self):
        self.name = 'tsp'
        self.instance_names = [
            'test8',  'pa561',
            'gr24',  'pr1002',
            'fri26', 'fl3795',
            'gr120', 'rl5915'
        ]


    def createInstance(self, instance_name):
        """
        Returns
        -------
        TSPInstance
        """

        tspfile = f'{tsp_storage}/{instance_name}.tsp'
        return read_instance_file(tspfile)



def read_instance_file(tspfile):
    name, dimension, D, C = None, None, None, None

    with open(tspfile, 'r') as f:
        for line in f:
            line = line.strip()
            line = line.replace(':', '')
            if 'NAME' in line:
                name = line.split()[1]
            if 'TYPE' in line:
                pType = line.split()[1]
            if 'DIMENSION' in line:
                dimension = int(line.split()[1])
            if 'EDGE_WEIGHT_TYPE' in line:
                edge_weight_type = line.split()[1]
            if 'EDGE_WEIGHT_FORMAT' in line:
                edge_weight_format = line.split()[1]
            if 'EDGE_WEIGHT_SECTION' in line:
                D = read_edge_weight(
                    f,
                    edge_weight_format,
                    dimension
                )
            if 'NODE_COORD_SECTION' in line:
                N, D = read_node_coord(
                    f,
                    edge_weight_type,
                    dimension,
                    D
                )

    tsp_instance = TSPInstance(name, dimension, D, C)
    return tsp_instance



def read_edge_weight(f, edge_weight_format, dim):
    D = np.zeros((dim, dim))
    if edge_weight_format == 'LOWER_DIAG_ROW':
        i, j = 0, 0
        while i < dim:
            for elm in map(float, f.readline().split()):
                D[i, j] = D[j, i] = elm
                (i, j) = (i, j+1) if j < i else (i+1, 0)
        return D
    if edge_weight_format == 'FULL_MATRIX':
        i, j = 0, 0
        while i < dim:
            for elm in map(float, f.readline().split()):
                D[i, j] = D[j, i] = elm
                j = j + 1
            i, j = i+1, 0
        return D


def read_node_coord(f, edge_weight_type, dim, D):
    N = dict()
    for _ in range(dim):
        line = f.readline()
        node_ix, x, y = line.split()
        node_ix, x, y = int(node_ix), float(x), float(y)
        N[node_ix] = (x, y)
    if edge_weight_type == 'EUC_2D':
        D = np.zeros((dim, dim))
        for i in range(dim):
            for j in range(dim):
                ii, jj = N[i+1], N[j+1]
                dist = math.sqrt((ii[0]-jj[0])**2+(ii[1]-jj[1])**2)
                D[i, j] = D[j, i] = dist
    return N, D



class TSPInstance(BaseInstance):
    """TSP Instance

    Parameters
    ----------
    name : str
      problem name
    dim : int
      dimension (#cities)
    D : numpy array
      Distance matrix (size is dim*dim)
    C : dict
      node coordinate data
    """
    def __init__(self, name, dim, D=None, C=None):
        self.name = name
        self.dim = dim
        self.D = D  # Distance matrix
        self.C = C  # Node Coordinate data
        logger.debug(self.__str__(detail=True))


    def getBestValue(self):
        """return the optimal value of objective function
        """
        return None


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
        if 'permutation' in solver.can_solve_problems:
            return True, self.createPermProblem()
        elif 'lp' in solver.can_solve_problems:
            return True, self.createLpProblem()
        else:
            logger.info('this instance only can be `permutation` formulation')
            return False, None


    def createPermProblem(self):
        # Variables
        perm = Variable('perm', lowBound=0, upBound=self.dim-1, cat='Permutation')

        # Object
        def tsp_dist(perm):
            distance = 0
            for head, tail in zip(perm, perm[1:]+[perm[0]]):
                distance += self.D[head][tail]
            return distance
        tsp_obj = CustomExpression(func=tsp_dist, variables=[perm])

        # Problem
        prob = Problem(name=f'TSP:{self.name}')
        prob += tsp_obj
        return prob


    def createLpProblem(self):
        # Variables
        cities = list(range(self.dim))
        x = Variable.matrix('x', len(cities), len(cities), cat='Binary')
        np.fill_diagonal(x, Const(0))

        # Problem
        prob = Problem(name=f'TSP(LP):{self.name}')

        # Objective
        tsp_obj = Sum(self.D * x)  # sum(D[i, j] * x[i, j] for all i, j)
        prob += tsp_obj

        # Constants (flow condition)
        for i in cities:
            prob += Sum(x[i, :]) == 1
            prob += Sum(x[:, i]) == 1

        # Connstants (remove subtour)
        subsets = [
            subset for subset in combinations(cities, n_cities)
            for n_cities in range(2, self.dim-1)
        ]
        for subset in tqdm(subsets):
            prob += Sum(x[subset, subset]) <= n_cities - 1
        return prob


    def __str__(self, detail=False):
        s  = f'NAME: {self.name}\n'
        s += f'DIMENSION: {self.D.shape[0]}'
        if detail:
            s += f'\nD: {self.D}'
        return s
