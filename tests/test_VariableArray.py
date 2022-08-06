import pytest

import numpy as np

from flopt.variable import Variable, VariableArray


def test_VariableArrayWithDict1():
    x = Variable('x', cat='Continuous')
    y = Variable('y', cat='Continuous')
    z = Variable('z', cat='Continuous')
    va = VariableArray([x, y, z])
    assert va.index(x.toMonomial()) == 0
    assert va.index(y.toMonomial()) == 1
    assert va.index(z.toMonomial()) == 2

def test_VariableArrayWithDict2():
    x = Variable('x', cat='Continuous')
    y = Variable('y', cat='Binary')
    z = Variable('z', cat='Spin')
    va = VariableArray([x, y, z])
    assert va.index(x.toMonomial()) == 0
    assert va.index(y.toMonomial()) == 1
    assert va.index(z.toMonomial()) == 2

