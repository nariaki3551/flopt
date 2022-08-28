import weakref
import functools
import operator
import itertools

import numpy as np

from flopt.polynomial import Monomial, Polynomial
from flopt.constraint import Constraint
from flopt.constants import (
    VariableType,
    ExpressionType,
    ConstraintType,
    number_classes,
    array_classes,
    np_float,
)
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


class ExpressionElement:
    """Expression Base Class

    Attributes
    ----------
    name : str
    type : str
    var_dict : None or dict
    polynomial : None or Polynomial
    parents : list of ExpressionElement
    """

    def __init__(self, name=None):
        if name is not None:
            self.name = name
        else:
            self.setName()
        self.var_dict = None
        self.polynomial = None

        # update parents
        self.parents = list()
        self.linkChildren()

    def setName(self):
        raise NotImplementedError

    def linkChildren(self):
        raise NotImplementedError

    def isPolynomial(self):
        raise NotImplementedError

    def setPolynomial(self):
        raise NotImplementedError

    def _value(self):
        """
        Returns
        -------
        float or int
            return value of expression
        """
        raise NotImplementedError

    def getVariables(self):
        """
        Returns
        -------
        set
          return the variable object used in this expressiono
        """
        raise NotImplementedError

    def isNeg(self):
        """
        Returns
        -------
        bool
            return if it is - value form else false
        """
        raise NotImplementedError

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

    def type(self):
        return self._type

    def constant(self):
        if self.polynomial is not None:
            return self.polynomial.constant()
        elif self.isPolynomial():
            self.setPolynomial()
            return self.polynomial.constant()
        else:
            import sympy

            return float(sympy.sympify(self.name).expand().as_coefficients_dict()[1])

    def isMonomial(self):
        if self.polynomial is not None:
            return self.polynomial.isMonomial()
        elif self.isPolynomial():
            self.setPolynomial()
            return self.polynomial.isMonomial()
        else:
            return False

    def toMonomial(self):
        if self.polynomial is None:
            self.setPolynomial()
        return self.polynomial.toMonomial()

    def toPolynomial(self):
        if self.polynomial is None:
            self.setPolynomial()
        return self.polynomial

    def isQuadratic(self):
        """
        Returns
        -------
        bool
            return true if this expression is quadratic else false
        """
        if self.polynomial is not None:
            return (
                self.polynomial.isQuadratic()
                or self.polynomial.simplify().isQuadratic()
            )
        elif self.isPolynomial():
            self.setPolynomial()
            return (
                self.polynomial.isQuadratic()
                or self.polynomial.simplify().isQuadratic()
            )
        else:
            return False

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
        from flopt.variable import VariableArray

        assert x is None or isinstance(
            x, VariableArray
        ), f"x must be None or VariableArray"
        from flopt.convert import QuadraticStructure

        if self.polynomial is None:
            self.setPolynomial()
        polynomial = self.polynomial.simplify()
        if x is None:
            x = VariableArray(sorted(self.getVariables(), key=lambda var: var.name))

        num_variables = len(x)

        Q = np.zeros((num_variables, num_variables), dtype=np_float)
        c = np.zeros((num_variables,), dtype=np_float)

        # set matrix Q and vector c
        # psude-code
        # |   if not polynomial.isLinear():
        # |       for i in range(num_variables):
        # |           Q[i, i] = 2 * polynomial.coeff(x[i], x[i])
        # |           for j in range(i+1, num_variables):
        # |               Q[i, j] = Q[j, i] = polynomial.coeff(x[i], x[j])
        for mono, coeff in polynomial:
            if mono.isLinear():
                c[x.index(mono)] = coeff
            elif mono.isQuadratic():
                if len(mono.terms) == 1:
                    var_a = list(mono.terms)[0]
                    a_ix = x.index(var_a.toMonomial())
                    Q[a_ix, a_ix] = 2 * coeff
                else:
                    var_a, var_b = list(mono.terms.keys())
                    a_ix = x.index(var_a.toMonomial())
                    b_ix = x.index(var_b.toMonomial())
                    Q[a_ix, b_ix] = Q[b_ix, a_ix] = coeff

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
        if self.polynomial is not None:
            return self.polynomial.isLinear() or self.polynomial.simplify().isLinear()
        elif self.isPolynomial():
            self.setPolynomial()
            return self.polynomial.isLinear() or self.polynomial.simplify().isLinear()
        else:
            return False

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
        from flopt.variable import VariableArray

        assert x is None or isinstance(
            x, VariableArray
        ), f"x must be None or VariableArray"
        from flopt.convert import LinearStructure

        if x is None:
            x = VariableArray(sorted(self.getVariables(), key=lambda var: var.name))

        num_variables = len(x)
        if self.polynomial is None:
            self.setPolynomial()

        c = np.zeros((num_variables,), dtype=np_float)
        for mono, coeff in self.polynomial:
            c[x.index(mono)] = coeff

        C = self.polynomial.constant()
        return LinearStructure(c, C, x=x)

    def isIsing(self):
        """
        Returns
        -------
        bool
            return true if this expression is ising else false
        """
        if any(
            var.type() not in {VariableType.Spin, VariableType.Binary}
            for var in self.getVariables()
        ):
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

        if any(var.type() == VariableType.Binary for var in self.getVariables()):
            return self.toSpin().toIsing()
        quadratic = self.toQuadratic(x)
        J = -np.triu(quadratic.Q)
        np.fill_diagonal(J, 0.5 * np.diag(J))
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
            {var.name: var for var in self.getVariables()},
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
            {var.name: var for var in self.getVariables()},
        )
        if isinstance(expr, number_classes):
            expr = Const(expr)
            expr.parents += self.parents
            return expr
        elif isinstance(expr, Expression):
            expr = eval(
                str(sympy.sympify(expr.name).expand()),
                {var.name: var for var in self.getVariables()},
            )
            expr.parents += self.parents
            return expr
        else:
            # VarElement family
            return Expression(expr, Const(0), "+")

    def toBinary(self):
        """create expression replased binary to spin

        Returns
        -------
        Expression
        """
        assert all(
            var.type() in {VariableType.Binary, VariableType.Spin, VariableType.Integer}
            for var in self.getVariables()
        )
        if all(var.type() == VariableType.Binary for var in self.getVariables()):
            return self
        var_dict = {
            var.name: SelfReturn(
                var.toBinary()
                if var.type() in {VariableType.Spin, VariableType.Integer}
                else var
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
        assert all(
            var.type() in {VariableType.Binary, VariableType.Spin, VariableType.Integer}
            for var in self.getVariables()
        )
        if all(var.type() == VariableType.Spin for var in self.getVariables()):
            return self
        var_dict = {
            var.name: SelfReturn(
                var.toSpin()
                if var.type() in {VariableType.Binary, VariableType.Integer}
                else var
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

    def traverseAncestors(self):
        """traverse ancestors of self

        Yield
        -----
        Expression or VarElement
        """
        for parent in self.parents:
            yield parent
            yield from parent.traverseAncestors()

    def __add__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return self
            return Expression(self, Const(other), "+")
        elif isinstance(other, ExpressionElement):
            if other.isNeg():
                # self + (-other) --> self - other
                return Expression(self, other.elmB, "-")
            else:
                return Expression(self, other, "+")
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return self
            return Expression(Const(other), self, "+")
        elif isinstance(other, ExpressionElement):
            return Expression(other, self, "+")
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return self
            elif other < 0:
                return Expression(self, Const(-other), "+")
            else:
                return Expression(self, Const(other), "-")
        elif isinstance(other, ExpressionElement):
            if other.isNeg():
                # self - (-1*other) -> self + other
                return Expression(self, other.elmB, "+")
            return Expression(self, other, "-")
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                # 0 - self --> -1 * self
                return -self
            else:
                return Expression(Const(other), self, "-")
        elif isinstance(other, ExpressionElement):
            if self.isNeg():
                # other - (-1*self) -> other + self
                return Expression(other, self.elmB, "+")
            return Expression(other, self, "-")
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
            return Expression(Const(other), self, "*")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "*")
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            elif other == 1:
                return self
            return Expression(Const(other), self, "*")
        elif isinstance(other, ExpressionElement):
            return Expression(other, self, "*")
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return self
            return Expression(self, Const(other), "/")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "/")
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            return Expression(Const(other), self, "/")
        elif isinstance(other, ExpressionElement):
            return Expression(other, self, "/")
        else:
            return NotImplemented

    def __pow__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return self
            return Expression(self, Const(other), "^")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "^")
        else:
            return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return Const(1)
            return Expression(Const(other), self, "^")
        elif isinstance(other, ExpressionElement):
            return Expression(other, self, "^")
        else:
            return NotImplemented

    def __and__(self, other):
        if isinstance(other, number_classes):
            return Expression(self, Const(other), "&")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "&")
        else:
            return NotImplemented

    def __rand__(self, other):
        return self and other

    def __or__(self, other):
        if isinstance(other, number_classes):
            return Expression(self, Const(other), "|")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "|")
        else:
            return NotImplemented

    def __ror__(self, other):
        return self or other

    def __neg__(self):
        # -1 * self
        return Expression(Const(-1), self, "*", name=f"-({self.name})")

    def __abs__(self):
        return abs(self.value())

    def __int__(self):
        return int(self.value())

    def __float__(self):
        return float(self.value())

    def __pos__(self):
        return self

    def __hash__(self):
        if (
            self.operator == "+"
            and isinstance(self.elmB, number_classes)
            and self.elmB == 0
        ):
            # a + 0
            return hash(self.elmA)
        elif (
            self.operator == "-"
            and isinstance(self.elmB, number_classes)
            and self.elmB == 0
        ):
            # a - 0
            return hash(self.elmA)
        elif (
            self.operator == "*"
            and isinstance(self.elmA, number_classes)
            and self.elmA == 1
        ):
            # 1 * b
            return hash(self.elmB)
        else:
            return hash((hash(self.elmA), hash(self.elmB), hash(self.operator)))

    def __eq__(self, other):
        # self == other --> self - other == 0
        return Constraint(self - other, ConstraintType.Eq)

    def __le__(self, other):
        # self <= other --> self - other <= 0
        return Constraint(self - other, ConstraintType.Le)

    def __ge__(self, other):
        # self >= other --> other - self <= 0
        return Constraint(other - self, ConstraintType.Le)

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


