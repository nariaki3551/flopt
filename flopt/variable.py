import math
import types
import random
import itertools

import numpy as np

import flopt
from flopt.polynomial import Monomial, Polynomial
from flopt.expression import ExpressionElement, Expression, Const
from flopt.constraint import Constraint
from flopt.constants import (
    VariableType,
    ConstraintType,
    number_classes,
    array_classes,
    np_float,
)
from flopt.env import (
    setup_logger,
    create_variable_mode,
    is_create_variable_mode,
    get_variable_id,
    get_variable_lower_bound,
    get_variable_upper_bound,
)


logger = setup_logger(__name__)


# -------------------------------------------------------
#   Variable Container Factory
# -------------------------------------------------------


class VariableArray(np.ndarray):
    def __new__(cls, array, *args, **kwargs):
        if isinstance(array, (list, tuple)):
            shape = (len(array),)
        else:
            shape = array.shape
        obj = super().__new__(cls, shape, dtype=VarElement)
        obj.mono_to_index = dict()
        obj.set_mono = False
        return obj

    def __init__(self, array, set_mono=True, *args, **kwargs):
        array = np.array(array, dtype=object)
        for i in itertools.product(*map(range, self.shape)):
            self[i] = array[i]
            if set_mono:
                self.mono_to_index[array[i].toMonomial()] = i
        self.set_mono = set_mono
        self.name = f"VariableArray({array})"

    def __array_finalize__(self, obj):
        self.mono_to_index = getattr(obj, "mono_to_index", None)

    def index(self, mono):
        assert self.set_mono
        if not isinstance(mono, Monomial):
            mono = mono.toMonomial()
        i = self.mono_to_index[mono]
        if len(i) == 1:
            return i[0]
        return i

    def to_value(self, var_dict):
        v = np.ndarray(self.shape)
        for i in itertools.product(*map(range, self.shape)):
            v[i] = var_dict[self[i].name].value()
        return v


# -------------------------------------------------------
#   Variable and Variable Container Factory
# -------------------------------------------------------


