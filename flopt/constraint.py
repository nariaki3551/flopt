from flopt.constants import number_classes


class Constraint:
    """Constraint Class

    three type constraint, ==, <=, and >=.

    - eq type (equal) expression == 0
    - le type (less than or equal) expression <= 0
    - ge type (greater than or equal) expression >= 0

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
    def __init__(self, left, right, _type, name=None):
        assert _type in {'eq', 'le', 'ge'},\
            f"""get constraint type {_type} but this is not supported.
                You must choice from eq, le or ge.
             """
        self.expression = left - right
        self.type = _type
        self.name = name
        self.left = left
        self.right = right


    def value(self, solution=None):
        return self.expression.value(solution)


    def feasible(self, solution=None):
        exp_value = self.value(solution)
        if self.type == 'eq':
            return exp_value == 0
        elif self.type == 'le':
            return exp_value <= 0
        elif self.type == 'ge':
            return exp_value >= 0


    def getVariables(self):
        return self.expression.getVariables()


    def isLinear(self):
        return self.expression.isLinear()


    def toSpin(self):
        if not isinstance(self.left, number_classes):
            self.left = self.left.toSpin()
        if not isinstance(self.right, number_classes):
            self.right = self.right.toSpin()
        self.expression = self.left - self.right
        return self


    def __str__(self):
        if self.type == 'eq':
            type_str = '=='
        elif self.type == 'le':
            type_str = '<='
        elif self.type == 'ge':
            type_str = '>='
        return f'{self.expression.name} {type_str} 0'

    def __repr__(self):
        return f'Constraint({repr(self.left)}, {repr(self.right)}, {self.type}, {self.name})'