# ------------------------------------------------
#   Expression Class
# ------------------------------------------------


class Expression(ExpressionElement):
    """Expression Base Class

    This represents the operation of two items
    elmA (operator) elmB

    Parameters
    ----------
    elmA : Variable family or Expression family
      first element
    elmB : Variable family or Expression family
      later element
    operator : str
      operator between elmA and elmB

    Attributes
    ----------
    elmA : Variable family or Expression family
      first element
    elmB : Variable family or Expression family
      later element
    operator : str
      operator between elmA and elmB

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

    operator "+", "-", "*", "/", "^" and "%" are supported for Integer, Binary and
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

    operator "&", "|" are supported for Binary Variable.

    >>> a = Variable(name='a', ini_value=1, cat='Binary')
    >>> b = Variable(name='b', ini_value=0, cat='Binary')
    >>> Expression(a, b, '&').value().value()  # a&b bitwise and
    >>> 0
    >>> Expression(a, b, '|').value().value()  # a&b bitwise or
    >>> 1
    """

    _type = ExpressionType.Normal

    def __init__(self, elmA, elmB, operator, name=None):
        self.elmA = elmA
        self.elmB = elmB
        self.operator = operator
        super().__init__(name=name)

    def setName(self):
        elmA_name = self.elmA.name
        elmB_name = self.elmB.name
        if isinstance(self.elmA, (Expression, Operation)):
            if self.operator in {"*", "/", "^", "%"}:
                elmA_name = f"({elmA_name})"
        if isinstance(self.elmB, Expression):
            if self.operator != "+" or self.elmB.name.startswith("-"):
                elmB_name = f"({elmB_name})"
        self.name = f"{elmA_name}{self.operator}{elmB_name}"

    def linkChildren(self):
        if isinstance(self.elmA, Expression):
            self.elmA.parents.append(self)
        if isinstance(self.elmB, Expression):
            self.elmB.parents.append(self)

    def isPolynomial(self):
        return (
            self.elmA.isPolynomial()
            and self.elmB.isPolynomial()
            and (
                self.operator == "+"
                or self.operator == "-"
                or self.operator == "*"
                or self.operator == "^"
            )
        )

    def setPolynomial(self):
        if self.operator == "+":
            self.polynomial = self.elmA.toPolynomial() + self.elmB.toPolynomial()
        elif self.operator == "-":
            self.polynomial = self.elmA.toPolynomial() - self.elmB.toPolynomial()
        elif self.operator == "*":
            self.polynomial = self.elmA.toPolynomial() * self.elmB.toPolynomial()
        elif (
            self.operator == "^"
            and isinstance(self.elmB, Const)
            and isinstance(self.elmB.value(), int)
        ):
            self.polynomial = self.elmA.toPolynomial() ** self.elmB.value()
        else:
            assert "check whethere this expresson is polynomial or not by .isPolynomial() before execution of setPolynomial()"

    def _value(self):
        """
        Returns
        -------
        float or int
            return value of expression
        """
        elmA = self.elmA
        elmB = self.elmB
        if self.var_dict is not None:
            if isinstance(self.elmA, ExpressionElement):
                self.elmA.setVarDict(self.var_dict)
            elif self.elmA.name in self.var_dict:
                elmA = self.var_dict[self.elmA.name]
            if isinstance(self.elmB, ExpressionElement):
                self.elmB.setVarDict(self.var_dict)
            elif self.elmB.name in self.var_dict:
                elmB = self.var_dict[self.elmB.name]
            self.unsetVarDict()

        if self.operator == "+":
            return elmA.value() + elmB.value()
        elif self.operator == "-":
            return elmA.value() - elmB.value()
        elif self.operator == "*":
            return elmA.value() * elmB.value()
        elif self.operator == "/":
            return elmA.value() / elmB.value()
        elif self.operator == "^":
            return elmA.value() ** elmB.value()
        elif self.operator == "%":
            return elmA.value() % elmB.value()
        elif self.operator == "&":
            return elmA.value() and elmB.value()
        elif self.operator == "|":
            return elmA.value() or elmB.value()

    def getVariables(self):
        """
        Returns
        -------
        set
          return the variable object used in this expressiono
        """
        variables = self.elmA.getVariables() | self.elmB.getVariables()
        return variables

    def traverse(self):
        """traverse Expression tree as root is self

        Yield
        -----
        Expression or VarElement
        """
        yield self
        yield from self.elmA.traverse()
        yield from self.elmB.traverse()

    def isNeg(self):
        return (
            self.operator == "*"
            and isinstance(self.elmA, Const)
            and self.elmA.value() == -1
        )

    def __mul__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            elif other == 1:
                return self
            elif other == -1:
                return -self
            return Expression(Const(other), self, "*")
        elif isinstance(other, Expression):
            if self.operator == "*" and isinstance(self.elmA, Const):
                if other.operator == "*" and isinstance(other.elmA, Const):
                    # (a*self) * (b*other) --> a * b * (self*other)
                    return (
                        self.elmA * other.elmA * Expression(self.elmB, other.elmB, "*")
                    )
                else:
                    # (a*self) * other --> a * (self*other)
                    return self.elmA * Expression(self.elmB, other, "*")
            else:
                if other.operator == "*" and isinstance(other.elmA, Const):
                    # self * (b*other) --> b * (self*other)
                    return other.elmA * Expression(self, other.elmB, "*")
                else:
                    return Expression(self, other, "*")
        elif isinstance(other, CustomExpression):
            return Expression(self, other, "*")
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            elif other == 1:
                return self
            return Expression(Const(other), self, "*")
        elif isinstance(other, Expression):
            if self.operator == "*" and isinstance(self.elmA, Const):
                if other.operator == "*" and isinstance(other.elmA, Const):
                    # (b*other) * (a*self) --> a * b * (other*self)
                    return (
                        self.elmA * other.elmA * Expression(other.elmB, self.elmB, "*")
                    )
                else:
                    # other * (a*self) --> a * (other*self)
                    return self.elmA * Expression(other, self.elmB, "*")
            else:
                if other.operator == "*" and isinstance(other.elmA, Const):
                    # (b*other) * self --> b * (other*self)
                    return other.elmA * Expression(other.elmB, self, "*")
                else:
                    return Expression(other, self, "*")
        elif isinstance(other, CustomExpression):
            return Expression(other, self, "*")
        else:
            return NotImplemented

    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"  Type    : {self._type}\n"
        s += f"  Value   : {self.value()}\n"
        return s

    def __repr__(self):
        s = f"Expression({self.elmA.name}, {self.elmB.name}, {self.operator})"
        return s


