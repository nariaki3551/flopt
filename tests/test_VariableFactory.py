import pytest

import numpy as np

from flopt import Variable
from flopt.variable import VarBinary, VarContinuous


def test_Variable_dict1():
    x = Variable.dict('x', [0, 1])
    assert isinstance(x[0], VarContinuous)
    assert isinstance(x[1], VarContinuous)
    assert x[0].name == "x_0"
    assert x[1].name == "x_1"
    assert len(x) == 2

def test_Variable_dict2():
    x = Variable.dict('x', range(2), cat='Binary')
    assert isinstance(x[0], VarBinary)
    assert isinstance(x[1], VarBinary)
    assert x[0].name == "x_0"
    assert x[1].name == "x_1"
    assert len(x) == 2

def test_Variable_dict3():
    x = Variable.dict('x', (range(2), range(2)))
    assert x[0, 0].name == "x_0_0"
    assert len(x) == 4

def test_Variable_dict3():
    x = Variable.dict('x', (range(2), range(2), range(2)))
    assert x[0, 0, 0].name == "x_0_0_0"
    assert len(x) == 8


def test_Variable_array1():
    x = Variable.array('x', 2)
    assert x.shape == (2, )
    assert x[0].name == "x_0"
    assert x[1].name == "x_1"

def test_Variable_array2():
    x = Variable.array('x', (2, 2))
    assert x.shape == (2, 2)
    assert x[0, 0].name == "x_0_0"
    assert x[0, 1].name == "x_0_1"
    assert x[1, 0].name == "x_1_0"
    assert x[1, 1].name == "x_1_1"

def test_Variable_array3():
    x = Variable.array('x', (2, 2, 2))
    assert x.shape == (2, 2, 2)


def test_Variable_matrix1():
    x = Variable.matrix('x', 2, 2)
    assert x.shape == (2, 2)
