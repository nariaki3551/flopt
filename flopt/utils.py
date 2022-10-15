import types
import operator
import functools

import numpy as np

from flopt.variable import VarElement, VariableArray
from flopt.expression import Expression, CustomExpression, Const
import flopt.expression
from flopt.solution import Solution
from flopt.constants import number_classes, array_classes


def Sum(x):
    """
    Parameters
    ----------
    x : iterator of varElement

    Returns
    -------
    all sum of x
    """
    if isinstance(x, types.GeneratorType):
        return Sum(list(x))
    if all(isinstance(_x, number_classes) for _x in x):
        return sum(x)
    elif isinstance(x, np.ndarray):
        return flopt.expression.Sum(x.ravel())
    else:
        return flopt.expression.Sum(x)


def Prod(x):
    """
    Parameters
    ----------
    x : iterator of varElement

    Returns
    -------
    all product of x
    """
    if isinstance(x, types.GeneratorType):
        return Prod(list(x))
    if all(isinstance(_x, number_classes) for _x in x):
        return functools.reduce(operator.mul, x)
    elif isinstance(x, np.ndarray):
        return flopt.expression.Prod(x.ravel())
    else:
        return flopt.expression.Prod(x)


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
    return Sum(_x * _y for _x, _y in zip(x, y))


def Sqrt(x):
    return x**0.5


def Norm(x):
    return Sqrt(Dot(x, x))


def Sqnorm(x):
    return Dot(x, x)


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
    if isinstance(x, (VarElement, Expression, Const, Solution)):
        return x.value()
    elif isinstance(x, (list, tuple)):
        cast = type(x)
        return cast([var.value() for var in x])
    elif isinstance(x, np.ndarray):

        def to_value(x):
            return x.value()

        cast = np.frompyfunc(to_value, 1, 1)
        return cast(x)
    else:
        return x


def get_dot_graph(expression, save_file, rankdir=None):
    with open(save_file, "w") as writer:
        print("digraph g {", file=writer)
        if rankdir is not None:
            print(f"rankdir = {rankdir};", file=writer)
        _get_dot_graph(expression, writer)
        print("}", file=writer)


def _get_dot_graph(expression, writer):
    node_self = id(expression)
    node_str = '{} [label="{}", color=orange, style=filled]'
    operation_str = '{} [label="{}", color=lightblue, style=filled]'
    edge_str = "{} -> {}"
    print(node_str.format(node_self, expression.getName()), file=writer)
    if isinstance(expression, flopt.expression.CustomExpression):
        node_operator = hash((expression, 1))
        operator_str = "CustomFunction"
        print(operation_str.format(node_operator, operator_str), file=writer)
        print(edge_str.format(node_operator, node_self), file=writer)
        for var in expression.arg:
            node = _get_dot_graph(var, writer)
            print(edge_str.format(node, node_operator), file=writer)
    elif isinstance(expression, flopt.expression.Expression):
        node_operator = hash((expression, expression.operator))
        print(operation_str.format(node_operator, expression.operator), file=writer)
        print(edge_str.format(node_operator, node_self), file=writer)
        nodeA = _get_dot_graph(expression.elmA, writer)
        nodeB = _get_dot_graph(expression.elmB, writer)
        print(edge_str.format(nodeA, node_operator), file=writer)
        print(edge_str.format(nodeB, node_operator), file=writer)
    elif isinstance(expression, flopt.expression.Reduction):
        node_operator = hash((expression, 1))
        operator_str = "+" if isinstance(expression, flopt.expression.Sum) else "*"
        print(operation_str.format(node_operator, operator_str), file=writer)
        print(edge_str.format(node_operator, node_self), file=writer)
        for elm in expression.elms:
            node = _get_dot_graph(elm, writer)
            print(edge_str.format(node, node_operator), file=writer)
    else:
        # VarElement or Const
        pass
    return node_self
