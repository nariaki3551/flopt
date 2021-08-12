import collections

from flopt.constraint import Constraint
from flopt.env import setup_logger

logger = setup_logger(__name__)


class SelfReturn:
    def __init__(self, var):
        self.var = var
    def value(self):
        return self.var



class Expression:
    """

    This represents the operation of two items
    elmA (operater) elmB

    Parameters
    ----------
    elmA : Variable family or Expression family
      first element
    elmB : Variable family or Expression family
      later element
    operater : str
      operater between elmA and elmB

    Examples
    --------

    >>> a = Variable(name='a', iniValue=1, cat='Integer')
    >>> b = Variable(name='b', iniValue=2, cat='Continuous')
    >>> c = Expression(a, b, '+')
    >>> print(c)
    >>> Name: a+b
         Type    : Expression
         Value   : 3
    >>> c.value()
    >>> 3
    >>> c.getVariables()
    >>> {VarElement("b", 1, 2, 2), VarElement("a", 0, 1, 1)}

    operater "+", "-", "*", "/", "^" and "%" are supported for Integer, Binary and
    Continuous Variables.

    >>> a = Variable(name='a', iniValue=1, cat='Integer')  # a.value() is 1
    >>> b = Variable(name='b', iniValue=2, cat='Continuous')  # b.value() is 2
    >>> Expression(a, b, '+').value()  # a+b addition
    >>> 3
    >>> Expression(a, b, '-').value()  # a-b substraction
    >>> -1
    >>> Expression(a, b, '*').value()  # a*b multiplication
    >>> 2
    >>> Expression(a, b, '/').value()  # a/b division
    >>> 0.5
    >>> Expression(a, b, '^').value()  # a/b division
    >>> 1
    >>> Expression(a, b, '%').value()  # a%b modulo
    >>> 1

    operater "&", "|" are supported for Binary Variable.

    >>> a = Variable(name='a', iniValue=1, cat='Binary')
    >>> b = Variable(name='b', iniValue=0, cat='Binary')
    >>> Expression(a, b, '&').value().value()  # a&b bitwise and
    >>> 0
    >>> Expression(a, b, '|').value().value()  # a&b bitwise or
    >>> 1
    """
    def __init__(self, elmA, elmB, operater):
        self.elmA_name = f'({elmA.name})' if elmA.getType() == 'Expression' else elmA.name
        self.elmB_name = f'({elmB.name})' if elmB.getType() == 'Expression' else elmB.name
        self.name = f'{self.elmA_name}{operater}{self.elmB_name}'
        self.type = 'Expression'
        self.elmA = elmA
        self.elmB = elmB
        self.operater = operater
        self.var_dict = None


    def setVarDict(self, var_dict):
        self.var_dict = var_dict


    def unsetVarDict(self):
        self.var_dict = None


    def value(self, solution=None):
        if solution is None:
            return self._value()
        else:
            self.setVarDict(solution.toDict())
            return self._value()


    def _value(self):
        """
        Returns
        -------
        float or int
            return value of expression
        """
        assert self.operater != '' or isinstance(self.elmB, ExpressionNull)
        elmA = self.elmA
        elmB = self.elmB
        if self.var_dict is not None:
            if isinstance(self.elmA, Expression):
                self.elmA.setVarDict(self.var_dict)
            elif self.elmA.name in self.var_dict:
                elmA = self.var_dict[self.elmA.name]
            if isinstance(self.elmB, Expression):
                self.elmB.setVarDict(self.var_dict)
            elif self.elmB.name in self.var_dict:
                elmB = self.var_dict[self.elmB.name]

        if self.operater == '+':
            return elmA.value() + elmB.value()
        elif self.operater == '-':
            return elmA.value() - elmB.value()
        elif self.operater == '*':
            return elmA.value() * elmB.value()
        elif self.operater == '/':
            return elmA.value() / elmB.value()
        elif self.operater == '^':
            return elmA.value() ** elmB.value()
        elif self.operater == '%':
            return elmA.value() % elmB.value()
        elif self.operater == '&':
            return elmA.value() and elmB.value()
        elif self.operater == '|':
            return elmA.value() or elmB.value()

        self.unsetVarDict()


    def getType(self):
        """
        Returns
        -------
        str
          return type of expressiono
        """
        return self.type


    def getVariables(self):
        """
        Returns
        -------
        set
          return the variable object used in this expressiono
        """
        variables = self.elmA.getVariables() | self.elmB.getVariables()
        return variables


    def hasCustomExpression(self):
        """
        Returns
        -------
        bool
            return true if CustomExpression object is in this expression else false
        """
        return self.elmA.hasCustomExpression() or self.elmB.hasCustomExpression()


    def maxDegree(self):
        """
        Returns
        -------
        int
            return the max degree of variants

        Note
        ----
        if the CustomExpression object is in this expresson,
        return Unknown
        """
        if self.hasCustomExpression():
            return 'Unknown'
        elif isinstance(self, ExpressionConst):
            return 0
        elif self.operater in {'%', '&', '|'}:
            return 'Unknown'
        else:
            import sympy
            expr = sympy.sympify(self.name)
            if expr.is_constant():
                return 0
            poly = sympy.poly(expr)
            return max(poly.degree_list())


    def isLinear(self):
        """
        Returns
        -------
        bool
            return true if this expression is linear else false

        Examples
        --------
        >>> import flopt
        >>> a = flopt.Variable('a', iniValue=3)
        >>> b = flopt.Variable('b', iniValue=3)
        >>> (a+b).isLinear()
        >>> True
        >>> (a*b).isLinear()
        >>> False
        >>> ce = flopt.CustomExpression(lambda x: x, [a])
        >>> ce.isLinear()
        >>> 'Unknown'
        """
        if self.hasCustomExpression():
            return 'Unknown'
        if self.maxDegree() > 1:
            return False
        import sympy
        expr = sympy.sympify(self.name)
        variables = self.getVariables()
        return all(expr.diff(var.name).is_constant() for var in variables)


    def toLinear(self, x=None):
        """
        Parameters
        ----------
        x: list or numpy.array of VarElement family

        Returns
        -------
        LpStructure

        Examples
        --------

        >>> a = flopt.Variable('a', cat='Binary')
        >>> b = flopt.Variable('b', cat='Binary')
        >>> c = flopt.Variable('c', lowBound=-1, upBound=2, cat='Integer')
        >>> expr = a + b + c + 4
        >>> expr
        >>> Name: c+(a+b)
              Type    : Expression
              Value   : 0
              Degree  : 1

        >>> # check to be able to linear
        >>> expr.isLinear()
        >>> True

        >>> linear = expr.toLinear()
        >>> linear.c
        >>> [[1.]
             [1.]
             [1.]]
        >>> linear.constant
        >>> 4
        >>> linear.x
        >>> [VarElement("c", -1, 2, 0),
             VarElement("b", 0, 1, 0),
             VarElement("a", 0, 1, 0)]
        """
        assert self.isLinear()
        import sympy
        import numpy as np
        expr = sympy.sympify(self.name).expand()
        LinearStructure = collections.namedtuple(
            'LinearStructure',
            'c constant x'
            )

        if x is None:
            x_list = list(self.getVariables())
            x_list.sort(key=lambda var: var.name)
            x = np.array(x_list)

        num_variables = len(x)
        c = np.zeros((num_variables, ))
        for i in range(num_variables):
            var_i = x[i]
            coeff = expr.coeff(var_i.name).as_coefficients_dict()[1]
            c[i] = coeff
        constant = expr.as_coefficients_dict()[1]
        return LinearStructure(c, constant, x)


    def isIsing(self):
        """
        Returns
        -------
        bool
            return true if this expression is linear else false
        """
        if any( var.type not in {'VarSpin', 'VarBinary'} for var in self.getVariables() ):
            return False
        if self.hasCustomExpression():
            return 'Unknown'
        if self.maxDegree() > 2:
            return False
        import sympy
        expr = sympy.sympify(self.name)
        variables = self.getVariables()
        x = list(self.getVariables())
        num_variables = len(x)

        for i in range(num_variables):
            var_i = x[i]
            diff_expr = expr.diff(var_i.name)
            for j in range(i+1, num_variables):
                var_j = x[j]
                if not diff_expr.diff(var_j.name).is_constant():
                    return False
        return True


    def toIsing(self, x=None):
        """
        Parameters
        ----------
        x : list or numpy.array or VarElement family

        Returns
        -------
        IsingStructure

        Examples
        --------

        .. code-block :: python

            import flopt
            a = flopt.Variable(name='a', iniValue=1, cat='Binary')
            b = flopt.Variable(name='b', iniValue=1, cat='Binary')
            c = flopt.Variable(name='c', iniValue=1, cat='Binary')

            # make Ising model
            import numpy as np
            x = np.array([a, b, c])
            J = np.array([
                [1, 2, 1],
                [0, 1, 1],
                [0, 0, 3]
            ])
            h = np.array([1, 2, 0])
            obj = - (x.T).dot(J).dot(x) - (h.T).dot(x)
            print(obj)
            >>> Name: (0-(((a*a)+(b*(b+(a*2))))+(c*((a+b)+(c*3)))))-(a+(b*2))
            >>>   Type    : Expression
            >>>   Value   : -12
            >>>   Degree  : 2

            # check to be able to ising
            print(obj.isIsing())
            >>> True

            # obj to Ising model
            ising = obj.toIsing()
            print(ising.J)
            >>> [[1. 2. 1.]
            >>>  [0. 1. 1.]
            >>>  [0. 0. 3.]]
            print(ising.h)
            >>> [1. 2. 0.]
            print(ising.x)
            >>> [VarElement("a", 0, 1, 1) VarElement("b", 0, 1, 1) VarElement("c", 0, 1, 1)]

        We set solution by

        .. code-block :: python

            solution = [1, -1, 1]
            for var, value in zip(ising.x, solution):
                var.setValue(value)
        """
        assert self.isIsing()
        import sympy
        import numpy as np
        IsingStructure = collections.namedtuple(
            'IsingStructure',
            'J h x'
            )
        _expr = self.toSpin()
        expr = sympy.sympify(_expr.name).expand()

        if x is None:
            x_list = list(_expr.getVariables())
            x_list.sort(key=lambda var: var.name)
            x = np.array(x_list)

        num_variables = len(x)

        J = np.zeros((num_variables, num_variables))
        for i in range(num_variables):
            var_i = x[i]
            coeff = expr.coeff(var_i.name, 2)
            J[i, i] = - coeff
            for j in range(i+1, num_variables):
                var_j = x[j]
                coeff = expr.coeff(var_i.name).coeff(var_j.name)
                J[i, j] = - coeff

        h = np.zeros((num_variables, ))
        for i in range(num_variables):
            var_i = x[i]
            coeff = expr.coeff(var_i.name).as_coefficients_dict()[1]
            h[i] = - coeff

        return IsingStructure(J, h, x)


    def reform(self, reform_type='simplify'):
        """
        Parameters
        ----------
        reform_type : {'expand', 'simplify'}
        """
        assert reform_type in {'expand', 'simplify'}
        import sympy
        if reform_type == 'expand':
            expr = sympy.sympify(self.name).expand()
            reform_expr = eval(
                str(expr),
                {var.name: var for var in self.getVariables()}
                )
            self = reform_expr
        else:
            expr = sympy.sympify(self.name).simplify()
            reform_expr = eval(
                str(expr),
                {var.name: var for var in self.getVariables()}
                )
            self = reform_expr
        return self


    def toBinary(self):
        """create expression replased binary to spin

        Returns
        -------
        Expression
        """
        if all( var.type == 'VarBinary' for var in self.getVariables() ):
            return self
        var_dict = {
            var.name: SelfReturn(var.toBinary() if var.type == 'VarSpin' else var)
            for var in self.getVariables()
        }
        self.setVarDict(var_dict)
        return self.value()


    def toSpin(self):
        """create expression replased binary to spin

        Returns
        -------
        Expression
        """
        if all( var.type == 'VarSpin' for var in self.getVariables() ):
            return self
        var_dict = {
            var.name: SelfReturn(var.toSpin() if var.type == 'VarBinary' else var)
            for var in self.getVariables()
        }
        self.setVarDict(var_dict)
        return self.value()


    def __add__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                return self
            other = ExpressionConst(other)
            return Expression(self, other, '+')
        elif isinstance(other, Expression):
            return Expression(self, other, '+')
        else:
            return NotImplemented

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                return self
            other = ExpressionConst(other)
            return Expression(self, other, '-')
        elif isinstance(other, Expression):
            return Expression(self, other, '-')
        else:
            return NotImplemented

    def __rsub__(self, other):
        return other + (-self)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                return ExpressionConst(0)
            elif other == 1:
                return self
            other = ExpressionConst(other)
            return Expression(self, other, '*')
        elif isinstance(other, Expression):
            return Expression(self, other, '*')
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 1:
                return self
            other = ExpressionConst(other)
            return Expression(self, other, '/')
        elif isinstance(other, Expression):
            return Expression(self, other, '/')
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                return ExpressionConst(0)
            other = ExpressionConst(other)
            return Expression(other, self, '/')
        elif isinstance(other, Expression):
            return Expression(other, self, '/')
        else:
            return NotImplemented

    def __pow__(self, other):
        if isinstance(other, (int, float)):
            if other == 1:
                return self
            other = ExpressionConst(other)
            return Expression(self, other, '^')
        elif isinstance(other, Expression):
            return Expression(self, other, '^')
        else:
            return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, (int, float)):
            if other == 1:
                return ExpressionConst(1)
            other = ExpressionConst(other)
            return Expression(other, self, '^')
        elif isinstance(other, Expression):
            return Expression(other, self, '^')
        else:
            return NotImplemented

    def __and__(self, other):
        if isinstance(other, (int, float)):
            other = ExpressionConst(other)
            return Expression(self, other, '&')
        elif isinstance(other, Expression):
            return Expression(self, other, '&')
        else:
            return NotImplemented

    def __rand__(self, other):
        return self and other

    def __or__(self, other):
        if isinstance(other, (int, float)):
            other = ExpressionConst(other)
            return Expression(self, other, '|')
        elif isinstance(other, Expression):
            return Expression(self, other, '|')
        else:
            return NotImplemented

    def __ror__(self, other):
        return self or other

    def __neg__(self):
        # 0 - self
        zero = ExpressionConst(0)
        return Expression(zero, self, '-')

    def __abs__(self):
        return abs(self.value())

    def __int__(self):
        return int(self.value())

    def __float__(self):
        return float(self.value())

    def __pos__(self):
        return self

    def __hash__(self):
        return hash((hash(self.elmA), hash(self.elmB), hash(self.operater)))

    def __eq__(self, other):
        return Constraint(self-other, 'eq')

    def __le__(self, other):
        return Constraint(self-other, 'le')

    def __ge__(self, other):
        return Constraint(self-other, 'ge')

    def __str__(self):
        s  = f'Name: {self.name}\n'
        s += f'  Type    : {self.type}\n'
        s += f'  Value   : {self.value()}\n'
        s += f'  Degree  : {self.maxDegree()}\n'
        return s

    def __repr__(self):
        s = f'Expression({self.elmA_name}, {self.elmB_name}, {self.operater})'
        return s



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

    In addition, we can use some operations ("+", "-", "*", "/") between CustomExpression and
    Variable, Expression and CustomExpression.

    >>> def user_func(x):
    >>>     return x
    >>> a = Variable('a', iniValue=3)
    >>> obj = CustomExpression(user_func, [a])
    >>> obj.value()
    >>> 3

    For example,

    >>> b = Variable('b', iniValue=1)
    >>> obj_b = obj + b  # 3+1
    >>> obj_b.value()
    >>> 4
    >>> obj_b.getVariables()
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
        if self.var_dict is None:
            variables = self.variables
        else:
            variables = [self.var_dict[var.name] for var in self.variables]

        value = self.func(*variables)
        if not isinstance(value, (int, float)):
            value = value.value()

        self.unsetVarDict()
        return value

    def getVariables(self):
        return set(self.variables)

    def hasCustomExpression(self):
        """
        Returns
        -------
        bool
            return true if CustomExpression object is in this expression else false
        """
        return True

    def __hash__(self):
        tmp = [hash(self.func)]
        for var in self.variables:
            tmp.append(hash(var))
        return hash(tuple(tmp))

    def __repr__(self):
        return 'CustomExpression'


