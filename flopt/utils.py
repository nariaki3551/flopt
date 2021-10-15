import numpy as np

from flopt.variable import VarElement
from flopt.expression import Expression, Const


def Sum(x):
    """
    Parameters
    ----------
    x : iterator of varElement

    Returns
    -------
    all sum of x
    """
    if isinstance(x, np.ndarray):
        return x.sum()
    else:
        return sum(x)


def Prod(x):
    """
    Parameters
    ----------
    x : iterator of varElement

    Returns
    -------
    all product of x
    """
    return np.prod(list(x))


def Dot(x, y):
    """
    Parameters
    ----------
    x : iterator of varElement or number
    y : iterator of varElement or number

    Returns
    -------
    inner product of x and y
    """
    return sum(_x * _y for _x, _y in zip(x, y))


def Value(x):
    """
    Parameters
    ----------
    x : VarElement or array of VarElement

    Examples
    --------

    >>> from flopt import Variable, value
    >>>
    >>> y = Variable('y', ini_value=1)
    >>> value(y)
    >>> 1
    >>>
    >>> x = Variable.array('x', 3, cat='Binary', ini_value=0)
    >>> value(x)
    >>> [0 0 0]
    """
    if isinstance(x, (VarElement, Expression, Const)):
        return x.value()
    elif isinstance(x, (list, tuple)):
        cast = type(x)
        return cast([var.value() for var in x])
    elif isinstance(x, np.ndarray):
        def to_value(x):
            return x.value()
        cast = np.frompyfunc(to_value, 1, 1)
        return cast(x)

