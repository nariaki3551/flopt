import math

import numpy as np

from flopt.variable import VariableArray
from flopt.constants import VariableType
from flopt.env import setup_logger


logger = setup_logger(__name__)


class Solution:
    """
    Solution Class

    Parameters
    ----------
    name : str
      name of solution
    variables : list of VarElement family
      variables which has no duplicate

    Attributes
    ----------
    name : str
        name of solution
    type : str
    _variables : list of varElement
        variable array
    _var_dict : dict
        key is name of variable, key is variable

    Examples
    ----------
    Create a Solution which has Integer, Continuous and Binary Variables

    >>> a = Variable(name="a", lowBound=0, upBound=1, cat="Integer")
    >>> b = Variable(name="b", lowBound=1, upBound=2, cat="Continuous")
    >>> c = Variable(name="c", cat="Binary")
    >>> sol = Solution("abc", [a, b, c])

    Four arithmetic operations are supported
    between Solutions or between a Solution and a constant.

    >>> sol1 = Solution("sol1", [a, b])
    >>> sol2 = Solution("sol2", [a, c])
    >>> sol_plus = sol1 + sol2  # (Solution + Solution or Solution + list)
    >>> sol_minus = sol1 - sol2  # (Solution - Solution or Solution - list)
    >>> sol_product = sol1 * 2  # (Solution * constant)
    >>> sol_divide = sol1 / 2  # (Solution / constant)
    """

    def __init__(self, name=None, variables=[]):
        self.name = name
        self.type = "Solution"
        self._variables = sorted(variables, key=lambda var: var.name)
        self._var_dict = None

    def toDict(self):
        """
        Returns
        -------
        dict:
            key is name of variable,
            value is VarElement family or Expression or Const
        """
        if self._var_dict is None:
            self._var_dict = {var.name: var for var in self._variables}
        return self._var_dict

    def value(self, solution=None):
        """
        Parameters
        ----------
        solution: None or Solution

        Returns
        -------
        list
            values of the variables in the Solution
        """
        if solution is not None:
            return [solution.toDict()[var.name] for var in solution]
        return [var.value() for var in self._variables]

    def setValue(self, name, value):
        """
        Parameters
        ----------
        name: str
        value: int or float
        """
        self.toDict()[name].setValue(value)

    def setValuesFromArray(self, array):
        """
        Parameters
        ----------
        array: iterator
            array of variable values
        """
        assert len(self._variables) == len(array)
        for var, value in zip(self._variables, array):
            var.setValue(value)

    def getVariables(self):
        """
        Returns
        -------
        list
          Variable instances which belong to the Solution
        """
        return self._variables

    def clone(self):
        """
        Returns
        -------
        Solution
          Copy of the Solution (call by value)
        """
        return +self

    def copy(self, other):
        """
        Copy the values of a Solution to itself (call by value)
        """
        for var, ovar in zip(self._variables, other._variables):
            var.setValue(ovar.value())

    def setRandom(self):
        """
        Set the solution values uniformly random
        """
        for var in self._variables:
            var.setRandom()
        return self

    def feasible(self):
        """
        Returns
        -------
        bool
          Whether the solution is feasible or not
        """
        return all(var.feasible() for var in self._variables)

    def clip(self):
        """
        Guarantee feasibility of the solution
        """
        for var in self._variables:
            var.clip()

    def squaredNorm(self):
        """
        Returns
        -------
        float
          Squared 2-norm of the solution as a vector in Euclid space
        """
        return sum(var.value() * var.value() for var in self._variables)

    def norm(self):
        """
        Returns
        -------
        float
          2-norm of the solution as a vector in Euclid space
        """
        return math.sqrt(self.squaredNorm())

    def dot(self, other):
        """
        Returns
        -------
        float
          Inner product between the Solution and another Solution
        """
        inner = sum(
            var1.value() * var2.value()
            for var1, var2 in zip(self._variables, other._variables)
        )
        return inner

    def __pos__(self):
        variables = [var.clone() for var in self._variables]
        return Solution(f"+({self.name})", variables)

    def __neg__(self):
        variables = [var.clone() for var in self._variables]
        for var in variables:
            var.setValue(-var.value())
        return Solution(f"-({self.name})", variables)

    def __add__(self, other):
        """
        Parameters
        ----------
        other: Solution or np.ndarray or list or float

        Returns
        -------
        solution: new instance of self + other
        """
        solution = self.clone()
        solution += other
        return solution

    def __iadd__(self, other):
        """
        Parameters
        ----------
        other: Solution or np.ndarray or list or float

        Returns
        -------
        solution: self added by other
        """
        if isinstance(other, Solution):
            for var1, var2 in zip(self._variables, other._variables):
                var1.setValue(var1.value() + var2.value())
        elif isinstance(other, (list, np.ndarray)):
            for var, v in zip(self._variables, other):
                var.setValue(var.value() + v)
        elif isinstance(other, (int, float)):
            for var in self._variables:
                var.setValue(var.value() + other)
        else:
            raise NotImplementedError
        return self

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        """
        Parameters
        ----------
        other: Solution or np.ndarray or list or float

        Returns
        -------
        solution: new instance of self - other
        """
        solution = self.clone()
        solution -= other
        return solution

    def __isub__(self, other):
        """
        Parameters
        ----------
        other: Solution or np.ndarray or list or float

        Returns
        -------
        solution: self substracted by other
        """
        if isinstance(other, Solution):
            for var1, var2 in zip(self._variables, other._variables):
                var1.setValue(var1.value() - var2.value())
        elif isinstance(other, (list, np.ndarray)):
            for var, v in zip(self._variables, other):
                var.setValue(var.value() - v)
        elif isinstance(other, (int, float)):
            for var in self._variables:
                var.setValue(var.value() - other)
        else:
            raise NotImplementedError
        return self

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        """
        Parameters
        ----------
        other: Solution or np.ndarray or list or float

        Returns
        -------
        solution: new instance of self * other
        """
        solution = self.clone()
        solution *= other
        return solution

    def __imul__(self, other):
        """
        Parameters
        ----------
        other: Solution or np.ndarray or list or float

        Returns
        -------
        solution: self multiplied by other
        """
        if isinstance(other, Solution):
            for var1, var2 in zip(self._variables, other._variables):
                var1.setValue(var1.value() * var2.value())
        elif isinstance(other, (list, np.ndarray)):
            for var, v in zip(self._variables, other):
                var.setValue(var.value() * v)
        elif isinstance(other, (int, float)):
            for var in self._variables:
                var.setValue(var.value() * other)
        else:
            raise NotImplementedError
        return self

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        """
        Parameters
        ----------
        other: Solution or np.ndarray or list or float

        Returns
        -------
        solution: new instance of self / other
        """
        solution = self.clone()
        solution /= other
        return solution

    def __itruediv__(self, other):
        """
        Parameters
        ----------
        other: Solution or np.ndarray or list or float

        Returns
        -------
        solution: self divided by other
        """
        if isinstance(other, list):
            other = [1.0 / v for v in other]
        if isinstance(other, (int, float, np.ndarray)):
            other = 1.0 / other
        else:
            NotImplementedError
        return self.__imul__(other)

    def __abs__(self):
        variables = [var.clone() for var in self._variables]
        for var in variables:
            var.setValue(abs(var.value()))
        return Solution("abs", variables)

    def __hash__(self):
        return hash((self.name, tuple(self._variables)))

    def __len__(self):
        return len(self._variables)

    def __iter__(self):
        return iter(self._variables)

    def __getitem__(self, k):
        return self._variables[k]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Solution({self.name}, [{', '.join([var.name for var in self._variables])}])"