class VariableFactory:
    """API of variable generation"""

    def checkName(self, name):
        assert "+" not in name, f"The + character cannot be used in the name."
        assert "-" not in name, f"The - character cannot be used in the name."
        assert "*" not in name, f"The * character cannot be used in the name."
        assert "/" not in name, f"The / character cannot be used in the name."
        assert "%" not in name, f"The % character cannot be used in the name."
        assert "^" not in name, f"The ^ character cannot be used in the name."
        assert "(" not in name, f"The ( character cannot be used in the name."
        assert ")" not in name, f"The ) character cannot be used in the name."
        if is_create_variable_mode():
            assert name.startswith("__"), f"The name must be started with __ characters"
        else:
            assert not name.startswith(
                "__"
            ), f"The name must not be started with __ characters"

    def __call__(
        self, name, lowBound=None, upBound=None, cat="Continuous", ini_value=None
    ):
        """Create Variable object

        Parameters
        ----------
        name : str
          name of variable
        lowBound : float, optional
          lowBound
        upBound : float, optional
          upBound
        cat : str, optional
          category of variable
        ini_value : float, optional
          set value to variable

        Returns
        -------
        Variable Family
          return Variable Family

        Examples
        --------
        Create Integer, Continuous and Binary Variable

        >>> from flopt import Variable
        >>> a = Variable(name='a', lowBound=0, upBound=1, cat='Integer')
        >>> c = Variable(name='c', lowBound=1, upBound=2, cat='Continuous')
        >>> b = Variable(name='b', cat='Binary')
        >>> s = Variable(name='s', cat='Spin')

        Create [lowBound, ..., upBound] range permutation variable

        >>> p = Variable(name='p', lowBound=0, upBound=10, cat='Permutation')

        We can see the data of variable, print().

        >>> print(p)
        >>> Name: p
        >>> Type    : VarPermutation
        >>> Value   : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> lowBound: 0
        >>> upBound : 10
        """
        if is_create_variable_mode():
            assert name is not None
            name = f"__{get_variable_id()}_" + name
        self.checkName(name)
        cat = str(cat)
        if cat == "Continuous":
            return VarContinuous(name, lowBound, upBound, ini_value)
        elif cat == "Integer":
            return VarInteger(name, lowBound, upBound, ini_value)
        elif cat == "Binary":
            if lowBound is not None and lowBound != 0:
                logger.warning(
                    f"lowBound of {name} is ignored because its category is Binary"
                )
            if upBound is not None and upBound != 1:
                logger.warning(
                    f"upBound of {name} is ignored because its category is Binary"
                )
            return VarBinary(name, ini_value)
        elif cat == "Spin":
            return VarSpin(name, ini_value)
        elif cat == "Permutation":
            assert lowBound is not None and upBound is not None
            return VarPermutation(name, lowBound, upBound, ini_value)
        else:
            raise ValueError(f"cat {cat} cannot be used")

    @classmethod
    def dicts(
        cls,
        name,
        indices=None,
        lowBound=None,
        upBound=None,
        cat=VariableType.Continuous,
        ini_value=None,
        index_start=[],
    ):
        """
        Parameters
        ----------
        name : str
          name of variable
        indices : tuple or generator
            keys of variable dictionary
        lowBound : float, optional
          lowBound
        upBound : float, optional
          upBound
        cat : str, optional
          category of variable
        ini_value : float, optional
          set value to variable

        Returns
        -------
        dict

        """

        if indices is None:
            raise TypeError(
                "LpVariable.dicts missing both 'indices' and deprecated 'indexs' arguments."
            )

        if isinstance(indices, types.GeneratorType):
            indices = tuple(indices)
        elif not isinstance(indices, tuple):
            indices = (indices,)

        index = indices[0]
        indices = indices[1:]
        variables = dict()
        if len(indices) == 0:
            for i in index:
                if isinstance(i, array_classes):
                    var_name = f"{name}_" + "_".join(map(str, i))
                else:
                    var_name = f"{name}_{i}"
                variables[i] = Variable(
                    var_name,
                    lowBound,
                    upBound,
                    cat,
                    ini_value,
                )
        else:
            for i in index:
                variables[i] = Variable.dicts(
                    name, indices, lowBound, upBound, cat, ini_value, index_start + [i]
                )
        return variables

    @classmethod
    def dict(
        cls, name, keys, lowBound=None, upBound=None, cat="Continuous", ini_value=None
    ):
        """
        Parameters
        ----------
        name : str
          name of variable
        keys : tuple or generator
            keys of variable dictionary
        lowBound : float, optional
          lowBound
        upBound : float, optional
          upBound
        cat : str, optional
          category of variable
        ini_value : float, optional
          set value to variable

        Returns
        -------
        dict

        Examples
        --------

        >>> Variable.dict('x', [0, 1])
        >>> {0: Variable(x_0, cat="Continuous", ini_value=0.0),
        >>>  1: Variable(x_1, cat="Continuous", ini_value=0.0)}
        >>>
        >>> Variable.dict('x', range(2), cat='Binary')
        >>> {0: Variable(x_0, cat="Binary", ini_value=0),
        >>>  1: Variable(x_1, cat="Binary", ini_value=0)}
        >>>
        >>> Variable.dict('x', (range(2), range(2)), cat='Binary')
        >>> {(0, 0): Variable(x_0_0, cat="Binary", ini_value=0),
             (0, 1): Variable(x_0_1, cat="Binary", ini_value=0),
             (1, 0): Variable(x_1_0, cat="Binary", ini_value=0),
             (1, 1): Variable(x_1_1, cat="Binary", ini_value=0)}
        >>>
        >>> # not work
        >>> # Variable.dict('x', [range(2), range(2)], cat='Binary')

        """
        if not isinstance(keys, tuple):
            iterator = keys
        else:
            iterator = itertools.product(*keys)
        variables = dict()
        for key in iterator:
            if isinstance(key, (range, types.GeneratorType)):
                raise ValueError(f"key must not be generator")
            if isinstance(key, array_classes):
                var_name = f"{name}_" + "_".join(map(str, key))
            else:
                var_name = f"{name}_{key}"
            variables[key] = Variable(var_name, lowBound, upBound, cat, ini_value)
        return variables

    def array(
        self, name, shape, lowBound=None, upBound=None, cat="Continuous", ini_value=None
    ):
        """
        Parameters
        ----------
        name : str
          name of variable
        shape : int of tuple of int
            shape of array
        lowBound : number class or array of number class
          lowBound
        upBound : number class or array of number class
          upBound
        cat : str or array of cat
          category of variable
        ini_value : number class or array of number class
          set value to variable

        Returns
        -------
        numpy.array

        Examples
        --------

        >>> Variable.array('x', 2, cat='Binary')
        >>> array([Variable(x_0, cat="Binary", ini_value=0),
        >>>        Variable(x_1, cat="Binary", ini_value=0)], dtype=object)
        >>>
        >>> Variable.array('x', (2, 2), cat='Binary')
        >>> array([[Variable(x_0_0, cat="Binary", ini_value=0),
        >>>         Variable(x_0_1, cat="Binary", ini_value=0)],
        >>>        [Variable(x_1_0, cat="Binary", ini_value=0),
        >>>         Variable(x_1_1, cat="Binary", ini_value=0)]], dtype=object)
        """
        if isinstance(shape, int):
            shape = (shape,)
        if isinstance(lowBound, array_classes):
            lowBound = np.array(lowBound, dtype=np_float)
        if isinstance(upBound, array_classes):
            upBound = np.array(upBound, dtype=np_float)
        if isinstance(cat, array_classes):
            cat = np.array(cat, dtype=str)
        if isinstance(ini_value, array_classes):
            ini_value = np.array(ini_value, dtype=np_float)
        iterator = itertools.product(*map(range, shape))
        variables = np.ndarray(shape, dtype=object)
        digits = [len(str(s)) for s in shape]
        for i in iterator:
            var_name = f"{name}_" + "_".join(
                str(s).zfill(digit) for s, digit in zip(i, digits)
            )
            _lowBound = lowBound[i] if isinstance(lowBound, array_classes) else lowBound
            _upBound = upBound[i] if isinstance(upBound, array_classes) else upBound
            _cat = cat[i] if isinstance(cat, array_classes) else cat
            _ini_value = (
                ini_value[i] if isinstance(ini_value, array_classes) else ini_value
            )
            variables[i] = Variable(var_name, _lowBound, _upBound, _cat, _ini_value)
        return VariableArray(variables)

    @classmethod
    def matrix(
        cls,
        name,
        n_row,
        n_col,
        lowBound=None,
        upBound=None,
        cat="Continuous",
        ini_value=None,
    ):
        """Overwrap of VariableFactory.array

        Parameters
        ----------
        name : str
          name of variable
        n_row : int
            number of rows
        n_col : int
            number of columns
        lowBound : number class or array of number class
          lowBound
        upBound : number class or array of number class
          upBound
        cat : str or array of cat
          category of variable
        ini_value : number class or array of number class
          set value to variable

        Returns
        -------
        numpy.array

        Examples
        --------

        >>> Variable.matrix('x', 2, 2, cat='Binary')
        >>> array([[Variable(x_0_0, cat="Binary", ini_value=0),
        >>>         Variable(x_0_1, cat="Binary", ini_value=0)],
        >>>        [Variable(x_1_0, cat="Binary", ini_value=0),
        >>>         Variable(x_1_1, cat="Binary", ini_value=0)]], dtype=object)

        """
        return Variable.array(name, (n_row, n_col), lowBound, upBound, cat, ini_value)


