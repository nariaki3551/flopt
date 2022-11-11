import types
import operator
import functools

import numpy as np

from flopt.variable import VarElement
from flopt.expression import (
    ExpressionElement,
    Expression,
    CustomExpression,
    Reduction,
    MathOperation,
    Const,
)
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


def Norm(x):
    return Dot(x, x) ** 0.5


def Sqnorm(x):
    return Dot(x, x)


def operation(operator, x):
    """
    Parameters
    ----------
    operator : function of x
    x : VarElement or array of VarElement
    """
    if isinstance(x, types.GeneratorType):
        return operation(operator, list(x))
    if isinstance(x, (VarElement, ExpressionElement)):
        return operator(x)
    elif isinstance(x, (list, tuple)):
        cls = x.__class__
        return cls(operator(var) for var in x)
    elif isinstance(x, np.ndarray):
        return np.frompyfunc(lambda var: operator(var), 1, 1)(x)
    return x


def Value(x):
    """Convert operation to number from variable and expression

    Parameters
    ----------
    x : array or generator of expressions or variables
    """
    return operation(lambda v: v.value(), x)


def sqrt(x):
    """squared root operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """
    return operation(lambda v: v**0.5, x)


def exp(x):
    """exponential operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """

    return operation(flopt.expression.Exp, x)


def cos(x):
    """cosine operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """

    return operation(flopt.expression.Cos, x)


def sin(x):
    """sine operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """

    return operation(flopt.expression.Sin, x)


def tan(x):
    """tangent operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """
    return operation(flopt.expression.Tan, x)


def log(x):
    """logarithmic operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """
    return operation(flopt.expression.Log, x)


def abs(x):
    """absolute operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """
    return operation(flopt.expression.Abs, x)


def floor(x):
    """floor operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """
    return operation(flopt.expression.Floor, x)


def ceil(x):
    """ceil operation

    Parameters
    ----------
    x : array or generator of expressions or variables
    """
    return operation(flopt.expression.Ceil, x)


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
    if isinstance(expression, ExpressionElement):
        if isinstance(expression, Const):
            return node_self
        node_operator = hash(expression)
        operator_str = expression.operator
        if isinstance(expression, CustomExpression):
            elms = expression.arg
        elif isinstance(expression, Expression):
            elms = [expression.elmA, expression.elmB]
        elif isinstance(expression, Reduction):
            elms = expression.elms
        elif isinstance(expression, MathOperation):
            elms = [expression.elm]
        print(operation_str.format(node_operator, operator_str), file=writer)
        print(edge_str.format(node_operator, node_self), file=writer)
        for elm in elms:
            node = _get_dot_graph(elm, writer)
            print(edge_str.format(node, node_operator), file=writer)
    else:
        # VarElement or Const
        pass
    return node_self
