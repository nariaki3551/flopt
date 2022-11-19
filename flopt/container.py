import operator
import itertools
import functools

import numpy as np


class FloptNdarray(np.ndarray):
    def __new__(cls, array, *args, **kwargs):
        if isinstance(array, set):
            array = list(array)
        return np.asarray(array, dtype=object).view(cls)

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
