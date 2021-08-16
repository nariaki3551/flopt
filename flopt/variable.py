import random

from flopt.expression import Expression, ExpressionConst
from flopt.constraint import Constraint
from flopt.env import setup_logger


logger = setup_logger(__name__)



# -------------------------------------------------------
#   Variable Utils
# -------------------------------------------------------


INI_BOUND = 1e10


class VariableFactory:
    """API of variable generation
    """
    def checkName(self, name):
        assert '+'   not in name, f'The + character cannot be used in the name.'
        assert '-'   not in name, f'The - character cannot be used in the name.'
        assert '*'   not in name, f'The * character cannot be used in the name.'
        assert '/'   not in name, f'The / character cannot be used in the name.'
        assert '%'   not in name, f'The % character cannot be used in the name.'
        assert '^'   not in name, f'The ^ character cannot be used in the name.'
        assert '('   not in name, f'The ( character cannot be used in the name.'
        assert ')'   not in name, f'The ) character cannot be used in the name.'


    def __call__(self, name, lowBound=None, upBound=None, cat='Continuous', ini_value=None):
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
        self.checkName(name)
        if cat == 'Continuous':
            return VarContinuous(name, lowBound, upBound, ini_value)
        elif cat == 'Integer':
            return VarInteger(name, lowBound, upBound, ini_value)
        elif cat == 'Binary':
            return VarBinary(name, ini_value)
        elif cat == 'Spin':
            return VarSpin(name, ini_value)
        elif cat == 'Permutation':
            return VarPermutation(name, lowBound, upBound, ini_value)
        else:
            raise ValueError(f"cat {cat} cannot be used")


    def dict(self, name, keys, lowBound=None, upBound=None, cat='Continuous', ini_value=None):
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

        >>> Variable.dict('x', range(2), cat='Binary')
        >>> {0: Variable(x_0, cat="Binary", ini_value=0),
        >>>  1: Variable(x_1, cat="Binary", ini_value=0)}

        >>> Variable.dict('x', (range(2), range(2)), cat='Binary')
        >>> {(0, 0): Variable(x_0_0, cat="Binary", ini_value=0),
             (0, 1): Variable(x_0_1, cat="Binary", ini_value=0),
             (1, 0): Variable(x_1_0, cat="Binary", ini_value=0),
             (1, 1): Variable(x_1_1, cat="Binary", ini_value=0)}

        >>> Variable.dict('x', (range(2), range(2), range(2)), cat='Binary)
        >>> {(0, 0, 0): Variable(x_0_0_0, cat="Binary", ini_value=0),
             (0, 0, 1): Variable(x_0_0_1, cat="Binary", ini_value=0),
             (0, 1, 0): Variable(x_0_1_0, cat="Binary", ini_value=0),
             (0, 1, 1): Variable(x_0_1_1, cat="Binary", ini_value=0),
             (1, 0, 0): Variable(x_1_0_0, cat="Binary", ini_value=0),
             (1, 0, 1): Variable(x_1_0_1, cat="Binary", ini_value=0),
             (1, 1, 0): Variable(x_1_1_0, cat="Binary", ini_value=0),
             (1, 1, 1): Variable(x_1_1_1, cat="Binary", ini_value=0)}

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
                raise ValueError(f'key must not be generator')
            if isinstance(key, (list, tuple)):
                var_name = f'{name}_' + '_'.join(map(str, key))
            else:
                var_name = f'{name}_{key}'
            variables[key] = self(var_name, lowBound, upBound, cat, ini_value)
        return variables


    def array(self, name, shape, lowBound=None, upBound=None, cat='Continuous', ini_value=None):
        """
        Parameters
        ----------
        name : str
          name of variable
        shape : int of tuple of int
            shape of array
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
        numpy.array

        Examples
        --------

        >>> Variable.array('x', 2, cat='Binary')
        >>> array([Variable(x_0, cat="Binary", ini_value=0),
        >>>        Variable(x_1, cat="Binary", ini_value=0)], dtype=object)

        >>> Variable.array('x', (2, 2), cat='Binary')
        >>> array([[Variable(x_0_0, cat="Binary", ini_value=0),
        >>>         Variable(x_0_1, cat="Binary", ini_value=0)],
        >>>        [Variable(x_1_0, cat="Binary", ini_value=0),
        >>>         Variable(x_1_1, cat="Binary", ini_value=0)]], dtype=object)

        >>> Variable.array('x', (2, 2, 2), cat='Binary')
        >>> array([[[Variable(x_0_0_0, cat="Binary", ini_value=0),
        >>>          Variable(x_0_0_1, cat="Binary", ini_value=0)],
        >>>         [Variable(x_0_1_0, cat="Binary", ini_value=0),
        >>>          Variable(x_0_1_1, cat="Binary", ini_value=0)]],
        >>>
        >>>        [[Variable(x_1_0_0, cat="Binary", ini_value=0),
        >>>          Variable(x_1_0_1, cat="Binary", ini_value=0)],
        >>>         [Variable(x_1_1_0, cat="Binary", ini_value=0),
        >>>          Variable(x_1_1_1, cat="Binary", ini_value=0)]]], dtype=object)

        """
        if isinstance(shape, int):
            shape = (shape, )
        iterator = itertools.product(*map(range, shape))
        variables = np.empty(shape, dtype=object)
        for i in iterator:
            var_name = f'{name}_' + '_'.join(map(str, i))
            variables[i] = self(var_name, lowBound, upBound, cat, ini_value)
        return variables


    def matrix(self, name, n_row, n_col, lowBound=None, upBound=None, cat='Continuous', ini_value=None):
        """Overwrap of VariableFactory.array

        Parameters
        ----------
        name : str
          name of variable
        n_row : int
            number of rows
        n_col : int
            number of columns
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
        numpy.array

        Examples
        --------

        >>> Variable.matrix('x', 2, 2, cat='Binary')
        >>> array([[Variable(x_0_0, cat="Binary", ini_value=0),
        >>>         Variable(x_0_1, cat="Binary", ini_value=0)],
        >>>        [Variable(x_1_0, cat="Binary", ini_value=0),
        >>>         Variable(x_1_1, cat="Binary", ini_value=0)]], dtype=object)

        """
        return self.array(name, (n_row, n_col), lowBound, upBound, cat, ini_value)


def value(x):
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
    if isinstance(x, VarElement):
        return x.value()
    elif isinstance(x, (list, tuple)):
        cast = type(x)
        return cast([var.value() for var in x])
    elif isinstance(x, np.ndarray):
        def to_value(x):
            return x.value()
        cast = np.frompyfunc(to_value, 1, 1)
        return cast(x)



# -------------------------------------------------------
#   Variable Classes
# -------------------------------------------------------

class VarElement:
    """Base Variable class
    """
    def __init__(self, name, lowBound, upBound, ini_value):
        self.name = name
        self.lowBound = lowBound
        self.upBound = upBound
        if ini_value is None:
            ini_value = self.getIniValue()
        self._value = ini_value


    def getType(self):
        """
        Returns
        -------
        str
          return variable type
        """
        return self.type


    def value(self, solution=None):
        """
        Returns
        -------
        float or int
          return value of variable
        """
        if solution is None:
            return self._value
        else:
            return solution.toDict()[self.name]


    def setValue(self, value):
        self._value = value


    def getLb(self):
        return self.lowBound if self.lowBound is not None else - INI_BOUND


    def getUb(self):
        return self.upBound if self.upBound is not None else INI_BOUND


    def feasible(self):
        """
        Returns
        -------
        bool
          return true if value of self is in between lowBound and upBound else false
        """
        return self.getLb() <= self._value <= self.getUb()


    def clip(self):
        """
        map in an feasible area by clipping.
        ex. value < lowBound -> value = lowBound,
        value > upBound  -> value = upBound
        """
        if self._value < self.getLb():
            self._value = self.getLb()
        elif self._value > self.getUb():
            self._value = self.getUb()


    def toDict(self):
        return {self.name: self}


    def getVariables(self):
        # for getVariables() in Expression class
        return {self}


    def hasCustomExpression(self):
        # for hasCustomExpression() in Expression class
        return False


    def isLinear(self):
        return True


    def setRandom(self):
        """set random value to variable
        """
        raise NotImplementedError()


    def maxDegree(self):
        return 1


    def clone(self):
        raise NotImplementedError()


    def __add__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 0:
                return self
            other = VarConst(other)
            return Expression(self, other, '+')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '+')
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 0:
                return self
            other = VarConst(other)
            return Expression(other, self, '+')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(other, self, '+')
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 0:
                return self
            other = VarConst(other)
            return Expression(self, other, '-')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '-')
        else:
            return NotImplemented

    def __rsub__(self, other):
        # other - self
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            name = f'-{self.name}' if other == 0 else None
            other = VarConst(other)
            return Expression(other, self, '-', name=name)
        elif isinstance(other, (VarElement, Expression)):
            return Expression(other, self, '-')
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 0:
                return VarConst(0)
            elif other == 1:
                return self
            elif other == -1:
                return -self
            other = VarConst(other)
            return Expression(other, self, '*')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '*')
        else:
            return NotImplemented

    def __rmul__(self, other):
        # other * self
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 0:
                return VarConst(0)
            elif other == 1:
                return self
            elif other == -1:
                return -self
            other = VarConst(other)
            return Expression(other, self, '*')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(other, self, '*')
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 1:
                return self
            elif other == -1:
                return -self
            other = VarConst(other)
            return Expression(self, other, '/')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '/')
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 0:
                return VarConst(0)
            other = VarConst(other)
            return Expression(other, self, '/')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(other, self, '/')
        else:
            return NotImplemented

    def __mod__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, int):
            other = VarConst(other)
            return Expression(self, other, '%')
        elif isinstance(other, (VarInteger, Expression)):
            return Expression(self, other, '%')
        else:
            raise NotImplementedError()

    def __pow__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 0:
                return VarConst(1)
            elif other == 1:
                return self
            other = VarConst(other)
            return Expression(self, other, '^')
        elif isinstance(other, (VarElement, Expression)):
            return Expression(self, other, '^')
        else:
            return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, (VarConst, ExpressionConst)):
            other = other.value()
        if isinstance(other, (int, float)):
            if other == 1:
                return VarConst(1)
            other = VarConst(other)
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
        zero = VarConst(0)
        return Expression(zero, self, '-', name=f'-{self.name}')

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
    """Ingeter Variable class
    """
    def __init__(self, name, lowBound, upBound, ini_value):
        super().__init__(name, lowBound, upBound, ini_value)
        self.type = 'VarInteger'


    def value(self, solution=None):
        """
        Returns
        -------
        float or int
          return value of variable
        """
        if solution is None:
            return int(self._value)
        else:
            return solution.toDict()[self.name]


    def getIniValue(self):
        return (self.getLb() + self.getUb()) // 2


    def setRandom(self):
        self._value = random.randint(self.getLb(), self.getUb())


    def clone(self):
        """
        Returns
        -------
        VarInteger
        """
        return VarInteger(self.name, self.lowBound, self.upBound, self._value)



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
    def __init__(self, name, ini_value, spin=None):
        super().__init__(name, 0, 1, ini_value)
        self.type = 'VarBinary'
        self.spin = spin


    def setValue(self, value):
        self._value = value
        if self.spin is not None:
            self.spin._value = int( 2 * value - 1 )


    def setRandom(self):
        self._value = random.randint(0, 1)


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
            self.spin = VarSpin(
                f'{self.name}_s',
                ini_value=int(2*self._value-1), binary=self,
            )
        return (self.spin + 1) * 0.5


    def clone(self):
        """
        Returns
        -------
        VarBinary
        """
        return VarBinary(self.name, self._value, self.spin)


    def __mul__(self, other):
        if id(other) == id(self):
            # a * a = a
            return self
        elif isinstance(other, Expression) and other.operater == '*':
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
        # (self+1)%2
        two = VarConst(2)
        return Expression(self+1, two, '%')

    def __and__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(other)
        return Expression(self, other, '&')

    def __rand__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(other)
        return Expression(other, self, '&')

    def __or__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(other)
        return Expression(self, other, '|')

    def __ror__(self, other):
        if isinstance(other, (int, float)):
            other = VarConst(other)
        return Expression(other, self, '|')

    def __repr__(self):
        return f'Variable("{self.name}", cat="Binary", ini_value={self.value()})'