# ------------------------------------------------
#   CustomExpression Class
# ------------------------------------------------


def unpack_variables(var_or_array):
    variables = set()
    if isinstance(var_or_array, array_classes):
        array = var_or_array
        for var in array:
            variables |= unpack_variables(var)
    else:
        var = var_or_array
        variables.add(var)
    return variables


def pack_variables(var_or_array, var_dict):
    if isinstance(var_or_array, array_classes):
        cls = var_or_array.__class__
        array = var_or_array
        import flopt.variable

        if isinstance(array, flopt.variable.VariableArray):
            return flopt.variable.VariableArray.init_ufunc(
                var_or_array.shape,
                lambda i: var_dict[array[i].name],
                set_mono=False,
            )
        else:
            return cls(
                itertools.starmap(pack_variables, [(var, var_dict) for var in array])
            )
    else:
        var = var_or_array
        return var_dict[var.name]


class CustomExpression(ExpressionElement):
    """Objective function from using user defined function.

    Parameters
    ----------
    func : function
      objective function
    arg: list of variables

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
      obj = CustomExpression(func=user_simulater, arg=[a, b])
      prob = Problem('simulater')
      prob += obj

    .. note::

      The order of variables in arg parameter must be the same as
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

    _type = ExpressionType.Custom

    def __init__(self, func, arg, name=None):
        self.func = func
        self.arg = arg
        self.variables = unpack_variables(arg)
        super().__init__(name=name)

    def setName(self):
        self.name = f"{self.func.__name__}(*)"

    def linkChildren(self):
        return

    def isPolynomial(self):
        return False

    def setPolynomial(self):
        self.polynomial = None

    def _value(self):
        if self.var_dict is None:
            arg = self.arg
        else:
            arg = pack_variables(self.arg, self.var_dict)

        value = self.func(*arg)
        if not isinstance(value, (int, float, np.number)):
            value = value.value()

        self.unsetVarDict()
        return value

    def getVariables(self):
        return self.variables

    def isNeg(self):
        return False

    def __hash__(self):
        tmp = [hash(self.func)]
        for var in self.variables:
            tmp.append(hash(var))
        return hash(tuple(tmp))

    def __str__(self):
        return f"{self.func.__name__}(*)"

    def __repr__(self):
        return f"CustomExpression({self.func.__name__, self.arg, self.name})"


class Const(float, ExpressionElement):
    """
    It is the expression of constant value.

    Parameters
    ----------
    value : int or float
      value
    name : str or None
        name of constant
    """

    _type = ExpressionType.Const

    def __init__(self, value, name=None):
        if name is None:
            name = f"{value}"
        self._value = value
        super().__init__(name=name)

    def setName(self):
        return NotImplemented

    def linkChildren(self):
        return

    def setPolynomial(self):
        self.polynomial = Polynomial(constant=self._value)

    def _value(self):
        return NotImplemented

    def getVariables(self):
        return set()

    def isNeg(self):
        return self._value < 0

    def value(self, *args, **kwargs):
        return self._value

    def constant(self):
        return self._value

    def isMonomial(self):
        return True

    def toMonomial(self):
        return Monomial(coeff=self._value)

    def isPolynomial(self):
        return True

    def toPolynomial(self):
        return Polynomial(constant=self._value)

    def isQuadratic(self):
        return True

    def toQuadratic(self, x=None):
        return Expression(Const(0), Const(0), "+").toQuadratic(x)

    def isLinear(self):
        return True

    def toLinear(self, x=None):
        return Expression(Const(0), Const(0), "+").toLinear(x)

    def isIsing(self):
        return True

    def simplify(self):
        return Const(self._value)

    def expand(self, *args, **kwargs):
        return Const(self._value)

    def __add__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value + other)
        return self._value + other

    def __radd__(self, other):
        if isinstance(other, number_classes):
            return Const(other + self._value)
        return other + self._value

    def __sub__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value - other)
        return self._value - other

    def __rsub__(self, other):
        if isinstance(other, number_classes):
            return Const(other - self._value)
        if self._value < 0:
            return other + (-self)
        else:
            return other - self._value

    def __mul__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value * other)
        return self._value * other

    def __rmul__(self, other):
        if isinstance(other, number_classes):
            return Const(other * self._value)
        return other * self._value

    def __truediv__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value / other)
        return self._value / other

    def __rtruediv__(self, other):
        if isinstance(other, number_classes):
            return Const(other / self._value)
        return other / self._value

    def __pow__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value**other)
        return self._value**other

    def __rpow__(self, other):
        if isinstance(other, number_classes):
            return Const(other**self._value)
        return other**self._value

    def __neg__(self):
        return Const(-self._value)

    def __hash__(self):
        return hash((self._value, self._type))

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        s = f"Const({self._value})"
        return s


# ------------------------------------------------
#   Utilities
# ------------------------------------------------
to_value_ufunc = np.frompyfunc(lambda x: x.value(), 1, 1)


def to_const(x):
    if isinstance(x, number_classes):
        return Const(x)
    return x


to_const_ufunc = np.frompyfunc(to_const, 1, 1)


# ------------------------------------------------
#   Operation Class
# ------------------------------------------------
class Operation(ExpressionElement):
    def __init__(self, var_or_exps, name=None):
        assert len(var_or_exps) > 0
        self.elms = to_const_ufunc(np.array(var_or_exps, dtype=object))
        super().__init__(name=name)

    def linkChildren(self):
        for elm in self.elms:
            if isinstance(elm, ExpressionElement):
                elm.parents.append(self)

    def getVariables(self):
        variables = set()
        for elm in self.elms:
            variables |= elm.getVariables()
        return variables

    def traverse(self):
        """traverse Expression tree as root is self

        Yield
        -----
        Expression or VarElement
        """
        yield self
        for elm in self.elms:
            yield from elm.traverse()

    def isNeg(self):
        return False

    def __hash__(self):
        return hash((self.name, self._type))


class Sum(Operation):
    """
    Parameters
    ----------
    var_of_exps : list of VarELement or ExpressionElement
    """

    _type = ExpressionType.Sum

    def setName(self):
        self.name = ""
        const = 0

        elm = self.elms[0]
        if isinstance(elm, number_classes):
            const += elm
        elif isinstance(elm, ExpressionElement) and elm.name.startswith("-"):
            self.name += f"({elm.name})"
        else:
            self.name += f"{elm.name}"

        for elm in self.elms[1:]:
            if isinstance(elm, number_classes):
                const += elm
            elif isinstance(elm, ExpressionElement) and elm.name.startswith("-"):
                self.name += f"+({elm.name})"
            else:
                self.name += f"+{elm.name}"

        if const > 0:
            self.name += f"+{const}"
        elif const < 0:
            self.name += f"-{-const}"

    def isPolynomial(self):
        return all(elm.isPolynomial() for elm in self.elms)

    def setPolynomial(self):
        self.polynomial = sum(elm.toPolynomial() for elm in self.elms)

    def _value(self):
        """
        Returns
        -------
        float or int
            return value of expression
        """

        if self.var_dict is not None:
            ret = 0
            for elm in self.elms:
                if isinstance(elm, ExpressionElement):
                    elm.setVarDict(self.var_dict)
                    ret += elm.value()
                elif elm.name in self.var_dict:
                    ret += self.var_dict[elm.name].value()
                else:
                    ret += elm.value()
            return ret
        else:
            return to_value_ufunc(self.elms).sum()

    def isLinear(self):
        return all(elm.isLinear() for elm in self.elms)

    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"  Type    : {self._type}\n"
        s += f"  Value   : {self.value()}\n"
        return s

    def __repr__(self):
        s = f"Sum({self.elms})"
        return s


class Prod(Operation):
    """
    Parameters
    ----------
    var_of_exps : list of VarELement or ExpressionElement
    """

    _type = ExpressionType.Prod

    def setName(self):
        self.name = ""
        const = 0

        elm = self.elms[0]
        if isinstance(elm, number_classes):
            const += elm
        elif isinstance(elm, ExpressionElement) and elm.name.startswith("-"):
            self.name += f"({elm.name})"
        else:
            self.name += f"{elm.name}"

        for elm in self.elms[1:]:
            if isinstance(elm, number_classes):
                const += elm
            elif isinstance(elm, ExpressionElement) and elm.name.startswith("-"):
                self.name += f"*({elm.name})"
            else:
                self.name += f"*{elm.name}"

        if const != 0:
            self.name = f"{const}*" + self.name

    def isPolynomial(self):
        return all(elm.isPolynomial() for elm in self.elms)

    def setPolynomial(self):
        self.polynomial = functools.reduce(
            operator.mul, (elm.toPolynomial() for elm in self.elms)
        )

    def _value(self):
        """
        Returns
        -------
        float or int
            return value of expression
        """
        if self.var_dict is not None:
            ret = 1
            for elm in self.elms:
                if isinstance(elm, ExpressionElement):
                    elm.setVarDict(self.var_dict)
                    ret *= elm.value()
                elif elm.name in self.var_dict:
                    ret *= self.var_dict[elm.name].value()
                else:
                    ret *= elm.value()
            return ret
        else:
            return to_value_ufunc(self.elms).prod()

    def isLinear(self):
        return sum(not isinstance(elm, number_classes) for elm in self.elms) <= 1

    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"  Type    : {self._type}\n"
        s += f"  Value   : {self.value()}\n"
        return s

    def __repr__(self):
        s = f"Prod({self.elms})"
        return s
