from flopt.constants import ConstraintType, number_classes


class Constraint:
    """Constraint Class

    three type constraint, == or <=

    - eq type (equal) expression == 0
    - le type (less than or equal) expression <= 0

    Parameters
    ----------
    expression : Expression family
        expression of constraint.
    type : str
        Constraint type. We must choice from eq, le or ge.

    Notes
    -----
    For some types, the constraint class may not be created
    if the constant is placed on the left side.

    >>> import flopt
    >>> import numpy as np
    >>> a = flopt.Variable('a', cat='Binary')
    >>> np.float64(0) <= a
    >>> True
    """

    def __init__(self, expression, _type, name=None):
        assert isinstance(_type, ConstraintType)
        self.expression = expression
        self.type = _type
        self.name = name
        self.hash = None

    def value(self, solution=None):
        return self.expression.value(solution)

    def feasible(self, solution=None):
        exp_value = self.value(solution)
        if self.type == ConstraintType.Eq:
            return exp_value == 0
        else:  # self.type == ConstraintType.Le
            return exp_value <= 0

    def getVariables(self):
        return self.expression.getVariables()

    def isLinear(self):
        return self.expression.isLinear()

    def toSpin(self):
        self.expression = self.expression.toSpin()
        return self

    def __hash__(self):
        if self.hash is None:
            self.hash = hash((Constraint, hash(self.expression), self.type))
        return self.hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        if self.type == ConstraintType.Eq:
            type_str = "=="
        else:  # self.type == ConstraintType.Le
            type_str = "<="
        return f"{self.expression.name} {type_str} 0"

    def __repr__(self):
        return f"Constraint({repr(self.expression)}, {self.type}, {self.name})"