class VarSpin(VarElement):
    """Spin Variable class, which takes only 1 or -1
    """
    def __init__(self, name, ini_value, binary=None):
        super().__init__(name, -1, 1, ini_value)
        self.type = 'VarSpin'
        self.binary = binary


    def setValue(self, value):
        self._value = value
        if self.binary is not None:
            self.binary._value = int( (value + 1) / 2 )


    def feasible(self):
        """
        Returns
        -------
        bool
          return true if value of self is 1 or -1 else false
        """
        return self._value in {-1, 1}


    def clip(self):
        """map in an feasible area by clipping.
        """
        if self._value <= 0:
            self._value = self.lowBound
        else:
            self._value = self.upBound


    def getIniValue(self):
        return random.choice([-1, 1])


    def setRandom(self):
        """set random value to variable
        """
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
            self.binary = VarBinary(
                f'{self.name}_b',
                ini_value=int((self._value+1)/2), spin=self,
            )
        return 2 * self.binary - 1


    def clone(self):
        """
        Returns
        -------
        VarSpin
        """
        return VarSpin(self.name, self._value, self.binary)


    def __mul__(self, other):
        if id(other) == id(self):
            return VarConst(1)
        elif isinstance(other, Expression) and other.operater == '*':
            if id(other.elmA) == id(self):
                # (a * b) * a = b
                if isinstance(other.elmB, (int, float)):
                    return VarConst(other.elmB)
                else:
                    return other.elmB
            elif id(other.elmB) == id(self):
                # (b * a) * a = b
                if isinstance(other.elmA, (int, float)):
                    return VarConst(other.elmA)
                else:
                    return other.elmA
        return super().__mul__(other)

    def __pow__(self, other):
        if isinstance(other, int):
            if other % 2 == 0:
                return VarConst(1)
            else:
                return self
        return super().__pow__(other)

    def __invert__(self):
        # -self
        return self.__neg__()

    def __repr__(self):
        return f'Variable("{self.name}", cat="Spin", ini_value={self._value})'