# -------------------------------------------------------
#   Variable Classes
# -------------------------------------------------------


class VarElement:
    """Base Variable class"""

    def __init__(self, name, lowBound=None, upBound=None, ini_value=None):
        self.name = name
        self.lowBound = lowBound
        self.upBound = upBound
        self._value = None
        if ini_value is not None:
            self._value = ini_value
        else:
            self.setRandom()
        self.monomial = Monomial({self: 1})

    def type(self):
        """
        Returns
        -------
        str
          return variable type
        """
        return self._type

    def value(self):
        """
        Returns
        -------
        float or int
          return value of variable
        """
        return self._value

    def setValue(self, value):
        self._value = value

    def getName(self):
        return self.name

    def getLb(self, must_number=False):
        if must_number:
            return (
                self.lowBound
                if self.lowBound is not None
                else get_variable_lower_bound(to_int=True)
            )
        else:
            return self.lowBound

    def getUb(self, must_number=False):
        if must_number:
            return (
                self.upBound
                if self.upBound is not None
                else get_variable_upper_bound(to_int=True)
            )
        else:
            return self.upBound

    def feasible(self):
        """
        Returns
        -------
        bool
          return true if value of self is in between lowBound and upBound else false
        """
        return (
            self.getLb(must_number=True) <= self._value <= self.getUb(must_number=True)
        )

    def clip(self):
        """
        map in an feasible area by clipping.
        ex. value < lowBound -> value = lowBound,
        value > upBound  -> value = upBound
        """
        if self.getLb() is not None:
            lb = self.getLb(must_number=True)
            self._value = max(self._value, lb)
        if self.getUb() is not None:
            ub = self.getUb(must_number=True)
            self._value = min(self._value, ub)

    def toDict(self):
        return {self.name: self}

    def getVariables(self):
        return {self}

    def isPolynomial(self):
        return True

    def toMonomial(self):
        return self.monomial

    def toPolynomial(self):
        return Polynomial({self.monomial: 1})

    def isLinear(self):
        return True

    def isQuadratic(self):
        return True

    def setRandom(self):
        """set random value to variable"""
        raise NotImplementedError()

    def clone(self):
        raise NotImplementedError()

    def max(self):
        if self.upBound is not None:
            return self.upBound
        return get_variable_upper_bound()

    def min(self):
        if self.lowBound is not None:
            return self.lowBound
        return get_variable_lower_bound()

    def traverse(self):
        yield self

    def traverseAncestors(self):
        raise NotImplementedError

    def __add__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return self
            return Expression(self, Const(other), "+")
        elif isinstance(other, VarElement):
            return Expression(self, other, "+")
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
        elif isinstance(other, (VarElement, ExpressionElement)):
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
        elif isinstance(other, VarElement):
            return Expression(self, other, "-")
        elif isinstance(other, ExpressionElement):
            if other.isNeg() and isinstance(other, Expression):
                # self - (-1*other) --> self + other
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
        elif isinstance(other, (VarElement, ExpressionElement)):
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
        elif isinstance(other, VarElement):
            return Expression(self, other, "*")
        elif isinstance(other, ExpressionElement):
            if isinstance(other, Expression):
                if other.operator == "*" and isinstance(other.elmA, Const):
                    # self * (a*other) -> a * (self * other)
                    return other.elmA * Expression(self, other.elmB, "*")
                else:
                    return Expression(other, self, "*")
            else:
                return Expression(other, self, "*")
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            elif other == 1:
                return self
            elif other == -1:
                return -self
            return Expression(Const(other), self, "*")
        elif isinstance(other, ExpressionElement):
            if isinstance(other, Expression):
                if other.operator == "*" and isinstance(other.elmA, Const):
                    # (a*other) * self -> a * (self * other)
                    return other.elmA * Expression(other.elmB, self, "*")
                else:
                    return Expression(other, self, "*")
            else:
                return Expression(other, self, "*")
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return self
            elif other == -1:
                return -self
            return Expression(self, Const(other), "/")
        elif isinstance(other, (VarElement, ExpressionElement)):
            return Expression(self, other, "/")
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(0)
            return Expression(Const(other), self, "/")
        elif isinstance(other, (VarElement, ExpressionElement)):
            return Expression(other, self, "/")
        else:
            return NotImplemented

    def __mod__(self, other):
        if isinstance(other, int):
            return Expression(self, Const(other), "%")
        elif isinstance(other, (VarInteger, ExpressionElement)):
            return Expression(self, other, "%")
        else:
            raise NotImplementedError()

    def __pow__(self, other):
        if isinstance(other, number_classes):
            if other == 0:
                return Const(1)
            elif other == 1:
                return self
            return Expression(self, Const(other), "^")
        elif isinstance(other, (VarElement, ExpressionElement)):
            return Expression(self, other, "^")
        else:
            return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, number_classes):
            if other == 1:
                return Const(1)
            return Expression(Const(other), self, "^")
        elif isinstance(other, (VarElement, ExpressionElement)):
            return Expression(other, self, "^")
        else:
            return NotImplemented

    def __abs__(self):
        return abs(self._value)

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __neg__(self):
        # -1 * self
        return Expression(Const(-1), self, "*", name=f"-{self.name}")

    def __pos__(self):
        return self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        # self == other --> self - other == 0
        if isinstance(other, (number_classes)) and other == 0:
            return Constraint(
                Expression(self, Const(0), "+", name=self.name) - other,
                ConstraintType.Eq,
            )
        else:
            return Constraint(self - other, ConstraintType.Eq)

    def __le__(self, other):
        # self <= other --> self - other <= 0
        if isinstance(other, (number_classes)) and other == 0:
            return Constraint(
                Expression(self, Const(0), "+", name=self.name), ConstraintType.Le
            )
        else:
            return Constraint(self - other, ConstraintType.Le)

    def __ge__(self, other):
        # self >= other --> other - self <= 0
        return Constraint(other - self, ConstraintType.Le)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'VarElement("{self.name}", {self.lowBound}, {self.upBound}, {self.value()})'


