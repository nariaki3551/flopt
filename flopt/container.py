import operator
import itertools
import functools

import numpy as np


class FloptNdarray(np.ndarray):
    def __new__(cls, array, *args, **kwargs):
        if isinstance(array, (list, tuple)):
            shape = (len(array),)
        else:
            shape = array.shape
        obj = super().__new__(cls, shape, dtype=object)
        return obj

    def __init__(self, array, *args, **kwargs):
        for i in itertools.product(*map(range, self.shape)):
            j = i[0] if isinstance(array, (list, tuple)) else i
            self[i] = array[j]

    def value(self, solution=None, var_dict=None):
        assert not (solution is not None and var_dict is not None)
        if solution is not None:
            var_dict = solution.toDict()
        v = np.ndarray(self.shape)
        for i in itertools.product(*map(range, self.shape)):
            if var_dict is not None and self[i].name in var_dict:
                v[i] = var_dict[self[i].name].value()
            else:
                v[i] = self[i].value()
        return v

    def setValue(self, values):
        assert self.shape == values.shape
        for i in itertools.product(*map(range, self.shape)):
            self[i].setValue(values[i])

    def getVariables(self):
        elm_generator = (self[i] for i in itertools.product(*map(range, self.shape)))
        return functools.reduce(
            operator.or_,
            (elm.getVariables() for elm in elm_generator),
        )

    def setRandom(self):
        for var in self.getVariables():
            var.setRandom()
        return self
