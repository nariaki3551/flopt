from flopt.constants import ConstraintType, number_classes
from flopt.env import setup_logger, create_variable_mode

logger = setup_logger(__name__)


class Constraint:
    """Constraint Class

    three type constraint, == or <=

    - eq type (equal) expression == 0
    - le type (less than or equal) expression <= 0

    Parameters
    ----------
    expression : Expression family
        expression of constraint.
    type : ConstraintType
        Constraint type (Eq or Le)

    Notes
    -----
    For some types, the constraint class may not be created
    if the constant is placed on the left side.

    .. code-block:: python

        import flopt
        import numpy as np
        a = flopt.Variable('a', cat='Binary')
        np.float64(0) <= a
        >>> True
        a >= np.float64(0)
        >>> Constraint(Expression(-1, a, *), Le, None)
    """

    def __init__(self, expression, _type, name=None):
        assert isinstance(_type, ConstraintType)
        self.expression = expression
        self._type = _type
        self.name = name
        self.hash = None

    def type(self):
        return self._type

    def value(self, solution=None):
        return self.expression.value(solution)

    def feasible(self, solution=None):
        exp_value = self.value(solution)
        if self._type == ConstraintType.Eq:
            return exp_value == 0
        else:  # self._type == ConstraintType.Le
            return exp_value <= 0

    def getVariables(self):
        return self.expression.getVariables()

    def isLinear(self):
        return self.expression.isLinear()

    def toSpin(self):
        self.expression = self.expression.toSpin()
        return self

    def __rshift__(self, other):
        """If self is satisfied, then other must be satisfied

        .. code-block:: python

           import flopt

           x = flopt.Variable("x", lowBound=0, upBound=10)
           prob = flopt.Problem()
           # if x is less or equal than 3, then x must be 0
           prob += (x <= 3) >> (x == 0)

        """
        assert isinstance(other, Constraint)
        import flopt

        epsilon = 1e-5
        slide_epsilon = 0.1 * epsilon

        def sazp(v):
            """Slide value for Avoiding Zero in pulus direction"""
            if v != 0:
                return v
            return vv if (vv := v + slide_epsilon) != 0 else vv + slide_epsilon

        def sazm(v):
            """Slide value for Avoiding Zero in minus direction"""
            if v != 0:
                return v
            return vv if (vv := v - slide_epsilon) != 0 else vv - slide_epsilon

        constraints = list()
        x = self.expression
        y = other.expression

        with create_variable_mode():
            delta = flopt.Variable(f"delta", cat="Binary")
        constraints += [sazm(x.min()) * delta <= x - epsilon]

        if self.type() == ConstraintType.Le:
            indicator = delta
        if self.type() == ConstraintType.Eq:
            with create_variable_mode():
                theta = flopt.Variable(f"theta", cat="Binary")
                sigma = flopt.Variable(f"sigma", cat="Binary")
            constraints += [sazp(x.max()) * theta <= x + epsilon]
            constraints += [sigma >= theta + delta - 1]
            indicator = sigma

        constraints += [y <= sazp(y.max()) * (1 - indicator)]
        if other.type() == ConstraintType.Eq:
            constraints += [y >= sazm(y.min()) * (1 - indicator)]

        return constraints

    def __hash__(self):
        if self.hash is None:
            self.hash = hash((Constraint, hash(self.expression), self._type))
        return self.hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        if self._type == ConstraintType.Eq:
            type_str = "=="
        else:  # self._type == ConstraintType.Le
            type_str = "<="
        return f"{self.expression.getName()} {type_str} 0"

    def __repr__(self):
        return f"Constraint({repr(self.expression)}, {self._type}, {self.name})"