class VarInteger(VarElement):
    """Integer Variable class"""

    _type = VariableType.Integer

    def __init__(self, name, lowBound, upBound, ini_value):
        lowBound = lowBound if lowBound is None else math.ceil(lowBound)
        upBound = upBound if upBound is None else math.floor(upBound)
        super().__init__(name, lowBound, upBound, ini_value)
        self.binarized = None
        self.binaries = set()

    def value(self):
        """
        Returns
        -------
        float or int
          return value of variable
        """
        return round(self._value)

    def getLb(self, must_number=False):
        if must_number:
            return (
                self.lowBound
                if self.lowBound is not None
                else get_variable_lower_bound(to_int=True)
            )
        else:
            return self.lowBound

    def getUb(self, must_number=False):
        if must_number:
            return (
                self.upBound
                if self.upBound is not None
                else get_variable_upper_bound(to_int=True)
            )
        else:
            return self.upBound

    def setRandom(self):
        lb = self.getLb(must_number=True)
        ub = self.getUb(must_number=True)
        self._value = random.randint(lb, ub)

    def toBinary(self):
        if self.binarized is None:
            l, u = int(self.getLb()), int(self.getUb())
            with create_variable_mode():
                self.binaries = Variable.array(
                    f"__bin_{self.name}", u - l + 1, cat="Binary"
                )
            self.binarized = flopt.Sum(
                Const(i) * var_bin for i, var_bin in zip(range(l, u + 1), self.binaries)
            )
            if isinstance(self.binarized, VarElement):
                self.binarized = Expression(self.binarized, Const(0), "+")
        return self.binarized

    def getBinaries(self):
        if self.binarized is None:
            self.toBinary()
        return self.binaries

    def toSpin(self):
        return self.toBinary().toSpin()

    def clone(self):
        return VarInteger(self.name, self.lowBound, self.upBound, self._value)

    def __and__(self, other):
        if isinstance(other, number_classes):
            other = Const(other)
        return Expression(self, other, "&")

    def __rand__(self, other):
        if isinstance(other, number_classes):
            other = Const(other)
        return Expression(other, self, "&")

    def __or__(self, other):
        if isinstance(other, number_classes):
            other = Const(other)
        return Expression(self, other, "|")

    def __ror__(self, other):
        if isinstance(other, number_classes):
            other = Const(other)
        return Expression(other, self, "|")

    def __repr__(self):
        return f'Variable("{self.name}", {self.lowBound}, {self.upBound}, "Integer", {self.value()})'