class VarContinuous(VarElement):
    """Continuous Variable class
    """
    def __init__(self, name, lowBound, upBound, ini_value):
        super().__init__(name, lowBound, upBound, ini_value)
        self.type = 'VarContinuous'


    def getIniValue(self):
        return (self.getLb() + self.getUb()) / 2


    def setRandom(self):
        self._value = random.uniform(self.getLb(), self.getUb())


    def clone(self):
        """
        Returns
        -------
        VarContinuous
        """
        return VarContinuous(self.name, self.lowBound, self.upBound, self._value)


    def __repr__(self):
        return f'Variable("{self.name}", cat="Continuous", ini_value={self._value})'



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

    We can use list operation to Peramutation Variable

    >>> b[1]
    >>> 1
    >>> len(b)
    >>> 4
    >>> b[1:3]
    >>> [1, 2]
    """
    def __init__(self, name, lowBound, upBound, ini_value):
        super().__init__(name, lowBound, upBound, ini_value)
        self.type = 'VarPermutation'


    def getIniValue(self):
        return list(range(self.getLb(), self.getUb()+1))


    def value(self):
        """
        Returns
        -------
        list
        """
        _value = self._value[:]  # copy
        return _value


    def setRandom(self):
        """shuffle the list
        """
        return random.shuffle(self._value)


    def clone(self):
        """
        Returns
        -------
        VarPermutation
        """
        return VarPermutation(self.name, self.lowBound, self.upBound, self._value)


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
    const : float or int
      value
    """
    def __init__(self, const, name=None):
        if name is None:
            name = f'{const}'
        super().__init__(name, const, const, const)
        self.type = 'VarConst'


    def getVariables(self):
        # for getVariables() in Expression class
        return set()


    def maxDegree(self):
        return 0

    def clone(self):
        """
        Returns
        -------
        VarConst
        """
        return VarConst(self._value)


    def __add__(self, other):
        return self._value + other

    def __radd__(self, other):
        return other + self._value

    def __sub__(self, other):
        return self._value - other

    def __rsub__(self, other):
        return other - self._value

    def __mul__(self, other):
        return self._value * other

    def __rmul__(self, other):
        return other * self._value

    def __truediv__(self, other):
        return self._value / other

    def __rtruediv__(self, other):
        return other / self._value

    def __mod__(self, other):
        return self._value % other

    def __pow__(self, other):
        return self._value ** other

    def __rpow__(self, other):
        return other ** self._value

    def __neg__(self):
        return - self._value

    def __pos__(self):
        return self._value

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        s  = f'Name: {self.name}\n'
        s += f'  Type    : {self.type}\n'
        s += f'  Value   : {self.value()}\n'
        return s

    def __repr__(self):
        return f'VarConst("{self.name}", {self.lowBound}, {self.upBound}, {self.value()})'


