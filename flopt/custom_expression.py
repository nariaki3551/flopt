from functools import reduce
from operator import mul

from flopt.variable import VarElement
from flopt.expression import Expression
from flopt.env import setup_logger


logger = setup_logger(__name__)


class CustomExpression(Expression):
    """
    Objective function from using user defined function.

    Parameters
    ----------
    func : function
      objective function
    variables : list
      variables

    Examples
    --------

    We have the objective funcion :math:`simulater(a, b)` where simulater is
    a black box function, a and b are continuous variable.
    In this case, we can input objective function into Problem
    by using CustomExpression as follows.

    .. code-block:: python

      a = Variable('a', cat='Continuous')
      b = Variable('b', cat='Continuous')
      def user_simulater(a, b):
          return simulater(a, b)
      obj = CustomExpression(func=user_simulater, variables=[a, b])
      prob = Problem('simulater')
      prob += obj

    .. note::

      The order of variables in the variables list must be the same as
      the func argument. (However even the name does not have to be the same.)
      In the case that objective function is simulater(a, b)
      where a is integer variable and b is the continuous variable,

      .. code-block:: python

        x = Variable('x', cat='Integer')
        y = Variable('y', cat='Continuous')
        def user_simulater(a, b):
            return simulater(a, b)
        obj = CustomExpression(func=user_simulater, variables=[x, y])
    

    In addition, we can use some operations ("+", "-", "*", "/") between CustomExpression and
    Variable, Expression and CustomExpression.

    >>> def user_func(x):
    >>>     return x
    >>> a = Variable('a', iniValue=3)
    >>> obj = CustomExpression(user_func, [a])
    >>> obj.value()
    >>> 3
    
    CustomExpression + Variable

    >>> b = Variable('b', iniValue=1)
    >>> obj_b = obj + b  # 3+1
    >>> obj_b.value()
    >>> 4
    >>> obj_b.variables
    >>> [VarElement("a", -10000000000.0, 10000000000.0, 3),
         VarElement("b", -10000000000.0, 10000000000.0, 1)]

    CustomExpression + Expression

    >>> c = Variable('c', iniValue=2)
    >>> obj_bc = (b+c) + obj # (1+2)+3
    >>> obj_bc.value()
    >>> 6
    >>> obj_bc.variables
    >>> [VarElement("a", -10000000000.0, 10000000000.0, 3),
         VarElement("b", -10000000000.0, 10000000000.0, 1),
         VarElement("c", -10000000000.0, 10000000000.0, 2)]
    
    CustomExpression + CustomExpression

    >>> def user_func2(y):
    >>>     return y
    >>> obj2 = CustomExpression(user_func2, [b])
    >>> obj2.value()
    >>> 1
    >>> obj_sum = (obj + obj2)  # 3+1
    >>> obj_sum.value()
    >>> 4
    >>> [VarElement("a", -10000000000.0, 10000000000.0, 3),
         VarElement("b", -10000000000.0, 10000000000.0, 1)]

    See Also
    --------
    flopt.expression.Expression
    """
    def __init__(self, func, variables):
        self.func = func
        self.variables = variables
        self.type = 'CustomExpression'
        self.var_dict = None

        res = (func(*variables))
        if isinstance(res, (int, float)):
            self.name = f'{res}'
        else:
            self.name = res.name

    def _value(self):
        """
        Returns
        -------
        int or float
          return objective value
        """
        if self.var_dict is None:
            variables = self.variables
        else:
            variables = [self.var_dict[var.name] for var in self.variables]

        value = self.func(*variables)
        if isinstance(value, (VarElement, Expression)):
            value = value.value()
        
        self.unsetVarDict()
        return value

    def getVariables(self):
        return set(self.variables)

    def __neg__(self):
        negative_func = lambda *x: - self.func(*x)
        return CustomExpression(negative_func, self.variables)

    def __pos__(self):
        return self

    def __abs__(self):
        return abs(self.value())

    def __int__(self):
        return int(self.value())

    def __float__(self):
        return float(self.value())

    def __hash__(self):
        tmp = [hash(self.func)]
        for var in self.variables:
            tmp.append(hash(var))
        return hash(tuple(tmp))
