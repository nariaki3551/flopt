import random
from math import ceil, floor

from flopt.expression import Expression
from flopt.constraint import Constraint
from flopt.env import setup_logger


logger = setup_logger(__name__)


INI_BOUND = 1e10

def Variable(name, lowBound=-INI_BOUND, upBound=INI_BOUND, cat='Continuous', iniValue=None):
    """
    Create Variable object

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
    iniValue : float, optional
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
    >>> b = Variable(name='b', lowBound=1, upBound=2, cat='Continuous')
    >>> c = Variable(name='b', lowBound=-2, intValue=3, cat='Continuous')
    >>> d = Variable(name='d', cat='Binary')

    Create [lowBound, ..., upBound] range permutation variable

    >>> e = Variable(name='e', lowBound=0, upBound=10, cat='Permutation')

    We can see the data of variable, print().

    >>> print(e)
    >>> Name: e
    >>> Type    : VarPermutation
    >>> Value   : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> lowBound: 0
    >>> upBound : 10
    """
    if cat == 'Continuous':
        return VarContinuous(name, lowBound, upBound, iniValue)
    elif cat == 'Integer':
        return VarInteger(name, lowBound, upBound, iniValue)
    elif cat == 'Binary':
        return VarBinary(name, iniValue)
    elif cat == 'Permutation':
        return VarPermutation(name, lowBound, upBound, iniValue)
    else:
        raise ValueError(f"cat {cat} cannot be used")



class VarElement:
    """
    Base Variable class
    """
    def __init__(self, name, lowBound, upBound, iniValue):
        self.name = name
        self.lowBound = lowBound
        self.upBound = upBound
        if iniValue is None:
            iniValue = self.getIniValue()
        self._value = iniValue

    def getType(self):
        """
        Returns
        -------
        str
          return variable type
        """
        return self.type

    def value(self):
        """
        Returns
        -------
        float or int
          return value of variable
        """
        return self._value

    def setValue(self, value):
        """
        set the value to variable
        """
        self._value = value

    def feasible(self):
        """
        Returns
        -------
        bool
          return true if value of self is in between lowBound and upBound else false
        """
        return self.lowBound <= self._value <= self.upBound

    def clip(self):
        """
        map in an feasible area by clipping.
        ex. value < lowBound -> value = lowBound,
        value > upBound  -> value = upBound
        """
        if self._value < self.lowBound:
            self._value = self.lowBound
        elif self._value > self.upBound:
            self._value = self.upBound

    def getVariables(self):
        # for getVariables() in Expression class
        return {self}

    def hasCustomExpression(self):
        # for hasCustomExpression() in Expression class
        return False

    def isLinear(self):
        return True

    def setRandom(self):
        """
        set random value to variable
        """
        pass  # define each VarElement family

    def maxDegree(self):
        return 1

    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
            return Expression(self, other, '+')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '+')
        else:
            return NotImplemented

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
            return Expression(self, other, '-')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '-')
        else:
            return NotImplemented

    def __rsub__(self, other):
        return other + (-self)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
            return Expression(self, other, '*')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '*')
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
            return Expression(self, other, '/')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '/')
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
            return Expression(other, self, '/')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(other, self, '/')
        else:
            return NotImplemented

    def __mod__(self, other):
        if isinstance(other, int):
            other = VarConst(f'{other}', other)
            return Expression(self, other, '%')
        elif isinstance(other, (VarInteger, Expression)):
            return Expression(self, other, '%')
        else:
            raise NotImplementedError()

    def __pow__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
            return Expression(self, other, '^')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '^')
        else:
            return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
            return Expression(other, self, '^')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(other, self, '^')
        else:
            return NotImplemented

    def __abs__(self):
        return abs(self._value)

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __neg__(self):
        # 0 - self
        zero = VarConst(f'0', 0)
        return Expression(zero, self, '-')

    def __pos__(self):
        return self

    def __hash__(self):
        return hash(self.name)

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
        s += f'  lowBound: {self.lowBound}\n'
        s += f'  upBound : {self.upBound}'
        return s

    def __repr__(self):
        return f'VarElement("{self.name}", {self.lowBound}, {self.upBound}, {self.value()})'


class VarInteger(VarElement):
    """
    Ingeter Variable class
    """
    def __init__(self, name, lowBound, upBound, iniValue):
        super().__init__(name, ceil(lowBound), floor(upBound), iniValue)
        self.type = 'VarInteger'

    def getIniValue(self):
        return (self.lowBound + self.upBound) // 2

    def value(self):
        if not isinstance(self._value, int):
            warn = f"value is not int, so output value is casted into int"
            logger.warning(warn)
        return int(self._value)

    def setRandom(self):
        self._value = random.randint(self.lowBound, self.upBound)


class VarBinary(VarInteger):
    """
    Binary Variable class


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
    def __init__(self, name, iniValue):
        super().__init__(name, 0, 1, iniValue)
        self.type = 'VarBinary'

    def setRandom(self):
        self._value = random.randint(0, 1)

    def __invert__(self):
        # (self+1)%2
        two = VarConst(f'2', 2)
        return Expression(self+1, two, '%')

    def __and__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
        return Expression(self, other, '&')

    def __rand__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
        return Expression(other, self, '&')

    def __or__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
        return Expression(self, other, '|')

    def __ror__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(f'{other}', other)
        return Expression(other, self, '|')


class VarContinuous(VarElement):
    """
    Continuous Variable class
    """
    def __init__(self, name, lowBound, upBound, iniValue):
        super().__init__(name, lowBound, upBound, iniValue)
        self.type = 'VarContinuous'

    def getIniValue(self):
        return (self.lowBound + self.upBound) / 2

    def setRandom(self):
        self._value = random.uniform(self.lowBound, self.upBound)


class VarPermutation(VarElement):
    """
    Permutation Variable class

    This has [lowBound, ... upBound] range permutation.

    Examples
    --------

    >>> a = Variable('a', lowBound=0, upBound=3, cat='Permutation')
    >>> a.value()
    >>> [2, 1, 3, 0]   # randomized
    >>> b = Variable('b', lowBound=0, upBound=3, iniValue=[0,1,2,3], cat='Permutation')
    >>> b.value()
    >>> [0, 1, 2, 3]

    We can use list operation to Peramutation Variable

    >>> b[1]
    >>> 1
    >>> len(b)
    >>> 4
    >>> b[1:3]
    >>> [1, 2]
    """
    def __init__(self, name, lowBound, upBound, iniValue):
        super().__init__(name, lowBound, upBound, iniValue)
        self.type = 'VarPermutation'

    def getIniValue(self):
        return list(range(self.lowBound, self.upBound+1))

    def value(self):
        """
        list
          return permutation
        """
        _value = self._value[:]  # copy
        return _value

    def setRandom(self):
        """
        shuffle the list
        """
        return random.shuffle(self._value)

    def __iter__(self):
        return iter(self._value)

    def __getitem__(self, k):
        return self._value[k]

    def __len__(self):
        return len(self._value)


class VarConst(VarElement):
    """
    It is the variable of constant value.
    We use it the operation including constant value.
    See VarElement class `__add__`, `__sub__`, and so on.

    Parameters
    ----------
    name : str
      name
    const : float or int
      value
    """
    def __init__(self, name, const):
        super().__init__(name, const, const, const)
        self.type = 'VarConst'

    def getVariables(self):
        # for getVariables() in Expression class
        return set()

    def maxDegree(self):
        return 0
