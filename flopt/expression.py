import collections

import numpy as np

from flopt.polynomial import Monomial, Polynomial
from flopt.constraint import Constraint
from flopt.constants import VariableType, ExpressionType, number_classes, np_float
from flopt.env import setup_logger

logger = setup_logger(__name__)


class SelfReturn:
    def __init__(self, var):
        self.var = var
    def value(self):
        return self.var


# ------------------------------------------------
#   Expression Base Class
# ------------------------------------------------

class Expression:
    """Expression Base Class

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

    Attributes
    ----------
    name : str
    type : str
    elmA : Variable family or Expression family
      first element
    elmB : Variable family or Expression family
      later element
    operater : str
      operater between elmA and elmB
    var_dict : None or dict
    expr : None or sympy.sympify

    Examples
    --------

    >>> a = Variable(name='a', ini_value=1, cat='Integer')
    >>> b = Variable(name='b', ini_value=2, cat='Continuous')
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

    >>> a = Variable(name='a', ini_value=1, cat='Integer')  # a.value() is 1
    >>> b = Variable(name='b', ini_value=2, cat='Continuous')  # b.value() is 2
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

    >>> a = Variable(name='a', ini_value=1, cat='Binary')
    >>> b = Variable(name='b', ini_value=0, cat='Binary')
    >>> Expression(a, b, '&').value().value()  # a&b bitwise and
    >>> 0
    >>> Expression(a, b, '|').value().value()  # a&b bitwise or
    >>> 1
    """
    def __init__(self, elmA, elmB, operater, name=None):
        self.elmA = elmA
        self.elmB = elmB
        self.operater = operater
        if name is not None:
            self.name = name
        else:
            self.setName()
        self._type = ExpressionType.Normal
        self.var_dict = None
        self.polynomial = None

        # set polynomial
        self.setPolynomial()

        # update parents
        self.parents = list()
        if isinstance(self.elmA, Expression):
            self.elmA.parents.append(self)
        if isinstance(self.elmB, Expression):
            self.elmB.parents.append(self)


    def setName(self):
        elmA_name = self.elmA.name
        elmB_name = self.elmB.name
        if isinstance(self.elmA, Expression):
            if self.operater in {'*', '/', '^', '%'}:
                elmA_name = f'({elmA_name})'
        if isinstance(self.elmB, Expression):
            if not self.operater == '+' or not self.elmB.name.startswith('-'):
                elmB_name = f'({elmB_name})'
        self.name = f'{elmA_name}{self.operater}{elmB_name}'


    def setPolynomial(self):
        if self.elmA.isPolynomial() and self.elmB.isPolynomial():
            if self.operater in {'+', '-', '*'}:
                if self.operater == '+':
                    self.polynomial = self.elmA.toPolynomial() + self.elmB.toPolynomial()
                elif self.operater == '-':
                    self.polynomial = self.elmA.toPolynomial() - self.elmB.toPolynomial()
                else:
                    self.polynomial = self.elmA.toPolynomial() * self.elmB.toPolynomial()
            elif self.operater == '^' and isinstance(self.elmB, Const) and isinstance(self.elmB.value(), int):
                self.polynomial = self.elmA.toPolynomial() ** self.elmB.value()
            else:
                self.polynomial = None
        else:
            self.polynomial = None


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


    def type(self):
        """
        Returns
        -------
        str
          return type of expressiono
        """
        return self._type


    def getVariables(self):
        """
        Returns
        -------
        set
          return the variable object used in this expressiono
        """
        variables = self.elmA.getVariables() | self.elmB.getVariables()
        return variables


    def constant(self):
        """
        Returns
        -------
        float
            constant value
        """
        if self.isPolynomial():
            return self.polynomial.constant()
        else:
            import sympy
            return float(sympy.sympify(self.name).expand().as_coefficients_dict()[1])


    def isNeg(self):
        """
        Returns
        -------
        bool
            return if it is - value form else false
        """
        return self.operater == '*'\
                and isinstance(self.elmA, Const) \
                and self.elmA.value() == -1


    def isMonomial(self):
        return self.isPolynomial() and self.polynomial.isMonomial()


    def toMonomial(self):
        return self.polynomial.toMonomial()


    def isPolynomial(self):
        return self.polynomial is not None


    def toPolynomial(self):
        return self.polynomial


    def isQuadratic(self):
        """
        Returns
        -------
        bool
            return true if this expression is quadratic else false
        """
        if not self.isPolynomial():
            return False
        return self.polynomial.isQuadratic() or self.polynomial.simplify().isQuadratic()


    def toQuadratic(self, x=None):
        """
        Parameters
        ----------
        x : list or numpy.array or VarElement family

        Returns
        -------
        collections.namedtuple
            QuadraticStructure('QuadraticStructure', 'Q c C x'),
            such that 1/2 x^T Q x + c^T x + C, Q^T = Q
        """
        assert self.isQuadratic()
        from flopt.convert import QuadraticStructure
        polynomial = self.polynomial.simplify()
        if x is None:
            x = np.array(sorted(self.getVariables(), key=lambda var: var.name))
        num_variables = len(x)

        Q = np.zeros((num_variables, num_variables), dtype=np_float)
        if not polynomial.isLinear():
            for i in range(num_variables):
                Q[i, i] = 2 * polynomial.coeff(x[i], x[i])
                for j in range(i+1, num_variables):
                    Q[i, j] = Q[j, i] = polynomial.coeff(x[i], x[j])

        c = np.zeros((num_variables, ), dtype=np_float)
        for i in range(num_variables):
            c[i] = polynomial.coeff(x[i])

        C = polynomial.constant()
        return QuadraticStructure(Q, c, C, x=x)


    def isLinear(self):
        """
        Returns
        -------
        bool
            return true if this expression is linear else false

        Examples
        --------
        >>> from flopt import Variable
        >>> a = Variable('a', ini_value=3)
        >>> b = Variable('b', ini_value=3)
        >>> (a+b).isLinear()
        >>> True
        >>> (a*b).isLinear()
        >>> False
        """
        if not self.isPolynomial():
            return False
        return self.polynomial.isLinear() or self.polynomial.simplify().isLinear()


    def toLinear(self, x=None):
        """
        Parameters
        ----------
        x: list or numpy.array of VarElement family

        Returns
        -------
        collections.namedtuple
            LinearStructure = collections.namedtuple('LinearStructure', 'c C x'),
            where c.T.dot(x) + C
        """
        assert self.isLinear()
        quadratic = self.toQuadratic(x)
        return self.toQuadratic(x).toLinear()


    def isIsing(self):
        """
        Returns
        -------
        bool
            return true if this expression is ising else false
        """
        if any( var.type() not in {VariableType.Spin, VariableType.Binary}
                for var in self.getVariables() ):
            return False
        return self.isQuadratic()


    def toIsing(self, x=None):
        """
        Parameters
        ----------
        x : list or numpy.array or VarElement family

        Returns
        -------
        collections.namedtuple
            IsingStructure('IsingStructure', 'J h x'),
            converted from sum(a_ij x_i x_j; i >= j) + sum(b_i x_i) + c
            = sum(a_ij x_i x_j; i >= j) + sum(b_i x_i) + sum(c/n x_i x_i),
            as J_ij = a_ij (i != j), a_ii + c/n (i == j), h_i = b_i
        """
        assert self.isIsing()
        from flopt.convert import IsingStructure
        if any( var.type() == VariableType.Binary for var in self.getVariables() ):
            return self.toSpin().toIsing()
        quadratic = self.toQuadratic(x)
        J = - np.triu(quadratic.Q)
        np.fill_diagonal(J, 0.5*np.diag(J))
        return IsingStructure(J, -quadratic.c, quadratic.C, quadratic.x)


    def simplify(self):
        """
        Returns
        -------
        Expression
        """
        import sympy
        expr = eval(
            str(sympy.sympify(self.name).simplify()),
            {var.name: var for var in self.getVariables()}
            )
        if isinstance(expr, number_classes):
            expr = Const(expr)
        expr.parents += self.parents
        return expr


    def expand(self):
        """
        Returns
        -------
        Expression
        """
        import sympy
        expr = eval(
            str(sympy.simplify(self.name).expand()),
            {var.name: var for var in self.getVariables()}
            )
        if isinstance(expr, number_classes):
            expr = Const(expr)
            expr.parents += self.parents
            return expr
        elif isinstance(expr, Expression):
            expr = eval(
                str(sympy.sympify(expr.name).expand()),
                {var.name: var for var in self.getVariables()}
                )
            expr.parents += self.parents
            return expr
        else:
            # VarElement family
            return Expression(expr, Const(0), '+')


    def toBinary(self):
        """create expression replased binary to spin

        Returns
        -------
        Expression
        """
        assert all(var.type() in {VariableType.Binary, VariableType.Spin, VariableType.Integer}
                for var in self.getVariables())
        if all( var.type() == VariableType.Binary for var in self.getVariables() ):
            return self
        var_dict = {
            var.name: SelfReturn(
                var.toBinary() if var.type() in {VariableType.Spin, VariableType.Integer} else var
                )
            for var in self.getVariables()
        }
        self.setVarDict(var_dict)
        return self.value().expand()


    def toSpin(self):
        """create expression replased binary to spin

        Returns
        -------
        Expression
        """
        assert all(var.type() in {VariableType.Binary, VariableType.Spin, VariableType.Integer}
                for var in self.getVariables())
        if all( var.type() == VariableType.Spin for var in self.getVariables() ):
            return self
        var_dict = {
            var.name: SelfReturn(
                var.toSpin() if var.type() in {VariableType.Binary, VariableType.Integer} else var
                )
            for var in self.getVariables()
        }
        self.setVarDict(var_dict)
        return self.value().expand()


    def traverse(self):
        """traverse Expression tree as root is self

        Yield
        -----
        Expression or VarElement
        """
        yield self
        if isinstance(self.elmA, Expression):
            for x in self.elmA.traverse():
                yield x
        if isinstance(self.elmB, Expression):
            for x in self.elmB.traverse():
                yield x


    def traverseAncestors(self):
        """traverse ancestors of self

        Yield
        -----
        Expression or VarElement
        """
        for parent in self.parents:
            yield parent
            if isinstance(parent, Expression):
                for x in parent.traverseAncestors():
                    yield x


    def __add__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return self
            return Expression(self, Const(other), '+')
        elif isinstance(other, Expression):
            if other.isNeg():
                # self + (-other) --> self - other
                return Expression(self, other.elmB, '-')
            else:
                return Expression(self, other, '+')
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return self
            return Expression(Const(other), self, '+')
        elif isinstance(other, Expression):
            return Expression(other, self, '+')
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return self
            elif other < 0:
                return Expression(self, Const(-other), '+')
            else:
                return Expression(self, Const(other), '-')
        elif isinstance(other, Expression):
            if other.isNeg():
                # self - (-1*other) -> self + other
                return Expression(self, other.elmB, '+')
            return Expression(self, other, '-')
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                # 0 - self --> -1 * self
                return Expression(Const(-1), self, '*', name=f'-{self.name}')
            else:
                return Expression(Const(other), self, '-')
        elif isinstance(other, Expression):
            if self.isNeg():
                # other - (-1*self) -> other + self
                return Expression(other, self.elmB, '+')
            return Expression(other, self, '-')
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            elif other == 1:
                return self
            elif other == -1:
                return -self
            return Expression(Const(other), self, '*')
        elif isinstance(other, Expression):
            if self.operater == '*' and isinstance(self.elmA, Const):
                if other.operater == '*' and isinstance(other.elmA, Const):
                    # (a*self) * (b*other) --> a * b * (self*other)
                    return self.elmA * other.elmA * Expression(self.elmB, other.elmB, '*')
                else:
                    # (a*self) * other --> a * (self*other)
                    return self.elmA * Expression(self.elmB, other, '*')
            else:
                if other.operater == '*' and isinstance(other.elmA, Const):
                    # self * (b*other) --> b * (self*other)
                    return other.elmA * Expression(self, other.elmB, '*')
                else:
                    return Expression(self, other, '*')
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            elif other == 1:
                return self
            return Expression(Const(other), self, '*')
        elif isinstance(other, Expression):
            if self.operater == '*' and isinstance(self.elmA, Const):
                if other.operater == '*' and isinstance(other.elmA, Const):
                    # (b*other) * (a*self) --> a * b * (other*self)
                    return self.elmA * other.elmA * Expression(other.elmB, self.elmB, '*')
                else:
                    # other * (a*self) --> a * (other*self)
                    return self.elmA * Expression(other, self.elmB, '*')
            else:
                if other.operater == '*' and isinstance(other.elmA, Const):
                    # (b*other) * self --> b * (other*self)
                    return other.elmA * Expression(other.elmB, self, '*')
                else:
                    return Expression(other, self, '*')
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return self
            return Expression(self, Const(other), '/')
        elif isinstance(other, Expression):
            return Expression(self, other, '/')
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            return Expression(Const(other), self, '/')
        elif isinstance(other, Expression):
            return Expression(other, self, '/')
        else:
            return NotImplemented

    def __pow__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return self
            return Expression(self, Const(other), '^')
        elif isinstance(other, Expression):
            return Expression(self, other, '^')
        else:
            return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return Const(1)
            return Expression(Const(other), self, '^')
        elif isinstance(other, Expression):
            return Expression(other, self, '^')
        else:
            return NotImplemented

    def __and__(self, other):
        if isinstance(other, number_classes):
            return Expression(self, Const(other), '&')
        elif isinstance(other, Expression):
            return Expression(self, other, '&')
        else:
            return NotImplemented

    def __rand__(self, other):
        return self and other

    def __or__(self, other):
        if isinstance(other, number_classes):
            return Expression(self, Const(other), '|')
        elif isinstance(other, Expression):
            return Expression(self, other, '|')
        else:
            return NotImplemented

    def __ror__(self, other):
        return self or other

    def __neg__(self):
        # -1 * self
        return Expression(Const(-1), self, '*', name=f'-{self.name}')

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
        return Constraint(self, other, 'eq')

    def __le__(self, other):
        return Constraint(self, other, 'le')

    def __ge__(self, other):
        return Constraint(self, other, 'ge')

    def __str__(self):
        s  = f'Name: {self.name}\n'
        s += f'  Type    : {self._type}\n'
        s += f'  Value   : {self.value()}\n'
        return s

    def __repr__(self):
        s = f'Expression({self.elmA.name}, {self.elmB.name}, {self.operater})'
        return s



