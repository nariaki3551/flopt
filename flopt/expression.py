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
from flopt.env import setup_logger, get_variable_lower_bound, get_variable_upper_bound

logger = setup_logger(__name__)


# -------------------------------------------------------
#   Expression Container
# -------------------------------------------------------


class ExpressionNdarray(np.ndarray):
    def __new__(cls, array, *args, **kwargs):
        if isinstance(array, (list, tuple, set)):
            shape = (len(array),)
        else:
            shape = array.shape
        obj = super().__new__(cls, shape, dtype=ExpressionElement)
        return obj

    def __init__(self, array, set_mono=True, *args, **kwargs):
        if isinstance(array, set):
            array = list(array)
        for i in itertools.product(*map(range, self.shape)):
            j = i[0] if isinstance(array, (list, tuple)) else i
            self[i] = array[j]
        self.name = f"ExpressionNdarray({array})"

    def value(self, solution=None):
        v = np.ndarray(self.shape)
        for i in itertools.product(*map(range, self.shape)):
            v[i] = self[i].value(solution)
        return v


# ------------------------------------------------
#   Expression Base Class
# ------------------------------------------------


class SelfReturn:
    def __init__(self, var):
        self.var = var

    def value(self):
        return self.var


class ExpressionElement:
    """Expression Base Class

    Attributes
    ----------
    name : str
    var_dict : None or dict
    polynomial : None or Polynomial
    parents : list of ExpressionElement
    """

    def __init__(self, name=None):
        self.name = name
        self.var_dict = None
        self.polynomial = None
        self.parents = []

    def setName(self):
        raise NotImplementedError

    def getName(self):
        if self.name is None:
            self.setName()
        return self.name

    def linkChildren(self):
        raise NotImplementedError

    def resetlinkChildren(self):
        for elm in self.traverse():
            if isinstance(elm, ExpressionElement):
                elm.parents = []
        self.linkChildren()
        return self

    def isPolynomial(self):
        raise NotImplementedError

    def setPolynomial(self):
        raise NotImplementedError

    def toPolynomial(self):
        if self.polynomial is None:
            self.setPolynomial()
        return self.polynomial

    def value(self):
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

    def type(self):
        if self.isLinear():
            return ExpressionType.Linear
        elif self.isQuadratic():
            return ExpressionType.Quadratic
        elif self.isPolynomial():
            return ExpressionType.Polynomial
        return self._type

    def constant(self):
        if self.isPolynomial():
            return self.toPolynomial().constant()
        else:
            import sympy

            return float(
                sympy.sympify(self.getName()).expand().as_coefficients_dict()[1]
            )

    def isMonomial(self):
        if self.isPolynomial():
            return self.toPolynomial().isMonomial()
        return False

    def toMonomial(self):
        return self.toPolynomial().toMonomial()

    def isQuadratic(self):
        """
        Returns
        -------
        bool
            return true if this expression is quadratic else false
        """
        if self.isPolynomial():
            return (
                self.toPolynomial().isQuadratic()
                or self.toPolynomial().simplify().isQuadratic()
            )
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
        from flopt.variable import VariableNdarray

        assert x is None or isinstance(
            x, VariableNdarray
        ), f"x must be None or VariableNdarray"
        from flopt.convert import QuadraticStructure

        polynomial = self.toPolynomial().simplify()
        if x is None:
            x = VariableNdarray(sorted(self.getVariables(), key=lambda var: var.name))

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
        if self.isPolynomial():
            return (
                self.toPolynomial().isLinear()
                or self.toPolynomial().simplify().isLinear()
            )
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
        from flopt.variable import VariableNdarray

        assert x is None or isinstance(
            x, VariableNdarray
        ), f"x must be None or VariableNdarray"
        from flopt.convert import LinearStructure

        if x is None:
            x = VariableNdarray(sorted(self.getVariables(), key=lambda var: var.name))

        num_variables = len(x)
        polynomial = self.toPolynomial()

        c = np.zeros((num_variables,), dtype=np_float)
        for mono, coeff in polynomial:
            c[x.index(mono)] = coeff

        C = polynomial.constant()
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
            str(sympy.sympify(self.getName()).simplify()),
            {var.name: var for var in self.getVariables()},
        )
        if isinstance(expr, number_classes):
            expr = Const(expr)
        return expr

    def expand(self):
        """
        Returns
        -------
        Expression
        """
        import sympy

        expr = eval(
            str(sympy.simplify(self.getName()).expand()),
            {var.name: var for var in self.getVariables()},
        )
        if isinstance(expr, number_classes):
            expr = Const(expr)
            return expr
        elif isinstance(expr, Expression):
            expr = eval(
                str(sympy.sympify(expr.getName()).expand()),
                {var.name: var for var in self.getVariables()},
            )
            return expr
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
        return self.value(var_dict=var_dict).expand()

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
        return self.value(var_dict=var_dict).expand()

    def __calculate(self, sense, default_value):
        """Calculate min/max value of expression

        Parameters
        ----------
        sense : str
        default_value : default value of excepsion case

        Returns
        -------
        float
            value of this expression can take
        """
        import flopt

        if self.isLinear():
            solver = flopt.Solver("ScipyMilpSearch")
        elif self.isQuadratic():
            solver = flopt.Solver("CvxoptQpSearch")
        else:
            logger.warning(
                f"{sense} value of {self.getName()} cannot be calculated because it is not linear or quaratic"
            )
            return default_value
        prob = flopt.Problem(sense=sense)
        prob += self
        status, logs = prob.solve(solver, msg=False)
        if status == flopt.SolverTerminateState.Normal:
            return prob.getObjectiveValue()
        elif status == flopt.SolverTerminateState.Unbounded:
            logger.warning(
                f"{sense} value of {self.getName()} cannot be calculated because it is unbounded"
            )
            return default_value
        else:
            logger.warning(
                f"{sense} value of {self.getName()} cannot be calculated by any reasons"
            )
            return default_value

    def max(self):
        """Calculate max value of expression when expression is linear or quadratic

        Returns
        -------
        float
            maximum value of this expression can take
        """
        return self.__calculate("Maximize", get_variable_upper_bound())

    def min(self):
        """Calculate min value of expression when expression is linear or quadratic

        Returns
        -------
        float
            minimum value of this expression can take
        """
        return self.__calculate("Minimize", get_variable_lower_bound())

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
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return self
            return Expression(Const(other), self, "+")
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
            if other.isNeg() and isinstance(other, Expression):
                # self - (-1*other) -> self + other
                return Expression(self, other.elmB, "+")
            return Expression(self, other, "-")
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                # 0 - self --> -1 * self
                return -self
            else:
                return Expression(Const(other), self, "-")
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return 0
            elif other == 1:
                return self
            elif other == -1:
                return -self
            return Expression(Const(other), self, "*")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "*")
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return 0
            elif other == 1:
                return self
            return Expression(Const(other), self, "*")
        elif isinstance(other, ExpressionElement):
            return Expression(other, self, "*")
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return self
            return Expression(self, Const(other), "/")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "/")
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return 0
            return Expression(Const(other), self, "/")
        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return self
            return Expression(self, Const(other), "^")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "^")
        return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return 1
            return Expression(Const(other), self, "^")
        return NotImplemented

    def __and__(self, other):
        if isinstance(other, number_classes):
            return Expression(self, Const(other), "&")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "&")
        return NotImplemented

    def __rand__(self, other):
        return self & other

    def __or__(self, other):
        if isinstance(other, number_classes):
            return Expression(self, Const(other), "|")
        elif isinstance(other, ExpressionElement):
            return Expression(self, other, "|")
        return NotImplemented

    def __ror__(self, other):
        return self | other

    def __neg__(self):
        # -1 * self
        return Expression(Const(-1), self, "*", name=f"-({self.getName()})")

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
        return hash((hash(self.elmA), hash(self.elmB), hash(self.operator)))

    def __call__(self, solution):
        """
        Parameters
        ----------
        solution: Solution
        """
        return self.value(solution)

    def __eq__(self, other):
        # self == other --> self - other == 0
        return Constraint(self - other, ConstraintType.Eq)

    def __le__(self, other):
        # self <= other --> self - other <= 0
        return Constraint(self - other, ConstraintType.Le)

    def __ge__(self, other):
        # self >= other --> other - self <= 0
        return Constraint(other - self, ConstraintType.Le)

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

    .. code-block:: python

        a = Variable(name="a", ini_value=1, cat="Integer")
        b = Variable(name="b", ini_value=2, cat="Continuous")
        c = Expression(a, b, "+")
        >>> print(c)
        >>> Name: a+b
             Type    : Expression
             Value   : 3
        c.value()
        >>> 3
        c.getVariables()
        >>> {VarElement("b", 1, 2, 2), VarElement("a", 0, 1, 1)}

    operator "+", "-", "*", "/", "^" and "%" are supported for Integer, Binary and
    Continuous Variables.

    .. code-block:: python

        a = Variable(name="a", ini_value=1, cat="Integer")  # a.value() is 1
        b = Variable(name="b", ini_value=2, cat="Continuous")  # b.value() is 2
        Expression(a, b, "+").value()  # a+b addition
        >>> 3
        Expression(a, b, "-").value()  # a-b substraction
        >>> -1
        Expression(a, b, "*").value()  # a*b multiplication
        >>> 2
        Expression(a, b, "/").value()  # a/b division
        >>> 0.5
        Expression(a, b, "^").value()  # a/b division
        >>> 1
        Expression(a, b, "%").value()  # a%b modulo
        >>> 1

    operator "&", "|" are supported for Binary Variable.

    .. code-block:: python

        a = Variable(name="a", ini_value=1, cat="Binary")
        b = Variable(name="b", ini_value=0, cat="Binary")
        Expression(a, b, "&").value().value()  # a&b bitwise and
        >>> 0
        Expression(a, b, "|").value().value()  # a&b bitwise or
        >>> 1
    """

    _type = ExpressionType.Unknown

    def __init__(self, elmA, elmB, operator, name=None):
        self.elmA = elmA
        self.elmB = elmB
        self.operator = operator
        super().__init__(name=name)

    @classmethod
    def fromPolynomial(cls, polynomial):
        from flopt import Sum, Prod

        elms = []
        for mono, coeff in polynomial:
            if len(prod_elms := [var**exp for var, exp in mono]) > 1:
                prod = Prod(prod_elms)
            else:
                prod = prod_elms[0]
            elms.append(coeff * mono.coeff * prod)
        if not polynomial.constant() == 0:
            elms += [Const(polynomial.constant())]
        if len(elms) == 0:
            return Const(0)
        elif len(elms) == 1:
            if not isinstance(elms, ExpressionElement):
                return elms[0] + Const(0)
            return elms[0]
        return Sum(elms)

    def setName(self):
        stack = [self]
        while stack:
            elm = stack.pop()
            if elm.name is not None:
                continue
            if isinstance(elm, (Reduction, Const)):
                elm.setName()
                continue
            elmA = elm.elmA
            elmB = elm.elmB
            if elmA.name is not None and elmB.name is not None:
                elmA_name = elm.elmA.getName()
                elmB_name = elm.elmB.getName()
                if isinstance(elm.elmA, (Expression, Reduction)):
                    if elm.operator in {"*", "/", "^", "%"}:
                        elmA_name = f"({elmA_name})"
                if isinstance(elm.elmB, Expression):
                    if elm.operator != "+" or elm.elmB.getName().startswith("-"):
                        elmB_name = f"({elmB_name})"
                elif isinstance(elm.elmB, Reduction):
                    elmB_name = f"({elmB_name})"
                elm.name = f"{elmA_name}{elm.operator}{elmB_name}"
            else:
                stack.append(elm)
                if elmA.name is None:
                    stack.append(elmA)
                if elmB.name is None:
                    stack.append(elmB)
        return self.name

    def linkChildren(self):
        if isinstance(self.elmA, ExpressionElement):
            self.elmA.parents.append(self)
            self.elmA.linkChildren()
        if isinstance(self.elmB, ExpressionElement):
            self.elmB.parents.append(self)
            self.elmB.linkChildren()

    def isPolynomial(self):
        return self.polynomial is not None or (
            self.elmA.isPolynomial()
            and self.elmB.isPolynomial()
            and (
                self.operator == "+"
                or self.operator == "-"
                or self.operator == "*"
                or self.operator == "^"
                or (self.operator == "/" and isinstance(self.elmB, Const))
            )
        )

    def setPolynomial(self):
        stack = [self]
        while stack:
            elm = stack.pop()
            if elm.polynomial is not None:
                continue
            if isinstance(elm, (Reduction, Const)):
                elm.setPolynomial()
                continue
            elmA = elm.elmA
            elmB = elm.elmB
            if elmA.polynomial is not None and elmB.polynomial is not None:
                if elm.operator == "+":
                    elm.polynomial = elmA.toPolynomial() + elmB.toPolynomial()
                elif elm.operator == "-":
                    elm.polynomial = elmA.toPolynomial() - elmB.toPolynomial()
                elif elm.operator == "*":
                    elm.polynomial = elmA.toPolynomial() * elmB.toPolynomial()
                elif elm.operator == "/" and isinstance(elmB, Const):
                    elm.polynomial = elmA.toPolynomial() * (1.0 / elmB.value())
                elif (
                    elm.operator == "^"
                    and isinstance(elmB, Const)
                    and isinstance(elmB.value(), int)
                ):
                    elm.polynomial = elmA.toPolynomial() ** elmB.value()
                else:
                    assert "check whethere this expresson is polynomial or not by .isPolynomial() before execution of setPolynomial()"
            else:
                stack.append(elm)
                if elmA.polynomial is None:
                    stack.append(elmA)
                if elmB.polynomial is None:
                    stack.append(elmB)
        return self.polynomial

    def value(self, solution=None, var_dict=None):
        """
        Returns
        -------
        float or int
            return value of expression
        """
        assert not (solution is not None and var_dict is not None)
        if solution is not None:
            var_dict = solution.toDict()
            solution = None

        if var_dict is not None and self.elmA.name in var_dict:
            elmA_value = var_dict[self.elmA.name].value()
        else:
            elmA_value = self.elmA.value(var_dict=var_dict)

        if var_dict is not None and self.elmB.name in var_dict:
            elmB_value = var_dict[self.elmB.name].value()
        else:
            elmB_value = self.elmB.value(var_dict=var_dict)

        if self.operator == "+":
            return elmA_value + elmB_value
        elif self.operator == "-":
            return elmA_value - elmB_value
        elif self.operator == "*":
            return elmA_value * elmB_value
        elif self.operator == "/":
            return elmA_value / elmB_value
        elif self.operator == "^":
            return elmA_value ** elmB_value
        elif self.operator == "%":
            return elmA_value % elmB_value
        elif self.operator == "&":
            return elmA_value & elmB_value
        elif self.operator == "|":
            return elmA_value | elmB_value

    def getVariables(self):
        return self.elmA.getVariables() | self.elmB.getVariables()

    def jac(self, x):
        """jacobian
        Parameters
        ----------
        x: list or numpy.array of VarElement family

        Returns
        -------
        jac: numpy array of Expression
            jac[i] = jacobian of self for x[i]

        Examples
        --------

        .. code-block:: python

            import flopt

            x = flopt.Variable("x")
            y = flopt.Variable("y")

            f = x * y

            # jacobian vector for [x, y]
            f.jac([x, y])
            >>> [Expression(y, 0, +) Expression(x, 0, +)]

            # jacobian vector for [y, x]
            f.jac([y, x])
            >>> [Expression(x, 0, +) Expression(y, 0, +)]
        """
        from flopt.variable import VariableNdarray

        assert isinstance(x, array_classes), f"x must be array like object"

        if not isinstance(x, VariableNdarray):
            x = VariableNdarray(x)

        num_variables = len(x)
        if self.polynomial is None:
            self.setPolynomial()

        jac = np.empty((num_variables,), dtype=object)
        for i in range(num_variables):
            jac[i] = Expression.fromPolynomial(self.polynomial.diff(x[i]))
        return ExpressionNdarray(jac)

    def hess(self, x):
        """hessian
        Parameters
        ----------
        x: list or numpy.array of VarElement family

        Returns
        -------
        hess: numpy array of Expression
            hess[i, j] = hessian of self for x[i] and x[j]

        Examples
        --------

        .. code-block:: python

            import flopt

            x = flopt.Variable("x")
            y = flopt.Variable("y")

            f = x * x * y

            # hessian matrix for [x, y]
            print(f.hess([x, y]))
            >>> [[Expression(y, 0, +) Expression(x, 0, +)]
            >>>  [Expression(2*x, 0, +) Const(0)]]

            # hessian matrix for [x, y]
            print(f.hess([y, x]))
            >>> [[Const(0) Expression(2*x, 0, +)]
            >>>  [Expression(x, 0, +) Expression(y, 0, +)]]
        """
        jac = self.jac(x)
        num_variables = len(x)
        hess = np.empty((num_variables, num_variables), dtype=object)
        for i in range(num_variables):
            for j in range(num_variables):
                hess[i, j] = Expression.fromPolynomial(jac[i].toPolynomial().diff(x[j]))
        return ExpressionNdarray(hess)

    def traverse(self):
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
                return 0
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
                return 0
            elif other == 1:
                return self
            return Expression(Const(other), self, "*")
        return NotImplemented

    def __str__(self):
        return self.getName()

    def __repr__(self):
        s = f"Expression({self.elmA.getName()}, {self.elmB.getName()}, {self.operator})"
        return s

    def __del__(self):
        if isinstance(self.elmA, Const):
            del self.elmA
        if isinstance(self.elmB, Const):
            del self.elmB


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

        if isinstance(array, flopt.variable.VariableNdarray):
            return array.value(var_dict)
        else:
            return cls(
                itertools.starmap(pack_variables, [(var, var_dict) for var in array])
            )
    else:
        var = var_or_array
        return var_dict[var.name].value()


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

      a = Variable("a", cat="Continuous")
      b = Variable("b", cat="Continuous")
      def user_simulater(a, b):
          return simulater(a, b)
      obj = CustomExpression(func=user_simulater, arg=[a, b])
      prob = Problem("simulater")
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

    def value(self, solution=None, var_dict=None):
        assert not (solution is not None and var_dict is not None)
        if solution is not None:
            var_dict = solution.toDict()
            solution = None
        if var_dict is not None:
            arg = pack_variables(self.arg, var_dict)
        else:
            arg = self.arg

        value = self.func(*arg)
        if not isinstance(value, number_classes):
            value = value.value()

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
        return f"CustomExpression({self.func.__name__, self.arg, self.getName()})"


class Const(ExpressionElement):
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
        if isinstance(value, Const):
            value = value._value
        self._value = value
        super().__init__(name=name)

    def setName(self):
        return NotImplemented

    def linkChildren(self):
        return

    def setPolynomial(self):
        self.polynomial = Polynomial(constant=self._value)

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
        return self

    def expand(self, *args, **kwargs):
        return self

    def __add__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value + other)
        return self._value + other

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value - other)
        return self._value - other

    def __rsub__(self, other):
        if isinstance(other, number_classes):
            return Const(other - self._value)
        if self._value < 0:
            return other + (-self)
        return other - self._value

    def __mul__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value * other)
        return self._value * other

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value / other)
        return self._value / other

    def __rtruediv__(self, other):
        return self / other

    def __pow__(self, other):
        if isinstance(other, number_classes):
            return Const(self._value**other)
        return self._value**other

    def __rpow__(self, other):
        return self**other

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
#   Reduction Class
# ------------------------------------------------
class Reduction(ExpressionElement):

    _type = ExpressionType.Unknown

    def __init__(self, var_or_exps, name=None):
        assert len(var_or_exps) > 0
        self.elms = to_const_ufunc(np.array(var_or_exps, dtype=object))
        super().__init__(name=name)

    def linkChildren(self):
        for elm in self.elms:
            if isinstance(elm, ExpressionElement):
                elm.parents.append(self)
                elm.linkChildren()

    def getVariables(self):
        return functools.reduce(operator.or_, (elm.getVariables() for elm in self.elms))

    def jac(self, x):
        """jacobian
        See Also
        --------
        Expression.jac
        """
        exp = self.expand()  # convert reduction obj to Expression
        return exp.jac(x)

    def hess(self, x=None):
        """hessian
        See Also
        --------
        Expression.hess
        """
        exp = self.expand()  # convert reduction obj to Expression
        return exp.hess(x)

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
        return hash(tuple(elm for elm in self.elms)) + hash(self._type)

    def __del__(self):
        for elm in self.elms:
            if isinstance(elm, Const):
                del elm


class Sum(Reduction):
    """
    Parameters
    ----------
    var_of_exps : list of VarELement or ExpressionElement
    """

    def setName(self):
        self.name = ""
        const = 0

        elm = self.elms[0]
        if isinstance(elm, number_classes):
            const += elm
        elif isinstance(elm, ExpressionElement) and elm.getName().startswith("-"):
            self.name += f"({elm.getName()})"
        else:
            self.name += f"{elm.getName()}"

        for elm in self.elms[1:]:
            if isinstance(elm, number_classes):
                const += elm
            elif isinstance(elm, ExpressionElement) and elm.getName().startswith("-"):
                self.name += f"+({elm.getName()})"
            else:
                self.name += f"+{elm.getName()}"

        if const > 0:
            self.name += f"+{const}"
        elif const < 0:
            self.name += f"-{-const}"

    def isPolynomial(self):
        return all(elm.isPolynomial() for elm in self.elms)

    def setPolynomial(self):
        self.polynomial = sum(elm.toPolynomial() for elm in self.elms)

    def value(self, solution=None, var_dict=None):
        """
        Returns
        -------
        float or int
            return value of expression
        """
        assert not (solution is not None and var_dict is not None)
        if solution is not None:
            var_dict = solution.toDict()
            solution = None
        if var_dict is not None:
            ret = 0
            for elm in self.elms:
                if elm.name in var_dict:
                    ret += var_dict[elm.name].value()
                else:
                    ret += elm.value(var_dict=var_dict)
            return ret
        return to_value_ufunc(self.elms).sum()

    def isLinear(self):
        return all(elm.isLinear() for elm in self.elms)

    def isQuadratic(self):
        return all(elm.isQuadratic() for elm in self.elms)

    def __repr__(self):
        s = f"Sum({self.elms})"
        return s


class Prod(Reduction):
    """
    Parameters
    ----------
    var_of_exps : list of VarELement or ExpressionElement
    """

    def setName(self):
        self.name = ""
        const = 0

        elm = self.elms[0]
        if isinstance(elm, number_classes):
            const += elm
        elif isinstance(elm, ExpressionElement) and elm.getName().startswith("-"):
            self.name += f"({elm.getName()})"
        else:
            self.name += f"{elm.getName()}"

        for elm in self.elms[1:]:
            if isinstance(elm, number_classes):
                const += elm
            elif isinstance(elm, ExpressionElement) and elm.getName().startswith("-"):
                self.name += f"*({elm.getName()})"
            else:
                self.name += f"*{elm.getName()}"

        if const != 0:
            self.name = f"{const}*" + self.name

    def isPolynomial(self):
        return all(elm.isPolynomial() for elm in self.elms)

    def setPolynomial(self):
        self.polynomial = functools.reduce(
            operator.mul, (elm.toPolynomial() for elm in self.elms)
        )

    def value(self, solution=None, var_dict=None):
        """
        Returns
        -------
        float or int
            return value of expression
        """
        assert not (solution is not None and var_dict is not None)
        if solution is not None:
            var_dict = solution.toDict()
            solution = None
        if var_dict is not None:
            ret = 1
            for elm in self.elms:
                if elm.name in var_dict:
                    ret *= var_dict[elm.name].value()
                else:
                    ret *= elm.value(var_dict=var_dict)
            return ret
        return to_value_ufunc(self.elms).prod()

    def isLinear(self):
        return self.toPolynomial().isLinear()

    def isQuadratic(self):
        return self.toPolynomial().isQuadratic()

    def __repr__(self):
        s = f"Prod({self.elms})"
        return s