class VarBinary(VarInteger):
    """Binary Variable class

    .. note::
      Binary Variable behaves differently in "-" and "~" operation.

      "-" is the subtraction as interger variable, and
      "~" is the inversion as binary (bool) variable.

      >>> a = Variable('a', intValue=1, cat='Binary')
      >>> a.value()
      >>> 1
      >>> (-a).value()
      >>> -1
      >>> (~a).value()
      >>> 0
    """

    _type = VariableType.Binary

    def __init__(self, name, ini_value=None, spin=None):
        super().__init__(name, 0, 1, ini_value)
        self.spin = spin

    def setValue(self, value):
        self._value = value
        if self.spin is not None:
            self.spin._value = int(2 * value - 1)

    def setRandom(self):
        self._value = random.randint(0, 1)

    def toBinary(self):
        return self

    def toSpin(self):
        """
        Returns
        -------
        Expression

        Notes
        -----
        to convert Spin expression
        {0, 1} to {-1, 1}
        """
        if self.spin is None:
            with create_variable_mode():
                self.spin = VarSpin(
                    f"{self.name}_s",
                    ini_value=int(2 * self._value - 1),
                    binary=self,
                )
        return (self.spin + 1) * 0.5

    def clone(self):
        return VarBinary(self.name, self._value, self.spin)

    def __mul__(self, other):
        if id(other) == id(self):
            # a * a = a
            return self
        elif isinstance(other, ExpressionElement) and other.operator == "*":
            if id(other.elmA) == id(self) or id(other.elmB) == id(self):
                # a * (a * b) = a * b
                # a * (b * a) = b * a
                return other
        return super().__mul__(other)

    def __pow__(self, other):
        if isinstance(other, int):
            return self
        return super().__pow__(other)

    def __invert__(self):
        # 1 -> 0
        # 0 -> 1
        return Expression(Const(1), self, "-")

    def __repr__(self):
        return f'Variable("{self.name}", cat="Binary", ini_value={self.value()})'