# ------------------------------------------------
#   CustomeExpression Class
# ------------------------------------------------

class CustomExpression(Expression):
    """Objective function from using user defined function.

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
    >>> a = Variable('a', ini_value=3)
    >>> obj = CustomExpression(user_func, [a])
    >>> obj.value()
    >>> 3

    For example,

    >>> b = Variable('b', ini_value=1)
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
    def __init__(self, func, variables, name=None):
        self.func = func
        self.variables = variables
        self.operater = None
        self.name = 'Custom'
        self._type = ExpressionType.Custom
        self.var_dict = None
        self.parents = list()

    def _value(self):
        if self.var_dict is None:
            variables = self.variables
        else:
            variables = [self.var_dict[var.name] for var in self.variables]

        value = self.func(*variables)
        if not isinstance(value, (int, float, np.number)):
            value = value.value()

        self.unsetVarDict()
        return value

    def getVariables(self):
        return set(self.variables)

    def isPolynomial(self):
        return False

    def isLinear(self):
        return False

    def traverse(self):
        yield self

    def __hash__(self):
        tmp = [hash(self.func)]
        for var in self.variables:
            tmp.append(hash(var))
        return hash(tuple(tmp))

    def __repr__(self):
        return 'CustomExpression'


class Const:
    """
    It is the expression of constant value.

    Parameters
    ----------
    value : int or float
      value
    name : str or None
        name of constant
    """
    def __init__(self, value, name=None):
        if name is None:
            name = f'{value}'
        self.name = name
        self._value = value
        self._type = ExpressionType.Const
        self.parents = list()   # dummy
        self.operater = None    # dummy
        self.parents = list()   # dummy

    def type(self):
        return self._type

    def value(self, *args, **kwargs):
        return self._value

    def constant(self):
        return self._value

    def getVariables(self):
        # for getVariables() in Expression calss
        return set()

    def isPolynomial(self):
        return True

    def toMonomial(self):
        return Monomial(coeff=self._value)

    def toPolynomial(self):
        return Polynomial(constant=self._value)

    def isQuadratic(self):
        return True

    def toQuadratic(self, x=None):
        return Expression(Const(0), Const(0), '+').toQuadratic(x)

    def isLinear(self):
        return True

    def toLinear(self, x=None):
        return Expression(Const(0), Const(0), '+').toLinear(x)

    def isIsing(self):
        return True

    def clone(self):
        return Const(self._value)

    def simplify(self):
        return self.clone()

    def expand(self, *args, **kwargs):
        return self.clone()

    def __add__(self, other):
        return self._value + other

    def __radd__(self, other):
        return other + self._value

    def __sub__(self, other):
        return self._value - other

    def __rsub__(self, other):
        if self._value < 0:
            return other + (-self)
        else:
            return other - self._value

    def __mul__(self, other):
        return self._value * other

    def __rmul__(self, other):
        return other * self._value

    def __truediv__(self, other):
        return self._value / other

    def __rtruediv__(self, other):
        return other / self._value

    def __pow__(self, other):
        return self._value ** other

    def __rpow__(self, other):
        return other ** self._value

    def __neg__(self):
        return Const(-self._value)

    def __hash__(self):
        return hash((self._value, self._type))

    def __repr__(self):
        s = f'Const({self._value})'
        return s