class ExpressionConst(Expression):
    """
    It is the expression of constant value.
    We use it the operation including constant value.
    See Expression class `__add__`, `__sub__`, and so on.

    Parameters
    ----------
    value : int or float
      value

    """
    def __init__(self, value):
        self.name = f'{value}'
        self._value = value
        self.type = 'ExpressionConst'

    def getType(self):
        return self.type

    def value(self):
        return self._value

    def getVariables(self):
        # for getVariables() in Expression calss
        return set()

    def hasCustomExpression(self):
        # for hasCustomExpression in Expression calss
        return False

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return ExpressionConst(self._value + other)
        elif isinstance(other, Expression):
            return self._value + other
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return ExpressionConst(self._value - other)
        elif isinstance(other, Expression):
            return self._value + other
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return ExpressionConst(self._value * other)
        elif isinstance(other, Expression):
            return self._value * other
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return ExpressionConst(self._value / other)
        elif isinstance(other, Expression):
            return self._value / other
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return ExpressionConst(other / self._value)
        elif isinstance(other, Expression):
            return other / self._value
        else:
            return NotImplemented

    def __pow__(self, other):
        if isinstance(other, (int, float)):
            return ExpressionConst(self._value ** other)
        elif isinstance(other, Expression):
            return self._value ** other
        else:
            return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, (int, float)):
            return ExpressionConst(other ** self._value)
        elif isinstance(other, Expression):
            return other ** self._value
        else:
            return NotImplemented

    def __neg__(self):
        return ExpressionConst(-self._value)

    def __hash__(self):
        return hash((self._value, self.type))

    def __repr__(self):
        s = f'ExpressionConst({self._value})'
        return s