class VarSpin(VarElement):
    """Spin Variable class, which takes only 1 or -1"""

    _type = VariableType.Spin

    def __init__(self, name, ini_value, binary=None):
        super().__init__(name, -1, 1, ini_value)
        self.binary = binary

    def setValue(self, value):
        self._value = value
        if self.binary is not None:
            self.binary._value = int((value + 1) / 2)

    def feasible(self):
        """
        Returns
        -------
        bool
          return true if value of self is 1 or -1 else false
        """
        return self._value in {-1, 1}

    def setRandom(self):
        """set random value to variable"""
        self._value = random.choice([-1, 1])

    def toBinary(self):
        """
        Returns
        -------
        Expression

        Notes
        -----
        to convert Binary expression
        {-1, 1} to {0, 1}
        """
        if self.binary is None:
            with create_variable_mode():
                self.binary = VarBinary(
                    f"{self.name}_b",
                    ini_value=int((self._value + 1) / 2),
                    spin=self,
                )
        return 2 * self.binary - 1

    def toSpin(self):
        return self

    def clone(self):
        return VarSpin(self.name, self._value, self.binary)

    def __mul__(self, other):
        if id(other) == id(self):
            return Const(1)
        elif isinstance(other, ExpressionElement) and other.operator == "*":
            if id(other.elmA) == id(self):
                # a * (a * b) = b
                if isinstance(other.elmB, number_classes):
                    return Const(other.elmB)
                else:
                    return other.elmB
            elif id(other.elmB) == id(self):
                # a * (b * a) = b
                if isinstance(other.elmA, number_classes):
                    return Const(other.elmA)
                else:
                    return other.elmA
        return super().__mul__(other)

    def __rmul__(self, other):
        if id(other) == id(self):
            return Const(1)
        elif isinstance(other, ExpressionElement) and other.operator == "*":
            if id(other.elmA) == id(self):
                # (a * b) * a = b
                if isinstance(other.elmB, number_classes):
                    return Const(other.elmB)
                else:
                    return other.elmB
            elif id(other.elmB) == id(self):
                # (b * a) * a = b
                if isinstance(other.elmA, number_classes):
                    return Const(other.elmA)
                else:
                    return other.elmA
        return super().__rmul__(other)

    def __pow__(self, other):
        if isinstance(other, int):
            if other % 2 == 0:
                return Const(1)
            else:
                return self
        return super().__pow__(other)

    def __invert__(self):
        # -self
        return self.__neg__()

    def __repr__(self):
        return f'Variable("{self.name}", cat="Spin", ini_value={self._value})'


class VarContinuous(VarElement):
    """Continuous Variable class"""

    _type = VariableType.Continuous

    def setRandom(self):
        lb = self.getLb(must_number=True)
        ub = self.getUb(must_number=True)
        self._value = random.uniform(lb, ub)

    def clone(self):
        return VarContinuous(self.name, self.lowBound, self.upBound, self._value)

    def __repr__(self):
        return f'Variable("{self.name}", {self.lowBound}, {self.upBound}, "Continuous", {self._value})'


class VarPermutation(VarElement):
    """Permutation Variable class

    This has [lowBound, ... upBound] range permutation.

    Examples
    --------

    >>> a = Variable('a', lowBound=0, upBound=3, cat='Permutation')
    >>> a.value()
    >>> [2, 1, 3, 0]   # randomized
    >>> b = Variable('b', lowBound=0, upBound=3, ini_value=[0,1,2,3], cat='Permutation')
    >>> b.value()
    >>> [0, 1, 2, 3]

    We can use list operation to Permutation Variable

    >>> b[1]
    >>> 1
    >>> len(b)
    >>> 4
    >>> b[1:3]
    >>> [1, 2]
    """

    _type = VariableType.Permutation

    def __init__(self, name, lowBound=None, upBound=None, ini_value=None):
        if ini_value is None:
            ini_value = list(range(lowBound, upBound + 1))
            random.shuffle(ini_value)
        super().__init__(name, lowBound, upBound, ini_value)

    def value(self):
        """
        Returns
        -------
        list
        """
        _value = self._value[:]  # copy
        return _value

    def setRandom(self):
        """shuffle the list"""
        return random.shuffle(self._value)

    def isPolynomial(self):
        return False

    def isLinear(self):
        return False

    def isQuadratic(self):
        return False

    def clone(self):
        return VarPermutation(self.name, self.lowBound, self.upBound, self._value)

    def __iter__(self):
        return iter(self._value)

    def __getitem__(self, k):
        return self._value[k]

    def __len__(self):
        return len(self._value)


# Variable
Variable = VariableFactory()
