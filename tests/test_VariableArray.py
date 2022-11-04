import pytest

import numpy as np

from flopt.variable import Variable, VariableNdarray


def test_VariableNdarrayWithDict1():
    x = Variable("x", cat="Continuous")
    y = Variable("y", cat="Continuous")
    z = Variable("z", cat="Continuous")
    va = VariableNdarray([x, y, z])
    assert va.index(x.toMonomial()) == 0
    assert va.index(y.toMonomial()) == 1
    assert va.index(z.toMonomial()) == 2


def test_VariableNdarrayWithDict2():
    x = Variable("x", cat="Continuous")
    y = Variable("y", cat="Binary")
    z = Variable("z", cat="Spin")
    va = VariableNdarray([x, y, z])
    assert va.index(x.toMonomial()) == 0
    assert va.index(y.toMonomial()) == 1
    assert va.index(z.toMonomial()) == 2


def test_VariableNdarrayWithDict2():
    x = Variable.array("x", (2, 2), cat="Continuous")
    assert x.index(x[0, 0].toMonomial()) == (0, 0)
    assert x.index(x[0, 1].toMonomial()) == (0, 1)
    assert x.index(x[1, 0].toMonomial()) == (1, 0)
    assert x.index(x[1, 1].toMonomial()) == (1, 1)
