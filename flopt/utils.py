import numpy as np

from flopt.variable import VarElement, VariableArray
from flopt.expression import Expression, CustomExpression, Const


def Sum(x):
    """
    Parameters
    ----------
    x : iterator of varElement

    Returns
    -------
    all sum of x
    """
    if isinstance(x, VariableArray):
        return x.sum().item()
    elif isinstance(x, np.ndarray):
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
    else:
        return x


def get_dot_graph(expression, save_file):
    with open(save_file, "w") as writer:
        print("digraph g {", file=writer)
        _get_dot_graph(expression, writer)
        print("}", file=writer)


def _get_dot_graph(expression, writer):
    node_self = id(expression)
    node_str = '{} [label="{}", color=orange, style=filled]'
    operation_str = '{} [label="{}", color=lightblue, style=filled]'
    edge_str = "{} -> {}"
    print(node_str.format(node_self, expression.name), file=writer)
    if isinstance(expression, CustomExpression):
        for var in expression.arg:
            node = id(var)
            print(node_str.format(node, var.name), file=writer)
            print(edge_str.format(node, node_self))
    elif isinstance(expression, Expression):
        nodeA = _get_dot_graph(expression.elmA, writer)
        nodeB = _get_dot_graph(expression.elmB, writer)
        node_operator = hash((expression, expression.operator))
        print(operation_str.format(node_operator, expression.operator), file=writer)
        print(edge_str.format(nodeA, node_operator), file=writer)
        print(edge_str.format(nodeB, node_operator), file=writer)
        print(edge_str.format(node_operator, node_self), file=writer)
    else:
        # VarElement or Const
        pass
    return node_self
