from functools import reduce
from operator import mul

from .variable import VarElement
from .expression import Expression

class CustomObject:
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
    by using CustomObject as follows.

    .. code-block:: python

      a = Variable('a', cat='Continuous')
      b = Variable('b', cat='Continuous')
      def user_simulater(a, b):
          return simulater(a, b)
      obj = CustomObject(func=user_simulater, variables=[a, b])
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
        obj = CustomObject(func=user_simulater, variables=[x, y])
    

    In addition, we can use some operations ("+", "-", "*", "/") between CustomObject and
    Variable, Expression and CustomObject.

    >>> def user_func(x):
    >>>     return x
    >>> a = Variable('a', iniValue=3)
    >>> obj = CustomObject(user_func, [a])
    >>> obj.value()
    >>> 3
    
    CustomObject + Variable

    >>> b = Variable('b', iniValue=1)
    >>> obj_b = obj + b  # 3+1
    >>> obj_b.value()
    >>> 4
    >>> obj_b.variables
    >>> [VarElement("a", -10000000000.0, 10000000000.0, 3),
         VarElement("b", -10000000000.0, 10000000000.0, 1)]

    CustomObject + Expression

    >>> c = Variable('c', iniValue=2)
    >>> obj_bc = (b+c) + obj # (1+2)+3
    >>> obj_bc.value()
    >>> 6
    >>> obj_bc.variables
    >>> [VarElement("a", -10000000000.0, 10000000000.0, 3),
         VarElement("b", -10000000000.0, 10000000000.0, 1),
         VarElement("c", -10000000000.0, 10000000000.0, 2)]
    
    CustomObject + CustomObject

    >>> def user_func2(y):
    >>>     return y
    >>> obj2 = CustomObject(user_func2, [b])
    >>> obj2.value()
    >>> 1
    >>> obj_sum = (obj + obj2)  # 3+1
    >>> obj_sum.value()
    >>> 4
    >>> [VarElement("a", -10000000000.0, 10000000000.0, 3),
         VarElement("b", -10000000000.0, 10000000000.0, 1)]

    """
    def __init__(self, func, variables):
        self.func = func
        self.variables = variables
        self.var_list = None
    
    def setVarList(self, var_list):
        self.var_list = var_list
    
    def unsetVarList(self):
        self.var_list = None

    def value(self):
        """
        Returns
        -------
        int or float
          return objective value
        """
        if self.var_list is None:
            variables = self.variables
            var_dict = None
        else:
            variables = self.var_list
            var_dict = {var.name : var for var in self.variables}

        value = self.func(*variables)
        if not isinstance(value, (int, float)):
            value = value.value()
        
        self.unsetVarList()
        return value

    def getVariables(self):
        return self.variables

    def __add__(self, other):
        if isinstance(other, (int, float)):
            variables = self.variables
            add_func = lambda *x: self.func(*x) + other
        elif isinstance(other, (VarElement, Expression)):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            add_func = lambda *x: self.func(*x[:n_self]) + other.value()
        elif isinstance(other, CustomObject):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            add_func = lambda *x: self.func(*x[:n_self]) + other.func(*x[n_self:])
        else:
            raise NotImplementedError
        return CustomObject(add_func, variables)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            variables = self.variables
            sub_func = lambda *x: self.func(*x) - other
        elif isinstance(other, (VarElement, Expression)):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            sub_func = lambda *x: self.func(*x[:n_self]) - other.value()
        elif isinstance(other, CustomObject):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            sub_func = lambda *x: self.func(*x[:n_self]) - other.func(*x[n_self:])
        else:
            raise NotImplementedError
        return CustomObject(sub_func, variables)

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            variables = self.variables
            mul_func = lambda *x: self.func(*x) * other
        elif isinstance(other, (VarElement, Expression)):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            mul_func = lambda *x: self.func(*x[:n_self]) * other.value()
        elif isinstance(other, CustomObject):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            mul_func = lambda *x: self.func(*x[:n_self]) * other.func(*x[n_self:])
        else:
            raise NotImplementedError
        return CustomObject(mul_func, variables)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            variables = self.variables
            div_func = lambda *x: self.func(*x) / other
        elif isinstance(other, (VarElement, Expression)):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            div_func = lambda *x: self.func(*x[:n_self]) / other.value()
        elif isinstance(other, CustomObject):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            div_func = lambda *x: self.func(*x[:n_self]) / other.func(*x[n_self:])
        else:
            raise NotImplementedError
        return CustomObject(div_func, variables)

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            variables = self.variables
            div_func = lambda *x: other / self.func(*x)
        elif isinstance(other, (VarElement, Expression)):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            div_func = lambda *x: other.value() / self.func(*x[:n_self])
        elif isinstance(other, CustomObject):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            div_func = lambda *x: other.func(*x[n_self:]) / self.func(*x[:n_self])
        else:
            raise NotImplementedError
        return CustomObject(div_func, variables)

    def __pow__(self, other):
        if isinstance(other, (int, float)):
            variables = self.variables
            pow_func = lambda *x: self.func(*x) ** other
        elif isinstance(other, (VarElement, Expression)):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            pow_func = lambda *x: self.func(*x[:n_self]) ** other.value()
        elif isinstance(other, CustomObject):
            variables = self.variables + list(other.getVariables())
            n_self = len(self.variables)
            pow_func = lambda *x: self.func(*x[:n_self]) ** other.func(*x[n_self:])
        else:
            raise NotImplementedError
        return CustomObject(pow_func, self.variables)

    def __neg__(self):
        negative_func = lambda *x: - self.func(*x)
        return CustomObject(negative_func, self.variables)

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

    def __str__(self):
        s  = f'Name: None\n'
        s += f'  Type    : CustomObject\n'
        s += f'  Value   : {self.value()}\n'
        return s
